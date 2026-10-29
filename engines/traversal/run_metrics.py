"""Stable local read-only JSONL entrypoint for B06 metrics; no polling or persistence."""
import argparse, json
from pathlib import Path
from metrics import evaluate

def main():
    p=argparse.ArgumentParser()
    p.add_argument("instrument")
    p.add_argument("--jsonl",required=True)
    p.add_argument("--interval",type=int,default=1)
    p.add_argument("--as-of-ms",type=int)
    args=p.parse_args()
    bars=[json.loads(s) for s in Path(args.jsonl).read_text().splitlines() if s.strip()]
    print(json.dumps(evaluate(args.instrument,bars,interval_minutes=args.interval,as_of=args.as_of_ms),indent=2))

if __name__=="__main__": main()
