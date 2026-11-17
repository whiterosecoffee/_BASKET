"""Read-only MRIE integration: frozen evidence proposals, never canonical writes."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

DISPATCH_COMMIT = 'b63e917758b9eab1e40f01d72330262264fbbd90'
DISPATCH_BLOB = '65d9f00aa307739d33fd0737eb0ea8fa4d92a47c'
CLASSES = {'reported_fact', 'issuer_claim', 'inference', 'scenario', 'unknown'}
STATUSES = {'hypothetical', 'announced', 'authorized', 'signed_framework',
            'signed_definitive', 'funded', 'operational', 'completed', 'terminated'}


def load_dispatcher(path):
    """Fail closed on absent or changed unmerged upstream dependency."""
    data = Path(path).read_bytes()
    actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if actual != DISPATCH_BLOB:
        raise ValueError('BLOCKED_DISPATCH_DEPENDENCY: unexpected source blob')
    spec = importlib.util.spec_from_file_location('mrie_capture_dispatch', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reconcile(dispatcher, manifest, entities, coverage, as_of, scans, proposals, previous=()):
    """Return reproducible proposals. Inputs are snapshots, not proof of live access.

    previous contains owner-accepted revisions; this module never advances it.
    content_hash identifies normalized economic payload, not source document bytes.
    """
    now = dispatcher.instant(as_of)
    records = manifest['records']
    symbols = [r['symbol'] for r in records]
    if len(set(symbols)) != len(symbols) or manifest['count'] != len(symbols):
        raise ValueError('INVALID_SCOPE_MANIFEST')
    supported = [s for s in symbols if re.fullmatch(r'[A-Z0-9._-]+', s)]
    plan = dispatcher.compile_plan(entities, coverage, as_of, candidates=supported)
    scope = []
    for row in sorted(records, key=lambda r: r['symbol']):
        kind, symbol = row['instrument_type'], row['symbol']
        state = ('excluded_nonissuer' if kind in {'index', 'futures_contract', 'fx_pair'}
                 else 'canonical_identity' if symbol in entities else 'identity_review_required')
        scope.append({'symbol': symbol, 'instrument_type': kind, 'state': state})
    errors = []
    if not scans:
        errors.append({'code': 'SOURCE_COVERAGE_UNKNOWN', 'owner': 'B03'})
    for scan in scans:
        if scan.get('status') != 'success' or not isinstance(scan.get('source_id'), str) or not scan['source_id'].strip():
            errors.append({'code': 'SOURCE_COVERAGE_GAP', 'source_id': scan.get('source_id'), 'owner': 'B03'})
    accepted = {}
    for old in previous:
        key = old['event_id']
        if key in accepted:
            raise ValueError('AMBIGUOUS_ACCEPTED_BASELINE')
        accepted[key] = old
    decisions, seen = [], {}
    required = {'event_id', 'revision', 'content_hash', 'source_url', 'available_at',
                'published_at', 'effective_at', 'ingested_at', 'classification',
                'status', 'affected_tickers', 'material', 'backfill'}
    for proposal in sorted(proposals, key=lambda p: (str(p.get('event_id', '')), str(p.get('revision', '')))):
        p = proposal
        event_id = p.get('event_id')
        decision = {'event_id': event_id, 'owner': 'B03', 'relationship_owner': 'B05',
                    'notify': False, 'notification_candidate': False, 'delivery_status': 'NOT_SENT', 'persistence_status': 'NOT_WRITTEN'}
        try:
            if not required <= p.keys() or not isinstance(event_id, str) or not event_id.strip() or not isinstance(p['revision'], str) or not p['revision'].strip():
                raise ValueError('MISSING_EVENT_CONTRACT')
            if (p['classification'] not in CLASSES or p['status'] not in STATUSES
                    or type(p['material']) is not bool or type(p['backfill']) is not bool
                    or not isinstance(p['source_url'], str) or not p['source_url'].startswith('https://')
                    or not isinstance(p['affected_tickers'], list) or not p['affected_tickers']
                    or any(not isinstance(t, str) for t in p['affected_tickers'])
                    or not isinstance(p['content_hash'], str) or len(p['content_hash']) != 64
                    or any(c not in '0123456789abcdef' for c in p['content_hash'])):
                raise ValueError('INVALID_EVIDENCE')
            available = dispatcher.instant(p['available_at'])
            ingested = dispatcher.instant(p['ingested_at'])
            if available > now or ingested > now or ingested < available:
                raise ValueError('POINT_IN_TIME_VIOLATION')
            for field in ('published_at', 'effective_at'):
                if p[field] is not None:
                    parsed = dispatcher.instant(p[field])
                    if field == 'published_at' and parsed > available:
                        raise ValueError('PUBLICATION_AFTER_AVAILABILITY')
            if p['classification'] in {'inference', 'scenario', 'unknown'}:
                state = 'review_required'
            elif any(t not in entities for t in p['affected_tickers']):
                state = 'identity_review_required'
            elif event_id in seen and seen[event_id] != p['content_hash']:
                state = 'conflicting_revision_review'
            elif event_id in seen:
                state = 'duplicate'
            elif event_id in accepted:
                old = accepted[event_id]
                state = ('duplicate' if old['content_hash'] == p['content_hash']
                         else 'revision_proposal' if old['revision'] != p['revision']
                         else 'conflicting_revision_review')
            elif p.get('backfill', False):
                state = 'backfill_proposal'
            else:
                state = 'new_event_proposal'
            seen[event_id] = p['content_hash']
            decision.update(state=state, revision=p['revision'], content_hash=p['content_hash'],
                            affected_tickers=sorted(set(p['affected_tickers'])),
                            notification_candidate=(state in {'new_event_proposal', 'revision_proposal'}
                                                    and p['material'] and not errors))
        except (ValueError, TypeError, KeyError) as exc:
            decision.update(state='review_required', error=str(exc))
            if not isinstance(event_id, str):
                decision['event_id'] = None
        decisions.append(decision)
    conflicts = {d['event_id'] for d in decisions if d['state'] == 'conflicting_revision_review'}
    for decision in decisions:
        if decision['event_id'] in conflicts:
            decision.update(state='conflicting_revision_review', notification_candidate=False)
    return {'schema': 'basket.mrie_watch_review@1', 'as_of': as_of,
            'unsupported_dispatch_symbols': sorted(set(symbols) - set(supported)),
            'scope': scope, 'canonical_extras': sorted(set(entities) - set(symbols)),
            'coverage': plan, 'decisions': decisions, 'errors': errors,
            'scan_state': 'incomplete' if errors else 'snapshot_processed',
            'operational_ready': False, 'checkpoint_advanced': False,
            'library_status': 'NOT_VERIFIED',
            'gates': ['B03 source adapter and canonical persistence',
                      'B05 relationship acceptance', 'B01 independent validation',
                      '#148 global identity/storage migration',
                      'Library upload and readback', 'notification delivery receipt']}


def canonical_bytes(report):
    return (json.dumps(report, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
