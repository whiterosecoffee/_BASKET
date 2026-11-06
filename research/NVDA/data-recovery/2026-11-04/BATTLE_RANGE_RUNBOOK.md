# NVDA battle ranges and momentum

B14 research runbook v1. Use this on each **NVDA battle ranges** refresh. Canonical traversal stays with B06 (issues #144 and #108, PRs #145, #109 and #150). Use the existing B02 journal and ingest path.

## Refresh

1. Record date, session, as-of time in CT, latest completed minute and adjustment basis. Keep premarket, regular and after-hours volume separate. Sum regular-session Massive minute-bar shares from 08:30 CT to the latest completed minute, show prior-session same-clock change, and label the total session-to-date. Report final daily volume separately from the vendor daily summary after close. A 20-session same-clock median is the preferred baseline when eligible history is available. Show coverage and comparator count.
2. Refresh the date-specific append-only NVDA minute journal with the existing importer. Keep complete five-minute windows aligned to the clock. Pull SIP trade pages until the cursor ends, using half-open time windows and $0.25 price bins. Sum decimal size where available. Rank bins by shares, tie-break at the lower price. Keep bar volume separate from raw reported-trade size and retain the queried interval, page count, provider and flags. Flag isolated off-range prints rather than using them to extend a zone.
3. Compare the latest three completed windows. Use adjacent populated bins around the mode to describe the observed trading pocket and report exact endpoints, shares and mode. Freeze the active range used for confirmation. Record any new range as a new observation, preserving the previous boundaries. One completed five-minute close outside the active range is a probe. Confirm SHIFT UP or SHIFT DOWN when a second consecutive close stays outside the same edge or a fully paginated modal bin migrates outside that edge in the direction of the break. If trade coverage is incomplete, use two completed closes and label the result bar-only. Do not use a partial bar window for confirmation.
4. For each completed window calculate signed dollars per minute and signed dollars per million shares from the prior window close. Compare the move with same-clock turnover, the previous window and the opposite leg. Track mode migration and concentration, close versus the range, failed reclaims, and relative return versus SMH and QQQ at matching timestamps. Record HIRO and strike OI separately if timestamped. High turnover with weak price progress is a possible absorption signal. Require a held retest or reclaimed swing before calling a reversal. Treat these as descriptive factors until validated out of sample.
5. Report one line for the session price and volume, then a short table with window, close, total bar volume, price-band shares, modal bin, signed dollars per million and state. Record the next invalidation and the data cutoff. Use fresh observations for every refresh and preserve missing values explicitly.

## Worked example — Nov. 6, 2026, 10:11 a.m. CT

Massive unadjusted bars cover 101 regular-session minutes through the 10:10 bar. Session volume 65.35M shares versus 111.92M on Nov. 5 at the same cutoff, down 41.6%. The prior session was a selloff comparator, with no typical-volume inference. Latest price $188.275.

| Window CT | Close | Bar shares | SIP modal bin and shares | Signed USD per 1M bar shares |
|---|---:|---:|---|---:|
| 09:55–10:00 | 189.5296 | 1.290M | 189.75–<190.00, 486K | −0.02 |
| 10:00–10:05 | 188.8600 | 1.379M | 188.75–<189.00, 497K | −0.49 |
| 10:05–10:10 | 188.4500 | 1.216M | 188.50–<188.75, 637K | −0.34 |

Each trade window exhausted its cursor on the first page. The 10:05 close and modal migration confirmed a move below the prior 189.25–<190.25 range. In the latest window 1.164M shares traded in 188.25–<188.75. The second close remained outside the old range while downside movement per share slowed. The 10:10 minute is a partial-window observation. Raw provider rows remain in the local workflow.

## Live tape matrix v1.1

Ask **which direction costs more shares per dollar, how active is the tape for this time of day, and did price gain acceptance at a boundary?** Keep the three readings separate. The cost is descriptive turnover, not dollars spent by buyers or sellers and not causal market impact.

### Fixed-window measurements

- Use completed, clock-aligned five-minute windows within one session. Use the preceding minute close as start, except at the regular open where the first eligible open starts the first window. Never mix opening or closing auction windows into an ordinary intraday comparison. Show partial windows separately and exclude them from shift confirmation.
- Let d = end close minus start, V = bar shares in millions, and path = sum of absolute consecutive one-minute close changes, including the start. Report signed speed d/5, signed ease d/V, and directional cost V/abs(d) for material moves only. Report near-flat when abs(d) is below a predeclared noise floor. Pilot floor is 5 basis points of the starting price, explicitly uncalibrated. Invalid prices, coverage gaps or nonpositive volume make the comparison unavailable. Coherence = abs(d)/path where path is positive. Low coherence flags back-and-forth or a retrace within a window.
- Participation = shares divided by the median for that same five-minute slot across the preceding 20 eligible sessions. Show the comparator count and use unavailable when 20 are not present. Show prior-window volume change separately. Keep cumulative regular-session turnover separate. Report matched-window returns versus SMH and QQQ as context without treating either as independent proof.
- For directional cost compare the nearest completed opposite-direction window in the same session and within the previous six five-minute slots, excluding near-flat and auction windows. Report both timestamps, up and down cost, and which moved more easily. If there is no eligible pair, show the available direction only. High or low ease is relative to that comparator. Participation above or below its median gives context; no calibrated significance threshold is implied.

### Read the combination, then check the boundary

| Ease of directional movement | Above typical participation | Below typical participation |
|---|---|---|
| Higher | Directional momentum candidate. Check close and retest. | Price traveled readily. Check whether follow-through survives heavier trading. |
| Lower | Possible resistance or absorption at a tested boundary. Check rejection, recovery and path coherence. | Muted move. Wait for a meaningful test. |

At similar readings or missing participation, describe the measured change without assigning a quadrant. Repeated high turnover and low progress followed by rejection at the upper edge is consistent with supply capping the move. The mirror image at the lower edge is consistent with demand supporting it. Confirming aggressive side or replenishment requires eligible trades matched to contemporaneous quotes, with unknown classifications kept separate. Report that evidence independently from bar turnover.

Use separate states: **ease flip** when the cheaper direction changes across eligible pairs, **probe / confirmed shift** under the existing five-minute close and modal-bin rule, and **reversal candidate** when a countertrend push is followed by a defended retest and a break of the prior countertrend swing. A fresh failure of the defended retest invalidates that candidate. A single efficient bar does not establish directional persistence. Report price-bin migration as unavailable when trade pagination is incomplete. Keep threshold and state versions with the input cutoff for replay. Before estimating predictive odds, validate by session type on time-ordered out-of-sample data.

### Nov. 6 worked tape read

10:30–10:35 CT rose $0.76 on 1.667M shares, costing 2.19M shares per dollar. 10:35–10:40 gained only $0.0191 on 1.393M and is near-flat under the pilot rule. The partial 10:40–10:44 drop lost $0.8991 on 0.735M, costing 0.82M shares per dollar. It is provisional and ineligible for the paired state. The confirmed observations are upward progress stalling near $189.45 and a subsequent partial decline to $188.29. Recheck the completed downside window and whether $188.25 holds before classifying a range shift.
