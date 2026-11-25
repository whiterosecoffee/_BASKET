# STX earnings growth and conditional share prices

Starting price469.00USD, Nov20,2026 at19:59ET after hours, source https://stockanalysis.com/stocks/stx/ read directly. Webpage snapshot, not canonical FETCH result. Financial baseline FY2026 issuer adjusted EPS15.58USD. Forward EPS40.60/66.50/90.37 from dated ChartMill research, Nov14FY2027 history point; still provisional with unresolved accounting/margin/cohort issues. See GROWTH_CHART.md and MARGIN_REVIEW.md. Current direct ChartMill fetch403; no claim of newly refreshed estimates.

{
  "model_version": "stx-eps-multiple-sensitivity/0.1.0",
  "record_class": "conditional_scenario_not_expected_return",
  "price_baseline": 469,
  "baseline_timestamp": "2026-11-20T19:59:00-05:00",
  "eps_baseline": 15.58,
  "rows": [
    {
      "year": 2027,
      "eps": 40.6,
      "yoy": 160.5905006418485,
      "cum": 160.5905006418485,
      "prices": [
        {
          "pe": 10,
          "price": 406,
          "cum_return": -13.432835820895528
        },
        {
          "pe": 15,
          "price": 609,
          "cum_return": 29.850746268656714
        },
        {
          "pe": 20,
          "price": 812,
          "cum_return": 73.13432835820895
        }
      ]
    },
    {
      "year": 2028,
      "eps": 66.5,
      "yoy": 63.793103448275865,
      "cum": 326.82926829268297,
      "prices": [
        {
          "pe": 10,
          "price": 665,
          "cum_return": 41.79104477611941
        },
        {
          "pe": 15,
          "price": 997.5,
          "cum_return": 112.68656716417911
        },
        {
          "pe": 20,
          "price": 1330,
          "cum_return": 183.5820895522388
        }
      ]
    },
    {
      "year": 2029,
      "eps": 90.37,
      "yoy": 35.89473684210527,
      "cum": 480.03851091142496,
      "prices": [
        {
          "pe": 10,
          "price": 903.7,
          "cum_return": 92.68656716417911
        },
        {
          "pe": 15,
          "price": 1355.5500000000002,
          "cum_return": 189.0298507462687
        },
        {
          "pe": 20,
          "price": 1807.4,
          "cum_return": 285.3731343283582
        }
      ]
    }
  ]
}

Price=annual EPS*chosen P/E. Cumulative price return=price/469-1; EPS cumulative=EPS/15.58-1. EPS and share-price percentages use different baselines. The10x/15x/20x multiples are illustrative assumptions, not probability-weighted outcomes or independently justified fair multiples. Dates roughlyJune of fiscal year are earnings-period endpoints, not share-price deadlines or confirmed report dates. Applying a P/E to that year's EPS does not specify the forward-year market pricing convention at endpoint. Dividends, trading costs/taxes excluded. No claim share price tracks cumulative EPS fromFY2026: current price already embeds future earnings.

Caveat: EPS forecast cuts and multiple contraction can reduce returns further;10x is not a downside floor. ExistingFY2028 stress EPS31.72 at10x=317.20, a32.37% loss from469, illustrating joint earnings/multiple risk. Scenarios not calibrated, no probabilities or trade instruction.

Next: independently reconcile earnings inputs and justify cycle-normalized valuation multiples before treating any value as an expected price.
