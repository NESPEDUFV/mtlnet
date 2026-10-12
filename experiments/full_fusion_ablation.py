"""Full fusion+alabama ablation study runner (v2).

Implements the staged protocol from docs/full_ablation_study/STUDY_DESIGN.md.
Each stage reads results from the previous stage to decide what to promote.

Fusion preset: space_hgi_time
  - Category: Sphere2Vec(64) + HGI(64) = 128D
  - Next: HGI(64) + Time2Vec(64) = 128D

Usage:
    # Run Stage 0 (baseline comparison: fusion + HGI reference)
    python experiments/full_fusion_ablation.py --stage 0

    # Run Stage 1 (arch x optimizer screen)
    python experiments/full_fusion_ablation.py --stage 1

    # Run Stage 2 (head variants on Stage 1 winners)
    python experiments/full_fusion_ablation.py --stage 2

    # Run Stage 3 (5-fold confirmation)
    python experiments/full_fusion_ablation.py --stage 3

    # Run Stage 4 (cross-state validation on florida)
    python experiments/full_fusion_ablation.py --stage 4

    # Run all stages sequentially
    python experiments/full_fusion_ablation.py --stage all

    # Dry-run: print commands without executing
    python experiments/full_fusion_ablation.py --stage 1 --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from ablation.candidates import MTLCandidate
from ablation.runner import (
    AblationResult,
    _run_candidate,
    _top_candidates,
    _write_manifest,
    _write_summary,
)

# =====================================================================
# Constants
# =====================================================================

STATE = "alabama"
ENGINE = "fusion"
EMBEDDING_DIM = 128
HGI_EMBEDDING_DIM = 64
SEED = 42
RESULTS_ROOT = _root / "results" / "ablations" / "full_fusion_study"

# =====================================================================
# Stage 0: Baseline Comparison (fusion + HGI reference)
# =====================================================================

STAGE_0_CANDIDATES = (
    # Fusion candidates
    MTLCandidate(
        name="s0_fusion_base_equal",
        stage="s0",
        model_name="mtlnet",
        mtl_loss="equal_weight",
        rationale="Simplest fusion baseline.",
    ),
    MTLCandidate(
        name="s0_fusion_cgc22_equal",
        stage="s0",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="equal_weight",
        rationale="Prior HGI winner architecture on fusion.",
    ),
    MTLCandidate(
        name="s0_fusion_dselectk_db",
        stage="s0",
        model_name="mtlnet_dselectk",
        model_params={"num_experts": 4, "num_selectors": 2, "temperature": 0.5},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Prior DGI winner architecture on fusion.",
    ),
)

# HGI reference — run separately with different engine/dim
_S0_HGI_REFERENCE = MTLCandidate(
    name="s0_hgi_cgc22_equal",
    stage="s0",
    model_name="mtlnet_cgc",
    model_params={"num_shared_experts": 2, "num_task_experts": 2},
    mtl_loss="equal_weight",
    rationale="HGI-only reference: prior best config for direct comparison.",
)

# =====================================================================
# Stage 1: Architecture x Optimizer (5 x 5 = 25)
# =====================================================================

_S1_ARCHS = [
    ("base", "mtlnet", {}),
    ("cgc22", "mtlnet_cgc", {"num_shared_experts": 2, "num_task_experts": 2}),
    ("cgc21", "mtlnet_cgc", {"num_shared_experts": 2, "num_task_experts": 1}),
    ("mmoe4", "mtlnet_mmoe", {"num_experts": 4}),
    ("dsk42", "mtlnet_dselectk", {"num_experts": 4, "num_selectors": 2, "temperature": 0.5}),
]

_S1_OPTS = [
    ("eq", "equal_weight", {}),
    ("db", "db_mtl", {"beta": 0.9, "beta_sigma": 0.5}),
    ("ca", "cagrad", {"c": 0.4}),
    ("al", "aligned_mtl", {}),
    ("uw", "uncertainty_weighting", {}),
]

STAGE_1_CANDIDATES = tuple(
    MTLCandidate(
        name=f"s1_{a_short}_{o_short}",
        stage="s1",
        model_name=a_model,
        model_params=dict(a_params),
        mtl_loss=o_loss,
        mtl_loss_params=dict(o_params),
        rationale=f"Stage 1: {a_model} + {o_loss}",
    )
    for a_short, a_model, a_params in _S1_ARCHS
    for o_short, o_loss, o_params in _S1_OPTS
)

# =====================================================================
# Stage 2: Head Variants (generated dynamically from Stage 1 results)
# =====================================================================

_S2_HEAD_VARIANTS = [
    ("hd_dcn", {
        "category_head": "category_dcn",
        "category_head_params": {"hidden_dims": [128, 64], "cross_layers": 2},
    }),
    ("hd_tcnr", {
        "next_head": "next_tcn_residual",
        "next_head_params": {"hidden_channels": 128, "num_blocks": 4, "kernel_size": 3, "dropout": 0.2},
    }),
    ("hd_both", {
        "category_head": "category_dcn",
        "category_head_params": {"hidden_dims": [128, 64], "cross_layers": 2},
        "next_head": "next_tcn_residual",
        "next_head_params": {"hidden_channels": 128, "num_blocks": 4, "kernel_size": 3, "dropout": 0.2},
    }),
]


def _build_stage2_candidates(stage1_winners: list[MTLCandidate]) -> tuple[MTLCandidate, ...]:
    """Generate Stage 2 candidates from Stage 1 winners + head variants."""
    candidates = []
    for winner in stage1_winners:
        for hv_short, hv_params in _S2_HEAD_VARIANTS:
            merged_params = dict(winner.model_params)
            merged_params.update(hv_params)
            candidates.append(MTLCandidate(
                name=f"s2_{winner.name[3:]}_{hv_short}",
                stage="s2",
                model_name=winner.model_name,
                model_params=merged_params,
                mtl_loss=winner.mtl_loss,
                mtl_loss_params=dict(winner.mtl_loss_params),
                rationale=f"Stage 2: {winner.name} + {hv_short}",
            ))
    return tuple(candidates)


# =====================================================================
# Execution helpers
# =====================================================================


def _load_summary(path: Path) -> list[AblationResult]:
    """Load AblationResult rows from a summary CSV."""
    rows = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in ("joint_score", "next_f1", "category_f1", "duration_seconds"):
                val = row.get(key, "")
                row[key] = float(val) if val else None
            row["returncode"] = int(row.get("returncode", -1))
            row["epochs"] = int(row.get("epochs", 0))
            row["folds"] = int(row.get("folds", 0))
            seed_val = row.get("seed", "")
            row["seed"] = int(seed_val) if seed_val else None
            rows.append(AblationResult(**{
                k: v for k, v in row.items() if k in AblationResult.__dataclass_fields__
            }))
    return rows


def _find_candidate_by_name(name: str, candidates: tuple[MTLCandidate, ...]) -> MTLCandidate:
    for c in candidates:
        if c.name == name:
            return c
    raise KeyError(f"Candidate {name!r} not found")


def _run_stage(
    label: str,
    candidates: tuple[MTLCandidate, ...],
    epochs: int,
    folds: int,
    dry_run: bool = False,
    engine: str = ENGINE,
    state: str = STATE,
    embedding_dim: int = EMBEDDING_DIM,
) -> Path:
    """Run a batch of candidates and return the summary CSV path."""
    label_root = RESULTS_ROOT / label
    label_root.mkdir(parents=True, exist_ok=True)

    _write_manifest(
        label_root / "manifest.json",
        stage=label,
        state=state,
        engine=engine,
        epochs=epochs,
        folds=folds,
        seed=SEED,
        candidates=candidates,
    )

    if dry_run:
        from ablation.runner import _candidate_argv
        print(f"\n[dry-run] Stage: {label} ({len(candidates)} candidates, engine={engine}, dim={embedding_dim})")
        for c in candidates:
            argv = _candidate_argv(c, state, engine, epochs, folds, SEED, embedding_dim)
            print(f"  {c.name}: {' '.join(argv)}")
        return label_root / "summary.csv"

    from ablation.runner import _default_data_root, _default_output_dir

    rows = [
        _run_candidate(
            candidate,
            state=state,
            engine=engine,
            epochs=epochs,
            folds=folds,
            seed=SEED,
            label_root=label_root,
            data_root=_default_data_root(),
            output_dir=_default_output_dir(),
            embedding_dim=embedding_dim,
        )
        for candidate in candidates
    ]

    summary_path = label_root / "summary.csv"
    _write_summary(summary_path, rows)
    print(f"[study] wrote summary: {summary_path}")

    # Print ranking
    successful = [r for r in rows if r.status == "ok" and r.joint_score is not None]
    successful.sort(key=lambda r: r.joint_score or 0.0, reverse=True)
    if successful:
        print(f"\n[study] === {label.upper()} RANKING ===")
        for i, r in enumerate(successful, 1):
            print(
                f"  {i:2d}. {r.candidate:30s}  joint={r.joint_score:.4f}  "
                f"next={r.next_f1:.4f}  cat={r.category_f1:.4f}  "
                f"time={r.duration_seconds:.0f}s"
            )

    return summary_path


# =====================================================================
# Stage runners
# =====================================================================


def run_stage_0(dry_run: bool = False) -> Path:
    print("[study] ========== STAGE 0: Baseline Comparison ==========")

    # Run fusion candidates
    fusion_path = _run_stage(
        "s0_fusion_1f_10ep", STAGE_0_CANDIDATES,
        epochs=10, folds=1, dry_run=dry_run,
    )

    # Run HGI reference (different engine + dim)
    print("\n[study] --- HGI Reference ---")
    hgi_path = _run_stage(
        "s0_hgi_ref_1f_10ep", (_S0_HGI_REFERENCE,),
        epochs=10, folds=1, dry_run=dry_run,
        engine="hgi", embedding_dim=HGI_EMBEDDING_DIM,
    )

    if not dry_run:
        # Print comparison
        fusion_rows = _load_summary(fusion_path)
        hgi_rows = _load_summary(hgi_path)
        print("\n[study] === FUSION vs HGI COMPARISON ===")
        for r in fusion_rows + hgi_rows:
            if r.status == "ok" and r.joint_score is not None:
                engine_tag = "FUSION" if "fusion" in r.candidate else "HGI  "
                print(
                    f"  {engine_tag} {r.candidate:30s}  joint={r.joint_score:.4f}  "
                    f"next={r.next_f1:.4f}  cat={r.category_f1:.4f}"
                )

    return fusion_path


def run_stage_1(dry_run: bool = False) -> Path:
    print("[study] ========== STAGE 1: Architecture x Optimizer Screen ==========")
    summary = _run_stage("s1_screen_1f_10ep", STAGE_1_CANDIDATES, epochs=10, folds=1, dry_run=dry_run)

    if dry_run:
        return summary

    # Promote top 5 to 2f x 15ep
    rows = _load_summary(summary)
    top5_names = _top_candidates(rows, 5)
    if not top5_names:
        print("[study] ERROR: Stage 1 produced no successful candidates. Cannot promote.")
        sys.exit(1)

    top5 = tuple(_find_candidate_by_name(n, STAGE_1_CANDIDATES) for n in top5_names)
    print(f"\n[study] Promoting top {len(top5)}: {', '.join(top5_names)}")
    promoted = _run_stage("s1_promoted_2f_15ep", top5, epochs=15, folds=2)
    return promoted


def run_stage_2(dry_run: bool = False) -> Path:
    print("[study] ========== STAGE 2: Head Variants ==========")

    promoted_path = RESULTS_ROOT / "s1_promoted_2f_15ep" / "summary.csv"
    if not promoted_path.exists():
        print(f"[study] ERROR: Stage 1 promoted results not found at {promoted_path}")
        print("[study] Run Stage 1 first.")
        sys.exit(1)

    rows = _load_summary(promoted_path)
    top3_names = _top_candidates(rows, 3)
    if not top3_names:
        print("[study] ERROR: Stage 1 promoted results contain no successful candidates.")
        sys.exit(1)
    top3 = [_find_candidate_by_name(n, STAGE_1_CANDIDATES) for n in top3_names]

    print(f"[study] Stage 1 top-{len(top3)}: {', '.join(top3_names)}")

    s2_candidates = _build_stage2_candidates(top3)
    return _run_stage("s2_heads_2f_15ep", s2_candidates, epochs=15, folds=2, dry_run=dry_run)


def run_stage_3(dry_run: bool = False) -> Path:
    print("[study] ========== STAGE 3: Full Confirmation ==========")

    all_candidates: dict[str, MTLCandidate] = {}
    all_results: list[AblationResult] = []

    # Stage 1 promoted
    s1_path = RESULTS_ROOT / "s1_promoted_2f_15ep" / "summary.csv"
    if s1_path.exists():
        all_results.extend(_load_summary(s1_path))
        for c in STAGE_1_CANDIDATES:
            all_candidates[c.name] = c

    # Stage 2
    s2_path = RESULTS_ROOT / "s2_heads_2f_15ep" / "summary.csv"
    if s2_path.exists():
        all_results.extend(_load_summary(s2_path))
        s1_rows = _load_summary(s1_path) if s1_path.exists() else []
        s1_top3_names = _top_candidates(s1_rows, 3)
        s1_top3 = [_find_candidate_by_name(n, STAGE_1_CANDIDATES) for n in s1_top3_names]
        for c in _build_stage2_candidates(s1_top3):
            all_candidates[c.name] = c

    if not all_results:
        print("[study] ERROR: No prior stage results found. Run Stages 1-2 first.")
        sys.exit(1)

    top3_names = _top_candidates(all_results, 3)
    top3 = [all_candidates[n] for n in top3_names]

    print(f"[study] Overall top-3: {', '.join(top3_names)}")

    s3_candidates = tuple(
        MTLCandidate(
            name=f"s3_{c.name}",
            stage="s3",
            model_name=c.model_name,
            model_params=dict(c.model_params),
            mtl_loss=c.mtl_loss,
            mtl_loss_params=dict(c.mtl_loss_params),
            rationale=f"Stage 3 confirmation of {c.name}",
        )
        for c in top3
    )

    return _run_stage("s3_confirm_5f_50ep", s3_candidates, epochs=50, folds=5, dry_run=dry_run)


def run_stage_4(dry_run: bool = False) -> Path:
    print("[study] ========== STAGE 4: Cross-State Validation (Florida) ==========")

    # Find top-1 from Stage 3
    s3_path = RESULTS_ROOT / "s3_confirm_5f_50ep" / "summary.csv"
    if not s3_path.exists():
        print(f"[study] ERROR: Stage 3 results not found at {s3_path}")
        print("[study] Run Stage 3 first.")
        sys.exit(1)

    rows = _load_summary(s3_path)
    top1_results = _top_candidates(rows, 1)
    if not top1_results:
        print("[study] ERROR: Stage 3 produced no successful candidates.")
        sys.exit(1)
    top1_name = top1_results[0]

    # Strip s3_ prefix to find the original candidate
    original_name = top1_name[3:]  # remove "s3_"

    # Search in all candidate pools
    all_candidates: dict[str, MTLCandidate] = {}
    for c in STAGE_1_CANDIDATES:
        all_candidates[c.name] = c
    # Also check Stage 2 candidates
    s1_path = RESULTS_ROOT / "s1_promoted_2f_15ep" / "summary.csv"
    if s1_path.exists():
        s1_rows = _load_summary(s1_path)
        s1_top3_names = _top_candidates(s1_rows, 3)
        s1_top3 = [_find_candidate_by_name(n, STAGE_1_CANDIDATES) for n in s1_top3_names]
        for c in _build_stage2_candidates(s1_top3):
            all_candidates[c.name] = c

    winner = all_candidates[original_name]
    print(f"[study] Stage 3 winner: {top1_name} -> validating on florida")

    s4_candidate = MTLCandidate(
        name=f"s4_florida_{winner.name}",
        stage="s4",
        model_name=winner.model_name,
        model_params=dict(winner.model_params),
        mtl_loss=winner.mtl_loss,
        mtl_loss_params=dict(winner.mtl_loss_params),
        rationale=f"Cross-state validation of {winner.name} on florida.",
    )

    return _run_stage(
        "s4_florida_5f_50ep", (s4_candidate,),
        epochs=50, folds=5, dry_run=dry_run,
        state="florida",
    )


# =====================================================================
# CLI
# =====================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Full fusion+alabama ablation study (v2).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--stage",
        choices=("0", "1", "2", "3", "4", "all"),
        required=True,
        help="Which stage to run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing.",
    )
    args = parser.parse_args()

    stages = ["0", "1", "2", "3", "4"] if args.stage == "all" else [args.stage]

    for stage in stages:
        if stage == "0":
            run_stage_0(dry_run=args.dry_run)
        elif stage == "1":
            run_stage_1(dry_run=args.dry_run)
        elif stage == "2":
            run_stage_2(dry_run=args.dry_run)
        elif stage == "3":
            run_stage_3(dry_run=args.dry_run)
        elif stage == "4":
            run_stage_4(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
