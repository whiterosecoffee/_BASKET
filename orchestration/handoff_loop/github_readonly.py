"""Bounded GitHub metadata observation; no evaluator/acceptance/dispatch adapter."""
from datetime import datetime
import hashlib
import math
import re
import shutil
import subprocess
import time

from .core import digest, require
from .synthetic_adapter import load_json, shape

REPOSITORY = 'whiterosecoffee/_BASKET'
PR_NUMBER = 264
BRANCH = 'work/169-handoff-loop-20261112'
API = 'https://api.github.com'
WEB = 'https://github.com'


def endpoints(head):
    require(type(head) is str and re.fullmatch('[0-9a-f]{40}', head) is not None, 'exact head required')
    return {'pr': f'/repos/{REPOSITORY}/pulls/{PR_NUMBER}',
            'ci': f'/repos/{REPOSITORY}/actions/runs?head_sha={head}&per_page=100'}


def epoch(value):
    require(type(value) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)', value) is not None, 'timezone-bearing source timestamp required')
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
    except (ValueError, OverflowError) as exc:
        raise ValueError('invalid source timestamp') from exc


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def normalize_supplied(responses, *, head, now, seen_observations=(), max_age=300):
    """Pure normalization never labels caller-supplied data as verified retrieval.

    A replay ID must be provided by the caller's existing ledger; this function
    owns no persistent ledger. Duplicate IDs in that ledger reject.
    """
    paths = endpoints(head)
    shape(responses, 'pr ci')
    require(finite(now) and finite(max_age) and max_age > 0, 'invalid clock/freshness bound')
    require(type(seen_observations) in (list, tuple) and all(type(x) is str for x in seen_observations), 'invalid replay inventory')
    require(len(set(seen_observations)) == len(seen_observations), 'duplicate replay inventory')
    bodies, sources = {}, {}
    for name, row in responses.items():
        shape(row, 'source_url observed_at raw_json raw_sha256')
        require(row['source_url'] == API + paths[name], 'substituted retrieval origin')
        require(finite(row['observed_at']) and 0 <= now - row['observed_at'] <= max_age, 'stale/future/invalid observation time')
        require(type(row['raw_json']) is str, 'raw response text required')
        actual = hashlib.sha256(row['raw_json'].encode('utf-8')).hexdigest()
        require(row['raw_sha256'] == actual, 'raw response digest mismatch')
        body = load_json(row['raw_json'])
        require(type(body) is dict, 'object response required')
        bodies[name] = body
        sources[name] = {'source_id': row['source_url'], 'observed_at': row['observed_at'], 'raw_response_sha256': actual}

    def check_times(body, name):
        require('created_at' in body and 'updated_at' in body, 'missing source times')
        created, updated = epoch(body['created_at']), epoch(body['updated_at'])
        require(created <= updated <= responses[name]['observed_at'], 'source time order/future timestamp')
        return {'created_at': body['created_at'], 'updated_at': body['updated_at']}

    pr = bodies['pr']
    require(all(k in pr for k in ('number','id','url','html_url','head','base','state','draft')), 'missing PR fields')
    require(type(pr['id']) is int and pr['id'] > 0 and type(pr['number']) is int and pr['number'] == PR_NUMBER, 'wrong PR identity')
    require(pr['url'] == API + paths['pr'] and pr['html_url'] == f'{WEB}/{REPOSITORY}/pull/{PR_NUMBER}', 'wrong PR origin')
    for side in ('head', 'base'):
        require(type(pr[side]) is dict and type(pr[side].get('repo')) is dict and pr[side]['repo'].get('full_name') == REPOSITORY, 'wrong repository')
    require(pr['head'].get('sha') == head and pr['head'].get('ref') == BRANCH, 'changed source head/branch')
    require(pr['base'].get('ref') == 'main', 'unexpected base branch')
    require(pr['state'] in ('open', 'closed') and type(pr['draft']) is bool, 'invalid PR state')
    pr_times = check_times(pr, 'pr')
    sources['pr'].update(resource_id=pr['id'], subject_revision=head, source_times=pr_times)
    ci = bodies['ci']
    require(type(ci.get('total_count')) is int and ci['total_count'] >= 0 and type(ci.get('workflow_runs')) is list, 'missing CI inventory')
    require(len(ci['workflow_runs']) <= 100 and ci['total_count'] >= len(ci['workflow_runs']), 'invalid CI count')
    runs, ids = [], set()
    for run in ci['workflow_runs']:
        require(type(run) is dict and all(k in run for k in ('id','url','html_url','head_sha','repository','status','conclusion','name')), 'missing run fields')
        rid = run['id']
        require(type(rid) is int and rid > 0 and rid not in ids, 'duplicate/invalid run ID')
        ids.add(rid)
        require(run['url'] == f'{API}/repos/{REPOSITORY}/actions/runs/{rid}' and run['html_url'] == f'{WEB}/{REPOSITORY}/actions/runs/{rid}', 'wrong run origin')
        require(type(run['repository']) is dict and run['repository'].get('full_name') == REPOSITORY and run['head_sha'] == head, 'run subject/revision mismatch')
        require(type(run['name']) is str and bool(run['name'].strip()), 'run name required')
        require(run['status'] in ('queued','in_progress','completed','waiting','requested','pending'), 'unsupported run status')
        conclusions = ('success','failure','neutral','cancelled','skipped','timed_out','action_required','stale','startup_failure')
        require((run['status'] == 'completed' and run['conclusion'] in conclusions) or (run['status'] != 'completed' and run['conclusion'] is None), 'inconsistent run conclusion')
        runs.append(dict(id=rid, url=run['html_url'], name=run['name'], head_sha=head,
                         status=run['status'], conclusion=run['conclusion'], source_times=check_times(run, 'ci')))
    runs.sort(key=lambda x: x['id'])
    sources['ci']['subject_revision'] = head
    source_identity = {'repository': REPOSITORY, 'pr': PR_NUMBER, 'head': head,
                       'pr_source_times': pr_times, 'pr_state': pr['state'], 'pr_draft': pr['draft'],
                       'runs': runs, 'total_count': ci['total_count']}
    observation_id = digest(source_identity)
    replay = observation_id in seen_observations
    complete = len(runs) == ci['total_count']
    return dict(schema='basket.handoff_github_observation@0.1-draft', availability='available',
                subject={'repository':REPOSITORY,'pr':PR_NUMBER,'revision':head}, observation_id=observation_id,
                disposition='no-change' if replay else 'observed', sources=sources,
                pr={'url':pr['html_url'],'state':pr['state'],'draft':pr['draft']},
                ci={'availability':'available' if runs and complete else 'unknown', 'complete':complete,
                    'reason':None if runs and complete else 'no exact-head runs' if not runs else 'bounded page incomplete', 'runs':runs},
                retrieval={'method':'supplied_payload','verified_local_retrieval':False},
                source_claims_verified=False, component_tests_verified=False,
                reviewer_acceptance=False, execution_authorized=False,
                evaluator_observation=None, acceptance_receipts=[])


def _read_responses(head):
    """Internal raw-response port for local callers; never persist these bodies."""
    paths = endpoints(head)
    executable = shutil.which('gh')
    if not executable:
        return None, unavailable(head, 'GitHub CLI unavailable')
    responses = {}
    for name, path in paths.items():
        try:
            result = subprocess.run([executable, 'api', '--hostname', 'github.com', '--method', 'GET',
                                     '-H', 'Accept: application/vnd.github+json', '-H', 'X-GitHub-Api-Version: 2022-11-28', path],
                                    capture_output=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None, unavailable(head, 'read unavailable or timed out')
        if result.returncode != 0:
            return None, unavailable(head, 'GitHub metadata GET failed')
        try:
            raw = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            return None, unavailable(head, 'invalid response encoding')
        responses[name] = dict(source_url=API+path, observed_at=time.time(), raw_json=raw,
                               raw_sha256=hashlib.sha256(result.stdout).hexdigest())
    return responses, None


def collect(*, head, seen_observations=()):
    """Two allowlisted GETs with existing gh access. No retry or credential changes.

    This process trusts the installed CLI, local runtime, HTTPS transport and
    clock. Its retrieval label is not a signature or independently portable proof.
    """
    responses, failure = _read_responses(head)
    if failure is not None:
        return failure
    packet = normalize_supplied(responses,head=head,now=time.time(),seen_observations=seen_observations)
    packet['retrieval'] = dict(method='local_gh_api_https_get', requested_origin=API,
                               verified_local_retrieval=True, verification='allowlisted GET + returned resource identity + SHA256 of raw UTF-8 JSON')
    return packet


def unavailable(head, reason):
    endpoints(head)
    return dict(schema='basket.handoff_github_observation@0.1-draft',availability='unavailable',reason=reason,
                subject={'repository':REPOSITORY,'pr':PR_NUMBER,'revision':head},
                retrieval={'method':'local_gh_api_https_get','verified_local_retrieval':False},
                source_claims_verified=False,component_tests_verified=False,reviewer_acceptance=False,
                execution_authorized=False,evaluator_observation=None,acceptance_receipts=[])
