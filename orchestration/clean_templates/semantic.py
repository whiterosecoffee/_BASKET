"""Local semantic evidence profile; delegates worker/lifecycle contracts, never executes."""
import copy
import json
from jsonschema import Draft202012Validator
from referencing import Registry
from orchestration import component_conformance as cc, worker_protocol as wp
from orchestration.clean_templates import lifecycle as lc


def obj(properties):
    return {"type": "object", "additionalProperties": False,
            "required": list(properties), "properties": properties}


def array(items, **limits):
    return {"type": "array", "items": items, **limits}


def profile():
    """Private wrapper shape, not a new worker/graph/status authority."""
    text = {"type": "string", "minLength": 1, "pattern": r"\S"}
    ref = cc.SCHEMA["$defs"]["artifact_ref"]
    nullable_ref = {"anyOf": [{"type": "null"}, ref]}
    task_schema = wp.read(wp.ROOT / "schemas/worker-task.v1.json")
    return obj({
        "profile": {"const": "clean-template-semantic-example-v1"},
        "synthetic": {"const": True},
        "lifecycle": {"type": "object"}, "resolution": {"type": "object"},
        "active_objectives": array(obj({
            "task_id": text, "owner_session": text, "purpose": text,
            "outcomes": array(text, minItems=1, uniqueItems=True),
            "non_goals": array(text, minItems=1, uniqueItems=True), "intake_id": text,
        }), minItems=1, maxItems=1),
        "planned_children": array(obj({
            "id": text, "parent_task_id": text, "purpose": text,
            "intended_owner": text, "acceptance": task_schema["properties"]["acceptance"],
            "branch": {"type": "null"}, "running_worker": {"type": "null"},
        })),
        "intake": array(obj({
            "id": text, "kind": {"enum": ["question", "idea", "commitment"]},
            "text": text, "source": ref,
            "supersedes": {"anyOf": [{"type": "null"}, text]},
            "approval": nullable_ref,
        }), minItems=1),
        "wake": obj({"id": text, "idempotency_key": text, "uncertain_effect": {"type": "boolean"}}),
        "known_effects": array(obj({"id": text, "evidence": ref})),
    })


def evaluate(packet, *, prior, now, expected_revision):
    """Compare supplied snapshots against a caller-retained prior and expected head.

    No storage/ledger/authentication is supplied. Even fully consistent fictional
    declarations cannot authorize execution. Prior and head need external attestation.
    """
    errors = []
    schema = profile()
    prior_shape_valid = False
    for name, value in (("packet", packet), ("prior", prior)):
        shape_errors = list(Draft202012Validator(
            schema, format_checker=cc.FORMATS, registry=Registry()).iter_errors(value))
        errors.extend(name + ": " + e.message for e in shape_errors)
        if name == "prior":
            prior_shape_valid = not shape_errors
    result = {"valid": False, "errors": [], "execution_authorized": False,
              "new_executions": [], "action": "reject", "known_effects":
              copy.deepcopy(prior["known_effects"]) if prior_shape_valid else []}
    if errors:
        result["errors"] = sorted(set(errors))
        return result
    result["known_effects"] = copy.deepcopy(prior["known_effects"])
    for name, value in (("packet", packet), ("prior", prior)):
        errors.extend(name + ": " + e for e in lc.validate(value["lifecycle"], now=now)["errors"])
        errors.extend(name + ": " + e for e in wp.validate_schema(value["resolution"], "resolution"))
    if errors:
        result["errors"] = sorted(set(errors))
        return result
    for value in (prior, packet):
        life, resolution = value["lifecycle"], value["resolution"]
        task, request = life["task"], life["request"]
        active = value["active_objectives"][0]
        if (active["task_id"] != task["task_id"] or active["purpose"] != task["objective"] or
                active["owner_session"] != life["session"]["session_id"]):
            errors.append("ACTIVE_OBJECTIVE_OWNER_MISMATCH")
        criteria = [a["id"] for a in task["acceptance"]]
        if (len(set(criteria)) != len(criteria) or set(active["outcomes"]) != set(criteria) or
                sorted(a["id"] for a in resolution["acceptance"]) != sorted(criteria)):
            errors.append("OUTCOMES_MUST_BIND_TASK_CRITERIA")
        for field in ("task_id", "spark_id", "issue", "branch"):
            if resolution[field] != task[field]:
                errors.append("RESOLUTION_TASK_MISMATCH")
        # This wrapper cannot promote canonical worker/integration states.
        if resolution["disposition"] != "in_progress" or task["state"] != "review":
            errors.append("PROFILE_DOES_NOT_PROMOTE_WORKER_STATUS")
        if any(a["result"] != "not_verified" for a in resolution["acceptance"]):
            errors.append("PROFILE_DOES_NOT_VERIFY_RESOLUTION_ACCEPTANCE")
        if request["source_revision"] != expected_revision:
            errors.append("EXPECTED_HEAD_MISMATCH")
        if value["wake"]["idempotency_key"] != request["idempotency_key"]:
            errors.append("WAKE_REQUEST_MISMATCH")
        ids = set()
        for child in value["planned_children"]:
            if child["id"] in ids or child["id"] == task["task_id"]:
                errors.append("DUPLICATE_CHILD_ID")
            ids.add(child["id"])
            if child["parent_task_id"] != task["task_id"]:
                errors.append("CHILD_PARENT_MISMATCH")
        seen = {}
        for entry in value["intake"]:
            if entry["id"] in seen:
                errors.append("DUPLICATE_INTAKE_ID")
            if entry["supersedes"] is not None and entry["supersedes"] not in seen:
                errors.append("CORRECTION_REQUIRES_RETAINED_PREDECESSOR")
            if (entry["kind"] == "commitment") != (entry["approval"] is not None):
                errors.append("COMMITMENT_REQUIRES_EXPLICIT_APPROVAL")
            seen[entry["id"]] = entry
        selected = seen.get(active["intake_id"])
        if selected is None or selected["kind"] != "commitment" or selected["text"] != active["purpose"]:
            errors.append("QUESTION_OR_IDEA_IS_NOT_ACTIVE_COMMITMENT")
        if any(e["supersedes"] == active["intake_id"] for e in value["intake"]):
            errors.append("ACTIVE_COMMITMENT_SUPERSEDED")
        effects = [e["id"] for e in value["known_effects"]]
        if len(effects) != len(set(effects)):
            errors.append("DUPLICATE_EFFECT_ID")
    for field in ("intake", "known_effects"):
        if packet[field][:len(prior[field])] != prior[field]:
            errors.append("PRIOR_" + field.upper() + "_MUST_BE_RETAINED")
    if packet["lifecycle"]["request"] != prior["lifecycle"]["request"]:
        errors.append("REPLAY_REQUEST_CHANGED_REQUIRES_OWNER_RECONCILIATION")
    if errors:
        result["errors"] = sorted(set(errors))
        return result
    result.update(valid=True, known_effects=copy.deepcopy(packet["known_effects"]),
                  action="reconcile_uncertain_effect" if packet["wake"]["uncertain_effect"] or
                  prior["wake"]["uncertain_effect"] else "reuse_existing_evidence")
    return result


if __name__ == "__main__":
    fixture = lc.read("semantic.examples.json")
    print(json.dumps({name: evaluate(packet, prior=fixture["prior"],
          now=fixture["evaluation_time"], expected_revision=fixture["expected_revision"])
          for name, packet in fixture["examples"].items()}, sort_keys=True))
