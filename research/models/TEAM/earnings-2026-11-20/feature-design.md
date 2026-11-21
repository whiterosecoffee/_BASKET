# Earnings-calendar and fixed-price EPS comparison

Consumer: Nathan assessing TEAM earnings growth versus valuation. Reuse repository B04 guidance and worker protocol; this is research, not a new engine/API or ingestion service.

Input: issuer EPS and report dates, period ends, one dated normalized consensus series, dated USD price, explicit outer-year and GAAP net-margin assumptions. Output: per-fiscal-year EPS, YoY and price/EPS, report-date certainty, plus preserved conditional return scenarios. Formula growth=100*(EPS_t/EPS_previous-1); valid only with positive prior EPS. P/E=reference price/EPS; suppress for nonpositive EPS. Round only presentation, retain input precision.

Method: issuer filings establish actual GAAP/adjusted differences; same-provider consensus avoids spurious revisions. Unknown FY2030 comparable EPS remains null;9.90 is separately labelled20% extrapolation. Earlier GAAP scenario uses revenue*net margin/diluted shares; net margin explicitly includes compensation and tax, and is not a detailed forecast bridge. Return horizons identify first full fiscal-year earnings supporting a chosen P/E, not probabilistic arrival dates. Annual June30 period ends are not August report dates.

Alternatives: primary dated QDD series5.52/6.66/8.25; StockAnalysis5.48/6.70 kept as separate provider view. Sparse FY2030 6.10 is quarantined pending matched-basis reconciliation. No extrapolation is relabelled consensus.

Example: FY28 6.66/5.52-1=20.6522%;134.65/6.66=20.2177x. GAAP FY26 loss has N/M P/E. Risks: consensus changes, thin outer-year cohorts, cash replacing equity compensation, tax differences, dilution, market multiple changes. A future cost bridge is planned in state.json before implementation. Evidence: sources and results in inputs-results.json, current GitHub claim in issue293.
