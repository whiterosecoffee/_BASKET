# MRVL–LITE maturation plan

Worker B04-189. Branch `work/189-mrvl-lite-maturation`. Scope `research/models/mrvl_lite/**`.

## Intended outcome

Compare executable entry cost, observed rebound from lowest eligible trade, merger discount and common-calendar earnings power. A result must identify historical evidence, modeled assumptions, unknowns and the next falsifiable condition. Forecasts never become probabilities without calibration.

## Audit and corrections

The conversation retrieved issuer terms and Massive prices but did not retain raw price snapshots in canonical ticker storage. Minute-bar lows establish a price and one-minute interval, not an exact trade timestamp. Session close and final-minute close must remain separate. A spread computed from independent lows is invalid because the low prints can occur at different seconds. A narrowing spread can arise from a falling acquirer rather than rising target.

Prior FY2028 and CY2028 comparisons mixed fiscal periods. The later calendar projection used annual prorating, a sparse two-analyst LITE FY2029 estimate, conflicting MRVL FY2029 estimates, and approximate ownership to infer diluted shares. Withdraw $254 as a verified base case. Preserve it as a conditional sensitivity in case.json. Approval to expose a target requires reconciled source dates, adjusted/GAAP basis, standalone/combined treatment, exact share denominator and common periods. Management's first-year accretion claim is an issuer statement to reconcile, not an input to force the model to match.

## Evidence scorecard

Scores are ordinal review judgments, not measured predictive accuracy. Scale 0 absent, 1 described, 2 partial, 3 locally reproducible, 4 independently verified, 5 integrated and observed in operation. Equal weighting is used only for this workstream audit.

| Dimension | Before | After this increment | Evidence / remaining gap |
|---|---:|---:|---|
| User objective and low-touch semantics | 3 | 4 | Frozen low-touch values and explicit timestamp precision |
| Source provenance | 2 | 3 | Dated source register, missing times remain null |
| Canonical persistence | 0 | 1 | Research retained, ticker data ingestion still owner-dependent |
| Pair synchronization | 2 | 3 | Tests reject mismatched times and sessions |
| EPS and dilution arithmetic | 2 | 3 | Direct share-count formula tested on synthetic fixtures |
| Forecast / fiscal comparability | 1 | 2 | Conflicted case suppresses target, quarterly alignment pending |
| Scenario and downside coverage | 2 | 2 | Plan covers break, delay, costs and multiple sensitivity |
| Reproducibility | 0 | 3 | Versioned input hash, deterministic CLI, nine local tests |
| Independent validation | 0 | 0 | B01 acceptance requested, no model CI proven |
| Ownership and integration | 0 | 2 | Dedicated branch, issue, isolated paths, draft PR |
| **Total / 50** | **12** | **23** | Research prototype only |

## Existing capabilities and reuse

Main inspected at b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95. Reviewed AGENTS.md, sparks.json, WORKER_PROTOCOL.md, compiled scopes and queue, live #136, relevant branches and 59 open PR changed-file lists. No observed collision with this new subtree. The first issue search incorrectly returned issues for an is:pr filter; switched to dedicated search_prs before completing collision review.

Reuse runtime/ticker_data.py and runtime/observations.py for canonical storage through B02, and #148 for resolver routing. Use #108/PR109 for descriptive traversal and historical replay. Existing #126/PR127 ETF valuation stays in its own subtree. B03 #12 owns canonical issuer events; B00 #180 already preserves MRVL–LITE event evidence. No duplicate scheduler, central queue, canonical price store or broad replacement engine is introduced. This small research calculator is an acceptance reference for later B04 integration.

## Ordered execution

| Stage | Owner and dependency | Deliverable | Acceptance / stop condition |
|---|---|---|---|
| M0 Correct and preserve | B04-189 | case.json, explicit withdrawal of target certainty, frozen low-touch baseline | Historical transcription labeled; no live claim or exact-trade timestamp invented |
| M1 Deterministic research math | B04-189 | model.py, test_model.py, SHA256 input identity | Nine tests pass; bad pair alignment and conflicting inputs suppress output |
| M2 Canonical daily replay | B02 with #148 routing | Locate existing MRVL/LITE stores first; one JSONL per ticker per exchange date; raw response/checkpoint receipts | Retry produces no duplicates; corrections append revisions; regular/extended separated; split basis declared; raw snapshot hash and coverage gaps returned |
| M3 Deal and estimates | B03 evidence and B04 evaluation | Approved terms, closing conditions, share classes, fully diluted shares, dated quarter-level GAAP/adjusted EPS and cash flow | Resolve 12.69 vs 7.25 MRVL EPS; prove standalone treatment; classify LITE two-estimate coverage; reconcile first-year accretion without double counting |
| M4 Full scenario bridge | B04 following M3 | CY2027 standalone and CY2028 pro forma, partial-year reported bridge, savings realization, integration cash costs, tax, financing, FCF and dilution | Income divided by explicit shares; quarterly periods align; terminal value and present value distinct; EPS/EV/FCF triangulation agrees or flags residual |
| M5 Paired traversal | B06 #108 following M2 | New session lows, retests, rebound from original and latest touch, synchronized spread, attribution and session VWAP | Real replay distinguishes low touch from close; last-price staleness and unmatched ticks fail closed; missing trades never fabricated |
| M6 Independent acceptance | B01 | Exact-head tests and real-data reconciliation | Test evidence names current SHA; source-ready data before live analytics; no skipped test counted as pass |
| M7 Operational observation | B02/B08 after integration authorization | Persistent entitled worker, restart/replay, retention and alert delivery receipts | Session-aware operation demonstrated; no operational claim from configured adapter alone |
| M8 Calibration | B07 after adequate history | Comparable merger/sector event study with costs, borrow, failed deals and holdout periods | Out-of-sample evidence before likelihood rankings or overshoot probabilities |

M0 and M1 implemented here. Later stages require owning-domain work and verified upstream inputs. Initial estimate was 8–14k tokens with low confidence; actual tokens and end-to-end efficiency remain unmeasured. Benefit is bounded to preventing demonstrated arithmetic, provenance and reporting errors.

## Consumer contract

Input prices carry ticker, currency, venue, observation timestamp, exchange session, adjustment basis and immutable source receipt. Price histories belong to B02. Output tracks original_low_touch, latest_session_low_touch, minute interval or actual trade timestamp, current_price, rebound_from_each, previous_session_low_delta, matched_pair_discount, coverage and validity. A single daily JSONL contains exactly one exchange date. Retain append-only corrections and never overwrite the original comparison anchor.

Forecast inputs carry source URL/class, retrieval time, available_at, effective_at, period start/end, basis, analyst count, dispersion, revisions, standalone/combined flag, dilution basis and confidence status. Unknown timestamps remain null and block point-in-time backtests. The prototype's explicit verification booleans are caller attestations, not an independent source verifier.

Scenario output carries model version, Git SHA supplied by the runner, input hash, USD, valuation date, forecast period, close date assumption, EPS, shares, multiple, present-value assumptions, costs and blockers. No recommendation or probability is emitted by the prototype.

## Model definitions and falsifiers

Combined adjusted EPS = (acquirer EPS * acquirer diluted shares + target EPS * target diluted shares + (pretax savings - incremental pretax costs) * (1-tax)) / (acquirer diluted shares + exchange ratio * target diluted shares). Use consistent same-period share and income bases. Other security conversions require an explicit extension rather than implicit approximation.

Merger spread = 1 - target price / (ratio * acquirer price). Rebound = current price / actual low touch - 1. At unchanged spread both equity returns match. Narrowing alone is insufficient evidence of buying; preserve component attribution. Standalone target earnings do not survive as a separately tradable equity after close.

Bear/base/bull is a sensitivity grid over earnings, multiple, costs, timing and completion outcome. Preserve a constant-earnings grid when the user assumes expectations hold. Deal-break downside must use independent standalone valuation, never assume a return to pre-announcement prices. Positive deal news can be outweighed by sector compression. Test sector-relative returns with COHR/CRDO and broader SOXX/QQQ, without claiming causality from correlation.

Relevant prior-art mechanisms are merger-arbitrage parity and carry, acquisition accretion/dilution accounting, event-time joins, point-in-time data with immutable revisions, event-study controls and walk-forward validation. Their concrete acceptance conditions appear above.

## Run

`python -m unittest discover -s research/models/mrvl_lite -p 'test_*.py' -v`

`python research/models/mrvl_lite/model.py research/models/mrvl_lite/case.json`

The real case deliberately returns blocked with null EPS/price. Synthetic tests prove calculation behavior independently of investment input readiness.
