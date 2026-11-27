"""AH-MRI component readiness assessment; this is NOT a release authorization.

All inputs are caller-declared evidence. This module cannot independently verify links,
tool entitlements, data provenance, test runs, or a merged/green main.
"""
from collections.abc import Mapping

GATES = (
    ("source_snapshot", "B02", "source-proven, point-in-time completed-session sample"),
    ("session_calendar", "B02", "official timezone/holiday/early-close adapter"),
    ("geometry_adapter", "B06", "synchronized independent traversal output"),
    ("cross_market_context", "B17", "synchronized breadth/sector context"),
    ("historical_replay", "B07", "walk-forward out-of-sample frozen replay"),
    ("independent_ci", "B01", "exact-head independently executed tests"),
    ("contract_arbitration", "B00", "approved consumer/producer contract"),
    ("operational_replay", "B08", "durable scheduler, replay and failure monitoring"),
)

def evaluate(evidence=None):
    """Deterministic checklist: claimed != independently verified."""
    if evidence is None:
        evidence = {}
    if not isinstance(evidence, Mapping):
        raise ValueError("evidence must be a mapping")
    gates = []
    for name, owner, required in GATES:
        attestation = evidence.get(name)
        if attestation is None:
            status, ref = "missing", None
        elif not isinstance(attestation, Mapping):
            status, ref = "invalid", None
        else:
            ref = attestation.get("evidence_ref")
            requested = attestation.get("status")
            # A user-supplied status cannot certify a production gate.
            status = ("claimed_unverified" if requested == "pass" and isinstance(ref, str)
                      and ref.strip() else "invalid")
        gates.append({"gate": name, "owner": owner, "required": required,
                      "status": status, "evidence_ref": ref if status == "claimed_unverified" else None})
    counted = sum(g["status"] == "claimed_unverified" for g in gates)
    return {
        "schema": "basket.ah_mri.readiness@0.1",
        "phase": "research_local",
        "attested_gates": counted,
        "required_gates": len(gates),
        "independently_verified_gates": 0,
        "production_ready": False,
        "release_authorized": False,
        "gates": gates,
        "blockers": [g["gate"] for g in gates if g["status"] != "claimed_unverified"],
        "warning": "External B00/B01 verification required; supplied claims are not independent evidence.",
    }
