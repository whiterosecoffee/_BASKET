# Traversal tool worker guidance

Parent instructions: repository root `AGENTS.md`, `orchestration/WORKER_PROTOCOL.md`, spark B06 in `orchestration/sparks.json`, then this node. This node specializes the canonical read-only B06 metrics capability (`engines/traversal/metrics.py`), not the B10 journal, B02 ingestion/runtime, B17 market context, or B00 schema/catalog owner.

Before action read `component.json`, `state.json` and only the relevant `feature-design.md`; use `review.md` to verify the smallest bounded change. GitHub issue #278 and PR #282 are live task/evidence authorities; local state is an as-of explanation, not a controller or evidence of CI.

Input: owner-resolved completed observations plus source manifest. Output: immutable-to-caller descriptive result with explicit health and null states. Never infer live entitlement or install another worker. No merge/release, canonical data mutation, or alert enablement. Route B00/B01/B02 dependencies through existing issues #96/#98/#148/#152. Avoid duplicating existing code.
