"""Per-ticker full-history JSONL (one JSON object per trading day). Source: prices/<T>.csv (OHLCV) and prices/benchmarks_close.csv (close only)."""
from __future__ import annotations

import csv
import json
from pathlib import Path


def export(pdir: Path, out: Path) -> dict[str, int]:
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for f in sorted(pdir.glob("*.csv")):
        if f.stem in ("PROVISIONAL",):
            continue
        with f.open(newline="") as fh:
            rd = csv.DictReader(fh)
            rows = []
            for r in rd:
                rec = {"t": f.stem, "date": r["date"]}
                for k, v in r.items():
                    if k != "date" and v not in ("", None):
                        rec[k] = float(v) if k != "volume" else int(float(v))
                rows.append(rec)
        if f.stem == "benchmarks_close":
            for t in ("MSFT", "SMH", "QQQ"):
                recs = [{"t": t, "date": r["date"], "close": r[t]} for r in rows if r.get(t) is not None]
                (out / f"{t}.jsonl").write_text("".join(json.dumps(x, separators=(",", ":")) + "\n" for x in recs))
                counts[t] = len(recs)
            continue
        (out / f"{f.stem}.jsonl").write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))
        counts[f.stem] = len(rows)
    return counts
