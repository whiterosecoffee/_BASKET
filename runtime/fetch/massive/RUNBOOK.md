# _FetchMassiveData — runbook skeleton

Status: **skeleton, issue #151.** No code, no registered worker, no live feed. See `../ARCHITECTURE.md` for the fixed/option split and measured evidence.

## Fixed procedure (do not vary)
1. Read the manifest watermark; list missing *settled* sessions (dry run by default). Weekdays only; a holiday returns 0 results and is recorded `no_bars`.
2. For each session: one call per ticker-day, `adjusted=false`, `sort=asc`, `limit=50000`, follow `next_url`. Key only from `MASSIVE_API_KEY`.
3. Sanitize fail-closed (rules in ARCHITECTURE.md). Record dropped counts by reason and `vw` flags as per-block counts.
4. Stage the block as final-format JSONL in `runtime/fetch/intake/<T>/`. Never store CSV.
5. Compute `sha256`; append a manifest record with `fetched_at`. A differing re-pull is a `conflict` and a new revision.
6. Continuity check against a refetch of the prior stored close; mismatch = `hold`, write nothing.
7. Stress-test before promotion: hash replay, two independent pulls identical, idempotent re-stage, manifest consistency, missing-minute report.
8. Promotion is a separate draft PR, only when the ticker home passes `tests/validate_stores.py`. Never merge.

## Runtime choices (record the choice and criteria in the run record)
See the option table in ARCHITECTURE.md. Do not invent new options silently.

## Unproven prerequisite
Connector output must reach the stager **without a model retyping rows** (tool-saved file or direct REST with a key). Until that route is demonstrated by a test, do not describe this worker as working.
