# Repeatable offline composition

`composition.request.json` supplies a synthetic JSON request to the existing
`component.probe` request port. Its readiness output becomes an in-memory artifact
in a JSON receipt; `consume` validates and reads that explicit output port.

The example reuses `schemas/component-blackbox.v1.json` call/result definitions
and `orchestration.component_conformance.check_exchange`. It adds no general
runner, fetcher, scheduler, materializer or archived implementation dependency.
The existing discovery bridge automatically includes its tests.

Run from the repository root (Python with jsonschema installed):

```powershell
python -m orchestration.clean_templates.composition --as-of 2026-11-12T00:00:00Z --code-sha 9ff7508308112da59f1fdeecc4a23136259a2f29
python -m unittest discover -s orchestration/clean_templates/tests -v
```

The command writes one JSON receipt to stdout, with a manifest, call, result and
explicit UTF-8 artifact strings. It writes no files. Identical inputs, metadata
and local method bytes produce identical serialized receipts. Python consumers
can call `compose(request, as_of=..., code_sha=...)`, serialize/deserialize the
receipt, then call `consume(receipt, expected_request=request)`.

Port schema hashes use the existing helper's sorted compact JSON serialization;
input provenance hashes the canonical request bytes. Method bytes pin the local
probe, seed validator and seed schema. Receipt validation uses only explicitly
supplied artifact bytes and fixed local contracts, never reference locators.

`result.status=ok` means the readiness calculation returned successfully. The
readiness artifact can still say `blocked` or `invalid`. Malformed request
envelopes raise `INVALID_REQUEST` before any receipt is returned. No capability
assertion, hash, contract profile or success status grants execution authority.

This is a fixture/probe receipt, not signed execution evidence. The caller declares
`code_sha` and `as_of`; `generated_at` repeats that fixture timestamp, not a measured
wall-clock time. Consumers check contract and byte integrity, not whether the
caller truthfully declared its source revision or executed the probe. Independent
acceptance, integration and operational qualification remain separate gates.

Predetermined tests cover success, missing capability, invalid seed, malformed
request, deterministic repeat, unchanged input, fixed-file-only access, no
network/dispatch, byte tampering, invalid output despite updated hashes, expected
request/manifest mismatch and repeatable CLI output.

A future materializer needs a separately scoped output-root/path policy and owner
approval, with atomic writes, collision/replay behavior and independent acceptance.
That extension is proposed only; this composition does not create components or
write outside this subtree.
