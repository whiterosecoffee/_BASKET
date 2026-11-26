"""Strict empty-domain request/result seam. No network, queue or filesystem writes."""
import argparse
import json
from pathlib import Path


def run(request):
    if not isinstance(request, dict) or set(request) != {"request_id", "payload"}:
        raise ValueError("request requires exactly request_id and payload")
    identity = request["request_id"]
    if not isinstance(identity, str) or not identity.strip() or len(identity) > 128:
        raise ValueError("request_id must be a nonblank string of at most 128 characters")
    if not isinstance(request["payload"], dict) or request["payload"]:
        raise ValueError("payload must be empty until domain owner extends the contract")
    return {"request_id": identity, "status": "ok", "payload": {}}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    try:
        request = json.loads(args.request.read_text(), object_pairs_hook=unique_pairs)
        print(json.dumps(run(request), sort_keys=True, separators=(",", ":")))
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, "Invalid request: " + str(error) + "\n")


if __name__ == "__main__":
    main()
