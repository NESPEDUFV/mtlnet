"""Faithful STAN baseline trainer (single-task next_region, 5-fold CV).

Mirrors the protocol used by ``scripts/p1_region_head_ablation.py`` so the
results are directly comparable to in-house STL region heads:

    - StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=seed)
      stratified on the target check-in's category and grouped by userid.
    - AdamW(lr=1e-4, wd=0.01) + OneCycleLR(max_lr=3e-3) + grad-clip 1.0.
    - 50 epochs default, batch 2048.
    - Best-epoch selection on val Acc@10.
    - Output JSON layout matches the in-house ``region_head_*`` JSONs.

Usage::

    PYTHONPATH=src DATA_ROOT=... OUTPUT_DIR=... \\
        python -m research.baselines.stan.train \\
            --state alabama --folds 5 --epochs 50 \\
            --tag FAITHFUL_STAN_al_5f50ep
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import StratifiedGroupKFold

_root = Path(__file__).resolve().parents[3]
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.globals import DEVICE  # noqa: E402
from tracking.metrics import compute_classification_metrics  # noqa: E402
from utils.seed import seed_everything  # noqa: E402

from research.baselines.stan.etl import (  # noqa: E402
    centroids_path as etl_centroids_path,
    out_path as etl_out_path,
)
from research.baselines.stan.model import FaithfulSTAN, haversine_km  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("faithful_stan")

def load_tensors(state: str):
    df = pd.read_parquet(etl_out_path(state))
    # Infer the sequence length (STAN CONTEXT_LEN) from the prefix-expansion columns,
    # so the trainer follows whatever --context-len the ETL produced.
    seq_len = sum(1 for c in df.columns if c.startswith("poi_idx_"))
    poi = np.stack([df[f"poi_idx_{k}"].to_numpy(np.int64) for k in range(seq_len)], axis=1)
    lat = np.stack([df[f"lat_{k}"].to_numpy(np.float32) for k in range(seq_len)], axis=1)
    lon = np.stack([df[f"lon_{k}"].to_numpy(np.float32) for k in range(seq_len)], axis=1)
    tmin = np.stack([df[f"t_minutes_{k}"].to_numpy(np.int64) for k in range(seq_len)], axis=1)
    hour = np.stack([df[f"hour_of_week_{k}"].to_numpy(np.int64) for k in range(seq_len)], axis=1)
    y = df["target_region_idx"].to_numpy(np.int64)
    cat = df["target_category"].astype("category").cat.codes.to_numpy(np.int64)
    uid = df["userid"].to_numpy(np.int64)
    n_pois = int(poi[poi >= 0].max()) + 1

    centroids_df = pd.read_parquet(etl_centroids_path(state)).sort_values("region_idx")
    centroids = centroids_df[["centroid_lat", "centroid_lon"]].to_numpy(np.float32)
    n_regions = int(centroids.shape[0])
    # Review fix (2026-06-26): region_emb [R,D] and region_centroids [R,2] MUST share R,
    # else the matching layer broadcast crashes. Assert rather than silently bumping
    # n_regions above the centroid count (which would desync them).
    assert int(y.max()) + 1 <= n_regions, (
        f"target region idx {int(y.max())} >= n_regions(centroids) {n_regions} — "
        f"centroid/region index desync; rebuild ETL")

    return (
        torch.from_numpy(poi),
        torch.from_numpy(hour),
        torch.from_numpy(lat),
        torch.from_numpy(lon),
        torch.from_numpy(tmin),
        torch.from_numpy(y),
        torch.from_numpy(centroids),
        cat, uid, n_pois, n_regions, seq_len,
    )


def train_one_fold(poi, hour, lat, lon, tmin, y, dd_poi, train_idx, val_idx,
                   n_pois, n_regions, *, epochs, batch_size, seed,
                   d_model, dropout, lr, seq_length, patience,
                   amp="off", use_compile=False, compile_mode="default") -> dict:
    seed_everything(seed)
    # Determinism off here (warn_only=True earlier just emitted spam without
    # actual determinism since CuBLAS isn't deterministic by default).
    torch.use_deterministic_algorithms(False)

    # Pre-move all fold tensors to GPU once. Eliminates DataLoader IPC, fork
    # pickling, and per-batch H2D copies — the dominant overhead on small
    # datasets (AL: 12K rows). For CA/TX (~360–460K rows × 9 windows) the
    # tensor footprint is ~150 MB total, trivially fitting on the 80 GB H100.
    train_idx_t = torch.as_tensor(train_idx, dtype=torch.long)
    val_idx_t = torch.as_tensor(val_idx, dtype=torch.long)

    def _gather(t, idx):
        return t.index_select(0, idx).to(DEVICE, non_blocking=torch.cuda.is_available())

    poi_tr = _gather(poi, train_idx_t); hour_tr = _gather(hour, train_idx_t)
    lat_tr = _gather(lat, train_idx_t); lon_tr = _gather(lon, train_idx_t)
    tmin_tr = _gather(tmin, train_idx_t); y_tr = _gather(y, train_idx_t)
    poi_va = _gather(poi, val_idx_t); hour_va = _gather(hour, val_idx_t)
    lat_va = _gather(lat, val_idx_t); lon_va = _gather(lon, val_idx_t)
    tmin_va = _gather(tmin, val_idx_t); y_va = _gather(y, val_idx_t)

    n_train = poi_tr.shape[0]
    steps_per_epoch = max(1, (n_train + batch_size - 1) // batch_size)

    model = FaithfulSTAN(
        n_pois=n_pois, n_regions=n_regions,
        d_model=d_model, dropout=dropout, seq_length=seq_length,
    ).to(DEVICE)
    # dd_poi[n_pois+1, R] is precomputed once in run() and already on DEVICE.
    # Opt-E/B compile modes:
    #   default         -> dynamic=True fusion (compatible with opt-D's torch.unique)
    #   max-autotune    -> opt-E: autotuned Triton GEMM/reduction templates (dynamic)
    #   reduce-overhead -> opt-B: CUDA graphs (kills launch overhead). Needs static
    #                      shapes -> opt-D's data-dependent torch.unique is incompatible,
    #                      so distinct_poi is forced OFF for this mode.
    if use_compile and torch.cuda.is_available():
        if compile_mode == "reduce-overhead":
            model.distinct_poi = False
            model = torch.compile(model, dynamic=False, mode="reduce-overhead")
        elif compile_mode == "max-autotune":
            model = torch.compile(model, dynamic=True, mode="max-autotune")
        else:
            model = torch.compile(model, dynamic=True)

    # Audit fix #5 (2026-06-26): STAN's reference trains at a CONSTANT LR (StepLR γ=1)
    # with early-stopping on a real val plateau, NOT OneCycle (which annealed the LR to
    # ~0 by ep50 so the prior run's "best at 49/50" never plateaued -> under-trained).
    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    crit = nn.CrossEntropyLoss()

    # Speed options (opt-in; fp32 default = board protocol). amp in {off,bf16,fp16}.
    # bf16 needs no GradScaler; fp16 does. Quality is A/B-validated against fp32 before use.
    amp_on = amp in ("bf16", "fp16") and torch.cuda.is_available()
    amp_dtype = torch.bfloat16 if amp == "bf16" else torch.float16
    scaler = torch.amp.GradScaler("cuda", enabled=(amp == "fp16" and torch.cuda.is_available()))
    g = torch.Generator(device=DEVICE if torch.cuda.is_available() else "cpu")
    g.manual_seed(seed)

    def _sync():
        if torch.cuda.is_available():
            torch.cuda.synchronize()

    best_acc10 = -1.0
    best_epoch = -1
    best_state = None
    epochs_since_improve = 0
    n_val = poi_va.shape[0]
    n_steps = (n_train + batch_size - 1) // batch_size
    for epoch in range(epochs):
        # ---- OBSERVER: per-epoch + per-phase timing + per-epoch val Acc@10 ----
        t_ep = time.time()
        model.train()
        perm = torch.randperm(n_train, generator=g, device=poi_tr.device)
        loss_sum = torch.zeros((), device=poi_tr.device)
        for s in range(0, n_train, batch_size):
            idx = perm[s:s + batch_size]
            poi_b = poi_tr[idx]; hour_b = hour_tr[idx]
            lat_b = lat_tr[idx]; lon_b = lon_tr[idx]
            t_b = tmin_tr[idx]; y_b = y_tr[idx]
            optim.zero_grad(set_to_none=True)
            with torch.autocast("cuda", dtype=amp_dtype, enabled=amp_on):
                out = model(poi_b, hour_b, lat_b, lon_b, t_b, dd_poi)
                loss = crit(out, y_b)
            scaler.scale(loss).backward()
            scaler.unscale_(optim)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optim)
            scaler.update()
            loss_sum += loss.detach()
        _sync(); t_train = time.time() - t_ep

        # Opt-C (val-once): per-epoch val computes ONLY Acc@10 (for early-stop) — no
        # [n_val,R] logit cache or CPU offload (FL: 4703×~300K ≈ 15 GB of churn/epoch).
        # On improvement we snapshot the model state; full metrics are recomputed ONCE
        # at the end from the best-epoch state.
        t_v = time.time()
        model.eval()
        top10_correct = 0
        with torch.no_grad():
            for s in range(0, n_val, batch_size):
                e = s + batch_size
                with torch.autocast("cuda", dtype=amp_dtype, enabled=amp_on):
                    out = model(poi_va[s:e], hour_va[s:e], lat_va[s:e],
                                lon_va[s:e], tmin_va[s:e], dd_poi)
                top10 = out.float().topk(min(10, out.shape[-1]), dim=-1).indices  # [b, 10]
                top10_correct += (top10 == y_va[s:e].unsqueeze(1)).any(-1).sum().item()
        _sync(); t_val = time.time() - t_v
        acc10 = top10_correct / n_val
        improved = acc10 > best_acc10 + 1e-5
        if improved:
            best_acc10 = acc10
            best_epoch = epoch + 1
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            epochs_since_improve = 0
        else:
            epochs_since_improve += 1
        # OBSERVER: flush a per-epoch line so convergence + the train/val time split
        # are visible live (run with `python -u`); reveals which phase is the bottleneck.
        logger.info("    ep %3d/%d  val_Acc@10=%.4f  best=%.4f@%-3d  loss=%.4f  "
                    "| train %5.1fs (%d steps, %.0f ms/step)  val %4.1fs%s",
                    epoch + 1, epochs, acc10, best_acc10, best_epoch,
                    float(loss_sum) / max(1, n_steps), t_train, n_steps,
                    1000.0 * t_train / max(1, n_steps), t_val,
                    "  <-best" if improved else "")
        if epochs_since_improve >= patience:
            logger.info("    early-stop at epoch %d (best Acc@10=%.4f @ep%d, patience=%d)",
                        epoch + 1, best_acc10, best_epoch, patience)
            break

    # Opt-C: recompute full metrics ONCE from the best-epoch state (single val pass).
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    logits_chunks = []
    with torch.no_grad():
        for s in range(0, n_val, batch_size):
            e = s + batch_size
            with torch.autocast("cuda", dtype=amp_dtype, enabled=amp_on):
                out = model(poi_va[s:e], hour_va[s:e], lat_va[s:e],
                            lon_va[s:e], tmin_va[s:e], dd_poi)
            logits_chunks.append(out.float().cpu())
    best_logits = torch.cat(logits_chunks, dim=0)
    m = compute_classification_metrics(best_logits, y_va.cpu(),
                                       num_classes=n_regions, top_k=(5, 10))
    return dict(m, best_epoch=best_epoch, n_epochs_ran=epoch + 1)


def run(state: str, folds: int, epochs: int, batch_size: int, seed: int,
        d_model: int, dropout: float, lr: float, patience: int,
        tag: str | None, amp: str = "off", use_compile: bool = False,
        only_fold: int | None = None, compile_mode: str = "default") -> None:
    # Audit fix #6: true fp32 — disable TF32 too (board protocol).
    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.set_float32_matmul_precision("highest")
    poi, hour, lat, lon, tmin, y, centroids, cat, uid, n_pois, n_regions, seq_len = load_tensors(state)
    logger.info("Loaded %s: rows=%d  n_pois=%d  n_regions=%d  seq_len=%d  centroids=%s",
                state, poi.shape[0], n_pois, n_regions, seq_len, tuple(centroids.shape))

    # Precompute the POI->region distance matrix ONCE (numerically the same binned
    # bias as the per-batch haversine — GPS noise << 3 km bins — but removes the
    # matching layer's per-batch trig, the runtime bottleneck). dd_poi[n_pois, R];
    # pad row (index n_pois) = 0 (masked anyway). Each POI's lat/lon = any check-in's.
    flat_poi = poi.reshape(-1).numpy()
    flat_lat = lat.reshape(-1).numpy(); flat_lon = lon.reshape(-1).numpy()
    valid = flat_poi >= 0
    poi_lat = np.zeros(n_pois + 1, np.float32); poi_lon = np.zeros(n_pois + 1, np.float32)
    poi_lat[flat_poi[valid]] = flat_lat[valid]
    poi_lon[flat_poi[valid]] = flat_lon[valid]
    _cent = centroids.to(DEVICE)
    _plat = torch.from_numpy(poi_lat).to(DEVICE); _plon = torch.from_numpy(poi_lon).to(DEVICE)
    dd_poi = haversine_km(_plat[:, None], _plon[:, None],
                          _cent[None, :, 0], _cent[None, :, 1])        # [n_pois+1, R]
    dd_poi[n_pois].zero_()                                            # pad POI row
    logger.info("Precomputed dd_poi %s (%.2f GB)", tuple(dd_poi.shape),
                dd_poi.numel() * 4 / 1e9)

    sgkf = StratifiedGroupKFold(n_splits=max(2, folds), shuffle=True, random_state=seed)
    splits = list(sgkf.split(np.zeros(len(cat)), cat, groups=uid))[:folds]

    out_dir = Path("docs/results/baselines")
    out_dir.mkdir(parents=True, exist_ok=True)
    tag_s = f"_{tag}" if tag else ""
    # --only-fold k: run just split k -> per-fold JSON (for fold-parallel execution;
    # aggregate the 5 _fold{k}.json afterwards). Default = all folds in one process.
    fold_suffix = f"_fold{only_fold}" if only_fold is not None else ""
    out_file = out_dir / f"faithful_stan_{state}_{folds}f_{epochs}ep{tag_s}{fold_suffix}.json"
    fold_iter = [(only_fold, splits[only_fold])] if only_fold is not None else list(enumerate(splits))

    fold_metrics = []
    for fold_idx, (train_idx, val_idx) in fold_iter:
        t0 = time.time()
        m = train_one_fold(
            poi, hour, lat, lon, tmin, y, dd_poi, train_idx, val_idx,
            n_pois=n_pois, n_regions=n_regions,
            epochs=epochs, batch_size=batch_size, seed=seed + fold_idx,
            d_model=d_model, dropout=dropout, lr=lr,
            seq_length=seq_len, patience=patience,
            amp=amp, use_compile=use_compile, compile_mode=compile_mode,
        )
        elapsed = time.time() - t0
        fold_metrics.append(m)
        logger.info("  fold %d: Acc@1=%.4f Acc@5=%.4f Acc@10=%.4f MRR=%.4f F1=%.4f (%.1fs, best_ep=%d)",
                    fold_idx, m.get("accuracy", 0), m.get("top5_acc", 0), m.get("top10_acc", 0),
                    m.get("mrr", 0), m.get("f1", 0), elapsed, m.get("best_epoch", 0))

    agg = {}
    for k in ["accuracy", "top5_acc", "top10_acc", "mrr", "f1"]:
        vals = [m.get(k, 0.0) for m in fold_metrics]
        agg[f"{k}_mean"] = float(np.mean(vals))
        agg[f"{k}_std"] = float(np.std(vals))
    logger.info("AGGREGATE: " + " ".join(f"{k}={v:.4f}" for k, v in agg.items()))

    payload = {
        "state": state, "folds": folds, "epochs": epochs, "seed": seed,
        "n_regions": n_regions, "n_pois": n_pois, "seq_len": seq_len,
        "config": {"d_model": d_model, "dropout": dropout,
                   "lr": lr, "patience": patience, "batch_size": batch_size,
                   "schedule": "constant", "precision": ("fp32" if amp == "off" else amp),
                   "compiled": use_compile, "sequence": "STAN prefix-expansion"},
        "only_fold": only_fold,
        "per_fold": fold_metrics, "aggregate": agg,
    }
    out_file.write_text(json.dumps(payload, indent=2))
    logger.info("Saved: %s", out_file)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--epochs", type=int, default=200,
                   help="epoch CAP; early-stopping ends training on a real plateau")
    p.add_argument("--batch-size", type=int, default=2048)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--dropout", type=float, default=0.3)
    p.add_argument("--lr", type=float, default=1e-3,
                   help="CONSTANT learning rate (STAN-faithful; no OneCycle)")
    p.add_argument("--patience", type=int, default=20,
                   help="early-stop patience on val Acc@10")
    p.add_argument("--tag", type=str, default=None)
    p.add_argument("--amp", choices=["off", "bf16", "fp16"], default="off",
                   help="mixed precision (off=fp32, board default; bf16/fp16 = speed, "
                        "quality A/B-validated vs fp32 before reporting)")
    p.add_argument("--compile", dest="use_compile", action="store_true",
                   help="torch.compile the model (fp32-faithful speedup)")
    p.add_argument("--only-fold", type=int, default=None,
                   help="run ONLY split k (0..folds-1) -> per-fold JSON, for fold-parallel runs")
    p.add_argument("--compile-mode", choices=["default", "max-autotune", "reduce-overhead"],
                   default="default",
                   help="torch.compile mode (with --compile): default=dynamic fusion, "
                        "max-autotune=opt-E autotuned kernels, "
                        "reduce-overhead=opt-B CUDA graphs (forces distinct_poi off)")
    args = p.parse_args()
    run(args.state, args.folds, args.epochs, args.batch_size, args.seed,
        args.d_model, args.dropout, args.lr, args.patience, args.tag,
        amp=args.amp, use_compile=args.use_compile, only_fold=args.only_fold,
        compile_mode=args.compile_mode)


if __name__ == "__main__":
    main()
