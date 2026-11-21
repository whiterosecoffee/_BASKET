# Why EPS growth differs from stock returns

Conceptual reconciliation using prior dated inputs, not new current-price research. Previous PRICE_SCENARIOS.md used469USD atNov20,2026 19:59ET; FY2026 actual15.58, FY2027/28/29 provisional vendor EPS40.60/66.50/90.37.

Important presentation correction: cumulative EPS started from historicalFY2026, whereas share-price scenarios started fromNov20 price. They are not aligned return baselines. A+480% EPS change from15.58 to90.37 is not a+480% future share-price prediction from469.

At469, price/FY2027EPS40.60=11.5517x. Holding that SAME earnings-year multiple constant gives:
[
  {
    "fy": 2027,
    "eps": 40.6,
    "price_at_constant_fy2027_multiple": 469,
    "return_from469": 0
  },
  {
    "fy": 2028,
    "eps": 66.5,
    "price_at_constant_fy2027_multiple": 768.1896551724137,
    "return_from469": 63.793103448275865
  },
  {
    "fy": 2029,
    "eps": 90.37,
    "price_at_constant_fy2027_multiple": 1043.9293103448276,
    "return_from469": 122.58620689655172
  }
]

This is illustrative arithmetic, not evidence the market actually discounts exactlyFY2027 or will preserve this multiple. EPS40.60->66.50 rises63.8%, hence a constant-multiple price469->768.19 rises63.8%. FY2027->FY2029EPS rises122.6%, giving1043.93. Different multiple anchors (trailing, current fiscal year, NTM) must not be mixed. Stock-price return=(EPS_future/EPS_anchor)*(PE_future/PE_anchor)-1, excluding dividends and assuming compatible accounting/share bases.

Expectations may already include growth. Risk, interest rates, cyclicality, forecast revisions, cash conversion and earnings quality affect multiple. EPS already includes dilution, so do not subtract dilution twice. Share-price causal attribution cannot be proved from implied PE arithmetic alone. All distant vendor EPS remains provisional with existing margin/cohort inconsistencies; illustrative constantPE path not an expected price forecast.

Next: choose a consistent earnings horizon and validate the EPS before assigning an expected multiple.
