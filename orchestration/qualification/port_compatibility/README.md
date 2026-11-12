# Portable port qualification

Issue #247, spark B00. This is a synthetic qualification corpus for the existing
`orchestration.component_conformance.check_exchange` helper, pinned to main
`74d913e8913d630d85451344689e093aeea07efc`. It is not a compatibility engine,
component implementation, dependency registry or domain acceptance.

Run from the repository root (Python 3.12 with jsonschema available):

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/qualification/port_compatibility -p test_ports.py -v
PYTHONDONTWRITEBYTECODE=1 python orchestration/qualification/port_compatibility/run.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/tests -p 'test_component*.py' -v
```

`run.py` prints a JSON receipt to stdout and unittest diagnostics to stderr. It
performs no writes or network access. Checked-in `evidence.json` records the actual
local run, not current CI state. Python 3.12.14 / jsonschema 4.26.0 were tested;
shared hosted CI pins jsonschema 4.23.0. This new folder is **not discovered by
shared CI**. No discovery bridge or shared workflow was changed.

## Corpus and exact mapping

`corpus.json` contains 15 self-contained exchange specimens. Each contains the
manifest, call, result, independent input fingerprint and exact UTF-8 artifact
strings. No downloaded/provider data or private conversation text is included.
Artifact names use `fixture://`; the helper receives their bytes explicitly and
never resolves them externally. Synthetic schemas are fixture-local, unregistered
contracts. The output is constructed, not produced by a domain computation.

| Cases | Existing contract enforcement |
| --- | --- |
| Valid exchange | `qualified_refs_v1`; manifest/call/result schema validation |
| Missing required input/output | `_bindings`: required set minus supplied bindings |
| Wrong named input/output | `_bindings`: supplied bindings minus declared set |
| Schema identity mismatch | `_bindings`: exact `schema_ref`, even with identical bytes |
| Schema version mismatch | `_bindings`: exact `schema_sha256`; fixture changes `$id` v1 to v2 and recomputes the binding hash |
| Component version mismatch | `check_exchange`: exact `contract_version == manifest.version` |
| Unexpected input/output payload | `_validate`: resolved schema `additionalProperties: false`; payload hash is recomputed to isolate the shape violation |
| Stale pinned input/output source | `_bytes`: supplied source bytes differ from the declared SHA-256 |
| Unresolved dependency declaration | **Unsupported**: helper accepts a declaration without checking availability or version range |

Schema version here is a changed schema identity/content pin, not a generic
semantic-version policy. Stale source here means changed bytes under an old pin,
not time-to-die or point-in-time eligibility. Input hashing is explicitly sorted,
compact JSON of the original input bindings. Negative variants retain the
independently supplied original fingerprint, so they isolate the named contract
checks without imposing a new universal hashing policy.

## Observed results and known gap

19 tests: **18 passed, 1 expected failure, 0 unexpected failures/errors/skips**.
The 15 corpus cases comprise one valid accepted exchange, 13 required rejections,
and one unsupported rejection. Four additional checks cover pins, repeat/mutation,
corpus coverage and independently computed input serialization. The existing
component suites separately passed **47 tests, 0 failures/errors/skips**.

`test_declared_dependency_without_resolution` requires rejection of a manifest
that declares `synthetic.unavailable >=2.0.0` without an available dependency.
The actual helper accepts it. The contract document's semantic gates 1 and 4
require dependency compatibility, but this helper has no dependency inventory
argument or range resolver. The expected failure preserves the unmet gate; it
is not a pass. `evidence.json` separately records `actual.outcome: accept` and
`expectation: unsupported_rejection`. No replacement resolver is introduced.

`source-pins.json` fingerprints the validator, canonical schema and contract
text. Tests compare current bytes to those pins, rerun every specimen, compare
outcomes, compare the entire in-memory corpus, and verify unchanged source hashes.
The source pin test intentionally fails if a future checkout changes those files;
requalification must then deliberately update the pins and review behavior.

## Acceptance boundary and next owner

Bounded supported exchange qualification is tested locally. Independent acceptance
remains with #105; shared contract decisions remain #103. #226's virtual traces
and #230's design remain read-only context, not implemented execution or evidence
for these results. Semver dependency resolution, cross-component composition,
units, entitlement, temporal availability, payload truth and operational behavior
are not accepted by this corpus. No archived runtime is a prerequisite.

Next action: #103/#105 owners review the unresolved-dependency specimen and decide
whether a separate approved dependency preflight is required. Preserve this gap
until exact-source owner implementation and independent acceptance exist.
