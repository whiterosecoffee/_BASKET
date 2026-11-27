"""Macro shave on multiples. Simple, transparent, and explicitly an approximation.

Gordon identity: P = CF/(r-g)  =>  dP/P = -dr/(r-g) = -dr / FCF_yield, so equity duration D ~ 1/FCF_yield.
Low-yield (long-duration) names lose more multiple per rate shock; high-yield / short-duration names lose less.
Negative FCF has no finite duration under this model, so it is capped and flagged (financing/credit risk dominates).
"""
from __future__ import annotations

MIN_D, MAX_D = 3.0, 40.0


def equity_duration(fcf_yield: float | None) -> tuple[float, str | None]:
    if fcf_yield is None:
        return MAX_D, "DURATION_UNKNOWN_CAPPED"
    if fcf_yield <= 0:
        return MAX_D, "NEG_FCF_DURATION_CAPPED"
    return max(MIN_D, min(MAX_D, 1.0 / fcf_yield)), None


def multiple_factor(duration: float, shock_bp: float) -> float:
    """Multiplicative change in the multiple for a parallel discount-rate shock (floor 0.3, linear approximation)."""
    return max(0.3, 1.0 - duration * shock_bp / 10_000.0)


def load_yields(path, as_of):
    import csv
    from datetime import date
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return sorted((date.fromisoformat(r["date"]), r) for r in csv.DictReader(f) if date.fromisoformat(r["date"]) <= as_of)
