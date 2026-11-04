# Codex / B00 Orchestrator — Two Specialized Workers (read first, dispatch without duplication)

**Repository:** https://github.com/whiterosecoffee/_BASKET
**Source issue:** https://github.com/whiterosecoffee/_BASKET/issues/155
**Source branch:** `work/155-market-flow-watch-review` (B06-owned planning documentation)
**Other owner:** https://github.com/whiterosecoffee/_BASKET/issues/126 and draft PR #127 (B04)

## Objective
Maintain two **separate** reusable tools:
- **Worker A: Current Market Vector Tracker (B06)** — synchronized 1/5/15/30/60-minute market vectors, QQQ/SPY and NDX/SPX relative leadership, semiconductor/hyperscaler breadth, rolling 5/20/60/200-day and intraday new highs/lows, VWAP, price-per-volume displacement, participation and versioned confirmed state transitions. Material-change alerts only.
- **Worker B: Ticker Forward Financial Evaluator (B04)** — 2027/2028 fiscal/calendar earnings, cash-flow, leverage and dilution bridges, conservative terminal-multiple stress, downside/return sensitivity and conditional entry scoring using read-only Worker A signals. Includes NVDA, CRWV, COHR, MRVL, LITE, INTC, AAOI, CRDO, ALAB.

## Mandatory source-first reconnaissance
Read `AGENTS.md`, `orchestration/sparks.json`, current `architecture/**` version contracts and these three design files from B06 PR; read all relevant current issues, PR diffs and live branches before claiming files. In particular inspect B02 PRs #15/#153, B06 #109/#145/#150/#160/#168, B17 #101, B04 #127, B01 #129, B08 #55, migration #148 and orchestrator queue #136. GitHub main is implementation authority; a draft is not merged.

## Dispatch protocol
1. Reconcile this proposal with existing #155 and #126. **Do not create duplicate B04/B06 branches** or launch inactive workers preemptively. Activate only already-authorized workers with exclusive file paths; create source-linked handoff issues if domain owners must receive work.
2. Keep B02 data ingestion and history independent of B06 calculations. Keep B04 fundamentals independent of B06 market vectors. Cross-domain shared schema changes go to B00; independent CI and point-in-time replay to B01.
3. First delivery = B06 deterministic replayable high/low + percentage vector + fail-closed regime event; B04 9-issuer coverage matrix + tested break-even-EPS and multiple-compression scenarios; neither requires an always-on process.
4. Use earliest validated blocker order; verify historical/data entitlement and timestamp support. Make a proposed dependency graph, explicit I/O interfaces, acceptance IDs and exact write paths. Publish a concise plan in the **existing orchestration issue #136 or authorized B00-owned paths** only after ownership reconciliation; do not overwrite competing B00 PRs.
5. Implement within actual owner branches, run domain tests and request B01 exact-head CI, open/update draft PRs; NEVER merge, release, tag, or deploy without explicit user authorization.

## Success measures / prohibitions
- Source verified current snapshots and past bars; fail closed for stale/conflicted/unsupported index/market data. Historical flow/tick retention only if verified durable storage.
- Observed percentage moves vs prior close and prior snapshot, explicitly named windows, not dollar price deltas. 52-week / session / 5-20-60-200-day high/low detection with dedupe.
- Market vector events versioned, threshold/hysteresis and invalidation reproducible; no notifications for unchanged conditions or absent source data.
- Valuation grounded in sourced forward EPS and FCF with dilution, financing, fiscal/calendar labels, alternative merger states. No invented multiple justification, weights, probabilities or terminal return accuracy.
- Each deliverable links issue, source commit, tests actually run, missing dependencies, and next owner action.

**First action:** Independently confirm actual GitHub main/PR state and return a two-worker dispatch map (owner, reused module, exact paths, dependencies, blocker, measurable acceptance) before any additional implementation.
