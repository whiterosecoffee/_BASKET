"""Verify staged vendor rows against the Ubuntu ticker archive and report proposed additions.

Scope: sessions with NO stored data (plan kind 'missing'). Existing rows are never changed.

Per ticker:
  1. Standardize staged rows with the sanitizer (documented rule: fractional vol/n -> int).
  2. EXACT comparison on every overlapping 1-min bar (same `t`), field by field.
     Each field of each row lands in exactly one bucket:
       exact      - identical value
       precision  - differs only because the stored value carries more decimals than the
                    vendor's published precision (round(stored, decimals(vendor)) == vendor)
       MISMATCH   - anything else
     Every bucket count is recorded. Mismatches are history drift (vendor restated a bar):
     reported, never overwritten. The ONLY gate is a basis shift: >=20 overlapping bars and
     zero matching closes (a split moves every close). No numeric tolerance anywhere.
  3. New lines = staged rows in missing ET sessions. Quality checks run on the would-be file.
The Ubuntu port produces a dry-run report. Env: APPLY_WORKERS, RAW_DIR, PLAN_FILE.
"""
import json, os, collections, argparse
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from concurrent.futures import ProcessPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__))
import ticker_jsonl_tool as T
from fetch_run import load_plan
RAW = os.path.join(HERE, "staging", os.environ.get("RAW_DIR", "raw"))
DATA_ROOT = Path(os.environ.get("TICKER_DATA_ROOT") or Path.home() / "OneDrive/_BASKET/_TICKERS")
ET = ZoneInfo("America/New_York")
GATED = ("o", "h", "l", "c", "vol")

_TBL = {}
def et_date(t):
    h = t // 3600000
    v = _TBL.get(h)
    if v is None:
        v = _TBL[h] = datetime.fromtimestamp(h * 3600, tz=timezone.utc).astimezone(ET).date().isoformat()
    return v

def decimals(x):
    s = repr(float(x))
    return len(s.split(".")[1]) if "." in s and "e" not in s else 0

def classify(stored, vendor):
    if stored == vendor: return "exact"
    if stored is None or vendor is None: return "MISMATCH"
    if isinstance(stored, float) and isinstance(vendor, float) and round(stored, decimals(vendor)) == vendor:
        return "precision"
    return "MISMATCH"

def process(tk, p):
    res = {"ticker": tk, "round": os.environ.get("RAW_DIR", "raw"), "applied": False}
    if not os.path.isfile(os.path.join(RAW, tk + ".done")):
        failed = os.path.isfile(os.path.join(RAW, tk + ".failed"))
        res["status"] = "staging_failed" if failed else "staging_unavailable_or_incomplete"
        res["ranges_unverified"] = p["ranges"]
        return res
    rawp = os.path.join(RAW, tk + ".jsonl")
    if not os.path.exists(rawp): res["status"] = "no_staged_file"; return res
    staged = [json.loads(l) for l in open(rawp, encoding="utf-8") if l.strip()]
    archive = DATA_ROOT / tk / f"{tk}.jsonl"
    if not archive.is_file():
        res["status"] = "archive_unavailable"
        return res
    with archive.open(encoding="utf-8") as fh:
        stored = [json.loads(line) for line in fh if line.strip()]
    sidx = {r["t"]: r for r in stored}
    std, changed = [], 0
    for r in staged:
        c, ch = T.SanitizeRow(r, "bar"); std.append(c); changed += bool(ch)
    res.update(staged_rows=len(staged), standardized_rows=changed)
    cmp = {f: collections.Counter() for f in ("o", "h", "l", "c", "vol", "vw", "n")}
    ov = 0; examples = []
    for r in std:
        b = sidx.get(r["t"])
        if b is None or b.get("class") != "bar" or b.get("grain") != "1min": continue
        ov += 1
        for f in cmp:
            k = classify(b[f], r[f]); cmp[f][k] += 1
            if k == "MISMATCH" and f in GATED and len(examples) < 3: examples.append((b["ts"], f, b[f], r[f]))
    res["overlap_rows"] = ov
    res["compare"] = {f: dict(c) for f, c in cmp.items()}
    # The new lines do not depend on any existing row, so field-level history drift is
    # REPORTED (exact counts above), not a reason to withhold them. What must stop a write is a
    # change of basis (a split): that changes EVERY overlapping close, so no row matches at all.
    c_ok = cmp["c"]["exact"] + cmp["c"]["precision"]
    res["drift_examples"] = examples
    if ov >= 20 and c_ok == 0:
        res["status"] = "HELD_basis_shift"; return res
    kinds = p["kind_by_session"]
    by = collections.defaultdict(list)
    for r in std: by[et_date(r["t"])].append(r)
    take, empty = {}, []
    for d, k in kinds.items():
        if k != "missing": continue
        if by.get(d): take[d] = by[d]
        else: empty.append(d)
    res["sessions_added"] = len(take)
    res["sessions_vendor_empty"] = len(empty)
    res["sessions_without_staged_rows"] = empty
    if not take: res["status"] = "nothing_to_add"; return res
    add = sorted((r for rows in take.values() for r in rows), key=lambda r: r["t"])
    if any(r["t"] in sidx for r in add): res["status"] = "HELD_t_collision"; return res
    new = sorted(stored + add, key=lambda r: r["t"])
    probs = (T.CheckRequiredFieldsPresent(new, "bar") + T.CheckTickerFieldMatchesFilename(new, tk) +
             T.CheckChronologicalOrderNoDuplicates(new) + T.CheckBarPriceConsistency(new, "bar") +
             T.CheckForBlankOrMissingValues(new, "bar", tk))
    res.update(rows_before=len(stored), rows_added=len(add), rows_after=len(new))
    if probs: res["status"] = "HELD_quality"; res["problems"] = probs[:5]; return res
    res["status"] = "ready"
    last_t = stored[-1]["t"] if stored else -1
    res["mode"] = "append" if add[0]["t"] > last_t else "rewrite"
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="")
    a = ap.parse_args()
    plan, plan_sha256 = load_plan()
    RAW = os.path.join(RAW, plan_sha256)
    only = [x for x in a.only.split(",") if x]
    tks = [t for t in plan if not only or t in only]
    print("mode dry-run tickers", len(tks), flush=True)
    out = []
    with ProcessPoolExecutor(max_workers=int(os.environ.get("APPLY_WORKERS", "3"))) as ex:
        futs = {ex.submit(process, t, plan[t]): t for t in tks}
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result(); out.append(r)
            if i % 50 == 0 or r["status"] not in ("ready", "nothing_to_add"):
                print("[%d/%d] %s %s" % (i, len(tks), r["ticker"], r["status"]), flush=True)
    os.makedirs(os.path.join(HERE, "staging"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "staging", "verify-dry.json"), "w"), separators=(",", ":"))
    print(collections.Counter(r["status"] for r in out))
