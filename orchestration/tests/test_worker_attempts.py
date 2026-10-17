import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("attempt_validator",ROOT/"orchestration/validate_worker_attempts.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AttemptQC(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=m.read(ROOT/"orchestration/planner/attempts/T-001.json")
  cls.s=m.read(ROOT/"orchestration/planner/worker-scopes.json")
 def qc(self,a):return m.evaluate(a,self.s)
 def test_resolution_replay(self):self.assertEqual(self.qc(self.a),[])
 def test_unproved_pass(self):
  a=copy.deepcopy(self.a);a["attempts"][1]["evidence"]=[]
  self.assertTrue(self.qc(a))
 def test_false_efficiency(self):
  a=copy.deepcopy(self.a);a["evaluation"]["first_pass_rate"]=1
  self.assertTrue(self.qc(a))
 def test_unsafe_training_adoption(self):
  a=copy.deepcopy(self.a);a["attempts"][1]["state"]="failed";a["attempts"][1]["resolution"]="failed again"
  self.assertTrue(self.qc(a))
 def test_unmatched_step(self):
  a=copy.deepcopy(self.a);a["attempts"][0]["step_id"]="T-999-S1"
  self.assertTrue(self.qc(a))
 def test_invalid_retry(self):
  a=copy.deepcopy(self.a);a["attempts"][1]["retry_of"]="nonexistent"
  self.assertTrue(self.qc(a))
 def test_missing_timing_must_not_be_inferred(self):
  a=copy.deepcopy(self.a);a["evaluation"]["measured_time_seconds"]=60
  self.assertTrue(self.qc(a))
if __name__=="__main__":unittest.main()
