"""Stateful API-double ordering/cycle checks; these are not live Project evidence."""
import argparse
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from api import API, Blocked, Project
from control import main, parse_issue_order, queue_order_records
import test_sync as support


class OrderedGitHub(support.FakeGitHub):
    def __init__(self, contents=()):
        super().__init__()
        self.items = [{"id": "item-" + str(i), "content": {"id": c} if c else None,
                       "fieldValues": {"nodes": [], "pageInfo": {"hasNextPage": False}}}
                      for i, c in enumerate(contents)]
        self.position_reads = 0
        self.change_on_read = None
        self.change_identity_on_read = None
        self.lose_position_response = False

    def __call__(self, endpoint, payload):
        q, v = payload["query"], payload["variables"]
        if "orderBy:{field:POSITION" in q:
            self.position_reads += 1
            if self.change_on_read == self.position_reads:
                self.items[-2:] = self.items[-2:][::-1]
            if self.change_identity_on_read == self.position_reads:
                self.items[-1]["content"] = {"id": "different-content"}
        if "updateProjectV2ItemPosition(" in q:
            self.queries.append(q)
            self.writes.append(payload)
            inp = v["input"]
            item = next(i for i in self.items if i["id"] == inp["itemId"])
            self.items.remove(item)
            index = next((n + 1 for n, i in enumerate(self.items) if i["id"] == inp["afterId"]), 0)
            self.items.insert(index, item)
            if self.lose_position_response:
                self.lose_position_response = False
                raise Blocked("api_unavailable", "order", "Response lost after position was applied")
            return {"data": {"updateProjectV2ItemPosition": {"clientMutationId": None}}}
        return super().__call__(endpoint, payload)

    def contents(self):
        return [(i.get("content") or {}).get("id") for i in self.items]

    def position_writes(self):
        return [p for p in self.writes if "updateProjectV2ItemPosition(" in p["query"]]


def gate_case():
    case = support.GateTests("test_pr_associated_exact_branch_and_stale_visible")
    case.setUp()
    return case


class NativeOrderingTests(unittest.TestCase):
    def test_explicit_order_preserves_unselected_and_repeats_without_writes(self):
        fake = OrderedGitHub(["a", None, "b", "pr1", "c", "other"])
        fake.items[0]["fieldValues"]["nodes"] = [{"field": {"name": "Priority"}, "name": "P0"}]
        original_fields = copy.deepcopy(fake.items[0]["fieldValues"])
        p = Project(API(fake), apply=True)
        result = p.order_items(fake.board, ["c", "b"])
        self.assertEqual(result["result"], "verified")
        self.assertEqual(fake.contents(), ["c", "b", "a", None, "pr1", "other"])
        self.assertEqual(fake.items[2]["fieldValues"], original_fields)
        self.assertTrue(all(op["verified"] for op in p.operations))
        count = len(fake.writes)
        self.assertEqual(p.order_items(fake.board, ["c", "b"])["result"], "unchanged")
        self.assertEqual(len(fake.writes), count)

    def test_changed_operator_order_persists(self):
        fake = OrderedGitHub(["a", "b", "c"])
        p = Project(API(fake), apply=True)
        p.order_items(fake.board, ["c", "a"])
        p.order_items(fake.board, ["a", "c"])
        self.assertEqual(fake.contents(), ["a", "c", "b"])

    def test_dry_run_never_mutates(self):
        fake = OrderedGitHub(["a", "b"])
        p = Project(API(fake))
        self.assertEqual(p.order_items(fake.board, ["b"])["result"], "planned")
        self.assertEqual(fake.contents(), ["a", "b"])
        self.assertEqual(fake.writes, [])
        self.assertFalse(p.operations[0]["verified"])

    def test_dry_run_planned_imports_use_no_real_mutation(self):
        fake = OrderedGitHub(["a"])
        p = Project(API(fake))
        self.assertEqual(p.sync(fake.board, [{"node_id": "b", "fields": {}}], fake.fields), [])
        result = p.order_items(fake.board, ["b", "a"])
        self.assertEqual(result["result"], "planned")
        self.assertIn("dry-run:b", str(p.operations))
        self.assertEqual(fake.contents(), ["a"])
        self.assertEqual(fake.writes, [])

    def test_bad_or_missing_ids_fail_before_position_writes(self):
        for ids in (["a", "a"], ["a", "missing"], [None], "a", [""]):
            with self.subTest(ids=ids):
                fake = OrderedGitHub(["a", "b"])
                with self.assertRaises(Blocked):
                    Project(API(fake), apply=True).order_items(fake.board, ids)
                self.assertEqual(fake.writes, [])

    def test_duplicate_project_content_is_not_silently_selected(self):
        fake = OrderedGitHub(["a", "a"])
        with self.assertRaises(Blocked):
            Project(API(fake), apply=True).order_items(fake.board, ["a"])
        self.assertEqual(fake.writes, [])

    def test_duplicate_project_item_id_is_rejected(self):
        fake = OrderedGitHub(["a", "b"])
        fake.items[1]["id"] = fake.items[0]["id"]
        with self.assertRaises(Blocked):
            Project(API(fake), apply=True).order_items(fake.board, ["b"])
        self.assertEqual(fake.writes, [])

    def test_no_permission_prevents_order_read_and_write(self):
        fake = OrderedGitHub(["a", "b"])
        fake.board["viewerCanUpdate"] = False
        with self.assertRaises(Blocked):
            Project(API(fake), apply=True).order_items(fake.board, ["b"])
        self.assertEqual(fake.position_reads, 0)
        self.assertEqual(fake.writes, [])

    def test_lost_response_requires_reread_not_blind_retry(self):
        fake = OrderedGitHub(["a", "b"])
        fake.lose_position_response = True
        p = Project(API(fake), apply=True)
        with self.assertRaises(Blocked):
            p.order_items(fake.board, ["b"])
        self.assertEqual(len(fake.position_writes()), 1)
        self.assertFalse(p.operations[0]["verified"])
        self.assertEqual(p.order_items(fake.board, ["b"])["result"], "unchanged")
        self.assertEqual(len(fake.position_writes()), 1)

    def test_concurrent_reorder_before_write_stops(self):
        fake = OrderedGitHub(["a", "b", "c", "d"])
        fake.change_on_read = 2
        with self.assertRaisesRegex(Blocked, "project_order_changed"):
            Project(API(fake), apply=True).order_items(fake.board, ["b"])
        self.assertEqual(fake.position_writes(), [])

    def test_concurrent_reorder_after_write_stops_without_next_move(self):
        fake = OrderedGitHub(["a", "b", "c", "d"])
        fake.change_on_read = 3
        p = Project(API(fake), apply=True)
        with self.assertRaisesRegex(Blocked, "project_order_changed"):
            p.order_items(fake.board, ["b", "d"])
        self.assertEqual(len(fake.position_writes()), 1)
        self.assertFalse(p.operations[0]["verified"])

    def test_complete_position_pagination(self):
        nodes = [{"id": str(i), "content": {"id": "c" + str(i)}} for i in range(120)]
        pages = []
        def request(endpoint, payload):
            self.assertIn("orderBy:{field:POSITION,direction:ASC}", payload["query"])
            page = 1 if payload["variables"].get("after") else 0
            pages.append(page)
            return {"data": {"node": {"items": support.connection(nodes[100:] if page else nodes[:100], not page, "next")}}}
        p = Project(API(request))
        self.assertEqual(p.order_items({"id": "P"}, ["c119"])["moves"], 1)
        self.assertEqual(pages, [0, 1])

    def test_identity_change_without_position_change_stops(self):
        fake = OrderedGitHub(["a", "b"])
        fake.change_identity_on_read = 2
        with self.assertRaisesRegex(Blocked, "project_order_changed"):
            Project(API(fake), apply=True).order_items(fake.board, ["b"])
        self.assertEqual(fake.position_writes(), [])

    def test_empty_order_has_no_side_effects(self):
        fake = OrderedGitHub(["a"])
        self.assertEqual(Project(API(fake), apply=True).order_items(fake.board, [])["moves"], 0)
        self.assertEqual(fake.queries, [])


class QueueOrderTests(unittest.TestCase):
    def run_cli(self, fake, *arguments):
        case = gate_case()
        with tempfile.TemporaryDirectory() as d, patch("control.collect", return_value=case.snapshot), \
                patch("control.API", return_value=API(fake)), patch("builtins.print"):
            output = Path(d) / "out.json"
            with patch("sys.argv", ["control", *arguments, "--report", str(output)]):
                result = main()
            return result, json.loads(output.read_text())

    def test_cli_apply_sync_and_order_repeat_without_mutation(self):
        fake = OrderedGitHub(["unselected"])
        result, report = self.run_cli(fake, "--apply", "--queue-order", "134")
        self.assertEqual(result, 0)
        self.assertEqual(fake.contents()[0], "I134")
        self.assertEqual(report["queue_order"]["position_result"]["result"], "verified")
        self.assertFalse(report["queue_order"]["dispatch_authorized"])
        writes = len(fake.writes)
        self.assertEqual(self.run_cli(fake, "--apply", "--queue-order", "134")[0], 0)
        self.assertEqual(len(fake.writes), writes)

    def test_cli_native_dry_run_plans_import_and_order_without_mutations(self):
        fake = OrderedGitHub(["unselected"])
        fake.fields[0]["options"] = [{"id": "native-" + name, "name": name}
                                      for name in ("Todo", "In Progress", "Done")]
        result, report = self.run_cli(fake, "--native-status", "--queue-order", "134")
        self.assertEqual(result, 0)
        self.assertEqual(report["queue_order"]["position_result"]["result"], "planned")
        self.assertEqual(fake.writes, [])

    def test_cli_default_does_not_reorder(self):
        fake = OrderedGitHub(["unselected"])
        result, report = self.run_cli(fake, "--apply")
        self.assertEqual(result, 0)
        self.assertNotIn("queue_order", report)
        self.assertEqual(fake.position_writes(), [])
        self.assertEqual(fake.contents()[0], "unselected")

    def test_cli_sync_failure_prevents_all_position_writes(self):
        fake = OrderedGitHub(["unselected"])
        fake.fail_content = "I134"
        result, report = self.run_cli(fake, "--apply", "--queue-order", "134")
        self.assertEqual(result, 2)
        self.assertTrue(report["blocked"])
        self.assertNotIn("position_result", report["queue_order"])
        self.assertEqual(fake.position_writes(), [])

    def test_cli_order_is_positive_unique(self):
        self.assertEqual(parse_issue_order("134, 201"), [134, 201])
        for text in ("", "134,134", "0", "-1", "abc", "1,"):
            with self.subTest(text=text), self.assertRaises(argparse.ArgumentTypeError):
                parse_issue_order(text)

    def test_pr_or_missing_issue_cannot_be_ordered_as_outcome(self):
        report = gate_case().run_report()
        for numbers in ([135], [999], [True], [134, 134]):
            with self.subTest(numbers=numbers), self.assertRaises(Blocked):
                queue_order_records(report, numbers)

    def test_ambiguous_native_issue_identity_is_rejected(self):
        report = gate_case().run_report()
        report["records"].append(copy.deepcopy(report["records"][0]))
        with self.assertRaises(Blocked):
            queue_order_records(report, [134])

    def test_invalid_cli_order_is_rejected_before_project_setup(self):
        case = gate_case()
        with tempfile.TemporaryDirectory() as d, patch("control.collect", return_value=case.snapshot), patch("control.Project") as project:
            with patch("sys.argv", ["control", "--apply", "--queue-order", "135", "--report", str(Path(d) / "out.json")]):
                self.assertEqual(main(), 2)
            project.assert_not_called()

    def test_dependency_and_review_cycle_never_becomes_dispatch(self):
        case = gate_case()
        task = copy.deepcopy(case.task)
        task["dependencies"] = [{"issue_number": 108, "kind": "handoff", "blocks_completion": True,
                                 "reason": "Await owner verification"}]
        case.issue["body"] = "```json\n" + json.dumps(task) + "\n```"
        case.issue["native_blockers"] = [{"number": 108, "state": "closed"}]
        # Closed upstream alone still does not clear the declared dependency.
        report = case.run_report()
        rows = queue_order_records(report, [134])
        self.assertEqual(rows[0]["fields"]["Status"], "BLOCKED")
        fake = OrderedGitHub(["other", "I134"])
        p = Project(API(fake), apply=True)
        fields, incompatible = p.ensure_fields(fake.board)
        self.assertEqual(incompatible, [])
        self.assertEqual(p.sync(fake.board, rows, fields), [])
        self.assertFalse(p.order_items(fake.board, ["I134"])["dispatch_authorized"])
        writes = len(fake.writes)
        self.assertEqual(p.sync(fake.board, rows, fields), [])
        p.order_items(fake.board, ["I134"])
        self.assertEqual(len(fake.writes), writes)
        # An explicit changed owner-claim fixture clears the dependency; ordering
        # itself never edits this claim, verifies completion, or starts a worker.
        task["dependencies"] = []
        case.issue["body"] = "```json\n" + json.dumps(task) + "\n```"
        case.issue["native_blockers"] = []
        updated = case.run_report()
        rows = queue_order_records(updated, [134])
        self.assertEqual(rows[0]["fields"]["Status"], "DRAFT_PR")
        self.assertEqual(p.sync(fake.board, rows, fields), [])
        self.assertEqual(p.order_items(fake.board, ["I134"])["moves"], 0)
        self.assertFalse(updated["executor_connected"])
        self.assertFalse(updated["merge_authorized"])
        self.assertNotIn(rows[0]["fields"]["Status"], ("READY", "COMPLETE"))


if __name__ == "__main__":
    unittest.main()
