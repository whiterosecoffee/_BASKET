# Actual execution journal

All repository work belongs to issue #136 and branch
`work/136-worker-execution-bridge`, forked from main
`afc4ada7bc6d7294071b3610fa77e59b206b6312`.

## Source recovery and verification

```sh
git fetch origin main
git worktree add --detach /workspace/basket-worker-audit origin/main
git worktree add --detach /workspace/basket-controller-ref origin/work/32-mrie-agentic-readiness-audit
git worktree add --detach /workspace/basket-contract-ref origin/work/106-worker-v2-contract-audit
```

GitHub repository tools read #106, #107, run 40927765356, current main, all open
PR changed paths and open issue claims/comments. PR #107 remained at
`eb099d8e2bf37918eaf11a46341289ff09651d9e` with that exact-head run successful.
Initial inventory: 39 open PRs, 78 existing issues, 22 fenced task claims; no overlap
with `orchestration/worker_bridge/**` or the new discovery shim. Later capture
includes the new #136 (79 issues and 23 claims). Captures are historical evidence.

## Native attempt — failed, not a model execution

```sh
PYTHONDONTWRITEBYTECODE=1 python -m orchestration.worker_bridge.cli \
  --controller-root /workspace/basket-controller-ref \
  --lease-comment-id 6539170676 --lease-id LEASE-B00-136-20261031-01 \
  --profile contract_engineer --capability contract_governance --capability implementation \
  --attempt-id ATT-136-engineer-1 \
  --instruction orchestration/worker_bridge/implementation-instruction.txt --execute --write
```

Outer command exited 2; the native `codex exec --ephemeral --json --sandbox
workspace-write ...` process exited 1 before model execution. Its app server could
not initialize runtime state on the read-only filesystem. Exact argv, timestamps,
prompt, stderr, empty native stream and hashes are in the attempt directory.
It used the pre-hardening bridge; do not replay it under the current policy.

## Supported host transport — actual executions

B00 used `prepare(...)` against the fresh connected GitHub source captures and
the pinned controller, then explicitly handed the existing #78 assignment packet
to `collaboration.spawn_agent`:

- `/root/worker136_contract_engineer`: authored only `test_agent_profiles.py` and
  ran `PYTHONDONTWRITEBYTECODE=1 python -m unittest orchestration.worker_bridge.test_agent_profiles -v`:
  ten passed, exit 0. Parent reran it and verified the exact returned file hash.
- `/root/worker136_qa_reviewer`: read-only review and
  `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/tests -p test_worker_bridge.py -v`:
  19 passed initially; four concrete guard defects reported.
- Follow-up `ATT-136-qa-host-2`: same read-only role verified the four fixes and
  reported 24 tests passed. Additional parent hardening added write-profile policy
  and dispatch-HEAD binding, then the full current suite ran successfully.

These are real host worker calls, not a Python mock. They do not prove native CLI
recovery, a production API transport or persistent B08 deployment. Parent-mediated
receipt recording is explicit; exact model version was not exposed by this host.

## Local verification

```sh
# Exact #32 dependency checkout: 60 pass, one fixture identity failure retained.
python -m unittest discover -s orchestration/agentic/tests -p 'test_*.py' -v
# Exact #107 checkout: six negative tests pass.
python -m unittest discover -s orchestration/tests -p 'test_worker_v2_contract.py' -v
# Current implementation checkout: 82 pass, zero skipped.
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
python orchestration/validate_versions.py
python orchestration/validate_sparks.py
```

`scenarios.demonstrate(...)` was called using the fresh source capture and exact
controller. It passed eight deliberately injected negative/recovery cases. Output
is `evidence/negative-scenarios.json`; those fixtures were not posted as live claims.

## User-authorized priority correction

On owning PR #33, both failed-attempt fixture events now explicitly target T-002,
and the assertion verifies that unrelated T-001 has no attempts. Added B00-owned
`orchestration/tests/test_agentic_controller.py` to the existing B01 discovery path.
No controller production code or CI workflow changed. New source commit:
`59a8e0eae91f96d64a1589ebfef03c4a7383662c`. Local commands produced 61 controller
passes and 111 aggregate orchestration passes. Independent PR run `41172651296`
checked out that exact head and confirmed 111 tests; push run `41172647936` used
an older workflow and is not the controller-execution proof.

The bridge pin now references the verified source. Prior failure logs, execution
receipts and source snapshots above remain immutable history. No new model call,
lease grant, merge or deployment occurred for this maintenance update.
