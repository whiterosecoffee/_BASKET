"""B00 regression against B01 #44 adversarial findings, excluding B01-owned files.

CI must run these. A historical GitHub fixture is NOT current integration truth.
"""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

planner = load_module("b00_planner", "orchestration/planner.py")
protocol = load_module("b00_protocol", "orchestration/worker_protocol.py")
attempts = load_module("b00_attempts", "orchestration/validate_worker_attempts.py")


class FailClosedQC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = planner.load(ROOT / "orchestration/planner/queue.json")
        cls.lib = planner.load(ROOT / "orchestration/planner/worker-library.json")
        cls.reg = planner.load(ROOT / "orchestration/sparks.json")
        cls.ev = planner.load(ROOT / "orchestration/examples/github-evidence-2026-10-16.json")
        cls.task = planner.load(ROOT / "orchestration/examples/B05.task.json")
        cls.report = planner.load(ROOT / "orchestration/examples/B05.resolution.json")
        cls.ledger = planner.load(ROOT / "orchestration/planner/attempts/T-001.json")
        cls.scopes = planner.load(ROOT / "orchestration/planner/worker-scopes.json")

    def test_valid_historical_component_preserves_evidence_phase(self):
        out = protocol.evidence_check(
            self.task, self.report, self.ev, self.reg)
        self.assertEqual(out["errors"], [])
        self.assertEqual(out["b00_evidence_phase"],
                         "component_verified_review_pending")

    def test_missing_confirmed_workflow_is_error_not_warning(self):
        report = copy.deepcopy(self.report)
        report["checks"] = []
        out = protocol.evidence_check(self.task, report, self.ev, self.reg)
        self.assertTrue(out["errors"])
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")

    def test_owner_breach_never_returns_verified_phase(self):
        report = copy.deepcopy(self.report)
        ev = copy.deepcopy(self.ev)
        path = "schemas/relationships.v1.json"
        report["changed_paths"].append(path)
        next(p for p in ev["pull_requests"] if p["number"] == 10
             )["changed_paths"].append(path)
        out = protocol.evidence_check(self.task, report, ev, self.reg)
        self.assertTrue(out["errors"])
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")

    def test_stale_ci_never_returns_verified_phase(self):
        report = copy.deepcopy(self.report)
        ev = copy.deepcopy(self.ev)
        report["pr"]["head_sha"] = "0" * 40
        next(p for p in ev["pull_requests"] if p["number"] == 10
             )["head_sha"] = "0" * 40
        out = protocol.evidence_check(self.task, report, ev, self.reg)
        self.assertTrue(out["errors"])
        self.assertEqual(out["b00_evidence_phase"], "evidence_invalid")

    def test_self_retry_rejected_without_lesson_dependency(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["attempts"][1]["retry_of"] = ledger["attempts"][1]["attempt_id"]
        ledger["lessons"] = []
        self.assertTrue(attempts.evaluate(ledger, self.scopes))

    def test_active_new_worker_never_redispatched(self):
        ev = copy.deepcopy(self.ev)
        # Historical fixture has T-006 ready, but an ACTIVE T-006
        # must never be returned as the next new worker.
        out = planner.run_plan(
            self.queue, self.lib, self.reg, ev, ("T-006",))
        self.assertNotEqual(out["next_new_worker"], "T-006")

    def test_all_active_slots_block_dispatch(self):
        out = planner.run_plan(
            self.queue, self.lib, self.reg, self.ev,
            ("T-004", "T-005", "T-006"))
        self.assertEqual(out["worker_slots_remaining"], 0)
        self.assertIsNone(out["next_new_worker"])


if __name__ == "__main__":
    unittest.main()
