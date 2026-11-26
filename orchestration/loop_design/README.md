# Scoped loop design

B00 [#232](https://github.com/whiterosecoffee/_BASKET/issues/232), branch `work/232-scoped-loop-contracts`. Scope: `orchestration/loop_design/**` plus the single discovery adapter `orchestration/tests/test_loop_design_bridge.py`. Canonical queue is #136; `_MAP` #230 and execution/controller owners #24/#32 remain authoritative and read-only.

Start with `contract.json`: four explicit audit → advance → independent review → outer-improvement roles, event cadence, inputs/outputs, hard eligibility gates, bounded budgets and checkpoint recovery. `checkpoint.schema.json` is a local design schema, not shared registration. `claim.json` uses the existing worker-task contract.

`scorecard.json` assesses repository evidence maturity, **not operational health**: baseline 15/50, refined 22/50 under an explicit 0–5 ordinal rubric. Scores are descriptive, not percentages, measured efficiency or deployment claims. Structured interfaces and offline cases improve design evidence; durable checkpoint storage, actual triggers and repeated end-to-end outcomes remain unproved. Private automation schedules, identifiers and prompts are excluded.

Run from the repository root:

    python -m unittest discover -s orchestration/loop_design -p 'test_*.py' -v

Requires Python and `jsonschema`. The test module is a small pure conformance model with synthetic inputs, no network/effects and no production dispatch. It verifies pinned source hashes, role pointers, schema examples/rejections, ranking gates, no eligible work, stable ties, unknown scores, uncertain-write recovery and independent exact-revision review. It does not prove that a real runner implements the JSON contract or satisfies all semantic obligations. Full existing orchestration/integration regression and external review are reported separately in the issue/PR.

## Refinement priorities

1. Preserve one issue/owner and smallest-depth outcome; don't expand blocked work or create duplicate ledgers.
2. Require current inputs, independent review and explicit authority before an effect. High scores never override a missing gate.
3. Persist checkpoints around effects in the existing controller implementation, with receipt-based reconciliation before retry. This branch only specifies that seam.
4. Compare measured outcomes/rework/effort and test one method change at a time. Unknown cost stays unknown.

No scheduler is configured, no recurring job is activated, and no merge/deploy is requested. This design can inform a separately authorized scheduling/runtime task after the current Level 1 qualification gates.

## Shared CI discovery

The B00 adapter loads every `test_*.py` in this folder through the existing shared orchestration discovery, enforcing required design-test identities and rejecting static or runtime skips and unexpected-success results. Missing imports, removed required tests and actual failures remain failures. No workflow file changes or network source fetches. In shallow checkouts lacking the archived commit, unchanged repository file bytes must still match the pinned SHA-256 values; missing or changed source bytes fail. This verifies content identity, not Git ancestry. Score remains 22/50; CI coverage is stronger evidence, not runtime qualification.
