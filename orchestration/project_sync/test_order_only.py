"""Position-only CLI regression checks; all transport/state here is synthetic."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from api import API, Blocked
from control import main
from test_ordering import OrderedGitHub, gate_case
from test_sync import connection


class ExistingOrderedGitHub(OrderedGitHub):
    def __init__(self, contents=()):
        super().__init__(contents)
        self.board.update(number=2, title="Existing board")
        # Deliberately incompatible with full sync: it must not be consulted.
        self.fields = [{"id": "native", "name": "Status", "dataType": "SINGLE_SELECT",
                        "options": [{"id": "custom", "name": "User state"}]}]
        for item in self.items:
            item["fieldValues"]["nodes"] = [
                {"field": {"name": "Priority"}, "name": "P1"},
                {"field": {"name": "Status"}, "name": "User state"},
                {"field": {"name": "Custom"}, "text": "preserve me"}]

    def __call__(self, endpoint, payload):
        if "projectsV2(" in payload["query"]:
            self.queries.append(payload["query"])
            return {"data": {"user": {"projectsV2": connection([self.board])}}}
        return super().__call__(endpoint, payload)


class OrderOnlyCLITests(unittest.TestCase):
    def run_cli(self, fake, *args, snapshot=None):
        with tempfile.TemporaryDirectory() as directory, \
                patch("control.collect", return_value=snapshot or gate_case().snapshot), \
                patch("control.API", return_value=API(fake)), patch("builtins.print"), \
                patch("control.Project.ensure_fields", side_effect=AssertionError("configuration forbidden")), \
                patch("control.Project.sync", side_effect=AssertionError("sync forbidden")):
            output = Path(directory) / "report.json"
            with patch("sys.argv", ["control", "--order-only", "--project-number", "2",
                                    "--queue-order", "134", *args, "--report", str(output)]):
                result = main()
            return result, json.loads(output.read_text())

    def test_apply_only_moves_existing_items_and_repeat_is_noop(self):
        fake = ExistingOrderedGitHub(["other", None, "P135", "I134"])
        fields = copy.deepcopy(fake.fields)
        items = {i["id"]: copy.deepcopy(i) for i in fake.items}
        result, report = self.run_cli(fake, "--apply")
        self.assertEqual(result, 0)
        self.assertEqual(report["sync_mode"], "order_only")
        self.assertEqual(report["queue_order"]["position_result"]["result"], "verified")
        self.assertEqual(fake.contents(), ["I134", "other", None, "P135"])
        self.assertEqual({i["id"]: i for i in fake.items}, items)
        self.assertEqual(fake.fields, fields)
        self.assertEqual(len(fake.writes), 1)
        self.assertEqual(fake.writes, fake.position_writes())
        self.assertEqual({op["operation"] for op in report["operations"]}, {"updateProjectV2ItemPosition"})
        self.assertNotIn("view_specifications", report)
        self.assertNotIn("incompatible_fields", report)
        count = len(fake.writes)
        result, repeat = self.run_cli(fake, "--apply")
        self.assertEqual(result, 0)
        self.assertEqual(repeat["queue_order"]["position_result"]["result"], "unchanged")
        self.assertEqual(repeat["operations"], [])
        self.assertEqual(len(fake.writes), count)

    def test_dry_run_never_writes_or_changes_field_values(self):
        fake = ExistingOrderedGitHub(["other", "I134"])
        before = copy.deepcopy(fake.items)
        result, report = self.run_cli(fake)
        self.assertEqual(result, 0)
        self.assertEqual(report["queue_order"]["position_result"]["result"], "planned")
        self.assertTrue(report["dry_run"])
        self.assertEqual(fake.items, before)
        self.assertEqual(fake.writes, [])

    def test_id_selector_works_without_field_configuration(self):
        fake = ExistingOrderedGitHub(["other", "I134"])
        with tempfile.TemporaryDirectory() as d, patch("control.collect", return_value=gate_case().snapshot), \
                patch("control.API", return_value=API(fake)), patch("builtins.print"), \
                patch("control.Project.ensure_fields", side_effect=AssertionError("forbidden")), \
                patch("control.Project.sync", side_effect=AssertionError("forbidden")), \
                patch("sys.argv", ["control", "--order-only", "--project-id", fake.board["id"],
                    "--queue-order", "134", "--apply", "--report", str(Path(d)/"report.json")]):
            self.assertEqual(main(), 0)
        self.assertEqual(fake.contents(), ["I134", "other"])

    def test_missing_member_never_imports_even_in_dry_run(self):
        for apply in ((), ("--apply",)):
            fake = ExistingOrderedGitHub(["other"])
            result, report = self.run_cli(fake, *apply)
            self.assertEqual(result, 2)
            self.assertEqual(report["blocked"][0]["code"], "queue_item_missing")
            self.assertEqual(report["operations"], [])
            self.assertEqual(fake.contents(), ["other"])
            self.assertEqual(fake.writes, [])

    def test_duplicate_members_stop_before_writes(self):
        fake = ExistingOrderedGitHub(["I134", "I134"])
        result, report = self.run_cli(fake, "--apply")
        self.assertEqual(result, 2)
        self.assertEqual(report["blocked"][0]["code"], "duplicate_project_items")
        self.assertEqual(fake.writes, [])

    def test_permission_denial_stops_before_position_read(self):
        fake = ExistingOrderedGitHub(["other", "I134"])
        fake.board["viewerCanUpdate"] = False
        result, report = self.run_cli(fake, "--apply")
        self.assertEqual(result, 2)
        self.assertEqual(report["blocked"][0]["code"], "permission_denied")
        self.assertEqual(fake.position_reads, 0)
        self.assertEqual(fake.writes, [])

    def test_observed_concurrent_order_change_stops(self):
        fake = ExistingOrderedGitHub(["other", "I134", "a", "b"])
        fake.change_on_read = 2
        result, report = self.run_cli(fake, "--apply")
        self.assertEqual(result, 2)
        self.assertEqual(report["blocked"][0]["code"], "project_order_changed")
        self.assertEqual(fake.writes, [])

    def test_uncertain_write_stops_then_rereads_on_repeat(self):
        fake = ExistingOrderedGitHub(["other", "I134"])
        fake.lose_position_response = True
        result, report = self.run_cli(fake, "--apply")
        self.assertEqual(result, 2)
        self.assertFalse(report["operations"][0]["verified"])
        self.assertEqual(len(fake.writes), 1)
        result, report = self.run_cli(fake, "--apply")
        self.assertEqual(result, 0)
        self.assertEqual(report["queue_order"]["position_result"]["result"], "unchanged")
        self.assertEqual(len(fake.writes), 1)

    def test_dependency_and_review_gates_remain_observations(self):
        fake = ExistingOrderedGitHub(["other", "I134"])
        snapshot = gate_case().snapshot
        snapshot["issues"][0]["native_blockers"] = [{"number": 108, "state": "open"}]
        result, report = self.run_cli(fake, "--apply", snapshot=snapshot)
        self.assertEqual(result, 0)
        self.assertEqual(report["queue_order"]["blocked_issues"], [134])
        self.assertFalse(report["queue_order"]["dispatch_authorized"])
        self.assertFalse(report["executor_connected"])
        self.assertEqual(report["records"][0]["fields"]["Status"], "BLOCKED")
        self.assertEqual(report["records"][1]["fields"]["Status"], "DRAFT_PR")
        self.assertEqual(fake.items[0]["fieldValues"]["nodes"][1]["name"], "User state")

    def test_missing_canonical_issue_blocks_before_board_read(self):
        fake = ExistingOrderedGitHub(["I134"])
        snapshot = gate_case().snapshot
        snapshot["issues"] = []
        result, report = self.run_cli(fake, "--apply", snapshot=snapshot)
        self.assertEqual(result, 2)
        self.assertEqual(report["blocked"][0]["code"], "queue_issue_missing")
        self.assertEqual(fake.queries, [])

    def test_collection_failure_blocks_without_project_calls(self):
        fake = ExistingOrderedGitHub(["I134"])
        with tempfile.TemporaryDirectory() as d, \
                patch("control.collect", side_effect=Blocked("snapshot_changed", "collect", "changed")), \
                patch("control.API", return_value=API(fake)), patch("builtins.print"), \
                patch("sys.argv", ["control", "--order-only", "--project-number", "2",
                    "--queue-order", "134", "--apply", "--report", str(Path(d)/"report.json")]):
            self.assertEqual(main(), 2)
        self.assertEqual(fake.queries, [])
        self.assertEqual(fake.writes, [])

    def test_invalid_modes_fail_before_api_or_collection(self):
        cases = [[], ["--project-number", "2"], ["--queue-order", "134"],
                 ["--create-project", "--queue-order", "134"],
                 ["--project-number", "2", "--queue-order", "134", "--native-status"],
                 ["--project-number", "2", "--queue-order", "134", "--snapshot", "old.json", "--apply"]]
        for args in cases:
            with self.subTest(args=args), patch("control.API") as api, patch("control.collect") as collect, \
                    patch("sys.stderr", new_callable=io.StringIO), \
                    patch("sys.argv", ["control", "--order-only", *args, "--report", "unused.json"]):
                with self.assertRaises(SystemExit) as ctx:
                    main()
                self.assertEqual(ctx.exception.code, 2)
                api.assert_not_called()
                collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
