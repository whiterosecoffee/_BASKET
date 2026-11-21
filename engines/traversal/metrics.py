"""B06 canonical traversal metrics layer. Read-only completed bars; storage remains B02/B10.
No detector, polling, persistence, or predictive probabilities are implemented here.
"""
import json
from math import isfinite
from collections.abc import Mapping
from datetime import datetime, timezone

METHOD = "basket.traversal.metrics@1"
WINDOWS = (5, 15, 60, 390)

def _finite_number(value, field):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f"{field} must be a finite number") from None
    if not isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number

def _integer(value, field):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")
    return value

def _require_finite_output(value):
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("Numeric overflow in derived traversal metrics")
    if isinstance(value, dict):
        for item in value.values():
            _require_finite_output(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _require_finite_output(item)

def _bar(raw):
    if isinstance(raw, list):
        if len(raw) != 8:
            raise ValueError("Expected 8-field legacy OHLCV record")
        t, o, h, l, c, v, vw, _ = raw
        raw = dict(t=t, o=o, h=h, l=l, c=c, v=v, vw=vw)
    if not all(k in raw for k in ("t", "o", "h", "l", "c", "v")):
        raise ValueError("Missing completed-bar fields")
    x = {k: _finite_number(raw[k], k) for k in ("o", "h", "l", "c", "v")}
    x["t"] = _integer(raw["t"], "bar start milliseconds")
    x["vw"] = _finite_number(raw["vw"], "vw") if raw.get("vw") is not None else None
    if x["v"] < 0 or x["l"] <= 0 or x["l"] > min(x["o"], x["c"]) or x["h"] < max(x["o"], x["c"]):
        raise ValueError("Invalid OHLCV")
    if x["vw"] is not None and x["vw"] <= 0:
        raise ValueError("Invalid VWAP")
    return x

def evaluate(instrument, observations, interval_minutes=1, as_of=None, currency="USD",
             prior_20_session_adv=None, same_clock_expected=None):
    """Descriptive simultaneous observed ranges, never prospectively frozen bands.

    as_of is an optional UTC cutoff in epoch ms; only completed observations
    available by that cutoff may be passed by the caller.
    Unknown trade scheduling, metadata, and true same-clock profiles remain null.
    """
    interval_minutes = _integer(interval_minutes, "interval_minutes")
    if interval_minutes <= 0 or not instrument:
        raise ValueError("Invalid instrument or interval")
    if as_of is not None:
        as_of = _integer(as_of, "as_of milliseconds")
    if prior_20_session_adv is not None:
        prior_20_session_adv = _finite_number(prior_20_session_adv, "prior_20_session_adv")
    if same_clock_expected is not None:
        if not isinstance(same_clock_expected, Mapping):
            raise ValueError("same_clock_expected must be a mapping")
        same_clock_expected = {
            minutes: _finite_number(value, "same_clock_expected")
            for minutes, value in same_clock_expected.items()
        }
    bars = [_bar(b) for b in observations]
    if not bars:
        raise ValueError("No completed observations")
    step = interval_minutes * 60000
    if any(b["t"] <= a["t"] for a, b in zip(bars, bars[1:])):
        raise ValueError("Duplicate or out-of-order observations")
    if as_of is not None and bars[-1]["t"] + step > as_of:
        raise ValueError("Incomplete or future bar")
    horizons = {}
    for minutes in WINDOWS:
        n = minutes // interval_minutes
        if n < 1 or minutes % interval_minutes or len(bars) < n:
            horizons[str(minutes)+"m"] = None
            continue
        s = bars[-n:]
        contiguous = all(b["t"] - a["t"] == step for a,b in zip(s,s[1:]))
        if not contiguous:
            horizons[str(minutes)+"m"] = None
            continue
        low, high = min(x["l"] for x in s), max(x["h"] for x in s)
        start, end = s[0]["o"], s[-1]["c"]
        changes = [b["c"] - a["c"] for a,b in zip(s,s[1:])]
        # Sampled close path includes the first open-to-close displacement;
        # this shares the origin of net progress but not hidden intrabar travel.
        path = abs(s[0]["c"] - start) + sum(abs(x) for x in changes)
        shares = sum(x["v"] for x in s)
        turnover = sum(x["v"]*(x["vw"] if x["vw"] is not None else (x["h"]+x["l"]+x["c"])/3) for x in s)
        up = sum(max(0,x) for x in changes)
        down = sum(max(0,-x) for x in changes)
        up_n = sum(x>0 for x in changes)
        down_n = sum(x<0 for x in changes)
        # Split turnover per observation by direction; no inference of signed order flow.
        up_dollars = sum(s[i+1]["v"]*(s[i+1]["vw"] or s[i+1]["c"]) for i,x in enumerate(changes) if x>0)
        down_dollars = sum(s[i+1]["v"]*(s[i+1]["vw"] or s[i+1]["c"]) for i,x in enumerate(changes) if x<0)
        up_eff = up*1e7/up_dollars if up_dollars>0 else None
        down_eff = down*1e7/down_dollars if down_dollars>0 else None
        horizons[str(minutes)+"m"] = {
            "observed_low":low, "observed_high":high,
            "position":(end-low)/(high-low) if high>low else None,
            "signed_return":end/start-1, "direction":end-start,
            "velocity_usd_per_min":(end-start)/minutes,
            "normalized_position_velocity":None,
            "acceleration":None,
            "up_move_per_10m_usd":up_eff, "down_move_per_10m_usd":down_eff,
            "directional_efficiency_ratio":up_eff/down_eff if up_n>=3 and down_n>=3 and down_eff else None,
            "up_samples":up_n,"down_samples":down_n,
            "net_progress_usd":end-start,
            "path_efficiency":(end-start)/path if path else None,
            "shares":shares,"estimated_turnover_usd":turnover,
            "prior_20_session_adv_pct":shares/prior_20_session_adv*100 if prior_20_session_adv and prior_20_session_adv>0 else None,
            "same_clock_rvol":shares/same_clock_expected[minutes] if same_clock_expected and same_clock_expected.get(minutes,0)>0 else None,
            "range_type":"observed_extrema", "band_version":None,
            "contacts":None,"rejections":None,"accepted_breaks":None,
            "complete_traversals":None
        }
    result = {"schema":METHOD,"instrument":instrument,"currency":currency,
            "as_of":datetime.fromtimestamp((as_of if as_of is not None else bars[-1]["t"]+step)/1000,timezone.utc).isoformat(),
            "observed_last_bar_start":bars[-1]["t"],"interval_minutes":interval_minutes,
            "observation_count":len(bars),"windows":horizons,
            "health":{"source_quality":"not_attested","freshness":"unknown","gap_windows":[k for k,v in horizons.items() if v is None]},
            "context":None,"frozen_bands":None,"structural_regime":None}
    _require_finite_output(result)
    return result
