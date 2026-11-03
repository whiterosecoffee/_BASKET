"""Deterministic, provider-agnostic market geometry; no polling or forecasts.

Input observations are already normalized and source-verified by the caller.
Each bar: {"t": UTC ISO-8601, "close": positive USD price,
"low": positive price, "high": positive price, "complete": true}.
Timestamps represent completed observations; caller supplies a shared as_of.
"""
from datetime import datetime, timezone
from math import isfinite

ANCHORS = ("SPY", "QQQ", "RSP", "IWM", "SMH")
RELATIVES = (("QQQ", "SPY"), ("RSP", "SPY"), ("SMH", "QQQ"), ("IWM", "SPY"))
WINDOWS = (1, 5, 15, 30, 60)


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be ISO-8601 UTC string")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise ValueError("timestamps must be UTC")
    return result.astimezone(timezone.utc)


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("price must be finite positive number")
    if not isfinite(value) or value <= 0:
        raise ValueError("price must be finite positive number")
    return float(value)


def _pct(current, previous):
    return round((current / previous - 1) * 100, 6)


def _normalize(bars, at):
    output = {}
    if not isinstance(bars, list):
        raise ValueError("bars must be a list")
    for bar in bars:
        t = _timestamp(bar["t"])
        if t > at:
            raise ValueError("future observation")
        if bar.get("complete") is not True:
            continue
        c, lo, hi = (_number(bar[k]) for k in ("close", "low", "high"))
        if not lo <= c <= hi:
            raise ValueError("close outside observed range")
        if t in output:
            raise ValueError("duplicate completed timestamp")
        output[t] = {"close": c, "low": lo, "high": hi}
    return dict(sorted(output.items()))


def compute_market_geometry(series, as_of, prior_closes=None, *, windows=WINDOWS, range_start=None):
    """Return geometry and strictly synchronized relative returns.

    Windows use observation at exactly as_of - N minutes, never nearest-neighbor
    interpolation. No missing-minute forward filling or cross-session inference.

    range_start is the inclusive timestamp of the first expected completed
    minute observation. The caller selects session/calendar boundaries. An
    explicit range requires every minute through as_of. Omission describes
    supplied observations only, with no completeness or session claim.
    """
    at = _timestamp(as_of)
    start = _timestamp(range_start) if range_start is not None else None
    if start is not None and (start > at or (at - start).total_seconds() % 60):
        raise ValueError("range_start must be whole minutes at or before as_of")
    prior_closes = prior_closes or {}
    normalized = {ticker: _normalize(bars, at) for ticker, bars in sorted(series.items())}
    result = {
        "as_of": at.isoformat(), "status": "descriptive_only",
        "range_basis": "bounded_minutes" if start is not None else "supplied_observations",
        "range_start": start.isoformat() if start is not None else None,
        "instruments": {}, "relatives": {}, "gaps": [],
        "macro_regime": "unknown", "live_monitor": False,
    }
    from datetime import timedelta
    for ticker in sorted(set(ANCHORS) | set(normalized)):
        data = normalized.get(ticker, {})
        if at not in data:
            result["instruments"][ticker] = None
            result["gaps"].append(ticker + ":missing_synchronized_as_of")
            continue
        last = data[at]["close"]
        recent = [v for t, v in data.items() if start is None or
                  (t >= start and (t - start).total_seconds() % 60 == 0)]
        complete = start is None or len(recent) == (at - start).total_seconds() // 60 + 1
        lo = min(x["low"] for x in recent) if complete else None
        hi = max(x["high"] for x in recent) if complete else None
        if not complete:
            result["gaps"].append(ticker + ":incomplete_observed_range")
        previous = prior_closes.get(ticker)
        day = _pct(last, _number(previous)) if previous is not None else None
        w = {}
        for n in windows:
            past = data.get(at - timedelta(minutes=n))
            w[str(n)] = _pct(last, past["close"]) if past else None
            if not past:
                result["gaps"].append(f"{ticker}:missing_{n}m")
        velocity = (w.get("5") / 5) if w.get("5") is not None else None
        previous5 = data.get(at - timedelta(minutes=10))
        middle5 = data.get(at - timedelta(minutes=5))
        previous_velocity = _pct(middle5["close"], previous5["close"]) / 5 if previous5 and middle5 else None
        acceleration = round((velocity - previous_velocity) / 5, 8) if velocity is not None and previous_velocity is not None else None
        result["instruments"][ticker] = {
            "price_usd": last, "day_pct": day, "returns_pct": w,
            "from_low_pct": _pct(last, lo) if complete else None,
            "range_position_pct": round(100 * (last - lo) / (hi - lo), 6) if complete and hi > lo else None,
            "velocity_pct_per_min": round(velocity, 8) if velocity is not None else None,
            "acceleration_pct_per_min2": acceleration,
            "observed_range": {"low": lo, "high": hi},
        }
        if previous is None:
            result["gaps"].append(ticker + ":missing_previous_close")
    for a, b in RELATIVES:
        pair = a + "/" + b
        x, y = normalized.get(a, {}), normalized.get(b, {})
        if at not in x or at not in y:
            result["relatives"][pair] = None
            continue
        current = x[at]["close"] / y[at]["close"]
        rel = {}
        for n in windows:
            t = at - timedelta(minutes=n)
            if t in x and t in y:
                rel[str(n)] = _pct(current, x[t]["close"] / y[t]["close"])
            else:
                rel[str(n)] = None
        result["relatives"][pair] = {"ratio": round(current, 8), "returns_pct": rel}
    return result


def render_compact(result):
    """Small mobile-friendly readout; deliberately no unsupported regime label."""
    rows = [f"Market geometry @ {result['as_of']} | Regime: unknown (descriptive only)"]
    for ticker in ANCHORS:
        x = result["instruments"].get(ticker)
        if not x:
            rows.append(ticker + ": unavailable")
            continue
        fmt = lambda n: "n/a" if n is None else f"{n:+.2f}%"
        rows.append(f"{ticker} {fmt(x['day_pct'])} day | {fmt(x['returns_pct'].get('15'))} 15m | {fmt(x['returns_pct'].get('60'))} 60m | {fmt(x['from_low_pct'])} from low ({result['range_basis']})")
    rows.append("Missing: " + str(len(result["gaps"])) + " fields")
    return "\n".join(rows)
