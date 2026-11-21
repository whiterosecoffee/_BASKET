# B06 #154 → _PATTERNS _SYSTEM_DESIGN: bounded architecture reconciliation

**Prepared:** 2026-11-21. **Status:** design handoff proposed, owner receipt/independent acceptance pending. **Source owner:** _BASKET B06 #154 / existing draft PR #160. **Target:** _PATTERNS registered `_SYSTEM_DESIGN` (`work/components-system-design`), routed through existing _PATTERNS task/branch management issue #5; not a new standalone branch, engine, schema, or worker claim.

## Live registry / evidence resolution
- _PATTERNS main `Snapshot.json` already registers `_BASKET_B06_154_HISTORICAL_STATE`, receipt `_HANDOFF_RECEIPTS/6ae9e667-464c-83ea-a7a5-ee62ad095614.json`; owner continuation branch `component/basket-b06-154-historical-state`, pinned historical component revision `e3d69d1b53f5f08691869061a2cadb5d61294ec3`. Its state says receiver pending, without editor.
- `_SYSTEM_DESIGN` receipt `_HANDOFF_RECEIPTS/01a1effb-8ea7-7dd3-ba88-f970c1f02457.json`; existing branch `work/components-system-design`, parent guidance `_COMPONENTS/_SYSTEM_DESIGN/{AGENTS.md,state.json,DESIGN.md}`. The design currently includes Evidence-Driven Change Intelligence (EDCI), saved intake `EVIDENCE_DRIVEN_CHANGE_INTELLIGENCE.md`, synthetic Market Flow Watch + Project Monitoring comparison, and B06 #155 owner ratification draft; acceptance pending.
- `_AGENT_FRAMEWORK` receipt `_HANDOFF_RECEIPTS/01a1f3d9-fb9e-7d60-8710-ec81920e744f.json`; existing `work/libraries-microsoft-agent-framework`, adoption review at `0758c08f1a8c5451a07df652bfaba985c7f6670b` is an offline synthetic review, not operational authority.
- Adjacent published components: `_BASKET_TRAVERSAL_TOOL_20261119`, `_BASKET_B06_149_MARKET_GEOMETRY`, `_BASKET_B06_155_MARKET_FLOW_WATCH`, `_MARKET_TRAJECTORY_OPERATOR`. Existing implementations and data remain in _BASKET owner scopes.
- Live _BASKET draft PR #160: head `47bf50589159422312c337c1193da7ad14c742d0` at this review, research reference `reference_state.py`/tests under `research/traversal/self_relative_state/**`. Named domain-daily-state GitHub job 135354197360 of run 44463053659 reported 26 tests OK; source history provenance and predictive lift not established.

## What is shared versus unique

**Shared EDCI parent (System Design):** Three separable axes: (1) evidence trust [VALID, PARTIAL, STALE, CONFLICTING, MISSING, REJECTED], (2) change to environmental state and competing hypotheses, with novelty/continuation/invalidation, (3) decision relevance [NONE, WATCH, MATERIAL] and gate [SUPPRESS, REVIEW, NOTIFY]. Keep event, available, ingested and decision cutoff separate; persist revisions/negative outcomes with their owners. No inferred probability from rarity. This general logic applies to market and project state; the System Design proposal is not yet independently accepted.

**B06 specialization:** pure completed-daily 10/30/200 SMA, distance, five-session slopes, persistence with censoring, Wilder ATR, 252-prior empirical midrank, approach velocity, explicit session/adjustment/null rules. Compose with existing B06 traversal #109/#145/#150 and B17 market context. B07 #93 evaluates independent historical episodes and held-out incremental value. B02 #148/#183 controls a local-first Massive fetch → persistence receipt and one-session-per-file JSONL; B14 owns ticker-level research. This is **not** general EDCI code and must not be copied to _PATTERNS.

**Experiment:** same B06 traversal-only baseline versus identical baseline plus prior-completed-session SMA30 five-session slope, frozen episode IDs, same alert budget and chronology, purged overlapping outcomes, independent sample count; falsifiers are no held-out lift, instability across dates, excessive false reversals, or insufficient episode coverage. If negative, retain slope as descriptive metadata.

## Minimal proposed composition contract (for owner review, not accepted interface)
- Parent inputs: `objective, scope, source_evidence_refs, prior_state_ref, hypothesis_refs, decision_policy_ref, cutoff, baseline_ref, method_versions`.
- Parent outputs: `evidence_status, change_state, hypothesis_updates, decision_relevance, disposition, evidence_refs, unknowns, invalidation_criteria, evaluation_ref`.
- B06 adapter inputs: immutable `instrument_id, venue, completed_sessions, source_manifest_hash, as_of, calendar_attestation, adjustment_policy, method_version`.
- B06 outputs: `descriptive_state_vector, eligible_count, null_reasons, features_versions` as evidence-linked derived measurements. The parent does **not** infer a stock recommendation from low percentile or automatically send a notification. The market-specific event policy stays B06/B07; delivery stays B08.
- Version/precedence: EDCI policy applies as common conceptual guidance if independently accepted; B00 data/contract rules govern market source and schema; B06 owns method arithmetic; B07 validation owns predictive promotion. Conflict => unresolved rather than silent inheritance.

## Prior-art mapping and smallest test
- Statistical process control / CUSUM / EWMA: optional change detection versus plain MA displacement, only after first paired slope experiment.
- Time-series momentum: price distance, slope and persistence each require separate incremental measurement.
- Event studies/survival: independent episodes, censoring/time-to-event, ambiguous bar ordering.
- Multiple testing and purged chronological holdouts: prevent hindsight and threshold search; negative results are accepted.
- Complex event processing and bitemporal event sourcing: correct session/cutoff/revision semantics.
- Signal detection/robust decision theory: distinct detection accuracy and action value, costs of delay/missed rebound.
- Microsoft's typed function/workflow approach: keep calculations as deterministic functions. Adopt agents only for competing interpretations and workflows only if orchestration/retry/human approval is genuinely required; Microsoft's SDK does not provide market causality, qualification or calibrated financial probabilities.

**Two bounded cross-domain test cases for System Design:**
1. Market: low 200D percentile + falling 30D slope + rising 200D slope, source VALID but only two independent prior analogues. Expected evidence=VALID, interpretation=trend disagreement/unresolved, decision=WATCH or NONE depending on explicit policy, **not** automatic rebound/NOTIFY. Compare simple percentile threshold, stateful threshold and EDCI at same input/cutoff; do not invent odds.
2. Project: B06 exact-head 26/26 synthetic CI passes but B00 formula acceptance and B02 replay are missing. Expected evidence=VALID for CI only, state=math reference verified but production integration unapproved, decision=REVIEW for owner contract disposition, **not** completed/merged. Compare against simple “CI green ⇒ ready” threshold.

## Receiver assignment (reuses existing ownership)
**To:** existing _PATTERNS `_SYSTEM_DESIGN` owner via private task manager #5. **Authorized now:** read-only exact-revision review of this packet and registered branches, produce accept/revise/defer comparison and a bounded owner-specific proposal. **Not authorized:** edit System Design branch without current ownership/branch claim and collision check, write _BASKET B06 or B02 data, create another top-level parent, merge PR, release or claim receiver started.

Acceptance:
1. Resolve live main Snapshot -> published receipts -> exact branch revisions, confirm same component IDs and evidence.
2. Inspect existing `DESIGN.md`, EDCI candidate and archived B06 capture; identify shared/unique fields and any contradiction with B00 #103.
3. Compare fixed market and project examples on simple threshold / stateful threshold / evidence-decision evaluation with same qualified input; show any *essential* incremental decision and cost of complexity, or reject.
4. Produce an ADR-style **reuse / reference / revise / defer** decision, explicit owner and minimal changed paths. Preserve source-driven 26-case test evidence and receiver acknowledgment as separate statuses.
5. Return decision and exact commit/evidence to B06 #154 and B00 #103; if accepted, owner edits only registered System Design paths on its own claimed branch and requests independent acceptance. No new branch unless existing owner demonstrably cannot host a distinct, exclusive capability.

**Receiver prompt:** Inspect live _PATTERNS main AGENTS.md/Snapshot.json/Handoff.md; resolve _SYSTEM_DESIGN, _BASKET_B06_154_HISTORICAL_STATE, _AGENT_FRAMEWORK and related B06 captures through receipts. Read this packet and _BASKET #154/PR160, B00 #103, B02 #148/#183, B07 #93. Assess whether historical-state derived evidence is a specialization composed under existing EDCI parent rather than a new engine. Run two bounded comparative desk cases, record reuse/reject reasons, owner and acceptance evidence. Do not modify another owner's paths, create duplicate parent/branch, or merge. Explicitly record whether receiver independently accessed the pinned component, otherwise leave PENDING.
