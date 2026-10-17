# _BASKET — Next worker dispatch batch

**Planner:** `orchestration/planner/goals.json` v1.0.0 → `queue.json` v1.1.0 → `worker-scopes.json`.
**Orchestrator:** B00 issue #1, same existing conversation/branch. **GitHub status:** snapshot checked October 17, 2026; refresh live before dispatch. No autonomous ChatGPT conversation creation is claimed.

## Objective and acceptance sequence

| Phase | Task | Session action | Exit requirement |
|---|---|---|---|
| M-001 | T-001/002/003 B05/B00/B01 | Already integrated | Main CI run 38990763024 succeeded on commit 5bf7fc14 |
| M-002 | T-009 B01 worker QC | New worker when a development slot is free | All B00 tests, goals/scopes/attempt validators run in CI, then main CI green |
| M-003 | T-004 B02 and T-005 B03 | **Resume** original worker chats/issues | Executed replay and event lifecycle tests plus source coverage |
| M-004 | T-010 B19, T-008 B05, T-011 B09 | Resume B19 now; other work gated | Dated economic gateways and deduplicated holdings/NAV |
| M-005 | T-006 B21 and T-007 B06 | New chats only at release of slots/dependencies | Narrative falsification and descriptive traversal reproduce |

**Worker slots:** three active code-writing conversations, excluding B00. GitHub drafts do not establish that those conversations are active. No branch for a dormant task may be pre-created. A new chat always creates a new issue and main-based branch.

## Dispatch cards — take in task order, not all at once

### A — B02 RESUME existing #11 / PR #15 — T-004

```text
Continue EXISTING _BASKET B02 worker conversation, issue #11, branch work/11-market-fx-observation-replay, draft PR #15. Task queue T-004; milestone M-003, goal G-002.

First fetch current main, AGENTS.md, orchestration/sparks.json, planner/goals.json, planner/queue.json and PR diff. Keep the SAME existing branch only if this is the original conversation; if a new ChatGPT conversation is necessary, create a NEW issue and UNIQUE branch and link old #11 (do not claim another chat's branch).

Own ONLY runtime/**, fx/**, tickers/*/history.jsonl, tickers/*/history.meta.json, tickers/*/intraday/**, tickers/*/live/**, engines/economics/freshness.py and tests/test_ttd.py. Read-only: event/graph/CI/schema files.

Goal: make 200+ completed-session history and USD/JPY FX replay deterministic and source/available/ingested-time correct. Execute actual regression suite, repair failures, integrate existing 262-session histories and date-matched FX, test TTD dependency invalidation, revision conflicts and non-running provider status. No invented live feed, fabricated quotes or stale USD NAV.

Post attempt ledger with failure → correction → successful retry, test commands/results and evidence URLs. Do not overclaim Massive entitlements or hosted runtime. Commit only owned files, validate, open/update own draft PR and report basket.worker_resolution@1. Hand off B01-only workflow changes. Retest until acceptance or a genuine external/provider blocker.
```

### B — B03 RESUME existing #12 / PR #14 — T-005

```text
Continue EXISTING _BASKET B03 worker conversation, issue #12, branch work/12-b03-canonical-issuer-events, draft PR #14. Task queue T-005; milestone M-003, goal G-002.

Read current main, worker protocol, source/event schemas and existing PR diff. Same original chat may continue its branch; otherwise start a NEW issue and unique branch linked to #12 and avoid reusing its branch.

Own ONLY tickers/*/events.json, research/filings/**, research/events/**. Start by running full events@1 and revision tests on actual runner; fix faulty validator and source gaps. Extend dated issuer releases/SEC/earnings/financing for SFTBY, CRWV, AAOI and NVDA with stable IDs, original sources, effective/available/ingested times, and accurate knowledge precision. Never invent intraday publication times.

Keep USD 10bn funded tranche within already announced USD 30bn follow-on and separate that from cumulative USD 64.6bn issuer-reported investment and current NAV. Treat framework, announced and completed differently. Hand off ownership changes to B05; do not modify B05/B02/B01 paths.

Record failed attempts, corrected tests, source coverage/unknowns and exact GitHub CI SHA in basket.worker_resolution@1. Update own draft PR and repeat QC until gated acceptance.
```

### C — B19 RESUME existing #17 / PR #18 — T-010

```text
Continue EXISTING _BASKET B19 worker conversation, issue #17, branch work/17-mrie-revenue-pool-resources and PR #18. Task queue T-010; milestone M-004, goal G-003.

Fetch current main and PR #18, then reconcile your seven research resource files with the newer B00 goals and queue. Own ONLY research/themes/supply-chain/**. B02, B03, B05 and shared schemas are read-only.

Move beyond the folder scaffold: compile sourced quarterly USD revenue evidence, customer-facing pool gateways (hyperscalers, neoclouds, telecom/enterprise, direct AI software, automation and robotics) versus OEM/intermediate flows; mark missing quarters, original currency, model assumptions and double-counted pathways. Validate cross-sector coverage and identify every uncertain contract as provisional.

Run scoped validator/negative checks, attach source/replay evidence, record failures and corrective attempts, produce exact handoff issues for canonical events or ownership edges, and update draft PR with a complete basket.worker_resolution@1. Never convert a hypothesized 250MW edge arrangement into confirmed contracted revenue.
```

### D — B01 NEW worker for remaining #6 — T-009 (next new-chat priority when a slot opens)

```text
Launch NEW _BASKET B01 — Independent Worker-QC Execution. Source handoff #6; queue task T-009; goal G-001 milestone M-002. This is a NEW chat: create ONE new GitHub worker issue and UNIQUE work/<issue>-b01-worker-qc branch FROM LATEST MAIN. The previous B01 #9 is closed; do not reuse its branch or issue.

Inspect AGENTS.md, orchestration/sparks.json, planner/goals.json, planner/queue.json, planner/worker-scopes.json, current PRs and ownership. Write ONLY tests/validate_stores.py, tests/integration/** and .github/workflows/**. B00 scripts/schemas and all ticker data are READ-ONLY.

Make CI run ALL required B00 validation scripts and unittest tests: validate_versions.py, validate_sparks.py, validate_planner.py, validate_goals.py, validate_worker_scopes.py, validate_worker_attempts.py, orchestration/tests/test_*.py, worker_protocol.py static fixture and strict ticker stores. Pin dependencies; missing scripts, failed tests and skipped mandatory checks FAIL the job. Include adversarial tests for stale CI SHA, missing/colliding task IDs, cross-domain writes, retry lineage, fabricated efficiency and concurrent worker-slot excess.

Run actual GitHub CI on exact PR head, repair only B01-owned failures; route B00 implementation errors back to B00 via a linked handoff with precise failing test and receiver prompt. Do not change B00 code or suppress errors. Open draft PR, record test count/evidence, and report basket.worker_resolution@1 with exact SHA and next action.
```

### E — B21 NEW narrative worker — T-006 (after a slot is free)

```text
Launch NEW _BASKET B21 — Narrative and Claims Falsification. Queue task T-006; goal G-004 milestone M-005. Read main AGENTS.md, registry, queue, worker protocol and active issues/PRs. Create NEW issue and UNIQUE branch from current main. Own ONLY engines/narrative/**, research/narrative/** and tests/test_narrative.py.

Independently audit the CoreWeave/OpenAI/Anthropic perpetual-valuation commentary: source type, price methodology, exchange liquidity, timing, basis and unsupported valuation assumptions. Classify verified observations, issuer statements, third-party claims and hypotheses; test causal alternatives and explicit falsifiers. Add point-in-time negative tests for future knowledge, expired inputs and illicit probability claims. Commit, run tests, open draft PR and report machine-readable issue/branch/SHA, QC failures, corrective retries and outstanding handoffs. Never alter canonical event or graph stores.
```

### Later gates

- **B06 T-007:** after B02 replay PR integration. New issue/branch; only engines/traversal/** and research/traversal/**; deterministic SFTBY/CRWV/AAOI traversal, no invented predictive probabilities.
- **B05 T-008:** after B03 canonical issuer event integration; new issue/branch for OpenAI holding reconciliation, referencing #16, never reopen prior completed repair #8.
- **B09 T-011:** after B02 and B05 outputs; new issue/branch for dated SFTBY holdings/NAV, original JPY basis, USD translation, and completeness limitations.

## B00 review loop

After each PR, CI run or completion report:
1. Read live GitHub issue/PR/head SHA and actual changed-file paths.
2. Run static scope/schema/queue checks and required domain negative tests.
3. If failed, record attempt and return to original owner; if cross-domain, open receiver handoff.
4. If passing, integrate commit-pinned PR, verify full main CI and mark the milestone exit criterion.
5. Release the next highest-priority unblocked task only within three verified active worker slots. Never silently merge unrelated paths or rewrite another worker's branch.
