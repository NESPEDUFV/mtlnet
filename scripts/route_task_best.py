"""substrate-protocol-cleanup Tier C1 — route_task_best.

Score the three per-fold MTL checkpoints produced by
``--save-task-best-snapshots`` against the held-out fold and print a
per-task routing table:

    | slot         | cat metric | reg metric |
    | cat_best     |   ...      |   ...      |
    | reg_best     |   ...      |   ...      |
    | joint_best   |   ...      |   ...      |

No retraining. The three checkpoints share the same model architecture
and the same training data; they differ only in which epoch was best by
which monitor.

The deploy interpretation of the table:

* cat-routed inference (cat from cat_best, reg from joint_best) vs
  joint-only inference (everything from joint_best) → reg degradation cost.
* reg-routed inference (reg from reg_best, cat from joint_best) vs
  joint-only → cat degradation cost.

Usage:

    python scripts/route_task_best.py \\
        --snapshots-dir results/check2hgi/alabama/task_best_snapshots \\
        --fold 1 \\
        --config results/check2hgi/alabama/config.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import torch

from configs.experiment import ExperimentConfig
from configs.globals import DEVICE
from configs.paths import EmbeddingEngine, IoPaths
from data.folds import FoldCreator, TaskType
from models.registry import create_model
from tasks import LEGACY_CATEGORY_NEXT, get_preset, resolve_task_set
from tracking.metrics import compute_classification_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


SLOTS = ("cat", "reg", "joint")


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Score the three per-fold MTL snapshots saved by "
            "--save-task-best-snapshots and print a per-task routing table."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--snapshots-dir",
        type=str,
        required=True,
        help=(
            "Directory containing the three per-fold checkpoints "
            "(fold{N}_cat_best.pt / fold{N}_reg_best.pt / fold{N}_joint_best.pt)."
        ),
    )
    parser.add_argument(
        "--fold",
        type=int,
        required=True,
        help="1-indexed fold number (matches the filename convention).",
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the run's config.json (used to rebuild the model + folds).",
    )
    parser.add_argument(
        "--task-set",
        type=str,
        default=None,
        help=(
            "FALLBACK task_set name (e.g. 'check2hgi_next_region') for OLD "
            "configs that never persisted a task_set. When config.model_params "
            "carries a task_set, THAT wins (it has the trained head overrides) "
            "and this flag is ignored with a warning — passing it forces the "
            "DEFAULT preset heads, which fail to load dual-tower snapshots. "
            "Normally leave this unset."
        ),
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Optional path to write the routing table as JSON.",
    )
    parser.add_argument(
        "--task-a-input-type",
        type=str,
        choices=("checkin", "region", "concat"),
        default=None,
        help=(
            "Override the task-a input modality used to rebuild the val "
            "loaders. When omitted, read from the run's config.json "
            "(config.task_a_input_type). Fallback for OLD configs that did "
            "not persist the field is 'checkin'."
        ),
    )
    parser.add_argument(
        "--task-b-input-type",
        type=str,
        choices=("checkin", "region", "concat"),
        default=None,
        help=(
            "Override the task-b input modality used to rebuild the val "
            "loaders. When omitted, read from the run's config.json "
            "(config.task_b_input_type). Fallback for OLD configs that did "
            "not persist the field is 'checkin'. CRITICAL: must match the "
            "modality the snapshots were TRAINED on (NORTH_STAR B9 = 'region'); "
            "a mismatch silently scores a region-trained reg head on checkin "
            "inputs → garbage reg metrics."
        ),
    )
    return parser.parse_args(argv)


def _load_state_dict(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(state, dict) and "state_dict" in state:
        # tolerate wrapped checkpoints
        return state["state_dict"]
    return state


def _score_state(
    state_dict: dict,
    model: torch.nn.Module,
    cat_loader,
    next_loader,
    task_a_num_classes: int,
    task_b_num_classes: int,
) -> dict:
    """Load ``state_dict`` into ``model`` and return per-task val metrics.

    Returns a dict with keys ``cat`` and ``reg`` each mapping to a metric
    dict from ``compute_classification_metrics``.
    """
    model.load_state_dict(state_dict)
    model.eval()
    cat_logits, cat_targets = [], []
    next_logits, next_targets = [], []
    with torch.no_grad():
        # Walk both loaders to completion. For routing analysis we do not
        # cycle the shorter one — each loader's full val set is scored once.
        for xb, yb in cat_loader:
            xb = xb.to(DEVICE)
            yb = yb.to(DEVICE)
            # Build a synthetic zero next batch matching batch size to
            # exercise the joint forward; reg metric is collected separately
            # below from the real next loader.
            dummy_next = torch.zeros(
                xb.size(0), 1, xb.size(-1) if xb.dim() == 3 else 1,
                device=DEVICE,
            )
            try:
                out_cat = model.cat_forward(xb if xb.dim() == 3 else xb.unsqueeze(1))
            except (AttributeError, NotImplementedError):
                out_cat, _ = model((xb if xb.dim() == 3 else xb.unsqueeze(1), dummy_next))
            cat_logits.append(out_cat.detach().cpu())
            cat_targets.append(yb.detach().cpu())
        for xb, yb in next_loader:
            xb = xb.to(DEVICE)
            yb = yb.to(DEVICE)
            try:
                out_next = model.next_forward(xb)
            except (AttributeError, NotImplementedError):
                dummy_cat = torch.zeros(
                    xb.size(0), 1, xb.size(-1), device=DEVICE,
                )
                _, out_next = model((dummy_cat, xb))
            next_logits.append(out_next.detach().cpu())
            next_targets.append(yb.detach().cpu())

    cat_metrics = compute_classification_metrics(
        torch.cat(cat_logits), torch.cat(cat_targets),
        num_classes=task_a_num_classes,
    )
    # Reg routing gate is on Acc@10 — request top-10 explicitly (the metric
    # fn defaults to top_k=(3,5), which would leave top10_acc absent → NaN).
    reg_metrics = compute_classification_metrics(
        torch.cat(next_logits), torch.cat(next_targets),
        num_classes=task_b_num_classes,
        top_k=(1, 3, 5, 10),
    )
    return {"cat": cat_metrics, "reg": reg_metrics}


def main(argv=None) -> None:
    args = _parse_args(argv)
    snap_dir = Path(args.snapshots_dir).resolve()
    if not snap_dir.is_dir():
        print(f"error: --snapshots-dir {snap_dir} not a directory", file=sys.stderr)
        sys.exit(2)

    snap_paths = {}
    for slot in SLOTS:
        p = snap_dir / f"fold{args.fold}_{slot}_best.pt"
        if not p.exists():
            print(f"error: missing snapshot {p}", file=sys.stderr)
            sys.exit(2)
        snap_paths[slot] = p

    config = ExperimentConfig.load(args.config)
    engine = EmbeddingEngine(config.embedding_engine)

    # Resolve task_set. Prefer explicit --task-set, else inspect
    # config.model_params, else legacy. NOTE: config.json round-trips the
    # task_set as a plain dict (JSON has no TaskSet type). We must
    # RECONSTRUCT it from the dict, NOT fall back to get_preset(name): the
    # run applied --cat-head / --reg-head overrides that mutate the preset's
    # head_factory per slot. get_preset returns the DEFAULT preset, whose
    # head topology mismatches the saved snapshots (load_state_dict fails).
    from tasks.registry import PrimaryMetric, TaskConfig
    from tasks.presets import TaskSet

    def _taskconfig_from_dict(d: dict) -> TaskConfig:
        return TaskConfig(
            name=d["name"],
            num_classes=d["num_classes"],
            head_factory=d.get("head_factory"),
            head_params=d.get("head_params"),
            is_sequential=d.get("is_sequential", True),
            primary_metric=PrimaryMetric(d.get("primary_metric", "f1")),
        )

    # PRECEDENCE: the config-persisted task_set ALWAYS wins when present, because
    # it carries the run's actual head_factory/head_params/num_classes overrides
    # (e.g. champion G's dual-tower: cat=next_gru, reg=next_stan_flow_dualtower).
    # get_preset(name) returns the DEFAULT preset heads (cat=next_mtl, reg=next_gru),
    # whose topology mismatches the saved snapshots → load_state_dict fails. So
    # --task-set is only a FALLBACK for OLD configs that never persisted a task_set,
    # and is IGNORED (with a warning) when a persisted one is present.
    _ts_raw = config.model_params.get("task_set")
    if hasattr(_ts_raw, "task_a"):
        # In-memory TaskSet (programmatic caller); already the trained topology.
        task_set = _ts_raw
    elif isinstance(_ts_raw, dict) and _ts_raw.get("task_a"):
        # Reconstruct WITH the run's head_factory overrides intact.
        task_set = TaskSet(
            name=_ts_raw.get("name", "reconstructed"),
            task_a=_taskconfig_from_dict(_ts_raw["task_a"]),
            task_b=_taskconfig_from_dict(_ts_raw["task_b"]),
        )
        if args.task_set is not None and args.task_set != task_set.name:
            logger.warning(
                "Ignoring --task-set=%s: config persists task_set '%s' with the "
                "trained head topology. The named preset rebuilds DEFAULT heads "
                "and would fail load_state_dict on the snapshots.",
                args.task_set, task_set.name,
            )
    elif args.task_set is not None:
        # Fallback: OLD config with no persisted task_set. Heads come from the
        # default preset and may mismatch the snapshots — warn.
        logger.warning(
            "config.model_params has no task_set; falling back to preset '%s'. "
            "Heads come from the DEFAULT preset and may mismatch the snapshots.",
            args.task_set,
        )
        task_set = get_preset(args.task_set)
    else:
        task_set = LEGACY_CATEGORY_NEXT

    # Resolve the per-task input modality. This MUST match the modality the
    # snapshots were trained with: a region-trained reg head scored on
    # checkin-modality loaders silently yields garbage reg metrics
    # (substrate-protocol-cleanup Tier C1 modality bug). Precedence:
    #   1. explicit --task-{a,b}-input-type CLI override
    #   2. the run's persisted config.task_{a,b}_input_type
    #   3. legacy fallback "checkin" (old configs predate the persisted field)
    task_a_input_type = (
        args.task_a_input_type
        if args.task_a_input_type is not None
        else getattr(config, "task_a_input_type", "checkin")
    )
    task_b_input_type = (
        args.task_b_input_type
        if args.task_b_input_type is not None
        else getattr(config, "task_b_input_type", "checkin")
    )
    logger.info(
        "Rebuilding val loaders with task_a_input_type=%s, task_b_input_type=%s",
        task_a_input_type, task_b_input_type,
    )

    # Recreate folds to retrieve fold N's val loaders. We rely on the seed
    # + n_splits in the config to reproduce the deterministic split that
    # produced the snapshots, and the SAME per-task input modality so the
    # gate metric (reg Acc@10) is computed on the trained inputs.
    task_type = TaskType.MTL_CHECK2HGI if task_set is not LEGACY_CATEGORY_NEXT else TaskType.MTL
    creator = FoldCreator(
        task_type=task_type,
        n_splits=config.k_folds,
        batch_size=config.batch_size,
        seed=config.seed,
        use_weighted_sampling=False,
        task_set=task_set if task_set is not LEGACY_CATEGORY_NEXT else None,
        task_a_input_type=task_a_input_type,
        task_b_input_type=task_b_input_type,
    )
    fold_results = creator.create_folds(config.state, engine)
    # fold_results is a dict keyed by 0-indexed fold; --fold is 1-indexed
    target_idx = args.fold - 1
    if target_idx not in fold_results:
        print(
            f"error: fold {args.fold} (0-indexed={target_idx}) not in "
            f"fold_results keys {list(fold_results.keys())}",
            file=sys.stderr,
        )
        sys.exit(2)
    fr = fold_results[target_idx]

    # Build model from config.model_params; ensure task_set is wired as the
    # resolved TaskSet OBJECT (config round-trips it as a dict, which
    # create_model cannot consume).
    model_params = dict(config.model_params)
    if task_set is not LEGACY_CATEGORY_NEXT:
        model_params["task_set"] = task_set
    model = create_model(config.model_name, **model_params).to(DEVICE)

    task_a_num_classes = task_set.task_a.num_classes or config.model_params.get("num_classes", 7)
    task_b_num_classes = task_set.task_b.num_classes or config.model_params.get("num_classes", 7)

    table = {}
    for slot, path in snap_paths.items():
        logger.info("Scoring slot=%s from %s", slot, path)
        state = _load_state_dict(path)
        scores = _score_state(
            state, model,
            fr.category.val.dataloader,
            fr.next.val.dataloader,
            task_a_num_classes=task_a_num_classes,
            task_b_num_classes=task_b_num_classes,
        )
        table[slot] = {
            "cat_f1": float(scores["cat"].get("f1", float("nan"))),
            "cat_accuracy": float(scores["cat"].get("accuracy", float("nan"))),
            "reg_f1": float(scores["reg"].get("f1", float("nan"))),
            "reg_accuracy": float(scores["reg"].get("accuracy", float("nan"))),
            "reg_top10_acc": float(scores["reg"].get("top10_acc", float("nan"))),
        }

    # Pretty-print
    print()
    print(f"Routing table (fold {args.fold}, state={config.state}, engine={config.embedding_engine})")
    print("-" * 80)
    header = f"{'slot':<12} {'cat F1':>10} {'cat Acc@1':>12} {'reg F1':>10} {'reg Acc@1':>12} {'reg Acc@10':>12}"
    print(header)
    print("-" * 80)
    for slot in SLOTS:
        row = table[slot]
        print(
            f"{slot+'_best':<12} "
            f"{row['cat_f1']:>10.4f} {row['cat_accuracy']:>12.4f} "
            f"{row['reg_f1']:>10.4f} {row['reg_accuracy']:>12.4f} "
            f"{row['reg_top10_acc']:>12.4f}"
        )
    print("-" * 80)
    # Per-task routing summary
    cat_routed_f1 = table["cat"]["cat_f1"]
    reg_routed_acc10 = table["reg"]["reg_top10_acc"]
    joint_cat_f1 = table["joint"]["cat_f1"]
    joint_reg_acc10 = table["joint"]["reg_top10_acc"]
    print("Per-task routing vs joint-best:")
    print(
        f"  cat:  cat_best F1   {cat_routed_f1:.4f}  vs  joint_best F1     {joint_cat_f1:.4f}  "
        f"(Δ={cat_routed_f1 - joint_cat_f1:+.4f})"
    )
    print(
        f"  reg:  reg_best Acc@10 {reg_routed_acc10:.4f}  vs  joint_best Acc@10 {joint_reg_acc10:.4f}  "
        f"(Δ={reg_routed_acc10 - joint_reg_acc10:+.4f})"
    )

    if args.output_json is not None:
        out = {
            "fold": args.fold,
            "state": config.state,
            "engine": config.embedding_engine,
            "task_a_input_type": task_a_input_type,
            "task_b_input_type": task_b_input_type,
            "table": table,
            "summary": {
                "cat_routed_f1": cat_routed_f1,
                "reg_routed_top10_acc": reg_routed_acc10,
                "joint_cat_f1": joint_cat_f1,
                "joint_reg_top10_acc": joint_reg_acc10,
            },
        }
        Path(args.output_json).write_text(json.dumps(out, indent=2, default=str))
        logger.info("Wrote routing JSON to %s", args.output_json)


if __name__ == "__main__":
    main()
