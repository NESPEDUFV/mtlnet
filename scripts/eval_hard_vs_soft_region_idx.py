"""B5 — inference-time hard-vs-soft region-index ablation on trained GETNext.

Tests the B5 hypothesis without retraining: for a GETNext MTL checkpoint,
recompute val-set predictions under three priors:

    soft   : α · softmax(probe(last_emb)) @ log_T   (original trained head)
    hard   : α · log_T[last_region_idx]             (faithful GETNext)
    none   : 0 (pure STAN, no graph prior)

and report Acc@1/5/10_indist + MRR_indist for each. If `hard > soft` on
Acc@1/5/MRR, the diffuse probe is acting as a noise floor and B5 proper
(retraining with hard index) is worth the 4-6h. If `hard ≈ soft`, the
soft probe is doing its job and B5 is not load-bearing.

`last_region_idx` is derived from `sequences_next.parquet` `poi_8` +
graph `placeid_to_idx` + `poi_to_region` — exactly the faithful GETNext
index used by the original paper.

This script is CPU-only, reads `next_region.parquet` + `sequences_next.parquet`
by column name only (additive/backward-compatible), and does NOT touch
any shared training module.

Usage::

    python scripts/eval_hard_vs_soft_region_idx.py \\
        --ckpt-dir results/check2hgi/alabama/checkpoints/mtl__check2hgi_next_region_20260421_191156_29497 \\
        --epoch 9
"""

from __future__ import annotations

import argparse
import json
import pickle as pkl
import sys
from pathlib import Path
from typing import Tuple

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from configs.paths import EmbeddingEngine, IoPaths
from data.folds import FoldCreator, TaskType
from models.registry import create_model
from tasks.presets import get_preset, resolve_task_set


def _derive_last_region_idx(state: str) -> np.ndarray:
    """Return last_region_idx per row of next_region.parquet, aligned with
    its row order (which is the row order of next.parquet, which is the
    row order of sequences_next.parquet)."""
    graph_path = IoPaths.CHECK2HGI.get_graph_data_file(state)
    with open(graph_path, "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    poi_to_region = np.asarray(poi_to_region, dtype=np.int64)

    seq_path = IoPaths.CHECK2HGI.get_temp_dir(state) / "sequences_next.parquet"
    poi_cols = [f"poi_{i}" for i in range(9)]
    seq_df = pd.read_parquet(seq_path, columns=poi_cols)
    poi_mat = seq_df[poi_cols].astype(np.int64).to_numpy()  # [N, 9]
    # Find the last non-padding POI per row. Pad is -1 (int, was stored as object).
    valid = poi_mat >= 0
    # If a row has no valid POI, sentinel = -1 (we'll flag these as "no prior").
    last_valid_pos = np.where(valid.any(axis=1), valid.shape[1] - 1 - valid[:, ::-1].argmax(axis=1), -1)
    N = poi_mat.shape[0]
    last_poi = np.where(last_valid_pos >= 0,
                        poi_mat[np.arange(N), np.clip(last_valid_pos, 0, None)],
                        -1)
    n_nopad = int((last_poi >= 0).sum())
    n_allpad = N - n_nopad
    if n_allpad > 0:
        print(f"[derive] {n_allpad}/{N} rows have no valid poi in 0..8 — treated as 'no prior'")
    # Resolve valid last_poi through placeid_to_idx
    valid_mask = last_poi >= 0
    unmapped_valid = valid_mask & ~np.isin(last_poi, list(placeid_to_idx.keys()))
    if unmapped_valid.any():
        bad = last_poi[unmapped_valid][:5].tolist()
        raise ValueError(f"{int(unmapped_valid.sum())} last_poi values unmapped (non-pad): {bad}")
    # Build lookup: -1 for pad rows, region_idx otherwise
    last_region = np.full(N, -1, dtype=np.int64)
    if valid_mask.any():
        poi_idx = pd.Series(last_poi[valid_mask]).map(placeid_to_idx).to_numpy(dtype=np.int64)
        last_region[valid_mask] = poi_to_region[poi_idx]
    return last_region


def _rebuild_val(cfg_dict: dict, fold: int = 0):
    """Rebuild val fold (region input) with the same seed as the saved run.

    Returns (fold_data, task_set, val_idx).
    """
    ts_cfg = cfg_dict["model_params"]["task_set"]
    preset = get_preset(ts_cfg["name"])
    ts = resolve_task_set(
        preset,
        task_b_num_classes=ts_cfg["task_b"].get("num_classes"),
        task_b_head_factory=ts_cfg["task_b"].get("head_factory"),
        task_b_head_params=ts_cfg["task_b"].get("head_params"),
    )
    tt = TaskType.MTL_CHECK2HGI
    creator = FoldCreator(
        task_type=tt,
        n_splits=cfg_dict["k_folds"],
        batch_size=cfg_dict["batch_size"],
        seed=cfg_dict["seed"],
        task_set=ts,
        task_a_input_type="checkin",
        task_b_input_type="region",
    )
    folds = creator.create_folds(
        state=cfg_dict["state"],
        embedding_engine=EmbeddingEngine(cfg_dict["embedding_engine"]),
    )
    keys = sorted(folds.keys())
    # Pull exact val indices from the creator so downstream alignment is bit-exact.
    fi = creator._fold_indices[TaskType.NEXT][fold]
    return folds[keys[fold]], ts, fi.val_indices


def _metrics(logits: torch.Tensor, y: torch.Tensor, num_classes: int) -> dict:
    """Compute Acc@1/5/10 + MRR. All restricted to samples whose label
    falls in [0, num_classes) (in-dist)."""
    logits = logits.cpu()
    y = y.cpu()
    mask = (y >= 0) & (y < num_classes)
    logits = logits[mask]
    y = y[mask]
    topk = logits.topk(10, dim=-1).indices
    correct_at = [(topk[:, :k] == y.unsqueeze(1)).any(dim=1).float().mean().item()
                  for k in (1, 5, 10)]
    ranks = (topk == y.unsqueeze(1)).float()
    # If the true class isn't in top-10, rank = 0 (MRR=0 for that sample)
    rr = torch.zeros(len(y))
    hit_any = ranks.any(dim=1)
    hit_idx = ranks.argmax(dim=1)[hit_any].float() + 1
    rr[hit_any] = 1.0 / hit_idx
    return {
        "n_indist": int(mask.sum().item()),
        "top1": correct_at[0] * 100,
        "top5": correct_at[1] * 100,
        "top10": correct_at[2] * 100,
        "mrr": rr.mean().item() * 100,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt-dir", required=True)
    p.add_argument("--epoch", type=int, required=True)
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    ckpt_dir = Path(args.ckpt_dir)
    cfg_dict = json.load(open(ckpt_dir / "config.json"))
    ckpt = torch.load(ckpt_dir / f"checkpoint_epoch_{args.epoch}.pt",
                      map_location=args.device, weights_only=False)
    sd = ckpt.get("state_dict", ckpt.get("model_state_dict", ckpt))

    fold_data, ts, val_idx = _rebuild_val(cfg_dict, fold=args.fold)
    mp = dict(cfg_dict["model_params"])
    mp["task_set"] = ts
    model = create_model(cfg_dict["model_name"], **mp).to(args.device)
    model.load_state_dict(sd, strict=False)
    model.eval()

    # Pull the head's log_T, alpha, probe, stan backbone
    head = model.next_poi
    log_T = head.log_T  # [R, R]
    alpha = head.alpha.item()
    num_regions = log_T.shape[0]
    print(f"[info] state={cfg_dict['state']}  alpha={alpha:.4f}  "
          f"num_regions={num_regions}  epoch={args.epoch}  fold={args.fold}")

    # Derive last_region_idx for the whole dataset (row-aligned with
    # next.parquet / next_region.parquet / sequences_next.parquet).
    last_region_idx_all = _derive_last_region_idx(cfg_dict["state"])

    # The val fold dataloader yields shuffled batches keyed to the fold's
    # row indices. To align last_region_idx with the batches, we need the
    # val split indices. FoldResult's `.next.val.x` / `.y` are slices of
    # x_task_b / y_region_tensor at val_idx — same indices as the aligned
    # last_region_idx. Derive val indices from .y by matching — but simpler:
    # re-query the fold creator to get val_idx. The FoldCreator caches
    # `_last_val_indices`? No — not guaranteed. Work-around: derive
    # val_idx from y shape + seed.
    #
    # Simpler: iterate val loader in order, and reconstruct aligned
    # last_region_idx via a match on the y tensor — which isn't unique.
    #
    # Cleanest: re-derive val_idx using the creator's indices list. For
    # the MTL_CHECK2HGI path we need the StratifiedGroupKFold split which
    # is deterministic under seed. Rather than re-running the split here,
    # we do: re-run the fold creator's split on the same userids and
    # stratify col with the same seed, and get val_idx directly.
    val_last_region = last_region_idx_all[val_idx]
    # Zero the prior contribution for rows whose last_region is either:
    #   (a) pad (-1; user had no valid POI in the 9-window), or
    #   (b) >= num_regions (last POI maps to a region outside the training
    #       target set — indexing log_T would be out-of-bounds).
    # Silent clipping is wrong because it would use an unrelated transition
    # row as if it were the true prior. Fall back to pure STAN in both cases.
    pad_mask = (val_last_region < 0) | (val_last_region >= num_regions)
    val_last_region_safe = np.where(pad_mask, 0, val_last_region)

    # Run the val dataloader once, capturing stan_logits, probe_logits, y.
    val_loader_b = fold_data.next.val.dataloader
    val_loader_a = fold_data.category.val.dataloader

    stan_logits_all = []
    probe_logits_all = []
    y_all = []

    # Hook to capture stan_logits (stan backbone output, before prior add)
    # and probe_logits (probe linear output). The GETNext head adds them
    # as `stan_logits + α * (softmax(probe) @ log_T)`; we hook both layers.
    _stan_cache, _probe_cache = [], []

    def _stan_hook(m, inp, out):
        _stan_cache.append(out.detach().cpu())

    def _probe_hook(m, inp, out):
        _probe_cache.append(out.detach().cpu())

    h1 = head.stan.register_forward_hook(_stan_hook)
    h2 = head.region_probe.register_forward_hook(_probe_hook)

    with torch.no_grad():
        for batch_b, batch_a in zip(val_loader_b, val_loader_a):
            x_b, y_b = batch_b
            x_a, _ = batch_a
            _ = model((x_a.to(args.device), x_b.to(args.device)))
            y_all.append(y_b)
    h1.remove()
    h2.remove()

    stan_logits = torch.cat(_stan_cache, dim=0)
    probe_logits = torch.cat(_probe_cache, dim=0)
    y = torch.cat(y_all, dim=0)
    last_region_t = torch.from_numpy(val_last_region_safe).long()
    pad_mask_t = torch.from_numpy(pad_mask)
    log_T_cpu = log_T.detach().cpu()

    assert len(stan_logits) == len(probe_logits) == len(y) == len(last_region_t), (
        f"size mismatch: stan={len(stan_logits)} probe={len(probe_logits)} "
        f"y={len(y)} last_region={len(last_region_t)}"
    )

    # Three priors
    prior_soft = F.softmax(probe_logits, dim=-1) @ log_T_cpu          # [B, R]
    prior_hard = log_T_cpu[last_region_t]                              # [B, R]
    # For pad-only rows, hard prior is zero (no last POI observed).
    prior_hard[pad_mask_t] = 0.0
    prior_none = torch.zeros_like(stan_logits)

    print(f"[info] val size = {len(y)}  α = {alpha:.4f}")
    print(f"[info] hard-index unique regions in val: {len(torch.unique(last_region_t))}")

    for label, prior in (("soft (trained)", prior_soft),
                         ("hard (faithful)", prior_hard),
                         ("none (pure STAN)", prior_none)):
        final = stan_logits + alpha * prior
        m = _metrics(final, y, num_regions)
        print(f"  {label:20s} → n_indist={m['n_indist']}  "
              f"Acc@1={m['top1']:5.2f}  Acc@5={m['top5']:5.2f}  "
              f"Acc@10={m['top10']:5.2f}  MRR={m['mrr']:5.2f}")

    # Bonus: probe-agreement — how often does soft-argmax match hard?
    soft_argmax = F.softmax(probe_logits, dim=-1).argmax(dim=-1)
    agree = (soft_argmax == last_region_t).float().mean().item() * 100
    print(f"\n[bonus] soft-probe argmax agrees with hard last_region_idx: {agree:.2f}%")


if __name__ == "__main__":
    main()
