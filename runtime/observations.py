"""Append-only point-in-time market/FX journal and deterministic snapshots.

Storage is local or hosted durable disk, never a GitHub streaming service.
No provider entitlement or live connectivity is implied.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

UTC = dt.timezone.utc


def timestamp(value):
    result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timezone-aware timestamp required")
    return result.astimezone(UTC)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_journal(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate(obs):
    required = ("entity_id", "kind", "source", "source_record_id", "observed_at",
                "available_at", "ingested_at", "currency", "value", "ttd_seconds")
    missing = [key for key in required if key not in obs]
    if missing:
        raise ValueError("missing fields: " + ", ".join(missing))
    for field in ("observed_at", "available_at", "ingested_at"):
        timestamp(obs[field])
    if timestamp(obs["available_at"]) > timestamp(obs["ingested_at"]):
        raise ValueError("observation cannot be ingested before availability")
    if obs["ttd_seconds"] < 0:
        raise ValueError("negative TTD")
    if obs.get("supersedes") == obs.get("record_id") and obs.get("supersedes") is not None:
        raise ValueError("self-supersession")
    return obs


def append(path, observation):
    """Atomic append under single-writer lock file (portable Windows/Unix).

    Exclusive lock-file creation fails closed for concurrent processes; stale locks
    require manual intervention, rather than silently accepting dual writers.
    """
    path = Path(path)
    obs = dict(observation)
    obs["record_id"] = digest({k: v for k, v in obs.items() if k != "record_id"})
    validate(obs)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(fd)
        existing = read_journal(path)
        ids = {row["record_id"] for row in existing}
        if obs["record_id"] in ids:
            raise ValueError("record already exists; immutable observations cannot be overwritten")
        if obs.get("supersedes"):
            prior = next((row for row in existing if row["record_id"] == obs["supersedes"]), None)
            if prior is None:
                raise ValueError("supersedes unknown record")
            if (prior["entity_id"], prior["kind"], prior["source_record_id"]) != (
                    obs["entity_id"], obs["kind"], obs["source_record_id"]):
                raise ValueError("revision refers to different logical observation")
            if timestamp(obs["available_at"]) < timestamp(prior["available_at"]):
                raise ValueError("correction availability cannot move backwards")
        with path.open("ab") as out:
            out.write(canonical(obs) + b"\n")
            out.flush()
            os.fsync(out.fileno())
    finally:
        lock.unlink(missing_ok=True)
    return obs


def replay(records, as_of):
    """Select records knowable at as_of; latest available correction wins."""
    cutoff = timestamp(as_of)
    eligible = [validate(dict(row)) for row in records
                if timestamp(row["available_at"]) <= cutoff
                and timestamp(row["ingested_at"]) <= cutoff]
    by_id = {row["record_id"]: row for row in eligible}
    superseded = {row["supersedes"] for row in eligible if row.get("supersedes") in by_id}
    active = [row for row in eligible if row["record_id"] not in superseded]
    keys = [(r["entity_id"], r["kind"], r["source_record_id"]) for r in active]
    if len(set(keys)) != len(keys):
        raise ValueError("conflicted revisions: independent active values for same observation")
    return sorted(active, key=lambda r: (r["entity_id"], r["kind"], r["source_record_id"]))


def state(record, as_of, dependencies=(), calculation_expires_at=None):
    """Freshness for current use; historical replay is independent of freshness."""
    if record is None:
        return "unavailable"
    if record.get("state") in ("conflicted", "unavailable"):
        return record["state"]
    now = timestamp(as_of)
    if timestamp(record["available_at"]) > now or timestamp(record["ingested_at"]) > now:
        return "unavailable"
    if timestamp(record["observed_at"]) > now:
        return "conflicted"
    if record.get("value") is None:
        return "unavailable"
    expiry = timestamp(record["observed_at"]) + dt.timedelta(seconds=record["ttd_seconds"])
    for dep in dependencies:
        if dep.get("state") in ("conflicted", "unavailable"):
            return dep["state"]
        expiry = min(expiry, timestamp(dep["expires_at"]))
    if calculation_expires_at:
        expiry = min(expiry, timestamp(calculation_expires_at))
    return "fresh" if now < expiry else "stale"


def snapshot(records, as_of, inputs=None, model_version="observation-journal@1"):
    """Canonical immutable manifest; stable hash excludes wall-clock generation time."""
    selected = replay(records, as_of)
    manifest = {
        "format": "basket.snapshot@1",
        "as_of": timestamp(as_of).isoformat(),
        "model_version": model_version,
        "inputs": inputs or {},
        "records": [{"record_id": row["record_id"], "source": row["source"],
                     "available_at": row["available_at"], "ingested_at": row["ingested_at"],
                     "currency": row["currency"], "content_sha256": digest(row)}
                    for row in selected]
    }
    return {"snapshot_sha256": digest(manifest), "manifest": manifest}


def adapter_access(entitled=False, worker_running=False):
    """An adapter is unavailable absent both provider entitlement and a running worker."""
    return "freshness_unverified" if entitled and worker_running else "unavailable"
