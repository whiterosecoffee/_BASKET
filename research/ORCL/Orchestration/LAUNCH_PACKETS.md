# Launch packets for any computer or AI agent

Status: v0. Issue #82. These render the unclaimed assignments in `assignments/` into text a human pastes into an agent. No agent is started by this file, and no provider credentials belong in any packet.

## Common preamble (identical for every provider)
```text
You are a NEW _BASKET worker for ORCL vector set {SET} ({FOLDER}).
Machine/agent label: {LABEL}.
1. Read AGENTS.md, orchestration/WORKER_PROTOCOL.md and research/ORCL/Orchestration/README.md.
2. Run: python research/ORCL/Orchestration/status.py. Stop on any hard flag.
3. Read the assignment: research/ORCL/Orchestration/assignments/{SET}.assignment.json.
4. Check the issue #{ISSUE} for an open claim. If one exists, stop and report.
5. Create a NEW GitHub issue for this revision and a UNIQUE branch work/<issue-number>-<objective-slug>
   from the base the assignment allows. Post a basket.worker_task@1 comment naming this machine/agent.
6. Edit only inside the exclusive write paths. Append to REVISIONS.md. Do not rewrite earlier entries.
7. Run the relevant tests, commit, push, open a DRAFT PR. Never merge.
8. Post a basket.worker_resolution@1 comment: head SHA, real checks only, blockers, ONE next action.
Do not assert prices, consensus or probabilities without a timestamped source. Missing data is a gap.
```

Fill in:
- Forward Multiple: SET=ORCL-FM, FOLDER=research/ORCL/Forward_Multiple, ISSUE=80
- Range Traversal: SET=ORCL-RT, FOLDER=research/ORCL/Range_Traversal, ISSUE=81

## Provider additions
- ChatGPT: paste the preamble plus the contents of the assignment JSON and the `input_manifest` files. You start the conversation; nothing is auto-created. It cannot push; have it return diffs for you to apply, and say so in the resolution.
- Codex: preamble plus checkout instructions: clone the repo, `git fetch origin`, check out the base, run `status.py` and the tests in the sandbox. Never place API keys in a prompt.
- Claude (Claude Code or a Claude chat with repo access): preamble as written. In a chat without repo access, treat it as ChatGPT.
- VS Code agent: open a local checkout of `whiterosecoffee/_BASKET`, paste the preamble into the agent, and run the terminal commands yourself or approve them. VS Code is an editor, not an autonomous remote runtime.

## Per-computer setup (once)
```text
git clone https://github.com/whiterosecoffee/_BASKET
cd _BASKET
python --version          # 3.9 or newer; status.py uses only the standard library
gh auth status            # or export GITHUB_TOKEN for read access
python research/ORCL/Orchestration/status.py
```
Branches are not on main until the draft PRs merge, so fetch them first: `git fetch origin 'refs/heads/work/*:refs/remotes/origin/work/*'`.

## Claim comment (interim, not a lease)
Post on the vector's issue:
```json
{
  "schema": "basket.worker_task@1",
  "task_id": "ORCL-FM-REV-<n>",
  "spark_id": "B22-proposed",
  "issue": {"number": 80},
  "branch": {"name": "work/<new-issue>-<slug>", "base": "<verified base SHA>"},
  "objective": "<one line>",
  "write_paths": ["research/ORCL/Forward_Multiple/**"],
  "claimed_at": null,
  "state": "claimed"
}
```
Machine or agent label goes in the comment text, not the JSON. Use null for any timestamp you cannot verify.

## Return
A `basket.worker_resolution@1` comment on the revision issue and PR: head SHA, checks that actually ran, changed paths, blockers, handoffs, one next action. A green local run is not integrated main.
