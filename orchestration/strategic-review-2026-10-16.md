# _BASKET — Strategic Direction and Execution Review

**As of:** October 16, 2026. **Owner:** Orchestration Issue #1, branch `work/1-conversation-sparks-orchestration`. **State:** proposal for review, not production-certified.

## Executive decision

_BASKET should be an **evidence-preserving economic inference system with a deterministic, timestamp-aware market-traversal layer**. It should not become a generic AI stock screener, a collection of persuasive investment theses, or a chat history masquerading as production infrastructure.

**North-star question:** Given today's verified observations and uncertainty, what changed in the economic graph, how much of it is already priced, what is the basket's traversal position and velocity, and what would falsify a decision to buy/hold/trim/re-enter?

This requires four distinct truth planes, each returning provenance, validity and model version:
1. **Observation plane** — quotes, dated financials, corporate announcements, SEC/issuer events, analyst or market narratives; separate what was measured from what was said.
2. **Economic graph** — capital, ownership, contracts, business pools, downstream/upstream impacts, currency and double-counting constraints.
3. **Inference plane** — deterministic calculations, scenario trees and explanatory hypotheses with explicit assumptions and falsifiers. Narrative market signals are *claims*, not equity transactions.
4. **Decision plane** — observable multi-horizon traversal, calibrated conditional ranges, transaction-cost-aware cycle tradeoffs and adverse cases. No learned probabilities until validation.

These planes can run independently, but derived outputs are invalid or provisional when material source dependencies are stale.

## Evidence-backed repository status

- Main has source roots `architecture/`, `engines/`, `fx/`, `runtime/`, `schemas/`, `tests/`, and `tickers/`.
- Main's ticker data includes AAOI, CRWV, OPENAI and SFTBY. The published architecture records 262 daily U.S. stock bars per eligible ticker and 326 historical JPYUSD daily bars; this is historical coverage, not proof of live feed or current NAV.
- `runtime/feeds.json` disables every proposed live adapter. Neither ChatGPT nor GitHub Actions is an entitlement-aware always-on quote feed.
- Main contains a narrative engine at `engines/narrative/`, existing tests and sample CRWV/OPENAI private-perp claims. This domain was not owned by the initial 21-spark registry; now spark B21.
- As of October 16, the Validate BASKET data workflow is failing on main and the orchestration branch (GitHub run 38926002189). The job specifically rejects SFTBY `relationships.json` fields `as_of`, `coverage`, `named_exposures`, `nav_reference_usd`, `pipeline`, `scope` under a schema with `additionalProperties: false`.
- Narrative tests succeeded in a separate main workflow; they do not validate upstream financial numbers, actual market feed reliability or causal conclusions.
- PR #2 is draft and unmerged. New conversations reading GitHub main cannot discover these spark documents until that PR is approved/merged. Do not launch a worker based on falsely assumed main docs.

## Seven strategic hazards

### A. 22 sparks do not mean 22 simultaneous agents
An unbounded parallel workforce increases shared-contract churn and handoff latency, without improving rate-limiting ingestion and validation. Start with 3–5 concurrently; schedule work by critical path and measurable release gates.

### B. Contract drift is already harming CI
SFTBY relationship data includes NAV/coverage context not allowed under graph contract. Do not disable validation or accept arbitrary fields merely to produce a green badge. Use B00 schema design decision, B05 data reconciliation, B01 independent test verification.

### C. Cross-domain ownership must follow *write surfaces*, not ticker interests
A company research worker should not directly modify relationship edges or event registries. The event owner B03 and graph owner B05 ingest validated proposals. Domain workers own test code in their module and/or explicitly assigned unit tests; B01 owns integration gates, not every test in the project.

### D. Historical truth does not expire like a quote
Separate `effective_at`, `observed_at`, `available_at`, `ingested_at`, `period_end`, and computation dependency expiration. A 2026Q2 filing remains a true historical filing even when no longer sufficient as the latest balance sheet. A quote can be obsolete within seconds, while still valid for backtesting. TTD means **Time to Die for use as current input**, not deletion of history.

### E. Evidence confidence and valuation precision are not interchangeable
Hard distinctions: announced vs signed vs funded vs completed; revenue vs capacity vs backlog vs booked earnings; price of a low-liquidity synthetic derivative vs real transacted enterprise equity; stated fixed debt coupon vs secondary-market yield; capital authorization vs dilution execution; shared profit pool vs incremental demand. Preserve contradictory facts and a falsification queue.

### F. GitHub is not the live data plane
Keep source, schemas, reproducible manifests, QA fixtures and curated snapshots in GitHub. Store high-volume 1m/5m rolling bars and append-only JSONL on durable local/object/database storage, linked by immutable hashes/checkpoints. Source-adapter provenance and entitlement checks must survive restarts. The repo will become costly and conflicting if multiple chat workers commit minute bars continuously.

### G. Descriptive traversal is not predictive accuracy
Compute 5/20/60/200-session range position, direction, price/volume velocity and acceleration as measurements; add event and fundamental overlays; only offer calibrated conditional probabilities after walk-forward tests. Explicitly account for spread, slippage, taxes where appropriate, missed rebounds and lost time out of market when discussing a ~3% trim/re-entry edge.

## Vertical slice rather than full universe
Prove one reproducible report connecting SFTBY, CRWV and AAOI. Include related NVDA/ARM/OPENAI/FX signals as secondary observed inputs when available, not as newly launched company research requirements.

Report contract:
- **Data:** source/provider, exchange, exact as-of, adjusted/unadjusted basis, timezone, TTD status, missing feed warning.
- **Price traversal:** descriptive 5/20/60/200 daily position, 1m/5m session position if entitled and within TTD, signed velocity and volume qualification, coherent session boundaries.
- **Economic state:** dated financial evidence, contract status, power/utilization/capex/financing, ownership/FX look-through with de-duplicated pools.
- **Narratives:** key claims, causal alternatives, weak assumptions and observation conditions that would support/refute each.
- **Output:** scenario paths in USD, range/re-entry cost, confidence/falsifiers, no invented point estimates, exact model/data versions.
- **Replay:** reproduce report for historical as-of timestamp without using later disclosures.

## Priority gates

| Gate | Definition of done | Owner |
|---|---|---|
| G0 | AGENTS and sparks on main; issue/branch created per conversation; no conflicting writes | B00 |
| G1 | CI green with relationship data/schema correctly reconciled and strict validation intact | B00 + B05 + B01 |
| G2 | Replayable single-provider ingestion, FX time alignment, TTD/entitlement tests and explicit unavailable statuses | B02 |
| G3 | Event, graph and narrative evidence can link source IDs, as-of times, contradicted claims, company files | B03 + B05 + B21 |
| G4 | 3-holdings deterministic report with descriptive traversal and scenario assumptions | B06 + B09/B10/B11 |
| G5 | Held-out walk-forward predictive evaluation and trade execution-cost accounting | B07 |
| G6 | Secured hosted tool/worker with observable health, cost, rate-limit and recovery behavior | B08 |

## Recommended worker activation
1. **Review/merge PR #2 when authorized**, and launch B00 contract-focused follow-up for the schema/data model (its own issue/branch).
2. **Wave 1:** B01 integrity gate (handoff #5); B05 relationship reconciliation (handoff #4); B02 feed/TTD; B03 event ledger; B21 narrative/claims. Start at most 3–5 at a time.
3. **Wave 2:** B06 traversal, B09 SFTBY, B10 CRWV and B11 AAOI. Company research can proceed while upstream calculations remain blocked; do not claim live NAV or trade probabilities.
4. **Wave 3:** B04 economics, B07 calibration, B08 tool deployment and B17 composite signals.
5. **Wave 4:** ARM, OpenAI, NVDA, optics, telco/cable, memory and full supply-chain expansion only after the vertical slice is reproducible.

## Concrete falsification discipline
For each hypothesis write: proposition, possible causal graph, 2–3 plausible alternatives, earliest data that could falsify it, source timestamp, materiality, status. Examples:
- *CRWV drawdown caused OpenAI perp valuation decline*: test oracle construction, sector factor, common liquidity and timestamp ordering.
- *SFTBY USD NAV rises mechanically with ARM*: reconcile dated ownership, cross-listing/ADR ratios, FX, hedges, liabilities and fund-level leverage; no stale price substitution.
- *NVDA edge network partnership increases CHTR value*: demand, operating/engineering unit costs, contract existence and economic share matter before speculation on strategic relationship.
- *A 3% trim is as good as a 3% gain*: account for probabilities, friction, timing, tax exposure, missed rebound, alternative upside and conditioning on event risk.

## Operational scorecard (no invented maturity index)
Monitor: failing CI checks, unresolved schema mismatches, freshness/entitlement status by field, source coverage for each required company fact, unresolved contradictory events, count/age of handoff blockers, market alignment gaps, deterministic report replay success, and out-of-sample calibration error. Refuse production-ready label until gates are evidenced.

## Strategic decision
Do **not** launch all sparks. Finish orchestration deployment and data-contract integrity, then parallelize on independent sources, measurements and falsification. Deliver a reproducible first vertical-slice report before broadening the entity graph. Preserve all research outputs but allow only verified facts to enter automated decisions.
