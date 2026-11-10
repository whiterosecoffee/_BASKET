# B00 Agentic Project Manager: evidence-gated control plane

This module is a deterministic and testable **orchestration library**, not yet a hosted autonomous service. It stays in the B00-owned orchestration/agentic directory; it does not alter the planner, queue or execution-loop files reserved by active B00 PR #25.

It validates a dependency DAG and complete, fresh GitHub PR/issue/CI evidence; classifies work into automatic_safe, requires_evidence and requires_owner; detects write-path collisions across **all open PRs**; reconstructs immutable attempt/lease/deliverable events; checks exact-head CI and independently reviewed acceptance; and outputs an ordered decision record with a source hash. It refuses automatic GitHub merges, releases and dormant worker creation.

## Commands

From repository root, with the GitHub token stored only as an environment secret:

    GITHUB_TOKEN=... python -m orchestration.agentic.cli --queue orchestration/planner/queue.json --live-github --events /persistent/worker-events.jsonl --decision-log /persistent/decisions.jsonl

Safe local validation is opt-in using repeated --check planner/goals/scopes/attempts/versions/sparks. Unknown or missing scripts fail, they are not silent passes.

Test from repository root:

    python -m unittest discover -s orchestration/agentic/tests -v

A queue entry does not establish an active worker. A draft PR does not prove an active session. An expired lease must be reconciled before opening capacity. New issues/branches are created by actual new worker conversations, not by this scheduler. A merged PR is not independently verified until source-pinned acceptance and CI at the relevant commit have been checked.

## Append-only state

The local event ledger requires schema basket.agentic_event@1, stable event_id, timestamp with timezone, task_id, type and type-specific proof. Deliverables use stable D-* identities, artifact path, source URL and SHA. Supersession and corrections append new events. Acceptance maps A1/A2/... to ordered task acceptance criteria; it requires external source and reviewer on the exact head commit. Single local writer fsync is implemented. **Multiple hosted writers still require transactional durable storage and race-safe leasing from B08.**

Decision records include main SHA, evidence digest, queue version, task IDs, blockers, write collisions, acceptance status, deliverable history, worker activity certainty and next safe/owner action. The recording of a decision does not execute that action.

## Next integrations

B00 queue PR #25 owns registration of additional queue tasks; T-012/T-013/T-014 are already reserved, with proposed B08 deployment task T-015 in handoff issue #34. B01 owns CI and independent integration tests; it must add this new package's tests through a separate B01-owned PR. B08 owns a persistent scheduler, Postgres journal, credentials, restart recovery, remote MCP and authenticated REST, observability and webhook retry. Its deployment can call this module by pinned Git SHA but is not accomplished by committing this code.

No direct cross-domain mutations, no auto merge and no claim that the new code has already spawned workers or been deployed.
