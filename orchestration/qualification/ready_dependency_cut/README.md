# Ready dependency cut — 2026-11-12

This is an immutable decision snapshot for [#252](https://github.com/whiterosecoffee/_BASKET/issues/252), based on main `74d913e8913d630d85451344689e093aeea07efc`. [#136's 25-action comment](https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6803494794) remains authoritative. Nothing here dispatches work, changes a queue, accepts a candidate, or changes another owner's files.

The smallest useful cloud-only cut is the existing **#247 named-port exchange qualification**. Its published main helper and synthetic bytes are sufficient for a bounded contract test; neither Melissa, a legacy archive, #243's composition patch nor an accepted broad map is needed. This is a one-node cut for that narrow outcome, not a claim of globally optimal scheduling or L1-08 completion. An empty set delivers no qualification. #245 reference portability and #246 receipt conformance are complementary second steps, already owned by their existing lanes.

## Readable sequence

1. Preserve the 25 canonical obligations and their owner/acceptance references. Only L1-01, L1-02 and L1-23 are canonically READY for read-only design. All WAIT predecessors remain explicit; provisional branch work does not check them off.
2. Existing #247 owner finishes its pinned positive/negative boundary evidence. Independent acceptance checks exact source and test results. No new assignment is made.
3. Consume #245 portability evidence and #246 receipt evidence when published and reviewed. Two independent second-reuse proposals are specified in the JSON: an independent nested exchange consumer and a no-change monitoring receipt consumer. Both have concrete contract seams and negative tests. Neither is reported executed or accepted by this session.
4. Existing #251/#249/#248/#250 owners supply baseline, dialect, ownership and recovery evidence in their disjoint scopes. Ordinal ranking is judgment about this bounded artifact sequence, not measured savings.
5. Before broad advancement, refresh all ten lane identities and owner results, then let #136/#236 owners decide the next accepted step. Only eight cloud lane claims were visible at the recorded cutoff; two are unknown. No worker is allocated to fill those unknown slots.

## Evidence correction and blockers

The latest pinned #230 disposition already adopted availability-at-cutoff offline. #236's fifth record confirms that wait was resolved. Do not recreate it or re-request the same decision. Before-effect source revision and permission checks remain adopted requirements with runtime implementation deferred to #32/#24, shared contract #103 and acceptance #105. The separate dependency-delta handoff remains with #32.

Laptop execution is required for the existing FETCH/durable-root binding proof, not for synthetic contract qualification. #243's last published head is known, but its Melissa continuation has uncertain local effects and remains owned. Archive-reference-only pointers are nonblocking for clean artifacts. Truly required schema/method/payload bytes and their exact pins are blocking inputs. Approval and predecessor acceptance are separate gates. No deployment, merge or production write is implied.

## Artifacts and verification

- `snapshot-2026-11-12.json`: 25 obligations, source revisions, original owners, six blocker classes, current cloud claims, PR file inventories, selection rationale and two second-reuse seams.
- `canonical-l1-source.md`: retained public repository source comment, supporting exact acceptance-text comparison.
- `task.json`: existing worker-task schema claim.
- `test_snapshot.py`: integrity and adversarial mutations, not a replacement scheduler/validator.

Run from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s orchestration/qualification/ready_dependency_cut -p 'test_*.py' -v
git diff --check
```

Tests verify reference completeness, dependency cycles, owner separation, ranking eligibility, unchanged replay, canonical acceptance retention and honest unknowns. They do not prove candidate behavior or remote claims. Shared CI discovers `orchestration/tests`, not this new folder; its success cannot establish focused coverage. No bridge or CI files were changed.

Publication and actual test results are recorded separately in the issue/PR receipt. Full ten-lane recommendation acceptance remains limited until the missing identities are verified. Every candidate remains distinct from accepted, integrated or operational work.
