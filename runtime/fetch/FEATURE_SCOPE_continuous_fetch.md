# Feature scope — continuously evolving `_FetchMassiveData` (queue seed)

Spark B02 | worker issue #151 | handoff #152 (request R6) | status: **proposal for B00 queue review**. This is a scope document, not an implementation, schedule or live feed. B00 owns `orchestration/planner/queue.json`; nothing here edits it.

## 1. Intent
The project owner wants a Massive fetch worker whose instructions are trained once and whose JSONL minute blocks are kept up to date for local functions, evolving over time. Owner direction: place it as a feature request, built **once the NVDA spark is online**.

## 2. Honest boundary
- "Continuous" here means **repeated settled-session updates**, not a live tick or quote feed. Same-day row counts changed between two pulls (893 vs 898), so only completed sessions are fetched.
- GitHub and chat sessions are not polling workers (`AGENTS.md`). Unattended operation needs an entitled adapter, a persistent process and durable storage. None is verified today.
- No claim of working until the connector-to-code route (R7) is demonstrated by a test.

## 3. Phases (each a separate queue entry or gate; none authorized yet)
| Phase | Deliverable | Entry gate | Exit evidence |
|---|---|---|---|
| P0 design (done, PR #153) | architecture record, runbook skeleton | none | draft PR, CI green |
| P1 stager | module + unittest on synthetic fixtures; sanitize, manifest, conflict/hold, dry-run plan; writes only to `runtime/fetch/intake/` | B00 answers R2, R7 | tests pass on exact head; independent B01 check |
| P2 ORCL pilot | stage real ORCL sessions, run stress tests, promote by separate authorized PR | R1 (ORCL home valid) + P1 | validator passes with ORCL present; two independent pulls identical; hash replay |
| P3 manual cadence | operator or session runs the runbook per settled session | P2 | run records show chosen options and criteria |
| P4 unattended operation | scheduled or persistent runner | NVDA spark online; entitled adapter; durable store; owner authorization | measured freshness and failure behaviour; no live-feed claim without that evidence |

## 4. In scope
Plan (dry-run default), fetch of settled sessions, sanitize, staging, manifest with hash and revision records, continuity hold, verification suite, authorized promotion, runbook and option table, per-run records of option choices.

## 5. Out of scope (other owners)
ORCL entity, events and relationships (company spark, B03, B05); schema files (B00); shared validator and CI (B01); hosting and persistent services (B08); path resolver (B00, #148); any valuation or trading use of the data.

## 6. Requirements carried from the design record
Fixed procedure and runtime option sets as in `ARCHITECTURE.md`. Unadjusted rows with basis recorded; no CSV stored; no forward-fill; volume never int-cast; `vw` outside `[l,h]` flagged as per-block counts (measured 24.5% of rows in one ORCL session); holiday = `no_bars`; differing re-pull = conflict + new revision; key only from `MASSIVE_API_KEY`; B02 paths only; never merge.

## 7. Acceptance for the whole feature (not per phase)
- A1 One ORCL session passes the full verification suite end to end, with evidence from a real runner.
- A2 A deliberately corrupted block (synthetic) is rejected or held, never promoted.
- A3 A simulated split triggers the continuity hold and writes nothing.
- A4 Re-running any stage is idempotent.
- A5 The connector-to-code route is shown to carry rows without model transcription.
- A6 Documents state, in plain words, what is live (nothing) and what is settled-session-fresh.

## 8. Risks and unknowns (unmeasured unless stated)
Storage growth (about 60 KB per liquid ticker-session from one session; widening needs a decision). Entitlement and rate limits. Connector fidelity (R7). Calendar and early-close coverage. Whether git remains the right store.

## 9. Draft queue entry (proposal; B00 assigns the real ID, values are my judgment, not measured)
```json
{
  "id": "T-0XX",
  "spark_id": "B02",
  "title": "Continuously evolving Massive fetch worker seed",
  "objective": "Stage, verify and authorizedly promote Massive 1-minute settled-session blocks per ticker, evolving from manual runbook to unattended operation once gates pass.",
  "priority": "P2",
  "impact": 4,
  "effort": 4,
  "mode": "orchestrator_review",
  "profiles": ["data_engineer", "qa_reviewer"],
  "recipe": "historical_replay",
  "capabilities": ["implementation", "immutable_replay", "source_audit"],
  "depends_on": [{"task_id": "T-0XX", "gate": "issue_exists"}],
  "acceptance": ["See sections 3 and 7 of runtime/fetch/FEATURE_SCOPE_continuous_fetch.md"],
  "write_scope": ["runtime/fetch/**"],
  "issue_number": 151,
  "pr_number": 153,
  "source_handoff_issues": [152],
  "worker_prompt_details": "Gate P4 on the NVDA spark being online; no live-feed claim; do not edit tickers/** until the ticker home validates."
}
```
`depends_on` needs the task ID of the NVDA-online work, which I could not identify; B00 to supply. Gate vocabulary here is the schema's (`merged`, `ci_passed_on_head`, `issue_exists`); none expresses "spark online", so B00 may need an additional gate or a different encoding.
