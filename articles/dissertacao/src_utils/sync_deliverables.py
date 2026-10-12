#!/usr/bin/env python3
"""Copy dissertation deliverables into the agent workspace, verify each by checksum, and FAIL loudly.

WHY THIS EXISTS
---------------
Twice in this project a deliverable was saved as an artifact from a STALE workspace copy, because the
`cp` that was supposed to refresh it ran with a different working directory than expected (a `cd` in
the same shell cell had moved it), so the copy landed somewhere else and the save silently promoted
the previous file. The artifact store then deduplicated it to the earlier version, which is why the
save's own echo looked normal: same size, same checksum, no error.

The second occurrence shipped a register artifact WITHOUT the section the accompanying message
promised. The failure is invisible at save time, so it has to be caught before the save.

WHAT THIS DOES
--------------
Copies each named file from the repository to the workspace using ABSOLUTE paths on both sides (never
relative, never dependent on cwd), then re-reads both and compares sha256. Any mismatch is a hard
error. Optionally asserts that a required string is present in the copied file, which is the check
that would have caught the BLOCO 0f case.

Usage:
    python3 src_utils/sync_deliverables.py --workspace /path/to/workspace
    python3 src_utils/sync_deliverables.py --workspace ... --require PENDENCIAS.md='BLOCO 0f'
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# repo-relative source -> workspace filename
DELIVERABLES = {
    "src_utils/PENDENCIAS.md": "PENDENCIAS.md",
    "src_utils/_history/_archive/PENDENCIAS_RESOLVIDOS.md": "PENDENCIAS_RESOLVIDOS.md",
    "science/AGENT_HANDOFF.md": "AGENT_HANDOFF.md",
    "src/dissertacao.pdf": "dissertacao_v3_defense.pdf",
    # main_final.pdf -> main_academico.pdf on 2026-07-29 (LATEX_UPGRADE.md §4 A-1). The
    # WORKSPACE name keeps "final" on purpose: it is what already-saved artifacts are called,
    # and renaming it would fork the artifact's version history rather than continue it.
    "src/build/main_academico.pdf": "dissertacao_v3_final.pdf",
}


def sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True, help="absolute path to the agent workspace")
    ap.add_argument("--require", action="append", default=[],
                    help="FILENAME='required substring'; asserts the substring is in the COPY")
    args = ap.parse_args()

    ws = os.path.abspath(args.workspace)
    if not os.path.isdir(ws):
        print(f"ERROR: workspace is not a directory: {ws}")
        return 1

    required: dict[str, str] = {}
    for spec in args.require:
        if "=" not in spec:
            print(f"ERROR: --require needs FILENAME='substring', got {spec!r}")
            return 1
        name, _, needle = spec.partition("=")
        required[name.strip()] = needle.strip().strip("'\"")

    rc = 0
    copied = 0
    skipped = 0
    for rel, dest_name in DELIVERABLES.items():
        src = os.path.join(REPO_ROOT, rel)
        dst = os.path.join(ws, dest_name)
        if not os.path.exists(src):
            # A MISSING SOURCE IS A FAILURE, not a skip. Until 2026-07-29 this printed SKIP and
            # left rc at 0, so with every source absent the tool printed five SKIP lines,
            # "deliverables in sync", and exit 0 while copying NOTHING into the workspace
            # (reproduced on an empty fixture repo: RC=0, 0 files in the workspace). This script
            # exists because a deliverable was saved from a stale workspace copy; a source that is
            # not there is the same failure one step earlier, and empty-result-means-pass is how
            # it stayed invisible. A stem renamed under this table (main_final -> main_academico,
            # 2026-07-29) lands here, which is precisely when it must be loud.
            print(f"  MISSING  {rel} (not present in repo) -- nothing was copied to {dest_name}")
            skipped += 1
            rc = 1
            continue
        shutil.copy2(src, dst)
        a, b = sha(src), sha(dst)
        if a != b:
            print(f"  MISMATCH {dest_name}: repo {a[:16]} vs workspace {b[:16]}")
            rc = 1
            continue
        note = ""
        if dest_name in required:
            needle = required[dest_name]
            with open(dst, encoding="utf8", errors="replace") as fh:
                body = fh.read()
            if needle not in body:
                print(f"  MISSING  {dest_name}: required text {needle!r} is not in the copy")
                rc = 1
                continue
            note = f" (contains {needle!r})"
        print(f"  OK      {dest_name}  {a[:16]}  {os.path.getsize(dst)} bytes{note}")

    print("deliverables in sync" if rc == 0 else "DELIVERABLES OUT OF SYNC -- do not save artifacts")
    return rc


if __name__ == "__main__":
    sys.exit(main())
