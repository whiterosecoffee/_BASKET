# NVDA frozen-evidence pilot — #148 / Q04

One function: resolve a **dated, source-backed NVDA evidence report** from an approved local snapshot. This extends PR #140's existing observation reader. It is not ingestion, valuation, a scheduler, a queue, or a 291-symbol migration.

## Ownership and physical/logical boundary

B00 owns this module under #148, branch `work/148-nvda-resolver-pilot`. B01 separately authored `tests/integration/test_nvda_pilot_acceptance.py` and `.github/workflows/nvda-pilot.yml`. All 46 open PR changed-file inventories were inspected before allocation; no target-path collision was found. Main base: `25ae331f2774250528fc939e3e7795583f8808a3`.

The approved pilot data root is `/workspace/_BASKET-local`; the logical home is **`_TICKERS/NVDA`**. All pilot snapshot writes use `stage` then explicit `activate`; readers use `resolve`/`report`. No current runtime or other worker branch is modified. The legacy source archive remains unchanged and is not an active second writer. This is NVDA-only snapshot activation, not global migration of the legacy runtime or the scaffold in PR #147.

A caller chooses its actual durable root explicitly. This execution workspace is not the user's workstation or a permanent hosted service. The private delivery archive contains data, sources and a minimal executable copy for restoration elsewhere. Provider rows remain outside the public repository.

## Public boundary

```python
from orchestration.nvda_pilot.store import Pilot, freeze, canonical
manifest = freeze(source_root, frozen_at)  # explicit source vintage
pilot = Pilot(local_root)
pilot.stage(source_root, manifest)        # verify all hashes; copy only
pilot.activate(manifest['manifest_id'])   # first activation, expected_current=None
route = pilot.resolve('NVDA', 'observations', 'read', as_of)
report = pilot.report(as_of)
```

- `freeze(source_root, frozen_at)` returns `basket.nvda_source_package@1`: NVDA identity, frozen time, sorted file inventory with size/SHA-256/role/availability, and canonical content-addressed manifest ID. No source file is edited.
- `stage(source_root, manifest)` verifies bytes and semantic identity before and after copying. A retry is `unchanged`; a mismatched/corrupt source is rejected. A partial copy is not activated.
- `activate(manifest_id, expected_current=None)` verifies the staged package and changes only one atomic pointer. Repeated identical activation is safe; changed unrelated heads are rejected. No pre-existing source is deleted.
- `rollback(expected_current)` verifies the prior version before switching; corrupt prior data or failed pointer writes leave the current version intact.
- `resolve(instrument_id, data_kind, access_mode, as_of)` accepts NVDA, `observations` or `source_reports`, and `read`. It returns logical path, version, physical source path, as-of and required-reader semantics. Report filenames are usable relative to the returned reports directory. Immutable snapshots reject arbitrary writes: a writer must stage a new version.
- `report(as_of)` returns `basket.nvda_evidence_report@1`: source manifest and implementation fingerprints, dated market coverage/quality counters, selected financial facts, available source reports, source reconciliation warnings and explicit limitations. No invocation time or absolute workspace path enters canonical report content.
- Library failures raise `PilotError(code,message)`; CLI failures emit structured JSON with nonzero exit status. No silent legacy fallback, empty-success source failure, fabricated values or stale-lock takeover.

The source package contains `observations.jsonl`, `reports/manifest.jsonl` and indexed report documents. Additional evidence files are hashed too. The original journal's source fingerprints must match packaged `source/massive.csv` when present. Report index entries must identify NVDA, give HTTPS provenance, actual retrieval availability and exact report hashes. Unindexed supporting files are not silently promoted to source reports.

## Point-in-time semantics

Observation selection reuses `TickerStore.read(as_of)` and its immutable revision chain. Both first availability **and** local ingestion must precede the cutoff. Report documents use their indexed `retrieved_at`, not publication dates as a proxy for known availability. Supporting reconciliation warnings use their explicit verification time, or conservatively the frozen package time if unspecified. Unknown precision stays unknown.

The resolver provides an as-of descriptor and the required reader; it does not claim that opening the entire physical JSONL file directly creates an as-of view. Consumers must use the declared reader or this report API. The immutable manifest is rechecked on reads and activation. Filesystem owners can still modify files out of band; such corruption is detected. OS/power-loss durability and network-filesystem operation are not qualified.

## Actual frozen source and result

Selected original November 1 vintage (not the later differing recapture):
- Original raw CSV SHA-256: `78310f336a11a5561ac5fc39026fa3a37662a9ced79e5930e4e9e2847dc78898`.
- Journal file SHA-256: `894fd47a7fdb0d1b7bc2f11114442ac7dab2c96c0395e78e0975874e0ecc3e3a`.
- Frozen package ID: `1c27bf3a093dffcd971797a8a6fc7c6367e7b9976ada610078baa126b1df54d3`; 12 source files.
- Report cutoff: `2026-11-04T02:56:11Z`.
- Canonical report SHA-256 (canonical JSON, excluding CLI newline): `b34a1522e35cfd58373d82f0aac1ca8fbaa425a0dc12bf4ccfc25be7896da7c9`.
- 4,690 market observations, 7 financial facts and 6 earnings-release documents. October 26–30 counts: 934/914/946/943/953, with 390 ET regular-clock minutes per date.
- Earlier replay at `2026-11-01T01:52:03Z`: same eligible market capture, 1 financial fact, 0 release documents and 0 later supporting warnings. Earlier than ingestion: no data, not a successful source scan.

**Qualification is integrity/replay only.** 4,664 bars have fractional volume; 864 provider VWAP values fall outside their bar's OHLC range. These values are preserved and flagged. No volume-based economic validity, signed flow, independent calendar completeness, SEC reconciliation, predictive accuracy or current valuation is certified. The $1 million difference between FY2027 quarterly revenue sum and the reported half-year figure is retained as an unresolved source warning.

The later November 4 recovery mentioned on #148 has a different raw hash and is not mixed into this package or backdated. It remains a separate vintage.

## Executed commands

```sh
python -m orchestration.nvda_pilot.cli --root /workspace/_BASKET-local freeze --source /workspace/nvda-frozen-input --frozen-at 2026-11-04T02:56:11Z --output /workspace/nvda-frozen-manifest.json
python -m orchestration.nvda_pilot.cli --root /workspace/_BASKET-local stage --source /workspace/nvda-frozen-input --manifest /workspace/nvda-frozen-manifest.json
python -m orchestration.nvda_pilot.cli --root /workspace/_BASKET-local activate --manifest-id 1c27bf3a093dffcd971797a8a6fc7c6367e7b9976ada610078baa126b1df54d3
python -m orchestration.nvda_pilot.cli --root /workspace/_BASKET-local report --as-of 2026-11-04T02:56:11Z
python -m orchestration.nvda_pilot.cli --root /workspace/_BASKET-local report --as-of 2026-11-01T01:52:03Z
python -m unittest discover -s orchestration/tests -p 'test_nvda_pilot.py' -v
python -m unittest discover -s tests/integration -p 'test_nvda_pilot_acceptance.py' -v
```

B01 independently exercised duplicate stage/activation, corrupt source/version/index/pointer, stale CAS and locks, partial copy, failed pointer write, rollback, unsafe paths and CLI symlink output, temporal document/warning cuts and cold restore. Initial defects and successful reruns are retained in `evidence/`. CI requires nonempty suites, no skipped success and exact PR/main checkout. Local acceptance does not substitute for published-head and main CI; see #148 for final run identities.

## Reuse and next boundary

Reused `runtime/ticker_data.py`, `runtime/observations.py`, existing history/schema semantics, the original reports/manifests, GitHub Issues and standard Actions. No new dependency, provider fetch, paid model backend or second worker implementation was needed. Separate B01 review is verification, not a competing resolver.

Q04 acceptance covers this usable NVDA-only snapshot/report and tested recovery. Q05 financial/cash-flow reconciliation can consume these source documents next; volume-dependent B06 recognition remains gated by B02 quality policy. The other 290 scaffold instruments, global migration, additional providers and deployment remain separate work.
