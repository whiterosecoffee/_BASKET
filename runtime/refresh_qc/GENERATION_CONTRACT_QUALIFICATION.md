# Existing generation/read contract qualification

## Exact sources and scope

B02-207 continuation, no ownership transfer or publication. Existing branch remains locally scoped to runtime/refresh_qc. PR242 is qualified at d103a99486589aa4aee24d4fa978532f1b288ac1; _MAP projection remains pinned at 1a9fdb7952676d026e92d001f88f62de67f103e0. Existing TickerStore/observation tests ran from base b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95, not a claim about current GitHub main.

The synthetic qualifier accepts a separately materialized reference bundle only when flow.py, objects.json and capture.schema.json match their recorded SHA256 pins. It executes the exact verified source bytes via compile/exec, never imports cached bytecode, and rechecks reference pins after qualification. All generated captures/artifacts are synthetic and temporary. No original NVDA file, production store or FETCH entrypoint is used. Reference code is not copied into this branch or modified at its owner.

## Executed results

- 7 pinned-reference qualification tests pass: create/read/identical replay; changed capture rejection with original bytes retained; old receipt rejected by changed reader identity; wrong source pin; synthetic/as-of admission; high-precision volume-loss detection; cached-bytecode substitution rejection.
- 33 local receiving tests pass separately: 21 ledger-binding and 12 exact-volume checks.
- 34 existing runtime tests pass: ObservationTests (6) and StoreTests (28). Named useful evidence includes revision_replay_and_deterministic_checkpoint, revision_asof_and_retry, stale_head_conflicts, changed_without_expected_head_conflicts, batch_invalid_member_is_atomic, interrupted_replace_preserves_previous_file, retract_preserves_history, hash_tampering_detected and lock_fails_closed.

These are local synthetic tests, not hosted CI, integration into main, real capture authenticity or crash/power-loss durability evidence. The 7-test suite passes because expected unsupported transitions are rejected. It does NOT mean durable generation functionality passes.

## Reuse and exact gaps

1. **Reuse existing observation revision semantics.** TickerStore already implements expected_head + supersedes, atomic batch validation, locking, replay and as-of availability/ingestion cutoffs. Preserve these contracts rather than inventing a parallel revision engine. It is NVDA-only, uses a bounded observations.jsonl journal and rewrites that file atomically. It does not provide R1 physical session partitions, immutable capture/schema/code generations or supported-reader dispatch. Existing owner files remain untouched.
2. **PR242 supports one immutable capture artifact only.** Changed capture for the same target is rejected. There is no generation ID/parent/head-pointer contract, generation selection or historical-reader registry. Copying its artifact naming convention would violate the existing R1 path decision. B02 must specify capture-generation metadata separate from R1 one-session record files; B00 must approve any shared schema/routing additions before changing those paths.
3. **Exact decimal boundary is unresolved.** PR242 strict_load uses standard json.loads and sanitize accepts int/float. Synthetic volume 1.250000000000000000000000000001 becomes 1.25. The B02 receiving guard rejects this candidate. Ordinary representable fractions in the original probe do not prove exact decimal preservation for arbitrary provider input. The minimal owner correction is decimal-preserving parse/serialization or explicit rejection of unsupported precision, with a versioned numeric contract. Do not claim numeric strings, Decimal or new decimal-string schema are accepted by PR242 today; our comparison guard's encoding flexibility is not a producer schema change.
4. **Reader identity is not reader selection.** Hashing current flow.py makes old artifacts unreadable after code changes. Required next contract: retained immutable schema/transform/verifier bundle and allowlisted reader-version selection pinned to that bundle. Unknown versions fail closed; never execute arbitrary artifact-supplied code. A registry/migration mechanism is absent, so no safe production adapter can guess one.
5. **Availability policies conflict.** _MAP first externally available revision and PR242 conservative local captured_at cannot share a field without a policy decision. TickerStore read uses both availability and ingestion. Choose policy explicitly for each consumer; unknown historical publication remains unknown, and current capture time cannot backfill historical PIT claims.
6. **Durability acceptance remains outstanding.** The reference is single-writer transient packaging. Existing TickerStore protects its journal but does not establish an atomic transaction spanning raw capture, R1 partition, bundle, generation metadata and index. Exact expected-head, lock/CAS scope, crash recovery and filesystem fsync guarantees must be specified and tested in the existing writer's authorized scope.

## Smallest next owner actions

- B00/PR242 owner: address the reproduced precision-loss boundary in its existing reference. Do not change B02 or legacy FETCH files. Carry the failing exact-number example into its own tests, then provide a new pinned revision for this qualification.
- B02/#207: draft the minimum immutable-generation/read interface by extending existing TickerStore revision semantics and R1 layout, not cloning a store. Required decisions: generation key/parent, exact retained bundle members, supported-reader allowlist, source vs local availability policy, atomic publication boundary and failure receipt. Keep this a proposal until shared schema/routing scope is approved.
- After those contracts and nested seed qualification are ready, exercise one synthetic revised generation with old/new consumer reads and crash/stale-head negatives. Real-data activation still requires qualified source metadata and explicit durable-root/cutover authority.

No new public comment, source repair, canonical activation, merge, schedule or publication occurred. Parent receives the actionable findings; prior publication denials remain intact.
