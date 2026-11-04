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

---

## Conversation intelligence closeout — basket.conversation_handoff@2 (2026-11-04)

**Protocol source:** B00 draft `orchestration/conversation_closeout/HANDOFF_PROMPT.md` from `work/169-conversation-closeout-cli`; this is a research worker's closeout application, not a new canonical orchestration policy. Full available conversation reviewed; no raw transcript export asserted beyond this conversation. Project policy remains in AGENTS.md and the versioned registry.

### Obligation ledger (as last checked; refresh live before action)

| Deliverable | Owner | State | Evidence | Remaining criterion / smallest action |
|---|---|---|---|---|
| Reframe 10/30/200 toward self-relative history | B06 #154 | Recorded | README + RESEARCH_CONTRACT | None for research handoff |
| Feature definitions, temporal guards, sparse-history behavior | B06 #154 | Recorded, experimental | RESEARCH_CONTRACT | B00 #103 approves/rejects eventual shared contract |
| Nonduplicating inventory and owners | B06 #154 | Recorded | README; PRs #109/#145/#150, #99/#101 | B00 integration sequence; no competing engine |
| Incremental M0–M5 plan and paired controlled test | B06 #154 | Specified | VALIDATION_AND_HANDOFF + PAIRED_REPLAY | Empirical event replay after canonical data/labels |
| Synthetic mechanism and data inventory | B06 #154 | Mechanism reproduced; empirical claims withheld | PAIRED_REPLAY; PR #160 narrative and cited hashes | No implication of measured historical lift |
| History, baseline/event cohort, calibration and independent integration | B00/B02 #148; B06 #144; B07 #93; B17 #100; B01 #98 | Transferred/blocked | Linked owner issue comments | Each owner supplies accepted contract/evidence on its own branch |
| Draft PR package | B06 #154 | Committed, not merged | PR #160, five owned research files | Explicit authorized PR disposition; verify relevant main CI if integrated |

### Reusable knowledge units (mechanism, alternatives, evidence and destination)

1. **Self-relative location is not a support signal.** A 200-session moving-average line is a coordinate, not verified liquidity. Mechanism: compute completed-session position and slope, then normalize deviation to the instrument's own volatility and past-only displacement distribution; persistence/approach speed disambiguate superficially similar contacts. Application: the March-versus-November QQQ 200D visual comparison is a *hypothesis generator* only. Alternative rejected: label every MA touch a defended support zone. Falsifier: equal-alert-coverage held-out classifier does not improve versus the traversal-only control. Destination: B06 RESEARCH_CONTRACT / B07 #93. Families: time-series momentum, statistical process control, robust ranks; **PIT**, **FALS**, **REPRO**.
2. **A state vector should preserve orthogonal evidence.** Trend direction, MA displacement, range efficiency, volume participation, synchronized market-relative returns and resolution are different observations. Collapsing them to one uncalibrated numerical score destroys interpretability and can double count price movement. Mechanism: small composable typed outputs with `as_of`, source manifests and missingness, joined only after consent to an accepted contract. Application: daily MA30 slope supplements #109 price-volume efficiency; #150 short-window geometry stays distinct from B17 factor/context comparison. Alternative rejected: second stand-alone combined traversal engine or arbitrary weighted “reversal probability.” Destination: B06 #108/#154, B00 #103. Families: **MOD**, **HEX**, **DBC**, observational feature engineering.
3. **An incremental test must hold the denominator fixed.** Adding an indicator can appear valuable merely because it filters harder or uses different dates. Mechanism: freeze #145 episode IDs, labels, horizon, temporal eligibility, threshold policy, same event population and identical alert coverage. Compare #109 baseline twice, once with **only** five-session SMA30 slope added. Keep unresolved/censored and simultaneous/ambiguous-bar outcomes as explicit cases. Measure per-class precision/recall deltas, false reversal confirmations, delay and uncertainty; purge overlapping episodes and split chronologically across tickers. Application: proposed paired study in PAIRED_REPLAY. Alternative rejected: cherry-picked March/November examples or success percentages derived from disjoint cohorts. Falsifier: no stable improvement on independent holdout; prefer simpler baseline. Destination: B07 #93, B06 #144. Families: matched event studies, time-series cross-validation, multiple-testing/data-snooping control, **FALS**.
4. **History quantity does not equal point-in-time eligibility.** A 500-bar window gives at most 301 SMA200 distance values; a 252-prior-distance percentile needs at least 452 completed closes. Legacy CRWV rows may exist while historical `available_at` or correction provenance is unknown, making retrospective features ineligible for strict as-of replay. Mechanism: resolve instrument and calendar, enforce session completeness, adjustment consistency, availability/revision timestamps and immutable input hashes; use null and explicit exclusion reason otherwise. Application: PAIRED_REPLAY's documented QQQ/NVDA/CRWV inventory; no canonical three-symbol historical replay yet. Alternative rejected: silently synthesize young-security MA200 or treat later-recovered NVDA minutes as earlier available. Destination: B00/B02 #148, B02 #152, B01 #98. Families: **PIT**, bitemporal provenance **PROV**, **EVS**, fail-closed contracts.
5. **Reuse first; distinguish semantic differences, not just similar labels.** #109 signed open-to-close progress divided by close-to-close dollar path is not automatically interchangeable with #145 absolute-log path efficiency; #150 must be provided calendar-bounded RTH `range_start` before claiming in-session extrema. Mechanism: version definitions, adapters and transformations; compare exact implementations before joining. Application: B06 PR #109/#145/#150 integration. Alternative rejected: same-named measures assumed equal or arbitrary prior-session fill. Destination: B00 #103 and B06 #108. Families: **DBC**, **MOD**, **REPRO**.
6. **Synthetic mechanism proof is not observed empirical lift.** Reordering identical price sets changes MA30 slope while leaving some range/notional and longer MA displacement features fixed. This proves the slope adds a distinct *measurement*, not independent discrimination after #109 efficiency or a trade advantage. Mechanism: synthetic unit fixture establishes arithmetic and null boundaries; later historical paired replay establishes (or falsifies) incremental value. Application: PAIRED_REPLAY, reproduced Python 3.12 fixture as recorded there. Alternative rejected: promote a demonstration to predictive probability. Destination: B06 #154 and B07 #93. Families: counterexample-based testing, **FALS**, **REPRO**.

### Execution audit (observable quality, subjective score; not a completion %)

| Dimension | 0–5 |
|---|---:|
| Objective control | 4 |
| Execution conversion | 4 |
| Reuse of existing capability | 5 |
| Ownership compliance | 5 |
| Verification discipline | 3 |
| Dependency handling | 4 |
| Resource efficiency | 4 |
| Knowledge extraction | 4 |
| Handoff quality | 4 |
| Closure discipline | 2 |
| **Total** | **39/50 = 3.9/5** |

**Corrections informed by actual execution (up to three):**
- Earlier path: propose a relatively broad M0–M5 ladder before isolating first controlled test. Better contemporaneously feasible path: freeze traversal-only versus traversal+SMA30 slope on identical events, then expand individually. Cause: feature exploration outran test isolation. Preventive rule: predeclare paired arms and exact denominator before classification. Existing destinations: PAIRED_REPLAY, B07 #93. Acceptance: identical event/cohort hashes and equal alert budget.
- Earlier path: imply that a passed generic GitHub workflow satisfied full analytical validation. Better path: inspect exact-head workflow jobs and separately execute synthetic tests and historical replay. Cause: insufficient separation of generic repository QC from domain evidence. Rule: label each test class and exact tested SHA. Destination: B01 #98. Acceptance: explicit domain replay/results and exact-head logs, with blocked measures remaining null.
- Earlier path: declare “Ready to Archive” while an explicitly chosen integration-confirmation gate remained unmet. Better path: distinguish **research handoff ready** from **GitHub integration verified**. Cause: inconsistent interpretation of completion versus archival criterion across prompts. Rule: require explicit gate and owner acceptance before archive claim; local closeout need not imply project stabilization. Destination: this file and B00 closeout protocol #169. Acceptance: verified PR disposition and applicable post-integration main checks, or an explicitly authorized out-of-scope transfer disposition.

### Maturation disposition / prioritization

- **Already consolidated:** six knowledge units above into the existing B06 #154 research artifacts; B06 boundaries reuse #109/#145/#150 and B10 #99.
- **Transfer, critical correctness (override ranking):** B00/B02 #148 point-in-time canonical resolver, complete daily/minute coverage, #152 quality. Do not create parallel data store.
- **Transfer, first empirical test (illustrative score: reusability 5, impact 4, novelty 3, evidence 2, feasibility 2, risk reduction 5 = 21/30):** B07 #93 with B06 #144 frozen episodes, paired comparison at equal coverage. Estimate: moderate implementation and coordination; not measured. No signal promotion until observed results.
- **Transfer, contract integration:** B00 #103 schema/adapter decision and B01 #98 independent test gates. Reuse existing issue threads.
- **Deferred:** automatic MA window optimization, hidden-state regime modeling, probabilistic price forecasts, historical lookback expansion beyond user-chosen 200–500 sessions, new weighted scores and operational streaming. Their marginal utility is unproven; they are not local incompleteness.
- **Discarded as unsupported:** MA200 proximity alone proves price support; synthetic fixture proves future rebound; a green data/QC workflow establishes independently calibrated trading signals.

**No release or merge has been authorized.** A research handoff is *generated and posted* in the existing issue/PR; recipient acknowledgment and implementation are not thereby established. Keep the draft PR unmerged until the appropriate authority reviews it.

### Receiver's smallest first action and retirement

Open issue #154 and PR #160 at the then-current head; verify all five owned file paths, the current exact-head CI, and the evidence in PAIRED_REPLAY. In the existing B00 #103/#148 threads, record acceptance/rejection of the experimental interface and exact point-in-time reader/episode availability. Only then assign paired replay to B06/B07. Report `basket.worker_resolution@1` on existing issue with accepted/rejected research, hashes, tests and blockers. Archive claim requires an explicitly accepted handoff endpoint or authorized integration/recorded alternative; do not interpret draft status as merged.
