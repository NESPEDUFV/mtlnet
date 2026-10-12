#!/usr/bin/env python3
"""Advisor follow-ups for HGI POI2Vec category-injection probes.

Variants added on top of build_hgi_category_variants.py:
  - A_sum_lam0.001 / A_sum_lam0.01 / A_sum_lam0.1 — Variant A with the canonical
    `.sum()` hierarchy-loss formulation (not `.sum()/N` from the first pass).
    Sweep λ to find the Pareto frontier between fclass-discriminability and
    category lift, before deciding A is broken.
  - C_balanced — Variant C with per-vocab loss weights λ_f=0.1, λ_c=1.0. The
    fclass skip-gram converges to ~0.02 by epoch 4 (305-class with k=5 random
    negs is trivial); category skip-gram stays ~4.76 (vocab=7, k=5 means
    almost-no-real-negatives). λ_c >> λ_f forces the optimizer to actually
    push category training.
  - D_orth — orthogonal additive. After joint skip-gram (as in C), compute
    poi_emb[i] = fclass_emb[f_i] + γ · proj_orth(cat_emb[c_i], fclass_emb[f_i])
    where proj_orth(c, f) = c − (c·f / ‖f‖²) f. Guarantees the cat
    contribution is perpendicular to the fclass vector — category adds
    information without overwriting fclass.

Usage:
    PYTHONPATH=src:research python scripts/probe/build_hgi_category_followups.py \\
        --variant {A_sum_lam0.001|A_sum_lam0.01|A_sum_lam0.1|C_balanced|D_orth|all} \\
        [--poi2vec-epochs 30] [--epoch 2000]

Each variant writes its outputs under output/hgi/arizona_cat{variant}/ and
plumbs everything the north-star eval needs (data/checkins symlink,
output/check2hgi/arizona_cat{variant} → arizona symlink, next_region.parquet
symlink). After the build, north-star (next-CAT + next-REG, 5f × 30ep) is
launched automatically — final results land in
docs/results/P1/.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pickle as pkl
import random
import shutil
import subprocess
import sys
import time
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import Node2Vec
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "research"))

from configs.paths import IoPaths, EmbeddingEngine  # noqa: E402
import embeddings.hgi.hgi as hgi_mod  # noqa: E402
from embeddings.hgi.poi2vec import POI2Vec, POISet  # noqa: E402
from data.inputs.builders import (  # noqa: E402
    generate_category_input,
    generate_next_input_from_poi,
)

# Re-use helpers from the first-pass build script.
sys.path.insert(0, str(REPO_ROOT / "scripts" / "probe"))
from build_hgi_category_variants import (  # noqa: E402
    setup_probe_temp_dir,
    save_poi2vec_output,
    build_probe_pickle,
    train_hgi_on_probe,
    fclass_linear_probe,
    embedding_stats,
)


CANONICAL_STATE = "arizona"
C2HGI_AZ_DIR = REPO_ROOT / "output" / "check2hgi" / "arizona"
TRANSITION_FOLD1 = C2HGI_AZ_DIR / "region_transition_log_seed42_fold1.pt"

ARGS: Namespace = None


# ============================================================================
# Variant A with .sum() hierarchy loss (not .sum()/N)
# ============================================================================


class EmbeddingModelA_Sum(nn.Module):
    """Variant A with the canonical `.sum()` hierarchy formulation, as in the
    reference poi2vec.py (not the `.sum()/N` averaged variant we ran first)."""

    def __init__(self, vocab_size_fclass, num_cat, embed_size, hierarchy_pairs,
                 le_lambda=0.1):
        super().__init__()
        self.in_embed = nn.Embedding(vocab_size_fclass, embed_size)
        self.out_embed = nn.Embedding(vocab_size_fclass, embed_size)
        self.cat_embed = nn.Embedding(num_cat, embed_size)
        nn.init.xavier_uniform_(self.in_embed.weight)
        nn.init.xavier_uniform_(self.out_embed.weight)
        nn.init.xavier_uniform_(self.cat_embed.weight)
        self.hierarchy_pairs = torch.tensor(hierarchy_pairs, dtype=torch.long)
        self.le_lambda = le_lambda

    def forward(self, center, pos, neg):
        c = self.in_embed(center).unsqueeze(2)
        log_pos = F.logsigmoid(torch.bmm(self.out_embed(pos), c).squeeze(2)).sum(1)
        log_neg = F.logsigmoid(torch.bmm(self.out_embed(neg), -c).squeeze(2)).sum(1)
        loss_skip = -(log_pos + log_neg).mean()
        if self.hierarchy_pairs.numel() > 0:
            if self.hierarchy_pairs.device != center.device:
                self.hierarchy_pairs = self.hierarchy_pairs.to(center.device)
            cat_idx = self.hierarchy_pairs[:, 0]
            fclass_idx = self.hierarchy_pairs[:, 1]
            diff = self.cat_embed(cat_idx) - self.in_embed(fclass_idx)
            loss_hier = 0.5 * self.le_lambda * (diff * diff).sum()
        else:
            loss_hier = torch.tensor(0.0, device=center.device)
        return loss_skip + loss_hier, loss_hier

    def get_embeddings(self):
        return self.in_embed.weight.detach().cpu().numpy()


def variant_a_sum(probe_state: str, poi2vec_epochs: int, le_lambda: float) -> dict:
    print(f"\n{'=' * 80}\nVARIANT {probe_state} — A with .sum() loss, λ={le_lambda}\n{'=' * 80}")
    t0 = time.time()
    probe_temp = setup_probe_temp_dir(probe_state, use_category_as_fclass=False)
    pois = pd.read_csv(probe_temp / "pois.csv")
    n_cat = int(pois["category"].max()) + 1

    p2v = POI2Vec(
        edges_file=str(probe_temp / "edges.csv"),
        pois_file=str(probe_temp / "pois.csv"),
        embedding_dim=64,
        device=torch.device("cpu"),
    )
    p2v.generate_walks(batch_size=128)
    pairs = list(set(tuple(r) for r in pois[["category", "fclass"]].values))

    ds = POISet(p2v.vocab_size, p2v.fclass_walks, p2v.global_co_occurrence, k=5)
    model = EmbeddingModelA_Sum(p2v.vocab_size, n_cat, 64, pairs, le_lambda=le_lambda)
    opt = torch.optim.Adam(model.parameters(), lr=0.05)
    loader = torch.utils.data.DataLoader(ds, batch_size=2048, shuffle=True,
                                         num_workers=10, persistent_workers=True)

    best_loss, best_emb = math.inf, None
    model.train()
    for ep in range(poi2vec_epochs):
        tot, lhier, num = 0.0, 0.0, 0
        for center, pos, neg in tqdm(loader, desc=f"A_sum ep {ep+1}/{poi2vec_epochs}"):
            opt.zero_grad()
            loss, lh = model(center, pos, neg)
            loss.backward()
            opt.step()
            tot += loss.item(); lhier += lh.item(); num += 1
        avg = tot / max(num, 1)
        if avg < best_loss:
            best_loss = avg
            best_emb = model.get_embeddings().copy()
        print(f"  A_sum ep {ep+1}: loss={avg:.4f}  hier={lhier/num:.4f}")
    fclass_emb = best_emb if best_emb is not None else model.get_embeddings()

    fclass_vals = pois["fclass"].values.astype(int)
    poi_emb = fclass_emb[fclass_vals].astype(np.float32)
    placeids = pois["placeid"].astype(int).tolist()
    poi_path = save_poi2vec_output(probe_temp, poi_emb, placeids)
    build_probe_pickle(probe_temp, poi_path)
    train_hgi_on_probe(probe_state, epoch=ARGS.epoch)

    return {
        "variant": probe_state, "wall_time_min": (time.time() - t0) / 60,
        "poi2vec_epochs": poi2vec_epochs, "hgi_epochs": ARGS.epoch,
        "le_lambda": le_lambda, "loss_form": "sum",
        "fclass_probe": fclass_linear_probe(probe_state, "fclass"),
        "category_probe": fclass_linear_probe(probe_state, "category", min_per_class=10),
        **embedding_stats(probe_state),
    }


# ============================================================================
# Variant C with balanced loss weights
# ============================================================================


class JointPOISetBalanced(torch.utils.data.Dataset):
    def __init__(self, vocab_fclass, vocab_cat, fclass_walks, cat_walks,
                 fclass_neg_cands, cat_neg_cands, k=5):
        assert len(fclass_walks) == len(cat_walks)
        self.fclass_walks = fclass_walks
        self.cat_walks = cat_walks
        self.fclass_neg = fclass_neg_cands
        self.cat_neg = cat_neg_cands
        self.k = k

    def __len__(self):
        return len(self.fclass_walks)

    def _sample_neg(self, candidates, n):
        if n <= len(candidates):
            return random.sample(candidates, n)
        out = random.sample(candidates, len(candidates))
        while len(out) < n:
            out.append(random.choice(candidates))
        return out

    def __getitem__(self, idx):
        fw = self.fclass_walks[idx]
        cw = self.cat_walks[idx]
        cf, cc = fw[0], cw[0]
        pf, pc = fw[1:], cw[1:]
        n = len(pf) * self.k
        nf = self._sample_neg(self.fclass_neg[int(cf)], n)
        nc = self._sample_neg(self.cat_neg[int(cc)], n)
        return (
            torch.tensor(cf, dtype=torch.long),
            torch.tensor(cc, dtype=torch.long),
            torch.tensor(pf, dtype=torch.long),
            torch.tensor(pc, dtype=torch.long),
            torch.tensor(nf, dtype=torch.long),
            torch.tensor(nc, dtype=torch.long),
        )


class EmbeddingModelCBalanced(nn.Module):
    def __init__(self, vocab_fclass, vocab_cat, embed_size,
                 lambda_f=0.1, lambda_c=1.0):
        super().__init__()
        self.f_in = nn.Embedding(vocab_fclass, embed_size)
        self.f_out = nn.Embedding(vocab_fclass, embed_size)
        self.c_in = nn.Embedding(vocab_cat, embed_size)
        self.c_out = nn.Embedding(vocab_cat, embed_size)
        for emb in [self.f_in, self.f_out, self.c_in, self.c_out]:
            nn.init.xavier_uniform_(emb.weight)
        self.lambda_f = lambda_f
        self.lambda_c = lambda_c

    def _skip_gram(self, in_t, out_t, center, pos, neg):
        c = in_t(center).unsqueeze(2)
        lp = F.logsigmoid(torch.bmm(out_t(pos), c).squeeze(2)).sum(1)
        ln = F.logsigmoid(torch.bmm(out_t(neg), -c).squeeze(2)).sum(1)
        return -(lp + ln).mean()

    def forward(self, cf, cc, pf, pc, nf, nc):
        loss_f = self._skip_gram(self.f_in, self.f_out, cf, pf, nf)
        loss_c = self._skip_gram(self.c_in, self.c_out, cc, pc, nc)
        total = self.lambda_f * loss_f + self.lambda_c * loss_c
        return total, loss_f, loss_c

    def fclass_embeddings(self):
        return self.f_in.weight.detach().cpu().numpy()

    def cat_embeddings(self):
        return self.c_in.weight.detach().cpu().numpy()


def _run_joint_skipgram(probe_temp: Path, model: EmbeddingModelCBalanced,
                        poi2vec_epochs: int, label: str):
    """Shared joint skip-gram trainer used by C_balanced and D_orth."""
    pois = pd.read_csv(probe_temp / "pois.csv")
    edges = pd.read_csv(probe_temp / "edges.csv")
    edge_index = torch.tensor(edges[["source", "target"]].values.T, dtype=torch.long)
    n2v = Node2Vec(edge_index=edge_index, embedding_dim=64, walk_length=10,
                   context_size=5, walks_per_node=5, p=0.5, q=0.5, sparse=True)
    fclass_walks, cat_walks = [], []
    fclass_arr = pois["fclass"].values.astype(int)
    cat_arr = pois["category"].values.astype(int)
    print(f"[{label}] generating POI walks → (fclass, category) sequences ...")
    for pos_rw, _ in tqdm(n2v.loader(batch_size=128, shuffle=True, num_workers=0)):
        for walk in pos_rw:
            poi_ids = walk.tolist()
            fclass_walks.append([int(fclass_arr[p]) for p in poi_ids])
            cat_walks.append([int(cat_arr[p]) for p in poi_ids])

    def neg_candidates(walks, vocab_size):
        co = {i: set() for i in range(vocab_size)}
        for w in walks:
            co[w[0]].update(w[1:])
        all_ids = set(range(vocab_size))
        cands = []
        for i in range(vocab_size):
            c = list(all_ids - co[i] - {i})
            if not c:
                c = [j for j in range(vocab_size) if j != i]
            cands.append(c)
        return cands

    vocab_fclass = int(pois["fclass"].max()) + 1
    vocab_cat = int(pois["category"].max()) + 1
    f_neg = neg_candidates(fclass_walks, vocab_fclass)
    c_neg = neg_candidates(cat_walks, vocab_cat)

    ds = JointPOISetBalanced(vocab_fclass, vocab_cat, fclass_walks, cat_walks,
                             f_neg, c_neg, k=5)
    opt = torch.optim.Adam(model.parameters(), lr=0.05)
    loader = torch.utils.data.DataLoader(ds, batch_size=2048, shuffle=True,
                                         num_workers=10, persistent_workers=True)

    best_loss = math.inf
    best_f, best_c = None, None
    model.train()
    for ep in range(poi2vec_epochs):
        tot, lf, lc, num = 0.0, 0.0, 0.0, 0
        for cf, cc, pf, pc, nf, nc in tqdm(loader, desc=f"{label} ep {ep+1}/{poi2vec_epochs}"):
            opt.zero_grad()
            loss, loss_f, loss_c = model(cf, cc, pf, pc, nf, nc)
            loss.backward()
            opt.step()
            tot += loss.item(); lf += loss_f.item(); lc += loss_c.item(); num += 1
        avg = tot / max(num, 1)
        print(f"  {label} ep {ep+1}: loss={avg:.4f}  (fclass_raw={lf/num:.4f}, cat_raw={lc/num:.4f})")
        if avg < best_loss:
            best_loss = avg
            best_f = model.fclass_embeddings().copy()
            best_c = model.cat_embeddings().copy()
    return best_f, best_c, pois


def variant_c_balanced(probe_state: str, poi2vec_epochs: int,
                       lambda_f: float = 0.1, lambda_c: float = 1.0,
                       gamma: float = 0.5) -> dict:
    print(f"\n{'=' * 80}\nVARIANT C_balanced — λ_f={lambda_f}, λ_c={lambda_c}, γ={gamma}\n{'=' * 80}")
    t0 = time.time()
    probe_temp = setup_probe_temp_dir(probe_state, use_category_as_fclass=False)
    pois_full = pd.read_csv(probe_temp / "pois.csv")
    vocab_fclass = int(pois_full["fclass"].max()) + 1
    vocab_cat = int(pois_full["category"].max()) + 1

    model = EmbeddingModelCBalanced(vocab_fclass, vocab_cat, 64,
                                    lambda_f=lambda_f, lambda_c=lambda_c)
    best_f, best_c, pois = _run_joint_skipgram(probe_temp, model, poi2vec_epochs,
                                               label="C_bal")
    fclass_vals = pois["fclass"].values.astype(int)
    cat_vals = pois["category"].values.astype(int)
    poi_emb = (best_f[fclass_vals] + gamma * best_c[cat_vals]).astype(np.float32)
    placeids = pois["placeid"].astype(int).tolist()
    poi_path = save_poi2vec_output(probe_temp, poi_emb, placeids)
    build_probe_pickle(probe_temp, poi_path)
    train_hgi_on_probe(probe_state, epoch=ARGS.epoch)

    return {
        "variant": probe_state, "wall_time_min": (time.time() - t0) / 60,
        "poi2vec_epochs": poi2vec_epochs, "hgi_epochs": ARGS.epoch,
        "lambda_f": lambda_f, "lambda_c": lambda_c, "gamma": gamma,
        "fclass_probe": fclass_linear_probe(probe_state, "fclass"),
        "category_probe": fclass_linear_probe(probe_state, "category", min_per_class=10),
        **embedding_stats(probe_state),
    }


# ============================================================================
# Variant D — orthogonal additive
# ============================================================================


def variant_d_orth(probe_state: str, poi2vec_epochs: int,
                   gamma: float = 0.5,
                   lambda_f: float = 0.1, lambda_c: float = 1.0) -> dict:
    print(f"\n{'=' * 80}\nVARIANT D_orth — orthogonal additive, γ={gamma}, "
          f"(λ_f={lambda_f}, λ_c={lambda_c} on joint skip-gram)\n{'=' * 80}")
    t0 = time.time()
    probe_temp = setup_probe_temp_dir(probe_state, use_category_as_fclass=False)
    pois_full = pd.read_csv(probe_temp / "pois.csv")
    vocab_fclass = int(pois_full["fclass"].max()) + 1
    vocab_cat = int(pois_full["category"].max()) + 1

    model = EmbeddingModelCBalanced(vocab_fclass, vocab_cat, 64,
                                    lambda_f=lambda_f, lambda_c=lambda_c)
    best_f, best_c, pois = _run_joint_skipgram(probe_temp, model, poi2vec_epochs,
                                               label="D_orth")

    # Per-POI orthogonal projection: at output time, for each POI i,
    #   f = fclass_emb[fclass[i]]
    #   c = cat_emb[cat[i]]
    #   c_orth = c − (c·f / ‖f‖²) f
    #   poi_emb[i] = f + γ * c_orth
    fclass_vals = pois["fclass"].values.astype(int)
    cat_vals = pois["category"].values.astype(int)
    f_per_poi = best_f[fclass_vals]                # [N_pois, 64]
    c_per_poi = best_c[cat_vals]                   # [N_pois, 64]
    f_norm_sq = (f_per_poi ** 2).sum(axis=1, keepdims=True) + 1e-8
    dot = (c_per_poi * f_per_poi).sum(axis=1, keepdims=True)
    c_orth = c_per_poi - (dot / f_norm_sq) * f_per_poi  # rejection of c onto f

    poi_emb = (f_per_poi + gamma * c_orth).astype(np.float32)

    # Sanity: orthogonality check — average cosine of (c_orth, f) should be ~0.
    cos = ((c_orth * f_per_poi).sum(axis=1) /
           (np.linalg.norm(c_orth, axis=1) * np.linalg.norm(f_per_poi, axis=1) + 1e-8))
    print(f"  orthogonality check: |mean cos(c_orth, f_per_poi)| = {np.abs(cos.mean()):.4e}")

    placeids = pois["placeid"].astype(int).tolist()
    poi_path = save_poi2vec_output(probe_temp, poi_emb, placeids)
    build_probe_pickle(probe_temp, poi_path)
    train_hgi_on_probe(probe_state, epoch=ARGS.epoch)

    return {
        "variant": probe_state, "wall_time_min": (time.time() - t0) / 60,
        "poi2vec_epochs": poi2vec_epochs, "hgi_epochs": ARGS.epoch,
        "lambda_f": lambda_f, "lambda_c": lambda_c, "gamma": gamma,
        "orth_mean_cos": float(np.abs(cos).mean()),
        "fclass_probe": fclass_linear_probe(probe_state, "fclass"),
        "category_probe": fclass_linear_probe(probe_state, "category", min_per_class=10),
        **embedding_stats(probe_state),
    }


# ============================================================================
# Plumbing for the north-star eval that follows each build
# ============================================================================


def setup_evaluation_symlinks(probe_state: str) -> None:
    """Ensure the variant has the symlinks p1_region_head_ablation needs."""
    # 1. data/checkins/Arizona_cat<X>.parquet → Arizona.parquet
    state_suffix = probe_state.split("arizona_cat", 1)[-1]  # e.g. "A_sum_lam0.001"
    checkin_link = REPO_ROOT / "data" / "checkins" / f"Arizona_cat{state_suffix}.parquet"
    if not checkin_link.exists():
        checkin_link.symlink_to("Arizona.parquet")
    # 2. output/check2hgi/arizona_cat<X> → arizona
    c2hgi_link = REPO_ROOT / "output" / "check2hgi" / probe_state
    if not c2hgi_link.exists():
        c2hgi_link.symlink_to("arizona")
    # 3. output/hgi/<state>/input/next_region.parquet → c2hgi canonical
    hgi_input = IoPaths.HGI.get_state_dir(probe_state) / "input"
    hgi_input.mkdir(parents=True, exist_ok=True)
    nr_link = hgi_input / "next_region.parquet"
    if not nr_link.exists():
        nr_link.symlink_to(
            REPO_ROOT / "output" / "check2hgi" / "arizona" / "input" / "next_region.parquet"
        )


def ensure_mtl_inputs(probe_state: str) -> None:
    """Regenerate input/{category,next}.parquet from the variant's embeddings.
    (Even though we're using p1 not MTL, we need next.parquet on the HGI side.)
    """
    generate_category_input(probe_state, EmbeddingEngine.HGI)
    generate_next_input_from_poi(probe_state, EmbeddingEngine.HGI)


def run_northstar(probe_state: str, folds: int, epochs: int) -> dict:
    """Run next_gru (next-CAT) and next_getnext_hard (next-REG) for the variant."""
    print(f"\n=== north-star for {probe_state} ({folds}f × {epochs}ep) ===")
    state_suffix = probe_state.split("arizona_cat", 1)[-1]
    cat_tag = f"NS_AZ_cat{state_suffix}_nextcat_5f{epochs}ep"
    reg_tag = f"NS_AZ_cat{state_suffix}_nextreg_5f{epochs}ep"
    cmd_cat = [
        sys.executable, "scripts/p1_region_head_ablation.py",
        "--state", probe_state, "--engine-override", "hgi",
        "--heads", "next_gru", "--input-type", "checkin", "--target", "category",
        "--folds", str(folds), "--epochs", str(epochs), "--seed", "42",
        "--tag", cat_tag,
    ]
    cmd_reg = [
        sys.executable, "scripts/p1_region_head_ablation.py",
        "--state", probe_state, "--engine-override", "hgi",
        "--region-emb-source", "hgi",
        "--heads", "next_getnext_hard", "--input-type", "region",
        "--folds", str(folds), "--epochs", str(epochs), "--seed", "42",
        "--override-hparams", "d_model=256", "num_heads=8",
        f"transition_path={TRANSITION_FOLD1}",
        "--per-fold-transition-dir", str(C2HGI_AZ_DIR),
        "--tag", reg_tag,
    ]
    rcs = {}
    for label, cmd in [("cat", cmd_cat), ("reg", cmd_reg)]:
        print(f"  >>> {label}: {' '.join(cmd[-6:])}")
        rcs[label] = subprocess.call(cmd, cwd=str(REPO_ROOT))
    return rcs


# ============================================================================
# Driver
# ============================================================================


VARIANT_SPECS = {
    "A_sum_lam0.001": ("A_sum", {"le_lambda": 0.001}),
    "A_sum_lam0.01":  ("A_sum", {"le_lambda": 0.01}),
    "A_sum_lam0.1":   ("A_sum", {"le_lambda": 0.1}),
    "C_balanced":     ("C_bal", {"lambda_f": 0.1, "lambda_c": 1.0, "gamma": 0.5}),
    "D_orth":         ("D_orth", {"lambda_f": 0.1, "lambda_c": 1.0, "gamma": 0.5}),
}


def _run_variant(variant: str, poi2vec_epochs: int) -> dict:
    kind, kw = VARIANT_SPECS[variant]
    probe_state = f"arizona_cat{variant}"
    setup_evaluation_symlinks(probe_state)
    if kind == "A_sum":
        metrics = variant_a_sum(probe_state, poi2vec_epochs, **kw)
    elif kind == "C_bal":
        metrics = variant_c_balanced(probe_state, poi2vec_epochs, **kw)
    elif kind == "D_orth":
        metrics = variant_d_orth(probe_state, poi2vec_epochs, **kw)
    else:
        raise ValueError(kind)
    ensure_mtl_inputs(probe_state)
    rcs = run_northstar(probe_state, folds=ARGS.ns_folds, epochs=ARGS.ns_epochs)
    metrics["northstar_rc"] = rcs
    metrics_path = IoPaths.HGI.get_state_dir(probe_state) / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    global ARGS
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", choices=[*VARIANT_SPECS.keys(), "all"], required=True)
    ap.add_argument("--poi2vec-epochs", type=int, default=30)
    ap.add_argument("--epoch", type=int, default=2000, help="HGI training epochs")
    ap.add_argument("--ns-folds", type=int, default=5)
    ap.add_argument("--ns-epochs", type=int, default=30)
    ARGS = ap.parse_args()

    if ARGS.variant == "all":
        out = {}
        for v in VARIANT_SPECS:
            out[v] = _run_variant(v, ARGS.poi2vec_epochs)
    else:
        _run_variant(ARGS.variant, ARGS.poi2vec_epochs)


if __name__ == "__main__":
    main()
