"""Compare exactly two offline probe receipts; never rank or authorize work."""
from orchestration import component_conformance as cc
from . import composition

LIMITATION = ("Integrity-checked declarations only; readiness and caller metadata "
              "are not authenticated computation or execution authority.")


def _index(items, payload):
    if not isinstance(items, list) or len(items) != 2:
        raise ValueError("EXPECTED_TWO_CANDIDATES")
    indexed = {}
    for item in items:
        if not isinstance(item, dict) or set(item) != {"candidate_id", payload}:
            raise ValueError("INVALID_CANDIDATE_ENVELOPE")
        identity = item["candidate_id"]
        if not isinstance(identity, str) or not identity.strip():
            raise ValueError("INVALID_CANDIDATE_ID")
        if identity in indexed:
            raise ValueError("DUPLICATE_CANDIDATE_ID")
        indexed[identity] = item[payload]
    return indexed


def _requests(candidates):
    requests = _index(candidates, "request")
    if len({cc.canonical(value) for value in requests.values()}) != 2:
        raise ValueError("DUPLICATE_REQUEST")
    return requests


def compare(candidates, receipts):
    """Bind each receipt to its expected candidate request using existing consume.

    No output is returned if either exchange fails. Request/receipt validation
    stays in composition.consume; this module checks only comparison identities.
    """
    requests = _requests(candidates)
    received = _index(receipts, "receipt")
    if set(requests) != set(received):
        raise ValueError("CANDIDATE_SET_MISMATCH")
    rows = []
    for identity in sorted(requests):
        request = requests[identity]
        readiness = composition.consume(received[identity], expected_request=request)
        rows.append({"candidate_id": identity,
                     "request_sha256": cc.digest(cc.canonical(request)),
                     "declared_readiness": readiness})
    return {"schema": "basket.clean_seed_comparison@1",
            "evidence_class": "offline_integrity_checked_declarations",
            "execution_authorized": False, "limitation": LIMITATION,
            "candidates": rows}


def compose_comparison(candidates, *, as_of, code_sha):
    """Compose the existing fixed probe twice, then consume its explicit ports."""
    requests = _requests(candidates)
    receipts = [{"candidate_id": identity,
                 "receipt": composition.compose(requests[identity], as_of=as_of,
                                                code_sha=code_sha)}
                for identity in sorted(requests)]
    return compare(candidates, receipts)


def example():
    candidates = [{"candidate_id": identity, "request": composition.read(filename)}
                  for identity, filename in (
                      ("basic-intake", "comparison.ready.request.json"),
                      ("review-required", "comparison.blocked.request.json"))]
    return compose_comparison(candidates, as_of="2026-11-12T00:00:00Z",
                              code_sha="6f5e39cd8590a6431bec56cd62af086bb28d6326")


if __name__ == "__main__":
    print(cc.canonical(example()).decode("utf-8"))
