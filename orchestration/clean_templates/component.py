"""Offline callable adaptation of the seed validator, not a new controller."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from .validate import validate_seed

ROOT = Path(__file__).resolve().parent


def probe(request):
    """Consume one JSON request and return readiness; never dispatch work.

    Invalid envelopes raise ValueError. Structurally invalid seeds return
    state=invalid, distinct from missing-capability state=blocked.
    """
    schema = json.loads((ROOT / "request.schema.json").read_text(encoding="utf-8"))
    errors = sorted(e.message for e in Draft202012Validator(schema).iter_errors(request))
    if errors:
        raise ValueError("INVALID_REQUEST: " + "; ".join(errors))
    return validate_seed(request["seed"], request["available_capabilities"])
