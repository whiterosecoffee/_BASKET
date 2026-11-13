# Offline JSON reference portability audit

B00 #245; parent #136 G1/G2. Python 3.10+ standard library only.
The isolated root is supplied explicitly. No laptop, archived component,
provider API, credentials, installation, or repository imports are required.

```sh
python -B orchestration/qualification/reference_portability/audit.py --root orchestration/qualification/reference_portability/fixtures --entry nested-case.json
python -B orchestration/qualification/reference_portability/audit.py --root orchestration/qualification/reference_portability/fixtures --entry reuse-case.json
python -B -m unittest discover -s orchestration/qualification/reference_portability -p 'test_*.py' -v
```

Library: `audit(root, entry)` returns a JSON-serializable report. CLI writes that
report to stdout, exits 0 on success and 1 on audit failures (2 for invalid CLI
arguments). Output contains stable root-relative POSIX source/target paths,
JSON-pointer declaration locations, exact-byte SHA-256 hashes, statuses and
error/informational findings. It contains no clock or absolute root identity.
The raw `ref` is preserved for diagnostics, including unsupported absolute paths;
do not publish reports containing private locators without reviewing them.

## Explicit declaration profile

Each visited JSON object may declare one top-level `references` array:

```json
{"references": [
  {"ref": "nested/worker.json", "use": "required"},
  {"ref": "old-design.json", "use": "archive"}
]}
```

Each declaration has `ref`, optional lowercase 64-character `sha256`, and
optional `use`: `required` (default), `reference_only`, or `archive`. Unknown
keys/usages, malformed declarations, duplicate JSON keys and nonfinite numbers
fail closed. Files without `references` are leaves. Required JSON files are
visited transitively, with cycle deduplication. Every edge is checked separately,
including multiple pins to the same target. Relative paths resolve from the
containing document, not the process working directory. `..` is supported only
while remaining inside the supplied root.

This is a local audit input profile, not a new registry or canonical component
schema. `ref`/`sha256` and exact-byte hashing follow the read-only
[`artifact_ref`](../../../schemas/component-blackbox.v1.json) and
[`component_conformance.digest`](../../component_conformance.py) conventions
at base `74d913e8913d630d85451344689e093aeea07efc`. No content normalization is
performed before hashing. The `use: reference_only` vocabulary aligns with
#243's clean seed, whose validator, capability semantics and files remain owned
there. Its `locator` declarations require an explicit caller-side projection;
this tool does not silently reinterpret existing manifests.

Missing `reference_only`/`archive` paths produce informational findings. Present
ones are not opened, hashed, parsed or followed: `reference_only_not_read` is
explicitly **not** hash verification. Their pins are syntax-checked only. Unsafe
or unsupported pointers still fail portability, but their content never becomes
a required runtime input. No referenced code is executed, and no network URL is
fetched. All symlinks, including in-root or broken links, are rejected before
opening; this is deliberately stricter than merely rejecting outside-root links.

## Two synthetic reuse cases

1. `nested-case.json` → `nested/worker.json` → `shared/payload.json` checks
   source-relative nested dependencies and a pinned synthetic payload.
2. `reuse-case.json` → the same `shared/payload.json` checks direct reuse of the
   identical bytes alongside two missing informational archive/reference pointers.

Both use one implementation and one payload; no copied payload or archive is
needed. `negative-cases.json` holds 15 declarations with expected rejection
codes. The suite materializes them in temporary isolated roots and additionally
creates symlink/cycle/malformed/size-limit cases. It checks replay, relocation,
CLI exits, nonexecution, and unchanged fixture byte hashes/mtimes. All evidence
is synthetic; there is no production/provider or operational qualification.

## Acceptance limits

- Only explicitly declared top-level `references` are audited. Arbitrary nested
  `ref`, `$ref`, `$id`, `$dynamicRef`, URI anchors/fragments, JSON Pointers and
  schema semantics are not resolved. A successful result does not prove an
  arbitrary JSON Schema or component is valid or dependency-complete.
- POSIX absolute paths, Windows drive/UNC paths, backslashes, URI schemes,
  home expansion, percent escapes and query/fragment syntax are unsupported.
  Case sensitivity, Unicode normalization, Windows reserved filenames and
  filesystem-specific name limits are not cross-platform certified.
- Supply a static isolated directory. This is not an OS sandbox: concurrent
  hostile file replacement, hard-link provenance, mounts and adversarial resource
  exhaustion are outside the contract. Reads may update filesystem access times;
  byte content and modification times are preserved, not access times.
- Limits fail closed: 1 MiB per file, 256 visited files, 4096 declarations,
  dependency depth 32. The audit never writes its inputs or report files.
- A required reference can be marked `resolved` for bytes/hash while its document
  has a separate parsing/declaration error. Always inspect top-level `ok` and
  `findings`, not an individual edge status.
- Shared CI does not discover this nested suite. Hosted shared green alone is
  not evidence that the focused tests ran. Independent review and explicit hosted
  discovery belong to a later owner-approved gate; no shared CI/bridge edits are
  included in this scope. No merge, deployment, or operational acceptance.


## Explicit integration projections (B00 #245 continuation)

`project_references.py` translates two existing source shapes into this audit's
profile. It is an opt-in producer-side adapter; #230/#243 adoption is not assumed.
It does not fetch sources, validate their full models, or change their files.

- `map_sources(document, selected)` requires explicit distinct source keys.
  Each selected `sources[key]` must have matching `path`, lowercase SHA-256 and
  a full commit ID. Paths/hashes become required local references. Place the
  resulting entry JSON at the isolated bundle root. Unselected sources are not
  audited. Commit IDs are retained as provenance, not independently verified.
- `seed_references(document)` accepts `basket.clean_seed@1` reference-only
  locators as informational `projection.reference_notes`. They never enter the
  file-reference traversal, so external archive URLs cannot become prerequisites.
  `requires` remains `required_capabilities`, with `capability_evaluation` set to
  `not_performed`. An OK file audit is **not seed readiness**. Unknown/required
  reference uses reject instead of being silently weakened.

Both are also available as a CLI, writing JSON to stdout:

```sh
python -B orchestration/qualification/reference_portability/project_references.py --profile map --document /explicit/source/system.json --select schemas/component-blackbox.v1.json
python -B orchestration/qualification/reference_portability/project_references.py --profile seed --document /explicit/source/seed.json
```

The caller explicitly supplies source documents and stages selected local bytes;
this module never clones, copies, downloads or writes an input bundle. Feed the
returned JSON to the existing audit as a bundle-root entry. Projection failures
produce JSON error output and exit1; success exits0. Source locators are preserved
as metadata and may be private; review before sharing reports.

Current focused suite: **49 tests** (original37 plus12 projection tests), also
passing with only this subtree copied outside the repository. Historical
`evidence.json` remains unchanged. `projection-evidence.json` records actual
producer composition against pinned _MAP and clean-seed source documents:
one selected canonical schema resolves with its exact hash; both seed reference
URLs remain notes and are never fetched. No real provider/market data is used.
This closes the missing runnable format translation, not independent acceptance,
owner adoption, full-model coverage or hosted focused-suite discovery.
