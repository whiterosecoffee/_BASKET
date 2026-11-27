"""Per-stock model JSON (`rotation.model/1`) and the stress-relativity tracker (`rotation.relativity/1`).

Anchor moments: a0 52-week high | a1 pre-compression close (Thu) | a2 52-week low / stress low (Friday low when it set the low)
                | a3 rebound peak (Mon high) | a4 snapshot last. Monday values are provisional.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from datetime import date
from pathlib import Path

from . import bands as bd
from . import history as hist
from . import multiplepoints as mp
from . import pointcompare as pc
from . import store

REFS = ("NVDA", "MSFT", "SMH", "QQQ")
ANCH = ("fri_low", "fri_close", "mon_high", "mon_last")


def _log_pos(p, lo, hi):
    return (math.log(p) - math.log(lo)) / (math.log(hi) - math.log(lo)) if hi > lo > 0 and p > 0 else None


def load_ranges(path: Path) -> dict:
    out = {}
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            out[r["ticker"]] = {"n_days": int(r["n_days"]), "first": r["first_date"], "low": float(r["low_through_1119"]), "high": float(r["high_through_1119"]),
                                "low_date": r["low_date"], "high_date": r["high_date"]}
    return out


def _e_basis(t: str, rat: dict) -> tuple[float | None, str | None]:
    r = rat.get(t)
    if not r:
        return None, None
    if r["eps"] > 0:
        return r["eps"], "eps_ttm_massive"
    return r["price"] / r["ps"], "sales_per_share_ttm (EPS<=0)"


def pit_series(t: str, data: Path, window_start: date):
    """Point-in-time multiple series for a subject on ONE basis (P/E if TTM EPS>0 now, else P/S), from reported quarters."""
    rows = hist.load_fund(data / "fundamentals" / f"{t}_quarterly.csv")
    bars = [b for b in store.load_bars(data / "prices" / f"{t}.csv", date(2026, 11, 20)) if b["date"] >= window_start]
    if not rows or not bars:
        return None
    tt = hist.ttm_at(rows, date(2026, 11, 20))
    use_eps = bool(tt and tt["eps"] > 0)
    series = []
    for b in bars:
        x = hist.ttm_at(rows, b["date"])
        if not x:
            continue
        e = x["eps"] if use_eps else x["revenue"] / x["sh"]
        if e > 0:
            series.append((b["date"], b["close"] / e, e))
    if not series:
        return None
    e_now = tt["eps"] if use_eps else tt["revenue"] / tt["sh"]
    return {"basis": "pit_ttm_gaap_eps_norm" if use_eps else "pit_ttm_sales_per_share", "series": series, "e_now": e_now, "rows": rows, "bars": bars}


def pit_bands(t: str, data: Path, p: dict) -> dict | None:
    """Tiers from the point-in-time multiple range actually seen in the 52-week window, plus the reported EPS updates against them."""
    ps = pit_series(t, data, date(2025, 11, 21))
    if not ps:
        return None
    ms = [m for _, m, _ in ps["series"]]
    m_hi_d, m_hi = max(((d, m) for d, m, _ in ps["series"]), key=lambda z: z[1])
    m_lo_series = min(ms)
    m_lo_fri = p["fri_low"] / ps["e_now"]
    m_lo = min(m_lo_series, m_lo_fri)
    if m_hi <= m_lo:
        return None
    b = bd.tier_bounds(m_lo, m_hi)
    e = ps["e_now"]
    eps_changes = [x[2] for x in ps["series"]]
    out = {"basis": ps["basis"], "first_valid_date": ps["series"][0][0], "n_obs": len(ps["series"]), "e_now": e,
           "multiple_low": m_lo, "multiple_high": m_hi, "multiple_high_date": m_hi_d, "eps_range_in_window": [min(eps_changes), max(eps_changes)],
           "eps_change_factor_in_window": max(eps_changes) / min(eps_changes), "multiple_bounds": b, "price_bands_at_current_E": bd.price_bands(e, b),
           "tier_at_points": {k: bd.tier_of(p[k] / e, b) for k in ("thu_close",) + ANCH}, "after_eps_update_scenarios_at_mon_last": bd.scenario_grid(p["mon_last"], e, b)}
    cl = {x["date"]: x["close"] for x in ps["bars"]}
    dates = sorted(cl)
    hist_rows, prev = [], None
    for r in ps["rows"]:
        tt = hist.ttm_at(ps["rows"], r["avail"])
        if not tt:
            continue
        ev = tt["eps"] if ps["basis"] == "pit_ttm_gaap_eps_norm" else tt["revenue"] / tt["sh"]
        if prev is not None and ev > 0 and prev > 0:
            d0 = next((d for d in dates if d >= r["avail"]), None)
            if d0:
                hist_rows.append({"update_date": r["avail"], "period_end": r["period_end"], "price_at_update": cl[d0], **bd.eps_update_effect(cl[d0], prev, ev, b)})
        prev = ev
    out["reported_eps_update_history"] = hist_rows[-4:]
    return out


def build_one(t: str, data: Path, pts, rat, rng, themes, meta) -> dict | None:
    p = pts.get(t)
    r = rng.get(t)
    if not (p and r and "mon_high" in p):
        return None
    prior_low, hi = r["low"], r["high"]
    hit = p["fri_low"] <= prior_low
    lo = min(prior_low, p["fri_low"])
    lo_date = "2026-11-20" if hit else r["low_date"]
    th = next((k for k, v in themes.items() if not k.startswith("_") and t in v), "other")
    pos = {k: _log_pos(p[k], lo, hi) for k in ANCH + ("thu_close",)}
    drop = p["thu_close"] - p["fri_close"]
    rec = lambda k: (p[k] - p["fri_low"]) / (hi - p["fri_low"]) if hi > p["fri_low"] else None
    model = {
        "schema": "rotation.model/1", "ticker": t, "theme": th, "provisional_monday": True, "monday_snapshot_et": meta.get("as_of_et"),
        "window_52w": {"basis": f"daily bars {r['first']}..2026-11-19 plus Friday low; n={r['n_days']}" + (" (since listing)" if r["n_days"] < 240 else ""),
                       "low": lo, "low_date": lo_date, "high": hi, "high_date": r["high_date"], "hit_52w_low_on_friday": hit,
                       "prior_52w_low_before_friday": prior_low, "range_log_width": math.log(hi / lo)},
        "anchor_moments": {"a0_52w_high": {"price": hi, "date": r["high_date"]}, "a1_pre_compression_thu_close": p["thu_close"],
                           "a2_stress_low_fri_low": p["fri_low"], "a2_fri_close": p["fri_close"], "a3_rebound_peak_mon_high": p["mon_high"],
                           "a4_last_snapshot": p["mon_last"], "mon_open": p["mon_open"], "mon_low": p["mon_low"]},
        "stress_relativity": {
            "drawdown_52w_high_to_fri_low": p["fri_low"] / hi - 1, "drawdown_52w_high_to_fri_close": p["fri_close"] / hi - 1,
            "fri_close_vs_52w_low": p["fri_close"] / lo - 1,
            "rebound_fri_low_to_peak": p["mon_high"] / p["fri_low"] - 1, "rebound_fri_close_to_last": p["mon_last"] / p["fri_close"] - 1,
            "recovery_of_friday_drop_at_peak": (p["mon_high"] - p["fri_close"]) / drop if drop > 0 else None,
            "recovery_of_friday_drop_at_last": (p["mon_last"] - p["fri_close"]) / drop if drop > 0 else None,
            "recovery_of_52w_range_at_peak": rec("mon_high"), "recovery_of_52w_range_at_last": rec("mon_last"),
            "position_in_52w_log_range": pos},
        "relativity": {},
    }
    for ref in REFS:
        if ref == t or ref not in pts or "mon_last" not in pts[ref]:
            continue
        q = pts[ref]
        x = {k: p[k] / q[k] for k in ANCH}
        model["relativity"][ref] = {"unit": f"1 {t} = x {ref}", "x": x, "x_change_fri_close_to_last": x["mon_last"] / x["fri_close"] - 1,
                                    "x_change_fri_low_to_peak": x["mon_high"] / x["fri_low"] - 1}
    e, basis = _e_basis(t, rat)
    if e:
        m_lo, m_hi = lo / e, hi / e
        b = bd.tier_bounds(m_lo, m_hi)
        model["eps_state"] = {"basis": basis, "e_now": e, "note": "52-week extremes may have occurred under different earnings; tiers are a constant-current-E counterfactual",
                              "tiers_basis": "constant_current_E_counterfactual"}
        model["bands"] = {"tiers_basis": "constant_current_E_counterfactual", "multiple_bounds": b, "price_bands_at_current_E": bd.price_bands(e, b),
                          "tier_at_points": {k: bd.tier_of(p[k] / e, b) for k in ("thu_close",) + ANCH},
                          "tier_migration_fri_low_to_peak": bd.tier_of(p["mon_high"] / e, b)["tier"] - bd.tier_of(p["fri_low"] / e, b)["tier"],
                          "after_eps_update_scenarios_at_mon_last": bd.scenario_grid(p["mon_last"], e, b)}
        if t in ("NVDA", "CRWV", "SNDK"):
            model["bands_point_in_time"] = pit_bands(t, data, p)
    else:
        b = bd.tier_bounds(lo, hi)
        model["eps_state"] = {"basis": None, "note": "no earnings basis in the loaded data; price-only tiers"}
        model["bands"] = {"tiers_basis": "price_only", "bounds": b, "tier_at_points": {k: bd.tier_of(p[k], b) for k in ("thu_close",) + ANCH}}
    return model


def build_all(data: Path) -> tuple[dict[str, dict], dict]:
    cdir = data / "cohort"
    pts, meta = pc.load_points(cdir)
    rat = mp.load_ratios(cdir / "ratios_20261120_massive.csv")
    rng = load_ranges(cdir / "range52w_through_20261119.csv")
    themes = json.loads((cdir / "peer_groups_by_industry.json").read_text())
    models = {t: m for t in sorted(pts) if (m := build_one(t, data, pts, rat, rng, themes, meta))}
    return models, meta


def relativity(models: dict[str, dict], meta: dict) -> dict:
    eq = {t: m for t, m in models.items() if m["theme"] != "benchmarks"}
    def rank(key):
        xs = sorted(((m["stress_relativity"][key], t) for t, m in eq.items() if m["stress_relativity"].get(key) is not None), reverse=True)
        return [{"rank": i + 1, "ticker": t, "value": v, "hit_52w_low_friday": eq[t]["window_52w"]["hit_52w_low_on_friday"], "theme": eq[t]["theme"]} for i, (v, t) in enumerate(xs)]
    hit = [t for t, m in eq.items() if m["window_52w"]["hit_52w_low_on_friday"]]
    rr = sorted((m["stress_relativity"]["recovery_of_52w_range_at_last"], t) for t, m in eq.items())
    n = len(rr)
    tiers = {}
    for i, (v, t) in enumerate(rr):
        tiers[t] = "laggard" if i < n / 3 else ("leader" if i >= 2 * n / 3 else "middle")
    def grp(ts, key):
        xs = [eq[t]["stress_relativity"][key] for t in ts if eq[t]["stress_relativity"].get(key) is not None]
        return {"n": len(xs), "median": statistics.median(xs), "min": min(xs), "max": max(xs)} if xs else {}
    vs = {}
    for ref in REFS:
        rows = sorted(((m["relativity"][ref]["x_change_fri_close_to_last"], t) for t, m in eq.items() if ref in m["relativity"]), reverse=True)
        vs[ref] = [{"rank": i + 1, "ticker": t, "x_change": v} for i, (v, t) in enumerate(rows)]
    return {
        "schema": "rotation.relativity/1", "comparison_id": "stress_relativity__52w_low_to_rebound__2026-11-23", "provisional": True, "as_of_et": meta.get("as_of_et"),
        "definition": {"stress_moment": "Friday 2026-11-20 (many names set or approached their 52-week lows)", "hit_52w_low_on_friday": "Friday low <= the lowest low of the prior 52 weeks (since listing for new issues)",
                       "recovery_of_52w_range": "(price - fri_low) / (52w_high - fri_low)", "recovery_of_friday_drop": "(price - fri_close) / (thu_close - fri_close)"},
        "n_equities": len(eq), "hit_52w_low_on_friday": sorted(hit), "share_hit_52w_low_on_friday": len(hit) / len(eq),
        "group_stats": {"hit_low": {"recovery_of_52w_range_at_last": grp(hit, "recovery_of_52w_range_at_last"), "recovery_of_friday_drop_at_last": grp(hit, "recovery_of_friday_drop_at_last"), "rebound_fri_close_to_last": grp(hit, "rebound_fri_close_to_last")},
                        "did_not_hit_low": {"recovery_of_52w_range_at_last": grp([t for t in eq if t not in hit], "recovery_of_52w_range_at_last"), "recovery_of_friday_drop_at_last": grp([t for t in eq if t not in hit], "recovery_of_friday_drop_at_last"), "rebound_fri_close_to_last": grp([t for t in eq if t not in hit], "rebound_fri_close_to_last")}},
        "rebound_order_by_change_fri_close_to_last": rank("rebound_fri_close_to_last"),
        "order_by_recovery_of_friday_drop_at_last": rank("recovery_of_friday_drop_at_last"),
        "order_by_recovery_of_52w_range_at_last": rank("recovery_of_52w_range_at_last"),
        "recovery_tiers_by_52w_range_terciles": tiers,
        "ratio_change_vs_reference_fri_close_to_last": vs,
        "caveats": ["Monday values are intraday and provisional", "Recovery of the 52-week range is small for names far above their lows; it measures distance travelled back from the stress low, not valuation",
                    "Terciles are rank-based and relative to this cohort only"]}


def write_all(data: Path) -> dict:
    models, meta = build_all(data)
    mdir = data / "models"
    mdir.mkdir(exist_ok=True)
    for t, m in models.items():
        (mdir / f"{t}.json").write_text(json.dumps(m, indent=2, default=str) + "\n")
    rel = relativity(models, meta)
    rdir = data / "relativity"
    rdir.mkdir(exist_ok=True)
    (rdir / "stress_relativity__52w_low_to_rebound__2026-11-23.json").write_text(json.dumps(rel, indent=2, default=str) + "\n")
    return {"models": len(models), "relativity": rel}
