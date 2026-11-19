"""B06: pure, fail-closed qualification gate for already-confirmed market events.

Does not detect regimes, retrieve data, persist checkpoints or send notifications.
Callers supply their own versioned event detector, evidence, cutoff and prior ID.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA = "basket.market_watch_gate@1"


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def qualify(event: Mapping[str, Any], *, prior_event_id: str | None,
            cutoff: str, max_lag_seconds: int, allowed_sessions: tuple[str, ...] =
            ("premarket", "regular", "after_hours")) -> dict[str, Any]:
    """Return a reasoned notification decision, never a trading prediction.

    Source freshness, signal confirmation and session correctness must be
    verified externally; this gate rejects missing or conflicting assertions.
    """
    reasons: list[str] = []
    if not isinstance(event, Mapping):
        return {"schema": SCHEMA, "notify": False, "reason_codes": ["invalid_event"], "event_id": None}
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id.strip():
        reasons.append("missing_event_id")
    elif event_id == prior_event_id:
        reasons.append("duplicate_event")
    if event.get("confirmed") is not True:
        reasons.append("unconfirmed")
    if event.get("material") is not True:
        reasons.append("immaterial")
    if event.get("session") not in allowed_sessions:
        reasons.append("invalid_session")
    if event.get("source_verified") is not True:
        reasons.append("unverified_source")
    if event.get("data_conflict") is not False:
        reasons.append("conflicted_or_unknown")
    if event.get("session") == "after_hours":
        if event.get("material_after_hours") is not True:
            reasons.append("no_material_after_hours")
    elif event.get("market_open") is not True:
        reasons.append("closed_session")
    if not isinstance(max_lag_seconds, int) or isinstance(max_lag_seconds, bool) or max_lag_seconds < 0:
        reasons.append("invalid_lag_policy")
    t = _utc(event.get("event_at"))
    c = _utc(cutoff)
    a = _utc(event.get("available_at"))
    if t is None or c is None or a is None:
        reasons.append("missing_or_invalid_timestamp")
    elif t > a or a > c or t > c:
        reasons.append("invalid_temporal_order")
    elif isinstance(max_lag_seconds, int) and not isinstance(max_lag_seconds, bool) and max_lag_seconds >= 0 and (c - t).total_seconds() > max_lag_seconds:
        reasons.append("stale_event")
    evidence = event.get("evidence_ids")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
        reasons.append("missing_evidence")
    if event.get("requires_cross_asset") is True and event.get("cross_asset_synchronized") is not True:
        reasons.append("unsynchronized_context")
    return {
        "schema": SCHEMA,
        "notify": len(reasons) == 0,
        "event_id": event_id if isinstance(event_id, str) and event_id.strip() else None,
        "reason_codes": reasons if reasons else ["qualified"],
    }
