import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("basket_loop", ROOT / "orchestration/execution_loop.py")
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)

class ExecutionLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = loop.planner.load(ROOT/"orchestration/planner/queue.json")
        cls.lib = loop.planner.load(ROOT/"orchestration/planner/worker-library.json")
        cls.reg = loop.planner.load(ROOT/"orchestration/sparks.json")
        cls.ev = loop.planner.load(ROOT/"orchestration/examples/github-evidence-2026-10-16.json")

    def test_review_and_rework_not_merged(self):
        result = loop.reconcile(self.q,self.lib,self.reg,self.ev,["T-004","T-005"])
        by_id = {x["task_id"]:x for x in result["actions"]}
        self.assertEqual(by_id["T-001"]["qc_phase"],"approval_review")
        self.assertEqual(by_id["T-004"]["qc_phase"],"qc_rework")
        self.assertEqual(by_id["T-009"]["qc_phase"],"blocked")
        self.assertEqual(by_id["T-006"]["qc_phase"],"dispatch_ready")
        self.assertEqual(result["worker_slots_remaining"],1)
        self.assertEqual(result["side_effects_executed"],[])
        self.assertTrue(result["approval_required_for_merge"])

    def test_unknown_capacity_never_dispatches(self):
        r=loop.reconcile(self.q,self.lib,self.reg,self.ev)
        by={a["task_id"]:a for a in r["actions"]}
        self.assertEqual(by["T-006"]["qc_phase"],"capacity_unknown")
        self.assertIsNone(r["next_new_worker"])

    def test_dependencies_block_reuse(self):
        r=loop.reconcile(self.q,self.lib,self.reg,self.ev,[])
        by={a["task_id"]:a for a in r["actions"]}
        self.assertEqual(by["T-007"]["qc_phase"],"blocked")
        self.assertEqual(by["T-008"]["qc_phase"],"blocked")

    def test_decision_fails_closed_without_fresh_evidence(self):
        review = loop.reconcile(self.q, self.lib, self.reg, self.ev, [])
        out = loop.decide_next(review)
        self.assertFalse(out["fresh_evidence_confirmed"])
        self.assertEqual(out["side_effects_executed"], [])
        self.assertFalse(out["automatic_merge"])
        self.assertFalse(out["automatic_worker_launch"])
        self.assertTrue(all(d["decision_class"] != "automatic_safe"
                            for d in out["ordered_decisions"]))

    def test_decision_preserves_approval_gate(self):
        review = loop.reconcile(self.q, self.lib, self.reg, self.ev, [])
        out = loop.decide_next(review, fresh_evidence=True)
        by_id = {d["task_id"]: d for d in out["ordered_decisions"]}
        self.assertEqual(by_id["T-001"]["decision_class"],
                         "requires_authorization")
        self.assertEqual(by_id["T-004"]["decision_class"], "requires_owner")
        self.assertEqual(by_id["T-007"]["decision_class"], "requires_evidence")
        self.assertNotEqual(out["selected"]["task_id"], "T-001")

    def test_safe_local_checks_are_declared_not_executed(self):
        review = loop.reconcile(self.q, self.lib, self.reg, self.ev, [])
        out = loop.decide_next(review)
        self.assertGreaterEqual(len(out["safe_local_checks"]), 3)
        self.assertEqual(out["checks_executed"], [])
        self.assertEqual(out["side_effects_executed"], [])


    def test_safe_check_failure_does_not_stop_next_check(self):
        class Result:
            def __init__(self, code):
                self.returncode = code
                self.stdout = ""
                self.stderr = "failure" if code else ""
        calls = []
        def fake_runner(argv, **kwargs):
            calls.append((argv, kwargs))
            return Result(1 if len(calls) == 1 else 0)
        out = loop.run_safe_checks(
            runner=fake_runner, check_ids=["planner_structure", "worker_scope"])
        self.assertEqual([r["status"] for r in out["results"]],
                         ["failed", "passed"])
        self.assertFalse(out["all_passed"])
        self.assertEqual(len(calls), 2)
        self.assertEqual(out["mutating_actions_executed"], [])

    def test_safe_check_rejects_untrusted_commands(self):
        for ids in (["arbitrary_command"], ["worker_scope", "worker_scope"]):
            with self.assertRaises(ValueError):
                loop.run_safe_checks(check_ids=ids)

    def test_safe_check_timeout_is_recorded_and_next_check_runs(self):
        import subprocess
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""
        calls = []
        def fake_runner(argv, **kwargs):
            calls.append(argv)
            if len(calls) == 1:
                raise subprocess.TimeoutExpired(argv, 1)
            return Result()
        out = loop.run_safe_checks(
            runner=fake_runner, check_ids=["planner_structure", "worker_scope"],
            timeout_seconds=1)
        self.assertEqual([r["status"] for r in out["results"]],
                         ["timeout", "passed"])


if __name__ == "__main__": unittest.main()
