"""Expectations investing: what free-cash-flow path does today's price already imply? (reverse DCF)

Assumptions are explicit inputs, not facts: discount rate r = risk-free + equity risk premium, terminal growth,
explicit-period length, and TTM free cash flow as the base. A negative implied growth means the market prices FCF
FALLING from here; a very high one means it prices heavy growth.
"""
from __future__ import annotations


def pv(fcf0: float, g: float, r: float, years: int, g_term: float) -> float:
    total, cf = 0.0, fcf0
    for t in range(1, years + 1):
        cf *= 1 + g
        total += cf / (1 + r) ** t
    tv = cf * (1 + g_term) / (r - g_term)
    return total + tv / (1 + r) ** years


def implied_growth(mcap: float, fcf0: float | None, r: float, years: int = 10, g_term: float = 0.03) -> float | None:
    """Constant FCF growth over `years` that equates PV to market cap; None if FCF <= 0 or unsolvable in [-80%, +200%]."""
    if not fcf0 or fcf0 <= 0 or r <= g_term:
        return None
    lo, hi = -0.8, 2.0
    if not (pv(fcf0, lo, r, years, g_term) <= mcap <= pv(fcf0, hi, r, years, g_term)):
        return None
    for _ in range(100):
        mid = (lo + hi) / 2
        if pv(fcf0, mid, r, years, g_term) < mcap:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
