"""Read daily bars from the _PATTERNS ticker store: <root>/<TICKER>/snapshots/<YYYY-MM-DD>.jsonl (1-minute rows, one ET date per file).

Rows follow `_PATTERNS/_TOOLS/ticker_rows.py`: ticker, t (epoch ms bar start), ts, px, vol, o, h, l, c, vw, n, src, class, grain [, verified].
`class` is "bar" (real OHLC) or "moment" (price-only: o/h/l/c are null, px is the minute close). Daily bars are built from the regular session
(09:30-15:59 ET start minutes); on price-only days the high and low come from minute closes, so they understate true extremes (reported as price_only).
Read-only. The root is passed in; this module never writes to the store.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
NON_EQUITY_PREFIX = ("I_", "C_", "X_", "O_", "F_")


def tickers(root: Path, equities_only: bool = True) -> list[str]:
    out = []
    for d in sorted(os.listdir(root)):
        if d.startswith("_") or not (root / d / "snapshots").is_dir():
            continue
        if equities_only and d.startswith(NON_EQUITY_PREFIX):
            continue
        out.append(d)
    return out


def _day_start_ms(day: str) -> int:
    return int(datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=ET).timestamp() * 1000)


def daily_bars(root: Path, sym: str) -> list[dict]:
    """Regular-session daily bars: date, o, h, l, c, v, minutes, price_only (minutes without a real bar)."""
    rows = []
    d = root / sym / "snapshots"
    for name in sorted(os.listdir(d)):
        if not name.endswith(".jsonl"):
            continue
        day = name[:-6]
        s0 = _day_start_ms(day)
        o = h = l = c = None
        v = n = po = 0
        first, last = 10**9, -1
        with (d / name).open(encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r.get("grain") == "1day":
                    continue
                m = (r["t"] - s0) // 60000
                if m < 570 or m > 959:
                    continue
                px, cc = r.get("px"), r.get("c")
                if px is None and cc is None:
                    continue
                hi = r["h"] if r.get("h") is not None else px
                lo = r["l"] if r.get("l") is not None else px
                cl = cc if cc is not None else px
                op = r["o"] if r.get("o") is not None else px
                h = hi if h is None or hi > h else h
                l = lo if l is None or lo < l else l
                if m < first:
                    first, o = m, op
                if m > last:
                    last, c = m, cl
                v += r.get("vol") or 0
                n += 1
                if r.get("class") != "bar":
                    po += 1
        if n:
            rows.append({"date": day, "o": o, "h": h, "l": l, "c": c, "v": v, "minutes": n, "price_only": po})
    return rows
