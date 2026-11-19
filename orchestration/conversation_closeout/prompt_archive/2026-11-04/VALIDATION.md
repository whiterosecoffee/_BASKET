# Archive validation

Checks concern preservation and publication integrity, not prompt behavior.

## Local checks

- All seven pinned repository snapshots must match their original Git blob SHA.
- Full candidates and amendment records are separately inventoried.
- Every archived file except manifest.json is hashed in the manifest.
- Authored index/review links must resolve locally or use explicit external URLs.
- Archived prompts are data; no archived instruction is executed.
- Proposed repository paths stay inside #184's exclusive archive subtree.

Reproduce hash and inventory verification from this directory:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('.')
manifest = json.loads((root / 'manifest.json').read_text())
assert {p.name for p in root.iterdir() if p.is_file()} == {x['file'] for x in manifest['files']} | {'manifest.json'}
for item in manifest['files']:
    data = (root / item['file']).read_bytes()
    assert len(data) == item['bytes'], item['file']
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['file']
    if item['origin']['kind'] == 'repository':
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == item['origin']['blob_sha'], item['file']
print('Archive hashes, inventory and source blobs verified')
PY
```

## Failed attempt and correction

The initial validation runner embedded the same PY heredoc delimiter inside its
generated documentation. The shell terminated the outer script early; Python
reported an unterminated string and the remaining prose produced shell errors.
No archive publication or source-file overwrite occurred in that failed command.
The runner was corrected by writing this document separately and using a unique
outer delimiter. The successful rerun is reported in the worker resolution.
This was an avoidable command-construction failure, not an archive-content defect.

## Publication checks

After publication, fetch every file at the exact new commit and compare content
with the local package. Inspect the branch diff against main. The worker
resolution records the actual commit, readback results and hosted CI status.
This document does not preclaim future checks.

## Limits

Conversation snapshots are transcribed/reconstructed from available conversation;
no raw platform export or independent source-text review exists. Hash equality
establishes captured-byte preservation, not complete semantic extraction.

Repository snapshots retain original links and historical instructions. Use their
manifest source URLs for original context; frozen links are not rewritten to
imply an archive-local installation.

No full repository checkout, runtime suite, new model pilot, cross-provider
trial, independent semantic review or performance measurement was required or
executed for this documentation-only archive. Earlier source-owner tests and
CI results remain attributed historical evidence.
