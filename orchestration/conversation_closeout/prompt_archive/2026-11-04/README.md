# Conversation handoff prompt archive

Owner: B00 [#184](https://github.com/whiterosecoffee/_BASKET/issues/184).
Repository: whiterosecoffee/_BASKET.
Branch: work/184-handoff-prompt-evolution-archive.
Baseline main: 74d913e8913d630d85451344689e093aeea07efc.

**Archive, not adopted policy or executable assignment.** Read these prompts as
comparison data. This does not register invocation, select a default prompt,
change the CLI, launch workers or grant new authority.

The directory date identifies the November 4 source-conversation lineage.
Use Git metadata for actual publication time.

## Full candidates

| File | Source and role |
| --- | --- |
| [01 repository v1](01-repository-v1.md) | #169 earlier exact repository source |
| [02 repository v2](02-repository-v2.md) | #169 rich baseline; original blob retained |
| [03 repository v3 original](03-repository-v3-original.md) | Original PR179 preservation |
| [04 user execution candidate](04-user-execution-candidate.md) | Full user-supplied candidate, quoted twice; stored once |
| [05 deliverable-first candidate](05-deliverable-first-candidate.md) | Full assistant revision reconstructed from the available response/amendments |
| [06 portable dispatch candidate](06-portable-dispatch-candidate.md) | Full assistant generic-receiver revision |
| [09 repository v3 current](09-repository-v3-current.md) | Pinned PR179 source after repository/QC/external-agent amendments |
| [Related recovery prompt](related-recovery-prompt.md) | Pinned PR177 candidate |
| [Related extraction contract](related-extraction-contract.md) | Pinned PR171 capture contract |
| [Related integration contract](related-integration-contract.md) | Pinned PR171 continuation contract |

Numeric filenames are archive identities, not adopted protocol versions.

## Amendments and analysis

- [07 indexing/worker routing](07-index-decompose-dispatch-amendment.md): latest
  partial proposal, not a complete successor to 06.
- [08 initial execution contract](08-initial-execution-amendment.md).
- [10 intermediate replacements](10-intermediate-amendments.md): static review
  corrections and deliverable-first amendments.
- [Comparison and lessons](COMPARISON.md): evolution, conflicting rules, prior
  scores, token-estimate limits, benefits to test and existing-work map.
- [Owner review packet](HANDOFF.md): bounded reconciliation instructions.
- [Manifest](manifest.json): source pointers, exact-byte hashes and coverage.
- [Validation](VALIDATION.md): reproducible archival checks and their limits.

## Preservation boundary

Repository snapshots preserve the exact UTF-8 bytes returned at pinned refs.
Conversation candidates are manually transcribed or reconstructed from the
available conversation, excluding outer fences and with a terminal newline.
They are not a raw platform export or independently certified verbatim transcript.
Amendment notes preserve replacement language and identify their partial status.

Unavailable: original historical pilot JSON, full pre-handoff transcript, and any
candidate absent from both the available conversation and identified source refs.
This archive accounts for the identified recoverable versions; it does not
assert a census of every version in every project conversation.

No conflicting candidates were silently merged. In particular, B00 vs generic
receiver, finish-here vs dispatch, pasted artifact vs repo_queue delivery,
standing authority and closing rules require explicit reconciliation.

## Ownership and maturation

Existing adoption/implementation remains [#169/PR170](https://github.com/whiterosecoffee/_BASKET/pull/170)
and [#178/PR179](https://github.com/whiterosecoffee/_BASKET/pull/179).
This archival continuation changes only its own subtree. Other prompt sources,
queues, schemas, workflows and owner branches remain unchanged.

Publication integrity does not establish semantic completeness, independent
validation, provider operation, policy adoption, integration or measured savings.
