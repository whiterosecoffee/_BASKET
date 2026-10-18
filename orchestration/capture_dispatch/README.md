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

## Archive handoff — 2026-10-17 Eastern

Ownership audit fetched every changed-file list for all 13 open PRs (#14, #15, #18, #22, #23, #25, #31, #33, #38, #43, #46, #47, #49). No other PR changed this workstream's three files. Active conversation count is unknown. PR lists show reserved work, not proof a conversation is running.

Important new integration boundary: PR #33 now owns orchestration/agentic/**, including manager.py, github_adapter.py and cli.py. This compiler must feed coverage-gap proposals into that manager; do not create a second lease store, scheduler, attempt ledger or automatic worker launcher here. PR #25 owns planner queue/execution-loop changes; PR #47 owns shared QC workflow. PR #46 owns dedicated OpenAI research CI. All were left untouched.

Pinned research-universe evidence:
- PR #18 head 109bbd9e76c29db24b19b74654221de5fb1b5133: 68 working research entity IDs.
- PR #23 head 6af9a5f221a760139c86e85f3f5da0b05fb206ba: 42 candidate ticker IDs.
- Intersection is empty; union is 110 distinct research IDs. This is NOT 110 admitted canonical entities or verified data feeds. B00 must reconcile identities/listings and inclusion/exclusion before asserting completeness.

Final scoped hardening: malformed coverage containers, string/empty provenance IDs, nonstring timestamps, invalid candidate identities and an empty direct compiler universe fail closed. Seven local tests passed after this change. Original shared workflow succeeded on 92986aac1e9170ddccd31dd4a9ee85eb75991641: https://github.com/whiterosecoffee/_BASKET/actions/runs/39093782003 . That workflow is not evidence of execution of this new test module. Recheck current head separately.

### Orchestrator receiver prompt

Resume B00 orchestration in the existing owning conversation. Retrieve #48/PR #49, #42/PR #43, #24/PR #25, #32/PR #33, #44/PR #47, B02 #11/PR #15, B03 #12/PR #14 and B08 #34. Refresh current heads, changed files, CI and explicit worker claims; do not infer running chats from open PRs. Preserve this branch and three-file ownership; do not start a duplicate dispatch worker.

1. Integrate this compiler as an offline coverage-proposal producer for the PR #33 agentic manager. Keep one manager/lease/attempt system; map proposals through existing versioned worker-task contracts. A proposal never grants path ownership or proves live coverage.
2. Through the current PR #25 owner, register exact dependent capture tasks with noncolliding IDs. Resolve the four B00 QC failures from PR #47 and require B01 rerun. Reconcile all 110 research IDs against canonical registry and show reasons for omissions, invalid identities and unregistered candidates.
3. B00 #42 reviews one source/revision/time/freshness envelope and exact runtime JSONL projection ownership. Preserve B02 market journals, B03 canonical events and B05 relationship stores; no competing canonical data.
4. Existing B02 and B03 owners implement source discovery -> normalize -> validate -> append -> checkpoint with real provider responses and explicit entitlement/source gaps. Capture may proceed before valuation or graph completion. Use same code across all admitted entities; sample tickers only test execution.
5. B08 #34 prepares persistent host/scheduler/auth now using fixtures, then wires reviewed real workers. Require measured scheduled execution, restart survival, lease/retry behavior and freshness health. Do not claim live on code/PR existence.
6. B01 independently runs python -m unittest discover -s orchestration/capture_dispatch -p 'test_*.py' -v at exact PR head, then independently tests B02/B03/B08. Do not edit workflows from B00 or count unrelated shared green CI as domain-test proof.
7. B21 builds perspective/signal projections using exact journal revision IDs, alternatives, falsifiers and expiry. B04/B05/B19 enrich downstream; no need to block initial capture.

First acceptance milestone: real external document -> validated per-ticker JSONL -> duplicate-safe restart/replay -> evidence-linked derived signal. Scale the same worker to the entire admitted registry with an explicit freshness and gap matrix. Completion requires this measured pipeline; neither this archived chat nor its draft PR proves it.
