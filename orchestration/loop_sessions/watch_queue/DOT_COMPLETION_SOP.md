# DOT completion SOP: maturity pointer plus delta

Owner: B00-235. Adopted for this observer; shared core adoption pending existing protocol/template owners.

1. Update maturity.json in the existing objective's owned folder on its scoped branch. Reuse the owner and branch.
2. Record maturity dimensions, exact evidence, unmet gates, unknowns and one next owner/action. Keep tested, published, independently accepted, integrated and operational states distinct.
3. Commit meaningful changes with their reason. Git history traces progression, corrections and regressions; do not embed an unbounded receipt log or private conversation history.
4. Validate and read back the committed object. Its containing commit binds its revision; avoid a self-referential commit SHA inside the object.
5. Return DOT a commit-pinned maturity.json link plus one short delta sentence. The branch URL locates latest state; the completion pointer identifies immutable evidence.
6. DOT reads that revision, compares with the last processed commit, verifies the evidence needed for its decision and advances the next existing owner/action. Delivery, acknowledgement and acceptance remain distinct.

Example completion:
[maturity.json](https://github.com/OWNER/REPO/blob/COMMIT/OWNED_PATH/maturity.json)
Delta: Placement reported complete; existing consumer owner still owes resolver readback.

## Exceptions
- No material change: reuse the verified pointer and an internal no-change delta. No heartbeat-only commit or repeated user alert.
- Failed/denied publication: retain the last verified pointer; report the unpublished delta and exact blocker. No false update claim.
- Uncertain write: inspect state before retry; reconcile newer authority against the exact operation.
- Duplicate completion of the same commit: no duplicate action. A changed commit is evidence, not permission to repeat an effect.
- Read ownership, branch and current blob immediately before writes; use expected-blob checks and preserve conflicting changes.
- Public objects exclude private paths, session identifiers, transcripts, credentials and raw datasets.
- Scoped maturity is an owner assessment, not a second canonical queue, lease proof or automatic operational authority.

## Core adoption
This pointer-first convention supersedes the earlier verbose completion envelope.
Reuse existing worker-resolution evidence semantics; the initial scoped maturity shape is a proposal, not an extension falsely claimed to validate against an existing schema.
Existing B00 protocol owner reconciles WORKER_PROTOCOL.md; #201 governing instructions; #243 templates; #169 closeout tooling; #105 independent validation. Receiver acknowledgement and global installation remain unverified.
Validation gates: exact-pointer readback, no-change reuse, wrong-head rejection, duplicate deduplication, failed publication retaining old pointer, concurrent-update conflict preservation, and unavailable private evidence remaining unknown.
Current validation is documentation and remote readback only; no runtime enforcement or transport tests claimed.
