# Rotation engine (B04: `engines/valuation/rotation`)

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

## Data (research/models/rotation/)
| file | source |
|---|---|
| `ratios.csv` | `ingest-ratios` from Massive `/stocks/financials/v1/ratios` CSV (price, market cap, EV) |
| `prices/<T>.csv` | `ingest-prices` from Massive aggs (`t`,`c`) or `date,close` |
| `estimates.csv` | `ingest-estimates`: consensus / house / guidance EPS+revenue by fiscal year. **provenance (kind, source, as_of) required**; append-only |
| `events.csv`, `positions.csv` | earnings dates; entry price for the tax term |

**Entitlement gap (checked 2026-11-22):** Massive Benzinga earnings, guidance and consensus endpoints return NOT_ENTITLED and Quartr requires Pro, so no forward-estimate feed is wired. Ratios, income statements and aggs work. Until an estimate source is entitled, load estimates from any export (or derive `guidance` rows from earnings-call transcripts) via `ingest-estimates`.

```
python -m engines.valuation.rotation.cli ingest-ratios ratios_export.csv
python -m engines.valuation.rotation.cli ingest-estimates my_estimates.csv
python -m engines.valuation.rotation.cli report --hold NVDA --tax 0.2 --rerate AAOI=1.1
python -m unittest engines.valuation.rotation.test_rotation
```
