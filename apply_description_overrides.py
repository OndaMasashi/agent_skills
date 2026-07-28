#!/usr/bin/env python3
"""Re-apply local description overrides to SKILL.md files.

Some skills' frontmatter `description` was locally enhanced (Japanese trigger
phrases + sibling-boundary negative triggers) for firing accuracy in a Japanese
environment. Most of those skills are upstream-derived, so a future upstream
sync may overwrite the description. Run this script after such a sync to
re-apply the local overrides recorded in `description_overrides.json`.

It replaces ONLY the frontmatter `description` entry with a YAML block scalar
(`description: |` + one indented line). All other frontmatter keys and the whole
body are preserved byte-for-byte. Output is UTF-8 WITHOUT BOM.

Usage:
  python apply_description_overrides.py            # dry-run (show plan)
  python apply_description_overrides.py --apply    # write changes
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OVERRIDES = os.path.join(ROOT, "description_overrides.json")
BOM = b"\xef\xbb\xbf"
INDENT = "  "
BLOCK_INDICATORS = ("", "|", ">", "|-", ">-", "|+", ">+")
APPLY = "--apply" in sys.argv


def splice_description(path, new_desc):
    """Return (new_bytes, changed_bool). Replaces the description block only."""
    raw = open(path, "rb").read()
    if raw.startswith(BOM):
        raw = raw[len(BOM):]
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)

    def bare(i):
        return lines[i].rstrip("\r\n")

    if not lines or bare(0) != "---":
        raise ValueError(f"{path}: no opening '---'")
    close = next((i for i in range(1, len(lines)) if bare(i) == "---"), None)
    if close is None:
        raise ValueError(f"{path}: no closing '---'")
    di = next((i for i in range(1, close) if bare(i).startswith("description:")), None)
    if di is None:
        raise ValueError(f"{path}: no 'description:' key")

    val = bare(di)[len("description:"):].strip()
    is_block = val in BLOCK_INDICATORS or val.startswith(("|", ">"))
    if is_block:
        dj = di + 1
        while dj < close and (bare(dj) == "" or bare(dj).startswith((" ", "\t"))):
            dj += 1
    else:
        dj = di + 1

    eol = "\r\n" if lines[di].endswith("\r\n") else ("\n" if lines[di].endswith("\n") else "\r\n")
    nd = new_desc.strip().replace("\r", " ").replace("\n", " ")
    newblock = [f"description: |{eol}", f"{INDENT}{nd}{eol}"]
    newlines = lines[:di] + newblock + lines[dj:]
    out = "".join(newlines).encode("utf-8")
    return out, (out != open(path, "rb").read())


def main():
    data = json.load(open(OVERRIDES, encoding="utf-8"))
    overrides = data["overrides"]
    changed = kept = missing = 0
    for skill, info in sorted(overrides.items()):
        path = os.path.join(ROOT, *info["folder"].split("/"), "SKILL.md")
        if not os.path.isfile(path):
            print(f"  MISSING  {skill}  ({path})")
            missing += 1
            continue
        out, diff = splice_description(path, info["new_description"])
        if diff:
            changed += 1
            print(f"  {'APPLY' if APPLY else 'WOULD-APPLY'}  {skill}")
            if APPLY:
                open(path, "wb").write(out)
        else:
            kept += 1
    print(f"\n{'APPLIED' if APPLY else 'DRY-RUN'}: changed={changed} unchanged={kept} missing={missing} total={len(overrides)}")


if __name__ == "__main__":
    main()
