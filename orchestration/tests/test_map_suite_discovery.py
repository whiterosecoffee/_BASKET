"""B00 discovery bridge: existing worker-qc runs real _MAP suites, fail closed."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('map_prepare_sources',ROOT/'_MAP/prepare_sources.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)

class MapSuiteDiscovery(unittest.TestCase):
    def test_declared_map_suites_execute(self):
        pins=json.loads((ROOT/'_MAP/source_pins.json').read_text())['commits']
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        prepared=prepare.ensure_pins(ROOT,pins,allow_fetch=os.environ.get('GITHUB_ACTIONS')=='true')
        result=subprocess.run([sys.executable,str(ROOT/'_MAP/run_suites.py')],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=180)
        receipt=json.loads(result.stdout);expected=json.loads((ROOT/'_MAP/suites.json').read_text())['suites']
        self.assertEqual({s['id'] for s in expected},{s['suite'] for s in receipt['suites']})
        self.assertEqual(len(expected),len(receipt['suites']))
        self.assertTrue(all(s['result']=='pass' and s['cases'] for s in receipt['suites']))
        self.assertEqual(head,subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
        status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','_MAP','orchestration/tests/test_map_suite_discovery.py'],cwd=ROOT,text=True)
        scoped_changes=[line for line in status.splitlines() if '__pycache__/' not in line and not line.endswith('.pyc')]
        surface='github_actions' if os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('GITHUB_RUN_ID') else 'local'
        print('MAP_HOSTED_DISCOVERY '+json.dumps({'checkout_head':head,'execution_surface':surface,'scoped_content_matches_head':not scoped_changes,'scoped_changes':scoped_changes,'source_pins':prepared,'suite_results':receipt['suites']},sort_keys=True),flush=True)

    def test_missing_source_fails_offline(self):
        with patch.object(prepare,'present',return_value=False),patch.object(prepare.subprocess,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'Missing pinned'):prepare.ensure_pins(ROOT,['a'*40])
            run.assert_not_called()

    def test_wrong_origin_cannot_fetch(self):
        with patch.object(prepare,'present',return_value=False),patch.object(prepare.subprocess,'check_output',return_value='https://example.invalid/repo'),patch.object(prepare.subprocess,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'exact _BASKET'):prepare.ensure_pins(ROOT,['a'*40],True)
            run.assert_not_called()

    def test_bad_pins_never_run_git(self):
        for pins in ([],['main'],['a'*40,'a'*40]):
            with patch.object(prepare,'present') as present:
                with self.assertRaises(ValueError):prepare.ensure_pins(ROOT,pins,True)
                present.assert_not_called()

    def test_successful_fetch_is_rechecked(self):
        with patch.object(prepare,'present',side_effect=[False,False]),patch.object(prepare.subprocess,'check_output',return_value='https://github.com/whiterosecoffee/_BASKET.git'),patch.object(prepare.subprocess,'run') as run:
            with self.assertRaisesRegex(RuntimeError,'remains unavailable'):prepare.ensure_pins(ROOT,['a'*40],True)
            run.assert_called_once()
if __name__=='__main__':unittest.main()
