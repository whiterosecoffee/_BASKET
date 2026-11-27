"""Stable offline, in-process AH-MRI entrypoint for caller-supplied observations.

This is not a hosted endpoint or market-data producer. B02 source certification,
B01 exact-head tests, and B00 shared API approval remain external gates.
"""
from collections.abc import Mapping

try:
    from .core import analyze, markdown
except ImportError:
    from core import analyze, markdown

def analyze_eod(request):
    """Return deterministic JSON/Markdown results or a bounded validation error.

    Contract: mapping with as_of, completed session, and instruments.
    No network activity, scheduling, storage, or source entitlement checks.
    """
    if not isinstance(request, Mapping):
        return _error("invalid_request", "expected JSON object")
    for field in ("as_of", "session", "instruments"):
        if field not in request:
            return _error("invalid_request", "missing required field: " + field)
    if not isinstance(request["session"], Mapping) or not isinstance(request["instruments"], list):
        return _error("invalid_request", "session must be an object and instruments a list")
    try:
        result = analyze(dict(request))
        rendered = markdown(result)
    except (ValueError, KeyError, TypeError, OverflowError) as err:
        # Do not echo data values or stack traces into consumer output.
        return _error("invalid_observations", type(err).__name__)
    return {
        "schema": "basket.ah_mri.invoke@0.1",
        "status": "research_provisional",
        "transport": "in_process_offline",
        "source_certified": False,
        "production_ready": False,
        "report": result,
        "markdown": rendered,
        "input_manifest_hash": result["input_manifest_hash"],
        "limitations": [
            "Caller-supplied timestamps and source IDs are not independently certified.",
            "No B02 provider adapter, historical calibration, scheduler, or live service.",
        ],
    }

def _error(code, detail):
    return {
        "schema": "basket.ah_mri.invoke@0.1",
        "status": code,
        "detail": detail,
        "transport": "in_process_offline",
        "source_certified": False,
        "production_ready": False,
        "report": None,
        "markdown": None,
    }
