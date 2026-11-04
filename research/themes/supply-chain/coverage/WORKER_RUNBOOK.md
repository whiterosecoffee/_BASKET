# B19 coverage worker contract and runbook

## Identity and ownership
Spark B19; worker issue #21, branch `work/21-underrepresented-ticker-coverage`, draft PR #23; parent B00. Exclusive paths for this worker: `research/themes/supply-chain/coverage/underrepresented-2026-10-17.json`, `check_coverage.py`, `test_check_coverage.py`, and this new runbook. Read PR #18 registry, B00 contracts and B03/B05 evidence only. Prohibited: `orchestration/**`, `schemas/**`, `tickers/**`, `engines/relationships/**`, `tests/integration/**`, `.github/workflows/**` and all existing PR #18 files.

## Objective and output
Maintain a research-only expansion inventory that identifies potential missing entities and economic segments without claiming canonical registration, market share, revenue or live prices. B00 uses the catalog for identity and prioritization; B19 #17 uses it for research reconciliation; B03/B05 receive verified source and relationship proposals only after review. Candidate JSON has local research schema `basket.b19-underrepresented-coverage@1`; shared contracts stay with B00.

## Discovery and deterministic pipeline
1. **Discover:** Read current main governance, this issue and PR changed filenames. Refuse overlapping writes.
2. **Acquire:** Read the complete B19 PR #18 registry at a pinned SHA and collect dated publisher evidence.
3. **Normalize:** Distinguish listed issuer vs private entity vs ETF, ticker aliases and ADRs. Keep original currency/FX basis for financial facts; never fabricate it.
4. **Verify:** Validate source class and HTTPS link, real publication date and cutoff; mark missing evidence explicitly. A URL is a pointer, not proof its claim has been independently reviewed.
5. **Reconcile:** Compare unique candidate identifiers against baseline IDs; differences are scoped to research registry, not user watchlist.
6. **Calculate:** No current valuations or dollar market shares in this research artifact. If denominator missing, null; do not sum intermediary gross revenue into final spending.
7. **Persist:** Update owned JSON and reference its Git commit plus pinned comparison SHA. Never overwrite historical observations in canonical stores.
8. **Validate:** Run checker and regression tests, with negative cases.
9. **Publish:** Commit to worker branch, draft PR. No merge.
10. **Invalidate:** When registry SHA, company identity, evidence claim/source revision, issuer financial filing or graph contract changes, re-run validation and flag dependent projections for owner review.

Idempotency: candidate ticker + research schema + pinned baseline commit; for evidence use immutable publisher URL + publication date + issuer source ID when known. Repeated identical input must yield the same candidate set. Failed acquisitions remain missing; do not retry infinitely. Source failures are recorded for correction, and partial coverage is not classified as success.

## Commands (from checked-out PR #23)
```bash
python -m unittest discover -s research/themes/supply-chain/coverage -p 'test_check_coverage.py' -v
python research/themes/supply-chain/coverage/check_coverage.py research/themes/supply-chain/coverage/underrepresented-2026-10-17.json
python research/themes/supply-chain/coverage/check_coverage.py research/themes/supply-chain/coverage/underrepresented-2026-10-17.json --registry /path/to/pinned/PR18/tickers.json
```
The optional registry must be the entire original pinned file, not an invented sample. Checker validates structure and explicit declared research-only constraints, **not** web-page truth, corporate identity or financial data.

## Interfaces and failure behavior
Input: B19 expansion JSON and optional PR #18 `mrie-b19-coverage-watchlist@1` registry; stable URL/date/source references. Output: JSON summary of candidate count, sorted IDs, optional baseline count and combined identifiers; exit code 0 only on accepted structure, 1 on evidence/date/duplicate/schema failures. Incomplete corporate identity remains `not_checked`. Source TTD and market-data licensing are B02 responsibilities. Canonical edges are B05; issuer events B03. Recompute upon pinned upstream revision change; no scheduled polling implied.

## QC and acceptance matrix
- Unique research IDs, research-only statuses, valid priorities: checker + negative unit cases; runtime result pending independent execution.
- Evidence HTTPS and real publication dates at/before cutoff: checker + negative unit cases.
- Baseline overlap rejected when supplied: checker + negative unit case.
- Reproducible timestamped issuer financial attribution: **not implemented**; requires B03/B19 #17 source intake.
- Exact-PR-head GitHub CI and domain integration: **not verified**; B01 handoff #52.
- Graph traversal / contracts: **not implemented**; B00 #50 and B05 #51.

## Failure register
1. Original date regex allowed impossible dates. Replaced with calendar parse and cutoff comparison; added tests. Independent B01 test execution remains pending; locally reported test evidence is linked from issue #52.
2. Previous environment failed fetching GitHub raw files for Python execution. Connector reads proved exact GitHub files; no test pass should be inferred from these reads.
3. Broad B19 subtree ownership overlaps PR #18 conceptually; worker writes only exact reserved files. New collisions route to B00.
4. Missing MANH and PAYP identity ambiguity require B00 registry reconciliation (#41).

## Lifecycle and reporting
Canonical vocabulary from WORKER_PROTOCOL: `claimed → building → review → component_verified → integrated → closed`, with `integration_blocked` or `withdrawn` when applicable. This PR is **review / integration_blocked**, not component-verified. Record exact SHA, changed paths, test command/outcome, source class, blockers, handoffs and ONE next action in final `basket.worker_resolution@1` issue comment. B00 verifies before promotion.

## Ranked backlog
P0 retain exact-head **23 domain unit tests** (11 candidate + 12 whole-map) and require B01's independent CI plus complete pinned PR #18/#147 input validation; fix failures. P0 reconcile issuer identities and preserve research-only status. P1 add precise source-review state and capacity/revenue data contracts only after B00 interface decisions. P1 B05 graph read-only MVP, then B01 integration QC. No new planner, worker registry or independent status ontology.

## Whole-basket mapping checks (2026-11-03)
New B19-owned research output: `whole-basket-role-map-2026-11-03.json`. It derives 291 symbol rows from B00 PR #147 `_TICKERS/manifest.json` at `321c93c281aeeb7d63b5d107cca6a320070d5f02` and uses the 19 B19 research pool IDs from PR #18 `registry/pools.json` at `6eab180632d251147d13a073c967dbd3031dfe92`.

The map is a provisional typed role classifier, not an entity master, revenue ledger, verified graph or production capacity feed. Capital managers/holding companies can use cross-cutting roles rather than invented spend-pool participation; funds, indexes, FX, futures and indicators are context only. Suggested symbols do not silently become user-tracked basket members.

Run after checking out the current PR #23 head and retrieving the exact pinned **complete** two input files (e.g. from their PR branch heads):

```bash
python -m unittest discover -s research/themes/supply-chain/coverage -p 'test_check_whole_map.py' -v
python research/themes/supply-chain/coverage/check_whole_map.py \\
  research/themes/supply-chain/coverage/whole-basket-role-map-2026-11-03.json \\
  /path/to/PR147/_TICKERS/manifest.json \\
  /path/to/PR18/research/themes/supply-chain/registry/pools.json \\
  --manifest-revision 321c93c281aeeb7d63b5d107cca6a320070d5f02 \\
  --pool-revision 6eab180632d251147d13a073c967dbd3031dfe92
```

Checker requires explicit revision strings matching the pinned map references, rejects lost/duplicate symbols, unknown pools, stale summary counts, illegal promotion of unverified roles to contracts/financial values, and nonissuer-as-issuer errors. It does **not** independently confirm that external file bytes came from those SHAs; B01 must retrieve them and independently verify commit/content fingerprints. A successful check proves structural integrity only. Upstream manifest/pool revisions trigger an incremental remap/diff, not silent reuse of stale classifications.

Remaining acceptance: B01 execute actual Python suite and exact-head workflow; B19 #17 import independently sourced buyer-purpose dollar pools with identifiable competing vendors, procurement status, sources, calendar periods, unique payer transactions, supplier tier paths and unknown budgets explicitly null; B05 builds verified relationships; B00 owns canonical identity and deployment. Dollar coverage remains unmeasured; 291/291 rows alone is not majority financial coverage.

## Conversation intelligence retained — buyer-dollar competition and whole-basket mapping (2026-11-03)

**Controlling user decisions.** The basket is the complete *user-tracked* ticker list. Additions are suggestions, never silent constituents. A revenue pool answers **who competes for which buyer dollars, for what product/contract, during which period?** The same organization can simultaneously be a buyer in one pool and a competing supplier in another. The first useful deliverable is low-resolution coverage of the entire tracked basket with specific research instructions, not unsupported numerical allocation; deeper financial mapping is a separate source-backed workflow.

**Problem → mechanism → application → test → destination**

1. **Buyer-purpose pools rather than sector-only lists (DBC; economic input-output / supply-chain accounting analogy).** A sector name such as "semiconductors" groups suppliers but does not identify the payer's actual budget, product alternatives or procurement event. Define a pool by \`buyer_or_cohort_id × spend_purpose × product_scope × geography × reporting_period × accounting_status\`; record qualified competitors, chosen supplier, internal-build alternative, contract/event IDs and an explicit unknown fraction. Example: MSFT accelerators and networking competed for by NVDA, AMD and internally developed chips, with MSFT's later cloud customers forming a *different* buyer pool. B19 #17 owns provisional pool research; B00 #20/#50 owns contract definitions; B05 #51 owns verified edge queries. **Falsifier:** a vendor listed as "competing" has no qualified or plausible product for the particular procurement period. Attributable vendor share is **null** if the source-backed matching buyer-dollar denominator is unavailable. The existing 19 B19 draft pool IDs are *topic taxonomy*, not yet completed buyer-budget records; do not silently redefine them.

2. **Flow conservation and retained value (input-output accounting, DBC, PROV).** A $1 customer payment can appear as cloud revenue, a cloud purchase of accelerators, hardware supplier revenue, foundry spending and equipment vendor revenue in different periods. These are distinct income/cost observations but not additive final demand. Model unique \`economic_transaction_id\`, payer, payee, pool, accounting state (announced/signed/delivered/recognized/paid), fiscal period, amount/currency/FX, supplier tier and source. Trace \`payer → immediate seller → upstream purchases\`, preserving allocation and unknown gaps. Keep equity, loan principal, guarantees and backlogs separate from recognized sales. **Counterexamples:** summing MSFT capex + NVDA reported sales + TSM foundry revenue as three AI market sizes; adding SFTBY's fund interest and parent look-through; calling Exol's minimum contract value realized SYM revenue. **Test:** repeat a supplier path or ownership loop and prove no duplicated originating payer dollars; mismatched period/FX fails closed. B19 #17 research reconciliations, B05 #51 graph, B01 #52 adversarial QC.

3. **Orthogonal universe, roles and evidence (MOD; CQRS/projection analogy; PIT).** The B00 #146 PR #147 291-symbol \`_TICKERS\` draft tracks market instruments and watchlist membership. B19's \`whole-basket-role-map-2026-11-03.json\` is a *read-only research projection* over that pinned manifest and B19 #17's 19-topic pool list: 291 unique symbols, 198 equity/receipt-like provisionally classified issuers, 93 funds/indexes/futures/other context, 278 deduplicated pool memberships. These counts establish mapping structure, **not** source-verified counterparty edges, revenue share, production capacity, majority spend coverage, canonical identity or migration. Holding/finance entities such as SFTBY, APO, BN and KKR have cross-cutting capital roles even if they do not sell within a topic pool. **Counterexample:** treating QQQ/SMH as issuer-revenue entities or mistaking 42 names absent from PR #18's 68-ID research registry as missing from the user's own watchlist. B00 retains instrument/security identity and folder ownership; B19 owns the derived role map; B05 alone promotes sourced edges.

4. **Temporal, capacity and competitive bottlenecks (PIT, FALS, EVS, REPRO).** Separate issuer statements from filings and third-party speculation; keep observed, first-available, effective, period-end and ingested dates with corrections. For every capacity figure distinguish proposed, reserved, under-construction, qualified, energized, deployed and utilized, including physical unit, process generation, geography and expected completion. Map bottleneck migration rather than assuming a permanent constraint: HBM/packaging yields, fiber and power can gate accelerator delivery; deployment labor, robot reliability, data collection and economic ROI can gate downstream commercialization. **Falsifier:** alternate supplier qualifies at scale or released capacity eliminates scarcity without loss of demand. **Tests:** pre-announcement as-of queries cannot see contracts; 702 MW proposed generation cannot appear as currently energized output; advertised robot fleets cannot substitute for paid autonomous operating hours. This requires B03 issuer events, B05 graph, B02 TTD where temporal observations apply and B01 checks.

**Lowest-complexity implementation choice.** Keep versioned source evidence and research projections in their existing owned locations. Reuse B00's proposed \`architecture/ECONOMIC_FLOW_GRAPH.md\` (PR #22), \`TICKER_FIRST_RESEARCH_ARCHITECTURE.md\` (PR #43), B19 #17's registry and the existing issue-backed orchestrator; do **not** introduce a separate graph database, event scheduler, canonical store or new sector schema to make research-only mappings appear functional. Advanced graph storage may be considered only after measured query/scale constraints justify it.

**Research method and black-box boundaries.** For each tracked identifier: (1) validate security identity and issuer/economic role; (2) identify buyer spending purpose and qualified alternatives; (3) source contracts, counterparties, amounts and statuses from primary filings/IR; (4) reconcile final payer spending, tier-1 supplier capture, tier-2+ upstream costs and retained margins, preserving unknown amounts; (5) measure qualified physical capacity and potential substitutions; (6) validate period consistency, evidence availability, unique transaction keys, denominator type and revisions; (7) persist only owner-approved records and recompute impacted projections when source revision or input hash changes. B19 candidate/role maps have no entitlement to mutate B05 relationships or B03 events. The input contract is the pinned B00 instrument manifest + B19 pool topics + source references; output is provisional roles, explicit missing-evidence gaps and research priority, never asserted current valuation.

**Failure lessons and corrections (POST; IDEM).**
- Initial 42-candidate comparison was against PR #18's research registry, **not** the user's basket. Correct comparison with B00 PR #147 proved 27/42 already represented and 15 still absent; across 72 distinct public-symbol research prospects 32 lacked scope markers. B00 #146 owns any additions and must verify ticker/venue/issuer type. Avoid changing universe semantics midstream without naming the denominator.
- First role-map summary had stale semiconductor count (41 vs row-derived 42) and duplicate \`LSCC\` membership; row-derived deduplication made 278 memberships. Always derive summary totals from the same unique row memberships and fail if fixtures diverge.
- Standard \`Validate BASKET data\` CI can pass while never discovering B19's checker modules. Prior commentary asserted 23 local cases passed; independent CI of those 23 and complete input SHA-to-byte verification remain unproven until B01 executes those exact tests. Never use generic green CI as domain acceptance. The checker compares supplied PR revision identifiers but **does not cryptographically prove** downloaded input bytes belong to them.

**Acceptance boundary and next research work.** Structural completeness means each of the pinned 291 tracked symbols appears once and each issuer-like row has a non-promoted provisional role. Economic completeness is measured *per buyer-defined pool*, with independent known-dollar coverage at each supplier tier and remaining unknown denominator explicitly separated. A >50% source-supported mapped-dollar fraction was proposed as a QA gate, **not** a user-approved definition of a pool or proof of whole-market majority. All 19 topic pools remain financially unmeasured in PR #18 until sourced entries arrive. Prioritize a single buyer-dollar competition pilot (MSFT procurement → NVDA/AMD/custom alternatives → foundry/HBM/packaging), then repeat the method across all pools via existing B19 #17 and B05/B01 contracts. No projected competitor dollar shares should be invented.

**Conversation quality review, not a measured performance metric.** Qualitative 0–5 assessment by dimension: objective control 4, execution conversion 4, reuse 4, ownership 5, verification 3, dependencies 4, resource efficiency 3, knowledge retention 3 before this synthesis, handoff quality 4, closure discipline 3. Total **37/50 (74%)** as reviewer judgment only. Most consequential corrections: verify "missing" against the named universe; recompute/validate row aggregates; require domain-specific independent CI before component-complete claims. No token savings or task-duration improvement is asserted. Existing handoff destinations #17, #50, #51, #52 and #146 suffice; create no additional tracking issue.
