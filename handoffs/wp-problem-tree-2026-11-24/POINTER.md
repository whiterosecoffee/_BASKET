# Pointer: wp-problem-tree handoff

Written: 2026-11-25. Refreshed: 2026-11-26 (pin updated; earlier pin `9fcb09c` is in git history).
Status: **pointer only. Not a QC submission, not accepted by any receiver, not integrated.**

Key principle (owner, 2026-11-26): "Patterns is the destination. Anything older gets a pointer to the new work." This file is such a pointer.

The handoff is for the wp-problem-tree (v0.4/v0.5) project, which is a different project from the basket work. Per the owner's statement of 2026-11-25, `_PATTERNS` is the receiver of record. The handoff text is not kept here.

| Item | Location |
|---|---|
| Handoff | `whiterosecoffee/_PATTERNS` (private), branch `handoff/wp-problem-tree-2026-11-24`, path `_HANDOFF_RECEIPTS/wp-problem-tree-2026-11-24/HANDOFF.md`, commit `d548af5a0ab9b741bfac3f8c6c152f0aea4d5767` as of 2026-11-26 (principle added) (follow the branch head; the pin records the state when this pointer was written). The handoff points back here under "Related locations" |
| Draft PR for it | `whiterosecoffee/_PATTERNS#39`. Its `validate` check is red, and it is also red on `_PATTERNS` `main`, so it is not caused by the file |
| Source of truth | `whiterosecoffee/wp-prompt-builder` `main` at `d0e81c71412a80ac12c0a4f9ab465cc7a58a35f7` or later, `reviews/conversation-recovery-2026-11-04.md` (section 9 is the 2026-11-24 delta) |

Superseded: an earlier full copy of the handoff sat in this branch at commit `9e2847a5cb0b72cad6b6635a6ae7a0b57e1f28d5`, path `handoffs/wp-problem-tree-2026-11-24/HANDOFF.md`. It stays in git history.

Placement: `handoffs/` is not in any spark's write paths. The path was chosen by the sender. B00 decides whether this pointer belongs here, or whether to close the draft PR.

Keeping current: the `_PATTERNS` handoff is authoritative. When it changes, update the pin above in the same session; when this pointer changes, update the "Related locations" section of the handoff. There is no automation; a sync check is a deferred idea (trigger: a pointer is found stale). Nothing outside `handoffs/` was changed by this branch.
