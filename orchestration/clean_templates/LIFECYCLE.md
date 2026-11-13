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

## Fresh demand versus prior fulfillment

The FETCH-owner review at `b733012` identified a **source-inspected risk under
owner testing**, not an executed FETCH failure: a fulfilled content-addressed
request might suppress a later identical demand after freshness expires.
`lifecycle.stale-demand.example.json` is a reusable synthetic negative for that
risk. Running this template test does not execute or establish a defect in FETCH.

The logical demand identifies what is needed. A new occurrence carries its own
request/idempotency identity and attempt ID. A persisted generation identifies
the retained artifact and may remain unchanged. Prior fulfillment is historical:
new demand requires a generation-matched freshness readback at or after its
request time, no later than evaluation time, and qualification still valid at
evaluation. Old or expired readback rejects even if request content is identical.
A fresh readback may reuse an unchanged generation without inventing a write.
Retries within the same occurrence retain the existing idempotency policy; the
prior-fulfillment record here describes a completed earlier occurrence.

Configured schedule, invoked attempt, completed outcome, independent acceptance
and consumer usability are separate fields and gates. A configured schedule can
be parked without invocation; it cannot claim completed or consumer-usable work.
Independent and consumer acceptance each require their own evidence reference.
These remain supplied declarations requiring authentic evidence from the owners.

A branch in a public repository is a public destination regardless of its name
or scope. A private-data destination requirement rejects `public`; retain data
locally or use an already authorized private destination. The template neither
changes repository visibility nor authorizes publication.

## Coverage and adoption scorecard

Artifact coverage: **8/10** under this explicit local rubric: 3 points for the
structured contrasting examples/contracts, 3 for required negative behavior,
2 for deterministic no-effect replay, and 0/2 for independent acceptance of this
increment (changes required at 8b9c88b; repair awaiting recheck). Historical evidence: 24 lifecycle tests and 68 shared-discovery tests
pass with no skips. This is a bounded checklist score, not code-coverage percent
or proof that all possible failures are tested.

Verified adoption: **0/8 governing-owner integration rows** in this increment's
matrix. References and local tests are present; no new launcher, bootstrap,
policy, scheduler or data-consumer enforcement has been integrated or observed.
Existing components' prior adoption is not being rescored as zero. Next improvement:
have the existing admission/launcher owner qualify one real blocked stale-demand
case and one fresh reuse case against authentic readback, then have the existing
bootstrap/policy owners adopt the reviewed rule. Those are owner actions, not
authorization supplied by this template.


## Independent review repair (F1-F4)

Review of local `8b9c88b` required changes; its passing producer suite did not
establish acceptance. Before repair, five regression tests reproduced three
assertion failures and four errors (including malformed-task subtests).

Malformed nested worker tasks now return structured rejection before semantic
access. Timestamp parsing normalizes lowercase t/z consistently with the shared
format checker, including the explicit evaluation clock.

Acceptance means acceptance of a successful completed result. Failed or parked
outcomes retain their producer failure receipts, but cannot carry accepted
labels. Pending/rejected statuses cannot retain acceptance receipts. Each accepted
receipt is an envelope with `role` (`independent` or `consumer`), `artifact`,
`request_sha256`, `attempt_id`, `persisted_generation_id`, and `producer_artifact`.
Bindings must match the current request and producer result. Acceptance artifacts
must differ from producer evidence and each other by both reference and digest.
This is local declaration consistency, not authenticated reviewer independence,
artifact retrieval, or execution authority; `execution_authorized` remains false.

The repair adds bound-positive, rebinding, role, attempt, generation, artifact
alias, failure-state and deterministic nonmutation checks. See
`lifecycle.validation.json` for executed counts and source/log hashes. Independent
recheck of the repaired revision remains required. Adoption stays 0/8; no owner
integration, FETCH execution, hosted run, publication, merge or deployment occurs.
