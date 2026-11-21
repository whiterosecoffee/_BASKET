# Fiscal-year valuation with revision and dilution checks

Parent: ../../../architecture/COMPONENT_QUICKSTART.md; domain: B11 in ../../../orchestration/sparks.json. Reuse existing worker lifecycle; no new engine or shared schema.

Consumer: investor comparing AAOI price against FY2027 adjusted earnings.
Inputs: USD timestamped price/session, EPS with period-end/accounting basis/source date, prior comparable snapshot, issuer capacity and capital disclosures. Outputs: FY P/E, estimate/price deltas, analyst range, scenario sensitivity and missing-input list.

Method: P/E=price/EPS (undefined for EPS<=0); revision=new/old-1; sensitivity price=EPS*multiple. Keep GAAP, adjusted and NTM separate. Dilution stress: incremental shares=gross raise/sale price; stressed EPS=baseline EPS*baseline shares/(baseline shares+incremental shares). Reject double counting where consensus already includes the issuance. Weighted-average timing and earnings on proceeds require a separate evidenced bridge.

Prior art: point-in-time financial statement analysis, earnings-revision attribution and cap-table sensitivity. Installed equipment is not qualified output, shipments or revenue. Exit-year capacity cannot be applied to twelve months. Multiple sensitivity is not a target/probability.

Review each update: verify units and period, compare two estimate sources (shared vendor means not independent coverage), read primary issuer disclosures, recalculate all fields, label stale prices and unknown timestamps, verify saved bytes. Existing machine-readable worker protocol records branch/integration evidence; state.json is a research checkpoint only. No test suite or automation claimed.

Example: 40.79/3.75=10.8773x. Prior 46.89/4.60=10.1935x: lower price need not mean a lower multiple after estimate cuts. Planned extension: quarterly capacity-to-EPS bridge once source inputs exist; do not invent utilization, yields or margins.
