# B00-132 — Control-plane consolidation decision and orchestrator handoff

**Decision date:** 2026-11-03. **Authoritative evidence:** GitHub issue/PR state, exact-head checks and approved main. **Worker branch:** `work/132-github-project-control-plane`. **Do not merge/release.**

## Accepted user decisions

1. **Execution coordinator:** Codex through GitHub **provisional default**. User selection arrived as `undefined`; preserve that uncertainty. The existing #136 queue describes Codex as primary coordinator; do not represent this as a newly explicit user selection. Reconfirm only if the coordinator choice materially affects a paid or irreversible action.
2. **Projects provisioning and sync:** reuse B00 issue #134 / draft PR #135 adapter; authorized to pursue supported Projects creation/sync with appropriate credential and dry-run, but credentials and actual Projects URL/ID remain unverified. No new adapter on #132.
3. **Redundant drafts:** evidence-based consolidation with original issue/PR links, test coverage, unique-contract comparison and historical disposition. **No automatic merging or closure merely because files overlap.** B00 should approve any retirement after preserving unique capability.
4. **Execution ceiling:** eligible agent may claim, code on isolated branch, run tests and open **draft** PR. No auto-merge, release/tag, destructive takeover, paid third-party dispatch, or unauthorized shared-path modifications.

## Observed overlap (verify current head before acting)

| Component | GitHub owner | Disposition |
|---|---|---|
| Existing `basket.worker_task@1`, `basket.worker_resolution@1`, `worker_protocol.py` | main B00 governance / #106 PR #107 candidate | Reuse canonical contracts; do not reinterpret task schema |
| Project sync API, idempotent item import, Project field mapping, collision/review/evidence guards | #134 PR #135: `orchestration/project_sync/**` | **Primary Project adapter**; 29 adapter tests reported on branch, exact-head independent CI still required |
| Routing, Project board guide, spark claim check | PR #123 | Retain separately; its agent instructions/ownership need governance review |
| Offline snapshot reducer | #132 PR #133: `orchestration/project_control_plane/**` | **Candidate for retirement**. Current reducer duplicates #135 and accepts a noncanonical flattened claim; tests use synthetic simplified shapes. It must NOT be advertised as compatible with canonical worker-task@1 without additional evidence. Do not add a second live adapter or runtime. |
| Existing execution queue | #136 | Canonical issue-based coordination and handoff recipient |
| Queue admission/schema-backed scope compilation | #138 | Separate B00 candidate; avoid a second issue registry |

## Immediate acceptance strategy for #132 (do not prematurely claim A3–A5)

1. Treat #133 as a bounded historical candidate, not a second execution plane. Preserve code and tests until #136 independently compares its unique behavior to #135.
2. Run exact-head `python -m unittest discover -s orchestration/project_control_plane -p 'test_*.py' -v` and inspect actual failures. Note that a legacy test passing on flattened claims is **not** proof of worker_task@1 compliance. Add a schema-valid fixture and negative cases on this branch **only if** #135 lacks the equivalent, and B00 allocates no conflicting write paths.
3. Check #135 coverage of: conflicting active claims across PR changed paths, renamed files, ambiguous branch matching, zero/missing checks, stale SHA, no post-merge inference, native dependency handling, and idempotent project sync.
4. If all useful behavior is covered by #135 with tests, recommend closing PR #133 **unmerged** as superseded after recording side-by-side evidence. Keep issue #132 as a linked historical resolution. If something is missing, raise an explicit #134 handoff rather than modifying `project_sync/**` from #132.
5. B01 independently tests whichever implementation survives; workflow files remain B01-owned.

## Acceptance gates for the combined outcome

- **Project identity:** existing Project discovered or created by #134, verified GraphQL node ID, URL, user/organization ownership and write permissions. On failure, explicitly BLOCKED.
- **Live board:** items mapped idempotently to existing issue/PR IDs; views and required fields verified, no duplicate task database.
- **Claim and code:** one valid schema claim, branch from main, exclusive paths, no collision; blocked on ambiguous owner.
- **Test and review:** exact PR head CI checks and independent component coverage; failures/missing evidence visible.
- **Main:** post-merge main checks separately verified; no automatic integration.
- **Lifecycle demo:** one low-risk case shows Ready→Claimed→Draft PR→Validation (and later main verification only after user-approved merge); failure/retry does not duplicate claim or branch.
- **Automation:** no paid agent, destructive takeover or spontaneous ChatGPT conversation creation.

## Receiver prompt — existing Codex orchestrator #136

> Read GitHub current main and all open changed-file lists. Retrieve #132/PR #133, #134/PR #135, #136, #138, PR #123, #106/PR #107 and canonical worker schemas. Codex via GitHub is the **provisional** primary coordinator; the user selection was undefined, not an affirmative new decision. The user authorized #134 as the Projects setup/sync path, evidence-based consolidation of redundant drafts, and automatic **claim→code→test→draft PR only**. No automatic merge, release, paid dispatch or cross-domain writes.
>
> First compare actual implementation and regression coverage: decide whether #133's offline reducer has independently valuable behavior not present in #135, or recommend it for evidence-preserving closure as superseded. Do not copy its flattened task assumptions into canonical schemas. Keep #134 owner of Project API, #123 owner of board/routing, #138 owner of queue admission, B01 owner of workflow verification. Use issue #136 Q06 to track verified Project ID/URL, fields/views and twice-idempotent import or precise credential blocker. Prioritize schema-valid claims and exact-head checks, then one low-risk lifecycle demo. Preserve ownership boundaries and issue/PR history. Report one next action with observed test run URL, tested head SHA, blockers and non-verified gates; do not claim operation based on configuration alone.
