# B06 — Traversal worker operating contract and runbook

**Parent:** B00. **Issue:** #57. **Branch:** `work/57-b06-oct16-traversal-stress-fixture`. **Draft PR:** #58.
**State mapping:** available (unclaimed) → `claimed`; implementing → `building`; testing/review-ready → `review`; independently accepted → `component_verified`; blocked → `integration_blocked`; merged and main-checked → `integrated`; retired → `closed` or `withdrawn` (only with recorded disposition). This file is descriptive, not a new status registry.

## Exclusive scope and interfaces
- **Writes:** `engines/traversal/**`, `research/traversal/**`. **Reads:** B02 `tickers/*/history.jsonl`, `tickers/*/intraday/**`, `fx/**`; B03 issuer events; B05 relationships; B00 schemas; B01 CI; B08 snapshot API.
- **Never write:** `runtime/**`, `fx/**`, `tickers/**`, `schemas/**`, `orchestration/**`, `tests/integration/**`, `.github/workflows/**`, `services/**`.
- **Input:** timestamped, source-identified same-listing price and previous close in original currency; observation and availability times, quote status, optional independent Tokyo threshold pair and material news. `evaluate` consumes a Python mapping, not an invented canonical schema. Missing inputs are rejected rather than silently filled.
- **Output:** pure deterministic `status` (review/quiet for UI decision only), `triggers`, `accepted`, `rejected`, and a non-predictive warning. This is not `basket.worker_task@1` status and is not a new canonical store.
- **Downstream:** B08 may consume a future B00-approved versioned interface after B02/B01 validation; current interface is experimental and local.
- **Provider:** no entitlement, polling, scheduling, persistence, or quote acquisition is implemented.

## Deterministic method
1. Discover/acquire: B02 provides inputs; no B06 provider access. Reject unknown source.
2. Normalize: parse timezone-aware ISO timestamps and numeric same-listing prices.
3. Verify: fail closed on future/expired observation, missing provenance, invalid values, previous-close masquerading as intraday.
4. Reconcile: compare percentage returns only when all inputs pass age and availability checks; relative divergence remains **provisional** because common timestamps alone do not prove feed synchronization.
5. Calculate: absolute SFTBY move >=3%, SFTBY–ARM/PAYP difference >=5 percentage points, independently evidenced Tokyo crossing of ¥4,800 or ¥5,000, material source-available news.
6. Persist: caller-owned; B06 only commits immutable research fixture and source code. No canonical observation mutation.
7. Validate: `python -m unittest discover -s engines/traversal -p 'test_alert_gates.py' -v`. Repeat calls are idempotent for identical inputs; input identity must eventually use B02 source revision plus available-at fingerprint.
8. Publish/invalidate: only after B01 approves and B08 consumes an approved contract; new source revision, changed FX, revised event, or new availability invalidates downstream calculations. No automatic retries: invalid data is rejected and must be corrected upstream.

## Acceptance / failure register
| ID | Evidence | Status |
| --- | --- | --- |
| A1 | Screenshot fixture preserves 5 USD assets, unverified trade times, separate Tokyo close and indicative FX | Implemented, JSON parsed |
| A2 | Pure alert gates, quiet path, price movement and peer divergence | Code and tests committed; execution pending |
| A3 | Reject stale/future/missing provenance and avoid ADR-implied Tokyo break | Code and tests committed; execution pending |
| A4 | Cross-session synchronization and FX source revisions | Blocked on B02 contract |
| A5 | Independent exact-head CI and integration | Blocked on B01/B00 approval |
| A6 | Durable operational alerts | Not implemented; B08/provider dependency |

Known failures: a user screenshot does not provide exchange execution timestamps; indicative FX cannot establish parity; cross-feed return comparisons may not be synchronized. No forecast probabilities. Repository clone from this environment failed DNS resolution; this is **not** a code test failure and must not be reported as passing tests.

## Improvement backlog
P0: run tests on real GitHub Actions or connected checkout and fix failures; P0: B02 normalized snapshot/revision fingerprint handoff; P1: B01 independent negative tests; P1: B00-approved versioned B08 interface; P2: extend descriptive 5/20/60/200-session and volume context using existing `range.py` rather than duplicating it.

**Worker protocol:** Issue #57 is the task claim; terminal resolution is posted as `basket.worker_resolution@1` using the B00 protocol. No alternate queue or worker manager is created.
