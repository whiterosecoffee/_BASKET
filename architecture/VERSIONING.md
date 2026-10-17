# _BASKET — Project, Contract, Data and Model Versioning Policy

Policy owner: spark B00. This is the source-of-truth RELEASE POLICY for GitHub work in `whiterosecoffee/_BASKET`.

## 1. Version layers are independent

| Layer | Authority | Version example | Why |
|---|---|---|---|
| Core project | `architecture/basket.architecture.json`, `CHANGELOG.md`, approved immutable Git tag | 0.4.1 declared; 0.5.0 planned | Release of an integrated capability with evidence |
| Orchestration | `orchestration/sparks.json` and complete Project Instructions | 1.3.0 candidate | Spark catalog can evolve without shipping a new market engine |
| Data contracts | `schemas/<contract>.vN.json` and schema identifiers inside records | relationships@1 | Append-only historical records need stable interpretation |
| Data observations | Source record ID, revision, timestamp, adjustment and dataset digest | `record_id`, `supersedes`, `snapshot_sha256` | Daily/minute records do not bump product version |
| Analytical engine | Engine-specific semantic version plus commit/config hash | `traversal@0.x` (illustrative only) | Calculation logic changes require exact reproducibility |
| Evaluation/report | Release/commit, model + data snapshot, source TTD and as-of | per report | Historical outputs must be replayable |

**Do not derive core project version automatically from schema number, chat count, date, number of commits, JSONL rows or a model-generated narrative.** `architecture/version-manifest.json` declares baseline, target, release gates and version relationships. The version manifest is descriptive, not a git tag or deploy action.

## 2. Semantic version rules

Core version `MAJOR.MINOR.PATCH[-prerelease][+metadata]`:
- During **0.x** development, bump MINOR for new cross-domain capabilities, new release foundations, or intentional breaking experimental changes with explicit migrations. Bump PATCH for backward-compatible corrections and documentation to an existing published release.
- At and after **1.0.0**, MAJOR means incompatible public interfaces, MINOR backward-compatible new functionality, PATCH bug fix/clarification.
- `-rc.N` is a release candidate, not GA; merely opening a PR is not a release candidate until validation is ready.
- The Git tag `vX.Y.Z` may be created only against an approved main commit when evidence passes and the user explicitly authorizes the release. The tag is the immutable release identity.
- A changelog `Unreleased` heading records proposed work without asserting public release completion.

Catalog changes use separate SemVer: patch for prompt edits/corrections; minor for new spark, ownership reallocation, launch policy extension or release metadata; major for incompatible catalog parser/identity changes or a breaking bootstrap contract.

## 3. Contract versioning and migrations

Schemas have independent identifiers and immutable interpretation of past records. Add optional backward-compatible fields only with review of validation, consumer support and existing records; incompatible changes create a new schema major. Do not silently rewrite or normalize historical data to new meanings. Document migrations as `old_schema -> new_schema` with source audit, fallback/error policy, compatibility and test fixtures. Keep schema validation strict: valid source data must be preserved, but domain-specific overflow context should be placed in its proper versioned context rather than disabling `additionalProperties`.

Maintain distinct `effective_at` (when an economic event takes effect), `observed_at`, `available_at` (first knowable by the market), `ingested_at`, reporting `period_end`, and `expires_at`/TTD. Date precision must not be misrepresented as intraday precision.

## 4. Data and computation snapshots

Each data row should provide: `entity_id`, `kind`, `schema`, `interval_start` or `observed_at`, `available_at`, `ingested_at`, source, currency, provider adjustment policy, unique immutable record/revision ID, and `supersedes` for corrections. The exact existing JSONL representation may be positional: its schema and meta-file provide the field map.

Create a **snapshot manifest** (future B02 implementation) that lists source, date/time interval, record count, logical feed versions, content hash for each shard, original currency/FX basis and earliest/latest available dates. The dataset's stable identifier is a SHA-256 digest of a deterministic, canonicalized manifest. Never hash inherently mutable "current" state without an as-of cutoff. Data snapshots live in durable storage, and optional lightweight manifests/checkpoints may be committed to Git. Avoid committing high-frequency live bars to Git as a continuous writer.

Every derived value inherits the earliest expiration among its own calculation TTL and all material dependencies; stale and conflicted inputs invalidate current-use computations but stay available for point-in-time historical replay.

## 5. Model and report version identity

Each model output must eventually include:
```json
{
  "engine_id": "example-engine",
  "engine_version": "0.1.0",
  "source_commit": "<git_sha>",
  "config_digest": "<sha256>",
  "inputs_snapshot_digest": "<sha256>",
  "as_of": "<ISO8601_UTC>",
  "generated_at": "<ISO8601_UTC>",
  "data_state": "historical|fresh|stale|unavailable|provisional",
  "classification": "observed|derived|scenario|forecast",
  "reporting_currency": "USD"
}
```
This is a **future output contract example**, not proof that existing engines already emit it. B06/B04/B07 must adopt their own implementation through linked dependency issues. A scenario's assumptions, falsifiers and provenance cannot be removed when it is saved as a versioned artifact. Comparisons between model versions require a consistent data vintage and backtest window.

## 6. Release procedure and gates

1. B00 proposes `next_candidate` and feature scope without falsely updating `declared_architecture_version`.
2. Each worker develops on a new, unique issue/branch, passes local tests, and opens a PR; cross-domain changes go through handoff issues.
3. Release integration reviews all dependent PRs against latest `main`, validates schema and source compatibility, checks independent data/test workflows, and documents evidence.
4. `v0.5.0` candidate **Orchestrated Foundation** has gates R0–R4 in `architecture/version-manifest.json`: canonical instructions merged; strict SFTBY relationship compliance without lost evidence; CI green on release commit; metadata/documentation validated; explicit user authorization.
5. After gates pass and user approves, update the architecture's declared version and changelog **on a B00-owned release PR**, merge with authorization, then create `v0.5.0` tag against the approved main commit. Do not mark released before the tag exists.
6. Create a release note containing Git SHA, immutable data snapshot IDs or explicit absence, key code+schema versions, tests/runs, known failures, disabled live feeds and non-implemented capabilities. Never call a release "production" simply because the documentation says so.
7. Next targets can be `v0.6.0` reliable ingestion/FX/TTD, `v0.7.0` deterministic joined three-holdings pilot, and `1.0.0` only after statistically calibrated, integrated, operationally reliable outputs (tentative roadmap, not release commitments).

## 7. Current state and known blockers

- `architecture/basket.architecture.json` and the current changelog declare **0.4.1**, not 0.5.0.
- `orchestration/sparks.json` is separately versioned as **1.3.0 candidate** on this branch.
- No GitHub published release objects were returned when checked on 2026-10-16; tags were not independently verified.
- `tests/validate_stores.py` is failing on the SFTBY relationships record's non-schema top-level fields. B05 #4 owns lossless normalization; B01 #5 owns strict CI verification. B00 #3 owns optional larger schema evolution.
- PR #2 and these documents are on the isolated orchestration branch until authorized merge; **not** present on main at publication time.

## 8. Governance

B00 owns this version policy and version manifest. B01 can add version validation to shared CI via handoff; B02 owns snapshot creation/TTD runtime; B04/B06/B07 own concrete engine metadata within their respective domains. Never modify other owners' code or data to make versioning look integrated. Prefer append-only manifest and provenance interfaces for cross-domain exchange.
