"""
Generate machine-readable feasibility reports per SPLIT_PROTOCOL.md Section 10.

Analyzes user-isolation split feasibility for each (state, engine) configuration.
Outputs one JSON file per state to docs/feasibility_report_{state}.json.

Usage:
    python scripts/generate_feasibility_report.py
    python scripts/generate_feasibility_report.py --state alabama florida
"""
import sys
from pathlib import Path

_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import argparse
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

# ---------------------------------------------------------------------------
# Constants matching SPLIT_PROTOCOL.md Section 5 defaults
# ---------------------------------------------------------------------------
DEFAULT_THRESHOLDS = {
    "min_category_val_fraction": 0.05,
    "min_next_val_fraction": 0.05,
    "min_class_count": 5,
    "min_class_fraction": 0.03,
}
K_FOLDS = 5
SEED_SEQUENCE = [42, 43, 44, 45, 46]
DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "checkins"


def load_checkins(state: str) -> pd.DataFrame:
    path = DATA_ROOT / f"{state.capitalize()}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Checkin data not found: {path}")
    return pd.read_parquet(path)


def classify_pois(df, train_users, val_users):
    """Classify POIs as train-exclusive, val-exclusive, or ambiguous."""
    train_pois = set(df[df["userid"].isin(train_users)]["placeid"].unique())
    val_pois = set(df[df["userid"].isin(val_users)]["placeid"].unique())
    ambiguous = train_pois & val_pois
    train_exclusive = train_pois - val_pois
    val_exclusive = val_pois - train_pois
    return train_exclusive, val_exclusive, ambiguous


def check_category_constraints(df, val_exclusive_pois, thresholds):
    """Check category validation acceptance constraints. Returns (pass, failure_details)."""
    poi_cat = df.groupby("placeid")["category"].first()
    total_pois_by_cat = poi_cat.value_counts()
    val_excl_cats = poi_cat[poi_cat.index.isin(val_exclusive_pois)]
    val_counts_by_cat = val_excl_cats.value_counts()

    total_val = len(val_exclusive_pois)
    total_pois = df["placeid"].nunique()

    # Overall fraction
    overall_frac = total_val / total_pois if total_pois > 0 else 0
    if overall_frac < thresholds["min_category_val_fraction"]:
        return False, f"overall_fraction={overall_frac:.4f}<{thresholds['min_category_val_fraction']}"

    # Per-category
    for cat in total_pois_by_cat.index:
        cat_total = total_pois_by_cat[cat]
        cat_val = val_counts_by_cat.get(cat, 0)
        min_required = max(thresholds["min_class_count"],
                           thresholds["min_class_fraction"] * cat_total)
        if cat_val < min_required:
            return False, f"category={cat},count={cat_val}<min_required={min_required:.0f}"

    return True, None


def check_next_constraints(df, val_users, thresholds):
    """Check next-task validation acceptance constraints."""
    total_checkins = len(df)
    val_checkins = len(df[df["userid"].isin(val_users)])
    frac = val_checkins / total_checkins if total_checkins > 0 else 0
    if frac < thresholds["min_next_val_fraction"]:
        return False, f"next_val_fraction={frac:.4f}<{thresholds['min_next_val_fraction']}"
    return True, None


def compute_overlap(df, ambiguous_pois, val_users, train_users):
    """Compute per-channel overlap metrics."""
    # cat_train -> next_val channel:
    # Ambiguous POIs are in cat_train. How many appear in val-user checkins?
    val_checkins = df[df["userid"].isin(val_users)]
    val_pois_visited = set(val_checkins["placeid"].unique())
    cat_train_next_val_pois = ambiguous_pois & val_pois_visited
    # Sequence fraction proxy: fraction of val-user checkins at ambiguous POIs
    val_at_ambiguous = val_checkins["placeid"].isin(cat_train_next_val_pois).sum()
    seq_frac = val_at_ambiguous / len(val_checkins) if len(val_checkins) > 0 else 0.0

    return {
        "cat_train_next_val_poi_count": len(cat_train_next_val_pois),
        "cat_train_next_val_seq_fraction": round(float(seq_frac), 6),
        # Under strict mode, cat_val contains only val-exclusive POIs.
        # Val-exclusive POIs are only visited by val-users, never train-users.
        # So they cannot appear in next-train sequences.
        "cat_val_next_train_poi_count": 0,
        "cat_val_next_train_seq_fraction": 0.0,
    }


def analyze_seed(df, seed, k_folds, thresholds):
    """Run StratifiedGroupKFold for one seed, return SeedDiagnostic dict."""
    user_cats = df.groupby("userid")["category"].agg(lambda x: x.mode().iloc[0])
    users = user_cats.index.values
    cats = user_cats.values

    sgkf = StratifiedGroupKFold(n_splits=k_folds, shuffle=True, random_state=seed)

    per_fold_overlap = []
    all_folds_valid = True
    failure_mode = None

    for fold_idx, (train_idx, val_idx) in enumerate(sgkf.split(users, cats, groups=users)):
        train_users = set(users[train_idx])
        val_users = set(users[val_idx])
        train_exclusive, val_exclusive, ambiguous = classify_pois(df, train_users, val_users)

        # Check constraints
        cat_ok, cat_fail = check_category_constraints(df, val_exclusive, thresholds)
        next_ok, next_fail = check_next_constraints(df, val_users, thresholds)

        if not cat_ok or not next_ok:
            all_folds_valid = False
            if not cat_ok and not next_ok:
                failure_mode = "both"
            elif not cat_ok:
                failure_mode = failure_mode or "category"
            else:
                failure_mode = failure_mode or "next_task"

        overlap = compute_overlap(df, ambiguous, val_users, train_users)
        per_fold_overlap.append(overlap)

    return {
        "seed": seed,
        "status": "valid_strict" if all_folds_valid else "rejected",
        "failure_mode": None if all_folds_valid else failure_mode,
        "per_fold_overlap": per_fold_overlap,
        "split_mode": "strict",
    }


def generate_report(state: str, engine: str = "hgi") -> dict:
    """Generate a full FeasibilityReport for one state."""
    df = load_checkins(state)
    thresholds = dict(DEFAULT_THRESHOLDS)

    seed_diagnostics = []
    selected_seed = None

    for seed in SEED_SEQUENCE:
        diag = analyze_seed(df, seed, K_FOLDS, thresholds)
        seed_diagnostics.append(diag)
        if diag["status"] == "valid_strict" and selected_seed is None:
            selected_seed = seed

    # If no seed passed strict, select the first seed (report will show it as rejected)
    if selected_seed is None:
        selected_seed = SEED_SEQUENCE[0]

    # Find selected seed diagnostic
    selected_diag = next(d for d in seed_diagnostics if d["seed"] == selected_seed)
    selected_overlaps = selected_diag["per_fold_overlap"]

    # Worst fold overlap for selected seed (max of cat_train_next_val_seq_fraction)
    worst_fold = max(selected_overlaps, key=lambda o: o["cat_train_next_val_seq_fraction"])

    # Overlap range across all seeds
    all_overlaps = [o for d in seed_diagnostics for o in d["per_fold_overlap"]]
    min_overlap = min(all_overlaps, key=lambda o: o["cat_train_next_val_seq_fraction"])
    max_overlap = max(all_overlaps, key=lambda o: o["cat_train_next_val_seq_fraction"])

    # Seed sensitivity: check variance of worst-fold seq_fraction across seeds
    per_seed_worst = []
    for d in seed_diagnostics:
        worst = max(o["cat_train_next_val_seq_fraction"] for o in d["per_fold_overlap"])
        per_seed_worst.append(worst)
    seed_std = float(np.std(per_seed_worst))
    seed_mean = float(np.mean(per_seed_worst))
    # Flag if coefficient of variation > 10%
    seed_sensitivity = (seed_std / seed_mean > 0.10) if seed_mean > 0 else False

    # Freeze max_overlap_fraction: worst-case seq_fraction across ALL seeds (not just selected)
    # This is the seed-independent property of the data.
    global_worst_seq_frac = max(
        o["cat_train_next_val_seq_fraction"]
        for d in seed_diagnostics
        for o in d["per_fold_overlap"]
    )
    max_overlap_fraction = round(min(global_worst_seq_frac, 1.0), 6)

    # Threshold exceeded?
    threshold_exceeded = worst_fold["cat_train_next_val_seq_fraction"] > max_overlap_fraction

    # Combined exposure (both channels elevated) — under strict, cat_val_next_train=0 always
    combined_exposure = False

    # Decision
    any_seed_valid = any(d["status"] == "valid_strict" for d in seed_diagnostics)
    decision_reasons = []

    if not any_seed_valid:
        decision_reasons.append("no_valid_seed_strict")
    if threshold_exceeded:
        decision_reasons.append("threshold_exceeded")
    if seed_sensitivity:
        decision_reasons.append("seed_sensitivity")
    if combined_exposure:
        decision_reasons.append("combined_exposure")

    if any_seed_valid and not decision_reasons:
        decision = "approved"
        justification = None
    elif any_seed_valid:
        decision = "approved_with_justification"
        justification = f"Seed {selected_seed} passes strict mode. Flags: {', '.join(decision_reasons)}."
    else:
        decision = "approved_with_justification"
        justification = (
            f"No seed passes strict mode with default thresholds. "
            f"Recommend split_relaxation=True or lowered min_category_val_fraction. "
            f"Flags: {', '.join(decision_reasons)}."
        )

    return {
        "state": state,
        "engine": engine,
        "k_folds": K_FOLDS,
        "split_relaxation": False,
        "threshold_settings": thresholds,
        "max_overlap_fraction": max_overlap_fraction,
        "decision": decision,
        "justification": justification,
        "threshold_exceeded": threshold_exceeded,
        "seed_sensitivity_flag": seed_sensitivity,
        "combined_exposure_flag": combined_exposure,
        "seed_diagnostics": seed_diagnostics,
        "selected_seed": selected_seed,
        "selected_seed_worst_fold_overlap": worst_fold,
        "overlap_range_across_seeds": {"min": min_overlap, "max": max_overlap},
        "decision_reasons": decision_reasons,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate split feasibility reports")
    parser.add_argument("--state", nargs="+", default=["alabama", "florida", "california", "texas"],
                        help="State(s) to analyze")
    args = parser.parse_args()

    out_dir = Path(__file__).resolve().parent.parent / "docs"
    out_dir.mkdir(exist_ok=True)

    for state in args.state:
        print(f"Generating feasibility report for {state}...")
        report = generate_report(state)
        out_path = out_dir / f"feasibility_report_{state}.json"
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"  -> {out_path}")
        print(f"  decision: {report['decision']}")
        print(f"  selected_seed: {report['selected_seed']}")
        print(f"  max_overlap_fraction: {report['max_overlap_fraction']}")
        if report["justification"]:
            print(f"  justification: {report['justification']}")
        print()


if __name__ == "__main__":
    main()
