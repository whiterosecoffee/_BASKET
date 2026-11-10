# Codex handoff — B00 #59 / PR #60
## Destination and authority
- Repository: https://github.com/whiterosecoffee/_BASKET
- Current project queue: https://github.com/whiterosecoffee/_BASKET/issues/136 (Q07).
- Source issue: https://github.com/whiterosecoffee/_BASKET/issues/59
- Source PR: https://github.com/whiterosecoffee/_BASKET/pull/60
- Source branch: `work/59-orchestrator-retirement-intake`.
- This conversation's only write scope: `orchestration/retirement_intake/**`.
- User selected reduced drift/unfinished work, bounded review then retirement, and an explicit receiver disposition for every deliverable.
- Current checked main: `25ae331f2774250528fc939e3e7795583f8808a3`. Refresh at receipt.

## Resource map
All paths below are under `orchestration/retirement_intake/` on PR60.
| Resource | Purpose | Truth/acceptance limit |
|---|---|---|
| `2026-10-18-*.json` (five records) | Preserve worker retirements, source SHAs, failures, ownership and dependencies | Historical claims; later corrections supersede status, never erase failures |
| `2026-10-29-startup-evidence.json` | Source-pinned main/issue/PR/branch/file/CI evidence | Historical input, not current discovery |
| `2026-10-29-capability-inventory.json` | Generated 32-entry discovery index | Not a current registry or runtime inventory |
| `2026-10-29-startup-report.md` | Findings, reuse map and historical next action | Current #136 priorities supersede old queue recommendations |
| `inventory.py`, `test_inventory.py` | Deterministic read-only index, fingerprints, invalidations, exact-path collisions, cache checks | Supplied evidence required; does not fetch/schedule/claim/merge; exact paths do not prove semantic ownership isolation |
| `WORKER_CONTRACT.md` | Scope, interfaces, lifecycle mapping, runbook, failure register | Reuse existing task/resolution/evidence contracts |
| This file | Self-contained retirement and acceptance route | Sender complete; recipient disposition and integration remain separate |

No new manager, scheduler, canonical ticker store or public data migration was created.
Missing cache records trigger discovery, never an assumption that a capability does not exist.

## Reproducible verification
Implementation source pinned to `505591723ce42e474a8b5f498849bbe6eab10edb`.
The final documentation commit preserves these implementation bytes.

```sh
python -m unittest discover -s orchestration/retirement_intake -p 'test_*.py' -v
python orchestration/retirement_intake/inventory.py --evidence orchestration/retirement_intake/2026-10-29-startup-evidence.json --query CRWV
```

- Eight inventory tests re-executed from fetched exact-source files during this final handoff: PASS.
- Earlier same-source local baseline: 57 orchestration + 29 integration tests, six validators and strict stores PASS.
- Original local dependency/import failure and corrective installation remain recorded; baseline counts are historical, not a fresh current-main test claim.
- Exact-source shared CI: https://github.com/whiterosecoffee/_BASKET/actions/runs/40924034800 — SUCCESS, independently fetched during final handoff.
- Shared CI did not execute the new inventory suite. Separate B01 acceptance request exists in #65; no duplicate QA worker.
- PR60 remains unmerged. No operational/deployment/live-data acceptance claimed.

## Codex disposition required
Record **accepted**, **scheduled** (named owner + acceptance gate), **rejected** (reason), or **superseded** (replacement link) for:
1. Historical retirement/failure evidence.
2. Discovery utility/tests/runbook: retain useful behavior through existing discovery/progress components, or explicitly supersede after comparison.
3. Dated snapshot/report: preserve as historical evidence; invalidate current-use claims.
4. PR60/#59: independently validate any retained code, then explicitly decide integration or documented supersession/closure.
Do not delete unique work to reduce PR count. Preserve branch and failure history. No new architecture or queue project.

Receipt request already posted:
https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6620909934

## Preserve the selected execution priority
Existing #136 Q04 / #148 owns the usable NVDA report plus identical same-manifest replay.
Full locked acceptance:
https://github.com/whiterosecoffee/_BASKET/issues/136#issuecomment-6620788324

Reuse merged NVDA adapter #139/PR140; proposed #146/PR147 is a scope scaffold, not a data cutover.
Keep newly retrieved 4,690 bars distinct from the unavailable original capture; no original/new byte-equality claim.
One logical write target, retained source reports, hash-preserving staged copy, point-in-time replay, idempotency, interruption/rollback negatives and independent exact-head acceptance precede scaling.
No broad 291-symbol migration, private raw data publication, dual writes or fabricated live-feed claim.
Keep B02 ingestion, B03 events, B05 edges, B06 analytics, B01 acceptance and B08 hosting distinct.
This handoff must not displace that selected pilot.

## Ready-to-paste receiver prompt
Continue existing _BASKET #136 Q07 using #59/PR60 and this HANDOFF.md; refresh current main, source heads and ownership. Record a disposition for each of the four deliverable groups above. Reuse useful discovery/fingerprint tests through existing components, preserve historical evidence and explicitly invalidate dated status. Independently verify retained code through B01 #65; distinguish local tests, shared CI, domain acceptance, integration and operation. Decide PR60/#59 integration or documented supersession without losing unique work. Keep the existing #136 Q04/#148 usable NVDA report/replay pilot moving under its locked acceptance. Do not open a competing queue, orchestrator or worker. Follow current delegated authority; this handoff itself does not authorize a merge or release. Return a linked disposition record and update the source issue; do not require this conversation to reopen.

## Retirement state
All sender resources and continuation instructions are persisted in this branch.
Conversation may be archived by the user's present instruction; that does not mark PR60 integrated or recipient acceptance passed.
Codex owns the pending disposition record and verification/closure decision.

## Full-protocol review supplement
[CONVERSATION_REVIEW.md](CONVERSATION_REVIEW.md) applies the complete draft handoff
prompt from closeout workstream #169 at06a7f0a1b197400f48b0317529c4184d48efe142.
It preserves eight mechanism-level knowledge units, the obligation ledger,
objective evolution, alternatives/counterexamples, a35/50 judgment score and
three corrective patterns. It is not CLI-generated semantic extraction.

Actual receiving dispositions now exist: [#59 comment6622146549](https://github.com/whiterosecoffee/_BASKET/issues/59#issuecomment-6622146549)
and [PR171 continuity record](https://github.com/whiterosecoffee/_BASKET/blob/76aaf2f9e4ac9ef433734feaeef232501591d4a7/orchestration/worker_bridge/CONVERSATION_CONTINUITY.md).
History RETAIN; utility SCHEDULED under#65; snapshot RETAIN HISTORICAL;
implementation integration/retirement OPEN. This supersedes the earlier
posted/requested-only receipt state, not the pending independent acceptance.
Review the utility against integrated discovery/progress before choosing reuse
or explicit supersession. Source-conversation transfer does not authorize issue
closure or PR merge.
