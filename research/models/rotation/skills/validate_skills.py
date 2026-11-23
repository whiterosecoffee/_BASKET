"""Validate skills against the Agent Skills format (agentskills.io; Microsoft Learn: name <=64 [a-z0-9-] matching the folder, description <=1024,
SKILL.md body < 500 lines, relative references exist). Exit 1 on any failure."""
from __future__ import annotations

import re
import sys
from pathlib import Path

NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def parse(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing YAML frontmatter")
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z-]+:", line):
            key, _, v = line.partition(":")
            fm[key] = v.strip()
        elif key and line.startswith("  "):
            fm[key] = (fm[key] + " " + line.strip()).strip() if fm[key] else line.strip()
    return fm, m.group(2)


def check(skill_dir: Path) -> list[str]:
    errs, f = [], skill_dir / "SKILL.md"
    if not f.exists():
        return [f"{skill_dir.name}: SKILL.md missing"]
    try:
        fm, body = parse(f.read_text())
    except ValueError as e:
        return [f"{skill_dir.name}: {e}"]
    n, d = fm.get("name", ""), fm.get("description", "")
    if not NAME.match(n) or len(n) > 64:
        errs.append(f"{skill_dir.name}: bad name {n!r}")
    if n != skill_dir.name:
        errs.append(f"{skill_dir.name}: name {n!r} must match directory")
    if not d or len(d) > 1024:
        errs.append(f"{skill_dir.name}: description empty or over 1024 characters ({len(d)})")
    if not re.search(r"\bUse when\b", d):
        errs.append(f"{skill_dir.name}: description should say when to use it")
    for k in fm:
        if k not in ALLOWED:
            errs.append(f"{skill_dir.name}: unknown frontmatter key {k!r}")
    if len(body.splitlines()) >= 500:
        errs.append(f"{skill_dir.name}: body is 500 lines or more")
    for ref in re.findall(r"`(references/[^`\s]+)`", body):
        if not (skill_dir / ref).exists():
            errs.append(f"{skill_dir.name}: missing {ref}")
    return errs


def main(root: Path) -> int:
    dirs = sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith((".", "__")))
    errs = [e for d in dirs for e in check(d)]
    if len(dirs) > 10:
        errs.append(f"{len(dirs)} skills advertised; keep at most 10 for reliable selection")
    print(f"{len(dirs)} skills checked, {len(errs)} problems")
    for e in errs:
        print(" -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(Path(__file__).resolve().parent))
