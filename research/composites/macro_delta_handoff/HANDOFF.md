# Macro deltas and physical diesel supply risk — receiver handoff

Source: issue #158, draft PR #159, branch `work/158-macro-delta-handoff`.
Decision record and evidence manifest: [proposal.v1.json](proposal.v1.json).
Execution coordinator: existing Codex #136, with B00 #59 routing.
Source conversation completion means this package is ready for the user to paste; it does not establish receiver receipt or implemented functionality.

## User-approved outcome

Both trading backdrop and physical supply risk. Lead with the latest changes; previous-check, 15-minute and prior-close comparisons. Physical risk includes Middle East shipping/refining disruption, usable specification-compliant diesel in the USA and abroad, and transmission to inflation, Treasury yields, credit and basket conditions.

Show rates/spreads in basis points, market prices in percent and physical quantities in their own units. Weekly observations keep release-to-release deltas and actual age. Use explicit unknown/stale/no-new-observation states. Do not infer causation, calibrated probabilities or imminent exhaustion from co-movement or inventory coverage.

Nested ranges: explicitly bounded outer historical range, session range, active pocket, latest and previous marker. Arbitrary chart tracks are not observed ranges or support/resistance.

## Reconcile before implementation

Refresh main, AGENTS.md, spark ownership, current PR heads, changed paths, CI and issue dispositions. Preserve existing ownership and user-authorized autonomy. No new implementation worker, store or queue merely to receive this proposal.

- #100 / PR101: extend market_context; already has previous-snapshot, prior-close and 15-minute alignment logic.
- #141 / PR142: extend macro measure register where absent, including physical diesel/refinery/shipping inputs.
- #149 / PR150, #144 / PR145 and PR109: coordinate B06 range semantics and verify current issue relationships from GitHub.
- #148 and #146 / PR147: canonical storage migration; main's NVDA-only adapter cannot silently become a whole-basket schema.
- B02: source acquisition, canonical data, timestamp/TTD and baseline alignment.
- B03: dated disruption, restart and delivery evidence.
- B01 / #102: independent replay, negative tests and integration proof.
- B08: only existing serving/runtime work if needed.

The source worker only owns research/composites/macro_delta_handoff/**. Receiver reserves exact implementation paths with existing owners.

## Required resources and honest gaps

The proposal contains the scope, formulas, required metadata, source-series list, owner map, prior-art rationale, eight implementation acceptance tests, local file hashes/counts, known limitations and receiver instructions.

Local historical evidence: 58 observation records and four raw snapshot captures. Paths and SHA-256 hashes are in the proposal. These are execution-workspace files, not proven durable user-controlled storage. Eight observations are partial conversation recoveries. A manifest is not the payload: locate original bytes through B02 before import/replay; otherwise record unavailable and retrieve replacement data with a new vintage where possible. A current snapshot request cannot recover a past snapshot. Do not manufacture historical tick/15-minute coverage from these samples.

Do not duplicate canonical data. Read via the approved logical ticker resolver; request missing records and source-vintage manifests from the ingestion owner. EIA/IEA URLs are acquisition breadcrumbs, not pinned complete publication archives. Non-ticker series need an owner-approved identity/location, not invented stock symbols or a new storage framework.

## Acceptance and closeout

Execute the eight D1-D8 acceptance specifications in proposal.v1.json through the appropriate existing owners. At minimum: deterministic two-pass frozen-input replay; idempotent import; no lookahead; missing/stale and timestamp-unit negatives; distinct three baselines; weekly-series semantics; explicit range horizons; full coverage denominators; independent exact-head evidence.

Use a small existing NVDA/QQQ consumer pilot first where it fits project priority; broad supply-risk coverage may remain explicit missing while adapters are qualified. Do not block proposal intake on full-basket deployment.

Record accepted/scheduled/rejected/superseded and responsible owner for each deliverable on #136, linking back to #158. Record actual test commands/results/SHAs, source manifests, unresolved gaps and next action. Preserve the eight tests even if extending another module. Do not close implementation work based on this document or issue-comment receipt.

Nothing was merged or released by the source conversation. PR159 is proposal-only. Apply the user's current release/merge policy rather than infer permission from archive readiness.
