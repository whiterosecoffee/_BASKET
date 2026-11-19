"""Observed-risk measurements and non-probabilistic Pareto comparison.

All returns are decimal fractions, not percentages. Inputs must be point-in-time
available. Constant target weights imply DAILY REBALANCING, not buy-and-hold
or realized ETF NAV returns. Transaction costs are NOT inferred.
"""
from datetime import datetime
from decimal import Decimal
from engine import dec

VERSION = "etf-risk@0.1.0"


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("ISO timestamp required")
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("timezone required")
    return value


def historical_risk(data, minimum_sessions=60):
    """Measure only synchronized, as-of-known daily total-return observations."""
    asof = _instant(data["as_of"])
    if data.get("data_kind") not in ("verified_observation", "synthetic_test"):
        raise ValueError("data kind required")
    if not data.get("source_manifest"):
        raise ValueError("source manifest required")
    if data.get("weight_policy") != "daily_constant_weight":
        raise ValueError("only explicitly rebalanced daily constant weights supported")
    weights = {k: dec(v) for k, v in data["weights"].items()}
    if not weights or any(v < 0 or v > 1 for v in weights.values()):
        raise ValueError("invalid weights")
    if abs(sum(weights.values()) - Decimal(1)) > Decimal("0.000001"):
        raise ValueError("weights do not reconcile")
    if minimum_sessions < 3:
        raise ValueError("minimum sessions must be >= 3")
    series = data["returns"]
    needed = set(weights) | {"benchmark"}
    if set(series) != needed:
        raise ValueError("security and benchmark coverage must match")
    mapped = {}
    for ticker, observations in series.items():
        if len(observations) < minimum_sessions:
            raise ValueError("insufficient observed sessions")
        dates = []
        values = []
        for obs in observations:
            date = obs["session"]
            if date in dates:
                raise ValueError("duplicate session")
            if _instant(obs["available_at"]) > asof:
                raise ValueError("lookahead")
            if date > data["as_of"][:10]:
                raise ValueError("future session")
            ret = dec(obs["total_return"])
            if ret < -1:
                raise ValueError("daily total return below -100%")
            dates.append(date)
            values.append(ret)
        if dates != sorted(dates):
            raise ValueError("session order required")
        mapped[ticker] = (dates, values)
    aligned_dates = mapped["benchmark"][0]
    if any(dates != aligned_dates for dates, _ in mapped.values()):
        raise ValueError("synchronized sessions required")
    p = [sum(weights[k] * mapped[k][1][i] for k in weights)
         for i in range(len(aligned_dates))]
    b = mapped["benchmark"][1]
    n = Decimal(len(p))
    avg = sum(p) / n
    var = sum((x - avg)**2 for x in p) / (n - 1)
    annualized_vol = var.sqrt() * Decimal(252).sqrt()
    downside = (sum(min(x, Decimal(0))**2 for x in p) / n).sqrt() * Decimal(252).sqrt()
    peak = Decimal(1)
    wealth = Decimal(1)
    max_drawdown = Decimal(0)
    for x in p:
        wealth *= 1 + x
        peak = max(peak, wealth)
        max_drawdown = min(max_drawdown, wealth / peak - 1)
    down_ix = [i for i, x in enumerate(b) if x < 0]
    downside_beta = None
    if len(down_ix) >= 3:
        bm = sum(b[i] for i in down_ix) / Decimal(len(down_ix))
        pm = sum(p[i] for i in down_ix) / Decimal(len(down_ix))
        denom = sum((b[i] - bm)**2 for i in down_ix)
        if denom > 0:
            downside_beta = sum((b[i]-bm)*(p[i]-pm) for i in down_ix)/denom
    return {
        "schema": "basket.etf_risk@1", "engine_version": VERSION,
        "data_kind": data["data_kind"], "as_of": data["as_of"],
        "sessions": len(p), "first_session": aligned_dates[0],
        "last_session": aligned_dates[-1],
        "annualized_volatility": str(annualized_vol),
        "annualized_downside_deviation": str(downside),
        "max_drawdown": str(max_drawdown),
        "downside_beta": str(downside_beta) if downside_beta is not None else None,
        "source_manifest": data["source_manifest"],
        "interpretation": "Daily-rebalanced modeled portfolio, aligned total returns; no expenses, financing, taxes or trading costs."
    }


def pareto_frontier(rows, horizon):
    """Non-dominated portfolios for one horizon. No probabilities or fabricated score.

    maximize conditional_upside; minimize stress_loss, drawdown_magnitude,
    round_trip_cost and concentration. Requires complete comparable inputs.
    """
    if str(horizon) not in ("2027", "2028"):
        raise ValueError("rank each supported horizon separately")
    keys = ("conditional_upside", "stress_loss", "drawdown_magnitude",
            "round_trip_cost", "concentration")
    vals = []
    ids = set()
    for row in rows:
        identifier = row["name"]
        if identifier in ids:
            raise ValueError("duplicate portfolio")
        ids.add(identifier)
        if str(row["horizon"]) != str(horizon):
            raise ValueError("mixed horizons")
        if row.get("evidence_status") not in ("synthetic_test", "verified_observation"):
            raise ValueError("evidence status required")
        x = {k: dec(row[k]) for k in keys}
        if x["stress_loss"] < 0 or x["drawdown_magnitude"] < 0 or x["round_trip_cost"] < 0:
            raise ValueError("risk and cost magnitudes must be nonnegative")
        if not 0 < x["concentration"] <= 1:
            raise ValueError("concentration must be a portfolio weight")
        vals.append((row, x))
    front = []
    for i, (row, x) in enumerate(vals):
        dominated = False
        for j, (_, y) in enumerate(vals):
            if i == j:
                continue
            non_worse = y["conditional_upside"] >= x["conditional_upside"] and all(
                y[k] <= x[k] for k in keys[1:])
            strictly = y["conditional_upside"] > x["conditional_upside"] or any(
                y[k] < x[k] for k in keys[1:])
            if non_worse and strictly:
                dominated = True
                break
        if not dominated:
            front.append(row["name"])
    return {"schema": "basket.etf_pareto@1", "horizon": str(horizon),
            "non_dominated": sorted(front), "evaluated": len(vals),
            "caveat": "Partial-order comparison, not a predictive ranking."}
