"""Validate parquet inputs for a (state, engine) combination.

Exit codes:
  0 — pass (and optional warnings only)
  1 — warnings only
  2 — fail

Writes JSON report to $STUDY_DIR/results/P0/integrity/<state>_<engine>.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from _state import REPO_ROOT, RESULTS_DIR, utcnow

CATEGORY_NAMES = {"Food", "Shopping", "Community", "Entertainment", "Outdoors", "Travel", "Nightlife"}
CATEGORY_IDS = {0, 1, 2, 3, 4, 5, 6}
SINGLE_DIM = 64
FUSION_DIM = 128
WINDOW = 9

REFERENCE_DISTRIBUTIONS: dict[str, dict[str, float]] = {
    "alabama": {
        "Food": 0.325, "Shopping": 0.313, "Community": 0.150,
        "Entertainment": 0.065, "Outdoors": 0.061, "Travel": 0.060, "Nightlife": 0.025,
    },
}


def _label_set(series) -> set:
    vals = series.unique()
    if series.dtype == object:
        return set(vals.tolist())
    return set(int(x) for x in vals)


def _label_ok(labels: set) -> bool:
    return labels.issubset(CATEGORY_NAMES) or labels.issubset(CATEGORY_IDS)


@dataclass
class Report:
    state: str
    engine: str
    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        self.passed = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "engine": self.engine,
            "passed": self.passed,
            "warnings": self.warnings,
            "errors": self.errors,
            "details": self.details,
            "generated_at": utcnow(),
        }


def _input_path(engine: str, state: str, kind: str) -> Path:
    return REPO_ROOT / "output" / engine / state / "input" / f"{kind}.parquet"


def _expected_dim(engine: str) -> int:
    return FUSION_DIM if engine == "fusion" else SINGLE_DIM


def _check_nan_inf(values: np.ndarray, label: str, report: Report) -> None:
    if np.isnan(values).any():
        report.fail(f"{label}: contains NaN")
    if np.isinf(values).any():
        report.fail(f"{label}: contains Inf")


def _l2_stats(matrix: np.ndarray) -> dict[str, float]:
    norms = np.linalg.norm(matrix, axis=1)
    return {
        "mean": float(norms.mean()),
        "std": float(norms.std()),
        "min": float(norms.min()),
        "max": float(norms.max()),
    }


def validate_category(engine: str, state: str, report: Report) -> set[int] | None:
    path = _input_path(engine, state, "category")
    if not path.exists():
        report.fail(f"category parquet missing at {path}")
        return None
    df = pd.read_parquet(path)
    dim = _expected_dim(engine)
    required_cols = {"placeid", "category"}
    missing = required_cols - set(df.columns)
    if missing:
        report.fail(f"category: missing columns {missing}")
        return None

    emb_cols = [c for c in df.columns if c not in required_cols]
    if len(emb_cols) != dim:
        report.fail(f"category: expected {dim} embedding cols, got {len(emb_cols)}")
        return None

    labels = _label_set(df["category"])
    if not _label_ok(labels):
        extras = labels - CATEGORY_NAMES - CATEGORY_IDS
        report.fail(f"category: unexpected labels {extras}")

    emb = df[emb_cols].to_numpy(dtype=np.float64, copy=False)
    _check_nan_inf(emb, "category embeddings", report)

    stats = _l2_stats(emb)
    if stats["mean"] < 0.01 or stats["mean"] > 1000:
        report.warn(f"category: unusual L2 mean {stats['mean']:.3f}")

    dist_raw = df["category"].value_counts(normalize=True).to_dict()
    dist = {str(k): float(v) for k, v in dist_raw.items()}
    reference = REFERENCE_DISTRIBUTIONS.get(state)
    if reference:
        for cls, expected in reference.items():
            observed = dist.get(cls, 0.0)
            if abs(observed - expected) / max(expected, 1e-6) > 0.20:
                report.warn(
                    f"category class {cls}: distribution {observed:.3f} vs expected ~{expected:.3f} (>20% deviation)"
                )

    report.details["category"] = {
        "rows": int(len(df)),
        "cols": int(df.shape[1]),
        "embedding_dim": len(emb_cols),
        "label_distribution": dist,
        "l2_norm": stats,
        "num_placeids": int(df["placeid"].nunique()),
    }
    return set(df["placeid"].unique().tolist())


def validate_next(engine: str, state: str, report: Report) -> set[str] | None:
    path = _input_path(engine, state, "next")
    if not path.exists():
        report.fail(f"next parquet missing at {path}")
        return None
    df = pd.read_parquet(path)
    dim = _expected_dim(engine)
    expected_emb_cols = dim * WINDOW

    required_cols = {"next_category", "userid"}
    missing = required_cols - set(df.columns)
    if missing:
        report.fail(f"next: missing columns {missing}")
        return None

    reserved = required_cols
    emb_cols = [c for c in df.columns if c not in reserved]
    if len(emb_cols) != expected_emb_cols:
        report.fail(
            f"next: expected {expected_emb_cols} embedding cols (dim={dim} × window={WINDOW}), got {len(emb_cols)}"
        )
        return None

    labels = _label_set(df["next_category"])
    if not _label_ok(labels):
        extras = labels - CATEGORY_NAMES - CATEGORY_IDS
        report.fail(f"next: unexpected labels {extras}")

    emb = df[emb_cols].to_numpy(dtype=np.float32, copy=False)
    _check_nan_inf(emb, "next embeddings", report)

    dist_raw = df["next_category"].value_counts(normalize=True).to_dict()
    dist = {str(k): float(v) for k, v in dist_raw.items()}

    report.details["next"] = {
        "rows": int(len(df)),
        "cols": int(df.shape[1]),
        "window": WINDOW,
        "embedding_dim": dim,
        "label_distribution": dist,
        "num_users": int(df["userid"].nunique()),
    }
    return set(df["userid"].unique().tolist())


def fusion_scale_ratio(state: str, report: Report) -> None:
    """Check scale ratios on fusion category input (first 64 dims vs last 64 dims).

    Pre-bug Alabama: Sphere2Vec ~ 0.55 vs HGI ~ 8.46 → ratio ~15:1.
    """
    path = _input_path("fusion", state, "category")
    if not path.exists():
        return
    df = pd.read_parquet(path)
    emb_cols = [c for c in df.columns if c not in {"placeid", "category"}]
    if len(emb_cols) != FUSION_DIM:
        return
    emb = df[emb_cols].to_numpy(dtype=np.float64)
    half1 = np.linalg.norm(emb[:, :SINGLE_DIM], axis=1).mean()
    half2 = np.linalg.norm(emb[:, SINGLE_DIM:], axis=1).mean()
    if half1 == 0 or half2 == 0:
        report.warn("fusion: one half of the embedding has zero L2 norm")
        return
    ratio = max(half1, half2) / min(half1, half2)
    report.details.setdefault("category", {})["fusion_half_l2"] = {
        "first_half_mean": float(half1),
        "second_half_mean": float(half2),
        "ratio": float(ratio),
    }
    if ratio < 5 or ratio > 30:
        report.warn(
            f"fusion: category half-L2 ratio {ratio:.2f} outside expected 5-30× band (pre-bug ~15×)"
        )


def cross_consistency(state: str, report: Report, engines: list[str]) -> None:
    """Check that POI sets and user sets match across engines for the same state."""
    poi_sets: dict[str, set] = {}
    user_sets: dict[str, set] = {}
    for engine in engines:
        cat_path = _input_path(engine, state, "category")
        next_path = _input_path(engine, state, "next")
        if cat_path.exists():
            poi_sets[engine] = set(pd.read_parquet(cat_path, columns=["placeid"])["placeid"].unique())
        if next_path.exists():
            user_sets[engine] = set(pd.read_parquet(next_path, columns=["userid"])["userid"].unique())

    if len(poi_sets) >= 2:
        engines_present = sorted(poi_sets)
        base = engines_present[0]
        for other in engines_present[1:]:
            diff = poi_sets[base] ^ poi_sets[other]
            if diff:
                report.fail(
                    f"cross-consistency: placeid sets differ between {base} and {other} (|Δ|={len(diff)})"
                )
    if len(user_sets) >= 2:
        engines_present = sorted(user_sets)
        base = engines_present[0]
        for other in engines_present[1:]:
            diff = user_sets[base] ^ user_sets[other]
            if diff:
                report.fail(
                    f"cross-consistency: userid sets differ between {base} and {other} (|Δ|={len(diff)})"
                )


def validate(state: str, engine: str, with_cross: list[str] | None) -> Report:
    report = Report(state=state, engine=engine)
    validate_category(engine, state, report)
    validate_next(engine, state, report)
    if engine == "fusion":
        fusion_scale_ratio(state, report)
    if with_cross:
        cross_consistency(state, report, engines=[engine, *with_cross])
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate study inputs for a state+engine.")
    parser.add_argument("--state", required=True, help="Dataset state, e.g. alabama")
    parser.add_argument("--engine", required=True, help="Embedding engine (dgi/hgi/fusion/...)")
    parser.add_argument(
        "--cross", nargs="*", default=None,
        help="Extra engines to cross-check POI/user sets against (same state).",
    )
    parser.add_argument(
        "--report-dir", default=None,
        help="Directory to write JSON report (default: $STUDY_DIR/results/P0/integrity/).",
    )
    args = parser.parse_args()

    report = validate(args.state, args.engine, args.cross)

    out_dir = Path(args.report_dir) if args.report_dir else RESULTS_DIR / "P0" / "integrity"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.state}_{args.engine}.json"
    with out_path.open("w") as fh:
        json.dump(report.to_dict(), fh, indent=2)

    print(f"[validate_inputs] state={args.state} engine={args.engine} → {out_path}")
    for w in report.warnings:
        print(f"  WARN  {w}")
    for e in report.errors:
        print(f"  FAIL  {e}")
    if not report.passed:
        return 2
    if report.warnings:
        return 1
    print("  OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
