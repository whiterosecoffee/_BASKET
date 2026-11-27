"""Distance from the 52-week low, drawdown from the 52-week high, and the empirical forward return after such states.

Everything is computed from daily regular-session bars (`snapshots.daily_bars`). Facts and scenarios are kept apart: the ranking is a
measurement of where each ticker sits today; the forward study is a historical frequency table from one 14-month window, not a forecast.
Prices are as stored (unadjusted for splits). A one-day close-to-close move beyond SPLIT_RATIO is flagged `split_suspect`, excluded from the
ranking and the study by default, and listed so a human can confirm whether it was a split or a real crash.
"""
from __future__ import annotations

import random
import statistics
from collections import defaultdict, deque
from datetime import datetime, timedelta

SPLIT_LOW, SPLIT_HIGH = 0.62, 1.60
HORIZONS = (5, 20, 60)
LOW_BUCKETS = ((0.05, "<=5%"), (0.10, "5-10%"), (0.20, "10-20%"), (0.40, "20-40%"), (9.9, ">40%"))
DD_BUCKETS = ((-0.60, "<=-60%"), (-0.40, "-60..-40"), (-0.25, "-40..-25"), (-0.10, "-25..-10"), (9.9, ">-10%"))


def split_suspects(bars: list[dict]) -> list[tuple[str, float]]:
    return [(b["date"], round(b["c"] / a["c"], 3)) for a, b in zip(bars, bars[1:]) if not SPLIT_LOW <= b["c"] / a["c"] <= SPLIT_HIGH]


def features(bars: list[dict], window_days: int = 364) -> list[dict]:
    """Per-day state: lo52, hi52 over the trailing calendar window, distance above the low, drawdown from the high, forward returns."""
    dts = [datetime.strptime(b["date"], "%Y-%m-%d") for b in bars]
    lo_q: deque[int] = deque()
    hi_q: deque[int] = deque()
    out = []
    for i, b in enumerate(bars):
        cut = dts[i] - timedelta(days=window_days)
        while lo_q and dts[lo_q[0]] < cut:
            lo_q.popleft()
        while hi_q and dts[hi_q[0]] < cut:
            hi_q.popleft()
        while lo_q and bars[lo_q[-1]]["l"] >= b["l"]:
            lo_q.pop()
        lo_q.append(i)
        while hi_q and bars[hi_q[-1]]["h"] <= b["h"]:
            hi_q.pop()
        hi_q.append(i)
        lo, hi = bars[lo_q[0]]["l"], bars[hi_q[0]]["h"]
        f = {"date": b["date"], "c": b["c"], "lo52": lo, "hi52": hi, "dist_low": b["c"] / lo - 1, "dd": b["c"] / hi - 1,
             "lo_date": bars[lo_q[0]]["date"], "hi_date": bars[hi_q[0]]["date"], "full": (dts[i] - dts[0]).days >= window_days - 14}
        for k in HORIZONS:
            f[f"f{k}"] = bars[i + k]["c"] / b["c"] - 1 if i + k < len(bars) else None
        out.append(f)
    return out


def ranking(per_ticker: dict[str, list[dict]], min_window_days: int = 150, as_of_floor: str | None = None) -> dict:
    """Latest-state table. Score = mean of (closeness to low) and (depth of drawdown) as cross-sectional percentile ranks."""
    rows, flagged, short = [], {}, []
    for sym, bars in per_ticker.items():
        sus = split_suspects(bars)
        if sus:
            flagged[sym] = sus[:3]
            continue
        if len(bars) < min_window_days:
            short.append(sym)
            continue
        f = features(bars)[-1]
        win = [b for b in bars if b["date"] >= (datetime.strptime(bars[-1]["date"], "%Y-%m-%d") - timedelta(days=364)).strftime("%Y-%m-%d")]
        po = sum(b["price_only"] for b in win) / max(1, sum(b["minutes"] for b in win))
        rows.append({"ticker": sym, "date": f["date"], "close": f["c"], "lo52": f["lo52"], "hi52": f["hi52"], "dist_low": f["dist_low"], "dd": f["dd"],
                     "lo_date": f["lo_date"], "hi_date": f["hi_date"], "price_only_share": po, "full_52w": f["full"]})
    if rows:
        pr = lambda key, rev: {r["ticker"]: i / max(1, len(rows) - 1) for i, r in enumerate(sorted(rows, key=lambda r: r[key], reverse=rev))}
        near, deep = pr("dist_low", False), pr("dd", False)   # lowest dist_low first; most negative dd first
        for r in rows:
            r["score"] = ((1 - near[r["ticker"]]) + (1 - deep[r["ticker"]])) / 2
        rows.sort(key=lambda r: -r["score"])
    stale = [r["ticker"] for r in rows if as_of_floor and r["date"] < as_of_floor]
    return {"rows": rows, "split_suspect": flagged, "too_short": short, "stale": stale}


def _bucket(x, table):
    return next(label for bound, label in table if x <= bound)


def forward_study(per_ticker: dict[str, list[dict]], horizon: int = 20, seed: int = 1, boot: int = 300) -> dict:
    """Frequency of positive and market-beating forward returns by distance-to-low and drawdown bucket (full 52-week windows only).

    `beat` is relative to the cross-sectional median forward return of the same date. The interval resamples whole dates, so observations that
    share a date (one market move) count once; it does not account for the same ticker appearing on many dates.
    """
    key = f"f{horizon}"
    obs = []
    for sym, bars in per_ticker.items():
        if split_suspects(bars):
            continue
        for f in features(bars):
            if f["full"] and f[key] is not None:
                obs.append((sym, f))
    by_date = defaultdict(list)
    for _, f in obs:
        by_date[f["date"]].append(f[key])
    med = {d: statistics.median(v) for d, v in by_date.items() if len(v) >= 30}
    obs = [(s, f) for s, f in obs if f["date"] in med]
    rng = random.Random(seed)

    def summarize(items):
        if not items:
            return None
        r = [f[key] for _, f in items]
        ex = [f[key] - med[f["date"]] for _, f in items]
        res = {"n": len(r), "tickers": len({s for s, _ in items}), "dates": len({f["date"] for _, f in items}), "p_up": sum(x > 0 for x in r) / len(r),
               "median": statistics.median(r), "p_beat_median_stock": sum(x > 0 for x in ex) / len(ex), "median_excess": statistics.median(ex)}
        if len(items) >= 200:
            bd = defaultdict(list)
            for _, f in items:
                bd[f["date"]].append(f[key] - med[f["date"]])
            ds, ps = list(bd), []
            for _ in range(boot):
                n = t = 0
                for d in rng.choices(ds, k=len(ds)):
                    n += len(bd[d]); t += sum(x > 0 for x in bd[d])
                ps.append(t / n)
            ps.sort()
            res["p_beat_ci90"] = [ps[int(0.05 * boot)], ps[int(0.95 * boot)]]
        return res

    out = {"horizon_days": horizon, "window": [min(med), max(med)] if med else None, "all": summarize(obs), "by_dist_low": {}, "by_drawdown": {}, "joint": {}}
    for _, label in LOW_BUCKETS:
        out["by_dist_low"][label] = summarize([(s, f) for s, f in obs if _bucket(f["dist_low"], LOW_BUCKETS) == label])
    for _, label in DD_BUCKETS:
        out["by_drawdown"][label] = summarize([(s, f) for s, f in obs if _bucket(f["dd"], DD_BUCKETS) == label])
    out["joint"] = {
        "near_low<=10%_and_dd<=-40%": summarize([(s, f) for s, f in obs if f["dist_low"] <= 0.10 and f["dd"] <= -0.40]),
        "near_low<=10%_and_dd>-40%": summarize([(s, f) for s, f in obs if f["dist_low"] <= 0.10 and f["dd"] > -0.40]),
        "far_from_low>40%_and_dd>-25%": summarize([(s, f) for s, f in obs if f["dist_low"] > 0.40 and f["dd"] > -0.25])}
    return out
