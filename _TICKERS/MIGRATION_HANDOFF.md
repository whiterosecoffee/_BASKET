# _TICKERS canonical migration and CRUD routing — orchestrator handoff

Status: **DESIGN / NOT EXECUTED**. Origin #146 / draft PR #147. The active canonical historical market-data paths remain `tickers/<ticker>/**` until migration is independently validated and a routing switch is approved. Scope markers in `_TICKERS/` are not a live data store.

## Goal and design constraints

Make `_TICKERS/<instrument_id>/` the discoverable logical home for every tracked instrument, able to hold research, source documents and evaluation outputs alongside structured financial data. Keep identities and taxonomies separate from executable engines; no duplicate ticker truth. Different instrument classes require differentiated schemas: equity/ADR/OTC, funds/ETPs, indices, FX and futures must not share invented earnings or OHLCV. Distinguish user watchlist membership from ownership, company/underlying ID from trading symbol, and reported data from scenario inference.

Target single-folder structure, created on demand rather than with empty Git directories:

```
_TICKERS/<id>/
  scope.json                 # instrument type, aliases, basket roles, listing/venue, watch status
  entity.json                # canonical fundamental profile, under company-research ownership
  observations/              # append-only observation journals; B02 owns market/FX
  history/                   # immutable bars and reconciled revisions
  earnings/                  # filings, transcripts, financial periods, source links; B03 primary events
  evaluations/               # versioned B04/B06/B07 analysis outputs with reproducibility manifest
  relationships/             # B05 canonical ownership/contract edges
  sources/                   # source manifests/hashes/availability, no unsourced copying
  README.md                  # local index and provenance
```

Do not eagerly create nonapplicable directories (e.g., index earnings). Keep generated artifacts and source binaries bounded; external object storage plus checksum manifests may be preferable to large Git binaries.

## Migration requirements

1. B00 inventory ALL existing `tickers/**`, related `research/<ticker>/**`, source-referenced JSONL, `runtime/**`, `fx/**`, event/relationship records, and active PR branches. Record current Git SHA, file paths, SHA-256 hashes, line counts, schemas, timestamps and provenance. Compare with the 291-scope manifest. Do not assume all tracked instruments have 200-session history or that every legacy record belongs to this basket.
2. B00 approves a versioned security-master mapping: stable entity ID, tradable instrument ID, exchange/MIC, symbol history, alias and ADR/underlying mapping, fund look-through and class; distinguish folder-safe aliases from exact provider symbols. Resolve ticker reuse and special identifiers such as .INX, USD/JPY, 688825.SS, BZ=F and TCS. Avoid forced renames without evidence.
3. B02 proposes the exact migration of `history.jsonl`, `history.meta.json`, `intraday/**`, `live/**`, and other market journals with immutable event IDs, original sequence and timestamp fields preserved. No backfill guesses. B03 owns canonical events/earnings ledgers, B05 canonical relationships, ticker researchers their entity records, B04/B06 evaluation output contracts, B01 CI, B08 deployed service path settings.
4. Introduce a single configurable path resolver used by CLI, ingestion/replay, reader API/MCP, evaluator, orchestrator and tests. Contract: `resolve(instrument_id, data_kind, access_mode, as_of) -> physical_path, schema, owner, source_manifest, migration_state`. Writes are single-target and fail closed; do not dual-write. Reads are new-path-first ONLY after a proven cutover; pre-cutover reads retain old paths. No silent fallback from a corrupt or stale new path.
5. Stage copy-on-write migration on distinct domain-owned branches, preserving exact original bytes for source records, link source/destination SHA-256 and counts, then compare normalized point-in-time replays, corrections, FX, event edges and evaluation manifests. Require idempotent re-run and rollback. Stop on any mismatch.
6. Publish backwards-compatible read-only pointer manifests `tickers/<symbol>/LOCATION.json` **only after** successful cutover, with target relative path, migration ID, source/target hashes, schema and effective commit. Keep legacy paths available during deprecation; remove or replace legacy files only after every active consumer is verified and authorized. A symlink alone is insufficient for GitHub API/web/Windows consumers.
7. B00 updates `AGENTS.md`, `orchestration/sparks.json`, architectural contracts and top-level developer instructions only after approving file-ownership transitions. B02/B03/B05/B04/B06/B08 adapt their own code/readers within assigned write paths. B01 runs strict schema, path-resolution, replay and compatibility tests on exact PR head and main after authorized integration.
8. Define earnings/evaluation metadata: source class, effective date, publication/available/ingested timestamp, financial period, original currency and date-matched USD/FX basis; engine version, code commit, inputs, as-of, TTD/expiry, uncertainties, scenario assumptions, falsifiers. Earnings reports are source/evidence records; evaluations are derived output, never overwriting reports.

## Acceptance

- 291 scope symbols deduplicated; aliases and instruments resolved or explicitly unresolved; no mistaken equity assumptions for fund/index/FX/futures.
- Every legacy source file accounted for (preserved, migrated, intentionally excluded with reason), cryptographic hashes and JSONL counts reconciled; no data loss or accidental deduplication of valid corrections.
- CRUD and replay work through a single tested resolver; zero writes to legacy destinations after cutover; all top-level entry points use new resolution; no ambiguous path imports.
- Existing consumers retain tested read compatibility for an explicit deprecation window; invalid/stale/unauthorized data fail closed.
- Earnings, filings, research and model evaluations are ticker-addressable without making duplicated canonical source records.
- CI is independently verified on PR exact head; no claim of persistent service/live data without entitlement and host. No migration, merge, release or deletion without approved dependencies and explicit authorization.

## Domain handoff routing

B00 owns security master, path contract and orchestration. B02 owns JSONL/FX/TTD and migrations of market files. B03 owns events and earnings-source ledgers; B05 owns relationship records; company sparks own individual entity profiles; B04/B06/B07 own derived evaluators and contracts; B08 owns service path routing; B01 owns cross-domain strict CI.

**Ready-to-paste receiver prompt:** Inspect #146, draft PR #147, AGENTS.md, sparks.json, version manifests, active open PR file changes and the current `tickers/` legacy data tree. Coordinate a transactional migration to `_TICKERS/` using stable identity resolution, SHA-256 source/destination manifests, replay equality and a common CRUD path resolver. Assign exclusive subprojects to B02/B03/B05 and company/evaluation owners, add backwards-compatible read-only pointers only after cutover, update all orchestration and top-level consumers after approval, and prove independent B01 validation on the exact commit. Do not touch another domain's paths, claim a migration prematurely, delete old data or merge without explicit user authorization.
