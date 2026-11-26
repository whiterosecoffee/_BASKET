"""Compare tracked Basket paths and blob identities at two explicit Git revisions."""

import argparse
from collections import Counter
import json
import subprocess


def git(repository, *arguments):
    return subprocess.check_output(["git", "-C", repository, *arguments])


def tree(repository, revision):
    pin = git(repository, "rev-parse", "--verify", f"{revision}^{{commit}}").decode().strip()
    entries = {}
    for record in git(repository, "ls-tree", "-r", "-z", pin).split(b"\0"):
        if record:
            metadata, path = record.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split()
            entries[path.decode("utf-8", errors="surrogateescape")] = (mode, kind, oid)
    return pin, entries


def compare(source, target):
    target_blobs = {entry for entry in target.values() if entry[1] == "blob"}
    rows = []
    for path, entry in sorted(source.items()):
        target_entry = target.get(path)
        if entry == target_entry:
            disposition = "same_path_same_object"
        elif entry in target_blobs:
            disposition = "same_blob_at_other_path"
        elif target_entry is not None:
            disposition = "same_path_different_object"
        else:
            disposition = "no_exact_match"
        rows.append({"path": path, "mode": entry[0], "kind": entry[1],
                     "source_object": entry[2], "disposition": disposition})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("basket_repo")
    parser.add_argument("basket_revision")
    parser.add_argument("patterns_repo")
    parser.add_argument("patterns_revision")
    args = parser.parse_args()
    basket_pin, basket = tree(args.basket_repo, args.basket_revision)
    patterns_pin, patterns = tree(args.patterns_repo, args.patterns_revision)
    rows = compare(basket, patterns)
    report = {
        "basket_revision": basket_pin,
        "patterns_revision": patterns_pin,
        "basket_paths": len(basket),
        "patterns_paths": len(patterns),
        "counts": dict(Counter(row["disposition"] for row in rows)),
        "rows": rows,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
