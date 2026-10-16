# _BASKET — Conversation Launchpad

**As of:** 2026-10-16 · **Owner:** B00, issue #1 · **Orchestration PR:** #2 (DRAFT, NOT MERGED)

This page is a **human-friendly launch queue**, not a substitute for live GitHub issue/PR status. Always recheck issues, active PR changed paths, and branch ownership before beginning work. Full dormant scope catalog: `orchestration/sparks.json`. Canonical rules: `AGENTS.md`. Complete Project Instructions: `orchestration/PROJECT_INSTRUCTIONS.md`.

## Current state — VERIFIED

- **Active:** B00 orchestrator in *this* conversation, issue #1, branch `work/1-conversation-sparks-orchestration`, PR #2 draft.
- **Ready to launch:** B05 relationship-contract repair (handoff #4); B01 independent test/CI verification (handoff #5).
- **Independent next launch:** B02 price/FX/TTD history and snapshot runtime (handoff #7).
- **Blocked from release:** strict SFTBY relationship schema compliance and passing `Validate BASKET data` CI. Narrative tests passing do not lift this blocker.
- **Dormant:** other 18 sparks; activating dormant sparks should be justified by verified dependencies, not by conversation count.

**Important distinction:** A handoff issue is **not** the receiving conversation's new worker issue. Each newly opened chat claims its handoff, creates a *different* new issue and its own branch from the latest `main`; it then links both.

## Launch queue — three independent, non-conflicting conversations

### A. Open a NEW ChatGPT _BASKET chat → B05 (start first)

Paste this single message:

```text
Launch B05: SFTBY relationship integrity. I am a NEW _BASKET conversation.
Read AGENTS.md and orchestration/sparks.json from main if merged; otherwise
READ them from work/1-conversation-sparks-orchestration (PR #2), without
using that as my development branch. Inspect existing issues/PR file changes.
Claim handoff #4. Create ONE NEW GitHub issue for THIS conversation, then
ONE UNIQUE branch work/<my-issue>-sftby-relationship-integrity based on the
latest main. Link the new issue/branch to handoff #4.

Owned writes: tickers/*/relationships.json, engines/relationships/**,
research/graph/** only. Make SFTBY relationships.json strictly valid under
the current relationships@1 schema; preserve all six additional context
fields with provenance and USD NAV caveats losslessly in research/graph/**.
Run validation, commit on MY branch, open a draft PR, never merge.
Report issue, branch, exact changed paths, tests, PR and next handoff.
```

**Acceptance:** B05-owned data fix, historical evidence preserved, existing schema intact, draft PR to main. The current CI status may remain red until integration/verification.

### B. Open a different NEW chat → B01 (can diagnose in parallel; verification follows A)

```text
Launch B01: Independent BASKET CI validation. I am a NEW conversation.
Read AGENTS.md and orchestration/sparks.json from main if merged, or
READ them from work/1-conversation-sparks-orchestration while PR #2 is
unmerged. Inspect issues, PR file changes, ownership and current CI.
Claim handoff #5; create a NEW worker issue and UNIQUE branch from latest
main. Do not reuse any existing branch. Link the new issue and branch.

Only write tests/validate_stores.py, tests/integration/** and
.github/workflows/**. Independently reproduce baseline SFTBY schema
failure from main, preserve strict validation, specify or add regression
checks, and verify B05 changes once available. If schema/data mutations
are required, use B00/B05 handoffs rather than modifying their files.
Also consider #6 for version-validation CI only after the data contract
is sound. Commit, open draft PR, report exact test/CI evidence and blockers.
```

**Acceptance:** independent clear failed-to-passing evidence, no disabled schema guards; B05 fix can be reviewed separately.

### C. Open another NEW chat → B02 (independent of SFTBY schema repair)

```text
Launch B02: Reliable price/FX/TTD data plane. I am a NEW _BASKET conversation.
Read AGENTS.md and orchestration/sparks.json from main if merged; otherwise
READ temporary copies from work/1-conversation-sparks-orchestration (PR #2).
Inspect all active work and claim handoff #7. Create a NEW worker issue and
UNIQUE branch from latest main. Link issue, branch, spark and handoff.

Only write B02 paths per sparks.json: runtime/**, fx/**,
tickers/*/history.jsonl and history.meta.json, tickers/*/intraday/**,
tickers/*/live/**, engines/economics/freshness.py, tests/test_ttd.py.
Audit provider entitlement and disabled feeds. Specify deterministic
replayable snapshot IDs, source/FX time alignment, append-only revisions,
TTD expiry and actual worker/storage requirements. Do not claim a live
feed when no working entitled adapter exists. Validate, commit, open draft
PR, report failures and dependencies.
```

**Acceptance:** reproducible data input/snapshot plan and tested local code, explicit stale/unavailable states; production continuous feed remains blocked until hosted authenticated provider exists.

## User operation: minimal manual action

**One-time:** Ensure these startup rules are present in the _BASKET ChatGPT Project Instructions. They are already in the canonical Project Instructions file, but ChatGPT Project settings are separate; repository writes do not automatically update them.

**For each new worker:** Open a NEW conversation inside the _BASKET project, paste A/B/C or say `Launch spark B05` once PR #2 has been merged. The conversation handles issue/branch creation and development. A new chat is necessary: this orchestrator cannot directly open another ChatGPT conversation.

**After worker creates draft PR:** Return here with `Review the _BASKET queue and next launch`. B00 checks GitHub for claims, open PRs, outstanding handoffs and paths, then selects the next smallest unblocked objective. No need to repaste worker results if in GitHub.

## Explicit states and gates

`dormant` (not started), `ready` (handoff available), `claimed` (new worker issue + branch linked), `building` (commits in branch), `review` (draft PR), `blocked` (needs a named external dependency), `integrated` (authorized merged PR). These are operational meanings, not automatic GitHub labels. **Never mark a state active/complete without fetching its actual linked GitHub evidence.**

To avoid duplicate claims: before starting, search active issues and open PR changed-file lists. If another chat has already claimed the same objective/path, **narrow the new conversation's scope** or hand off; never reuse its branch.

## Direction / no scope creep

B00 should optimize work allocation, state transparency and integration order. Do **not** turn every discussion into schema versioning, full-scale roadmap creation or another new spark. Start 2–3 workers, get the SFTBY validation failure repaired, prove isolated branch+PR workflow, then grow only if dependencies justify it. Current V0.5.0 is **planned**, not released. No current market-price inference from stale data and no uncalibrated traversal probabilities.
