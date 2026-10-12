"""T2P.0 MECHANISM probe (2026-06-05) — mixed-loader vs full-model-forward.

The standalone reg head in a single-task loop hits the (c) ceiling (AL 62.88),
but the SAME head inside the joint mtl_cv loop (T2P.0) caps at 52.90 — a 10pp gap
with loss/grad-clip/metric-selection/input/recipe/folds/precision all verified
IDENTICAL. Two differences remain vs T2P.0: (1) the mixed cat+reg loader, (2) the
FULL-model forward + per-head optimizer (vs a standalone head).

This probe builds the FULL MTLnetCrossAttnDualTower (private_only) + the EXACT
per-head optimizer T2P.0 uses, but trains in a SINGLE-task loop (one reg loader,
cat input = zeros, only the reg loss back-propagated). So the ONLY difference from
T2P.0 is the single vs mixed loader.

  probe ~= 62 -> the MIXED LOADER itself is the poison (the joint mixed-batch
                 iteration degrades reg; mechanism = the joint loop).
  probe ~= 52 -> the FULL-MODEL forward / per-head optimizer is the poison (the same
                 head trains worse inside the full model than standalone).

Run: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t2p0_mechanism_probe.py --state alabama
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
from data.folds import load_next_data
from data.inputs.region_sequence import build_region_sequence_tensor
from models.registry import create_model
from tasks.presets import CHECK2HGI_NEXT_REGION, resolve_task_set
from training.helpers import setup_per_head_optimizer

V14 = "check2hgi_design_k_resln_mae_l0_1"
SEED, EPOCHS, BS, WD, MAX_LR = 42, 50, 2048, 0.01, 3e-3
MODEL_PARAMS = dict(feature_size=64, shared_layer_size=256, num_heads=8,
                    num_layers=4, seq_length=9, num_shared_layers=4)


def topk_acc(logits, y, k=10):
    return (logits.topk(k, -1).indices == y.unsqueeze(-1)).any(-1).float().mean().item()


def run_state(state, mixed=False):
    eng = EmbeddingEngine(V14)
    X, y_cat, userids, _ = load_next_data(state, eng)
    region_seq = build_region_sequence_tensor(state, region_engine=eng, seq_engine=eng).float()
    # cat (checkin) input sequence — for the optional real-cat mixed loop.
    from data.folds import _convert_to_tensors, TaskType
    x_checkin, y_cat_t = _convert_to_tensors(X, y_cat, TaskType.NEXT, embedding_dim=64, slide_window=9)
    x_checkin = x_checkin.float()
    rdf = IoPaths.load_next_region(state, eng)
    y_region = torch.from_numpy(np.ascontiguousarray(rdf["region_idx"].to_numpy(np.int64)))
    n_regions = int(y_region.max().item()) + 1
    n_cat = int(y_cat_t.max().item()) + 1
    print(f"[{state}] region_seq {tuple(region_seq.shape)} n_regions={n_regions} "
          f"mixed={mixed} (real-cat loop)" )

    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    fold_best = []
    for fold, (tr, va) in enumerate(sgkf.split(np.asarray(X), np.asarray(y_cat), groups=np.asarray(userids))):
        tr_ds = TensorDataset(region_seq[tr], y_region[tr])
        tr_dl = DataLoader(tr_ds, batch_size=BS, shuffle=True)
        cat_dl = DataLoader(TensorDataset(x_checkin[tr], y_cat_t[tr]), batch_size=BS, shuffle=True)
        va_x, va_y = region_seq[va].to(DEVICE), y_region[va].to(DEVICE)

        # EXACT T2P.0 full model: MTLnetCrossAttnDualTower, reg head private_only prior-OFF.
        ts = resolve_task_set(
            CHECK2HGI_NEXT_REGION, task_b_num_classes=n_regions,
            task_a_head_factory="next_gru",  # match mtl_cv's --cat-head next_gru (was default next_mtl)
            task_b_head_factory="next_stan_flow_dualtower",
            task_b_head_params={"raw_embed_dim": 64, "fusion_mode": "private_only",
                                "freeze_alpha": True, "alpha_init": 0.0},
        )
        model = create_model("mtlnet_crossattn_dualtower", task_set=ts,
                             num_classes=n_regions, **MODEL_PARAMS).to(DEVICE)
        opt = setup_per_head_optimizer(model, cat_lr=1e-3, reg_lr=3e-3, shared_lr=1e-3,
                                       weight_decay=WD, alpha_no_weight_decay=False)
        steps = len(tr_dl)
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=MAX_LR, epochs=EPOCHS,
                                                    steps_per_epoch=steps, pct_start=0.3)
        actx = torch.autocast(DEVICE.type, dtype=torch.float16) if DEVICE.type == "cuda" else _null()
        best = 0.0
        from itertools import cycle
        for ep in range(EPOCHS):
            model.train()
            cat_iter = cycle(cat_dl) if mixed else None
            for xb, yb in tr_dl:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                if mixed:
                    cx, cy = next(cat_iter)
                    cx, cy = cx.to(DEVICE), cy.to(DEVICE)
                    if cx.size(0) != xb.size(0):       # align batch dims (last partial batch)
                        m = min(cx.size(0), xb.size(0)); cx, cy, xb2, yb2 = cx[:m], cy[:m], xb[:m], yb[:m]
                    else:
                        xb2, yb2 = xb, yb
                else:
                    cx = xb.new_zeros(xb.size(0), 9, 64); xb2, yb2 = xb, yb
                opt.zero_grad(set_to_none=True)
                with actx:
                    out_cat, out_next = model((cx, xb2))        # full-model forward (cat path runs)
                    # mtl_cv static_weight cat0: loss = 1.0*reg + 0.0*cat -> only reg backprops.
                    loss = F.cross_entropy(out_next.float(), yb2)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step(); sched.step()
            model.eval()
            with torch.no_grad():
                accs = []
                for i in range(0, va_x.size(0), BS):
                    xb = va_x[i:i+BS]
                    with actx:
                        lg = model.next_forward(xb)           # T2P.0's disjoint eval path
                    accs.append((topk_acc(lg.float(), va_y[i:i+BS], 10), xb.size(0)))
                tot = sum(n for _, n in accs)
                acc10 = sum(a*n for a, n in accs) / tot
            best = max(best, acc10)
        fold_best.append(best * 100)
        print(f"  [{state}] fold{fold+1}: best val Acc@10 = {best*100:.2f}")
    m, s = float(np.mean(fold_best)), float(np.std(fold_best))
    print(f"\n[{state}] FULL-MODEL single-task reg Acc@10 = {m:.2f} ± {s:.2f}  "
          f"folds={[round(f,2) for f in fold_best]}")
    print(f"  >>> standalone single-task was 62.88(AL)/73.12(FL); T2P.0 joint was 52.90/59.53. "
          f"~62 => mixed loader is the poison; ~52 => full-model forward is.")
    return m, s


class _null:
    def __enter__(self): return None
    def __exit__(self, *a): return False


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--state", required=True)
    ap.add_argument("--mixed", action="store_true",
                    help="interleave a REAL cat loader (mtl_cv-style mixed loop, cat-weight 0) "
                         "to test mixed-batch-structural vs mtl_cv-specific")
    a = ap.parse_args()
    torch.manual_seed(SEED); np.random.seed(SEED)
    t0 = time.time(); run_state(a.state, mixed=a.mixed)
    print(f"=== {a.state} mixed={a.mixed} done in {time.time()-t0:.0f}s ===")


if __name__ == "__main__":
    main()
