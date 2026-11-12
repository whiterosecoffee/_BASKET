# B02-207 receiving assessment, 2026-11-12

## Disposition

Accepted for bounded read-only assessment under the owner's instruction to pick up #207. This is a continuation of work/207-local-refresh-quality-gate, not a replacement fetcher, QC implementation or data store. Remote branch was verified at b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95; no published refresh_qc implementation exists at that revision. An earlier unpublished implementation was not recoverable in the accessible checkout/artifacts. Do not infer that it never existed.

Existing FETCH entrypoints and actual configured legacy storage were read directly on the laptop. Private absolute paths and raw provider rows are deliberately omitted. No plan, network fetch, sanitizer, apply, canonical migration or schedule was run. Source files remain untouched. No claim of R1 compliance, production readiness or historical point-in-time authority.

## Exact dependencies

- Receiving handoff: https://github.com/whiterosecoffee/_BASKET/issues/207#issuecomment-6810093014
- Revision clarification: https://github.com/whiterosecoffee/_BASKET/issues/207#issuecomment-6810187418
- PR242 reference: d103a99486589aa4aee24d4fa978532f1b288ac1, orchestration/data_flow_objects/README.md.
- PR231 map: 1a9fdb7952676d026e92d001f88f62de67f103e0, _MAP/data_flow/projection.json.
- Neither dependency was imported. Both remain candidate/unmerged designs. _MAP's available_at means first external revision availability; reference captured_at is conservative local materialization. These meanings are incompatible without an explicit policy. Never rename one into the other.

## Existing boundary mapping

1. fetch_plan.py reads session scans and emits a plan. Even this planning command writes plan.json, so it was inspected rather than executed.
2. fetch_run.py calls Massive aggregates with adjusted=true and maps rows into staging/raw* per-ticker JSONL. It deduplicates by timestamp using last assignment and overwrites that staging filename. Completion markers are ticker/round scoped, not source/schema/transform generation identities.
3. verify_apply.py loads staged and stored rows, calls the existing sanitizer, compares overlap and optionally appends or rewrites the legacy store. Its command-line dry run writes a report, so it was not invoked during this read-only assessment.
4. ticker_jsonl_tool.py resolves MERGED_STORE to flat per-ticker files, not R1 one-session physical files. It rounds fractional volume/count to integers. The observed default root exists locally but is not approved here as a canonical R1 root.
5. Missing production boundaries: immutable capture generations, retained schema/transform/verifier bundle, supported historical reader dispatch, explicit expected-head/supersession and availability policy, crash durability and canonical promotion.

## Executed aggregate-only evidence

A streaming Python read parsed numbers with Decimal, hashed original bytes and inspected exchange-local dates with America/New_York. No rows were printed or written.

- Legacy NVDA: 495319 rows, 523 dates, 2024-09-09 through 2026-10-08; 256054 minute bars, 239264 minute moments, 1 daily bar. 102469302 bytes. SHA256 51ed6a7b5373d55169fbbbba980549881ce518f67582a772112e04183ba9dd3c.
- Existing raw_r3 NVDA staging: 5673 minute bars over 6 dates, 2026-10-01 through 2026-10-08; 5670 fractional-volume rows. 1295242 bytes. SHA256 656a6bad72cff3e6483663a7b117b5e708de5e80c700a12448af753ad2b40131.
- Both parsed without invalid JSON; size and modification time were unchanged during the hashing pass.
- Selected existing date 2026-10-08: 941 rows in each source, no duplicate timestamp, no failures in the bounded class/grain/OHLC ordering/nonnegative-volume/minute-alignment checks. All 941 overlapping OHLC records match exactly; 940 volume values differ. This is consistent with the inspected rounding path, not proof of provider correctness or an independently authenticated capture.
- SHA256 of selected original lines in original order: legacy 03b9530d30d187988e6bac8e8c5f46c710902ddcaa28f80f663e793d14a049a9; staging b14e2c7b3f4111586c4555584ddef099b8bbc66f0f15d0ac15cd17cbd207105b.
- These are in-memory date selections, NOT newly created or validated physical daily partitions. Coverage is observed, not exchange-calendar-certified completeness.

## Fail-closed disposition

Canonical eligibility: BLOCKED. Every inspected row lacks explicit adjusted, available_at, ingested_at, id, supersedes, currency, venue, entitlement and schema_version fields. Existing code's adjusted=true request is intent, not proof of historical source basis or row-linked request provenance. Ledger records may supply additional evidence but have not yet been reconciled to these exact source hashes. File timestamps cannot repair missing historical first availability.

Additional code-review concerns: apply reads stored bytes before obtaining its lock, so the lock does not cover the entire read/validate/write transaction; append is not crash-atomic; timestamp dictionaries can erase duplicate conflicts before validation. These are static findings, not exploit tests or changes to the legacy tools.

## Next bounded owner action

Reconcile the existing raw_r3 capture against its plan, done marker and ledger, bind those artifacts and current script hashes into a private read-only receipt, and explicitly preserve unknown historical provenance. Then qualify the adapter and immutable-generation/read contract against the nested seed gates before any implementation or canonical write. Recover prior unpublished QC code if it becomes accessible; do not duplicate it. Any source repair, canonical-root activation, merge, publication or schedule stays separately gated. Local note-only commit is not a published receiving disposition.
