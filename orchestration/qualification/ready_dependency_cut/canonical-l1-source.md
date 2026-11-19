<!-- basket:l1-actionable-queue:2026-11-11:v1 -->
## Populated Level 1 queue: contracts, virtual flows, seeds and pattern workers

This turns the existing design plans into **25 individually addressable queue entries**, not 25 new issues or a second task database. Canonical work remains #136 with the existing owner issues below. The earlier implementation horizon, accepted evidence and financial/domain obligations are preserved; this Level 1 sequence takes priority over deeper build/integration work.

### Source and deduplication

Existing plans, retained unchanged:
- [Inventory and SFU/worker library](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6802415047)
- [Nested relationships, seed options and prior-intent-only gates](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6802665589)
- [JSON Level 1 projection](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6803140838)
- [Model/scenario/trace design method](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6803163587)

Deduplication reviewed #136 body/all 120 comments and both pages of current open issues/PRs. Existing authorities include #224/#59 inventory, #103/#105 contracts, #134 seeds/Projects, #156 architecture/kit, #78/#106 worker contracts, #64 independent worker evidence and #24 planner scope. Existing #138 remains deferred; this does not revive queue-admission machinery.

**Delta:** 21 entries below operationalize already-recorded requirements. L1-18, L1-19, L1-22 and L1-23 add explicit coverage-ranking, held-out worker qualification and queue-option decision deliverables requested by the latest instruction. They extend existing owners rather than duplicate them. No code implementation, working simulator, trained model, active worker claim, board setup or runtime acceptance is asserted.

### Queue conventions

Each L1 ID is an addressable item in this comment. READY means eligible read-only design/research, not claimed or completed. WAIT lists predecessor acceptance. Owner means routing responsibility, not an active worker. Actual artifact writes require the existing owner's accepted exact scope; a JSON path must be collision-checked and allocated before creation. All first-pass artifacts are JSON records or pointers to existing authorities; existing non-JSON files need not be rewritten.

### Foundation and nested composition

- [ ] **L1-01 · READY · B00 #224/#59: reconcile component identities.** Pointer-depth inventory of projects, tools, data, schemas, templates, contracts and workers; retain existing IDs and distinguish aliases/definitions/instances. Exit: every known group has a source/owner/revision or an explicit unresolved reference. Start with the existing 17-group index and candidate destinations, not a fresh registry.
- [ ] **L1-02 · READY · B00 #224/#223: capture prior intent only.** Record each prior candidate's goal, consumer, useful behavior, evidence and one-off/nesting mismatch. Exit: queued disposition linked to the original owner; no old implementation imported, moved or relabelled as reusable.
- [ ] **L1-03 · WAIT 01 · B00 #136/#156: record top-level decisions.** Separate definition/instance, containment/dependency/dataflow, state/effect ownership and parent/child responsibility. Exit: decisions include alternatives, rationale, unresolved questions and revisit triggers.
- [ ] **L1-04 · WAIT 01,03 · B00 #103 with B01 #105: reconcile the contract vocabulary.** Map model fields to existing black-box/artifact/call/result contracts and existing schema definitions. Exit: version/provenance/error/missingness fields have one authority; genuine schema gaps are explicit, not invented contracts.
- [ ] **L1-05 · WAIT 03,04 · B00 #136/#103: specify the pointer and binding record.** Identify canonical source, pinned revision, optional fragment, hash when actually measured, access boundary and resolver status. Exit: changed/unavailable/disallowed pointers fail explicitly; private bindings and data remain outside public records.
- [ ] **L1-06 · WAIT 03–05 · B00 #136/#103: define model, scenario and trace records.** Keep model/schema/seed revisions distinct and separate expected outcomes from observed virtual results. Exit: three compatible provisional JSON record roles mapped to existing authorities, with evidence class and unknown values preserved.
- [ ] **L1-07 · WAIT 01,04–06 · B00 #136/#224: populate the broad Level 1 model.** Link components and typed relationships at pointer depth. Exit: every major category represented or explicitly missing; no duplicate status database, fabricated executable ports for documents/data, or financial-relationship schema overloaded with software composition.
- [ ] **L1-08 · WAIT 07 · B00 #103 with B01 #105: review structure and references.** Check unique IDs, dangling references, containment cycles, port names and declared version compatibility. Exit: source-pinned positive/negative validation receipt identifies what was actually checked versus manually reviewed.
- [ ] **L1-09 · WAIT 07,08 · B00 #136 with existing domain owners: select one nested flow.** Map research parent → data/analysis/report children → resolve/validate SFU, including shared child references and two producer/consumer boundaries. Exit: named inputs/outputs, state/effect owner, failure propagation and a clean boundary between clone and FETCH responsibilities.

### Virtual scenarios and critical review

- [ ] **L1-10 · WAIT 06,09 · B00 #136 with independent B01 review: freeze a scenario pack.** One success plus missing/stale input, wrong hash/schema, cyclic containment, duplicate input, conflicting children, unsupported seed option and partial-failure cases. Exit: synthetic or permitted pointer fixtures, independent expected structural outcomes and explicit invariants; no real effects.
- [ ] **L1-11 · WAIT 10 · B00 #136: record the success trace.** Assistant acts as bounded interpreter of documented rules. Exit: immutable model/scenario/rule references, ordered handoffs and before/after state; result labelled assistant-simulated, never runtime-executed.
- [ ] **L1-12 · WAIT 10 · B00 #136: record negative traces.** Trace each fault without inventing missing transitions or modifying expectations to pass. Exit: typed failure/blocked outcomes, retained diagnostics and explicit semantic unknowns; no fabricated current assessment.
- [ ] **L1-13 · WAIT 11,12 · independent reviewer via #105/#136: critique and repeat the traces.** Challenge assumptions and rerun the frozen scenario against the same rules. Exit: disagreement/change register distinguishes interpretation consistency from deterministic execution, concurrency or calculation correctness.
- [ ] **L1-14 · WAIT 13 · B00 #136/#103: revise and repin the model.** Resolve demonstrated gaps through their existing owners. Exit: each change links failing scenario → decision → revised contract/model; prior traces remain intact and affected cases are retraced.

### Seeds, leverage and worker patterns

- [ ] **L1-15 · WAIT 03,04 · existing #134 owner with #156: inventory seed option sets.** Record pinned seed version, supported nested shape, included contracts/tests/setup, configurable options, dependencies and gaps. Exit: a JSON projection of existing Copier/kit choices, not a second generator or a claim that today's flat scaffold proves nesting.
- [ ] **L1-16 · WAIT 09,14,15 · #134 with B00 #136: specify closest-compatible-seed selection.** Apply hard compatibility/scope/effect constraints before ranking reusable coverage and adaptation cost. Exit: selected candidate, alternatives, bounded delta and explicit no-suitable-seed outcome; never silently choose a merely similar incompatible seed.
- [ ] **L1-17 · WAIT 03,16 · B00 #136 with #78/#106: specify the clean launch packet.** Fresh task/branch identity, seed provenance, exact paths, owner, purpose, inputs/outputs, dependency pins, effects, collision checks and acceptance. Exit: clone/FETCH scopes remain disjoint; prior branch authority is not inherited by cloning.
- [ ] **L1-18 · WAIT 07,14 · B00 #136/#156: build the component-by-building-block coverage matrix.** Candidate primitives include identity/reference resolution, contract validation, composition/binding, scenario/trace evidence, seed selection and worker task/result handling. Exit: every coverage edge cites a concrete requirement; distinguish component count from repeated instances and avoid double-counting nested parents.
- [ ] **L1-19 · WAIT 18 · B00 #136/#156: rank the smallest high-coverage baseline.** Compare marginal uncovered requirements satisfied against implementation/rework cost, critical dependency risk and evidence confidence. Exit: transparent assumptions, sensitivity check and ranked minimum set; no invented measured savings or score precision.
- [ ] **L1-20 · WAIT 04,17,19 · B00 #78/#106 with existing worker-library owner: specify pattern worker recipes.** Define bounded intake/dedup, model mapping, contract review, seed selection, scenario tracing and independent verification roles using existing capabilities. Exit: each recipe has versioned instructions, examples, input/result contracts, allowed effects, stop/escalation rules and ownership; recipe definition is not worker launch.
- [ ] **L1-21 · WAIT 20 · existing #78/#106 owners with B01 #64: specify queue handoff and rework behavior.** Reuse task/result lifecycle with dedup key, claim/lease, dependency gate, revision checks, retry limit, uncertain-outcome handling and same-owner rework. Exit: virtual duplicate/partial-failure cases cannot double-complete or bypass an unresolved approval.
- [ ] **L1-22 · WAIT 10,20,21 · independent B01 #64/#105: define held-out worker qualification.** Use pattern examples for preparation and separate unseen cases for evaluation; include refusal to invent evidence and scope/permission boundary negatives. Exit: proposed rubric, pass threshold, failure taxonomy and regression/version policy. “Trained” initially means instructed and evaluated recipes; model fine-tuning requires a separate demonstrated need and decision.

### Organization and promotion decision

- [ ] **L1-23 · READY · B00 #136 with #134/#138: compare queue arrangements and Linear.** Research current native capabilities, availability, setup/cost, dependencies, visibility, automation, ownership conflicts and migration/sync burden. Compare one canonical GitHub queue with filtered design/ready/review/blocked lanes; multiple independently owned queues; and Linear as a deliberate alternative or projection. Exit: source-backed recommendation with one canonical authority and migration criteria. Do not create a Linear workspace, mirror issues, add sync machinery or reopen #138 during research.
- [ ] **L1-24 · WAIT 14,16,19,22,23 · B00 #136/#156: present the building-block proposal.** Include ranked reusable baseline, component coverage, nested flow, seed decision, worker patterns, queue organization and deferred items. Exit: explicit decisions needed, bounded first implementation scope and evidence gaps. Proposal acceptance remains distinct from build/integration approval.
- [ ] **L1-25 · WAIT 24 and design acceptance · existing scoped owner plus independent B01: decide the first thin executable probe.** Specify clean-checkout parent/child exchange, schema/error propagation, unsupported dependency, repeat generation/replay and no overwrite/mutation cases. Exit: go/no-go with exact scope and acceptance. Only then implement/prove the selected clone; legacy adaptation and integration remain separately gated downstream.

### Current next actions and preserved obligations

Begin L1-01/L1-02 source reconciliation and L1-23 queue research; advance the dependency-ready design items only. A record's existence is not completion. Use evidence-linked checkoff and amend the same L1 entry rather than create duplicates.

Prior Q01–Q10, the 30-step implementation horizon, financial requests, failed evidence, existing claims and all source issues remain preserved. The current priority defers deeper work; it does not cancel obligations, merge branches, transfer ownership or erase earlier acceptance. #24 retains queue-file scope and GitHub remains the live authority pending the L1-23 decision.
