"""Trainer for the STL ReHDM variant (precomputed-embedding input)."""
from __future__ import annotations

import argparse
import json
import os
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

from research.baselines.rehdm.model_stl import ReHDMSTL, ReHDMSTLConfig
from research.baselines.rehdm.train import set_seed, _device, _move


class STLTrajectoryStore:
    """Per-trajectory feature arrays + collaborator-pool cache."""

    def __init__(self, df: pd.DataFrame, max_len: int):
        self.max_len = max_len
        feat_cols = [c for c in df.columns if c.startswith("e") and c[1:].isdigit()]
        self.feat_cols = feat_cols
        self.emb_dim = len(feat_cols)

        df = df.sort_values(["traj_idx", "pos_in_traj"]).reset_index(drop=True)
        traj_ids_all = sorted(df["traj_idx"].unique().tolist())

        self.feats: dict[int, np.ndarray] = {}
        self.lengths: dict[int, int] = {}
        self.targets: dict[int, int] = {}
        self.users: dict[int, int] = {}
        self.start_t: dict[int, np.int64] = {}
        self.end_t: dict[int, np.int64] = {}
        self.poi_set: dict[int, set] = {}
        self.split: dict[int, str] = {}

        ts = df["datetime"].astype("int64").to_numpy() // 10**9
        feat_mat = df[feat_cols].to_numpy(dtype=np.float32)
        for tid, g in df.groupby("traj_idx", sort=False):
            if len(g) < 2:
                continue
            ix = g.index.to_numpy()
            total = min(len(ix), max_len + 1)
            input_len = total - 1
            arr = np.zeros((max_len, self.emb_dim), dtype=np.float32)
            arr[:input_len] = feat_mat[ix[:input_len]]
            self.feats[int(tid)] = arr
            self.lengths[int(tid)] = input_len
            self.targets[int(tid)] = int(g["region_idx"].to_numpy()[input_len])
            self.users[int(tid)] = int(g["user_idx"].to_numpy()[0])
            self.start_t[int(tid)] = int(ts[ix[0]])
            self.end_t[int(tid)] = int(ts[ix[input_len - 1]])
            self.poi_set[int(tid)] = set(g["poi_idx"].to_numpy()[:input_len].tolist())
            self.split[int(tid)] = g["split"].iloc[0]

        self.traj_ids = [t for t in traj_ids_all if t in self.split]
        self.train_ids = [t for t in self.traj_ids if self.split[t] == "train"]
        self.val_ids = [t for t in self.traj_ids if self.split[t] == "val"]
        self.test_ids = [t for t in self.traj_ids if self.split[t] == "test"]

        self.user_to_train_traj: dict[int, list[int]] = defaultdict(list)
        self.poi_to_train_traj: dict[int, list[int]] = defaultdict(list)
        for tid in self.train_ids:
            self.user_to_train_traj[self.users[tid]].append(tid)
            for p in self.poi_set[tid]:
                self.poi_to_train_traj[p].append(tid)

    def precompute_collab_pools(self, max_inter_pool: int = 32):
        self._intra_pool: dict[int, list[int]] = {}
        self._inter_pool: dict[int, list[int]] = {}
        for tid in self.traj_ids:
            start = self.start_t[tid]
            u = self.users[tid]
            self._intra_pool[tid] = [
                t for t in self.user_to_train_traj[u]
                if t != tid and self.end_t[t] < start
            ]
            seen, pool = set(), []
            for p in self.poi_set[tid]:
                for t in self.poi_to_train_traj[p]:
                    if t in seen or t == tid:
                        continue
                    if self.users[t] == u:
                        continue
                    if self.end_t[t] >= start:
                        continue
                    seen.add(t); pool.append(t)
                    if len(pool) >= max_inter_pool:
                        break
                if len(pool) >= max_inter_pool:
                    break
            self._inter_pool[tid] = pool

    def collaborators(self, target_tid, max_intra, max_inter, rng=None):
        intra = self._intra_pool[target_tid][-max_intra:]
        pool = self._inter_pool[target_tid]
        if len(pool) > max_inter:
            inter = (rng or random).sample(pool, max_inter)
        else:
            inter = pool[:max_inter]
        return intra, inter

    def stack(self, tids):
        feats = torch.from_numpy(np.stack([self.feats[t] for t in tids]))
        mask = torch.zeros(len(tids), self.max_len, dtype=torch.float32)
        for i, t in enumerate(tids):
            mask[i, : self.lengths[t]] = 1.0
        return feats, mask


class STLDataset(Dataset):
    def __init__(self, store, ids):
        self.store = store; self.ids = ids
    def __len__(self):
        return len(self.ids)
    def __getitem__(self, i):
        return self.ids[i]


def make_collate_stl(store, max_intra, max_inter, training):
    rng = None if training else random.Random(0)
    def collate(batch_tids):
        target_feats, target_mask = store.stack(batch_tids)
        targets = torch.tensor([store.targets[t] for t in batch_tids], dtype=torch.long)
        if not training or (max_intra + max_inter) == 0:
            return target_feats, target_mask, None, None, None, None, targets

        all_collab, edges, seen = [], [], {}
        for ti, tid in enumerate(batch_tids):
            intra, inter = store.collaborators(tid, max_intra, max_inter, rng=rng)
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

        c_feats, c_mask = store.stack(all_collab)
        adj = torch.zeros(len(batch_tids), len(all_collab))
        et = torch.zeros(len(batch_tids), len(all_collab), dtype=torch.long)
        for ti, ci, rt in edges:
            adj[ti, ci] = 1.0; et[ti, ci] = rt
        return target_feats, target_mask, c_feats, c_mask, adj, et, targets
    return collate


@torch.no_grad()
def evaluate(model, store, ids, batch_size, device, max_intra=3, max_inter=3):
    model.eval()
    loader = DataLoader(
        STLDataset(store, ids), batch_size=batch_size, shuffle=False,
        collate_fn=make_collate_stl(store, max_intra, max_inter, training=True),
    )
    n = c1 = c5 = c10 = 0
    mrr = 0.0
    for batch in loader:
        tf, tm, cf, cm, adj, et, y = batch
        tf = tf.to(device); tm = tm.to(device); y = y.to(device)
        if cf is not None:
            cf = cf.to(device); cm = cm.to(device); adj = adj.to(device); et = et.to(device)
        logits = model(tf, tm, cf, cm, adj, et)
        ranks = (-logits).argsort(-1)
        pos = (ranks == y.unsqueeze(1)).nonzero()[:, 1] + 1
        c1 += (pos <= 1).sum().item(); c5 += (pos <= 5).sum().item(); c10 += (pos <= 10).sum().item()
        mrr += (1.0 / pos.float()).sum().item(); n += y.numel()
    return {"acc@1": c1/max(n,1), "acc@5": c5/max(n,1),
            "acc@10": c10/max(n,1), "mrr": mrr/max(n,1), "n": n}


def train_one_run(state, engine, seed, epochs, batch_size, lr, max_lr, max_len,
                  max_intra, max_inter, output_root, results_dir, tag, run_idx):
    set_seed(seed); device = _device()
    print(f"[stl] seed={seed} device={device}")
    in_dir = output_root / "baselines" / "rehdm" / f"{state}_{engine}"
    df = pd.read_parquet(in_dir / "inputs.parquet")
    vocab = json.loads((in_dir / "vocab.json").read_text())

    store = STLTrajectoryStore(df, max_len=max_len)
    store.precompute_collab_pools(max_inter_pool=max(32, max_inter * 4))
    print(f"[stl] traj train={len(store.train_ids)} val={len(store.val_ids)} test={len(store.test_ids)}")

    cfg = ReHDMSTLConfig(n_regions=vocab["n_regions"], emb_dim=vocab["emb_dim"])
    model = ReHDMSTL(cfg).to(device)
    print(f"[stl] params={sum(p.numel() for p in model.parameters())/1e6:.2f}M")

    train_loader = DataLoader(
        STLDataset(store, store.train_ids), batch_size=batch_size, shuffle=True,
        collate_fn=make_collate_stl(store, max_intra, max_inter, training=True),
    )
    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    steps = max(1, len(train_loader)) * epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(optim, max_lr=max_lr, total_steps=steps)

    best_val = -1.0; best_test = None
    for ep in range(epochs):
        model.train(); t0 = time.time(); loss_sum = 0.0
        for batch in train_loader:
            tf, tm, cf, cm, adj, et, y = batch
            tf = tf.to(device); tm = tm.to(device); y = y.to(device)
            if cf is not None:
                cf = cf.to(device); cm = cm.to(device); adj = adj.to(device); et = et.to(device)
            optim.zero_grad()
            logits = model(tf, tm, cf, cm, adj, et)
            loss = F.cross_entropy(logits, y)
            if not torch.isfinite(loss): continue
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                optim.zero_grad(); continue
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optim.step(); sched.step()
            loss_sum += loss.item() * y.size(0)
        val = evaluate(model, store, store.val_ids, batch_size, device, max_intra, max_inter)
        print(f"[stl] ep={ep+1}/{epochs} loss={loss_sum/max(1,len(store.train_ids)):.4f} "
              f"val_acc@10={val['acc@10']:.4f} mrr={val['mrr']:.4f} dt={time.time()-t0:.1f}s")
        if val["acc@10"] > best_val:
            best_val = val["acc@10"]
            best_test = evaluate(model, store, store.test_ids, batch_size, device, max_intra, max_inter)

    out = {"tag": tag, "state": state, "engine": engine, "run": run_idx, "seed": seed,
           "config": cfg.__dict__, "best_val_acc@10": best_val, "test": best_test, "vocab": vocab}
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / f"{tag}_run{run_idx}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[stl] wrote {out_path}")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--engine", required=True, choices=["check2hgi", "hgi"])
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--max-lr", type=float, default=5e-4)
    p.add_argument("--max-len", type=int, default=20)
    p.add_argument("--max-intra", type=int, default=3)
    p.add_argument("--max-inter", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output-root", default=os.environ.get("OUTPUT_DIR", "output"))
    p.add_argument("--results-dir", default="docs/results/baselines")
    p.add_argument("--tag", required=True)
    args = p.parse_args()

    out_root = Path(args.output_root); res_dir = Path(args.results_dir)
    runs = []
    for i in range(args.folds):
        runs.append(train_one_run(
            state=args.state.lower(), engine=args.engine, seed=args.seed + i,
            epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, max_lr=args.max_lr,
            max_len=args.max_len, max_intra=args.max_intra, max_inter=args.max_inter,
            output_root=out_root, results_dir=res_dir, tag=args.tag, run_idx=i,
        ))
    accs = [r["test"]["acc@10"] for r in runs if r["test"]]
    mrrs = [r["test"]["mrr"] for r in runs if r["test"]]
    summary = {
        "tag": args.tag, "state": args.state.lower(), "engine": args.engine,
        "n_runs": len(runs),
        "test_acc@10_mean": float(np.mean(accs)) if accs else None,
        "test_acc@10_std": float(np.std(accs, ddof=1)) if len(accs) > 1 else None,
        "test_mrr_mean": float(np.mean(mrrs)) if mrrs else None,
        "test_mrr_std": float(np.std(mrrs, ddof=1)) if len(mrrs) > 1 else None,
    }
    with open(res_dir / f"{args.tag}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[stl] summary -> {summary}")


if __name__ == "__main__":
    main()
