# MRVL moat, margin protection and session-method review
As of2026-11-21. Existing B04 issue290 / draftPR292. Assessment, not trading instruction.

## Financial judgment
Inference: moat strongest in hard-to-replace high-speed analog/SerDes/DSP IP and qualified designs; conditional in custom XPU programs where buyers own much of the architecture; emerging in integrated optical scale-up. Design embedding supports program retention, but each new generation can be rebid. Customer bargaining power, custom non-portability, price reductions, unrecovered NRE, packaging/foundry costs and technological substitution limit margin protection.
Issuer evidence: August2026 10-Q explains ASIC model lower gross margins, uncertain NRE recovery, customer-specific products not readily sold elsewhere, and ongoing ASP pressure. Q2FY27 reported GAAP/adjusted gross margin53.1/58.9%; Q3 adjusted guidance57.5–58.5%. October investor-day FY31 target56–59% gross and44–46% operating margin is NON-GAAP and assumes scale/OpEx discipline; it is not a GAAP floor.
A useful margin-dollar check: at scenarioFY29 revenue31.76B, one percentage point of operating margin is317.6M pretax or0.2657 EPS at18% tax and980M shares. No new consensus forecast implied.
Sources:
https://investor.marvell.com/sec-filings/all-sec-filings/content/0001835632-26-000025/mrvl-20260801.htm
https://investor.marvell.com/news-events/press-releases/detail/1031/marvell-technology-inc-reports-second-quarter-of-fiscal-year-2027-financial-results
https://investor.marvell.com/_assets/_c8b5c7be7627f26c20be25056bbe4c06/marvell/db/3711/35439/file/marvell-investor-day-2026-presentaion-deck-print-version.pdf

## Session purpose and methods
Purpose: determine whether MRVL's compressed price buys durable future common-share earnings and cash.
Chain: customer program -> qualified design/production -> shipments/price -> stream revenue -> gross-profit dollars -> operating cost -> taxes/SBC/acquisition costs -> diluted EPS and FCF -> valuation.
Methods already used: timestamped issuer/consensus distinction, signed GAAP inverse reconciliations, fiscal/calendar mapping, EPS growth/multiple arithmetic, partnership contract qualification, TAM/category arithmetic and correlated revenue/margin/dilution stresses.
Limits: arithmetic/replay and remote persistence verified; future stream margins, signed backlog, NRE terms, common-share denominator and recurring FCF not fully evidenced; no predictive probabilities, live runtime or independently accepted forward-GAAP estimate.

## Prior-art families and useful additions
- Industrial organization and resource-based moat analysis: switching/requalification costs, scarce IP and buyer power; falsify with rebids/lost sockets or declining contribution per design.
- Segment unit economics and DuPont/ROIC: split volume, ASP, product mix, yield, NRE coverage, R&D, working capital and invested capital. Revenue scale is not economic return.
- Accounting reconciliation/accretion-dilution: preserve signed adjustments and common-share claims; combine MRVL/LITE only with same-period net income, shares and closing weights.
- Point-in-time research/event studies: freeze estimates before each report, attribute revisions, avoid hindsight and exact calendar claims from annual proration.
- Scenario/reverse valuation: test correlated revenue, margin and share shocks; compute what earnings must materialize at an explicit multiple; avoid arbitrary probabilities.
- Engineering contracts/replay: typed inputs/outputs, pinned source and deterministic expected result; do not equate a calculator pass with finance truth.

## Microsoft application
Apply Microsoft Engineering Fundamentals design reviews and ADRs: one bounded user story, explicit alternatives, source-pinned acceptance examples, early async design review, independent semantic review and evidence tied to actual source revision. A suitable first story is 'For one reported quarter, reconcile gross-profit dollars through diluted GAAP EPS and FCF, distinguishing missing stream data.' Success means exact issuer total reconciliation and explicit unknown stream attribution, not fabricated split estimates.
Track source/basis defects, estimate-revision attribution, reconciliation residuals and time-to-verified update. Add only checks addressing concrete failure cases (mixed fiscal periods, stale estimates, duplicate synergy, denominator drift). Microsoft provides engineering practice, not investment validation.
https://github.com/microsoft/code-with-engineering-playbook/blob/main/docs/design/design-reviews/README.md
https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record

## Existing patterns lookup and placement recommendation
Inspected live default Snapshot.json/root AGENTS/Handoff and137 branch names across two pages.
Closest SAME-ISSUER work exists:
_PATTERNS branch save/mrvl-lite-b04-189 atf15340e3d0c3b2e32bceec833e3b3b46e6077cf4, _OBJECTS/_MRVL_LITE. Its durable branch-local receipt mrvl-lite-b04-189-save-20261119.json pins component97f03fab79da52da6664be655bea6ffc7b7a0ecb. Guidance explicitly says preserve original _BASKET B04 owner189. Current state says preserved_research_inputs_unresolved, independent receiver pending, canonical main registration pending. The default root index inspected has no _MRVL_LITE entry. Branch existence therefore does not prove canonical admission.
Recommended: retain current work/290-mrvl-gaap-calendar-2028 and draftPR292 as the concrete implementation; original189/PR191 remains merger owner. Propose linking this standalone/GAAP/margin addendum to the existing _MRVL_LITE component, with reusable method inherited from ticker guidance and financial deltas kept local. Reconcile owner scope and fresh receiver acceptance before any cross-branch consolidation. No wholesale Git merge or new parallel MRVL branch proposed.
Related, not substitutes: codex/mrie-earnings-watch (checkpoint/recovery integration, not a valuation parent); work/libraries-microsoft-agentic-agile exactpublished2f152aacff345767c0895b1ed2cd8a2f508b9563 (story/acceptance workflow); _OBJECTS/_TICKER/Agents.md (data qualification/routing). Reuse their applicable guidance by reference; do not merge unrelated capabilities.
No _PATTERNS writes, registration, receiver execution or merge performed. If canonical owner chooses a standalone ticker sibling, capture it as a planned node first; do not create a general valuation engine until a second issuer demonstrates reusable inputs/outputs.

Next smallest action: one Q3 evidence-to-margin-dollar-to-GAAP-EPS/FCF reconciliation after December1, carrying source-specific unknowns and comparing revisions to the frozen pre-report panel.
