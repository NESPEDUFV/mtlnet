"""Archive a training run into $STUDY_DIR/results/<phase>/<test_id>/.

Copies summary/full_summary.json, the run's manifest.json (if present), and
per-fold info so the raw numbers stay inspectable. Writes a slim metadata.json
pointing back at the original run_dir and summarizing observed metrics.

Idempotent: if the target exists with the same summary content, it's a no-op.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from _state import REPO_ROOT, RESULTS_DIR, mutate_state, set_test, utcnow


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_summary(run_dir: Path) -> dict[str, Any]:
    summary_path = run_dir / "summary" / "full_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing {summary_path}")
    with summary_path.open() as fh:
        return json.load(fh)


def _resolve_manifest(run_dir: Path) -> Path | None:
    candidates = [run_dir / "manifest.json", run_dir.parent / "manifest.json"]
    for c in candidates:
        if c.exists():
            return c
    return None


def _harmonic(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    if a + b == 0:
        return 0.0
    return 2 * a * b / (a + b)


def _joint_score(summary: dict[str, Any]) -> float | None:
    """Joint F1 at joint-peak checkpoint (reported as `joint_f1`)."""
    try:
        cat = float(summary["category"]["f1"]["mean"])
        nxt = float(summary["next"]["f1"]["mean"])
    except (KeyError, TypeError):
        return None
    return _harmonic(cat, nxt)


def _joint_score_taskbest(summary: dict[str, Any]) -> tuple[float | None, float | None, float | None]:
    """Joint F1 computed from per-task-best checkpoints (diagnostic).

    Returns (joint_f1_taskbest, cat_f1_taskbest, next_f1_taskbest).
    Reveals ceiling performance when each task selects its own best epoch,
    vs. the single joint-peak checkpoint used for deployment.
    See claim C32 and docs/archive/fusion-study/issues/P1_METHODOLOGY_FLAWS.md F1.
    """
    try:
        db = summary["diagnostic_task_best"]
        cat_t = float(db["category"]["f1"]["mean"])
        nxt_t = float(db["next"]["f1"]["mean"])
    except (KeyError, TypeError):
        return (None, None, None)
    return (_harmonic(cat_t, nxt_t), cat_t, nxt_t)


def _extract_observed(summary: dict[str, Any]) -> dict[str, Any]:
    def get(section: str, key: str) -> float | None:
        try:
            return float(summary[section][key]["mean"])
        except (KeyError, TypeError):
            return None

    def get_std(section: str, key: str) -> float | None:
        try:
            return float(summary[section][key]["std"])
        except (KeyError, TypeError):
            return None

    joint_tb, cat_tb, next_tb = _joint_score_taskbest(summary)

    return {
        "cat_f1": get("category", "f1"),
        "cat_f1_std": get_std("category", "f1"),
        "cat_accuracy": get("category", "accuracy"),
        "next_f1": get("next", "f1"),
        "next_f1_std": get_std("next", "f1"),
        "next_accuracy": get("next", "accuracy"),
        "joint_f1": _joint_score(summary),
        "cat_f1_taskbest": cat_tb,
        "next_f1_taskbest": next_tb,
        "joint_f1_taskbest": joint_tb,
    }


def archive(
    run_dir: Path,
    *,
    phase: str,
    test_id: str,
    claim_ids: list[str] | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise FileNotFoundError(f"run_dir does not exist: {run_dir}")

    summary = _load_summary(run_dir)
    summary_path = run_dir / "summary" / "full_summary.json"
    summary_hash = _sha256(summary_path)

    target_dir = RESULTS_DIR / phase / test_id
    target_dir.mkdir(parents=True, exist_ok=True)

    target_summary = target_dir / "full_summary.json"
    if target_summary.exists() and not overwrite:
        if _sha256(target_summary) == summary_hash:
            print(f"[archive] idempotent: {target_summary} unchanged")
        else:
            raise RuntimeError(
                f"refusing to overwrite differing summary at {target_summary}; pass --overwrite"
            )
    shutil.copy2(summary_path, target_summary)

    manifest_path = _resolve_manifest(run_dir)
    if manifest_path is not None:
        shutil.copy2(manifest_path, target_dir / "manifest.json")

    folds_dir = run_dir / "folds"
    if folds_dir.exists():
        info_files = sorted(folds_dir.glob("fold*_info.json"))
        if info_files:
            fold_dest = target_dir / "folds"
            fold_dest.mkdir(exist_ok=True)
            for f in info_files:
                shutil.copy2(f, fold_dest / f.name)

    observed = _extract_observed(summary)

    metadata = {
        "test_id": test_id,
        "phase": phase,
        "claim_ids": claim_ids or [],
        "run_dir": str(run_dir.relative_to(REPO_ROOT)) if run_dir.is_relative_to(REPO_ROOT) else str(run_dir),
        "summary_sha256": summary_hash,
        "archived_at": utcnow(),
        "observed": observed,
    }

    if manifest_path is not None:
        with manifest_path.open() as fh:
            manifest = json.load(fh)
        metadata["git_commit"] = manifest.get("git_commit")
        metadata["config"] = manifest.get("config")
        metadata["dataset_signatures"] = manifest.get("dataset_signatures")

    with (target_dir / "metadata.json").open("w") as fh:
        json.dump(metadata, fh, indent=2)

    print(f"[archive] {test_id} → {target_dir}")
    print(f"  observed: {observed}")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive a training run into $STUDY_DIR/results/.")
    parser.add_argument("--run-dir", required=True, help="Path to the training run directory.")
    parser.add_argument("--phase", required=True, help="Phase ID (P0..P5).")
    parser.add_argument("--test-id", required=True, help="Test ID used in state.json.")
    parser.add_argument("--claims", nargs="*", default=None, help="Claim IDs this test addresses.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite differing existing archive.")
    parser.add_argument(
        "--no-state", action="store_true",
        help="Skip updating state.json (useful when invoked standalone).",
    )
    args = parser.parse_args()

    metadata = archive(
        Path(args.run_dir),
        phase=args.phase,
        test_id=args.test_id,
        claim_ids=args.claims,
        overwrite=args.overwrite,
    )

    if not args.no_state:
        try:
            with mutate_state() as state:
                existing = (
                    state.get("phases", {})
                    .get(args.phase, {})
                    .get("tests", {})
                    .get(args.test_id, {})
                )
                existing.update(
                    {
                        "status": "archived",
                        "phase": args.phase,
                        "test_id": args.test_id,
                        "results_archive": str((RESULTS_DIR / args.phase / args.test_id).relative_to(REPO_ROOT)),
                        "observed": metadata["observed"],
                        "archived_at": metadata["archived_at"],
                    }
                )
                if args.claims:
                    existing["claim_ids"] = args.claims
                if "git_commit" in metadata:
                    existing["git_commit"] = metadata["git_commit"]
                set_test(state, args.phase, args.test_id, existing)
        except FileNotFoundError as exc:
            print(f"[archive] WARN: state.json missing; skipping state update: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
