"""Offline consistency checks for proposed lifecycle snapshots; no admission/effects."""
import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry
from orchestration import component_conformance as cc
from orchestration import worker_protocol

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def validate(snapshot, *, now):
    """Check supplied synthetic checkpoint declarations, never collect or trust them.

    Actual identity, leases, qualification and evidence truth belong to existing
    admission/collector owners. This does not resolve refs, launch or write files.
    """
    cc.canonical(snapshot)
    if not isinstance(now, str) or not cc.valid_datetime(now):
        raise ValueError("INVALID_NOW")
    schema = read("lifecycle.schema.json")
    schema["$defs"] = {"artifact_ref": cc.SCHEMA["$defs"]["artifact_ref"]}
    errors = sorted(e.message for e in Draft202012Validator(
        schema, format_checker=cc.FORMATS, registry=Registry()).iter_errors(snapshot))
    if errors:
        return {"valid": False, "errors": errors, "execution_authorized": False}
    errors.extend(worker_protocol.validate_schema(snapshot["task"], "task"))
    request, session = snapshot["request"], snapshot["session"]
    outcome, data = snapshot["outcome"], snapshot["input"]
    instant = datetime.fromisoformat(now.replace("Z", "+00:00"))
    def time(value):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    if time(request["deadline"]) <= instant:
        errors.append("DEADLINE_EXPIRED")
    if time(data["qualified_until"]) <= instant:
        errors.append("INPUT_STALE")
    demand = request["demand"]
    readback = data["freshness_readback"]
    if (time(readback["checked_at"]) < time(demand["requested_at"]) or
            time(readback["checked_at"]) > instant or
            time(demand["requested_at"]) > instant):
        errors.append("CURRENT_DEMAND_NEEDS_FRESHNESS_READBACK")
    if readback["persisted_generation_id"] != demand["persisted_generation_id"]:
        errors.append("GENERATION_READBACK_MISMATCH")
    prior = demand["prior_fulfillment"]
    if prior is not None:
        if prior["attempt_id"] == demand["attempt_id"]:
            errors.append("NEW_DEMAND_MUST_NOT_REUSE_PRIOR_ATTEMPT")
        if time(prior["completed_at"]) >= time(demand["requested_at"]):
            errors.append("PRIOR_FULFILLMENT_ORDER_INVALID")
    if request["input_revision"] != data["artifact"]["sha256"]:
        errors.append("INPUT_REVISION_MISMATCH")
    fingerprint = cc.digest(cc.canonical(request))
    for binding in (snapshot["acknowledgment"], outcome["receipt"]):
        if binding["request_sha256"] != fingerprint:
            errors.append("REQUEST_BINDING_MISMATCH")
    if snapshot["acknowledgment"]["session_id"] != session["session_id"]:
        errors.append("ACK_SESSION_MISMATCH")
    if snapshot["ownership"]["active_writers"] != [session["session_id"]]:
        errors.append("WRITER_MISMATCH")
    if request["branch"] != snapshot["task"]["branch"]["name"]:
        errors.append("BRANCH_MISMATCH")
    for path in request["planned_writes"]:
        if (path.startswith("/") or "\\" in path or
                any(part in ("", ".", "..") for part in path.split("/")) or
                not worker_protocol.permitted(path, snapshot["task"]["write_paths"])):
            errors.append("OUTSIDE_OWNED_PATHS")
    if snapshot["role"] != "fetch_owner":
        if request["operation"] != "consume" or data["access"] != "read_only":
            errors.append("CONSUMER_MUST_NOT_FETCH_OR_WRITE_DATA")
    if snapshot["role"] == "data_consumer" and data["provider_owner"] != "_FETCH":
        errors.append("DATA_MUST_ROUTE_TO_FETCH")
    if snapshot["role"] == "fetch_owner" and data["provider_owner"] != "_FETCH":
        errors.append("FETCH_OWNER_REQUIRED")
    if outcome["state"] == "completed" and not (outcome["invoked"] and outcome["run_observed"]):
        errors.append("SCHEDULE_IS_NOT_EXECUTION")
    if outcome["independent_acceptance"] == "accepted" and outcome["independent_receipt"] is None:
        errors.append("INDEPENDENT_ACCEPTANCE_NEEDS_RECEIPT")
    if outcome["consumer_acceptance"] == "accepted" and outcome["acceptance_receipt"] is None:
        errors.append("ACCEPTANCE_REQUIRES_SEPARATE_RECEIPT")
    if snapshot["privacy"]["input_class"] == "private" and snapshot["privacy"]["publish_input"]:
        errors.append("PRIVATE_INPUT_MUST_NOT_BE_PUBLISHED")
    if (snapshot["privacy"]["requires_private_destination"] or
            snapshot["privacy"]["input_class"] == "private"):
        if snapshot["privacy"]["destination_visibility"] == "public":
            errors.append("PUBLIC_BRANCH_IS_NOT_PRIVATE_DESTINATION")
    if outcome["consumer_usable"] and not (
            outcome["state"] == "completed" and outcome["invoked"] and outcome["run_observed"] and
            outcome["independent_acceptance"] == "accepted" and
            outcome["consumer_acceptance"] == "accepted"):
        errors.append("CONSUMER_USABILITY_NEEDS_ALL_GATES")
    return {"valid": not errors, "errors": sorted(set(errors)),
            "execution_authorized": False}


if __name__ == "__main__":
    fixture = read("lifecycle.examples.json")
    print(json.dumps({name: validate(value, now=fixture["evaluation_time"])
                      for name, value in fixture["examples"].items()}, sort_keys=True))
