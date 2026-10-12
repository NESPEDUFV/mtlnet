"""CLI entrypoint for MTLnet training (Phase 6).

Usage:
    python scripts/train.py --state florida --engine dgi --epochs 1 --folds 1
    python scripts/train.py --state florida --engine dgi --task category
    python scripts/train.py --state alabama --engine dgi --candidate cgc_equal
    python scripts/train.py --state alabama --engine dgi --mtl-loss static_weight --category-weight 0.25
    python scripts/train.py --config experiments/configs/mtl_hgi_florida.py

⚠  Check2HGI MTL — the bare CLI defaults DO NOT reproduce paper-canonical numbers.
    Three flags must be overridden (each silent default drops one head by 10–30 pp):
      * --mtl-loss            default nash_mtl  →  use static_weight + --category-weight 0.75
      * --cat-head / --reg-head  default preset → use next_gru / next_getnext_hard
      * --task-b-input-type   default checkin   →  use region (B9 spec, task_a stays checkin)
    Full canonical invocation in docs/NORTH_STAR.md §Champion and CLAUDE.md.
    The MTL preset CHECK2HGI_NEXT_REGION sets head_factory + num_classes only —
    NOT the input modality, the loss, or the cat-head. Pass them explicitly.

All imports use final Phase 5 canonical paths.
Notes:
    --folds N: run only the first N folds.  The split structure uses
    max(2, N) splits (StratifiedKFold requires >= 2), but execution stops
    after N folds.  Use this to run a quick smoke test without full CV.
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Ensure repo root and src/ are on sys.path when invoked directly.
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.experiment import DatasetSignature, ExperimentConfig
from configs.globals import CATEGORIES_MAP
from configs.paths import EmbeddingEngine, IoPaths, MTL_CHECK2HGI_ALLOWED_ENGINES
from data.folds import (
    FoldCreator,
    TaskType,
    _RestrictedFoldMapping,
    load_folds,
    rebuild_dataloaders,
)
from tasks import (
    CHECK2HGI_NEXT_REGION,
    LEGACY_CATEGORY_NEXT,
    TaskSet,
    get_preset,
    resolve_task_set,
)
from tasks.presets import list_presets
from training.callbacks import ModelCheckpoint
from utils.seed import seed_everything
from tracking import DatasetHistory, MLHistory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

_VALID_TASKS = ("mtl", "category", "next")
_VALID_ENGINES = [e.value for e in EmbeddingEngine]
_NO_CHECKPOINTS = False
# Multi-fold fan-out (set in main() from --run-id / --per-fold-seed). Default
# None/False → single-process behaviour unchanged. Read in _run_mtl_check2hgi.
_RUN_ID = None
_PER_FOLD_SEED = False


def _make_run_dir(results_path: Path, task: str, config: ExperimentConfig) -> Path:
    """Create a per-invocation run directory and persist its config.

    Returns a unique subdirectory under ``<results_path>/checkpoints/`` named
    ``<task>_<timestamp>`` with the run's ``config.json`` already written
    inside it. The timestamp format is ``%Y%m%d_%H%M%S_<pid>`` so two runs
    of the same task started in the same second cannot collide
    (a sub-second resolution alone would still race; appending the PID
    is a cheap absolute guarantee).

    Saving the config here (before training starts) means the canonical
    per-run config record is preserved even if training crashes mid-fold.
    ``scripts/evaluate.py`` auto-discovers the file via ``parent /
    config.json`` (see ``scripts/evaluate.py`` config-discovery loop).
    """
    import os
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(results_path) / "checkpoints" / f"{task}_{ts}_{os.getpid()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    config.save(run_dir / "config.json")
    return run_dir


def _default_checkpoint_callbacks(run_dir: Path, monitor: str) -> list:
    """Build the default callback list for a runner.

    Wires a single ``ModelCheckpoint`` that watches ``monitor`` (a key in
    ``CallbackContext.metrics``, see ``src/training/callbacks.py``) and
    writes best-so-far weights into ``run_dir``. ``run_dir`` should come
    from :func:`_make_run_dir` so the checkpoints land alongside the
    run's ``config.json``.

    The monitor strings live in this file's call sites and must match
    the keys actually emitted by each runner:
        mtl_cv.py:241-247    → val_f1_next, val_f1_category, val_loss, ...
        category_cv.py / next_cv.py → val_f1, val_loss, val_acc, ...
    A typo here is silently dropped by ModelCheckpoint (`current is None
    → return`) and no checkpoint is ever saved.
    """
    return [
        ModelCheckpoint(
            save_dir=run_dir,
            monitor=monitor,
            mode="max",
            save_best_only=True,
        )
    ]


# ---------------------------------------------------------------------------
# Runner dispatch
# ---------------------------------------------------------------------------

def _run_mtl(config: ExperimentConfig, results_path: Path, fold_results: dict) -> dict:
    from training.runners.mtl_cv import train_with_cross_validation

    # Legacy preset both default to F1, so this is a no-op today — the
    # explicit dict keeps intent readable and prevents silent drift if a
    # slot's primary_metric ever changes.
    from tasks.presets import LEGACY_CATEGORY_NEXT
    task_monitors = {
        LEGACY_CATEGORY_NEXT.task_a.name: LEGACY_CATEGORY_NEXT.task_a.primary_metric.value,
        LEGACY_CATEGORY_NEXT.task_b.name: LEGACY_CATEGORY_NEXT.task_b.primary_metric.value,
    }
    history = MLHistory(
        model_name="MTLNet",
        tasks={"next", "category"},
        num_folds=len(fold_results),
        datasets={
            DatasetHistory(
                raw_data=IoPaths.get_next(config.state, EmbeddingEngine(config.embedding_engine)),
                folds_signature=None,
                description="Next-POI prediction input",
            ),
            DatasetHistory(
                raw_data=IoPaths.get_category(
                    config.state, EmbeddingEngine(config.embedding_engine)
                ),
                folds_signature=None,
                description="Category prediction input",
            ),
        },
        label_map=CATEGORIES_MAP,
        save_path=results_path,
        verbose=True,
        task_monitors=task_monitors,
        min_epoch=int(getattr(config, "min_best_epoch", 0) or 0),
        run_id=_RUN_ID,
    )

    if _NO_CHECKPOINTS:
        cbs = []
    else:
        run_dir = _make_run_dir(results_path, task="mtl", config=config)
        cbs = _default_checkpoint_callbacks(run_dir, monitor="val_f1_category")
    with history:
        results = train_with_cross_validation(
            dataloaders=fold_results,
            history=history,
            config=config,
            results_path=results_path,
            callbacks=cbs,
            per_fold_seed=_PER_FOLD_SEED,
        )

    return results


def _run_mtl_check2hgi(
    config: ExperimentConfig,
    results_path: Path,
    fold_results: dict,
    task_set: TaskSet,
) -> dict:
    """Dispatch MTL runs on the check2HGI preset (or any non-legacy task_set).

    Differs from ``_run_mtl`` on four axes:

    * ``MLHistory.tasks`` uses the preset's slot names
      (``next_category`` / ``next_region`` instead of ``category`` / ``next``).
    * ``DatasetHistory`` points at ``next.parquet`` + ``next_region.parquet``
      (there is no separate category.parquet on this track).
    * ``ModelCheckpoint`` watches ``val_joint_geom_lift`` — the metric emitted
      by ``mtl_cv.py`` alongside ``val_joint_score`` specifically for
      high-cardinality-head setups where macro-F1 is a weak summary.
    * ``train_with_cross_validation`` receives the resolved ``task_set``.
    """
    from training.runners.mtl_cv import train_with_cross_validation

    engine = EmbeddingEngine(config.embedding_engine)
    # Wire each task's primary_metric (declared in the preset) into
    # MLHistory so the per-task BestModelTracker monitors the intended
    # metric. A default monitor='f1' would mismatch heads like
    # CHECK2HGI_NEXT_REGION, which declares Acc@1 for next_region.
    task_monitors = {
        task_set.task_a.name: task_set.task_a.primary_metric.value,
        task_set.task_b.name: task_set.task_b.primary_metric.value,
    }
    history = MLHistory(
        model_name="MTLNet",
        tasks={task_set.task_a.name, task_set.task_b.name},
        num_folds=len(fold_results),
        datasets={
            DatasetHistory(
                raw_data=IoPaths.get_next(config.state, engine),
                folds_signature=None,
                description="next_category input (shared X)",
            ),
            DatasetHistory(
                raw_data=IoPaths.get_next_region(config.state, engine),
                folds_signature=None,
                description="next_region input (shared X, region labels)",
            ),
        },
        label_map=CATEGORIES_MAP,
        save_path=results_path,
        verbose=True,
        task_monitors=task_monitors,
        min_epoch=int(getattr(config, "min_best_epoch", 0) or 0),
        run_id=_RUN_ID,
    )

    if _NO_CHECKPOINTS:
        cbs = []
    else:
        run_dir = _make_run_dir(results_path, task=f"mtl__{task_set.name}", config=config)
        # val_joint_geom_lift = sqrt((acc1_a/maj_a) * (acc1_b/maj_b))
        cbs = _default_checkpoint_callbacks(run_dir, monitor="val_joint_geom_lift")
    with history:
        results = train_with_cross_validation(
            dataloaders=fold_results,
            history=history,
            config=config,
            results_path=results_path,
            callbacks=cbs,
            task_set=task_set,
            per_fold_seed=_PER_FOLD_SEED,
        )

    return results


def _run_single_task(config, results_path, fold_results, *, task, run_cv,
                     model_name, fold_attr, getter, description) -> dict:
    """Shared single-task (category / next) CV launcher. The two paths differ only in
    which ``run_cv`` module, fold attribute, dataset getter, and labels they use."""
    folds = []
    for i in sorted(fold_results):
        # One access per fold: a lazy mapping (--only-fold/--only-folds) builds the fold on
        # each access; for the eager dict both reads return the same object.
        fold_data = getattr(fold_results[i], fold_attr)
        folds.append((fold_data.train.dataloader, fold_data.val.dataloader))
    history = MLHistory(
        model_name=model_name,
        model_type="Single-Task",
        tasks=task,
        num_folds=len(folds),
        datasets={
            DatasetHistory(
                raw_data=str(getter(config.state, EmbeddingEngine(config.embedding_engine))),
                folds_signature=None,
                description=description,
            )
        },
        label_map=CATEGORIES_MAP,
        save_path=str(results_path),
        verbose=True,
        display_report=True,
    )
    if _NO_CHECKPOINTS:
        cbs = []
    else:
        run_dir = _make_run_dir(results_path, task=task, config=config)
        cbs = _default_checkpoint_callbacks(run_dir, monitor="val_f1")
    with history:
        results = run_cv(
            history, folds, config,
            results_path=results_path,
            callbacks=cbs,
        )
    history.display.end_training()
    return results


def _run_category(config: ExperimentConfig, results_path: Path, fold_results: dict) -> dict:
    from training.runners.category_cv import run_cv
    return _run_single_task(
        config, results_path, fold_results, task="category", run_cv=run_cv,
        model_name="Category", fold_attr="category", getter=IoPaths.get_category,
        description="Category prediction input",
    )


def _run_next(config: ExperimentConfig, results_path: Path, fold_results: dict) -> dict:
    from training.runners.next_cv import run_cv
    return _run_single_task(
        config, results_path, fold_results, task="next", run_cv=run_cv,
        model_name="Next", fold_attr="next", getter=IoPaths.get_next,
        description="Next-POI prediction input",
    )


_RUNNERS = {
    "mtl": _run_mtl,
    "category": _run_category,
    "next": _run_next,
}

_TASK_TYPES = {
    "mtl": TaskType.MTL,
    "mtl_check2hgi": TaskType.MTL_CHECK2HGI,
    "category": TaskType.CATEGORY,
    "next": TaskType.NEXT,
}

_DEFAULT_FACTORIES = {
    "mtl": ExperimentConfig.default_mtl,
    "category": ExperimentConfig.default_category,
    "next": ExperimentConfig.default_next,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv=None) -> argparse.Namespace:
    from configs.canon import DEFAULT_CANON, CANON_CHOICES, resolve_canon_argv

    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)

    # --canon: inject a pinned-version recipe bundle BEFORE the user's flags so explicit
    # flags override it (argparse last-wins). MTL-only; no-op under --config or --canon none.
    _pre = argparse.ArgumentParser(add_help=False)
    _pre.add_argument("--canon", default=DEFAULT_CANON)
    _pre.add_argument("--task", default=None)
    _pre.add_argument("--config", default=None)
    _known, _ = _pre.parse_known_args(argv)
    _task = _known.task or "mtl"
    _canon_active = (
        _known.config is None and _task == "mtl" and _known.canon not in (None, "none")
    )
    effective_argv = resolve_canon_argv(_known.canon, argv) if _canon_active else argv

    parser = argparse.ArgumentParser(
        description="Train an MTLnet model via cross-validation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--canon",
        type=str,
        default=DEFAULT_CANON,
        choices=CANON_CHOICES,
        help=(
            "Canonical version recipe bundle to inject for --task mtl (default v18 = delivered "
            "generation, leak-free substrate; v11..v17 pin their own, older substrates; "
            "v16 = champion-G base). Explicit flags override the bundle. Use --canon "
            "v11/v12/v15/v16 to reproduce a prior version, or --canon none for bare smoke "
            "defaults. See docs/results/CANONICAL_VERSIONS.md."
        ),
    )
    parser.add_argument(
        "--state",
        type=str,
        default=None,
        help="Dataset state (e.g. florida, alabama). Required unless --config is provided.",
    )
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        choices=_VALID_ENGINES,
        help="Embedding engine. Required unless --config is provided.",
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        choices=_VALID_TASKS,
        help="Task type to train (mtl / category / next). Defaults to mtl.",
    )
    parser.add_argument(
        "--task-set",
        type=str,
        default=None,
        choices=list_presets(),
        help=(
            "MTL task-set preset. Only used with --task mtl. Defaults to "
            "legacy_category_next (bit-exact with the pre-parameterisation "
            "runner). check2hgi_next_region activates the 2-task "
            "{next_category, next_region} pair on check2HGI embeddings."
        ),
    )
    parser.add_argument(
        "--model",
        dest="model_name",
        type=str,
        default=None,
        help=(
            "Registered model name to use. For Phase 1/2 MTL experiments, "
            "examples are 'mtlnet', 'mtlnet_mmoe', 'mtlnet_cgc', and "
            "'mtlnet_dselectk'."
        ),
    )
    parser.add_argument(
        "--candidate",
        type=str,
        default=None,
        help=(
            "Named MTL candidate from src/ablation/candidates.py, e.g. "
            "equal_weight, baseline_nash, cgc_equal, or cgc_famo. "
            "Explicit --model, --model-param, --mtl-loss, and "
            "--mtl-loss-param flags override candidate defaults."
        ),
    )
    parser.add_argument(
        "--model-param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Override a model parameter. May be passed multiple times. "
            "Values are parsed as JSON when possible, so numbers and booleans "
            "keep their type."
        ),
    )
    parser.add_argument(
        "--mtl-loss",
        type=str,
        default=None,
        help=(
            "Registered MTL loss to use, e.g. nash_mtl, equal_weight, "
            "static_weight, uncertainty_weighting, random_weight, rlw, famo, "
            "fairgrad, bayesagg_mtl, go4align, excess_mtl, stch, or db_mtl. "
            "Unset → trainer default is nash_mtl, which throws ECOS cvxpy solver "
            "errors mid-training and falls back to warm-start (degrades to fixed "
            "weights). NORTH_STAR B9 USES '--mtl-loss static_weight --category-weight 0.75'."
        ),
    )
    parser.add_argument(
        "--mtl-loss-param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Override an MTL loss parameter. May be passed multiple times. "
            "Values are parsed as JSON when possible."
        ),
    )
    parser.add_argument(
        "--category-weight",
        type=float,
        default=None,
        help=(
            "Convenience parameter for --mtl-loss static_weight. "
            "Sets the category loss weight; next weight is 1 - category_weight."
        ),
    )
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=None,
        help="Override gradient accumulation steps.",
    )
    parser.add_argument(
        "--use-class-weights",
        dest="use_class_weights",
        action="store_true",
        default=None,
        help=(
            "Pass class-balanced weights to per-head CrossEntropyLoss. "
            "Recommended for the check2HGI next_region head on Florida "
            "(22%% majority-class region would otherwise dominate the "
            "loss and starve the next_category gradient under NashMTL). "
            "Absent classes get weight 1.0 (see src/training/helpers.py)."
        ),
    )
    parser.add_argument(
        "--no-class-weights",
        dest="use_class_weights",
        action="store_false",
        default=None,
        help="Force-disable class-balanced CE weighting even if the config default is on.",
    )
    # PER-TASK class-weight overrides (MTL only). The legacy
    # --[no-]class-weights flag couples BOTH heads; these override per task and
    # take precedence. None → inherit use_class_weights. Best default: reg OFF
    # (Acc@10), cat ON (macro-F1) — set in ExperimentConfig.default_mtl.
    parser.add_argument("--reg-class-weights", dest="use_class_weights_reg",
                        action="store_true", default=None,
                        help="MTL: class-weight the REG (next_region) CE. Recovers pre-C25 behaviour.")
    parser.add_argument("--no-reg-class-weights", dest="use_class_weights_reg",
                        action="store_false", default=None,
                        help="MTL: unweighted REG CE (the C25 fix; matches the STL Acc@10 ceiling).")
    parser.add_argument("--cat-class-weights", dest="use_class_weights_cat",
                        action="store_true", default=None,
                        help="MTL: class-weight the CAT (next_category) CE (macro-F1 benefits).")
    parser.add_argument("--no-cat-class-weights", dest="use_class_weights_cat",
                        action="store_false", default=None,
                        help="MTL: unweighted CAT CE.")
    # --- STL loss calibration (next_cv.py cat tune; leak-free, train-only stats) ---
    parser.add_argument("--focal-gamma", type=float, default=0.0,
                        help="T1.4: focal focusing parameter (>0 enables focal). STL cat lever.")
    parser.add_argument("--logit-adjust-tau", type=float, default=0.0,
                        help="T1.4: Menon ICLR'21 logit-adjustment temperature (>0 adds "
                             "tau*log P_train(y) to logits). Macro-F1-consistent; STL cat lever.")
    parser.add_argument("--cat-label-smoothing", type=float, default=0.0,
                        help="T1.4: label smoothing for the STL next-cat criterion.")
    parser.add_argument("--tail-loss", choices=["none", "balanced", "cb", "ldam"], default="none",
                        help="T1.4: imbalance handling for the STL criterion. 'balanced' = "
                             "sklearn balanced weights (== the T1.1 cat ceiling), 'cb' = "
                             "Class-Balanced, 'ldam' = LDAM margins.")
    parser.add_argument("--cb-beta", type=float, default=0.999, help="T1.4: CB beta (with --tail-loss cb).")
    parser.add_argument("--ldam-max-margin", type=float, default=0.5, help="T1.4: LDAM max margin.")
    parser.add_argument("--ldam-scale", type=float, default=30.0, help="T1.4: LDAM logit scale.")
    parser.add_argument(
        "--task-a-input-type",
        type=str,
        choices=("checkin", "region", "concat"),
        default="checkin",
        help=(
            "Check2HGI MTL only: input modality for task-a slot (next_category). "
            "'checkin' (default, bit-exact-legacy) = 9-window of check-in emb; "
            "'region' = 9-window of region emb via placeid→region lookup; "
            "'concat' = [checkin ⊕ region] stacked on feature axis. Used by the "
            "P4 per-task-modality ablation (CH03)."
        ),
    )
    parser.add_argument(
        "--task-b-input-type",
        type=str,
        choices=("checkin", "region", "concat"),
        default="checkin",
        help=(
            "Check2HGI MTL only: input modality for task-b slot (next_region). "
            "NORTH_STAR B9 SPECIFIES 'region' (per docs/NORTH_STAR.md §Champion). "
            "The default 'checkin' is a SMOKE-MODE convenience and produces ~28%% "
            "reg Acc@10 at AL (vs ~50%% canonical). Always pass "
            "'--task-b-input-type region' for any benchmark comparable to "
            "RESULTS_TABLE.md §0.1. P1 showed region-emb input is the right "
            "modality for the region head (53%% Acc@10 vs 20%% on check-in)."
        ),
    )
    parser.add_argument(
        "--next-target",
        type=str,
        choices=("next_category", "next_poi"),
        default=None,
        help="Target interface marker for next-task experiments.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed override for reproducibility checks.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Number of training epochs. Overrides config value.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Training batch size. Overrides config value.",
    )
    parser.add_argument(
        "--max-lr",
        type=float,
        default=None,
        help="OneCycleLR max_lr. Overrides config value. STL next uses 0.01, STL region GRU 0.003, MTL default 0.001.",
    )
    parser.add_argument(
        "--scheduler",
        type=str,
        choices=("onecycle", "constant", "cosine", "warmup_constant",
                 "reg_head_warmup_decay"),
        default=None,
        help=(
            "LR scheduler type. 'onecycle' (default) preserves legacy "
            "behaviour. 'constant' holds --max-lr fixed (disentangles "
            "'more epochs' from 'stretched OneCycleLR schedule', F45). "
            "'cosine' decays from --max-lr to 0 without warmup. "
            "'warmup_constant' (F48-H2) linearly warms LR over "
            "--pct-start of total steps, then holds --max-lr forever. "
            "'reg_head_warmup_decay' (F50 F64/B2) applies a ramp-hold-decay "
            "multiplier ONLY to reg_head + alpha_no_wd groups (others stay "
            "at base LR); requires per-head optimizer."
        ),
    )
    parser.add_argument(
        "--reg-head-warmup-decay-peak-mult",
        dest="reg_head_warmup_decay_peak_mult",
        type=float,
        default=10.0,
        help=(
            "F64/B2 — peak LR multiplier for reg_head during warmup-decay "
            "schedule (default 10.0 → reg_head LR peaks at 10× its base)."
        ),
    )
    parser.add_argument(
        "--reg-head-warmup-decay-warmup-epochs",
        dest="reg_head_warmup_decay_warmup_epochs",
        type=int,
        default=5,
        help=(
            "F64/B2 — epochs of linear ramp-up for reg_head LR (default 5)."
        ),
    )
    parser.add_argument(
        "--reg-head-warmup-decay-plateau-epochs",
        dest="reg_head_warmup_decay_plateau_epochs",
        type=int,
        default=15,
        help=(
            "F64/B2 — last epoch of the peak-LR plateau (default 15). "
            "Linear decay from this epoch to total --epochs back to base."
        ),
    )
    parser.add_argument(
        "--joint-loader-strategy",
        dest="joint_loader_strategy",
        type=str,
        choices=("max_size_cycle", "min_size_truncate"),
        default=None,
        help=(
            "F65 — joint-dataloader cycling strategy. 'max_size_cycle' "
            "(legacy default) cycles the shorter loader to match longer. "
            "'min_size_truncate' stops at the shortest loader's end with no "
            "cycling — tests whether the F50 D5 reg-saturation observation "
            "is driven by the cycle pattern."
        ),
    )
    parser.add_argument(
        "--pct-start",
        type=float,
        default=None,
        help=(
            "OneCycleLR pct_start (warmup fraction). PyTorch default 0.3. "
            "Smaller values push peak LR earlier and leave more epochs in "
            "annealing. Used by F46."
        ),
    )
    parser.add_argument(
        "--cat-lr",
        type=float,
        default=None,
        help=(
            "Per-head LR (F48-H3) — LR for the cat encoder + cat head "
            "param group. When --cat-lr, --reg-lr and --shared-lr are "
            "ALL set, the optimizer is built with three distinct param "
            "groups and --max-lr is ignored. Pair with --scheduler "
            "constant so the per-group LRs survive."
        ),
    )
    parser.add_argument(
        "--reg-lr",
        type=float,
        default=None,
        help="Per-head LR — LR for the next encoder + next head group (F48-H3).",
    )
    parser.add_argument(
        "--shared-lr",
        type=float,
        default=None,
        help=(
            "Per-head LR — LR for the cross-attn + final_ln group (F48-H3). "
            "Default recommendation: shared_lr = reg_lr (cross-attn is in "
            "the reg gradient path; throttling it reproduces F44 not H3)."
        ),
    )
    parser.add_argument(
        "--freeze-cat-stream",
        dest="freeze_cat_stream",
        action="store_true",
        default=False,
        help=(
            "F49 encoder-frozen λ=0 isolation: set requires_grad=False on "
            "category_encoder + category_poi so the cat encoder cannot "
            "co-adapt as a reg-helper via cross-attention K/V. Requires "
            "--mtl-loss static_weight --category-weight 0.0 (the cat-loss "
            "must be zero or the configuration is incoherent). See "
            "docs/findings/F49_LAMBDA0_DECOMPOSITION_GAP.md."
        ),
    )
    parser.add_argument(
        "--freeze-reg-stream",
        dest="freeze_reg_stream",
        action="store_true",
        default=False,
        help=(
            "W6 category-side encoder-isolation probe (MIRROR of "
            "--freeze-cat-stream): set requires_grad=False on next_encoder "
            "+ next_poi so the region stream cannot co-adapt as a cat-helper "
            "via cross-attention K/V. Requires --mtl-loss static_weight "
            "--category-weight 1.0 (reg-loss must be zero). Tests whether the "
            "joint category win is the shared trunk (architecture) or "
            "region->category transfer. See RESULTS_BOARD / mobiwac W6."
        ),
    )
    parser.add_argument(
        "--freeze-cat-after-epoch",
        dest="freeze_cat_after_epoch",
        type=int,
        default=None,
        metavar="N",
        help=(
            "F50 P3 (warmup-then-freeze): train cat side normally for the "
            "first N epochs, then freeze category_encoder + category_poi "
            "from epoch N onward. Reg + shared keep training. Tests whether "
            "continued cat-encoder co-adaptation (per F49 Layer 2) is "
            "hurting reg at FL. Unlike --freeze-cat-stream this does NOT "
            "require --category-weight 0.0; cat is trained for the warmup "
            "window then frozen. See `MTL_FLAWS_AND_FIXES.md` §3 H1.5."
        ),
    )
    parser.add_argument(
        "--alternating-optimizer-step",
        dest="alternating_optimizer_step",
        action="store_true",
        default=False,
        help=(
            "F50 P4 (per-batch alternating-SGD): even batches update cat-side "
            "params from L_cat only; odd batches update reg-side params from "
            "L_reg only. Shared params see one task's gradient signal per "
            "batch (alternating). Tests 'does fine-grained alternation prevent "
            "shared backbone hijacking?'. Requires --mtl-loss static_weight "
            "and --gradient-accumulation-steps 1. See MTL_FLAWS_AND_FIXES.md §3 H1.5."
        ),
    )
    parser.add_argument(
        "--reg-encoder-lr",
        dest="reg_encoder_lr",
        type=float,
        default=None,
        metavar="LR",
        help=(
            "F50 D3 (per-encoder LR split): separate LR for next_encoder, "
            "splitting it out of the reg group. Default reuses --reg-lr. Tests "
            "mechanism α — the reg encoder is under-trained at FL because "
            "loss-side cat_weight=0.75 scaling effectively shrinks reg "
            "gradient by 4x. Suggested: 1e-2 or 3e-2 (10x reg_lr) to "
            "compensate for the loss-side scaling."
        ),
    )
    parser.add_argument(
        "--reg-head-lr",
        dest="reg_head_lr",
        type=float,
        default=None,
        metavar="LR",
        help=(
            "F50 D6 (reg head LR split): separate LR for next_poi (where α "
            "scalar lives in next_getnext_hard). Tests whether α growth is "
            "the bottleneck (D1 + cat_weight sweep show STL α=0 ≈ MTL ≈ 73 pp; "
            "STL α-trainable = 82.44 pp; the prior is functionally disabled "
            "in MTL). Suggested: 3e-2 (10x reg_lr) to wake up α."
        ),
    )
    parser.add_argument(
        "--reg-head-param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override region head hyperparameter (task_b_head_params) in the MTL task_set. Repeatable. E.g. --reg-head-param hidden_dim=512 --reg-head-param num_layers=3",
    )
    parser.add_argument(
        "--per-fold-transition-dir",
        dest="per_fold_transition_dir",
        type=str,
        default=None,
        metavar="DIR",
        help=(
            "AUDIT-C4 fix: directory containing per-fold transition matrices "
            "(``region_transition_log_fold{1..k}.pt``). When set, the trainer "
            "swaps the static ``transition_path`` in next-head params for the "
            "fold-specific file each fold, eliminating val->train leakage in "
            "the GETNext graph prior. Build with: "
            "python scripts/compute_region_transition.py --state STATE --per-fold"
        ),
    )
    parser.add_argument(
        "--min-best-epoch",
        dest="min_best_epoch",
        type=int,
        default=0,
        metavar="N",
        help=(
            "F50 B1: earliest epoch (0-indexed) eligible to be selected as "
            "best by the per-task BestModelTracker. Defends against "
            "init-artifact peaks (e.g. GETNext alpha_init=2.0 makes ep 1 "
            "the prior alone, not learned signal). Set to 2 or 3 to skip "
            "the init window. Default 0 = legacy behaviour."
        ),
    )
    parser.add_argument(
        "--checkpoint-selector",
        dest="checkpoint_selector",
        type=str,
        default="geom_simple",
        choices=["geom_simple", "joint_f1_mean", "geom_lift"],
        help=(
            "C21 (mtl-protocol-fix): which scalar gates the single joint MTL "
            "checkpoint per epoch. DEFAULT 'geom_simple' = sqrt(cat_macroF1 * "
            "reg_Acc@10) — selects on the reported headline metrics (cat 'f1', "
            "reg 'top10_acc_indist'), scale-coherent, no majority normalization; "
            "recovered +5.62pp reg Acc@10 vs the v11 selector (docs/CONCERNS.md "
            "§C21). 'joint_f1_mean' = 0.5*(cat_f1+reg_f1) reproduces the v11 "
            "paper-canon LEGACY (broken) selector — use ONLY for v11 reproduction. "
            "'geom_lift' = the interim acc1/majority-lift geometric mean. "
            "MTL only; ignored for STL tasks."
        ),
    )
    parser.add_argument(
        "--alpha-no-weight-decay",
        dest="alpha_no_weight_decay",
        action="store_true",
        help=(
            "F50 B9: exempt the learnable alpha scalar (next_getnext_hard* "
            "head's graph-prior weight) from AdamW weight decay. WD=0.05 "
            "applies a constant pull-toward-zero every step, fighting the "
            "gradient-driven alpha growth needed to reach STL's ep 17-20 "
            "regime (alpha ~ 2.0). Requires per-head LR mode "
            "(--cat-lr/--reg-lr/--shared-lr)."
        ),
    )
    parser.add_argument(
        "--reg-freeze-at-epoch",
        dest="reg_freeze_at_epoch",
        type=int,
        default=None,
        metavar="N",
        help=(
            "substrate-protocol-cleanup Tier C2 — freeze the reg-side stream "
            "(next_encoder + next_poi) at the start of epoch N and zero the "
            "reg loss contribution from that epoch onward. Cat continues "
            "training joint with the now-fixed reg representation. Tests "
            "whether locking in the reg ep ~2-4 peak while letting cat "
            "improve yields a better joint deploy outcome. Mirror of "
            "--freeze-cat-after-epoch but inverted. Requires --task mtl. "
            "See docs/studies/substrate-protocol-cleanup/INDEX.md §C2."
        ),
    )
    parser.add_argument(
        "--zero-cat-kv",
        dest="zero_cat_kv",
        action="store_true",
        default=False,
        help=(
            "substrate-protocol-cleanup Tier C3 — forward-only ablation that "
            "zeroes the cat-stream K/V tensors before cross-attention's "
            "softmax(Q K^T) V step in mtlnet_crossattn._CrossAttnBlock. "
            "The reg stream's Q still queries, but the cat-side K/V "
            "contribute nothing to reg's update through the cross channel. "
            "Tests P4's residual capacity-stealing hypothesis. Projection "
            "weights are NOT zeroed (reversible by flag). Requires "
            "--model mtlnet_crossattn. See INDEX.md §C3."
        ),
    )
    parser.add_argument(
        "--save-task-best-snapshots",
        dest="save_task_best_snapshots",
        action="store_true",
        default=False,
        help=(
            "substrate-protocol-cleanup Tier C1 — save three full MTL "
            "checkpoints per fold (one per per-task-best epoch + one per "
            "joint-best epoch): "
            "fold{N}_cat_best.pt, fold{N}_reg_best.pt, fold{N}_joint_best.pt "
            "under <results>/task_best_snapshots/. Opt-in; the existing "
            "single-best path is untouched. Use scripts/route_task_best.py "
            "to score the three checkpoints on the held-out fold. Requires "
            "--task mtl. See INDEX.md §C1."
        ),
    )
    parser.add_argument(
        "--log-t-kd-weight",
        dest="log_t_kd_weight",
        type=float,
        default=None,
        metavar="W",
        help=(
            "substrate-protocol-cleanup Tier A1 / mtl-protocol-fix Phase 3 "
            "§4.5 — KL distillation weight from the per-fold log_T into the "
            "reg head output. Adds L_reg += W · τ² · KL(softmax(reg_logits/τ) "
            "|| softmax(log_T[last_region_idx]/τ)) to the reg loss before "
            "the MTL combiner. **v12 DEFAULT (2026-05-30): 0.2 ON, scoped to "
            "--task mtl --task-set check2hgi_next_region only.** Pass 0.0 for "
            "the v11 paper-canon (no-KD) reproduction. Tier A1 PROMOTED "
            "multi-seed n=20 at AL/AZ (W=0.2: +2.27/+4.91 pp disjoint reg, "
            "p=9.54e-07, leak-clean); FL/CA/TX seed=42 pilot (+2.4/+1.4/+1.7 "
            "pp). See docs/results/CANONICAL_VERSIONS.md. Requires "
            "--reg-head with a log_T-aware head (next_getnext_hard, "
            "next_stan_flow, next_getnext) AND --per-fold-transition-dir "
            "so the head's buffered log_T is the train-only per-fold prior. "
            "See docs/results/mtl_protocol_fix/phase3_rank1_findings.md."
        ),
    )
    parser.add_argument(
        "--loss-scale-norm",
        dest="loss_scale_norm",
        action="store_true",
        default=False,
        help=(
            "T4.0a (mtl_improvement) — divide each task's CE by "
            "log(num_classes) BEFORE the MTL combiner, decoupling the built-in "
            "~4.7x CE-magnitude gap (ln(n_regions)≈8.5 reg vs ln(7)≈1.95 cat) "
            "from the inter-task weight. MTL-only; default off (champion G + "
            "all --canon versions untouched)."
        ),
    )
    parser.add_argument(
        "--aligned-pairing",
        dest="aligned_pairing",
        action="store_true",
        default=False,
        help=(
            "G0.1 (closing_data P0 gate) — drive the Check2HGI MTL cat+reg TRAIN "
            "loaders from ONE shared per-epoch permutation so cat-window k trains "
            "paired with reg-window k (same window) instead of independent shuffles "
            "(random cross-task pairing). MTL-check2hgi only; default off (champion "
            "G untouched). Requires KD off + alpha frozen (the champion-G recipe)."
        ),
    )
    parser.add_argument(
        "--log-t-kd-gate",
        dest="log_t_kd_gate",
        type=str,
        default=None,
        choices=["none", "coverage_max", "coverage_entropy"],
        help=(
            "R5 (mtl_frontier) — per-instance gating of the log_T-KD weight. "
            "Redistributes the (batch-mean-fixed) KD weight across check-ins by "
            "Markov-coverage of the sample's last-region log_T row: 'coverage_max' "
            "(teacher max-prob) / 'coverage_entropy' (normalized 1-H) upweight "
            "peaked (Markov-binding) samples and downweight flat ones, mean-1 "
            "normalized per batch so the TOTAL KD budget == global-W. Tests "
            "redistribution, not strength. Requires --log-t-kd-weight > 0. "
            "Default 'none' = global W (bit-identical). MTL-only; champion G "
            "untouched. See docs/studies/mtl_frontier/FINDINGS.md §R5."
        ),
    )
    parser.add_argument(
        "--log-t-kd-tau",
        dest="log_t_kd_tau",
        type=float,
        default=None,
        metavar="TAU",
        help=(
            "substrate-protocol-cleanup Tier A1 — temperature τ for the "
            "log_T KD term. Standard distillation form with τ² scaling "
            "preserves gradient magnitude. Default 1.0 (sharp teacher = "
            "the raw log_T row already in log-prob space). Phase 3 used "
            "τ=1.0 throughout; no τ sweep was performed. Higher τ softens "
            "the prior, lower sharpens it."
        ),
    )
    parser.add_argument(
        "--log-c-kd-weight",
        dest="log_c_kd_weight",
        type=float,
        default=None,
        metavar="W",
        help=(
            "R1 (mtl_frontier) — ESMM co-location KD weight. Adds a SECOND "
            "distillation term to the reg loss whose teacher is the "
            "cat-marginalized region prior prior(reg)=Σ_c P(reg|c)·P̂(c) "
            "(P̂=softmax(cat_logits).detach()), on top of any --log-t-kd-weight. "
            "Requires --reg-head next_stan_flow_dualtower with a buffered log_C "
            "(per-fold region_colocation_log_seed{S}_fold{N}.pt at "
            "--per-fold-transition-dir; build via "
            "scripts/compute_region_colocation.py --per-fold). Default 0.0 = off."
        ),
    )
    parser.add_argument(
        "--log-c-kd-tau",
        dest="log_c_kd_tau",
        type=float,
        default=None,
        metavar="TAU",
        help=(
            "R1 — temperature τ for the log_C co-location KD term (same "
            "Hinton τ² form as --log-t-kd-tau). Default 1.0."
        ),
    )
    parser.add_argument(
        "--log-c-kd-warmup-epochs", dest="log_c_kd_warmup_epochs", type=int,
        default=None, metavar="N",
        help="R3 — apply BOTH co-location KD arms only from epoch N on (CrossDistil "
             "warm-up; teacher is noisy early). Default 0 = always on.",
    )
    parser.add_argument(
        "--log-c-kd-ec-lambda", dest="log_c_kd_ec_lambda", type=float,
        default=None, metavar="L",
        help="R3 — CrossDistil error-correction: blend the soft co-location teacher "
             "with the ground-truth one-hot, teacher*=(1-L)·teacher+L·onehot(y). "
             "0=pure soft (R1).",
    )
    parser.add_argument(
        "--cat-kd-weight", dest="cat_kd_weight", type=float, default=None, metavar="W",
        help="R3 reverse arm — distill the reg-implied category prior "
             "Σ_r P(cat|r)·P̂_reg(r) into the CAT head. Default 0.0 = off.",
    )
    parser.add_argument(
        "--cat-kd-tau", dest="cat_kd_tau", type=float, default=None, metavar="TAU",
        help="R3 — temperature τ for the reverse cat-KD term. Default 1.0.",
    )
    parser.add_argument(
        "--alpha-frozen-until-epoch",
        dest="alpha_frozen_until_epoch",
        type=int,
        default=None,
        metavar="N",
        help=(
            "F50 B4: freeze the learnable alpha scalar at its init value "
            "for the first N epochs, then unfreeze. Lets the cat task "
            "stabilise at the un-amplified prior magnitude before alpha "
            "starts growing and disturbing the shared backbone. Default "
            "(unset/0) = alpha trainable from epoch 0 (legacy)."
        ),
    )
    parser.add_argument(
        "--reg-head",
        type=str,
        default=None,
        help=(
            "Override the region-task head factory (task_b.head_factory) in the MTL task_set. "
            "Default preserves the preset's choice (next_gru for CHECK2HGI_NEXT_REGION). "
            "NORTH_STAR B9 USES 'next_getnext_hard' (STAN-Flow with α·log_T prior). "
            "The preset default 'next_gru' is the P1 region-head ablation winner but is "
            "NOT the paper-canonical reg head. See docs/NORTH_STAR.md §Champion."
        ),
    )
    parser.add_argument(
        "--cat-head-param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override category head hyperparameter (task_a_head_params) in the MTL task_set. Repeatable. Symmetric to --reg-head-param.",
    )
    parser.add_argument(
        "--cat-head",
        type=str,
        default=None,
        help=(
            "Override the category-task head factory (task_a.head_factory) in the MTL task_set. "
            "Default preserves the preset's choice (None → MTLnet's CategoryHeadTransformer / next_mtl). "
            "NORTH_STAR B9 USES 'next_gru' per F27 cat-head ablation. See docs/NORTH_STAR.md §Champion. "
            "Use e.g. --cat-head next_gru or --cat-head category_ensemble for the F27 cat-head ablation."
        ),
    )
    parser.add_argument(
        "--folds",
        type=int,
        default=None,
        help=(
            "Number of CV folds to RUN (not the split count). "
            "Use 1 for a quick smoke test. "
            "The split structure uses max(2, N) splits. "
            "⚠ When combined with --per-fold-transition-dir, N < 5 will be "
            "rejected by mtl_cv.py's n_splits guard unless the per-fold log_T "
            "was rebuilt at the matching n_splits. Rebuild via: "
            "`python scripts/compute_region_transition.py --state <S> "
            "--per-fold --n-splits max(2,N) --seed <seed>`. See "
            "docs/studies/mtl-exploration/LEAK_BLAST_RADIUS_AUDIT.md."
        ),
    )
    parser.add_argument(
        "--only-fold",
        type=int,
        default=None,
        help=(
            "[ONLY-FOLD] Run EXACTLY fold k (0-indexed) of the canonical n_splits=5 split. "
            "For scoring per-(state,seed,fold) substrate baselines (B1 CTLE / B2a POI2Vec / "
            "B2b skipgram) leak-cleanly against the matching 5-split seeded log_T — the "
            "single-fold substrate must be evaluated on exactly its own fold of the 5-split, "
            "which --folds N (n_splits=max(2,N)) cannot express. Mutually exclusive with "
            "--folds. Default None => no behavior change (the champion never passes it)."
        ),
    )
    parser.add_argument(
        "--only-folds",
        type=str,
        default=None,
        help=(
            "[MULTI-FOLD] Run a SUBSET of the canonical 5-split, comma-separated, 0-indexed "
            "(e.g. '2,3' or '0'). Like --only-fold but for several folds at once; forces the "
            "5-split + matching per-fold seeded log_T. The fan-out building block: launch one "
            "process per fold, all sharing a --run-id, then aggregate. Mutually exclusive with "
            "--folds / --only-fold."
        ),
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help=(
            "[MULTI-FOLD] Fix the results-rundir leaf to this name so N fold-processes (each "
            "--only-folds k) write into ONE execution dir for clean aggregation, instead of each "
            "inventing its own timestamped dir. Implies --per-fold-seed (the fan-out must be "
            "fold-order-independent). NB: the rundir leaf is lowercased. Default None => the "
            "legacy <ts>_<pid> rundir."
        ),
    )
    parser.add_argument(
        "--per-fold-seed",
        dest="per_fold_seed",
        action="store_true",
        default=False,
        help=(
            "[MULTI-FOLD] Reseed from (seed + fold_id) before each fold so fold k is reproducible "
            "regardless of execution order — a fanned-out fold equals its place in a sequential "
            "run. Auto-enabled by --run-id. Default off => byte-identical single-global-seed runs."
        ),
    )
    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=None,
        help=(
            "Embedding dimension. Overrides model_params feature_size/input_dim/embed_dim. "
            "Required for engines with non-default dimensions (e.g. fusion=128)."
        ),
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help=(
            "Path to an experiment config file that exports config() -> ExperimentConfig. "
            "CLI flags override values from the file."
        ),
    )
    parser.add_argument(
        "--replace-model-params",
        action="store_true",
        default=False,
        help=(
            "When set, --model-param values REPLACE the default model_params "
            "instead of merging. Useful when switching to a model with a "
            "different constructor signature."
        ),
    )
    parser.add_argument(
        "--folds-path",
        type=str,
        default=None,
        help=(
            "Path to a frozen fold_indices_{task}.pt file (see "
            "scripts/study/freeze_folds.py). When omitted, the canonical "
            "path output/{engine}/{state}/folds/fold_indices_{task}.pt is "
            "auto-loaded if present and its input signatures still match; "
            "otherwise folds are generated from scratch and a warning is "
            "logged."
        ),
    )
    parser.add_argument(
        "--no-folds-cache",
        action="store_true",
        default=False,
        help="Ignore any cached folds and always regenerate. Use only for debugging.",
    )
    parser.add_argument(
        "--no-checkpoints",
        action="store_true",
        default=False,
        help="Skip saving model checkpoints. Saves disk for disposable runs (screen, promote).",
    )
    parser.add_argument(
        "--tf32",
        action="store_true",
        default=False,
        help=(
            "CUDA: enable TF32 for fp32 matmul + cudnn (no-op on MPS/CPU). "
            "Trades small numeric drift on non-autocast paths for ~5-10%% "
            "throughput. Off by default to keep parity with NORTH_STAR."
        ),
    )
    parser.add_argument(
        "--weight-decay",
        dest="weight_decay",
        type=float,
        default=None,
        help="AdamW weight_decay override (F51 Tier 3).",
    )
    parser.add_argument(
        "--adam-eps",
        dest="adam_eps",
        type=float,
        default=None,
        help="AdamW eps override — config field optimizer_eps (F51 Tier 3).",
    )
    parser.add_argument(
        "--adam-beta2",
        dest="adam_beta2",
        type=float,
        default=None,
        help="AdamW beta2 override (default 0.999). Lower (~0.95) is a "
             "standard large-batch/bs8192 stabilizer — config optimizer_beta2.",
    )
    parser.add_argument(
        "--onecycle-per-head-lr",
        dest="onecycle_per_head_lr",
        action="store_true",
        help="Make --cat-lr/--reg-lr/--shared-lr actually apply under --scheduler onecycle "
             "(sets MTL_ONECYCLE_PER_HEAD_LR=1: per-group OneCycle max_lr). Without it the "
             "per-head LRs are INERT under onecycle (scalar max_lr broadcasts to all groups). "
             "Part of the v17 candidate recipe (bs8192 + effective cat-lr 1e-3).",
    )
    parser.add_argument(
        "--max-grad-norm",
        dest="max_grad_norm",
        type=float,
        default=None,
        help="Gradient clipping max norm. Set to 0 (or negative) to disable (F51 Tier 3).",
    )
    parser.add_argument(
        "--eta-min",
        dest="eta_min",
        type=float,
        default=None,
        help="CosineAnnealingLR eta_min floor LR (F51 Tier 3).",
    )
    parser.add_argument(
        "--compile",
        dest="compile_model",
        action="store_true",
        default=False,
        help=(
            "Wrap the model in torch.compile (CUDA only). First fold "
            "incurs compilation overhead; steady-state speedup ~1.2-1.5x. "
            "May introduce numeric drift vs NORTH_STAR — exploratory."
        ),
    )
    parser.add_argument(
        "--profile",
        dest="profile_run",
        action="store_true",
        default=False,
        help=(
            "Enable the ephemeral run profiler/audit (src/training/profiling.py): per-fold "
            "section timing, throughput, peak GPU mem, torch.compile recompiles, GPU util, and "
            "pain-point flags (bottlenecks) — logged at fold/run end, NOT persisted into results. "
            "Set MTL_PROFILE_JSON=<path> to also dump the report. Numerically inert."
        ),
    )
    args = parser.parse_args(effective_argv)
    # --onecycle-per-head-lr drives the env gate read in setup_scheduler (helpers.py); set it here so
    # the canon-bundled recipe (v17) is self-contained and does not need an env var passed separately.
    if getattr(args, "onecycle_per_head_lr", False):
        import os as _os_phlr
        _os_phlr.environ["MTL_ONECYCLE_PER_HEAD_LR"] = "1"
    # Record whether the canon bundle was actually injected (for the manifest / auto-derivations).
    args._canon_active = bool(_canon_active)
    if not _canon_active:
        args.canon = "none"
    return args


def _coerce_cli_value(raw: str):
    """Parse CLI override values while keeping strings usable.

    Python-style literals are accepted alongside JSON: ``json.loads`` rejects
    ``True``/``False``/``None``, so without this mapping ``KEY=False`` stayed
    the string ``"False"`` — and ``bool("False") is True``, silently inverting
    every boolean head/model/loss param passed in Python style (2026-06-12
    code audit, P1-F).
    """
    _PY_LITERALS = {"True": True, "False": False, "None": None}
    if raw in _PY_LITERALS:
        return _PY_LITERALS[raw]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _parse_key_value_overrides(items: list[str], option_name: str) -> dict:
    overrides = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"{option_name} expects KEY=VALUE, got {item!r}")
        key, raw_value = item.split("=", 1)
        if not key:
            raise ValueError(f"{option_name} requires a non-empty key")
        overrides[key] = _coerce_cli_value(raw_value)
    return overrides


def _apply_cli_overrides(
    config: ExperimentConfig,
    args: argparse.Namespace,
) -> ExperimentConfig:
    """Apply CLI overrides without creating folds or touching the filesystem."""
    if args.state is not None:
        config = dataclasses.replace(config, state=args.state)
    if args.engine is not None:
        config = dataclasses.replace(config, embedding_engine=args.engine)
    if args.task is not None and args.task != config.task_type:
        config = dataclasses.replace(config, task_type=args.task)
    if args.epochs is not None:
        config = dataclasses.replace(config, epochs=args.epochs)
    if args.batch_size is not None:
        if args.batch_size <= 0:
            raise ValueError("--batch-size must be > 0")
        config = dataclasses.replace(config, batch_size=args.batch_size)
    if args.max_lr is not None:
        if args.max_lr <= 0:
            raise ValueError("--max-lr must be > 0")
        config = dataclasses.replace(config, max_lr=args.max_lr)
    if args.scheduler is not None:
        config = dataclasses.replace(config, scheduler_type=args.scheduler)
    if args.pct_start is not None:
        if not (0 < args.pct_start < 1):
            raise ValueError("--pct-start must be in (0, 1)")
        config = dataclasses.replace(config, pct_start=args.pct_start)
    # reg_head warmup-decay schedule params (only consumed when
    # scheduler_type == "reg_head_warmup_decay"). Always stamp on config so
    # the runner reads via getattr without needing presence checks.
    config = dataclasses.replace(
        config,
        reg_head_warmup_decay_peak_mult=float(args.reg_head_warmup_decay_peak_mult),
        reg_head_warmup_decay_warmup_epochs=int(args.reg_head_warmup_decay_warmup_epochs),
        reg_head_warmup_decay_plateau_epochs=int(args.reg_head_warmup_decay_plateau_epochs),
    )
    if args.joint_loader_strategy is not None:
        config = dataclasses.replace(
            config, joint_loader_strategy=args.joint_loader_strategy)
    # Per-head LR. Validate as a triple — partial sets are an error since
    # the runner only switches to per-head mode when all three are present.
    _per_head_set = {
        "cat_lr": args.cat_lr,
        "reg_lr": args.reg_lr,
        "shared_lr": args.shared_lr,
    }
    _set_keys = [k for k, v in _per_head_set.items() if v is not None]
    if _set_keys and len(_set_keys) != 3:
        raise ValueError(
            f"--cat-lr / --reg-lr / --shared-lr must all be set together, "
            f"got only {_set_keys}. Per-head LR is an all-or-nothing mode."
        )
    if len(_set_keys) == 3:
        for k, v in _per_head_set.items():
            if v <= 0:
                raise ValueError(f"--{k.replace('_', '-')} must be > 0")
        config = dataclasses.replace(
            config,
            cat_lr=args.cat_lr, reg_lr=args.reg_lr, shared_lr=args.shared_lr,
        )
    if args.next_target is not None:
        config = dataclasses.replace(config, next_target=args.next_target)
    if args.seed is not None:
        config = dataclasses.replace(config, seed=args.seed)
    if args.gradient_accumulation_steps is not None:
        if args.gradient_accumulation_steps <= 0:
            raise ValueError("--gradient-accumulation-steps must be > 0")
        config = dataclasses.replace(
            config,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
        )
    if args.use_class_weights is not None:
        config = dataclasses.replace(config, use_class_weights=args.use_class_weights)
    # Per-task class-weight overrides (take precedence over --[no-]class-weights).
    if getattr(args, "use_class_weights_reg", None) is not None:
        config = dataclasses.replace(config, use_class_weights_reg=args.use_class_weights_reg)
    if getattr(args, "use_class_weights_cat", None) is not None:
        config = dataclasses.replace(config, use_class_weights_cat=args.use_class_weights_cat)
    # STL loss calibration (next_cv.py cat tune). Only assembles a non-empty
    # dict when a calibration flag is set, so default runs keep the legacy path.
    _lc = {}
    if getattr(args, "focal_gamma", 0.0):
        _lc["focal_gamma"] = float(args.focal_gamma)
    if getattr(args, "logit_adjust_tau", 0.0):
        _lc["logit_adjust_tau"] = float(args.logit_adjust_tau)
    if getattr(args, "cat_label_smoothing", 0.0):
        _lc["label_smoothing"] = float(args.cat_label_smoothing)
    if getattr(args, "tail_loss", "none") not in (None, "none"):
        _lc["tail_mode"] = args.tail_loss
        _lc["cb_beta"] = float(getattr(args, "cb_beta", 0.999))
        _lc["ldam_max_m"] = float(getattr(args, "ldam_max_margin", 0.5))
        _lc["ldam_scale"] = float(getattr(args, "ldam_scale", 30.0))
    if _lc:
        config = dataclasses.replace(config, loss_calibration=_lc)
    # F51 Tier 3 overrides
    if getattr(args, "weight_decay", None) is not None:
        if args.weight_decay < 0:
            raise ValueError("--weight-decay must be >= 0")
        config = dataclasses.replace(config, weight_decay=float(args.weight_decay))
    if getattr(args, "adam_eps", None) is not None:
        if args.adam_eps <= 0:
            raise ValueError("--adam-eps must be > 0")
        config = dataclasses.replace(config, optimizer_eps=float(args.adam_eps))
    if getattr(args, "adam_beta2", None) is not None:
        if not (0.0 < args.adam_beta2 < 1.0):
            raise ValueError("--adam-beta2 must be in (0, 1)")
        config = dataclasses.replace(config, optimizer_beta2=float(args.adam_beta2))
    if getattr(args, "max_grad_norm", None) is not None:
        # Allow 0 / negative as "disable clipping" — runner already guards.
        config = dataclasses.replace(config, max_grad_norm=float(args.max_grad_norm))
    if getattr(args, "eta_min", None) is not None:
        if args.eta_min < 0:
            raise ValueError("--eta-min must be >= 0")
        config = dataclasses.replace(config, eta_min=float(args.eta_min))

    if args.candidate is not None:
        if config.task_type != "mtl":
            raise ValueError("--candidate can only be used with --task mtl")
        from ablation.candidates import get_candidate

        try:
            candidate = get_candidate(args.candidate)
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
        model_params = dict(config.model_params)
        model_params.update(candidate.model_params)
        config = dataclasses.replace(
            config,
            model_name=candidate.model_name,
            model_params=model_params,
            mtl_loss=candidate.mtl_loss,
            mtl_loss_params=dict(candidate.mtl_loss_params),
        )

    model_param_overrides = _parse_key_value_overrides(
        args.model_param, "--model-param"
    )
    if args.model_name is not None:
        config = dataclasses.replace(config, model_name=args.model_name)
    if getattr(args, "replace_model_params", False) and not model_param_overrides:
        raise ValueError("--replace-model-params requires at least one --model-param")
    if model_param_overrides:
        if getattr(args, "replace_model_params", False):
            model_params = model_param_overrides
        else:
            model_params = dict(config.model_params)
            model_params.update(model_param_overrides)
        config = dataclasses.replace(config, model_params=model_params)

    loss_param_overrides = _parse_key_value_overrides(
        args.mtl_loss_param, "--mtl-loss-param"
    )
    if args.mtl_loss is not None:
        if config.task_type != "mtl":
            raise ValueError("--mtl-loss can only be used with --task mtl")
        config = dataclasses.replace(
            config,
            mtl_loss=args.mtl_loss,
            mtl_loss_params={},
        )
    if args.category_weight is not None:
        if config.mtl_loss != "static_weight":
            raise ValueError(
                "--category-weight requires --mtl-loss static_weight"
            )
        loss_param_overrides["category_weight"] = args.category_weight
    if loss_param_overrides:
        loss_params = dict(config.mtl_loss_params)
        loss_params.update(loss_param_overrides)
        config = dataclasses.replace(config, mtl_loss_params=loss_params)

    if getattr(args, "freeze_cat_stream", False):
        if config.task_type != "mtl":
            raise ValueError("--freeze-cat-stream requires --task mtl")
        if config.mtl_loss != "static_weight":
            raise ValueError(
                "--freeze-cat-stream requires --mtl-loss static_weight "
                "(the F49 encoder-frozen variant is defined for "
                "category_weight=0.0 under static_weight)"
            )
        cat_w = config.mtl_loss_params.get("category_weight")
        if cat_w is None or float(cat_w) != 0.0:
            raise ValueError(
                "--freeze-cat-stream requires --category-weight 0.0; "
                "freezing the cat stream while still applying L_cat is "
                f"incoherent (got category_weight={cat_w!r})"
            )
        config = dataclasses.replace(config, freeze_cat_stream=True)

    if getattr(args, "freeze_reg_stream", False):
        if config.task_type != "mtl":
            raise ValueError("--freeze-reg-stream requires --task mtl")
        if getattr(args, "freeze_cat_stream", False):
            raise ValueError(
                "--freeze-reg-stream and --freeze-cat-stream are mutually "
                "exclusive (they probe opposite directions)"
            )
        if config.mtl_loss != "static_weight":
            raise ValueError(
                "--freeze-reg-stream requires --mtl-loss static_weight "
                "(the W6 region-frozen probe is defined for "
                "category_weight=1.0 under static_weight)"
            )
        cat_w = config.mtl_loss_params.get("category_weight")
        if cat_w is None or float(cat_w) != 1.0:
            raise ValueError(
                "--freeze-reg-stream requires --category-weight 1.0 "
                "(reg-loss=0); freezing the reg stream while still applying "
                f"L_reg is incoherent (got category_weight={cat_w!r})"
            )
        config = dataclasses.replace(config, freeze_reg_stream=True)

    if getattr(args, "freeze_cat_after_epoch", None) is not None:
        n = int(args.freeze_cat_after_epoch)
        if config.task_type != "mtl":
            raise ValueError("--freeze-cat-after-epoch requires --task mtl")
        if n < 1 or n >= int(config.epochs):
            raise ValueError(
                f"--freeze-cat-after-epoch={n} must be in [1, epochs-1] "
                f"(epochs={config.epochs})"
            )
        if getattr(config, "freeze_cat_stream", False):
            raise ValueError(
                "--freeze-cat-after-epoch and --freeze-cat-stream are mutually "
                "exclusive (the latter freezes from epoch 0)."
            )
        config = dataclasses.replace(config, freeze_cat_after_epoch=n)

    if getattr(args, "alternating_optimizer_step", False):
        if config.task_type != "mtl":
            raise ValueError("--alternating-optimizer-step requires --task mtl")
        if config.mtl_loss != "static_weight":
            raise ValueError(
                "--alternating-optimizer-step requires --mtl-loss static_weight "
                "(per-batch task selection bypasses the MTL weighter)."
            )
        if int(config.gradient_accumulation_steps) != 1:
            raise ValueError(
                "--alternating-optimizer-step requires --gradient-accumulation-steps 1 "
                f"(got {config.gradient_accumulation_steps}); alternation is by batch-idx."
            )
        config = dataclasses.replace(config, alternating_optimizer_step=True)

    if getattr(args, "reg_encoder_lr", None) is not None:
        if config.task_type != "mtl":
            raise ValueError("--reg-encoder-lr requires --task mtl")
        if not all(getattr(config, k, None) is not None for k in ("cat_lr", "reg_lr", "shared_lr")):
            raise ValueError(
                "--reg-encoder-lr requires per-head LR mode "
                "(--cat-lr, --reg-lr, --shared-lr all set)."
            )
        config = dataclasses.replace(config, reg_encoder_lr=float(args.reg_encoder_lr))

    if getattr(args, "reg_head_lr", None) is not None:
        if config.task_type != "mtl":
            raise ValueError("--reg-head-lr requires --task mtl")
        if not all(getattr(config, k, None) is not None for k in ("cat_lr", "reg_lr", "shared_lr")):
            raise ValueError(
                "--reg-head-lr requires per-head LR mode "
                "(--cat-lr, --reg-lr, --shared-lr all set)."
            )
        config = dataclasses.replace(config, reg_head_lr=float(args.reg_head_lr))

    if getattr(args, "per_fold_transition_dir", None) is not None:
        if config.task_type != "mtl":
            raise ValueError("--per-fold-transition-dir requires --task mtl")
        config = dataclasses.replace(
            config, per_fold_transition_dir=str(args.per_fold_transition_dir)
        )
    elif (
        getattr(args, "_canon_active", False)
        and config.task_type == "mtl"
        and args.engine is not None
        and args.state is not None
    ):
        # Under --canon (mtl), default the seeded per-fold log_T dir to output/<engine>/<state>
        # so a bare `--canon` run uses leak-free seeded log_T (the canon recipes all require it).
        # Explicit --per-fold-transition-dir still wins (handled above).
        config = dataclasses.replace(
            config, per_fold_transition_dir=f"output/{args.engine}/{config.state}"
        )

    if getattr(args, "min_best_epoch", 0):
        config = dataclasses.replace(
            config, min_best_epoch=int(args.min_best_epoch)
        )

    # Joint checkpoint selector (default geom_simple). MTL-only knob.
    _sel = getattr(args, "checkpoint_selector", "geom_simple")
    if _sel != getattr(config, "checkpoint_selector", "geom_simple"):
        if config.task_type != "mtl":
            raise ValueError("--checkpoint-selector requires --task mtl")
        config = dataclasses.replace(config, checkpoint_selector=_sel)

    if getattr(args, "alpha_no_weight_decay", False):
        if config.task_type != "mtl":
            raise ValueError("--alpha-no-weight-decay requires --task mtl")
        if not all(getattr(config, k, None) is not None for k in ("cat_lr", "reg_lr", "shared_lr")):
            raise ValueError(
                "--alpha-no-weight-decay requires per-head LR mode "
                "(--cat-lr, --reg-lr, --shared-lr all set)."
            )
        config = dataclasses.replace(config, alpha_no_weight_decay=True)

    if getattr(args, "alpha_frozen_until_epoch", None) is not None:
        if config.task_type != "mtl":
            raise ValueError("--alpha-frozen-until-epoch requires --task mtl")
        n = int(args.alpha_frozen_until_epoch)
        if n < 0:
            raise ValueError(f"--alpha-frozen-until-epoch must be >= 0, got {n}")
        config = dataclasses.replace(config, alpha_frozen_until_epoch=n if n > 0 else None)

    # substrate-protocol-cleanup Tier C2 — --reg-freeze-at-epoch.
    if getattr(args, "reg_freeze_at_epoch", None) is not None:
        n = int(args.reg_freeze_at_epoch)
        if config.task_type != "mtl":
            raise ValueError("--reg-freeze-at-epoch requires --task mtl")
        if n < 1 or n >= int(config.epochs):
            raise ValueError(
                f"--reg-freeze-at-epoch={n} must be in [1, epochs-1] "
                f"(epochs={config.epochs})"
            )
        config = dataclasses.replace(config, reg_freeze_at_epoch=n)

    # --zero-cat-kv. Wired into model_params so MTLnetCrossAttn.__init__
    # receives the kwarg via create_model(name, **model_params). No-op for
    # other model_names; validate that the user picked a compatible model.
    if getattr(args, "zero_cat_kv", False):
        if config.task_type != "mtl":
            raise ValueError("--zero-cat-kv requires --task mtl")
        if config.model_name != "mtlnet_crossattn":
            raise ValueError(
                f"--zero-cat-kv requires --model mtlnet_crossattn (got "
                f"{config.model_name!r}); the K/V channel is defined only "
                f"for the cross-attention model variant."
            )
        model_params = dict(config.model_params)
        model_params["zero_cat_kv"] = True
        config = dataclasses.replace(config, model_params=model_params)

    # substrate-protocol-cleanup Tier A1 — --log-t-kd-weight / --log-t-kd-tau.
    # Validates only basic sanity; the head-compat check (must be a
    # log_T-aware reg head) happens at train_model() time so the override
    # plumbing stays decoupled from the task_set registry import path.
    #
    # v12 DEFAULT FLIP (2026-05-30): log_T-KD is now ON by default (W=0.2,
    # τ=1.0) but SCOPED to MTL `check2hgi_next_region` — the only task-set
    # whose reg head consumes the per-fold log_T prior. The ExperimentConfig
    # dataclass field default stays 0.0 (it is task-agnostic and shared by
    # category/next runs); the v12 default is applied HERE, at the CLI layer,
    # only when the run is MTL + check2hgi_next_region and the user did NOT
    # pass an explicit --log-t-kd-weight. Category-only, non-region task-sets,
    # and non-MTL tasks are untouched (weight stays 0.0). Pass
    # --log-t-kd-weight 0.0 to recover the v11 paper-canon (no-KD) behaviour.
    # See docs/results/CANONICAL_VERSIONS.md (v11 vs v12).
    _V12_LOG_T_KD_DEFAULT_W = 0.2
    _V12_LOG_T_KD_DEFAULT_TAU = 1.0
    _task_set_name = getattr(args, "task_set", None) or LEGACY_CATEGORY_NEXT.name
    _is_check2hgi_region_mtl = (
        config.task_type == "mtl"
        and _task_set_name == CHECK2HGI_NEXT_REGION.name
    )
    if getattr(args, "log_t_kd_weight", None) is not None:
        # Explicit user override — honour it verbatim (incl. 0.0 for v11).
        w = float(args.log_t_kd_weight)
        if config.task_type != "mtl":
            raise ValueError("--log-t-kd-weight requires --task mtl")
        if w < 0.0:
            raise ValueError(
                f"--log-t-kd-weight={w} must be >= 0.0 (0.0 = off)"
            )
        config = dataclasses.replace(config, log_t_kd_weight=w)
        if w > 0.0:
            logger.info(
                "log_T-KD ON (W=%.3g) via explicit --log-t-kd-weight "
                "(v12 default is 0.2 for check2hgi_next_region MTL; pass "
                "--log-t-kd-weight 0.0 for v11 paper-canon)",
                w,
            )
        else:
            logger.info(
                "log_T-KD OFF (W=0.0) via explicit --log-t-kd-weight — "
                "v11 paper-canon (no-KD) reproduction mode"
            )
    elif _is_check2hgi_region_mtl:
        # v12 default ON, only for the task-set whose reg head reads log_T.
        config = dataclasses.replace(
            config, log_t_kd_weight=_V12_LOG_T_KD_DEFAULT_W
        )
        logger.info(
            "log_T-KD default ON (W=%.3g) — v12 default; pass "
            "--log-t-kd-weight 0.0 for v11 paper-canon",
            _V12_LOG_T_KD_DEFAULT_W,
        )
    if getattr(args, "log_t_kd_tau", None) is not None:
        tau = float(args.log_t_kd_tau)
        if tau <= 0.0:
            raise ValueError(
                f"--log-t-kd-tau={tau} must be > 0.0"
            )
        config = dataclasses.replace(config, log_t_kd_tau=tau)
    elif _is_check2hgi_region_mtl and config.log_t_kd_weight > 0.0:
        # Pin the v12 default τ=1.0 alongside the v12 default weight so the
        # KD term is fully specified without requiring --log-t-kd-tau.
        config = dataclasses.replace(
            config, log_t_kd_tau=_V12_LOG_T_KD_DEFAULT_TAU
        )

    # Per-instance log_T-KD gate (opt-in, MTL-only, default none).
    if getattr(args, "log_t_kd_gate", None) is not None:
        gate = str(args.log_t_kd_gate)
        if gate != "none" and config.task_type != "mtl":
            raise ValueError("--log-t-kd-gate requires --task mtl")
        if gate != "none" and config.log_t_kd_weight <= 0.0:
            raise ValueError(
                "--log-t-kd-gate requires --log-t-kd-weight > 0 (it gates that weight)"
            )
        config = dataclasses.replace(config, log_t_kd_gate=gate)
        if gate != "none":
            logger.info("R5 per-instance log_T-KD gate ON (%s, batch-mean-1 normalized)", gate)

    # log_C co-location KD. Opt-in, MTL-only, default OFF
    # (no version default; never auto-enabled). Stacks on top of log_t_kd.
    if getattr(args, "log_c_kd_weight", None) is not None:
        wc = float(args.log_c_kd_weight)
        if args.task != "mtl":
            raise ValueError("--log-c-kd-weight requires --task mtl")
        if wc < 0.0:
            raise ValueError(f"--log-c-kd-weight={wc} must be >= 0.0 (0.0 = off)")
        config = dataclasses.replace(config, log_c_kd_weight=wc)
        logger.info(
            "log_C co-location KD %s (W=%.3g) via --log-c-kd-weight (R1)",
            "ON" if wc > 0.0 else "OFF", wc,
        )
    if getattr(args, "log_c_kd_tau", None) is not None:
        tau_c = float(args.log_c_kd_tau)
        if tau_c <= 0.0:
            raise ValueError(f"--log-c-kd-tau={tau_c} must be > 0.0")
        config = dataclasses.replace(config, log_c_kd_tau=tau_c)

    # CrossDistil refinements + reverse arm. All opt-in, MTL-only.
    if getattr(args, "log_c_kd_warmup_epochs", None) is not None:
        we = int(args.log_c_kd_warmup_epochs)
        if we < 0:
            raise ValueError("--log-c-kd-warmup-epochs must be >= 0")
        config = dataclasses.replace(config, log_c_kd_warmup_epochs=we)
    if getattr(args, "log_c_kd_ec_lambda", None) is not None:
        ec = float(args.log_c_kd_ec_lambda)
        if not (0.0 <= ec <= 1.0):
            raise ValueError("--log-c-kd-ec-lambda must be in [0,1]")
        config = dataclasses.replace(config, log_c_kd_ec_lambda=ec)
    if getattr(args, "cat_kd_weight", None) is not None:
        wk = float(args.cat_kd_weight)
        if args.task != "mtl":
            raise ValueError("--cat-kd-weight requires --task mtl")
        if wk < 0.0:
            raise ValueError("--cat-kd-weight must be >= 0.0")
        config = dataclasses.replace(config, cat_kd_weight=wk)
        logger.info("R3 reverse cat-KD %s (W=%.3g)", "ON" if wk > 0 else "OFF", wk)
    if getattr(args, "cat_kd_tau", None) is not None:
        tk = float(args.cat_kd_tau)
        if tk <= 0.0:
            raise ValueError("--cat-kd-tau must be > 0.0")
        config = dataclasses.replace(config, cat_kd_tau=tk)

    # Loss-scale normalization — opt-in, MTL-only.
    if getattr(args, "loss_scale_norm", False):
        if config.task_type != "mtl":
            raise ValueError("--loss-scale-norm requires --task mtl")
        config = dataclasses.replace(config, loss_scale_norm=True)
        logger.info(
            "loss-scale-norm ON (T4.0a) — each task CE divided by "
            "log(num_classes) before the MTL combiner"
        )

    # aligned-pairing — opt-in, MTL-only.
    if getattr(args, "aligned_pairing", False):
        if config.task_type != "mtl":
            raise ValueError("--aligned-pairing requires --task mtl")
        config = dataclasses.replace(config, aligned_pairing=True)
        logger.info(
            "aligned-pairing ON (G0.1) — cat+reg train loaders share one "
            "per-epoch permutation (aligned cross-task pairing)"
        )

    # substrate-protocol-cleanup Tier C1 — --save-task-best-snapshots.
    if getattr(args, "save_task_best_snapshots", False):
        if config.task_type != "mtl":
            raise ValueError("--save-task-best-snapshots requires --task mtl")
        config = dataclasses.replace(config, save_task_best_snapshots=True)

    # Persist the per-task input modality into the config so any downstream
    # scorer (e.g. scripts/route_task_best.py) can rebuild the validation
    # loaders with the SAME modality this run trained on. Mirrors the value
    # passed to FoldCreator in _build_folds.
    config = dataclasses.replace(
        config,
        task_a_input_type=getattr(args, "task_a_input_type", "checkin"),
        task_b_input_type=getattr(args, "task_b_input_type", "checkin"),
    )

    return config


def _signatures_match(meta_path: Path, task: str, state: str, engine: EmbeddingEngine) -> bool:
    """Check if cached meta.json's input signatures still match the current parquets.

    Loud mismatch beats silent cache hit: if inputs changed since freeze, force
    regeneration rather than serve stale splits.
    """
    if not meta_path.exists():
        return False
    try:
        meta = json.loads(meta_path.read_text())
    except json.JSONDecodeError:
        return False
    cached = meta.get("inputs_signatures", {})
    expected_files: list[tuple[str, Path]] = []
    if task in ("mtl", "category"):
        expected_files.append(("category.parquet", IoPaths.get_category(state, engine)))
    if task in ("mtl", "next"):
        expected_files.append(("next.parquet", IoPaths.get_next(state, engine)))
    for name, path in expected_files:
        if name not in cached or not path.exists():
            return False
        live = DatasetSignature.from_path(path)
        if live.sha256 != cached[name].get("sha256"):
            return False
    return True


def _resolve_folds(
    args: argparse.Namespace,
    config: ExperimentConfig,
    engine: EmbeddingEngine,
    task_key: str,
    task_set: Optional[TaskSet] = None,
) -> dict:
    """Return the fold_results dict — either loaded from a frozen cache or
    generated on the fly.

    Precedence:
      1. Explicit --folds-path (fail loud if missing or unreadable)
      2. --no-folds-cache forces regeneration
      3. Canonical cache at output/{engine}/{state}/folds/fold_indices_{task}.pt
         IF its input signatures still match the current parquets
      4. Generate from scratch, with a warning pointing at freeze_folds.py
    """
    task_type = _TASK_TYPES[task_key]

    def _from_scratch(reason: str) -> dict:
        logger.warning(
            "Generating folds on the fly (%s). "
            "Run `python scripts/study/freeze_folds.py --state %s --engine %s --task %s` "
            "to freeze them; paired statistical tests require frozen splits.",
            reason, config.state, engine.value, task_key,
        )
        creator = FoldCreator(
            task_type=task_type,
            n_splits=config.k_folds,
            batch_size=config.batch_size,
            seed=config.seed,
            use_weighted_sampling=False,
            task_set=task_set,
            task_a_input_type=getattr(args, "task_a_input_type", "checkin"),
            task_b_input_type=getattr(args, "task_b_input_type", "checkin"),
            aligned_pairing=getattr(config, "aligned_pairing", False),
            # Build only the selected fold(s) on single-task --only-fold / --only-folds;
            # the full k-fold run keeps the eager path.
            lazy_single_task=(getattr(args, "only_fold", None) is not None
                              or getattr(args, "_only_folds_list", None) is not None),
        )
        return creator.create_folds(config.state, engine)

    if args.no_folds_cache:
        return _from_scratch("--no-folds-cache set")

    if args.folds_path is not None:
        cache_path = Path(args.folds_path)
        if not cache_path.exists():
            raise SystemExit(f"--folds-path {cache_path} does not exist")
        logger.info("Loading folds from %s (explicit --folds-path)", cache_path)
        serialized = load_folds(cache_path)
        return rebuild_dataloaders(serialized, batch_size=config.batch_size, use_weighted_sampling=False)

    canonical = IoPaths.get_folds_dir(config.state, engine) / f"fold_indices_{task_key}.pt"
    meta = canonical.with_suffix(".meta.json")
    if not canonical.exists():
        return _from_scratch(f"no cache at {canonical}")
    if not _signatures_match(meta, task_key, config.state, engine):
        return _from_scratch(
            f"cache {canonical} is stale (input parquet signature changed since freeze)"
        )
    logger.info("Loading frozen folds from %s", canonical)
    serialized = load_folds(canonical)
    # Warn if cached n_splits < requested k_folds (can't expand)
    cached_n = len(next(iter(serialized.fold_indices.values())))
    if cached_n < config.k_folds:
        raise SystemExit(
            f"cached folds have n_splits={cached_n} but config requests "
            f"k_folds={config.k_folds}; re-freeze with --n-splits or reduce --folds"
        )
    return rebuild_dataloaders(serialized, batch_size=config.batch_size, use_weighted_sampling=False)


def _load_config_from_file(path: str) -> ExperimentConfig:
    """Load ExperimentConfig from a Python file that exports config()."""
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location("_exp_cfg", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "config"):
        raise AttributeError(f"Config file {path!r} must export a config() function.")
    return mod.config()


def _preflight_canon_guards(args) -> None:
    """[anti-stumble] Visibility guards so a fresh agent/dev does not silently hit a wrong
    flow. WARN-only by default → **numerically inert** (no config/computation change); set
    ``MTL_STRICT=1`` to hard-fail (freeze-grade runs). Covers the three silent stumbles the
    pre-freeze defaults-audit surfaced (2026-06-19): development-seed 42, champion-recipe-on-
    the-wrong-substrate, and torch ≠ 2.11.0+cu128. The recipe itself is already enforced by
    ``--canon`` (default v18); these only catch the values canon deliberately does NOT pin.
    Guard (2) also carries a HARD refusal that ignores MTL_STRICT: the v18 recipe on any
    non-v18 substrate reproduces nothing published and every other check2hgi build is leaked.
    """
    import os as _os
    from configs.canon import CANON_BUNDLES

    strict = _os.environ.get("MTL_STRICT", "").strip() in ("1", "true", "True")

    def _emit(msg: str) -> None:
        if strict:
            raise SystemExit("MTL_STRICT=1 → " + msg)
        logger.warning(msg)

    canon = getattr(args, "canon", None)
    # pipeline_audit 2026-07-01 (V4) — read the injection decision recorded at
    # parse time (args._canon_active) instead of recomputing it with a stricter
    # predicate: injection treats a missing --task as mtl (`_known.task or
    # "mtl"`), so recomputing with `task == "mtl"` let a bare
    # `train.py --state X` inject the full v17 recipe yet SKIP guards 1-2
    # (dev-seed 42 + wrong-substrate) even under MTL_STRICT=1. The getattr
    # fallback mirrors the injection resolution for hand-built namespaces.
    canon_active = getattr(
        args, "_canon_active",
        (getattr(args, "task", None) or "mtl") == "mtl"
        and getattr(args, "config", None) is None
        and canon not in (None, "none"),
    )

    if canon_active:
        # (1) development-seed 42 is NOT paper-grade (overshoots §0.1 at large states).
        if getattr(args, "seed", None) is None:
            _emit("[canon-guard] --seed not set → development seed 42 (overshoots §0.1 by "
                  "~+3pp CA / +8pp TX). Paper-grade numbers require --seed in {0,1,7,100}.")
        # (2) champion recipe running on a DIFFERENT substrate than the canon bundle pins.
        # LAST --engine wins, mirroring argparse: a bundle built as `_V16 + [... --engine X]`
        # (v18 does exactly this) carries two --engine tokens, and the effective one is the
        # last. Reading the first would have made this guard fire on every bare v18 run,
        # comparing against the overridden value. Found 2026-09-08 while adding v18.
        bundle = CANON_BUNDLES.get(canon, [])
        _engines = [bundle[i + 1] for i, t in enumerate(bundle)
                    if t == "--engine" and i + 1 < len(bundle)]
        bundle_engine = _engines[-1] if _engines else None
        resolved_engine = getattr(args, "engine", None)
        if bundle_engine and resolved_engine and resolved_engine != bundle_engine:
            # (2a) HARD REFUSAL, regardless of MTL_STRICT: the leak-free recipe pointed at any
            # other substrate. Every check2hgi build except check2hgi_v18 predates the forward-
            # only fix — bidirectional consecutive-visit edges plus the category in the node
            # features, so a node can carry a feature of the target it predicts. The v18 recipe
            # on a pre-v18 substrate reproduces NOTHING that was ever published, and the pairing
            # is far more likely a mistake than an intent. Reproducing an older generation is
            # still one flag away: --canon v11..v17 pin their own substrates and are untouched.
            if bundle_engine == "check2hgi_v18":
                raise SystemExit(
                    f"[canon-guard] REFUSING: --canon {canon} is the leak-free recipe (substrate "
                    f"'{bundle_engine}') but --engine resolved to '{resolved_engine}'. That pair "
                    f"reproduces no published result, and every check2hgi build other than "
                    f"check2hgi_v18 carries the consecutive-visit leak. Either drop --engine and "
                    f"let the bundle pin it, or say which generation you mean: --canon v17 (v14 "
                    f"substrate), --canon v11 (frozen BRACIS), or --canon none for a bare run. "
                    f"This guard does not honour MTL_STRICT=0 -- a silent leaked substrate is "
                    f"what the v18 rebuild existed to remove."
                )
            _emit(f"[canon-guard] --canon {canon} is pinned to substrate '{bundle_engine}' "
                  f"but --engine resolved to '{resolved_engine}' → the champion recipe is on "
                  f"a DIFFERENT substrate (wrong-substrate stumble; use the matching --canon).")

    # (3) torch build: the frozen reg Acc@10 tie-break depends on the fp16 TopK kernel.
    try:
        import torch as _torch
        if _torch.__version__ != "2.11.0+cu128":
            _emit(f"[canon-guard] torch is '{_torch.__version__}', expected '2.11.0+cu128' "
                  f"(torch ≥2.12 rewrote the TopK kernel → frozen reg Acc@10 tie-break shifts).")
    except Exception:
        pass


def main(argv=None) -> None:
    args = _parse_args(argv)
    _preflight_canon_guards(args)

    # Build config
    if args.config is not None:
        config = _load_config_from_file(args.config)
    else:
        if args.state is None or args.engine is None:
            print(
                "error: --state and --engine are required when --config is not provided.",
                file=sys.stderr,
            )
            sys.exit(1)
        task = args.task or "mtl"
        factory = _DEFAULT_FACTORIES[task]
        config = factory(
            name=f"{task}_{args.state}_{args.engine}",
            state=args.state,
            embedding_engine=args.engine,
        )

    # Apply CLI overrides
    try:
        config = _apply_cli_overrides(config, args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    # --embedding-dim: override the dimension key in model_params.
    if args.embedding_dim is not None:
        _DIM_KEYS = {
            "mtl": "feature_size",
            "category": "input_dim",
            "next": "embed_dim",
        }
        dim_key = _DIM_KEYS.get(args.task, _DIM_KEYS.get(config.task_type, "feature_size"))
        updated_params = dict(config.model_params)
        updated_params[dim_key] = args.embedding_dim
        config = dataclasses.replace(config, model_params=updated_params)

    # --folds: limits execution, doesn't change split structure.
    # StratifiedKFold requires n_splits >= 2, so we use max(2, requested).
    max_folds = args.folds  # None means run all folds
    # --only-folds: parse the comma-separated subset once (0-indexed canonical fold ids).
    only_folds_list = None
    if getattr(args, "only_folds", None):
        try:
            only_folds_list = sorted({int(x) for x in str(args.only_folds).split(",") if x.strip() != ""})
        except ValueError:
            raise SystemExit(f"--only-folds must be comma-separated ints (got {args.only_folds!r}).")
        if not only_folds_list:
            raise SystemExit("--only-folds was empty.")
    args._only_folds_list = only_folds_list

    if getattr(args, "only_fold", None) is not None:
        # [ONLY-FOLD] force the canonical 5-split so fold k matches the per-fold substrate
        # + the n_splits=5 seeded log_T. Mutually exclusive with --folds — EXCEPT
        # --folds 5, which is what every --canon bundle injects and is semantically
        # identical to the forced canonical 5-split (pre-2026-07-01 this made
        # --only-fold unusable under ANY active canon). Inert by default.
        if only_folds_list is not None or (max_folds is not None and max_folds != 5):
            raise SystemExit("--only-fold, --only-folds and --folds are mutually exclusive; pass one (--folds 5 is tolerated: it equals the forced canonical 5-split).")
        config = dataclasses.replace(config, k_folds=5)
    elif only_folds_list is not None:
        # [MULTI-FOLD] same as --only-fold but for a subset; force the canonical 5-split.
        if max_folds is not None and max_folds != 5:
            raise SystemExit("--only-folds and --folds are mutually exclusive; pass one (--folds 5 is tolerated: it equals the forced canonical 5-split).")
        config = dataclasses.replace(config, k_folds=5)
    elif max_folds is not None:
        n_splits = max(2, max_folds)
        config = dataclasses.replace(config, k_folds=n_splits)

    # Multi-fold fan-out wiring. --run-id implies --per-fold-seed (the fan-out must be
    # fold-order-independent so a fanned-out fold equals its place in a sequential run).
    global _RUN_ID, _PER_FOLD_SEED
    _RUN_ID = getattr(args, "run_id", None)
    _PER_FOLD_SEED = bool(getattr(args, "per_fold_seed", False)) or (_RUN_ID is not None)

    seed_everything(config.seed)

    if getattr(args, "profile_run", False):
        from training.profiling import enable_profiler
        enable_profiler(True)

    # Train diagnostics (batch-0 grad-cosine) default flip (user decision
    # 2026-07-01): OFF for bare runs (they cost 2 extra full backwards/epoch +
    # host syncs, and force donated_buffer=False under --compile — ~9% AL wall),
    # ON when profiling (--profile / MTL_PROFILE=1). Explicit
    # MTL_TRAIN_DIAGNOSTICS=1/0 always wins (grad-cosine is a science
    # diagnostic — mechanism studies can enable it without the profiler, and a
    # profiled run can disable it to measure production-exact timing). Legacy
    # MTL_NO_TRAIN_DIAGNOSTICS=1 still forces OFF (handled in mtl_cv).
    import os as _os_diag
    if _os_diag.environ.get("MTL_TRAIN_DIAGNOSTICS") is None:
        _prof_on = bool(getattr(args, "profile_run", False)) or (
            _os_diag.environ.get("MTL_PROFILE") == "1")
        _os_diag.environ["MTL_TRAIN_DIAGNOSTICS"] = "1" if _prof_on else "0"
        if _prof_on:
            logger.info("train diagnostics ON (profiling run) — grad-cosine adds "
                        "2 backwards/epoch; set MTL_TRAIN_DIAGNOSTICS=0 for "
                        "production-exact profiled timing")

    # Optional CUDA perf knobs — both default-off so paper runs match
    # NORTH_STAR exactly. They live here (post-seed) because the seed
    # path also touches torch globals.
    if args.tf32:
        import torch
        if torch.cuda.is_available():
            torch.set_float32_matmul_precision("high")
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            logger.info("TF32 enabled (matmul_precision=high, cudnn.allow_tf32=True)")
        else:
            logger.info("--tf32 requested but CUDA unavailable; ignored")
    if args.compile_model:
        config = dataclasses.replace(config, use_torch_compile=True)
        # The MTL runner calls torch.autograd.grad(retain_graph=True) for the
        # gradient-cosine diagnostic (mtl_cv._compute_gradient_cosine). Inductor's
        # default donated-buffer optimization is incompatible — must be disabled
        # before any compiled fn is built.
        # P4 (pipeline_audit 2026-07-01, default flipped same day): diagnostics
        # are OFF by default (ON when profiling / MTL_TRAIN_DIAGNOSTICS=1), so
        # donated buffers stay enabled for bare runs — but ONLY for MTL losses
        # that never call retain_graph in their own backward (static_weight;
        # nash_mtl/pcgrad/gradnorm/cagrad/aligned_mtl all do).
        import os as _os_p4
        _diag_on = _os_p4.environ.get("MTL_TRAIN_DIAGNOSTICS", "0") == "1" and (
            _os_p4.environ.get("MTL_NO_TRAIN_DIAGNOSTICS", "0") != "1")
        _loss_retains_graph = getattr(config, "mtl_loss", None) not in ("static_weight",)
        if not _diag_on and not _loss_retains_graph:
            logger.info(
                "torch.compile enabled (use_torch_compile=True, donated_buffer "
                "left at inductor default — train diagnostics off and "
                "static_weight loss: no retain_graph users)"
            )
        else:
            import torch._functorch.config as _ft_config
            _ft_config.donated_buffer = False
            logger.info(
                "torch.compile enabled (use_torch_compile=True, "
                "donated_buffer=False for retain_graph=True compatibility)"
            )

    engine = EmbeddingEngine(config.embedding_engine)
    task_key = config.task_type if config.task_type in _RUNNERS else "mtl"

    # Resolve task_set for MTL runs. Default preset keeps legacy
    # {category, next} behaviour bit-exact; non-legacy preset activates
    # the check2HGI task pair and switches fold-creation to MTL_CHECK2HGI.
    task_set: Optional[TaskSet] = None
    is_check2hgi_track = False
    if task_key == "mtl":
        preset_name = args.task_set or LEGACY_CATEGORY_NEXT.name
        task_set = get_preset(preset_name)
        is_check2hgi_track = preset_name == CHECK2HGI_NEXT_REGION.name
        # MTL counterfactual allows --engine hgi provided
        # output/hgi/<state>/input/next_region.parquet exists (built by
        # scripts/probe/build_hgi_next_region.py). Cat input also flips to
        # HGI's input/next.parquet automatically via IoPaths.
        # Designs B/J/L (Lever 5) and the Lever-4 stack reuse the canonical
        # c2hgi graph + sequences verbatim (only the substrate embeddings
        # differ), so the check2hgi_next_region task pair is valid for them.
        # Per-fold log_T is cp'd from canonical (n_regions identical). The
        # allow-list is the single source of truth in configs/paths.py
        # (shared with data/folds.py).
        if is_check2hgi_track and engine not in MTL_CHECK2HGI_ALLOWED_ENGINES:
            print(
                f"error: --task-set {preset_name} requires --engine in "
                f"{[e.value for e in MTL_CHECK2HGI_ALLOWED_ENGINES]} "
                f"(got {engine.value}).",
                file=sys.stderr,
            )
            sys.exit(2)
        # Apply --reg-head / --reg-head-param / --cat-head / --cat-head-param
        # overrides BEFORE fold creation so FoldCreator sees the final
        # ``task_b.head_factory`` when deciding which dataloader path to use
        # (e.g. aux-publishing for the B5 head ``next_getnext_hard``). Cat
        # overrides don't currently affect fold creation but are applied here
        # symmetrically so the early task_set is the authoritative source
        # of head choice. The later ``resolve_task_set`` call after fold
        # creation additionally sets ``task_b_num_classes``, which can only
        # be known once labels are loaded — that pass is kept.
        if is_check2hgi_track and (
            args.reg_head or args.reg_head_param
            or args.cat_head or args.cat_head_param
        ):
            _early_reg_head_params = _parse_key_value_overrides(
                args.reg_head_param or [], "--reg-head-param"
            )
            _early_cat_head_params = _parse_key_value_overrides(
                args.cat_head_param or [], "--cat-head-param"
            )
            task_set = resolve_task_set(
                task_set,
                task_a_head_factory=args.cat_head,
                task_a_head_params=_early_cat_head_params or None,
                task_b_head_factory=args.reg_head,
                task_b_head_params=_early_reg_head_params or None,
            )

    # Resolve folds: prefer the frozen cache under
    # output/{engine}/{state}/folds/fold_indices_{task}.pt (see
    # scripts/study/freeze_folds.py). Falls back to on-the-fly generation
    # with a warning — required for paired statistical tests across
    # ablation runs.
    fold_resolve_key = "mtl_check2hgi" if is_check2hgi_track else task_key
    fold_results = _resolve_folds(
        args, config, engine, fold_resolve_key,
        task_set=task_set if is_check2hgi_track else None,
    )

    # For the check2HGI track: resolve task_b.num_classes from the
    # full next_region label space (the preset stores 0 as a
    # placeholder) and inject the resolved ``task_set`` into model_params.
    #
    # Computing ``n_regions`` from a single fold's train labels is a
    # subtle bug: val folds can contain regions absent from any given
    # train fold (cross-fold user partition doesn't preserve region
    # support). If the model is sized for a too-small n_regions and
    # val/other-fold labels exceed that range, bincount-based metrics
    # fail at runtime. Using the max across EVERY fold's (train ∪ val)
    # labels yields the true label-space size.
    if is_check2hgi_track:
        assert task_set is not None
        # Resolve task_b (region) num_classes from the union of train
        # and val labels across every fold. Cross-fold user partition
        # doesn't preserve region support, so a single fold's train
        # labels can miss classes present in val or other folds; a
        # too-small n_regions breaks bincount-based metrics at runtime.
        # task_a (next_category) is always 7 — no runtime resolution needed.
        # The fold mapping precomputes the global region count (max id + 1 over all
        # rows == the per-fold train∪val max across every fold); use it to avoid
        # materialising all folds just to size the model (esp. for --only-folds fan-out).
        n_regions = getattr(fold_results, "n_regions", None)
        if n_regions is None:
            max_b = -1
            for fr in fold_results.values():
                max_b = max(
                    max_b,
                    int(fr.next.train.y.max().item()),
                    int(fr.next.val.y.max().item()),
                )
            n_regions = max_b + 1
        reg_head_params = _parse_key_value_overrides(
            args.reg_head_param or [], "--reg-head-param"
        )
        cat_head_params = _parse_key_value_overrides(
            args.cat_head_param or [], "--cat-head-param"
        )
        task_set = resolve_task_set(
            task_set,
            task_a_head_factory=args.cat_head,
            task_a_head_params=cat_head_params if cat_head_params else None,
            task_b_num_classes=n_regions,
            task_b_head_params=reg_head_params if reg_head_params else None,
            task_b_head_factory=args.reg_head,
        )
        logger.info(
            "check2HGI task_set resolved: task_a=%s/%d, task_b=%s/%d",
            task_set.task_a.name, task_set.task_a.num_classes,
            task_set.task_b.name, task_set.task_b.num_classes,
        )
        updated_params = dict(config.model_params)
        updated_params["task_set"] = task_set
        config = dataclasses.replace(config, model_params=updated_params)

        # pipeline_audit 2026-07-01 (V3) — cond_coupling ≠ none feeds the CAT
        # batch row i's posterior as conditioning for the REG batch row i in
        # the same forward. Under the DEFAULT independent train shuffles those
        # rows are unrelated samples: the conditioning signal is semantically
        # garbage at train time while val is row-aligned. Any cond_coupling
        # experiment without --aligned-pairing is mechanistically confounded
        # (this bit the mtl_frontier R-CC arms and b4_cascade.py). WARN by
        # default; hard-fail under MTL_STRICT=1.
        _cc = str((task_set.task_b.head_params or {}).get("cond_coupling", "none"))
        if _cc != "none" and not getattr(config, "aligned_pairing", False):
            _cc_msg = (
                f"[cond-guard] reg-head cond_coupling={_cc!r} is active but "
                f"--aligned-pairing is OFF: the two MTL train loaders shuffle "
                f"independently, so the cat posterior of row i conditions an "
                f"UNRELATED reg row i at train time while validation is "
                f"row-aligned. Pass --aligned-pairing for a semantically "
                f"paired conditioning signal."
            )
            import os as _os_cc
            if _os_cc.environ.get("MTL_STRICT") == "1":
                raise SystemExit("MTL_STRICT=1 → " + _cc_msg)
            logger.warning(_cc_msg)

    # Apply --only-fold / --folds limit (run only the requested fold(s)).
    # config.k_folds stays as the split structure count (>= 2);
    # runners use len(fold_results) to determine actual execution count.
    if getattr(args, "only_fold", None) is not None:
        # [ONLY-FOLD] keep EXACTLY fold k (0-indexed), PRESERVING its dict key so the runner
        # loads region_transition_log_seed{seed}_fold{k+1}.pt. Fail loud on a stale (<5)-split
        # cache or an out-of-range k.
        if len(fold_results) != 5:
            raise SystemExit(
                f"--only-fold needs the canonical 5-split (got {len(fold_results)} folds); "
                f"re-freeze folds / rebuild the per-fold substrate at n_splits=5.")
        if args.only_fold not in fold_results:
            raise SystemExit(
                f"--only-fold {args.only_fold} not in available folds {sorted(fold_results)}")
        fold_results = _RestrictedFoldMapping(fold_results, [args.only_fold])
    elif getattr(args, "_only_folds_list", None) is not None:
        # [MULTI-FOLD] keep the requested subset, PRESERVING dict keys so each fold
        # loads its own region_transition_log_seed{seed}_fold{k+1}.pt and is named by
        # real id in the (shared) rundir. n_regions was already resolved over all 5
        # folds above, so the subset model is sized identically across fan-out processes.
        if len(fold_results) != 5:
            raise SystemExit(
                f"--only-folds needs the canonical 5-split (got {len(fold_results)} folds); "
                f"re-freeze folds / rebuild the per-fold substrate at n_splits=5.")
        missing = [k for k in args._only_folds_list if k not in fold_results]
        if missing:
            raise SystemExit(
                f"--only-folds {missing} not in available folds {sorted(fold_results)}")
        # pipeline_audit 2026-07-01 (V5) — lazy subset view: the old dict
        # comprehension eagerly built EVERY selected fold's loaders + slices at
        # once, defeating _LazyFoldMapping and its single-fold-peak RAM-guard
        # model (≥3 selected folds at TX overlap OOM-kill the host).
        fold_results = _RestrictedFoldMapping(fold_results, args._only_folds_list)
    elif max_folds is not None and max_folds < len(fold_results):
        # Same lazy-view treatment; for _LazyFoldMapping keys() is range(n) so
        # first-max_folds selection matches the old list(items())[:max_folds].
        fold_results = _RestrictedFoldMapping(
            fold_results, list(fold_results.keys())[:max_folds])

    results_path = IoPaths.get_results_dir(config.state, engine)
    results_path.mkdir(parents=True, exist_ok=True)

    # DVC tracks `results/<engine>/<state>/config.json` as a metric file
    # (see dvc.yaml). This file is overwritten by every training run on
    # purpose — DVC consumes it as the "latest run snapshot" for dashboards.
    # The CANONICAL per-run config is written into the per-invocation
    # checkpoint dir (see _default_checkpoint_callbacks above), so each
    # individual run's config is preserved alongside its weights and is
    # auto-discovered by scripts/evaluate.py via parent / config.json.
    config.save(results_path / "config.json")

    logger.info("=" * 72)
    logger.info(
        "Training: state=%s  engine=%s  task=%s  epochs=%d  folds=%d",
        config.state,
        config.embedding_engine,
        task_key,
        config.epochs,
        len(fold_results),
    )
    logger.info("=" * 72)

    # Validate loss + gradient accumulation compatibility before training.
    # All balancers that backprop internally / return loss=None must be listed
    # here, else they hit a TypeError at mtl_cv backward under grad_accum>1.
    # (Omitting one is safe only because default_mtl pins grad_accum=1.)
    _BACKWARD_ONLY_LOSSES = {
        "nash_mtl", "pcgrad", "gradnorm", "cagrad", "aligned_mtl",
    }
    grad_accum = getattr(config, "gradient_accumulation_steps", 1) or 1
    if (
        task_key == "mtl"
        and grad_accum > 1
        and config.mtl_loss in _BACKWARD_ONLY_LOSSES
    ):
        logger.error(
            "--mtl-loss %r calls backward() internally and is incompatible "
            "with gradient_accumulation_steps=%d. Use "
            "gradient_accumulation_steps=1 or a loss with get_weighted_loss().",
            config.mtl_loss,
            grad_accum,
        )
        sys.exit(2)

    global _NO_CHECKPOINTS
    _NO_CHECKPOINTS = getattr(args, "no_checkpoints", False)

    if is_check2hgi_track:
        assert task_set is not None
        _run_mtl_check2hgi(config, results_path, fold_results, task_set)
    else:
        runner = _RUNNERS[task_key]
        runner(config, results_path, fold_results)

    logger.info("Done. Results written to: %s", results_path)


if __name__ == "__main__":
    main()
   