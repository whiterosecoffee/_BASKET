# Build the next useful block from the existing boundary

Owner: B00 #156 / PR157. Baseline: main `d1b4888` (2026-11-10).
This is a small adoption kit, not a new framework. The target is less time to an
accepted, reusable outcome, not more manifests, tests or abstractions.

## What to reuse

- **Interface:** `schemas/component-blackbox.v1.json` from merged PR104. Reuse its
  manifest, call/result and source/artifact references. No new shared schema.
- **Method:** `architecture/BLOCK_ENGINEERING_METHOD.md` for stages and reviews.
  Its historical description of PR104 as unmerged is superseded by merge
  `9021ffb`; its planning-only qualifications still apply to unimplemented blocks.
- **Scaffold:** the worked `example()` in
  `orchestration/tests/test_component_conformance.py`. Copy only the manifest,
  domain fixture and thin boundary mapping, not the shared validator or algorithm.
  For project bootstrap use existing #134/PR135 Copier work. It is a separate
  unmerged project template, not a dependency for this kit. Do not write a second
  generator or copy an entire repository to create one block.
- **Reusable check:** `orchestration.component_conformance.check_exchange`.
  Provide an approved manifest, actual call/result, an explicit reference-to-bytes
  map and an independently computed expected input digest. Nothing is fetched or
  executed from a manifest. It raises on failed checks and returns no qualification
  badge. Existing `jsonschema` and its `referencing` dependency suffice.
- **Lifecycle:** existing worker-task/resolution/evidence schemas, GitHub issue,
  branch, PR and accepted main. Keep planned, branch-tested, independently
  accepted, integrated and operational claims separate. No second status ledger.
- **CI:** existing orchestration discovery already executes this suite. Domain
  owners reuse their own tests; B01 owns the existing exact-source gate and
  shared workflows. Never run arbitrary manifest `test_command` values.

## Smallest repeatable recipe

1. Name one consumer and the useful output it needs. Find existing code, schema,
   owner and fixture first. Choose reuse, configure, extend or build; record why.
   Internal helpers inherit their enclosing capability's boundary.
2. Verify current main and active ownership. Obtain exact disjoint paths from B00.
   Write the input/output meaning and a representative expected output before code.
   Preserve missing values and failure meanings rather than inventing defaults.
3. Adapt the fixture specimen: component ID/version, owner, typed ports, assumptions,
   effects, declared errors, actual schema/content hashes and owner-specific tests.
   Pin real code separately in release evidence. The example's `a...a` code SHA is
   deliberately a shape-only placeholder and must never be used as execution proof.
4. Invoke the existing pure calculation behind a thin adapter. Test the expected
   useful result, one likely failure, unchanged-input replay and the receiving
   consumer. Add only risks specific to this block, not copies of all shared tests.
5. Call the common conformance check. Supply bytes already obtained through the
   authorized owner/resolver. Payload schemas in this helper are self-contained
   Draft 2020-12 with local fragment references; external references fail closed.
   A different schema dialect or multi-file registry needs an explicit extension,
   not fetching arbitrary references during validation.
6. Run focused tests, affected existing consumers and required aggregate checks.
   B01 independently checks actual source SHA, nonzero execution and unchanged
   source. Keep draft status until accepted; verify main after authorized integration.
7. Record measured elapsed work and rework against the accepted outcome. Apply
   the recipe to a second real consumer before expanding the abstraction.

## Executed exemplar and check boundaries

The specimen imports B00's existing `worker_protocol.evidence_check`, supplies the
existing dated B05 task/resolution/GitHub fixtures and current spark catalog, wraps
its real output, validates its bytes and lets a separate consumer decode the result.
The consumer asserts the expected phase, one passing historical CI check, no errors
and `merge_authorized == false`. A second execution proves deterministic output and
no input mutation. A stale-CI variant invokes the same evaluator and requires an
`evidence_invalid` verdict, while the enclosing calculation itself succeeds.
It does **not** authorize a merge or claim current GitHub state.
The in-test payload schemas are fixture contracts, not newly approved public APIs.

The shared tests cover actual payload/schema/source/method hash mismatches, missing
references, invalid payloads, duplicate/required/optional/unknown ports, wrong
component/version/run/as-of/input digest, typed failures, strict dates and no
implicit file/network/command execution. These common risks are tested once.

This is bounded **conformance**, not complete semantic qualification. Domain owners
still verify as-of availability/freshness, units/FX/session/calendar, source truth,
entitlement, source-class meaning, correction lineage, effects/authorization,
compatible dependency versions and actual code/execution identity. A test explicitly
shows descriptive unit/time/access fields cannot establish these facts. The kit
checks the bytes of a superseded reference, not the validity of its revision chain.
Input digest serialization is the consumer's documented rule; this example hashes
canonical JSON input bindings only. Do not silently impose it on existing domains.

Run from repository root with the existing pinned environment:

```sh
python -m unittest discover -s orchestration/tests -p 'test_component_conformance.py' -v
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
```

## Outcome measures and stop rule

Use existing issue/PR and worker-attempt records, not a new metrics store. Record
start, first passing consumer, accepted result, active work seconds, rework seconds,
failed attempts and verified reuse count when actually measured. Distinguish wall
clock waiting from active work. Token/cost data stays null if unavailable.
Compare the first three similar real blocks by time to first useful output and
accepted output, including integration and rework. Test count is a guard against
missing execution, never a productivity target. No time saving or ROI is claimed
until comparable measurements exist. Stop extending the kit when the next block
only needs domain code and fixtures.

## Existing owners and next adoption

B00 #103/#156 owns the shared boundary/adoption recipe; #105 B01 owns independent
acceptance, with #214's existing source gate reused rather than cloned. B01 may
later consolidate reviewed execution metadata and run shared harness regressions
once per workflow, without changing domain assertions. #134 keeps Copier/project
bootstrap. B06 #108 keeps traversal; B17 #100 keeps market context. The next domain
pilot belongs to one of these existing owners after its scope is confirmed. Neither
is modified or declared qualified by this B00-only example.
