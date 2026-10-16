# _BASKET — Live-work launchpad (historical snapshot: 2026-10-16)

**Owner:** B00 issue #1 · **PR:** [#2](https://github.com/whiterosecoffee/_BASKET/pull/2) (draft / unmerged at snapshot time) · **Catalog:** 1.5.0 (not yet on main).

**Purpose:** one clear work queue, not 22 simultaneous conversations. Re-fetch GitHub issues/PRs and current CI **before** relaying any state as current. Dates and branch snapshots here are historical evidence, not live surveillance.

**Queue source:** [Planner & active task DAG](planner/README.md), [queue.json](planner/queue.json), [worker-library.json](planner/worker-library.json). This document is a historical human-readable snapshot; rerun the planner with fresh GitHub evidence for actionable status.  
**Protocol:** [WORKER_PROTOCOL.md](WORKER_PROTOCOL.md) defines the task and resolution payloads, independent GitHub evidence evaluation, acceptance criteria, non-overlapping paths, and CI SHA reconciliation. [PROJECT_INSTRUCTIONS.md](PROJECT_INSTRUCTIONS.md) contains the complete ChatGPT Project Instructions in one copyable block.

## Four first-wave worker reports — source-checked at 2026-10-16

| Spark | Worker issue | Branch / draft PR | B00 assessment | Exact next gate |
|---|---|---|---|---|
| **B05** relationships | [#8](https://github.com/whiterosecoffee/_BASKET/issues/8) | `work/8-sftby-relationship-integrity`, [PR #10](https://github.com/whiterosecoffee/_BASKET/pull/10) | **Component verified**: current PR head had successful strict-data CI run [38956838273](https://github.com/whiterosecoffee/_BASKET/actions/runs/38956838273); historical context sidecar | B00 code review → explicit user merge authorization → verify main CI |
| **B01** CI | [#9](https://github.com/whiterosecoffee/_BASKET/issues/9) | `work/9-b01-independent-ci-validation`, [PR #13](https://github.com/whiterosecoffee/_BASKET/pull/13) | Regression checks passed; overall job [38956961596](https://github.com/whiterosecoffee/_BASKET/actions/runs/38956961596) failed because main SFTBY data not fixed | Refresh/retest AFTER approved PR #10 + PR #2 integration |
| **B02** market/FX/TTD | [#11](https://github.com/whiterosecoffee/_BASKET/issues/11) | `work/11-market-fx-observation-replay`, [PR #15](https://github.com/whiterosecoffee/_BASKET/pull/15) | Initial append-only journal committed; domain tests and data-provider integration still unverified; unrelated main schema CI failure | Resume **same worker conversation** for own incomplete objective; run domain tests/replay, address faults; no new duplicate worker claim |
| **B03** issuer events | [#12](https://github.com/whiterosecoffee/_BASKET/issues/12) | `work/12-b03-canonical-issuer-events`, [PR #14](https://github.com/whiterosecoffee/_BASKET/pull/14) | Two starter SoftBank events, incomplete primary-source coverage/replay validation; unrelated main schema CI failure | Resume **same worker conversation**; run schema/domain tests, expand issuer evidence; preserve unknown timestamps |

`main` still carries original SFTBY data defect until PR #10 is **authorized and merged**. An approved worker PR can be integrated separately; **B03→B05 #16** is a new OpenAI fund/ownership double-counting handoff, not a blocker that should expand the completed B05 schema-repair PR.

## Current priority

1. **B00 integration/review**: inspect PR #10, PR #2 and PR #13 exact diffs and CI, request explicit merge authorization before any merge. Do not tag or advance core version.
2. **B01 after main updates**: execute the strict combined data, relationship-regression, spark catalog, version manifest and worker protocol fixture tests. Update #5/#6 state from real CI, not chat claims.
3. **B02/B03 resumes**: fix remaining domain tests and fill constrained point-in-time replay/source gaps; each retains its existing branch/issue. If the original conversation is unavailable, begin a **new worker issue and new branch**, with a read-only handoff from the incomplete prior issue.
4. **New B21 next once a slot is available**: narrative claims, causal alternatives, counterfactuals and TTD tied to B03 issuer-event provenance.
5. **New B06 after usable B02 historical snapshot**: deterministic range/velocity/volume traversal for SFTBY, CRWV and AAOI; no probabilities absent B07 held-out testing.

## Open a new conversation — only when prior tasks have enough capacity

### Next truly new domain: B21 — Narrative intelligence
```text
Launch _BASKET Spark B21 — Narrative, Claims & Falsification.
I am a NEW _BASKET worker conversation. Fetch AGENTS.md,
orchestration/sparks.json and orchestration/WORKER_PROTOCOL.md from
main after PR #2 merges, else READ from temporary branch
work/1-conversation-sparks-orchestration. Verify open issues,
PR changed paths, current branches and domain ownership.

Create ONE NEW worker GitHub issue and ONE UNIQUE branch FROM current
main. Post a basket.worker_task@1 payload in your issue, with
exclusive paths and specific acceptance criteria. Do not reuse branches.

Own ONLY engines/narrative/**, research/narrative/**,
tests/test_narrative.py. Validate the existing CoreWeave/OpenAI/
Anthropic narrative engine. Distinguish reports, issuer facts,
synthetic private valuation marks, cash, funding, revenue, and
economic hypotheses. Reproduce the causal claim tests and
time-stamped falsifiers without unsupported probabilities.

Run validation, commit and open draft PR. Post complete
basket.worker_resolution@1 JSON payload with checks and exact run
URLs/PR SHA, acceptance results, changed paths, blockers, handoffs,
unknowns and one next action. Do not claim CI or live prices that
were not executed/verified. Never merge without authorization.
```

### Next dependency-bound domain: B06 — Descriptive traversal
Launch only when B02 provides reliable historical snapshot/replay evidence. New B06 issue/branch; own `engines/traversal/**` and `research/traversal/**`; include deterministic as-of, 5/20/60/200 ranges, velocity/volume direction, trading frictions and lost-rebound scenarios. No calibrated probabilities before B07.

## Worker response standard

The worker issue should contain a machine-readable **task claim** matching `schemas/worker-task.v1.json`. The worker's closing response should include a machine-readable **resolution** matching `schemas/worker-resolution.v1.json`. B00 requests or builds a **current** `schemas/worker-evidence.v1.json` snapshot from GitHub and runs `orchestration/worker_protocol.py`.

**Output**: actual issue/branch/PR refs, owned changed paths, CI/test success or failure and exact SHA, criterion-by-criterion pass/fail/not verified, open dependencies, new handoffs, unknowns and a single next action. A completed chat does not close the GitHub implementation issue.

## Parallelism

Recommend **three active code-writing conversations**, up to five only after the CI/integration process is reliable. A completed PR handed to B00 for review does not occupy a writing slot, but do not merge without explicit user authorization.
