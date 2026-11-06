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
