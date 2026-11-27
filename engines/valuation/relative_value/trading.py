"""Trading-side facts for a profile: ratios (1:x), relative performance, zones, repeat traversals, extremes, rebound.

Everything here uses prices only. No estimates, no multiples, no targets: that is the valuation side.
"""
from __future__ import annotations

import math
from datetime import date

from .metrics import ratio_stats

ZONE_WIDTH = 1.04  # 4% log bins


def _ret(cl: list[float], n: int) -> float | None:
    return cl[-1] / cl[-1 - n] - 1 if len(cl) > n else None


def _dret(cl: list[float], k: int) -> list[float]:
    cl = cl[-(k + 1):]
    return [cl[i] / cl[i - 1] - 1 for i in range(1, len(cl))]


def corr_beta(x: list[float], y: list[float]) -> tuple[float | None, float | None]:
    """corr and beta of x on y over equal-length daily-return lists."""
    n = min(len(x), len(y))
    if n < 20:
        return None, None
    x, y = x[-n:], y[-n:]
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx == 0 or syy == 0:
        return None, None
    return sxy / math.sqrt(sxx * syy), sxy / syy


def relationship(subj: list[tuple[date, float]], ref: list[tuple[date, float]], lookback: int = 250) -> dict | None:
    """'1 SUBJ = x REF' and its history, plus relative performance, correlation and beta."""
    dr = dict(ref)
    ser = [(t, p, dr[t]) for t, p in subj if t in dr]
    if len(ser) < 60:
        return None
    ratios = [(t, p / r) for t, p, r in ser]
    win = ratios[-lookback:]
    xs = sorted(v for _, v in win)
    cur = ratios[-1][1]
    st = ratio_stats([(t, p) for t, p, _ in ser], [(t, r) for t, _, r in ser], lookback) or {}
    lo = min(win, key=lambda z: z[1]); hi = max(win, key=lambda z: z[1])
    sc, rc = [p for _, p, _ in ser], [r for _, _, r in ser]
    out = {
        "unit": "1 subject share = x reference shares", "x_now": cur, "reference_per_subject_inverse": 1 / cur,
        "as_of": ser[-1][0].isoformat(), "median_250d": xs[len(xs) // 2], "p10": xs[int(.1 * (len(xs) - 1))], "p90": xs[int(.9 * (len(xs) - 1))],
        "min": {"x": lo[1], "date": lo[0].isoformat()}, "max": {"x": hi[1], "date": hi[0].isoformat()},
        "z_250d": st.get("z"), "percentile_250d": st.get("pctile"), "half_life_days": st.get("half_life_days"),
        "relative_return": {f"{n}d": ((1 + _ret(sc, n)) / (1 + _ret(rc, n)) - 1) if len(sc) > n else None for n in (1, 5, 20, 60)},
    }
    for k in (250, 60):
        c, b = corr_beta(_dret(sc, k), _dret(rc, k))
        out[f"corr_{k}d"], out[f"beta_{k}d"] = c, b
    return out


def default_weights(rels: dict[str, dict | None]) -> dict:
    """Relationship weights ~ 250d R^2 vs each reference, normalised. Override via relationship_weights.json."""
    r2 = {k: (v["corr_250d"] ** 2 if v and v.get("corr_250d") is not None else 0.0) for k, v in rels.items()}
    tot = sum(r2.values())
    if tot <= 0:
        n = len(rels) or 1
        return {k: 1 / n for k in rels}
    return {k: v / tot for k, v in r2.items()}


def zone_index(price: float) -> int:
    return math.floor(math.log(price) / math.log(ZONE_WIDTH))


def zone_bounds(idx: int) -> tuple[float, float]:
    return ZONE_WIDTH ** idx, ZONE_WIDTH ** (idx + 1)


def zones(closes: list[tuple[date, float]], vols: list[float] | None, top: int = 6) -> list[dict]:
    """Price zones (4% log bins): dwell days, volume share, visits and the direction of entry."""
    idx = [zone_index(p) for _, p in closes]
    stats: dict[int, dict] = {}
    prev = None
    tv = sum(vols) if vols else 0.0
    for i, (t, p) in enumerate(closes):
        z = stats.setdefault(idx[i], {"dwell": 0, "vol": 0.0, "visits": 0, "from_above": 0, "from_below": 0, "first": t, "last": t})
        z["dwell"] += 1
        z["last"] = t
        if vols:
            z["vol"] += vols[i]
        if prev is None or idx[i] != prev:
            z["visits"] += 1
            if prev is not None:
                z["from_above" if prev > idx[i] else "from_below"] += 1
        prev = idx[i]
    spot = idx[-1]
    out = []
    for k, z in stats.items():
        lo, hi = zone_bounds(k)
        out.append({"low": round(lo, 4), "high": round(hi, 4), "dwell_days": z["dwell"], "visits": z["visits"],
                    "volume_share": round(z["vol"] / tv, 4) if tv else None, "entries_from_above": z["from_above"],
                    "entries_from_below": z["from_below"], "first": z["first"].isoformat(), "last": z["last"].isoformat(),
                    "role_vs_spot": "contains_spot" if k == spot else ("support_side" if k < spot else "resistance_side"), "_k": k})
    key = (lambda z: z["volume_share"] or 0) if vols else (lambda z: z["dwell_days"])
    return sorted(out, key=key, reverse=True)[:top]


def zone_of(price: float, closes: list[tuple[date, float]], vols: list[float] | None) -> dict:
    k = zone_index(price)
    lo, hi = zone_bounds(k)
    days = [i for i, (_, p) in enumerate(closes) if zone_index(p) == k]
    visits, prev = 0, None
    for i, (_, p) in enumerate(closes):
        z = zone_index(p)
        if z == k and prev != k:
            visits += 1
        prev = z
    tv = sum(vols) if vols else 0.0
    return {"price": price, "zone_low": round(lo, 4), "zone_high": round(hi, 4), "dwell_days": len(days), "visits": visits,
            "volume_share": round(sum(vols[i] for i in days) / tv, 4) if vols and tv else None,
            "last_visit_before_now": closes[days[-1]][0].isoformat() if days else None}


def level_crossings(closes: list[tuple[date, float]], level: float) -> dict:
    """How many times did the close cross a level, and when last? (repeat traversal of a price)."""
    n, last, prev = 0, None, None
    for t, p in closes:
        s = p >= level
        if prev is not None and s != prev:
            n += 1
            last = t
        prev = s
    return {"level": level, "crossings": n, "last_cross": last.isoformat() if last else None}


def extremes_and_rebound(bars: list[dict], prov: dict | None, window: int = 252) -> dict:
    """Friday's (last final bar) extreme versus the provisional next session."""
    last = bars[-1]
    win = bars[-window:]
    lo = min(win, key=lambda b: b["low"]); hi = max(win, key=lambda b: b["high"]); ever = min(bars, key=lambda b: b["low"])
    v20 = sum(b["volume"] for b in bars[-21:-1]) / 20
    rng = last["high"] - last["low"]
    out = {
        "last_final_bar": {"date": last["date"].isoformat(), "open": last["open"], "high": last["high"], "low": last["low"], "close": last["close"],
                           "volume": last["volume"], "volume_vs_prior20d": last["volume"] / v20,
                           "close_location_in_range": (last["close"] - last["low"]) / rng if rng else None,
                           "made_52w_low": last["low"] <= lo["low"] * 1.0000001},
        "window_52w": {"low": lo["low"], "low_date": lo["date"].isoformat(), "high": hi["high"], "high_date": hi["date"].isoformat(),
                       "drawdown_close_vs_high": last["close"] / hi["high"] - 1, "low_to_high_range": hi["high"] / lo["low"] - 1},
        "lowest_low_in_data": {"low": ever["low"], "date": ever["date"].isoformat(), "first_bar": bars[0]["date"].isoformat()},
        "dd_peak_to_low": lo["low"] / hi["high"] - 1,
    }
    if prov:
        gap = prov["open"] / last["close"] - 1
        out["provisional_next_session"] = {
            "status": prov.get("status", "PROVISIONAL"), "open": prov["open"], "high": prov["high"], "low": prov["low"], "last": prov["close"],
            "gap_open_vs_prior_close": gap, "last_vs_prior_close": prov["close"] / last["close"] - 1,
            "last_vs_prior_low": prov["close"] / last["low"] - 1,
            "session_low_above_prior_low": prov["low"] > last["low"],
            "gap_unfilled_vs_prior_high": prov["low"] > last["high"],
            "retrace_of_peak_to_low_drop": (prov["close"] - lo["low"]) / (hi["high"] - lo["low"]) if hi["high"] > lo["low"] else None,
            "session_range_pct": prov["high"] / prov["low"] - 1,
        }
    return out
