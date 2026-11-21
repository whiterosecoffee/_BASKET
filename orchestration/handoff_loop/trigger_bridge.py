"""Fail-closed live boundary and explicitly simulated trigger-binding contract."""
from .core import digest, require
from .dry_run import deliver_supplied, identifier, validate_checkpoint
from .github_readonly import endpoints, finite
from .synthetic_adapter import load_json, shape
from pathlib import Path

MISSING_INTERFACES = (
    'authenticated current invocation with stable original run ID and target binding',
    'authoritative current owner/session/environment observation',
    'authoritative exclusive lease/fence observation and expiry',
)


def admit_live_trigger(checkpoint_path, invocation=None):
    """No authoritative provider port exists in this increment. No file is opened.

    Forwarded prompts, automation configuration and caller-supplied IDs/booleans
    cannot enable this boundary. Do not replace this with caller `verified=True`.
    """
    return dict(schema='basket.handoff_trigger_admission@0.1-draft', status='blocked',
                reason='authoritative trigger/ownership/lease interface unavailable',
                missing_interfaces=list(MISSING_INTERFACES), actual_trigger_verified=False,
                ownership_verified=False, lease_verified=False, dispatch_authorized=False,
                checkpoint_written=False, effective_decisions=0)


def checkpoint_binding(state):
    validate_checkpoint(state)
    return digest({key:state[key] for key in ('schema','disposable','harness_id','head','implementation')})


def simulate_binding(pins, trigger, owner, lease, *, now, max_age=300):
    """Validate proposed fixture contracts only. This does not authenticate inputs."""
    shape(pins, 'provider automation_id target_session environment_id owner_id lease_id lease_fence checkpoint_id checkpoint_binding head')
    shape(trigger, 'mode provider automation_id original_run_id delivery_id target_session environment_id checkpoint_id checkpoint_binding head scheduled_for issued_at observed_at')
    shape(owner, 'mode source_id owner_id target_session environment_id head active observed_at')
    shape(lease, 'mode source_id lease_id owner_id target_session environment_id checkpoint_id checkpoint_binding head exclusive fence observed_at expires_at')
    require(finite(now) and finite(max_age) and max_age > 0, 'invalid clock/freshness bound')
    endpoints(pins['head'])
    require(pins['provider'] == 'fixture-scheduler', 'unsupported simulated provider')
    for key in ('automation_id','target_session','environment_id','owner_id','lease_id','checkpoint_id'):
        identifier(pins[key])
    require(type(pins['checkpoint_binding']) is str and len(pins['checkpoint_binding']) == 64 and all(c in '0123456789abcdef' for c in pins['checkpoint_binding']), 'invalid checkpoint binding')
    for record in (trigger, owner, lease):
        require(record['mode'] == 'simulated', 'only explicitly simulated evidence supported')
        require(finite(record['observed_at']) and 0 <= now-record['observed_at'] <= max_age, 'stale/future observation')
        for key in ('target_session','environment_id','head'):
            require(record[key] == pins[key], 'target binding mismatch')
    for key in ('provider','automation_id','checkpoint_id','checkpoint_binding'):
        require(trigger[key] == pins[key], 'trigger binding mismatch')
    for key in ('owner_id',):
        require(owner[key] == pins[key], 'owner mismatch')
    for key in ('lease_id','owner_id','checkpoint_id','checkpoint_binding'):
        require(lease[key] == pins[key], 'lease binding mismatch')
    for key in ('original_run_id','delivery_id'):
        identifier(trigger[key])
    for record in (owner,lease):
        require(type(record['source_id']) is str and record['source_id'].startswith('synthetic://') and len(record['source_id']) > len('synthetic://'), 'synthetic evidence source required')
    require(owner['active'] is True and lease['exclusive'] is True, 'active exclusive owner required')
    require(type(lease['fence']) is int and lease['fence'] > 0, 'positive lease fence required')
    require(type(pins['lease_fence']) is int and pins['lease_fence'] > 0 and lease['fence'] == pins['lease_fence'], 'lease fence mismatch')
    require(finite(lease['expires_at']) and lease['observed_at'] <= now < lease['expires_at'], 'lease expired/invalid')
    require(finite(trigger['scheduled_for']) and finite(trigger['issued_at']) and trigger['scheduled_for'] <= trigger['issued_at'] <= trigger['observed_at'] <= now and now-trigger['scheduled_for'] <= max_age, 'stale/inconsistent trigger time')
    identity = {key:trigger[key] for key in ('provider','automation_id','original_run_id','target_session','environment_id','checkpoint_id','checkpoint_binding','head')}
    # Delivery IDs change across retries; original run identity must not.
    wake = dict(id='trigger-'+digest(identity)[:56],head=pins['head'],scheduled_for=trigger['scheduled_for'])
    return dict(schema='basket.handoff_trigger_binding_simulation@0.1-draft',mode='simulated',
                identity=identity,wake=wake,lease_fence=lease['fence'],input_digest=digest([pins,trigger,owner,lease]),
                actual_trigger_verified=False,ownership_verified=False,lease_verified=False,dispatch_authorized=False)


def deliver_simulated_trigger(path, pins, trigger, owner, lease, responses, *, now, expected_digest):
    """Alternative fixture evidence only; explicitly not connected to live events."""
    binding = simulate_binding(pins,trigger,owner,lease,now=now)
    state = load_json(Path(path).read_text(encoding='utf-8'))
    require(state['harness_id'] == pins['checkpoint_id'] and checkpoint_binding(state) == pins['checkpoint_binding'], 'wrong disposable checkpoint')
    result = deliver_supplied(path,binding['wake'],responses,expected_digest=expected_digest,now=now)
    return dict(mode='simulated',binding=binding,result=result,actual_trigger_verified=False,dispatch_authorized=False)
