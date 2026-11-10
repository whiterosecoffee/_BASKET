"""Build one existing QC request from committed source bytes, without submitting it.

Codex, Claude Code and other clients use the same file. No provider calls,
credentials, network, queue writes, lease grants or review/acceptance claims.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from .qc_intake import request_id, require, validate_request
from orchestration.worker_protocol import permitted


def build_request(task, source_pr, revision, primary_paths, handoff_path,
                  item_ids, read_bytes):
    """Reuse the intake contract; a local pin is not authenticated GitHub evidence."""
    artifacts = [dict(path=p, revision=revision, role='primary', sha256='0' * 64)
                 for p in primary_paths]
    artifacts.append(dict(path=handoff_path, revision=revision, role='handoff', sha256='0' * 64))
    request = dict(task=copy.deepcopy(task), source_pr=source_pr, artifacts=artifacts,
                   item_ids=list(item_ids), review_kind='closeout_semantic')
    request['request_id'] = request_id(request)
    # Reject unsafe paths, wrong ownership/identity and unpinned refs BEFORE reads.
    validate_request(request)
    handoff = None
    for artifact in artifacts:
        data = read_bytes(artifact['path'], revision)
        require(isinstance(data, bytes), 'artifact reader must return bytes')
        artifact['sha256'] = hashlib.sha256(data).hexdigest()
        if artifact['role'] == 'handoff':
            handoff = data.decode('utf-8')
    observed = re.findall(r'^([A-Z][A-Z0-9_-]*[0-9])(?=[: \t])', handoff, re.M)
    require(len(observed) == len(set(observed)), 'duplicate handoff item IDs')
    require(set(observed) == set(item_ids), 'handoff and submitted item IDs differ')
    # This catches obvious omissions only. The reviewer independently recovers
    # source obligations; matching IDs do not prove semantic completeness.
    request['artifacts'].sort(key=lambda a: (a['path'], a['revision'], a['role']))
    request['item_ids'].sort()
    request['request_id'] = request_id(request)
    return validate_request(request)


def git(repo, *args):
    result = subprocess.run(['git', '--no-replace-objects', '--literal-pathspecs', '-C', str(repo), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(result.returncode == 0, 'git source read failed: ' + result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def committed_reader(repo, revision):
    require(re.fullmatch(r'[0-9a-f]{40}', revision) is not None, 'revision must be a full commit SHA')
    require(git(repo, 'cat-file', '-t', revision).strip() == b'commit', 'revision is not a commit')
    def read_bytes(path, rev):
        require(rev == revision, 'reader revision differs from pinned commit')
        entry = git(repo, 'ls-tree', '-z', revision, '--', path)
        require(entry.startswith((b'100644 blob ', b'100755 blob ')) and
                entry.partition(b'\t')[2] == path.encode('utf-8') + b'\0',
                'artifact is missing or is not a regular committed file')
        return git(repo, 'cat-file', 'blob', revision + ':' + path)
    return read_bytes


def write_request(repo, output, request):
    """Create an owner-local file; identical replay is a no-op, never overwrite."""
    validate_request(request)
    root = Path(repo).resolve()
    relative = Path(output)
    require(not relative.is_absolute() and all(p not in ('', '.', '..') for p in output.split('/'))
            and '\\' not in output, 'output must be a safe repository-relative path')
    require(permitted(output, request['task']['write_paths']), 'output outside task ownership')
    # Even B00 producers cannot use this helper to overwrite the shared index or
    # a reviewer receipt. Those require the existing intake worker and CAS.
    reserved = 'orchestration/conversation_closeout/versions/'
    require(output != reserved + 'QC_QUEUE.json' and not output.startswith(reserved + 'qc_archive/'),
            'shared queue and receipts belong to the intake reviewer')
    target = root / relative
    require(not any(p.is_symlink() for p in [target, *target.parents] if p != root)
            and target.resolve().is_relative_to(root), 'output symlink or path escape')
    # Parents must already exist; do not create directories outside a task claim.
    require(target.parent.is_dir(), 'output parent directory does not exist')
    data = (json.dumps(request, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    try:
        with target.open('xb') as stream:
            stream.write(data)
    except FileExistsError:
        require(target.is_file() and target.read_bytes() == data, 'output exists with different content; choose a new filename')
        return 'unchanged'
    return 'created'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-repo', type=Path, required=True)
    parser.add_argument('--task', type=Path, required=True, help='Existing basket.worker_task@1 JSON')
    parser.add_argument('--source-pr', type=int, required=True)
    parser.add_argument('--revision', required=True, help='Full source commit SHA, not HEAD or a branch')
    parser.add_argument('--primary', action='append', required=True, help='Owner-scoped repository path')
    parser.add_argument('--handoff', required=True, help='Owner-scoped complete handoff path')
    parser.add_argument('--item-id', action='append', required=True)
    parser.add_argument('--output', required=True, help='New owner-scoped path relative to source repository')
    args = parser.parse_args(argv)
    try:
        task = json.loads(args.task.read_text(encoding='utf-8'))
        root = Path(git(args.source_repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
        require(root == args.source_repo.resolve(), 'source-repo must be the checkout root')
        request = build_request(task, args.source_pr, args.revision, args.primary,
                                args.handoff, args.item_id, committed_reader(root, args.revision))
        status = write_request(root, args.output, request)
        print(json.dumps({'status': status, 'request_id': request['request_id'],
                          'output': args.output, 'submitted': False, 'accepted': False}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc), 'submitted': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
