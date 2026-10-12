#!/usr/bin/env python3
"""Probe — three ways to inject CATEGORY into HGI's POI2Vec, evaluated on AZ.

Variants
--------
- baseline : canonical POI2Vec at fclass granularity, fresh re-run at the same
             epoch budget as A/B/C so comparisons are apples-to-apples.
             (The existing output/hgi/arizona/ was trained at 100 epochs; we
             re-train at --poi2vec-epochs here for a fair comparison.)

- A : fix the latent bug in EmbeddingModel — give CATEGORY its own
      nn.Embedding(num_cat, D) table (currently category IDs alias the first
      num_cat rows of the fclass table). Raise the hierarchical L2 weight from
      1e-8 to a meaningful value (default 0.1). POI reconstruction unchanged:
      poi_emb = fclass_emb[f]. Category info enters only through the L2 pull.

- B : train POI2Vec twice — once at fclass (vocab 305), once at category
      (vocab 7). Concatenate per-POI to 128-dim, then reduce to 64-dim via
      PCA. Both signals explicit; no hierarchy regulariser needed.

- C : single training, two embedding tables. Each Node2Vec walk yields a
      fclass sequence AND a category sequence; loss = skip_gram(fclass) +
      skip_gram(category). POI reconstruction is the additive composition
      poi_emb = fclass_emb[f] + gamma * cat_emb[c] (gamma default 0.5).

Outputs land in output/hgi/arizona_cat{baseline,A,B,C}/, isolated from the
canonical arizona run. Each variant writes a JSON record of (fclass_probe,
cat_probe, embedding stats, wall time) into the same dir for later comparison.

Usage:
    PYTHONPATH=src:research python scripts/probe/build_hgi_category_variants.py \\
        --variant {baseline,A,B,C} [--poi2vec-epochs 30] [--epoch 2000]

    # convenience: --variant all  runs the four in sequence.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pickle as pkl
import random
import shutil
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

from configs.paths import IoPaths  # noqa: E402
import embeddings.hgi.hgi as hgi_mod  # noqa: E402
from embeddings.hgi.poi2vec import POI2Vec, POISet, EmbeddingModel  # noqa: E402


CANONICAL_STATE = "arizona"


# ============================================================================
# Common helpers
# ============================================================================


def setup_probe_temp_dir(probe_state: str, use_category_as_fclass: bool = False) -> Path:
    """Build a per-variant temp dir: copy canonical edges.csv + canonical pois.csv.

    If use_category_as_fclass=True, overwrite the 'fclass' column with 'category'
    (used by variant B's second pass and by the older category-only baseline).
    """
    src_temp = IoPaths.HGI.get_temp_dir(CANONICAL_STATE)
    dst_temp = IoPaths.HGI.get_temp_dir(probe_state)
    dst_temp.mkdir(parents=True, exist_ok=True)
    shutil.copy(src_temp / "edges.csv", dst_temp / "edges.csv")
    pois = pd.read_csv(src_temp / "pois.csv")
    if use_category_as_fclass:
        pois = pois.copy()
        pois["fclass"] = pois["category"]
    pois.to_csv(dst_temp / "pois.csv", index=False)
    return dst_temp


def save_poi2vec_output(probe_temp: Path, embeddings: np.ndarray, placeids: list[int]) -> Path:
    """Write per-POI embeddings as the tensor format preprocess_hgi expects."""
    path = probe_temp / "poi_embeddings.pt"
    torch.save({
        "in_embed.weight": torch.tensor(embeddings, dtype=torch.float32),
        "placeids": placeids,
    }, path)
    return path


def build_probe_pickle(probe_temp: Path, new_poi_emb_path: Path) -> Path:
    """Load canonical AZ gowalla.pt, swap node_features, save into probe dir."""
    src_pkl = IoPaths.HGI.get_temp_dir(CANONICAL_STATE) / "gowalla.pt"
    with open(src_pkl, "rb") as f:
        data = pkl.load(f)
    blob = torch.load(new_poi_emb_path)
    new_features = blob["in_embed.weight"].numpy().astype(np.float32)
    new_placeids = [int(p) for p in blob["placeids"]]
    canonical_placeids = [int(p) for p in data["place_id"]]
    if new_placeids != canonical_placeids:
        order = {pid: i for i, pid in enumerate(new_placeids)}
        idx = np.array([order[pid] for pid in canonical_placeids], dtype=np.int64)
        new_features = new_features[idx]
    assert new_features.shape == data["node_features"].shape, (
        f"shape mismatch: {new_features.shape} vs {data['node_features'].shape}"
    )
    data["node_features"] = new_features
    dst_pkl = probe_temp / "gowalla.pt"
    with open(dst_pkl, "wb") as f:
        pkl.dump(data, f)
    return dst_pkl


def train_hgi_on_probe(probe_state: str, epoch: int) -> None:
    args = Namespace(
        dim=64, attention_head=4, alpha=0.5,
        lr=0.006, gamma=1.0, max_norm=0.9, warmup_period=40,
        epoch=epoch, device="cpu",
    )
    hgi_mod.train_hgi(probe_state, args)


def fclass_linear_probe(probe_state: str, label_col: str = "fclass",
                        min_per_class: int = 5) -> float:
    """5-fold linear probe accuracy from POI embedding → {fclass, category}."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import StandardScaler
    pois = pd.read_csv(IoPaths.HGI.get_temp_dir(CANONICAL_STATE) / "pois.csv")
    label_by_pid = dict(zip(pois["placeid"].astype(int), pois[label_col].astype(int)))
    emb_path = IoPaths.HGI.get_state_dir(probe_state) / "embeddings.parquet"
    if not emb_path.exists():
        return float("nan")
    df = pd.read_parquet(emb_path)
    emb_cols = [c for c in df.columns if c.isdigit()]
    X = df[emb_cols].values.astype(np.float32)
    y = np.array([label_by_pid.get(int(p), -1) for p in df["placeid"]], dtype=np.int64)
    keep = y >= 0
    X, y = X[keep], y[keep]
    counts = pd.Series(y).value_counts()
    valid = set(counts[counts >= min_per_class].index)
    m = np.array([yi in valid for yi in y])
    X, y = X[m], y[m]
    if len(np.unique(y)) < 2:
        return float("nan")
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    accs = []
    for tr, te in kf.split(X, y):
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(max_iter=2000)
        clf.fit(sc.transform(X[tr]), y[tr])
        accs.append(clf.score(sc.transform(X[te]), y[te]))
    return float(np.mean(accs))


def embedding_stats(probe_state: str) -> dict:
    """Summary stats on the POI and region embeddings of a probe state."""
    poi_path = IoPaths.HGI.get_state_dir(probe_state) / "embeddings.parquet"
    reg_path = IoPaths.HGI.get_state_dir(probe_state) / "region_embeddings.parquet"
    df = pd.read_parquet(poi_path)
    rdf = pd.read_parquet(reg_path)
    X = df[[c for c in df.columns if c.isdigit()]].values
    R = rdf[[c for c in rdf.columns if c.startswith("reg_")]].values
    return {
        "n_pois": int(len(df)),
        "poi_unique_rows": int(np.unique(X, axis=0).shape[0]),
        "poi_norm_mean": float(np.linalg.norm(X, axis=1).mean()),
        "poi_dim_std_mean": float(X.std(0).mean()),
        "n_regions": int(len(rdf)),
        "region_norm_mean": float(np.linalg.norm(R, axis=1).mean()),
        "region_dim_std_mean": float(R.std(0).mean()),
    }


# ============================================================================
# Variant A — separate category embedding table + meaningful λ
# ============================================================================


class EmbeddingModelA(nn.Module):
    """Skip-gram + hierarchical L2 with a SEPARATE category embedding table.

    Fixes the canonical bug where category IDs (LabelEncoder 0..num_cat-1) aliased
    the first num_cat rows of the fclass table.
    """

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
            loss_hier = 0.5 * self.le_lambda * (diff * diff).sum() / len(self.hierarchy_pairs)
        else:
            loss_hier = torch.tensor(0.0, device=center.device)
        return loss_skip + loss_hier, loss_hier

    def get_embeddings(self):
        return self.in_embed.weight.detach().cpu().numpy()


def variant_a(probe_state: str, poi2vec_epochs: int, le_lambda: float = 0.1) -> dict:
    """Run variant A end-to-end. Returns metrics dict."""
    print(f"\n{'=' * 80}\nVARIANT A — separate category table, λ={le_lambda}\n{'=' * 80}")
    t0 = time.time()
    probe_temp = setup_probe_temp_dir(probe_state, use_category_as_fclass=False)
    pois = pd.read_csv(probe_temp / "pois.csv")
    n_cat = int(pois["category"].max()) + 1

    # Bootstrap the canonical POI2Vec object (gets walks + co-occurrence)
    p2v = POI2Vec(
        edges_file=str(probe_temp / "edges.csv"),
        pois_file=str(probe_temp / "pois.csv"),
        embedding_dim=64,
        device=torch.device("cpu"),
    )
    p2v.generate_walks(batch_size=128)

    # Pull (category, fclass) hierarchy pairs from pois.csv.
    pairs = list(set(tuple(r) for r in pois[["category", "fclass"]].values))

    ds = POISet(p2v.vocab_size, p2v.fclass_walks, p2v.global_co_occurrence, k=5)
    model = EmbeddingModelA(p2v.vocab_size, n_cat, 64, pairs, le_lambda=le_lambda)
    opt = torch.optim.Adam(model.parameters(), lr=0.05)
    loader = torch.utils.data.DataLoader(ds, batch_size=2048, shuffle=True,
                                         num_workers=10, persistent_workers=True)

    best_loss, best_emb = math.inf, None
    model.train()
    for ep in range(poi2vec_epochs):
        tot, num = 0.0, 0
        for center, pos, neg in tqdm(loader, desc=f"A ep {ep+1}/{poi2vec_epochs}"):
            opt.zero_grad()
            loss, _ = model(center, pos, neg)
            loss.backward()
            opt.step()
            tot += loss.item(); num += 1
        avg = tot / max(num, 1)
        if avg < best_loss:
            best_loss = avg
            best_emb = model.get_embeddings().copy()
        print(f"  A epoch {ep+1}: loss={avg:.4f}")
    fclass_emb = best_emb if best_emb is not None else model.get_embeddings()

    # Reconstruct POI emb = fclass_emb[fclass]
    fclass_vals = pois["fclass"].values.astype(int)
    poi_emb = fclass_emb[fclass_vals].astype(np.float32)
    placeids = pois["placeid"].astype(int).tolist()
    poi_path = save_poi2vec_output(probe_temp, poi_emb, placeids)

    build_probe_pickle(probe_temp, poi_path)
    train_hgi_on_probe(probe_state, epoch=ARGS.epoch)

    metrics = {
        "variant": "A", "wall_time_min": (time.time() - t0) / 60,
        "poi2vec_epochs": poi2vec_epochs, "hgi_epochs": ARGS.epoch,
        "le_lambda": le_lambda,
        "fclass_probe": fclass_linear_probe(probe_state, "fclass"),
        "category_probe": fclass_linear_probe(probe_state, "category", min_per_class=10),
        **embedding_stats(probe_state),
    }
    return metrics


# ============================================================================
# Variant B — concat fclass + category, PCA to 64
# ============================================================================


def _train_canonical_poi2vec(probe_temp: Path, epochs: int) -> np.ndarray:
    """Train canonical POI2Vec given a probe_temp containing edges.csv + pois.csv.
    Returns the per-POI embedding matrix (after fclass→POI reconstruction)."""
    p2v = POI2Vec(
        edges_file=str(probe_temp / "edges.csv"),
        pois_file=str(probe_temp / "pois.csv"),
        embedding_dim=64,
        device=torch.device("cpu"),
    )
    p2v.generate_walks(batch_size=128)
    fclass_emb = p2v.train(epochs=epochs, batch_size=2048, lr=0.05, k=5,
                           le_lambda=1e-8)  # canonical lambda — effectively zero
    pois = pd.read_csv(probe_temp / "pois.csv")
    fclass_vals = pois["fclass"].values.astype(int)
    return fclass_emb[fclass_vals].astype(np.float32)


def variant_b(probe_state: str, poi2vec_epochs: int) -> dict:
    """Run variant B: train POI2Vec twice (fclass-, then category-encoded), concat, PCA."""
    print(f"\n{'=' * 80}\nVARIANT B — concat fclass + category, PCA→64\n{'=' * 80}")
    t0 = time.time()

    # Pass 1: fclass-encoded pois.csv
    fclass_dir = setup_probe_temp_dir(probe_state + "_fcpass", use_category_as_fclass=False)
    print(">> Pass 1: POI2Vec at fclass granularity")
    fclass_poi_emb = _train_canonical_poi2vec(fclass_dir, poi2vec_epochs)

    # Pass 2: category-encoded pois.csv
    cat_dir = setup_probe_temp_dir(probe_state + "_catpass", use_category_as_fclass=True)
    print(">> Pass 2: POI2Vec at category granularity")
    cat_poi_emb = _train_canonical_poi2vec(cat_dir, poi2vec_epochs)

    # Concat 64+64=128, then PCA to 64
    concat = np.concatenate([fclass_poi_emb, cat_poi_emb], axis=1).astype(np.float32)
    print(f"  concat shape: {concat.shape}, reducing to 64 dims via PCA")
    from sklearn.decomposition import PCA
    pca = PCA(n_components=64, random_state=42)
    reduced = pca.fit_transform(concat).astype(np.float32)
    print(f"  PCA explained variance ratio (top 5): "
          f"{[round(float(x), 4) for x in pca.explained_variance_ratio_[:5]]}")
    print(f"  PCA total variance retained: {pca.explained_variance_ratio_.sum():.4f}")

    probe_temp = setup_probe_temp_dir(probe_state, use_category_as_fclass=False)
    pois = pd.read_csv(probe_temp / "pois.csv")
    placeids = pois["placeid"].astype(int).tolist()
    poi_path = save_poi2vec_output(probe_temp, reduced, placeids)

    build_probe_pickle(probe_temp, poi_path)
    train_hgi_on_probe(probe_state, epoch=ARGS.epoch)

    return {
        "variant": "B", "wall_time_min": (time.time() - t0) / 60,
        "poi2vec_epochs": poi2vec_epochs, "hgi_epochs": ARGS.epoch,
        "pca_variance_retained": float(pca.explained_variance_ratio_.sum()),
        "fclass_probe": fclass_linear_probe(probe_state, "fclass"),
        "category_probe": fclass_linear_probe(probe_state, "category", min_per_class=10),
        **embedding_stats(probe_state),
    }


# ============================================================================
# Variant C — joint skip-gram on both vocabs, additive composition
# ============================================================================


class JointPOISet(torch.utils.data.Dataset):
    """Like POISet but emits BOTH fclass and category indices per walk position."""

    def __init__(self, vocab_fclass, vocab_cat, fclass_walks, cat_walks,
                 fclass_neg_cands, cat_neg_cands, k=5):
        assert len(fclass_walks) == len(cat_walks)
        self.fclass_walks = fclass_walks
        self.cat_walks = cat_walks
        self.fclass_neg = fclass_neg_cands  # list[list[int]] indexed by center fclass
        self.cat_neg = cat_neg_cands        # list[list[int]] indexed by center category
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


class EmbeddingModelC(nn.Module):
    """Two skip-gram heads — one over fclass vocab, one over category vocab — sharing nothing."""

    def __init__(self, vocab_fclass, vocab_cat, embed_size):
        super().__init__()
        self.f_in = nn.Embedding(vocab_fclass, embed_size)
        self.f_out = nn.Embedding(vocab_fclass, embed_size)
        self.c_in = nn.Embedding(vocab_cat, embed_size)
        self.c_out = nn.Embedding(vocab_cat, embed_size)
        for emb in [self.f_in, self.f_out, self.c_in, self.c_out]:
            nn.init.xavier_uniform_(emb.weight)

    def _skip_gram(self, in_t, out_t, center, pos, neg):
        c = in_t(center).unsqueeze(2)
        lp = F.logsigmoid(torch.bmm(out_t(pos), c).squeeze(2)).sum(1)
        ln = F.logsigmoid(torch.bmm(out_t(neg), -c).squeeze(2)).sum(1)
        return -(lp + ln).mean()

    def forward(self, cf, cc, pf, pc, nf, nc):
        loss_f = self._skip_gram(self.f_in, self.f_out, cf, pf, nf)
        loss_c = self._skip_gram(self.c_in, self.c_out, cc, pc, nc)
        return loss_f + loss_c, loss_f, loss_c

    def fclass_embeddings(self):
        return self.f_in.weight.detach().cpu().numpy()

    def cat_embeddings(self):
        return self.c_in.weight.detach().cpu().numpy()


def variant_c(probe_state: str, poi2vec_epochs: int, gamma: float = 0.5) -> dict:
    """Joint skip-gram on both vocabs, POI emb = fclass + γ·category."""
    print(f"\n{'=' * 80}\nVARIANT C — joint skip-gram + additive (γ={gamma})\n{'=' * 80}")
    t0 = time.time()
    probe_temp = setup_probe_temp_dir(probe_state, use_category_as_fclass=False)
    pois = pd.read_csv(probe_temp / "pois.csv")
    vocab_fclass = int(pois["fclass"].max()) + 1
    vocab_cat = int(pois["category"].max()) + 1

    # Generate POI walks once, convert to BOTH fclass and category sequences.
    edges = pd.read_csv(probe_temp / "edges.csv")
    edge_index = torch.tensor(edges[["source", "target"]].values.T, dtype=torch.long)
    n2v = Node2Vec(edge_index=edge_index, embedding_dim=64, walk_length=10,
                   context_size=5, walks_per_node=5, p=0.5, q=0.5, sparse=True)
    fclass_walks, cat_walks = [], []
    fclass_arr = pois["fclass"].values.astype(int)
    cat_arr = pois["category"].values.astype(int)
    print("Generating POI walks → (fclass, category) sequences ...")
    for pos_rw, _ in tqdm(n2v.loader(batch_size=128, shuffle=True, num_workers=0)):
        for walk in pos_rw:
            poi_ids = walk.tolist()
            fclass_walks.append([int(fclass_arr[p]) for p in poi_ids])
            cat_walks.append([int(cat_arr[p]) for p in poi_ids])

    # Co-occurrence + negative candidates per vocab.
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

    print("  building negative candidate lists ...")
    f_neg = neg_candidates(fclass_walks, vocab_fclass)
    c_neg = neg_candidates(cat_walks, vocab_cat)

    ds = JointPOISet(vocab_fclass, vocab_cat, fclass_walks, cat_walks,
                     f_neg, c_neg, k=5)
    model = EmbeddingModelC(vocab_fclass, vocab_cat, 64)
    opt = torch.optim.Adam(model.parameters(), lr=0.05)
    loader = torch.utils.data.DataLoader(ds, batch_size=2048, shuffle=True,
                                         num_workers=10, persistent_workers=True)

    best_loss = math.inf
    best_f, best_c = None, None
    model.train()
    for ep in range(poi2vec_epochs):
        tot, lf, lc, num = 0.0, 0.0, 0.0, 0
        for cf, cc, pf, pc, nf, nc in tqdm(loader, desc=f"C ep {ep+1}/{poi2vec_epochs}"):
            opt.zero_grad()
            loss, loss_f, loss_c = model(cf, cc, pf, pc, nf, nc)
            loss.backward()
            opt.step()
            tot += loss.item(); lf += loss_f.item(); lc += loss_c.item(); num += 1
        avg = tot / max(num, 1)
        print(f"  C epoch {ep+1}: loss={avg:.4f}  (fclass={lf/num:.4f}  cat={lc/num:.4f})")
        if avg < best_loss:
            best_loss = avg
            best_f = model.fclass_embeddings().copy()
            best_c = model.cat_embeddings().copy()

    fclass_vals = pois["fclass"].values.astype(int)
    cat_vals = pois["category"].values.astype(int)
    poi_emb = (best_f[fclass_vals] + gamma * best_c[cat_vals]).astype(np.float32)
    placeids = pois["placeid"].astype(int).tolist()
    poi_path = save_poi2vec_output(probe_temp, poi_emb, placeids)

    build_probe_pickle(probe_temp, poi_path)
    train_hgi_on_probe(probe_state, epoch=ARGS.epoch)

    return {
        "variant": "C", "wall_time_min": (time.time() - t0) / 60,
        "poi2vec_epochs": poi2vec_epochs, "hgi_epochs": ARGS.epoch,
        "gamma": gamma,
        "fclass_probe": fclass_linear_probe(probe_state, "fclass"),
        "category_probe": fclass_linear_probe(probe_state, "category", min_per_class=10),
        **embedding_stats(probe_state),
    }


# ============================================================================
# Variant baseline — canonical fclass-only POI2Vec, re-run at the same epochs
# ============================================================================


def variant_baseline(probe_state: str, poi2vec_epochs: int) -> dict:
    """Apples-to-apples canonical: same as existing arizona run, but at this
    epoch budget so the comparison against A/B/C is fair."""
    print(f"\n{'=' * 80}\nVARIANT baseline — canonical fclass POI2Vec, "
          f"re-run at {poi2vec_epochs} epochs\n{'=' * 80}")
    t0 = time.time()
    probe_temp = setup_probe_temp_dir(probe_state, use_category_as_fclass=False)
    poi_emb = _train_canonical_poi2vec(probe_temp, poi2vec_epochs)
    pois = pd.read_csv(probe_temp / "pois.csv")
    placeids = pois["placeid"].astype(int).tolist()
    poi_path = save_poi2vec_output(probe_temp, poi_emb, placeids)
    build_probe_pickle(probe_temp, poi_path)
    train_hgi_on_probe(probe_state, epoch=ARGS.epoch)
    return {
        "variant": "baseline", "wall_time_min": (time.time() - t0) / 60,
        "poi2vec_epochs": poi2vec_epochs, "hgi_epochs": ARGS.epoch,
        "fclass_probe": fclass_linear_probe(probe_state, "fclass"),
        "category_probe": fclass_linear_probe(probe_state, "category", min_per_class=10),
        **embedding_stats(probe_state),
    }


# ============================================================================
# Driver
# ============================================================================


ARGS: Namespace = None  # populated in main()


def _run(variant: str, poi2vec_epochs: int) -> dict:
    probe_state = f"arizona_cat{variant}"
    funcs = {
        "baseline": lambda: variant_baseline(probe_state, poi2vec_epochs),
        "A": lambda: variant_a(probe_state, poi2vec_epochs, le_lambda=ARGS.le_lambda),
        "B": lambda: variant_b(probe_state, poi2vec_epochs),
        "C": lambda: variant_c(probe_state, poi2vec_epochs, gamma=ARGS.gamma),
    }
    metrics = funcs[variant]()
    out_path = IoPaths.HGI.get_state_dir(probe_state) / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[{variant}] metrics → {out_path}")
    print(json.dumps(metrics, indent=2))
    return metrics


def main():
    global ARGS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=["baseline", "A", "B", "C", "all"],
                        required=True)
    parser.add_argument("--poi2vec-epochs", type=int, default=30,
                        help="POI2Vec epochs (default 30; canonical default is 100). "
                             "Lower for faster iteration; all variants use the same.")
    parser.add_argument("--epoch", type=int, default=2000, help="HGI training epochs")
    parser.add_argument("--le-lambda", type=float, default=0.1,
                        help="Hierarchical L2 weight for variant A")
    parser.add_argument("--gamma", type=float, default=0.5,
                        help="Additive blend weight for variant C")
    ARGS = parser.parse_args()

    if ARGS.variant == "all":
        results = {}
        for v in ["baseline", "A", "B", "C"]:
            results[v] = _run(v, ARGS.poi2vec_epochs)
        # Final compact table
        print(f"\n{'=' * 80}\nFINAL COMPARISON\n{'=' * 80}")
        keys = ["variant", "poi2vec_epochs", "fclass_probe", "category_probe",
                "poi_norm_mean", "poi_dim_std_mean", "wall_time_min"]
        rows = [[r.get(k) for k in keys] for r in results.values()]
        print(pd.DataFrame(rows, columns=keys).to_string(index=False))
    else:
        _run(ARGS.variant, ARGS.poi2vec_epochs)


if __name__ == "__main__":
    main()
