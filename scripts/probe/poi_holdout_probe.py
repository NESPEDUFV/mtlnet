"""G3 — Per-POI hold-out leak probe (Tier 6 mandatory pre-flight).

Honest leak audit at the POI representation level. Mirrors `leak_sniff_ijm.py`'s
shape ("encoder honest, probe fair") but at a different stratum: instead of
predicting the next-step *category* from the last check-in's embedding, we predict
the *region label* of a POI from its pooled POI embedding under 5-fold CV across
POIs. The probe fit never sees the held-out POIs.

Calibration logic
-----------------
Canonical Check2HGI explicitly supervises POI -> region via the p2r boundary, so
some region-recoverability is expected by design. The probe's job is to flag
*delta* lift vs the shipping-stack baseline:

  * **Honest variant** (e.g., T6.1 with shared pool + co-visit InfoNCE): probe
    lifts modestly, scaled with visit-count quantile (high-visit POIs lift more
    than low-visit POIs because the signal is graph-derived).
  * **Leak fingerprint** (e.g., T5.1 free per-POI nn.Embedding): probe lifts
    uniformly across visit-count quantiles, especially in the low-visit bucket
    where the encoder couldn't have learned the region from check-ins alone --
    the lift then comes from per-POI memorisation.

Outputs
-------
JSON with overall + per-quantile means and stds for top-1 / top-5 / macro-F1.
Run twice with --output to a candidate path then diff against the shipping
baseline to gate any Tier-6 promotion.

See `docs/studies/canonical_improvement/INDEX.html#G3` for the design.
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import KFold

REPO = Path(__file__).resolve().parents[2]


def load_poi_data(
    engine: str,
    state: str,
    embedding_path: Path | None,
    graph_pickle: Path | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Return (X, region_labels, visit_count_log, meta).

    X is [N_pois, D]; region_labels is [N_pois] int64; visit_count_log is
    [N_pois] float32. `meta` carries the source paths and a few summary stats so
    the JSON output is self-describing.
    """
    emb_path = embedding_path or REPO / "output" / engine / state / "poi_embeddings.parquet"
    g_path = graph_pickle or REPO / "output" / engine / state / "temp" / "checkin_graph.pt"

    poi_df = pd.read_parquet(emb_path)
    emb_cols = sorted([c for c in poi_df.columns if c.isdigit()], key=int)
    if "placeid" not in poi_df.columns:
        raise ValueError(f"{emb_path} missing 'placeid' column")
    if not emb_cols:
        raise ValueError(f"{emb_path} has no numeric embedding columns")

    with open(g_path, "rb") as f:
        graph = pickle.load(f)
    placeid_to_idx: dict = graph["placeid_to_idx"]
    poi_to_region: np.ndarray = graph["poi_to_region"]
    num_regions: int = int(graph["num_regions"])
    if "poi_visit_count_log" in graph:
        visit_count_log = np.asarray(graph["poi_visit_count_log"], dtype=np.float32)
    else:
        # Older cached graphs (pre-T4.3) omit poi_visit_count_log. Derive it from
        # checkin_to_poi (each check-in counts once for its POI) so the quantile
        # diagnostic stays available without re-running preprocess.
        c2p = np.asarray(graph["checkin_to_poi"], dtype=np.int64)
        counts = np.bincount(c2p, minlength=int(graph["num_pois"])).astype(np.float32)
        visit_count_log = np.log(np.maximum(counts, 1.0)).astype(np.float32)

    poi_df["poi_idx"] = poi_df["placeid"].map(placeid_to_idx)
    if poi_df["poi_idx"].isna().any():
        missing = int(poi_df["poi_idx"].isna().sum())
        raise ValueError(f"{missing} placeids in {emb_path} not in {g_path} mapping")
    poi_df = poi_df.sort_values("poi_idx").reset_index(drop=True)
    order = poi_df["poi_idx"].to_numpy(np.int64)

    X = poi_df[emb_cols].to_numpy(np.float32)
    y = poi_to_region[order].astype(np.int64)
    vlog = visit_count_log[order].astype(np.float32)

    meta = {
        "embedding_path": str(emb_path),
        "graph_pickle": str(g_path),
        "n_pois": int(X.shape[0]),
        "emb_dim": int(X.shape[1]),
        "n_regions_in_data": int(np.unique(y).size),
        "n_regions_total": num_regions,
        "visit_log_min": float(vlog.min()),
        "visit_log_max": float(vlog.max()),
    }
    return X, y, vlog, meta


def _fit_and_predict_proba(
    X: np.ndarray,
    y: np.ndarray,
    tr: np.ndarray,
    va: np.ndarray,
    seed: int,
    max_iter: int = 1000,
    tol: float = 1e-3,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit LogReg on (X[tr], y[tr]); return (y_pred, proba) on X[va]."""
    clf = LogisticRegression(
        max_iter=max_iter,
        tol=tol,
        C=1.0,
        solver="lbfgs",
        random_state=seed,
    )
    clf.fit(X[tr], y[tr])
    proba = clf.predict_proba(X[va])
    y_pred = clf.classes_[proba.argmax(axis=1)]
    return y_pred, proba, clf.classes_


def _scores_for_subset(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    proba: np.ndarray,
    classes: np.ndarray,
    mask: np.ndarray,
) -> dict:
    if not mask.any():
        return {"n": 0, "top1": float("nan"), "top5": float("nan"), "macro_f1": float("nan")}
    yt = y_true[mask]
    yp = y_pred[mask]
    pp = proba[mask]
    top1 = float((yt == yp).mean())
    k = min(5, pp.shape[1])
    # Manual top-k: held-out folds can contain region labels absent from the
    # training fold (and thus from ``classes``); count those as misses rather
    # than letting sklearn's strict label-set check raise.
    top_k_idx = np.argpartition(-pp, kth=k - 1, axis=1)[:, :k]
    top_k_labels = classes[top_k_idx]
    top5 = float(np.any(top_k_labels == yt[:, None], axis=1).mean())
    macro_f1 = float(f1_score(yt, yp, average="macro", zero_division=0))
    return {"n": int(mask.sum()), "top1": top1, "top5": top5, "macro_f1": macro_f1}


def run_probe(
    X: np.ndarray,
    y: np.ndarray,
    vlog: np.ndarray,
    n_folds: int,
    seed: int,
    max_pois: int | None = None,
    min_region_size: int = 1,
    max_iter: int = 1000,
    tol: float = 1e-3,
) -> dict:
    """5-fold CV over POIs. Return per-fold + aggregate scores.

    Optional `max_pois` / `min_region_size` shave compute for large states
    (e.g., FL with 76 K POIs × 4 703 regions). Both transforms are recorded
    in the output JSON so probe runs against the same state stay comparable.
    """
    sampling_info: dict = {
        "max_pois": max_pois,
        "min_region_size": min_region_size,
        "n_pois_pre_filter": int(X.shape[0]),
        "n_regions_pre_filter": int(np.unique(y).size),
    }
    if min_region_size > 1:
        # Drop POIs whose region label appears < min_region_size times.
        # Singleton-region POIs add noise without changing the probe's
        # discrimination signal at the population level.
        _, counts = np.unique(y, return_counts=True)
        valid_regions = set(np.unique(y)[counts >= min_region_size].tolist())
        mask = np.array([yi in valid_regions for yi in y], dtype=bool)
        X, y, vlog = X[mask], y[mask], vlog[mask]
    if max_pois is not None and X.shape[0] > max_pois:
        rng = np.random.default_rng(seed)
        idx = rng.choice(X.shape[0], size=max_pois, replace=False)
        idx.sort()
        X, y, vlog = X[idx], y[idx], vlog[idx]
    sampling_info["n_pois_post_filter"] = int(X.shape[0])
    sampling_info["n_regions_post_filter"] = int(np.unique(y).size)

    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)

    # Visit-count quantile bins: bottom 25 %, middle 50 %, top 25 %.
    q25, q75 = np.quantile(vlog, [0.25, 0.75])
    bin_masks = {
        "low_visit_q25": vlog <= q25,
        "mid_visit_q50": (vlog > q25) & (vlog < q75),
        "high_visit_q75": vlog >= q75,
    }

    fold_records = []
    for k, (tr, va) in enumerate(kf.split(X), start=1):
        y_pred, proba, classes = _fit_and_predict_proba(
            X, y, tr, va, seed, max_iter=max_iter, tol=tol
        )
        y_va = y[va]

        rec: dict = {"fold": k, "n_train": int(tr.size), "n_val": int(va.size)}
        rec["overall"] = _scores_for_subset(
            y_va, y_pred, proba, classes, np.ones_like(y_va, dtype=bool)
        )
        for name, full_mask in bin_masks.items():
            rec[name] = _scores_for_subset(
                y_va, y_pred, proba, classes, full_mask[va]
            )
        fold_records.append(rec)

    def _agg(metric_path: tuple[str, str]) -> dict:
        bucket, metric = metric_path
        vals = np.array([r[bucket][metric] for r in fold_records], dtype=np.float64)
        finite = vals[np.isfinite(vals)]
        if finite.size == 0:
            return {"mean": float("nan"), "std": float("nan"), "n_folds": 0}
        return {
            "mean": float(finite.mean()),
            "std": float(finite.std(ddof=1)) if finite.size > 1 else 0.0,
            "n_folds": int(finite.size),
        }

    buckets = ["overall", "low_visit_q25", "mid_visit_q50", "high_visit_q75"]
    metrics = ["top1", "top5", "macro_f1"]
    summary = {b: {m: _agg((b, m)) for m in metrics} for b in buckets}

    return {
        "folds": fold_records,
        "summary": summary,
        "n_folds": n_folds,
        "seed": seed,
        "sampling": sampling_info,
        "solver": {"max_iter": max_iter, "tol": tol, "C": 1.0, "name": "lbfgs"},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--engine", default="check2hgi", help="Embedding engine (default: check2hgi)")
    ap.add_argument("--state", required=True, help="State name (e.g., alabama)")
    ap.add_argument("--seed", type=int, default=42, help="CV split seed (default: 42)")
    ap.add_argument("--n-folds", type=int, default=5, help="Number of POI folds (default: 5)")
    ap.add_argument(
        "--embedding-path",
        type=Path,
        default=None,
        help="Override path to poi_embeddings.parquet (e.g., a T6.* candidate output)",
    )
    ap.add_argument(
        "--graph-pickle",
        type=Path,
        default=None,
        help="Override path to checkin_graph.pt (POI -> region mapping source)",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON output path (default: docs/results/canonical_improvement/G3_<state>.json)",
    )
    ap.add_argument(
        "--tag",
        default="shipping",
        help="Variant tag for the output JSON (e.g., 'shipping', 'T5.1', 'T6.1_lambda0.1')",
    )
    ap.add_argument(
        "--max-pois",
        type=int,
        default=None,
        help="Cap POI count via deterministic subsample (for large states; e.g., 20000 on FL)",
    )
    ap.add_argument(
        "--min-region-size",
        type=int,
        default=1,
        help="Drop POIs whose region has < this many POIs (default: 1 = keep all)",
    )
    ap.add_argument("--max-iter", type=int, default=1000, help="LBFGS max iterations")
    ap.add_argument("--tol", type=float, default=1e-3, help="LBFGS tolerance")
    args = ap.parse_args()

    X, y, vlog, meta = load_poi_data(
        args.engine, args.state, args.embedding_path, args.graph_pickle
    )
    print(
        f"[G3] {args.state}: {meta['n_pois']} POIs, {meta['emb_dim']}-dim, "
        f"{meta['n_regions_in_data']}/{meta['n_regions_total']} regions populated",
        file=sys.stderr,
    )

    result = run_probe(
        X,
        y,
        vlog,
        n_folds=args.n_folds,
        seed=args.seed,
        max_pois=args.max_pois,
        min_region_size=args.min_region_size,
        max_iter=args.max_iter,
        tol=args.tol,
    )
    payload = {
        "tag": args.tag,
        "engine": args.engine,
        "state": args.state,
        "meta": meta,
        **result,
    }

    out_path = args.output or (
        REPO / "docs" / "results" / "canonical_improvement" / f"G3_{args.state}_{args.tag}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    s = result["summary"]
    print(f"[G3] {args.state} ({args.tag}) — overall:")
    print(
        f"       top1={s['overall']['top1']['mean']*100:5.2f} ± {s['overall']['top1']['std']*100:4.2f}  "
        f"top5={s['overall']['top5']['mean']*100:5.2f} ± {s['overall']['top5']['std']*100:4.2f}  "
        f"macroF1={s['overall']['macro_f1']['mean']*100:5.2f} ± {s['overall']['macro_f1']['std']*100:4.2f}"
    )
    for bucket in ("low_visit_q25", "mid_visit_q50", "high_visit_q75"):
        b = s[bucket]
        print(
            f"  {bucket:>16s}  top1={b['top1']['mean']*100:5.2f} ± {b['top1']['std']*100:4.2f}  "
            f"top5={b['top5']['mean']*100:5.2f} ± {b['top5']['std']*100:4.2f}  "
            f"macroF1={b['macro_f1']['mean']*100:5.2f} ± {b['macro_f1']['std']*100:4.2f}"
        )
    print(f"[G3] JSON written to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
