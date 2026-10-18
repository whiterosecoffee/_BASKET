# Capital-to-Profit Economic Graph — architecture proposal

Status: **proposed, not implemented**. Owner B00, issue #20. Uses existing B05 relationship, B03 event, B19 supply-chain, B04 valuation, B02 market/FX/TTD, B06 traversal and B21 claims/falsification boundaries. No schema or runtime modification in this PR.

## Mission

Answer: **Who originated capital; who commits it; who deploys it; what is delivered; through which intermediaries is money paid; who earns sustainable incremental economic profit; who bears the financing, utilization and obsolescence risks?** Measure direct and look-through basket exposure without duplicate counting. USD-first, preserving original currency, transaction-date FX and sources.

## Distinct graph nodes

- Legal issuer, security/ADR, subsidiary, SPV, joint venture, managed investment fund, economic investor, ultimate customer, enterprise workload, project/campus and physical capacity tranche.
- Product/technology generation, manufacturing service, packaging, power/cooling infrastructure, network interconnect, distribution channel and royalty-bearing architecture.
- Funding facility and instrument (senior, hybrid, asset-backed, guarantee, prepaid capacity, convertible, unfunded commitment), collateral pool, equity class, valuation mark and realizable liquid asset.
- Demand/revenue pool by end-consumer segment (consumer subscriptions; API usage; enterprise agents; hyperscaler/cloud services; AI-SaaS; public/industrial; robotics/automation; telco/edge; physical AI; research/quantum), with customer gateway and quarter.
- Observations/claims/hypotheses, contract milestones and independent falsifiers are first-class versioned records, not issuer attributes silently interpreted as truth.

## Typed relationships (proposed contract; B05 implementation required)

| Kind | From -> To | Required distinguishing dimensions |
|---|---|---|
| owns_equity / controls / manages_fund | Investor -> issuer/fund | Direct vs indirect; class; percent; voting/economic rights; valuation date; source; pledge status |
| provides_debt / guarantees / pledges_collateral | Provider -> obligor/project | Drawn/unfunded/contingent; facility ceiling vs funded amount; maturity; coupon; collateral; recourse; covenant; priority |
| commits_capital / disburses_capital / recycles_proceeds | Investor -> receiver | Announced/signed/funded/completed; gross vs net; funding date; use of proceeds; parent/fund source |
| purchases_service / leases_capacity | Buyer -> supplier/project | Period; contractual minimum; utilization; cancellation; backlog vs recognized revenue; price; direct end buyer vs intermediary |
| supplies_component / integrates_OEM / manufactures_for | Vendor -> purchaser | Bill-of-material depth; product generation; sourcing alternatives; attribution fraction; design win vs shipment |
| licenses_IP / pays_royalty | Chip designer -> IP owner | Units; ASP basis; effective royalty rate; CSS/core/ISA; design generation and lag |
| builds_capacity / controls_power / distributes_service | Developer -> facility/customer | MW/IT MW, commissioning phases, cooling/power/grid status, throughput, geography, ultimate customer |
| strategic_partner / proposed_partnership | Party -> party | Nonfinancial unless explicit contract; do not infer ownership, exclusivity or guaranteed orders |
| competes_with / substitutes_for | Supplier -> supplier | Qualified switching availability; node/package compatibility; time to qualify; pricing pressure |
| depends_on / bottleneck_for | Economic activity -> input | Physical capacity, financing, delivery, technical qualification, demand, implementation lag |

Do not treat the graph as a single level: many OEMs are *upstream from a cloud or systems integrator*, rather than adjacent to ultimate demand. Multiple routes and allocations per issuer are mandatory.

## Capital versus revenue and profit waterfall

For each unique end-demand pool, quarter and channel:
1. Identify end customer funding source (organic FCF, debt, equity, government etc); track source and whether real final demand or intercompany transfer.
2. Traverse customer gateway (cloud, neocloud, OEM, integration company, telco, channel distributor) to suppliers by actual invoicing relationships.
3. Attribute recognized revenue by unique invoice/service delivery period, separating contracted backlog, prepayments, funded capex, project commitment and reported gross merchandise/transaction flow.
4. Reconcile vendor receipts to vendor COGS, cash conversion, incremental EBIT/FCF, required maintenance and growth capex, opportunity cost, and sustainable ROIC above WACC. Capture **profit retention** rather than equating supplier revenue to value capture.
5. Mark external capital versus circular/strategic funding; retain the cash legs but forbid recirculated funding from creating synthetic new final demand. Do not net unrelated entities by default.
6. Project high-level demand pools only with explicitly sourced assumptions and reconciliation against customers' spending and suppliers' reported revenue. Unknown allocation remains unknown, not a forced 100% split.

## Non-double-counting invariants

- Same economic equity stake reachable through parent and fund must have ONE primary economic ownership key and netlook-through weight; cross holdings and ADR equivalents cannot add new NAV.
- A financing guarantee is contingent credit support, NOT $X cash investment or operating revenue.
- Announced project CAPEX and contracted financing capacity are NOT completed capex, funding, supplier sales, delivered megawatts or earnings.
- Gross ARM ownership value minus associated asset-backed debt should not mark down the fixed debt when ARM market price falls; distinguish company-adjusted net investment value versus gross shares and liability.
- A funded equity tranche at cost affects assets and cash/debt together; cannot simply add full cost to historical NAV, nor count a fund's OpenAI interest and parent OpenAI interest twice.
- Unrealized private-equity valuation is a dated accounting mark/transaction-implied scenario, never a live public quote. Disallow 'IPO perps' becoming confirmed equity prices without trade provenance.
- Purchase obligations are distinct from supplier-recognized revenue and from cash receipts; customer spending traversing tiers cannot count as new end-demand at each tier.
- Public ticker ownership from dated 13F is historical and incomplete for non-13F assets; disposition must not be inferred from absent current disclosure.

## Relevant prototype pathways (hypotheses requiring independent edge sourcing)

- Enterprise/customer -> OpenAI subscriptions/API/agent fees -> cloud/neocloud compute contracts -> systems -> NVDA GPUs/networking, ARM CPU IP royalties, MU memory, AAOI/LITE/COHR optics, TTMI PCBs, AAON cooling, network and energy; allocate only where named counterparties and purchase paths have evidence.
- Investors/bond buyers -> SoftBank parent/Vision Fund and SB Energy -> OpenAI stake / facility and physical data-center projects; distinguish completed equity subscriptions from project-guarantee ceilings and inferred alliances.
- NVIDIA -> ARM as architecture licensee for Grace/Vera CPU design, while ARM competes through its own CPU; neither implies Nvidia equity ownership by SFTBY.
- Customer -> hyperscaler or telco/ISP network -> distributed inference services -> edge power/cooling, network and servers; ordinary connectivity revenue must not automatically be classified as AI service revenue.
- Consumer of physical automation -> system integrator -> robotics hardware, sensing, compute, software; direct software/workflow providers (e.g. enterprise automation) may capture revenue nearer to end customer than component OEMs.
- Bottleneck mapping: semiconductor fabrication, advanced packaging, HBM, transceivers, advanced PCB, power procurement, commissioning, thermal management, fiber/network, enterprise integration and financing availability. Scarcity -> profits only if suppliers retain pricing power after utilization, yields, depreciation and customer bargaining.

## Mandatory provenance and freshness

Every numeric edge observation: stable id and revision, source URL/document+source class, original currency, venue, observed_at, available_at, ingested_at, effective_at, period_end if applicable, date-matched FX pair/rate/source, current validity and TTD. Separate verified observation, issuer statement, third-party claim, modeled scenario, inference, contradicted and unknown. Material derivatives inherit the earliest expired dependency. Persist algorithm/config version, commit and input-manifest SHA-256.

## Analyses the graph must answer

- Breadth and depth of each revenue pool: which entities are paid at N supplier levels; what part is ultimate spending vs intermediary pass-through; identify omitted suppliers and demand.
- Relative profit capture per dollar of outside capital versus valuation, liquidity, dilution and risk; compare ARM royalty versus direct AGI CPU hardware, NVDA platform capture, TTMI/AAOI/AAON production scaling, Intel foundry, SoftBank parent/Fund look-through.
- Scenario propagation: rate/yield change -> financing cost and asset discount -> project timing -> orders -> capacity utilization -> margins -> NAV/LTV/covenants/FCF -> SFTBY price scenarios.
- Interdependency and failure modes: substitution/alternate suppliers; power/packaging bottleneck release; double-exposed capital pools; margin preservation; out-of-cycle sales.
- Trading traversal as **descriptive** price/volume dynamics with walk-forward evidence required before probabilities or trim/rebuy advantage claims.

## Interfaces and ownership handoffs

- **B05**: implement typed, time-bound economic/financing/contract/ownership edges in `engines/relationships/**`, `research/graph/**` and existing canonical ticker relationships; start from ownership handoff #16. Do not loosen strict relationships@1.
- **B19**: revenue pools, customer-gateway, depth-of-sale, issuer-quarter evidence and coverage flags under `research/themes/supply-chain/**`; PR #18 is independent and should not be overwritten.
- **B03**: separately record contract signing, funding completion, capacity milestones, royalties, order and earnings events, without false USD commitment-to-revenue conversion.
- **B04**: SOTP/NAV, consolidated-look-through and funding waterfall math; reconcile gross holdings, debt, collateral, private marks, dilution, rate/FX and scenario assumptions.
- **B02**: historical and live price/FX evidence, provider entitlements, stale/unknown observation states, deterministic snapshot replay.
- **B06**: deterministic scenario/network traversal tied to material graph edges and evidence status; no predictive probabilities without validation.
- **B21**: causal alternatives, claims, issuer incentives, explicit falsification and confidence without invented calibration.
- **B01**: independent negative tests: duplicate invoice, fund look-through, guarantee double counting, stale FX, private mark treated as live, announced versus completed, royalty double counting, collateral liability treatment.

## Acceptance checklist

- [x] Contract proposal explicitly distinguishes investor, operator, intermediary, supplier, end consumer, and retained economic profit.
- [x] Preserves ownership / capital / contract / physical capacity / royalty dimensions without asserting speculative counterparty relationships as facts.
- [x] States NAV, guarantee and supplier-pass-through double counting negative invariants.
- [x] Defines USD-first provenance, source/availability/ingestion and TTD requirements.
- [ ] Owners implement domain contracts with source-verified fixtures, independently verified strict validation and replay.
- [ ] Integrated main CI, reproducible tested outputs and authorized release.

No current quote, balance sheet, private valuation, or transaction size in this design document is asserted as live.


## Worker operating contract — B00-20 (architecture-only, 2026-10-18 review)

**Identity and ownership.** Spark B00, parent orchestrator B00, existing issue #20, branch `work/20-capital-profit-graph`, draft PR #22. This conversation is a bounded architecture-document worker, not a substitute for the separate B00 issue #50. Its **exclusive write permission** is this document only. Read-only inputs: main `AGENTS.md`, `orchestration/sparks.json`, `orchestration/WORKER_PROTOCOL.md`, `schemas/worker-task.v1.json`, `schemas/worker-resolution.v1.json`, issue #50, and B00 PRs #43/#49. Forbidden writes: all other `architecture/**` files, `schemas/**`, `orchestration/**`, `tickers/**`, `engines/**`, `research/**`, `runtime/**`, `tests/**` and `.github/**`. A broad B00 spark grant does not override the narrower issue-specific scope.

**Purpose.** Make design requirements independently consumable by B00 #50, B05 #51 and B01 #52 without inventing new canonical schemas. Success: stable specification, explicit interface invariants, acceptance/failure matrix, no ownership collisions, a linked draft PR and evidence-backed worker resolution. Failure: unsupported source claims, undocumented contract choices, edits outside the one file, asserted implementation or CI without evidence.

**Interface and producers.** This Markdown document is a **proposal**, not a schema or machine-readable API:
- B00 #50 is the producer of the approved typed multigraph/entity identity, segment membership, contracts and as-of query interface. Its consumers are B05 #51 and B01 #52; any approved contract/schema version and migration come from B00 only.
- B05 #51 produces read-only entity-neighborhood, segment-map and payer-to-supplier traversal outputs. Each query must accept stable entity IDs, as-of cutoff, dataset/snapshot identity and verified-only policy; must return sorted edges, edge kind, state, source and temporal evidence, or an explicit missing/incompatible/stale result. The **exact payload schema remains blocked on B00 #50**.
- B19 #17/#21 produces sourced supplier gateways and revenue-pool hypotheses; it does not mutate canonical B05 edges. B03 #12 provides issuer events; B02 #11 provides immutable price/FX observations and replay metadata; B04 #30/B09 #28 consume graph ownership for valuation; B06 consumes deterministic graph+market snapshots.
- B01 #52 must independently test exclusion of future/incomplete edges, duplicate invoice/royalty/capital/ownership flows, invalid share denominators, cycles, changed-source fingerprints and stale inputs. Tests operate on pinned immutable data and the exact approved contract SHA.

**Freshness and provider boundary.** No direct external provider is required to interpret this architecture document. A production economic query inherits observation freshness from B02 and the first-available/source dates from B03/B05/B19. Entitlement failures, unknown publication time, outdated FX, unsupported schema major or unverifiable counterparty edges fail closed; an expired historical fact remains queryable only as historical evidence. Monetary amounts are USD-first while retaining the original transaction currency and dated conversion basis.

**Lifecycle mapping.** `available` = unclaimed planned work (no worker task record); `claimed` = canonical claimed; `implementing` = `building`; `testing` = `building` until verified; `review-ready` = `review`; `integration-blocked` = `integration_blocked`; `integrated` = `integrated`; `retired` = `closed` or `withdrawn` only after B00 records disposition. Do not write these friendly labels into versioned payloads. For resolution use schema's `in_progress`, `component_verified`, `ready_for_integration`, `integration_blocked`, `integrated`, `blocked` or `withdrawn`. Issue #20 is presently a draft-PR review state, not integrated.

## Deterministic handoff workflow and recovery

| Stage | Input/source of truth | Output and validation | Idempotency/retry/checkpoint |
|---|---|---|---|
| Discover | Live main instructions, worker issue, actual PR changed files | Exclusive file list and dependencies | Key = issue #20 + branch head; reread on every material edit |
| Acquire | GitHub primary docs and B00/B05/B19 handoffs | Dated source/reference inventory; missing explicitly tracked | Key = URL + ref SHA; retry transient connector error, never fake absent docs |
| Normalize | Existing terminology and `relationships@1` constraints | Proposed typed edge taxonomy, no incompatible rewrite | Key = architecture document commit; rejected ambiguity remains unresolved |
| Verify | Source class, effective/available/ingested dates, link and scope checks | Evidence/no-lookahead assessment | Key = source revision; conflicting claims persist as conflicted |
| Reconcile | Ownership/fund look-through, financing, invoices, royalties | Double-counting negative invariants | Key = ultimate economic exposure + source obligation + period |
| Calculate | Proposed graph path and USD/FX source metadata | **No values calculated by this worker**; downstream model-only math | Recompute only when relevant source revision, edge contract, FX or model hash changes |
| Persist | Exclusive branch, this Markdown file | Git commit and draft PR revision | Key = branch+file path+content; recover by fetching latest head, no force push |
| Validate | Canonical schema guidance and actual content | Structural assertions, owner-scope audit, source status | Fail if missing headings/unknown claim promoted; rerun at each revision |
| Publish | Draft PR #22 and `basket.worker_resolution@1` comment | Orchestrator-readable evidence and blockers | Append new revision-linked evidence; never call CI green without run |
| Invalidate | Change in source/version/freshness/dependency fingerprints | Requery affected graph and derived NAV/traversal snapshots | Never mutate historical snapshots; append corrections and mark derived state invalid |

**Failure classes / runbook.** F1 conflicting active edits: stop only the disputed file, preserve branch, route to #50. F2 missing schema decision: keep taxonomy illustrative and query result contract blocked. F3 absent market entitlement or stale inputs: return unavailable/stale, not live. F4 duplicative parent-fund/guarantee/capex economics: fail accounting reconciliation, ask B05/B04 owner. F5 source published after `as_of`: exclude from historical replay. F6 missing CI: report `not_run` rather than `pass`. F7 failed fetch/write: refetch actual head before retry, never silently force/rebase. Attempts must retain failed state in PR comments or existing B00 knowledge records; do not create another worker ledger.

**Acceptance matrix.** A1 full economic roles/typed links and downstream consumers: designed in this file; implementation pending. A2 temporal source and USD/TTD controls: designed; provider integration pending B02. A3 non-double-counting invariants: designed; negative fixtures pending B01 #52. A4 deterministic queries and stable entity aliases: specified, actual interface pending B00 #50 and B05 #51. A5 exact SHA, verified tests and repository merge: not yet verified, B00 review required.

**Prioritized nonduplicative improvement backlog.** (1) B00 #50 decide stable entity/segment schema and read-only query input/output with error semantics; (2) B05 #51 implement one bounded graph fixture and deterministic as-of traversal; (3) B01 #52 independently run negative tests; (4) B19 #17/#21 attach payer-to-supplier evidence with coverage gaps; (5) B02 #11 provide pinned USD/FX snapshots; (6) B04/B09 reconcile NAV and B06 add descriptive traversal after contract readiness; (7) B08 #53 deployment only after independently validated snapshot semantics.

**Retirement condition.** B00 acknowledges PR #22 as the source artifact for #50, independently checks changed paths/commit/validation, and either integrates or explicitly supersedes this document. PR #22 remaining draft does not prevent retiring this conversation, but prevents claiming integration.
