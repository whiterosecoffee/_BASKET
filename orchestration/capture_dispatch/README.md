# Full-basket capture dispatch

Issue #48, B00. Executable offline dispatch proposal, not a daemon or production data feed. Extends the direction of #42 / PR #43 without editing its owned file, queue.json (#24/PR #25), runtime or canonical records.

Run from a complete repository checkout:

```sh
python orchestration/capture_dispatch/plan.py --tickers tickers --as-of 2026-10-18T03:00:00Z
python -m unittest discover -s orchestration/capture_dispatch -p 'test_*.py' -v
```

The first command discovers every canonical ticker directory. --candidates accepts a JSON array of research-universe IDs and reports unregistered candidates separately; it never silently promotes them. --coverage accepts ticker -> capability -> state, with observed_at, first_available_at, expires_at, record_ids and source_ids. Only a provenance-backed state inside its validity interval is fresh. Coverage input must be supplied by a verified journal reader; it is not independently verified by this compiler. Task keys are stable ticker/capability identities, not replacement worker issue IDs. Missing data generates work; blocked providers generate gap-resolution work. Entity classes beyond public_equity/private_company fail closed pending explicit support. Applicable topic selection is a receiver responsibility: all-topic missing coverage is a proposal, never a conclusion about a company's business.

## Required data plane

Use a configurable durable local root, mounted on persistent storage when hosted. Proposed logical layout, pending B00/B02/B03/B21 owner contract review:

- tickers/<ID>/observations.jsonl: sourced economic observations and issuer statements.
- tickers/<ID>/perspectives.jsonl: hypotheses, competing interpretations, falsifiers and revisions.
- tickers/<ID>/signals.jsonl: derived changes referencing exact observation/perspective IDs and method versions.
- tickers/<ID>/state.json: rebuildable checkpoint, provider watermarks, freshness and coverage.

These are runtime data paths, not instructions to create competing GitHub canonical stores. Preserve existing history.jsonl, events.json and relationships.json ownership and projections. Reuse B02 append journal rather than introducing a competing writer. Do not persist raw fetched documents as verified facts automatically.

Every economic record needs immutable ID, entity ID, domain, metric/claim, value and units when applicable, period/effective time, first availability, observation and ingestion times, evidence category, source URL/document ID and content hash, revision/supersedes identity, USD/original-currency/dated-FX provenance, freshness policy, worker/run identity. Unknown source times remain null and prevent point-in-time claims requiring them. Perspective and signal rows also carry input record IDs, model/version, horizon, assumptions, alternatives, falsifiers and expiry. A market price, company guidance, third-party report and inferred relationship are distinct evidence categories.

## Owner execution sequence

1. B00 #42 reviews JSONL logical contracts and existing-store compatibility; #24/PR #25 owner registers this work with stable noncolliding task IDs. Reconcile canonical registry with B19 #17/#21 research universes, showing exclusions and missing entities. Never let a five-ticker sample define full coverage.
2. B02 #11/PR #15 reuses its append-only writer, adds entitled provider adapters and ticker-independent discovery/fetch/normalize/validate/append/checkpoint execution. B03 #12/PR #14 supplies filing/IR facts, issuer revisions and event projection; contract/capacity, capex, HBM/DRAM, optics and power evidence must be dated and attributed. Company research workers own company interpretation, not feed writes.
3. B21 implements perspective/signal projections from exact ticker journal IDs. Recompute only affected inputs; propagate relationship impact through B05 stable edges. B04/B19 perform valuation and aggregate flow reconciliation without adding supplier pass-through to final demand.
4. B08 #34 runs persistent scheduling, leases, bounded retries/backoff, restart recovery and health/freshness reporting. Freshness is data-class/provider-specific; live means a measured successful adapter run and durable writes. Chat automations cannot supply a continuously running local process.
5. B01 independently tests exact revision: duplicate ingestion, source amendments, point-in-time replay, missing entitlement, concurrent writer/crash recovery, stale/future-input signal suppression, complete-universe coverage, ownership isolation and post-restart persistence. A branch test pass is not integrated deployment.

Deliverable is a running ticker-agnostic worker fleet with coverage for every admitted entity and explicit gaps. Reports read those stores; Monday summaries are optional views. No position sizing. USD throughout.

## Acceptance evidence

Five local unittests passed on 2026-10-18 UTC (2026-10-17 Eastern): fanout/idempotency; freshness and provenance; private-entity and candidate separation; blocked provider and timezone rejection; canonical discovery fail-closed. Six public-equity test fixtures generate 42 unique capability proposals. These are synthetic test inputs, not 42 live workers or economic observations. No full-repository discovery, live provider call, hosted persistence or CI run has been claimed.
