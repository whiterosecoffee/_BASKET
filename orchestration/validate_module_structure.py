#!/usr/bin/env python3
"""Report modules under engines/ that lack the standard layout (MODULE_STANDARD.md).

Gaps are reported, exit 0, unless --strict. Stdlib only.
"""
from __future__ import annotations
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SECTIONS = ["Purpose", "Owner spark", "Inputs", "Outputs", "Run", "Tests", "Evidence and limits"]


def check_module(root: pathlib.Path, name: str) -> list[str]:
    mod = root / "engines" / name
    gaps = []
    readme = mod / "README.md"
    if not readme.exists():
        gaps.append("README.md")
    else:
        headings = [l.lstrip("# ").strip() for l in readme.read_text(encoding="utf-8").splitlines() if l.startswith("#")]
        gaps += ["README section: " + s for s in SECTIONS if s not in headings]
    if not (mod / "contract.json").exists():
        gaps.append("contract.json")
    if not (mod / "fixtures").is_dir():
        gaps.append("fixtures/")
    if not (mod / (name + ".py")).exists():
        gaps.append(name + ".py")
    if not (root / "tests" / ("test_" + name + ".py")).exists():
        gaps.append("tests/test_%s.py" % name)
    return gaps


def check_all(root: pathlib.Path = ROOT) -> dict[str, list[str]]:
    engines = root / "engines"
    names = sorted(p.name for p in engines.iterdir() if p.is_dir() and not p.name.startswith("__")) if engines.is_dir() else []
    return {n: g for n in names if (g := check_module(root, n))}


def main(argv: list[str]) -> int:
    gaps = check_all()
    for name, items in gaps.items():
        print("engines/%s missing: %s" % (name, "; ".join(items)))
    print("%d module(s) with gaps" % len(gaps))
    return 1 if gaps and "--strict" in argv else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
