"""Resolve only declared immutable Git objects; optional explicit source-only fetch."""
import argparse
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
ALLOWED_ORIGINS={'https://github.com/whiterosecoffee/_BASKET','https://github.com/whiterosecoffee/_BASKET.git','git@github.com:whiterosecoffee/_BASKET.git'}
def present(root,pin):
    return subprocess.run(['git','cat-file','-e',pin+'^{commit}'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

def ensure_pins(root,pins,allow_fetch=False):
    root=Path(root)
    if not pins or len(pins)!=len(set(pins)) or any(not isinstance(p,str) or not re.fullmatch('[a-f0-9]{40}',p) for p in pins):
        raise ValueError('nonempty unique immutable commit pins required')
    missing=[p for p in pins if not present(root,p)]
    if missing and not allow_fetch:raise RuntimeError('Missing pinned source objects; prepare explicitly before offline execution: '+','.join(missing))
    if missing:
        origin=subprocess.check_output(['git','remote','get-url','origin'],cwd=root,text=True).strip()
        if origin not in ALLOWED_ORIGINS:raise RuntimeError('Source fetch requires the exact _BASKET origin')
        for pin in missing:
            subprocess.run(['git','fetch','--no-tags','--depth=1','origin',pin],cwd=root,check=True,timeout=90,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if not present(root,pin):raise RuntimeError('Fetched source pin remains unavailable: '+pin)
    return {'pins':pins,'fetched':missing,'checkout_unchanged':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fetch-missing',action='store_true');args=parser.parse_args()
    pins=json.loads((ROOT/'_MAP/source_pins.json').read_text())['commits']
    before=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    result=ensure_pins(ROOT,pins,args.fetch_missing)
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==before
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
