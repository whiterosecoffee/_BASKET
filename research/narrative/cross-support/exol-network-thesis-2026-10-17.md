# Strategic cross-support: Exol and AI-RAN
Research specification v1; B21 issue #37, receiving archival handoff #27.
Branch: work/37-cross-support-evidence. Research as-of: 2026-10-17 America/New_York; retrieved 2026-10-18 UTC.
Status: source-reviewed research, not canonical graph, engine integration, current valuation or calibrated forecast.

## Thesis and decision
**Hypothesis H0:** linked capital providers, operators and technology suppliers can reduce qualification, integration and commercialization friction, increasing opportunities for other participants. The investable result depends on retained incremental profit after financing, utilization, depreciation and capital costs. Connectedness alone supplies neither protection against macro losses nor a measured partnership probability.

The strongest documented path here is SoftBank Group/Symbotic funding and systems access into GreenBox/Exol, followed by Exol selecting Manhattan execution software. NVIDIA/SoftBank Corp. and NVIDIA/Nokia/T-Mobile provide a separate technology reference case. These are overlapping networks, not one verified end-to-end commercial contract. Common dependencies can amplify correlated losses as readily as create support.

## Provenance and temporal policy
S1–S5 below are primary company publications; their existence/content was retrieved, but operating performance and economics are **company statements**, not independently audited observations. Dates are publication dates with day precision; exact first-available times and transaction completion times remain null unless expressly described. observed_at/ingested_at have date precision 2026-10-18 UTC; exact times are null. period_end is not applicable to announcement records. No FX conversion: cited amounts are USD-native.

Historical announcement truth does not expire merely with age. Current ownership, funding, deployment and revenue status are **unverified_current** until refreshed from filings or counterparty disclosures. No record is qualified for live financial computation; numeric scenarios inherit the earliest stale/unknown dependency. On a new source or contradiction, append a dated revision with a distinct ID; never silently replace the original statement.

| ID | Primary source / publication date | Source-reviewed content and limits |
|---|---|---|
| S1 | [SoftBank Group and Symbotic, 2023-07-24](https://group.softbank/en/news/press/20230724) | Announced GreenBox Systems LLC, 65%/35% ownership at formation; approximately $7.5B systems purchase contract over six years starting FY2024; initial $100M pro-rata capital. Current paid amounts and ownership not established by this historical release. |
| S2 | [Manhattan Associates, 2026-05-14](https://www.manh.com/about-us/newsroom/press-releases/exol-announces-partnership-manhattan-associates-supply-chain-execution) | Exol selected Active WM/TM as core execution platforms. Fee, binding minimum, recognized revenue and full rollout not disclosed. Describes $7.5B backing/commitment; do not reinterpret as fully funded equity. |
| S3 | [NVIDIA and SoftBank Corp., 2024-11-12](https://nvidianews.nvidia.com/news/nvidia-and-softbank-accelerate-japans-journey-to-global-ai-powerhouse) | Reports concurrent 5G and AI inference outdoor trial; plans for Blackwell/Grace Blackwell and marketplace. This counterparty is SoftBank Corp., not automatically SoftBank Group parent. Economics are promotional estimates, not realized returns. |
| S4 | [NVIDIA/Nokia, 2025-10-28](https://nvidianews.nvidia.com/news/nvidia-nokia-ai-telecommunications) | Strategic AI-RAN product integration, planned $1B NVIDIA Nokia investment subject to closing conditions; T-Mobile trials expected in 2026. Closing not verified by this announcement. |
| S5 | [NVIDIA/T-Mobile, 2026-03-16](https://nvidianews.nvidia.com/news/nvidia-t-mobile-and-partners-integrate-physical-ai-applications-on-ai-ran-ready-infrastructure) | Reports T-Mobile pilot with Nokia anyRAN and NVIDIA infrastructure plus physical-AI developer demonstrations. Pilot evidence does not establish nationwide paid deployment or Exol demand. |

Identity bridge: the distributed S2 issuer release identifies GreenBox Systems LLC d/b/a Exol ([issuer release syndicated by Yahoo](https://finance.yahoo.com/sectors/technology/articles/exol-announces-strategic-partnership-manhattan-123000133.html)). This is an issuer statement carried by a third party, not independent corroboration. Legal continuity/current ownership still requires registry/filing confirmation before B05 canonical promotion. The first-party S2 page describes both a California site and an operational Atlanta facility while its boilerplate calls Atlanta its first facility; site counts/status require reconciliation rather than treating all six as operating.

## Exol: commercial and economic chain
**Company statements (S1/S2):** SoftBank Group and Symbotic established the venture; Symbotic technology anchors automation; Manhattan was selected for warehouse and transport execution. The topology demonstrates capital plus hardware plus execution software, without proving that the capital relationship caused Manhattan's selection.

Direct support: the systems contract creates a potential order-to-installation path for Symbotic; software selection creates a commercial opportunity for Manhattan. Indirect support: access to shared automated capacity may let customers adopt automation without buying their own entire system. Second-order support (H1): more throughput and deployed robots may create additional simulation, model training, inference, networking and endpoint compute demand. Provider, volume and incremental spend remain unknown.

Capital-to-profit waterfall (methodology, not computed results):
1. Separate outside equity, drawn debt and customer payments into Exol; initial announced funding is not proof of subsequent cash settlement.
2. Track Exol orders, deposits, system delivery/acceptance and Symbotic revenue recognition separately. Symbotic's equity contribution and supplier receipts are different cash legs.
3. Track Exol's Manhattan subscription/implementation obligation, go-live and recognized supplier revenue by period; no contract value is available here.
4. Track customer fulfillment revenue against labor, property, power, transport, software, maintenance, depreciation and financing burden.
5. For each beneficiary compute conditional incremental NOPAT = incremental EBIT × (1 − applicable tax rate); incremental economic profit = incremental NOPAT − WACC × average incremental invested capital. Separate unlevered economic profit from equity cash flow after debt service. No values are computed without attributable margins/capital.
6. Reconcile parent economic entitlement through current legal ownership, fees, debt, minority interests and tax; cash invested is not newly created NAV.

S1's expected recurring software/parts/services opportunity depends on eventual deployment; it is not an additional present cash receipt. Warrants linked to installation payments create conditional dilution/economic incentives, not free financing. Initial announced $100M and $7.5B systems contract must not be summed as investment or revenue.

## Relationship-derived opportunity and falsification ledger
All H rows are **uncalibrated hypotheses/unconfirmed opportunities**. Their effective/available dates are null; analyst registration date is 2026-10-18 UTC. source_ids denote context, not proof of the proposed commercial edge. Missing disclosure means unknown, not falsified. An explicit alternative selection falsifies only the corresponding provider claim for that scope/time.

| ID / source_ids | Proposed support / beneficiary | Mechanism and measurable milestone | Alternative / falsifier | Accounting key |
|---|---|---|---|---|
| H1 / S1,S2 | Exol -> NVIDIA training/simulation/inference | Integrated robot/warehouse data may create workloads; require named NVIDIA product, buyer, paid deployment and workload attribution | CPU/classical optimization, another accelerator, or pre-existing embedded compute handles demand; named alternative weakens NVIDIA-specific claim | EXOL-COMPUTE/project/workload/period |
| H2 / S1,S3,S4 | NVIDIA-related financing or strategic partnership -> Exol | Familiar partners may shorten diligence; require signed terms, financing provider, recourse and funded cash | Independent procurement/financing, no strategic discount, or explicit rejection; common investor alone is insufficient | EXOL-FUND/instrument/tranche |
| H3 / S1,S2 | Exol -> CoreWeave GPU hosting | Batch training/simulation could be outsourced; require named capacity agreement and incremental usage | Hyperscaler, owned infrastructure or other host wins; generic GPU demand does not imply CRWV revenue | EXOL-COMPUTE/same workload; host allocation |
| H4 / S2,S4,S5 | Exol -> Nokia/T-Mobile connectivity/edge | Low latency/mobile coverage may support facility/fleet workloads; require site-specific equipment/carrier selection and paid service | Wired Ethernet, Wi-Fi, private cellular or alternate carrier meets requirements at lower cost | EXOL-NET/site/service/period |
| H5 / S2,S3 | Exol -> Arm endpoint compute | Efficient controllers/robot endpoints might use licensed Arm silicon; require BOM/SoC confirmation and royalty-bearing shipments | x86, RISC-V or existing processors; Arm-based product does not reveal royalty rate or incremental royalties | EXOL-BOM/SoC/units/period |
| H6 / S1–S5 | Existing ties -> partner-selection advantage | Shared interfaces, proven deployment and references may lower bid/integration cost; log qualified bids, wins/losses, time-to-go-live and total cost against matched independent projects | Performance/price explains wins entirely, tied partners lose repeatedly, integration remains costly | SELECTION/project/bid/version |
| H7 / S3–S5 | AI-RAN -> recurring distributed AI revenue | Reusable radio/compute/software integration may raise useful utilization; require paying tenants, billed GPU-hours and radio SLA evidence | Radio priorities, power limits or inadequate paid demand prevent incremental utilization/profit | AIRAN/site/workload/period |

No ledger row asserts Exol has selected NVIDIA, CoreWeave, Nokia, T-Mobile or Arm. Arm IP economics accrue through a licensee/SoC supply chain, not automatically a direct Exol royalty payment.

## AI-RAN reference case and repeatable architectures
**Company statements S3–S5:** SoftBank Corp. supplies a Japan trial/operator reference; NVIDIA supplies compute/software; Nokia supplies radio integration; T-Mobile supplies a separate US network/pilot context. SoftBank Group's capital role in Exol does not make SoftBank Corp. a party to Exol contracts. This is not proof of a single four-party financing arrangement.

**Inference:** shared reference designs and software interfaces can reduce porting and qualification work and provide credible customer references. Two reusable patterns merit testing:
- Fulfillment: capital/service operator + robotic system + WM/TM execution + optional compute/connectivity. Reference reuse requires measured integration cost, deployment time, reliability and customer utilization; optional layers remain unselected.
- Telco edge: radio workloads + GPU compute + orchestration + tenant applications. Reuse requires radio SLA isolation, usable capacity at the relevant times, commercial demand, power/cooling and security. Spare theoretical capacity is not billable utilization.

NVIDIA may gain hardware/software sales, Nokia integration/support revenue and T-Mobile service revenue; each remains subject to actual contracts, recognition and costs. Benefits can compete: on-device Arm compute may substitute for edge/cloud demand; telco inference may substitute for central hosting; existing hardware may absorb new workloads without new GPU purchases. Shared financing and technology exposure can transmit a shock across several holdings.

## Milestones, counterfactuals and review gates
At each relevant issuer quarter and every material contract announcement, B21 reviews:
- M1 legal identity/current ownership and funded capital vs commitments (B05/B03 evidence).
- M2 site opening, customer acceptance, paid throughput/utilization and renewal. Announced area is not operating throughput.
- M3 Manhattan go-live, contracted fees and attributable recognized revenue/margin, where disclosed.
- M4 each optional provider decision, contract scope, purchase price, delivered units/usage and source.
- M5 supplier incremental EBIT, maintenance/growth capex, working capital and capital charge; label attribution unknown if company reporting cannot isolate it.
- M6 AI-RAN pilot -> contracted rollout -> live paying tenant -> positive incremental economic profit with radio SLA maintained.

These are event-driven review triggers, not an implemented scheduler. Exol's May 2026 planned openings over the following 12 months imply a May 2027 review window, not guaranteed opening dates. A delay weakens rollout assumptions; it does not prove the company has failed.

To test H6, prospectively record eligible projects before supplier selection; compare related vs unrelated bids controlling for workload, geography, scale, reliability and total cost. Include losses, procurement constraints and subsidies; prohibit selecting only successful references. No causal coefficient, win probability or investment return follows from this small set of press releases.

Strong falsifiers for the broad economic thesis: connected projects repeatedly earn below capital cost despite deployment; related financing only shifts losses between investors; customer willingness to pay does not cover operations/capital; supposed platform reuse does not reduce integration burden. Conversely, supplier selection alone supports a relationship claim, not the full profit thesis.

## Double-counting controls
- Use legal counterparty + project + instrument/invoice + delivery period as economic keys; retain revisions and gross cash legs.
- Count ultimate customer fulfillment spending once as final demand. Exol-to-Symbotic/Manhattan/hosting payments are intermediate supplier revenues, not additional independent final demand.
- Keep announced commitments, paid capital, backlog, revenue, cash receipts and profit in separate measures. S2's $7.5B wording cannot create a second $7.5B pool alongside S1.
- Parent ownership value is a look-through claim on the business, not additive to a separately counted full enterprise value. Apply attributable ownership only after legal/fund/financing reconciliation.
- A GPU purchase and cloud rental can both be real transactions but cannot both represent Exol buying the same compute asset. Hosting includes hardware depreciation/financing; do not add supplier revenue as hosting margin.
- NVIDIA investment in Nokia is capital, not Nokia product revenue; planned investment is not funded cash. Arm license fees/royalties are not the full chip selling price.
- Strategic capital can fund vendor purchases; trace recycling, customer subsidy and related-party economics before calling it independent organic demand.
- Original 12/24/36/60-month return assumptions remain **unvalidated historical scenarios**. Their numeric ranges were not supplied in #27 or accessible source material; do not reconstruct them. No price target, probability or fair-value output is authorized by this artifact.

## Existing framework and remaining owners
Read main engines/narrative/engine.py: it validates numeric, unit-bearing claim records and has CRWV/SFTBY-specific derivations. This qualitative relationship ledger is intentionally not passed off as an ingested numeric record. Extending that engine is a separate B21 task requiring contract/QC work, not a reason to modify schemas here. T-006 remains the distinct CoreWeave/OpenAI/Anthropic engine-audit objective; this document does not complete it or the B00 PR #25 capital-capture queue seed.

| Owner / existing work | Exact receiver boundary and next acceptance |
|---|---|
| B00 #20 / PR #22 | architecture/ECONOMIC_FLOW_GRAPH.md proposal already defines the needed capital/contract/profit distinctions; no duplicate architecture task. B00 #24/PR #25 alone owns queue registration. |
| B03 #12 / PR #14 | tickers/*/events.json and research/events/**: promote only source-supported announcement/trial/selection events, retaining announced vs completed; this case requires targeted intake. |
| B05 #16 and B00 #20 | Existing #16 is OpenAI-specific, not Exol intake. A targeted Exol/AI-RAN edge handoff is required under research/graph/** and canonical relationships after strict contracts/identity reconciliation. No hypothetical supplier edge as confirmed. |
| B19 #17 / PR #18 | research/themes/supply-chain/** already owns supplier-depth/pool reconciliation. Consume this case when quarterly amounts are disclosed; no duplicate revenue-pool framework. |
| B04 #30 / B00 #20 | engines/valuation/**, engines/economics/models/**, research/models/**: #30 is OpenAI-specific; generic economic-profit work remains with B04 under #20 architecture intake. Exol numeric model deferred until margins/capital disclosed. |
| B14 / B16 / B12 / B10 | research/NVDA/**, research/themes/edge/**, research/ARM/**, research/CRWV/**: provider opportunity monitoring only; no named Exol deal means no issuer revenue estimate. |
| B21 #37 | This source-reviewed specification; future ingestion/adversarial engine tests remain separate. |

Research preservation is unblocked. Canonical promotion, automated monitoring, current ownership, realized supplier economics, partner-selection causality and calibrated return claims remain pending with the owners above.

## Attempt and validation record
Repository reads and primary-source review completed. Initial clone endpoint returned HTTP 400; connector retrieval used instead. Initial connector argument-binding errors were corrected using live tool metadata; no branch/file mutation occurred on failed calls. Structural checks cover unique ledger/source IDs, complete table columns, required evidence caveats and a single permitted changed path. These are document checks, not a test of causal truth or runtime integration. Draft PR and exact commit/CI evidence are recorded in worker issue #37.
