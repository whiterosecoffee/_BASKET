# ORCL vector orchestration

Status: v0 (unverified in production; unit-tested offline only). Issue #82.
Partition logic: this folder only tells computers and agents how to find, claim, run and evolve the ORCL vector sets. The analyses themselves live in `research/ORCL/Forward_Multiple/` (#80) and `research/ORCL/Range_Traversal/` (#81). Nothing here changes an analysis.

## What this is
A thin ORCL layer on top of the existing orchestration prior art:
- the `basket.agent_assignment@1` contract and provider adapters (draft, #78/#79),
- the worker claim and resolution payloads (`orchestration/WORKER_PROTOCOL.md`),
- the B00 controller that will own leases and retries (#32), B08 transport (#34/#53), B01 tests (#65).

## What this is not
- Not a daemon, scheduler or dispatcher. Nothing runs by itself.
- Not a lease store. Claims and leases are never written to files here.
- Not a merge authority. No agent merges; B00 and the user decide.
- Not live proof of anything. `status.py` reports a GitHub read at one moment.

## Files
- `vectors.json`: static registry of vector sets, files, branches, issues, write paths, dependencies, proposed owner.
- `assignments/ORCL-FM.assignment.json`, `assignments/ORCL-RT.assignment.json`: `basket.agent_assignment@1` envelopes. Null SHA and null lease mean unclaimed and unverified.
- `LAUNCH_PACKETS.md`: copy-paste launch text per provider and the multi-computer protocol.
- `status.py`, `test_status.py`: read-only drift, scope and collision report from live GitHub state, and its offline tests.
- `spark-proposal.json`: proposed ORCL spark (B22) for B00 to ratify. It was validated against `orchestration/validate_sparks.py` on a temporary copy; `sparks.json` is untouched.

## Roles
- You: set direction, approve any write beyond a branch, authorize merges.
- B00: arbitrates ownership of `research/ORCL/**` and registers the spark. Currently in succession (#59, #60).
- Agents (ChatGPT, Codex, Claude, VS Code agents): execute one assignment on one computer, return a resolution payload. No standing authority.
- GitHub: the only shared state: issues, branches, PRs, head SHAs, CI.
- `status.py`: the observer. Run it before any claim and after any push.

## Multi-computer protocol (interim, until the #32 controller exists)
1. Fetch fresh: `git fetch origin`, then run `python research/ORCL/Orchestration/status.py`. Any hard flag stops the run.
2. Pick one vector set. Check its issue for an open claim comment. If one exists, stop or hand off.
3. Claim by posting a `basket.worker_task@1` comment on the vector's issue naming the computer or agent label and the exact base SHA. This is an interim convention, not a lease.
4. Work only inside the assignment's exclusive write paths, on a unique branch (see Evolution below).
5. Append an entry to the folder's `REVISIONS.md`. Never rewrite an earlier entry.
6. Run the relevant tests and `status.py` again. Commit, push, open a draft PR.
7. Post a `basket.worker_resolution@1` comment with the head SHA, real checks only, blockers and one next action.
8. Pin analysis runs: every run of a vector records the commit SHA of the instructions it used.

## Evolution
Each revision is a new issue and a new branch from main, named `work/<issue-number>-<objective-slug>`. Branch identities are never reused (AGENTS.md). Revisions are append-only in `REVISIONS.md`.
Known conflict: the vector files are not on main yet, so a revision branched from main would not contain them. Until #80 and #81 merge, revisions need either the owning conversation or a B00-approved base. Merging the draft PRs fixes this.

## Drift flags (from `status.py`)
Hard (exit 2): BRANCH_MISSING, SCOPE_VIOLATION, COLLISION:#n, MISSING_FILE, FILES_TRUNCATED, TREE_TRUNCATED.
Informational: UNRATIFIED, UNMERGED, NO_PR, DRIFT (branch behind main).
Evidence failure (exit 3): any API error. Fails closed; never reports a stale snapshot.

## Not built (owners)
- Leases, retries, input fingerprints: B00 #32.
- Authenticated transport and a persistent runner: B08 #34/#53.
- Fail-closed CI for forged leases and stale SHAs: B01 #65.
- Scheduled status runs and notifications: unowned; needs a persistent process (B08) or a scheduled task you choose.

## Open decisions
- Ratify spark B22 (B00), or split ownership between B04 and B06.
- Whether `status.py` should be wired into CI (B01).
