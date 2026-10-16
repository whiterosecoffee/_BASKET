#!/usr/bin/env python3
"""B00-owned offline tests of worker task/report/source truth contracts.

Run from root: python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
Requires jsonschema>=4.23, same dependency as strict BASKET data validator.
"""
import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "worker_protocol", ROOT / "orchestration/worker_protocol.py")
wp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wp)


class WorkerProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = ROOT / "orchestration/examples"
        cls.task = wp.read(root / "B05.task.json")
        cls.report = wp.read(root / "B05.resolution.json")
        cls.evidence = wp.read(root / "github-evidence-2026-10-16.json")
        cls.catalog = wp.read(ROOT / "orchestration/sparks.json")

    def evaluate(self, task=None, report=None, evidence=None):
        return wp.evidence_check(task or self.task, report or self.report,
                                 evidence or self.evidence, self.catalog)

    def test_schema_valid_samples(self):
        for data, name in ((self.task, "task"),
                           (self.report, "resolution"),
                           (self.evidence, "evidence")):
            self.assertEqual(wp.validate_schema(data, name), [])

    def test_verified_component_not_integrated(self):
        out = self.evaluate()
        self.assertEqual(out["errors"], [])
        self.assertEqual(out["mandatory_acceptance_unresolved"], [])
        self.assertEqual(out["checks_passed_on_pr_head"], 1)
        self.assertEqual(out["b00_evidence_phase"],
                         "component_verified_review_pending")
        self.assertFalse(out["merge_authorized"])

    def test_pr_changed_path_cross_owner_rejected(self):
        report = copy.deepcopy(self.report)
        evidence = copy.deepcopy(self.evidence)
        report["changed_paths"].append("schemas/relationships.v1.json")
        pr = next(p for p in evidence["pull_requests"] if p["number"] == 10)
        pr["changed_paths"].append("schemas/relationships.v1.json")
        out = self.evaluate(report=report, evidence=evidence)
        self.assertTrue(any("outside task claim" in x for x in out["errors"]))
        self.assertTrue(any("another spark" in x for x in out["errors"]))

    def test_pr_path_tampering_rejected(self):
        report = copy.deepcopy(self.report)
        report["changed_paths"] = []
        out = self.evaluate(report=report)
        self.assertTrue(any("differ from GitHub PR" in x for x in out["errors"]))

    def test_wrong_ci_commit_rejected(self):
        evidence = copy.deepcopy(self.evidence)
        run = next(r for r in evidence["workflow_runs"] if r["id"] == 38956838273)
        run["head_sha"] = "0" * 40
        out = self.evaluate(evidence=evidence)
        self.assertTrue(any("workflow success not verified" in x for x in out["errors"]))

    def test_missing_mandatory_acceptance_rejected(self):
        report = copy.deepcopy(self.report)
        report["acceptance"][0]["result"] = "not_verified"
        out = self.evaluate(report=report)
        self.assertTrue(any("mandatory acceptance unresolved" in x for x in out["errors"]))

    def test_report_cannot_fake_integrated(self):
        report = copy.deepcopy(self.report)
        report["disposition"] = "integrated"
        out = self.evaluate(report=report)
        self.assertTrue(any("requires PR merged" in x for x in out["errors"]))

    def test_zero_evidence_pass_rejected(self):
        report = copy.deepcopy(self.report)
        report["checks"][0]["evidence_urls"] = []
        out = self.evaluate(report=report)
        self.assertTrue(any("pass without evidence URL" in x for x in out["errors"]))

    def test_unowned_task_path_rejected(self):
        task = copy.deepcopy(self.task)
        task["write_paths"].append("schemas/worker-task.v1.json")
        out = self.evaluate(task=task)
        self.assertTrue(any("outside spark ownership" in x for x in out["errors"]))

    def test_glob_matching_does_not_cross_one_directory(self):
        self.assertTrue(wp.permitted("tickers/SFTBY/relationships.json",
                                     ["tickers/*/relationships.json"]))
        self.assertFalse(wp.permitted("tickers/SFTBY/extra/relationships.json",
                                      ["tickers/*/relationships.json"]))
        self.assertTrue(wp.permitted(
            "research/graph/SFTBY/relationships-context-2026-10-16.json",
            ["research/graph/**"]))


if __name__ == "__main__":
    unittest.main()
