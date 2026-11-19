# NVDA quantity eligibility — provider evidence and local characterization

Amends the earlier broad quality blocker in #185/#152; research policy only, not an approved B02 production rule. Algorithm `nvda-recovery-preflight@0.2.0` adds session counts and explicit interpretation while retaining every original record and warning. Original v2 ZIP and its hashes unchanged.

## Provider evidence checked 2026-11-04

- [Massive stock VWAP eligibility](https://massive.com/knowledge-base/article/how-is-a-stock-bars-vwap-calculated-and-why-can-it-fall-outside-the-high-and-low): volume/VWAP can include trades excluded from bar high/low. Therefore VWAP outside high/low alone does not establish an error. Minute VWAP aggregation is not automatically identical to daily VWAP.
- [Massive fractional volume](https://massive.com/knowledge-base/article/why-does-volume-return-as-a-decimal-value-from-the-aggregates-endpoint): fractional-share trading contributes fractional volume; preserve decimal quantities rather than truncating them. This is separate from the adjustment flag.
- [Massive eligibility rules](https://massive.com/knowledge-base/article/how-does-massive-create-the-open-high-low-close-volume-aggregate-bars): trade condition metadata and session-specific treatment determine which statistical fields update. A single generic condition filter is insufficient for every session.

These are provider methodology statements, not an independent reconstruction of each captured NVDA minute. No individual trade-condition reconciliation has been performed here.

## Observed local results

Input: the immutable v2 package manifest referenced in manifest.json; eight daily sessions,7,437 bars. All eight dates have390 regular minute observations.

| Session scope | Bars | VWAP outside high/low | Interpretation |
|---|---:|---:|---|
| Regular | 3,120 | 34 | 1.09% of regular bars; not standalone corruption |
| Extended combined | 4,317 | 1,252 | 29.00%; different eligibility/liquidity context |
| All | 7,437 | 1,286 | Counts are this capture vintage, not the earlier #152 frozen pilot |

Preserve the earlier report and its864 flags as a separate source vintage. Do not overwrite or silently relabel that snapshot to the current1286 count. A comparison needs corresponding source hashes and logical observations, not aggregate counts alone.

## What analysis is supportable

| Quantity | Research use now | Limit |
|---|---|---|
| OHLC extrema and close path | Descriptive aggregate observations | Source-defined price eligibility; not every executed trade or official close |
| Bar volume | Preserve reported fractional values | Not unique holders, aggressor imbalance or OI changes |
| Provider minute VWAP | Retain with eligibility label | Do not reject or clip solely for crossing OHLC; per-bar provenance remains necessary |
| Sum(volume × provider VWAP) / sum(volume) | Approximate volume-eligible minute-window VWAP if inputs otherwise qualified | Declare rounding, interval, session and source vintage; not an official daily VWAP |
| Volume at exactly $200 or a narrow price band | Unavailable from minute bars | Requires trades, decimal sizes, cancellation/correction handling and matching eligibility rules |
| Hedge pressure/dealer inventory | Not established by these aggregates | Separate licensed options observations and verified normalization required |

No blanket instruction to discard the1286 bars or block all dollar-weighted research remains justified solely by the out-of-range flag. Conversely provider documentation does not certify every bar, quote freshness, exchange completeness, correction state or exact-price execution profile. B02 still owns production acceptance and representative trade reconciliation.

## CI distinction

At head e2a63130ff454f618b06c7832e3be8e375037ff2, [shared workflow41935622943](https://github.com/whiterosecoffee/_BASKET/actions/runs/41935622943) passed. Its worker-qc job126943218921 runs orchestration tests and independent integration tests; stores job126943219306 validates stores. The workflow does not explicitly discover this research directory. No independent execution of this research suite is established by that green run.

32 research tests now pass locally, including preserved legitimate out-of-range VWAP and fractional volume, no exact-price profile inference, and the earlier structural/semantic rejection cases. B01 receiver command after checking the latest PR187 head:
`python -m unittest discover -s research/NVDA/data-recovery/2026-11-04 -p 'test_audit.py' -v`

One next owner action: B02 receives this documented eligibility distinction under #152 and specifies canonical permitted measures; B01 independently runs the exact-head research command without this B14 worker changing shared CI.
