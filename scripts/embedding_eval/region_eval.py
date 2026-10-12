"""Corrected L0/L1 for next-reg using REGION embeddings (the actual task input).

The category probe (run.py) feeds the per-item *final* embedding — correct for
next-cat. But next-reg's real input is the **region embedding**
(`region_embeddings.parquet`, cols reg_0..reg_D), looked up per sequence step via
placeid->region (the `--task-b-input-type region` modality; the docs show region
input gives ~53% Acc@10 vs ~20% on checkin input). So next-reg must be screened
on the region-embedding artifact, NOT the final embedding.

Region ids are the SHARED census-tract partition (check2hgi poi_to_region); both
HGI and Check2HGI region_embeddings.parquet are indexed by the same region_id,
which is exactly how p1_region_head_ablation.py looks them up for either engine.

╔══════════════════════════════════════════════════════════════════════════════╗
║ ⚠ next-reg L0/L1 ARE DIAGNOSTICS, NOT RANKERS — see L0_METHODOLOGY.md          ║
║                                                                                ║
║ next-reg is a TRANSITION task: the predictive signal lives in log_T, NOT in    ║
║ the static region geometry (empirically corr(region-cosine, T_ij) ~= 0.05).    ║
║ We validated 8 static metrics (adjacency, transition-alignment, crs-align, ...)║
║ — NONE ranks substrates concordantly with L2. So:                              ║
║   • DO NOT use any metric below to CROWN a region substrate.                   ║
║   • RANK next-reg substrates at L2 only: p1_region_head_ablation.py            ║
║       --heads next_stan_flow --input-type region --folds 5 (multi-seed).       ║
║   • The metrics below are DIAGNOSTICS that flag ONE geometric axis each, used  ║
║     to EXPLAIN an L2 result, never to decide it.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Diagnostics computed here (all train-free):
- adjacency coherence: fraction of each region's cosine-kNN that are graph-adjacent
  (region_adjacency). Flags the GEOGRAPHIC-adjacency axis. NOTE: log_T-redundant and
  anti-ranks design_b — diagnostic only.
- region-silhouette (POI-level, label=poi_to_region; see ``region_silhouette``): flags
  the SPATIAL-COHESION axis. The one diagnostic that concordantly localizes HGI's
  cross-substrate next-reg advantage (HGI ~ -0.46 vs Check2HGI family ~ -0.65). Still
  NOT a within-family ranker.
- linear CKA across engines: "same space?" diagnostic only, never a quality signal.
- 1-step transition probe (L1): given the CURRENT region embedding, linearly predict the
  NEXT region. A 1-step-Markov reduction of the 9-window+log_T task — near-tie across
  engines (self-transition ~0.49), too crude to resolve the gap. Diagnostic only.
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
from sklearn.model_selection import train_test_split

from configs.paths import EmbeddingEngine, IoPaths
from tracking.metrics import compute_classification_metrics


def _dev():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_region_emb(state: str, engine: EmbeddingEngine):
    """Return (emb [R,D] indexed by region_id, n_regions). Missing ids -> zeros."""
    import pandas as pd
    path = IoPaths.get_embedd(state, engine).parent / "region_embeddings.parquet"
    if not path.exists():
        return None, 0
    df = pd.read_parquet(path)
    reg_cols = [c for c in df.columns if str(c).startswith("reg_")]
    rid = df["region_id"].to_numpy(dtype=np.int64)
    R = int(rid.max()) + 1
    emb = np.zeros((R, len(reg_cols)), dtype=np.float32)
    emb[rid] = df[reg_cols].to_numpy(dtype=np.float32)
    return emb, R


def load_pairs(state: str):
    """(current_region, next_region) from the shared check2hgi next_region.parquet."""
    nr = IoPaths.load_next_region(state, EmbeddingEngine.CHECK2HGI)
    last = nr["last_region_idx"].to_numpy(dtype=np.int64)
    nxt = nr["region_idx"].to_numpy(dtype=np.int64)
    m = last >= 0
    return last[m], nxt[m]


def adjacency_coherence(emb: np.ndarray, state: str, k: int = 10,
                        n_folds: int = 5, seed: int = 42):
    """Per-region fraction of cosine top-k NN that are graph-adjacent. kNN runs
    over the full (fixed) region set; variance comes from averaging the per-region
    coherence over 5 disjoint region-folds. Returns (mean, sd)."""
    from sklearn.model_selection import KFold
    g = pickle.load(open(IoPaths.CHECK2HGI.get_graph_data_file(state), "rb"))
    ei = np.asarray(g["region_adjacency"])
    R = emb.shape[0]
    adj = [set() for _ in range(R)]
    for a, b in zip(ei[0], ei[1]):
        if a < R and b < R:
            adj[int(a)].add(int(b)); adj[int(b)].add(int(a))
    has = (np.linalg.norm(emb, axis=1) > 0)
    dev = _dev()
    x = F.normalize(torch.from_numpy(emb).to(dev, torch.float32), dim=1)
    sims = x @ x.T
    sims.fill_diagonal_(float("-inf"))
    nn = sims.topk(min(k, R - 1), dim=1).indices.cpu().numpy()
    scored = [r for r in range(R) if has[r] and adj[r]]
    per_region = np.array([np.mean([n in adj[r] for n in nn[r]]) for r in scored])
    if len(per_region) < n_folds:
        return float(per_region.mean()) if len(per_region) else float("nan"), 0.0
    fold_means = [per_region[te].mean() for _, te in
                  KFold(n_folds, shuffle=True, random_state=seed).split(per_region)]
    return float(np.mean(fold_means)), float(np.std(fold_means, ddof=1))


def region_silhouette(state: str, engine_dir: str, sample: int = 10000, seed: int = 0):
    """SPATIAL-COHESION diagnostic (the validated cross-substrate next-reg flag).

    Clusters the POI-level embeddings by their REGION (label = poi_to_region, the
    task's own label space — NOT the 7 categories), and reports region-silhouette +
    region-kNN-accuracy. A higher (less negative) silhouette means POIs in the same
    region sit together → the embedding carries POI-level spatial cohesion, which is
    the axis HGI's Delaunay graph raises and where it leads next-reg (HGI ~ -0.46 vs
    Check2HGI family ~ -0.65).

    ⚠ DIAGNOSTIC, NOT A RANKER. It concordantly localizes HGI's CROSS-substrate
    advantage, but it anti-ranks WITHIN the Check2HGI family (design_b's fclass lowers
    cohesion yet helps the head). Use it to EXPLAIN the spatial axis, never to crown a
    substrate — that is L2's job. See L0_METHODOLOGY.md.

    ``engine_dir`` is the output/ subdir name (e.g. 'hgi', 'check2hgi_resln_design_b').
    Reads poi_embeddings.parquet, or embeddings.parquet for POI-level HGI.
    """
    import pandas as pd
    from scripts.embedding_eval.geometry import knn_loo, silhouette as _sil
    base = _root / "output" / engine_dir / state.lower()
    path = base / "poi_embeddings.parquet"
    if not path.exists():
        path = base / "embeddings.parquet"   # HGI stores POI-level emb here
    df = pd.read_parquet(path)
    dim_cols = [c for c in df.columns if c.isdigit()]
    emb = df[dim_cols].to_numpy(np.float32)
    g = pickle.load(open(IoPaths.CHECK2HGI.get_graph_data_file(state), "rb"))
    p2i, p2r = g["placeid_to_idx"], np.asarray(g["poi_to_region"])
    reg = np.array([p2r[p2i[int(p)]] if int(p) in p2i else -1 for p in df["placeid"]])
    m = reg >= 0
    emb, reg = emb[m], reg[m]
    sil = _sil(emb, reg, sample=sample, seed=seed)
    knn = knn_loo(emb, reg, k=10)
    return {"region_silhouette": sil, "region_knn10_acc": knn["knn10_acc"]}


def transition_probe(emb, last, nxt, n_folds=5, seed=42, epochs=300, lr=1e-2):
    """5-fold CV linear probe: region_emb[current] -> next region. Returns
    {metric:(mean,sd)} over the 5 folds (mirrors L2's 5-fold protocol)."""
    from sklearn.model_selection import KFold
    uniq, nxt = np.unique(nxt, return_inverse=True)  # densify to [0,C)
    nxt = nxt.astype(np.int64)
    n_classes = len(uniq)
    X = emb[last]                       # [N, D] current region's embedding
    dev = _dev()
    runs = []
    for tr_idx, te_idx in KFold(n_folds, shuffle=True, random_state=seed).split(X):
        xtr, xte, ytr, yte = X[tr_idx], X[te_idx], nxt[tr_idx], nxt[te_idx]
        xtr, xes, ytr, yes = train_test_split(xtr, ytr, test_size=0.15, random_state=seed)
        mu, sd = xtr.mean(0, keepdims=True), xtr.std(0, keepdims=True) + 1e-6
        xtr, xes, xte = (xtr - mu) / sd, (xes - mu) / sd, (xte - mu) / sd
        xtr_t = torch.from_numpy(xtr).to(dev, torch.float32)
        ytr_t = torch.from_numpy(ytr).to(dev, torch.long)
        xes_t = torch.from_numpy(xes).to(dev, torch.float32)
        yes_t = torch.from_numpy(yes).to(dev, torch.long)
        xte_t = torch.from_numpy(xte).to(dev, torch.float32)
        yte_t = torch.from_numpy(yte).to(dev, torch.long)
        torch.manual_seed(seed)
        clf = torch.nn.Linear(X.shape[1], n_classes).to(dev)
        opt = torch.optim.AdamW(clf.parameters(), lr=lr)
        gen = torch.Generator().manual_seed(seed)
        best, best_state, bad = float("inf"), None, 0
        for _ in range(epochs):
            clf.train()
            perm = torch.randperm(xtr_t.shape[0], generator=gen).to(dev)
            for i in range(0, len(perm), 8192):
                bidx = perm[i:i + 8192]
                opt.zero_grad()
                F.cross_entropy(clf(xtr_t[bidx]), ytr_t[bidx]).backward()
                opt.step()
            clf.eval()
            with torch.no_grad():
                esl = F.cross_entropy(clf(xes_t), yes_t).item()
            if esl < best - 1e-4:
                best, bad = esl, 0
                best_state = {k: v.detach().clone() for k, v in clf.state_dict().items()}
            else:
                bad += 1
                if bad >= 20:
                    break
        if best_state:
            clf.load_state_dict(best_state)
        clf.eval()
        with torch.no_grad():
            logits = clf(xte_t)
        runs.append(compute_classification_metrics(logits, yte_t, num_classes=n_classes, top_k=(5, 10)))
    out = {}
    for key in runs[0]:
        v = np.array([r[key] for r in runs])
        out[key] = (float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0)
    return out


def main():
    ap = argparse.ArgumentParser(description="Corrected next-reg eval on region embeddings")
    ap.add_argument("--engines", nargs="+", required=True)
    ap.add_argument("--state", default="florida")
    ap.add_argument("--seed", type=int, default=42, help="5-fold shuffle seed")
    ap.add_argument("--n-folds", type=int, default=5)
    ap.add_argument("--region-silhouette", action="store_true",
                    help="Also print the POI-level region-silhouette spatial-cohesion "
                         "DIAGNOSTIC (cross-substrate HGI-gap flag; NOT a ranker).")
    args = ap.parse_args()

    last, nxt = load_pairs(args.state)
    print(f"[{args.state}] {len(last)} transition pairs, {int(nxt.max())+1} regions, "
          f"self-transition rate={np.mean(last==nxt):.3f}  (5-fold CV, mean±SD)")
    print("⚠ DIAGNOSTICS ONLY — next-reg substrate RANKING is decided at L2, never here "
          "(see L0_METHODOLOGY.md).\n")
    sil_h = f" {'reg_silhouette':>16s}" if args.region_silhouette else ""
    print(f"{'engine':30s} {'adj_coh@10':>16s} {'probe_acc':>16s} {'acc@5':>16s} {'acc@10':>16s}{sil_h}")
    for name in args.engines:
        emb, R = load_region_emb(args.state, EmbeddingEngine(name))
        if emb is None:
            print(f"{name:30s}  region_embeddings.parquet MISSING")
            continue
        am, asd = adjacency_coherence(emb, args.state, n_folds=args.n_folds, seed=args.seed)
        pr = transition_probe(emb, last, nxt, n_folds=args.n_folds, seed=args.seed)
        def cell(k): m, s = pr[k]; return f"{m:.4f}±{s:.4f}"
        sil_c = ""
        if args.region_silhouette:
            try:
                rs = region_silhouette(args.state, name)
                sil_c = f" {rs['region_silhouette']:>16.4f}"
            except Exception as e:
                sil_c = f" {'n/a':>16s}"
        print(f"{name:30s} {f'{am:.4f}±{asd:.4f}':>16s} {cell('accuracy'):>16s} "
              f"{cell('top5_acc'):>16s} {cell('top10_acc'):>16s}{sil_c}")


if __name__ == "__main__":
    main()
