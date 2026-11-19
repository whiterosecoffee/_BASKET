# GitHub Projects synchronization adapter — B00 #134

This is a tested **partial increment**, not a deployed control plane. GitHub Issues,
PRs, Project items and exact commit checks remain authoritative. Generated reports
are dated observations, never a competing task database. No executor is connected.

## Ownership and reuse

Worker #134 owns `orchestration/project_sync/**` and, after user-approved Copier
adoption, `orchestration/bootstrap/**`, root `copier.yml`, `orchestration/sparks.json`
and `architecture/version-manifest.json`. See `../bootstrap/README.md`. Main baseline:
`afc4ada7bc6d7294071b3610fa77e59b206b6312`. PR #2 is merged; no bootstrap exception applies.

The 2026-11-10 user-authorized continuation additionally reconciles only the
generated `orchestration/planner/worker-scopes.json` against this branch's catalog.
PR #25's branch, queue, goals, and implementation are preserved. See
`RECONCILIATION-2026-11-10.md` for the bounded correction and verification record.

- Reuse `orchestration/worker_protocol.py` for schema, path and resolution evaluation.
- Preserve #132 / PR #133's offline reducer, including its owned subtree. This adapter
  adds the missing API/mutation layer and translates actual worker-task@1 objects;
  it does not replace that branch or import unmerged code into main.
- Preserve PR #123's board guide, routing and claim checker. No routing assignment
  establishes a connected executor or permission to expand ownership.
- Existing `github_snapshot.py` is queue-driven/read-only; this collector instead
  enumerates all open repository work and exact-head checks. No changes to its API.

## Run

Use the repository's existing Python/jsonschema environment and authenticated `gh`.
No new dependency/service is introduced. Run from the repository root:

```sh
python -m unittest discover -s orchestration/project_sync -p 'test_*.py' -v
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
python orchestration/project_sync/control.py --report /tmp/basket-project-report.json
python orchestration/project_sync/control.py --create-project --report /tmp/basket-project-plan.json
# Explicit additive mutations, after reviewing the dry-run report:
python orchestration/project_sync/control.py --apply --create-project --report /tmp/basket-project-applied.json
```

The default owner is `whiterosecoffee`; organization Projects require explicit
`--owner ORG --owner-kind organization`. Exact title matches are reused. Multiple
matches block selection. `viewerCanUpdate` is checked before existing-Project writes;
the create mutation is the authoritative owner-create permission check. Read-only
discovery cannot prove create authorization. There is no token printed or embedded.

To connect an existing board with any title, select its number or native node ID:

```sh
# Existing user-selected board: https://github.com/users/whiterosecoffee/projects/2
# Use --native-status only after verifying Todo/In Progress/Done on that board.
python orchestration/project_sync/control.py --owner whiterosecoffee --project-number 2 --report /tmp/basket-project-2-plan.json
# After reviewing the dry-run and authorizing additive field/item synchronization:
python orchestration/project_sync/control.py --owner whiterosecoffee --project-number 2 --apply --report /tmp/basket-project-2-applied.json
```

`--project-number` and `--project-id` are mutually exclusive with each other and
`--create-project`. Selection is restricted to Projects visible under `--owner` and
`--owner-kind`, never a global node lookup. An absent, closed, ambiguous or
inaccessible explicit target blocks; it never falls back to the default title or
creates a replacement board. Renaming the selected board does not change its
identity. Without a selector, existing exact-title discovery/create behavior is
unchanged. These flags do not verify live access, configure views, install a
scheduler or authorize workflow/secrets changes.

GitHub CLI uses supported credential storage or `GH_TOKEN`. A user-owned Project
requires a credential authorized for Projects read/write (classic PAT `project`,
plus appropriate repository access; or a supported fine-grained token with Projects
read/write and repository read access). Repository `GITHUB_TOKEN` alone does not
grant user Projects v2 access. The connected ChatGPT GitHub tools in this session
have repository operations but **no exposed Projects/GraphQL endpoint**. Local gh
authentication was invalid and its proxy unreachable. No actual Project ID, URL,
field, view or write permission has been verified.

Exit 2 means blocked/partial; report JSON includes the operation and structured
reason. Read rate limits have bounded retries; writes are never retried blindly.
After a lost mutation response, repeat the whole command: it re-reads Project state
before another write. Additions use native content IDs; existing field values are
compared before updating. Existing duplicates stop synchronization; nothing is
deleted, closed, merged, reassigned, released or dispatched. Historical `--snapshot`
input is allowed for audit, and prohibited together with `--apply`.

## Fields and views

The adapter creates missing text fields Domain, Spark ID, Worker, Branch, Validation
and Acceptance; DATE Last Verified; select Priority, Execution Mode and Status.
It **does not rewrite existing option IDs**. The default mode expects the full
lifecycle options in `api.STATES`. For a board using GitHub's standard `Todo`,
`In Progress`, `Done` options, explicitly pass `--native-status` on both dry-run and
apply. This mode preserves the native Status field and adds a single-select
`Workflow State` field containing the detailed lifecycle. BACKLOG/READY map to
Todo; COMPLETE/CANCELLED map to Done; other lifecycle states map to In Progress.
The detailed field distinguishes BLOCKED, FAILED, draft/review and cancellation;
coarse Status is not acceptance evidence or proof that a worker is active.
Configure detailed views using Workflow State when this mode is selected.

Existing field types/options and duplicate names are preflighted before any field
is created. Incompatibility blocks all configuration writes and item updates.
Neither mode infers priority or changes an existing Priority value unless a caller
explicitly supplies that field. No priority order or ready/complete inference is
introduced by this compatibility option.

Keep native assignees, linked pull requests, issue dependencies and milestones for
ownership/PR/Blocked By/Milestone. Do not create parallel text copies. Worker is
the observed GitHub assignee; an unassigned claim is blocked. Branch is taken from
the claim/actual PR. Last Verified is created but intentionally not stamped merely
because a run occurred; acceptance/integration still needs independent evidence.
Priority and execution mode are not inferred from agent names or stale catalogs.

`views.json` contains the ten requested **unapplied view specifications**. View
creation/filter mutation is not implemented or verified by this adapter; configure
through the Project UI after authorization and check each filter against actual
field names. Views show the same native items, without making copies.
Use the report's `view_specifications` for the selected mode: `--native-status`
rewrites the detailed filters, grouping and displayed lifecycle column to Workflow
State. The original `views.json` targets custom lifecycle Status, not native mode.
Generated specifications remain unapplied and require a real Project UI check.

## Explicit native queue order

The optional `--queue-order 134,201` uses canonical **open issue numbers** from the
fresh repository observation. Replace these example numbers with the operator's
chosen queue; this is not a recommended priority list. It moves the selected native
Project items to the front in that order, leaving every unselected item (including
PRs, draft/redacted items and other-repository items) in its prior relative order.
No Rank field, local queue database, new issue or duplicate Project item is created.
Existing Priority values and worker/dependency ownership are unchanged.

```sh
# Review a plan first; add --native-status if that is the board's configured mode.
python orchestration/project_sync/control.py --queue-order 134,201 --report /tmp/basket-order-plan.json
# Existing synchronization runs first, followed by explicit native position writes.
python orchestration/project_sync/control.py --apply --queue-order 134,201 --report /tmp/basket-order-applied.json
```

For a bounded position-only change on an existing board, add `--order-only`:

```sh
python orchestration/project_sync/control.py --project-number 2 --order-only --queue-order 134,201 --report /tmp/basket-order-only-plan.json
# After reviewing the plan, serialize writers and apply the same explicit order:
python orchestration/project_sync/control.py --project-number 2 --order-only --queue-order 134,201 --apply --report /tmp/basket-order-only-applied.json
```

This mode requires `--queue-order` and an explicit `--project-number` or
`--project-id`. It cannot create a Project or combine with `--native-status`.
It still collects fresh repository evidence and reports ownership/dependency gates,
but skips field configuration and item synchronization entirely. Every selected
issue must already be on the board; missing or duplicate identities block before
any position write. It never imports an item, changes field definitions/values,
Priority or Status, or applies view specifications. Reports identify
`sync_mode: order_only`; their derived record fields are observations only, not
applied board values. Repeating an unchanged order performs zero writes. Historical
`--snapshot --apply` remains forbidden. Full synchronization remains the default
when `--order-only` is absent. This is a bounded command, not a scheduled worker.

The flag does not select a "next ready" issue. Blocked issues may be ordered, but
remain blocked; `queue_order.blocked_issues` exposes those gates and
`dispatch_authorized` stays false. Closing an upstream issue alone does not clear a
declared completion dependency. The review/rework cycle and launch authorization
remain with the existing owner/controller contracts, not Project position.

All requested issue numbers are validated before Project setup. PR numbers,
missing/duplicate issues and ambiguous native identities are rejected. In full mode, position
writes run only after field/item synchronization has no operational failures.
The full synchronization covers all collected records, not only the ordered
subset; `--apply --queue-order` is not a position-only command.
Dry-run plans include dependent imports without executing them. Repeating an
unchanged successful order produces zero position writes.

The adapter uses GitHub's native `updateProjectV2ItemPosition`, with complete
POSITION-ascending pagination and pre/post-write order-and-identity comparisons.
Uncertain mutation responses stop, and the next invocation reads actual state
before planning another move. Serialize all Project writers: GitHub exposes no
position compare-and-swap or atomic multi-item transaction. Detected concurrent
changes stop further moves without undoing either writer's changes; this is not a
lock and cannot eliminate the read/write race. If a later move fails, previously
verified moves can remain applied: no rollback is attempted. Inspect the partial
operations, then reread/replan the full order. Views sorted by a field may not
display native item order. No live board/view behavior has been verified here.
Each move reads the entire paginated order twice. Large boards or long selections
can hit API limits and stop partially; bulk-order scalability is not established.
See [GitHub's Projects GraphQL reference](https://docs.github.com/en/graphql/reference/projects)
and `ORDERING-2026-11-10.md` for source and verification boundaries.

## Evidence and state boundaries

- Validate fenced worker claims against existing schemas, spark scopes, issue/task/
  branch identity and observed branches; ambiguous registrations block ownership.
- Compare declared glob/subtree scopes conservatively and actual PR changed files,
  including renamed source paths. Open PRs do not establish worker activity or
  authorize takeover. False-positive overlap flags require B00 arbitration.
- Native blockers and declared completion dependencies block claim/readiness.
  Declared dependencies stay conservatively blocked until a separately verified
  resolution is supplied; closed issues alone never clear them in this increment.
- Associate PRs by a validated exact branch. Issue-number-prefixed branches can
  be displayed for legacy work, but never validate an absent/invalid worker claim.
- Draft PRs remain DRAFT_PR (or BLOCKED); current-head failures remain visible in
  Validation. Missing/skipped/stale tests are unverified. Most recent check/workflow
  attempts supersede old attempts. Branch green never implies integration.
- `resolution_gate` composes the existing evaluator and additionally requires
  acceptance, no blocking report, non-draft merge, a main/merge ancestry comparison,
  and an explicit set of passing applicable main workflows before COMPLETE.
  This interface is not wired to auto-complete: open-work synchronization never
  emits COMPLETE or READY, and does not ingest closed/merged history yet.
- Categories are conservative: Planned for no executable claim, In progress for
  observed open PRs, Blocked for invalid ownership/dependencies. Other requested
  maturity dispositions require independent resolution evidence; they are not
  guessed from prose, closure or labels. PR rows retain their own CI state even
  when the associated issue is blocked.

Limitations: collection aborts on endpoint failure or observed PR/main head movement.
GraphQL top-level pagination and REST lists are supported; more than 100 field values
on an item block comparison rather than truncate it. Initial all-open-work collection
is API-intensive. The dated audit records the actual capture limits. No stale-owner
reassignment, claim-writing transaction, stale-PR closure or automatic agent invocation
exists. Launch/eligibility can consume the validated report, but launch is not enabled.

## B01 handoff (tracked in #134; no second issue created)

Ready-to-paste receiver prompt:

> B01: inspect #134, PR #133 and PR #123, then independently verify this adapter at
> the exact PR head. Run both test commands above. In your own worker issue/branch,
> integrate tests into B01-owned CI and review `workflow.yml.example` before placing
> an approved version under `.github/workflows/`. Use trusted main code for any
> job receiving PROJECTS_TOKEN, serialize Project writers, provide read-only
> repository permissions and an owner-authorized Project token. Verify one real
> dry-run and then actual idempotent synchronization twice. Capture Project ID/URL,
> permissions, configured native relationships/fields/views and resulting item IDs.
> Do not merge #134, #133 or #123 or claim an executor connected. This request is
> pending; B01 has not been observed receiving or starting it.

The example is **inactive**, uses main code and no PR checkout, and requires the
implementation to be reviewed/integrated before it can execute. No automatic
event synchronization is installed by this B00 PR.

## October 30 reversal dependency

PR #125 is offline SpotGamma HIRO intake, not a verified reversal engine. Preserve
B02's minute-data/durable-storage/FX/TTD contract → B06 #108 traversal → B01 replay.
Required B06 observations: dollar-volume price impact, direction/velocity,
acceleration, seller exhaustion, repeated support, failed breakdowns, ETF versus
constituent divergence and reversal confirmation. This worker changes no market,
valuation, narrative, source-verification or traversal runtime.
