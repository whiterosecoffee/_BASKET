"""B00 Massive worker control-plane contract; does not ingest or present live prices."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
import json

UTC = dt.timezone.utc
ALLOWED_CAPABILITIES = frozenset({
    "reference", "daily_bars", "minute_bars", "last_trade", "fx_daily", "earnings"
})
ALLOWED_STATUS = frozenset({"available", "not_entitled", "unknown"})
OWNERS = {"B02": ("runtime/", "fx/"), "B03": ("research/filings/", "research/events/"), "B08": ("services/", "deployment/"), "B01": ("tests/", ".github/workflows/")}


def utc(value):
    if isinstance(value, dt.datetime):
        parsed = value
    else:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone-aware UTC timestamp required")
    return parsed.astimezone(UTC)


def validate_specs(specs):
    if not isinstance(specs, dict) or specs.get("schema") != "basket.massive_workers@1":
        raise ValueError("invalid worker contract schema")
    ids = set()
    for worker in specs.get("workers", []):
        wid = worker.get("id")
        if not wid or wid in ids:
            raise ValueError("missing/duplicate worker id")
        ids.add(wid)
        owner = worker.get("owner")
        if owner not in OWNERS:
            raise ValueError("unknown worker owner")
        cap = worker.get("capability")
        if cap not in ALLOWED_CAPABILITIES:
            raise ValueError("unknown capability")
        if not isinstance(worker.get("cadence_seconds"), int) or worker["cadence_seconds"] < 60:
            raise ValueError("worker cadence must be >= 60 seconds")
        if not isinstance(worker.get("ttd_seconds"), int) or worker["ttd_seconds"] < 0:
            raise ValueError("invalid observation TTL")
        outputs = worker.get("writes", [])
        if not outputs or any(not any(p.startswith(prefix) for prefix in OWNERS[owner]) for p in outputs):
            raise ValueError("worker writes outside owned path")
        if worker.get("transport") == "chatgpt_plugin_background":
            raise ValueError("ChatGPT plugin session is not a persistent worker")
        if worker.get("claim_live", False) and cap != "last_trade":
            raise ValueError("live claim requires last_trade entitlement")
    return True


def capability_gate(worker, provider):
    status = provider.get(worker["capability"], "unknown")
    if status not in ALLOWED_STATUS:
        raise ValueError("invalid capability status")
    if status == "not_entitled":
        return "blocked_entitlement"
    if status != "available":
        return "verification_required"
    if worker.get("transport") == "direct_provider_api" and provider.get("backend_credentials") != "available":
        return "blocked_backend_credentials"
    return "eligible_not_running"


def freshness(observation, now, ttd_seconds):
    """Return quality state; recording a stale bar cannot promote it to a live quote."""
    required = ("source", "ticker", "event_at", "available_at", "ingested_at", "observed_at", "currency")
    if any(not observation.get(k) for k in required):
        return "missing_provenance"
    try:
        t = {k: utc(observation[k]) for k in ("event_at", "available_at", "ingested_at", "observed_at")}
        current = utc(now)
    except (TypeError, ValueError):
        return "invalid_timestamp"
    if not (t["event_at"] <= t["available_at"] <= t["ingested_at"] <= t["observed_at"] <= current):
        return "invalid_time_order"
    age = (current - t["event_at"]).total_seconds()
    return "fresh_as_of" if age <= ttd_seconds else "expired_historical"


def reconcile(specs, provider, now, observations=None, runtime_verified=False, heartbeats=None):
    validate_specs(specs)
    results = []
    for worker in specs["workers"]:
        status = capability_gate(worker, provider)
        latest = (observations or {}).get(worker["id"])
        observed = freshness(latest, now, worker["ttd_seconds"]) if latest else "no_observation"
        hb = (heartbeats or {}).get(worker["id"])
        try:
            heartbeat_ok = bool(runtime_verified and hb and 0 <= (utc(now) - utc(hb)).total_seconds() <= worker["cadence_seconds"] * 2)
        except (TypeError, ValueError):
            heartbeat_ok = False
        running = bool(heartbeat_ok and status == "eligible_not_running")
        results.append({"id": worker["id"], "owner": worker["owner"], "capability": worker["capability"],
                        "dispatch": status, "observation": observed,
                        "live_usable": bool(running and observed == "fresh_as_of" and worker.get("claim_live")),
                        "running": running})
    return {"schema": "basket.massive_worker_reconciliation@1", "as_of": utc(now).isoformat(),
            "active_runtime_verified": bool(runtime_verified), "workers": results}


def load(path=None):
    return json.loads(Path(path or Path(__file__).with_name("massive_worker_jobs.json")).read_text(encoding="utf-8"))