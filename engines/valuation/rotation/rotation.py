"""Rotation decision: is switching from HELD to CAND worth it after costs, taxes and catalyst timing?"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from .calendarize import ntm
from .metrics import View, _frac


@dataclass
class Params:
    horizon_months: int = 12
    multiple_band: float = 0.15          # bear/bull = NTM multiple -/+ band
    probs: tuple[float, float, float] = (0.25, 0.50, 0.25)  # bear, base, bull
    round_trip_cost: float = 0.0020      # fraction of position (spread + slippage, both legs)
    tax_rate: float = 0.0                # applied to unrealised gain on HELD if sold
    hurdle: float = 0.08                 # minimum after-friction edge over the horizon
    catalyst_window_days: int = 21
    rerate: dict = field(default_factory=dict)  # ticker -> target multiple factor (e.g. 1.10 = expect +10% re-rating)


def exp_return(v: View, p: Params, scen: float, rerate: float = 1.0) -> float | None:
    """Price return to horizon = (EPS_NTM at horizon / EPS_NTM now) * (target multiple / current multiple) - 1."""
    t = v.as_of + timedelta(days=round(30.4375 * p.horizon_months))
    fwd = ntm(v.eps, t.year, _frac(t))
    if not (fwd and v.ntm_eps and v.ntm_eps > 0 and fwd > 0):
        return None
    return fwd / v.ntm_eps * rerate * (1 + scen) - 1


def scenarios(v: View, p: Params) -> dict[str, float] | None:
    rr = p.rerate.get(v.ticker, 1.0)
    r = [exp_return(v, p, s, rr) for s in (-p.multiple_band, 0.0, p.multiple_band)]
    if None in r:
        return None
    return {"bear": r[0], "base": r[1], "bull": r[2], "exp": sum(w * x for w, x in zip(p.probs, r))}


def decide(held: View, cand: View, p: Params, entry_price: float | None, next_earn: dict[str, date]) -> dict:
    out = {"held": held.ticker, "cand": cand.ticker, "signal": "INSUFFICIENT_DATA", "notes": []}
    if not (held.usable and cand.usable):
        out["notes"] = [f"{v.ticker}: {','.join(v.flags) or 'no data'}" for v in (held, cand) if not v.usable]
        return out
    sh, sc = scenarios(held, p), scenarios(cand, p)
    if not (sh and sc):
        out["notes"].append("non-positive EPS in horizon; P/E method not meaningful")
        return out
    friction = p.round_trip_cost
    if entry_price and held.price > entry_price:
        friction += p.tax_rate * (held.price - entry_price) / held.price
    edge = {k: sc[k] - sh[k] - friction for k in ("bear", "base", "bull", "exp")}
    out.update(held_ret=sh, cand_ret=sc, edge=edge, friction=friction)
    out["robust"] = edge["bear"] > 0 and edge["base"] > 0 and edge["bull"] > 0
    out["resid_gap"] = (held.resid - cand.resid) if held.resid is not None and cand.resid is not None else None
    for v in (held, cand):
        tf = [f[5:] for f in v.flags if f.startswith("TAPE:")]
        if tf:
            out["notes"].append(f"{v.ticker} tape: {','.join(tf)}")
    he, ce = next_earn.get(held.ticker), next_earn.get(cand.ticker)
    hd = (he - held.as_of).days if he else None
    cd = (ce - held.as_of).days if ce else None
    out["days_to_earnings"] = {held.ticker: hd, cand.ticker: cd}
    if edge["exp"] >= p.hurdle and out["robust"]:
        out["signal"] = "ROTATE"
        if hd is not None and hd <= p.catalyst_window_days and edge["exp"] < 2 * p.hurdle:
            out["signal"] = "WAIT_FOR_PRINT"
            out["notes"].append(f"{held.ticker} reports in {hd}d; edge is under 2x hurdle, so the print may re-rate the held name first")
        elif cd is not None and cd <= p.catalyst_window_days:
            out["notes"].append(f"{cand.ticker} reports in {cd}d; consider entering after the print to avoid event variance")
    elif edge["exp"] >= p.hurdle:
        out["signal"] = "CONTESTED"
        out["notes"].append("expected edge clears hurdle but not in all three multiple scenarios")
    else:
        out["signal"] = "HOLD"
    return out
