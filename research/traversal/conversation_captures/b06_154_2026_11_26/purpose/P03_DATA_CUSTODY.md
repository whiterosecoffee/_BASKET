# P03 — Source-Custody and Local-First Ingestion

**Status:** binding user requirement and owner handoff, enforcement not demonstrated for all Massive fetches. **Owner:** B02 through B00 #148 and #183; B14 NVDA research publication via #136.

## Problem
A retrospective Massive result held only in a transient analytics workspace may produce a correct-looking report with no source-replay evidence. Separately copied data files lead to divergent corrections and unknown effective versus available timestamps.

## Contract
Before every intended Massive retrieval: query the approved ticker identity/venue/path resolver, local dataset/adjustment coverage, corrections, gaps and TTD. Fetch only required qualified observations through existing B02 maintainer. After each fetch: atomically validate and persist into the ONE owner-approved logical source. Each physical JSONL file is one exchange-local session/day; revisions remain append-only or immutable supersedes, preserving source ID/effective/observed/available/ingested time, provider/entitlement, basis, row hashes and coverage. Report actual accepted/duplicate/revised/rejected counts, destination and cold-replay receipt. If not stored, label NOT_PERSISTED and prevent canonical use. No dual-reader migration or backdated availability.

## Historical gap
The #154 Nov4 NVDA/QQQ pilot retrieved 526 adjusted daily aggregates per symbol (through Nov4) but their canonical durable source copy was NOT VERIFIED. Earlier NVDA-only local pilots do not automatically qualify QQQ or broader universe. PR145 UI loads supplied local observation JSON but is not itself an ingestion service.

## Smallest next action
B00 names the accepted daily source root and path resolver under #148/#183; B02 demonstrates repeated fetch idempotency and cold replay with actual hashes; B14 writes only a derived NVDA analytical record referencing source manifest. No new B06 data store.