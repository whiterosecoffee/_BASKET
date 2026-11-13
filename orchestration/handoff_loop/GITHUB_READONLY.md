# Bounded real GitHub metadata observation

`github_readonly.py` adds one real read-only source integration: existing PR264
metadata and its exact-head Actions run inventory. It neither supplies workstation
ownership/online flags to the evaluator nor creates acceptance receipts. The
synthetic adapter is not relabelled as a real collector.

## Retrieval and normalization

`collect(head=<exact SHA>)` resolves the existing installed `gh` executable and
issues exactly two explicit GETs via `gh api --hostname github.com`:

1. `https://api.github.com/repos/whiterosecoffee/_BASKET/pulls/264`
2. `https://api.github.com/repos/whiterosecoffee/_BASKET/actions/runs?head_sha=<SHA>&per_page=100`

The collector uses existing CLI access, GitHub REST API version 2022-11-28 and the
standard GitHub JSON media type. It does not request credentials, change login,
expand scopes, retry requests, follow supplied URLs, execute received commands,
write GitHub records or start workflows. Each request has a 30-second timeout.
No raw stderr, raw body, credential, personal host path or private routing ID is
returned. Source JSON is retained only in memory; its exact UTF-8 byte SHA256 and
sanitized public metadata are returned.
The raw digest covers CLI stdout JSON bytes, not a wire-level HTTP transcript.

The pure `normalize_supplied(responses, head=..., now=..., seen_observations=())`
accepts two exact response envelopes: source_url, observed_at, raw_json,
raw_sha256. It validates the fixed requested origins, raw digest, strict JSON
parsing, PR number, both repository identities, expected head branch/SHA, resource
URLs, CI run repository/head, statuses and timestamps. No payload may set a trusted
transport label. This API always reports `method: supplied_payload` and
`verified_local_retrieval: false`, even for a byte-for-byte copied real response.
Only `collect` adds its local retrieval label after it has performed both GETs.

Observation timestamps are the local epoch time immediately after each successful
GET. They must be finite, not future and at most max_age seconds old (default 300).
Source created/updated timestamps must include a timezone, parse successfully, be
ordered and not exceed observation time. Old source update dates are not themselves
stale retrieval: an unchanged PR can legitimately have an old updated_at value.
Exact source/subject revision is the pinned Git head; changed heads fail closed.

This reuses the existing strict JSON decoder and canonical digest from the accepted
synthetic adapter/core. It follows the inspected worker evidence and #246 receipt
distinction between metadata, executed tests and acceptance. It does not amend those
owners' schemas or interpret an admission eligibility receipt as execution authority.
Its new versioned output is `basket.handoff_github_observation@0.1-draft`.

## Unknown, unavailable and replay

Unavailable CLI, denied/failed transport, timeout or bad response encoding returns
`availability: unavailable` with a sanitized reason and all authority fields false.
Malformed, mismatched or stale responses raise ValueError before returning evidence;
no partial successful packet is released. No exact-head runs means CI is unknown,
not failed or passed. More runs than the bounded page can supply also means unknown
and incomplete; the collector does not paginate or infer aggregate success.

Duplicate run IDs, duplicate JSON keys or repeated IDs in the supplied replay
inventory reject. The semantic observation ID binds subject, source update times,
PR state and normalized run records. Identical metadata fetched again has the same
ID despite a newer retrieval time. A caller-provided seen ID yields `no-change`;
there is no new acceptance or action authority on either first read or replay.
An existing controller must own durable deduplication; this module owns no ledger.

## Trust and limits

`verified_local_retrieval: true` means this process observed the allowlisted local
CLI GET and validated resource identities/digests. It trusts the installed CLI,
local runtime/configuration, resolver, HTTPS trust and system clock. It does not
independently verify GitHub certificates, sign an attestation, authenticate an
exported JSON packet, or resist a compromised process/CLI. Python callers could
patch code or forge exported output; source-ID checks on supplied data alone do
not establish transport authenticity. Exported evidence remains a worker report
until an independent verifier rechecks the source and implementation.

SHA256 detects byte substitution against the captured digest; it is not a source
signature. The two reads are not an atomic GitHub snapshot. A later head/source
change requires a fresh read and new pin. Retained historical digests identify the
responses read, but raw bodies are deliberately not published, so replaying the
exact historical bytes requires a separately authorized private capture.

`source_claims_verified`, `component_tests_verified`, `reviewer_acceptance`, and
`execution_authorized` always remain false. A shared workflow's reported success
does not prove the Handoff component suite ran. No jobs/logs are fetched in this
increment. `evaluator_observation` is null and `acceptance_receipts` is empty:
GitHub metadata cannot establish current local writer leases or workstation state.

## Evidence and tests

`github-read-evidence.json` contains one actual bounded read from this collector,
its implementation file SHA256, source URLs/IDs, observed/source timestamps,
subject SHA, raw-response digests and sanitized workflow metadata. It is historical
evidence for the specifically recorded head, not evidence about later adapter
commits or operational status. No private source responses are committed.

Run `python -m unittest orchestration.handoff_loop.test_core orchestration.handoff_loop.test_adversarial orchestration.handoff_loop.test_synthetic_adapter orchestration.handoff_loop.test_github_readonly -v`.
Unit-test transport is mocked and labelled as fixture-only in the test module;
those tests do not prove a live read. The actual-read report is separate.

Next bounded step: Dot independently reruns the pure validation attacks and one
allowlisted read at the repaired adapter head, checks returned PR/head/source
metadata and verifies shared-CI versus component-test distinctions. Only then
consider a separately scoped collector for actual local host/ownership/lease
observations. Real acceptance authority and live dispatch remain with their
existing owners and require independent gates; no migration, routing or activation
is performed here.
