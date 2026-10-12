"""Shared stale-`log_T` freshness preflight (CLAUDE.md hard rule).

The per-fold region-transition prior ``region_transition_log_seed{S}_fold{N}.pt`` is
built from the train split of ``input/next_region.parquet``. ``regen_emb_t3.py`` does
NOT rebuild the log_T, so an old log_T silently survives a substrate regen and inflates
reg Acc@10 by **+8 pp (STL) / +12 pp (MTL-disjoint)** (mtl_protocol_fix Phase 2 P5;
FL seed=42 stale-May-6 case). The mandated rule: ``log_T mtime >= next_region.parquet mtime``
before any ``--per-fold-transition-dir`` run.

This was implemented three different ways across the codebase, two of them non-portable:
- ``src/training/runners/mtl_cv.py`` — inline Python ``st_mtime`` guard (C22, portable, OK).
- ``scripts/closing_data/c1_run_g.sh`` — shell ``stat -f %m`` (**BSD/macOS only**; silently
  no-ops the guard on the Linux A40 where ``stat`` needs ``-c %Y``).
- ``scripts/pre_freeze_gates/a4_eval.py`` / ``scripts/p1_region_head_ablation.py`` — **no guard**.

This module is the single portable assert wired into every ``--per-fold-transition-dir``
consumer (pre-freeze audit 2026-06-17, HANDOFF_A40_PREFREEZE §0.3). Python ``st_mtime`` is
cross-platform, so the same code path is correct on the A40 (Linux) and the Mac (BSD).
"""
from __future__ import annotations

from pathlib import Path


class StaleLogTError(ValueError):
    """Raised when a per-fold log_T is older than the substrate parquet it was built from."""


def next_region_parquet_for(per_fold_dir: str | Path) -> Path:
    """The substrate parquet a per-fold log_T directory is built from."""
    return Path(per_fold_dir) / "input" / "next_region.parquet"


def assert_log_t_fresh(
    log_t_path: str | Path,
    parquet_path: str | Path | None = None,
    *,
    state: str | None = None,
    seed: int | None = None,
    n_splits: int | None = None,
) -> None:
    """Assert ``log_t_path`` is at least as new as the substrate parquet it derives from.

    Args:
        log_t_path: a ``region_transition_log_seed{S}_fold{N}.pt`` file (must exist).
        parquet_path: the ``next_region.parquet`` it was built from. Default:
            ``<log_t dir>/input/next_region.parquet`` (matches the layout
            ``compute_region_transition.py`` and ``mtl_cv.py`` assume).
        state / seed: only used to make the rebuild hint actionable.
        n_splits: if given, also assert the log_T payload's stored ``n_splits``
            matches (a different fold count means a different StratifiedGroupKFold
            split → val transitions leak into the prior, the same class of leak as
            a stale mtime). Mirrors the inline guard in ``mtl_cv.py``. Omit to keep
            the cheap mtime-only fast path (no torch load).

    Raises:
        FileNotFoundError: log_T missing.
        StaleLogTError: log_T mtime < parquet mtime, or n_splits mismatch.

    No-op (returns) for the mtime check when the parquet is absent — there is nothing
    to be stale against (mirrors the mtl_cv.py guard, which only fires when present).
    """
    log_t_path = Path(log_t_path)
    if not log_t_path.exists():
        raise FileNotFoundError(
            f"per-fold log_T missing: {log_t_path}. Build with: python "
            f"scripts/compute_region_transition.py --state {state or '<state>'} "
            f"--per-fold --seed {seed if seed is not None else '<seed>'}"
        )
    parquet_path = (
        Path(parquet_path)
        if parquet_path is not None
        else next_region_parquet_for(log_t_path.parent)
    )
    if parquet_path.exists():
        if log_t_path.stat().st_mtime < parquet_path.stat().st_mtime:
            raise StaleLogTError(
                f"Stale per-fold log_T detected: {log_t_path} mtime is older than "
                f"{parquet_path} mtime. The substrate parquet has been regenerated since "
                f"this log_T was built; running would silently leak ~+8 to +12 pp into "
                f"reg Acc@10. Rebuild: python scripts/compute_region_transition.py "
                f"--state {state or '<state>'} --per-fold "
                f"--seed {seed if seed is not None else '<seed>'}"
            )
    if n_splits is not None:
        import torch  # lazy: only when the caller opts into the n_splits check
        payload = torch.load(log_t_path, map_location="cpu", weights_only=False)
        stored = payload.get("n_splits") if isinstance(payload, dict) else None
        if stored is not None and int(stored) != int(n_splits):
            raise StaleLogTError(
                f"per-fold log_T {log_t_path} was built with n_splits={stored} but the "
                f"caller is running at n_splits={n_splits}; the fold split differs, which "
                f"leaks val transitions into the prior. Rebuild for n_splits={n_splits}: "
                f"python scripts/compute_region_transition.py --state {state or '<state>'} "
                f"--per-fold --n-splits {n_splits} --seed {seed if seed is not None else '<seed>'}"
            )


def assert_per_fold_dir_fresh(
    per_fold_dir: str | Path,
    seed: int,
    n_folds: int,
    *,
    state: str | None = None,
    parquet_path: str | Path | None = None,
    check_n_splits: bool = True,
) -> None:
    """Run :func:`assert_log_t_fresh` over all ``n_folds`` seeded log_T files in a dir.

    Convenience wrapper for the seeded layout
    ``<dir>/region_transition_log_seed{seed}_fold{1..n_folds}.pt``. By default also
    verifies each log_T's stored ``n_splits`` matches ``n_folds`` (set
    ``check_n_splits=False`` for the cheap mtime-only check).
    """
    pq = (
        Path(parquet_path)
        if parquet_path is not None
        else next_region_parquet_for(per_fold_dir)
    )
    for fold in range(1, n_folds + 1):
        lt = Path(per_fold_dir) / f"region_transition_log_seed{seed}_fold{fold}.pt"
        assert_log_t_fresh(
            lt, pq, state=state, seed=seed,
            n_splits=n_folds if check_n_splits else None,
        )
