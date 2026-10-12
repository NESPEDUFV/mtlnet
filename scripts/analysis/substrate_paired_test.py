"""Substrate-comparison paired statistical tests (I6 of SUBSTRATE_COMPARISON_PLAN).

Inputs: per-fold metrics for two substrates on the same task / state /
head, optionally collected across multiple seeds. Outputs: paired-t
and Wilcoxon signed-rank tests for the superiority hypothesis, plus a
TOST (Two One-Sided Tests) procedure for non-inferiority with a
pre-specified equivalence margin δ.

Convention:
- 5 folds × 1 seed → 5 paired samples (smallest 1-sided Wilcoxon p = 1/32 = 0.0312).
- 3 seeds × 5 folds → 15 paired samples; finer resolution.
- Δ_i = metric_i(check2hgi) − metric_i(hgi). Positive = Check2HGI wins.

Usage::

    python scripts/analysis/substrate_paired_test.py \\
        --check2hgi PATH_OR_DIR --hgi PATH_OR_DIR \\
        --metric f1 --task cat --state alabama \\
        --tost-margin 0.02

    --check2hgi may point either to:
      (a) a single summary JSON containing per-fold metrics, or
      (b) a directory of per-seed summary JSONs (script aggregates).

Outputs JSON to docs/results/paired_tests/<state>_<task>_<metric>.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

_root = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Per-fold extraction — try several JSON layouts produced by this codebase
# ---------------------------------------------------------------------------

_METRIC_KEYS = {
    "f1": ("f1", "macro_f1", "f1_macro", "f1_per_fold"),
    "acc": ("accuracy", "acc", "acc1", "acc_per_fold"),
    "acc1": ("acc1", "accuracy", "acc_per_fold"),
    "acc5": ("acc5",),
    "acc10": ("acc10",),
    "mrr": ("mrr",),
}


def _find_per_fold(d: dict, metric: str) -> list[float] | None:
    """Search a result-dict for per-fold values of `metric`. Best-effort."""
    candidates = _METRIC_KEYS.get(metric, (metric,))

    # Layout A: linear-probe / paired-test JSON — top-level "<metric>_per_fold"
    for k in (f"{metric}_per_fold", "f1_per_fold", "acc_per_fold"):
        if k in d and isinstance(d[k], list):
            return [float(x) for x in d[k]]

    # Layout B: training summary — nested under "next" / "category" / etc.
    for tk in ("next", "category", "mtl"):
        sub = d.get(tk) or {}
        for cand in candidates:
            v = sub.get(cand)
            if isinstance(v, dict):
                if "per_fold" in v:
                    return [float(x) for x in v["per_fold"]]
                if "min" in v and "max" in v and "mean" in v and "std" in v:
                    # We only have aggregates — give up on per-fold.
                    return None
            if isinstance(v, list):
                return [float(x) for x in v]

    # Layout C: flat per-fold dict like {"fold_0": ..., ...}
    folds = []
    for i in range(20):
        v = d.get(f"fold_{i}") or d.get(f"fold{i}")
        if v is None:
            break
        if isinstance(v, dict):
            for cand in candidates:
                if cand in v:
                    folds.append(float(v[cand]))
                    break
    if folds:
        return folds

    return None


def _load_per_fold(path: Path, metric: str) -> list[float]:
    """Load per-fold metric values from a JSON file or a directory of seed JSONs."""
    paths = [path] if path.is_file() else sorted(path.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"no JSONs found at {path}")
    samples: list[float] = []
    for p in paths:
        with open(p) as f:
            d = json.load(f)
        per_fold = _find_per_fold(d, metric)
        if per_fold is None:
            print(f"[WARN] could not locate per-fold {metric!r} in {p}; skipping",
                  file=sys.stderr)
            continue
        samples.extend(per_fold)
    if not samples:
        raise RuntimeError(f"no per-fold {metric!r} samples extracted from {path}")
    return samples


# ---------------------------------------------------------------------------
# Stat tests
# ---------------------------------------------------------------------------

def paired_tests(deltas: list[float]) -> dict:
    """Paired-t (if Shapiro-Wilk passes) + Wilcoxon. One-sided 'greater'."""
    arr = np.array(deltas, dtype=float)
    n = len(arr)
    out: dict = {
        "n": int(n),
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if n > 1 else 0.0,
        "median": float(np.median(arr)),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "n_positive": int((arr > 0).sum()),
        "n_negative": int((arr < 0).sum()),
        "n_zero": int((arr == 0).sum()),
    }

    if n >= 3:
        sw_stat, sw_p = stats.shapiro(arr)
        out["shapiro_w"] = float(sw_stat)
        out["shapiro_p"] = float(sw_p)
        out["normality_assumed"] = bool(sw_p > 0.05)
    else:
        out["normality_assumed"] = False

    if n >= 2:
        # paired-t (one-sample t against 0)
        t_stat, t_p_two = stats.ttest_1samp(arr, popmean=0.0)
        out["paired_t_stat"] = float(t_stat)
        out["paired_t_p_two_sided"] = float(t_p_two)
        # One-sided greater: half the two-sided if t > 0 else 1 - half
        out["paired_t_p_greater"] = float(t_p_two / 2 if t_stat > 0 else 1 - t_p_two / 2)

    if n >= 1 and not (arr == 0).all():
        try:
            wx_stat, wx_p = stats.wilcoxon(arr, alternative="greater",
                                           zero_method="wilcox")
            out["wilcoxon_stat"] = float(wx_stat)
            out["wilcoxon_p_greater"] = float(wx_p)
        except ValueError as e:
            out["wilcoxon_error"] = str(e)
    return out


def tost_non_inferiority(deltas: list[float], margin: float) -> dict:
    """TOST: H0: μ ≤ −δ OR μ ≥ δ. We test the lower bound only (non-inferiority).

    Two one-sided tests; non-inferiority concludes if H0_lower rejected.
    For 'check2hgi non-inferior to hgi', we want μ > −δ.

    p_lower: P(μ ≤ −δ) — small means non-inferior.
    """
    arr = np.array(deltas, dtype=float)
    n = len(arr)
    if n < 2:
        return {"tost_skipped": "n<2"}
    # Shift the test: test if (Δ + δ) > 0 (i.e. Δ > −δ).
    shifted = arr + margin
    t_stat, t_p_two = stats.ttest_1samp(shifted, popmean=0.0)
    p_lower = float(t_p_two / 2 if t_stat > 0 else 1 - t_p_two / 2)
    return {
        "margin": float(margin),
        "p_lower_one_sided": p_lower,
        "non_inferior_at_alpha_0.05": bool(p_lower < 0.05),
        "shifted_mean": float(shifted.mean()),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check2hgi", type=Path, required=True,
                    help="JSON file or directory of seed-JSONs for the Check2HGI side.")
    ap.add_argument("--hgi", type=Path, required=True,
                    help="JSON file or directory of seed-JSONs for the HGI side.")
    ap.add_argument("--metric", required=True,
                    choices=list(_METRIC_KEYS.keys()),
                    help="Per-fold metric to compare.")
    ap.add_argument("--task", required=True, choices=["cat", "reg"])
    ap.add_argument("--state", required=True)
    ap.add_argument("--tost-margin", type=float, default=None,
                    help="If set, also run TOST non-inferiority with this δ "
                         "(in metric units, e.g. 0.02 for 2 pp).")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else (
        _root / "docs" / "studies" / "check2hgi" / "results" / "paired_tests"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    c2 = _load_per_fold(args.check2hgi, args.metric)
    hg = _load_per_fold(args.hgi, args.metric)
    if len(c2) != len(hg):
        raise ValueError(
            f"per-fold count mismatch: check2hgi has {len(c2)}, hgi has {len(hg)}. "
            f"For paired tests both sides must share the same fold/seed protocol."
        )
    deltas = [a - b for a, b in zip(c2, hg)]

    res = {
        "metric": args.metric, "task": args.task, "state": args.state,
        "check2hgi_per_fold": c2,
        "hgi_per_fold": hg,
        "deltas": deltas,
        "superiority": paired_tests(deltas),
    }
    if args.tost_margin is not None:
        res["non_inferiority_tost"] = tost_non_inferiority(deltas, args.tost_margin)

    out = out_dir / f"{args.state}_{args.task}_{args.metric}.json"
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    sup = res["superiority"]
    print(f"[paired] state={args.state} task={args.task} metric={args.metric} "
          f"n={sup['n']} Δ̄={sup['mean']:+.4f}  pos/neg={sup['n_positive']}/{sup['n_negative']}")
    if "wilcoxon_p_greater" in sup:
        print(f"[paired]   wilcoxon p_greater = {sup['wilcoxon_p_greater']:.4f}")
    if "paired_t_p_greater" in sup:
        print(f"[paired]   paired-t p_greater  = {sup['paired_t_p_greater']:.4f}")
    if "non_inferiority_tost" in res:
        ni = res["non_inferiority_tost"]
        print(f"[tost]    δ={ni['margin']:.4f}  p_lower={ni['p_lower_one_sided']:.4f}  "
              f"non_inferior@α=0.05: {ni['non_inferior_at_alpha_0.05']}")
    print(f"[paired] saved → {out}")


if __name__ == "__main__":
    main()
