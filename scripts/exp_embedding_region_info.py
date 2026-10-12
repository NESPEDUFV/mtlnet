"""Does the check-in embedding already encode region info?

Quick probing experiment. Fits a simple logistic regression from
check-in embedding → region label on held-out check-ins, vs the
same task conditioned on explicit region embeddings.

Three comparisons:

  (A) Check-in emb → region.    How much region info is directly
      recoverable from check-in alone?
  (B) Random baseline.          Majority-class recall; sets the
      floor for interpreting (A) and (C).
  (C) POI emb → region.         Upper bound within check2HGI's own
      representation — POI embeddings aggregate check-ins, so they
      should encode region near-perfectly (since boundary 2 of the
      check2HGI loss directly trains POI ↔ region).

Interpretation:
  - If (A) is near (C), check-in emb already recovers region → using
    region embeddings as a separate input stream probably adds
    little. Go with Option A (dual-stream still OK; cheaper); SOTA
    cross-attention (Option C) may be overkill.
  - If (A) ≪ (C), check-in emb loses region info in compression;
    using region embeddings directly as input is a real gain.
  - (A) ≈ (B) would be surprising (check2HGI's whole point).
"""

from __future__ import annotations

import argparse
import logging
import pickle as pkl
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import IoPaths

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def _load(state: str):
    """Return (checkin_embs, poi_embs, region_embs, placeid_to_idx, poi_to_region, checkin_to_poi)."""
    state_l = state.lower()
    cp = pd.read_parquet(f"/Volumes/Vitor's SSD/ingred/output/check2hgi/{state_l}/embeddings.parquet")
    pp = pd.read_parquet(f"/Volumes/Vitor's SSD/ingred/output/check2hgi/{state_l}/poi_embeddings.parquet")
    rp = pd.read_parquet(f"/Volumes/Vitor's SSD/ingred/output/check2hgi/{state_l}/region_embeddings.parquet")
    with open(IoPaths.CHECK2HGI.get_graph_data_file(state), "rb") as f:
        g = pkl.load(f)

    # Column layouts (verified): checkin has [userid, placeid, category,
    # datetime, '0'..'63']; POI has [placeid, '0'..'63']; region has
    # [region_id, 'reg_0'..'reg_63'].
    checkin_emb_cols = [str(i) for i in range(64)]
    checkin_embs = cp[checkin_emb_cols].to_numpy(dtype=np.float32)
    poi_emb_cols = [str(i) for i in range(64)]
    poi_embs = pp[poi_emb_cols].to_numpy(dtype=np.float32)
    region_emb_cols = [f"reg_{i}" for i in range(64)]
    region_embs = rp[region_emb_cols].to_numpy(dtype=np.float32)

    checkin_to_poi = np.asarray(g["checkin_to_poi"], dtype=np.int64)
    poi_to_region = np.asarray(g["poi_to_region"], dtype=np.int64)
    return checkin_embs, poi_embs, region_embs, checkin_to_poi, poi_to_region


def _sample(max_rows: int, x: np.ndarray, y: np.ndarray, seed: int = 42):
    if len(x) <= max_rows:
        return x, y
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(x), size=max_rows, replace=False)
    return x[idx], y[idx]


def run(state: str, max_rows: int = 50000, seed: int = 42):
    logger.info("Loading %s check2HGI embeddings…", state)
    checkin_embs, poi_embs, _region_embs, checkin_to_poi, poi_to_region = _load(state)
    logger.info(
        "shapes: checkin=%s poi=%s ; n_regions=%d",
        checkin_embs.shape, poi_embs.shape, int(poi_to_region.max()) + 1,
    )

    # (A) check-in → region via checkin_to_poi ∘ poi_to_region
    y_checkin = poi_to_region[checkin_to_poi]
    X_a, y_a = _sample(max_rows, checkin_embs, y_checkin, seed=seed)
    logger.info("(A) check-in → region: n=%d, n_regions=%d", len(X_a), int(y_a.max()) + 1)

    # (C) POI → region
    y_poi = poi_to_region
    X_c, y_c = _sample(max_rows, poi_embs, y_poi, seed=seed)
    logger.info("(C) POI → region: n=%d, n_regions=%d", len(X_c), int(y_c.max()) + 1)

    # (B) majority baseline — computed from same label distribution as (A).
    maj_counts = np.bincount(y_checkin)
    maj_class = int(np.argmax(maj_counts))
    maj_acc = maj_counts[maj_class] / len(y_checkin)
    logger.info("(B) majority-class region=%d (acc@1=%.4f)", maj_class, maj_acc)

    # Train/test splits, 80/20.
    def _fit_eval(X, y, label: str):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=None)
        # max_iter modest; lbfgs/saga OK for ~1e3 classes on 50k samples
        # sklearn >= 1.7 dropped the ``multi_class`` kwarg; lbfgs on multi-class
        # data is multinomial by default now. Keep the solver explicit.
        clf = LogisticRegression(
            max_iter=300, n_jobs=-1, solver="lbfgs",
            C=1.0, verbose=0,
        )
        logger.info("[%s] fitting LogisticRegression on %d train rows, %d classes…",
                    label, len(Xtr), int(np.max(y)) + 1)
        clf.fit(Xtr, ytr)
        preds = clf.predict(Xte)
        acc1 = accuracy_score(yte, preds)
        # Acc@5 / Acc@10 via decision_function / predict_proba
        try:
            proba = clf.predict_proba(Xte)
            n_classes = proba.shape[1]
            k5 = min(5, n_classes)
            k10 = min(10, n_classes)
            acc5 = top_k_accuracy_score(yte, proba, k=k5, labels=clf.classes_)
            acc10 = top_k_accuracy_score(yte, proba, k=k10, labels=clf.classes_)
        except Exception as e:
            logger.warning("top-k failed for %s: %s", label, e)
            acc5 = acc10 = float("nan")
        logger.info("[%s] Acc@1=%.4f  Acc@5=%.4f  Acc@10=%.4f", label, acc1, acc5, acc10)
        return dict(acc1=acc1, acc5=acc5, acc10=acc10)

    r_a = _fit_eval(X_a, y_a, "A: check-in→region")
    r_c = _fit_eval(X_c, y_c, "C: POI→region")

    print()
    print("=" * 70)
    print(f"RESULTS for state={state} (max_rows={max_rows})")
    print("=" * 70)
    print(f"(B) Majority-class Acc@1:          {maj_acc:.4f}")
    print(f"(A) Check-in emb → region Acc@1:   {r_a['acc1']:.4f}  Acc@5: {r_a['acc5']:.4f}  Acc@10: {r_a['acc10']:.4f}")
    print(f"(C) POI emb      → region Acc@1:   {r_c['acc1']:.4f}  Acc@5: {r_c['acc5']:.4f}  Acc@10: {r_c['acc10']:.4f}")
    print()
    # Delta interpretation
    delta_ac = r_c['acc1'] - r_a['acc1']
    print(f"Δ (C - A) on Acc@1: {delta_ac:+.4f}")
    if delta_ac < 0.05:
        print("→ Check-in embeddings recover region info almost as well as POI embeddings.")
        print("  Using region embeddings as a separate input stream probably adds little.")
    elif delta_ac > 0.20:
        print("→ Large gap. Check-in embeddings lose region info in compression.")
        print("  Using region embeddings as input is a real gain.")
    else:
        print("→ Moderate gap. Dual-stream input is likely to give a measurable lift.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="alabama")
    parser.add_argument("--max-rows", type=int, default=50000)
    args = parser.parse_args()
    run(args.state, max_rows=args.max_rows)


if __name__ == "__main__":
    main()
