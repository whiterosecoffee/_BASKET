"""Virtual ETF: spot rotation that targets share-count and expected end-value gains.

Core identity (one swap, A -> B at spot, before frictions):
    shares_B = shares_A * P_A / P_B                      (share-count multiplier = spot ratio R = P_A/P_B)
    end value swap / end value stay = (P_A/P_B) * (T_B/T_A) = (1 + r_B) / (1 + r_A),   r = T/P - 1
So a swap helps exactly when A's spot price is rich relative to its expected end price versus B's.
Expected end prices T come from user targets (targets.csv) or, if absent, from the EPS x multiple model.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .store import d

HOLD_FIELDS = ["ticker", "shares", "basis_price", "as_of"]
TARGET_FIELDS = ["ticker", "scenario", "target_price", "horizon_date", "source", "as_of"]
LEDGER_FIELDS = ["date", "ticker", "delta_shares", "price", "fee", "reason"]
SCEN = ("bear", "base", "bull")


@dataclass
class Name:
    ticker: str
    price: float
    ret: dict            # scenario -> return over the common horizon (normalised)
    exp: float           # probability-weighted return
    sigma: float | None  # horizon-scaled volatility
    basis: str           # "user_target" | "model"
    flags: list = field(default_factory=list)

    def target(self, s: str) -> float:
        return self.price * (1 + (self.exp if s == "exp" else self.ret[s]))


@dataclass
class Costs:
    round_trip: float = 0.002   # fraction of traded notional, per swap (sell leg + buy leg)
    tax_rate: float = 0.0       # on unrealised gain of shares sold


def _rows(path: Path):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return [r for r in csv.DictReader(f) if r and not (next(iter(r.values())) or "#").startswith("#")]


def load_targets(path: Path, as_of: date, horizon_months: int, probs=(0.25, 0.5, 0.25)) -> dict[str, dict]:
    """Latest user target per (ticker, scenario) known at as_of; returns normalised to the common horizon.

    A target with its own horizon_date is annualised and rescaled so every name uses the same horizon.
    Needs all three scenarios; a lone base target is accepted with bear/bull = base (flagged).
    """
    best: dict[tuple, dict] = {}
    for r in _rows(path):
        if d(r["as_of"]) > as_of:
            continue
        k = (r["ticker"].upper(), r["scenario"])
        if k not in best or r["as_of"] >= best[k]["as_of"]:
            best[k] = r
    out: dict[str, dict] = {}
    for t in {k[0] for k in best}:
        row = {s: best.get((t, s)) for s in SCEN}
        flags = []
        if row["base"] is None:
            continue
        for s in ("bear", "bull"):
            if row[s] is None:
                row[s] = row["base"]
                flags.append(f"{s.upper()}_MISSING_USING_BASE")
        out[t] = {"raw": row, "flags": flags, "horizon_months": horizon_months, "probs": probs}
    return out


def normalise_returns(row: dict, price: float, as_of: date, horizon_months: int) -> dict[str, float]:
    ret = {}
    for s in SCEN:
        days = max(30, (d(row[s]["horizon_date"]) - as_of).days)
        gross = float(row[s]["target_price"]) / price
        ret[s] = gross ** ((horizon_months * 30.4375) / days) - 1 if gross > 0 else -1.0
    return ret


def realised_vol(bars: list[dict], horizon_months: int, window: int = 252) -> float | None:
    cl = [b["close"] for b in bars[-(window + 1):]]
    if len(cl) < 30:
        return None
    r = [math.log(cl[i] / cl[i - 1]) for i in range(1, len(cl))]
    m = sum(r) / len(r)
    sd = math.sqrt(sum((x - m) ** 2 for x in r) / (len(r) - 1))
    return sd * math.sqrt(252) * math.sqrt(horizon_months / 12)


def swap(a: Name, b: Name, shares_a: float, basis_a: float | None, c: Costs, hurdle: float = 0.08) -> dict:
    """Evaluate selling `shares_a` of A and buying B at spot."""
    gross = shares_a * a.price
    gain = max(0.0, a.price - basis_a) * shares_a if basis_a else 0.0
    fric = gross * c.round_trip + c.tax_rate * gain
    shares_b = (gross - fric) / b.price
    out = {"shares_a": shares_a, "shares_b": shares_b, "share_multiplier": shares_b / shares_a,
           "spot_ratio": a.price / b.price, "friction": fric, "friction_pct": fric / gross}
    for s in SCEN + ("exp",):
        out[f"edge_{s}"] = (shares_b * b.target(s)) / (shares_a * a.target(s)) - 1
    out["fair_ratio"] = a.target("exp") / b.target("exp")
    out["rich_pct"] = out["spot_ratio"] / out["fair_ratio"] - 1          # >0: A rich vs B in end-value terms
    f = out["friction_pct"]
    out["trigger_a_to_b"] = out["fair_ratio"] * (1 + hurdle) / (1 - f)    # swap A->B only above this spot ratio
    out["trigger_b_to_a"] = out["fair_ratio"] / ((1 + hurdle) / (1 - f))  # swap back only below this
    out["robust"] = all(out[f"edge_{s}"] > 0 for s in SCEN)
    out["signal"] = ("SWAP" if out["edge_exp"] >= hurdle and out["robust"]
                     else "CONTESTED" if out["edge_exp"] >= hurdle else "STAY")
    return out


def target_weights(names: list[Name], max_w: float = 0.5, min_mu: float = 0.0) -> dict[str, float]:
    """w ~ mu/sigma among names with mu > min_mu, capped at max_w (excess redistributed pro rata)."""
    score = {n.ticker: (n.exp / n.sigma if n.sigma and n.exp > min_mu else 0.0) for n in names}
    w = {t: 0.0 for t in score}
    free, budget = {t for t, s in score.items() if s > 0}, 1.0
    while free and budget > 1e-12:
        tot = sum(score[t] for t in free)
        over = {t for t in free if budget * score[t] / tot > max_w - w[t] + 1e-12}
        if not over:
            for t in free:
                w[t] += budget * score[t] / tot
            break
        for t in over:
            budget -= max_w - w[t]
            w[t] = max_w
        free -= over
    return w


def propose(names: list[Name], hold: dict[str, dict], c: Costs, max_w=0.5, band=0.10, stage=0.33) -> dict:
    """Self-financing rebalance toward target weights with a no-trade band and staged entries into falling knives."""
    px = {n.ticker: n.price for n in names}
    nav = sum(h["shares"] * px[t] for t, h in hold.items() if t in px)
    cur = {n.ticker: hold.get(n.ticker, {"shares": 0})["shares"] * n.price / nav for n in names}
    tgt = target_weights(names, max_w)
    delta = {t: tgt[t] - cur[t] for t in tgt}
    buys = {t: v * nav for t, v in delta.items() if v > band}
    sells = {t: -v * nav for t, v in delta.items() if v < -band}
    notes = []
    for n in names:
        if n.ticker in buys and any(f in n.flags for f in ("TAPE:NEW_52W_LOW",)):
            buys[n.ticker] *= stage
            notes.append(f"{n.ticker}: new 52w low, staged to {stage:.0%} of intended buy")
    if not buys or not sells:
        return {"nav": nav, "current": cur, "target": tgt, "orders": [], "notes": notes + ["inside no-trade band or one-sided"]}
    need = sum(buys.values())
    gf = {t: (max(0, px[t] - hold[t].get("basis_price", px[t])) / px[t]) for t in sells}
    avail = sum(sells.values())
    net_frac = 1 - c.round_trip - c.tax_rate * sum(gf[t] * sells[t] for t in sells) / avail
    scale = min(1.0, need / (avail * net_frac))
    orders = [{"ticker": t, "side": "SELL", "shares": sells[t] * scale / px[t], "price": px[t]} for t in sells]
    got = avail * scale * net_frac
    orders += [{"ticker": t, "side": "BUY", "shares": buys[t] * min(1.0, got / need) / px[t], "price": px[t]} for t in buys]
    return {"nav": nav, "current": cur, "target": tgt, "orders": orders, "notes": notes}


def load_holdings(init: Path, ledger: Path, as_of: date) -> dict[str, dict]:
    """Initial holdings plus append-only ledger replay (average-cost basis)."""
    h: dict[str, dict] = {}
    for r in _rows(init):
        h[r["ticker"].upper()] = {"shares": float(r["shares"]), "basis_price": float(r["basis_price"])}
    for r in sorted(_rows(ledger), key=lambda r: r["date"]):
        if d(r["date"]) > as_of:
            continue
        t, ds, px = r["ticker"].upper(), float(r["delta_shares"]), float(r["price"])
        cur = h.setdefault(t, {"shares": 0.0, "basis_price": px})
        if ds > 0:
            cur["basis_price"] = (cur["shares"] * cur["basis_price"] + ds * px) / (cur["shares"] + ds)
        cur["shares"] += ds
    return {t: v for t, v in h.items() if v["shares"] > 1e-9}


def simulate_pair(pa: list[tuple[date, float]], pb: list[tuple[date, float]], lookback=60, band=0.10, cost=0.002) -> dict:
    """Price-only mechanical test: hold A, swap to B when A/B exceeds its rolling mean by `band`, back when below.

    No fundamentals. It tests only whether ratio-band rotation accumulated shares, in sample.
    """
    db = dict(pb)
    ser = [(t, p, db[t]) for t, p in pa if t in db]
    if len(ser) < lookback + 5:
        return {}
    holding, shares, swaps = "A", 1.0, 0
    start_a = ser[lookback][1]
    for i in range(lookback, len(ser)):
        t, a, b = ser[i]
        fair = sum(x[1] / x[2] for x in ser[i - lookback:i]) / lookback
        r = a / b
        if holding == "A" and r > fair * (1 + band):
            shares, holding, swaps = shares * a / b * (1 - cost), "B", swaps + 1
        elif holding == "B" and r < fair / (1 + band):
            shares, holding, swaps = shares * b / a * (1 - cost), "A", swaps + 1
    t, a, b = ser[-1]
    a0, b0 = ser[lookback][1], ser[lookback][2]
    end_a_units = shares if holding == "A" else shares * b / a          # value in A-share equivalents
    usd = shares * (a if holding == "A" else b) / a0                     # multiple of starting USD value
    return {"start": ser[lookback][0], "end": t, "swaps": swaps, "end_holding": holding,
            "rotator_A_units": end_a_units, "hold_A_A_units": 1.0, "hold_B_A_units": (a0 / b0) * (b / a),
            "rotator_usd_x": usd, "hold_A_usd_x": a / a0, "hold_B_usd_x": b / b0, "final_ratio": a / b}
