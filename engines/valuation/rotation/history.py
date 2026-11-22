"""Standardized historical multiples from reported quarterlies, point-in-time and split-normalised."""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from .store import d

STD_SPLITS = (2, 3, 4, 5, 6, 8, 10, 15, 20)


def load_fund(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"period_end": d(r["period_end"]), "filing": d(r["filing_date"]), "revenue": float(r["revenue"]),
                         "ni": float(r["net_income"]), "sh": float(r["diluted_shares_reported"])})
    rows.sort(key=lambda r: r["period_end"])
    return normalise(rows)


def normalise(rows: list[dict]) -> list[dict]:
    """Put every quarter on the latest share basis and fix unusable filing dates.

    Massive's history mixes split-adjusted and unadjusted share counts (e.g. SNDK 1.2B vs 0.15B diluted shares),
    so a quarter whose share count is within 8% of a standard split multiple of the latest quarter is scaled.
    filing_date is sometimes a restatement date a year late; if it is >120 days after period end, availability
    falls back to period_end + 45 days.
    """
    if not rows:
        return rows
    latest = rows[-1]["sh"]
    for r in rows:
        ratio, k = latest / r["sh"], 1.0
        for s in STD_SPLITS:
            if abs(ratio / s - 1) < 0.08:
                k = float(s)
        r["split_k"] = k
        r["sh_norm"] = r["sh"] * k
        r["eps_norm"] = r["ni"] / r["sh_norm"]
        gap = (r["filing"] - r["period_end"]).days
        r["avail"] = r["filing"] if 0 <= gap <= 120 else r["period_end"] + timedelta(days=45)
    return rows


def ttm_at(rows: list[dict], t: date) -> dict | None:
    known = [r for r in rows if r["avail"] <= t][-4:]
    if len(known) < 4 or (known[-1]["period_end"] - known[0]["period_end"]).days > 330:
        return None
    return {"eps": sum(r["eps_norm"] for r in known), "revenue": sum(r["revenue"] for r in known), "sh": known[-1]["sh_norm"]}


def multiple_history(bars: list[dict], rows: list[dict]) -> dict[str, list[tuple[date, float]]]:
    pe, ps = [], []
    for b in bars:
        t = ttm_at(rows, b["date"])
        if not t:
            continue
        if t["eps"] > 0:
            pe.append((b["date"], b["close"] / t["eps"]))
        if t["revenue"] > 0:
            ps.append((b["date"], b["close"] * t["sh"] / t["revenue"]))
    return {"pe": pe, "ps": ps}


def quantile(xs: list[float], q: float) -> float:
    s = sorted(xs)
    i = q * (len(s) - 1)
    lo = int(i)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)


def stats(series: list[tuple[date, float]], min_obs: int = 120) -> dict | None:
    xs = [v for _, v in series]
    if len(xs) < min_obs:
        return None
    return {"n": len(xs), "p25": quantile(xs, .25), "median": quantile(xs, .5), "p75": quantile(xs, .75),
            "min": min(xs), "max": max(xs), "first": series[0][0], "last": series[-1][0]}


def eps_regime_ok(rows: list[dict], t: date, max_growth: float = 6.0) -> bool:
    """History is only a usable standard if TTM EPS did not change regime (>6x) inside the window."""
    vals = [x["eps"] for r in rows if (x := ttm_at(rows, r["avail"]))]
    vals = [v for v in vals if v > 0]
    return len(vals) >= 4 and max(vals) / min(vals) <= max_growth
