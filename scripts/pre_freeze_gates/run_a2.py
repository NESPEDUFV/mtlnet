"""pre_freeze_gates A2 — run the full feature-concat cell matrix via the p1 harness.

Cells: arms {hgi, hgifeat, v14} × tasks {category, region} × states × seeds, 5 folds × 30 ep.
Each cell shells out to scripts/p1_region_head_ablation.py (resume-safe). Tag encodes the cell
so JSONs are addressable by the collector. Region cells pass the seeded per-fold train-only
log_T dir (substrate-independent prior, held constant across arms).

Usage:
    python scripts/pre_freeze_gates/run_a2.py --states alabama arizona --seeds 0 1 7 100 \
        --tasks category region
    python scripts/pre_freeze_gates/run_a2.py --states florida --seeds 0 --tasks category region
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
# Use the SAME interpreter as this parent (.venv on the Mac board; conda on H100/A40 where
# there is no .venv). BASELINE_PY overrides if ever needed.
import os
PY = os.environ.get("BASELINE_PY") or sys.executable
HARNESS = str(_root / "scripts" / "p1_region_head_ablation.py")

V14 = "check2hgi_design_k_resln_mae_l0_1"

# arm -> (engine_override, region_emb_source, add_visit_features)
ARMS = {
    "hgi":     ("hgi", "hgi", False),
    "hgifeat": ("hgi", "hgi", True),
    "v14":     (V14, V14, False),
    "v11":     ("check2hgi", "check2hgi", False),  # paper-canon Check2HGI (on-disk, zero drift)
}


def cell_cmd(state, arm, task, seed, folds, epochs):
    eo, reg_src, add_feat = ARMS[arm]
    tag = f"A2_{arm}_{task}_s{seed}"
    cmd = [PY, HARNESS, "--state", state, "--heads", "next_gru" if task == "category" else "next_stan_flow",
           "--folds", str(folds), "--epochs", str(epochs), "--seed", str(seed),
           "--target", task, "--engine-override", eo, "--tag", tag]
    if task == "category":
        cmd += ["--input-type", "checkin"]
    else:  # region
        cmd += ["--input-type", "region", "--region-emb-source", reg_src,
                "--per-fold-transition-dir", f"output/check2hgi/{state.lower()}"]
    if add_feat:
        cmd += ["--add-visit-features"]
    return tag, cmd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", nargs="+", required=True)
    ap.add_argument("--seeds", nargs="+", type=int, required=True)
    ap.add_argument("--tasks", nargs="+", default=["category", "region"], choices=["category", "region"])
    ap.add_argument("--arms", nargs="+", default=list(ARMS), choices=list(ARMS))
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30)
    args = ap.parse_args()

    cells = []
    for state in args.states:
        for task in args.tasks:
            for seed in args.seeds:
                for arm in args.arms:
                    cells.append((state, arm, task, seed))
    print(f"[run_a2] {len(cells)} cells")
    for i, (state, arm, task, seed) in enumerate(cells, 1):
        tag, cmd = cell_cmd(state, arm, task, seed, args.folds, args.epochs)
        print(f"\n[run_a2] ({i}/{len(cells)}) {state} {arm} {task} seed={seed} :: {tag}", flush=True)
        r = subprocess.run(cmd, cwd=str(_root))
        if r.returncode != 0:
            print(f"[run_a2] WARN cell failed rc={r.returncode}: {tag}", flush=True)
    print("\n[run_a2] ALL CELLS DONE", flush=True)


if __name__ == "__main__":
    main()
