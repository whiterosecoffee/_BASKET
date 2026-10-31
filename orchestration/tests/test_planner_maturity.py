"""Regression tests for queue decisions, resource gates and GitHub progress recovery."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


planner = module("mature_planner", "orchestration/planner.py")
tracker = module("mature_progress", "orchestration/progress_tracker.py")
provider = module("mature_provider", "orchestration/github_snapshot.py")
snapshot_cases = module("snapshot_cases", "orchestration/tests/test_github_snapshot.py")


class PlanningMaturityTests(unittest.TestCase):
    def setUp(self):
        self.q = planner.load(ROOT / "orchestration/planner/queue.json")
        self.lib = planner.load(ROOT / "orchestration/planner/worker-library.json")
        self.reg = planner.load(ROOT / "orchestration/sparks.json")
        self.ev = planner.load(ROOT / "orchestration/examples/github-evidence-2026-10-16.json")
        self.task = next(t for t in self.q["tasks"] if t["id"] == "T-006")

    def plan(self, **kwargs):
        return planner.run_plan(self.q, self.lib, self.reg, self.ev, ["T-004", "T-005"], **kwargs)

    def entry(self, tid="T-001", **kwargs):
        return next(t for t in self.plan(**kwargs)["ordered_tasks"] if t["id"] == tid)

    def estimate(self, maximum=100):
        self.task["token_estimate"] = {"min": 50, "max": maximum,
                                       "confidence": "low", "basis": "Controlled test assumption"}

    def test_newer_failure_overrides_old_success_on_same_head(self):
        old = next(r for r in self.ev["workflow_runs"] if r["conclusion"] == "success")
        new = dict(old, id=old["id"] + 100, url=old["url"] + "-new", conclusion="failure")
        self.ev["workflow_runs"].insert(0, new)
        row = self.entry()
        self.assertFalse(row["branch_ci_pass"])
        self.assertEqual(row["checks"][0]["result"], "FAIL")
        self.assertEqual(row["checks"][0]["run_id"], new["id"])

    def test_pending_rerun_invalidates_historical_success(self):
        old = next(r for r in self.ev["workflow_runs"] if r["conclusion"] == "success")
        self.ev["workflow_runs"].append(dict(old, id=old["id"] + 1, url=old["url"] + "-new", conclusion="pending"))
        self.assertEqual(self.entry()["checks"][0]["result"], "PENDING")
        self.assertFalse(self.entry()["branch_ci_pass"])

    def test_every_required_workflow_must_pass(self):
        self.q["tasks"][0]["required_workflows"] = ["Validate BASKET data", "Independent domain acceptance"]
        row = self.entry()
        self.assertFalse(row["branch_ci_pass"])
        self.assertEqual([x["result"] for x in row["checks"]], ["PASS", "NOT_RUN"])

    def test_skipped_workflow_is_not_success(self):
        self.ev["workflow_runs"][0]["conclusion"] = "skipped"
        self.assertEqual(self.entry()["checks"][0]["result"], "UNKNOWN")
        self.assertFalse(self.entry()["branch_ci_pass"])

    def test_head_change_invalidates_checks(self):
        next(p for p in self.ev["pull_requests"] if p["number"] == 10)["head_sha"] = "0" * 40
        self.assertEqual(self.entry()["checks"][0]["result"], "NOT_RUN")

    def test_declared_budget_prevents_over_budget_dispatch(self):
        self.estimate(200)
        out = self.plan(token_budget=100)
        self.assertIsNone(out["next_new_worker"])
        row = next(t for t in out["ordered_tasks"] if t["id"] == "T-006")
        self.assertEqual(row["resource_gate"], "additional_resources_required")
        self.assertFalse(row["ready_for_action"])

    def test_missing_estimate_is_not_fabricated_to_fit_budget(self):
        self.assertEqual(self.entry("T-006", token_budget=100)["resource_gate"], "estimate_required")
        self.assertIsNone(self.plan(token_budget=100)["next_new_worker"])

    def test_fit_uses_conservative_maximum_and_reports_unknown_quota(self):
        self.estimate(100)
        out = self.plan(token_budget=100)
        self.assertEqual(out["next_new_worker"], "T-006")
        self.assertIsNone(out["actual_remaining_quota"])
        self.assertFalse(out["resource_estimates_are_measurements"])

    def test_reuse_benefit_is_qualified_estimate_not_measured_cost(self):
        self.estimate(100)
        self.task["reuse_estimate"] = {"tokens_saved_per_use": 30, "expected_uses": 10,
                                        "basis": "Controlled forecast, not measurements"}
        self.assertEqual(self.entry("T-006")["estimated_net_token_reduction"], 200)
        self.assertIsNone(self.entry()["estimated_net_token_reduction"])

    def test_invalid_estimate_ranges_or_boolean_values_rejected(self):
        self.estimate(40)
        with self.assertRaisesRegex(ValueError, "invalid token estimate"):
            self.plan()
        self.estimate(100)
        self.task["token_estimate"]["min"] = True
        with self.assertRaises(ValueError):
            self.plan()

    def test_negative_or_boolean_budget_rejected(self):
        for value in (-1, True):
            with self.assertRaises(ValueError):
                self.plan(token_budget=value)

    def test_new_fields_validate_and_old_queue_still_validates(self):
        validator = Draft202012Validator(planner.load(ROOT / "schemas/task-queue.v1.json"))
        validator.validate(self.q)
        self.estimate()
        validator.validate(self.q)
        self.task["required_workflows"] = []
        self.assertTrue(list(validator.iter_errors(self.q)))

    def test_draft_pr_is_never_integration_ready(self):
        report = tracker.build_report(self.q, self.lib, self.reg, self.ev)
        row = next(t for t in report["ordered_tasks"] if t["id"] == "T-001")
        self.assertTrue(row["branch_ci_pass"])
        self.assertFalse(row["integration_review_eligible"])
        self.assertFalse(row["integration_ready"])
        self.assertEqual(row["acceptance"], "NOT_VERIFIED")

    def test_report_contract_rejects_fabricated_completion(self):
        report = tracker.build_report(self.q, self.lib, self.reg, self.ev)
        report["ordered_tasks"][0]["integration_ready"] = True
        with self.assertRaises(ValueError):
            tracker.validate_contract(report, "progress-report.v1.json")

    def test_input_contract_rejects_unsupported_evidence(self):
        self.ev["actual_quota"] = 1000000
        with self.assertRaises(ValueError):
            tracker.build_report(self.q, self.lib, self.reg, self.ev)

    def test_hidden_history_and_code_are_not_current_progress(self):
        issue = {"number": 136, "url": "https://example.invalid/issues/136", "body":
                 "- [ ] **S01 — current**\n<details>\n- [x] S01 — old\n<details>\n- [x] old\n</details>\n</details>\n```md\n- [x] example\n```\n- [x] S02 — recorded"}
        rows = tracker.checklist(issue)
        self.assertEqual([i["id"] for i in rows], ["136:S01", "136:S02"])
        self.assertEqual([i["checked"] for i in rows], [False, True])
        self.assertTrue(all(i["acceptance"] == "NOT_VERIFIED" for i in rows))

    def test_duplicate_capture_is_idempotent_and_correction_preserves_id(self):
        issue = {"number": 136, "url": "https://example.invalid/issues/136", "body": "- [ ] S01 — current\n- [ ] S01 — current"}
        rows = tracker.checklist(issue)
        self.assertEqual(len(rows), 1)
        issue["body"] = "- [x] S01 — corrected"
        revised = tracker.checklist(issue)[0]
        self.assertEqual(rows[0]["id"], revised["id"])
        self.assertTrue(revised["checked"])

    def test_conflicting_identity_is_visible_not_silently_overwritten(self):
        self.ev["issues"][0]["body"] = "- [x] S01 — old\n- [ ] S01 — new"
        report = tracker.build_report(self.q, self.lib, self.reg, self.ev)
        self.assertEqual(report["errors"][0]["code"], "CHECKLIST_CONFLICT")

    def test_new_issue_outside_legacy_queue_is_not_lost(self):
        self.ev["issues"].append({"number": 136, "url": "https://example.invalid/136",
                                  "state": "open", "title": "Orchestration", "body": "- [ ] S01 — task"})
        report = tracker.build_report(self.q, self.lib, self.reg, self.ev, focus_issue=136)
        self.assertIn(136, [i["number"] for i in report["unplanned_open_issues"]])
        self.assertEqual(report["checklist_counts"], {"checked": 0, "open": 1})
        self.assertFalse(report["checklist_completion_is_verified_acceptance"])

    def test_resume_from_same_evidence_is_deterministic_and_read_only(self):
        original = copy.deepcopy(self.ev)
        a = tracker.build_report(self.q, self.lib, self.reg, self.ev)
        b = tracker.build_report(self.q, self.lib, self.reg, self.ev)
        self.assertEqual(a, b)
        self.assertEqual(original, self.ev)
        self.assertEqual(a["side_effects_executed"], [])

    def test_missing_focus_issue_is_not_an_empty_success(self):
        report = tracker.build_report(self.q, self.lib, self.reg, self.ev, focus_issue=999)
        self.assertEqual(report["errors"][0]["code"], "ISSUE_NOT_OBSERVED")

    def test_workflow_pagination_does_not_silently_truncate(self):
        calls = []
        def fetch(path):
            calls.append(path)
            return {"workflow_runs": [{"id": 1}] * 100 if path.endswith("page=1") else [{"id": 2}]}
        self.assertEqual(len(provider.workflow_pages(fetch, "/runs")), 101)
        self.assertEqual(len(calls), 2)
        with self.assertRaises(provider.EvidenceUnavailable):
            provider.workflow_pages(lambda _: {"workflow_runs": [{}] * 100}, "/runs", max_pages=2)

    def test_discovery_paginates_and_excludes_prs_from_issues(self):
        base = snapshot_cases.GitHubSnapshotTests().fake
        def fetch(path):
            if "/issues?state=open" in path:
                return [{"number": 999}, {"number": 888, "pull_request": {}}]
            if "/pulls?state=open" in path:
                return [{"number": 888}]
            return base(path)
        evidence = provider.collect(self.q, fetch, discover_open=True)
        self.assertIn(999, [i["number"] for i in evidence["issues"]])
        self.assertNotIn(888, [i["number"] for i in evidence["issues"]])
        self.assertIn(888, [p["number"] for p in evidence["pull_requests"]])
        Draft202012Validator(planner.load(ROOT / "schemas/worker-evidence.v1.json")).validate(evidence)

    def test_api_partial_failure_does_not_produce_success_snapshot(self):
        def unavailable(path):
            raise provider.EvidenceUnavailable("rate limited; retry after source recovery")
        with self.assertRaises(provider.EvidenceUnavailable):
            provider.collect(self.q, unavailable)

    def test_rate_limit_preserves_retry_hint_without_silent_retry(self):
        error = HTTPError("https://api.github.com/example", 429, "rate limited",
                          {"Retry-After": "30"}, None)
        with patch.object(provider, "urlopen", side_effect=error) as call:
            with self.assertRaises(provider.EvidenceUnavailable) as raised:
                provider.fetch_json("/repos/whiterosecoffee/_BASKET/branches/main")
        self.assertEqual(raised.exception.code, "RATE_LIMITED")
        self.assertEqual(raised.exception.retry_after, "30")
        self.assertEqual(call.call_count, 1)

    def test_cli_reports_structured_error_for_unreadable_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text("{")
            out = subprocess.run([sys.executable, str(ROOT / "orchestration/progress_tracker.py"),
                                  "--evidence", str(path)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 1)
        self.assertEqual(json.loads(out.stdout)["code"], "PROGRESS_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
