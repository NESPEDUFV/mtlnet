"""Compute simple (non-learned) baselines for the check2HGI study.

These form the floor every learned model must beat (CH04) and are
the "known-good reference" equivalent to the fusion study's P0.4 CBIC
replication. If a trained model's Acc@10 is not ≥ 2× the best simple
baseline, the pipeline is broken.

Usage::

    python scripts/compute_simple_baselines.py --state alabama --task next_poi
    python scripts/compute_simple_baselines.py --state florida --task next_region
    python scripts/compute_simple_baselines.py   # defaults: AL+FL × both tasks

Outputs JSON per state per task under
``docs/results/P0/simple_baselines/<state>/<task>.json``

Baselines computed:

  random        — uniform draw over all labels; Acc@K = K / n_classes (closed-form).
  majority      — always predict the most frequent label in train fold.
  top_k_popular — return the top-K most frequent labels (cumulative freq).
  markov_1step  — P(next | current): argmax over learned transition matrix from train.
  user_history  — per-user top-K visited labels from train trajectories.

All baselines are evaluated on each of the 5 frozen folds and reported
as mean ± std across folds (matching the statistical protocol for
learned-model comparisons in P1/P2).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import EmbeddingEngine, IoPaths
from configs.model import InputsConfig
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SEED = 42
N_SPLITS = 5
SLIDE_WINDOW = InputsConfig.SLIDE_WINDOW


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_task_data(state: str, task: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """Load labels + userids + sequence POI windows for a task.

    Returns (y_labels, userids, y_strat, window_last_pois, window_last_regions, n_classes).

    - window_last_pois: POI index of the last position (for legacy
      POI-level Markov-1step).
    - window_last_regions: [N, SLIDE_WINDOW] int array of region indices
      along the 9-step window (for N-step region-level Markov); padded
      positions (placeid == -1) are filled with -1.
    """
    engine = EmbeddingEngine.CHECK2HGI

    # Always load next.parquet for X features (needed for userids + stratification key)
    next_df = IoPaths.load_next(state, engine)
    userids = next_df["userid"].astype(str).to_numpy()

    # Stratification key (next_category): needed for StratifiedGroupKFold
    from configs.globals import CATEGORIES_MAP
    inv_categories = {v: k for k, v in CATEGORIES_MAP.items()}
    y_strat = next_df["next_category"].map(inv_categories).to_numpy(dtype=np.int64)

    # Load task-specific labels
    if task == "next_category":
        # next_category uses the same labels as next.parquet's next_category
        # column — already loaded as y_strat above. Just reuse.
        y = y_strat
        n_classes = 7
    elif task == "next_region":
        task_df = IoPaths.load_next_region(state, engine)
        y = task_df["region_idx"].to_numpy(dtype=np.int64)
        n_classes = int(y.max()) + 1
    else:
        raise ValueError(f"Unknown task: {task}")

    # Load graph maps (placeid↔poi_idx, poi_idx→region_idx) + sequences
    seq_path = IoPaths.CHECK2HGI.get_temp_dir(state) / "sequences_next.parquet"
    seq_df = pd.read_parquet(seq_path)
    import pickle as pkl
    with open(IoPaths.CHECK2HGI.get_graph_data_file(state), "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    poi_to_region = np.asarray(poi_to_region, dtype=np.int64)

    # Last-POI (poi_8) for legacy Markov-1step
    last_poi_col = f"poi_{SLIDE_WINDOW - 1}"
    last_pois_raw = seq_df[last_poi_col].astype(np.int64).to_numpy()
    window_last_pois = np.array([
        placeid_to_idx.get(int(pid), -1) for pid in last_pois_raw
    ], dtype=np.int64)

    # Full region trajectory for N-step region-level Markov.
    # Padded positions (placeid == -1) → -1 in window_last_regions.
    window_last_regions = np.full((len(seq_df), SLIDE_WINDOW), -1, dtype=np.int64)
    for i in range(SLIDE_WINDOW):
        col = f"poi_{i}"
        placeids = seq_df[col].astype(np.int64).to_numpy()
        mask = placeids != -1
        valid = placeids[mask]
        poi_idx = pd.Series(valid).map(placeid_to_idx).to_numpy(dtype=np.int64)
        window_last_regions[np.where(mask)[0], i] = poi_to_region[poi_idx]

    return y, userids, y_strat, window_last_pois, window_last_regions, n_classes


# ---------------------------------------------------------------------------
# Baseline implementations
# ---------------------------------------------------------------------------

def _acc_at_k(preds_topk: np.ndarray, truth: np.ndarray, k: int) -> float:
    """Acc@K: fraction of samples where truth is in top-K predictions.

    preds_topk: (N, max_K) — top-max_K predicted labels per sample.
    truth: (N,) — true labels.
    """
    return float(np.mean([truth[i] in preds_topk[i, :k] for i in range(len(truth))]))


def _mrr(preds_topk: np.ndarray, truth: np.ndarray) -> float:
    """MRR over the top-K predictions."""
    rr = []
    for i in range(len(truth)):
        ranks = np.where(preds_topk[i] == truth[i])[0]
        rr.append(1.0 / (ranks[0] + 1) if len(ranks) > 0 else 0.0)
    return float(np.mean(rr))


def baseline_random(n_classes: int, n_val: int) -> Dict[str, float]:
    """Closed-form: Acc@K = K / n_classes."""
    return {
        "acc1": 1.0 / n_classes,
        "acc5": min(5.0 / n_classes, 1.0),
        "acc10": min(10.0 / n_classes, 1.0),
        "mrr": sum(1.0 / (r + 1) for r in range(n_classes)) / n_classes,
    }


def baseline_majority(y_train: np.ndarray, y_val: np.ndarray) -> Dict[str, float]:
    """Always predict the single most frequent train label."""
    counts = Counter(y_train)
    most_common = counts.most_common(1)[0][0]
    correct = (y_val == most_common)
    return {
        "acc1": float(correct.mean()),
        "acc5": float(correct.mean()),   # same as acc1 for a single prediction
        "acc10": float(correct.mean()),
        "mrr": float(correct.mean()),    # rank is always 1 if correct, else 0
    }


def baseline_top_k_popular(y_train: np.ndarray, y_val: np.ndarray, max_k: int = 10) -> Dict[str, float]:
    """Always return top-K most frequent train labels."""
    counts = Counter(y_train)
    top_labels = np.array([label for label, _ in counts.most_common(max_k)])
    # Broadcast: (N, max_k)
    preds = np.tile(top_labels, (len(y_val), 1))
    return {
        "acc1": _acc_at_k(preds, y_val, 1),
        "acc5": _acc_at_k(preds, y_val, 5),
        "acc10": _acc_at_k(preds, y_val, 10),
        "mrr": _mrr(preds, y_val),
    }


def baseline_markov_1step(
    last_pois_train: np.ndarray,
    y_train: np.ndarray,
    last_pois_val: np.ndarray,
    y_val: np.ndarray,
    n_classes: int,
    max_k: int = 10,
) -> Dict[str, float]:
    """1-step Markov: P(next_label | last_poi_in_window).

    Builds a transition count matrix from train and predicts via
    argmax-top-K for each val sample's last POI.
    """
    # Build transition counts: transition[last_poi] → Counter of next labels
    transition: Dict[int, Counter] = defaultdict(Counter)
    for last_poi, label in zip(last_pois_train, y_train):
        if last_poi >= 0:  # skip unmapped
            transition[int(last_poi)][int(label)] += 1

    # Fallback for unseen last_pois: global frequency
    global_counts = Counter(y_train)
    global_topk = [label for label, _ in global_counts.most_common(max_k)]

    preds_list = []
    for last_poi in last_pois_val:
        if int(last_poi) in transition:
            topk = [label for label, _ in transition[int(last_poi)].most_common(max_k)]
        else:
            topk = global_topk
        # Pad to max_k with -1 (won't match any real label)
        topk = topk[:max_k] + [-1] * (max_k - len(topk))
        preds_list.append(topk)

    preds = np.array(preds_list)
    return {
        "acc1": _acc_at_k(preds, y_val, 1),
        "acc5": _acc_at_k(preds, y_val, 5),
        "acc10": _acc_at_k(preds, y_val, 10),
        "mrr": _mrr(preds, y_val),
    }


def baseline_markov_kstep_region(
    regions_train: np.ndarray,   # [N_train, SLIDE_WINDOW]
    y_train: np.ndarray,          # [N_train]
    regions_val: np.ndarray,      # [N_val, SLIDE_WINDOW]
    y_val: np.ndarray,            # [N_val]
    k: int,
    max_k_topk: int = 10,
) -> Dict[str, float]:
    """K-step region-level Markov with N-gram backoff.

    Conditions on the last ``k`` regions in the input window and predicts
    the next region. Keys with fewer than 1 train sample fall back to
    k-1 history (then k-2, ..., then global frequency). This is the
    classical NLP "stupid backoff" approach for sparse N-grams — with
    only ~10K-160K training rows and 1109+ regions, raw K>1 counts are
    too sparse to use without backoff.

    This is the sequence-aware baseline to compare the neural head
    (which sees the full 9-step window) against — a count-based method
    given progressively more context.
    """
    if k < 1 or k > regions_train.shape[1]:
        raise ValueError(f"k must be in [1, {regions_train.shape[1]}], got {k}")

    # Build transition maps for each order 1..k
    # transition_maps[m] maps tuple(last_m_regions) -> Counter(next_region).
    transition_maps: List[Dict[tuple, Counter]] = [defaultdict(Counter) for _ in range(k + 1)]
    for row_idx in range(len(y_train)):
        label = int(y_train[row_idx])
        row = regions_train[row_idx]
        # For each order m, key is the last m regions in the window
        # (skipping if any are padded -1).
        for m in range(1, k + 1):
            tail = tuple(int(r) for r in row[-m:])
            if -1 in tail:
                continue
            transition_maps[m][tail][label] += 1

    # Global fallback from train-only label distribution
    global_counts = Counter(int(y) for y in y_train)
    global_topk = [label for label, _ in global_counts.most_common(max_k_topk)]

    preds_list = []
    for row_idx in range(len(y_val)):
        row = regions_val[row_idx]
        topk = None
        # Try order k, then k-1, ..., then 1. First hit wins.
        for m in range(k, 0, -1):
            tail = tuple(int(r) for r in row[-m:])
            if -1 in tail:
                continue
            if tail in transition_maps[m]:
                topk = [label for label, _ in transition_maps[m][tail].most_common(max_k_topk)]
                break
        if topk is None:
            topk = global_topk
        topk = topk[:max_k_topk] + [-1] * (max_k_topk - len(topk))
        preds_list.append(topk)

    preds = np.array(preds_list)
    return {
        "acc1": _acc_at_k(preds, y_val, 1),
        "acc5": _acc_at_k(preds, y_val, 5),
        "acc10": _acc_at_k(preds, y_val, 10),
        "mrr": _mrr(preds, y_val),
    }


def baseline_user_history(
    userids_train: np.ndarray,
    y_train: np.ndarray,
    userids_val: np.ndarray,
    y_val: np.ndarray,
    max_k: int = 10,
) -> Dict[str, float]:
    """Per-user: return top-K most-visited labels from their train history."""
    user_counts: Dict[str, Counter] = defaultdict(Counter)
    for uid, label in zip(userids_train, y_train):
        user_counts[str(uid)][int(label)] += 1

    # Global fallback for users with no train history
    global_counts = Counter(y_train)
    global_topk = [label for label, _ in global_counts.most_common(max_k)]

    preds_list = []
    for uid in userids_val:
        uid_str = str(uid)
        if uid_str in user_counts:
            topk = [label for label, _ in user_counts[uid_str].most_common(max_k)]
        else:
            topk = global_topk
        topk = topk[:max_k] + [-1] * (max_k - len(topk))
        preds_list.append(topk)

    preds = np.array(preds_list)
    return {
        "acc1": _acc_at_k(preds, y_val, 1),
        "acc5": _acc_at_k(preds, y_val, 5),
        "acc10": _acc_at_k(preds, y_val, 10),
        "mrr": _mrr(preds, y_val),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def compute_baselines_for_task(state: str, task: str) -> Dict:
    """Compute all simple baselines on 5-fold CV for one state × task.

    Returns a dict ready to write as JSON.
    """
    y, userids, y_strat, window_last_pois, window_last_regions, n_classes = _load_task_data(state, task)

    sgkf = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    fold_results = []

    for fold_idx, (train_idx, val_idx) in enumerate(sgkf.split(np.zeros(len(y)), y_strat, groups=userids)):
        y_train, y_val = y[train_idx], y[val_idx]
        uid_train, uid_val = userids[train_idx], userids[val_idx]
        lp_train, lp_val = window_last_pois[train_idx], window_last_pois[val_idx]
        reg_train, reg_val = window_last_regions[train_idx], window_last_regions[val_idx]

        fold = {
            "fold": fold_idx,
            "n_train": int(len(train_idx)),
            "n_val": int(len(val_idx)),
        }

        fold["random"] = baseline_random(n_classes, len(val_idx))
        fold["majority"] = baseline_majority(y_train, y_val)
        fold["top_k_popular"] = baseline_top_k_popular(y_train, y_val)
        fold["markov_1step"] = baseline_markov_1step(
            lp_train, y_train, lp_val, y_val, n_classes,
        )
        fold["user_history"] = baseline_user_history(
            uid_train, y_train, uid_val, y_val,
        )
        # Macro-F1 for the two category floors (not derivable from acc alone)
        if task == "next_category":
            _maj_cls = Counter(y_train).most_common(1)[0][0]
            fold["majority"]["macro_f1"] = float(f1_score(
                y_val, np.full(len(y_val), _maj_cls), average="macro", zero_division=0))
            _trans: dict = defaultdict(Counter)
            for _lp, _lbl in zip(lp_train, y_train):
                if _lp >= 0:
                    _trans[int(_lp)][int(_lbl)] += 1
            _global_top1 = Counter(y_train).most_common(1)[0][0]
            _m1_top1 = np.array([
                _trans[int(_lp)].most_common(1)[0][0] if int(_lp) in _trans else _global_top1
                for _lp in lp_val
            ])
            fold["markov_1step"]["macro_f1"] = float(f1_score(
                y_val, _m1_top1, average="macro", zero_division=0))
        # Region-level N-step Markov with backoff. Only for next_region —
        # next_category uses 7 classes, where Markov-K is trivially bounded
        # by the majority baseline anyway.
        if task == "next_region":
            for m in (1, 2, 3, 5, 7, 9):
                fold[f"markov_{m}step_region"] = baseline_markov_kstep_region(
                    reg_train, y_train, reg_val, y_val, k=m,
                )
        fold_results.append(fold)

        msg = (
            f"[{state}/{task}] fold {fold_idx}: "
            f"majority_acc1={fold['majority']['acc1']:.4f} "
            f"markov_acc1={fold['markov_1step']['acc1']:.4f} "
            f"user_hist_acc1={fold['user_history']['acc1']:.4f}"
        )
        if task == "next_region":
            msg += (
                f" | mk1={fold['markov_1step_region']['acc10']:.4f}"
                f" mk2={fold['markov_2step_region']['acc10']:.4f}"
                f" mk3={fold['markov_3step_region']['acc10']:.4f}"
                f" mk5={fold['markov_5step_region']['acc10']:.4f}"
                f" mk7={fold['markov_7step_region']['acc10']:.4f}"
                f" mk9={fold['markov_9step_region']['acc10']:.4f}"
            )
        logger.info(msg)

    # Aggregate across folds
    baseline_names = ["random", "majority", "top_k_popular", "markov_1step", "user_history"]
    if task == "next_region":
        baseline_names += [f"markov_{m}step_region" for m in (1, 2, 3, 5, 7, 9)]
    metric_names = ["acc1", "acc5", "acc10", "mrr"]
    aggregate = {}
    for bl in baseline_names:
        agg = {}
        for m in metric_names:
            vals = [f[bl][m] for f in fold_results]
            agg[f"{m}_mean"] = float(np.mean(vals))
            agg[f"{m}_std"] = float(np.std(vals))
        aggregate[bl] = agg

    if task == "next_category":
        for _bl in ("majority", "markov_1step"):
            _f1_vals = [f[_bl]["macro_f1"] * 100 for f in fold_results]
            aggregate[_bl]["macro_f1_mean"] = float(np.mean(_f1_vals))
            aggregate[_bl]["macro_f1_std"] = float(np.std(_f1_vals))

    # Best simple baseline (max acc10 mean across all baselines)
    best_bl = max(baseline_names, key=lambda bl: aggregate[bl]["acc10_mean"])
    best_acc10 = aggregate[best_bl]["acc10_mean"]

    return {
        "state": state,
        "task": task,
        "n_classes": n_classes,
        "n_folds": N_SPLITS,
        "seed": SEED,
        "majority_fraction": float(Counter(y).most_common(1)[0][1] / len(y)),
        "best_simple_baseline": best_bl,
        "best_simple_acc10_mean": best_acc10,
        "per_fold": fold_results,
        "aggregate": aggregate,
    }


def main():
    parser = argparse.ArgumentParser(description="Compute simple baselines for check2HGI study")
    parser.add_argument("--state", type=str, action="append", default=None)
    parser.add_argument("--task", type=str, action="append", default=None,
                        choices=["next_category", "next_region"])
    args = parser.parse_args()
    states = args.state or ["alabama", "florida"]
    tasks = args.task or ["next_category", "next_region"]

    study_dir = Path("docs/results/P0/simple_baselines")

    for state in states:
        for task in tasks:
            logger.info("=" * 60)
            logger.info("Computing baselines: state=%s task=%s", state, task)
            logger.info("=" * 60)
            result = compute_baselines_for_task(state, task)

            out_dir = study_dir / state
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{task}.json"
            out_path.write_text(json.dumps(result, indent=2))
            if task == "next_category":
                agg = result["aggregate"]
                f1_summary = {
                    "majority_f1_mean": agg["majority"]["macro_f1_mean"],
                    "majority_f1_std": agg["majority"]["macro_f1_std"],
                    "top_k_popular_top1_f1_mean": agg["majority"]["macro_f1_mean"],
                    "top_k_popular_top1_f1_std": agg["majority"]["macro_f1_std"],
                    "markov_1step_f1_mean": agg["markov_1step"]["macro_f1_mean"],
                    "markov_1step_f1_std": agg["markov_1step"]["macro_f1_std"],
                }
                f1_path = out_dir / "next_category_f1.json"
                f1_path.write_text(json.dumps(f1_summary, indent=2))
                logger.info("Saved F1 summary: %s", f1_path)
            logger.info(
                "Saved: %s | best_baseline=%s acc10=%.4f | majority_fraction=%.4f",
                out_path, result["best_simple_baseline"],
                result["best_simple_acc10_mean"],
                result["majority_fraction"],
            )


if __name__ == "__main__":
    main()
