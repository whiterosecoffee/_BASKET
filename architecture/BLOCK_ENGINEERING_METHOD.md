# Reusable block engineering — operating method

**Status:** current user-directed planning standard, with an example validated against an existing schema. This is not a registered runtime, a new scheduler or proof of qualified block implementations. Reconcile agent-written conventions against this direction and demonstrated needs.

## Work in complete cycles

The orchestrator owns progression through authorized stages. A subtask, document or review is not an automatic stopping point. Correct ordinary defects, update evidence and advance within the same work cycle. Interrupt the user only for a consequential unresolved preference, authority boundary, missing external access or additional resources. Current work remains planning/specification; do not infer authorization for product construction from a completed planning artifact.

Use outcome-level work packages containing independently inspectable tasks. A work cycle ends at an accepted deliverable or genuine blocking boundary, not after merely listing what to do next. Reground and publish a compact progress delta rather than repeat the full history.

## Standard objects and existing sources

| Object / responsibility | Reuse source | Coverage and remaining work |
|---|---|---|
| Component definition, typed ports and errors | PR #104 at `3908ef1dc33c65ee19e87b54a6d63a191659b9fa`, `schemas/component-blackbox.v1.json` | Existing proposal, not main. Has identity, versions, determinism, ports, errors, dependencies and acceptance. Explicit assumptions/guarantees/effects remain gaps. Its determinism enum does not fully describe arbitrary stochastic-agent execution. |
| Input/output payloads and call/result envelopes | Each port's versioned schema; envelope prose in PR #104 | Referenced schemas and envelope prose are not proof of actual executable schema coverage. Specify gaps before implementation. |
| Capability/profile/recipe blueprint | Main `schemas/worker-library.v1.json` | Reuse now. [Example](examples/orchestrator-blueprint.example.json) is a planning specimen, not a second active catalog. |
| Planned task and dependencies | Main `schemas/task-queue.v1.json` | Existing scope, capability and dependency fields. Cost estimates, option/stage review and stronger evidence gates require a compatibility proposal; do not add unsupported fields silently. |
| Assignment and task claim | Existing worker-task schema and adapter proposal #78 | Reuse identities, owned paths and authority; verify actual compatible versions before execution. |
| Result and evidence | Existing worker-resolution / worker-evidence schemas | Reuse exact artifact identity and actual checks; planned work cannot report passed execution. |
| Stage/attribute review and economics | Current issue records pending minimal compatible representation | Required information is specified below; no competing schema/framework is introduced here. |

A complete block definition references its input/output schemas, examples and acceptance. An abstract capability or recipe is not automatically an implemented/qualified block. Distinguish planned, structurally validated, behaviorally verified, independently verified, integrated and operational evidence.

## Predefined single-purpose capability blueprints

| Blueprint | Input -> output | Principal interaction boundary |
|---|---|---|
| Capture message | Authorized source event -> durable intake receipt | Identity, privacy, duplicate/retry semantics |
| Extract intent | Intake + current requirements -> classified requirement links | Source/interpretation separation and coverage |
| Analyze problem | Observations + goal -> causal hypotheses/questions | Evidence, counterevidence and bounded uncertainty |
| Evaluate options | Problem + alternatives + criteria -> decision/maturity record | Evidence-backed comparison, cost, reopen triggers |
| Select eligible work | Current tasks + gates/resources -> selection or no-selection reason | Dependency, scope, authority, token assumptions |
| Reconcile progress | Observed results + canonical records -> progress/portfolio delta | Retry-safe effects and stale-evidence handling |
| Review result | Artifact + acceptance + evidence -> attribute verdicts/disposition | No self-review misrepresented as independent |
| Compose blocks | Provider/consumer definitions -> compatibility/recipe result | Guarantees satisfy assumptions; effects and versions compatible |

Class, size, runtime and implementation may differ. High cohesion defines a block; do not split every helper into a service or generalize before real consumers demonstrate need.

## Stages and gates

| Stage | Required result | Review before advancing |
|---|---|---|
| 1. Orient and capture | Goal, source, decomposition, canonical queue placement | Intent coverage, contradictions, scope and relevance |
| 2. Investigate and select | Existing implementation/prior art, causal map, alternatives and economics | Reuse, evidence, downstream unlock, assumptions and alternatives |
| 3. Specify and qualify readiness | Contracts, fixtures, effects, dependencies, assignment, resource estimate and recovery | Required attributes covered; meaningful acceptance/negative scenarios; no hidden blockers |
| 4. Implement or adapt | Bounded owner-scoped artifact meeting the agreed contract | Actual changed scope, structural/semantic tests and resource usage |
| 5. Verify and integrate | Independent applicable checks and accepted composition | Exact heads/fixtures, compatibility and post-merge acceptance; merge is not deployment |
| 6. Operate and evolve | Observed behavior, failures and comparable outcome costs | Retain/revert improvement; update fixtures/recipes and revisit affected options |

Repeat the affected step when its review fails; do not restart the entire project. Reviews are always recorded, but independent model review is selective and risk-based. Deterministic checks are preferred for structural assertions.

## Review all applicable attributes

Use an evidence-anchored ordinal scale: **0 absent/violated; 1 specified; 2 demonstrated on representative cases; 3 independently verified; 4 operationally observed**. Also allow **UNKNOWN** and **N/A with reason**. These are proposed review labels, not additions to production schemas or calibrated probabilities.

Review every required contract attribute as well as these groups:
- purpose/cohesion and consumer relevance;
- input/output semantics, assumptions, guarantees and invariants;
- effects, ownership, dependencies and composition compatibility;
- provenance, uncertainty and error/recovery behavior;
- fixtures, reproducibility, regression and independent evidence;
- actual reuse and portability;
- token/compute/integration cost, expected savings and estimate confidence;
- observability, maintainability and operational evidence.

Record artifact/version, criterion, score or explicit unknown, evidence, reviewer/independence, failure consequence and corrective action. A composite score must never hide a failed mandatory gate; do not average UNKNOWN into success. Scores indicate evidence maturity, not investment performance. Reuse claims need actual consumers; cheaper-looking calls need accepted-outcome comparisons including rework.

## Sequence for throughput, not conversational turn order

1. Capture new input and reconcile corrections without automatically interrupting current execution.
2. Select among eligible tasks; exclude unsupported authority/resources, unresolved dependencies and conflicting writes.
3. Prefer the task that unlocks useful downstream work or resolves a consequential uncertainty at proportionate cost. Apply documented policy transparently; do not treat the old custom score as proven optimal.
4. Batch compatible independent reads/checks and combine related tasks into a complete outcome package. Keep one writer per actual scope; more bots are not automatically faster.
5. Review at each stage and resolve ordinary findings in-cycle. Preserve alternatives/deferred tasks with return triggers.
6. Update evidence and zoom out after an accepted increment, interruption or changed assumption. Continue eligible authorized work; no routine NEXT request.

Use the current package only. Token estimates state input/context, analysis, implementation and verification where measurable, basis/confidence, reuse horizon and expected reduction. Exact balance and unsupported savings remain UNKNOWN. Do not invoke Claude or provision Spark merely because they appear in the map.

## This planning cycle — completed work and actual limits

| Step | Review evidence | Verdict / maturity |
|---|---|---|
| Inspect existing objects | Main worker-library/task schemas and exact PR #104 component proposal read | Reuse found; envelope/effect/review/economics gaps explicit |
| Define reusable blueprint specimen | Example uses existing capability/profile/recipe schema | Six local checks passed: schema validity, specimen conformance, two rejection cases and profile/recipe references; execution qualification not claimed |
| Establish stage and attribute reviews | Method specifies stage results, evidence scale, mandatory gates and correction loop | Specified (1); empirical benefit/independent acceptance UNKNOWN |
| Reconcile map and sequence | Project-map link and GitHub progress update | Recorded planning change; automated workflow unverified |

### Specimen attribute review

The scale above is applied conservatively. Structural conformance is demonstrated; intended purpose, I/O meaning and reuse are only specified. No independently versioned per-blueprint payload schema or behavior is claimed implemented by this specimen.

| Blueprint | Purpose | Library structure | I/O meaning | Typed port schemas | Intended reuse | Measured efficiency |
|---|---|---|---|---|---|---|
| `capture_message` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |
| `extract_intent` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |
| `analyze_problem` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |
| `evaluate_options` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |
| `select_eligible_work` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |
| `reconcile_progress` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |
| `review_result` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |
| `compose_blocks` | 1 | 2 | 1 | 0 | 1 | UNKNOWN |

Other applicable attributes: required evidence/artifact declarations and recipe/profile references pass structural validation; actual assumption/guarantee enforcement, effects isolation, failure recovery, domain correctness, provider substitution and operations are not demonstrated. Consequently none of these conceptual blueprints is declared execution-qualified. The next specification work is targeted payload/effect/acceptance coverage, not another abstract catalog.

Two contrasting paper checks: an issuer-evidence flow requires source/excerpt/period semantics, uncertainty and replay; a market-data flow requires time/unit/freshness/FX semantics, duplicate safety and write ownership. Both use the same analysis/review/assembly pattern but different payload schemas and domain fixtures. This is a coherence review, not a live pipeline or executed domain test.

The first implementation-ready work package must close the minimum intake/reconciliation gaps exposed by representative cases, reusing current planner/controller candidates. It must not wait for a universal schema platform, new backend or complete portfolio refactor.

## Authority, provenance and detail

Codex owns orchestration decisions and complete authorized cycles; GitHub owns durable state and checks; Claude is an optional qualified independent/alternative provider; future NVIDIA Spark is reserved for qualified local execution/evaluation. Existing domain/B01/B08 functions retain actual scoped responsibilities.

This method assembles established requirements engineering, Kanban/pull, Design by Contract, ports/adapters, consumer-driven testing, architecture decision records, scenario review and PDCA. Existing research is linked from the [queue](https://github.com/whiterosecoffee/_BASKET/issues/136). It is not a novel foundational framework.

[Concise project map](PROJECT_MAP.md) · [Detailed map](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6546147461)
