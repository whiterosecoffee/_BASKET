# Handoff: wp-problem-tree (v0.4/v0.5) problem-tree project

Written: 2026-11-24
Status: **generated and pushed to a branch. Not submitted to any QC queue, not accepted by any receiver, not integrated, no PR merged.**
Source of truth: `whiterosecoffee/wp-prompt-builder` (GitHub name `wp-problem-tree` after the owner's rename), `main` at `7e8d21bb2f4d170b59f2e951d76182d1ed3098b1` (PR #40), file `reviews/conversation-recovery-2026-11-04.md`. That file holds the full inventory, evidence and loss audit; this handoff is its transferable core. A receiver must not need the source conversation.
Placement: this file sits at a path chosen by the sender. Neither repository assigned it an owner. The receiver's controller decides its real home.

## Receiver and authority
Any assistant or human the owner designates. Authority: the owner's current instructions only. This handoff grants no write access to wp-prompt-builder, Prompts (v0.3) or any other repository.

## Objective
Pre-solve root problems independently so any unique convergence of them can be solved by combining their solutions. Recognise the shape, assemble what is pre-solved, treat only the residual as new work.
Lineage the owner stated: v0.3 = repo `Prompts` (rename to `prompts-v0.3` pending), v0.4 = wp-prompt-builder, v0.5 = wp-problem-tree ("least developed, best thesis"). v0.4 and v0.5 sit parallel to v0.3. v0.4 must not be visible to v0.3 or earlier; v0.4 may read v0.3 as prior art, one way.

## Owner rules
- Act in auto mode; no blocking questions; raise one question, the one the rest depends on.
- State cost (ANSWER, WRITE, COMPUTE, FETCH plus an estimate) before work; COMPUTE and FETCH need a yes; stop over 25k tokens.
- No new structure the turn a definition arrives; challenge the owner's definitions rather than adopt them.
- Prior art is a load-bearing external foundation: never renamed, never mixed with what is derived.
- Nothing is "solved" until accepted upstream and attested within scope. Parts inherit their combination's score; a rejection is logged only when a superior combination supersedes a variant.
- Write nodes through IntakeNode (delta_runtime.py) where it exists, never directly.
- No model identifiers in commits or pull requests.

## Obligations (state as of 2026-11-24)
O1: Run the problem-tree prompt (`pairs/2026-09-29T0140Z/prompt.md`) on one real intent. State: proposed, awaiting an intent from the owner. Evidence: only the author has run it.
O2: Find existing conversations covering the same ground and converge them. State: partly done. 35 `Prompts` sessions and its `SPARK.md` admission boundary identified; only a skim.
O3: Define the v0.4/v0.5 boundary: two repositories split at a chosen commit, or one repository with a folder per version; may v0.5 read v0.4? State: recorded as a ghost in `ideas/constraints/version-lineage.md`; owner decision.
O3a: Rename `Prompts` to `prompts-v0.3`. State: blocked; owner action in repository settings.
O4: Confirm wp-prompt-builder is not visible to v0.3 or earlier sessions. State: recorded as a constraint; visibility never checked.
O5: Store diffs as variants in separate folders: `variants/<source>/<timestamp>/<path>`. State: proposed, unbuilt; depends on O3.
O6: Find the two OneDrive names (METHOD, PROMPT) that block syncing. State: searched all branches of three repos and Google Drive, none found; owner to paste a code-point dump from the folder.
O7: Run the transcript-harvest prompt (`reviews/transcript-harvest-prompt-2026-10-01.md`) locally. State: written, never run.
O8: Export of the conversation. State: offered, no owner yes.
O9: Relation of `_BASKET` to the lineage. State: unknown.
O10: Question Q20 (are objective, constraint, guardrail, perspective, principle, assumption separate types or roles?) then Q17-19, Q21-25. State: blocked on the owner.
O11: Locate the other session that organises records as JSONL, one line per what, why and how. State: unlocated.
O12: Verify 11 unverified prior-art solutions. State: deferred; trigger: O1 needs them.

## Knowledge
K1: Variants as separate paths. A collision needs two writers on one path, so give each source a path prefix and timestamp. A diff is the difference between two variant folders; convergence is a new variant with a `supersedes` edge; unresolved = a path with two or more variants and none superseding. Corroborated by the `Prompts` branch-isolation plan. Untested. Falsifier: a reader cannot tell which variant is current without a supersede index.
K2: Four-part constraint statement: what must be attested (checkably), where a solution lives, why it is unmet, what would clear it; then contingent or structural. Default suspicion: "structural" claims are usually contingent.
K3: Problem graph. Observed problems converge on shared factors; leverage = number of problems a factor feeds. Acceptance is scored at the combination. Attestation form: "Within [bounds], I attest that [aspect] is solved as well as we have been able to define it, as accepted upstream by [solution]." The matcher scored F1 0.44-0.48 against the author's own labels. Zero attestations exist.
K4: Lossless reduction by hash manifest: store minimal facts, derive lists, verify by sha256 over canonical sorted JSON. 742 of 756 objects rebuilt; 14 had stale lists. Rejected by the owner as a deliverable; kept on branch `lossless`. Do not revive.
K5: Transcript harvest design: read-only sources, container outside synced folders, per-run timestamp folder, hash dedupe, one manifest line per file, unreachable sources stated in four parts. Untested.
K6: One-way visibility: the newer version reads the older as prior art, never the reverse; the access boundary is set before content crosses.
K7: OneDrive illegal-name causes: leading or trailing space or period, reserved characters, invisible characters (U+00A0, U+200B), reserved device names, over-long paths. Diagnose with a code-point dump; rename with the `\\?\` prefix. From memory, untested on the owner's machine.
K8: Transcript locations: Claude Code writes `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`; cloud sessions lose theirs with the container; claude.ai chat exports as one `conversations.json`.
K9: Prior-art lens set: 12 families, 59 solutions (48 verified, 11 unverified) in `map/`.

## Decisions, rejected work, failures
- Rejected by the owner: the `lossless` reduction (closed PR #36).
- Failures to avoid: structure built the same turn a definition arrived; bulk copies written without a cost line; a prompt left in a git-ignored path and lost when the container reset; owner turns after T124 not captured as moments in `map/moment`.
- Assumptions and limits: the review rests on the compaction summary for turns before 2026-09-30; the desktop-app folder names and transcript field names are from memory; repository visibility is unchecked.

## Independent work now, and blockers
- Independent: read `Prompts` `MASTER-*.json` and `seeds/` (read-only); read the "Consolidate transcripts and prompts into _Archive-Chunks" session output; if an intent is supplied, O1.
- Blocked on the owner: O3, O3a, O4, O10.

## Next action and closeout
Next action: put the v0.4/v0.5 boundary question to the owner, then record the answer in `ideas/constraints/version-lineage.md` in wp-prompt-builder.
Close this handoff when O3 and Q20 are answered and O1 has a non-author run, or when the owner states it is no longer wanted.
