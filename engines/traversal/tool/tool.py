"""Read-only source-gated entrypoint over the existing B06 traversal metrics API.

No polling, persistence, event detection, prediction or alert delivery.
"""
import hashlib
import json

REQUEST = "basket.traversal.request@1"
OUTPUT = "basket.traversal.tool@1"


def digest(observations):
    payload = json.dumps(observations, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _ms(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be nonnegative integer UTC epoch milliseconds")
    return value


def run(request, mode="historical"):
    """Evaluate independently supplied completed bars; fail closed for live use."""
    if mode not in ("historical", "current"):
        raise ValueError("mode must be historical or current")
    if request.get("schema") != REQUEST:
        raise ValueError("unsupported request schema")
    symbol = request.get("instrument")
    observations = request.get("observations")
    source = request.get("source")
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("instrument required")
    if not isinstance(observations, list) or not observations:
        raise ValueError("nonempty observation list required")
    if not isinstance(source, dict):
        raise ValueError("source manifest required")
    interval = source.get("interval_minutes")
    if type(interval) is not int or interval not in (1, 5, 15):
        raise ValueError("supported intervals: 1, 5, 15 minutes")
    as_of = _ms(request.get("as_of_ms"), "as_of_ms")
    for field in ("provider", "source_id", "currency", "adjustment_basis", "session"):
        if not isinstance(source.get(field), str) or not source[field]:
            raise ValueError(f"source.{field} required")
    if source["currency"] != "USD":
        raise ValueError("non-USD requires upstream verified FX adapter")
    if source.get("sha256") != digest(observations):
        raise ValueError("source SHA256 does not match observations")
    for field in ("available_at_ms", "received_at_ms"):
        value = source.get(field)
        if value is not None:
            _ms(value, field)
            if value > as_of:
                raise ValueError(f"{field} is later than requested as-of")
    ttd = source.get("ttd_ms")
    if ttd is not None:
        _ms(ttd, "ttd_ms")
    starts = []
    for bar in observations:
        if isinstance(bar, dict):
            start = bar.get("t")
        elif isinstance(bar, list) and len(bar) == 8:
            start = bar[0]
        else:
            raise ValueError("observation must be OHLCV object or legacy eight-field array")
        starts.append(_ms(start, "bar_start"))
    if any(b <= a for a, b in zip(starts, starts[1:])):
        raise ValueError("duplicate or unordered bars")
    completed = starts[-1] + interval * 60000
    if completed > as_of:
        raise ValueError("last bar incomplete at requested as-of")
    reasons = []
    for key, wanted, reason in (
        ("quality", "verified", "source_quality_unverified"),
        ("completeness", "complete", "source_incomplete_or_unknown"),
        ("calendar_verified", True, "session_calendar_unverified"),
        ("entitlement", "realtime", "realtime_entitlement_unverified"),
    ):
        if source.get(key) != wanted:
            reasons.append(reason)
    if source.get("available_at_ms") is None or source.get("received_at_ms") is None:
        reasons.append("point_in_time_availability_unknown")
    if ttd is None or as_of - completed > ttd:
        reasons.append("expired_or_unknown_ttd")
    if any(b-a != interval*60000 for a, b in zip(starts, starts[1:])):
        reasons.append("continuity_unverified_or_gapped")
    if mode == "current":
        # A caller-provided manifest is not independent B00/B02 entitlement proof.
        reasons.append("independent_resolver_attestation_missing")
        return {
            "schema": OUTPUT, "instrument": symbol, "mode": mode,
            "status": "blocked_current", "reasons": sorted(set(reasons)),
            "as_of_ms": as_of, "completed_at_ms": completed,
            "observation_sha256": source["sha256"], "metrics": None,
            "alerts_emitted": 0,
        }
    from engines.traversal.metrics import evaluate
    metrics = evaluate(symbol, observations, interval_minutes=interval,
                       as_of=as_of, currency=source["currency"])
    return {
        "schema": OUTPUT, "instrument": symbol, "mode": mode,
        "status": "historical_descriptive", "reasons": sorted(set(reasons)),
        "as_of_ms": as_of, "completed_at_ms": completed,
        "observation_sha256": source["sha256"], "metrics": metrics,
        "alerts_emitted": 0,
    }
