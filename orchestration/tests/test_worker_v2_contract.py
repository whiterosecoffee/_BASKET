"""Negative gates for the existing B00 worker evaluator; no network calls."""
import copy
import importlib.util
from pathlib import Path
import unittest
import subprocess
import sys

from orchestration.planner import ci_results, evidence_maps
from orchestration.agentic.manager import ci_green

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


class SharedCIEvidenceTests(unittest.TestCase):
    """One table exercises planner policy, controller and worker/main gates."""

    setUpClass = classmethod(WorkerV2ContractTests.setUpClass.__func__)
    check = WorkerV2ContractTests.check

    def run_fixture(self, *, run_id=90000000000, sha=None, name="Validate BASKET data",
                    conclusion="success", attempt=None):
        run = {"id": run_id,
               "url": "https://github.com/whiterosecoffee/_BASKET/actions/runs/" + str(run_id),
               "head_sha": sha or self.report["pr"]["head_sha"],
               "name": name, "conclusion": conclusion}
        if attempt is not None:
            run["run_attempt"] = attempt
        return run

    def matrix(self):
        good = self.run_fixture()
        failure = self.run_fixture(run_id=90000000001, conclusion="failure")
        latest_good = self.run_fixture(run_id=90000000002)
        cases = [
            ("exact_sha", [good], True),
            ("wrong_sha", [self.run_fixture(sha="f" * 40)], False),
            ("unrelated", [self.run_fixture(name="Unrelated smoke test")], False),
            ("missing", [], False),
            ("older_green_newer_failure", [good, failure], False),
            ("older_failure_newer_green", [failure, latest_good], True),
            ("unrelated_newer_failure", [good, self.run_fixture(
                run_id=90000000001, name="Unrelated smoke test", conclusion="failure")], True),
            ("wrong_sha_newer_failure", [good, self.run_fixture(
                run_id=90000000001, sha="f" * 40, conclusion="failure")], True),
            ("rerun_failure", [good, self.run_fixture(attempt=2, conclusion="failure")], False),
            ("rerun_success", [self.run_fixture(conclusion="failure"),
                               self.run_fixture(attempt=2)], True),
            ("conflicting_latest", [good, self.run_fixture(conclusion="failure")], False),
            ("identical_duplicate", [good, copy.deepcopy(good)], True),
            ("conflicting_old_attempt", [good, self.run_fixture(conclusion="failure"),
                                        self.run_fixture(attempt=2)], True),
        ]
        for state in ("pending", "cancelled", "skipped", "neutral", "timed_out", "action_required"):
            cases.append((state, [good, self.run_fixture(
                run_id=90000000001, conclusion=state)], False))
        return cases

    def test_shared_pr_head_matrix_is_order_invariant(self):
        sha = self.report["pr"]["head_sha"]
        for name, runs, expected in self.matrix():
            for ordered in (runs, list(reversed(runs))):
                with self.subTest(case=name, reversed=ordered != runs):
                    evidence = copy.deepcopy(self.evidence)
                    evidence["workflow_runs"] = ordered
                    report = copy.deepcopy(self.report)
                    # This check claims the aggregate workflow, not unrelated runs.
                    cited = [r for r in runs if r["name"] == "Validate BASKET data"] or runs
                    report["checks"][0]["evidence_urls"] = sorted({r["url"] for r in cited})
                    self.assertEqual(wp.validate_schema(evidence, "evidence"), [])
                    policy = ci_results(sha, evidence_maps(evidence)[2])
                    self.assertEqual(all(r["result"] == "PASS" for r in policy), expected)
                    self.assertEqual(ci_green(evidence, sha), expected)
                    out = self.check(report=report, evidence=evidence)
                    self.assertEqual(out["b00_evidence_phase"] ==
                                     "component_verified_review_pending", expected)
                    self.assertEqual(bool(out["checks_passed_on_pr_head"]), expected)

    def test_shared_current_main_matrix_is_order_invariant(self):
        for name, runs, expected in self.matrix():
            for ordered in (runs, list(reversed(runs))):
                with self.subTest(case=name, reversed=ordered != runs):
                    evidence = copy.deepcopy(self.evidence)
                    main_sha = evidence["main_commit"]
                    main_runs = copy.deepcopy(ordered)
                    for run in main_runs:
                        if run["head_sha"] == self.report["pr"]["head_sha"]:
                            run["head_sha"] = main_sha
                    evidence["workflow_runs"] += main_runs
                    report = copy.deepcopy(self.report)
                    report["disposition"] = "integrated"
                    report["pr"].update(state="closed", merged=True)
                    next(p for p in evidence["pull_requests"] if p["number"] == 10).update(
                        state="closed", merged=True)
                    self.assertEqual(wp.validate_schema(evidence, "evidence"), [])
                    self.assertEqual(ci_green(evidence, main_sha), expected)
                    out = self.check(report=report, evidence=evidence)
                    self.assertEqual(out["errors"], [])
                    self.assertEqual(out["b00_evidence_phase"] == "integrated_main_ci_verified", expected)
                    self.assertFalse(out["merge_authorized"])

    def test_auxiliary_workflow_can_pass_without_satisfying_required_gate(self):
        evidence = copy.deepcopy(self.evidence)
        auxiliary = self.run_fixture(name="NVDA resolver pilot acceptance")
        evidence["workflow_runs"].append(auxiliary)
        report = copy.deepcopy(self.report)
        check = copy.deepcopy(report["checks"][0])
        check.update(id="auxiliary-ci", evidence_urls=[auxiliary["url"]])
        report["checks"].append(check)
        out = self.check(report=report, evidence=evidence)
        self.assertEqual(out["errors"], [])
        self.assertEqual(out["b00_evidence_phase"], "component_verified_review_pending")
        self.assertEqual(out["checks_passed_on_pr_head"], 1)
        report["checks"] = [check]
        out = self.check(report=report, evidence=evidence)
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")
        self.assertEqual(out["checks_passed_on_pr_head"], 0)

    def test_mixed_workflow_citations_cannot_hide_auxiliary_failure(self):
        for state in ("success", "failure", "pending", "skipped", "neutral"):
            with self.subTest(state=state):
                evidence = copy.deepcopy(self.evidence)
                auxiliary = self.run_fixture(name="NVDA resolver pilot acceptance", conclusion=state)
                evidence["workflow_runs"].append(auxiliary)
                report = copy.deepcopy(self.report)
                report["checks"][0]["evidence_urls"].append(auxiliary["url"])
                out = self.check(report=report, evidence=evidence)
                self.assertEqual(out["b00_evidence_phase"] ==
                                 "component_verified_review_pending", state == "success")
                self.assertEqual(bool(out["errors"]), state != "success")

    def test_auxiliary_latest_failure_invalidates_auxiliary_pass(self):
        evidence = copy.deepcopy(self.evidence)
        good = self.run_fixture(name="NVDA resolver pilot acceptance")
        failed = self.run_fixture(name=good["name"], attempt=2, conclusion="failure")
        evidence["workflow_runs"] += [failed, good]
        report = copy.deepcopy(self.report)
        check = copy.deepcopy(report["checks"][0])
        check.update(id="auxiliary-ci", evidence_urls=[good["url"]])
        report["checks"].append(check)
        out = self.check(report=report, evidence=evidence)
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")
        self.assertTrue(any("auxiliary-ci" in error for error in out["errors"]))

    def test_old_success_citation_cannot_claim_new_success(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["workflow_runs"].append(self.run_fixture())
        out = self.check(evidence=evidence)
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")
        self.assertEqual(out["checks_passed_on_pr_head"], 0)

    def test_workflow_claim_without_pr_is_not_head_verified(self):
        report = copy.deepcopy(self.report)
        report["pr"] = None
        report["changed_paths"] = []
        out = self.check(report=report)
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")
        self.assertEqual(out["checks_passed_on_pr_head"], 0)

    def test_protocol_cli_works_outside_repository_cwd(self):
        args = [sys.executable, str(ROOT / "orchestration/worker_protocol.py")]
        for key, filename in (("task", "B05.task.json"), ("resolution", "B05.resolution.json"),
                              ("evidence", "github-evidence-2026-10-16.json")):
            args += ["--" + key, str(ROOT / "orchestration/examples" / filename)]
        out = subprocess.run(args, cwd=ROOT.parent, text=True, capture_output=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("component_verified_review_pending", out.stdout)

if __name__ == "__main__":
    unittest.main()
