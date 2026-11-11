# _MAP — structured system planning

Owner: B00, [#230](https://github.com/whiterosecoffee/_BASKET/issues/230), `work/230-map-system-planning`. Sole write scope `_MAP/**`; current ownership claim is linked in system.json.

Start with **system.json**: architecture pointers, eight system groups, typed relationships, seven module-review patterns, planning flow, queue read/write contract and explicit coverage gaps. **map.schema.json** describes this local planning document and explains fields; it does not replace shared schemas.

Every new or changed module should check the applicable patterns and report evidence or exceptions in its existing issue/PR. Existing architecture, schema, worker library and domain owners remain authoritative. Shared catalog/AGENTS registration needs additive reconciliation by its existing owner; no shared files are changed here.

The canonical queue remains issue #136. This branch is a dedicated top-level planning lane, not a second task ledger. Read fresh queue state before choosing work; record authorized scoped deltas through the existing controller, preserve unrelated obligations, detect drift and verify readback. The JSON describes this contract; it does **not** implement queue execution.

JSON-first Level 1 remains the priority. PR225, PR227 and PR229 are unmerged candidate references. Existing historical method prose can lag later integration; pinned source presence does not imply present operational acceptance. No seed selected, clone, runtime activation, merge or deployment.

Run `python _MAP/validate.py` for local structure/pointers/coverage checks. For existing boundary regressions: `python -m unittest discover -s orchestration/tests -p 'test_component*.py'`. Checks do not establish full-system semantic completeness. Continue expanding source-backed modules and ports inside this lane, recording gaps and queue receipts rather than claiming universal coverage.

**Rebuild direction:** existing components must be rewritten against a cohesive system. Current source pointers preserve behavior/evidence, not an endorsement of legacy reuse. Define the new contracts and patterns first, then queue scoped replacements and acceptance. Additive top-level design diffs should support new use cases without repeatedly refactoring that new design; they do not exempt old components from rewrite. No source is deleted by this planning increment.

Validation prerequisites: Python with `jsonschema`, Git, and the pinned commits in the local object database. On a fresh checkout, fetch the read-only candidate branches `work/226-json-virtual-workflow` and `work/228-requirements-relationship-selection` before running the validator. It reads their pinned bytes with `git show` and never checks out or executes candidate code. Missing commits stop validation rather than silently trusting remote pointers.

Intent reconciliation is explicit in `instruction_semantics`: resolve scope, chronology and purpose, admit one coherent bounded rule, and route shared instruction edits to #201. `archive_microtests` defines small comparisons against pinned old versions: preserve required behavior, accept justified corrections, retire incidental behavior, or leave the difference unresolved. Old output equality is not the oracle. AM1 now has an executed offline microtest; AM2–AM4 are not run. Structural tests alone do not imply archived replay or rewritten-component acceptance.

**First behavioral slice:** `python _MAP/microtests/freshness/run.py` stages a two-child validation/current-use qualification boundary using synthetic fixtures. Seven outcomes are checked against pinned archived schema/runtime and a separate small test model, with four malformed-input and three malformed/contradictory-output rejections. The archived schema accepts an expired record labeled fresh, while archived runtime and the intended clean semantics reject current use. This is useful behavior evidence, not production module reuse or a general workflow engine. The original source and inputs remain unchanged.

**Queue handoff slice:** `python _MAP/microtests/queue_handoff/run.py` executes 12 synthetic traces through pinned archived claim/result/acceptance guards and a separate uncertain-write test model. It covers stale/expired claim, duplicate result, missing/wrong-head acceptance, failed CI and matching/absent/unavailable/conflicting readback. Next means an eligible proposal only; all external effects are zero. Historical finite operator proof is retained, not promoted to autonomous execution.
