# Premarket Update and Deltas operator

Worker B17 #265. This bounded operator reuses the integrated market-context engine from #100/PR101 and the research gates in #163/PR165. It supplies an invocation template and deterministic presentation helper. Scheduling and canonical ingestion remain separate dependencies.

## Invocation

`Update` and `Deltas` perform the same capture, persistence and analysis sequence. `Deltas` foregrounds changes since the previous successful observation. A ticker-qualified request narrows the display while retaining its benchmark context. Respect the user's latest explicit storage destination, including `NVDA.jsonl`.

Read current global AGENTS.md, the applicable domain scope and the task claim. Resolve the exchange calendar, session and real data root. Inspect a representative journal and its writer before fetching. Reuse the configured universe, the existing `engines/composites/market_context/context.py` refresh and freshness rules, and accepted provider adapters. Never manufacture a parallel canonical store when a root is unavailable.

Capture snapshots for the configured roles and minute or 15-minute aggregates for the core display. Append source observations through the authorized writer to resolved ticker journals before claiming a successful capture. Preserve source identity and corrections. Check duplicate-free replay. Source time must advance before a new capture counts as movement. Flag missing, stale, sparse and provisional observations. Preserve partial bars as revisions or explicitly provisional evidence. A 15-minute aggregate is not an individual trade or a one-minute bar.

Use fixed ET windows starting 04:00 PRE, 09:30 RTH and 16:00 AH. Label the developing window partial. Show actual high touches and window volume. Low-volume highs are observations rather than established resistance. Compare completed windows with completed windows.

Report current price and separate returns from prior regular close, prior AH final-minute close, previous successful snapshot, session open, session high and session low. Preserve each session anchor across transitions. Missing or incompatible baselines remain unknown. For 5/15/60-minute movement and group eligibility reuse the integrated engine's alignment, freshness and coverage rules. Report current eligible/expected counts. GOOG and GOOGL represent one issuer in breadth.

Check primary issuer releases, SEC filings, financing, export restrictions, supply-chain disruptions and scheduled official macro releases since the last successful check. Record publication, event, retrieval and first-known times. Quotes, rates, credit spreads and macro releases have distinct validity rules. Express yields and actual credit spreads in basis points. Treat HYG/IEF as price proxies. If a news or macro check was not executed, explicitly say not checked. Never interpret an ETF price as measured net inflow.

Classify separately by horizon: regular close versus previous close, current session versus its anchor, recovery from lows, and recent matched-window direction. Require breadth and benchmark confirmation to call a broad recovery. Prices alone do not establish forced liquidation, dealer hedging, causality or validated predictive probabilities.

## Fixed output template

1. Session, exchange date, as-of, timezone, source and one-sentence trajectory.
2. Delta table: ticker, current USD, prior-close %, prior-AH %, previous-capture %, distance from session peak %, recovery from session low %, source time/status.
3. Fifteen-minute high and volume matrix for NVDA, core ETFs and configured leaders, latest three completed windows plus partial window. Full session on request.
4. Supply-chain group breadth and medians with eligible/expected denominator; benchmark relative change in percentage points.
5. New material news and macro deltas with dated primary sources, or explicit unchecked/unavailable status.
6. Numeric confirmation/invalidation references grounded in observed ranges; persistence receipt and one Next step.

Retain source and report manifests with configuration version, input capture IDs, baseline IDs and checks. Never claim an installed `_LOOP` or running scheduler based on this operator template.

## Report helper

`python research/composites/premarket_operator/report.py --snapshot /path/snapshot.csv --bars /path/bar-directory --as-of 2026-11-13T13:24:35Z`

The directory holds `<TICKER>.csv` Massive 15-minute aggregate responses. The helper computes presentation math and filters PRE windows. It does not establish entitlements, verify freshness, append canonical observations, check news, or implement traversal. Those steps are required by the operator. Unknown baselines remain absent. Configured leaders are a watchlist rather than a current market-cap ranking.

## Acceptance

Use a captured response to verify prior-close and peak math, partial window labels, exact 15-minute boundaries, and missing ticker output. Check the task claim against the existing worker-task schema. Independently qualify the writer and duplicate/revision behavior through B02. Current publication is a draft until applicable review and CI gates are verified.
