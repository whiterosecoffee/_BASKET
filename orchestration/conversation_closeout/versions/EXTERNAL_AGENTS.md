# External Codex / Claude Code: one review request file

Codex CLI, Claude Code, Copilot and a human can use the same interface. GitHub
Issues and PRs remain the coordination record. This helper prepares the existing
QC intake request; it does not start an agent or create a second queue. The
provider-neutral assignment contract remains with [#78 / PR79](https://github.com/whiterosecoffee/_BASKET/pull/79).

## Existing contracts and destination

- Assignment: existing `basket.worker_task@1` from the source issue, with its
  existing branch, exact authorized paths, dependencies and acceptance.
- Work result: existing `basket.worker_resolution@1` on the source issue/PR.
  This request is an additional closeout-review pointer, not a replacement.
- Request: the unchanged object consumed by `qc_intake.validate_request` and
  `enqueue`: `request_id`, `task`, `source_pr`, `review_kind`, `artifacts`,
  `item_ids`. `review_kind` remains `closeout_semantic`.
- Artifact: repository-relative path, full commit SHA, SHA256 of exact bytes,
  role `primary` or `handoff`. At least one primary and exactly one handoff.
- Authoritative project queue: [issue #136](https://github.com/whiterosecoffee/_BASKET/issues/136).
  B00's existing review-reference index is `QC_QUEUE.json` on this PR179 branch.
  It is not a second project lifecycle. Main availability must be verified after
  integration, not inferred from this draft.

The smallest adaptation is a local builder around the existing intake contract:
lower error risk than manually calculating hashes, low implementation cost,
reversible and no new service to operate. Manual JSON remains compatible.
A replacement queue/provider SDK would add state and authority without helping
this bounded file handoff, so neither is introduced. Time/cost savings are not
measured.

## Use from either external coding agent

1. Read current `AGENTS.md`, the source issue, actual branch/PR ownership and
   assigned acceptance. Resolve any active writer conflict before changing files.
   The helper only checks the supplied claim against its pinned catalog; it does
   not authenticate the claim, grant a lease or establish current permission.
2. Work in the existing source branch. Persist primary work and a complete
   handoff in paths owned by that task. Include top-level stable records such as
   `O1: obligation` and `K1: knowledge`, with evidence, limitations, destinations
   and one next owner action. Keep credentials and private/raw payloads out.
3. Commit the source artifacts and preserve the full commit SHA. Push under the
   task's existing authority. Local Git objects are not proof of GitHub delivery.
4. Run the helper below. Use an already reviewed helper checkout containing this
   module. While PR179 is unmerged, a separate detached worktree at its reviewed
   full commit SHA avoids switching or modifying the source branch. Do not copy
   another worker's files into the source branch just to run the helper.

Requirements: Python 3.10+, Git, and the repository's `jsonschema>=4.23` dependency.
No provider SDK, credential, hosted service or network connection is used by
the helper. In the following shell template, replace every placeholder with
the actual existing task values. Paths after `--primary`, `--handoff` and
`--output` are relative to the SOURCE checkout, not the helper checkout.

```sh
# Optional one-time helper worktree, after fetching and verifying its revision:
git worktree add --detach ../basket-qc-helper <REVIEWED_HELPER_FULL_COMMIT_SHA>
cd ../basket-qc-helper
python -m orchestration.conversation_closeout.versions.qc_submit \
  --source-repo /absolute/path/to/source-checkout \
  --task /absolute/path/to/existing-worker-task.json \
  --source-pr <EXISTING_SOURCE_PR_NUMBER> \
  --revision <SOURCE_FULL_COMMIT_SHA> \
  --primary <OWNER_PATH/primary-file> \
  --handoff <OWNER_PATH/complete-handoff.md> \
  --item-id O1 --item-id K1 \
  --output <OWNER_PATH/qc-request.json>
```

Repeat `--primary` for other evidence artifacts and `--item-id` for every handoff
ID. The existing task may be saved locally from its authenticated source issue;
the helper does not infer or rewrite it. The output directory must already exist
inside the source checkout and be within the task claim. A task with no owned
metadata destination must obtain one from its controller, not invent a path.

Only committed bytes are hashed, even if the worktree is dirty. `HEAD`, branch
names, shortened SHAs, missing/non-regular blobs, unsafe/unowned paths and obvious ID omissions
fail. Output is normalized JSON. Repeating identical inputs is a no-op; changed
content requires a new filename. Existing files, symlinks, the shared QC_QUEUE
and reviewer archive files are never overwritten. There is no file lock or
cross-process ownership lease; use a trusted, single-writer local checkout.

Success reports `created` or `unchanged`, with `submitted: false` and
`accepted: false`. Exit 2 is blocked; do not publish a stale output after failure.

5. Commit the generated file in the same authorized source branch and push it.
   This second commit avoids the circular problem of a request referring to its
   own not-yet-created commit. The request keeps the earlier artifact revision.
6. Verify GitHub can return the request file and every artifact at the pinned
   revisions. Then post this marker and the immutable file URL on the EXISTING
   source PR, under the task's authorized repository communication scope:

```text
<!-- basket-qc-submit@1 -->
Request file: https://github.com/whiterosecoffee/_BASKET/blob/<REQUEST_COMMIT>/<OWNER_PATH/qc-request.json>
Request ID: <request_id printed by the helper>
Review the existing pinned request using the B00 intake contract. This is a
submission, not accepted intake or completion.
```

The subscribed B00 intake worker reads this small file, verifies source PR/issue,
task ownership, immutable bytes and source meaning, then appends the request to
the EXISTING index using expected-head compare-and-swap. External/domain agents
must not write that shared index. A file in an arbitrary folder is not a trigger;
the marked PR comment is the existing submission signal. Do not make duplicate
comments on retry: first check for the request ID, receipt and existing intake.
If automation is disabled or has not run, the submission remains pending. No
continuous watcher or delivery/acceptance guarantee is implied.

7. B00's independent source review determines accepted/rework/blocked/superseded
   and records a per-item receipt. Intake acceptance is not feature acceptance,
   main integration, deployment or permission to merge.

## Handoff for this bounded helper increment

O1: Provide one executable provider-neutral builder for the existing QC request
contract, with real committed-byte hashing and deterministic request identity.
Primary artifact: qc_submit.py. Existing consumer: qc_intake.py, unchanged.

O2: Preserve ownership and asynchronous truth. Create only a new owner-local
request; do not write QC_QUEUE, archives, credentials, transports, provider
configuration or source code outside this lane. The existing source PR marker
routes to B00/#136. Submission and independent acceptance remain separate.

O3: Verify replay, stale/missing sources, unsafe/unowned paths, symlinks, duplicate
and omitted IDs, dirty worktrees and actual CLI output. Run
`python -m unittest discover -s orchestration/conversation_closeout/versions -p 'test_*.py' -v`
at the published source revision. Existing shared CI does not discover this
versions suite; report its independent local execution separately. Verify the
actual PR head and named tests before reporting CI evidence. Existing #178
scope and prior queue/archive history remain intact.

K1: A local commit/hash and a schema-valid request only establish reproducible
input bytes and structure. The reviewer must independently retrieve GitHub
evidence and recover obligations from source anchors. Matching submitted and
handoff IDs does not establish semantic completeness, user authorization,
provider runtime operation or reduced build time. The helper cannot detect an
obligation omitted from both handoff and supplied IDs.

Source anchors: [scoped continuation](https://github.com/whiterosecoffee/_BASKET/pull/179#issuecomment-6782059108),
[existing consumer and automation receipt](https://github.com/whiterosecoffee/_BASKET/pull/179#issuecomment-6768491075),
and [agent-neutral boundaries](https://github.com/whiterosecoffee/_BASKET/pull/79).
Missing evidence: no external Codex or Claude session was launched, no real
external-agent consumer test occurred, no multiwriter/crash-recovery claim, and
no exact-head shared CI or independent review is inferred from local tests.

Next action: the existing B00 QC worker reviews the pinned helper request,
records its bounded verdict and routes any production integration work through
the existing #136, #78 and B01 owners. Do not create a replacement queue.
