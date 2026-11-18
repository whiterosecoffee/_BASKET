"""Dry run: decide exactly what to ask the vendor for, per ticker. No network, no writes
outside this folder. Output: plan.json + printed summary.

Needed sessions per ticker (ET session dates inside the 24-month window):
  - missing sessions (never fetched / stopped / interior holes)
  - sessions whose only data is price-only ('moment') or a single daily bar
Fetch ranges = clusters of needed sessions (merged when <= GAP_MERGE sessions apart), each
extended backwards to include ANCHOR sessions that already hold full 1-min bars, so every
fetch carries rows we can compare against what is stored (restatement / basis tripwire).
"""
import json, glob, os, collections
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
import ticker_jsonl_tool as T

START = date(2024, 10, 1)
END = date.fromisoformat(os.environ.get("PLAN_END", "2026-09-30"))  # last COMPLETE session wanted
GAP_MERGE, ANCHORS = 20, 1
ASKED = json.load(open(os.path.join(HERE, os.environ["ASKED_PLAN"])))["plan"] if os.environ.get("ASKED_PLAN") else {}
MISSING_ONLY = os.environ.get("MISSING_ONLY", "1") == "1"  # gap-analysis scope: only sessions with NO data
SPECIAL_CLOSURES = {date(2025, 1, 9)}

def symbol(tk):
    if tk.startswith("I_"): return "I:" + tk[2:]
    if tk.startswith("C_"): return "C:" + tk[2:]
    return tk

def main():
    exp = [d.isoformat() for d in T.expected_trading_days(START, END) if d not in SPECIAL_CLOSURES]
    plan, tot = {}, collections.Counter()
    scan_dir = os.environ.get("SESSION_SCAN_DIR")
    if not scan_dir:
        raise SystemExit("Set SESSION_SCAN_DIR to the directory containing session scan JSON files")
    scans = sorted(glob.glob(os.path.join(scan_dir, "*.json")))
    if not scans:
        raise SystemExit("No session scan JSON files found in SESSION_SCAN_DIR")
    for f in scans:
        r = json.load(open(f, encoding="utf-8")); tk, days = r["ticker"], r["days"]
        needed, kind, bars = [], {}, []
        for d in exp:
            e = days.get(d)
            if e is None: needed.append(d); kind[d] = "missing"; continue
            src, cls, gr = max(e["srcs"], key=e["srcs"].get).split("|")
            if MISSING_ONLY: bars.append(d)  # present = not our job in this scope
            elif cls == "moment": needed.append(d); kind[d] = "price_only"
            elif gr == "1day": needed.append(d); kind[d] = "daily_only"
            else: bars.append(d)
        if ASKED:  # sessions already requested in an earlier round and still empty: do not ask again
            asked = set(ASKED.get(tk, {}).get("needed", []))
            needed = [d for d in needed if d not in asked]
            kind = {d: k for d, k in kind.items() if d in set(needed)}
        if not needed: continue
        idx = {d: i for i, d in enumerate(exp)}
        clusters, cur = [], [needed[0]]
        for d in needed[1:]:
            if idx[d] - idx[cur[-1]] <= GAP_MERGE: cur.append(d)
            else: clusters.append(cur); cur = [d]
        clusters.append(cur)
        ranges = []
        for c in clusters:
            lo = c[0]
            prior = [b for b in bars if b < lo][-ANCHORS:]
            nxt = [b for b in bars if b > c[-1]][:ANCHORS]
            ranges.append({"from": (prior[0] if prior else lo), "to": (nxt[-1] if nxt else END.isoformat()) if c[-1] != exp[-1] else END.isoformat(),
                           "needed": len(c)})
        plan[tk] = {"symbol": symbol(tk), "needed": needed, "kinds": dict(collections.Counter(kind.values())),
                    "kind_by_session": kind, "ranges": ranges}
        for k, v in plan[tk]["kinds"].items(): tot[k] += v
    pages = sum(max(1, -(-(( date.fromisoformat(g["to"]) - date.fromisoformat(g["from"])).days * 5 // 7 + 1)) // 50) for p in plan.values() for g in p["ranges"])
    reqs = sum(len(p["ranges"]) for p in plan.values())
    out = {"window": [START.isoformat(), END.isoformat()], "tickers": len(plan), "needed_sessions": dict(tot),
           "min_requests": reqs, "est_pages": pages, "plan": plan}
    json.dump(out, open(os.path.join(HERE, os.environ.get("PLAN_FILE", "plan.json")), "w"), separators=(",", ":"))
    print("tickers needing work:", len(plan), "| needed ticker-sessions:", dict(tot), "(total %d)" % sum(tot.values()))
    print("ranges (min requests):", reqs, "| estimated pages @50k rows:", pages)
    print("tickers by kind mix:", collections.Counter(tuple(sorted(p["kinds"])) for p in plan.values()).most_common(8))

if __name__ == "__main__":
    main()
