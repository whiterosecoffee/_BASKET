# Startup reconciliation — October 29, 2026

Main: `afc4ada7bc6d7294071b3610fa77e59b206b6312`. Exact main Actions:
[strict data/QC 39154102082](https://github.com/whiterosecoffee/_BASKET/actions/runs/39154102082)
and [OpenAI 39154102166](https://github.com/whiterosecoffee/_BASKET/actions/runs/39154102166)
both succeeded. These runs verify that commit, not subsequent deployments.

Reconciliation inspected all 27 open PR changed-file lists, 37 branches and the
complete 132-entry main tree. No exact-file collision found among open PRs.
This does not settle broad issue-scope, graph/contract or semantic collisions.
Open PRs do not establish currently active worker capacity.

## Reuse map

| Function | Owner/work | Actual location | Current distinction |
|---|---|---|---|
| Task planning and worker QC | B00/B01 main | orchestration/planner.py, worker_protocol.py, worker-library.json | Integrated source and green main; worker-library has 9 procedures, 6 profiles, 8 recipes |
| Queue expansion | B00 #24 / PR25 | orchestration/planner/**, execution_loop.py | Draft 14-task candidate; exact-head OpenAI gate red; main still 11 tasks |
| Agentic manager | B00 #32 / PR33 | orchestration/agentic/** | Draft source, dedicated acceptance #65; no verified hosted loop |
| Coverage proposals | B00 #48 / PR49 | orchestration/capture_dispatch/** | Offline compiler, feeds existing manager; no live producer |
| Revision journal | B02 #11 / PR15 | runtime/observations.py | Draft; old exact-head failure predates schema repair; refresh/retest |
| Issuer event intake | B03 #12 / PR14 | research/events/**, tickers/SFTBY/events.json | Draft source sample, not full-basket ingestion |
| REST snapshots | B08 #53 / PR55 | services/mrie_snapshot/** | Local REST proof; #34 remote persistence/MCP acceptance open |
| CRWV economics | B10 #86 / PR87, B01 #89 / PR90 | research/CRWV/tool/** | Runnable offline component; PR90 exact-head financial gate green at pinned source, unmerged |
| Ticker range matrix | B10 #95 / PR99 | research/CRWV/trading-tool/** | Generic ticker component manifest present; B06/B02/B08 integration pending |
| Basket market context | B17 #100 / PR101 | engines/composites/market_context/** | Callable local input contract; domain acceptance #102, not continuous feed |
| ORCL valuation/tracker | B00 #75 / PR77 | engines/valuation/orcl_bridge/**, orchestration/ticker_trackers/** | Draft implementation; registration/ownership and feed dependencies remain |
| Agent-neutral assignments | B00 #78 / PR79 | orchestration/agent_adapters/README.md | Draft contract, no functioning agent transport |
| Component contracts | B00 #103 / PR104 | schemas/component-blackbox.v1.json | Draft manifest/schema, independent validator handoff #105 |

The JSON index contains all PR paths, source identities, exact-head check evidence
and dependency references. It leaves undeclared versions/invocations and operation
unknown rather than deriving them from green shared checks.

## History and deployment limits

Main contains 262 daily rows each for AAOI, CRWV, SFTBY; OpenAI history is empty.
No `_DATA` directory was found in this inspected main tree. This is not evidence
that a separate repository, laptop or uninspected historical ref lacks the larger
dataset. No ingestion/deployment/last-trade entitlement was reverified by this audit.
Do not rebuild another data store because a cached path is missing.

## Next action and verification

Highest priority: existing queue owner #24 refresh PR25 from repaired main, reconcile
T-009 with the completed #44/#47 implementation and source-pin current goals/scopes.
Require all six validators, orchestration and independent integration tests, plus
exact-head strict/OpenAI CI. Preserve old red runs. Do not duplicate this queue worker.
Then connect already implemented manager/dispatcher through existing #65 and
source/replay/hosting handoffs, rather than creating another scheduler.

Startup classification: **extend** existing #59 intake with a generated discovery
index; **repair/integrate** existing queue work next. No user intervention required
for owner-scoped repairs; merge approval remains required only after reviewable green
candidates exist.

Local validation on refreshed #59 tree: inventory 8/8, orchestration 57/57,
independent integration 29/29, six validators and strict stores PASS. Initial broad
test attempt failed three imports because jsonschema was missing; installed the
workflow pins jsonschema==4.23.0 and PyYAML==6.0.2, then reran successfully. These are
local results, not B01 independent inventory acceptance or deployment evidence.
