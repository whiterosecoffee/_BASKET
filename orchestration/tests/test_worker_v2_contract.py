"""Negative gates for the existing B00 worker evaluator; no network calls."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("worker_protocol", ROOT / "orchestration/worker_protocol.py")
wp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wp)

class WorkerV2ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / "orchestration/examples"
        cls.task = wp.read(base / "B05.task.json")
        cls.report = wp.read(base / "B05.resolution.json")
        cls.evidence = wp.read(base / "github-evidence-2026-10-16.json")
        cls.catalog = wp.read(ROOT / "orchestration/sparks.json")

    def check(self, task=None, report=None, evidence=None):
        return wp.evidence_check(task or self.task, report or self.report,
                                 evidence or self.evidence, self.catalog)

    def test_duplicate_resolution_acceptance_fails(self):
        report = copy.deepcopy(self.report)
        report["acceptance"].append(copy.deepcopy(report["acceptance"][0]))
        outcome = self.check(report=report)
        self.assertEqual(outcome["b00_evidence_phase"], "evidence_invalid")
        self.assertTrue(any("duplicate acceptance" in x for x in outcome["errors"]))

    def test_unknown_acceptance_fails(self):
        report = copy.deepcopy(self.report)
        report["acceptance"].append({"id": "A999", "result": "pass",
                                     "evidence_urls": ["https://example.org/proof"]})
        self.assertTrue(any("unknown acceptance" in x for x in
                            self.check(report=report)["errors"]))

    def test_no_pr_head_ci_is_not_component_verified(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["workflow_runs"] = []
        outcome = self.check(evidence=evidence)
        self.assertEqual(outcome["b00_evidence_phase"], "evidence_invalid")
        self.assertEqual(outcome["checks_passed_on_pr_head"], 0)

    def test_missing_issue_is_invalid(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["issues"] = [x for x in evidence["issues"]
                              if x["number"] != self.task["issue"]["number"]]
        self.assertTrue(any("issue not verified" in x for x in
                            self.check(evidence=evidence)["errors"]))

    def test_report_task_branch_mismatch_is_invalid(self):
        report = copy.deepcopy(self.report)
        report["branch"]["name"] = "work/999-not-this-conversation"
        self.assertTrue(any("task/resolution mismatch: branch" in x
                            for x in self.check(report=report)["errors"]))

    def test_missing_mandatory_criterion_cannot_be_verified(self):
        report = copy.deepcopy(self.report)
        report["acceptance"] = []
        out = self.check(report=report)
        self.assertTrue(out["mandatory_acceptance_unresolved"])
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")


    def test_merged_pr_without_main_ci_remains_unverified(self):
        """Merge evidence cannot substitute for successful main-head CI."""
        report = copy.deepcopy(self.report)
        evidence = copy.deepcopy(self.evidence)
        report["disposition"] = "integrated"
        report["pr"]["state"] = "closed"
        report["pr"]["merged"] = True
        pr = next(p for p in evidence["pull_requests"] if p["number"] == 10)
        pr["state"] = "closed"
        pr["merged"] = True
        out = self.check(report=report, evidence=evidence)
        self.assertEqual(out["errors"], [])
        self.assertEqual(out["b00_evidence_phase"], "integrated_main_ci_unverified")
        self.assertFalse(out["merge_authorized"])

    def test_main_ci_must_match_current_main_commit(self):
        """Only an independent success at the currently observed main SHA qualifies."""
        report = copy.deepcopy(self.report)
        evidence = copy.deepcopy(self.evidence)
        report["disposition"] = "integrated"
        report["pr"]["state"] = "closed"
        report["pr"]["merged"] = True
        pr = next(p for p in evidence["pull_requests"] if p["number"] == 10)
        pr["state"] = "closed"
        pr["merged"] = True
        success = copy.deepcopy(evidence["workflow_runs"][0])
        success["id"] = 999999
        success["url"] = "https://github.com/whiterosecoffee/_BASKET/actions/runs/999999"
        success["head_sha"] = evidence["main_commit"]
        evidence["workflow_runs"].append(success)
        out = self.check(report=report, evidence=evidence)
        self.assertEqual(out["errors"], [])
        self.assertEqual(out["b00_evidence_phase"], "integrated_main_ci_verified")
        self.assertFalse(out["merge_authorized"])

    def test_reported_pass_with_failed_workflow_fails_closed(self):
        """A worker cannot promote a failed workflow using a positive self-report."""
        evidence = copy.deepcopy(self.evidence)
        run = next(r for r in evidence["workflow_runs"] if r["id"] == 38956838273)
        run["conclusion"] = "failure"
        out = self.check(evidence=evidence)
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")
        self.assertTrue(any("workflow success not verified" in e for e in out["errors"]))

if __name__ == "__main__":
    unittest.main()
