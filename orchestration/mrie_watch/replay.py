"""Reconcile a frozen scope against canonical identities without network/writes."""
import argparse
import json
from pathlib import Path
from orchestration.mrie_watch.watch import canonical_bytes, load_dispatcher, reconcile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dispatcher', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--tickers', required=True)
    parser.add_argument('--as-of', required=True)
    args = parser.parse_args()
    dispatcher = load_dispatcher(args.dispatcher)
    result = reconcile(dispatcher, json.loads(Path(args.manifest).read_text()),
                       dispatcher.discover(args.tickers), {}, args.as_of, [], [])
    print(canonical_bytes(result).decode(), end='')


if __name__ == '__main__':
    main()
