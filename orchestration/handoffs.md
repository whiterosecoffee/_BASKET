# Cross-domain handoff protocol

**Active dependencies as of 2026-10-16:** contract/schema #3 → canonical SFTBY graph migration #4 → independent CI verification #5. These are *handoff issues*, not worker issue/branch assignments. Receiving conversations each create their own new issue and branch when launched.

**Trigger:** A spark needs any change outside its `write_paths`, or its proposed change collides with an active issue/PR. It must **not** edit the target.

## Required dependency issue template

```markdown
Title: [HANDOFF BXX→BYY] <concise requested change>
Origin: #<source issue>, spark BXX, branch work/<origin>
Owner: spark BYY
Affected paths (target ownership): <exact paths>
Why needed: <decision/analysis blocked or improved>
Evidence: <dated source URLs, retrieval timestamps and confidence>
Current behavior/contract: <verifiable observation>
Requested behavior/data: <specific payload, schema and interface>
Acceptance criteria: <tests, expected outputs, edge cases>
Urgency/dependency: <blocks | unblocks | optional>
No implicit transfer: owner must explicitly claim this issue.
```

**Ready-to-paste receiver prompt**

```text
Launch _BASKET spark BYY for GitHub handoff issue #<id>. Read AGENTS.md
and orchestration/sparks.json from main. Create a NEW issue for your
new conversation and UNIQUE branch from current main; link this handoff.
Implement only within your owned write paths. Review source evidence,
validate affected contracts, commit tests/results, and open a draft PR.
Report blockers back to source issue. Do not write source spark files.
```

## Example
B11 AAOI discovers evidence that an optical supplier contract is signed. B11 adds evidence under `research/AAOI/**` and opens a handoff to B05 for `tickers/AAOI/relationships.json`, and B03 for `tickers/AAOI/events.json` if the event ledger must change. B11 does **not** edit those cross-domain files. Neither B05 nor B03 is assumed to receive a live chat notification: the handoff remains an issue until the owners pick it up.

## Contract governance
Schema changes or shared architectural changes are B00 mediated. To avoid circular ownership, dependency issues identify primary author, integration owner, review owner and any blocking requirements. PR merges are controlled; branch-per-conversation is never waived.
