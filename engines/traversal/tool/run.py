"""Command-line wrapper for the B06 read-only traversal tool."""
import argparse
import json
from pathlib import Path
from .tool import run


def main():
    p = argparse.ArgumentParser(description="Provenance-gated traversal readout")
    p.add_argument("--input", required=True, help="Path to request JSON")
    p.add_argument("--mode", default="historical", choices=("historical", "current"))
    args = p.parse_args()
    result = run(json.loads(Path(args.input).read_text(encoding="utf-8")), args.mode)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result["status"] == "blocked_current" else 0


if __name__ == "__main__":
    raise SystemExit(main())
