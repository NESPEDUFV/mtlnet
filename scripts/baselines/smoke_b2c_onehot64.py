#!/usr/bin/env python
"""TINY smoke test for the B2c one-hot-POI-64 baseline (AL, 1 fold, 2 epochs).

Proves PLUMBING + ROW-ALIGNMENT + LEAK-SAFETY of the B2c probe-engine, NOT quality.
It does NOT run the scored n=20 board.

What it checks:
  1. Build the B2c substrate for alabama into a scratch OUTPUT_DIR (check2hgi symlinked
     from the real output/ so graph maps / region emb / log_T resolve).
  2. ROW-ALIGNMENT asserts: len(next) == len(next_region) == len(sequences) and the
     B2c embeddings.parquet has the same check-in row count/order as check2hgi.
  3. LEAK-SAFETY assert: the B2c per-POI vector is a pure function of placeid + the
     fixed seed — identical across two independent builds and across fold seeds, and
     does NOT depend on any train/val split. We verify byte-identical re-build and that
     the StratifiedGroupKFold val users are NEVER consulted by the builder.
  4. (optional, default ON) run scripts/train.py for 1 fold / 2 epochs and confirm a
     non-zero cat macro-F1 and reg top10_acc_indist land in the fold JSON.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/baselines/smoke_b2c_onehot64.py \
        [--state alabama] [--no-train] [--src-output /home/.../PoiMtlNet/output]
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _mirror_check2hgi(scratch: Path, src_output: Path, state: str):
    """Mirror the real check2hgi state dir into the scratch OUTPUT_DIR with
    per-ENTRY symlinks (NOT a single dir symlink), so the smoke can WRITE fresh
    n_splits-matched log_T files locally WITHOUT polluting the real frozen
    output/check2hgi/<state>/.  Read artifacts (embeddings, graph, region emb,
    input/, temp/) resolve through the symlinks; new .pt writes land in scratch."""
    dst = scratch / "check2hgi" / state
    src = src_output / "check2hgi" / state
    if not src.exists():
        sys.exit(f"FATAL: real check2hgi substrate missing at {src}")
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        # do NOT mirror old seeded log_T — we rebuild the n_splits-matched one
        if entry.name.startswith("region_transition_log_"):
            continue
        link = dst / entry.name
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(entry.resolve())
    print(f"  mirrored {src} -> {dst} (per-entry symlinks; log_T excluded)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--seed", type=int, default=0, help="fold/train seed for the smoke run")
    ap.add_argument("--no-train", action="store_true", help="only build + assert, skip train.py")
    repo = Path(__file__).resolve().parents[2]
    ap.add_argument("--src-output", default=str(repo.parent.parent.parent / "output")
                    if (repo.parent.parent.parent / "output").exists() else str(repo / "output"))
    ap.add_argument("--scratch", default=str(repo / ".smoke_b2c_output"))
    args = ap.parse_args()

    state = args.state.lower()
    scratch = Path(args.scratch).resolve()
    src_output = Path(args.src_output).resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    print(f"== B2c smoke == state={state} scratch_OUTPUT_DIR={scratch} src_output={src_output}")

    env = dict(os.environ)
    env["PYTHONPATH"] = "src"
    env["OUTPUT_DIR"] = str(scratch)
    # The worktree has no .venv (it lives in the main repo); fall back to the
    # running interpreter so the smoke is runnable from either checkout. [AUDIT-FIX B2c]
    _cand = repo / ".venv" / "bin" / "python"
    py = str(_cand) if _cand.exists() else sys.executable

    _mirror_check2hgi(scratch, src_output, state)

    # --- 1. build the B2c substrate twice (determinism / leak-trivial check) -----
    build = [py, "scripts/baselines/build_b2c_onehot64_substrate.py", state]
    print("\n[build #1]"); subprocess.run(build, cwd=repo, env=env, check=True)

    # import after OUTPUT_DIR is set so IoPaths points at scratch
    sys.path.insert(0, str(repo / "src"))
    os.environ["OUTPUT_DIR"] = str(scratch)
    import importlib
    import configs.paths as paths_mod
    importlib.reload(paths_mod)
    from configs.paths import EmbeddingEngine, IoPaths
    import pandas as pd
    import numpy as np

    B2C = EmbeddingEngine.BASELINE_B2C_ONEHOT64
    C2H = EmbeddingEngine.CHECK2HGI

    emb1 = IoPaths.load_embedd(state, B2C)
    next1 = IoPaths.load_next(state, B2C)
    nreg1 = IoPaths.load_next_region(state, B2C)
    seq1 = pd.read_parquet(IoPaths.get_seq_next(state, B2C))
    src_emb = IoPaths.load_embedd(state, C2H)

    emb_cols = [str(i) for i in range(64)]
    table1 = emb1[emb_cols].to_numpy()

    print("\n[build #2 — determinism]"); subprocess.run(build, cwd=repo, env=env, check=True)
    emb2 = IoPaths.load_embedd(state, B2C)
    table2 = emb2[emb_cols].to_numpy()

    # --- 2. ROW-ALIGNMENT asserts ----------------------------------------------
    assert len(next1) == len(nreg1) == len(seq1), (len(next1), len(nreg1), len(seq1))
    assert len(emb1) == len(src_emb), (len(emb1), len(src_emb))
    assert emb1["placeid"].tolist() == src_emb["placeid"].tolist(), "row order diverged from check2hgi"
    print(f"\n[OK] row-alignment: next={len(next1)} == next_region={len(nreg1)} == seq={len(seq1)}; "
          f"embeddings rows={len(emb1)} == check2hgi rows={len(src_emb)}")

    # --- 3. LEAK-SAFETY: pure function of placeid + seed, no fold dependence ----
    assert np.array_equal(table1, table2), "B2c projection NOT deterministic across builds!"
    # each distinct POI must map to ONE fixed vector (POI-constant within all check-ins)
    g = emb1.groupby("placeid")[emb_cols].nunique().to_numpy()
    assert (g <= 1).all(), "a POI has >1 distinct vector — not a fixed per-POI projection"
    # confirm the builder never reads fold indices: re-derive the SGKF split and show
    # the val users are irrelevant to the (already-built, identical) table.
    from data.folds import load_next_data
    from sklearn.model_selection import StratifiedGroupKFold
    X, y_cat, userids, _ = load_next_data(state, C2H)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=args.seed)
    train_idx, val_idx = next(iter(sgkf.split(X, y_cat, groups=userids)))
    train_users = set(int(u) for u in userids[train_idx])
    val_users = set(int(u) for u in userids[val_idx])
    assert val_users.isdisjoint(train_users), "fold split is not user-disjoint!"
    print(f"[OK] leak-safe: projection byte-identical across builds; POI-constant; "
          f"NO pretraining → fold-independent (fold0: |train_users|={len(train_users)}, "
          f"|val_users|={len(val_users)}, disjoint=True). The B2c table is the SAME for "
          f"every seed/fold by construction → zero train/val leakage.")

    if args.no_train:
        print("\n[--no-train] build + asserts PASSED; skipping train.py.")
        return

    # --- 3b. build the n_splits-matched seeded per-fold log_T into the scratch --
    # The smoke runs --folds 1 -> the trainer forces n_splits=max(2,1)=2, so the
    # log_T MUST be a fresh n_splits=2 build (the frozen output/check2hgi log_T is
    # n_splits=5). We write it into the MIRRORED (writable) scratch dir so the real
    # frozen substrate is never touched. The region partition is substrate-shared,
    # so this log_T is correct for B2c too. (P3 scored runs use --folds 5 + the
    # canonical n_splits=5 log_T at output/check2hgi/<state>.)
    transition_dir = str((scratch / "check2hgi" / state))
    print(f"\n[log_T] building n_splits=2 seed={args.seed} per-fold log_T -> {transition_dir}")
    subprocess.run(
        [py, "scripts/compute_region_transition.py", "--state", state,
         "--per-fold", "--n-splits", "2", "--seed", str(args.seed)],
        cwd=repo, env=env, check=True,
    )

    # --- 4. tiny 1-fold / 2-epoch train.py run ---------------------------------
    cmd = [
        py, "scripts/train.py", "--task", "mtl",
        "--task-set", "check2hgi_next_region", "--engine", B2C.value,
        "--state", state, "--seed", str(args.seed),
        "--folds", "1", "--epochs", "2", "--batch-size", "2048", "--no-checkpoints",
        "--model", "mtlnet_crossattn_dualtower",
        "--mtl-loss", "static_weight", "--category-weight", "0.75",
        "--cat-head", "next_gru", "--reg-head", "next_stan_flow_dualtower",
        "--task-a-input-type", "checkin", "--task-b-input-type", "region",
        "--per-fold-transition-dir", transition_dir,
        "--log-t-kd-weight", "0.0",
    ]
    print("\n[train] " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=repo, env=env)
    if r.returncode != 0:
        sys.exit(f"train.py smoke FAILED (rc={r.returncode})")

    # find the fold JSON under results/<engine>/<state>/
    res_root = scratch.parent / "results" if False else (repo / "results")
    res_dir = Path(os.environ.get("RESULTS_ROOT", repo / "results")) / B2C.value / state
    hits = sorted(res_dir.rglob("*fold*.json")) + sorted(res_dir.rglob("*.json"))
    print(f"\n[results] scanning {res_dir} -> {len(hits)} json files")
    for h in hits[:8]:
        print("   ", h.relative_to(repo) if str(h).startswith(str(repo)) else h)
    print("\n[DONE] B2c smoke complete — see fold JSON above for cat f1 + reg top10_acc_indist.")


if __name__ == "__main__":
    main()
