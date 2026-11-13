# Verified archive placement

Owner: existing B02/fetch.massive source lane. This command relocates existing local
archive files into `_TICKERS/<TICKER>/<TICKER>.jsonl`; it does not acquire vendor data,
normalize records or qualify market-history completeness.

Inputs are an explicit completed archive-placement manifest, original source root,
current staging root, target _TICKERS root, existing writer-authority root and private
journal directory. Inspect collisions and Git exclusions before `--execute`. The
plan command is read-only. The execute command uses the existing source writer lock.

Per file, in NVDA/AAOI/CRWV/SFTBY-first order:
1. Verify original and staging SHA-256 and any previously recorded original hash.
2. Create an exclusive partial destination, copy, flush and hash it.
3. Rename without overwriting, hash the final file and append durable verified evidence.
4. Persist placement state; recheck originals/staging, then retire only that exact
   verified staging file. Never delete the original source.
5. Record retirement. At completion publish `_FETCH-placement.json` in the target.

The copy/verify/retire sequence avoids another persistent corpus while keeping an
original recovery source. Unknown destination collisions or partial files stop the
run. A restart can accept only a target bound to this operation's prepared journal
and matching the current original hash. Interrupted partials require inspection;
the implementation never blindly deletes them. Rollback restores the prior staging
path from a hash-matched final or untouched original; preserve the journal first.
No recursive delete or overwrite operation is used.

`resolve_archive(manifest, ticker)` verifies the final checksum and returns
archive_available_not_qualified. It is a placement lookup, not the qualified daily
resolver. Metadata-only lookup can skip byte hashing explicitly after final hash
verification, but must not be represented as a new checksum verification.

Private data and manifests must be excluded from Git using verified narrow rules;
component source files remain visible. Operational manifests, original paths and
raw records are not committed with this code. Existing smaller histories in other
component directories remain separate and untouched.

Shared _MAP/template owners receive exact new roots, relative ticker paths, pinned
hashes and the unqualified-archive status from the private completion receipt. They
must explicitly adopt routing; the relocation does not edit their registries or
pretend the analyst's qualified-source requirements are satisfied.

Offline tests exercise original preservation, idempotent lookup/restart, collision
and mismatched-staging refusal, escape rejection, competing lock refusal and a crash
after final copy but before staging retirement. Production evidence belongs in the
private journal and completion receipt; tests alone do not prove an executed move.
