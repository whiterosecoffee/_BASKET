# B01 handoff: execute the declared _MAP offline suites

Requested receiver: existing B01 acceptance owner (#102), coordinated with B00 #230 / PR231. This is a prepared handoff, not a receiving claim or hosted implementation. B00 has not edited `.github/workflows/**` or shared integration tests.

## Smallest requested gate

On the exact candidate PR head, use the existing supported Python environment with `jsonschema`. Materialize the two explicitly referenced read-only candidate commits needed by the map's pinned source checks (PR227 / `10be98031aa5dbd9b5841cc8f88bab5b834790e2`, PR229 / `c33ecd6f8f790af7e43d58d980ed88d59734bf67`) and the pinned main archive `74d913e8913d630d85451344689e093aeea07efc`. Fail if pins cannot be resolved; do not silently use current candidate branch contents.

Run `python _MAP/run_suites.py`. It first validates the map, then executes each declared bounded runner in `suites.json`, checking actual case IDs and replay output against retained evidence. It does not fetch network resources, write queue records, launch agents or operate production systems. Temporary extraction of pinned repository code occurs only in scratch. Retain stdout as an exact-head artifact.

## Acceptance

- Every declared suite actually executes and returns successful exit status.
- Missing/duplicate fixtures, stale evidence hashes, unknown output cases and invalid nested contracts fail.
- Assert declared suite IDs and actual receipts, not fixed case-count thresholds that prevent adding cases.
- Review the suite manifest and runner changes as executable test code. The manifest does not grant permission to arbitrary commands.
- Shared-green CI alone remains distinct from this dedicated check until the owner installs and verifies it.
- Existing workflow collision, ownership and required-check decisions belong to B01. No direct workflow mutation, required-check change or production integration is authorized by this document.

## Bounded B00 discovery resolution

Instead of changing a B01-owned workflow, the coordinator authorized one new B00-owned discovery test, `orchestration/tests/test_map_suite_discovery.py`, after 68 open PR file lists showed no collision. It uses the existing orchestration unittest step to prepare missing exact source objects and execute the declared suite runner. No B01 acceptance, required-check policy change or workflow ownership transfer is inferred. The old external-comment gate was not retried; the repository scope amendment records this exact extension.

Exact-head hosted proof must show the discovery test passing plus `MAP_HOSTED_DISCOVERY` with the tested SHA and every suite receipt in worker-qc logs. Implementation and local shallow-checkout tests alone are not that proof.
