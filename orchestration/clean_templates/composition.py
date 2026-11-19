"""Fixed request -> existing probe -> checked JSON receipt; not a runner."""
import copy
import json
from pathlib import Path

from orchestration import component_conformance as cc
from .component import probe

ROOT = Path(__file__).resolve().parent
WARNING = "Capability assertions and receipt conformance grant no execution authority."


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))


def manifest():
    value = read("component.json")
    value["boundary_profile"] = "qualified_refs_v1"
    for port in value["inputs"] + value["outputs"]:
        name = {"request": "request.schema.json", "readiness": "readiness.schema.json"}[port["name"]]
        port.update(schema_sha256=cc.digest(cc.canonical(read(name))),
                    freshness_policy="not_applicable", source_class="scenario")
    return value


def compose(request, *, as_of, code_sha):
    """Run the fixed probe. Timestamp and source revision are caller declarations.

    as_of also supplies fixture generated_at, not measured execution time.
    """
    request = copy.deepcopy(request)
    request_bytes = cc.canonical(request)
    readiness = probe(request)
    contract = manifest()
    artifacts = {}

    def reference(name, data):
        artifacts[name] = data.decode("utf-8")
        return {"ref": name, "sha256": cc.digest(data)}

    def binding(port, value):
        name = {"request": "request.schema.json", "readiness": "readiness.schema.json"}[port["name"]]
        reference(port["schema_ref"], cc.canonical(read(name)))
        payload = reference("example://" + port["name"], cc.canonical(value))
        source = dict(source_id=port["name"], artifact=payload, record_type="scenario",
                      subject_id="clean-seed-offline-example", observed_at=None,
                      available_at=None, ingested_at=None, effective_at=None,
                      published_at=None, period=None, session="not_applicable",
                      unit="protocol_record", currency=None, freshness="not_applicable",
                      entitlement="not_required", supersedes=None)
        return dict(schema_ref=port["schema_ref"], schema_sha256=port["schema_sha256"],
                    artifact=payload, sources=[source])

    inputs = {"request": binding(contract["inputs"][0], request)}
    outputs = {"readiness": binding(contract["outputs"][0], readiness)}
    method = reference("example://probe-method", cc.canonical({
        name: cc.digest((ROOT / name).read_bytes())
        for name in ("component.py", "validate.py", "seed.schema.json")}))
    identity = dict(component_id=contract["component_id"], contract_version=contract["version"],
                    run_id="probe-" + cc.digest(request_bytes), as_of=as_of)
    call = dict(contract="basket.component_call@1", **identity, inputs=inputs,
                method=method, options=dict(offline=True, seed=None))
    result = dict(contract="basket.component_result@1", **identity, status="ok", outputs=outputs,
                  provenance=dict(input_sha256=cc.digest(request_bytes), method=method,
                                  code_sha=code_sha, generated_at=as_of),
                  quality=dict(freshness="not_applicable", missing_inputs=[], conflicts=[],
                               warnings=[WARNING]), error=None)
    receipt = dict(manifest=contract, call=call, result=result, artifacts=artifacts)
    consume(receipt, expected_request=request)
    return receipt


def consume(receipt, *, expected_request):
    """Check contracts/bytes against the local manifest and expected request.

    Conformance does not attest execution, source revision or independent review.
    """
    if set(receipt) != {"manifest", "call", "result", "artifacts"}:
        raise ValueError("INVALID_RECEIPT")
    contract = manifest()
    if receipt["manifest"] != contract:
        raise ValueError("UNEXPECTED_MANIFEST")
    artifacts = {key: value.encode("utf-8") for key, value in receipt["artifacts"].items()}
    expected_bytes = cc.canonical(expected_request)
    cc.check_exchange(contract, receipt["call"], receipt["result"], artifacts,
                      expected_input_sha256=cc.digest(expected_bytes))
    request_ref = receipt["call"]["inputs"]["request"]["artifact"]["ref"]
    if artifacts[request_ref] != expected_bytes:
        raise ValueError("REQUEST_MISMATCH")
    output_ref = receipt["result"]["outputs"]["readiness"]["artifact"]["ref"]
    return json.loads(artifacts[output_ref])


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", required=True, help="Fixture timestamp, not execution time")
    parser.add_argument("--code-sha", required=True, help="Caller-declared source revision")
    args = parser.parse_args()
    request = read("composition.request.json")
    print(cc.canonical(compose(request, as_of=args.as_of, code_sha=args.code_sha)).decode())


if __name__ == "__main__":
    main()
