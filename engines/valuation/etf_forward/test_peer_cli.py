import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIXTURE=HERE/'smh_soxx.synthetic.json'
SCRIPT=HERE/'compare_funds.py'
class TestCli(unittest.TestCase):
 def test_json_cli(self):
  result=subprocess.run([sys.executable,str(SCRIPT),str(FIXTURE)],capture_output=True,text=True,check=True)
  obj=json.loads(result.stdout)
  self.assertEqual(obj['schema'],'basket.etf_peer_comparison_output@1')
  self.assertEqual(obj['data_kind'],'synthetic_test')
  self.assertIn('2028',obj['years'])
 def test_markdown_cli(self):
  result=subprocess.run([sys.executable,str(SCRIPT),str(FIXTURE),'--format','markdown'],capture_output=True,text=True,check=True)
  self.assertIn('SYNTHETIC TEST DATA',result.stdout)
  self.assertIn('No risk-adjusted winner established',result.stdout)
if __name__=='__main__': unittest.main()
