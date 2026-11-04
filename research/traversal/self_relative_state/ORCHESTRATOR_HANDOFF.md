# _BASKET B06 #154 — Orchestrator transfer and archive gate

**Repository:** whiterosecoffee/_BASKET  
**Issue:** https://github.com/whiterosecoffee/_BASKET/issues/154  
**Draft PR:** https://github.com/whiterosecoffee/_BASKET/pull/160  
**Worker branch:** `work/154-self-relative-historical-state`  
**Spark:** B06  
**Permitted writes:** `research/traversal/self_relative_state/**` only  
**Status:** research deliverables persisted in draft PR; **not merged or integrated**.

## Durable conversation decisions and motivation

The initial seed was the use of 10/30/200-day moving averages to measure how a ticker performs relative to its **own** history, rather than solely compare it with an index or visually interpret chart support. The more general research object is a point-in-time *self-relative state vector* with price-to-average displacement, volatility-normalized unusualness, MA slope, cross-horizon disagreement, persistence, approach speed, and historical conditional event outcomes. The objective is **incremental evidence** beyond B06 traversal, not a second engine or a promise of predictive alpha.

User-resolved selections:
- **Primary goal:** incremental information beyond already available metrics.
- **Historical lookback:** recent **200–500 completed daily sessions**; explicitly handle post-warmup shortages and CRWV's potential inability to support SMA200.
- **Handoff policy:** research artifacts first; do not implement production state calculation on #154 branch.
- **Ownership:** preserve exactly one existing issue #154, branch `work/154-self-relative-historical-state`, and existing draft PR #160. Do not open a duplicate B06 worker.
- **Release:** never merge without explicit authorization. Never describe a draft PR as merged, deployed, calibrated or live.

## Committed materials to read in order
1. `README.md` — capability overlap, owner boundaries and scope.
2. `RESEARCH_CONTRACT.md` — proposed daily inputs, temporal invariants, definitions, nulls and noncanonical experimental shape.
3. `VALIDATION_AND_HANDOFF.md` — M0–M5 test ladder, experiment design and receiver prompt.
4. `PAIRED_REPLAY.md` — separate traversal-only controlled comparison and synthetic mechanism check; retained as research, execution not claimed here.
5. This file — final transfer, evidence and archive gate.

## Verified dependency and collision map

| Domain | Existing source | Why reuse / what remains |
|---|---|---|
| B06 | PR #109: `engines/traversal/metrics.py` | Intraday observed ranges, turnover and path efficiency; do not duplicate |
| B06 | PR #145: `research/traversal/october_2026_compression_stress/**` | Event morphology, prior art, range transitions; reuse vocabulary |
| B06 | PR #150: `engines/traversal/market_geometry/core.py` | Synchronized intraday geometry and relative return ratios; do not duplicate |
| B10 | PR #99: `research/CRWV/trading-tool/**` | Minute consumer, event journal and poller; do not fork |
| B17 | #100 / PR #101: `engines/composites/market_context/**` | Context; proposed daily comparable windows are not proven implemented |
| B00/B02 | #148 / PR #147 | `_TICKERS` scope folders are *not* migrated history or authoritative resolver implementation |
| B00 | #103 / PR #104 | Shared component standards and schema approval; #154's research JSON is not canonical |
| B07 | #93 | Historical outcome validation and calibration |
| B01 | #98 | Independent exact-head integration checks |

Targeted handoff requests were posted to existing issues #148 (B00/B02), #103 (B00), #93 (B07), #100 (B17) and #98 (B01). Do not interpret comments as claims of receiver acceptance.

## Verification evidence and limitations

At PR head `1d3c5985c861d88d2a7abd14e4aca8bfd0bff384`:
- GitHub branch and draft PR confirmed; **five** added files at the currently inspected head, all inside owned research subtree (including `PAIRED_REPLAY.md` from a separate research update).
- GitHub workflow `Validate BASKET data`, run **41762058583**, returned `completed/success` for this commit.
- No empirical historical-source replay, no M0–M5 statistical performance results, no new live engine, no new public-market history, no approved shared schema.
- GitHub validation on this research branch is not evidence that downstream interfaces are integrated or production-ready.
- Latest inspected PR head `fd7144f10b21f2ef2e225017ae76fb970ab55493` passed GitHub Actions `Validate BASKET data` run `41762449382`; this verifies repository checks only. A subsequent edit changes the head; recheck exact-head workflow before final claim.

## Archival and integration criteria

Conversation context is no longer required to **reconstruct research intent** because decisions, architecture boundaries, testing protocol, handoff routing and blockers are persisted in PR #160. But the user's stronger **archive-ready** standard is **only after GitHub integration is verified**.

The orchestrator must verify, in order:
1. B00 has reviewed and accepted or explicitly rejected/composed each research contract, with issue/PR evidence.
2. Draft PR #160 is merged **only after explicit authorization**, or any consciously rejected/closed outcome is fully recorded with disposition and migrated essential knowledge; no silent cancellation.
3. The appropriate target branch/main commit and CI evidence are checked after authorized integration (passing branch CI alone is insufficient).
4. All downstream tasks remain tracked in GitHub issues with exact receiver, scope, acceptance and blocker states.
5. A dated final `basket.worker_resolution@1` response references the issue, PR, integrated SHA (if any), CI run, test status, changed paths and outstanding work.

**Current archival disposition:** `handoff_ready=true`; `integrated=false`; `archive_ready=false`. The orchestrator, not a future chat-memory inference, must change the archive verdict on verified evidence.

## Ready-to-paste orchestrator prompt

> **_BASKET B06 historical self-relative state — reconcile, integrate and verify (#154 / PR #160).** Read live GitHub main, `AGENTS.md`, `orchestration/sparks.json`, issue #154, draft PR #160 and its five files in `research/traversal/self_relative_state/**`. Confirm PR head, changed paths, ownership, workflows, comments and related open PRs before action; preserve existing issue/branch and do **not** create a duplicate B06 worker. User choices are **incremental information**, **recent 200–500 completed daily sessions**, **research-only handoff**. Resolve conceptual overlap with B06 PRs #109/#145/#150 and B10 #99; compose a small daily historical-state contract rather than another traversal implementation. Respect B00 #103 component/schema ownership; coordinate B00/B02 #148 resolver/data migration, B17 #100 same-horizon context, B07 #93 held-out event discrimination and B01 #98 independent CI through existing owner issues, not cross-domain writes. Preserve completed-session, as-of/available/ingested/revision identity, adjusted-price/FX basis, 200D warmup and failure-to-observe semantics. Test incremental value using predeclared M0–M5 benchmarks and chronological overlap-controlled replay; reject unvalidated probabilities and fabricated CRWV 200D. Review draft PR #160 and its validation, request any scoped corrections through its owner, and never merge without explicit authorization. Do not claim main integration, release, live execution, or archive readiness on a draft. Report source-verified state, accepted architecture, owned paths, dependency order, unresolved evidence, issue/PR/CI URLs and `basket.worker_resolution@1`; mark this conversation **archive-ready only after authorized integration and main CI are verified**, otherwise preserve an explicit blocker and next owner action.

## Required next orchestrator action
Review PR #160 against current main and B06 active drafts, route B00 interface arbitration and #148 data resolver dependency, and report an explicit non-archive-ready status until integration is actually verified.
