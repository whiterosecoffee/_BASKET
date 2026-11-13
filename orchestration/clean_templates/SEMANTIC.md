# Local semantic conformance example

This bounded example consumes the existing lifecycle validator and canonical
worker-task/resolution schemas. `semantic.py` defines only a private wrapper
shape for synthetic evidence. It does not establish a shared schema, graph,
status ledger, scheduler, or admission authority.

Run from the repository root:

```powershell
python -B -m orchestration.clean_templates.semantic
python -B -m unittest discover -s orchestration/clean_templates/tests -p test_semantic.py -v
python -B -m unittest orchestration.tests.test_clean_template_seed -v
```

`semantic.examples.json` contains a complete prior packet and four self-contained
candidate snapshots: planned child, duplicate wake, uncertain replay, and retained
correction. All data and artifact references are synthetic. Its fixed evaluation
clock and expected revision describe a fixture, not current time or live Git state.
The CLI prints JSON only; validation reads fixed local schemas and never resolves
artifact references, imports archives, dispatches work, fetches data, or writes.

## Meaning and evidence boundary

- Exactly one active objective binds the existing task's purpose, criterion IDs
  and session owner. Non-goals are explicit. Scope and input revision remain in
  the existing task/lifecycle request rather than a duplicated authority.
- Planned children carry purpose, intended owner and canonical acceptance
  criteria, with null branch and running worker. Their existence creates no
  allocation. Promotion requires the controller's separate canonical worker claim.
- Intake retains source references and original question/idea/commitment records.
  Later corrections append `supersedes` links to retained earlier records.
  Compared with caller-retained prior input, deletion, edits or reordered history
  reject. Questions/ideas cannot select an active objective. An explicitly approved
  appended commitment can reference a question without rewriting that question.
  An approval reference is a declaration, not authenticated permission.
- Replay compares the entire request against the supplied prior request and
  compares both source revisions with the caller's `expected_revision`. Existing
  lifecycle acceptance bindings still reject stale request/attempt/generation/
  producer evidence. Changed requests require owner reconciliation, not auto-retry.
- Duplicate wake IDs or new wake IDs for the same request reuse evidence. Known
  effect records must remain an unchanged prefix; additional supplied observations
  are not effects performed by this function. Invalid packets retain prior effects
  when the prior wrapper is well shaped. The function never edits either input.
- Any uncertainty in either supplied wake returns `reconcile_uncertain_effect`;
  clearing a later flag cannot clear earlier uncertainty. A real reconciliation
  checkpoint and durable journal are the runtime owner's responsibility. The
  lifecycle object remains the last known checkpoint, not evidence that the
  uncertain operation completed. No real uncertain write was performed here.

Every result has `execution_authorized=false` and `new_executions=[]`, including
valid packets. `valid` means local declaration consistency only. No authenticated
host, global sole-owner proof, artifact truth, current private destination, real
HEAD observation, durable idempotency or exactly-once guarantee is provided.
Caller-retained prior input is essential: replacing both snapshots can forge a
consistent story; only an authenticated external journal can prevent that.

The wrapper deliberately permits only canonical task `review` and resolution
`in_progress` with unverified criterion results. Existing lifecycle acceptance
has its own bounded semantics; this wrapper does not turn it into a canonical
integration status. Planned/local/tested/independently accepted/published/
integrated/operational are separate evidence stages, never an automatic ladder.

## Evidence and owner adoption

Producer execution: 20 semantic tests and 99 shared-discovery tests passed without
skips on MELISSA. The shared suite includes existing stale acceptance and public
private-destination negatives; they are reused rather than cloned. Source/log
hashes and exact commands are in `semantic.validation.json`.

The predecessor `0279d14b1aa222299871fc38ba4af4daed8a94e1` was independently
accepted for F1-F4 local consistency only (35 lifecycle / 79 shared tests,
81 mutation and 22 binding probes). This new semantic increment requires its own
independent exact-revision review. No hosted result qualifies this unpublished
increment. Historical Windows WinError 1314 and publication restrictions remain.

`semantic.adoption.json` supplies the compact owner packet: #230 map registration,
#134 Copier, #201 instructions, #103 canonical contract reconciliation, #105
semantic acceptance, and the existing runtime/controller owner through #136.
It references pinned _MAP design relationships without importing or registering
new graph implementation. The parent controller coordinates these owners; this
lane sends no duplicate dispatches. Governing adoption remains **0/8** from the
existing lifecycle matrix. Artifact checklist **8/10** is a producer rubric,
not independent acceptance, measured code coverage, or project-wide enforcement.


## Provider-neutral data example

`semantic.data-example.json` records the architecture correction: `_FETCH` is the
master class; Massive is one source adapter in dependency metadata. Two fictional
ticker components have distinct scoped worker-task branches and accountable
owners. The issue numbers/branches are synthetic examples, not created resources
or ownership claims. Tickers request data through `_FETCH` and read qualified
local data; acquisition, persistence, repair and refresh stay with `_FETCH`.
Generic request/outcome contracts contain no Massive-specific fields. Adapter
capabilities are illustrative metadata, not verified entitlement or execution.
The parent coordinates #230 and governing owners; this example edits no live
_FETCH implementation or adapter and performs no fetch.


### Intended product scope versus verified maturity

_FETCH is the master for **ongoing live source acquisition, standardization,
sanitization and persistence to the requesting component's authorized local
repository store**. Later component use is a separate read-only step against
qualified persisted data. Massive remains one adapter; generic contracts remain
provider-neutral. Offline evidence is not an offline-only product requirement.

The fixture separates `intended_capabilities` from `verified_maturity`. This lane
has tested local synthetic declarations; it has not verified live acquisition or
operation. Each fictional requester retains its accountable owner, scoped branch
and private local destination. _FETCH persistence requires explicit authorization
for that destination; a public source branch is not the private data store.
Provenance and revision/correction lineage must survive the pipeline; unresolved
conflicts are quarantined before qualified consumer use. Explicit current versus
historical temporal policy remains required, without arbitrary expiry of old facts.

The adoption packet asks existing _FETCH/runtime and governing owners, through the
parent, to demonstrate that pipeline. This fixture creates no store, entitlement,
source connection or runtime and grants no execution or publication authority.
