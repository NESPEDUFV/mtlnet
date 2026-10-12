"""Preliminary prototype: an adjacency-AWARE next-region head.

Tests the hypothesis that a substrate with higher region adj_coh (sidefeat) has
spatial structure that a head exploiting the region-adjacency graph can convert to
next-region accuracy. Cheap proxy for a full region-GNN head: propagate the region
embeddings k hops over the geographic adjacency graph (symmetric-normalized GCN
propagation Â^k·E) BEFORE the 1-step transition probe. k=0 = the current linear
probe; k>0 = adjacency-aware. Compare control vs candidate across k.

If k>0 lifts next-region (esp. for the higher-adj_coh substrate), an adjacency-aware
head unlocks the structure → the L0 adj_coh signal is exploitable, not just geometry.
"""
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
for p in (_root, _root / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.model_selection import KFold

from configs.paths import EmbeddingEngine, IoPaths
from scripts.embedding_eval.region_eval import load_pairs, load_region_emb
from tracking.metrics import compute_classification_metrics


def _norm_adj(state: str, R: int) -> np.ndarray:
    """Symmetric-normalized adjacency with self-loops: D^-1/2 (A+I) D^-1/2  [R,R]."""
    g = pickle.load(open(IoPaths.CHECK2HGI.get_graph_data_file(state), "rb"))
    ei = np.asarray(g["region_adjacency"])
    A = np.eye(R, dtype=np.float32)
    for a, b in zip(ei[0], ei[1]):
        if a < R and b < R:
            A[int(a), int(b)] = 1.0; A[int(b), int(a)] = 1.0
    d = A.sum(1); dinv = 1.0 / np.sqrt(np.clip(d, 1e-6, None))
    return (A * dinv[None, :]) * dinv[:, None]


def _probe(X, y, n_classes, seed=42, epochs=300):
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    accs = []
    for tr, te in KFold(5, shuffle=True, random_state=seed).split(X):
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        xtr = torch.from_numpy(((X[tr]-mu)/sd).astype(np.float32)).to(dev)
        ytr = torch.from_numpy(y[tr]).long().to(dev)
        xte = torch.from_numpy(((X[te]-mu)/sd).astype(np.float32)).to(dev)
        yte = torch.from_numpy(y[te]).long().to(dev)
        clf = torch.nn.Linear(X.shape[1], n_classes).to(dev)
        opt = torch.optim.AdamW(clf.parameters(), lr=1e-2)
        gen = torch.Generator().manual_seed(seed)
        best, bad, bs = 1e9, 0, None
        for _ in range(epochs):
            perm = torch.randperm(xtr.shape[0], generator=gen).to(dev)
            for i in range(0, len(perm), 8192):
                b = perm[i:i+8192]; opt.zero_grad()
                F.cross_entropy(clf(xtr[b]), ytr[b]).backward(); opt.step()
            with torch.no_grad():
                l = F.cross_entropy(clf(xte), yte).item()
            if l < best-1e-4: best, bad, bs = l, 0, {k:v.clone() for k,v in clf.state_dict().items()}
            else:
                bad += 1
                if bad >= 15: break
        if bs: clf.load_state_dict(bs)
        with torch.no_grad():
            m = compute_classification_metrics(clf(xte), yte, num_classes=n_classes, top_k=(5,10))
        accs.append((m["accuracy"], m["top10_acc"]))
    a = np.array(accs)
    return a.mean(0), a.std(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engines", nargs="+", required=True)
    ap.add_argument("--state", default="florida")
    ap.add_argument("--khops", nargs="+", type=int, default=[0, 1, 2])
    args = ap.parse_args()

    last, nxt = load_pairs(args.state)
    uniq, nxt = np.unique(nxt, return_inverse=True); nxt = nxt.astype(np.int64)
    n_classes = len(uniq)
    print(f"[{args.state}] {len(last)} pairs, {n_classes} next-regions. Adjacency-aware (GCN^k) transition probe.\n")
    print(f"{'engine':24s}{'k':>3s}{'Acc@1':>16s}{'Acc@10':>16s}")
    Ahat = None
    for name in args.engines:
        emb, R = load_region_emb(args.state, EmbeddingEngine(name))
        if emb is None: print(f"{name} MISSING"); continue
        if Ahat is None or Ahat.shape[0] != R:
            Ahat = _norm_adj(args.state, R)
        E = emb.copy()
        for k in args.khops:
            Ek = E if k == 0 else np.linalg.matrix_power(Ahat, k) @ E
            (a1, a10), (s1, s10) = _probe(Ek[last], nxt, n_classes)
            print(f"{name:24s}{k:>3d}{f'{a1:.4f}±{s1:.4f}':>16s}{f'{a10:.4f}±{s10:.4f}':>16s}")
        print()


if __name__ == "__main__":
    main()
