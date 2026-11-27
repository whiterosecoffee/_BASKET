"""Price-band tiers in MULTIPLE space and how they migrate after an EPS update.

Definitions (see prompts/MASTER_MODEL_PROMPT.md):
- E       the earnings (TTM EPS) or, when EPS <= 0, sales per share.
- M       multiple = price / E.
- Tiers   N equal log-spaced tiers between the 52-week-low multiple and the 52-week-high multiple (T1 = compression floor, TN = expansion ceiling).
- Bands   price bands = E x tier bounds. When E changes (an EPS update) the bands move with E, the tier bounds in multiple space do not,
          so a price that did not move can fall into a different tier.
When the 52-week extremes happened under a different EPS than today's, the tiers are a constant-current-EPS counterfactual and are flagged.
"""
from __future__ import annotations

import math

N_TIERS = 5
LABELS = ("T1_compression_floor", "T2_depressed", "T3_mid", "T4_elevated", "T5_expansion_ceiling")


def tier_bounds(m_lo: float, m_hi: float, n: int = N_TIERS) -> list[float]:
    """n+1 boundaries, equal in log space from m_lo to m_hi."""
    if m_lo <= 0 or m_hi <= m_lo:
        raise ValueError("need 0 < m_lo < m_hi")
    r = (m_hi / m_lo) ** (1.0 / n)
    return [m_lo * r ** k for k in range(n + 1)]


def tier_of(m: float, bounds: list[float]) -> dict:
    """1-based tier; below the floor -> 0 ('below_floor'), above the ceiling -> n+1 ('above_ceiling')."""
    n = len(bounds) - 1
    if m < bounds[0]:
        return {"tier": 0, "label": "below_52w_low_multiple", "position_in_tier": None}
    if m > bounds[-1]:
        return {"tier": n + 1, "label": "above_52w_high_multiple", "position_in_tier": None}
    for k in range(n):
        if bounds[k] <= m <= bounds[k + 1]:
            pos = (math.log(m) - math.log(bounds[k])) / (math.log(bounds[k + 1]) - math.log(bounds[k]))
            return {"tier": k + 1, "label": LABELS[k] if n == len(LABELS) else f"T{k + 1}", "position_in_tier": pos}
    return {"tier": n, "label": LABELS[-1], "position_in_tier": 1.0}


def price_bands(e: float, bounds: list[float]) -> list[dict]:
    out = []
    for k in range(len(bounds) - 1):
        lo, hi = e * bounds[k], e * bounds[k + 1]
        out.append({"tier": k + 1, "label": LABELS[k] if len(bounds) - 1 == len(LABELS) else f"T{k + 1}", "price_low": lo, "price_high": hi,
                    "spread_abs": hi - lo, "spread_pct_of_low": hi / lo - 1})
    return out


def eps_update_effect(price: float, e_old: float, e_new: float, bounds: list[float]) -> dict:
    """What an EPS update does to the bands and to a price that does not move."""
    t0, t1 = tier_of(price / e_old, bounds), tier_of(price / e_new, bounds)
    return {"eps_old": e_old, "eps_new": e_new, "eps_change": e_new / e_old - 1, "band_shift_pct": e_new / e_old - 1,
            "tier_before": t0["tier"], "tier_after": t1["tier"], "tier_moves": t1["tier"] - t0["tier"],
            "multiple_before": price / e_old, "multiple_after": price / e_new,
            "spread_abs_widening_pct": e_new / e_old - 1}


def scenario_grid(price: float, e: float, bounds: list[float], changes=(-0.25, -0.10, 0.10, 0.25, 0.50)) -> list[dict]:
    return [dict(eps_update_effect(price, e, e * (1 + c), bounds), scenario=f"EPS {c:+.0%} (hypothetical)") for c in changes]
