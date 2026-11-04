# Band method (shared by TODAY, 72H and 10D)

Vector: how a narrow touch band is found, counted and described. Window files supply the bar set; this file supplies the procedure.

## Inputs
- A bar set from the window file: first and last timestamp, bars used, bars missing versus the session calendar.
- Method parameters below, printed with every result as method and version.

## Procedure
1. Range: high, low, midpoint, last close, position in range = (last - low) / (high - low), return from the prior close. Reproduce `engines/traversal/range.py` outputs for the daily series where the repo data exists.
2. Band finding: locate price zones touched repeatedly. Band width is a parameter; v0 default is 0.25 times the median true range of the bars used (5-minute true range for TODAY and 72H, daily true range for 10D).
3. Distinct touches: an excursion counts once. Price must exit the band and reset before the next touch is counted.
4. Per band report:
   - lower and upper endpoint in USD, pivot
   - distinct touches and last touch time
   - rejection distance in USD: the move away from the band after each touch
   - dwell seconds: time spent inside the band
   - break and retest status
   - invalidation level
5. Dollar volume per band, with the method named:
   - exact: sum of price times size, needs tick data
   - bar aggregate: bar VWAP times volume
   - estimate: close times volume, labeled as an estimate
   Volume of bars touching a band is not exact volume inside it. Overlapping bands are not additive.
6. Regime for the window: balance, trend_up, trend_down, expansion, event_dislocation or unknown. Never force a chop label. Use unknown when evidence is insufficient.
7. Rank bands by dollar volume, then by distinct touches.

## Output fields (match the tracker traversal panel)
lower_band, upper_band, pivot, regime, distinct_touches, last_touch_at, rejection_distance_usd, dwell_seconds, break_retest, invalidation, volume_method. Each zone also carries session, lookback, method and version, and source revision IDs.

## Failure modes
- A first-bar low treated as support.
- Overlapping touched-bar volumes summed.
- A breakout retest counted as a new band.
- Extended-hours bars inside regular-session bands.
- Stale latest bar: label NON-ACTIONABLE.

## Open parameters
- Width multiplier (0.25 times median true range) is uncalibrated.
- Dwell threshold for a valid band.
- Minimum distinct touches for a band to be reported (v0: 2).
