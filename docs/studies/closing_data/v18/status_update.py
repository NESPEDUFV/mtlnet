#!/usr/bin/env python
"""Rewrite v18 status.json + PROGRESS.md from the per-cell sidecars on disk.

The sidecars are the source of truth: a cell is done iff its sidecar exists. This script never
invents state, so a resumed run and a fresh run produce the same picture. status.json is written
atomically (temp + rename) so a reader never sees a half-file.

Usage:  status_update.py [--phase wave1] [--blocked-on "..."] [--running-file <path>]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SIDE = REPO / "docs/results/closing_data/v18"
BASE = REPO / "docs/studies/closing_data/v18"
STATES = ["istanbul", "alabama", "arizona", "florida", "texas", "california"]
SEEDS = [0, 1, 7, 100]
FAMILIES = ["cat", "reg", "joint"]


def gpu_free_mib() -> int:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15)
        return int(out.stdout.strip().splitlines()[0])
    except Exception:
        return -1


def disk_free_gb(path: str) -> int:
    try:
        return int(shutil.disk_usage(path).free / 2**30)
    except Exception:
        return -1


def commit_sha() -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return "unknown"


def load_cells() -> list[dict]:
    cells = []
    for st in STATES:
        for sd in SEEDS:
            for fam in FAMILIES:
                p = SIDE / f"{st}_s{sd}_{fam}.json"
                c = {"state": st, "seed": sd, "family": fam, "status": "pending",
                     "wall_seconds": None, "rundir": None, "cat": None, "reg": None}
                if p.exists():
                    try:
                        d = json.loads(p.read_text())
                        c.update(status="done",
                                 wall_seconds=d.get("wall_seconds"),
                                 rundir=d.get("rundir"),
                                 cat=d.get("cat"), reg=d.get("reg"))
                    except Exception as e:                       # a truncated sidecar is a failure
                        c["status"] = "failed"
                        c["error"] = f"unreadable sidecar: {e}"
                cells.append(c)
    return cells


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="wave1")
    ap.add_argument("--blocked-on", default=None)
    ap.add_argument("--running-file", default=str(BASE / "logs/running.jsonl"))
    ap.add_argument("--verify-flags-file", default=str(BASE / "logs/verify_flags.jsonl"))
    args = ap.parse_args()

    cells = load_cells()
    done = [c for c in cells if c["status"] == "done"]

    running = []
    rf = Path(args.running_file)
    if rf.exists():
        for line in rf.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            pid = r.get("pid")
            if pid and Path(f"/proc/{pid}").exists():          # only genuinely-alive jobs
                running.append(r)

    flags = []
    vf = Path(args.verify_flags_file)
    if vf.exists():
        flags = [l for l in vf.read_text().splitlines() if l.strip()]

    # current_n counts a seed only when ALL THREE families are banked for it. Counting joint
    # alone (the pre-2026-08-11 behaviour) structurally cannot see a lagging cat or reg, so a
    # state whose joint cells were all done reported its full n while dedicated cells were
    # still missing -- observed on florida 2026-08-10, where joint s7/s100 landed but cat/reg
    # did not.
    current_n = {}
    seeds_complete = {}
    for st in STATES:
        n = 0
        complete = []
        for sd in SEEDS:
            fams = {c["family"] for c in done if c["state"] == st and c["seed"] == sd}
            if set(FAMILIES) <= fams:
                n += 1
                complete.append(sd)
        current_n[st] = n * 5                                   # 5 folds per complete seed
        seeds_complete[st] = complete

    status = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "commit_sha": commit_sha(),
        "phase": "blocked" if args.blocked_on else args.phase,
        "current_n": current_n,
        "seeds_complete": seeds_complete,
        "cells": cells,
        "running": running,
        "gpu_free_mib": gpu_free_mib(),
        "disk_free_gb": disk_free_gb("/dados"),
        "disk_free_gb_home": disk_free_gb("/home"),
        "blocked_on": args.blocked_on,
        "verify_flags": flags,
    }

    out = BASE / "status.json"
    fd, tmp = tempfile.mkstemp(dir=str(BASE), suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(status, fh, indent=2)
    os.replace(tmp, out)                                        # atomic

    # ---- PROGRESS.md ---------------------------------------------------------------------
    by = {(c["state"], c["seed"], c["family"]): c for c in cells}
    L = []
    L.append("# v18 — PROGRESS\n")
    L.append(f"> Rewritten after every completed cell. `updated_at` {status['updated_at']} · "
             f"phase **{status['phase']}** · commit `{status['commit_sha'][:8]}`\n")
    if args.blocked_on:
        L.append(f"> ⛔ **BLOCKED:** {args.blocked_on}\n")
    L.append("## Matrix — 6 states × 4 seeds × 3 families\n")
    L.append("`.` pending · `~` running · `D` done · `F` failed. Families in each cell: cat / reg / joint.\n")
    L.append("| state | " + " | ".join(f"seed {s}" for s in SEEDS) + " | n (joint) |")
    L.append("|---|" + "---|" * (len(SEEDS) + 1))
    run_keys = {(r.get("state"), r.get("seed"), r.get("family")) for r in running}
    sym = {"pending": ".", "done": "D", "failed": "F"}
    for st in STATES:
        row = [f"| {st} "]
        for sd in SEEDS:
            marks = []
            for fam in FAMILIES:
                c = by[(st, sd, fam)]
                m = "~" if (st, sd, fam) in run_keys else sym.get(c["status"], "?")
                marks.append(m)
            row.append("| " + " ".join(marks) + " ")
        row.append(f"| {current_n[st]} |")
        L.append("".join(row))
    L.append("")

    walls = [c["wall_seconds"] for c in done if c["wall_seconds"]]
    if walls:
        L.append("## Timing\n")
        L.append(f"- cells done: **{len(done)} / {len(cells)}**")
        L.append(f"- measured wall-clock total: **{sum(walls)/3600:.2f} h**")
        for fam in FAMILIES:
            w = [c["wall_seconds"] for c in done if c["family"] == fam and c["wall_seconds"]]
            if w:
                L.append(f"- {fam}: n={len(w)}, mean {sum(w)/len(w)/60:.1f} min, "
                         f"max {max(w)/60:.1f} min")
        remaining = len(cells) - len(done)
        if walls and remaining:
            L.append(f"- naive estimate for the remaining {remaining} cells (serial): "
                     f"**{remaining * (sum(walls)/len(walls)) / 3600:.1f} h**")
        L.append("")

    if running:
        L.append("## Running now\n")
        for r in running:
            L.append(f"- {r.get('state')} s{r.get('seed')} {r.get('family')} "
                     f"(pid {r.get('pid')}, since {r.get('started_at')})")
        L.append("")

    if flags:
        L.append("## [VERIFY] flags — open\n")
        for f in flags:
            L.append(f"- {f}")
        L.append("")

    L.append(f"## Environment\n")
    L.append(f"- GPU free: {status['gpu_free_mib']} MiB · /dados free: {status['disk_free_gb']} GB "
             f"· /home free: {status['disk_free_gb_home']} GB\n")
    (BASE / "PROGRESS.md").write_text("\n".join(L) + "\n")
    print(f"[status] {len(done)}/{len(cells)} cells done · phase={status['phase']} "
          f"· running={len(running)}")


if __name__ == "__main__":
    main()
