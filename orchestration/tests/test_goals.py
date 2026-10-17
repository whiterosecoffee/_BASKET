import copy
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("goal_validator",ROOT/"orchestration/validate_goals.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class GoalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=m.load("orchestration/planner/goals.json")
  cls.q=m.load("orchestration/planner/queue.json")
 def check(self,g):return m.validate(g,self.q)
 def test_complete_goal_milestone_task_mapping(self):self.assertEqual(self.check(self.g),[])
 def test_missing_task_fails(self):
  g=copy.deepcopy(self.g);g["milestones"][-1]["task_ids"].pop()
  self.assertTrue(any("unmapped" in x for x in self.check(g)))
 def test_unknown_task_fails(self):
  g=copy.deepcopy(self.g);g["milestones"][-1]["task_ids"].append("T-999")
  self.assertTrue(any("unknown queue task" in x for x in self.check(g)))
 def test_duplicate_task_owner_fails(self):
  g=copy.deepcopy(self.g);g["milestones"][0]["task_ids"].append("T-009")
  self.assertTrue(any("multiple" in x for x in self.check(g)))
 def test_milestone_cycle_fails(self):
  g=copy.deepcopy(self.g);g["milestones"][0]["depends_on"].append("M-005")
  self.assertTrue(any("cycle" in x for x in self.check(g)))
 def test_unauthorized_concurrency_policy_fails(self):
  g=copy.deepcopy(self.g);g["execution_policy"]["active_code_writers_limit"]=5
  self.assertTrue(any("capacity" in x for x in self.check(g)))
if __name__=="__main__":unittest.main()
