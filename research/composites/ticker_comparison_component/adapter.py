"""A thin offline boundary over existing B17 calculations, never a second engine."""
import json
from pathlib import Path
from types import ModuleType

from jsonschema import Draft202012Validator
from orchestration import component_conformance as cc

HERE = Path(__file__).resolve().parent
# Exact reviewed domain code. Refuse different bytes before executing either file.
DEPENDENCIES = {
    'compare': ('37f6bfe0ef8cc243cfe319526cc7471bc0b77f5f',
                '606037595bdc3e8252b80cf5e088477e21e3a32d558421a297cf403c690ccbc3'),
    'context': ('1517dc3cf549c4e2dd7695781bf01485b9dc6db6',
                '6c27025681566b5c6a101402f708bedb79ba1d20c1db9d2ffe6e6bf6f1c459d2'),
}


def run(request, *, compare_path, context_path, run_id, generated_at):
    """Return (manifest, call, result, supplied_bytes) for local authorized sources.

    Structural requests fail before execution. Semantically invalid history returns
    declared invalid_history. Dependency mismatch fails before any import. No code
    path or command is ever taken from request, component manifest or artifact refs.
    generated_at is caller-supplied execution time, separate from evaluation cutoff.
    """
    manifest = json.loads((HERE / 'component.json').read_bytes())
    artifacts = {name: (HERE / name).read_bytes()
                 for name in ('request.schema.json', 'comparison.schema.json')}
    request_schema = json.loads(artifacts['request.schema.json'])
    Draft202012Validator(request_schema, format_checker=cc.FORMATS).validate(request)
    # Canonical round-trip freezes caller input before running borrowed functions.
    request_bytes = cc.canonical(request)
    request = json.loads(request_bytes)
    sources = {'compare': Path(compare_path).read_bytes(),
               'context': Path(context_path).read_bytes()}
    for name, data in sources.items():
        if cc.digest(data) != DEPENDENCIES[name][1]:
            raise ValueError('Unapproved ' + name + ' dependency bytes')
    modules = {}
    for name, data in sources.items():
        module = ModuleType('basket_component_' + name)
        # Execute the exact verified bytes; no second filesystem read/bytecode cache.
        module.__file__ = str(compare_path if name == 'compare' else context_path)
        exec(compile(data, module.__file__, 'exec'), module.__dict__)
        modules[name] = module

    def reference(name, data):
        artifacts[name] = data
        return {'ref': name, 'sha256': cc.digest(data)}

    def binding(name, data, record_type, unit):
        port = next(p for p in manifest['inputs'] + manifest['outputs'] if p['name'] == name)
        ref = reference(name + '.json', data)
        return dict(schema_ref=port['schema_ref'], schema_sha256=port['schema_sha256'],
                    artifact=ref, sources=[dict(
            source_id=request['source']['id'], artifact=ref, record_type=record_type,
            subject_id='NVDA,CRWV,SMH,QQQ', observed_at=None, available_at=None,
            ingested_at=None, effective_at=None, published_at=None,
            period='through ' + request['cutoff'], session='RTH', unit=unit,
            currency='USD', freshness='not_applicable',
            entitlement=request['source']['entitlement'], supersedes=None)])

    methods = {name: dict(commit=DEPENDENCIES[name][0],
                          artifact=reference(name + '.py', data))
               for name, data in sources.items()}
    methods['adapter'] = reference('adapter.py', Path(__file__).read_bytes())
    method = reference('method.json', cc.canonical(methods))
    inputs = {'request': binding('request', request_bytes,
        'scenario' if request['source']['kind'] == 'synthetic' else 'aggregate_bar',
        'split_adjusted_close')}
    call = dict(contract='basket.component_call@1', component_id=manifest['component_id'],
                contract_version=manifest['version'], run_id=run_id,
                as_of=request['evaluated_at'], inputs=inputs, method=method,
                options=dict(offline=True, seed=None))
    outputs, error = {}, None
    try:
        output = modules['compare'].compare(
            request['rows'], request['cutoff'], request['evaluated_at'],
            modules['context'].change, windows=request['windows'],
            correlation_window=request['correlation_window'])
        outputs['comparison'] = binding('comparison', cc.canonical(output),
                                        'model_output', 'percent_and_correlation')
    except (ValueError, OverflowError, OSError) as exc:
        error = dict(code='invalid_history', message=str(exc), retryable=False)
    result = dict(contract='basket.component_result@1', component_id=manifest['component_id'],
        contract_version=manifest['version'], run_id=run_id, as_of=call['as_of'],
        status='error' if error else 'ok', outputs=outputs,
        provenance=dict(input_sha256=cc.digest(request_bytes), method=method,
                        code_sha=DEPENDENCIES['compare'][0], generated_at=generated_at),
        quality=dict(freshness='not_applicable', missing_inputs=[], conflicts=[],
                     warnings=['Historical current-revision diagnostic, not live or PIT qualified.',
                               'Source rights and split-adjustment basis are caller assertions.']),
        error=error)
    # Shared validator owns envelope/port/hash checks; no duplicate checker here.
    cc.check_exchange(manifest, call, result, artifacts,
                      expected_input_sha256=cc.digest(request_bytes))
    return manifest, call, result, artifacts
