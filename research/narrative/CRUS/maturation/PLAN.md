# CRUS research maturation plan

Owner B21, issue #188, branch `work/188-crus-research-maturation`.
Baseline main: `b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95`.
Scope: `research/narrative/CRUS/maturation/**` only. Research prototype, not a release.

## Objective and decision boundary

Turn a conversational description of Cirrus Logic into a reproducible assessment of whether incremental chip content, shipments and retained profit can justify the price paid for 2027 and 2028 earnings. Maximize risk-adjusted appreciation as the eventual evaluation objective. Do not equate price compression, AI branding, design interest or buyback authorization with undervaluation or realized profit.

This increment implements evidence readiness and falsification only. B04 retains valuation ownership, B02 observations, B03 canonical issuer facts/events, B05 relationships, B06 traversal, B07 empirical calibration, B01 independent acceptance and B00 contracts/ticker routing. There is no registered CRUS company spark in the inspected catalog. Do not invent one or write `_TICKERS/CRUS` without B00 path assignment. This ticker-specific B21 directory is a research staging location, not a competing canonical ticker store.

## Baseline score: observable conversation execution

Scores are reviewer judgments using the repository WORKER_PROTOCOL weights. They measure review maturity, not stock attractiveness, investment return or calibrated probability. Denominators stay fixed; missing evidence earns no points.

| Dimension | Weight | Before | Evidence and deficiency |
|---|---:|---:|---|
| Scope compliance | 20 | 2 | Read-only repo search/AGENTS read, but no issue, branch or durable research on the initial ticker request |
| Test evidence | 25 | 0 | No executed calculation, adversarial or replay checks |
| Source/provenance | 20 | 12 | Issuer/SEC sources and timestamped secondary quote; no archived input identity, full reconciliation or field-level validity |
| Dependency discipline | 15 | 3 | No cross-owner writes, but no explicit owner work packets |
| Reproducibility | 10 | 2 | Concentration arithmetic shown; no deterministic input manifest or executable replay |
| Reporting clarity | 10 | 7 | Clear product explanation and caveats; repeatedly deferred next steps; incomplete financial scope |
| **Total** | **100** | **26** | Useful explanation; not an operational investment evaluation |

Separate analytical coverage: business mechanism 3/5; primary financial reconciliation 1/5; AI attribution 1/5; 2027/2028 valuation 0/5; market context 1/5; risk/falsification 2/5; economic conclusion remains unavailable. These anchored ordinal ratings prevent strong presentation from masking missing valuation. No total stock score is produced.

Root causes: moving from explanation to recommendation without a frozen evidence boundary; using source links as a substitute for replayable records; omitting the initial worker bootstrap; no explicit fiscal/calendar bridge; describing potential end-market growth without an attributable dollar model. Corrections below target those causes. Do not erase prior uncertain claims or backdate newly obtained evidence.

## Discovery and reuse

- Main `engines/narrative/engine.py`: existing numeric narrative audit with timestamp/TTD validation and CRWV/SFTBY-specific derivations. Read, do not modify. It requires exact timestamps and is not a natural fit for qualitative/date-only CRUS evidence. The new small offline checker is a consumer readiness experiment; it does not replace that engine or add a universal schema.
- B21 PR #38: qualitative sources, mechanisms, alternatives, falsifiers, double-counting and handoff precedent; changed path is disjoint.
- B04 #126 / PR #127: existing company-vs-ETF forward valuation implementation. Consume owner-reviewed outputs after financial normalization; do not build another optimizer.
- Main #173 integration / B00 #148: NVDA-only frozen source resolver and existing B02 `TickerStore` patterns. This does NOT authorize applying an NVDA resolver to CRUS. B00 must generalize routing explicitly.
- B02 #11 and #151 / PR #153: observations/replay and minute-fetch work. Provider data belongs in a durable data plane, daily JSONL partitions, not this public research directory.
- B00 #146 / PR #147: ticker scaffold inspected; CRUS marker absent from the changed-file list. B00 #148 owns migration/routing arbitration.
- Live inspection: 59 open PR changed-file inventories checked, no proposed-directory collision. Active worker count is unknown; PR count is not active worker count. Queue/scopes are historical plans, not completion evidence.

## Planned implementation sequence

| Stage | Priority and owner | Deliverables | Acceptance / dependency | Current disposition |
|---|---|---|---|---|
| 0 Governance and baseline | P0 B21 | New issue/branch, narrow paths, rubric, collision inventory, pinned main | No other owner paths modified; task payload posted | Implemented in this increment |
| 1 Evidence triage | P0 B21; B03 downstream | Dated research snapshot; source class, publication precision, retrieval time, conflicts, missing inputs | Unknown values remain null; historical reports cannot masquerade as current inputs | Implemented as conservative triage; full source reconciliation pending |
| 2 Executable readiness | P0 B21 | `audit.py`, adversarial tests, deterministic report and input/implementation hashes | Future/expired/unknown/conflicted data block; complete synthetic inputs still emit no valuation | Implemented and locally tested; independent CI pending |
| 3 Canonical identity and source normalization | P0 B00/B03/B05 | CRUS home assignment; earnings/10-Q/10-K reconciliation; customer and supply relationships | Correct period, GAAP basis, units, availability; no duplicated canonical stores | Owner handoff required |
| 4 Revenue-to-profit bridge | P1 B04 with B19 evidence | Smartphone/PC/other revenue model; content, units, share, ASP, margin and expense drivers | Sum to issuer total, explain residuals, no AI/non-Apple conflation | Requires stage 3 and attributable evidence |
| 5 2027/2028 valuation | P1 B04 | Fiscal and calendar horizons separately; EPS/FCF, net cash, dilution; reverse valuation and scenario grid | Current quote and dated estimate vintage; full earnings/multiple decomposition; no unsupported target precision | Requires stages 3–4 and B02 data |
| 6 Market and portfolio context | P1 B02/B06/B17 | 200+ completed sessions, low touches, session VWAP, 5/20/60/200 context, QQQ/SPY/semiconductor benchmark | Retain raw observations and quality flags; costs, liquidity and missed-rebound sensitivity | Requires accepted observations; cannot infer signed money flows from volume |
| 7 Independent acceptance and operation | P1 B01/B00; B08 later | Exact-head tests, owner review, integration evidence; event-driven refresh specification | No skipped/empty success; approved merge and green main separately; only then scheduler | No merge or deployment authorized |

Each stage ends with a reusable output and explicit blocker list. Reuse latest accepted owner components before requesting another implementation. Do not pre-create downstream worker branches. Full maturation is not claimed merely because this plan and its checker exist.

## Evidence and model requirements

Collect quarterly and annual issuer statements with accession, URL, period start/end, fiscal year, GAAP/non-GAAP basis, original currency/unit, source/available/observed/ingested times and validity. Reconcile revenue, gross profit, operating expenses, tax, diluted shares, cash, debt, SBC, working capital and cash flow. Preserve date-only publication as date-only; do not fabricate midnight availability. Q1 90% single-customer concentration and an annual 91% Apple statement are different periods and identity evidence, not interchangeable values.

For each product opportunity record: product, buyer, use case, development stage, disclosed design win, production date, shipments, dollar content, recognized revenue, margin and competitive alternatives. Stage order is interest → sample → design win → production → shipment → revenue → retained profit; movement requires evidence. A tape-out proves design completion for fabrication, not production revenue. Customer concentration and product mix are overlapping dimensions: Apple is not identical to smartphone, and non-Apple is not identical to AI.

B04 proposed bridge: revenue by mutually exclusive product/customer cells = units × attach rate × content per unit × realized ASP factor. Reconcile the sum to consolidated revenue with an explicit unknown residual. Incremental operating profit = incremental gross profit − incremental R&D − incremental selling/admin expense. EPS uses net interest, tax and diluted shares; FCF separately uses cash taxes, capex and working-capital movement. Buyback authorization cannot reduce shares until executed; avoid subtracting buyback cash twice. The existing illustrative `0.91×(-5%)+0.09×30%=-1.85%` is a scenario identity, not a forecast and not attributable AI growth.

Separate FY2027/FY2028 from calendar 2027/2028; never relabel fiscal estimates as calendar estimates. Use quarterly bridge where available; otherwise return calendar estimates unavailable. Show trailing, current consensus and analyst scenarios as distinct series. Compare companies on the same accounting basis. A seasonal quarter must not be multiplied by four as an annual forecast.

Valuation sensitivity should separate earnings growth, multiple change, net cash and diluted-share effects. Show break-even implied EPS at the current price under explicit multiples, plus downside if shipments/content/margins disappoint. Rank scenario outputs descriptively; probabilities require B07 point-in-time walk-forward evidence. Add maximum customer exposure, liquidity, cyclicality, estimate dispersion and drawdown to risk review. No total investment score until inputs and weights are defined and tested.

## Prior-art families and concrete applications

| Family | Application | Avoided failure |
|---|---|---|
| Data contracts and design by contract | Required metrics, units, accounting basis and typed failure states at the consumer boundary | Silent substitution of stale or missing values |
| Bitemporal/event-sourced data | Separate reporting period, public availability and local ingestion; append correction vintages | Look-ahead and rewritten history |
| Content-addressed reproducibility | Canonical JSON input hash, implementation hash, pinned Git revision | Unrepeatable conclusions after sources change |
| Stage-gate product commercialization | Require evidence at design, production, shipment and revenue transitions | Treating AI interest as booked growth |
| Driver-based accounting / DuPont-style decomposition | Revenue → gross profit → operating earnings → EPS and FCF | Growth without retained profit; buyback double counting |
| Reverse valuation and sensitivity analysis | Infer earnings required by price under a range of multiples | False single-point fair value |
| Scientific falsification and competing hypotheses | Milestones, alternative explanations and disconfirming observations | Confirmation bias and causal overclaim |
| Walk-forward evaluation / ablation | Compare incremental AI features against simple valuation/sector benchmarks | Attractive but untested risk-adjusted rankings |

## Black-box contract and operational limits

Input: one versioned CRUS research JSON snapshot plus explicit timezone-aware `as_of`. Output: model version, input SHA-256, implementation SHA-256, per-record flags, fixed required-metric gate statuses. Outputs `valuation` and `investment_score` are always null. CLI exit 0 means inputs eligible for owner review; 2 means valid snapshot but research blocked; 1 means invalid input. None means a trade signal or verified source truth.

Research records are manually reviewed observations, not independently verified financial data. The checker uses supplied review states and source references; it cannot authenticate web content. Multiple records for a required metric block pending owner reconciliation rather than picking the newest or most favorable. Unknown availability blocks current use. The snapshot uses historical issuer material, so blocked is the expected correct result.

Publication-date snapshots are versioned JSON; no new market JSONL is created. On revision add a new dated snapshot with predecessor reference; retain old files. Do not silently correct source facts in place. Source extracts here are concise paraphrases, not full third-party content. No live provider, subscription, scheduler or alert is implemented.

## Budget, stopping rules and refresh

Initial implementation estimate: 8,000–12,000 tokens, not metered actual usage. Value: enforce evidence gaps and produce a ready-to-review handoff before paying for broader data/model work. No new paid service. Keep the small checker local until B00/B21 review shows a shared abstraction is warranted. Do not generalize to the whole basket solely because CRUS passes synthetic tests.

Refresh on material earnings, guidance, product production, design loss, acquisition or financing evidence; this is a policy, not an active automation. B02 sets quote TTD by session/consumer contract. B03/B04 invalidate dependent forward assumptions after material disclosures. Maintain immutable old vintages and recompute only affected outputs.

Stop financial publication when a required input is missing, expired, conflicted or not available at the cutoff. Continue independent source collection and owner handoffs. Integration requires independent B01 evidence and B00 review; neither a high maturity score nor this user's implementation authorization permits a merge.
