# CRWV daily-history acceptance review

B02 #196 reviews existing #186 / PR122. This directory is an offline acceptance
runner, not an ingestion implementation or a second market-data store.

## Exact evidence and disposition

Source PR122: `827dd1ee9e9239c5761013c05f320b30e795c84c`.
Main reviewed: `b4910122a4c3f6ade747f2e4d59bd2d2e84b3c95`.
B02 accepts the **retained historical bytes and lossless staging operation** at
this source revision. This is qualified integrity acceptance, not acceptance of
canonical cutover, production ingestion, economic volume accuracy, historical
availability or current trading use. Candidate remains in PR122.

- All 20 source research/intraday files checked against exact committed bytes.
- October 19,186 rows: all 22 individual daily hashes/counts match the published
  preparation manifest, exact byte reassembly, zero changed files on replay.
- November 2/3/4: 918/921/819 rows; each file contains exactly its ET date and
  metadata hash/count agrees. Each contains 390 regular-session observations.
- VWAP outside OHLC: October 2,374; November 78/84/27; all 2,563 retained.
- Last October bar START: October30 12:09 ET; END:12:10. November4 START:17:42
  ET; END:17:43. Existing `as_of_last_bar` means coverage end, not row timestamp.
  Audit emits both names explicitly; no observation values were changed.
- October30 and November4 remain partial. Endpoint/count checks do not establish
  absence of qualifying-trade gaps or full exchange-calendar coverage.
- Original October CSV is absent in this checkout. Its recorded hash is retained,
  but this audit does not repeat the producer's real-CSV roundtrip or prove an
  authenticated vendor retrieval. Synthetic CSV checks and source JSONL replay
  are separately executable. Unknown first availability/retrieval stays unknown.
- All six existing research tests and six independent B02 validator tests pass
  locally. Real-source audit output is `evidence.json`. This is B02 review of B10
  evidence, **not B01 independent CI**.

## Reproduction

Use separate clean checkouts. No dependency branch is reused for writes.

```sh
git worktree add /tmp/crwv-source 827dd1ee9e9239c5761013c05f320b30e795c84c
python -m unittest discover -s runtime/crwv_history_acceptance -p 'test_*.py' -v
python -m unittest discover -s /tmp/crwv-source/research/CRWV/market-research-2026-10-29 -p 'test_*.py' -v
python runtime/crwv_history_acceptance/audit.py --source-root /tmp/crwv-source
```

Audit refuses a different source HEAD, modified source bytes, invalid bars,
wrong/mixed session dates, altered hashes/counts/cutoffs/anomaly counts and
changed staged replay. It invokes the existing splitter into an automatically
removed temporary directory, then independently verifies outputs. Report is
stdout only; no canonical writes and no persistent duplicate histories.

## Existing consumer usability

| Main consumer | Observed support | Remaining work |
|---|---|---|
| `engines/traversal/range.py` pure `read_bars` / `traverse` | Explicit November4 input parsed all819 bars; arithmetic runs | Windows count observations, not elapsed minutes or daily sessions; gaps need policy |
| Same module CLI and `sftby_zoom.py` | Hard-coded `DATE.5m.jsonl` discovery | Cannot discover these1m files; B06 must add interval-aware routing without relabeling bars |
| `runtime/ticker_data.py` | NVDA-only journal adapter | Cannot import CRWV positional minute arrays as its journal schema |
| `orchestration/nvda_pilot` | Approved NVDA-only frozen-evidence resolver | #148 must explicitly extend routing; NVDA acceptance is not CRWV acceptance |

Existing CRWV daily history remains unchanged. It is not replaced by minute
rows. No claim of usable point-in-time trading replay: first availability is
unknown. The offline research byte replay is usable now with explicit inputs;
canonical ticker analysis is not integrated.

## Ownership and required next transitions

61 live open PR heads were inspected using their Git diffs against current main.
Only PR122 overlaps CRWV intraday; none overlaps this new audit directory.
PR111 retains daily-history ownership; PR153 retains runtime/fetch docs;
PR15 retains its observation/TTD scope. B10 owns PR122 research scripts.

1. B00/#148/#183 resolve one-date canonical routing and explicit PR122 canonical
   path transfer/update ownership. Preserve existing monthly Git source and its
   hash. No new competing history PR, no destructive original rewrite, no dual
   monthly+daily reader that doubles October. The user requested reuse of PR122;
   a new conversation cannot silently push to its owning conversation's branch.
2. B02 canonical adopter updates PR122 through the authorized owner transition:
   22 daily JSONL+metadata pairs, existing November pairs, a non-JSONL migration
   manifest/index and compatible reader selection. Archive/reference original
   bytes without leaving an active multi-day JSONL reader. Keep exact hashes and
   cutoffs; unknown source times stay null. Revise obsolete canonical README.
3. B06/#108 verifies interval-aware consumer behavior through the approved
   read interface. No fabricated5m files or200-session claims from200minute rows.
4. B01/#6 independently executes this audit and candidate tests on the **final
   adopted exact head**, adds owned domain CI as needed, and verifies failures
   stay visible. Repin this source-audit intentionally after source changes;
   do not simply disable the HEAD or clean-byte checks. Current shared PR122
   run41937645821 is successful, but its inspected jobs do not run these minute
   domain checks. B01 must also test production atomic/revision/restart behavior
   if that behavior is included in adoption; this staging tool does not supply it.
5. Only after gates pass, seek explicit merge authorization. Nothing merged.

The latest #148 partition directive explicitly requires B00 routing/allocation
before a new writer. Therefore this review stops at acceptance evidence and
owner handoff, not unauthorized canonical mutation. #186 remains the existing
acceptance queue item. No new owner execution or receipt is inferred from a
posted GitHub comment.
