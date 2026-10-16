# _BASKET — Essential Conversation Launch Pack

**Prerequisite:** Review and authorize merge of PR #2 into `main`. Confirmed cross-domain handoffs: [B00 contract #3](https://github.com/whiterosecoffee/_BASKET/issues/3), [B05 SFTBY migration #4](https://github.com/whiterosecoffee/_BASKET/issues/4), and [B01 CI verification #5](https://github.com/whiterosecoffee/_BASKET/issues/5). Until then, the starter file exists only in the orchestration branch. Every *new* conversation reads the merged `AGENTS.md` + `orchestration/sparks.json` and creates its own NEW GitHub issue and branch; these prompts never preassign the currently active branch.

## W0: Contract steward — B00
```text
Launch spark B00 — Shared Contract Reconciliation.
Create a new issue and unique branch from main; do not reuse the orchestration branch.
Inspect the failing SFTBY relationship-schema validation run 38926002189.
Define where holdings look-through, NAV references, coverage metadata and acquisition pipeline data properly belong; update only owned shared schemas/architecture plus migration instructions. Do not edit tickers/SFTBY/relationships.json or CI scripts. Open precise linked handoffs to B05 for data migration and B01 for validation checks. Prove the revised schema's strictness and backwards compatibility or versioned migration.
```

## W1: Make trust and evidence operational

### B01 — CI integrity
```text
Launch spark B01 — Integrity and CI Rescue. Create your own issue and new branch from main after reading AGENTS.md and sparks.json. Reproduce run 38926002189: SFTBY relationships.json contains undeclared properties rejected by the relationships schema. Own only shared tests/validator/CI. Diagnose root cause and propose strict assertions; coordinate with B00 schema owner and B05 relationship owner through linked handoff issues. Do not relax validation or edit the data/schema yourself. Include failing and passing CI evidence and regression tests.
```

### B05 — Canonical relationship graph
```text
Launch spark B05 — Relationship Graph and SFTBY Reconciliation. Create your own issue and new branch. Inspect SFTBY relationships.json and schemas/relationships.v1.json; perform point-in-time stock/flow, ownership, fund, NAV and acquisition-status separation. Write only canonical relationships files and relationship engine/research graph under B05 ownership; ask B00 for any contract change; send event changes to B03. Remove accidental mixing by explicit versioned, tested migration rather than dropping useful evidence. Acceptance: canonical relationship data valid, dated, USD-aware and non-double-counted.
```

### B02 — Historical and live feed truth
```text
Launch spark B02 — Data, FX and Time to Die. Create your own issue and branch. Audit runtime/feeds.json and ttd.py, the existing 262 daily bars per eligible public ticker and 326 JPYUSD historical bars. Separate reproducible historical data from live entitlement and worker state. Implement read/replay, append-only corrections, timestamp alignment, TTD invalidation and tests in owned files. Do not imply continuously updated data until a durable worker and authorized provider work. Provide sample status showing fresh, expired and unavailable fields.
```

### B03 — Earnings and event evidence
```text
Launch spark B03 — Point-in-Time Earnings and Events. Create your own issue and new branch. Verify the prior MRIE 2026-10-16 backfill against primary SEC/issuer documents where possible, preserving source/accession IDs, effective vs available times, deal/authorization status and contradictory evidence. Write only tickers/*/events.json and research/events or filings. Send relationship changes to B05, schema requests to B00, company-model implications to their owners. Provide idempotent revision/replay demonstration.
```

### B21 — Narrative/false-assumption analysis
```text
Launch spark B21 — Narrative and False-Assumption Intelligence. Create your own issue and branch. Inspect engines/narrative/engine.py and CoreWeave/OpenAI/Anthropic case. Treat article claims, synthetic private-company perp marks, SEC facts and assumptions differently. Trace reported valuation derivation; avoid promoting correlation into causality. Audit available_at vs observed_at vs event/economic effective dates, expire quote-based inputs, and preserve competing explanations/falsifiers. Extend tests under owned tests/test_narrative.py and produce a reproducible uncertainty report. Handoff canonical event/graph changes to B03/B05.
```

## W2: First investment-intelligence vertical slice

### B06 — Traversal and cycle mechanics
```text
Launch spark B06 — Traversal and Cycle Engine. Create your own issue and new branch. Audit engines/traversal/range.py and sftby_zoom.py. Compute descriptive 5/20/60/200 daily range, intraday when dated and entitled, price/volume velocity, acceleration and conditional cycle paths. Explicitly model transaction costs, missed rebounds and counterfactual trim/re-entry for 3% moves. Never assert calibrated likelihoods before B07 validates. Provide dated USD-first output and replay fixture.
```

### B09 — SoftBank parent and USD NAV
```text
Launch spark B09 — SFTBY Parent Holdings and NAV. Create your own issue and unique branch. Reconcile 9984.T/OTC ADR mechanics, disclosed ownership/commitments, ARM/OpenAI and fund look-through, USDJPY exchange exposure, debt currency/maturities and dated holding valuations. Own only tickers/SFTBY/entity.json and research/SFTBY/**; request canonical graph edges via B05 and events via B03. Produce dated USD NAV scenario and confidence ranges, but do not label any output live when constituent feeds are stale/missing.
```

### B10 — CoreWeave economics
```text
Launch spark B10 — CRWV GPU Lifecycle and Financing. Create your own issue and new branch. Reconcile debt structure, actual convertible/ATM issuance, GPU cohort refresh, utilization, power commissioning, contract RPO, residual hardware value and the 5–7 year cash-flow profile. Own tickers/CRWV/entity.json and research/CRWV/**. Distinguish contracted dollars from profits and financing authorizations from executed deals. Output bear/base/bull bridge with dated evidence; route canonical events/edges to B03/B05.
```

### B11 — AAOI manufacturing economics
```text
Launch spark B11 — AAOI Optical Manufacturing. Create your own issue and branch. Model optical transceiver manufacturing capacity, customer demand, margins, dilution, competition and supplier bottlenecks. Separate global optics TAM from laser subcomponent TAM and company-specific attainable sales. Own tickers/AAOI/entity.json and research/AAOI/**. Do not claim direct LITE→AAOI contracts without evidence. Send verified events/relationships to their owners and publish dated, falsifiable unit-economics scenarios.
```

## Execution discipline
Keep at most 3–5 concurrently active sparks. A new conversation gets a *new issue and branch*, even if resuming another spark. A shared dependency issue is not a worker branch, and no direct message can be sent from one conversation into another. Use issue titles and linked PRs for handoffs. Merge only with explicit authorization. The full original prompts and read/write boundaries live in `orchestration/sparks.json`.
