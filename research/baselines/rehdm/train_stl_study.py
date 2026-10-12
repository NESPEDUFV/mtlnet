"""STL ReHDM trainer under the *study* protocol (5-fold StratifiedGroupKFold).

Designed for cell-for-cell comparison with the rest of the study's STL
baselines (`next_gru`, `next_stan`, etc.). Reads the in-house
`output/<engine>/<state>/folds/fold_indices_mtl.pt` package directly:

- `task_tensors['next']['x']`: float32 [N, 9, emb_dim]  (per-row 9-step window)
- `task_tensors['next']['y']`: int64  [N]               (region target)
- `fold_indices['next']`: list of 5 (train_idx, val_idx) tuples

Two deviations from `train_stl.py`'s paper-protocol path:

1. **Fold-based** (5 StratifiedGroupKFold splits) instead of seeded chronological
   replication. This matches every other study STL row in the comparison table.
2. **Intra-user collaborators only** (`r=0`). Inter-user (`r=1`) is dropped
   because the per-row userid is the only identifying signal in the fold
   tensors — there is no per-position POI to mine "shared-POI" collaborators.
   Time-precedence is also dropped (StratifiedGroupKFold breaks temporal
   ordering by design). Both deviations are documented in the baseline page.

Output JSONs land at
`docs/results/baselines/<tag>_run{0..4}.json`
+ `<tag>_summary.json`.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

from research.baselines.rehdm.model_stl import ReHDMSTL, ReHDMSTLConfig
from research.baselines.rehdm.train import set_seed, _device


def load_study_data(engine: str, state: str, output_root: Path):
    """Load per-row 9-step embeddings, region target, category target, userid.

    Returns x [N, 9, emb_dim], y_region [N], y_cat [N], userids [N].
    Stratification (y_cat) and grouping (userids) match
    `p1_region_head_ablation.py:451`.
    """
    import pandas as pd
    eng_base = output_root / engine / state.lower() / "input"
    region_src = output_root / "check2hgi" / state.lower() / "input" / "next_region.parquet"
    seq_src = output_root / engine / state.lower() / "temp" / "sequences_next.parquet"
    df_n = pd.read_parquet(eng_base / "next.parquet")
    df_r = pd.read_parquet(region_src)
    df_s = pd.read_parquet(seq_src)
    assert len(df_r) == len(df_n) == len(df_s), \
        f"row mismatch: r={len(df_r)} n={len(df_n)} s={len(df_s)}"
    df_n["userid"] = df_n["userid"].astype(np.int64)
    df_r["userid"] = df_r["userid"].astype(np.int64)
    df_s["userid"] = df_s["userid"].astype(np.int64)
    if engine != "check2hgi":
        assert (df_n["userid"].values == df_r["userid"].values).all(), \
            "userid order mismatch — region targets cannot align with engine embeddings"
    assert (df_n["userid"].values == df_s["userid"].values).all(), \
        "userid order mismatch with sequences_next.parquet"
    emb_cols = [c for c in df_n.columns if c.isdigit()]
    flat = df_n[emb_cols].to_numpy(dtype=np.float32)
    n_rows, seq_len = flat.shape[0], 9
    emb_dim = len(emb_cols) // seq_len
    assert emb_dim * seq_len == len(emb_cols), f"emb_cols={len(emb_cols)} not divisible by 9"
    x = flat.reshape(n_rows, seq_len, emb_dim)
    y_region = df_r["region_idx"].to_numpy(dtype=np.int64)
    raw_cat = df_n["next_category"].to_numpy()
    cat_to_idx = {c: i for i, c in enumerate(sorted(set(raw_cat.tolist())))}
    y_cat = np.array([cat_to_idx[c] for c in raw_cat], dtype=np.int64)
    userids = df_n["userid"].to_numpy(dtype=np.int64)
    poi_cols = [f"poi_{i}" for i in range(seq_len)]
    poi_seq = df_s[poi_cols].to_numpy(dtype=np.int64)
    return torch.from_numpy(x), torch.from_numpy(y_region), y_cat, userids, poi_seq


class StudySTLStore:
    def __init__(self, x: torch.Tensor, y: torch.Tensor, userids: np.ndarray,
                 poi_seq: np.ndarray, train_idx: np.ndarray, val_idx: np.ndarray,
                 max_inter_pool: int = 32):
        self.x = x.float()           # [N, 9, emb_dim]
        self.y = y.long()            # [N]
        self.users = userids.astype(np.int64)
        self.poi_seq = poi_seq.astype(np.int64)  # [N, 9]
        self.N, self.T, self.emb_dim = self.x.shape
        self.max_len = self.T

        self.train_idx = np.asarray(train_idx, dtype=np.int64)
        self.val_idx = np.asarray(val_idx, dtype=np.int64)

        # Train-fold indices, by user (intra-user pool) and by POI (inter-user pool source).
        self.user_to_train_rows: dict[int, list[int]] = defaultdict(list)
        self.poi_to_train_rows: dict[int, list[int]] = defaultdict(list)
        for ri in self.train_idx:
            self.user_to_train_rows[int(self.users[ri])].append(int(ri))
            for p in set(self.poi_seq[ri].tolist()):
                if p >= 0:
                    self.poi_to_train_rows[int(p)].append(int(ri))

        # Precompute per-row collaborator pools (caps memory + amortises lookup).
        self._intra_pool: dict[int, list[int]] = {}
        self._inter_pool: dict[int, list[int]] = {}
        all_idx = np.concatenate([self.train_idx, self.val_idx])
        for ri in all_idx:
            ri = int(ri)
            u = int(self.users[ri])
            self._intra_pool[ri] = [r for r in self.user_to_train_rows[u] if r != ri]
            seen, pool = set(), []
            for p in set(self.poi_seq[ri].tolist()):
                if p < 0:
                    continue
                for r in self.poi_to_train_rows.get(p, ()):
                    if r in seen or r == ri:
                        continue
                    if int(self.users[r]) == u:
                        continue   # exclude same-user (those are intra-user)
                    seen.add(r); pool.append(r)
                    if len(pool) >= max_inter_pool:
                        break
                if len(pool) >= max_inter_pool:
                    break
            self._inter_pool[ri] = pool

    def collaborators(self, ri: int, max_intra: int, max_inter: int,
                      rng: random.Random | None = None):
        """Intra-user (same userid in train) + inter-user (shared POI, different userid).

        Cold-user val rows: intra is empty by construction (StratifiedGroupKFold);
        inter still works because POI overlap doesn't require user overlap.
        Time-precedence is dropped (StratifiedGroupKFold is non-temporal).
        """
        intra_pool = self._intra_pool[ri]
        if len(intra_pool) > max_intra:
            intra = (rng or random).sample(intra_pool, max_intra)
        else:
            intra = intra_pool[:max_intra]
        inter_pool = self._inter_pool[ri]
        if len(inter_pool) > max_inter:
            inter = (rng or random).sample(inter_pool, max_inter)
        else:
            inter = inter_pool[:max_inter]
        return intra, inter


class StudySTLDataset(Dataset):
    def __init__(self, store: StudySTLStore, ids):
        self.store = store; self.ids = list(ids)
    def __len__(self):
        return len(self.ids)
    def __getitem__(self, i):
        return int(self.ids[i])


def _row_mask(store: "StudySTLStore", ids):
    # Derive a real attention mask from poi_seq: positions with poi_idx >= 0 are valid
    # check-ins, padded positions are 0. Avoids the theta-query pooling and
    # POI-level transformer attending to zero-embedding pad cells.
    psq = store.poi_seq[ids]
    return torch.from_numpy((psq >= 0).astype(np.float32))


def make_collate_study(store: StudySTLStore, max_intra: int, max_inter: int, training: bool):
    rng = None if training else random.Random(0)

    def collate(batch_ids):
        b = len(batch_ids)
        target_feats = torch.stack([store.x[i] for i in batch_ids])
        target_mask = _row_mask(store, np.asarray(batch_ids, dtype=np.int64))
        targets = torch.stack([store.y[i] for i in batch_ids])

        if (max_intra + max_inter) == 0:
            return target_feats, target_mask, None, None, None, None, targets

        all_collab, edges, seen = [], [], {}
        for ti, ri in enumerate(batch_ids):
            intra, inter = store.collaborators(ri, max_intra, max_inter, rng=rng)
            for c in intra:
                if c not in seen:
                    seen[c] = len(all_collab); all_collab.append(c)
                edges.append((ti, seen[c], 0))
            for c in inter:
                if c not in seen:
                    seen[c] = len(all_collab); all_collab.append(c)
                edges.append((ti, seen[c], 1))
        if not all_collab:
            return target_feats, target_mask, None, None, None, None, targets
        c_feats = torch.stack([store.x[c] for c in all_collab])
        c_mask = _row_mask(store, np.asarray(all_collab, dtype=np.int64))
        adj = torch.zeros(b, len(all_collab))
        et = torch.zeros(b, len(all_collab), dtype=torch.long)
        for ti, ci, rt in edges:
            adj[ti, ci] = 1.0; et[ti, ci] = rt
        return target_feats, target_mask, c_feats, c_mask, adj, et, targets
    return collate


@torch.no_grad()
def evaluate(model, store, ids, batch_size, device, max_intra=3, max_inter=3):
    model.eval()
    _mp_ctx = "fork" if not torch.cuda.is_available() else None
    loader = DataLoader(
        StudySTLDataset(store, ids), batch_size=batch_size, shuffle=False,
        num_workers=2, persistent_workers=True,
        pin_memory=torch.cuda.is_available(),
        multiprocessing_context=_mp_ctx,
        collate_fn=make_collate_study(store, max_intra, max_inter, training=False),
    )
    n = c1 = c5 = c10 = 0; mrr = 0.0
    for batch in loader:
        tf, tm, cf, cm, adj, et, y = batch
        tf = tf.to(device); tm = tm.to(device); y = y.to(device)
        if cf is not None:
            cf = cf.to(device); cm = cm.to(device); adj = adj.to(device); et = et.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=torch.cuda.is_available()):
            logits = model(tf, tm, cf, cm, adj, et)
        logits = logits.float()
        ranks = (-logits).argsort(-1)
        pos = (ranks == y.unsqueeze(1)).nonzero()[:, 1] + 1
        c1 += (pos <= 1).sum().item(); c5 += (pos <= 5).sum().item(); c10 += (pos <= 10).sum().item()
        mrr += (1.0 / pos.float()).sum().item(); n += y.numel()
    return {"acc@1": c1/max(n,1), "acc@5": c5/max(n,1),
            "acc@10": c10/max(n,1), "mrr": mrr/max(n,1), "n": n}


def train_one_fold(engine, state, fold_idx, train_idx, val_idx, x, y, userids, poi_seq,
                   epochs, batch_size, lr, max_lr, max_intra, max_inter, seed, n_regions,
                   results_dir, tag):
    set_seed(seed); device = _device()
    print(f"[stl-study] fold={fold_idx} engine={engine} state={state} device={device}")
    store = StudySTLStore(x, y, userids, poi_seq, train_idx, val_idx)

    cfg = ReHDMSTLConfig(n_regions=n_regions, emb_dim=store.emb_dim)
    model = ReHDMSTL(cfg).to(device)
    print(f"[stl-study] params={sum(p.numel() for p in model.parameters())/1e6:.2f}M "
          f"train={len(store.train_idx)} val={len(store.val_idx)}")

    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.set_float32_matmul_precision("high")
    _mp_ctx = "fork" if not torch.cuda.is_available() else None
    train_loader = DataLoader(
        StudySTLDataset(store, store.train_idx), batch_size=batch_size, shuffle=True,
        collate_fn=make_collate_study(store, max_intra, max_inter, training=True),
        num_workers=4, persistent_workers=True,
        pin_memory=torch.cuda.is_available(),
        multiprocessing_context=_mp_ctx,
    )
    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        optim, max_lr=max_lr, total_steps=max(1, len(train_loader)) * epochs,
    )
    best_val = -1.0; best_metrics = None
    for ep in range(epochs):
        model.train(); t0 = time.time(); loss_sum = 0.0; nseen = 0
        for batch in train_loader:
            tf, tm, cf, cm, adj, et, yb = batch
            tf = tf.to(device); tm = tm.to(device); yb = yb.to(device)
            if cf is not None:
                cf = cf.to(device); cm = cm.to(device); adj = adj.to(device); et = et.to(device)
            optim.zero_grad()
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=torch.cuda.is_available()):
                logits = model(tf, tm, cf, cm, adj, et)
                loss = F.cross_entropy(logits, yb)
            if not torch.isfinite(loss):
                continue
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                optim.zero_grad(); continue
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optim.step(); sched.step()
            loss_sum += loss.item() * yb.size(0); nseen += yb.size(0)
        val = evaluate(model, store, store.val_idx, batch_size, device, max_intra, max_inter)
        print(f"[stl-study] fold={fold_idx} ep={ep+1}/{epochs} "
              f"loss={loss_sum/max(1,nseen):.4f} val_acc@10={val['acc@10']:.4f} "
              f"mrr={val['mrr']:.4f} dt={time.time()-t0:.1f}s")
        if val["acc@10"] > best_val:
            best_val = val["acc@10"]; best_metrics = val

    out = {"tag": tag, "state": state, "engine": engine, "fold": fold_idx,
           "config": cfg.__dict__, "best_val_acc@10": best_val, "metrics": best_metrics}
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / f"{tag}_fold{fold_idx}.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"[stl-study] wrote {tag}_fold{fold_idx}.json")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--engine", required=True, choices=["check2hgi", "hgi"])
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch-size", type=int, default=2048)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--max-lr", type=float, default=5e-4)
    p.add_argument("--max-intra", type=int, default=3)
    p.add_argument("--max-inter", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output-root", default=os.environ.get("OUTPUT_DIR", "output"))
    p.add_argument("--results-dir", default="docs/results/baselines")
    p.add_argument("--tag", required=True)
    args = p.parse_args()

    from sklearn.model_selection import StratifiedGroupKFold
    out_root = Path(args.output_root); res_dir = Path(args.results_dir)
    x, y, y_cat, userids, poi_seq = load_study_data(args.engine, args.state, out_root)
    n_regions = int(y.max().item()) + 1
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=args.seed)
    folds = list(sgkf.split(np.zeros(len(y_cat)), y_cat, groups=userids))
    print(f"[stl-study] N={x.shape[0]} T={x.shape[1]} emb_dim={x.shape[2]} "
          f"folds={len(folds)} n_regions={n_regions}")

    runs = []
    for fi, (tr, va) in enumerate(folds):
        runs.append(train_one_fold(
            engine=args.engine, state=args.state.lower(), fold_idx=fi,
            train_idx=tr, val_idx=va, x=x, y=y, userids=userids, poi_seq=poi_seq,
            epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, max_lr=args.max_lr,
            max_intra=args.max_intra, max_inter=args.max_inter, seed=args.seed,
            n_regions=n_regions, results_dir=res_dir, tag=args.tag,
        ))
    accs1 = [r["metrics"]["acc@1"] for r in runs if r["metrics"]]
    accs5 = [r["metrics"]["acc@5"] for r in runs if r["metrics"]]
    accs10 = [r["metrics"]["acc@10"] for r in runs if r["metrics"]]
    mrrs = [r["metrics"]["mrr"] for r in runs if r["metrics"]]
    summary = {
        "tag": args.tag, "state": args.state.lower(), "engine": args.engine,
        "protocol": "5-fold StratifiedGroupKFold (study protocol)",
        "n_folds": len(runs),
        "acc@1_mean":  float(np.mean(accs1)),
        "acc@1_std":   float(np.std(accs1, ddof=1)) if len(accs1) > 1 else None,
        "acc@5_mean":  float(np.mean(accs5)),
        "acc@5_std":   float(np.std(accs5, ddof=1)) if len(accs5) > 1 else None,
        "acc@10_mean": float(np.mean(accs10)),
        "acc@10_std":  float(np.std(accs10, ddof=1)) if len(accs10) > 1 else None,
        "mrr_mean":    float(np.mean(mrrs)),
        "mrr_std":     float(np.std(mrrs, ddof=1)) if len(mrrs) > 1 else None,
    }
    with open(res_dir / f"{args.tag}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[stl-study] summary -> {summary}")


if __name__ == "__main__":
    main()
