"""Offline CLI for verified, caller-supplied AH-MRI input only.

python research/traversal/ah_mri/run.py input.json --json-out result.json --md-out report.md
"""
import argparse
import json
from pathlib import Path
from core import analyze, markdown

def main():
    p=argparse.ArgumentParser(description="AH-MRI offline close/AH research report (not a live feed)")
    p.add_argument("input", type=Path)
    p.add_argument("--json-out",type=Path)
    p.add_argument("--md-out",type=Path)
    args=p.parse_args()
    data=json.loads(args.input.read_text(encoding="utf-8"))
    report=analyze(data)
    body=markdown(report)
    if args.json_out:
        args.json_out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if args.md_out:
        args.md_out.write_text(body,encoding="utf-8")
    if not args.md_out:
        print(body,end="")
if __name__=="__main__":
    main()
