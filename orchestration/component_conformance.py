"""Offline, reference-only conformance checks for the existing component boundary.

A passing check is not domain qualification or execution authorization. Callers
supply an explicit map of approved reference -> bytes. Nothing is fetched, run,
written, or imported from a manifest. Payload schemas must be self-contained
Draft 2020-12 schemas. Domain freshness, units, entitlement and effects remain
owner-specific checks; this module does not award a 'qualified' lifecycle state.
"""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry

SCHEMA = json.loads((Path(__file__).resolve().parents[1] /
                     'schemas/component-blackbox.v1.json').read_text())
FORMATS = FormatChecker()


@FORMATS.checks('date-time', raises=ValueError)
def valid_datetime(value):
    if not isinstance(value, str):
        return True
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})', value):
        return False
    offset = re.search(r'([+-])(\d{2}):(\d{2})$', value)
    if offset and (int(offset[2]) > 23 or int(offset[3]) > 59):
        return False
    return datetime.fromisoformat(value.upper().replace('Z', '+00:00')).tzinfo is not None


class ConformanceError(ValueError):
    """A declared boundary or its provided bytes disagree."""


def canonical(value):
    """Fixture serialization only; not an imposed domain output hash standard."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ConformanceError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def _nonfinite(value):
    raise ConformanceError('Nonfinite JSON value: ' + value)


def _float(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ConformanceError('Nonfinite JSON number: ' + value)
    return parsed


def _json(data):
    return json.loads(data, object_pairs_hook=_object, parse_constant=_nonfinite,
                      parse_float=_float)


def _validate(value, schema):
    # Explicit empty registry disables network retrieval, including indirect refs.
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FORMATS,
                        registry=Registry()).validate(value)


def _envelope(value, definition=None):
    schema = SCHEMA if definition is None else {
        '$schema': SCHEMA['$schema'], '$defs': SCHEMA['$defs'],
        '$ref': '#/$defs/' + definition}
    _validate(value, schema)


def _bytes(reference, artifacts):
    try:
        data = artifacts[reference['ref']]
    except KeyError as exc:
        raise ConformanceError('Reference not supplied: ' + reference['ref']) from exc
    if not isinstance(data, bytes) or digest(data) != reference['sha256']:
        raise ConformanceError('Reference bytes/hash mismatch: ' + reference['ref'])
    return data


def _local_schema(schema):
    """Inspect only schema locations, never literal const/enum/default data."""
    if not isinstance(schema, dict):
        return
    if '$schema' in schema and schema['$schema'] != SCHEMA['$schema']:
        raise ConformanceError('Only Draft 2020-12 payload schemas are supported')
    for key in ('$ref', '$dynamicRef'):
        if key in schema and (not isinstance(schema[key], str) or
                              not schema[key].startswith('#')):
            raise ConformanceError('Payload schema references must be local fragments')
    for key in ('additionalProperties', 'unevaluatedProperties', 'propertyNames',
                'contains', 'items', 'not', 'if', 'then', 'else',
                'unevaluatedItems', 'contentSchema'):
        if key in schema:
            _local_schema(schema[key])
    for key in ('$defs', 'definitions', 'properties', 'patternProperties', 'dependentSchemas'):
        for child in schema.get(key, {}).values():
            _local_schema(child)
    for key in ('allOf', 'anyOf', 'oneOf', 'prefixItems'):
        for child in schema.get(key, []):
            _local_schema(child)


def _named(items, key):
    indexed = {item[key]: item for item in items}
    if len(indexed) != len(items):
        raise ConformanceError('Duplicate declaration: ' + key)
    return indexed


def _bindings(ports, bindings, artifacts, require_ports=True):
    declared = _named(ports, 'name')
    required = {name for name, port in declared.items() if port['required']}
    if set(bindings) - set(declared) or (require_ports and required - set(bindings)):
        raise ConformanceError('Missing required or undeclared port')
    for name, binding in bindings.items():
        port = declared[name]
        if any(binding[key] != port[key] for key in ('schema_ref', 'schema_sha256')):
            raise ConformanceError('Port schema pin mismatch: ' + name)
        schema = _json(_bytes({'ref': binding['schema_ref'],
                               'sha256': binding['schema_sha256']}, artifacts))
        Draft202012Validator.check_schema(schema)
        _local_schema(schema)
        _validate(_json(_bytes(binding['artifact'], artifacts)), schema)
        for source in binding['sources']:
            _bytes(source['artifact'], artifacts)
            if source['supersedes'] is not None:
                _bytes(source['supersedes'], artifacts)


def check_exchange(manifest, call, result, artifacts, *, expected_input_sha256):
    """Check an exchange against an approved manifest and explicitly supplied bytes.

    expected_input_sha256 is computed independently using the consumer's documented
    input serialization; the common schema intentionally defines no universal one.
    Unknown/unprovided references fail, even for failure results. Input preflight
    is a separate owner responsibility; this is a post-execution exchange check.
    No adapter is invoked here.
    """
    _envelope(manifest)
    _envelope(call, 'call')
    _envelope(result, 'result')
    if manifest.get('boundary_profile') != 'qualified_refs_v1':
        raise ConformanceError('Pinned reference profile required for this helper')
    _named(manifest['inputs'], 'name')
    _named(manifest['outputs'], 'name')
    errors = _named(manifest['errors'], 'code')
    for envelope in (call, result):
        if (envelope['component_id'] != manifest['component_id'] or
                envelope['contract_version'] != manifest['version']):
            raise ConformanceError('Component identity/version mismatch')
    if any(call[key] != result[key] for key in ('run_id', 'as_of')):
        raise ConformanceError('Request/result identity mismatch')
    if result['provenance']['input_sha256'] != expected_input_sha256:
        raise ConformanceError('Input fingerprint mismatch')
    if result['provenance']['method'] != call['method']:
        raise ConformanceError('Method/config reference mismatch')
    _bytes(call['method'], artifacts)
    _bindings(manifest['inputs'], call['inputs'], artifacts)
    _bindings(manifest['outputs'], result['outputs'], artifacts,
              require_ports=result['status'] == 'ok')
    if result['error'] is not None:
        error = result['error']
        if (error['code'] not in errors or
                error['retryable'] != errors[error['code']]['retryable']):
            raise ConformanceError('Undeclared error code/retry policy')
