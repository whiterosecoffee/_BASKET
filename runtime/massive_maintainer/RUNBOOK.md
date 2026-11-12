# Massive local maintainer

Owner: `work/local-20261112-massive-maintainer`, B02 source-specific implementation.
Base: main `74d913e8913d630d85451344689e093aeea07efc`.
Issue publication was denied by automatic approval review; this local branch has no issue number.
No scheduler, deployment, merge, or modification of the #207 checkout is included.

## Resume on this workstation

Run from this isolated checkout, with Python 3.12 and `tzdata` available:

```powershell
python -m runtime.massive_maintainer.maintain --root "$env:BASKET_DATA_ROOT" --legacy "$env:BASKET_LEGACY_ROOT" --key-file "$env:MASSIVE_KEY_FILE" --audit-batch 2 --history-batch 1
```

The external scheduled owner resumes this command on this branch. This program does
not create or install any scheduler. Default dates are yesterday and today in New
York; explicit `--dates YYYY-MM-DD,YYYY-MM-DD` and `--ticker` bound a manual pull.
The default pass inventories all legacy filenames and boundary timestamps, audits
two changed/unaudited files, services at most two pending consumer requests, refreshes
the two NVDA dates, and confirms one previously unconfirmed audited history date.
The history cursor derives from committed local partition manifests, so interrupted
runs resume without skipping unpublished data. Provider failures stop the fetch batch.
Empty responses remain blocked/unclassified, not market-closed conclusions. A blocked
history date needs explicit investigation before proceeding; do not synthesize bars.

## Data and publication contract

Private data root contains `inventory.json`, `audits/`, `archive/`, `quarantine/`,
`raw/`, `generations/`, `receipts/`, `index.json`, `runs/`, and `progress.json`.
No operational data, machine manifest or credential belongs in git.
Each immutable generation has `tickers/<T>/intraday/<exchange-date>.1m.jsonl`.
Rows are one instrument/date/grain, USD US stocks only after provider reference
confirmation, split adjusted, and decimal numeric values are strings. Reference and
query bytes are archived before normalization. `available_at` remains unknown.
Ingestion timestamps, raw hashes, endpoints and revision lineage live in immutable
receipts and the manifest. `supersedes` preserves prior generations; identical pulls
reuse the same canonical bytes/hash. Atomic manifest replacement is the visibility
boundary after staged file readback. Reader checksums detect corruption.

Legacy files are read-only. Before validation/migration, copy their exact bytes and
verify SHA-256. An explicit audit-only `vol` to `v` mapping accommodates the old
schema without mutating evidence. Invalid rows are quarantined by archive line and
hash. No legacy rows are promoted merely because they parse. The first audit's schema
mapping failure is retained in the dated run history; audit schema 2 corrects it.
Raw archives and old generations must not be deleted by scheduled runs.

`WRITER.lock` uses exclusive creation on the one local machine. It is not a distributed
OneDrive lock. After a crash, inspect its PID and confirm no owner process is running
before manually removing it. `STOP` in the data root prevents new provider requests
and new audit batches; an in-progress request or audit finishes safely. Retain receipts.

## Consumer entry point

Discovery pointer: `<data-root>/_MAP/massive-local.json`. Consumers load that pointer
and use `runtime.massive_maintainer.maintain.resolve(pointer, ticker, date,
required_through, max_age_seconds=1200)`. For current analysis supply the actual
required observation timestamp in epoch milliseconds. Omitting it is explicitly
historical-only. Missing/stale data produces a content-addressed refresh request and
status. It must not cause a consumer-owned Massive call or a stale-data fallback.
Requests are fulfilled only when the requested timestamp is reached. An absent bar
may need investigation rather than unlimited fetching.

```powershell
python -m runtime.massive_maintainer.acceptance --pointer "$env:BASKET_DATA_POINTER" --day 2026-11-11
python -m unittest runtime.massive_maintainer.test_maintain -v
```

The acceptance example denies urllib network access and reads/checks real local
NVDA data. This is a consumer integration example, not proof that every existing
analysis worker has been changed. Their routing adoption and the central `_MAP`
controller contract must be independently verified. Existing main is not modified.

## Coverage and limitations

Full audit is incremental; inventory boundary timestamps are not verified min/max.
Each confirmed date means all returned bars in the successful paginated Massive query
were persisted and validated. It does not claim every expected minute exists.
Gaps remain `vendor_absence_unclassified`; calendar closure, no eligible trade,
vendor absence, and confirmed missing observations need separate source evidence.
No market calendar or trade-entitlement claim is fabricated. Entire missing dates
and the gap from the legacy archive end to current dates require a separate review
queue; this first batch resumes audited session dates, not that entire date interval.
All other source dates, identities, adjustment bases, and securities remain unverified.
The source-confirmed adjusted history is as fetched, not point-in-time split history.
One-second request pacing, bounded retries, host checks, and private Bearer credentials
apply. Current market entitlement is only demonstrated by the actual successful
requests; no streaming or trade/quote entitlement is implied.

Provider contract checked: https://massive.com/docs/rest/stocks/aggregates/custom-bars
and https://massive.com/knowledge-base/article/why-are-there-missing-aggregates-in-massives-data .

## Portable continuation checkpoint

Owner: existing `_FETCH` / B02 lane. Exclusive implementation scope:
`runtime/massive_maintainer/**`. This is a development checkpoint, not an
operational service or integrated main release. No issue or PR was created.

Before using a command above, configure the explicit machine-local variables:
`BASKET_DATA_ROOT`, `BASKET_LEGACY_ROOT`, `MASSIVE_KEY_FILE`, and
`BASKET_DATA_POINTER`. They must identify existing private locations; no credentials,
absolute personal paths, generated datasets or machine manifests are supplied here.
The maintainer command performs provider requests, including pending requests; do
not run it while the current local-only placement/verification restriction applies.
No source refresh is authorized until the specific missing range is established.

Current local workstream evidence: 356 existing archive files were staged with
matching sizes and originals preserved. Sixty were hash-checked and record-scanned;
NVDA was separately hash-matched. The other 295 hashes and detailed quality checks
remain outstanding. This is copying, not a completed relocation or qualification.
These operational receipts live outside Git and must be rechecked on the owning
workstation; pulling this branch does not provide market data.

The accepted target is a top-level `_TICKERS` component. The `_MAP` owner must
reconcile discovery and folder-local resolver contracts. Do not create another
corpus, silently promote the staging location, overwrite smaller existing histories,
or remove originals merely because sizes match. The previous relocation handoff
review was blocked; this checkpoint does not resolve or bypass that review.

Dependencies: B00/_MAP for the final location and shared contracts, B01 for independent
acceptance, and the existing NVDA analyst for consumer verification. Reuse prior
fetch, resolver, daily-partition and journal work rather than spawning competing
owners. Consumer filename expectations and source/coverage manifests are not yet
reconciled. No persistent refresh runner or scheduling acceptance is demonstrated.

Validation for this checkpoint: `python -B -m unittest
runtime.massive_maintainer.test_maintain -v` ran 11 tests successfully. This is local
unit validation only; it does not prove restart after a process crash, all-basket
correctness, live provider entitlement, consumer adoption or CI approval.

Next action: the existing `_FETCH` owner resumes local verification and coordinates
the `_TICKERS` cutover contract with `_MAP`, preserving single-writer ownership and
the no-repull constraint. A receiving worker must verify branch/HEAD, dirty state,
local data availability and prior writer exit before taking ownership. Pulling the
branch alone does not transfer writer ownership.
