# Schema standards decision — B00 #249

Recommendation: retain JSON Schema Draft 2020-12 and the existing offline component helper. Require an explicit dialect on newly authored reusable payload schemas as an owner-reviewed admission rule; do not silently translate Draft 7 schemas. This is a proposed adoption decision and tested qualification corpus, not a canonical schema, production validator, or accepted system policy.

`decision.json` is the machine-readable decision and bounded inventory. `corpus.json` contains 23 original synthetic cases; `test_interoperability.py` executes them plus two source/inventory checks. `evidence.json` records actual versions, results and content hashes. Run from repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/qualification/schema_standards -p 'test_*.py' -v
```

Use an already provisioned interpreter. No installation is needed or performed here. Local executions passed 25 tests on each of jsonschema 4.26.0 and 4.23.0, both with referencing 0.37.0. The existing component regression suite passed 47 tests on 4.26.0. The pinned source hashes intentionally fail after upstream helper/schema/version-policy changes; refresh them only after reviewing changed semantics. These tests directly call private helper seams for qualification, not as a promised public API.

## Concrete findings and decision

All 15 direct `schemas/*.json` definitions on main `74d913e8913d630d85451344689e093aeea07efc` declare 2020-12. The inventory is bounded to that canonical directory, not every candidate branch or nested example. Four contain `$id` values pointing to GitHub `blob/main`; these identify schemas but do not pin immutable bytes. The component boundary separately carries `schema_ref` and `schema_sha256`, and the helper verifies supplied bytes. Preserve that distinction. `contract_version` identifies the selected component boundary; `.v1.json`, `basket.*@1`, dialect, component version and repository revision are separate axes. See the pinned [boundary contract](https://github.com/whiterosecoffee/_BASKET/blob/74d913e8913d630d85451344689e093aeea07efc/architecture/BLACK_BOX_COMPONENT_CONTRACT.md) and [version policy](https://github.com/whiterosecoffee/_BASKET/blob/74d913e8913d630d85451344689e093aeea07efc/architecture/VERSIONING.md).

| Family | Near-term fit | Decision |
|---|---|---|
| JSON Schema 2020-12 | Existing canonical dialect; local `$defs`/`$ref`, reference siblings, closed compositions and tuples work in the tested cases | Adopt existing implementation unchanged; adapt admission guidance to require explicit dialect |
| JSON Schema Draft 7 | Useful comparison for older external schemas; `$ref` siblings and unknown `unevaluatedProperties` yield different acceptance | Reject as an automatic replacement or silent down-conversion; retain only explicit future migration evidence |

The paired cases show Draft 7 accepts an integer below a `$ref` sibling minimum and an extra property under `unevaluatedProperties`; 2020-12 rejects them. Both are expected observations, not test failures. Old tuple syntax is rejected under 2020-12. The standards describe these different keyword semantics: [Draft 7 core](https://json-schema.org/draft-07/draft-handrews-json-schema-01), [2020-12 core](https://json-schema.org/draft/2020-12/json-schema-core), and [2020-12 changes](https://json-schema.org/draft/2020-12/release-notes).

The existing helper rejects explicit Draft 7/unknown dialects and external `$ref`/`$dynamicRef`, but accepts a missing `$schema` by assuming 2020-12. That is an observed gap in explicit admission, not a claim of misvalidation for every undeclared schema. New clean artifacts should declare the dialect; existing owner #156 can decide whether requiring it is compatible for older payloads. Missing fragment targets fail resolution. An empty Registry prevents remote retrieval; the tests also prohibit socket construction and assert schema/instance equality before and after. The trusted libraries expose the [offline Registry API](https://python-jsonschema.readthedocs.io/en/v4.23.0/referencing/); no repository registry is added.

`format` is annotation by default in the direct validator case; the existing helper's explicit date-time checker rejects the same malformed input. Preserve its checker and timezone/leap-second conventions. See [validator configuration](https://python-jsonschema.readthedocs.io/en/stable/validate/). Local recursive dynamic references pass the two small cases. Cross-resource dynamic scope, custom required vocabularies, cross-dialect embedded resources, arbitrary unknown keywords, all optional formats, non-Python validator parity and full JSON Schema Test Suite conformance remain unqualified. No support claim is made for them. URI/path escape behavior and port compatibility belong to separate lanes.

## Dependencies, licensing and acceptance boundary

The existing shared CI pins jsonschema 4.23.0; the cloud default has 4.26.0. Both installed environments were exercised without changing dependencies. Installed jsonschema, referencing, attrs, rpds-py and jsonschema-specifications report MIT licenses; exact versions are in evidence. Retain notices if redistributing implementation code: [jsonschema license](https://github.com/python-jsonschema/jsonschema/blob/v4.26.0/COPYING), [referencing license](https://github.com/python-jsonschema/referencing/blob/v0.37.0/COPYING). No implementation code or specification examples are vendored. Specification texts have their own IETF notices and are cited, not relicensed. MIT metadata is not an audit of every optional/transitive dependency or an approval to add one.

Acceptance here is a local, synthetic dialect qualification only: 25/25 on each installed version, zero errors/failures/skips; no network calls or mutated inputs in corpus execution. Hosted shared CI does not discover this folder, so its success cannot certify these tests. No independent review, full standard compliance, domain payload qualification, integration or operational acceptance is claimed. Failed exploratory commands (missing root requirements file and unauthenticated gh CLI) did not change repository content; connector reads and installed package metadata supplied the required evidence.

Next action: existing #103/#156 owners review the explicit-dialect admission recommendation and #105 independently reruns this exact corpus before any adoption. #136 G1/G2, #224 and #230 remain existing routing authorities; their files are untouched.
