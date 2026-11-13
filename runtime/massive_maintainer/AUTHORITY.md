# FETCH authority and separation contract

Status: scoped design contract plus the existing Massive implementation; not a new
provider-neutral engine, shared schema release, or operational deployment.

## Authority

The generic `_FETCH` master class owns acquisition orchestration: admission,
coalescing, bounded retry, raw persistence, validation, publication and receipts.
Its single source-specific writer lane here is B02 / `fetch.massive`, branch
`work/local-20261112-massive-maintainer`, exclusive scope
`runtime/massive_maintainer/**`. The private controller retains conversation and
workstation routing; personal paths and session routing identifiers do not belong
in this repository. Continue this owner rather than launch a replacement writer.
The machine-readable scope declaration is OWNER.json; it is not an active-process
lease. The runtime WRITER.lock is local and requires separate live verification.

`Massive` is one provider adapter. It owns provider URL/parameter translation,
credential use, transport pacing, raw response capture and response interpretation.
Provider-specific schemas and errors must not become ticker business logic.

Ticker components are clients: declare instrument, date/grain, session, adjustment,
coverage/completion and freshness requirements; request through `_FETCH`; consume
qualified local snapshots through discovery/resolver. They do not fetch from the
vendor, mutate shared histories, issue their own acquisition permits or claim a
missing index proves missing source history. A refresh-required result blocks
current inference while historical returned bars remain separately accessible.

## Implemented boundary and limits

`maintain.run` currently combines orchestration and Massive-specific policy in one
module; `Massive.get` is its concrete transport adapter and `resolve` is local-only.
There is no implemented generic Python `_FETCH` base class in this increment.
This contract establishes the required roles without pretending that an extraction
or multi-provider integration has occurred. Request files and local permits are
module-specific contracts, not newly approved cross-domain schemas.

Flow: component requirement -> local resolver -> demand request -> exclusive owner
-> inventory and explicit admission -> provider adapter -> immutable raw and safe
provenance -> validation/quarantine -> staged daily generation -> manifest -> local
consumer eligibility. Failure yields blocked/deferred/quarantined evidence; it
never grants permission to invent bars or bypass the owner.

Current eligibility requires a declared PRE/RTH/AH interval with every requested
minute observed, complete pagination, OK source status, completed/fresh observations
and fresh retrieval. This conservative implementation cannot qualify intervals
containing asserted no-trade minutes, unknown gaps or calendar closures. It does
not infer those states from absence. Existing-date acquisition remains admission-
blocked pending a separate explicit refresh contract; absence permits cover only
one date in the named local inventory/index scope.

## Shared-owner handoff (not applied)

B00 owns orchestration registries, planner scopes, worker-library and launch templates.
Existing `_MAP`/resolver owners retain shared discovery and migration ownership.
Requested adoption: register this existing source lane and branch; route all ticker
demand to it; keep owner/session/exclusive-path/lease records separate from code
completion, data freshness and scheduler execution evidence. Version the reusable
request and receipt contracts through the normal cross-domain review.

Request fields needed: request ID, component owner, instrument identity, provider,
date/grain/session/adjustment, required interval/completion, freshness, observed
generation and admission/evidence references. Receipt fields needed: request and
attempt IDs, owner/revision, raw/provenance hashes, output generation, qualified or
blocked/deferred/quarantined state, actual tests, independent acceptance and next
permitted action. Retry lineage and failed attempts remain retained.

Acceptance for shared adoption: a ticker discovers a snapshot through `_MAP`,
submits an unmet requirement, the existing writer acknowledges it, and the ticker
reads a qualified local result with network disabled. Verify routing acknowledgments
and runner receipts; a scheduled supervisor or open conversation is not a live
refresh process. No cross-owner registry/template edits or publication are part of
this local commit. Expected-head publication remains the next code gate.
