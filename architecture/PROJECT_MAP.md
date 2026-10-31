# _BASKET — Project Map

**Purpose:** reusable block engineering, proven through financial trading research and company/ticker analysis. Creation, composition and stress testing are activities of one discipline.

**Status:** planning map; not proof of deployed functionality. This is the concise entry point for the current user direction. Older agent-authored policies are candidates for reconciliation, not presumed superior architecture.

## Goal and principles

Build single-purpose, encapsulated blocks that can be recombined into increasingly complex use cases. Each block declares:
- what it requires: inputs, dependencies and assumptions;
- what it guarantees: outputs, behavior and explicit failure states;
- what it owns: state, effects, resources and permitted interactions.

Assembly requires compatible assumptions and guarantees, including meaning, units, freshness, provenance and effects. Contracts describe boundaries; scoped permissions and runtime controls enforce them. A block may be code, an agent operation or a coherent composition; it need not be a separate service.

The economic goal is lower cost per comparable accepted creation, test and integration through reuse of blocks, adapters, fixtures and recipes. Measure improvement without weakening acceptance; do not presume continuously declining costs.

## Responsibilities

| Participant | Responsibility |
|---|---|
| User | Outcomes, consequential business tradeoffs and additional resource authority |
| Codex / B00 | Extract intent; maintain this map and queue; research and compare established options; sequence and perform bounded authorized work; reconcile evidence |
| Claude | Proposed independent causal/architecture/acceptance review and alternative scoped engineering provider; not assumed connected |
| GitHub | Authoritative work and decision records, dependencies, Projects views, source history, PRs, checks and supported automation |
| Future NVIDIA Spark | Reserved local execution/evaluation node; qualify models, isolation, recovery, conformance and economics before use |
| Existing domain owners / B01 / B08 | Domain implementation, independent verification and runtime operation respectively; platform assignments do not imply running workers |

## Architecture

**Conversation -> durable intake -> interpretation and option analysis -> eligible queue -> authorized execution adapter -> qualified block/composition -> evidence and improvement.**

GitHub is the control plane. Agents and code are interchangeable execution providers only after qualification. Existing financial-data stores are the data plane; do not create another ticker registry, research database, scheduler or task database.

The initial use cases cover market observations/FX/replay, issuer evidence, valuation, traversal, research/falsification and persistence. Massive/local JSONL ingestion is user-reported context; verify actual paths and runtime behavior before operational claims. Preserve the existing earnings watch until accepted cutover and explicit retirement approval.

## Methodology

[Operating method, predefined blueprint specimen, stages and reviews](BLOCK_ENGINEERING_METHOD.md).

1. Capture every instruction and preserve its source. Separate original intent from interpretation; consolidate duplicates and retain corrections.
2. Investigate the problem beneath the request. Use branching causal questions, evidence and counterevidence; depth follows decision value.
3. Discover existing capabilities and maintained prior art before proposing additions. Compare reuse, configuration, adaptation, purchase, construction and no action where relevant.
4. Retain alternatives, maturity, assumptions and revisit triggers. Apply hard gates before evidence-based comparisons; unknown is not success.
5. Define provided/required contracts, side effects and consumer acceptance before construction. Prefer established component, Design by Contract, ports/adapters and conformance patterns.
6. Select work by outcomes, readiness, dependencies, downstream unlock and cost—not message order. Operate the available manual workflow before automating it.
7. Verify exact artifacts and applicable integration/operational behavior. Schema compatibility, green branch CI, merge and deployment are separate claims.
8. Reground at outcome, component and task levels after interruption, material change and acceptance. Revisit deferred vectors.
9. Improve through evaluated changes: observe -> explain -> compare -> test -> retain/revert. Review each stage and all applicable attributes with evidence. Resolve ordinary findings and advance through complete authorized cycles; a subtask is not a stopping point. Avoid speculative refactoring.

## Main steps

| Order | Deliverable | Lead |
|---|---|---|
| 1 | Persistent project map and concise entry point | Codex + GitHub |
| 2 | Demonstrated minimum manual intake/progress/return loop | Codex + GitHub |
| 3 | Existing-component map and established-pattern comparison; retain option sets | Codex; targeted Claude review if available |
| 4 | One implementation-ready, owner-scoped GitHub orchestrator increment | Codex + independent B01 verification |
| 5 | Qualified reuse/composition across contrasting financial use cases | Domain engineers + independent acceptance |
| 6 | Alternative providers and future NVIDIA Spark qualification | B08 + component owners |
| 7 | Evidence-backed branch integration/refactoring after patterns are established | Codex + relevant owners |
| Ongoing | Measure accepted-outcome cost and evolve reusable methods | Codex; GitHub evidence; other providers selectively |

## Resources, evidence and detail

Use the current service package sparingly, primarily for planning. Each selected work item needs a token estimate with basis/confidence and expected downstream savings; unavailable quota or cost telemetry remains unknown. Flag execution-ready work needing additional resources before committing expenditure. Do not require repeated NEXT prompts for authorized work.

The recorded inventory identified 53 branches, 79 open issues and 40 open draft PRs across nine capability families. It is a dated discovery snapshot, not current worker activity or acceptance proof. Main observed: `afc4ada7bc6d7294071b3610fa77e59b206b6312`.

- [Current queue and progress](https://github.com/whiterosecoffee/_BASKET/issues/136)
- [Detailed project map and platform assignments](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6546147461)
- [Repository decomposition and retained branch options](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6544886903)
- [Planning maturity evaluation](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6544842272)

Automated conversation capture, a qualified end-to-end orchestration loop, Claude/Spark connectivity and measured cost reductions remain unverified. Proposed responsibilities and tests are not execution evidence.
