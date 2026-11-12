# Portable port and dependency qualification

Issue #247 / PR254, B00 bounded continuation under #103. Existing validator
`orchestration.component_conformance.check_exchange` now performs offline direct
dependency preflight in addition to the original named-port checks. Approved
additional paths are the validator, its existing component test file and
`architecture/BLACK_BOX_COMPONENT_CONTRACT.md`; no schema or CI changes.

```sh
PYTHONDONTWRITEBYTECODE=1 python orchestration/qualification/port_compatibility/run.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/tests -p 'test_component*.py' -v
```

The runner prints reproducible JSON to stdout and test diagnostics to stderr.
`evidence.json` records actual results. `corpus.json` contains 22 self-contained
synthetic exchanges, with exact UTF-8 artifact strings. No provider data or
private text is used; outputs are constructed, not domain execution.

## Contract mapping

| Cases | Actual enforcement |
| --- | --- |
| Valid exchange | Existing qualified_refs_v1 schema and exchange checks |
| Missing/wrong named input and output | `_bindings` required and declared sets |
| Schema identity/version mismatch | Exact schema_ref and schema_sha256 pins; no schema-version inference |
| Component version mismatch | Exact contract_version against manifest |
| Unexpected payload | Resolved local schema additionalProperties=false with recomputed payload hash |
| Stale source | Actual source bytes against declared SHA-256; not temporal freshness |
| Missing dependency inventory / unavailable dependency | `_dependency_preflight` explicit dict and direct identity lookup |
| Compatible/incompatible version | Numeric major/minor/patch exact equality or single >= lower bound |
| Unsupported/malformed constraint and inventory | Strict fail-closed syntax and inventory validation |

Call with `dependency_inventory={"synthetic.unavailable": "2.1.0"}` for a declared
`>=2.0.0` dependency. Supported forms are `M.m.p`, `=M.m.p`, `>=M.m.p` using ASCII
nonnegative integer parts without leading zeros. >= deliberately permits higher
major versions; it does not assert semantic compatibility. No whitespace, ranges,
unions, wildcards, prerelease/build metadata or general semver dialect. Every
supplied entry is validated when dependencies exist. Dependency-free exchanges
preserve previous behavior. Inventory availability/version facts are caller
assertions, not independently attested implementation or authorization evidence.
No discovery, recursive resolution, fetching or execution occurs.

## Results, history and limits

Focused suite: **26 passed**, zero expected failures, failures, errors or skips.
Existing component suites: **58 passed**, including 11 named preflight regressions.
Full orchestration results are separately recorded in attempts.json after execution.
Repeated exchange observations and complete corpus inputs remain identical; current
validator/contract/schema bytes match source-pins.json before and after execution.
Canonical schema remains unchanged. The fixture fingerprint uses sorted compact
JSON of original inputs; negative cases retain that independent fingerprint.

Historical source `65c9782ff2a6fa9b8fd0b4fe3d40dfb3a89c913c` had 18 passes and one
expected failure because unresolved dependencies were accepted. This is preserved
in historical-evidence.json and historical-source-pins.json, and the original Git
revision. The same reproducer is now an ordinary required rejection. No historical
failure is erased or retroactively relabelled as passing.

Shared hosted CI discovers the 11 new regressions in the existing component suite,
but does **not** discover this portable focused folder. Environment versions are in
evidence.json; shared CI pins jsonschema 4.23.0. Independent #105 acceptance remains
separate. Temporal/unit/entitlement, transitive dependencies, inventory truth,
composition and domain/operational acceptance remain outside the demonstrated scope.
Next: #105 reviews exact-head preflight evidence under #103 authority.
