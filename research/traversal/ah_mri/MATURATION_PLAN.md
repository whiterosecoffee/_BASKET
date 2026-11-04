# AH-MRI Maturation Plan — B06 #166
Status: scoped implementation plan; no production deployment, live data, merge or release authorization. As-of assessment: 2026-11-04, refreshed from GitHub main and PR #168. Current local branch is independent and must be refreshed before integration.

## Product acceptance target
An operator can request `AH-MRI EOD YYYY-MM-DD` and receive a USD-first report with provider-verified completed-session close, eligible after-hours print (or explicit missing), synchronized breadth and sector relatives, event surprises using as-known consensus, observed vs conditional battle bands, triggers/falsifiers, and input manifest/reproducibility metadata. Report generation must not imply live connectivity unless the entitled hosted producer and scheduler are proven.

## Baseline maturity — weighted qualitative rubric (0–10, not measured forecast performance)

| Dimension | Weight | Baseline | Target | Why |
| --- | ---: | ---: | ---: | --- |
| Architecture / reuse | 15% | 7 | 9 | B06-owned component; integration pending |
| Source provenance / data | 20% | 5 | 9 | local as-of checks, no provider-backed fixture |
| Market regime analytics | 15% | 4 | 9 | geometry/composites unconnected |
| Support / stress analysis | 15% | 3 | 9 | no verified volume-price distribution |
| Backtesting / calibration | 15% | 1 | 8 | no out-of-sample replay |
| Validation / reliability | 10% | 4 | 9 | synthetic tests defined; exact-head CI pending |
| Operations / automation | 5% | 1 | 8 | CLI only, no hosted schedule |
| Report usability | 5% | 6 | 9 | readable Markdown/JSON, missing macro attribution |
| **Weighted composite** | **100%** | **3.8** | **8.8** | author-assessed readiness, NOT predictive performance |

**Scoring convention:** 0 absent; 1–3 preliminary; 4–6 prototype; 7–8 validated component; 9–10 integrated, evidenced and operated. Scores must only advance against cited acceptance artifacts, not commits or issue counts.

## Ranked opportunities / smallest first, impact:effort
P0 readiness and fail-closed evidence gate: impact 5, effort 1, ratio 5.0, independent of new market inputs.
P0 exact-head local suite and results: impact 5, effort 1, ratio 5.0, gated by correct checkout.
P1 B02 canonical session snapshot fixture: impact 5, effort 3, ratio 1.67; blocked on entitled adapter.
P2 B06 geometry/B17 context composition: impact 5, effort 3, ratio 1.67; dependent on versioned source shapes and synchronized clocks.
P3 observed support / price-volume footprint: impact 5, effort 4, ratio 1.25; requires qualified volume/trade data.
P4 historical replay/calibration B07: impact 5, effort 5, ratio 1.0; requires frozen complete source vintages.
P5 macro/earnings/options enrichment: impact 4, effort 5, ratio 0.8; conditional on provider capability/units.
P6 B08 hosted scheduling and B00 release: impact 4, effort 5, ratio 0.8; dependent on all gates.

### Phase gates, ownership, acceptance
**P0 (this worker: only `research/traversal/ah_mri/**`).**
- Define full-state readiness checker and test cases; prevent `production_ready` when provider, geometry, historical replay or independent review absent.
- Harden session/end-point and macro vintage handling; allow `unknown` as correct result.
- Run offline deterministic tests against exact head; document actual execution platform and SHA. If inaccessible, mark NOT RUN and hand B01 request.
- Keep tool output versioned and manifest hash; do not claim data provenance merely from user-authored `source` strings.

**P1 (B02, existing issue #152 / #148 and B00 routing).**
- Supply immutable snapshot fixture from licensed source for SPY, QQQ, NVDA, CRWV, ORCL, with exact as-of, MIC, venue, trade-vs-quote, adjusted prior close, time-to-die, official session close, source identity and append-only revisions. Demonstrate early-close and missing AH coverage.
- Acceptance: same snapshot replays byte-identical report and no as-of lookahead, with independently verified source and provider entitlement. NO new B06 poller.

**P2 (B06 existing #149/#108; B17 #100).**
- Connect bounded 1/5/15/30/60m returns, range position/velocity from existing geometry, and QQQ/SPY, RSP/SPY, SMH/QQQ, IWM/SPY synchronized relatives.
- Acceptance: comparisons null on unsynchronized or incomplete windows, no composite constructed by swapping mixed RTH/AH clocks. No duplicate traversal algorithms in AH-MRI.

**P3 (B06 geometry/evidence owners; B02 source).**
- Price/volume-at-price buckets with source-normalized trade size/price, session completeness, adjusted history and acceptance/rejection; reference levels always distinguished from confirmed measured zones. Macro adverse definition requires event/expectation units and sign.
- Acceptance: frozen fixtures specify confirmation, invalidation and observed breach; sample size, time window, calculator version, source IDs. No dealer signed GEX from OI alone.

**P4 (B07 calibration / B01 independent).**
- Walk-forward pre-registered evaluation using only available-at timestamps; baseline previous-low/ATR/simple pivot vs volume-density model. Measure zone contact, hold, breach, false signal, recovery, risk/reward after friction by day/regime, and missed rebound cost. Report sample count, confidence intervals and failure segments; never forecast calibrated probability before evidence.

**P5 (B03 issuer event ownership; B02 market data; B00 contract).**
- Official economic/earnings schedules, expectation vintages and actual release time, Treasury/credit/FX, options surfaces if licensed. Separate surprise direction, market reaction, and asserted mechanism, with contradiction tracking.
- Acceptance: matched-unit surprise, 0–5/5–30/30–60min reactions only if contiguous comparable bars exist; options signed positioning explicitly unknown absent independently justified inventory assumptions.

**P6 (B08 / B02 / B00 / B01).**
- Durable hosted scheduler after market close and after AH cutoff, replay-idempotent records, cold-restart test, silent no-change policy, rate limit handling, alert transport, timezone/holiday calendar and observability.
- Acceptance: ≥30 independent eligible-session reports produced with no silent stale-as-live classifications, documented failure/repair procedure and runbook. Threshold is an acceptance proposal, not observed evidence.

**P7 release governance (B00/B01).**
- Independent CI on exact PR head, migration compatibility, no ownership collisions, approved merge only, verify green main CI and manifest, versioned release only after separate authorization.

## Stop conditions / exclusions
- Missing approved canonical snapshot -> no claim of today's complete EOD analysis from AH-MRI.
- Missing B07 calibration -> support zones descriptive and stress paths hypothetical, no numeric probabilities.
- Missing hosted runner -> no claim of automatic delivery.
- Do not write outside `research/traversal/ah_mri/**`. No new competing issue, branch, provider adapter, schema or CI workflow.
- Older analysis (June 24) and November 4 news/quotes in chat are not a source-verified fixture.

## Dependency edges
P0 -> P1 -> P2 -> P3 -> P4 -> P6 -> P7.
P1 -> P5 -> P6, with P3/P5 parallel after B02 readiness.
B00 arbitration precedes any cross-domain shared-schema changes. B01 exact-head unit checks may happen at P0 and should repeat at integration.

## Next action
B01 exact-head test verification, B02 real frozen session input, B00 consumer contract routing. Continue B06-only documentation and consumer-side checks independently; do not merge.
