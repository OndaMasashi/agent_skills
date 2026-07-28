#!/usr/bin/env python3
"""Validate every skills/*/SKILL.md frontmatter.

Guards against the 2026-02/04 breakage class where a batch edit wrote a UTF-8
BOM and/or dropped the YAML frontmatter, silently disabling skill firing.

Checks per SKILL.md:
  1. No UTF-8 BOM (EF BB BF) at the start — a BOM makes the frontmatter parser
     fail, so `description` never reaches the system prompt.
  2. Frontmatter present: file starts with `---`, has a closing `---`, and
     contains both `name:` and `description:` keys.
  3. `name` matches the folder name (warning only — upstream skills sometimes
     intentionally differ, e.g. vercel-* / *-node).

Exit code 0 = all good; 1 = at least one BLOCK-level problem (BOM / missing fm).
Run after any bulk edit of SKILL.md files, or wire into a pre-commit hook.

Usage:  python validate_skill_frontmatter.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BOM = b"\xef\xbb\xbf"
# Directories that are not skills (no firing frontmatter expected).
SKIP_DIRS = {"template", ".claude-plugin", "node_modules", "spec", ".git"}

block = []   # fatal: BOM or missing frontmatter -> disables firing
warn = []    # non-fatal: name/folder mismatch

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    if "SKILL.md" not in filenames:
        continue
    full = os.path.join(dirpath, "SKILL.md")
    rel = os.path.relpath(full, ROOT).replace("\\", "/")
    folder = os.path.basename(dirpath)
    raw = open(full, "rb").read()

    if raw.startswith(BOM):
        block.append(f"{rel}: UTF-8 BOM at start (breaks frontmatter parsing)")
        raw = raw[len(BOM):]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        block.append(f"{rel}: not valid UTF-8")
        continue

    lines = [l.rstrip("\r") for l in text.split("\n")]
    if not lines or lines[0].strip() != "---":
        block.append(f"{rel}: no opening '---' frontmatter delimiter")
        continue
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        block.append(f"{rel}: frontmatter never closed with '---'")
        continue
    inner = "\n".join(lines[1:close])
    name_m = re.search(r"(?m)^name:\s*(.+?)\s*$", inner)
    if not name_m:
        block.append(f"{rel}: missing 'name:' in frontmatter")
    # matches inline text and block scalars ('description: |' / '>')
    if not re.search(r"(?m)^description:\s*\S", inner):
        block.append(f"{rel}: missing/empty 'description:' in frontmatter")
    if name_m:
        name = name_m.group(1).strip().strip('"').strip("'")
        if name != folder:
            warn.append(f"{rel}: name '{name}' != folder '{folder}'")

total = sum(1 for dp, dn, fn in os.walk(ROOT) if "SKILL.md" in fn)
print(f"Scanned SKILL.md files (excluding {sorted(SKIP_DIRS)})")
if block:
    print(f"\nBLOCK ({len(block)}) — these skills will NOT fire:")
    for b in block:
        print(f"  ✗ {b}")
if warn:
    print(f"\nWARN ({len(warn)}) — name/folder mismatch (usually harmless):")
    for w in warn:
        print(f"  ! {w}")
if not block and not warn:
    print("\nAll SKILL.md frontmatter valid. ✓")
elif not block:
    print("\nNo blocking problems. ✓ (warnings only)")

sys.exit(1 if block else 0)
