"""P1 — Next-POI head ablation: target = placeid (poi_idx), not region.

Mirrors `scripts/p1_region_head_ablation.py` but with two changes:
  * num_classes = num_pois (large: ~12k AL, ~77k FL)
  * per-step input = substrate's POI embedding looked up by placeid

The probe answers the user's stated research question on the next-POI
axis: does the merge family (J) beat HGI on next-POI prediction, where
HGI's POI-stable representation literally cannot distinguish two visits
to the same POI?

Substrates (via --poi-emb-source):
  * `check2hgi`             → output/check2hgi/<state>/poi_embeddings.parquet
  * `hgi`                   → output/hgi/<state>/embeddings.parquet
  * `check2hgi_design_<x>`  → output/check2hgi_design_<x>/<state>/poi_embeddings.parquet

All three are 64-dim, indexed by `placeid`.

Usage::

    python scripts/p1_poi_head_ablation.py \\
        --state alabama --heads next_gru --folds 5 --epochs 50 --seed 42 \\
        --poi-emb-source check2hgi_design_j \\
        --tag T1_AL_design_j_next_poi_5f50ep
"""
from __future__ import annotations
import argparse
import json
import logging
import pickle as pkl
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader

from configs.globals import DEVICE
from configs.model import InputsConfig
from configs.paths import IoPaths
from data.dataset import POIDataset
from models.registry import _MODEL_REGISTRY, _ensure_registered  # type: ignore
from tracking.metrics import StreamingClsMetrics, compute_classification_metrics

logger = logging.getLogger("p1_poi")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

REPO = _root


def _poi_emb_path(state: str, source: str) -> Path:
    state_lc = state.lower()
    if source == "check2hgi":
        return REPO / "output/check2hgi" / state_lc / "poi_embeddings.parquet"
    if source == "hgi":
        return REPO / "output/hgi" / state_lc / "embeddings.parquet"
    if source.startswith("check2hgi_design_"):
        return REPO / "output" / source / state_lc / "poi_embeddings.parquet"
    raise ValueError(f"Unknown POI-emb source: {source}")


def _load_poi_emb(state: str, source: str) -> tuple[np.ndarray, dict]:
    """Return (poi_emb [n_pois, D], placeid_to_emb_row dict)."""
    path = _poi_emb_path(state, source)
    df = pd.read_parquet(path)
    emb_cols = [c for c in df.columns if c.isdigit()]
    emb = df[emb_cols].to_numpy(dtype=np.float32)
    placeids = df["placeid"].astype(np.int64).to_numpy()
    placeid_to_row = {int(p): i for i, p in enumerate(placeids)}
    return emb, placeid_to_row


def _build_poi_sequence_tensor(state: str, poi_emb_source: str,
                                emb_dim: int = 64) -> torch.Tensor:
    """[N_seq, 9, D] tensor: each step is the POI embedding of that step's placeid."""
    seq_path = REPO / "output/check2hgi" / state.lower() / "temp" / "sequences_next.parquet"
    seq_df = pd.read_parquet(seq_path)
    poi_emb, placeid_to_row = _load_poi_emb(state, poi_emb_source)

    n = len(seq_df)
    out = np.zeros((n, 9, emb_dim), dtype=np.float32)
    for i in range(9):
        col = f"poi_{i}"
        placeids = seq_df[col].astype(np.int64).to_numpy()
        mask = placeids != -1
        valid = placeids[mask]
        rows = pd.Series(valid).map(placeid_to_row).to_numpy()
        # Drop entries that don't map (shouldn't happen if substrate covers all POIs)
        valid_mask_local = ~pd.isna(rows)
        rows_clean = rows[valid_mask_local].astype(np.int64)
        idx_in_out = np.where(mask)[0][valid_mask_local]
        out[idx_in_out, i, :] = poi_emb[rows_clean]
    return torch.from_numpy(out)


def _load_data(state: str, poi_emb_source: str):
    """Load (x_tensor, y_poi_tensor, userids, emb_dim, n_pois).

    Derives the placeid → poi_idx mapping at runtime from sequences_next.parquet
    + the c2hgi graph's placeid_to_idx, then filters out unmapped rows so
    AL/AZ/FL all work without an ahead-of-time `next_poi.parquet` artefact.
    """
    state_lc = state.lower()
    seq_path = REPO / "output/check2hgi" / state_lc / "temp" / "sequences_next.parquet"
    graph_path = REPO / "output/check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    seq_df = pd.read_parquet(seq_path)
    with open(graph_path, "rb") as f:
        g = pkl.load(f)
    placeid_to_idx = g["placeid_to_idx"]
    target_int = pd.to_numeric(seq_df["target_poi"], errors="coerce").astype("Int64")
    poi_idx = target_int.map(placeid_to_idx)
    mask = poi_idx.notna().to_numpy()
    if not mask.all():
        n_drop = (~mask).sum()
        logger.info(f"filtering {n_drop}/{len(seq_df)} rows with unmapped target_poi")

    # Build per-step substrate POI emb input over ALL rows, then filter.
    x_full = _build_poi_sequence_tensor(state, poi_emb_source, emb_dim=64)
    assert x_full.shape[0] == len(seq_df), (
        f"sequence row mismatch x={x_full.shape[0]} vs seq_df={len(seq_df)}"
    )
    x = x_full[torch.from_numpy(mask)]
    y_poi = poi_idx[mask].astype(np.int64).to_numpy()
    userids = seq_df.loc[mask, "userid"].astype(np.int64).to_numpy()
    n_pois = int(y_poi.max()) + 1
    n_seq = len(y_poi)
    y_poi_tensor = torch.from_numpy(y_poi)
    logger.info(f"x={tuple(x.shape)}, n_pois={n_pois}, n_seqs={n_seq}, source={poi_emb_source}")
    return x, y_poi_tensor, userids, 64, n_pois


def _instantiate_head(head_name: str, emb_dim: int, n_classes: int,
                       seq_length: int, overrides: dict):
    import inspect
    if head_name not in _MODEL_REGISTRY:
        raise ValueError(f"Unknown head: {head_name}")
    target_cls = _MODEL_REGISTRY[head_name]
    sig = inspect.signature(target_cls.__init__)
    accepted = set(sig.parameters.keys()) - {"self"}
    kwargs = {"embed_dim": emb_dim, "num_classes": n_classes}
    if "seq_length" in accepted:
        kwargs["seq_length"] = seq_length
    for k, v in overrides.items():
        if k in accepted:
            try:
                if "." in v:
                    kwargs[k] = float(v)
                else:
                    kwargs[k] = int(v)
            except ValueError:
                kwargs[k] = v
    return target_cls(**kwargs)


def _train_one_fold(model, train_dl, val_dl, optimizer, scheduler, criterion,
                     epochs: int, n_classes: int, head_name: str):
    best = {"top10_acc": -1.0, "epoch": 0, "metrics": None}
    for ep in range(1, epochs + 1):
        model.train()
        for x, y in train_dl:
            x = x.to(DEVICE); y = y.to(DEVICE)
            logits = model(x) if head_name != "next_getnext_hard" else model(x)  # no aux
            loss = criterion(logits, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if scheduler is not None:
                scheduler.step()  # OneCycleLR is a per-step scheduler
        # eval
        model.eval()
        # POI cardinality is the LARGEST in the study — larger than the region head's, which
        # already needed a 20 GB workaround at CA/TX. This used to cat the full [N_val, C] with
        # no guard of any kind; it survives only at small states, which is exactly where the
        # banked poi_head_* results come from. Stream above the hand-rolled cutoff (per-row
        # reductions, identical dict, O(N) memory), keep the full path below it where the
        # torchmetrics branch is the only equivalent one.
        _stream = StreamingClsMetrics.should_stream(n_classes)
        # Banked path (poi_head_* results), so the ambiguity certificate is measured here
        # every epoch rather than inferred from another head or another state.
        _acc = (StreamingClsMetrics(n_classes, top_k=(5, 10), diagnose_ties=True)
                if _stream else None)
        all_logits, all_targets = [], []
        with torch.no_grad():
            for x, y in val_dl:
                x = x.to(DEVICE); y = y.to(DEVICE)
                out = model(x)
                if _stream:
                    _acc.update(out, y)
                else:
                    all_logits.append(out)
                    all_targets.append(y)
        if _stream:
            m = _acc.compute()
        else:
            logits = torch.cat(all_logits)
            targets = torch.cat(all_targets)
            m = compute_classification_metrics(logits, targets, num_classes=n_classes, top_k=(5, 10))
        if m.get("top10_acc", 0) > best["top10_acc"]:
            best = {"top10_acc": m["top10_acc"], "epoch": ep, "metrics": m}
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--heads", nargs="+", default=["next_gru"])
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--batch-size", dest="batch_size", type=int, default=2048)
    ap.add_argument("--max-lr", dest="max_lr", type=float, default=3e-3)
    ap.add_argument("--poi-emb-source", dest="poi_emb_source", required=True)
    ap.add_argument("--override-hparams", nargs="*", default=[])
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    _ensure_registered()
    overrides = {}
    for kv in args.override_hparams:
        if "=" in kv:
            k, v = kv.split("=", 1); overrides[k] = v

    torch.manual_seed(args.seed); np.random.seed(args.seed)

    x, y_poi, userids, emb_dim, n_pois = _load_data(args.state, args.poi_emb_source)
    seq_length = x.shape[1]

    # StratifiedGroupKFold by userid, but stratification on poi_idx is meaningless
    # at 76k classes. Use GroupKFold-like split via SGKF on a coarse y bucket.
    # Bucket poi_idx by 1000 to approximate stratification.
    y_bucket = (y_poi.numpy() // 1000).astype(np.int64) if hasattr(y_poi, "numpy") else (y_poi // 1000).astype(np.int64)
    sgkf = StratifiedGroupKFold(n_splits=args.folds, shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(np.zeros(len(y_poi)), y_bucket, groups=userids))

    out_path = REPO / "docs/results/P1" / f"poi_head_{args.state}_5f{args.epochs}ep_{args.tag}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results = {"heads": {}}

    for head_name in args.heads:
        logger.info(f"=== HEAD {head_name} ===")
        per_fold = []
        for fold_i, (train_idx, val_idx) in enumerate(splits):
            x_tr, x_v = x[train_idx], x[val_idx]
            y_tr, y_v = y_poi[train_idx], y_poi[val_idx]
            train_dl = DataLoader(POIDataset(x_tr.numpy(), y_tr.numpy()), batch_size=args.batch_size, shuffle=True)
            val_dl = DataLoader(POIDataset(x_v.numpy(), y_v.numpy()), batch_size=args.batch_size, shuffle=False)
            model = _instantiate_head(head_name, emb_dim, n_pois, seq_length, overrides).to(DEVICE)
            optimizer = torch.optim.AdamW(model.parameters(), lr=args.max_lr / 25,
                                          weight_decay=0.05)
            scheduler = torch.optim.lr_scheduler.OneCycleLR(
                optimizer, max_lr=args.max_lr,
                total_steps=args.epochs * len(train_dl))
            # label_smoothing matches p1_region_head_ablation.py; mitigates head-class
            # bias under the Zipfian POI visit distribution (n_pois ~ 12k–77k).
            criterion = CrossEntropyLoss(label_smoothing=0.1)
            best = _train_one_fold(model, train_dl, val_dl, optimizer, scheduler, criterion,
                                    args.epochs, n_pois, head_name)
            logger.info(f"  fold {fold_i}: best={best['metrics']} @ ep={best['epoch']}")
            per_fold.append(best["metrics"])
        results["heads"][head_name] = {"per_fold": per_fold}

    out_path.write_text(json.dumps(results, indent=2, default=float))
    logger.info(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
