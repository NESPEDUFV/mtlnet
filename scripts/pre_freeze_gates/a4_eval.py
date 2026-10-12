"""A4 transductivity bound — evaluate the TRAIN-ONLY substrate, fold-matched, vs full-corpus v14.

For each fold f: build the region-sequence input from the GEOID-remapped train-only region
embeddings (scripts/pre_freeze_gates/a4_build.py output), then train next_stan_flow on the train
split and evaluate Acc@10 on the val split — using the SAME per-fold seeded train-only log_T and
the SAME StratifiedGroupKFold(seed) split the full-corpus v14 reg arm used (A2). The delta in
val Acc@10 (full-corpus − train-only) is the transductive inflation.

Reuses the validated harness internals (_train_single_task, graph maps, region-sequence build) so
the only thing that differs from the A2 v14 reg cell is the substrate's training corpus.

Usage:
    python scripts/pre_freeze_gates/a4_eval.py --state florida --seed 0 --folds 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "scripts"))

from configs.paths import EmbeddingEngine, IoPaths
from data.folds import load_next_data
from data.log_t_freshness import assert_log_t_fresh
import p1_region_head_ablation as H
from pre_freeze_gates.a2_collect import per_fold_metric

A4_DIR = _root / "results" / "pre_freeze_gates" / "a4"
WINDOW = 9


def build_region_seq_from_emb(state, region_emb):
    """Replicate H._build_region_sequence_tensor but with an explicit region_emb array."""
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, EmbeddingEngine.CHECK2HGI))
    placeid_to_idx, poi_to_region = H._load_graph_maps(state)
    dim = region_emb.shape[1]
    n = len(seq_df)
    out = np.zeros((n, WINDOW, dim), dtype=np.float32)
    for i in range(WINDOW):
        placeids = seq_df[f"poi_{i}"].astype(np.int64).to_numpy()
        mask = placeids != -1
        valid = placeids[mask]
        poi_idx = pd.Series(valid).map(placeid_to_idx).to_numpy(dtype=np.int64)
        region_idx = poi_to_region[poi_idx]
        out[np.where(mask)[0], i, :] = region_emb[region_idx]
    return torch.from_numpy(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=2048)
    args = ap.parse_args()
    state_lc = args.state.lower()

    # Canonical labels / split basis (identical to the harness).
    _, y_cat, userids, _ = load_next_data(args.state, EmbeddingEngine.CHECK2HGI)
    _, y_region_t, _, _, _, n_regions, last_region_t = H._load_checkin_region_data(args.state)
    y_region = y_region_t
    sgkf = StratifiedGroupKFold(n_splits=max(2, args.folds), shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(np.zeros(len(y_cat)), y_cat, groups=userids))[:args.folds]

    logt_dir = _root / "output" / "check2hgi" / state_lc
    # Full-corpus v14 region embeddings (the comparand) — trained per fold on the SAME device here so
    # the delta is device-pure (NOT compared against the separately-run A2 MPS number).
    def _read_region_emb(path):
        # harness schema: region_id + reg_*; sort by region_id so row == region index.
        df = pd.read_parquet(path)
        cols = [c for c in df.columns if c.startswith("reg_")]
        if "region_id" in df.columns:
            df = df.sort_values("region_id").reset_index(drop=True)
        return df[cols].to_numpy(dtype=np.float32)

    full_region_emb = _read_region_emb(
        _root / "output" / "check2hgi_design_k_resln_mae_l0_1" / state_lc / "region_embeddings.parquet")

    def _eval_fold(region_emb, train_idx, val_idx, f):
        x_region = build_region_seq_from_emb(args.state, region_emb)
        logt = logt_dir / f"region_transition_log_seed{args.seed}_fold{f + 1}.pt"
        # Stale-log_T freshness preflight (CLAUDE.md hard rule; shared portable util).
        # logt_dir here is the check2hgi substrate dir, so the parquet it derives from
        # is logt_dir/input/next_region.parquet (the util's default).
        assert_log_t_fresh(logt, state=state_lc, seed=args.seed, n_splits=max(2, args.folds))
        m = H._train_single_task(
            "next_stan_flow", x_region, y_region, train_idx, val_idx,
            emb_dim=region_emb.shape[1], n_classes=n_regions,
            epochs=args.epochs, batch_size=args.batch_size, seed=args.seed + f,
            overrides={"transition_path": str(logt)}, max_lr=3e-3, label_smoothing=0.0, input_ln=False,
            aux_tensor=last_region_t,
        )
        pmb = m.get("per_metric_best", {})
        return float(pmb["top10_acc"]["top10_acc"]) if "top10_acc" in pmb else float(m["top10_acc"])

    trainonly_acc10, full = [], []
    for f, (train_idx, val_idx) in enumerate(splits):
        emb_path = A4_DIR / f"{state_lc}_s{args.seed}_f{f}_regemb.parquet"
        if not emb_path.exists():
            print(f"[a4_eval] MISSING {emb_path.name} — run a4_build first; skipping")
            trainonly_acc10.append(None); full.append(None)
            continue
        to_emb = _read_region_emb(emb_path)
        a_to = _eval_fold(to_emb, train_idx, val_idx, f)
        a_full = _eval_fold(full_region_emb, train_idx, val_idx, f)
        trainonly_acc10.append(a_to); full.append(a_full)
        print(f"[a4_eval] {args.state} s{args.seed} f{f}: full={a_full*100:.2f} train-only={a_to*100:.2f} Δ={(a_full-a_to)*100:+.2f}pp")

    import configs.globals as _g
    out = {
        "state": args.state, "seed": args.seed, "folds": args.folds, "epochs": args.epochs,
        "device": str(_g.DEVICE),
        "trainonly_acc10": trainonly_acc10,
        "fullcorpus_v14_acc10": full,
    }
    valid = [(t, fu) for t, fu in zip(trainonly_acc10, full) if t is not None and fu is not None]
    if valid:
        to = np.array([v[0] for v in valid]); fu = np.array([v[1] for v in valid])
        out["mean_trainonly"] = float(to.mean())
        out["mean_fullcorpus"] = float(fu.mean())
        out["mean_inflation_pp"] = float((fu - to).mean() * 100)
        print(f"\n[a4_eval] {args.state} seed={args.seed} (n={len(valid)} folds):")
        print(f"  full-corpus v14 Acc@10 = {fu.mean()*100:.2f}")
        print(f"  train-only   v14 Acc@10 = {to.mean()*100:.2f}")
        print(f"  TRANSDUCTIVE INFLATION  = {(fu-to).mean()*100:+.2f} pp")
    else:
        print("[a4_eval] no paired folds yet (need a4_build outputs + A2 v14 reg cell).")

    outp = A4_DIR / f"a4_result_{state_lc}_s{args.seed}.json"
    outp.write_text(json.dumps(out, indent=2))
    print(f"[a4_eval] wrote {outp}")


if __name__ == "__main__":
    main()
