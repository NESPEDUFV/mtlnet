"""Training entrypoint for the faithful ReHDM next-region baseline.

Loads the parquet emitted by `etl.py`, builds per-batch sub-hypergraphs of
collaborative trajectories (intra-user same prior history; inter-user
collaborators with at least one shared POI and end-time strictly before the
target's start), trains the model with cross-entropy and OneCycleLR.

Result JSON is written to
`docs/results/baselines/<tag>.json`.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
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

from research.baselines.rehdm.model import ReHDM, ReHDMConfig


# --- A2 (faithfulness): spatio-temporal message bucketization (paper Eq. 9) ---
# Log-width buckets for the inter-trajectory time gap Δt (target.start −
# collab.end, seconds ≥ 0 by the precedence filter) and the haversine distance
# Δd (km) between trajectory centroids. Must match ReHDMConfig.n_{time,dist}_buckets.
# TODO(verify): ReHDM does not specify the encoder family or bucket widths
# (paper ambiguity #4). log2 widths are a defensible STHGCN-style default;
# confirm against the authors' released code before treating as canonical.
N_TIME_BUCKETS = 32
N_DIST_BUCKETS = 32


def _time_bucket(dt_seconds: float) -> int:
    hours = max(0.0, dt_seconds) / 3600.0
    return min(int(math.log2(hours + 1.0)), N_TIME_BUCKETS - 1)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _dist_bucket(km: float) -> int:
    return min(int(math.log2(max(0.0, km) + 1.0)), N_DIST_BUCKETS - 1)


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class TrajectoryStore:
    """Holds per-trajectory ID arrays + bookkeeping for collaborator lookup."""

    ID_COLS = ["user_idx", "poi_idx", "category_idx", "hour_idx", "day_idx", "quadkey_idx"]

    def __init__(self, df: pd.DataFrame, max_len: int):
        self.max_len = max_len
        df = df.sort_values(["traj_idx", "pos_in_traj"]).reset_index(drop=True)
        self.traj_ids = sorted(df["traj_idx"].unique().tolist())

        self.ids = {c: {} for c in self.ID_COLS}
        self.lengths: dict[int, int] = {}
        self.targets: dict[int, int] = {}
        self.users: dict[int, int] = {}
        self.start_t: dict[int, np.int64] = {}
        self.end_t: dict[int, np.int64] = {}
        self.poi_set: dict[int, set] = {}
        self.split: dict[int, str] = {}
        # A2 (faithfulness): per-trajectory centroid for the Δd message term.
        # Only available if the ETL persisted lat/lon (updated etl.py cols);
        # for legacy parquets without them, `self.has_geo` stays False and the
        # s_ij term degrades to a single bucket (see make_collate).
        self.lat: dict[int, float] = {}
        self.lon: dict[int, float] = {}
        self.has_geo = "latitude" in df.columns and "longitude" in df.columns

        ts = df["datetime"].astype("int64").to_numpy() // 10**9
        for tid, g in df.groupby("traj_idx", sort=False):
            if len(g) < 2:
                continue  # need at least 1 input + 1 target
            ix = g.index.to_numpy()
            total = min(len(ix), max_len + 1)
            input_len = total - 1  # encoder sees all but the last; last is target
            for c in self.ID_COLS:
                arr = np.zeros(max_len, dtype=np.int64)
                arr[:input_len] = g[c].to_numpy()[:input_len]
                self.ids[c][int(tid)] = arr
            self.lengths[int(tid)] = input_len
            self.targets[int(tid)] = int(g["region_idx"].to_numpy()[input_len])
            self.users[int(tid)] = int(g["user_idx"].to_numpy()[0])
            self.start_t[int(tid)] = int(ts[ix[0]])
            self.end_t[int(tid)] = int(ts[ix[input_len - 1]])
            self.poi_set[int(tid)] = set(g["poi_idx"].to_numpy()[:input_len].tolist())
            self.split[int(tid)] = g["split"].iloc[0]
            if self.has_geo:
                self.lat[int(tid)] = float(g["latitude"].to_numpy()[:input_len].mean())
                self.lon[int(tid)] = float(g["longitude"].to_numpy()[:input_len].mean())

        self.traj_ids = [t for t in self.traj_ids if t in self.split]
        self.train_ids = [t for t in self.traj_ids if self.split[t] == "train"]
        self.val_ids = [t for t in self.traj_ids if self.split[t] == "val"]
        self.test_ids = [t for t in self.traj_ids if self.split[t] == "test"]

        self.user_to_train_traj: dict[int, list[int]] = defaultdict(list)
        self.poi_to_train_traj: dict[int, list[int]] = defaultdict(list)
        for tid in self.train_ids:
            self.user_to_train_traj[self.users[tid]].append(tid)
            for p in self.poi_set[tid]:
                self.poi_to_train_traj[p].append(tid)

        # --- Vectorised-gather buffers (data-movement optimisation, byte-identical) ---
        # Pre-stack the per-column ID arrays and a precomputed mask into contiguous
        # [n_traj, max_len] tensors, indexed by a stable tid->row map. `stack()` then
        # becomes a single advanced-index gather instead of a Python list-comp +
        # per-row mask loop. The contents are exactly what the old loop produced.
        self._row_of: dict[int, int] = {t: i for i, t in enumerate(self.traj_ids)}
        n_traj = len(self.traj_ids)
        self._id_mat: dict[str, torch.Tensor] = {}
        for c in self.ID_COLS:
            mat = np.stack([self.ids[c][t] for t in self.traj_ids]) if n_traj else \
                np.zeros((0, max_len), dtype=np.int64)
            self._id_mat[c] = torch.from_numpy(mat)
        mask_mat = torch.zeros(n_traj, max_len, dtype=torch.float32)
        for i, t in enumerate(self.traj_ids):
            mask_mat[i, : self.lengths[t]] = 1.0
        self._mask_mat = mask_mat

    def stack(self, tids: list[int]):
        rows = torch.tensor([self._row_of[t] for t in tids], dtype=torch.long)
        ids = {c: self._id_mat[c].index_select(0, rows) for c in self.ID_COLS}
        mask = self._mask_mat.index_select(0, rows)
        return ids, mask

    def precompute_collab_pools(self, max_inter_pool: int = 32) -> None:
        """Precompute time-precedence-valid collaborator pools per traj.

        Filling `_intra_pool[tid]` and `_inter_pool[tid]` once amortises the
        per-batch Python iteration that previously dominated CPU time.
        """
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
                    seen.add(t)
                    pool.append(t)
                    if len(pool) >= max_inter_pool:
                        break
                if len(pool) >= max_inter_pool:
                    break
            self._inter_pool[tid] = pool

    def collaborators(
        self, target_tid: int, max_intra: int, max_inter: int,
        rng: random.Random | None = None,
    ) -> tuple[list[int], list[int]]:
        """O(1) lookup of cached pools, then truncate (and optionally shuffle)."""
        intra = self._intra_pool[target_tid][-max_intra:]
        pool = self._inter_pool[target_tid]
        # A7 (faithfulness/cleanup): the old `(rng or random).random() < 1.0`
        # guard was a tautology (random() ∈ [0,1) is always < 1.0), so the
        # `else` branch was dead and one RNG draw was wasted (perturbing the
        # stream). Sample only when the pool actually exceeds the cap.
        if len(pool) > max_inter:
            inter = (rng or random).sample(pool, max_inter)
        else:
            inter = pool[:max_inter]  # already ≤ cap; == pool
        return intra, inter


class ReHDMDataset(Dataset):
    def __init__(self, store: TrajectoryStore, ids: list[int]):
        self.store = store
        self.ids = ids

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, i):
        return self.ids[i]


def make_collate(
    store: TrajectoryStore, max_intra: int, max_inter: int, training: bool,
    seeded: bool = False,
):
    # A6 (reproducibility): decouple "build collaborators" from "seeded rng".
    # Training uses a stochastic rng (None → global `random`) as data
    # augmentation; evaluation passes `training=True` (so the sub-hypergraph IS
    # built per §4.2) *and* `seeded=True` so inter-user sampling is deterministic
    # across runs (README "verified-fixed bug #3"). The old code keyed the seed
    # off `training`, so the eval path (training=True) silently used the global
    # rng and was NOT actually seeded.
    rng = random.Random(0) if (seeded or not training) else None

    def collate(batch_tids: list[int]):
        target_ids, target_mask = store.stack(batch_tids)
        targets = torch.tensor([store.targets[t] for t in batch_tids], dtype=torch.long)

        if not training or (max_intra + max_inter) == 0:
            return (target_ids, target_mask, None, None, None, None, None, None,
                    targets)

        all_collab: list[int] = []
        # (target_row, collab_row, edge_type, time_bucket, dist_bucket)
        edges: list[tuple[int, int, int, int, int]] = []
        seen_to_idx: dict[int, int] = {}
        for ti, tid in enumerate(batch_tids):
            intra, inter = store.collaborators(tid, max_intra, max_inter, rng=rng)
            t_start = store.start_t[tid]
            for c, rtype in [(c, 0) for c in intra] + [(c, 1) for c in inter]:
                if c not in seen_to_idx:
                    seen_to_idx[c] = len(all_collab)
                    all_collab.append(c)
                # A2: Δt / Δd message buckets for this (target, collaborator) edge.
                tb = _time_bucket(t_start - store.end_t[c])
                if store.has_geo:
                    db = _dist_bucket(_haversine_km(
                        store.lat[tid], store.lon[tid], store.lat[c], store.lon[c]))
                else:
                    db = 0
                edges.append((ti, seen_to_idx[c], rtype, tb, db))

        if not all_collab:
            return (target_ids, target_mask, None, None, None, None, None, None,
                    targets)

        collab_ids, collab_mask = store.stack(all_collab)
        adjacency = torch.zeros(len(batch_tids), len(all_collab), dtype=torch.float32)
        edge_types = torch.zeros(len(batch_tids), len(all_collab), dtype=torch.long)
        time_buckets = torch.zeros(len(batch_tids), len(all_collab), dtype=torch.long)
        dist_buckets = torch.zeros(len(batch_tids), len(all_collab), dtype=torch.long)
        # Vectorised scatter from the `edges` list. Each (ti, ci) pair is
        # unique: intra (same-user) and inter (different-user, see :122) pools
        # are user-disjoint and `seen_to_idx` dedups, so no (ti, ci) is written
        # twice — index-assignment has no duplicate-index ambiguity here.
        if edges:
            e = torch.tensor(edges, dtype=torch.long)  # [E, 5]
            ti_idx, ci_idx = e[:, 0], e[:, 1]
            adjacency[ti_idx, ci_idx] = 1.0
            edge_types[ti_idx, ci_idx] = e[:, 2]
            time_buckets[ti_idx, ci_idx] = e[:, 3]
            dist_buckets[ti_idx, ci_idx] = e[:, 4]
        return (target_ids, target_mask, collab_ids, collab_mask, adjacency,
                edge_types, time_buckets, dist_buckets, targets)

    return collate


def _move(ids: dict, device):
    return {k: v.to(device) for k, v in ids.items()}


@torch.no_grad()
def evaluate(model, store, ids, batch_size, device, max_intra=4, max_inter=4,
             amp_enabled: bool = False):
    """Evaluate with the same sub-hypergraph protocol as training (paper §4.2)."""
    model.eval()
    # macOS spawn can't pickle the closure returned by make_collate; use fork there.
    _mp_ctx = "fork" if not torch.cuda.is_available() else None
    loader = DataLoader(
        ReHDMDataset(store, ids), batch_size=batch_size, shuffle=False,
        num_workers=2, persistent_workers=True,
        pin_memory=torch.cuda.is_available(),
        multiprocessing_context=_mp_ctx,
        # A6: seeded=True → deterministic inter-user sampling at eval time.
        collate_fn=make_collate(store, max_intra, max_inter, training=True, seeded=True),
    )
    n = 0
    correct1 = correct5 = correct10 = 0
    mrr = 0.0
    for batch in loader:
        t_ids, t_mask, c_ids, c_mask, adj, et, tb, db, y = batch
        t_ids = _move(t_ids, device); t_mask = t_mask.to(device); y = y.to(device)
        if c_ids is not None:
            c_ids = _move(c_ids, device); c_mask = c_mask.to(device)
            adj = adj.to(device); et = et.to(device)
            tb = tb.to(device); db = db.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=amp_enabled):
            logits = model(t_ids, t_mask, c_ids, c_mask, adj, et, tb, db)
        logits = logits.float()
        ranks = (-logits).argsort(dim=-1)
        pos = (ranks == y.unsqueeze(1)).nonzero()[:, 1] + 1
        correct1 += (pos <= 1).sum().item()
        correct5 += (pos <= 5).sum().item()
        correct10 += (pos <= 10).sum().item()
        mrr += (1.0 / pos.float()).sum().item()
        n += y.numel()
    return {
        "acc@1": correct1 / max(n, 1),
        "acc@5": correct5 / max(n, 1),
        "acc@10": correct10 / max(n, 1),
        "mrr": mrr / max(n, 1),
        "n": n,
    }


def train_one_run(
    state: str, seed: int, epochs: int, batch_size: int,
    lr: float, max_lr: float, max_len: int, max_intra: int, max_inter: int,
    output_root: Path, results_dir: Path, tag: str, run_idx: int,
):
    set_seed(seed)
    device = _device()
    print(f"[train] seed={seed} device={device}")

    in_dir = output_root / "baselines" / "rehdm" / state
    df = pd.read_parquet(in_dir / "inputs.parquet")
    vocab = json.loads((in_dir / "vocab.json").read_text())

    store = TrajectoryStore(df, max_len=max_len)
    store.precompute_collab_pools(max_inter_pool=max(32, max_inter * 4))
    print(
        f"[train] trajectories train={len(store.train_ids)} "
        f"val={len(store.val_ids)} test={len(store.test_ids)}"
    )

    cfg = ReHDMConfig(
        n_users=vocab["n_users"], n_pois=vocab["n_pois"],
        n_categories=vocab["n_categories"], n_quadkeys=vocab["n_quadkeys"],
        n_regions=vocab["n_regions"],
        n_time_buckets=N_TIME_BUCKETS, n_dist_buckets=N_DIST_BUCKETS,
    )
    model = ReHDM(cfg).to(device)
    print(f"[train] params={sum(p.numel() for p in model.parameters())/1e6:.2f}M")

    # A1 (correctness): bf16 autocast escape hatch. The A40 grad-NaNs on bf16
    # backward at large region domains (C≈4.7k–8.5k for FL/CA/TX) — the NaN
    # guards below would then silently skip most batches. Gate:
    #   REHDM_DISABLE_AMP=1 → force fp32; =0 → force bf16 (CUDA only);
    #   unset → auto: fp32 when n_regions > REHDM_AMP_REGION_CAP (default 3000),
    #   bf16 otherwise. Doubles as the B1 perf lever (bf16 speedup at small states).
    _amp_env = os.environ.get("REHDM_DISABLE_AMP")
    _region_cap = int(os.environ.get("REHDM_AMP_REGION_CAP", "3000"))
    if _amp_env == "1":
        amp_enabled = False
    elif _amp_env == "0":
        amp_enabled = torch.cuda.is_available()
    else:
        amp_enabled = torch.cuda.is_available() and vocab["n_regions"] <= _region_cap
    print(f"[train] amp(bf16)={amp_enabled} n_regions={vocab['n_regions']}")

    if torch.cuda.is_available():
        # B4 (numerics consistency): only enable TF32 under the bf16 path (where
        # matmuls are bf16 anyway). Under the fp32-faithful path (amp disabled),
        # leave TF32 OFF so "fp32" means true fp32 (matches the board protocol).
        _tf32 = amp_enabled
        torch.backends.cuda.matmul.allow_tf32 = _tf32
        torch.backends.cudnn.allow_tf32 = _tf32
        torch.set_float32_matmul_precision("high" if _tf32 else "highest")
    # On non-CUDA (macOS MPS/CPU), spawn can't pickle make_collate's closure → use fork
    # and reduce worker count (CUDA path keeps the validated 12-worker recipe).
    _mp_ctx = "fork" if not torch.cuda.is_available() else None
    _nw = 12 if torch.cuda.is_available() else 4
    train_loader = DataLoader(
        ReHDMDataset(store, store.train_ids), batch_size=batch_size, shuffle=True,
        collate_fn=make_collate(store, max_intra, max_inter, training=True),
        num_workers=_nw, persistent_workers=True, prefetch_factor=4,
        pin_memory=torch.cuda.is_available(),
        multiprocessing_context=_mp_ctx,
    )
    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    steps = max(1, len(train_loader)) * epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(optim, max_lr=max_lr, total_steps=steps)

    best_val = -1.0
    best_test_metrics: dict | None = None
    best_state: dict | None = None            # B2: snapshot of best-val weights
    n_skipped_loss = 0                        # A1: surface NaN-storm visibility
    n_skipped_grad = 0
    for ep in range(epochs):
        model.train()
        t0 = time.time()
        loss_sum = 0.0
        for batch in train_loader:
            t_ids, t_mask, c_ids, c_mask, adj, et, tb, db, y = batch
            t_ids = _move(t_ids, device); t_mask = t_mask.to(device)
            if c_ids is not None:
                c_ids = _move(c_ids, device); c_mask = c_mask.to(device)
                adj = adj.to(device); et = et.to(device)
                tb = tb.to(device); db = db.to(device)
            y = y.to(device)
            optim.zero_grad()
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=amp_enabled):
                logits = model(t_ids, t_mask, c_ids, c_mask, adj, et, tb, db)
                loss = F.cross_entropy(logits, y)
            if not torch.isfinite(loss):
                print(f"[train] non-finite loss at ep={ep+1}; skipping batch")
                n_skipped_loss += 1
                continue
            loss.backward()
            bad_grad = False
            for p in model.parameters():
                if p.grad is not None and not torch.isfinite(p.grad).all():
                    bad_grad = True; break
            if bad_grad:
                print(f"[train] non-finite grad at ep={ep+1}; skipping step")
                n_skipped_grad += 1
                optim.zero_grad(); continue
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optim.step(); sched.step()
            loss_sum += loss.item() * y.size(0)

        val = evaluate(model, store, store.val_ids, batch_size, device,
                       max_intra, max_inter, amp_enabled=amp_enabled)
        print(
            f"[train] ep={ep+1}/{epochs} loss={loss_sum/max(1,len(store.train_ids)):.4f} "
            f"val_acc@10={val['acc@10']:.4f} mrr={val['mrr']:.4f} dt={time.time()-t0:.1f}s"
        )
        if val["acc@10"] > best_val:
            best_val = val["acc@10"]
            # B2 (perf): snapshot best-val weights instead of running a full test
            # eval every time val improves; the single test eval happens once
            # after the loop. Bit-exact vs the old per-improvement test eval given
            # A6's seeded eval RNG (model.eval() + deterministic collaborators).
            best_state = copy.deepcopy(model.state_dict())

    if best_state is not None:
        model.load_state_dict(best_state)
        best_test_metrics = evaluate(
            model, store, store.test_ids, batch_size, device,
            max_intra, max_inter, amp_enabled=amp_enabled,
        )

    if n_skipped_loss or n_skipped_grad:
        print(f"[train] WARNING skipped batches: loss={n_skipped_loss} grad={n_skipped_grad} "
              f"(bf16 NaN storm? try REHDM_DISABLE_AMP=1)")

    out = {
        "tag": tag, "state": state, "run": run_idx, "seed": seed,
        "config": cfg.__dict__, "best_val_acc@10": best_val,
        "test": best_test_metrics, "vocab": vocab,
        "amp_bf16": amp_enabled,
        "skipped_batches": {"loss": n_skipped_loss, "grad": n_skipped_grad},
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / f"{tag}_run{run_idx}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[train] wrote {out_path}")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--folds", type=int, default=5, help="number of seeded runs")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--max-lr", type=float, default=5e-4)
    p.add_argument("--max-len", type=int, default=20)
    p.add_argument("--max-intra", type=int, default=4)
    p.add_argument("--max-inter", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output-root", default=os.environ.get("OUTPUT_DIR", "output"))
    p.add_argument(
        "--results-dir",
        default="docs/results/baselines",
    )
    p.add_argument("--tag", required=True)
    args = p.parse_args()

    out_root = Path(args.output_root)
    res_dir = Path(args.results_dir)
    runs = []
    for i in range(args.folds):
        runs.append(
            train_one_run(
                state=args.state.lower(), seed=args.seed + i, epochs=args.epochs,
                batch_size=args.batch_size, lr=args.lr, max_lr=args.max_lr,
                max_len=args.max_len, max_intra=args.max_intra, max_inter=args.max_inter,
                output_root=out_root, results_dir=res_dir, tag=args.tag, run_idx=i,
            )
        )

    accs = [r["test"]["acc@10"] for r in runs if r["test"]]
    mrrs = [r["test"]["mrr"] for r in runs if r["test"]]
    summary = {
        "tag": args.tag,
        "state": args.state.lower(),
        "n_runs": len(runs),
        "test_acc@10_mean": float(np.mean(accs)) if accs else None,
        "test_acc@10_std": float(np.std(accs, ddof=1)) if len(accs) > 1 else None,
        "test_mrr_mean": float(np.mean(mrrs)) if mrrs else None,
        "test_mrr_std": float(np.std(mrrs, ddof=1)) if len(mrrs) > 1 else None,
    }
    with open(res_dir / f"{args.tag}_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[train] summary -> {summary}")


if __name__ == "__main__":
    main()
