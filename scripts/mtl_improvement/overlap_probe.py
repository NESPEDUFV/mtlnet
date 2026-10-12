#!/usr/bin/env python
"""Overlapping-window validation probe (pipeline-audit HIGH finding).

The audit found generate_sequences defaults to NON-overlapping windows (stride=9) -> AL trains on
12,709 sequences instead of ~96-108k (a 7.5-8.4x training-data loss that caps BOTH ceilings,
head-independent). This probe validates the lift IN ISOLATION (no disk writes to engine dirs, frozen
substrate untouched): it builds cat (and optionally reg) sequences at stride ∈ {9 control, 1 overlap}
and trains the ceiling head through ONE identical harness that matches the real trainers, so the
overlap-vs-control delta is the windowing effect alone. The control arm should reproduce ~the frozen
ceiling (49.97 cat AL / 62.88 reg AL), validating the harness.

cat: next_gru + logit-adjust τ=0.5, AdamW(lr1e-4,wd0.01)+OneCycle(max_lr1e-2), 50ep, bs2048, fp16
     -- matches next_cv.py. Metric = macro-F1 (diagnostic-best epoch).
reg: next_stan (≡ next_stan_flow α=0, no prior/aux), region-emb input, OneCycle max_lr3e-3, fp32
     -- matches p1. Metric = Acc@10 (diagnostic-best epoch).

Usage: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/overlap_probe.py <state> <cat|reg> [strides]
"""
import sys
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold

from configs.globals import DEVICE
from configs.paths import EmbeddingEngine, IoPaths
from models.registry import create_model
from losses.calibrated import build_calibrated_loss

V14 = EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_MAE_L0_1
W = 9
EMB = 64


def _seed(s=42):
    torch.manual_seed(s); np.random.seed(s)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(s)


def build_cat(state, stride):
    """Return X[N,9,64] float32, y[N] cat int64, groups[N] userid — at the given stride."""
    from data.inputs.core import convert_user_checkins_to_sequences
    from configs.globals import CATEGORIES_MAP
    name2idx = {v: k for k, v in CATEGORIES_MAP.items()}  # 'Outdoors'->4, ...
    def to_int(c):
        if isinstance(c, (int, np.integer)):
            return int(c)
        return name2idx.get(str(c), 7)  # unknown/'None' -> 7 (dropped below)
    df = IoPaths.load_embedd(state, V14).sort_values(["userid", "datetime"])
    emb_cols = [str(i) for i in range(EMB)]
    Xs, ys, gs = [], [], []
    for uid, udf in df.groupby("userid"):
        udf = udf.reset_index(drop=True)
        res, _ = convert_user_checkins_to_sequences(udf, emb_cols, W, EMB, stride=stride)
        for r in res:
            Xs.append(r[:W * EMB]); ys.append(to_int(r[W * EMB])); gs.append(uid)
    X = np.asarray(Xs, np.float32).reshape(-1, W, EMB)
    y = np.asarray(ys, np.int64)
    # cat labels: keep classes 0..6 (drop 'None'/7 if present, like the real builder)
    keep = y < 7
    return X[keep], y[keep], np.asarray(gs)[keep]


def build_reg(state, stride):
    """Return Xreg[N,9,64] region-emb seq, yreg[N] region_idx, groups[N] userid — at stride.
    Reg head input is the region-embedding sequence (≡ p1 --input-type region); target = region
    of the target POI. Uses next_stan (== next_stan_flow α=0, no prior/aux)."""
    from data.inputs.core import convert_user_checkins_to_sequences, PADDING_VALUE
    from data.inputs.region_sequence import _load_region_embeddings, _load_graph_maps
    reg_emb = _load_region_embeddings(state, V14)          # [n_regions, 64]
    placeid_to_idx, poi_to_region = _load_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1
    zero = np.zeros(EMB, np.float32)

    def poi_region(p):
        if p in (PADDING_VALUE, str(PADDING_VALUE), -1, "-1"):
            return None
        idx = placeid_to_idx.get(p, placeid_to_idx.get(str(p)))
        if idx is None:
            return None
        r = int(poi_to_region[idx])
        return r if 0 <= r < n_regions else None

    df = IoPaths.load_embedd(state, V14).sort_values(["userid", "datetime"])
    emb_cols = [str(i) for i in range(EMB)]
    Xs, ys, gs = [], [], []
    for uid, udf in df.groupby("userid"):
        udf = udf.reset_index(drop=True)
        _, poi_seqs = convert_user_checkins_to_sequences(udf, emb_cols, W, EMB, stride=stride)
        for seq in poi_seqs:                                # [poi_0..poi_8, target_poi, userid]
            hist, tgt = seq[:W], seq[W]
            tr = poi_region(tgt)
            if tr is None:
                continue
            rows = [reg_emb[r] if (r := poi_region(p)) is not None else zero for p in hist]
            Xs.append(np.vstack(rows)); ys.append(tr); gs.append(uid)
    X = np.asarray(Xs, np.float32).reshape(-1, W, EMB)
    return X, np.asarray(ys, np.int64), np.asarray(gs), n_regions


def run_reg(state, stride):
    X, y, g, nreg = build_reg(state, stride)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    fold_best = []
    # stratify needs each class countable; fall back to plain GroupKFold-like via y clipping
    ystrat = y
    for fi, (tr, va) in enumerate(sgkf.split(X, ystrat, g)):
        _seed(42 + fi)
        Xtr, ytr, Xva, yva = X[tr], y[tr], X[va], y[va]
        model = create_model("next_stan", embed_dim=EMB, num_classes=nreg,
                             d_model=128, num_heads=4, seq_length=W, dropout=0.3).to(DEVICE)
        crit = nn.CrossEntropyLoss()
        opt = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01, eps=1e-8)
        steps = (len(Xtr) + 2047) // 2048
        sch = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-3, epochs=50, steps_per_epoch=steps)
        best = 0.0
        for ep in range(50):
            model.train(); perm = np.random.permutation(len(Xtr))
            for i in range(0, len(Xtr), 2048):
                idx = perm[i:i + 2048]
                xb = torch.from_numpy(Xtr[idx]).to(DEVICE)
                yb = torch.from_numpy(ytr[idx]).to(DEVICE)
                opt.zero_grad(set_to_none=True)
                loss = crit(model(xb), yb)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step(); sch.step()
            best = max(best, acc_at_k(model, Xva, yva, k=10))
        fold_best.append(best)
        print(f"  fold{fi}: Acc@10_best={fold_best[-1]:.2f}")
    return len(y), float(np.mean(fold_best)), float(np.std(fold_best, ddof=1))


def macro_f1(model, Xv, yv, bs=2048):
    model.eval(); preds = []
    with torch.no_grad():
        for i in range(0, len(Xv), bs):
            xb = torch.from_numpy(Xv[i:i + bs]).to(DEVICE)
            preds.append(model(xb).argmax(1).cpu().numpy())
    return f1_score(yv, np.concatenate(preds), average="macro") * 100


def acc_at_k(model, Xv, yv, k=10, bs=2048):
    model.eval(); hit = 0
    with torch.no_grad():
        for i in range(0, len(Xv), bs):
            xb = torch.from_numpy(Xv[i:i + bs]).to(DEVICE)
            topk = model(xb).topk(k, dim=1).indices.cpu().numpy()
            yb = yv[i:i + bs]
            hit += sum(yb[j] in topk[j] for j in range(len(yb)))
    return hit / len(yv) * 100


def run_cat(state, stride):
    X, y, g = build_cat(state, stride)
    nseq = len(y)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    fold_best = []
    for fi, (tr, va) in enumerate(sgkf.split(X, y, g)):
        _seed(42 + fi)
        Xtr, ytr, Xva, yva = X[tr], y[tr], X[va], y[va]
        model = create_model("next_gru", embed_dim=EMB, num_classes=7).to(DEVICE)
        crit = build_calibrated_loss(7, torch.from_numpy(ytr), logit_adjust_tau=0.5, device=DEVICE)
        opt = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01, eps=1e-8)
        steps = (len(Xtr) + 2047) // 2048
        sch = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=1e-2, epochs=50, steps_per_epoch=steps)
        best = 0.0
        for ep in range(50):
            model.train(); perm = np.random.permutation(len(Xtr))
            for i in range(0, len(Xtr), 2048):
                idx = perm[i:i + 2048]
                xb = torch.from_numpy(Xtr[idx]).to(DEVICE)
                yb = torch.from_numpy(ytr[idx]).to(DEVICE)
                opt.zero_grad(set_to_none=True)
                with torch.autocast("cuda", dtype=torch.float16, enabled=(DEVICE.type == "cuda")):
                    loss = crit(model(xb), yb)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step(); sch.step()
            best = max(best, macro_f1(model, Xva, yva))
        fold_best.append(best)
        print(f"  fold{fi}: macroF1_best={fold_best[-1]:.2f}")
    return nseq, float(np.mean(fold_best)), float(np.std(fold_best, ddof=1))


def main():
    state = sys.argv[1] if len(sys.argv) > 1 else "alabama"
    task = sys.argv[2] if len(sys.argv) > 2 else "cat"
    strides = [int(s) for s in sys.argv[3].split(",")] if len(sys.argv) > 3 else [9, 1]
    print(f"=== overlap probe {state} {task} strides={strides} (control=9, overlap=1) ===")
    for st in strides:
        if task == "cat":
            nseq, m, s = run_cat(state, st)
            label = "non-overlap(control)" if st == 9 else f"overlap(stride={st})"
            print(f"[{label}] n_seq={nseq:,}  cat macroF1 = {m:.2f} ± {s:.2f}\n")
        else:
            nseq, m, s = run_reg(state, st)
            label = "non-overlap(control)" if st == 9 else f"overlap(stride={st})"
            print(f"[{label}] n_seq={nseq:,}  reg Acc@10 = {m:.2f} ± {s:.2f}\n")


if __name__ == "__main__":
    main()
