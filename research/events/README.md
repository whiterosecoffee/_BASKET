# B03 issuer-event evidence and revision policy

Canonical records remain compatible with `schemas/events.v1.json` and are projections, not the revision store. Versioned immutable event revisions live under `research/events/<ticker>/`; corrections MUST create new files rather than overwrite earlier revisions. `supersedes` must refer to a prior revision. Event IDs stable per economic occurrence; repeated filing/announcement/revision is NOT another independent commitment.

Required before admitting a new record: primary source URL, source classification, exact claim, known effective date, first-public date (date-only if time unknown), independently recorded ingestion time if available, lifecycle classification and accounting group/metric dimension. Never backdate knowledge to effective date. Unknown observation/ingestion times are null rather than fabricated.

Lifecycle: hypothetical, announced, authorized, signed_framework, signed_definitive, funded, operational, completed, terminated. A framework agreement is not booked revenue; funding a previously announced tranche is not a new cumulative commitment. Balances, capacity, backlog, contracts and realized revenue are distinct dimensions; do not sum them together. 

Initial coverage: SFTBY two issuer releases (2026-10-01 OpenAI third tranche, 2026-10-08 exploratory Sarawak framework), other tickers unverified and remain empty/not created. The Oct 1 USD 10 billion belongs within the disclosed USD 30 billion follow-on; not additive to the completed total. Historical source statements are not current NAV.

Dependencies: B00 schema versioning; B05 ownership reconciliation; B02 provenance/TTD snapshot interface; B01 independent CI. MRIE 2026-10-16 backfill not yet located and must not be claimed complete.
