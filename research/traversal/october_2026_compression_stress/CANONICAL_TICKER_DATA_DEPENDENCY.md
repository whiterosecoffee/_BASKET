# Canonical ticker data dependency and zero-duplication policy

User direction November 3, 2026: all instrument data belongs under logical _TICKERS/{ticker-symbol}; canonical ticker-symbol.jsonl records are owned by ingestion, not B06.

## Verified migration state
B00 issue #146 and draft PR #147 stage _TICKERS scope records, but existing canonical tickers/** history has not been migrated. B00 handoff #148 defines the transactional migration and unified CRUD resolver. The _TICKERS target is NOT yet a proven ready-to-read history source on main. Do not silently read an unverified alternative and call it canonical.

## Requirements for B06
- Consume a single B00-approved logical resolver: resolve(instrument_id, data_kind, access_mode, as_of). The target logical home is _TICKERS/{ticker-symbol}; the resolver reports exact versioned location, SHA/manifest, freshness, completeness and migration state.
- No B06-owned copies of historical bars, market JSONL, earnings, ticker fundamentals, quote streams, company event or relationship records. No independent SQLite mirror, second poller or duplicate live ingestion.
- Derived battle-range metadata and event JSONL are B06's own data class, not duplicated raw ticker observations. Store only immutable source record IDs, canonical paths, input hash, range boundaries, state transitions and output model version. Confirm B00-approved destination for ticker-local derived events before persisting there.
- A limited explicitly SYNTHETIC unit-test fixture is permitted, clearly noncanonical. Historical research reports contain aggregate measures or references, never copied raw rows as a secondary price archive.
- Fail closed on missing resolver or missing canonical data: mark BLOCKED_CANONICAL_DATA, record required missing intervals. Temporary legacy reading may occur only when the authorized resolver explicitly returns a documented pre-cutover legacy path, read-only.
- Never append new line entries directly as B06. Submit missing-lines requests to B00 orchestrator and B02, under #148, to append missing verified entries to the eventual approved _TICKERS/{ticker-symbol}/{ticker-symbol}.jsonl target. Preserve original provider, timestamp, entitlement, dedupe identity and corrections.
- Never manufacture price or OHLCV to fill coverage holes; do not count shared parent/child minute bars twice.

## Missing-line handoff envelope
Request fields: request_id, originating_issue=144, target_issue=148, ticker_symbol, data_kind, interval, start_utc, end_utc, exchange_session, canonical_target, source_requirement, missing_reason, as_of_utc, consumer_test, required_validation. Each required ticker/timeframe gets its own auditable request, not bulk blind backfill.

## Owners
B00: naming, security master, canonical resolver and orchestration; B02: source ingestion and append-only ticker JSONL; B01: migration validation; B06: consumption and derived range engine; B03/B05: events/relationships per existing ownership. No writes by B06 outside new research/traversal/october_2026_compression_stress/** in issue #144 / draft PR #145.

## Acceptance
1. Zero duplicate market observation records in B06 branch.
2. Source reads route through resolver and as-of snapshot manifest, or return explicit blocked state.
3. Missing bars generate B02/B00 handoff rather than a parallel source.
4. Derived events reference source record identities and reproduce their outputs without copying bars.
5. No claim that _TICKERS migration is complete until issue #148 and independent CI verify cutover.