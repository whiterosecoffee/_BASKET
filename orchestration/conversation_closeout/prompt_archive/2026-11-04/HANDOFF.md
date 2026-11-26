# Receiving-owner review packet

Receiver: existing #169/#178 prompt owners, coordinated through #136.
Mode: archive review and reconciliation; this document does not launch a worker.

Repository: https://github.com/whiterosecoffee/_BASKET
Source preservation: issue #184, branch work/184-handoff-prompt-evolution-archive.
Read the actual PR head and manifest before use.

## First action

Review COMPARISON.md and manifest.json, then compare 06-portable-dispatch-candidate.md
and 07-index-decompose-dispatch-amendment.md against pinned current PR179,
PR171 extraction/integration and PR177 recovery sources.

## Required outcomes

R1: account for every identified source and acknowledge irrecoverable history.
R2: retain complete candidate texts, intermediate amendments and lessons.
R3: classify unique requirements as covered, missing, conflicting, deferred or
rejected, preserving a reason and owner.
R4: explicitly decide the execution-vs-dispatch and delivery-mode conflicts before
selecting any controlling successor.
R5: validate genuinely missing behavior with fixed expected cases and a fresh
receiver where available, separately from archive integrity checks.

Source owner paths remain exclusive. This archive grants no permission to edit
another branch, adopt policy, merge, tag, release or start another worker.
Carry existing user authorization accurately; do not invent a fresh approval gate
for already authorized review.

## Existing capabilities to reuse or compare

- #169/PR170: formatter/evidence CLI, not a transcript extractor.
- #178/PR179: v3 cases, preservation and QC intake; actual model/provider operation
  and generalized semantic correctness remain separate gates.
- PR171: extraction and integration contracts.
- PR177: displaced-work recovery and source-anchor loss audit.
- #78/PR79: portable assignment envelope.
- #226/PR227, #232/PR233: worker/reviewer composition and bounded review loops.
- #224/PR225, #230/PR231: existing discovery and planning maps.

## Lessons and score boundaries

COMPARISON.md retains positive/negative lessons and historical assessment targets.
Do not turn a later recovery into erasure of earlier execution failure.
Do not infer benefit from a longer prompt, more workers, repeatable formatting
or successful byte-preservation checks.

## Acceptance and return

Return exact source identities, covered/gap/conflict decisions, actual test
commands/results where executed, stored lesson destinations and one next action
to the existing workstream. Keep produced, persisted, accepted, adopted and
operationally observed distinct.

Retire this review packet when the existing owner records the candidate
dispositions and any validation dependencies. Archive publication itself requires
no new prompt framework or repository policy adoption.
