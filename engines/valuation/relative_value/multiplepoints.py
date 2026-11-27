"""Valuation multiples at named price points (e.g. the extreme low and the rebound peak). Contract: research/models/rotation/AGENTS.md.

Trailing P/E at a point = point price / EPS. The EPS is held FIXED at the latest reported TTM (so differences between points
are pure price/multiple, no earnings change). The cohort uses Massive's ratio EPS (one consistent basis); the three subjects also
get a second basis from the repository's split-normalised GAAP fundamentals and, where available, a forward basis.
"""
from __future__ import annotations

import csv
import statistics
from pathlib import Path

POINT_ORDER = ("thu_close", "fri_close", "fri_low", "mon_open", "mon_high", "mon_last")
ROLE = {"fri_low": "max_compression", "mon_high": "peak_rebound", "thu_close": "pre_compression", "fri_close": "last_final_close",
        "mon_open": "rebound_open", "mon_last": "snapshot_last"}


def load_ratios(path: Path) -> dict[str, dict]:
    out = {}
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            out[r["ticker"]] = {"price": float(r["price"]), "mcap": float(r["market_cap"]), "eps": float(r["eps_ttm"]), "pe": float(r["pe_ttm"]) if r["pe_ttm"] else None,
                                "ps": float(r["ps"]), "evs": float(r["ev_to_sales"]), "ev": float(r["enterprise_value"]), "date": r["date"]}
    return out


def multiples_at(points: dict[str, float], rat: dict) -> dict:
    """P/E (if EPS>0), P/S and EV/S at each point; sales and share count held fixed."""
    base = rat["price"]
    pe, ps, evs = {}, {}, {}
    netdebt = rat["ev"] - rat["mcap"]
    for k in POINT_ORDER:
        p = points.get(k)
        if p is None:
            continue
        pe[k] = p / rat["eps"] if rat["eps"] > 0 else None
        ps[k] = rat["ps"] * p / base
        ev_p = rat["mcap"] * p / base + netdebt
        evs[k] = rat["evs"] * ev_p / rat["ev"] if rat["ev"] > 0 else None
    return {"pe": pe, "ps": ps, "evs": evs}


def summarize_pair(d: dict, lo: str = "fri_low", hi: str = "mon_high") -> dict | None:
    if d.get(lo) is None or d.get(hi) is None:
        return None
    return {"at_low": d[lo], "at_peak": d[hi], "turns_added": d[hi] - d[lo], "expansion": d[hi] / d[lo] - 1}


def cohort_stats(rows: list[dict], key: str) -> dict:
    xs = [r[key] for r in rows if r.get(key) is not None]
    if not xs:
        return {}
    return {"n": len(xs), "median": statistics.median(xs), "min": min(xs), "max": max(xs)}


def build(data: Path, asof) -> dict:
    """Assemble the JSON document `rotation.multiples/1` (cohort on one basis, subjects on three)."""
    import json

    from . import history as hist
    from . import pointcompare as pc
    from . import store
    from .metrics import build_view

    cdir = data / "cohort"
    pts, meta = pc.load_points(cdir)
    themes = json.loads((cdir / "peer_groups_by_industry.json").read_text())
    rat = load_ratios(cdir / "ratios_20261120_massive.csv")
    tick, excluded = [], []
    for t, p in sorted(pts.items()):
        if t not in rat:
            excluded.append({"ticker": t, "reason": "no ratios row in Massive (ETF, ADR or not covered)"})
            continue
        m = multiples_at(p, rat[t])
        th = next((k for k, v in themes.items() if not k.startswith("_") and t in v), "other")
        tick.append({"ticker": t, "theme": th, "price_points": {k: p[k] for k in POINT_ORDER if k in p},
                     "eps_ttm_massive": rat[t]["eps"], "pe_ttm": m["pe"], "ps": m["ps"], "ev_to_sales": m["evs"],
                     "pe_low_to_peak": summarize_pair(m["pe"]), "ps_low_to_peak": summarize_pair(m["ps"]),
                     "pe_status": "defined" if rat[t]["eps"] > 0 else "not_meaningful_eps<=0"})
    flat = [{"pe_exp": r["pe_low_to_peak"]["expansion"] if r["pe_low_to_peak"] else None, "ps_exp": r["ps_low_to_peak"]["expansion"],
             "pe_low": r["pe_ttm"].get("fri_low"), "pe_peak": r["pe_ttm"].get("mon_high"), "ps_low": r["ps"].get("fri_low"), "ps_peak": r["ps"].get("mon_high")}
            for r in tick if r["theme"] != "benchmarks"]
    subjects = {}
    for t in ("NVDA", "CRWV", "SNDK"):
        rows = hist.load_fund(data / "fundamentals" / f"{t}_quarterly.csv")
        bars = store.load_bars(data / "prices" / f"{t}.csv", asof)
        cl = [(b["date"], b["close"]) for b in bars]
        pk_d, pk_p = max(cl[-252:], key=lambda z: z[1])
        ttm_now, ttm_then = hist.ttm_at(rows, asof), hist.ttm_at(rows, pk_d)
        p = pts[t]
        sub = {"fifty_two_week_peak_close": {"date": pk_d, "price": pk_p}, "points": {k: p[k] for k in POINT_ORDER if k in p}}
        if ttm_now and ttm_now["eps"] > 0:
            e = ttm_now["eps"]
            sub["fundamentals_gaap_norm_ttm"] = {"eps_now": e, "pe": {k: p[k] / e for k in POINT_ORDER if k in p},
                                                 "pe_at_52w_peak_point_in_time": pk_p / ttm_then["eps"] if ttm_then and ttm_then["eps"] > 0 else None,
                                                 "eps_then": ttm_then["eps"] if ttm_then else None, "pe_52w_peak_price_on_current_eps": pk_p / e,
                                                 "note": "EPS held at the latest TTM; the 52w-peak P/E is shown both on the EPS known then and on today's EPS"}
            lo, hi = p["fri_low"] / e, p["mon_high"] / e
            peak_now = pk_p / e
            sub["fundamentals_gaap_norm_ttm"]["share_of_52w_peak_multiple_lost_at_low"] = 1 - lo / peak_now
            sub["fundamentals_gaap_norm_ttm"]["share_of_that_loss_recovered_at_rebound_peak"] = (hi - lo) / (peak_now - lo)
        snap = store.load_ratios(data / "ratios.csv", asof).get(t)
        if snap:
            view = build_view(t, snap, store.load_estimates(data / "estimates.csv", asof), asof)
            guide = store.load_guidance(data / "guidance.csv", asof)
            fwd, basis = None, None
            if view.ntm_eps and view.ntm_eps > 0:
                fwd, basis = view.ntm_eps, "NTM EPS from estimates.csv (EXTRAPOLATED years flagged in profile)"
            elif (t, "eps") in guide:
                g = guide[(t, "eps")]
                fwd, basis = g["mid"] * g["annualize"], "annualised guided EPS (guidance x factor), run-rate not a forecast"
            if fwd:
                sub["forward"] = {"eps": fwd, "basis": basis, "pe": {k: p[k] / fwd for k in POINT_ORDER if k in p}, "pe_52w_peak_price": pk_p / fwd}
            rv = guide.get((t, "revenue"))
            if rv and snap["enterprise_value"]:
                nd = snap["enterprise_value"] - snap["market_cap"]
                rev = rv["mid"] * rv["annualize"] * 1e9
                sub["ev_to_guided_annualised_revenue"] = {"revenue_usd": rev, "basis": f"{rv['period']} guidance midpoint x {rv['annualize']}; net debt and share count held at 2026-11-20",
                                                          "ev_s": {k: (snap["market_cap"] * p[k] / snap["price"] + nd) / rev for k in POINT_ORDER if k in p},
                                                          "ev_s_52w_peak_price": (snap["market_cap"] * pk_p / snap["price"] + nd) / rev}
        subjects[t] = sub
    return {
        "schema": "rotation.multiples/1", "comparison_id": "multiples_at_max_compression_and_peak_rebound__2026-11-23",
        "definitions": {"max_compression": "fri_low: 2026-11-20 session low (final), the lowest print of the drawdown for the three subjects",
                        "peak_rebound": "mon_high: 2026-11-23 session high at the snapshot (PROVISIONAL)", "pre_compression": "thu_close", "last_final_close": "fri_close"},
        "as_of_et": meta.get("as_of_et"), "provisional": True,
        "method": "multiple at a point = point price / fixed EPS (or sales); earnings are held constant so the change between points is price (multiple) only",
        "bases": {"cohort": "Massive ratios EPS_ttm as of 2026-11-20 (one consistent basis; GAAP-like and can lag the latest quarter)",
                  "subjects_extra": ["split-normalised GAAP TTM from fundamentals/*.csv (includes the latest reported quarter)", "forward: NTM estimate or annualised guidance"]},
        "subjects": subjects,
        "cohort_summary": {"n": len(flat), "pe_expansion_low_to_peak_median": cohort_stats(flat, "pe_exp"), "ps_expansion_low_to_peak_median": cohort_stats(flat, "ps_exp"),
                           "pe_at_low": cohort_stats(flat, "pe_low"), "pe_at_peak": cohort_stats(flat, "pe_peak"), "ps_at_low": cohort_stats(flat, "ps_low"), "ps_at_peak": cohort_stats(flat, "ps_peak"),
                           "n_pe_not_meaningful": sum(1 for r in tick if r["theme"] != "benchmarks" and r["pe_status"] != "defined")},
        "per_ticker": tick, "excluded": excluded,
        "caveats": ["Monday points are provisional", "EPS held fixed, so this isolates the multiple and ignores any earnings revision in the window",
                    "Massive EPS can be GAAP with one-offs (e.g. LITE -72.56) and lags the newest quarter; P/E is blank when EPS <= 0 and P/S is shown instead"]}
