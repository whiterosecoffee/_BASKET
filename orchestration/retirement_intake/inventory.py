"""Read-only discovery index over supplied GitHub evidence; never a scheduler.

Snapshots are historical. Re-fetch GitHub evidence before relying on current state.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate(evidence):
    for flag in ('open_prs_complete', 'open_issues_complete', 'branches_complete'):
        if evidence.get(flag) is not True:
            raise ValueError('incomplete evidence: ' + flag)
    if evidence.get('tree_truncated') is not False:
        raise ValueError('incomplete main tree')
    if not re.fullmatch('[0-9a-f]{40}', evidence.get('main_sha', '')):
        raise ValueError('invalid main SHA')
    if datetime.fromisoformat(evidence['observed_at'].replace('Z', '+00:00')).utcoffset() is None:
        raise ValueError('observation requires timezone')
    numbers = set()
    for pr in evidence['pull_requests']:
        if pr['number'] in numbers:
            raise ValueError('duplicate PR')
        numbers.add(pr['number'])
        if not pr.get('files_complete') or not re.fullmatch('[0-9a-f]{40}', pr['head_sha']):
            raise ValueError('incomplete PR evidence')
        paths = [f['path'] for f in pr['files']]
        if len(paths) != len(set(paths)):
            raise ValueError('duplicate changed path')
        if any(p.startswith('/') or '..' in p.split('/') for p in paths):
            raise ValueError('unsafe repository path')


def exact_checks(pr):
    # Return evidence only: green unrelated CI does not verify domain behavior.
    return [r for r in pr['ci'] if r['sha'] == pr['head_sha']]


def build(evidence, previous=None):
    validate(evidence)
    capabilities = []
    path_owners = {}
    for pr in sorted(evidence['pull_requests'], key=lambda p: p['number']):
        paths = sorted(f['path'] for f in pr['files'])
        for path in paths:
            path_owners.setdefault(path, []).append(pr['number'])
        owner = re.search(r'\bB\d{2}\b', pr['title'])
        code = [p for p in paths if p.endswith('.py') and '/test' not in p and not p.rsplit('/', 1)[-1].startswith('test_')]
        contracts = [p for p in paths if '/contracts/' in p or p.startswith('schemas/') or p.endswith('component.json')]
        deps = sorted(set(int(n) for n in re.findall(r'#(\d+)\b', pr['body'] or '')))
        item = dict(id='pr-' + str(pr['number']), name=pr['title'], owner=owner.group() if owner else None,
                    owner_evidence='PR title; issue scope review still required',
                    branch=pr['branch'], commit_sha=pr['head_sha'], pr=pr['number'],
                    url=f"https://github.com/{evidence['repository']}/pull/{pr['number']}",
                    source_paths=paths, dependency_issues=deps, contract_paths=contracts,
                    input_schema_version=None, output_schema_version=None,
                    entrypoint_candidates=code, invocation=None,
                    tests=[p for p in paths if '/test' in p or p.rsplit('/', 1)[-1].startswith('test_')],
                    exact_head_ci=exact_checks(pr), implementation_state='review',
                    operational_evidence=None, historical_coverage=None, freshness=None,
                    limitation='Discovery only; schema versions, invocation and operation require source/runner review.',
                    dependency_fingerprint=fingerprint(dict(head=pr['head_sha'], files=pr['files'], main=evidence['main_sha'])))
        item['declared_interface'] = evidence.get('component_details', {}).get(str(pr['number']))
        capabilities.append(item)
    blobs = {f['path']: f['sha'] for f in evidence['main_tree'] if f['type'] == 'blob'}
    main_components = [
        ('planner', 'Evidence-gated task planner', 'B00', ['orchestration/planner.py', 'orchestration/github_snapshot.py'], 'python orchestration/planner.py --help'),
        ('worker-qc', 'Worker claim and acceptance validation', 'B00', ['orchestration/worker_protocol.py'], 'python orchestration/worker_protocol.py --help'),
        ('ttd', 'Observation freshness and ingestion CLI', 'B02', ['runtime/ttd.py', 'runtime/feeds.json'], 'python runtime/ttd.py --help'),
        ('traversal', 'Historical daily range traversal', 'B06', ['engines/traversal/range.py'], 'python engines/traversal/range.py --help'),
        ('narrative', 'Narrative evidence processing', 'B21', ['engines/narrative/engine.py'], None),
    ]
    for key, name, owner, paths, command in main_components:
        present = {p: blobs[p] for p in paths if p in blobs}
        if present:
            capabilities.append(dict(id='main-' + key, name=name, owner=owner,
                branch='main', commit_sha=evidence['main_sha'], source_paths=sorted(present),
                dependency_fingerprint=fingerprint(present), implementation_state='integrated',
                invocation_candidate=command, domain_test_verification=None,
                operational_evidence=None, limitation='Source present on main; live operation not inferred.'))
    old = {c['id']: c for c in (previous or {}).get('capabilities', [])}
    invalidated = [c['id'] for c in capabilities if c['id'] in old and old[c['id']]['dependency_fingerprint'] != c['dependency_fingerprint']]
    retired = sorted(set(old) - {c['id'] for c in capabilities})
    return dict(repository=evidence['repository'], observed_at=evidence['observed_at'],
        main_sha=evidence['main_sha'], evidence_sha256=fingerprint(evidence),
        cache_policy='Historical evidence only; any relevant SHA/fingerprint change requires refresh.',
        main_ci=evidence['main_ci'], capabilities=capabilities,
        exact_path_collisions=[dict(path=p, prs=owners) for p, owners in sorted(path_owners.items()) if len(owners) > 1],
        scope_review='Exact path comparison complete; issue/glob/semantic ownership still requires review.',
        invalidated_records=invalidated, absent_since_previous=retired,
        absence_policy='Refresh missing records; never infer deletion, merge or nonexistence from cache absence.',
        operational_status='unverified', active_worker_capacity=None)


def cache_matches(inventory, evidence, max_age_seconds=300, now=None):
    validate(evidence)
    now = now or datetime.now(timezone.utc)
    observed = datetime.fromisoformat(evidence['observed_at'].replace('Z', '+00:00'))
    age = (now - observed).total_seconds()
    return (0 <= age <= max_age_seconds and inventory.get('main_sha') == evidence['main_sha']
            and inventory.get('evidence_sha256') == fingerprint(evidence))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--query', default='')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = build(json.loads(args.evidence.read_text()), json.loads(args.previous.read_text()) if args.previous else None)
    if args.query:
        report = [c for c in report['capabilities'] if args.query.casefold() in json.dumps(c).casefold()]
    rendered = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        if args.output.exists():
            parser.error('refusing to overwrite historical report; choose a new revision filename')
        args.output.write_text(rendered)
    else:
        print(rendered, end='')


if __name__ == '__main__':
    main()
