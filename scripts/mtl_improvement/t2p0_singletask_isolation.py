"""T2P.0 JOINT-LOOP isolation (2026-06-05) — the user-requested decider.

Q: the isolated reg STAN reaches 52.90/59.53 in the train.py-MTL joint harness
(T2P.0) but 62.88-66.8 in the p1 harness on BYTE-IDENTICAL input. Is the ~10-14pp
the JOINT mixed-loop (cat+reg interleaved) or a train.py-vs-p1 harness detail?

This trains the EXACT T2P.0 reg head (NextHeadStanFlowDualTower, fusion_mode=
private_only, prior-OFF — self-contained in private_only: forward ignores the shared
`x`, reads only raw_region_seq) on the IDENTICAL input + IDENTICAL folds + IDENTICAL
recipe (AdamW wd=0.01, OneCycleLR max_lr=3e-3, 50ep, bs2048, fp16) — but in a
SINGLE-TASK loop: NO cat loader, NO mixed `max_size_cycle` iteration, NO per-head
optimizer. So vs T2P.0 the ONLY removed variable is the joint mixed-loop machinery.

  single-task ~= 66  -> the JOINT mixed-loop is the poison -> T2P.1 (staged) is the lever.
  single-task ~= 52  -> it's a train.py-harness/eval/head detail, NOT the joint loop
                        -> staging won't fix it; the "joint loop caps reg" framing is too strong.

Folds replicate folds.py:_create_check2hgi_mtl_folds EXACTLY:
  sgkf = StratifiedGroupKFold(5, shuffle=True, random_state=42).split(X, y_cat, groups=userids)
Input replicates the MTL reg task: build_region_sequence_tensor (verified byte-identical
to the p1 (c) input). Metric: best-epoch val top10 acc per fold, mean across folds
(= the per-task diagnostic-best the T2P.0 agg reports).

Run: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t2p0_singletask_isolation.py --state alabama
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import StratifiedGroupKFold

from configs.paths import IoPaths, EmbeddingEngine
from configs.globals import DEVICE
from data.folds import load_next_data, _convert_to_tensors
from data.inputs.region_sequence import build_region_sequence_tensor
from models.next.next_stan_flow_dualtower.head import NextHeadStanFlowDualTower
from configs.model import InputsConfig

V14 = "check2hgi_design_k_resln_mae_l0_1"
SEED = 42
EPOCHS = 50
BS = 2048
WD = 0.01
MAX_LR = 3e-3


def topk_acc(logits, y, k=10):
    topk = logits.topk(k, dim=-1).indices  # [B,k]
    return (topk == y.unsqueeze(-1)).any(-1).float().mean().item()


def topk_acc_indist(logits, y, train_labels_t, k=10):
    """mtl_cv's top{k}_acc_indist: top-k over ONLY val samples whose true label
    was seen in train (excludes cold-start). Mirrors mtl_eval.py:28-51."""
    mask = torch.isin(y, train_labels_t)
    if int(mask.sum()) == 0:
        return 0.0
    lg, yy = logits[mask], y[mask]
    topk = lg.topk(k, dim=-1).indices
    return (topk == yy.unsqueeze(-1)).any(-1).float().mean().item()


def run_state(state: str):
    eng = EmbeddingEngine(V14)
    # --- inputs/labels exactly as the MTL fold builder assembles them ---
    X, y_cat, userids, dim = load_next_data(state, eng)          # for the split (matches folds.py)
    region_seq = build_region_sequence_tensor(state, region_engine=eng, seq_engine=eng)  # [N,9,64]
    rdf = IoPaths.load_next_region(state, eng)
    y_region = torch.from_numpy(np.ascontiguousarray(rdf["region_idx"].to_numpy(np.int64)))
    n_regions = int(y_region.max().item()) + 1
    region_seq = region_seq.float()
    print(f"[{state}] region_seq {tuple(region_seq.shape)}  n_regions={n_regions}  N={len(y_region)}")

    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_best = []
    for fold, (tr, va) in enumerate(sgkf.split(np.asarray(X), np.asarray(y_cat), groups=np.asarray(userids))):
        tr_ds = TensorDataset(region_seq[tr], y_region[tr])
        va_x, va_y = region_seq[va].to(DEVICE), y_region[va].to(DEVICE)
        train_labels_t = torch.as_tensor(sorted(set(y_region[tr].tolist())),
                                         dtype=va_y.dtype, device=DEVICE)
        tr_dl = DataLoader(tr_ds, batch_size=BS, shuffle=True, drop_last=False)

        # EXACT T2P.0 reg head: dual-tower private_only, prior-OFF (alpha=0 buffer).
        head = NextHeadStanFlowDualTower(
            embed_dim=256, num_classes=n_regions, seq_length=9, d_model=128,
            num_heads=8, dropout=0.1, raw_embed_dim=64,
            priv_num_heads=4, priv_dropout=0.3, fusion_mode="private_only",
            alpha_init=0.0, freeze_alpha=True,
        ).to(DEVICE)
        opt = torch.optim.AdamW(head.parameters(), lr=1e-4, weight_decay=WD, eps=1e-8)
        steps = len(tr_dl)
        sched = torch.optim.lr_scheduler.OneCycleLR(
            opt, max_lr=MAX_LR, epochs=EPOCHS, steps_per_epoch=steps, pct_start=0.3)
        actx = torch.autocast(DEVICE.type, dtype=torch.float16) if DEVICE.type == "cuda" else _null()

        # dummy shared input (private_only ignores it; kept for the forward signature)
        best, best_id = 0.0, 0.0
        for ep in range(EPOCHS):
            head.train()
            for xb, yb in tr_dl:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                dummy = xb.new_zeros(xb.size(0), 9, 256)
                opt.zero_grad(set_to_none=True)
                with actx:
                    logits = head(dummy, raw_region_seq=xb)
                    loss = F.cross_entropy(logits.float(), yb)
                loss.backward()
                nn.utils.clip_grad_norm_(head.parameters(), 1.0)
                opt.step(); sched.step()
            # eval (full val in chunks)
            head.eval()
            with torch.no_grad():
                logits_all = []
                for i in range(0, va_x.size(0), BS):
                    xb = va_x[i:i+BS]
                    dummy = xb.new_zeros(xb.size(0), 9, 256)
                    with actx:
                        logits_all.append(head(dummy, raw_region_seq=xb).float())
                lg = torch.cat(logits_all, 0)
                acc10 = topk_acc(lg, va_y, 10)
                acc10_id = topk_acc_indist(lg, va_y, train_labels_t, 10)
            if acc10 > best:
                best, best_id = acc10, acc10_id
        fold_best.append(best * 100)
        print(f"  [{state}] fold{fold+1}: best val Acc@10 plain={best*100:.2f} indist={best_id*100:.2f}")
    mean = float(np.mean(fold_best)); std = float(np.std(fold_best))
    print(f"\n[{state}] SINGLE-TASK isolated reg Acc@10 (best-epoch, mean±std over 5 folds): "
          f"{mean:.2f} ± {std:.2f}  folds={[round(f,2) for f in fold_best]}")
    return mean, std


class _null:
    def __enter__(self): return None
    def __exit__(self, *a): return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    a = ap.parse_args()
    torch.manual_seed(SEED); np.random.seed(SEED)
    t0 = time.time()
    m, s = run_state(a.state)
    print(f"\n=== {a.state}: single-task isolated reg Acc@10 = {m:.2f}±{s:.2f} "
          f"(T2P.0 joint was 52.90/59.53; p1 was 62.88-66.8) — {time.time()-t0:.0f}s ===")


if __name__ == "__main__":
    main()
