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

if __name__ == "__main__": unittest.main()
