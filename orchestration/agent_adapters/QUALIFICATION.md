# Provider handoff qualification: bounded preparation

Owner: existing B00 #78 / PR79. This record qualifies the existing file boundary,
not an external model, new dispatcher, lease, planning-tool integration or runtime.
No PR179 source or queue was changed during this work.

## D1: one existing plan-to-result mapping

Use the existing request-file feature as the bounded case, without opening a
duplicate issue or branch:

- Plan: [#178 task claim](https://github.com/whiterosecoffee/_BASKET/pull/179#issuecomment-6782138188)
  names objective, five owned paths, dependencies and A1-A4 acceptance. This is
  an explicit mature scope, not proof of automatic promotion from a planning app.
- Existing development destination: issue #178, branch
  `work/178-module-contract-reconciliation`, PR179. Repeated review retains these
  identities; this qualification created none of them.
- Source implementation: `a51a3c53963307c01c6f097e4e55fefb34723b19`.
- Result: [existing worker resolution](https://github.com/whiterosecoffee/_BASKET/pull/179#issuecomment-6782242312)
  uses `basket.worker_resolution@1`, reports actual checks/limits and references
  request head `2136af98e028104cd15fcc1a774712b7d2060c4e`.
- Review artifact: [EXTERNAL_AGENTS.request.json](https://github.com/whiterosecoffee/_BASKET/blob/2136af98e028104cd15fcc1a774712b7d2060c4e/orchestration/conversation_closeout/versions/EXTERNAL_AGENTS.request.json),
  ID `de1836eb14f1a727226825556520667a936aca5cb3ff31bae9bf0cd165d7002d`.
  Its four artifact hashes pin the source implementation, not a floating branch.
- Receiver outcome: [bounded automatic intake acceptance](https://github.com/whiterosecoffee/_BASKET/pull/179#issuecomment-6782317231),
  with immutable receipt at `6c63600dd49b7ce1d117f392a2d28cc1b6bc3366`.
- Subsequent test coverage: helper checkout
  `0c2cb2c9017a6d7c92180530978fecd86c6b4dc6` includes the existing discovery bridge.
  [CI42934211183](https://github.com/whiterosecoffee/_BASKET/actions/runs/42934211183)
  executes all 41 closeout/QC tests within 219 orchestration tests, plus 53
  integration tests. Older source/result evidence remains historical.

The existing result was produced in the current project workflow, not by a
qualified external Codex or Claude Code session. It is a valid mapping specimen,
not the external-result acceptance demonstration requested by #78. There is no
actual external-provider result available in this bounded case. No provenance
field is relabeled to make it appear otherwise.

Current owners remain #178 for the helper/intake, #78 for provider/result and
planning-promotion qualification, #136/#32 for controller/lease decisions, B08
for durable transport and B01 for shared acceptance infrastructure.

## D2: actual source-checkout CLI replay now observed

The earlier record explicitly lacked production Git-object replay. A fresh real
Git clone now made the exact source objects available. In an isolated detached
checkout at `0c2cb2c9017a6d7c92180530978fecd86c6b4dc6`, the production CLI read
artifacts at `a51a3c53963307c01c6f097e4e55fefb34723b19` and replayed the existing
request twice. Both runs exited 0 and returned the SAME request ID with
`status=unchanged`, `submitted=false`, `accepted=false`. An unpinned `HEAD` input
exited 2 with `revision must be a full commit SHA`. Output bytes and clean Git
status were preserved. The existing 41 tests also passed from that checkout.

[Machine-readable observed results](qualification/production-cli-replay.json)
record source/request hashes and both outcomes. This is Python CLI execution,
NOT a model invocation. No new review submission was necessary for an unchanged
request. Shared queue/archive writes remain exclusively with the intake worker.

Reproduce from that detached helper/source checkout; keep TASK_FILE outside the
repository and populate it with the exact `task` object in the committed request:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m orchestration.conversation_closeout.versions.qc_submit \
  --source-repo "$PWD" --task "$TASK_FILE" --source-pr 179 \
  --revision a51a3c53963307c01c6f097e4e55fefb34723b19 \
  --primary orchestration/conversation_closeout/versions/qc_submit.py \
  --primary orchestration/conversation_closeout/versions/test_qc_submit.py \
  --primary orchestration/conversation_closeout/versions/README.md \
  --handoff orchestration/conversation_closeout/versions/EXTERNAL_AGENTS.md \
  --item-id O1 --item-id O2 --item-id O3 --item-id K1 \
  --output orchestration/conversation_closeout/versions/EXTERNAL_AGENTS.request.json
```

Do not substitute the current branch head for the artifact revision. This replay
tests a specific immutable request, not acceptance of later source changes.

## Existing APIs to reuse, not rebuild

Observed main at qualification time was
`74d913e8913d630d85451344689e093aeea07efc`; refresh before any later operation.

- `orchestration.worker_protocol.validate_schema` and `evidence_check` retain
  worker-result schema and independent GitHub evidence checks, including the
  integrated #106 exact-head required-workflow policy. A submitted report is
  still an assertion until checked against fresh evidence.
- `orchestration.agentic.manager.evaluate`, `collisions`, `lease_state` and
  `fingerprint` retain controller policy, ownership and replay identity.
- `orchestration.worker_bridge.prepare` already renders the agent assignment;
  its CLI without `--execute` is the existing preflight/packet path. Do not add
  another eligibility checker or scheduler merely for provider qualification.
- The bridge's observed `controller-lock.json` still pins
  `59a8e0eae91f96d64a1589ebfef03c4a7383662c`. Current-main #106 changes must NOT be
  assumed to be inside that older pin. Any pin refresh belongs to its current
  owner and requires source binding and independent verification. Historical
  lease/event examples are not current execution authority.
- PR179's `qc_submit` and `qc_intake` remain the file builder and review intake.
  Review receipts remain separate from submitted worker resolutions.

## Provider feasibility and unexecuted boundary

The checked cloud executor exposes Codex CLI `0.167.0-alpha.4`; its help advertises
read-only sandbox, ephemeral execution and structured output. These are local
interface observations only. Authentication, current entitlement/quota, endpoint
health and a successful external model call were NOT checked or inferred.
The help command also emitted a read-only-filesystem PATH-alias warning. It does
not establish whether a real session would start. Prior runtime failures remain
historical; no bypass or retry of external execution was attempted here.

Claude Code was not found on this executor's PATH. That is not a claim that it is
unavailable on other computers or accounts. No installation, account, credential,
quota purchase, auth-file inspection or provider configuration was attempted.
Visual Studio/Copilot and VS Code remain distinct, unqualified routes; GitHub
access does not establish their independent budgets or authentication.

One bounded future qualification could ask a specifically authorized Codex or
Claude Code agent to review ONLY the pinned public task/request/code, run the
existing test command, and return `basket.worker_resolution@1` with exact source,
commands, actual exit codes, missing checks and one next action. Use a read-only
source checkout and a caller-owned result location. No source commit, queue
write, network expansion, child delegation or merge belongs to that attempt.
The existing controller must establish the applicable claim/attempt boundary;
no lease or authorization is generated by this document.

Next action: the existing #78/#136 owner verifies a specific user-authorized,
authenticated provider route and current controller bindings, then runs one
bounded read-only attempt and independently reviews its actual result. Until
then external-provider execution is `not_run`, not denied, pending remotely or
successful. Unknown budget/usage remains unknown. Automatic failover and broader
planning synchronization remain deferred.
