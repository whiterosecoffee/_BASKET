"""Basket-wide stress/rebound metrics over the full tracked universe (manifest snapshot from branch work/146, plus additions).

Read-only use of the universe manifest: this module never writes to `_TICKERS/`. Grouping uses the user's own basket_groups and the
manifest's instrument_type; no new classification is invented here.
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

from . import cohort as co

ADDITIONS = {"FLEX": "equity_or_depositary_receipt", "HIMX": "equity_or_depositary_receipt", "INOD": "equity_or_depositary_receipt", "TTMI": "equity_or_depositary_receipt",
             "IBIDY": "equity_or_depositary_receipt", "CXMT-USD": "equity_or_depositary_receipt"}


def load_universe(udir: Path) -> dict[str, dict]:
    m = json.loads((udir / "basket_manifest_work146_snapshot.json").read_text())
    uni = {r["symbol"]: {"type": r["instrument_type"], "groups": r["basket_groups"], "in_manifest": True} for r in m["records"]}
    for s, ty in ADDITIONS.items():
        uni.setdefault(s, {"type": ty, "groups": ["added_2026_11_23_from_user_screenshots"], "in_manifest": False})
    return uni


def load_points(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"ticker": r["ticker"], "thu": float(r["thu_close_1119"]), "f_low": float(r["fri_low_1120"]), "f_high": float(r["fri_high_1120"]),
                         "f_close": float(r["fri_close_1120"]), "m_open": float(r["mon_open_1123"]), "m_high": float(r["mon_high_1123"]),
                         "m_low": float(r["mon_low_1123"]), "m_last": float(r["mon_last_1123"])})
    return rows


def load_low52(path: Path) -> dict[str, bool]:
    """Exact Friday 52-week-low classification (stage-2 exact bars for candidates; all other names were eliminated by sampled lows)."""
    if not path.exists():
        return {}
    with path.open(newline="") as f:
        return {r["ticker"]: r["hit"] == "1" for r in csv.DictReader(f)}


def sympathy(ms: list[dict], cdir: Path) -> dict:
    from . import sympathy as sy
    groups = {k: v for k, v in json.loads((cdir / "peer_groups_by_industry.json").read_text()).items() if not k.startswith("_") and k != "benchmarks"}
    out = {}
    for key in ("fri_change", "mon_change"):
        out[key] = sy.analyse({m["ticker"]: m[key] for m in ms}, groups)
    return out


def _stat(xs):
    xs = [x for x in xs if x is not None]
    return {"n": len(xs), "median": statistics.median(xs), "mean": sum(xs) / len(xs), "min": min(xs), "max": max(xs)} if xs else {}


def run(udir: Path) -> dict:
    uni = load_universe(udir)
    rows = load_points(udir / "basket_points_20261119_23.csv")
    ms = co.metrics(rows, {}, {})
    for m in ms:
        u = uni.get(m["ticker"], {"type": "unknown", "groups": []})
        m["instrument_type"], m["basket_groups"] = u["type"], u["groups"]
        m["peak_change"] = m["mon_change_massive"]  # last vs Friday close (kept explicit)
    by_type: dict[str, list[dict]] = {}
    for m in ms:
        by_type.setdefault(m["instrument_type"], []).append(m)
    by_group: dict[str, list[dict]] = {}
    for m in ms:
        if m["instrument_type"] == "equity_or_depositary_receipt":
            for g in m["basket_groups"]:
                by_group.setdefault(g, []).append(m)
    eq = by_type.get("equity_or_depositary_receipt", [])
    fd = by_type.get("fund_or_etp", [])
    cs = co.cross_section([dict(m, theme="x") for m in eq])
    low52 = load_low52(udir / "low52w_friday_classification.csv")
    hits = sorted(t for t, v in low52.items() if v)
    covered = {m["ticker"] for m in ms}
    missing = sorted(s for s, u in uni.items() if u["type"] in ("equity_or_depositary_receipt", "fund_or_etp") and s not in covered)
    def block(v):
        return {"n": len(v), "fri_change": _stat([m["fri_change"] for m in v]), "mon_change": _stat([m["mon_change"] for m in v]),
                "recovery_of_friday_drop": _stat([m["recovery_of_fri_drop"] for m in v]),
                "share_above_thursday_close": sum(m["above_thu_close"] for m in v) / len(v), "share_gap_unfilled": sum(m["gap_unfilled"] for m in v) / len(v)}
    order = sorted(eq, key=lambda m: -m["mon_change"])
    return {
        "schema": "rotation.basket_rebound/1", "as_of_et": "2026-11-23T13:51", "provisional": True,
        "universe": {"manifest_symbols": sum(1 for u in uni.values() if u["in_manifest"]), "additions_not_in_manifest": sorted(s for s, u in uni.items() if not u["in_manifest"]),
                     "total_identifiers": len(uni), "by_type": {k: sum(1 for u in uni.values() if u["type"] == k) for k in sorted({u["type"] for u in uni.values()})},
                     "with_massive_daily_bars": len(ms), "tradable_but_no_massive_bars": missing,
                     "not_priced_here": "indices, futures and the FX pair are not covered by the stock grouped-daily file; they need their own feed"},
        "friday_52w_low": {"n_hit": len(hits), "n_priced": len(ms), "share_hit": len(hits) / len(ms), "tickers": hits,
                           "method": "stage 1: sampled grouped-daily lows eliminated names whose sampled low was clearly below Friday low; stage 2: exact daily bars for remaining candidates (QNT: since listing, 118 bars)",
                           "rebound_hit_vs_not": {("hit" if k else "not_hit"): _stat([m["mon_change"] for m in ms if (m["ticker"] in hits) == k]) for k in (True, False)}},
        "sympathy_peer_groups": sympathy(ms, udir.parent / "cohort"),
        "equities": block(eq), "funds_etps": block(fd), "cross_section_equities": cs,
        "by_basket_group_equities": {g: block(v) for g, v in sorted(by_group.items(), key=lambda kv: -len(kv[1]))},
        "top_rebound_equities": [{"ticker": m["ticker"], "mon_change": m["mon_change"], "recovery_of_friday_drop": m["recovery_of_fri_drop"], "fri_change": m["fri_change"]} for m in order[:15]],
        "bottom_rebound_equities": [{"ticker": m["ticker"], "mon_change": m["mon_change"], "recovery_of_friday_drop": m["recovery_of_fri_drop"], "fri_change": m["fri_change"]} for m in order[-15:]],
        "biggest_friday_drops_equities": [{"ticker": m["ticker"], "fri_change": m["fri_change"], "mon_change": m["mon_change"]} for m in sorted(eq, key=lambda m: m["fri_change"])[:15]],
        "equities_below_thursday_close_now": sorted(m["ticker"] for m in eq if not m["above_thu_close"]),
        "per_ticker": [{k: m[k] for k in ("ticker", "instrument_type", "basket_groups", "fri_change", "mon_change", "recovery_of_fri_drop", "fri_close_location", "gap_unfilled", "above_thu_close", "mon_low_above_fri_low")} for m in sorted(ms, key=lambda m: m["ticker"])],
        "caveats": ["Monday values are intraday (13:51 ET) and provisional", "The universe manifest is a draft snapshot from branch work/146 (identity classes provisional)",
                    "Missing names are mostly OTC ADRs and foreign listings that the stock daily file does not carry"]}
