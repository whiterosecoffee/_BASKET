import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

from api import API, Blocked, Project, TITLE, STATES
from control import reconcile, resolution_gate, overlap, check_state, payloads, ROOT


def connection(rows, more=False, cursor=None):
    return {"nodes": copy.deepcopy(rows), "pageInfo": {"hasNextPage": more, "endCursor": cursor}}


class FakeGitHub:
    """Stateful API double: API state, not local controller state, owns idempotency."""
    def __init__(self, projects=None):
        self.board = dict(id="P1", title=TITLE, url="https://github.com/users/example/projects/1",
                          closed=False, viewerCanUpdate=True)
        self.projects = [self.board] if projects is None else projects
        self.items, self.writes, self.queries = [], [], []
        self.fields = [{"id": "status", "name": "Status", "dataType": "SINGLE_SELECT",
                        "options": [{"id": n, "name": n} for n in STATES]}]
        self.fail_content = None
        self.lose_add_response = False

    def __call__(self, endpoint, payload):
        q, v = payload["query"], payload["variables"]
        self.queries.append(q)
        if q.startswith("mutation"):
            self.writes.append(payload)
        if "projectsV2(" in q:
            return {"data": {"user": {"id": "U1", "projectsV2": connection(self.projects)}}}
        if "createProjectV2(" in q:
            self.projects.append(self.board)
            return {"data": {"createProjectV2": {"projectV2": self.board}}}
        if "fields(" in q:
            return {"data": {"node": {"fields": connection(self.fields)}}}
        if "createProjectV2Field(" in q:
            self.fields.append({"id": v["input"]["name"], **v["input"]})
            return {"data": {"createProjectV2Field": {"projectV2Field": {"id": "field"}}}}
        if "items(" in q:
            return {"data": {"node": {"items": connection(self.items)}}}
        if "addProjectV2ItemById(" in q:
            if v["c"] == self.fail_content:
                raise Blocked("permission_denied", "add", "No access")
            item = {"id": "item" + str(len(self.items)), "content": {"id": v["c"]},
                    "fieldValues": {"nodes": [], "pageInfo": {"hasNextPage": False}}}
            self.items.append(item)
            if self.lose_add_response:
                self.lose_add_response = False
                raise Blocked("api_unavailable", "add", "Response lost after server applied mutation")
            return {"data": {"addProjectV2ItemById": {"item": {"id": item["id"]}}}}
        if "updateProjectV2ItemFieldValue(" in q:
            inp = v["input"]
            item = next(i for i in self.items if i["id"] == inp["itemId"])
            field = next(f for f in self.fields if f["id"] == inp["fieldId"])
            nodes = item["fieldValues"]["nodes"]
            nodes[:] = [n for n in nodes if n["field"]["name"] != field["name"]]
            value = next(iter(inp["value"].values()))
            nodes.append({"field": {"name": field["name"]}, "name": value})
            return {"data": {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": item["id"]}}}}
        if "user(login:" in q:
            return {"data": {"user": {"id": "U1"}}}
        raise AssertionError(q)


class APITests(unittest.TestCase):
    def test_discover_reuses_existing(self):
        fake = FakeGitHub()
        p = Project(API(fake), apply=True)
        self.assertEqual(p.discover(True)["id"], "P1")
        self.assertEqual(fake.writes, [])

    def test_create_missing_only_when_explicit(self):
        fake = FakeGitHub([])
        p = Project(API(fake), apply=True)
        with self.assertRaises(Blocked):
            p.discover()
        self.assertEqual(p.discover(True)["id"], "P1")
        self.assertEqual(len(fake.writes), 1)
        p.discover(True)
        self.assertEqual(len(fake.writes), 1)

    def test_create_dry_run_never_mutates(self):
        fake = FakeGitHub([])
        self.assertIsNone(Project(API(fake)).discover(True))
        self.assertEqual(fake.writes, [])

    def test_permission_denied_clear(self):
        fake = FakeGitHub()
        fake.board["viewerCanUpdate"] = False
        with self.assertRaises(Blocked) as ctx:
            Project(API(fake), apply=True).discover()
        self.assertEqual(ctx.exception.result["code"], "permission_denied")

    def test_graphql_partial_data_never_success(self):
        api = API(lambda *a: {"data": {"project": {}}, "errors": [{"type": "FORBIDDEN"}]})
        with self.assertRaises(Blocked) as ctx:
            Project(api).discover()
        self.assertEqual(ctx.exception.result["code"], "permission_denied")

    def test_import_once_repeated_run_no_writes(self):
        fake = FakeGitHub()
        p = Project(API(fake), apply=True)
        records = [{"node_id": "issue1", "fields": {"Status": "BACKLOG"}}] * 2
        self.assertEqual(p.sync(fake.board, records, fake.fields), [])
        self.assertEqual(len(fake.items), 1)
        writes = len(fake.writes)
        self.assertEqual(p.sync(fake.board, records, fake.fields), [])
        self.assertEqual(len(fake.writes), writes)

    def test_lost_mutation_response_re_read_before_retry(self):
        fake = FakeGitHub()
        fake.lose_add_response = True
        p = Project(API(fake), apply=True)
        rows = [{"node_id": "i", "fields": {"Status": "BACKLOG"}}]
        self.assertEqual(p.sync(fake.board, rows, fake.fields)[0]["code"], "api_unavailable")
        self.assertEqual(p.sync(fake.board, rows, fake.fields), [])
        self.assertEqual(len(fake.items), 1)

    def test_partial_failure_keeps_success_and_retries_safely(self):
        fake = FakeGitHub()
        fake.fail_content = "b"
        p = Project(API(fake), apply=True)
        rows = [{"node_id": n, "fields": {}} for n in ["a", "b", "c"]]
        self.assertEqual(len(p.sync(fake.board, rows, fake.fields)), 1)
        self.assertEqual(len(fake.items), 1)
        fake.fail_content = None
        self.assertEqual(p.sync(fake.board, rows, fake.fields), [])
        self.assertEqual(len(fake.items), 3)

    def test_rate_limit_read_retry_bounded(self):
        attempts, sleeps = [], []
        def call(*a):
            attempts.append(1)
            if len(attempts) < 3:
                raise Blocked("rate_limited", "query", "Quota", 1)
            return {"data": {"ok": True}}
        self.assertTrue(API(call, sleeps.append).gql("query")["ok"])
        self.assertEqual(sleeps, [1, 1])

    def test_mutation_rate_limit_never_blind_retry(self):
        attempts = []
        def call(*a):
            attempts.append(1)
            raise Blocked("rate_limited", "mutation", "Quota")
        with self.assertRaises(Blocked):
            API(call).gql("mutation", mutation=True)
        self.assertEqual(len(attempts), 1)

    def test_rest_and_graphql_pagination(self):
        def call(endpoint, payload):
            if endpoint != "graphql":
                return list(range(100)) if endpoint.endswith("&page=1") else [100]
            more = "after" not in payload["variables"]
            return {"data": {"conn": connection([1] if more else [2], more, "cursor")}}
        api = API(call)
        self.assertEqual(len(api.rest_pages("/test")), 101)
        self.assertEqual(api.connection("query", {}, lambda d: d["conn"]), [1, 2])

    def test_repeated_cursor_rejected(self):
        api = API(lambda *a: {"data": {"conn": connection([], True, "same")}})
        with self.assertRaises(Blocked):
            api.connection("query", {}, lambda d: d["conn"])

    def test_field_creation_repeat_safe(self):
        fake = FakeGitHub()
        p = Project(API(fake), apply=True)
        p.ensure_fields(fake.board)
        writes = len(fake.writes)
        p.ensure_fields(fake.board)
        self.assertEqual(len(fake.writes), writes)

    def test_incompatible_status_is_blocked_not_replaced(self):
        fake = FakeGitHub()
        fake.fields[0]["options"] = []
        p = Project(API(fake))
        _, blocked = p.ensure_fields(fake.board)
        self.assertEqual(blocked[0]["field"], "Status")
        self.assertEqual(fake.writes, [])


class GateTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / "orchestration/sparks.json").read_text())
        self.task = json.loads((Path(__file__).parent / "task.json").read_text())
        self.issue = {"number": 134, "node_id": "I134", "html_url": self.task["issue"]["url"],
                      "body": "```json\n" + json.dumps(self.task) + "\n```", "assignees": [{"login": "owner"}],
                      "comments_data": [], "native_blockers": []}
        self.pr = {"number": 135, "node_id": "P135", "head": {"ref": self.task["branch"]["name"], "sha": "a" * 40},
                   "base": {"ref": "main"}, "draft": True, "html_url": "https://github.com/example/pull/135",
                   "updated_at": "2026-10-01T00:00:00Z", "files": [{"filename": "orchestration/project_sync/api.py"}],
                   "checks": [{"id": 1, "name": "tests", "head_sha": "a" * 40, "status": "completed", "conclusion": "success"}]}
        self.snapshot = {"as_of": "2026-10-31T00:00:00Z", "main_commit": "b" * 40,
                         "issues": [self.issue], "pull_requests": [self.pr], "branches": [{"name": self.task["branch"]["name"]}]}

    def run_report(self):
        return reconcile(self.snapshot, self.catalog, datetime(2026, 10, 31, tzinfo=timezone.utc))

    def test_pr_associated_exact_branch_and_stale_visible(self):
        r = self.run_report()
        self.assertEqual(r["records"][0]["pr"], 135)
        self.assertEqual(r["records"][0]["fields"]["Status"], "DRAFT_PR")
        self.assertEqual(r["findings"][0]["code"], "stale_pr")
        self.assertNotIn("COMPLETE", str(r))

    def test_unresolved_dependency_prevents_claim(self):
        self.issue["native_blockers"] = [{"number": 108, "state": "open"}]
        r = self.run_report()["records"][0]
        self.assertEqual(r["fields"]["Status"], "BLOCKED")
        self.assertEqual(r["blocked_by"], [108])

    def test_head_changes_invalidate_check(self):
        self.assertEqual(check_state(self.pr), "head_passed_not_integrated")
        self.pr["head"]["sha"] = "c" * 40
        self.assertEqual(check_state(self.pr), "unverified")

    def test_ci_failure_visible_even_for_draft(self):
        self.pr["checks"][0]["conclusion"] = "failure"
        self.assertEqual(self.run_report()["records"][0]["fields"]["Validation"], "failed")

    def test_latest_failed_attempt_supersedes_older_success(self):
        self.pr["checks"].append({**self.pr["checks"][0], "id": 2, "conclusion": "failure"})
        self.assertEqual(check_state(self.pr), "failed")

    def test_missing_or_skipped_evidence_unverified(self):
        self.pr["checks"] = []
        self.assertEqual(check_state(self.pr), "unverified")
        self.pr["checks"] = [{"id": 1, "name": "tests", "head_sha": "a" * 40, "status": "completed", "conclusion": "skipped"}]
        self.assertEqual(check_state(self.pr), "unverified")

    def test_globs_and_subtrees(self):
        for a, b in [("orchestration/**", "orchestration/project_sync/api.py"),
                     ("research/*/entity.json", "research/CRWV/**"), ("research/[AB]*/x", "research/AAOI/x")]:
            self.assertTrue(overlap(a, b))
        self.assertFalse(overlap("runtime/**", "orchestration/**"))

    def test_actual_pr_files_collide_without_declared_claim(self):
        self.snapshot["pull_requests"].append({**self.pr, "number": 9, "node_id": "P9", "head": {"ref": "other", "sha": "c" * 40}})
        r = self.run_report()
        self.assertEqual(r["records"][0]["fields"]["Status"], "BLOCKED")
        self.assertTrue(any(f["code"] == "actual_pr_scope_collision" for f in r["findings"]))

    def test_declared_subtree_claim_collision(self):
        task = copy.deepcopy(self.task)
        task.update(task_id="B00-200", issue={"number": 200, "url": "https://github.com/whiterosecoffee/_BASKET/issues/200"},
                    branch={"name": "work/200-other", "base": "main"}, write_paths=["orchestration/**"])
        issue = {**self.issue, "number": 200, "node_id": "I200", "html_url": task["issue"]["url"],
                 "body": "```json\n" + json.dumps(task) + "\n```"}
        self.snapshot["issues"].append(issue)
        self.snapshot["branches"].append({"name": "work/200-other"})
        r = self.run_report()
        self.assertTrue(any(f["code"] == "declared_scope_collision" for f in r["findings"]))
        self.assertEqual(r["records"][0]["fields"]["Status"], "BLOCKED")

    def test_renamed_source_path_scope_breach(self):
        self.pr["files"][0]["previous_filename"] = "runtime/foreign.py"
        self.assertIn("changed_file_outside_scope", self.run_report()["records"][0]["errors"])

    def test_ambiguous_claim_never_selects_arbitrary_owner(self):
        self.issue["comments_data"] = [{"body": "```json\n" + json.dumps({**self.task, "objective": "A different objective for ambiguity"}) + "\n```"}]
        self.assertIn("ambiguous_task_claim", self.run_report()["records"][0]["errors"])

    def test_reconcile_same_snapshot_is_identical(self):
        self.assertEqual(self.run_report(), self.run_report())

    def test_invalid_claim_not_registered(self):
        task = {**self.task, "task_id": "B00-999"}
        self.issue["body"] = "```json\n" + json.dumps(task) + "\n```"
        r = self.run_report()["records"][0]
        self.assertIn("task_identity_mismatch", r["errors"])
        self.assertEqual(r["fields"]["Status"], "BLOCKED")

    def test_unassigned_owner_blocked(self):
        self.issue["assignees"] = []
        self.assertIn("owner_missing", self.run_report()["records"][0]["errors"])

    def test_merge_requires_main_ci_and_acceptance(self):
        examples = ROOT / "orchestration/examples"
        task = json.loads((examples / "B05.task.json").read_text())
        resolution = json.loads((examples / "B05.resolution.json").read_text())
        evidence = json.loads((examples / "github-evidence-2026-10-16.json").read_text())
        self.assertNotEqual(resolution_gate(task, resolution, evidence, self.catalog)["status"], "COMPLETE")
        resolution["disposition"] = "integrated"
        resolution["pr"]["merged"] = True
        resolution["pr"]["draft"] = False
        resolution["blockers"] = []
        pr = next(p for p in evidence["pull_requests"] if p["number"] == resolution["pr"]["number"])
        pr["merged"] = True
        pr["draft"] = False
        self.assertNotEqual(resolution_gate(task, resolution, evidence, self.catalog)["status"], "COMPLETE")
        evidence["workflow_runs"].append({**evidence["workflow_runs"][0], "name": "Validate BASKET data",
                                         "id": 99999999999, "url": "https://github.com/whiterosecoffee/_BASKET/actions/runs/99999999999",
                                         "head_sha": evidence["main_commit"], "conclusion": "success"})
        self.assertNotEqual(resolution_gate(task, resolution, evidence, self.catalog)["status"], "COMPLETE")
        proof = {"main_sha": evidence["main_commit"], "merged_commit_sha": "a" * 40,
                 "ancestry_status": "ahead", "compare_url": "https://github.com/whiterosecoffee/_BASKET/compare/merge...main",
                 "required_workflows": ["Validate BASKET data"]}
        self.assertEqual(resolution_gate(task, resolution, evidence, self.catalog, proof)["status"], "COMPLETE")
        resolution["acceptance"][0]["result"] = "not_verified"
        self.assertNotEqual(resolution_gate(task, resolution, evidence, self.catalog, proof)["status"], "COMPLETE")


if __name__ == "__main__":
    unittest.main()
