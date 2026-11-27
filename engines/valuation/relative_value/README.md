# Rotation engine (B04: `engines/valuation/relative_value`)

## Virtual ETF: spot rotation for share count and expected end value
A paper portfolio of N names. At spot, sell the name whose price is rich relative to its expected end price and buy the one that is cheap relative to its own; keep rotating where expected return per unit of risk is highest.

- **Swap math** (`portfolio.swap`): `shares_B = shares_A x P_A/P_B` (share-count multiplier = spot ratio), and `end value swap / stay = (1+r_B)/(1+r_A)` where `r = T/P - 1`. Costs and tax on realised gain reduce `shares_B`. `STAY`/`CONTESTED`/`SWAP` requires an edge over the hurdle and, for `SWAP`, a positive edge in bear, base and bull.
- **Round-trip triggers**: a fair spot ratio `T_A/T_B` gives two thresholds, `TRIG_A>B` and `TRIG_B>A`. Swap A to B only above the first and back only below the second, so you never trade inside the hurdle-plus-friction band.
- **Weights** (`target_weights`): `w ~ E[ret]/sigma` among names with positive expected return, capped (default 50%), re-weighted only when drift exceeds a no-trade band (default 10pp). Buys into a name making a new 52-week low are staged (default 33% of intended size).
- **Expected end prices** come from `targets.csv` (your bear/base/bull target prices with a horizon date, normalised to a common horizon) or, if absent, from the EPS x multiple model. Every output says which (`BASIS`).
- **Virtual ledger**: `holdings.csv` (start) plus append-only `ledger.csv` (paper trades, average-cost basis). `rebalance --record` appends orders.
- **Price-only sanity test** (`simulate A B`): swaps on ratio vs its rolling mean. It is a mechanics check, not a forecast.

```
python -m engines.valuation.relative_value.cli swap NVDA --tax 0.2
python -m engines.valuation.relative_value.cli rebalance --horizon 12 --record
python -m engines.valuation.relative_value.cli simulate NVDA SNDK
```

**Warning from the price-only test (2025-26 data, in sample):** rotating on a rolling-mean ratio did not accumulate shares versus holding the stronger name, and starting in SNDK it sold out of a 16x winner early. A ratio anchored to history mean-reverts only if there is no fundamental trend. This is why the engine anchors the fair ratio on *expected end values*, not on past ratios, and why target quality is the whole game.

Answers: *"Is it worth rotating from HELD to CANDIDATE, after costs, taxes and catalyst timing?"* on an apples-to-apples basis.

## Apples-to-apples rules
- **Calendarized**: fiscal years (labelled by year-end year) are blended to calendar years, so a Jan-FYE company is compared with a Dec-FYE one.
- **Same horizon**: NTM EPS is a time-weighted blend of CY(t) and CY(t+1); forward P/E shown for CY2026–2030.
- **One basis**: estimates carry `basis` (`non_gaap`/`gaap`); `CHECK_EPS_BASIS` flags a forward/TTM wedge >3x or <0.5x.
- **Gaps are explicit**: years beyond supplied estimates are extrapolated by fading last growth (x0.8/yr, capped -20%..+50%) and flagged `EXTRAPOLATED:<years>`.
- **Growth-adjusted**: `RESID` = NTM P/E turns richer(+)/cheaper(-) than the cohort P/E~EPS-CAGR line (needs >=4 usable tickers). `PEG` uses 2026-30 EPS CAGR.
- **TTD / point-in-time**: estimates older than 120d or prices older than 5d make a ticker unusable (`STALE_*`) and the signal `INSUFFICIENT_DATA`. Nothing dated after `--asof` is read.

## Rotation logic
`return = (EPS_NTM at horizon / EPS_NTM now) x re-rating factor x (1 + multiple scenario) - 1`, scenarios bear/base/bull = multiple -/+15%, weights 25/50/25.
`edge = cand_return - held_return - round_trip_cost - tax_rate x unrealised_gain_fraction`.
- `ROTATE`: expected edge >= hurdle (8%) and edge > 0 in all three scenarios.
- `WAIT_FOR_PRINT`: would rotate, but HELD reports within 21d and edge < 2x hurdle (the print may re-rate HELD first).
- `CONTESTED`: clears hurdle but not in every scenario. `HOLD`: below hurdle.
Re-ratings you expect at earnings are explicit inputs: `--rerate NVDA=1.10`. Nothing is inferred about earnings outcomes.

## Auto targets from three anchors (`anchors.py`, `history.py`)
`cli anchors [--write]` builds bear/base/bull returns over the horizon from three independent anchors and blends them (default F 50% / I 30% / R 20%, renormalised if one is missing). `--write` appends them to `targets.csv` with `source=auto:...`; your own rows with a later `as_of` override them.
- **F, standardized estimates:** company estimates/guidance (NVDA consensus EPS path, SNDK guided run-rate, CRWV backlog-conversion revenue with EV/sales held constant and net debt rolled forward). The multiple moves by a flat band by default; the band is the realised horizon volatility clamped to 15-50%. `--rerate w` (default off) moves the multiple `w` of the way toward historical TRAILING P/E quartiles, compared like for like with today's trailing P/E; it is off by default because history is a poor target once growth matures.
- **I, industry forecasts:** `industry.csv` scenarios, each tagged `published` or `assumption`, translated by `anchor_map.json` (NVDA: EPS growth = beta x hyperscaler capex growth; SNDK: a bits x price P&L bridge using TrendForce supply and price direction; CRWV: revenue tracks capex growth). Every translation parameter is an editable assumption.
- **R, historical spot ratio:** each name's price ratio to every other name, partially reverted (`--lam`, default 25%) toward its own 250-day median. Relative-only and zero-sum across the cohort. Low weight on purpose: the price-only simulation showed ratio reversion accumulates no shares when the ratio trends.
- **Guards:** `ANCHOR_DISAGREE` when anchor base returns differ by >50pp (the name's weight cap is halved in `rebalance`); `HIST_UNRELIABLE` when history is short or EPS changed regime >6x; `history.py` normalises split-adjusted vs unadjusted share counts (Massive mixes them) and replaces filing dates that are >120 days late with period end + 45 days.

## Implied expectations (`implied.py`)
Reverse DCF on trailing FCF: the constant 10-year FCF growth that justifies today's market cap at `r = 10y yield + ERP` (default 4.5%) and 3% terminal growth. These are assumptions, not facts. Compare with consensus before setting `targets.csv`. Note Massive's TTM FCF can lag the last four reported quarters (NVDA: 127.0B vs 148.6B from releases), which understates the market's pessimism.

## Data (research/models/rotation/)
| file | source |
|---|---|
| `ratios.csv` | `ingest-ratios` from Massive `/stocks/financials/v1/ratios` CSV (price, market cap, EV) |
| `prices/<T>.csv` | `ingest-prices` from Massive aggs (`t`,`c`) or `date,close` |
| `estimates.csv` | `ingest-estimates`: consensus / house / guidance EPS+revenue by fiscal year. **provenance (kind, source, as_of) required**; append-only |
| `guidance.csv` | company guidance from primary releases (per-share pre-split values carry `split_factor`; `annualize` factor is explicit). Report shows price / annualised guided EPS and EV / annualised guided revenue |
| `holdings.csv`, `targets.csv`, `ledger.csv` | virtual ETF inputs and paper trades (see above) |
| `events.csv`, `positions.csv` | earnings dates; entry price for the tax term |

**Estimate sourcing (2026-11-22):** `estimates.csv` and `guidance.csv` now hold figures from company press releases (primary) and, where marked, secondary consensus (CNBC) with the source and date on every row. SNDK and CRWV have no forward-EPS rows: SNDK is covered by quarterly guidance, CRWV is loss-making. Earnings dates in `events.csv` are unconfirmed and SNDK's two sources conflict.

**Entitlement gap (checked 2026-11-22):** Massive Benzinga earnings, guidance and consensus endpoints return NOT_ENTITLED and Quartr requires Pro, so no forward-estimate feed is wired. Ratios, income statements and aggs work. Until an estimate source is entitled, load estimates from any export (or derive `guidance` rows from earnings-call transcripts) via `ingest-estimates`.

```
python -m engines.valuation.relative_value.cli ingest-ratios ratios_export.csv
python -m engines.valuation.relative_value.cli ingest-estimates my_estimates.csv
python -m engines.valuation.relative_value.cli report --hold NVDA --tax 0.2 --rerate AAOI=1.1
python -m unittest engines.valuation.relative_value.test_rotation
```

## Basket universe (300+ names)
`cli basket` runs the stress/rebound statistics over the full tracked universe: the draft manifest snapshot from branch `work/146-basket-universe-taxonomy`
(291 symbols, read-only copy in `research/models/rotation/universe/`) plus 6 additions = 297 identifiers; 243 have Massive daily bars.
`low52w_friday_classification.csv` holds the exact Friday 52-week-low flag (39 of 243 hit). Gaps: 20 tradable names without Massive bars
(mostly OTC ADRs), plus indices/futures/FX, which need their own feed. Names still missing from the manifest must be added to `ADDITIONS` in `basket.py`.


## Layout and related work
Package `engines/valuation/relative_value/` (renamed from `.../rotation/` on 2026-11-26 so it cannot collide with PR #298, which adds `engines/valuation/rotation/rotation.py`). Data, prompts and skills stay under `research/models/rotation/`. Boundaries with other open work: `research/models/rotation/RELATED_WORK.md`.

## Rebound study (`cli rebound`)
`snapshots.py` reads the `_PATTERNS` daily store (`_TICKERS/<T>/snapshots/<date>.jsonl`, read-only) and builds regular-session daily bars. `rebound.py` ranks tickers by distance above the 52-week low and drawdown from the 52-week high, excludes `split_suspect` names (unadjusted prices), and tabulates forward 20-day returns by bucket with a date-clustered interval. Run: `python -m engines.valuation.relative_value.cli rebound --snapshots <path>/_TICKERS --out research/models/rotation/relativity/rebound_<date>.json --as-of-floor <date>`. Tests use a synthetic store; the first real-store run is pending because the workstation holding the store was offline.
