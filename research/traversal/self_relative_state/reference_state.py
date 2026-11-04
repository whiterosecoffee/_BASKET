"""Research-only arithmetic oracle for B06 #154, NOT a production engine.

Caller supplies already resolved, calendar-qualified, one-session-per-record
completed daily observations with point-in-time available_at and adjustment.
Never reads/writes JSONL, fetches Massive, or emits a trade probability.
"""
from datetime import date, datetime, timezone
from math import isfinite

METHOD = "basket.self_relative.reference@0"
WINDOWS = (10, 30, 200)


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("available_at/as_of must be ISO timestamps")
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timestamp must have timezone")
    return t.astimezone(timezone.utc)


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError("OHLC must be numeric")
    if not isfinite(value) or value <= 0:
        raise ValueError("OHLC must be finite and positive")
    return float(value)


def _mean(xs):
    return sum(xs) / len(xs)


def evaluate(rows, *, as_of, instrument, input_manifest_hash,
             calendar_validated=False):
    """Completed-daily descriptive features only; no historical outcome labels.

    rows must be ordered by exchange-local trading session and supplied by a
    B02/B00-approved resolver. Corrections/revisions resolved by caller.
    calendar_validated attests external calendar verification, not performed
    here. Fail closed otherwise. Missing history produces None.
    """
    if not calendar_validated:
        raise ValueError("caller must validate session calendar")
    if not instrument or not input_manifest_hash:
        raise ValueError("instrument and input_manifest_hash required")
    cutoff = _instant(as_of)
    selected = []
    previous_date = None
    adjustment = None
    excluded_tail_started = False
    for raw in rows:
        if not isinstance(raw, dict):
            raise ValueError("bar must be object")
        day = date.fromisoformat(raw["session_date"])
        if previous_date is not None and day <= previous_date:
            raise ValueError("duplicate or unordered session")
        previous_date = day
        kind = raw["adjustment"]
        if adjustment is None:
            adjustment = kind
        if kind != adjustment:
            raise ValueError("mixed adjustment policies")
        vals = {k: _number(raw[k]) for k in ("o", "h", "l", "c")}
        if vals["l"] > min(vals["o"], vals["c"]) or vals["h"] < max(vals["o"], vals["c"]):
            raise ValueError("invalid OHLC")
        available = _instant(raw["available_at"])
        eligible = raw.get("complete") is True and available <= cutoff
        if not eligible:
            excluded_tail_started = True
            continue
        if excluded_tail_started:
            raise ValueError("non-prefix eligible sessions; refusing to compress a history gap")
        selected.append((day, vals))
    prices = [bar["c"] for _, bar in selected]
    n = len(prices)

    def sma(window, end):
        if end + 1 < window:
            return None
        return _mean(prices[end-window+1:end+1])

    def distance(window, end):
        avg = sma(window, end)
        return 100 * (prices[end] / avg - 1) if avg is not None else None

    def slope(window, end):
        current, prior = sma(window, end), sma(window, end-5) if end >= 5 else None
        return 100 * (current / prior - 1) if current is not None and prior else None

    features = {}
    for window in WINDOWS:
        key = str(window)
        if not n:
            features[key] = dict(sma=None, distance_pct=None, slope_5_pct=None,
                                 approach_velocity_pp_per_session=None,
                                 signed_persistence_sessions=None, left_censored=None)
            continue
        now = n-1
        avg = sma(window, now)
        dist = distance(window, now)
        prior_dist = distance(window, now-5) if now >= 5 else None
        persist, left_censored = None, None
        if avg is not None:
            sign = (prices[now] > avg) - (prices[now] < avg)
            persist = 0
            left_censored = False
            if sign:
                for ix in range(now, window-2, -1):
                    old = sma(window, ix)
                    old_sign = (prices[ix] > old) - (prices[ix] < old)
                    if old_sign != sign:
                        break
                    persist += sign
                    if ix == window-1:
                        left_censored = True
        features[key] = {
            "sma": avg,
            "distance_pct": dist,
            "slope_5_pct": slope(window, now),
            "approach_velocity_pp_per_session":
                (dist-prior_dist)/5 if dist is not None and prior_dist is not None else None,
            "signed_persistence_sessions": persist,
            "left_censored": left_censored,
        }

    atr = None
    if n >= 15:
        trs = [max(selected[ix][1]["h"]-selected[ix][1]["l"],
                   abs(selected[ix][1]["h"]-prices[ix-1]),
                   abs(selected[ix][1]["l"]-prices[ix-1]))
               for ix in range(1, n)]
        atr = _mean(trs[:14])
        for tr in trs[14:]:
            atr = (13*atr + tr)/14
    dist200 = features["200"]["distance_pct"]
    features["200"]["distance_atr_units"] = (
        (prices[-1]-features["200"]["sma"])/atr
        if atr is not None and atr > 0 and dist200 is not None else None)
    features["200"]["wilder_atr14"] = atr

    rank_n, percentile = 0, None
    if n >= 452:
        historical = [distance(200, idx) for idx in range(n-253, n-1)]
        rank_n = len(historical)
        current = distance(200, n-1)
        percentile = 100 * sum((x < current) + .5 * (x == current)
                               for x in historical) / rank_n
    features["200"]["rank_prior_n"] = rank_n
    features["200"]["rank_percentile"] = percentile

    features["sma10_vs_30_pct"] = (
        100*(features["10"]["sma"]/features["30"]["sma"]-1)
        if features["10"]["sma"] is not None and features["30"]["sma"] is not None else None)
    features["sma30_vs_200_pct"] = (
        100*(features["30"]["sma"]/features["200"]["sma"]-1)
        if features["30"]["sma"] is not None and features["200"]["sma"] is not None else None)
    return {
        "method": METHOD,
        "status": "descriptive_only",
        "instrument": instrument,
        "as_of": cutoff.isoformat(),
        "input_manifest_hash": input_manifest_hash,
        "eligible_completed_sessions": n,
        "last_session": selected[-1][0].isoformat() if selected else None,
        "adjustment": adjustment,
        "features": features,
        "limits": ["no_internal_calendar_check", "no_source_revision_resolution",
                   "no_empirical_classifier", "no_predictive_probabilities"],
    }
