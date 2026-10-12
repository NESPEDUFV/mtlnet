"""A4 — CAT transductivity bound (in-coverage POI-level proxy).

Cat is the substrate-driven axis where Check2HGI's lift lives, so it's where transductive inflation
actually bites — but the check-in-level cat setup hits the inductive wall (a train-only check-in graph
has no nodes for val users' check-ins). This proxy measures the transductivity of the substrate's
**POI-level** representation on next-category, on the **in-coverage subset** (val sequences whose input
POIs are all train-covered — no inductive gap there):

  per fold: x = 9-window of POI-level v14 embeddings (placeid→vector), y = next_category, next_gru.
  Arm FULL = full-corpus v14 poi_embeddings; arm TRAIN-ONLY = train-only-fold v14 poi_embeddings
  (`*_trainonly_poi.parquet`). Train on the train split, eval macro-F1 (f1-best) on val∩in-coverage —
  SAME rows for both arms, same device. Inflation = full − train-only.

CAVEATS (state in the writeup): (1) POI-level proxy, NOT the exact check-in-level §0.1 cat setup —
it tests POI-representation transductivity, the measurable part of the cat axis. (2) Excludes val
sequences with any cold (train-unseen) POI — report the excluded fraction. (3) Both arms POI-level, so
the contrast is fair within this proxy.

Usage: INGRED_DEVICE=cpu python scripts/pre_freeze_gates/a4_cat_eval.py --state alabama --seed 0 --folds 5
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
import p1_region_head_ablation as H

A4_DIR = _root / "results" / "pre_freeze_gates" / "a4"
V14 = "check2hgi_design_k_resln_mae_l0_1"
WINDOW = 9


def _poi_lookup(parquet_path):
    """placeid -> 64-d vector dict from a poi_embeddings.parquet (placeid + '0'..'63')."""
    df = pd.read_parquet(parquet_path)
    emb_cols = [c for c in df.columns if c.isdigit()]
    emb = df[emb_cols].to_numpy(dtype=np.float32)
    return {int(p): emb[i] for i, p in enumerate(df["placeid"].to_numpy())}, len(emb_cols)


def _build_x(seq_df, lookup, dim):
    """[N,9,dim] POI-level windows; padding (-1) and missing placeids -> zero vector."""
    n = len(seq_df)
    out = np.zeros((n, WINDOW, dim), dtype=np.float32)
    for i in range(WINDOW):
        pids = seq_df[f"poi_{i}"].astype(np.int64).to_numpy()
        for r, p in enumerate(pids):
            if p != -1:
                v = lookup.get(int(p))
                if v is not None:
                    out[r, i] = v
    return torch.from_numpy(out)


def _incoverage_mask(seq_df, to_keys):
    """Boolean over rows: all non-pad input placeids are train-covered (in to_keys)."""
    n = len(seq_df)
    cols = [f"poi_{i}" for i in range(WINDOW)]
    arr = seq_df[cols].astype(np.int64).to_numpy()
    mask = np.ones(n, dtype=bool)
    for r in range(n):
        for p in arr[r]:
            if p != -1 and int(p) not in to_keys:
                mask[r] = False
                break
    return mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=2048)
    args = ap.parse_args()
    state_lc = args.state.lower()

    seq_df = pd.read_parquet(IoPaths.get_seq_next(args.state, EmbeddingEngine.CHECK2HGI))
    _, y_cat, userids, _ = load_next_data(args.state, EmbeddingEngine.CHECK2HGI)  # cat labels + groups
    y_cat = np.asarray(y_cat, dtype=np.int64)
    n_classes = int(y_cat.max()) + 1

    full_lookup, dim = _poi_lookup(_root / "output" / V14 / state_lc / "poi_embeddings.parquet")
    x_full_all = _build_x(seq_df, full_lookup, dim)
    y_t = torch.from_numpy(y_cat)

    sgkf = StratifiedGroupKFold(n_splits=max(2, args.folds), shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(np.zeros(len(y_cat)), y_cat, groups=userids))[:args.folds]

    rows = []
    for f, (train_idx, val_idx) in enumerate(splits):
        poi_path = A4_DIR / f"{state_lc}_s{args.seed}_f{f}_trainonly_poi.parquet"
        if not poi_path.exists():
            print(f"[a4_cat] MISSING {poi_path.name} — skip fold {f}")
            rows.append(None); continue
        to_lookup, _ = _poi_lookup(poi_path)
        to_keys = set(to_lookup.keys())
        x_to_all = _build_x(seq_df, to_lookup, dim)

        cov = _incoverage_mask(seq_df, to_keys)
        val_cov = val_idx[cov[val_idx]]
        frac = len(val_cov) / max(1, len(val_idx))
        if len(val_cov) < 20:
            print(f"[a4_cat] fold {f}: too few in-coverage val rows ({len(val_cov)}) — skip")
            rows.append(None); continue

        def _run(x_all):
            # train on full train split; eval on val∩in-coverage (custom val_idx).
            m = H._train_single_task(
                "next_gru", x_all, y_t, train_idx, val_cov, emb_dim=dim, n_classes=n_classes,
                epochs=args.epochs, batch_size=args.batch_size, seed=args.seed + f,
                overrides={}, max_lr=3e-3, label_smoothing=0.0, input_ln=False, aux_tensor=None)
            pmb = m.get("per_metric_best", {})
            return float(pmb["f1"]["f1"]) if "f1" in pmb else float(m["f1"])

        a_full = _run(x_full_all)
        a_to = _run(x_to_all)
        rows.append({"fold": f, "n_val_incov": int(len(val_cov)), "incov_frac": frac,
                     "full_f1": a_full, "trainonly_f1": a_to})
        print(f"[a4_cat] {args.state} s{args.seed} f{f}: in-cov {frac*100:.1f}% (n={len(val_cov)}) "
              f"full={a_full*100:.2f} train-only={a_to*100:.2f} Δ={(a_full-a_to)*100:+.2f}pp")

    good = [r for r in rows if r]
    import configs.globals as _g
    out = {"state": args.state, "seed": args.seed, "device": str(_g.DEVICE), "metric": "cat macro-F1 (POI-level proxy)",
           "per_fold": rows}
    if good:
        full = np.array([r["full_f1"] for r in good]); to = np.array([r["trainonly_f1"] for r in good])
        out["mean_full"] = float(full.mean()); out["mean_trainonly"] = float(to.mean())
        out["mean_inflation_pp"] = float((full - to).mean() * 100)
        out["mean_incov_frac"] = float(np.mean([r["incov_frac"] for r in good]))
        print(f"\n[a4_cat] {args.state} s{args.seed} (n={len(good)} folds, in-cov {out['mean_incov_frac']*100:.1f}%):")
        print(f"  full={full.mean()*100:.2f}  train-only={to.mean()*100:.2f}  CAT INFLATION={out['mean_inflation_pp']:+.2f} pp")
    outp = A4_DIR / f"a4_cat_result_{state_lc}_s{args.seed}.json"
    outp.write_text(json.dumps(out, indent=2))
    print(f"[a4_cat] wrote {outp}")


if __name__ == "__main__":
    main()
