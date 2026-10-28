# Battle-band traversal matrix
2026-10-28. B10 research prototype for shared B06 promotion. No persistent scheduler/live worker is deployed.

## One directional score centered on 1
For a fixed corridor of width W, bar close movements clipped to that corridor are normalized as travel/W.
Use the last 15 completed regular-session minutes; exponentially decay weights with 5-minute half-life.
For direction d:
E_d = sum(w * directional normalized travel) / (sum(w * assigned dollar turnover) / ADDV20).
Score S = E_up / E_down.
S=1 balances observed directional efficiency; S=2 means upward travel is twice as efficient; S=0.5 means downward travel is twice as efficient.
It is NOT probability, net order flow, net trend, resistance strength or expected profit. Preserve net displacement separately.
ADV20/ADDV20 and corridor width cancel algebraically in S; do not multiply by them again to manufacture a volume-sensitive bias. Dollar turnover and recency already weight the directional comparison.

## Persistent matrix row
ticker | session | zone_id/version | lower band | upper band | as_of/cutoff |
bar-assigned corridor shares/$ turnover | lower-band and upper-band assigned shares/$ |
volume as %ADV20 | dollar turnover as %ADDV20 | same-time RVOL if available |
S_15m | previous nonoverlapping S_15m | change | S_5m if sufficient |
range position | net displacement | per-side count/effective N | quality/freshness.
Unknown scores are null, not 1. Default publication needs >=3 qualifying bars per direction and effective N>=2 per side; these are conservative engineering gates, not calibrated confidence levels.
Range positions may exceed [0,1] for breakouts. Lack of current data does not imply score=1 or no breakout.

## Volume and range limitations
Dollar turnover is bar VWAP * shares, gross, not buying/selling cash.
A bar belongs when its VWAP lies in the corridor. This deliberately labels entire-bar assignment, NOT precise volume-at-price.
Lower/upper cluster volume uses the same approximate membership.
Close movement is clipped at corridor bounds; this does not reconstruct intrabar path.
Neutral bars contribute corridor turnover but no directional numerator/denominator; preserve their turnover separately.
Overlapping corridors are non-additive. Do not sum their volumes.
Bands are supplied/frozen before evaluation. Prototype fixture uses low/high quantiles from the first 15 minutes, frozen at 09:45; they are provisional corridors, not verified support/resistance clusters.
Independent touch counts, completed-leg first-passage records, acceptance-after-breakout statistics and automatic cluster detection remain B06 follow-on work. Consecutive candles cannot be treated as independent tests.
The current research fixture cannot verify the later user-reported hold above $60. Preserve it as a user observation pending entitled fresh market data.

## Volume overlay
ADV20 is arithmetic mean share volume over the preceding 20 completed sessions.
ADDV20 is arithmetic mean daily VWAP * shares over those same sessions.
Percent ADV shows consumption of normal daily volume; it is NOT same-time RVOL.
Same-time participation requires a historical minute profile on the same session convention. It remains null in this fixture; no uniform 390-minute interpolation.
Falling participation plus strong upward efficiency may indicate thinning supply, not a surge of buyers.

## Reproduction
From this directory:
python -m unittest test_battle_matrix -v
python battle_matrix.py matrix-input-2026-10-28.json --out matrix-output-2026-10-28T1416Z.json --history battle-matrix-history.jsonl

Input data: Massive minute bars and prior daily aggregates for CRWV and ORCL, retrieved 2026-10-28 around 14:31 UTC. Common output cutoff 14:16 UTC / 10:16 ET. Delayed approximately 15 minutes. Not a current quote.
Fixture requires USD and consistent split-adjustment. Canonical ingestion belongs to B02.
Twelve local tests cover directional interpretation, dollar-volume weighting, price/share-scale invariance, multi-ticker separation, prefix replay, insufficient samples, missing baseline, freeze dates, duplicates, turnover reconciliation, idempotent append and revised snapshots.
Input/algorithm hashes identify immutable snapshots. Repeated identical append is a no-op; revisions link to prior same-cutoff snapshot. Outputs are dated snapshots, not an automatically maintained database. File append is single-writer; production concurrency/atomic append stays with B02/B08.

## Integration
Current code/tests/fixtures live only in B10-owned research/CRWV/debt/2026-10-22/**.
B00/B06 should adopt the generic calculator and zone lifecycle in shared traversal, B02 provides entitled observations/profile, B07 validates thresholds/probabilities, B08 persists/schedules/presents, B01 adds exact-head CI.
Reuse dependency #70. Do not unilaterally write shared engines, contracts or runtime.
No model fitting, performance probability or trading recommendation is produced.

