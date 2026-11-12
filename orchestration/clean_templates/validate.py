"""Pure validation for clean seeds; references are never opened or executed."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).with_name("seed.schema.json")


def validate_seed(seed, available_capabilities):
    """Return structural errors separately from genuine capability blockers.

    Availability is supplied by the caller, not inferred from archived files,
    issue status, network access, or successful validation of this manifest.
    """
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(error.message for error in Draft202012Validator(schema).iter_errors(seed))
    if errors:
        return {"state": "invalid", "errors": errors, "missing_capabilities": []}
    if not isinstance(available_capabilities, (list, tuple, set)) or any(
        not isinstance(value, str) or not value for value in available_capabilities
    ):
        raise ValueError("available_capabilities must be explicit nonempty capability names")
    missing = sorted(set(seed["requires"]) - set(available_capabilities))
    return {"state": "blocked" if missing else "ready_for_local_probe",
            "errors": [], "missing_capabilities": missing}
