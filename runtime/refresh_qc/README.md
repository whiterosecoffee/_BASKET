# Read-only FETCH ledger binding

Issue #207, scoped to runtime/refresh_qc. This is a narrow evidence-reconciliation tool, not the previously unpublished QC gate, fetcher, sanitizer, canonical writer or durable store. It performs no source writes or network requests and never authorizes promotion.

## Execution and trust

`python -B -m unittest discover -s runtime/refresh_qc -p test_ledger_binding.py -v`

`python -B runtime/refresh_qc/ledger_binding.py --manifest <private-manifest.json>`

The private manifest supplies ticker, round and an artifacts object. Each artifact contains an explicit local path and previously selected lowercase SHA256 pin. Required logical artifact names: plan, done, request_ledger, apply_ledger, capture, output, fetch_plan.py, fetch_run.py, verify_apply.py, ticker_jsonl_tool.py. Do not commit a real path-bearing manifest. Output is a sanitized JSON receipt on stdout; the caller may retain it privately or publish only approved aggregate evidence. Exit 2 means blocked. Avoid redirecting output over any input. No apply command is called.

The verifier checks exact current bytes against pins; one plan range; exact ticker/provider symbol/date range; successful request and marker with matching row counts; one unambiguous apply receipt with the current output hash; distinct minute timestamps within the date range; nonnegative finite volume; and planned missing-session presence. Numeric dates/statuses/counts cannot masquerade as valid strings/integers. Duplicate JSON keys, non-object records and stale pins fail closed. JSON artifacts have a 32 MiB limit; decimal volume supports at most 1000 digits and adjusted exponents -308 through 308. Larger artifacts/precisions need a reviewed extension, not silently relaxed checks.

This deliberately does not validate OHLC quality, full calendar coverage, current entitlement, source authenticity, revision validity or durable publication. Count/range matches cannot create a missing historical capture-hash link. Current script identities are not evidence of which code ran in October. The captured request ledger time is a logged observation, not historical first external availability. A receipt pins this verifier's bytes and its local receipt version; it is not a signature. Re-execute against explicit trusted pins rather than treating a saved receipt as authority. Mutation outside a read window is not locked, and no multi-file transactional snapshot is claimed.

## Real read-only result, 2026-11-12

`ledger-binding-evidence-2026-11-12.json` records two identical executions against the existing NVDA raw_r3 inputs. 5673 staged minute bars, 6 observed dates, 5670 fractional-volume rows. Plan has five missing sessions with an October 1 anchor. Marker, request ledger and apply staged counts agree. The request is logged at 2026-10-09T19:32:38Z. Recorded final apply hash exactly equals today's legacy file. No historical capture hash, executed-code identity or historical first availability has been established. Canonical eligibility is false.

Independent read review reproduced all aggregate counts/hashes in RECEIVING_ASSESSMENT_2026-11-12.md. On October 8 all 941 stored volumes equal staged values rounded half-up; 940 differ from the retained fractional values. This supports the observed rounding explanation, not authenticated historical causation.

A separate in-memory test of the extracted legacy sanitizer reproduced representation dependence and non-idempotence: numeric fractions round on the first call, while equivalent numeric strings convert to fractions first and round on the second call. No legacy module entrypoint was executed and no source values were changed.

## Exact correction and durable-generation acceptance

1. Preserve original files and raw capture bytes, their current hashes and the historical ledger chain. Never patch rounded volume in place or claim recovered historical precision from already-rounded values.
2. Establish a versioned fractional-volume/unit contract at the approved nested component boundary. Numeric-equivalent encodings must produce the same exact value; second sanitation must be unchanged; no integer conversion or binary-float rounding may change volume. Trade counts require an explicit independent units/type policy. Test decimal fractions, numeric strings, zero, negative/nonfinite rejection and repeat behavior.
3. Treat retained staging as candidate evidence until request/source, adjustment, calendar, venue/currency, entitlement and revision bindings are qualified. Existing adjusted=true source code alone is insufficient provenance. Reject missing bindings rather than filling historical availability from file timestamps or current capture time.
4. Once qualified and authorized, append a NEW immutable generation with explicit source hashes, parent generation/expected head, supersession reason, instrument/session/grain/basis, versioned schema and exact transform/verifier bundle. Preserve older generations and readers; never substitute current code for an older bundle. Consumer selection requires explicit supported revision and source pins, with fail-closed unknown revisions.
5. Publish one physical exchange-session partition only after exact-content verification. Lock or compare-and-swap the entire read/validate/publish transaction, reject stale expected heads and competing writers, fsync staged files/metadata and use an atomic commit marker. Restart/crash tests must show either prior complete generation or new complete generation, never a partial visible result. Platform filesystem durability still requires real integration evidence.
6. Acceptance tests: same-source replay unchanged; revised source adds a generation without changing prior bytes; wrong source/schema/code hash rejected; old-reader replay preserved; unsupported reader rejected; invalid/mixed-session/conflicting rows rejected without publication; concurrent/stale-head write rejected; crash interruption recoverable; separate consumer rereads and verifies exact bytes. Legacy row counts or old_bytes_unchanged=None are not sufficient verification.
7. Keep _MAP availability meaning distinct from PR242's local materialization cutoff. Historical PIT requires original external revision availability; a conservative current observation only supports access after observation. Resolve through the existing contract owner, not a field rename.

These are acceptance requirements, not an implemented writer or approval to activate one. Current safe next step is the existing-owner contract/seed qualification of this mapping and recovery of prior QC artifacts. Original NVDA modification, production FETCH changes, canonical activation, publishing, merging and scheduling are not performed by this increment.
