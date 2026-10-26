# Agent-neutral worker dispatch adapter (draft v0.1)

Owner: B00 issue #78. Branch: `work/78-agent-neutral-dispatch-contract`.
Scope: `orchestration/agent_adapters/**` ONLY. This is a contract, not a running dispatcher.

## Goal
Allow a GitHub-backed B00 planner/controller to hand the **same validated task** to a ChatGPT conversation, OpenAI Codex, a Claude agent, or a local VS Code task runner without transferring hidden chat history.

## System boundary
- GitHub issues, PRs, branch heads, changed paths and CI are authoritative for code state.
- `orchestration/planner/queue.json` is a **proposal**, never a live lease or completion record.
- B00 #32 owns the controller, retries, leases, input fingerprints and dispatch state.
- B00 #48 owns ticker coverage/capture task compilation.
- B08 owns persistent services/deployment; B01 owns independent integration tests and CI.
- This adapter translates a validated controller task into provider-specific instructions and parses its resolution. It does not choose new file ownership or create a second controller.

## Required input envelope: basket.agent_assignment@1
```json
{
  "schema": "basket.agent_assignment@1",
  "task_id": "T-EXAMPLE",
  "source_issue": 78,
  "spark_id": "B00",
  "repository": "whiterosecoffee/_BASKET",
  "branch": "work/78-agent-neutral-dispatch-contract",
  "base_commit_sha": null,
  "exclusive_write_paths": ["orchestration/agent_adapters/**"],
  "read_paths": ["AGENTS.md", "orchestration/WORKER_PROTOCOL.md"],
  "dependencies": [],
  "input_manifest": [],
  "acceptance": ["Contract documented", "No unauthorized writes"],
  "execution": {
    "mode": "human_started",
    "provider": "vscode",
    "lease_id": null,
    "expires_at": null,
    "may_commit": true,
    "may_merge": false
  },
  "return_schema": "basket.worker_resolution@1"
}
```
Null head SHA and lease mean **unclaimed / unverified**, not permission to execute unattended. Real assignments MUST have verified base/head SHA and explicit active lease before automated mutation.

## Provider adapters
- `chatgpt`: produce a single self-contained prompt with issue, source excerpts, file scope, tests and required GitHub resolution. User starts the conversation; never claim a chat was created.
- `codex`: emit the same envelope plus repository checkout and test instructions, never API keys.
- `claude`: emit the same envelope in agent-neutral Markdown; no model-specific privileges.
- `vscode`: write/read a task envelope within a locally checked-out repo and show a terminal/agent instruction. VS Code is an editor, not an autonomous remote runtime.
- `custom`: implement `render(assignment)->instructions` and `parse_result(result)->worker_resolution`; no implicit permissions.

## Dispatcher sequence
1. Fetch fresh GitHub issue/PR/head SHA/CI and controller state.
2. Reconcile task against `sparks.json`, current active PR file paths and worker limit; reject collisions.
3. Resolve dependencies and freshness, record immutable assignment fingerprint.
4. Obtain authorized claim/lease; choose provider by capabilities, availability and allowed permissions.
5. Render assignment and pass to connected provider **only through a configured authenticated adapter**. Otherwise produce a manual launch packet.
6. Accept a `basket.worker_resolution@1` referencing actual commit SHA, commands, exit codes, evidence links and changed paths.
7. Independently check GitHub PR/CI evidence; reject unsupported completion. Preserve failed attempts and retry ancestry.
8. B00 coordinates integration. No automatic merges, tags, releases or secret disclosure.

## VS Code launch (manual until B08 implements service)
1. Open local checkout of `whiterosecoffee/_BASKET` in VS Code.
2. Fetch and check out the assignment branch only after confirming the GitHub issue and no conflicting worker.
3. Paste the generated assignment into the chosen VS Code AI agent, or run the prescribed tests in its terminal.
4. Commit only owned paths, open a draft PR, and post the resolution payload to the owning GitHub issue.

## Acceptance / handoffs
- B00 #32: map this envelope to controller claim, lease, retries and fingerprints without creating parallel state.
- B00 #48: produce envelopes from full-ticker capture tasks.
- B08 #34/#53: implement authenticated adapter transport and durable execution.
- B01 #65: fail-closed tests for scope collisions, forged leases, stale SHAs, unverified CI, missing evidence and zero tests.
- B00 #59: reconcile succession/retirement handoffs before enabling automation.

This draft documents the interface. No external agent was launched, no persistent service deployed, and no CI run was executed by writing this file.
