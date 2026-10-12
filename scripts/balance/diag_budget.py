"""What does the embedding spend its dimensions on, and is that spend balanced?

THIS SCRIPT DOES NOT REPLACE THE EXISTING LADDER. The repository already has a four-level,
leak-aware evaluation stack, and it is the primary evidence for any claim about an embedding:

    L0  train-free geometry     scripts/embedding_eval/geometry.py   kNN-LOO, silhouette,
                                                                     centroid-separability, CKA
    L0r region diagnostics      scripts/embedding_eval/region_eval.py  adjacency-coherence
    L1  linear probe            scripts/embedding_eval/linear_probe.py
    L2  single-task sequence    scripts/embedding_eval/run.py --emit-l2l3
    L3  multi-task              scripts/embedding_eval/collect_l2l3.py
    gates leak_sniff.py, autocorrelation_ceiling.py, region_persistence.py, region_gnn_probe.py

The governing rule is in docs/studies/archive/embedding_eval/L0_METHODOLOGY.md and it is obeyed here
rather than rediscovered:

  * next-category is a STATIC-ATTRIBUTE task. Own-label geometry (kNN-LOO, silhouette, centroid-sep)
    maps monotonically to the L2 category score, so L0 is a legitimate near-sufficient RANKER for it.
    The balance gap is a next-category gap, so L0 can rank our arms without the downstream model.
  * next-region is a TRANSITION task. NO static-geometry metric may rank substrates for it.
    Adjacency-coherence is a DIAGNOSTIC only; it once anti-ranked v13, which is the error that
    motivated that audit. Region ranking starts at L2 with the transition prior present.

What this script adds is the two measurements the ladder does NOT have, both of which speak directly
to "more features, no improvement" in a way own-label separability cannot:

  B2 SUBSPACE OVERLAP. L0 asks whether a factor is recoverable. It never asks whether two factors are
     recoverable from the SAME directions. For each pair of factors, fit a linear map and compare the
     principal subspaces its weights span. High overlap means one direction is doing double duty, so
     improving one factor degrades another. That is a mechanism for "more features, no gain" that no
     own-label metric can see, because each factor scores fine in isolation.

  B3 SPECTRAL CONCENTRATION. The participation ratio of the covariance eigenvalues gives the effective
     number of dimensions actually carrying variance. A 64-d embedding with an effective rank of 6 has
     58 dimensions doing nothing, and adding input features to it cannot help regardless of what those
     features carry. L0 is scale- and rank-blind by construction, so it cannot report this.

B1 (per-factor recoverability) is included as the shared axis that lets B2 and B3 be interpreted, and
it is computed with the same user-disjoint discipline as the rest of the study. Where a claim about
embedding quality is made, the L0 and L1 numbers from the repository's own scripts are the evidence;
B1/B2/B3 explain the mechanism behind them.
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import f1_score

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

# The repository's own L0 implementation. Importing it rather than reimplementing keeps every number
# comparable to the archived embedding_eval results and inherits their fixes (silhouette drops
# singleton labels, kNN-LOO excludes self).
from embedding_eval.geometry import knn_loo, silhouette, centroid_separability  # noqa: E402

N_CAT = 7
FACTORS = ("category", "hour_bucket", "weekday", "place_top50", "region_top50", "gap_bin")


def _load_graph(state: str) -> dict:
    with open(REPO / "output" / "check2hgi" / state / "temp" / "checkin_graph.pt", "rb") as fh:
        return pickle.load(fh)


def build_factors(state: str, md: pd.DataFrame, d: dict) -> dict[str, np.ndarray]:
    """Per-visit label for every factor the representation was given, or could have been given.

    place_top50 and region_top50 keep only the fifty most frequent values and mark the rest as -1, so
    the probe has a learnable label set; a probe over 11,848 classes measures optimizer patience, not
    representation content.
    """
    uid = md["userid"].to_numpy()
    dt = pd.to_datetime(md["datetime"])
    c2p = np.asarray(d["checkin_to_poi"])
    reg = np.asarray(d["poi_to_region"])[c2p]

    t = dt.astype("int64").to_numpy() / 1e9 / 3600.0
    gap = np.zeros(len(t), dtype=np.float32)
    for u in np.unique(uid):
        m = np.where(uid == u)[0]
        gap[m[1:]] = np.diff(t[m])
    pos = gap[gap > 0]
    qs = np.quantile(pos, np.linspace(0, 1, 11)) if pos.size else np.zeros(11)

    def top_k(v, k=50):
        keep = pd.Series(v).value_counts().head(k).index
        out = np.where(np.isin(v, keep), v, -1)
        return out

    return {
        "category": md["category"].astype(str).to_numpy(),
        "hour_bucket": (dt.dt.hour // 4).to_numpy(),
        "weekday": dt.dt.dayofweek.to_numpy(),
        "place_top50": top_k(c2p),
        "region_top50": top_k(reg),
        "gap_bin": np.clip(np.searchsorted(qs, gap), 0, 10),
    }


def user_split(uid: np.ndarray, seed: int, test_frac: float = 0.3):
    """User-disjoint split. A visit-level split would let the probe memorize a user's own habits."""
    us = np.unique(uid)
    rng = np.random.default_rng(seed)
    te_u = set(rng.choice(us, max(1, int(round(us.size * test_frac))), replace=False).tolist())
    te = np.array([u in te_u for u in uid])
    return ~te, te


def probe_factor(Z, y, uid, seeds=3) -> dict:
    """Macro-F1 of a linear probe recovering y from Z, plus the majority floor on the same rows."""
    m = y != -1 if np.issubdtype(np.asarray(y).dtype, np.number) else np.ones(len(y), bool)
    Zm, ym, um = Z[m], np.asarray(y)[m], uid[m]
    if len(np.unique(ym)) < 2:
        return {"macro_f1_mean": float("nan"), "note": "fewer than two classes"}
    scores = []
    for s in range(seeds):
        tr, te = user_split(um, s)
        if tr.sum() < 50 or te.sum() < 50 or len(np.unique(ym[tr])) < 2:
            continue
        clf = LogisticRegression(max_iter=500)
        clf.fit(Zm[tr], ym[tr])
        scores.append(f1_score(ym[te], clf.predict(Zm[te]), average="macro", zero_division=0))
    maj = pd.Series(ym).value_counts(normalize=True).iloc[0]
    return {"macro_f1_mean": float(np.mean(scores)) if scores else float("nan"),
            "macro_f1_sd": float(np.std(scores)) if scores else float("nan"),
            "majority_share": float(maj), "n_rows": int(m.sum()),
            "n_classes": int(len(np.unique(ym))), "n_seeds": len(scores)}


def spectral(Z: np.ndarray) -> dict:
    """B3: how many of the available dimensions carry variance at all."""
    Zc = Z - Z.mean(0, keepdims=True)
    ev = np.linalg.svd(Zc, compute_uv=False) ** 2 / max(1, len(Z) - 1)
    ev = ev[ev > 0]
    p = ev / ev.sum()
    # participation ratio: (sum l)^2 / sum l^2, the standard effective-dimension estimate
    pr = float((ev.sum() ** 2) / (ev ** 2).sum())
    return {"dim": int(Z.shape[1]), "effective_rank_participation": pr,
            "effective_rank_fraction": pr / Z.shape[1],
            "entropy_bits": float(-(p * np.log2(p)).sum()),
            "var_top1": float(p[0]), "var_top5": float(p[:5].sum()),
            "var_top10": float(p[:10].sum()),
            "n_dims_for_90pct_var": int(np.searchsorted(np.cumsum(p), 0.90) + 1)}


def subspace_overlap(Z: np.ndarray, facs: dict, rank: int = 5) -> dict:
    """B2: do two factors live in the same directions?

    For each factor, regress a one-hot of its label onto the embedding and take the top-`rank` right
    singular vectors of the coefficient matrix: the directions the embedding uses to express that
    factor. Overlap between two factors is the mean squared cosine between their subspaces, which is
    the normalized projection metric and lies in [0, 1].
    """
    bases = {}
    for name, y in facs.items():
        m = (np.asarray(y) != -1) if np.issubdtype(np.asarray(y).dtype, np.number) else np.ones(len(y), bool)
        ym = np.asarray(y)[m]
        cls = np.unique(ym)
        if len(cls) < 2:
            continue
        Y = np.zeros((m.sum(), len(cls)), dtype=np.float32)
        Y[np.arange(m.sum()), np.searchsorted(cls, ym)] = 1.0
        W = Ridge(alpha=1.0).fit(Z[m], Y).coef_          # [n_classes, dim]
        k = min(rank, W.shape[0], W.shape[1])
        _, _, Vt = np.linalg.svd(W, full_matrices=False)
        bases[name] = Vt[:k]
    out = {}
    names = sorted(bases)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            M = bases[a] @ bases[b].T
            out[f"{a}|{b}"] = float((M ** 2).sum() / min(bases[a].shape[0], bases[b].shape[0]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--arms", nargs="+", required=True, help="label=path per-visit embedding parquet")
    ap.add_argument("--max-rows", type=int, default=40000)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    st = args.state.lower()
    d = _load_graph(st)
    md_all = d["metadata"].reset_index(drop=True)
    res = {"state": st, "max_rows": args.max_rows, "arms": {},
           "what_each_block_means": {
               "B1_capacity_allocation": "linear recoverability of each factor, against its majority floor",
               "B2_subspace_overlap": "mean squared cosine between the directions two factors use; 1 = same subspace",
               "B3_spectral": "participation ratio = effective number of dimensions carrying variance",
               "B4_geometry": "cosine silhouette and kNN leave-one-out per factor",
           }}

    for spec in args.arms:
        label, path = spec.split("=", 1)
        emb = pd.read_parquet(path)
        dims = sorted([c for c in emb.columns if str(c).isdigit()], key=int)
        assert dims, f"{label}: no digit-named dimension columns in {path}"
        # align to graph metadata order by (userid, datetime, placeid) if the arm is a subset
        n = len(emb)
        rng = np.random.default_rng(0)
        idx = np.arange(n)
        if n > args.max_rows:
            idx = np.sort(rng.choice(idx, args.max_rows, replace=False))
        Z = emb[dims].to_numpy(np.float32)[idx]
        sub_md = emb.iloc[idx]

        # factors are derived from the ARM's own metadata columns where present, else from the graph
        if {"category", "datetime", "userid"}.issubset(emb.columns):
            md_arm = sub_md[["userid", "datetime", "category"]].reset_index(drop=True)
            # place/region come from the graph, matched by position when the arm covers all visits
            if n == len(md_all):
                gsub = {k: v[idx] for k, v in build_factors(st, md_all, d).items()}
                facs = dict(gsub)
                facs["category"] = md_arm["category"].astype(str).to_numpy()
            else:
                facs = {k: v for k, v in build_factors(st, md_arm, d).items()
                        if k in ("category", "hour_bucket", "weekday", "gap_bin")}
        else:
            facs = build_factors(st, md_all.iloc[idx].reset_index(drop=True), d)

        uid = sub_md["userid"].to_numpy() if "userid" in sub_md else md_all["userid"].to_numpy()[idx]
        # L0 from the repository's own code, on the category labels, which is the axis
        # L0_METHODOLOGY certifies as a valid ranker for this task.
        ycat = np.asarray(facs["category"])
        l0 = {}
        try:
            l0.update(knn_loo(Z, ycat, k=10))
            l0["silhouette"] = silhouette(Z, ycat, sample=10000, seed=0)
            l0.update(centroid_separability(Z, ycat))
        except Exception as ex:                       # a metric that cannot run is recorded, not hidden
            l0["error"] = f"{type(ex).__name__}: {ex}"

        arm = {"dim": len(dims), "n_rows": int(len(Z)),
               "L0_repo_geometry_category": l0,
               "L0_validity_note": ("own-label geometry RANKS next-category (a static-attribute task) "
                                    "per L0_METHODOLOGY; it must NOT be used to rank next-region"),
               "B1_capacity_allocation": {k: probe_factor(Z, v, uid) for k, v in facs.items()},
               "B3_spectral": spectral(Z),
               "B2_subspace_overlap": subspace_overlap(Z, facs)}
        res["arms"][label] = arm
        b1 = arm["B1_capacity_allocation"]
        print(f"  {label:16s} L0: knn10_f1={l0.get('knn10_macro_f1', float('nan')):.4f} "
              f"sil={l0.get('silhouette', float('nan')):.4f}", flush=True)
        print(f"  {'':16s} dim={len(dims):3d} eff_rank={arm['B3_spectral']['effective_rank_participation']:6.2f} "
              f"({arm['B3_spectral']['effective_rank_fraction']*100:4.1f}%)  "
              + "  ".join(f"{k[:8]}={b1[k]['macro_f1_mean']:.3f}" for k in FACTORS if k in b1),
              flush=True)

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, indent=2))
    print(f"[budget] wrote {outp}")


if __name__ == "__main__":
    main()
