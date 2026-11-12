# Two-candidate offline comparison

This second consumer uses the existing composition's explicit request and receipt
ports to compare two synthetic clean-seed candidates. It does not rank candidates,
choose a worker, or execute either candidate's declared work.

Scope: existing B00-243 writer and `work/243-clean-template-boundary`, based on
`6f5e39cd8590a6431bec56cd62af086bb28d6326`. New files only in clean_templates.
The earlier failed PR acceptance-status update remains unresolved and is not
retried by this increment. Prior independent acceptance does not cover this delta.

From the repository root:

```powershell
python -B -m orchestration.clean_templates.comparison
python -B -m unittest orchestration.tests.test_clean_template_seed -v
```

The command prints one deterministic JSON report to stdout and writes no output
files. `comparison.report.example.json` is a checked-in synthetic expected result.
The basic-intake request declares no capabilities; review-required lacks its
required review capability and remains blocked. Fixture timestamp and revision
are explicit declarations, not execution timestamps or source authentication.

API: `compose_comparison(candidates, as_of=..., code_sha=...)` invokes the existing
`compose` for each request, then `compare(candidates, receipts)` calls existing
`consume` for both exchanges. Candidates contain `candidate_id` and `request`;
receipt entries contain `candidate_id` and `receipt`. Both lists contain exactly
two entries. IDs are nonblank, unique, case-sensitive labels. Canonically identical
requests are rejected even under different labels. Reports sort by candidate ID;
input order does not influence output. Inputs are not modified.

Receipts must bind to the expected request for the same candidate ID. Swapped
requests or receipts, mismatched candidate sets, duplicate IDs/requests, missing
artifacts and byte tampering reject the whole comparison without partial output.
Receipt schemas, hashes and request binding reuse existing consume validation.
Invalid seeds and missing capabilities retain `invalid` and `blocked` states in
`declared_readiness`; transport `status=ok` is never converted to ready.

**Integrity is not authenticated authority.** The report contains declarations,
not verified computation or permission. A coherently rehashed, schema-valid false
readiness may pass the underlying integrity-only consumer, as documented and
independently demonstrated for the prior composition. This consumer does not add
authentication. It always reports `execution_authorized=false`. A downstream use
requiring truthful computation/source identity needs a separate acceptance boundary.

Predetermined tests cover two candidates, blocked/invalid preservation, swapped
requests and receipts, duplicate identities/requests, missing artifacts, tampering,
stable order/repeat, nonmutation, no archive/network/dispatch/output writes and
shared discovery. New independent acceptance remains required. No merge,
deployment, operational qualification or Windows-wide pass is implied.
