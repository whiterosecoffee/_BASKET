# Rotation application: SNDK → SKHY
As of November 21, 2026, 00:03 America/Phoenix. US markets closed; reference market date November 20.
Status: conditional application of existing #198 forecasts to #305 rotation contract; not a newly verified forecast, execution signal, canonical feed or validated optimizer.

## Reconciled inputs
Massive daily summaries requested after FETCH/B02 update request in #311. SNDK regular $79.24 / AH $81.40; SKHY regular $103.57 / AH $106.2972. Exact AH last trade timestamps absent in daily summary, so these are asynchronous last-trade references, not a matched executable bid/ask pair. A new quote refresh is required before a trade. Raw response retained in evidence/2026-11-20.jsonl; same-day local evidence written at /workspace/scratch/8d0493f0855c/rotation-evidence/2026-11-20.jsonl. This does not establish FETCH ingestion.
SNDK issuer confirms 8:1 split, trading adjusted November 20. Per-share forecasts must use post-split basis. https://investor.sandisk.com/news-releases/news-release-details/sandisk-reports-fiscal-first-quarter-2027-financial-results .
SKHY instrument: Nasdaq USD ADR, depositary records show ORD:DR 1:10. https://depositaryreceipts.citi.com/adr/guides/pgm_d.aspx?cusip=78392B206&pageId=15&subpageid=105 .
Existing #198 comparison was corrected for using Korean share versus US ADR prices; do not restore the inflated Korean-entry return on a US ADR purchase.

Authoritative prior research input: https://github.com/whiterosecoffee/_BASKET/issues/198#issuecomment-7058973148 .
It supplies provisional calendarized EPS / judgmental issuer-specific terminal P/Es:
SNDK CY2027–30 EPS [33.045,36.9644,37.3675,37.23], P/E [4.5,4,3.75,3.5].
SKHY CY2027–30 USD EPS/ADR [39.96,49.69,57.2454,92.3826], P/E [3.75,3.5,3.25,3].
These multiples are assumptions, not independently established fair values. SKHY 2028 single-broker estimate and 2029/30 thin-panel estimates, FX held constant, are material uncertainty. Existing normalization removes a misleading identical-multiple ranking. No independent re-estimation here.
The same issuer-specific model favors SNDK on 2027/28 returns, approaches parity in 2029 and favors SKHY in a speculative 2030 projection. Earlier stronger SK rankings depended on different multiple assumptions and/or Korean entry prices.

## Conditional threshold
R = SNDK executable sale bid / SKHY executable purchase ask.
Switch pre-cost gross terminal wealth ratio = R * terminal_SKHY / terminal_SNDK.
2028 terminal values $173.915 and $147.8576 imply:
- Parity R=0.85017164.
- 10% relative wealth hurdle R=0.93518880 (policy example, not calibrated optimal buffer).
- AH last-trade reference R=0.76577746.
- If SKHY stays $106.2972, parity SNDK ~$90.37; 10% hurdle ~$99.41.
- If SNDK stays $81.40, 10% hurdle SKHY <=$87.04.
Taxes, spread/fees, whole shares, financing, ADR charges, dividends/withholding, FX and execution delay can change the threshold; this simple table excludes them. Positive tax drag raises required R; do not assume losses produce immediate cash. Dividends and tax treatment require consistent terminal total-wealth accounting.
These are joint price conditions, not predictions SNDK will reach $99 or SKHY will fall to $87. Do not insist on a SNDK rebound if fundamentals deteriorate.

## Model sensitivity and conclusion
CY2028 issuer-specific scenario: SNDK ~+81.64% vs SKHY ~+63.61% from AH references; switching relative edge -9.93%, not simply the difference in percentage returns. Under identical exit P/Es, SKHY instead leads by ~2.94% relative wealth; that small and assumption-sensitive edge does not justify claiming a robust switch.
CY2029 issuer-specific edge ~+1.67% before costs; too small to establish a decisive advantage. CY2030 apparent edge ~+62.87% depends heavily on SKHY EPS rising from ~$57.25 to ~$92.38; no clock-based instruction follows from thin estimates.
Practical answer: no demonstrated immediate full-rotation advantage through 2028 under current reconciled issuer-specific assumptions. Reassess at an improved ratio, independently stronger SKHY recurring earnings/valuation, or weaker SNDK estimates. A precise optimal date cannot be determined from these inputs.
Next evidence: synchronized executable quotes; revalidate same-endpoint recurring EPS/FX and justified relative multiples in owning #198 workstream; user account/tax constraints only through private inputs.

## Reproducible outputs
{
  "reference_ratio": 0.7657774616829042,
  "rows": [
    {
      "year": 2027,
      "S": 148.70250000000001,
      "K": 149.85,
      "sndk_return": 82.68120393120392,
      "skhy_return": 40.97266908253463,
      "relative_edge": -22.831322517655593,
      "parity_ratio": 0.9923423423423425,
      "hurdle10_ratio": 1.0915765765765768,
      "sndk_at_k_parity": 105.48321243243245,
      "sndk_at_k_hurdle": 116.0315336756757,
      "skhy_at_s_hurdle": 74.57103949160235
    },
    {
      "year": 2028,
      "S": 147.8576,
      "K": 173.915,
      "sndk_return": 81.64324324324322,
      "skhy_return": 63.61202364690697,
      "relative_edge": -9.92672189418583,
      "parity_ratio": 0.8501716355690998,
      "hurdle10_ratio": 0.9351887991260098,
      "sndk_at_k_parity": 90.37086438041572,
      "sndk_at_k_hurdle": 99.40795081845731,
      "skhy_at_s_hurdle": 87.0412477951759
    },
    {
      "year": 2029,
      "S": 140.128125,
      "K": 186.04755,
      "sndk_return": 72.14757371007371,
      "skhy_return": 75.02582382226437,
      "relative_edge": 1.6719667028465501,
      "parity_ratio": 0.7531844681641872,
      "hurdle10_ratio": 0.8285029149806059,
      "sndk_at_k_parity": 80.06140004934223,
      "sndk_at_k_hurdle": 88.06754005427646,
      "skhy_at_s_hurdle": 98.24950344550744
    },
    {
      "year": 2030,
      "S": 130.30499999999998,
      "K": 277.14779999999996,
      "sndk_return": 60.079852579852535,
      "skhy_return": 160.72916313882203,
      "relative_edge": 62.87443981044565,
      "parity_ratio": 0.4701642950079344,
      "hurdle10_ratio": 0.5171807245087279,
      "sndk_at_k_parity": 49.97714809931741,
      "sndk_at_k_hurdle": 54.97486290924915,
      "skhy_at_s_hurdle": 157.39179003108092
    }
  ]
}
Checks: formula cross-checks and source revision inspected. Inputs remain provisional; no probability, timing backtest, trading instruction or automatic monitor created. Original scope #305; B04 request #311.
