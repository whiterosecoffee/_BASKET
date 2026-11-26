# P02 — Visual Range, Volume and Nested Comparisons

**Status:** actual offline UI implemented in a different B06 branch; this node is a reference, NOT another UI. **Owner:** B06 #144, draft PR #145, branch work/144-october-compression-stress at feaff2a6a72c09a36f425d309bcb8859c971aab4.

## Problem
A single price line hides revisits, zones of participation, nesting across horizons and the difference between directional velocity and movement per share. The user wants the attractive interactive comparisons preserved for future analysis, without losing the underlying methodological limitations.

## Source and visual contract
Open PR145 path research/traversal/october_2026_compression_stress/presentation. Its index.html and controller.js drive the eight selectable views (Rails, Ribbons, Threads, Heatmap, Nested Profiles, Compression/Expansion, Swing Structure, Movement/Shares & Turns), selectable Premarket/5/21/63/252 session backdrops, earlier/later navigation and granularity/slices controls. zones.js/context.js provide Zone Participation and Nested Context matrices. Turn Episodes is an unimplemented design in MATRIX_DESIGN.md.

Inputs: qualified, timestamped OHLCV/VWAP observations, ticker/session/basis, selected window and fixed USD price zones. Outputs: descriptive chart and a single selected matrix; no provider fetch/stream, no trade advice or calibrated trend odds. Context and display must share as-of and source basis; normalization and source gaps are visible.

## Quality risks
Whole-minute VWAP allocation is a sample estimate, not true traded-at-price dwell; bar volume is unsigned. Profiles normalized individually cannot show absolute turnover differences; overlapping timeframes do not create independent evidence. A pivot confirmed 3 bars later must be dated at confirmation. Invalid intervals and future bars cannot be silently joined. Mobile/desktop displays should match numerical calculations.

## Smallest next action
Fresh session reads pinned HTML/JS/docs/tests and compares them to any original chat-rendered screenshots, marking exact identity verified/unverified. B06 #144 owns all UI changes; no copy to #154. If later adding SMA state overlay, require B00/B02 approved common as-of data contract.