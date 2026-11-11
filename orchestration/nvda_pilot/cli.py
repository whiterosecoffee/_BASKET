"""Explicit NVDA snapshot operations; errors are structured, never empty success."""
import argparse
import json
import os
import tempfile
from pathlib import Path
import sys
from .store import Pilot, PilotError, canonical, freeze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('freeze')
    p.add_argument('--source', required=True)
    p.add_argument('--frozen-at', required=True)
    p.add_argument('--output', required=True)
    p = sub.add_parser('stage')
    p.add_argument('--source', required=True)
    p.add_argument('--manifest', required=True)
    p = sub.add_parser('activate')
    p.add_argument('--manifest-id', required=True)
    p.add_argument('--expected-current')
    p = sub.add_parser('rollback')
    p.add_argument('--expected-current', required=True)
    p = sub.add_parser('report')
    p.add_argument('--as-of', required=True)
    p = sub.add_parser('resolve')
    p.add_argument('--instrument-id', default='NVDA')
    p.add_argument('--data-kind', choices=['observations', 'source_reports'], required=True)
    p.add_argument('--as-of', required=True)
    args = parser.parse_args()
    try:
        pilot = Pilot(args.root)
        if args.command == 'freeze':
            value = freeze(args.source, args.frozen_at)
            target = Path(args.output)
            # Manifest is sidecar metadata, never an overwrite of a source asset.
            if target.is_symlink():
                raise PilotError('UNSAFE_PATH', 'manifest output cannot be a symlink')
            if target.resolve().is_relative_to(Path(args.source).resolve()) and target.resolve() != Path(args.source).resolve() / 'SOURCE_MANIFEST.json':
                raise PilotError('UNSAFE_PATH', 'write manifest outside source or use SOURCE_MANIFEST.json')
            target.parent.mkdir(parents=True, exist_ok=True)
            staged = None
            try:
                with tempfile.NamedTemporaryFile(mode='wb', dir=target.parent, prefix='.manifest-', delete=False) as out:
                    staged = Path(out.name)
                    out.write(canonical(value) + b'\n')
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(staged, target)
            finally:
                if staged is not None:
                    staged.unlink(missing_ok=True)
        elif args.command == 'stage':
            value = pilot.stage(args.source, json.loads(Path(args.manifest).read_text()))
        elif args.command == 'activate':
            value = pilot.activate(args.manifest_id, args.expected_current)
        elif args.command == 'rollback':
            value = pilot.rollback(args.expected_current)
        elif args.command == 'resolve':
            value = pilot.resolve(args.instrument_id, args.data_kind, 'read', args.as_of)
        else:
            value = pilot.report(args.as_of)
        sys.stdout.buffer.write(canonical(value) + b'\n')
        return 0
    except (PilotError, OSError, ValueError, KeyError, TypeError) as exc:
        sys.stdout.buffer.write(canonical({'schema': 'basket.nvda_pilot_error@1', 'status': 'error',
                                         'code': getattr(exc, 'code', 'INVALID_INPUT'), 'message': str(exc)}) + b'\n')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
