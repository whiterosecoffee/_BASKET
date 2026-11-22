"""Apples-to-apples valuation view per ticker: calendarized, same horizon, same basis, same currency (USD)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

from .calendarize import calendarize, extend, ntm
from .store import Est

YEARS = (2026, 2027, 2028, 2029, 2030)
EST_STALE_DAYS = 120
PRICE_STALE_DAYS = 5


@dataclass
class View:
    ticker: str
    price: float
    as_of: date
    price_date: date
    eps: dict[int, float] = field(default_factory=dict)       # calendar-year EPS
    rev: dict[int, float] = field(default_factory=dict)
    extrapolated: set[int] = field(default_factory=set)
    ntm_eps: float | None = None
    ev: float | None = None
    market_cap: float | None = None
    est_age_days: int | None = None
    flags: list[str] = field(default_factory=list)
    resid: float | None = None  # growth-adjusted rich(+)/cheap(-) vs cohort, in P/E turns

    def pe(self, y: int) -> float | None:
        e = self.eps.get(y)
        return self.price / e if e and e > 0 else None

    @property
    def ntm_pe(self) -> float | None:
        return self.price / self.ntm_eps if self.ntm_eps and self.ntm_eps > 0 else None

    @property
    def cagr(self) -> float | None:
        a, b = self.eps.get(YEARS[0]), self.eps.get(YEARS[-1])
        if not a or not b or a <= 0 or b <= 0:
            return None
        return (b / a) ** (1 / (YEARS[-1] - YEARS[0])) - 1

    @property
    def peg(self) -> float | None:
        g = self.cagr
        return self.ntm_pe / (g * 100) if self.ntm_pe and g and g > 0 else None

    @property
    def ev_sales_ntm(self) -> float | None:
        a, b = self.rev.get(self.as_of.year), self.rev.get(self.as_of.year + 1)
        if not (self.ev and a and b):
            return None
        f = _frac(self.as_of)
        return self.ev / ((1 - f) * a + f * b)

    @property
    def usable(self) -> bool:
        return self.ntm_eps is not None and "STALE_ESTIMATES" not in self.flags and "STALE_PRICE" not in self.flags


def _frac(dt: date) -> float:
    return (dt.timetuple().tm_yday - 1) / 365.0


def _series(ests: dict[int, Est] | None):
    if not ests:
        return {}, 12, None
    fye = next(iter(ests.values())).fye_month
    return {y: e.value for y, e in ests.items()}, fye, max(e.as_of for e in ests.values())


def build_view(ticker: str, snap: dict, estimates: dict, as_of: date) -> View:
    v = View(ticker, snap["price"], as_of, snap["asof"], market_cap=snap["market_cap"], ev=snap["enterprise_value"])
    if (as_of - snap["asof"]).days > PRICE_STALE_DAYS:
        v.flags.append("STALE_PRICE")
    newest = []
    for metric, store in (("eps", v.eps), ("revenue", v.rev)):
        fy, fye, newest_as_of = _series(estimates.get((ticker, metric)))
        if not fy:
            continue
        newest.append(newest_as_of)
        ext, added = extend(fy, YEARS[-1] + (1 if fye < 12 else 0))
        store.update(calendarize(ext, fye))
        if metric == "eps":
            v.extrapolated = {y for y in YEARS if (y in added) or (fye < 12 and y + 1 in added)}
    if not v.eps:
        v.flags.append("NO_ESTIMATES")
        return v
    v.est_age_days = (as_of - min(newest)).days
    if v.est_age_days > EST_STALE_DAYS:
        v.flags.append("STALE_ESTIMATES")
    if v.extrapolated:
        v.flags.append("EXTRAPOLATED:" + ",".join(map(str, sorted(v.extrapolated))))
    v.ntm_eps = ntm(v.eps, as_of.year, _frac(as_of))
    # Basis cross-check: forward vs reported TTM EPS (GAAP) — large wedge means non-GAAP/GAAP mismatch.
    ttm = _num(snap.get("earnings_per_share"))
    if ttm and v.ntm_eps and ttm > 0 and not (0.5 < v.ntm_eps / ttm < 3.0):
        v.flags.append("CHECK_EPS_BASIS")
    return v


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def add_growth_adjusted_residuals(views: list[View]) -> None:
    """Cross-sectional OLS: NTM P/E ~ a + b*EPS CAGR(%). Residual = P/E turns richer than growth justifies."""
    pts = [(v.cagr * 100, v.ntm_pe, v) for v in views if v.usable and v.cagr is not None and v.ntm_pe]
    if len(pts) < 4:
        return
    n = len(pts)
    mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    if sxx == 0:
        return
    b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
    a = my - b * mx
    for g, pe, v in pts:
        v.resid = pe - (a + b * g)


def ratio_stats(pa: list[tuple[date, float]], pb: list[tuple[date, float]], lookback: int = 252) -> dict | None:
    """Price ratio A/B over time: current level, z-score and percentile versus the lookback window."""
    db = dict(pb)
    r = [(t, p / db[t]) for t, p in pa if t in db][-lookback:]
    if len(r) < 30:
        return None
    xs = [x for _, x in r]
    mu = sum(xs) / len(xs)
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / (len(xs) - 1))
    cur = xs[-1]
    # Mean-reversion speed: AR(1) on log ratio, x_t - x_{t-1} = a + b*x_{t-1}; half-life = ln2 / -ln(1+b).
    lx = [math.log(x) for x in xs]
    dx, lag = [lx[i] - lx[i - 1] for i in range(1, len(lx))], lx[:-1]
    ml, md = sum(lag) / len(lag), sum(dx) / len(dx)
    var = sum((v - ml) ** 2 for v in lag)
    b = sum((v - ml) * (w - md) for v, w in zip(lag, dx)) / var if var else 0.0
    hl = math.log(2) / -math.log(1 + b) if -1 < b < 0 else None
    return {"ratio": cur, "z": (cur - mu) / sd if sd else 0.0, "pctile": sum(x <= cur for x in xs) / len(xs),
            "n": len(xs), "half_life_days": hl}
