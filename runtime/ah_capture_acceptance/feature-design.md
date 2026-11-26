# Historical AH capture acceptance

Problem: analysis was retained locally but incorrectly treated path arbitration as
the only remaining blocker. R1 was subsequently decided; FETCH host/file ownership
and canonical adoption remain unverified. This node is a metadata handoff, not code.

Input: existing private archive containing named-field Nov5 journals, complete AH
CSV responses, and the Nov6 import receipt. Output: exact hashes, counts, lineage and
source-match results, plus explicit adoption state. Source rows stay private.

Method: reuse existing observation identity serialization (sorted compact JSON;
SHA256 excluding record_id), inspect each exchange-local session date, require
unique record IDs and linear supersedes, and match all AH OHLCV/VWAP/transaction
fields to retained CSV. Repeat import was exercised Nov6; do not imply a fresh
workstation replay. Deterministic read-only verification needs no new pipeline.

Consumer calculation: for each half-open 15-minute window, high=max(minute highs),
volume=sum(provider minute volumes), final value=last emitted minute close. This
is aggregate-qualified evidence, not tick-level extrema or aggressor flow. Missing
SMH minutes are absent aggregates, not zero-volume fabricated candles.

R1: https://github.com/whiterosecoffee/_BASKET/issues/207#issuecomment-6700016254
FETCH ownership: https://github.com/whiterosecoffee/_BASKET/issues/207#issuecomment-6835830005
Archive requirement: https://github.com/whiterosecoffee/_BASKET/issues/207#issuecomment-6930649927

R1 daily partitions and the later NVDA.jsonl archive request require an explicit
owner mapping; neither staging export establishes canonical authority. The receiver
must locate its actual archive, preserve prior records, reject incompatible basis,
apply only missing or superseding observations, and prove repeat/restart/readback.
Reuse #207 QC and #183 contract. Do not rewrite shared schema or runtime here.

Prior art: append-only event sourcing retains corrections; content-addressed
artifacts bind evidence to exact bytes; idempotent ingestion makes retry safe.
These mechanisms do not prove source truth, entitlement, completeness or live operation.

Receiver: read #199 and this state, obtain the private package through the existing
operator context, verify evidence.json hashes, resolve actual NVDA/SMH archive and
daily partition identities, then return accepted/rejected/deferred disposition with
host/path, pre/post hashes, added/revised/unchanged counts and consumer mapping.
Do not claim completion from this publication or create a competing owner.
