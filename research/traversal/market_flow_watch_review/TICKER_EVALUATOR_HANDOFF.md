# Worker B — Ticker Financial Evaluation & Conditional Entry (B04 receiver plan)

**Source:** B06 issue #155 (read-only planning/handoff), with earlier user-requested extension comment on B04 issue #126. **Receiving owner:** B04 existing issue #126, branch `work/126-etf-forward-valuation`, draft PR #127; no new B04 branch launched by this conversation. B04 must reconcile its issue scope with current main and PR changed files before edits.

## Mission
Rank financially durable U.S.-tradable AI/emerging-technology equities after compression for **separate end-2027 and end-2028 horizons**, with trading entry evidence provided **read-only** by Worker A. Initial universe: NVDA, CRWV, COHR, MRVL, LITE, INTC; add AAOI, CRDO, ALAB and comparable peers. Ranking target is conditional **risk-adjusted share-price appreciation**, not largest drawdown or highest forecast earnings growth.

## Reuse existing engine
B04 ETF-forward valuation prototype #126/PR #127; B02 market/FX; B03 events/issuer filings; B17 composites; B06 vectors; B01 exact-head CI #129; B00 source/data registry arbitration #128 and _TICKERS migration #148. No duplicate market stores, ticker folders or source registries.

## Input/source coverage matrix
Per ticker record:
- UTC quote observed/available timestamps, exchange session, last trade/regular close, FX basis, provider and source provenance.
- GAAP and non-GAAP per-share earnings with diluted share count, fiscal-year labels and calendarization rules; analyst count, consensus dispersion, 7/30/90-day EPS revision deltas where source supports.
- 2026–2028 segment revenue, gross/operating margins, SG&A/R&D, D&A, taxes, debt/interest, maturities, liquidity, SBC and share issuance/buybacks, capex, OCF, FCF, EV and cash balances.
- Deal/merger lifecycle; contracted vs billable capacity/backlog when relevant; company claim vs audited observation vs scenario.
- Missing, contradictory, stale, provisional statuses and immutable input-manifest hash. Never assert published estimates without dated source evidence.

## Financial engine: deterministic per-issuer bridge
1. Fiscal and calendar 2027 / 2028 revenue → EBIT → after-interest taxes → diluted EPS; independently reconcile cash flow / FCF and share count. Explicitly distinguish historical reported, current analyst consensus and model assumption.
2. Current 2027/2028 P/E, EV/sales, EV/EBITDA and FCF yield only where well-defined; negative EPS or FCF => N/M, not arbitrary P/E.
3. Break-even 2028 diluted EPS = entry share price / assumed terminal P/E. Multiple contraction 10/20/30/40% requires EPS increase 11.1/25/42.9/66.7% to preserve price *from matching initial earnings baseline*. Stress 0/10/20/30% EPS misses, revenue/margin/dilution/financing sensitivity. For each scenario, show present-to-horizon price return, dividend and trading costs as separately available.
4. Sectors demand different justified multiples. Present conservative/base/expansion bands as explicit assumptions and reverse-implied fundamentals, not peer-derived precision without timestamped peer data.
5. NVDA: margin durability, GPU refresh cadence, hyperscaler/inference demand. CRWV: contracted→active→billable MW, revenues, depreciation, interest, refinance, dilution, cash-flow funding gap. COHR/AAOI/CRDO/ALAB: datacenter interconnect demand and margin scale. MRVL/LITE: stand-alone and close/no-close merger branches, **verify** 4.5 MRVL shares per LITE and model pro-forma share dilution, integration and synergies, prevent double-counting. INTC: products vs foundry capex and external-customer economics.
6. Conditional Pareto ranking for downside, upside, liquidity, leverage, earnings quality and entry validation. No invented forecasts, probabilities, Sharpe or fair-value point estimate when data insufficient.

## Separation of concerns
- B04 writes only under `engines/valuation/etf_forward/**` or other B04-exclusive path after actual PR inspection.
- B06 produces versioned market vectors/new high-low/trigger **read-only**; B04 uses them as an entry gate and never duplicates market traversal logic.
- B02/B03 write their own canonical records. B00 assigns cross-domain schema fields. B01 independently verifies.
- An attractive 2028 model without confirmed floor is labeled `fundamentally_attractive_technical_unconfirmed`; a confirmed rebound without valuation cushion is not labeled undervalued.

## Minimum deliverable
A 9-row source coverage grid, a deterministic testable break-even EPS/multiple stress evaluator (source-gated), separate fiscal/calendar horizon labels, three example pinned fixtures for NVDA, COHR, INTC, and missing-data outputs for CRWV/MRVL/LITE rather than fabricated numbers. Then progressively verify each issuer and model the finance/merger exceptions. Integrate ETF-versus-individual portfolio optimization later, preserving A1–A7 in #126.

## Acceptance
- Correct math and fiscal/calendar conversion, negative EPS and cash flow nulls, forecast vintage consistency, 20% EPS miss / 30% P/E compression sensitivity, dilution reconciliation.
- No leakage from future analyst revisions into past replay; source SHA, observed_at/available_at and full reproducible manifest.
- Merger terms checked from original disclosure; combined vs standalone EPS separated; financing exposure quantified or unavailable.
- B01 exact-head integration tests and observed results. Draft PR only; no merge.
