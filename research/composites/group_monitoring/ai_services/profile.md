# AI services integrators — initial cumulative baseline

Research cutoff: 2026-11-19T14:12:48.431Z, November 19 Tucson morning.
Status: source-checked research pilot; no prior persisted run, live service or DOT receipt.

GDYN shows the clearest matched labor-productivity proxy and margin improvement.
EXL has faster revenue growth with roughly flat adjusted operating margin.
Genpact growth is concentrated in ATS. CGI EPS growth is substantially associated
with fewer diluted shares. These are different mechanisms, not a valuation ranking.

| Company | Quarter revenue, prior → latest (USD) | Growth | Own margin definition, prior → latest |
|---|---:|---:|---|
| GDYN | $104.163M → $114.294M | +9.7% | adjusted EBITDA 12.2% → 20.0% |
| EXLS | $529.585M → $633.959M | +19.7% | adjusted operating 19.4% → 19.3% |
| G | $1,291.257M → $1,385.400M | +7.3% | adjusted operating 17.7% → 17.8% |
| GIB | $2801.785M → $2894.083M | +3.3% CAD | adjusted EBIT 16.6% → 16.4% |

Comparisons are quarters ended September 30, 2025 → 2026. CGI is FY Q4;
the others Q3. CGI original revenue is CAD4,013.837M → CAD4,146.063M.
Both USD values use the [Bank of Canada November 18 rate](https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date=2026-11-18&end_date=2026-11-18),
USD1 = CAD1.4326: constant translation, not period-average USD reporting.
The margin definitions differ and are not ranked as equivalent measures.

## Material mechanisms

- **GDYN:** matched headcount 4,971 → 4,559; annualized quarterly revenue per
period-end employee $83,817 → $100,280 (+19.6%).
GAAP gross margin 33.3% → 40.3%; adjusted EPS $0.09 → $0.18.
The labor proxy does not isolate AI causation.
- **EXLS:** adjusted EPS $0.48 → $0.62; gross margin 38.5% → 38.0%.
Company-defined data/AI-led growth includes acquisition and mix effects.
Aimpoint adds delivery capability; purchase price/EPS contribution remain unresolved.
- **G:** ATS revenue $310.986M → $405.104M; CBS $980.271M → $980.296M.
Mars's November 12 center expansion confirms operating activity, but no verified
contract value establishes an incremental earnings contribution.
- **GIB:** adjusted earnings CAD471.716M → CAD475.360M (+0.8%);
diluted shares 221.916M → 205.492M (-7.4%); adjusted EPS CAD2.13 →
CAD2.31 (+8.5%). Total book-to-bill 109.2% and AI-embedded managed-service
book-to-bill 122% are bookings indicators, not measured AI revenue.

## Sources and unresolved comparisons

Primary earnings sources: [GDYN October 29](https://www.sec.gov/Archives/edgar/data/1743725/000174372526000029/grid-20260930xex991.htm),
[EXL October 27](https://ir.exlservice.com/news-releases/news-release-details/exl-reports-2026-third-quarter-results), [Genpact November 5](https://media.genpact.com/2026-11-05-Genpact-Reports-Third-Quarter-2026-Results),
[CGI November 11](https://www.sec.gov/Archives/edgar/data/1061574/000106157426000020/cgi-fy26_q4xpressrelease.htm).
These verify disclosed statements; issuer AI categories differ.
[Relationships](relationships.json) preserve dates and unknown economics.
EXL NVIDIA/Microsoft pages establish capability claims, not new weekly revenue.

Only GDYN has verified matched headcount in this extraction. Rounded website
counts are excluded. Cash flow, balance-sheet exposure, customer concentration
and geographic mix need aligned extraction. [Forecast leads](estimate_research.json)
retain unresolved secondary 2027/2028 estimates and CGI's conflicting cached
values. No comparable consensus revision or forward-P/E ranking is established.

A separate Massive snapshot attempt returned timestamped GDYN/EXLS trades but
no current G/GIB trade. Licensed raw snapshots are outside this public package.
No live-feed claim, complete repricing comparison or local ticker update receipt
is made. No private source data is committed.

## Continuity and acceptance

[Observations](observations.jsonl) preserve 45 public-source numerical records,
including explicit nulls. [Projection](profile.json) is reproducible.
[State](state.json) preserves the original baseline and open questions.
A first persisted baseline cannot establish a week-over-week revision.
Real successive updates and a second segment remain acceptance work.

Next step: obtain timestamped comparable 2027/2028 EPS and matched headcounts,
then update this baseline using one genuine new disclosure or correction.
