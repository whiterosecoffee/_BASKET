"""Completed-minute research consumer, not a provider client or trading system.
Detector/score adapted from B10 PR69 range_replay.py and battle_matrix.py.
All constants below are uncalibrated engineering choices; keep source versioned.
"""
import copy
import hashlib
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION = 'ticker-patterns@1.0.0'
ET = ZoneInfo('America/New_York')
MINUTE = 60000
CONFIG = {'formation': 30, 'window': 15, 'half_life': 5, 'min_side_bars': 3,
          'min_effective_n': 2, 'break_closes': 2, 'tick': .01,
          'cluster_range_fraction': .6, 'retreat_width_fraction': .1}


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def method_hash():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def clock(s):
    d = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError('timezone required')
    return int(d.timestamp()*1000)


def stamp(t):
    return datetime.fromtimestamp(t/1000, ET).isoformat()


def session(t):
    return datetime.fromtimestamp(t/1000, ET).date().isoformat()


def minute(t):
    d = datetime.fromtimestamp(t/1000, ET)
    return d.hour*60+d.minute


def contiguous(bars):
    return all(b['t']-a['t'] == MINUTE for a, b in zip(bars, bars[1:]))


def validate_bars(bars):
    previous = -1
    for b in bars:
        if any(not isinstance(b[k], (float, int)) or isinstance(b[k], bool)
               or not math.isfinite(b[k]) for k in ('t', 'o', 'h', 'l', 'c', 'v', 'vw')):
            raise ValueError('finite numeric bar fields required')
        if b['t'] != int(b['t']) or b['t'] <= previous:
            raise ValueError('unique increasing integer timestamps required')
        previous = b['t']
        if b['v'] < 0 or min(b[k] for k in ('o', 'h', 'l', 'c', 'vw')) <= 0:
            raise ValueError('invalid price/volume')
        if not b['l'] <= min(b['o'], b['c']) <= max(b['o'], b['c']) <= b['h']:
            raise ValueError('invalid OHLC envelope')


def cluster(points, tolerance):
    groups = []
    for p, i in sorted(points):
        if not groups or p-groups[-1][0][0] > tolerance:
            groups.append([])
        groups[-1].append((p, i))
    candidates = []
    for group in groups:
        selected = []
        for p, i in sorted(group, key=lambda x: x[1]):
            if not selected or i-selected[-1][1] >= 3:
                selected.append((p, i))
        if len(selected) >= 2:
            candidates.append(selected)
    return max(candidates, key=lambda g: (len(g), max(i for _, i in g))) if candidates else None


def detect(past):
    if len(past) != CONFIG['formation'] or not contiguous(past):
        return None
    tolerance = max(3*CONFIG['tick'], statistics.median(b['h']-b['l'] for b in past)*CONFIG['cluster_range_fraction'])
    lows, highs = [], []
    for i in range(1, len(past)-1):
        a, b, c = past[i-1:i+2]
        if b['l'] <= a['l'] and b['l'] < c['l']:
            lows.append((b['l'], i))
        if b['h'] >= a['h'] and b['h'] > c['h']:
            highs.append((b['h'], i))
    lower, upper = cluster(lows, tolerance), cluster(highs, tolerance)
    if not lower or not upper:
        return None
    def band(g):
        return [min(p for p, _ in g)-tolerance*.25, max(p for p, _ in g)+tolerance*.25]
    lb, ub = band(lower), band(upper)
    if lb[1] >= ub[0] or ub[1]-lb[0] < 3*tolerance or not lb[0] <= past[-1]['c'] <= ub[1]:
        return None
    return {'lower': lb, 'upper': ub, 'width': ub[1]-lb[0], 'tolerance': tolerance,
            'formation_start': past[0]['t'], 'frozen_at': past[-1]['t']+MINUTE,
            'pivot_counts': {'lower': len(lower), 'upper': len(upper)}}


def activity(rows):
    v = sum(b['v'] for b in rows)
    d = sum(b['v']*b['vw'] for b in rows)
    return {'shares': v, 'dollars': d, 'bars': len(rows), 'vwap': d/v if v else None}


def path(rows, width):
    if not rows or not contiguous(rows):
        return {'signed_efficiency': None, 'gross_ranges': None, 'net_ranges': None,
                'state': 'empty_or_gapped'}
    points = [rows[0]['o']]+[b['c'] for b in rows]
    gross = sum(abs(b-a) for a, b in zip(points, points[1:]))
    net = points[-1]-points[0]
    return {'signed_efficiency': net/gross if gross else None,
            'gross_ranges': gross/width, 'net_ranges': net/width,
            'state': 'flat' if not gross else 'observed_close_path'}


def score(rows, zone, previous):
    """S=(weighted up travel/up $)/(weighted down travel/down $).
    Range width and common ADV normalization cancel. S>1 is NOT net-up drift.
    No volume sign or investor intent is inferred from candle direction.
    """
    sides = {s: {'travel': 0., 'dollars': 0., 'bars': 0, 'w': 0., 'w2': 0.} for s in ('up', 'down')}
    neutral = 0.
    lo, hi = zone['lower'][0], zone['upper'][1]
    clip = lambda p: min(hi, max(lo, p))
    for b in rows:
        move = (clip(b['c'])-clip(previous))/(hi-lo)
        previous = b['c']
        if not lo <= b['vw'] <= hi:
            continue
        dollars = b['v']*b['vw']
        if not move:
            neutral += dollars
            continue
        if dollars <= 0:
            continue
        s = sides['up' if move > 0 else 'down']
        w = 2**(-((rows[-1]['t']-b['t'])/MINUTE)/CONFIG['half_life'])
        s['travel'] += w*abs(move)
        s['dollars'] += w*dollars
        s['bars'] += 1
        s['w'] += w
        s['w2'] += w*w
    for s in sides.values():
        s['effective_n'] = s['w']**2/s['w2'] if s['w2'] else 0.
        s['efficiency_per_dollar'] = s['travel']/s['dollars'] if s['dollars'] else None
    enough = contiguous(rows) and all(s['bars'] >= CONFIG['min_side_bars'] and s['effective_n'] >= CONFIG['min_effective_n'] for s in sides.values())
    ratio = sides['up']['efficiency_per_dollar']/sides['down']['efficiency_per_dollar'] if enough else None
    return {'ratio': ratio, 'state': 'scored' if ratio is not None else 'insufficient_or_gapped',
            'sides': sides, 'neutral_dollars': neutral}


def baseline(daily, day):
    prior = [b for b in daily if session(b['t']) < day][-20:]
    return {'sessions': len(prior), 'adv20': statistics.mean(b['v'] for b in prior) if len(prior) == 20 else None,
            'addv20': statistics.mean(b['v']*b['vw'] for b in prior) if len(prior) == 20 else None}


def rvol(rows, profiles, day, calendar=None):
    offsets = {minute(b['t']) for b in rows}
    if calendar is None:
        calendar = {}
        for b in profiles:
            if 570 <= minute(b['t']) < 960:
                calendar.setdefault(session(b['t']), []).append(b)
    candidates = {d: bars for d,bars in calendar.items() if d < day}
    volumes = []
    for _, bars in sorted(candidates.items())[-20:]:
        # Comparable completed 390-minute sessions only; early closes excluded.
        if len(bars) == 390 and minute(bars[0]['t']) == 570 and minute(bars[-1]['t']) == 959 and contiguous(bars):
            volumes.append(sum(b['v'] for b in bars if minute(b['t']) in offsets))
    expected = statistics.mean(volumes) if len(volumes) >= 5 else None
    return {'ratio': sum(b['v'] for b in rows)/expected if expected else None,
            'profile_sessions': len(volumes), 'reason': None if expected else 'need five prior complete matching sessions'}


def nearest(patterns, ticker, asof, vector, retrospective=False):
    matches = []
    if vector[1] is None or vector[2] is None:
        return []
    def transform(v):
        return [v[0], math.log(max(.05, min(20., v[1]))), v[2]]
    target = transform(vector)
    for r in patterns:
        if r.get('ticker') != ticker or clock(r['evaluated_through']) >= asof or r['quality']['right_censored']:
            continue
        available = r['quality'].get('available_at')
        if not retrospective and (available is None or clock(available) > asof):
            continue
        f = r['features_at_freeze']
        v = [f['start_position'], f['formation_flow']['score'], f['formation_path']['signed_efficiency']]
        if v[1] is None or v[2] is None:
            continue
        distance = math.sqrt(sum((a-b)**2 for a, b in zip(target, transform(v))))
        # Outcomes attached AFTER distance; never used in contemporaneous feature vector.
        matches.append({'event_id': r['event_id'], 'distance': distance,
                        'evaluated_through': r['evaluated_through'], 'available_at': available,
                        'outcome': r['outcome']['first_passage']['outcome'],
                        'point_in_time_verified': available is not None and clock(available) <= asof})
    return sorted(matches, key=lambda r: (r['distance'], r['event_id']))[:10]


def boundary_state():
    return {'armed': True, 'active': None, 'away': 0, 'contacts': 0, 'retreats': 0,
            'last_contact_at': None, 'last_response': None}


def boundary_step(state, bar, band, side, width):
    """Adjacent contact bars form one episode; rearm after two fully-away bars.
    Same-bar touch+retreat ordering is unknown; report ambiguous rather than reject.
    """
    events = []
    touch = bar['l'] <= band[1] and bar['h'] >= band[0]
    retreat_buffer = max(2*CONFIG['tick'], width*CONFIG['retreat_width_fraction'])
    if touch and state['armed']:
        state['contacts'] += 1
        state['active'] = {'started_at': bar['t'], 'shares': 0., 'dollars': 0.}
        state['last_contact_at'] = bar['t']+MINUTE
        state['armed'] = False
        events.append({'kind': side+'_contact', 'at': bar['t']+MINUTE})
    active = state['active']
    if active:
        active['shares'] += bar['v']
        active['dollars'] += bar['v']*bar['vw']
        through = bar['c'] > band[1]+.02 if side == 'upper' else bar['c'] < band[0]-.02
        retreat = bar['c'] < band[0]-retreat_buffer if side == 'upper' else bar['c'] > band[1]+retreat_buffer
        if through or retreat:
            response = 'closed_through' if through else 'same_bar_touch_retreat_ambiguous' if bar['t'] == active['started_at'] else 'retreated_after_contact'
            state['last_response'] = response
            if response == 'retreated_after_contact':
                state['retreats'] += 1
            events.append({'kind': side+'_'+response, 'at': bar['t']+MINUTE, **active})
            state['active'] = None
    far = bar['h'] < band[0]-retreat_buffer if side == 'upper' else bar['l'] > band[1]+retreat_buffer
    state['away'] = state['away']+1 if far else 0
    if state['active'] is None and state['away'] >= 2:
        state['armed'] = True
    return events


def prefix_hash(rows):
    value = None
    for b in rows:
        value = digest({'prior': value, 'bar': b})
    return value


def context_hash(batch, end, retrospective, cached=None):
    day = session(end-1)
    source = {k: v for k, v in batch['source'].items() if k != 'retrieved_at'}
    base = cached if cached is not None else {'daily': [b for b in batch.get('daily', []) if session(b['t']) < day][-20:],
                   'profiles': [b for b in batch.get('profiles', []) if session(b['t']) < day]}
    return digest({'base_hash': base if isinstance(base,str) else digest(base),
                   'patterns': [r for r in batch.get('patterns', []) if clock(r['evaluated_through']) < end],
                   'source': source, 'retrospective': retrospective})


def new_state(ticker):
    return {'version': VERSION, 'method_hash': method_hash(), 'ticker': ticker, 'session': None,
            'last_t': None, 'prefix_hash': None, 'context_hash': None, 'zone': None,
            'zone_generation': 0, 'last_break': None}


def update(batch, asof, state=None, retrospective=False):
    """Full ordered prefix input; returns new state + one signal per NEW completed bar.
    Revisions fail closed; caller can explicitly start a separate replay generation.
    """
    ticker = batch['ticker']
    if not isinstance(ticker, str) or not ticker or len(ticker) > 32:
        raise ValueError('ticker required')
    source = batch['source']
    for k in ('source_id', 'provider', 'entitlement', 'observation_kind', 'adjustment'):
        if not source.get(k):
            raise ValueError('source manifest field required: '+k)
    observed = clock(source.get('retrieved_at') or source['ingested_at'])
    if asof > observed:
        raise ValueError('as_of later than retrieval')
    if source['observation_kind'] not in ('historical', 'delayed', 'realtime'):
        raise ValueError('unknown observation kind')
    for key in ('bars', 'daily', 'profiles'):
        validate_bars(batch.get(key, []))
    rows = [b for b in batch['bars'] if b['t']+MINUTE <= asof and 570 <= minute(b['t']) < 960]
    if any(b['t'] % MINUTE for b in rows):
        raise ValueError('one-minute start-aligned bars required')
    state = copy.deepcopy(state) if state else new_state(ticker)
    if state['ticker'] != ticker or state['method_hash'] != method_hash():
        raise ValueError('ticker/method mismatch; explicit new generation required')
    if state['last_t'] is not None:
        prior = [b for b in rows if b['t'] <= state['last_t']]
        if prefix_hash(prior) != state['prefix_hash']:
            raise ValueError('processed observations revised or prefix missing; explicit new generation required')
    if state['last_t'] is not None and state['context_hash'] != context_hash(batch, state['last_t']+MINUTE, retrospective):
        raise ValueError('processed context revised; explicit new generation required')
    context = {k: batch.get(k, []) for k in ('daily', 'profiles', 'patterns')}
    context['source_identity'] = {k: v for k, v in source.items() if k not in ('retrieved_at',)}
    context['retrospective'] = retrospective
    # Only past context for each signal is hashed below. Full context may grow normally.
    calendar = {}
    for b in batch.get('profiles', []):
        if 570 <= minute(b['t']) < 960:
            calendar.setdefault(session(b['t']), []).append(b)
    context_by_day = {}
    signals = []
    for index, bar in enumerate(rows):
        if state['last_t'] is not None and bar['t'] <= state['last_t']:
            continue
        end = bar['t']+MINUTE
        day = session(bar['t'])
        today = [b for b in rows[:index+1] if session(b['t']) == day]
        events = []
        if state['session'] != day:
            if state['zone']:
                events.append({'kind': 'range_session_end', 'range_id': state['zone']['id'], 'at': end})
            state.update(session=day, zone=None, last_break=None)
        elif state['last_t'] is not None and bar['t']-state['last_t'] != MINUTE:
            if state['zone']:
                events.append({'kind': 'range_invalidated_data_gap', 'range_id': state['zone']['id'], 'at': end})
            state['zone'] = None
        zone = state['zone']
        if zone:
            definition = zone['definition']
            for side in ('upper', 'lower'):
                events += boundary_step(zone['boundaries'][side], bar, definition[side], side, definition['width'])
            lb, ub = definition['lower'], definition['upper']
            boundary = 'lower' if bar['c'] <= lb[1] else 'upper' if bar['c'] >= ub[0] else None
            if boundary:
                anchor = zone['anchor']
                if anchor and anchor['side'] != boundary:
                    zone['traversals'] += 1
                    events.append({'kind': 'close_traversal_'+('up' if boundary == 'upper' else 'down'),
                                   'at': end, 'range_id': zone['id'], 'start_at': anchor['at'],
                                   'minutes': (end-anchor['at'])/MINUTE})
                if not anchor or anchor['side'] != boundary:
                    zone['anchor'] = {'side': boundary, 'at': end}
            if bar['l'] <= lb[1] and bar['h'] >= ub[0]:
                events.append({'kind': 'both_bands_same_bar_order_unknown', 'at': end})
            side = 'up' if bar['c'] > definition['upper'][1]+.02 else 'down' if bar['c'] < definition['lower'][0]-.02 else None
            zone['outside_count'] = zone['outside_count']+1 if side and side == zone['outside_side'] else 1 if side else 0
            zone['outside_side'] = side
            if zone['outside_count'] >= CONFIG['break_closes']:
                event = {'kind': 'confirmed_break_'+side, 'at': end, 'range_id': zone['id'], 'definition': definition}
                events.append(event)
                state['last_break'] = event
                state['zone'] = None
        else:
            definition = detect(today[-CONFIG['formation']:])
            if definition:
                state['zone_generation'] += 1
                zone_id = digest({'ticker': ticker, 'definition': definition, 'version': VERSION})
                formation_flow = score(today[-15:], definition, today[-16]['c'])
                formation_path = path(today[-30:], definition['width'])
                vector = [(bar['c']-definition['lower'][0])/definition['width'], formation_flow['ratio'], formation_path['signed_efficiency']]
                state['zone'] = {'id': zone_id, 'definition': definition, 'generation': state['zone_generation'],
                                 'outside_count': 0, 'outside_side': None, 'anchor': None, 'traversals': 0,
                                 'boundaries': {s: boundary_state() for s in ('upper', 'lower')},
                                 'matches_at_freeze': nearest(batch.get('patterns', []), ticker, end, vector, retrospective)}
                events.append({'kind': 'range_frozen', 'at': end, 'range_id': zone_id, 'definition': definition})
        current = state['zone']
        w5, w15 = today[-5:], today[-15:]
        consecutive5 = len(w5) == 5 and contiguous(w5)
        net5 = w5[-1]['c']-w5[0]['o'] if consecutive5 else None
        threshold = max(.02, .1*statistics.median(b['h']-b['l'] for b in today[-30:]))
        direction = 'unknown' if net5 is None else 'up' if net5 > threshold else 'down' if net5 < -threshold else 'flat'
        base = baseline(batch.get('daily', []), day)
        vol = activity(w15)
        flow, position = None, None
        classification = direction+'_no_active_range'
        if current:
            d = current['definition']
            position = (bar['c']-d['lower'][0])/d['width']
            eligible = [b for b in w15 if b['t'] >= d['frozen_at']]
            prior_bar = next((b for b in reversed(today) if eligible and b['t'] == eligible[0]['t']-MINUTE), None)
            flow = score(eligible, d, prior_bar['c'] if prior_bar else bar['c'])
            upper = current['boundaries']['upper']
            recent_upper = upper['last_contact_at'] is not None and upper['last_contact_at'] > end-5*MINUTE
            if bar['c'] > d['upper'][1]:
                classification = 'above_range_break_unconfirmed'
            elif bar['c'] < d['lower'][0]:
                classification = 'below_range_break_unconfirmed'
            elif recent_upper and upper['active']:
                classification = 'testing_ceiling'
            elif any(e['kind'] == 'upper_retreated_after_contact' for e in events):
                classification = 'retreat_after_ceiling_contact'
            elif direction == 'down' and not recent_upper:
                classification = 'drifting_lower_ceiling_untested_5m'
            elif any(e['kind'] == 'lower_retreated_after_contact' for e in events):
                classification = 'rebound_after_floor_contact'
            else:
                classification = 'rising_inside_range' if direction == 'up' else 'falling_inside_range' if direction == 'down' else 'range_chop'
        break_event = next((e for e in events if e['kind'].startswith('confirmed_break_')), None)
        if break_event:
            classification = break_event['kind']
        lag = (observed-end)/1000
        source_available = source.get('available_at')
        point_in_time = source_available is not None and clock(source_available) <= end
        freshness = 'historical' if source['observation_kind'] == 'historical' else 'delayed' if source['observation_kind'] == 'delayed' or lag > 120 else 'recent_observation'
        # Historical truth persists. This field never grants a live trading entitlement.
        if day not in context_by_day:
            context_by_day[day] = {'daily': [b for b in batch.get('daily', []) if session(b['t']) < day][-20:],
                         'profiles': [b for b in batch.get('profiles', []) if session(b['t']) < day],
                         'source_identity': context['source_identity'], 'retrospective': retrospective}
            context_by_day[day]['base_hash'] = digest({k:context_by_day[day][k] for k in ('daily','profiles')})
            context_by_day[day]['input_context_hash'] = digest(context_by_day[day])
        known_context = context_by_day[day]
        new_prefix = digest({'prior': state['prefix_hash'], 'bar': bar})
        signal = {'schema': VERSION, 'ticker': ticker, 'currency': batch.get('currency', 'USD'),
                  'as_of': end, 'session': day, 'method_hash': state['method_hash'],
                  'input_hash': digest({'prefix': new_prefix, 'context': known_context['input_context_hash']}),
                  'source': source, 'lag_seconds_at_retrieval': lag, 'freshness': freshness,
                  'point_in_time_verified': point_in_time, 'last_price': bar['c'],
                  'classification': classification, 'direction_5m': direction, 'delta_5m': net5,
                  'range_position': position, 'active_range': copy.deepcopy(current),
                  'flow_15m': flow, 'path_15m': path(w15, current['definition']['width'] if current else max(.01, max(b['h'] for b in w15)-min(b['l'] for b in w15))),
                  'activity_15m': vol, 'baseline': base,
                  'quality': {'window_bars':len(w15), 'window_contiguous':contiguous(w15),
                              'vwap_outside_ohlc_bars':sum(not b['l']<=b['vw']<=b['h'] for b in w15),
                              'vwap_policy':'retain vendor VWAP; do not clamp or infer exact volume at price'},
                  'volume_pct_adv20': 100*vol['shares']/base['adv20'] if base['adv20'] else None,
                  'same_time_rvol': rvol(w15, batch.get('profiles', []), day, calendar), 'events': events,
                  'historical_matches_mode': 'retrospective_not_point_in_time' if retrospective else 'strict_available_at',
                  'limitations': ['OHLCV not signed flow or exact volume at price', 'heuristic states, not calibrated probabilities', 'no polling or execution worker']}
        # Retrieval wall-clock changes don't generate another analytical signal.
        signal['signal_id'] = digest({k: v for k, v in signal.items() if k not in ('source', 'lag_seconds_at_retrieval', 'freshness')})
        signals.append(signal)
        state['last_t'] = bar['t']
        state['prefix_hash'] = new_prefix
        state['context_hash'] = context_hash(batch, end, retrospective, known_context['base_hash'])
    return state, signals
