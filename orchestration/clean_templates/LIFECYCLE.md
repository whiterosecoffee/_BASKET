# Proposed persistent-session lifecycle template

This is a LOCAL, synthetic design/validation increment on B00-243, based on
`bca24f865f3b988efb0372fc064d94989a884b9b`. It neither retries that commit's denied
publication nor the earlier failed acceptance-status edit. The scope is only
`orchestration/clean_templates/**`. No governing policy, admission component,
launcher, scheduler, _FETCH, _MAP or shared schema is modified.

`lifecycle.method.json` defines the proposed stages, references and adoption
matrix. `lifecycle.examples.json` contains three contrasting synthetic completion
checkpoints: existing _FETCH-owner refresh, read-only market-data consumption,
and non-market clean comparison. All conversation IDs, artifact locators and
observations are fixtures. They do not claim actual sessions, data or receipts.
The embedded B00-243 task describes evaluating the template, not authority to
own _FETCH; hypothetical refresh has no actual effects or planned writes.

`lifecycle.schema.json` is a module-local draft profile, not a canonical worker
contract. `lifecycle.validate` binds the existing component contract's artifact
reference definition, reuses worker-protocol task validation and path guards,
and checks checkpoint consistency. No copies of admission logic, leases, durable
request queues, scheduler or receipt engine are introduced. Existing execution
admission remains the launch-authority owner's separate integration dependency.

```powershell
python -B -m orchestration.clean_templates.lifecycle
python -B -m unittest discover -s orchestration/clean_templates/tests -p test_lifecycle.py -v
python -B -m unittest orchestration.tests.test_clean_template_seed -v
```

The first command prints deterministic validation results and writes no output.
Evaluation time is an explicit fixture input, never silently today's time.
The 2030 times are synthetic clock values, not current data-freshness evidence.

## Meaning and boundaries

These are acknowledged completion/failure/parking checkpoints. An initial request
without acknowledgment is pending, not a valid completed checkpoint. The workflow
must discover/resume an existing open conversation accessible to Nathan and Dot,
check actual executor identity and isolated worktree, and reconcile one active
writer before any work. Missing attachment means park; no cloud substitution or
replacement conversation. Assertions in a fixture cannot prove those observations.

Request identity, idempotency key, deadline, input revision and branch are explicit.
Acknowledgment and outcome receipt references bind to the canonical request hash.
Old acknowledgments cannot validate a changed request. Duplicate wakes reuse the
same key and inspect the existing effect ledger; this linter neither owns a ledger
nor supplies exactly-once execution. Unknown effect state blocks the checkpoint;
the existing writer must inspect actual artifacts/readback before retrying. Failed
and parked checkpoints keep an evidence receipt and route recovery to the owner.

Data consumers read qualified local inputs only. Missing/stale qualification blocks
them. Acquisition, persistence, repair and refresh route to existing _FETCH.
Non-market consumers apply the same lifecycle to local clean artifacts. Qualified
flags, declared hashes and observation receipts here are **not authenticated truth**;
existing collectors must verify bytes, source, freshness and owner at execution.

Schedule configuration is separate from observed execution. Observed completion
is separate from consumer acceptance, which needs its own receipt. All validator
results retain `execution_authorized=false`, even when valid. No merge, deployment,
operational acceptance, policy adoption or Windows-wide pass follows.

Private raw inputs, paths, credentials and conversation content stay local. Public
handoffs may include only sanitized code/test/documentation and evidence summaries,
under independently established publication authority. This linter cannot scan
arbitrary text for secrets and cannot approve publication.

## Adoption disposition

The matrix names the governing owner for each rule; it is a proposal, not a sent
or accepted handoff. #134/PR135 must adopt bootstrap defaults; #201 must reconcile
project instructions; #230 must register relationship/routing pointers; existing
admission and launcher owners must bind authentic observations and atomic leases;
#103/#105 retain receipt contracts and independent acceptance. _FETCH retains its
data lifecycle. Existing controller/scheduler owners retain recurring execution.
Actual integration, enforcing host/ownership, live qualification and scheduling
exceed this lane's scope and are intentionally not implemented.
