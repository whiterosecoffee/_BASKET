# Closeout prompt versions

External Codex, Claude Code and other agents can prepare the same small review
request file with [EXTERNAL_AGENTS.md](EXTERNAL_AGENTS.md) and `qc_submit.py`.
This additive local helper feeds the existing intake adapter; it does not submit
or accept work, launch a provider, or replace the Issues queue.

## Repository delivery and automatic QC overlay

Primary work stays in its source owner's repository paths. The complete handoff
is persisted there, and QC_QUEUE.json records pinned references for the existing
Issues queue #136. See [QC_WORKER.md](QC_WORKER.md) for submission, priority,
automatic trigger, review and immutable archive behavior. This replaces manual
prompt copying for authorized repo_queue delivery; no merge/default-policy
promotion is implied. The first real source handoff is [QC_HANDOFF.md](QC_HANDOFF.md).

`qc_intake.py` reuses existing worker-task schemas/ownership helpers. It is a
pure intake/receipt adapter, not a scheduler or domain executor. At the initial ba757db increment, twelve QC tests
plus seven previous tests passed locally. The 2026-11-10 rework has 28 passing
owner-local tests, including paired intact/K5-omitted and prior-review regressions. Independent review found two defects;
failed regression runs and corrections are recorded in VALIDATION.md. Automation
configuration and observed execution remain separate evidence: original review
comment6648499459 shows an automatic run returning rework, not accepted archival.

Subsequent bounded automatic acceptance is recorded separately in
[comment6768491075](https://github.com/whiterosecoffee/_BASKET/pull/179#issuecomment-6768491075)
for the corrected closeout and
[comment6782317231](https://github.com/whiterosecoffee/_BASKET/pull/179#issuecomment-6782317231)
for the external-agent request. Immutable requests and receipts remain pinned
to their original revisions. These observed runs do not establish external
provider operation, continuous monitoring or feature/main integration.

## v3 candidate — 2026-11-04

- File: [HANDOFF_PROMPT.v3-candidate.md](HANDOFF_PROMPT.v3-candidate.md).
- Original complete chat candidate preserved at e949f402b84471dca89ba78f2a442573b0c8db39. The current candidate adds narrowly reviewed compatibility and actionability amendments; see VALIDATION.md. The v2 snapshot remains byte-identical.
- This is the procedure that GENERATES a B00 handoff, not a generated handoff to send to B00.
- Candidate, not adopted policy. Not wired into the CLI or default invocation. No merge or release implied.

## v2 baseline — exact retained source

- File: [HANDOFF_PROMPT.v2-source.md](HANDOFF_PROMPT.v2-source.md).
- Repository source: orchestration/conversation_closeout/HANDOFF_PROMPT.md at 06a7f0a1b197400f48b0317529c4184d48efe142, issue #169 / PR #170.
- Original Git blob SHA: f3e6c4b8a656b27feeed4ea32b86792faa1a7be2.
- Preserved byte-for-byte as returned by the UTF-8 file API. The original file and owner branch are not modified.

## Change rationale and compatibility

Observed failures in this conversation: embedded NEXT treated as assignment; existing branch prompt missed by main-only search; executable work deferred; incidental cleanup blocked closeout; requested orchestrator recipient suppressed; trimming lost requirements and mechanisms; reusable procedure confused with generated artifact.

V3 retains two-track capture, obligation/opportunity distinction, causal knowledge units, evidence/falsifiers, reconciliation, scored attempt and lessons. It makes the B00 handoff a required artifact, completes authorized local work first, distinguishes inherited context from assignment, retains pending questions and side effects, and attaches improvements to scored weaknesses.

Intentional behavioral changes: v2's conditional handoff and four terminal archive dispositions become a mandatory B00 handoff; score dimension wording and decision handling change. V3 is therefore a candidate successor, not a byte-identical replacement or compatible CLI schema revision. Existing worker task/resolution contracts and the supplied-evidence CLI are unchanged.

Lossless means both source versions remain recoverable in full. It does not assert semantic equivalence or validated superiority. V2 includes illustrative taxonomy/ranking/retrieval/CLI guidance not reproduced verbatim in v3; it remains available in the full baseline. No automatic union of conflicting output rules was attempted.

## Verification and next pilot

Initial preservation was documentation-only with no semantic validation. The subsequent user-authorized comparison adds three bounded paired manual cases and seven frozen-output regression tests; see [VALIDATION.md](VALIDATION.md). These do not establish generalized model reliability. Baseline full conversation history is not available here.

Run the new owner-local tests with:
`python -m unittest discover -s orchestration/conversation_closeout/versions -p 'test_*.py' -v`.
No external services are required. Python jsonschema and the existing worker
protocol, task schema and spark catalog are required. The current suite has 41
tests, including the 13 external-agent request-builder tests; Git is required
for the local repository fixtures. It reuses Python unittest and the existing
module's supplied-evidence testing pattern.

`orchestration/tests/test_closeout_versions.py` now imports the three canonical
TestCase classes into the existing mandatory `worker-qc` discovery:
`python -m unittest discover -s orchestration/tests -p 'test_*.py' -v`.
No assertions, CI workflow or integration tests are duplicated or changed.
Imports are unconditional, so a missing module/dependency fails instead of
silently skipping the suite. Verify the current head and actual named tests in
runner logs before claiming CI execution. Historical results predating this
bridge remain local-only evidence for these 41 tests; they are not retroactively
upgraded to CI evidence.

Related: #178 (this preservation work), #169 / PR #170 (existing closeout implementation). Existing main and PR governance remains applicable.
