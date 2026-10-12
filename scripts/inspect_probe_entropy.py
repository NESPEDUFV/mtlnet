"""B5 feasibility: does the learned region_probe act like a near-one-hot index?

If the probe output is peaky (top-1 probability ~1.0, entropy ~0), then
replacing the soft probe with a hard `last_region_idx` lookup changes the
prior negligibly and B5 is not worth the 4-6h of pipeline work.
If the probe is diffuse (top-1 < 0.3, entropy > 3.0), the soft probe is
acting as a learned smoother and hard-indexing would meaningfully alter
behaviour; B5 would be a load-bearing experiment.

Usage::

    python scripts/inspect_probe_entropy.py \\
        --ckpt-dir results/check2hgi/alabama/checkpoints/mtl__check2hgi_next_region_20260421_191156_29497 \\
        --epoch 9
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
import torch
import torch.nn.functional as F

from configs.experiment import ExperimentConfig
from data.folds import FoldCreator, TaskType
from models.registry import create_model


def rebuild_val_loader(cfg: ExperimentConfig, fold: int = 0):
    """Re-run the exact fold split and return the val DataLoader for fold i."""
    from configs.paths import EmbeddingEngine
    from tasks.presets import get_preset, resolve_task_set
    model_params = cfg.__dict__.get("model_params") or {}
    ts_cfg = model_params.get("task_set", {}) if isinstance(model_params, dict) else {}
    preset = get_preset(ts_cfg.get("name", "check2hgi_next_region"))
    ts = resolve_task_set(
        preset,
        task_b_num_classes=ts_cfg.get("task_b", {}).get("num_classes"),
        task_b_head_factory=ts_cfg.get("task_b", {}).get("head_factory"),
        task_b_head_params=ts_cfg.get("task_b", {}).get("head_params"),
    )
    # Task_type in saved config is "mtl" but with task_set=check2hgi_next_region
    # we must use MTL_CHECK2HGI to trigger the right fold creator branch.
    tt = TaskType.MTL_CHECK2HGI if ts.name.startswith("check2hgi") else TaskType(cfg.task_type)
    creator = FoldCreator(
        task_type=tt,
        n_splits=cfg.k_folds,
        batch_size=cfg.batch_size,
        seed=cfg.seed,
        task_set=ts,
        task_a_input_type=getattr(cfg, "task_a_input_type", "checkin") or "checkin",
        task_b_input_type=getattr(cfg, "task_b_input_type", "region") or "region",
    )
    folds = creator.create_folds(state=cfg.state, embedding_engine=EmbeddingEngine(cfg.embedding_engine))
    keys = sorted(folds.keys())
    return folds[keys[fold]], ts


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt-dir", required=True)
    p.add_argument("--epoch", type=int, default=9)
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--device", default="cpu")
    p.add_argument("--max-batches", type=int, default=10)
    args = p.parse_args()

    ckpt_dir = Path(args.ckpt_dir)
    cfg_dict = json.load(open(ckpt_dir / "config.json"))
    ckpt = torch.load(
        ckpt_dir / f"checkpoint_epoch_{args.epoch}.pt",
        map_location=args.device,
        weights_only=False,
    )
    sd = ckpt.get("state_dict", ckpt.get("model_state_dict", ckpt))

    # Minimal ExperimentConfig-like shim (only fields FoldCreator reads)
    class _Cfg:
        pass
    cfg = _Cfg()
    for k, v in cfg_dict.items():
        setattr(cfg, k, v)
    # Flatten nested task_set reference if model_params hold it
    cfg.task_set = cfg_dict["model_params"]["task_set"]["name"]

    fold_data, ts = rebuild_val_loader(cfg, fold=args.fold)

    # Rebuild model
    model_params = cfg_dict["model_params"]
    mp = dict(model_params)
    mp["task_set"] = ts
    model = create_model(cfg.model_name, **mp).to(args.device)
    missing, unexpected = model.load_state_dict(sd, strict=False)
    print(f"[load] missing={len(missing)}  unexpected={len(unexpected)}")
    if missing:
        print("  first missing:", missing[:5])
    if unexpected:
        print("  first unexpected:", unexpected[:5])
    model.eval()

    # Hook the region_probe output
    probe_logits_list = []

    def _hook(mod, inp, out):
        probe_logits_list.append(out.detach().cpu())

    h = model.next_poi.region_probe.register_forward_hook(_hook)

    # For MTL_CHECK2HGI: task_b (region) goes into FoldResult.next,
    # task_a (category) goes into FoldResult.category.
    val_loader_b = fold_data.next.val.dataloader  # region inputs + labels
    val_loader_a = fold_data.category.val.dataloader  # category inputs + labels
    val_loader = val_loader_b  # for iteration structure reference
    num_classes = model_params["task_set"]["task_b"]["num_classes"]
    print(f"[info] num_regions={num_classes}  uniform entropy={np.log(num_classes):.3f}")

    top1_probs, top5_probs, entropies = [], [], []
    argmax_ids = []

    with torch.no_grad():
        for i, (batch_b, batch_a) in enumerate(zip(val_loader_b, val_loader_a)):
            if i >= args.max_batches:
                break
            x_b, _ = batch_b  # region input
            x_a, _ = batch_a  # category input
            x_a = x_a.to(args.device)
            x_b = x_b.to(args.device)
            try:
                _ = model((x_a, x_b))
            except Exception as e:
                print(f"[warn] forward failed: {e}")
                break

            if probe_logits_list:
                logits = probe_logits_list[-1]
                probs = F.softmax(logits, dim=-1)
                tp, _ = probs.max(dim=-1)
                ent = -(probs * (probs.clamp_min(1e-12)).log()).sum(dim=-1)
                top5, _ = probs.topk(min(5, probs.size(-1)), dim=-1)
                top1_probs.append(tp)
                top5_probs.append(top5.sum(dim=-1))
                entropies.append(ent)
                argmax_ids.append(probs.argmax(dim=-1))

    h.remove()

    if not top1_probs:
        print("[error] No probe outputs captured. Verify model forward was invoked.")
        return

    top1 = torch.cat(top1_probs).numpy()
    top5 = torch.cat(top5_probs).numpy()
    ent = torch.cat(entropies).numpy()
    am = torch.cat(argmax_ids).numpy()
    uniq, counts = np.unique(am, return_counts=True)

    print("\n=== Region-probe concentration (AL GETNext, epoch %d, fold %d) ===" % (args.epoch, args.fold))
    print(f"  samples analysed: {len(top1)}")
    print(f"  top-1 prob   mean={top1.mean():.4f}  median={np.median(top1):.4f}  min={top1.min():.4f}  max={top1.max():.4f}")
    print(f"  top-5 prob   mean={top5.mean():.4f}  median={np.median(top5):.4f}")
    print(f"  entropy      mean={ent.mean():.4f}  median={np.median(ent):.4f}  uniform={np.log(num_classes):.3f}")
    print(f"  unique argmax regions across val: {len(uniq)} / {num_classes}")
    print(f"  top-10 argmax region frequencies (region_id, count, freq):")
    order = np.argsort(-counts)[:10]
    for j in order:
        print(f"    r={int(uniq[j])}  n={int(counts[j])}  freq={counts[j]/len(am):.3f}")

    # Decision criterion
    print("\n--- Interpretation ---")
    if top1.mean() > 0.85:
        print("  PEAKY probe: top-1 > 0.85 on average.")
        print("  Hard-indexing ≈ soft probe. B5 would produce near-identical results.")
        print("  RECOMMENDATION: skip B5; report 'probe already degenerated to one-hot'.")
    elif top1.mean() < 0.25:
        print("  DIFFUSE probe: top-1 < 0.25 on average.")
        print("  The probe is acting as a learned *smoother*, not a hard index.")
        print("  RECOMMENDATION: B5 is load-bearing; run it to see if hard index ≫ soft.")
    else:
        print("  INTERMEDIATE: 0.25 ≤ top-1 ≤ 0.85.")
        print("  Soft probe is informative but not one-hot. B5 is *maybe* worth running.")
        print("  RECOMMENDATION: defer B5 unless variance/α inspection suggests prior is load-bearing.")


if __name__ == "__main__":
    main()
