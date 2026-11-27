"""Persistent per-ticker profile JSON.

VALUATION TRACK  (what the business is worth on estimates): EPS growth path, weighted EPS, multiple-modifier events.
TRADING TRACK    (what the tape says): 1:x ratios vs NVDA/MSFT/SMH/QQQ, relative performance, price zones, repeat
                 traversals, extreme low vs rebound.
RECONCILIATION   how much of the price move since the peak was EPS vs multiple.
EXCHANGE GRID    when is swapping this name for a reference profitable, under a grid of reference outcomes.
The tracks never read each other's inputs.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

from . import history as hist
from . import portfolio as pf
from . import store
from . import trading as tr
from .calendarize import extend
from .metrics import build_view

SUBJECTS = ("NVDA", "CRWV", "SNDK")
BENCH = ("MSFT", "SMH", "QQQ")
ALL = SUBJECTS + BENCH
REFS = ("NVDA", "MSFT", "SMH", "QQQ")
SCHEMA = "rotation.profile/1"
WEIGHTS_EPS = {"ttm": 0.20, "ntm": 0.40, "cy1": 0.25, "cy2": 0.15}


def _r(x, nd=6):
    if isinstance(x, float):
        return None if (math.isnan(x) or math.isinf(x)) else round(x, nd)
    if isinstance(x, dict):
        return {k: _r(v, nd) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_r(v, nd) for v in x]
    if isinstance(x, date):
        return x.isoformat()
    return x


def load_universe(data: Path, asof: date, include_prov: bool) -> dict:
    bars, closes, vols = {}, {}, {}
    for t in SUBJECTS:
        b = store.load_bars(data / "prices" / f"{t}.csv", asof)
        bars[t], closes[t], vols[t] = b, [(x["date"], x["close"]) for x in b], [x["volume"] for x in b]
    with (data / "prices" / "benchmarks_close.csv").open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if store.d(r["date"]) <= asof]
    for t in BENCH:
        closes[t] = [(store.d(r["date"]), float(r[t])) for r in rows]
    prov = {}
    pp = data / "prices" / "PROVISIONAL.csv"
    if include_prov and pp.exists():
        for r in store._rows(pp):
            prov[r["ticker"]] = {"date": store.d(r["date"]), "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]),
                                 "close": float(r["close"]), "volume": float(r["volume"]), "status": r["status"]}
    return {"bars": bars, "closes": closes, "vols": vols, "prov": prov}


def _react(closes: list[tuple[date, float]], when: date, timing: str, prov: dict | None = None) -> dict | None:
    dates = [t for t, _ in closes]
    cl = [c for _, c in closes]
    if prov and when == prov["date"]:
        return {"day": when, "modifier": prov["close"] / cl[-1], "provisional": True}
    i = next((k for k, t in enumerate(dates) if t >= when), None)
    if i is None:
        return None
    j, p = (i + 1, i) if timing == "AMC" else (i, i - 1)
    if j >= len(cl) or p < 0:
        return None
    return {"day": dates[j], "modifier": cl[j] / cl[p], "provisional": False}


def events_block(t: str, data: Path, u: dict, asof: date) -> dict:
    qqq, prov = u["closes"]["QQQ"], u["prov"]
    out = {"realized": [], "scheduled": [], "hypothetical": []}
    rows = store._rows(data / "multiple_events.csv")
    earn_mods = []
    for r in rows:
        if r["ticker"] not in ("*", t):
            continue
        base = {"date": r["date"] or None, "type": r["type"], "description": r["description"], "source": r["source"], "eps_changed": r["eps_changed"] or None}
        if r["status"] in ("realized", "realized_provisional"):
            pv = prov.get(t) if r["status"] == "realized_provisional" else None
            when = store.d(r["date"])
            m = _react(u["closes"][t], when, r["timing"], pv)
            q = _react(qqq, when, r["timing"], prov.get("QQQ") if pv else None)
            if not m:
                continue
            base.update({"reaction_day": m["day"], "multiple_modifier": m["modifier"], "market_adjusted_modifier": m["modifier"] / q["modifier"] if q else None,
                         "provisional": m["provisional"],
                         "attribution": "mix of EPS revision and multiple" if r["eps_changed"] == "yes" else "multiple (estimates unchanged that day)"})
            out["realized"].append(base)
            if r["type"] == "earnings" and not m["provisional"]:
                earn_mods.append(m["modifier"])
        elif r["status"] == "scheduled":
            out["scheduled"].append(base)
        else:
            an = _react(u["closes"][t], store.d(r["analog_date"]), "INTRADAY")
            if an:
                mod = 1 / an["modifier"] if "inverse" in r["source"] else an["modifier"]
                base.update({"modifier_from_analog": mod, "analog_date": r["analog_date"], "kind": "assumption: scale borrowed from a past tape event"})
            out["hypothetical"].append(base)
    out["realized"].sort(key=lambda e: e["date"])
    if earn_mods:
        out["earnings_reaction_history"] = {"n": len(earn_mods), "mean_abs_move": sum(abs(m - 1) for m in earn_mods) / len(earn_mods), "moves": [m - 1 for m in earn_mods]}
    for s in out["scheduled"]:
        s["modifier"] = None
        s["note"] = "unknown until the print; use earnings_reaction_history for scale"
    return out


def growth_path(t: str, data: Path, asof: date, view) -> dict:
    ests = store.load_estimates(data / "estimates.csv", asof).get((t, "eps"), {})
    fy = {y: e.value for y, e in ests.items()}
    path = []
    if fy:
        fye = next(iter(ests.values())).fye_month
        ext, added = extend(fy, max(fy) + 3)
        prev = None
        for y in sorted(ext):
            e = ests.get(y)
            path.append({"fiscal_year": y, "eps": ext[y], "yoy": (ext[y] / prev - 1) if prev else None,
                         "kind": e.kind if e else "extrapolated", "basis": e.basis if e else "fade 0.8x of last growth, capped -20%..+50%",
                         "source": e.source if e else "calendarize.extend"})
            prev = ext[y]
    rows = hist.load_fund(data / "fundamentals" / f"{t}_quarterly.csv")
    q, prev = [], None
    for r in rows[-6:]:
        q.append({"period_end": r["period_end"], "eps_gaap_norm": r["eps_norm"], "revenue": r["revenue"],
                  "qoq_eps": (r["eps_norm"] / prev - 1) if prev and prev > 0 else None, "split_k_applied": r["split_k"]})
        prev = r["eps_norm"]
    g = store.load_guidance(data / "guidance.csv", asof)
    guide = [{"metric": m, "period": v["period"], "low": v["low"], "high": v["high"], "annualized_mid": v["mid"] * v["annualize"], "basis": v["basis"],
              "source": v["source"]} for (tk, m), v in g.items() if tk == t]
    consec = 0
    for p in path:
        if p["yoy"] is not None and p["yoy"] > 0:
            consec += 1
        elif p["yoy"] is not None:
            break
    return {"fiscal_year_path": path, "consecutive_growth_years_in_path": consec, "quarterly_actuals_gaap_norm": q, "guidance": guide}


def weighted_metric(t: str, data: Path, asof: date, view, price: float) -> dict:
    rows = hist.load_fund(data / "fundamentals" / f"{t}_quarterly.csv")
    tt = hist.ttm_at(rows, asof) if rows else None
    guide = store.load_guidance(data / "guidance.csv", asof)
    comps, metric = {}, "eps"
    if tt and tt["eps"] > 0:
        comps["ttm"] = tt["eps"]
    if view.ntm_eps:
        comps["ntm"] = view.ntm_eps
        for k, y in (("cy1", asof.year + 1), ("cy2", asof.year + 2)):
            if view.eps.get(y):
                comps[k] = view.eps[y]
    elif (t, "eps") in guide:
        g = guide[(t, "eps")]
        comps["ntm"] = g["mid"] * g["annualize"]
    if not comps:
        metric = "revenue_per_share"
        sh = tt["sh"] if tt else None
        if tt and sh:
            comps["ttm"] = tt["revenue"] / sh
        g = guide.get((t, "revenue"))
        if g and sh:
            comps["ntm"] = g["mid"] * g["annualize"] * 1e9 / sh
    w = {k: WEIGHTS_EPS[k] for k in comps}
    tot = sum(w.values()) or 1
    wv = sum(comps[k] * w[k] / tot for k in comps) if comps else None
    return {"metric": metric, "components": comps, "weights_used": {k: v / tot for k, v in w.items()}, "weighted_value": wv,
            "price_to_weighted": (price / wv) if wv and wv > 0 else None,
            "price_to_each": {k: (price / v if v > 0 else None) for k, v in comps.items()}}


def reconciliation(t: str, data: Path, u: dict, asof: date) -> dict | None:
    rows = hist.load_fund(data / "fundamentals" / f"{t}_quarterly.csv")
    cl = u["closes"][t][-252:]
    if not rows or len(cl) < 30:
        return None
    pk = max(cl, key=lambda z: z[1])
    now_t, now_p = cl[-1]
    a, b = hist.ttm_at(rows, pk[0]), hist.ttm_at(rows, asof)
    if not (a and b):
        return None
    use_eps = a["eps"] > 0 and b["eps"] > 0
    f = (lambda x, p: p / x["eps"]) if use_eps else (lambda x, p: p * x["sh"] / x["revenue"])
    base = (lambda x: x["eps"]) if use_eps else (lambda x: x["revenue"] / x["sh"])
    m0, m1 = f(a, pk[1]), f(b, now_p)
    fund = base(b) / base(a) - 1
    mult = m1 / m0 - 1
    out = {"basis": "ttm_gaap_eps_norm" if use_eps else "ttm_revenue_per_share (EPS<=0)", "peak_date": pk[0], "price_peak": pk[1], "price_now": now_p,
           "ttm_then": base(a), "ttm_now": base(b), "trailing_multiple_then": m0, "trailing_multiple_now": m1,
           "price_change": now_p / pk[1] - 1, "fundamental_component": fund, "multiple_component": mult,
           "identity_check": (1 + fund) * (1 + mult) - 1}
    pv = u["prov"].get(t)
    if pv:
        m2 = f(b, pv["close"])
        out["provisional"] = {"price": pv["close"], "price_change_vs_peak": pv["close"] / pk[1] - 1, "trailing_multiple": m2,
                              "multiple_recovered_of_decline": (m2 - m1) / (m0 - m1) if m0 != m1 else None}
    return out


def exchange_grid(t: str, data: Path, asof: date, price: float, rels: dict, hurdle: float, cost: float, horizon: int = 12) -> dict | None:
    tg = pf.load_targets(data / "targets.csv", asof, horizon)
    if t not in tg:
        return None
    ret = pf.normalise_returns(tg[t]["raw"], price, asof, horizon)
    exp = 0.25 * ret["bear"] + 0.5 * ret["base"] + 0.25 * ret["bull"]
    src = " ".join(r["source"] for r in tg[t]["raw"].values())
    out = {"subject_returns_from_targets": {**ret, "exp": exp}, "targets_source": src[:160], "hurdle": hurdle, "round_trip_cost": cost, "vs": {}}
    for ref, rel in rels.items():
        if not rel:
            continue
        grid = {}
        for rr in (-0.20, -0.10, 0.0, 0.10, 0.20, 0.30):
            be = (1 + rr) * (1 + hurdle) / (1 - cost) - 1
            grid[f"{rr:+.0%}"] = {"breakeven_subject_return": be, **{k: ret[k] > be for k in ("bear", "base", "bull")}, "exp": exp > be}
        out["vs"][ref] = {"spot_x": rel["x_now"], "reading": "holding REF instead of SUBJECT is profitable only if the SUBJECT return clears breakeven; "
                          "cells show whether each subject scenario clears it for each assumed REF return", "grid_by_ref_return": grid}
    return out


def build_profile(t: str, data: Path, asof: date, include_prov: bool = True, hurdle: float = 0.08, cost: float = 0.002) -> dict:
    meta = json.loads((data / "profile_meta.json").read_text()).get(t, {})
    u = load_universe(data, asof, include_prov)
    snaps = store.load_ratios(data / "ratios.csv", asof)
    ests = store.load_estimates(data / "estimates.csv", asof)
    cl = u["closes"][t]
    final_date, price = cl[-1]
    rels = {ref: tr.relationship(cl, u["closes"][ref]) for ref in REFS if ref != t}
    wfile = json.loads((data / "relationship_weights.json").read_text()) if (data / "relationship_weights.json").exists() else {}
    wov = wfile.get(t)
    if wov:
        s = sum(wov.values()) or 1
        weights, wmethod = {k: v / s for k, v in wov.items()}, "manual override (relationship_weights.json)"
    else:
        weights, wmethod = tr.default_weights(rels), "250d R^2 of daily returns vs each reference, normalised"
    prov = u["prov"].get(t)
    prov_rel = {}
    if prov:
        for ref, rel in rels.items():
            pr = u["prov"].get(ref)
            if rel and pr:
                prov_rel[ref] = {"x_provisional": prov["close"] / pr["close"], "x_final": rel["x_now"], "change": (prov["close"] / pr["close"]) / rel["x_now"] - 1,
                                 "within_p10_p90": rel["p10"] <= prov["close"] / pr["close"] <= rel["p90"]}
    bars = u["bars"].get(t)
    trading = {"as_of_final": final_date, "last_final_close": price,
               "relationships": {k: v for k, v in rels.items() if v}, "relationship_weights": {"method": wmethod, "values": weights},
               "weighted_relative_return": {f"{n}d": sum(weights[k] * rels[k]["relative_return"][f"{n}d"] for k in weights if rels.get(k) and rels[k]["relative_return"].get(f"{n}d") is not None) for n in (5, 20, 60)},
               "provisional_ratios_vs_refs": prov_rel or None}
    if bars:
        trading["extremes_and_rebound"] = tr.extremes_and_rebound(bars, prov)
        vols = u["vols"][t]
        trading["zones_top"] = [{k: v for k, v in z.items() if k != "_k"} for z in tr.zones(cl, vols)]
        e = trading["extremes_and_rebound"]
        lv = {"final_low": e["last_final_bar"]["low"], "final_close": e["last_final_bar"]["close"], "52w_high": e["window_52w"]["high"]}
        if prov:
            lv.update({"provisional_open": prov["open"], "provisional_last": prov["close"]})
        trading["key_levels"] = {k: {**tr.zone_of(v, cl, vols), **tr.level_crossings(cl, v)} for k, v in lv.items()}
    else:
        trading["zones_top"] = [{k: v for k, v in z.items() if k != "_k"} for z in tr.zones(cl, None)]
        trading["key_levels"] = {"final_close": {**tr.zone_of(price, cl, None), **tr.level_crossings(cl, price)}}
        if prov:
            trading["provisional_session"] = {"open": prov["open"], "high": prov["high"], "low": prov["low"], "last": prov["close"],
                                              "last_vs_final_close": prov["close"] / price - 1, "status": prov["status"]}
    if t in SUBJECTS:
        snap = snaps.get(t)
        view = build_view(t, snap, ests, asof) if snap else None
        val = {"basis": "estimates, guidance and reported fundamentals only; no price-action inputs", "track": "valuation",
               "growth_path": growth_path(t, data, asof, view) if view else None,
               "weighted_metric": weighted_metric(t, data, asof, view, snap["price"]) if view else None,
               "multiple_modifier_events": events_block(t, data, u, asof),
               "flags": view.flags if view else None}
        tg = pf.load_targets(data / "targets.csv", asof, 12)
        if t in tg:
            r = pf.normalise_returns(tg[t]["raw"], snap["price"], asof, 12)
            val["scenario_targets_12m"] = {"returns": r, "prices": {k: snap["price"] * (1 + v) for k, v in r.items()},
                                           "source": " ".join(x["source"] for x in tg[t]["raw"].values())[:200]}
        recon = reconciliation(t, data, u, asof)
        ex = exchange_grid(t, data, asof, snap["price"], rels, hurdle, cost) if snap else None
    else:
        sn = snaps.get(t)
        val = {"track": "valuation", "status": "not_modeled", "reason": "benchmark: no estimates/guidance loaded; subject-only modeling",
               "ratios_snapshot": ({"price_to_earnings_ttm": float(sn["price_to_earnings"]), "eps_ttm": float(sn["earnings_per_share"]), "ev_to_sales": float(sn["ev_to_sales"])}
                                   if sn and sn.get("price_to_earnings") else None)}
        recon, ex = None, None
    prof = {"schema": SCHEMA, "ticker": t, "generated_for_asof": asof, "final_data_through": final_date,
            "provisional_included": bool(prov), "provisional_note": "intraday bar at 2026-11-23 13:42 ET; not a close" if prov else None,
            "identity": meta, "valuation": val, "trading": trading, "reconciliation": recon, "fair_value_exchange": ex,
            "provenance": {"prices": "Massive /v2/aggs (adjusted)", "fundamentals": "Massive income statements, split-normalised", "estimates": "estimates.csv/guidance.csv (sourced per row)",
                           "events": "multiple_events.csv (headline sources are secondary and unverified)"}}
    return _r(prof)


def write_all(data: Path, asof: date, include_prov: bool = True, hurdle: float = 0.08, cost: float = 0.002) -> list[Path]:
    out = []
    pdir = data / "profiles"
    pdir.mkdir(exist_ok=True)
    for t in ALL:
        p = pdir / f"{t}.json"
        p.write_text(json.dumps(build_profile(t, data, asof, include_prov, hurdle, cost), indent=2) + "\n")
        out.append(p)
    return out
