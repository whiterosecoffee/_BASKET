"""Sympathetic response inside nested groups (cross-sectional, one event).

Levels: cohort (all names) > peer group (industry, hand-assigned) > name. For each name i and level L the leave-one-out group mean
g_i = mean(x_j, j in L, j != i). Sympathy beta = OLS slope of x_i on g_i across names; R2 = share of cross-name variance explained.
Nested decomposition: x_i = c + (group_mean_i - c) + (x_i - group_mean_i), reported as variance shares (between-group / within-group).
Note: leave-one-out cohort means are mechanically anti-correlated with own value (beta -> -(n-1)), so the cohort level is NOT regressed; the
one-way ANOVA intraclass correlation ICC(1) measures how much of the cross-name dispersion is shared within peer groups instead.
One event gives a cross-section only; time-series sympathy (rolling beta, lead-lag, residual correlation) needs per-ticker history (see history/).
"""
from __future__ import annotations

import statistics


def _ols(x: list[float], y: list[float]) -> dict:
    n = len(x)
    if n < 4:
        return {"n": n}
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return {"n": n}
    return {"n": n, "beta": sxy / sxx, "r2": sxy * sxy / (sxx * syy)}


def loo_mean(vals: dict[str, float], members: list[str], t: str) -> float | None:
    o = [vals[m] for m in members if m != t and m in vals]
    return sum(o) / len(o) if o else None


def icc1(groups: list[list[float]]) -> float | None:
    gs = [g for g in groups if len(g) >= 2]
    k, n = len(gs), sum(len(g) for g in gs)
    if k < 2 or n <= k:
        return None
    mu = sum(sum(g) for g in gs) / n
    ssb = sum(len(g) * (sum(g) / len(g) - mu) ** 2 for g in gs)
    ssw = sum(sum((x - sum(g) / len(g)) ** 2 for x in g) for g in gs)
    msb, msw = ssb / (k - 1), ssw / (n - k)
    n0 = (n - sum(len(g) ** 2 for g in gs) / n) / (k - 1)
    d = msb + (n0 - 1) * msw
    return (msb - msw) / d if d else None


def analyse(vals: dict[str, float], groups: dict[str, list[str]]) -> dict:
    """vals: ticker -> move; groups: group -> tickers (names outside every group are ignored for the group level)."""
    names = sorted(t for g in groups.values() for t in g if t in vals)
    grp_of = {t: g for g, ms in groups.items() for t in ms}
    xs_grp, ys_grp = [], []
    resid = {}
    for t in names:
        b = loo_mean(vals, groups[grp_of[t]], t)
        if b is not None:
            xs_grp.append(b); ys_grp.append(vals[t])
            resid[t] = vals[t] - b
    mu = statistics.mean(vals[t] for t in names)
    gm = {g: statistics.mean(vals[t] for t in ms if t in vals) for g, ms in groups.items() if any(t in vals for t in ms)}
    tot = sum((vals[t] - mu) ** 2 for t in names)
    between = sum((gm[grp_of[t]] - mu) ** 2 for t in names)
    return {"n_names": len(names),
            "icc1": icc1([[vals[t] for t in ms if t in vals] for ms in groups.values()]),
            "peer_group_level": _ols(xs_grp, ys_grp),
            "variance_share": {"between_groups": between / tot if tot else None, "within_groups": 1 - between / tot if tot else None},
            "group_means": gm,
            "idiosyncratic_vs_group_loo": dict(sorted(resid.items(), key=lambda kv: kv[1]))}
