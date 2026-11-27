"""Two-point evaluation: compare point A with point B for each instrument. Contract: research/models/rotation/AGENTS.md.

A point is a labelled price (e.g. fri_close, mon_high). B is later than or equal to A in time unless the pair is explicitly
a path comparison (A=fri_low, B=mon_high is allowed because both are realised prices). Nothing here forecasts.
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

POINTS = {
    "thu_close": "2026-11-19 regular-session close (final)",
    "fri_low": "2026-11-20 session low (final)",
    "fri_high": "2026-11-20 session high (final)",
    "fri_close": "2026-11-20 regular-session close (final)",
    "mon_open": "2026-11-23 session open (final once printed)",
    "mon_high": "2026-11-23 session high so far (PROVISIONAL: can still rise)",
    "mon_low": "2026-11-23 session low so far (PROVISIONAL: can still fall)",
    "mon_last": "2026-11-23 last price at snapshot time (PROVISIONAL: not a close)",
}
PROVISIONAL = {"mon_high", "mon_low", "mon_last"}


def load_points(dirpath: Path) -> tuple[dict[str, dict[str, float]], dict]:
    """Thu/Fri from the Massive Thu-Fri file; Monday from the latest *_ET snapshot file."""
    base: dict[str, dict[str, float]] = {}
    with (dirpath / "massive_2026-11-19_23.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            base[r["ticker"]] = {"thu_close": float(r["thu_close_1119"]), "fri_low": float(r["fri_low_1120"]), "fri_high": float(r["fri_high_1120"]),
                                 "fri_close": float(r["fri_close_1120"])}
    snaps = sorted(dirpath.glob("massive_mon_*ET.csv"))
    meta = {"monday_snapshot_file": snaps[-1].name if snaps else None}
    if snaps:
        with snaps[-1].open(newline="") as f:
            for r in csv.DictReader(f):
                if r["ticker"] in base:
                    base[r["ticker"]].update({"mon_open": float(r["open"]), "mon_high": float(r["high"]), "mon_low": float(r["low"]), "mon_last": float(r["last"])})
                    meta["as_of_et"] = r["as_of_et"]
                    meta["volume_" + r["ticker"]] = float(r["volume"])
    return base, meta


def compare_one(p: dict[str, float], a: str, b: str) -> dict | None:
    if a not in p or b not in p:
        return None
    A, B = p[a], p[b]
    out = {"a": A, "b": B, "change": B / A - 1}
    thu, flo, fhi, fcl = p.get("thu_close"), p.get("fri_low"), p.get("fri_high"), p.get("fri_close")
    last, mlo, mhi, mop = p.get("mon_last"), p.get("mon_low"), p.get("mon_high"), p.get("mon_open")
    if thu and fcl and thu > fcl:
        out["share_of_friday_drop_recovered_at_b"] = (B - fcl) / (thu - fcl)
    if thu:
        out["b_vs_thursday_close"] = B / thu - 1
    if fhi:
        out["b_vs_friday_high"] = B / fhi - 1
    if flo:
        out["b_vs_friday_low"] = B / flo - 1
    if last is not None and b != "mon_last":
        out["giveback_from_b_to_last"] = last / B - 1
        if B != A:
            out["giveback_share_of_move"] = (B - last) / (B - A)
        if flo is not None and B > flo:
            out["last_position_in_friday_low_to_b_range"] = (last - flo) / (B - flo)
    if mlo is not None and flo is not None:
        out["monday_low_held_above_friday_low"] = mlo > flo
    if mlo is not None and fhi is not None:
        out["gap_unfilled"] = mlo > fhi
    if mop is not None and mhi is not None and mop > 0:
        out["peak_at_open_proxy"] = (mhi - mop) / mop < 0.001          # proxy only: no intraday timestamps in this data
    return out


def summarize(rows: list[dict], key: str) -> dict:
    xs = [r[key] for r in rows if r.get(key) is not None]
    if not xs:
        return {}
    return {"n": len(xs), "median": statistics.median(xs), "mean": sum(xs) / len(xs), "min": min(xs), "max": max(xs)}


def build(dirpath: Path, themes: dict, a: str, b: str, subjects=("NVDA", "CRWV", "SNDK")) -> dict:
    pts, meta = load_points(dirpath)
    tick = []
    for t, p in sorted(pts.items()):
        c = compare_one(p, a, b)
        if not c:
            continue
        th = next((k for k, v in themes.items() if not k.startswith("_") and t in v), "other")
        tick.append({"ticker": t, "theme": th, "points": {k: v for k, v in p.items()}, "comparison": c})
    eq = [r for r in tick if r["theme"] != "benchmarks"]
    flat = [dict(r["comparison"], ticker=r["ticker"], theme=r["theme"]) for r in eq]
    by_theme = {}
    for r in flat:
        by_theme.setdefault(r["theme"], []).append(r)
    ranks = sorted(flat, key=lambda r: -r["change"])
    prov = a in PROVISIONAL or b in PROVISIONAL or any(k in PROVISIONAL for k in ("mon_last",))
    return {
        "schema": "rotation.compare/1",
        "comparison_id": f"{a}__vs__{b}__2026-11-23",
        "point_a": {"label": a, "definition": POINTS[a], "status": "provisional" if a in PROVISIONAL else "final"},
        "point_b": {"label": b, "definition": POINTS[b], "status": "provisional" if b in PROVISIONAL else "final"},
        "context_points": {k: POINTS[k] for k in POINTS if k not in (a, b)},
        "as_of_et": meta.get("as_of_et"), "monday_snapshot_file": meta.get("monday_snapshot_file"),
        "provisional": prov,
        "provisional_note": "Monday values come from a snapshot taken while the session was open; mon_high can still rise and mon_last is not a close." if prov else None,
        "adjustment_basis": "Massive adjusted daily aggregates (split/dividend adjusted); screenshots are not used for prices here",
        "selection_bias_warning": "A session high is a maximum over the path, so change(A->high) overstates what was holdable. Read it with giveback_from_b_to_last and the A->last change.",
        "subjects": {t: next((r for r in tick if r["ticker"] == t), None) for t in subjects},
        "cohort_summary": {"n_excluding_benchmarks": len(eq), "change": summarize(flat, "change"),
                           "share_of_friday_drop_recovered_at_b": summarize(flat, "share_of_friday_drop_recovered_at_b"),
                           "giveback_from_b_to_last": summarize(flat, "giveback_from_b_to_last"),
                           "giveback_share_of_move": summarize(flat, "giveback_share_of_move"),
                           "share_peak_at_open_proxy": sum(1 for r in flat if r.get("peak_at_open_proxy")) / len(flat),
                           "share_b_above_thursday_close": sum(1 for r in flat if r.get("b_vs_thursday_close", -1) > 0) / len(flat),
                           "share_b_above_friday_high": sum(1 for r in flat if r.get("b_vs_friday_high", -1) > 0) / len(flat)},
        "theme_summary": {k: {"n": len(v), "median_change": statistics.median(r["change"] for r in v),
                              "median_giveback_share_of_move": statistics.median(r["giveback_share_of_move"] for r in v if r.get("giveback_share_of_move") is not None),
                              "tickers": [r["ticker"] for r in v]} for k, v in by_theme.items()},
        "ranking_by_change": [{"rank": i + 1, "ticker": r["ticker"], "change": r["change"], "giveback_share_of_move": r.get("giveback_share_of_move")} for i, r in enumerate(ranks)],
        "per_ticker": tick,
    }


def write(dirpath: Path, out: Path, a: str, b: str) -> dict:
    themes = json.loads((dirpath / "peer_groups_by_industry.json").read_text())
    doc = build(dirpath, themes, a, b)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n")
    return doc
