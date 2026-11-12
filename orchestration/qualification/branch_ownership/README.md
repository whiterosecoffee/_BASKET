# Branch ownership qualification

Issue #248 / B00. Candidate Level 1 qualification for queue #136, based on main
`74d913e8913d630d85451344689e093aeea07efc`. This is a synthetic adversarial corpus
and a thin test adapter over published functions, not a lock service, controller,
registry, live ownership ledger, clean runtime or permission engine.

## Reproduce

From this checkout's root with Python 3.10+ and the existing jsonschema dependency:

```sh
python -B -m unittest discover -s orchestration/qualification/branch_ownership -p 'test_*.py' -v
python -B orchestration/qualification/branch_ownership/replay.py
```

The second command prints JSON and writes nothing. Compare its parsed result with
`observed.json`. All timestamps, issue numbers 9001/9002, task IDs, paths and leases
in `cases.json` are synthetic. The `live_connector` input value is deliberately
used to exercise the existing freshness guard; it is not evidence of a live call.
`context_only` records facts the selected API cannot consume, never hidden inputs.

## Evidence and acceptance

Actual first run: **21 tests passed, zero failures/errors/skips** (17 named cases
plus coverage, deterministic replay/immutability, bad source pin and malformed
fixture checks). `observed.json` records all 17 observations and repeats, with zero
observation mismatches and **seven explicit enforcement gaps**. Passing the corpus
means these bounded observations reproduce; it does not mean the unsafe cases are
prevented. Tests were independently authored for this lane, not independently
reviewed by a second agent. No operational, integrated or accepted-runtime claim.

`cases.json` separates normative disposition from the published function's expected
output. `sources.json` binds policy references and all invoked repository source /
schema files to SHA-256 at the base commit. Hash checking happens before imports
and after replay, so changed dependencies fail closed; no source is copied or
modified. Source pins also support shallow checkouts without pretending historical
Git objects are present. `preflight.json` is the actual historical 70-open-PR file
inventory, not continuing authority. Owner issues #78/#103/#106/#201/#24/#32 and
current #136 comments were read. No `.agents` skills exist in the pinned main tree.

| Case family | Observed behavior | Bounded disposition |
| --- | --- | --- |
| Unique issue/branch and owned subtree | Worker claim validates; disjoint PR produces no collision | Structurally valid; no execution permission |
| Two issues using one branch | Worker branch prefix mismatch rejected | Reject branch reuse |
| Two tasks sharing one issue/branch | Event validation returns normally | GAP: no cross-task single-writer check |
| Existing changed file / overlapping claim globs | Collision list / existing intersect function detects overlap | Block conflicting write; preserve owner |
| Unwritten competing claim | No PR collision returned | GAP: inspect live issue claims separately |
| Stale branch origin / claim timestamp | Worker check returns no error | GAP: no origin-SHA or claim-age verification |
| Old GitHub snapshot / expired lease | Freshness guard rejects / expired task reported, capacity untrusted | Refresh evidence; no automatic takeover |
| Unconfirmed previous write | Pending attempt returned, retry_required=false | GAP: inspect outcome before retry; false is not permission |
| Broad wildcard | Outside-owned wildcard rejected; broad B00 domain accepted | GAP: domain ownership is not an exclusive worker allocation |
| Archived closed PR reference | No active path collision | Reference does not grant ownership or become a prerequisite |
| Archive label on an open writer | Actual open changed-file collision remains | Label cannot erase current ownership |
| Pending approval | Reported blocker preserved; merge_authorized=false | GAP: approval adjudication absent; distinct from path conflict |

The seven gap records cover shared issue/branch writers, unwritten claims, stale
base, stale claim, uncertain prior write, broad domain allocation, and approval.
The archive cases exercise PR state, not an archive-role interpreter. The adapter
never filters a current open writer merely because context labels it archived.
The collision function does not certify complete inventory, glob completeness,
active worker identity, exclusion of races, permissions or distributed fencing.

## Ownership and next action

Writes are exclusively `orchestration/qualification/branch_ownership/**`.
Published manager/planner/worker checks are read-only test dependencies. Archived
and external provider implementations are not prerequisites. #243/PR244 clean
seed, #241 data flow, #207 runtime, `_MAP`, loop design, schemas, shared tests and
CI remain untouched. No live claims, leases, journals, provider rows or credentials
are written by replay. No merge or deployment.

Final run: **22 qualification tests passed**, including a new saved-observation
equality check; **10 worker-protocol and 23 manager regression tests passed**,
zero failures/errors/skips. No failed test attempts.

The existing shared workflow does not discover this nested directory; any green
shared CI cannot be counted as execution of these 22 tests. Hosted discovery and
independent acceptance remain unverified unless separately evidenced. Next action:
B00/#32 and #78 review the seven gap dispositions against the existing owner
contracts before selecting any minimal owner-scoped repair; do not install a
second controller or transfer ownership from this qualification report.

## Attempt history

Read-only discovery initially used incorrect connector argument names; those calls
returned argument errors without execution. The task-comment call was denied by
automatic review because the connector was PR-targeted while #248 is an issue.
No comment was posted. After verifying the target was the newly created issue,
the explicit issue-update operation successfully attached the task JSON to its
body. The issue/branch/checkout and qualification tests then succeeded. This is
not a pending publication approval and is separate from repository path conflicts.
GitHub CLI authentication is unavailable; repository reads use public Git and
publication uses the connected GitHub API. No credentials were read or modified.
