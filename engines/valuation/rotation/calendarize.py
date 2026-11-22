"""Put every company on the same calendar-year axis and fill gaps explicitly."""
from __future__ import annotations

MAX_G, MIN_G = 0.50, -0.20


def extend(fy: dict[int, float], to_year: int, fade: float = 0.8) -> tuple[dict[int, float], set[int]]:
    """Extrapolate fiscal-year values to `to_year` by fading the last observed growth.

    Returns (values, extrapolated_years). Needs two positive points; otherwise no extension.
    """
    out, ext = dict(fy), set()
    ys = sorted(fy)
    if len(ys) < 2 or fy[ys[-1]] <= 0 or fy[ys[-2]] <= 0:
        return out, ext
    g = fy[ys[-1]] / fy[ys[-2]] - 1.0
    for y in range(ys[-1] + 1, to_year + 1):
        g = max(MIN_G, min(MAX_G, g)) * fade
        out[y] = out[y - 1] * (1 + g)
        ext.add(y)
    return out, ext


def calendarize(fy: dict[int, float], fye_month: int) -> dict[int, float]:
    """Fiscal-year (labelled by year-end year) -> calendar-year values.

    CY_Y = (m/12) * FY_Y + ((12-m)/12) * FY_{Y+1}.  Jan FYE (m=1): CY2026 = 1/12*FY2026 + 11/12*FY2027 (FY2027 ends Jan 2027).
    """
    if fye_month == 12:
        return dict(fy)
    w = fye_month / 12.0
    return {y: w * fy[y] + (1 - w) * fy[y + 1] for y in fy if y + 1 in fy}


def ntm(cy: dict[int, float], as_of_year: int, frac_elapsed: float) -> float | None:
    """Next-twelve-months blend of calendar-year values at a point in the year."""
    a, b = cy.get(as_of_year), cy.get(as_of_year + 1)
    if a is None or b is None:
        return None
    return (1 - frac_elapsed) * a + frac_elapsed * b
