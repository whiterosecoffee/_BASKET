"""Rebound cohort: how much of the last completed session's drop did each name recover, and which groups led?

Inputs are a user snapshot (intraday %, as typed from screenshots) and Massive daily bars. All Monday numbers are
provisional. Pure functions; nothing here predicts.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path


def _f(x):
    return float(x) if x not in ("", None) else None


def load(dirpath: Path) -> tuple[list[dict], dict, dict]:
    shots = {}
    with (dirpath / "snapshot_2026-11-23_user.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            shots[r["ticker"]] = {"order": int(r["order"]), "name": r["name"], "price": float(r["price"]), "pct": float(r["pct_vs_prior_close"]) / 100}
    rows = []
    with (dirpath / "massive_2026-11-19_23.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"ticker": r["ticker"], "thu": float(r["thu_close_1119"]), "f_low": float(r["fri_low_1120"]), "f_high": float(r["fri_high_1120"]),
                         "f_close": float(r["fri_close_1120"]), "m_open": float(r["mon_open_1123"]), "m_high": float(r["mon_high_1123"]),
                         "m_low": float(r["mon_low_1123"]), "m_last": float(r["mon_last_1123"])})
    themes = json.loads((dirpath / "peer_groups_by_industry.json").read_text())
    return rows, shots, themes


def theme_of(t: str, themes: dict) -> str:
    return next((k for k, v in themes.items() if not k.startswith("_") and t in v), "other")


def metrics(rows: list[dict], shots: dict, themes: dict) -> list[dict]:
    out = []
    for r in rows:
        s = shots.get(r["ticker"])
        last = s["price"] if s else r["m_last"]
        drop = r["thu"] - r["f_close"]
        rng = r["f_high"] - r["f_low"]
        out.append({
            "ticker": r["ticker"], "theme": theme_of(r["ticker"], themes), "snapshot_order": s["order"] if s else None,
            "fri_change": r["f_close"] / r["thu"] - 1,
            "mon_change": s["pct"] if s else r["m_last"] / r["f_close"] - 1,
            "mon_change_massive": r["m_last"] / r["f_close"] - 1,
            "recovery_of_fri_drop": (last - r["f_close"]) / drop if drop > 0 else None,
            "fri_close_location": (r["f_close"] - r["f_low"]) / rng if rng else None,
            "mon_low_above_fri_low": r["m_low"] > r["f_low"], "gap_unfilled": r["m_low"] > r["f_high"],
            "above_thu_close": last > r["thu"], "mon_gap_open": r["m_open"] / r["f_close"] - 1,
            "mon_last_vs_session_range": (r["m_last"] - r["m_low"]) / (r["m_high"] - r["m_low"]) if r["m_high"] > r["m_low"] else None,
            "in_user_snapshot": bool(s),
        })
    return out


def _corr(x, y):
    n = len(x)
    if n < 5:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sxx * syy) if sxx and syy else None, sxy / sxx if sxx else None


def rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    for k, i in enumerate(s):
        r[i] = k
    return r


def cross_section(ms: list[dict]) -> dict:
    eq = [m for m in ms if m["theme"] != "benchmarks"]
    x, y = [m["fri_change"] for m in eq], [m["mon_change"] for m in eq]
    c = _corr(x, y)
    sp = _corr(rank(x), rank(y))
    return {"n": len(eq), "pearson_fri_vs_mon": c[0] if c else None, "slope_mon_on_fri": c[1] if c else None,
            "spearman_fri_vs_mon": sp[0] if sp else None, "median_fri": sorted(x)[len(x) // 2], "median_mon": sorted(y)[len(y) // 2],
            "share_above_thursday_close": sum(m["above_thu_close"] for m in eq) / len(eq),
            "share_gap_unfilled": sum(m["gap_unfilled"] for m in eq) / len(eq)}


def theme_table(ms: list[dict]) -> list[dict]:
    g: dict[str, list[dict]] = {}
    for m in ms:
        g.setdefault(m["theme"], []).append(m)
    rows = []
    for k, v in g.items():
        rec = [m["recovery_of_fri_drop"] for m in v if m["recovery_of_fri_drop"] is not None]
        rows.append({"theme": k, "n": len(v), "mean_fri": sum(m["fri_change"] for m in v) / len(v), "mean_mon": sum(m["mon_change"] for m in v) / len(v),
                     "mean_recovery": sum(rec) / len(rec) if rec else None, "tickers": [m["ticker"] for m in v]})
    return sorted(rows, key=lambda r: -r["mean_mon"])
