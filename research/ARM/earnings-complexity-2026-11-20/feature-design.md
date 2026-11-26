# ARM complexity, earnings and valuation — November 20, 2026

## Contract and method
Input: dated issuer results, management outlook, separately dated adjusted-EPS consensus, USD session close and explicit sensitivity assumptions in inputs.json. Output: results.json and this explanation. Parent role and scope are in AGENTS.md/state.json. calculate.py contains the formulas. No forecast probability or operational feed.

## Finding
Increasing complexity benefits Arm through richer IP, higher core count, subsystems and custom silicon adoption. Equity compression can coexist with that growth because the royalty conversion lags design commitments and the valuation already discounts fast earnings growth. The November 20 close was $152.20, down 14.09%; low $150.37 (Massive). These are historical session prices.

Q2 FY27 (September 2026): revenue $1.443B, +27%; license revenue $773M, +50%; royalties $670M, +8%; adjusted EPS $0.52, +33%; GAAP EPS $0.12. Source: results. Licensing is 53.6% of the quarter's revenue. Annualized contract value grew 12%, so a single 50% license-growth quarter cannot simply be compounded. Source: results.

## Complexity transmission
Arm's presentation says royalty scales with core count and illustrates higher per-core pricing with richer CSS. The relationship is contract-specific, not an automatic fee on every extra transistor. CSS supplies integrated, verified CPU/interconnect/system foundations, increasing the value Arm can capture as integration gets harder. More agents and richer systems can expand CPU core demand; actual unit deployment and negotiated rates still govern revenue. Source: presentation, especially royalty-driver slides; filing business model (percentage of chip ASP or fixed per-unit fee).

Management reported data-center royalties doubled and physical-AI royalties rose 50%. However FY26 royalty mix was 78% edge, 14% cloud and 8% physical AI. Source: presentation and results. Do not interpret cloud CPU share as share of all AI spending. GPU/HBM/SSD complexity does not automatically increase Arm's bill.

## Why compression
1. The fastest-growing royalty businesses are smaller than the edge base. Memory-price pressure on phones offsets richer IP. Q3 total royalty growth guidance is low single digits YoY. Source: transcript.
2. Licensing is lumpy and precedes production royalty growth. ACV provides a more normalized check. Source: results.
3. Silicon raises revenue opportunity but changes economics. Management targets up to $2B cumulative AGI CPU sales across FY27-FY28, beginning commercial shipments in FY27 Q4 (Jan-Mar 2027). First-version gross margin is roughly 30-40%, versus around 97% current company gross margin. Source: transcript and results. Hardware revenue must not be treated as royalty profit.
4. Adjusted EPS excludes substantial costs: Q2 $0.52 versus GAAP $0.12; $376M SBC is roughly 26% of revenue. Source: results/filing. This is material to owner economics.
5. Wider semiconductor selling adds valuation pressure. The sector decline is independently reported (sector source); forced liquidations, specific fund selling and SoftBank collateral sales are not established here.

## EPS calendar and valuation
S&P Global consensus displayed by Stock Analysis, last checked November 17: FY26 adjusted actual $1.77; FY27 ending March 31, 2027 $2.27; FY28 ending March 31, 2028 $3.09. These imply about 28% then 36% growth. FY28 spans April 2027-March 2028; it is not calendar 2028. At $152.20 the respective forecast P/Es are about 67x and 49x. No claim these estimates incorporate every November 20 event.

Valuation arithmetic: FY28 EPS $2.50/$3.09/$4.00 means approximately 61x/49x/38x at today's reference close. At 40x those EPS cases imply $100/$123.60/$160; at 50x $125/$154.50/$200. These are unweighted sensitivities, not targets or fair values. An example of EPS growing 36% while P/E moves 80x to 50x produces a 15% stock decline.

## Incremental earnings potential
Assume 1.1B diluted shares, 15% marginal tax and $1B incremental annual royalties. A modeled 70-85% incremental operating margin gives roughly $0.54-$0.66 incremental adjusted EPS. Those margins and tax are assumptions, not issuer guidance.

For $1B chip sales at 30-40% gross margin, after-tax gross profit per share is only $0.23-$0.31 BEFORE incremental opex. This is not EPS guidance and cannot be added to consensus without reconciling what consensus already includes. Avoid counting lost license/royalty revenue twice when direct silicon replaces partner designs.

## Falsifiers, limitations and next action
The strongest evidence would be total royalty acceleration, higher realized royalty per server deployment, successful Jan-Mar deliveries, improving silicon gross margins and EPS estimates rising after costs/dilution. Weaker conversion, persistent edge weakness, higher costs or revisions downward weaken the investment case. Exact ARM-versus-sector attribution and customer-specific royalty contracts remain unknown. Refresh consensus and independently review the draft PR; do not merge without authorization.

Source URLs, dates and classifications are in inputs.json. They are references, not archived verbatim source documents.
