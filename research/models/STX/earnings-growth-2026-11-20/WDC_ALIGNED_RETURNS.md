# STX versus WDC — aligned FY2027 EPS anchors

Quotes: November20,2026 19:59ET after-hours, STX469USD/WDC268.50USD; directly read https://stockanalysis.com/stocks/stx/ and https://stockanalysis.com/stocks/wdc/. Public-page dated capture, not canonical FETCH output. Forecast inputs retained from WDC_COMPARISON.md, not freshly certified: ChartMill FY2027/28/29 STX40.60/66.50/90.37, WDC25.25/41.46/54.35. Existing accounting/margin/cohort limitations persist.

{
  "STX": {
    "price": 469,
    "eps": [
      40.6,
      66.5,
      90.37
    ],
    "anchor_pe": 11.551724137931034,
    "rows": [
      {
        "fy": 2027,
        "eps": 40.6,
        "cumulative_eps_pct": 0,
        "price_same_multiple": 469,
        "price_with_25pct_multiple_cut": 351.75,
        "return_same_multiple_pct": 0,
        "return_with_25pct_multiple_cut_pct": -25
      },
      {
        "fy": 2028,
        "eps": 66.5,
        "cumulative_eps_pct": 63.793103448275865,
        "price_same_multiple": 768.1896551724137,
        "price_with_25pct_multiple_cut": 576.1422413793102,
        "return_same_multiple_pct": 63.793103448275865,
        "return_with_25pct_multiple_cut_pct": 22.844827586206897
      },
      {
        "fy": 2029,
        "eps": 90.37,
        "cumulative_eps_pct": 122.58620689655172,
        "price_same_multiple": 1043.9293103448276,
        "price_with_25pct_multiple_cut": 782.9469827586207,
        "return_same_multiple_pct": 122.58620689655172,
        "return_with_25pct_multiple_cut_pct": 66.93965517241378
      }
    ]
  },
  "WDC": {
    "price": 268.5,
    "eps": [
      25.25,
      41.46,
      54.35
    ],
    "anchor_pe": 10.633663366336634,
    "rows": [
      {
        "fy": 2027,
        "eps": 25.25,
        "cumulative_eps_pct": 0,
        "price_same_multiple": 268.5,
        "price_with_25pct_multiple_cut": 201.375,
        "return_same_multiple_pct": 0,
        "return_with_25pct_multiple_cut_pct": -25
      },
      {
        "fy": 2028,
        "eps": 41.46,
        "cumulative_eps_pct": 64.19801980198021,
        "price_same_multiple": 440.87168316831685,
        "price_with_25pct_multiple_cut": 330.65376237623764,
        "return_same_multiple_pct": 64.19801980198021,
        "return_with_25pct_multiple_cut_pct": 23.148514851485167
      },
      {
        "fy": 2029,
        "eps": 54.35,
        "cumulative_eps_pct": 115.24752475247526,
        "price_same_multiple": 577.9396039603961,
        "price_with_25pct_multiple_cut": 433.45470297029703,
        "return_same_multiple_pct": 115.24752475247526,
        "return_with_25pct_multiple_cut_pct": 61.43564356435645
      }
    ]
  }
}

Method: anchor_PE=current_price/FY2027E EPS. price_scenario=endpoint_EPS*anchor_PE*multiple_factor. Constantfactor1.0; stressfactor.75. No chosen multiple justified as fair value, no probabilities. Holding comparable fiscal-year EPS multiples is an illustrative convention, not a forecast of the market's NTM denominator at future dates. FY2027 anchor is a normalization point; zero modeled return at this point does not forecast unchanged price throughJune2027 or prove allFY2027 earnings already priced in. EPS cumulative begins FY2027; stock cumulative begins the dated current quote. Matched algebra demonstrates equal growth if same multiple holds; it does not establish causation or market expectations. Future fiscal period endpoints approximatelyJune2028/June2029, not guaranteed price deadlines. Dividends/costs/taxes omitted.

Inference: similar FY2027->FY2028 growth (~64% each) and FY2027->FY2029 growth (~123% STX/~115%WDC). STX premium on same FY2027 inputs approximately8.6%, but earnings reliability/quality must be reconciled before ranking value. Smaller current implied multiple alone does not prove WDC is a better investment.

Next: independently reconcile comparable adjusted earnings and cycle-normalized margins; preserve unresolved STX vendor inconsistencies.
