"""Execute plan.json: pull vendor minute bars into staging/raw/<TICKER>.jsonl (vendor values,
untouched except for mapping into the row shape). Never touches the data folder.

Resumable: a ticker with a .done marker under staging/raw/<plan-sha256>/ is skipped. Every request outcome is
appended to staging/ledger.jsonl. Create a file named STOP here to halt cleanly.
Env: FETCH_WORKERS (default 8), FETCH_ONLY (comma list of tickers).
"""
import hashlib, json, os, sys, time, threading
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import massive_client as m
RAW = os.path.join(HERE, "staging", os.environ.get("RAW_DIR", "raw")); LEDGER = os.path.join(HERE, "staging", "ledger.jsonl")
SRC = "massive-aggs-v2-1min-refetch"
_lock = threading.Lock()


def load_plan():
    """Use the same plan bytes for parsing and selection of its staging directory."""
    path = Path(HERE) / os.environ.get("PLAN_FILE", "plan.json")
    data = path.read_bytes()
    return json.loads(data)["plan"], hashlib.sha256(data).hexdigest()

def log(rec):
    rec["at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with _lock, open(LEDGER, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, separators=(",", ":")) + "\n")

def conv(tk, r):
    t = r["t"]
    return {"ticker": tk, "t": t, "ts": datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "px": r["c"], "vol": r.get("v"), "o": r["o"], "h": r["h"], "l": r["l"], "c": r["c"],
            "vw": r.get("vw"), "n": r.get("n"), "src": SRC, "class": "bar", "grain": "1min"}

def do_ticker(tk, p):
    if os.path.exists(os.path.join(RAW, tk + ".done")): return tk, "skip", 0
    rows, status_all = {}, []
    for g in p["ranges"]:
        if os.path.exists(os.path.join(HERE, "STOP")): return tk, "stopped", 0
        pages = 0; n0 = len(rows); st = None
        try:
            for st, body, hdr in m.aggs(p["symbol"], 1, "minute", g["from"], g["to"], adjusted="true"):
                pages += 1
                if st != 200: break
                for r in body.get("results", []) or []: rows[r["t"]] = conv(tk, r)
        except Exception as e:
            st = "EXC:" + type(e).__name__
        log({"ticker": tk, "symbol": p["symbol"], "from": g["from"], "to": g["to"], "status": st, "pages": pages, "rows": len(rows) - n0})
        status_all.append(st)
    tmp = os.path.join(RAW, tk + ".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for t in sorted(rows): fh.write(json.dumps(rows[t], separators=(",", ":")) + "\n")
    os.replace(tmp, os.path.join(RAW, tk + ".jsonl"))
    ok = all(s == 200 for s in status_all)
    marker = ".done" if ok else ".failed"  # only a fully successful ticker is skipped on resume
    with open(os.path.join(RAW, tk + marker), "w") as fh: fh.write(json.dumps({"rows": len(rows), "statuses": status_all, "ok": ok}))
    return tk, ("ok" if ok else "errors:%s" % sorted(set(map(str, status_all)))), len(rows)

if __name__ == "__main__":
    plan, plan_sha256 = load_plan()
    RAW = os.path.join(RAW, plan_sha256)
    only = [x for x in os.environ.get("FETCH_ONLY", "").split(",") if x]
    tks = [t for t in plan if (not only or t in only)]
    w = int(os.environ.get("FETCH_WORKERS", "8")); t0 = time.time(); done = 0; tot = 0
    print("tickers", len(tks), "workers", w, flush=True)
    os.makedirs(RAW, exist_ok=True)
    with ThreadPoolExecutor(max_workers=w) as ex:
        futs = [ex.submit(do_ticker, t, plan[t]) for t in tks]
        for f in as_completed(futs):
            tk, res, n = f.result(); done += 1; tot += n
            if res not in ("ok", "skip") or done % 20 == 0:
                print("[%d/%d] %s %s rows=%d total_rows=%d %.0fs" % (done, len(tks), tk, res, n, tot, time.time() - t0), flush=True)
    print("FINISHED rows=%d %.0fs" % (tot, time.time() - t0), flush=True)
