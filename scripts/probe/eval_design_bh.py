"""Evaluate Designs B and H once training artifacts are ready.

Drives:
  1. Build next.parquet for both engines (cat input).
  2. Launch cat STL (next_gru) AL+AZ × {B, H}.
  3. Launch reg STL (next_getnext_hard) AL+AZ × {B, H}.
  4. Run generality probes incl. new substrates.
  5. Extract per-fold metrics, run paired tests.
  6. Update results table in `docs/studies/merge_design/MERGE_DESIGN_NOTES.md`.

Designed to be invoked once training is complete:
    python scripts/probe/eval_design_bh.py --designs B H

Each {state, design} cell is a separate subprocess; runs in parallel.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))


ENGINE_MAP = {
    "B": "check2hgi_design_b",
    "H": "check2hgi_design_h",
    "I": "check2hgi_design_i",
    "J": "check2hgi_design_j",
    "M": "check2hgi_design_m",
}


def build_inputs(designs: list[str], states: list[str]) -> None:
    from configs.paths import EmbeddingEngine
    from data.inputs.builders import generate_next_input_from_checkins

    for d in designs:
        engine = EmbeddingEngine(ENGINE_MAP[d])
        for st in states:
            print(f"[build_inputs] {d}/{st}")
            generate_next_input_from_checkins(st, engine)


def launch_cat_runs(designs: list[str], states: list[str], log_dir: Path) -> list[subprocess.Popen]:
    procs = []
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": "src",
        "DATA_ROOT": str(REPO.parents[2]),
        "OUTPUT_DIR": str(REPO / "output"),
        "PYTORCH_MPS_HIGH_WATERMARK_RATIO": "0.0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    })
    for d in designs:
        engine_name = ENGINE_MAP[d]
        for st in states:
            tag = f"{st}_{d}_cat"
            log = log_dir / f"{tag}.log"
            cmd = [
                "python3", "-u", "scripts/train.py",
                "--task", "next", "--state", st, "--engine", engine_name,
                "--model", "next_gru", "--folds", "5", "--epochs", "50",
                "--seed", "42", "--no-checkpoints",
            ]
            print(f"[cat] launching {tag}")
            f = open(log, "w")
            p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
            procs.append((p, f, tag))
    return procs


def launch_reg_runs(designs: list[str], states: list[str], log_dir: Path) -> list[subprocess.Popen]:
    procs = []
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": "src",
        "DATA_ROOT": str(REPO.parents[2]),
        "OUTPUT_DIR": str(REPO / "output"),
        "PYTORCH_MPS_HIGH_WATERMARK_RATIO": "0.0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    })
    for d in designs:
        engine_name = ENGINE_MAP[d]
        for st in states:
            upst = st.upper()
            tag = f"{st}_{d}_reg"
            log = log_dir / f"{tag}.log"
            run_tag = f"STL_{upst}_design_{d.lower()}_reg_gethard_pf_5f50ep_leakfree"
            cmd = [
                "python3", "-u", "scripts/p1_region_head_ablation.py",
                "--state", st, "--heads", "next_getnext_hard",
                "--folds", "5", "--epochs", "50", "--seed", "42",
                "--input-type", "region",
                "--region-emb-source", engine_name,
                "--override-hparams", "d_model=256", "num_heads=8",
                f"transition_path=output/check2hgi/{st}/region_transition_log_seed42_fold1.pt",
                "--per-fold-transition-dir", f"output/check2hgi/{st}",
                "--tag", run_tag,
            ]
            print(f"[reg] launching {tag} (run_tag={run_tag})")
            f = open(log, "w")
            p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
            procs.append((p, f, tag))
    return procs


def wait_all(procs):
    bad = []
    for p, f, tag in procs:
        rc = p.wait()
        f.close()
        if rc != 0:
            bad.append((tag, rc))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--designs", nargs="+", default=["B", "H"])
    ap.add_argument("--states", nargs="+", default=["alabama", "arizona"])
    args = ap.parse_args()

    log_dir = REPO / "logs" / "design_bh_eval"
    log_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 64); print("STAGE 1 — build next.parquet"); print("=" * 64)
    build_inputs(args.designs, args.states)

    print("\n" + "=" * 64); print("STAGE 2 — launch cat + reg in parallel"); print("=" * 64)
    cat_procs = launch_cat_runs(args.designs, args.states, log_dir)
    reg_procs = launch_reg_runs(args.designs, args.states, log_dir)

    print(f"\n  {len(cat_procs)} cat + {len(reg_procs)} reg = {len(cat_procs)+len(reg_procs)} runs")
    print("  waiting for completion...")

    bad_cat = wait_all(cat_procs)
    bad_reg = wait_all(reg_procs)

    if bad_cat:
        print("\n  ⚠ cat failures:", bad_cat)
    if bad_reg:
        print("\n  ⚠ reg failures:", bad_reg)

    print("\n" + "=" * 64); print("STAGE 3 — generality probes"); print("=" * 64)
    subs = ["canonical", "hgi"] + [f"design_{d.lower()}" for d in args.designs]
    subprocess.run(
        ["python3", "scripts/probe/generality_probes.py",
         "--states"] + args.states + ["--substrates"] + subs,
        env={**os.environ, "PYTHONPATH": "src"},
    )

    print("\nDone. See logs/design_bh_eval/ + results/check2hgi_design_*/ + paired_tests/.")


if __name__ == "__main__":
    main()
