import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("scope_validator",ROOT/"orchestration/validate_worker_scopes.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class WorkerScopeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=m.read("orchestration/sparks.json");cls.q=m.read("orchestration/planner/queue.json");cls.l=m.read("orchestration/planner/worker-library.json");cls.s=m.read("orchestration/planner/worker-scopes.json")
 def check(self,s):return m.validate(self.r,self.q,self.l,s)
 def test_valid(self):self.assertEqual(self.check(self.s),[])
 def test_cross_domain(self):
  s=copy.deepcopy(self.s);s["scopes"][0]["exclusive_write_paths"]=[".github/workflows/**"]
  self.assertTrue(self.check(s))
 def test_recipe_corruption(self):
  s=copy.deepcopy(self.s);s["scopes"][0]["steps"][0]["capability"]="unknown"
  self.assertTrue(self.check(s))
 def test_mismatched_issue(self):
  s=copy.deepcopy(self.s);s["scopes"][0]["owner_issue"]=999
  self.assertTrue(self.check(s))
 def test_duplicate_scope(self):
  s=copy.deepcopy(self.s);s["scopes"].append(s["scopes"][0])
  self.assertTrue(self.check(s))
if __name__=="__main__":unittest.main()
