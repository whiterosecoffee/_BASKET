"""Pure B00 dependency-fingerprint gate; no task queue, scheduler, or data-plane writes.

Canonical data producers (B02/B03/B04/B05...) own their observations. This module
only decides whether a downstream owner should recompute after a *relevant* input
revision, and declines current-use decisions on unknown or stale provenance.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import re

SCHEMA = "basket.dependency_snapshot@1"
SHA = re.compile(r"[a-f0-9]{64}\Z")


class DependencyError(ValueError):
    """A source contract or point-in-time prerequisite was not met."""


def _time(value: str) -> datetime:
    if not isinstance(value, str):
        raise DependencyError("source timestamp missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DependencyError("invalid source timestamp") from exc
    if parsed.utcoffset() is None:
        raise DependencyError("source timestamp must include offset")
    return parsed.astimezone(timezone.utc)


def _hash(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(data.encode("utf-8")).hexdigest()


def snapshot(records: list[dict], *, as_of: str) -> dict:
    """Validate and fingerprint immutable input references. No future knowledge.

    Each reference is producer-owned, identified by producer+contract+record_id;
    `source_sha256` is the raw evidence digest, not an invented model estimate.
    """
    cutoff = _time(as_of)
    if not isinstance(records, list):
        raise DependencyError("input records must be an array")
    out, seen = [], set()
    required = {"producer", "contract", "record_id", "revision_id", "source_sha256",
                "effective_at", "available_at", "ingested_at", "valid_until",
                "source_url", "evidence_class", "original_currency", "fx_reference"}
    for rec in records:
        if not isinstance(rec, dict) or set(rec) != required:
            raise DependencyError("unknown or missing dependency fields")
        if any(not isinstance(rec[key], str) or not rec[key].strip()
               for key in ("producer", "contract", "record_id", "revision_id")):
            raise DependencyError("incomplete producer identity")
        if not isinstance(rec["source_url"], str) or not rec["source_url"].startswith("https://"):
            raise DependencyError("original source URL is required")
        if rec["evidence_class"] not in {"verified_observation", "company_statement", "inference", "scenario", "unknown_or_conflicted"}:
            raise DependencyError("unknown evidence class")
        if not isinstance(rec["original_currency"], str) or not re.fullmatch(r"[A-Z]{3}", rec["original_currency"]):
            raise DependencyError("original ISO currency required")
        if rec["original_currency"] != "USD" and not isinstance(rec["fx_reference"], str):
            raise DependencyError("foreign exposure requires FX source-reference")
        if rec["original_currency"] == "USD" and rec["fx_reference"] is not None:
            raise DependencyError("USD source must not imply FX conversion")
        if not SHA.fullmatch(rec["source_sha256"]):
            raise DependencyError("source digest must be SHA-256")
        key = (rec["producer"], rec["contract"], rec["record_id"])
        if key in seen:
            raise DependencyError("conflicting or duplicate dependency identities")
        seen.add(key)
        available = _time(rec["available_at"])
        ingested = _time(rec["ingested_at"])
        _time(rec["effective_at"])
        expiry = _time(rec["valid_until"])
        if ingested < available:
            raise DependencyError("ingestion predates first availability")
        if expiry <= available:
            raise DependencyError("expiry cannot precede source availability")
        if ingested > cutoff or available > cutoff:
            raise DependencyError("future-unavailable source cannot enter as-of snapshot")
        out.append(dict(rec))
    out.sort(key=lambda r: (r["producer"], r["contract"], r["record_id"]))
    expired = [r["producer"] + "/" + r["contract"] + "/" + r["record_id"]
               for r in out if _time(r["valid_until"]) <= cutoff]
    return {"schema": SCHEMA, "as_of": cutoff.isoformat(), "inputs": out,
            "fingerprint": _hash(out), "expired_ids": expired,
            "current_use_valid": not expired}


def recompute_decision(*, previous: dict | None, current: dict,
                       model_version: str, config_sha256: str,
                       required_ids: list[str]) -> dict:
    """Return a deterministic nonexecuting intent; never infer worker activity.

    Invalidation is triggered by changed input contents, revisions, or provenance,
    not by a worker run, check, retry or scheduled poll with unchanged evidence.
    """
    if current.get("schema") != SCHEMA or not isinstance(current.get("inputs"), list):
        raise DependencyError("unknown current snapshot contract")
    expected = snapshot(current["inputs"], as_of=current["as_of"])
    if expected != current:
        raise DependencyError("tampered or unreconciled input snapshot")
    if not isinstance(model_version, str) or not model_version.strip() or not SHA.fullmatch(config_sha256):
        raise DependencyError("model/config identity missing")
    if len(required_ids) != len(set(required_ids)) or not all(isinstance(x, str) and x for x in required_ids):
        raise DependencyError("duplicate or empty required IDs")
    names = {r["producer"] + "/" + r["contract"] + "/" + r["record_id"] for r in current["inputs"]}
    # Foreign exposures implicitly depend on their exact FX revision. It must be
    # fresh, unconflicted and present even when the caller omitted it from IDs.
    fx_required = {r["fx_reference"] for r in current["inputs"]
                   if r["original_currency"] != "USD"
                   and r["producer"] + "/" + r["contract"] + "/" + r["record_id"] in required_ids}
    all_required = set(required_ids) | fx_required
    missing = sorted(all_required - names)
    invalid = sorted(set(current["expired_ids"]) & all_required)
    conflicts = sorted(r["producer"] + "/" + r["contract"] + "/" + r["record_id"]
                       for r in current["inputs"] if r["evidence_class"] == "unknown_or_conflicted"
                       and r["producer"] + "/" + r["contract"] + "/" + r["record_id"] in all_required)
    missing_fx = sorted(r["fx_reference"] for r in current["inputs"]
                        if r["original_currency"] != "USD" and r["fx_reference"] not in names
                        and r["producer"] + "/" + r["contract"] + "/" + r["record_id"] in required_ids)
    if previous is not None:
        if previous.get("schema") != SCHEMA or snapshot(previous["inputs"], as_of=previous["as_of"]) != previous:
            raise DependencyError("prior snapshot invalid; no safe comparison")
        if _time(previous["as_of"]) > _time(current["as_of"]):
            raise DependencyError("point-in-time clock regressed")
    old = {} if previous is None else {
        r["producer"] + "/" + r["contract"] + "/" + r["record_id"]: r
        for r in previous["inputs"]
    }
    new = {r["producer"] + "/" + r["contract"] + "/" + r["record_id"]: r
           for r in current["inputs"]}
    changed = sorted(key for key in set(old) | set(new) if old.get(key) != new.get(key))
    fingerprint = _hash({"inputs": current["fingerprint"], "model_version": model_version,
                         "config": config_sha256, "as_of": current["as_of"]})
    if missing or invalid or conflicts or missing_fx:
        state = "blocked"
    elif previous is None or changed:
        state = "recompute_required"
    else:
        state = "unchanged"
    return {"schema": "basket.dependency_decision@1", "state": state,
            "source_snapshot_sha256": current["fingerprint"],
            "idempotency_key": fingerprint, "changed_ids": changed,
            "missing_required_ids": missing, "expired_required_ids": invalid,
            "conflicted_required_ids": conflicts, "missing_fx_references": missing_fx,
            "no_execution_performed": True}