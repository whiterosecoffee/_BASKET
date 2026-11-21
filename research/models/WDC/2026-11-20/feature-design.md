# WDC earnings and competitive-economics research contract

Consumer: Nathan's WDC/STX/SNDK comparison. Reuse B04 issue291 and STX PR296 WDC_COMPARISON; this node adds WDC-specific business and margin evidence. Parent is root AGENTS/B04; no new shared engine or schema.

Input: issuer FY2026 actual adjusted diluted EPS10.22; one ChartMill forward series; separate S&P crosscheck; public price displays; issuer roadmap and competitor announcements. Output: dated annual/cumulative growth table, fixed-price multiples, source-displayed compression, revenue/competition assessment and sensitivity. inputs-results.json retains derived arithmetic and source URLs; no licensed raw provider data.

YoY=EPS_t/EPS_previous-1. Cumulative=EPS_t/issuerFY2026EPS-1. P/E=261.11/EPS. Compression=price/799.87-1. Peak recovery=799.87/price-1. Future periods late June/early July are approximate; report dates are distinct. Do not add annual percentages to produce cumulative growth.

Adjusted EPS excludes SBC and other items; it is not owner earnings or GAAP. Vendor10.19 baseline is preserved as disagreement, not used instead of issuer10.22. ChartMill forward years are never spliced with S&P forecasts. A vendor operating margin above its gross margin is a quality flag, not an accepted financial model. Long-horizon cells remain provisional. Primary guidance supports near-term direction only.

Sensitivity holds annual OpEx1.62B, other expense0.06B, tax17%, diluted shares380M, based on annualized Q2 guidance. Reverse-solve gross margin for vendor EPS; vary margin at FY2028 vendor revenue30.454B. These assumptions are favorable if expenses rise; buybacks/lower tax could improve EPS. Do not call it bear/base/bull probability or price forecast.

Review: recalculate all formulas with independent Python; verify source classes, fiscal labels, denominator, conflicts, price session and absence of canonical writes; read back exact published files. No code test suite needed for documentation and fixed arithmetic. Hosted CI/independent source acceptance are separate. Next: coherent same-cohort revenue-to-GAAP/diluted-EPS bridge, then canonical FETCH history receipt.
