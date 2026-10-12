"""O1 (audit AUDIT_TIER1_TIERS_2026-06-03 §2/§6) — settle the α=0 question.

The T1.4 reg tune found α=0 (log_T prior frozen OFF) beats the default
prior-ON (learnable α, init 0.1) STL-reg ceiling at every state
(AL 62.88 vs 62.32, FL 73.31 vs 70.28, ...). But a *learnable* α can always
drive itself to 0, so prior-ON should be ≥ frozen-α0 — yet it scored WORSE.
That means either (i) α did NOT converge to its optimum (optimisation
artifact) or (ii) the encoder co-adapted to a nonzero prior.

p1_region_head_ablation does not persist the model, so the learned α was
never saved. This probe RE-RUNS the exact prior-ON config (faithful — it
reuses p1's own `_train_single_task` via a `_build_head` monkeypatch that
captures the trained head) and reads the final learned α per fold.

Also emits two cheap diagnostics the audit asked for:
  - standalone log_T Acc@10 (prior alone, no encoder) — is the prior any good?
  - log_T row coverage at this state — rule out "just a sparse/bad prior".

Verdict logic:
  α converged ≈0 yet prior-ON scored < frozen-α0  -> optimisation artifact
  α stayed ≈0.1 (init)                            -> "model didn't drop prior"

Usage:
  PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/o1_alpha_probe.py \
      --states alabama florida [arizona georgia] --folds 5 --epochs 50
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import importlib.util

import numpy as np
import torch
from sklearn.model_selection import StratifiedGroupKFold

# p1_region_head_ablation lives in scripts/ which is not a package — load by path.
_p1_path = _root / "scripts" / "p1_region_head_ablation.py"
_spec = importlib.util.spec_from_file_location("p1_region_head_ablation", _p1_path)
p1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p1)

from tracking.metrics import compute_classification_metrics  # noqa: E402

V14 = "check2hgi_design_k_resln_mae_l0_1"

# ---- monkeypatch: capture the head instance built inside _train_single_task ----
_CAPTURED: dict = {}
_orig_build_head = p1._build_head


def _capturing_build_head(head_name, emb_dim, n_classes, seq_length, overrides):
    head = _orig_build_head(head_name, emb_dim, n_classes, seq_length, overrides)
    _CAPTURED["head"] = head
    return head


p1._build_head = _capturing_build_head


def _read_alpha(head) -> float:
    """next_stan_flow keeps α as `self.alpha` (Parameter when learnable)."""
    a = getattr(head, "alpha", None)
    if a is None:
        return float("nan")
    return float(a.detach().cpu().item())


def _logT_for_fold(state: str, seed: int, fold_idx: int, n_classes: int) -> torch.Tensor:
    pf = Path(f"output/check2hgi/{state}") / f"region_transition_log_seed{seed}_fold{fold_idx + 1}.pt"
    payload = torch.load(pf, map_location="cpu", weights_only=False)
    log_T = payload["log_transition"] if isinstance(payload, dict) else payload
    log_T = log_T.float()[:n_classes, :n_classes].contiguous()
    return log_T


def _standalone_prior_acc10(log_T, last_region, y, val_idx, n_classes) -> float:
    """Acc@10 of the prior ALONE (logits = log_T[last_region]) on the val split."""
    li = last_region[val_idx].clamp(min=0, max=n_classes - 1)
    logits = log_T[li]  # [Nval, C]
    targets = y[val_idx]
    m = compute_classification_metrics(logits, targets, num_classes=n_classes, top_k=(5, 10))
    return float(m.get("top10_acc", 0.0))


def _row_coverage(log_T) -> dict:
    """Fraction of source-region rows that carry real transition mass.

    compute_region_transition leaves unseen (source,*) rows as a constant
    (log of a uniform / smoothing floor); a "covered" row has non-uniform
    structure i.e. row.max() > row.min(). Reports coverage + mean distinct
    high-mass targets per covered row.
    """
    R = log_T.shape[0]
    row_max = log_T.max(dim=1).values
    row_min = log_T.min(dim=1).values
    covered = (row_max > row_min)
    n_cov = int(covered.sum().item())
    return {
        "n_regions": int(R),
        "n_covered_rows": n_cov,
        "coverage_frac": round(n_cov / R, 4) if R else 0.0,
    }


def run_state(state: str, folds: int, epochs: int, seed: int = 42) -> dict:
    print(f"\n{'#'*70}\n# O1 α-probe — {state}  (prior-ON, learnable α init 0.1, v14)\n{'#'*70}")
    x_tensor, y_region, y_cat, userids, emb_dim, n_regions, last_region = p1._load_data(
        state, input_type="region", region_emb_source=V14,
    )
    if last_region is None:
        raise RuntimeError(f"{state}: last_region_idx missing — cannot run prior head.")

    sgkf = StratifiedGroupKFold(n_splits=max(2, folds), shuffle=True, random_state=seed)
    splits = list(sgkf.split(np.zeros(len(y_cat)), y_cat, groups=userids))[:folds]

    max_lr = p1._HEAD_MAX_LR["next_stan_flow"]  # 3e-3
    per_fold = []
    for fi, (tr, va) in enumerate(splits):
        pf = Path(f"output/check2hgi/{state}") / f"region_transition_log_seed{seed}_fold{fi + 1}.pt"
        overrides = {"transition_path": str(pf)}  # prior ON, learnable α (no freeze)
        _CAPTURED.clear()
        metrics = p1._train_single_task(
            "next_stan_flow", x_tensor, y_region, tr, va,
            emb_dim, n_regions, epochs, 2048, seed + fi,
            overrides, max_lr, label_smoothing=0.0, input_ln=False,
            aux_tensor=last_region,
        )
        alpha = _read_alpha(_CAPTURED["head"])
        log_T = _logT_for_fold(state, seed, fi, n_regions)
        prior_acc10 = _standalone_prior_acc10(log_T, last_region, y_region, va, n_regions)
        cov = _row_coverage(log_T)
        rec = {
            "fold": fi + 1,
            "alpha_learned": round(alpha, 5),
            "prioron_acc10": round(float(metrics.get("top10_acc", 0.0)) * 100, 3),
            "standalone_prior_acc10": round(prior_acc10 * 100, 3),
            "logT_coverage": cov,
            "best_epoch": int(metrics.get("best_epoch", 0)),
        }
        per_fold.append(rec)
        print(f"  fold {fi+1}: α={alpha:+.5f}  prior-ON Acc@10={rec['prioron_acc10']:.2f}  "
              f"standalone-prior Acc@10={rec['standalone_prior_acc10']:.2f}  "
              f"cov={cov['coverage_frac']:.2%} ({cov['n_covered_rows']}/{cov['n_regions']})")

    alphas = [r["alpha_learned"] for r in per_fold]
    accs = [r["prioron_acc10"] for r in per_fold]
    pri = [r["standalone_prior_acc10"] for r in per_fold]
    summary = {
        "state": state, "seed": seed, "folds": folds, "epochs": epochs,
        "alpha_mean": round(float(np.mean(alphas)), 5),
        "alpha_std": round(float(np.std(alphas, ddof=1)), 5) if len(alphas) > 1 else 0.0,
        "alpha_per_fold": alphas,
        "prioron_acc10_mean": round(float(np.mean(accs)), 3),
        "standalone_prior_acc10_mean": round(float(np.mean(pri)), 3),
        "coverage_frac": per_fold[0]["logT_coverage"]["coverage_frac"],
        "per_fold": per_fold,
    }
    print(f"  -> α mean={summary['alpha_mean']:+.5f} ±{summary['alpha_std']:.5f}  "
          f"prior-ON Acc@10={summary['prioron_acc10_mean']:.2f}  "
          f"standalone-prior Acc@10={summary['standalone_prior_acc10_mean']:.2f}")
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", nargs="+", default=["alabama", "florida"])
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="docs/results/mtl_improvement/o1_alpha_probe.json")
    args = ap.parse_args()

    results = {}
    for st in args.states:
        results[st] = run_state(st, args.folds, args.epochs, args.seed)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(results, open(out, "w"), indent=2)
    print(f"\nSaved: {out}")

    print(f"\n{'='*70}\nO1 VERDICT TABLE\n{'='*70}")
    print(f"{'state':<10} {'α(mean±sd)':>16} {'prior-ON@10':>12} {'stand-prior@10':>15} {'cov':>7}")
    for st, s in results.items():
        print(f"{st:<10} {s['alpha_mean']:+.4f}±{s['alpha_std']:.4f}   "
              f"{s['prioron_acc10_mean']:>10.2f}  {s['standalone_prior_acc10_mean']:>13.2f}  "
              f"{s['coverage_frac']:>6.1%}")


if __name__ == "__main__":
    main()
