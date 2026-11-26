"""Execute every declared bounded offline suite; no network or external actions."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent

def local(ref):
    path=(ROOT/ref).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('out-of-scope suite path')
    return path

def main():
    manifest=json.loads((ROOT/'suites.json').read_text());ids=set();receipts=[]
    subprocess.run([sys.executable,str(ROOT/'validate.py')],check=True,stdout=subprocess.PIPE,text=True,timeout=90)
    for suite in manifest['suites']:
        assert suite['id'] not in ids;ids.add(suite['id'])
        runner=local(suite['runner']);assert runner.name=='run.py'
        case_data=json.loads(local(suite['cases']).read_text())['cases']
        expected=[c['id'] for c in case_data];assert len(expected)==len(set(expected))
        result=subprocess.run([sys.executable,str(runner)],check=True,stdout=subprocess.PIPE,text=True,timeout=90)
        evidence=json.loads(result.stdout)
        assert evidence['evidence_class']==suite['evidence_class']
        actual=[c['id'] for c in evidence[suite['results_key']]]
        assert len(actual)==len(set(actual)) and set(actual)==set(expected)
        stored=json.loads(local(suite['evidence']).read_text())
        for key,value in evidence.items():assert stored[key]==value,(suite['id'],key)
        receipts.append({'suite':suite['id'],'cases':actual,'result':'pass','runner_sha256':hashlib.sha256(runner.read_bytes()).hexdigest()})
    print(json.dumps({'scope':'actual local offline suite execution, not hosted or production','suites':receipts},indent=2))
if __name__=='__main__':main()
