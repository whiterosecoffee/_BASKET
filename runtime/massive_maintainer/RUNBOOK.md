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

This entrypoint does not install or prove a scheduler. Default yesterday/today
and history candidates are plans only: acquisition requires an explicit, validated
`--admission-file`. Without one the run records blocked outcomes. Existing legacy
ticker history and indexed dates remain blocked by the absent-day gate. The pass
may inventory/audit local inputs, so do not invoke it against production merely to
test admission. Offline tests use disposable stores. Provider failures stop the
fetch batch; deferred retry receipts persist their next eligible time. Empty or
missing intervals are not inferred to be market closures or no-trade periods.

See AUTHORITY.md and OWNER.json for generic `_FETCH`, provider adapter and ticker
consumer roles. This module is the existing Massive lane, not a new generic engine.

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
required_through, max_age_seconds=1200, coverage=...)`. Omitting required_through
is historical returned-bar access only. Current use requires an explicit coverage
object: start_t/end_t (inclusive minute timestamps, end_t=required_through), session
PRE/RTH/AH, completion all_minutes_present, timezone America/New_York and adjustment
split_adjusted. Unknown, sparse or delayed input cannot qualify current. The last
requested minute must have completed and remain within the freshness limit; a
recent refetch cannot refresh the observation's age. Request fulfilment uses the
same eligibility gate. Missing evidence returns refresh_required without granting
acquisition permission. No no-trade minutes or closures are invented.

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

## Resolver integrity repair

Independent review found that checksum verification alone did not bind the bytes to
the requested ticker/date or index schema/count. On the original checkpoint, four
new offline regressions failed: ticker relabel, exchange-date relabel, incompatible
index schema, and a declared one-row count for a 960-row fixture.

The resolver now validates the index schema/source, query identity/date/grain and
adjustment, then reads the partition once and validates that checksum-verified byte
snapshot. Every row must match the canonical schema and requested ticker/date;
count, chronological uniqueness and first/last bounds must match the manifest.
The tested partition-integrity failures raise ValueError before a current/historical
qualification or freshness request; malformed pointer roots have the error-type
limitation recorded below. Additional tests cover checksum-valid row metadata corruption,
manifest bounds, boolean row counts and query mismatch.

After repair, `python -B -m unittest runtime.massive_maintainer.test_maintain -v`
passed all 17 tests. The earlier four failures are intentional reproduction evidence,
not hidden failed attempts. Tests use temporary synthetic data; no vendor requests
or production-data writes occurred. This supersedes the 11-test checkpoint count.
Independent partition controls were subsequently retested as recorded below. Hash/semantic consistency
is not cryptographic proof of provider provenance, complete coverage, consumer
adoption or freshness. Returned paths still require consumers to pin/check revisions
when reading later; this change does not provide a filesystem transaction spanning
a consumer's subsequent open.

### Pointer contract follow-up

Independent retesting accepted the partition repair but found that an incompatible
pointer schema was still accepted. The new regression failed on eafc097 before the
fix. The resolver now requires a dictionary pointer with schema
`basket.massive.minute@1` before accessing its root or index. Regression controls
reject incompatible, omitted and malformed pointer schemas and retain a valid
pointer success case. All 18 offline tests pass after repair; no production data
or vendor requests were involved. Independent retesting of this follow-up is recorded below. Pointer schema validation does not authenticate who supplied the pointer
or establish dataset completeness or current freshness.


### Independent artifact acceptance receipt

The parent supplied an independent retest for code revision
`6c24e70117996bfff4bc0917e1fb3e991f10d8c7`, matching maintain.py SHA-256
`f27d9271366d73d021dc97a0f139680e58f5a618e8255cf2050e966da41292f8`.
The owner reread the clean checkout and matched that source hash before recording
this receipt. This is reported reviewer evidence, not a new owner-executed retest.
The reviewer timestamp was not provided.

Accepted bounded controls:
- Valid NVDA partition resolves successfully.
- Incompatible or missing pointer schema, and missing/list/string pointer, reject.
- Wrong ticker, exchange date, index schema and row count remain rejected.
- Missing or malformed pointer root also fails closed, but currently raises
  KeyError/TypeError rather than a stable contract error. This remains unresolved;
  do not promise a uniform ValueError interface for all invalid configurations.

The reviewer reported no writes or network. Remote provenance, the complete test
suite, current data qualification and consumer integration were outside this
independent recheck. The prior owner-run 18-test suite is a separate evidence item.
This receipt accepts only the listed artifact controls; it does not mark the
workstream integrated, data fresh, migration approved, or refresh operational.
No implementation changed while reconciling this receipt. No new test run is claimed.

Next independent acceptance remains the actual NVDA consumer and qualified input
contract once its existing data/discovery dependencies are met. Preserve the
no-repull restriction and unresolved migration handoff; do not launch a second
writer or infer permission to move data from this artifact review.

### Data-root contract repair (maintenance 2026-11-12T23:55:10Z)

At source head `10a0353b5aa9481d5854b1d4e01b79b7d76d615d`, the new offline
root-contract regression reproduced six KeyError/TypeError cases and four cases
that reached the root read before validation. The earlier independent receipt is
historical evidence; its unresolved error-type issue is addressed by this change.

After reading the pointer and validating its schema, resolve now requires root to
be a non-empty, non-whitespace, NUL-free absolute path string. Missing, null,
boolean, numeric, list, object, empty, whitespace, NUL and relative roots raise
`ValueError: invalid resolver root: expected an absolute non-empty path string`
before accessing the supplied data root. Relative roots are deliberately rejected
so they cannot silently resolve against a receiving worker's working directory.
The pointer itself must still be read; this is not a claim of zero filesystem IO.
OS availability/access errors for syntactically valid absolute paths remain OS
errors, not this configuration error.

`python -B -m unittest runtime.massive_maintainer.test_maintain -v` passed 19 tests,
including ten invalid-root subcases with root reads/writes guarded and a valid
historical-resolution control. `git diff --check` passed. This is owner-run offline
validation; independent acceptance of the new revision remains pending. No live
data qualification, migration, refresh, schedule, merge or deployment is claimed.


### Request lifecycle repair - 2026-11-13

Base revision b733012404ecb08528a3c356087853b796574f3b; local uncommitted follow-up.
A fulfilled request now rechecks the indexed snapshot identity, checksum, bounds
and requested age before suppressing repeat demand. Expired identical requests
reopen; a fresh successful replay coalesces. Requests preserve max_age_seconds;
older requests retain the original 1200-second default. Corrupt indexed bytes
fail closed without authorizing acquisition.

Before repair, three new regressions produced two failures and one missing-field
error. After repair, the owned offline suites pass 29 tests. The unchanged 22-case
isolated stress assertions improve from 11 passed / 11 failed to 12 passed /
10 failed, with zero harness errors. These are owner-run tests, not independent
acceptance. No live fetch, production writes, deployment or publication occurred.

This is only a lifecycle correction, not acquisition admission. Existing default
and absent-index plans still lack proof of missing local coverage and entitlement
admission. Malformed request isolation, identity vintages, delayed/sparse coverage,
full request provenance, expected-head publication, invalid-bar quarantine and
long Retry-After compliance remain unresolved. Do not activate unattended refresh.

Dot/B00 integration dependency: retain this existing FETCH owner/conversation;
standardize owner/session/branch/exclusive-path records, versioned requests,
freshness and admission evidence, generation-bound receipts and receiver
acknowledgment in B00-owned templates. The hourly supervisor is not a five-minute
worker. This note does not modify shared templates or claim top-level integration.
Next bounded action: fail-closed acquisition admission with isolated assertions
that existing unqualified history and absent admission evidence cause zero calls.


### Fail-closed acquisition admission - 2026-11-13

Local uncommitted follow-up on b733012. All run() acquisition plans now require
an explicit --admission-file. Consumer requests, explicit/default dates and an
absent index are never permission to acquire. Missing/invalid admission yields
blocked progress/run receipts; malformed requests retain original bytes plus a
content-hashed quarantine disposition and do not abort unrelated valid plans.

The owner-issued local permit schema basket.massive.admission@1 binds owner,
source Massive, ticker, exact exchange date, grain 1m, adjustment split_adjusted,
purpose acquire_absent_day, absolute legacy_root, inventory_sha256 (encoded
inventory records, excluding inventory timestamp), index_sha256 (exact bytes or
explicit null), authorization_ref, entitlement_ref, and expires_at (aware timestamp,
future and no more than one hour away). No permit is generated automatically.
References are owner attestations, not cryptographic authorization or a live
entitlement check. This is an internal module contract, not a shared B00 schema.

Any matching legacy ticker file conservatively blocks, regardless of index state.
An indexed date blocks even with a permit. Missing inventory directory, changed
inventory metadata/index, wrong scope, expiry or absent references block. Absence
is bounded to the explicitly named flat legacy directory and this index; it is
not proof of global archive absence. The owner must establish the complete source
scope before issuing a real permit. Direct low-level fetch_day() remains internal;
this gate applies to run()/CLI dispatch. No schedule or caller was activated.
Existing-date refresh remains blocked pending its separate bounded contract.

Tests: 40 offline regressions pass (26 original, 3 lifecycle, 11 admission).
Initial eight admission tests reproduced eight failing subcases and two errors.
Stress after lifecycle: 12/22 passed. Unadapted callers after admission: 12/22
passed because three formerly implicit acquisitions are now blocked while cases
14, 15 and 22 pass. With explicit synthetic permits for cases 01/21 and admission
mocked only to isolate lifecycle case 13: 15/22 pass; seven genuine defects remain
(05,09,16,17,18,19,20). This is owner-run evidence, not independent acceptance.
No real vendor calls, production data writes or publication occurred.

Next smallest repair: bind a bounded existing-date refresh admission to the exact
observed generation and explicit stale/missing interval; reject changed generations,
legacy overlap and unsupported scope, while preserving coalescing and zero-call
negative controls. B00 still owns any shared request/template adoption. Do not
claim this absent-day gate qualifies data or provides unattended refresh.


### Retry deferral and request provenance - 2026-11-13

Local uncommitted follow-up; same owner and base b733012. Numeric Retry-After and
HTTP dates are supported. HTTP server Date, when present, provides a conservative
second clock basis. Negative/nonfinite/malformed headers persist a review-required
hold. Missing headers use exponential backoff. The four-attempt limit and pacing
remain; the client has a cumulative retry-sleep budget of at most 30 seconds.
A wait exceeding budget, or retry exhaustion, writes an immutable retry receipt
and retry-after.json before raising RetryDeferred. run() records a deferred result.
Later clients read the hold before transport; no 120-second sleep or early retry.

Same-client holds also use monotonic time. Backward wall-clock movement prolongs
holds. Across process restarts the UTC deadline relies on the workstation clock;
a forward clock jump after restart is not independently detectable. This is not
a distributed clock guarantee. Malformed-header holds require owner review.
No scheduler/resume service is installed by this change.

Successful raw responses now have immutable raw-receipts containing GET endpoint,
ordered decoded request_params (including duplicate keys/blanks), response receipt
time and SHA-256 identity. Receipts persist before JSON parsing. apiKey parameters
are stripped; unknown query keys reject before transport, and the active credential
in the retained path/values rejects. Authorization headers and original query
strings are never stored in receipts. Approved parameter names are deliberately
limited to the implemented aggregate/reference/pagination needs. Parameter values
are decoded semantics, not original percent-encoding bytes. Response identity is
the exact raw hash, not a claimed provider request ID.

Owner-run evidence: 51 offline tests pass; 22 retained-fixture stress cases now
have 17 passes, 5 failures, zero harness errors. Prior stage was 15/22. Stress case
05 now asserts durable deferral and no second call instead of requiring a long
sleep, as specified for bounded runs. Cases 01/21 use explicit synthetic permits;
case13 mocks only admission to isolate lifecycle. Case18 now passes. Remaining
failures: 09 stable identity conflict,16 date-pinned reference,17 sparse/delayed
freshness,19 expected-head revision,20 invalid-OHLC quarantine receipt.
No vendor calls, production writes, commit/push, deployment or independent
acceptance occurred. Next bounded repair recommendation: invalid-response
quarantine receipt binding exact raw hashes to the validation rejection.


### Raw-bound quarantine dispositions - 2026-11-13 maintenance 14:55Z

Same MELISSA owner and local uncommitted branch; original base b733012.
quarantine_response verifies each referenced immutable raw SHA-256 and stores a
content-addressed response disposition with reason stage, exception type, requested
symbol/date and sanitized request scope. Raw receipt timestamps remain separately
preserved; excluding attempt timestamps from the disposition makes repeats stable.
No raw bytes or previous dispositions are rewritten.

Massive.get records parse rejection after raw persistence. fetch_day retains
reference/page evidence and records reference identity/schema rejection, aggregate
identity/schema rejection, incomplete pagination, and partition validation or
publication failure before re-raising. A page that persisted but failed parsing
is included through the client's last_evidence. Non-object envelopes, malformed
results lists and non-string next_url values explicitly reject. This does not
establish stable instrument identity across vintages or add historical reference
parameters. Direct lower-level promote fixtures without raw are not authenticated
by this mechanism. A filesystem failure preventing receipt writes still raises;
this is not a guarantee of durability on an unavailable filesystem.

Before: six new tests exposed ten failing assertions/subcases due to absent
receipts. After: 58 offline tests pass, including seven quarantine tests for OHLC,
parse/schema/identity errors, pagination interruption, unchanged prior index and
generation, raw checksum readback and identical repeat dispositions. Retained
22-case stress suite improved 17 to 18 passes; case20 now passes, with four
remaining failures (09 identity change,16 reference date,17 sparse/delayed freshness,
19 expected-head). No stress assertions changed this increment. Earlier explicit
fixture permits, isolated lifecycle gate mock and durable-deferral expectation
remain documented. Owner-run evidence only; independent acceptance pending.

Historical raw_r2/raw_r3 provenance gaps remain: absent original response IDs/hashes,
returned adjustment flags/factors and executed transformation revision are not
retroactively recovered by new code. Migration authorization remains separately
unresolved. No live fetch, source relocation, production promotion, schedule,
publication or deployment occurred. Next bounded recommendation: prevent
sparse/delayed responses from satisfying current-data consumer requirements.


### Current eligibility and historical identity - 2026-11-13

Base b733012; 68 owner-run offline regressions pass. Historical reference queries
now include the requested date. At least one CIK/FIGI identifier is required;
recorded identity fields must match previous entries for this symbol. Missing prior
identity or changed identity rejects while retaining the conflicting reference raw
and quarantine receipt. This is conservative continuity, not automated corporate
reorganization resolution. Historical metadata is not retroactively repaired.

Stress improved from18/22 to21/22. Sparse DELAYED, date-pinned reference and changed
CIK cases pass. The sole remaining failure is19 expected-head publication. Positive
fixtures explicitly declare completion/session, simulate the observation clock and
carry matching baseline identity. An initial fixture identity mismatch was retained
before correcting the fixture; no adverse assertion was removed. Earlier synthetic
permits, lifecycle-only gate mock and durable retry deferral remain documented.

No source acquisition, production changes, migration, schedule activation or
independent acceptance occurred. Shared templates remain a B00 handoff. Local
commit is explicitly authorized; publication is not retried. Next bounded code
change is expected-head publication with stale-writer rejection and replay controls.
