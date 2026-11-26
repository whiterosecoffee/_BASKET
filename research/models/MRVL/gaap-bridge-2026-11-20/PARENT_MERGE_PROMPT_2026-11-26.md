Merge this handoff into the existing LITE–Marvell parent conversation. Reconcile against newer verified work, preserve useful corrections and evidence, and continue the smallest actionable task. Do not create a parallel merger model, duplicate ingestion, overwrite another owner’s files, or merge Git branches without explicit authorization.

PURPOSE
Maintain one analysis connecting customer programs → qualified production → shipments/pricing → revenue by stream → margins/cash → compensation, financing and dilution → standalone and combined EPS → valuation. Keep standalone MRVL, LITE and post-close combined economics separately addressable.

READ EXISTING WORK FIRST
Repository: whiterosecoffee/_BASKET.
Original merger owner: issue #189, draft PR #191; research/models/mrvl_lite/**.
This session’s complementary work: issue #290, draft PR #292.
Branch: work/290-mrvl-gaap-calendar-2028.
Verified research revision before this handoff: ed48cc1d8dd6139c04eb37dad8ffa6113fe4a8e4.
Directory: research/models/MRVL/gaap-bridge-2026-11-20/
Read AGENTS.md, state.json, feature-design.md, REPORT.md, inputs.json, results.json, horizon-2026-2030.json, streams-partnerships-stress-2026-11-20.json and moat-method-pattern-review-2026-11-21.md.

PR #292 is draft and unmerged. Arithmetic, deterministic replay and remote file readback were checked; independent financial acceptance and current-head CI were not established. These are research artifacts, not a live feed.

IMPORTANT CORRECTIONS
• Retrieved November 2 deal terms specify 4.5 MRVL shares per LITE share, correcting the earlier 5.5 assumption. Expected closing was first-half calendar 2028, subject to approvals. Reverify current terms.
• Celestial AI is distinct from Celestica (ticker CLS). Do not treat “CLS” as an acquired Celestial AI ticker.
• The prior FY2029 MRVL EPS conflict ($12.69 versus $7.25) was partly a vintage mismatch: MRTNZ explicitly dated $7.25 to July 30, while November aggregates showed approximately $12.60–$12.73. This does not resolve diluted/basic or standalone/deal-inclusive forecast treatment.
• FY2029 ends around January 2029 and mostly covers calendar 2028. Exact calendar earnings require monthly/quarterly net income and calendar-weighted shares; annual EPS proration is not exact.
• Historical price reference: $125.75, November 20, 2026 at 19:59 ET. Never present it as current.

FORWARD EARNINGS EVIDENCE — HISTORICAL ESTIMATE PANEL
One consistent November 17 FMP/DeltaScreener vintage:
Fiscal year | Mostly calendar | Adjusted EPS | YoY | P/E at historical $125.75
FY2027      | 2026            | $4.21        | 48.2% | 29.9x
FY2028      | 2027            | $7.28        | 72.9% | 17.3x
FY2029      | 2028            | $12.51       | 71.8% | 10.1x
FY2030      | 2029            | $18.99       | 51.8% | 6.6x
FY2031      | 2030            | $28.95       | 52.4% | 4.3x

Cumulative annual EPS growth from FY2027’s $4.21: +72.9%, +197.1%, +351.1%, +587.6% by fiscal years ending approximately January 2028/2029/2030/2031. These are forecast-dependent earnings increases, not promised share-price returns. Future March full-year reporting windows were inferred, not announced. December 1, 2026 was the announced next quarterly report. Refresh estimates before current valuation.

GAAP BRIDGE — THE MOST USEFUL ADDITION
Reproduced issuer Q2 FY2027 GAAP net income $308.0M from adjusted $865.9M, and H1 GAAP $342.5M from adjusted $1,583.9M, using signed adjustments.
Q3 guidance bridge: $1.10 adjusted EPS − $0.34 SBC − $0.21 amortization + $0.03 tax effects − $0.05 other = $0.53 GAAP.
Keep ordinary cash R&D, depreciation and interest already included in adjusted earnings; do not subtract them twice.

The filing scheduled existing acquisition amortization at $292.7M FY2028 and $139.6M FY2029. However, $1.297B of indefinite-lived acquired development assets could begin amortizing at production, with expected 6–13-year lives. Runoff alone is not a complete future expense schedule.

Separate conditional reference model used adjusted EPS $7.37/$12.60 and revenue $19.84B/$31.76B for FY2028/FY2029. Assumptions: diluted shares 950M/980M, SBC 10% of revenue, adjusted-tax reconstruction 11%, GAAP tax 18%, additional development-asset amortization $162.125M/year and other exclusions $100M/year. Outputs: approximately $4.60/$8.62 modeled GAAP EPS, or 27.3x/14.6x at the historical reference price.
These are sensitivities, not issuer guidance or verified consensus GAAP. Do not silently combine their input vintage with the EPS panel above.

GROWTH ENGINES AND TAM
October investor-day FY2031 midpoint revenue targets:
• Interconnect $37.5B against stated ~$65B TAM.
• Custom silicon $30B against ~$235B TAM.
• Switching/storage $10B against ~$85B TAM.
• Communications/other $2.5B against ~$15B TAM.
Total ~$80B revenue against ~$400B TAM. Management targets, not booked revenue. Interconnect implies roughly 58% share if category boundaries align; this is a key execution hurdle.
Long-term adjusted targets: gross margin 56–59%, operating margin 44–46%, EPS >$30 FY2031. Do not translate these directly into GAAP or combined-company outcomes.

PARTNERSHIPS AND MOAT
• Google: signed custom-silicon agreement spanning TPU-adjacent inference, memory, storage and networking. $120B is discretionary-purchase-linked warrant milestones through FY2033, not guaranteed backlog; potential warrant shares approach 59M.
• AWS: five-year multi-generation custom AI/connectivity agreement; no disclosed guaranteed annual revenue.
• NVIDIA: NVLink Fusion-compatible custom silicon/scale-up, photonics and AI-RAN. $2B investment is financing, not sales.
• Celestial AI: historical issuer expectation of initial revenue in second-half FY2028, $500M annualized exiting FY2028 and $1B exiting FY2029. Exit rates are not annual revenue.
• Proposed Lumentum combination: lasers/transceivers/optical switching could strengthen integrated solutions. Combined $550B TAM overlaps standalone $400B; do not add them.

Moat assessment: strongest in specialized connectivity IP, customer qualification and embedded designs; less assured in custom programs exposed to large-buyer bargaining and generational rebids. Watch ASP declines, yield/packaging costs, development-cost recovery, SBC and customer insourcing. Customer-specific designs can also leave Marvell unable to resell a canceled product.
Track gross-profit dollars, operating leverage, cash conversion and EPS per diluted share rather than treating revenue growth as margin protection.

STRESS EVIDENCE
FY2029 conditional standalone GAAP-like reference:
• Reference: EPS $8.62.
• Revenue 20% below reference, 5% extra shares: ~$5.67.
• Revenue 40% below reference, another five points of operating-margin pressure on remaining revenue, 10% extra shares: ~$2.28.
Assumed 50% decremental pretax margin and 18% tax; existing SBC/amortization retained. No scenario probabilities. At $31.76B revenue, each operating-margin point is ~$317.6M pretax or ~$0.266 EPS under those tax/share assumptions.

PLACEMENT AND NEXT ACTION
Existing _PATTERNS branch save/mrvl-lite-b04-189 contains _OBJECTS/_MRVL_LITE. Its preserved component receipt pins 97f03fab79da52da6664be655bea6ffc7b7a0ecb; canonical registration and receiver acceptance were pending at inspection. Reconcile live registry/owner status before changes. Link this complementary research into that component rather than building another MRVL engine.

Use source-pinned accounting reconciliation, segment unit economics, switching-cost/buyer-power analysis, point-in-time estimate tracking and deterministic replay. Apply Microsoft-style bounded stories, design review and decision records; engineering checks do not certify financial assumptions.

Continue with the combined earnings bridge: same-period MRVL/LITE revenue and net income, stream-specific margins, actual diluted share classes, closing-date weights, development costs, purchase accounting, SBC, taxes and realized synergies. Do not add company EPS directly or use approximate ownership as an exact denominator. Preserve unknowns when disclosures do not support a split. Keep market acquisition with existing FETCH and report any unacknowledged refresh.

Return a concise reconciliation: retained insights, superseded inputs, source/basis conflicts, current verified EPS/multiples, and ONE next action. Do not claim this parent has received or accepted the handoff until it actually reads it.
