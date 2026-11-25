# Earnings-growth comparison contract

Inherits root standing guidance and B04 scope by explicit reference from AGENTS.md; no executable inheritance is implied.

Problem: compare issuer actuals and forecasts without treating vendor differences as revisions, mixing fiscal/calendar periods or substituting adjusted EPS for GAAP.

Input: issuer annual/quarterly releases, guidance and one dated estimate series per provider; USD/share; period-end and source/publication/retrieval metadata. Missing availability, expiry and analyst counts remain null.

Output: reported versus guidance versus consensus table, reproducible growth, discrepancy record and limited interpretation. Formula: 100*(later/earlier-1); ordinary percentage growth requires a positive denominator. CAGR=(last/first)^(1/years)-1. Never infer price returns from EPS growth alone.

Method/prior art: standard financial-statement reconciliation and horizontal EPS analysis; reuse prior project comparison issue291 and the existing B04 hierarchy. Forecast years stay within a provider series. An explicitly disclosed issuer-actual baseline may replace a conflicting vendor actual; retain both and show the effect. Fiscal years are issuer periods, not common calendar years.

Evidence/example: ChartMill actual15.53 differs from issuer15.58; FY2027 forecast40.60 gives161.4% versus corrected160.6%. Search-indexed long horizons are provisional; locked cells are not treated as direct-page verification. StockAnalysis39.98/65.34 remains a separate comparison series.

Exceptions/limits: no GAAP forecast manufactured from a small current GAAP-adjusted difference; tax adjustments may offset SBC. Allocation is distinct from finalized pricing. No market ingestion, ticker canonical writes, forecasting calibration, fair-value target or operational feed.

Review: verify units/periods, direct-source actual, guidance classification, estimate dates, no provider splice, explicit locked/search-only evidence, arithmetic repeat and owned-file publication. Next node may only be developed after state records its input/output and evidence prerequisites.
