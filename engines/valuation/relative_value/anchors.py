"""Three independent anchors for expected end price, then a transparent blend.

F  standardized estimates : company estimates/guidance x standardized (history-based) multiple
I  industry forecasts     : published industry drivers translated to the company through explicit, editable assumptions
R  historical spot ratio  : partial reversion of each pair's price ratio toward its own median (relative-only, zero-sum)

Every anchor returns {bear, base, bull} RETURNS over the horizon plus flags. Nothing here predicts; it makes the
assumptions behind each target visible and lets you see where the anchors disagree.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

from . import history as hist
from .calendarize import ntm
from .metrics import View, _frac
from .store import d

SC = ("bear", "base", "bull")


def load_industry(path: Path, as_of: date) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    if path.exists():
        with path.open(newline="") as f:
            for r in csv.DictReader(f):
                if d(r["as_of"]) <= as_of:
                    out.setdefault(r["metric"], {})[r["scenario"]] = float(r["value"])
    return out


def load_map(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def std_factors(trailing_now: float | None, st: dict | None, ok: bool, rerate_w: float, band: float) -> tuple[dict, list]:
    """Multiple CHANGE factors (1.0 = unchanged) for bear/base/bull.

    Default (rerate_w = 0): flat band, no historical re-rating. If rerate_w > 0 and the history is reliable, the
    TRAILING P/E now is compared with the TRAILING historical quartiles (like for like) and the multiple moves
    rerate_w of the way. History is a poor target on its own: multiples compress as growth matures.
    """
    flat = {"bear": 1 - band, "base": 1.0, "bull": 1 + band}
    if rerate_w <= 0 or not (st and ok and trailing_now and trailing_now > 0):
        return flat, ["MULT_FLAT_BAND" if rerate_w <= 0 else "HIST_UNRELIABLE_FLAT_BAND"]
    f = lambda q: 1 + rerate_w * (st[q] / trailing_now - 1)
    return {"bear": min(1 - band, f("p25")), "base": f("median"), "bull": max(1 + band, f("p75"))}, \
           [f"HIST_TRAILING_PE(median={st['median']:.1f},now={trailing_now:.1f},w={rerate_w})"]


def anchor_F(t: str, v: View, cfg: dict, guide: dict, st_pe, ok_pe, trailing_now, horizon_m: int, rerate_w: float, band: float, ev_info: dict) -> dict | None:
    kind = cfg.get("fundamental")
    when = v.as_of + timedelta(days=round(30.4375 * horizon_m))
    fac, fl = std_factors(trailing_now, st_pe, ok_pe, rerate_w, band)
    if kind == "eps_estimates":
        fwd = ntm(v.eps, when.year, _frac(when))
        if not (fwd and v.ntm_eps and v.ntm_eps > 0):
            return None
        g = fwd / v.ntm_eps
        return {"ret": {s: g * fac[s] - 1 for s in SC}, "flags": fl + (["EXTRAPOLATED_EPS"] if v.extrapolated else [])}
    if kind == "eps_runrate":
        if not guide.get((t, "eps")):
            return None
        flat, fl2 = std_factors(None, None, False, 0.0, band)
        return {"ret": {s: flat[s] - 1 for s in SC}, "flags": fl2 + ["RUNRATE_FLAT_NO_GROWTH_VIEW"]}
    if kind == "ev_sales_levered":
        ev, mcap = ev_info["ev"], ev_info["mcap"]
        nd0 = ev - mcap
        base_rev = cfg["backlog_b"] * cfg["backlog_conv_24m"] / 2
        nd_T = nd0 / 1e9 + cfg["capex_2027_b"] - cfg["ocf_2027_b"]
        m0 = ev / 1e9 / cfg["ref_revenue_b"]
        ret = {s: max(-0.99, (m0 * base_rev * cfg["scen_mult"][s] - nd_T) / (mcap / 1e9) - 1) for s in SC}
        return {"ret": ret, "flags": [f"NET_DEBT_{nd0/1e9:.0f}B_TO_{nd_T:.0f}B", f"EV_S_{m0:.2f}x_CONSTANT", "LEVERED_EQUITY_WIDE_RANGE"]}
    return None


def anchor_I(t: str, v: View, cfg: dict, ind: dict, guide: dict, ev_info: dict) -> dict | None:
    c = cfg.get("industry")
    if not c:
        return None
    typ = c["type"]
    if typ == "linear":
        drv = ind.get(c["driver"])
        return {"ret": {s: c["beta"] * drv[s] for s in SC}, "flags": ["MULTIPLE_HELD_CONSTANT"]} if drv else None
    if typ == "memory_pnl":
        bits, asp = ind.get(c["bits"]), ind.get(c["asp"])
        if not (bits and asp):
            return None
        op0 = 1 - (1 - c["gm"]) - c["opex"]
        ret = {}
        for s in SC:
            r1 = (1 + bits[s]) * (1 + asp[s])
            c1 = (1 - c["gm"]) * (1 + bits[s]) * (1 + c["cost_per_bit_change"])
            op1 = r1 - c1 - c["opex"] * (1 + c["opex_growth"])
            ret[s] = op1 / op0 - 1
        return {"ret": ret, "flags": ["MULTIPLE_HELD_CONSTANT", "EPS~OPERATING_PROFIT(TAX_CONSTANT)", "OFF_GUIDED_RUNRATE"]}
    if typ == "linear_revenue":
        drv = ind.get(c["driver"])
        f = cfg.get("fundamental_cfg", cfg)
        if not drv:
            return None
        ev, mcap = ev_info["ev"], ev_info["mcap"]
        nd_T = (ev - mcap) / 1e9 + cfg["capex_2027_b"] - cfg["ocf_2027_b"]
        m0 = ev / 1e9 / cfg["ref_revenue_b"]
        ret = {s: max(-0.99, (m0 * cfg["ref_revenue_b"] * (1 + c["beta"] * drv[s]) - nd_T) / (mcap / 1e9) - 1) for s in SC}
        return {"ret": ret, "flags": ["EV_S_CONSTANT", "REVENUE_TRACKS_INDUSTRY_CAPEX", "LEVERED_EQUITY_WIDE_RANGE"]}
    return None


def anchor_R(prices: dict[str, list[tuple[date, float]]], lookback: int = 250, lam: float = 0.25) -> dict[str, dict]:
    """Each name vs every other: partial reversion (lam) of price ratio toward its own median. Relative-only."""
    out = {}
    for a, pa in prices.items():
        moves = []
        for b, pb in prices.items():
            if a == b:
                continue
            dbm = dict(pb)
            ser = [(t, p / dbm[t]) for t, p in pa if t in dbm][-lookback:]
            if len(ser) < 60:
                continue
            xs = sorted(x for _, x in ser)
            med = xs[len(xs) // 2]
            moves.append(lam * (med / ser[-1][1] - 1))
        if not moves:
            continue
        m = sum(moves) / len(moves)
        sd = math.sqrt(sum((x - m) ** 2 for x in moves) / max(1, len(moves) - 1)) if len(moves) > 1 else 0.05
        s = max(0.05, sd)
        out[a] = {"ret": {"bear": m - s, "base": m, "bull": m + s}, "flags": [f"RELATIVE_ONLY(lam={lam},peers={len(moves)})"]}
    return out


def blend(an: dict[str, dict | None], w: dict[str, float]) -> dict:
    live = {k: v for k, v in an.items() if v}
    tot = sum(w[k] for k in live)
    ret = {s: sum(w[k] / tot * live[k]["ret"][s] for k in live) for s in SC}
    bases = [v["ret"]["base"] for v in live.values()]
    spread = max(bases) - min(bases) if len(bases) > 1 else 0.0
    flags = [f"ANCHORS={','.join(live)}"] + (["ANCHOR_DISAGREE(base spread %.0fpp)" % (spread * 100)] if spread > 0.5 else [])
    if len(live) < len(an):
        flags.append("MISSING_ANCHOR:" + ",".join(k for k in an if k not in live))
    return {"ret": ret, "spread": spread, "flags": flags, "weights": {k: w[k] / tot for k in live}}
