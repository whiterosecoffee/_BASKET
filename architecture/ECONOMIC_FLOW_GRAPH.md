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
