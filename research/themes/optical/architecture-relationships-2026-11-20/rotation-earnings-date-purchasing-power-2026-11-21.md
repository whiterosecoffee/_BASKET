# Dated earnings and exchange purchasing power: SNDK to SKHY
Application of the existing rotation contract; all data/forecast inputs reused, no new market pull.
Reference prices: November 20, 2026 Massive AH summaries SNDK81.40, SKHY106.2972; asynchronous last trades, not executable bid/ask.
Forecast source: https://github.com/whiterosecoffee/_BASKET/issues/198#issuecomment-7058973148 . Prior applied note remains conditional, not superseded as an invalid calculation.

## Correction in decision framing
The previous answer evaluated switching now against holding to a terminal date. The user's follow-up adds a distinct choice: continue holding SNDK while BOTH prices evolve, then exchange into SKHY. A present fixed-candidate-price threshold cannot identify the best future switching date.
At date t, SKHY shares per SNDK = SNDK projected price(t)/SKHY projected price(t). If using an EPS/P-E scenario, = EPS_S(t)*PE_S(t)/(EPS_K(t)*PE_K(t)). Use matching calendar dates, share/ADR units and valuation conventions. Prices respond to forward expectations, not mechanically to earnings-report publication.
A report-date implementation must update next-twelve-month/next-year EPS available on each date, remaining uncertainty and forward multiples; reporting EPS growth is not itself an additional price gain when already priced in.
The retained forecasts are annual calendarized EPS with assumed date-specific P/Es, not verified rolling NTM forecasts on actual quarterly report dates.

## Annual checkpoint calculation
USD per SNDK share / SKHY ADR, no dividends, taxes, financing or trading costs, fractional shares; FX assumptions retained from source.
[
  {
    "date": "2027-12-31",
    "S_eps": 33.045,
    "K_eps": 39.96,
    "S_pe": 4.5,
    "K_pe": 3.75,
    "S_price": 148.70250000000001,
    "K_price": 149.85,
    "SKHY_per_SNDK": 0.9923423423423425,
    "S_eps_yoy": null,
    "K_eps_yoy": null,
    "extra_SKHY_vs_now": 29.586256059499316
  },
  {
    "date": "2028-12-31",
    "S_eps": 36.9644,
    "K_eps": 49.69,
    "S_pe": 4,
    "K_pe": 3.5,
    "S_price": 147.8576,
    "K_price": 173.915,
    "SKHY_per_SNDK": 0.8501716355690998,
    "S_eps_yoy": 11.860795884400055,
    "K_eps_yoy": 24.349349349349335,
    "extra_SKHY_vs_now": 11.020717912058608
  },
  {
    "date": "2029-12-31",
    "S_eps": 37.3675,
    "K_eps": 57.2454,
    "S_pe": 3.75,
    "K_pe": 3.25,
    "S_price": 140.128125,
    "K_price": 186.04755,
    "SKHY_per_SNDK": 0.7531844681641872,
    "S_eps_yoy": 1.0905087056735763,
    "K_eps_yoy": 15.205071442946272,
    "extra_SKHY_vs_now": -1.6444716838547535
  },
  {
    "date": "2030-12-31",
    "S_eps": 37.23,
    "K_eps": 92.3826,
    "S_pe": 3.5,
    "K_pe": 3,
    "S_price": 130.30499999999998,
    "K_price": 277.14779999999996,
    "SKHY_per_SNDK": 0.4701642950079344,
    "S_eps_yoy": -0.3679668160834981,
    "K_eps_yoy": 61.379953673133556,
    "extra_SKHY_vs_now": -38.60301216300074
  }
]
Current reference ratio = 0.7657774616829042.
2027 exchange purchasing power is 29.59% greater than immediate switch in this scenario. 2028 is11.02% greater, 2029 is1.64% less and2030 is38.60% less.
CY2027→28 EPS growth: SNDK11.86%, SKHY24.35%. Later SKHY growth is more speculative, especially61.38% in2030. Multiples differ by company and date: they are judgmental assumptions, not empirical fair-value estimates or a constant-P/E forecast.

## Example per 100 original SNDK shares, same2028 endpoint
{
  "rotate_now_SKHY_per_original_SNDK": 76.57774616829042,
  "wait_2027_SKHY_per_original_SNDK": 99.23423423423425,
  "hold_to2028_value": 14785.759999999998,
  "rotate_now_then2028_value": 13318.018724858228,
  "rotate_2027_then2028_value": 17258.321846846848,
  "SKHY_2028_eps_claim_now": 3805.1482071023506,
  "SKHY_2028_eps_claim_wait2027": 4930.9490990991
}
Immediate switch acquires76.58 SKHY, worth$13,318 in2028 under the scenario.
Hold SNDK through2027 then exchange acquires99.23 SKHY, worth$17,258 in2028.
Hold SNDK through2028 is worth$14,786.
This is a deterministic scenario path comparison, not proof of an optimal trading policy. Actual ratio may never approach the2027 value. Timing maximum may occur between annual checkpoints, or immediately if estimates/repricing change. Selection of a modeled maximum has forecast error and execution risk.
EPS attributable to purchased SKHY shares is not a cash distribution: per original SNDK, immediate switch has a modeled$38.05 claim on2028 annual SKHY earnings; waiting to2027 has$49.31, compared with$36.96 SNDK2028 EPS if retained. This does not establish stock attractiveness independently of terminal multiples, retained capital, cash conversion, taxes and risk.

## Report dates and smallest next action
Official sources checked:
https://investor.sandisk.com/news-events/events
https://investor.sandisk.com/news-releases/news-release-details/sandisk-report-first-quarter-fiscal-year-2027-results-october-29
https://news.skhynix.com/en/q3-2026-earnings-conference-call/
https://www.sec.gov/Archives/edgar/data/2120882/000119312526420934/d413172d6k.htm
They establish prior October2026 reports; no future2027 quarterly schedule verified here. Search exposes unconfirmed conflicting secondary January/February2027 dates; do not assign exact event-day entries using them.
All table dates December31 are valuation checkpoints, not confirmed earnings announcements. No interpolation to quarterly EPS performed.
B04/#198 next: derive a sourced quarterly rolling forward EPS bridge at each issuer report; reprice both legs under coupled scenarios; compare exchange-ratio path and net terminal wealth against immediate switching and holding; do not duplicate valuation/ingestion. B02 matched quotes needed for any executable recommendation.

Status: scenario arithmetic reviewed; exact report timing, forecast path validity, costs/taxes and probability of opportunity unverified. Shared engine implementation stays with B04 #311; no new engine or monitor.
