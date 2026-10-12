"""The training loop. One loop, three families — the difference between them is data, not code.

The reference has three: a runner for the category family, a second one inside an ablation script for
the region family, and a third for the joint model. The region one was a copy that fell two months
behind the shared fixes and shipped a scoring path that cost ~39% of a cell's wall-clock, undetected,
because nothing forced it to use the library. That is the structural reason this file exists.

Invariants implemented here, numbered as in docs/SYSTEM_MAP.md:

* **S14** gradient clipping at max-norm 1.0, every family.
* **S15** the scheduler advances per optimizer step, and its budget is built from the true number of
  steps per epoch. An off-by-one here shifts every learning rate after the first epoch with nothing
  to indicate it.
* **S2** all class statistics come from the training split.
* **S7** both epoch-selection conventions are computed from the same recorded series.

Per-fold reseeding is the contract from the reference's region family, adopted for all three: fold k
trains under `seed + k`, so a fold is independent of the folds before it and a single-fold re-run
reproduces its place in a sequential run.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import torch

from ..config import Precision, Resolved, TaskFamily
from ..device import DeviceSpec, empty_cache
from ..seeding import fold_seed, seed_everything
from ..data import dataset, loaders, splits
from ..models.factory import build_head
from ..models.joint import JointModel
from . import capacity
from . import checkpoints as ckpt
from . import diagnostics as diag
from . import losses, metrics, scoring

logger = logging.getLogger(__name__)


@dataclass
class EpochSeries:
    """Per-epoch validation metrics for one task, in epoch order."""

    values: dict[str, list[float]] = field(default_factory=dict)

    def log(self, metrics_dict: dict[str, float]) -> None:
        for key, value in metrics_dict.items():
            self.values.setdefault(key, []).append(float(value))

    def as_mapping(self) -> dict[str, list[float]]:
        return self.values


def _capture_architecture(model) -> tuple[dict[str, int], str]:
    """Parameter counts by path plus the module tree, taken BEFORE compilation.

    Before, deliberately: `torch.compile` wraps the module, so `repr` after it describes an
    OptimizedModule and every path gains a `_orig_mod.` prefix that no longer matches the recipe.
    """
    from . import report

    return report.parameter_counts(model), repr(model)


@dataclass
class FoldResult:
    fold: int
    seed: int
    epochs: int
    wall_seconds: float
    train_loss: list[float]
    val: dict[str, EpochSeries]
    selection: dict
    ambiguous_rows: dict[str, int]
    diagnostics: dict = field(default_factory=dict)
    #: Forward FLOPs, measured on fold 0 where the model is built. Empty on other folds.
    flops: dict = field(default_factory=dict)
    #: Parameters per path and the module tree, captured where the model exists. Carried as data
    #: rather than as the model object, which would pin a GPU model alive for the whole cell — and
    #: recorded at all because the reference's capacity audit described a model it never built.
    parameter_counts: dict[str, int] = field(default_factory=dict)
    architecture: str = ""
    #: Per-row outer predictions from the SELECTED checkpoint — the persistence contract. None when
    #: not requested, because capturing costs one extra validation pass and a CPU weight copy.
    rows: dict | None = None
    #: WHICH held-out stream the per-epoch series — and therefore `selection["value"]` — came from.
    #: `"inner_val"` under sealing, `"outer_fold"` under the legacy rule. Recorded because the two
    #: are not the same estimand: um número legado viu a própria seleção, e o otimismo disso é
    #: **sugerido em ~0,66 pp por UM fold de Alabama** — não medido (`waves/sealed_bridge.toml:9`).
    #: Parear um contra o outro reportaria esse viés como efeito.
    eval_stream: str = "outer_fold"
    #: Which weights this fold left on disk, by role. Empty when retention is off.
    checkpoints: dict = field(default_factory=dict)


def base_of(model: torch.nn.Module) -> torch.nn.Module:
    """The module under a `torch.compile` wrapper, or the model itself."""
    return getattr(model, "_orig_mod", model)


def train_fold(resolved: Resolved, inputs: dataset.Inputs, fold: splits.Fold,
               spec: DeviceSpec, *, build_model: Callable[[int, int], torch.nn.Module] | None = None,
               on_epoch: Callable[[int, dict], None] | None = None,
               capture_predictions: bool = False,
               run_dir: Path | None = None) -> FoldResult:
    """Train one fold of a dedicated family and return its per-epoch record.

    The head comes from the recipe by default. `build_model` overrides that for tests; it is not the
    normal path, because a head built outside the configuration is a head whose shape the result
    cannot record.
    """
    cfg = resolved.train
    if cfg.family is TaskFamily.JOINT:
        raise ValueError("the joint family has two streams; call train_joint_fold")
    seed = fold_seed(cfg.seed, fold.index, decorrelated=cfg.decorrelated_fold_seed)
    seed_everything(seed)

    diag.reset_peak_memory(spec.device)          # before the data moves, so residency counts
    train_stream, val_stream = dataset.fold_streams(inputs, fold, cfg.family, spec.device)
    # Under the sealed protocol the epoch loop never sees `val_stream`: it validates on the inner
    # split and the outer fold is read once, after selection. Audit criterion 6 is this line.
    selection_stream = dataset.selection_stream(inputs, fold, cfg.family, spec.device)
    epoch_stream = selection_stream if selection_stream is not None else val_stream
    eval_stream = "inner_val" if selection_stream is not None else "outer_fold"
    num_classes = inputs.n_categories if cfg.family is TaskFamily.CAT else inputs.n_regions
    embed_dim = int(train_stream.x.shape[-1])

    if build_model is not None:
        model = build_model(embed_dim, num_classes)
    else:
        head_cfg = cfg.cat_head if cfg.family is TaskFamily.CAT else cfg.reg_head
        model = build_head(head_cfg, embed_dim=embed_dim, num_classes=num_classes)
    model = model.to(spec.device)
    captured_counts, captured_arch = _capture_architecture(model)
    # Fold 0 only, and HERE — on the object the run holds. A number measured on a model rebuilt from
    # module defaults is the R14 defect: the published audit counted 644,359 where the run used
    # 1,433,863, and a "capacity-matched" arm ran at 230% of target.
    captured_flops = (capacity.measure_flops(model, (train_stream.x[:1],))
                      if fold.index == 0 else {})
    # Mirrors the joint path, which no longer trades compile for the probe. A dedicated cell has no
    # shared trunk and no second loss, so `grad_geometry` is meaningless here and never gated this —
    # it only did so to keep the two paths executing alike, which they now do by compiling.
    if spec.can_compile:
        model = torch.compile(model)

    loss_cfg = cfg.cat_loss if cfg.family is TaskFamily.CAT else cfg.reg_loss
    criterion = losses.build(
        num_classes,
        # S2 — the leak guard: TRAIN labels only, named at the call site.
        train_stream.y.detach().cpu().numpy(),
        logit_adjust_tau=loss_cfg.logit_adjust_tau,
        balanced_weights=loss_cfg.class_weights,
        label_smoothing=loss_cfg.label_smoothing,
        device=spec.device,
    )

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg.optim.lr, weight_decay=cfg.optim.weight_decay,
        eps=cfg.optim.eps, betas=(0.9, cfg.optim.beta2),
    )
    steps = loaders.steps_per_epoch(len(train_stream), cfg.batch_size)
    scheduler = _build_scheduler(optimizer, cfg, steps)

    # The training label set decides which validation rows are in-distribution. Computed once, from
    # the training split, before any epoch runs.
    train_labels = set(np.unique(train_stream.y.detach().cpu().numpy()).tolist())
    is_region = cfg.family is TaskFamily.REG

    series = {cfg.family.value: EpochSeries()}
    train_losses: list[float] = []
    best_seen, best_epoch_seen, best_state = float("-inf"), 0, None
    # Weights are tracked whenever ANYTHING will use them — persisting rows needs the selected
    # state, and so does retention. Tying it to capture alone meant a retention-only run silently
    # kept nothing.
    keep = ckpt.FoldCheckpoints(run_dir, fold.index, cfg.retain_checkpoints, cfg.epochs)
    track_best = capture_predictions or keep.active
    keep.maybe_trajectory(model, 0)
    worst_ambiguity: dict[str, int] = {}
    started = time.time()
    generator = torch.Generator().manual_seed(seed)
    diagnose = diag.FoldDiagnostics() if cfg.diagnostics else None
    health = diag.GradHealth(spec.device, cfg.optim.max_grad_norm) if diagnose else None
    compile_before = diag.compile_snapshot() if diagnose else {}
    if diagnose is not None:
        # A dedicated cell has no trunk to probe, so the field says so rather than being absent and
        # ambiguous with "we forgot to turn it on".
        diagnose.execution = {"compiled": bool(spec.can_compile), "probe": "n/a (no shared trunk)",
                              "precision": str(cfg.precision.value), "tf32": bool(spec.can_tf32),
                              "device": str(spec.device)}

    for epoch in range(cfg.epochs):
        model.train()
        running = torch.zeros((), device=spec.device)
        seen = 0
        _train_timer = diag.Phase(diagnose.train_seconds, spec.device) if diagnose else _null()
        # The auxiliary tensor (last_region_idx) is deliberately unused. It feeds the region head's
        # trajectory-flow prior, and v18 runs that prior inert — the reference itself never reads it
        # in this configuration. The stream still carries it so that a head which DOES consume it is
        # a drop-in rather than something this loop has to special-case.
        with _train_timer:
          for x, y, _aux in loaders.batches(train_stream, cfg.batch_size, shuffle=True,
                                            generator=generator):
            optimizer.zero_grad(set_to_none=True)
            with spec.autocast():
                logits = model(x)
                loss = criterion(logits, y)
            loss.backward()
            # S14. The returned pre-clip norm was discarded for a year; it is the cheapest forensic
            # signal there is, and it costs nothing because clip_grad_norm_ already computes it.
            total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.optim.max_grad_norm)
            if health is not None:
                health.observe(total_norm.detach())
            optimizer.step()
            # S15 — per optimizer step, never per epoch.
            scheduler.step()
            running += loss.detach() * y.shape[0]
            seen += int(y.shape[0])
        train_losses.append(float(running.item() / max(seen, 1)))
        if diagnose is not None:
            health.flush(diagnose)
            diagnose.learning_rates.append([g["lr"] for g in optimizer.param_groups])

        with (diag.Phase(diagnose.val_seconds, spec.device) if diagnose else _null()):
            epoch_metrics = _validate(model, epoch_stream, criterion, cfg, spec, num_classes,
                                      train_labels if is_region else None, is_region)
        for key, value in epoch_metrics.pop("_ambiguous", {}).items():
            worst_ambiguity[key] = max(worst_ambiguity.get(key, 0), value)
        series[cfg.family.value].log(epoch_metrics)
        if on_epoch is not None:
            on_epoch(epoch, epoch_metrics)

        # Keep the best-so-far weights so the persistence contract can evaluate THE SELECTED
        # checkpoint rather than whatever the last epoch happened to leave behind. Tracked with the
        # same key and the same min_best_epoch rule the final selector uses, and cross-checked
        # against it below — a silent disagreement would persist rows from the wrong model.
        keep.maybe_trajectory(model, epoch + 1)
        if track_best:
            # The SELECTED lane, not the diagnostic one: raw top-10 for region (protocol §1's
            # reported estimand and the banked v18 convention), macro-F1 for category. It must be
            # the same key and gate `single_task_best` uses, or the cross-check below is a coin flip.
            key = "top10_acc" if is_region else "f1"
            value = epoch_metrics.get(key)
            # The loop is 0-based and `scoring` reports `index + 1`. Tracking the raw loop variable
            # made the guard fire with "epoch 12 vs 13" on the first real run — which is the guard
            # working, and the reason it compares rather than assumes.
            if value is not None and epoch >= cfg.min_best_epoch and value > best_seen:
                best_seen, best_epoch_seen = value, epoch + 1
                # ckpt.snapshot, NOT model.state_dict(): after torch.compile the wrapper prefixes
                # every key with `_orig_mod.`, and a file with those keys will not load into a fresh
                # model. All three v18 recipes pin compile=true, so an inline state_dict() made
                # every retained checkpoint of a 270-fit campaign unloadable — discovered only when
                # the §8a scorer opened one, after the compute was spent.
                best_state = ckpt.snapshot(model)

    selection = scoring.single_task_best(
        series[cfg.family.value].as_mapping(),
        "top10_acc_indist" if is_region else "f1",
        min_best_epoch=cfg.min_best_epoch,
    )
    # The cross-check gates BOTH consumers. It used to run only under `capture_predictions` while
    # the file was written regardless, so a retention-only run could bank a `fold*_selected.pt`
    # whose epoch nobody had verified against the selector — a checkpoint labelled "selected" that
    # is not the selected one is worse than no checkpoint, because it loads.
    if track_best and best_state is not None and best_epoch_seen != selection["epoch"]:
        raise RuntimeError(
            f"the tracked checkpoint (epoch {best_epoch_seen}) disagrees with the selector "
            f"(epoch {selection['epoch']}). Persisting the wrong model is worse than persisting "
            f"none, so this fails rather than guesses.")
    if keep.active and best_state is not None:
        keep.selected(best_state, best_epoch_seen, best_seen)

    rows = None
    if capture_predictions:
        if best_state is None:
            raise RuntimeError("no epoch qualified for selection; cannot persist predictions")
        base_of(model).load_state_dict(best_state)
        # The one-shot outer evaluation. Always `val_stream` — the sealed fold — never the stream
        # the epochs were scored on.
        captured = _validate(model, val_stream, criterion, cfg, spec, num_classes,
                             train_labels if is_region else None, is_region, capture_rows=True)
        rows = captured["_rows"]

    diag_summary = {}
    if diagnose:
        diagnose.peak_memory_bytes = diag.peak_memory(spec.device)
        diagnose.compile_counters = diag.compile_counters(compile_before)
        key = "top10_acc" if is_region else "f1"
        diag_summary = diagnose.summary(series[cfg.family.value].values.get(key))

    empty_cache(spec.device)
    return FoldResult(
        fold=fold.index, seed=seed, epochs=cfg.epochs, wall_seconds=time.time() - started,
        train_loss=train_losses, val=series, selection=selection,
        ambiguous_rows=worst_ambiguity, diagnostics=diag_summary,
        parameter_counts=captured_counts, architecture=captured_arch, rows=rows,
        eval_stream=eval_stream, checkpoints=keep.manifest(), flops=captured_flops,
    )


class _null:
    """A no-op stand-in for a timing context, so the loop body has one shape."""

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


@torch.no_grad()
def _validate(model, stream: loaders.TaskStream, criterion, cfg, spec: DeviceSpec,
              num_classes: int, train_labels: set[int] | None,
              is_region: bool, capture_rows: bool = False) -> dict[str, float]:
    """One validation pass: the criterion's value and the full metric dict.

    The loss is computed through the SAME criterion training used, logit adjustment included. That
    is what the reference records, and it is the honest reading: a validation loss computed with a
    different criterion than the one being optimised describes a different objective.

    Note this is the loss only — the reported METRICS are computed from the raw logits, which is why
    logit adjustment stays a train-time device and cannot reach a scored number.
    """
    model.eval()
    top_k = (1, 5, 10) if is_region else (3, 5)
    accumulator = metrics.StreamingMetrics(
        num_classes, top_k=top_k,
        keep_top_k=cfg.keep_top_k if capture_rows else 0)
    total_loss = torch.zeros((), device=spec.device)
    seen = 0

    for x, y, _aux in loaders.batches(stream, cfg.batch_size, shuffle=False):
        with spec.autocast():
            logits = model(x)
            loss = criterion(logits, y)
        total_loss += loss.detach() * y.shape[0]
        accumulator.update(logits.detach(), y)
        seen += int(y.shape[0])

    out = accumulator.compute()
    out["loss"] = float(total_loss.item() / max(seen, 1)) if seen else 0.0

    if train_labels is not None:
        _, targets, rank, hits = accumulator.concat()
        out.update(metrics.in_distribution(targets, rank, hits, train_labels))
        out.update(metrics.region_score(out))

    out["_ambiguous"] = {f"top{k}": v for k, v in accumulator.ambiguous.items()}
    if capture_rows:
        # The persistence contract (protocol §2). Captured here because these arrays exist only
        # while the model runs: everything downstream is post-processing, but the rows themselves
        # cannot be recovered later without retraining.
        preds, targets, rank, _ = accumulator.concat()
        out["_rows"] = {"y_pred": preds.cpu().numpy(), "y_true": targets.cpu().numpy(),
                        "rank_of_true": rank.cpu().numpy(),
                        **{k: v.cpu().numpy() for k, v in accumulator.distribution().items()}}
    return out


def _build_scheduler(optimizer, cfg, steps_per_epoch: int):
    """OneCycle over the true step budget.

    `steps_per_epoch` must be the number of optimizer steps an epoch actually performs. Over-budget
    and the schedule never finishes its anneal; under-budget and it finishes early and the tail
    trains at the floor. Neither raises.
    """
    if cfg.optim.scheduler == "onecycle":
        max_lrs = _per_group_max_lr(optimizer, cfg)
        return torch.optim.lr_scheduler.OneCycleLR(
            optimizer, max_lr=max_lrs, epochs=cfg.epochs, steps_per_epoch=steps_per_epoch,
        )
    if cfg.optim.scheduler == "constant":
        return torch.optim.lr_scheduler.ConstantLR(optimizer, factor=1.0, total_iters=0)
    raise ValueError(f"unknown scheduler {cfg.optim.scheduler!r}")


def _per_group_max_lr(optimizer, cfg) -> float | list[float]:
    """One max_lr per parameter group.

    For a dedicated family there is one group and one rate. The joint family has three, and the
    reference only applied them because a driver exported an environment variable — without it the
    scalar broadcast to every group and the run was silently a different recipe. Here the rates are
    part of the configuration and the joint family refuses to construct without them.
    """
    if len(optimizer.param_groups) == 1:
        return cfg.optim.max_lr
    raise NotImplementedError("per-group rates are set up by the joint runner")


def evaluate_folds(results: list[FoldResult]) -> dict:
    """Fold-mean and sample standard deviation, with the lane named.

    ddof=1, matching the reference, so a cross-pipeline comparison of dispersion is like for like;
    at n=5 that is ~12% larger than the population figure.

    `lane` is reported, not implied. A region mean carries a second entry for the joint convention,
    because the two are different estimators at different epochs and comparing them silently is the
    mistake this whole scoring path exists to prevent.
    """
    values = [r.selection["value"] for r in results]
    streams = {r.eval_stream for r in results}
    if len(streams) > 1:
        raise ValueError(f"folds of one cell were scored on different streams {sorted(streams)}; "
                         f"their mean would average two estimands")
    out = {
        "eval_stream": results[0].eval_stream,
        "lane": results[0].selection.get("lane", "diag_best"),
        "metric": results[0].selection["metric"],
        "per_fold": values,
        # The REAL fold ids beside the values. A cell run with --only-folds banks a short list, and
        # a consumer that re-derives ids by position pairs the wrong folds across arms.
        "fold_ids": [r.fold for r in results],
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "n_folds": len(values),
        "best_epochs": [r.selection["epoch"] for r in results],
    }
    if all("joint_convention" in r.selection for r in results):
        alt = [r.selection["joint_convention"]["top10_full"] for r in results]
        out["joint_convention"] = {
            "lane": "joint_diag_best",
            "metric": "top10_acc_indist * (1 - ood_fraction)",
            "per_fold": alt,
            "mean": float(np.mean(alt)),
            "std": float(np.std(alt, ddof=1)) if len(alt) > 1 else 0.0,
            "best_epochs": [r.selection["joint_convention"]["epoch"] for r in results],
        }
    return out


__all__ = ["EpochSeries", "FoldResult", "train_fold", "train_joint_fold",
           "evaluate_folds"]


# ---------------------------------------------------------------- the joint family

def train_joint_fold(resolved: Resolved, inputs: dataset.Inputs, fold: splits.Fold,
                     spec: DeviceSpec, capture_predictions: bool = False,
                     run_dir: Path | None = None, *,
                     on_epoch: Callable[[int, dict, dict], None] | None = None) -> FoldResult:
    """Train one fold of the joint model.

    Beyond the dedicated loop, three things are specific here and each one changes results:

    * **S13 pairing.** The two training streams are shuffled INDEPENDENTLY, so cross-attention sees
      randomly-paired category and region rows. Validation walks both in order. Every banked v18
      joint cell trained this way, and the aligned alternative — which is what a single joint dataset
      would naturally give — is a different training distribution for the shared trunk.
    * **Per-head learning rates.** Three parameter groups at three rates. In the reference these only
      took effect because a driver exported an environment variable; without it the scalar rate
      reached every group and the run was quietly the previous recipe.
    * **Two epoch-selection conventions**, computed from the same recorded series and both reported.
    """
    cfg = resolved.train
    if cfg.family is not TaskFamily.JOINT:
        raise ValueError(f"train_joint_fold is for the joint family, not {cfg.family}")

    seed = fold_seed(cfg.seed, fold.index, decorrelated=cfg.decorrelated_fold_seed)
    seed_everything(seed)

    diag.reset_peak_memory(spec.device)

    cat_train, cat_val, reg_train, reg_val = dataset.joint_streams(inputs, fold, spec.device)
    # Sealed: the epoch loop scores the inner split and the outer fold stays untouched until the
    # checkpoint is fixed. Without this the joint arm selected on the outer fold while the dedicated
    # arms did not, which would bias a joint-vs-STL comparison in the joint's favour.
    _selection = dataset.joint_selection_streams(inputs, fold, spec.device)
    cat_eval, reg_eval = _selection if _selection is not None else (cat_val, reg_val)
    eval_stream = "inner_val" if _selection is not None else "outer_fold"

    model = JointModel(
        feature_size=int(cat_train.x.shape[-1]),
        n_categories=inputs.n_categories,
        n_regions=inputs.n_regions,
        cat_head_params=dict(cfg.cat_head.params) if cfg.cat_head else None,
        reg_head_params=dict(cfg.reg_head.params) if cfg.reg_head else None,
    ).to(spec.device)
    captured_counts, captured_arch = _capture_architecture(model)
    captured_flops = (capacity.measure_flops(model, (cat_train.x[:1], reg_train.x[:1]))
                      if fold.index == 0 else {})
    # The probe no longer forces eager. It used to: taking a second gradient through the TRAINING
    # graph is incompatible with the compiled backward, which donates activation buffers and mutates
    # attention tensors in place. Measured, that cost 35.2% of wall — of which 24.4% was losing
    # compile and only 8.7% was the probe. `gradient_geometry_sidecar` builds its own eager graph on
    # the uncompiled base module instead, so the two are no longer exclusive.
    if spec.can_compile:
        model = torch.compile(model)

    cat_criterion = losses.build(
        inputs.n_categories, cat_train.y.detach().cpu().numpy(),
        logit_adjust_tau=cfg.cat_loss.logit_adjust_tau,
        balanced_weights=cfg.cat_loss.class_weights, device=spec.device,
    )
    # The region criterion is plain cross-entropy, always. It is built independently of the
    # calibration config, which is why logit adjustment can only ever reach the category head.
    reg_criterion = losses.build(
        inputs.n_regions, reg_train.y.detach().cpu().numpy(),
        logit_adjust_tau=0.0, balanced_weights=False, device=spec.device,
    )

    optimizer = _joint_optimizer(model, cfg)
    steps = loaders.steps_per_epoch(len(cat_train), cfg.batch_size)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=[g["lr"] for g in optimizer.param_groups],
        epochs=cfg.epochs, steps_per_epoch=steps,
    )

    train_labels = set(np.unique(reg_train.y.detach().cpu().numpy()).tolist())
    series = {"cat": EpochSeries(), "reg": EpochSeries()}
    train_losses: list[float] = []
    best_selector, best_selector_epoch, best_state = float("-inf"), 0, None
    keep = ckpt.FoldCheckpoints(run_dir, fold.index, cfg.retain_checkpoints, cfg.epochs)
    track_best = capture_predictions or keep.active
    keep.maybe_trajectory(model, 0)
    worst_ambiguity: dict[str, int] = {}
    started = time.time()
    generator = torch.Generator().manual_seed(seed)
    diagnose = diag.FoldDiagnostics() if cfg.diagnostics else None
    health = diag.GradHealth(spec.device, cfg.optim.max_grad_norm) if diagnose else None
    compile_before = diag.compile_snapshot() if diagnose else {}
    if diagnose is not None:
        diagnose.execution = {"compiled": bool(spec.can_compile),
                              "probe": "eager_sidecar" if cfg.grad_geometry else "off",
                              "precision": str(cfg.precision.value), "tf32": bool(spec.can_tf32),
                              "device": str(spec.device)}
    base_model = model._orig_mod if hasattr(model, "_orig_mod") else model
    shared_params = list(base_model.shared_parameters()) if diagnose else []
    shared_groups = base_model.shared_parameter_groups() if diagnose else None

    cat_running = torch.zeros((), device=spec.device)
    reg_running = torch.zeros((), device=spec.device)
    for epoch in range(cfg.epochs):
        model.train()
        running = torch.zeros((), device=spec.device)
        batches = 0
        with (diag.Phase(diagnose.train_seconds, spec.device) if diagnose else _null()):
          for (x_cat, y_cat, _), (x_reg, y_reg, _) in loaders.joint_batches(
            cat_train, reg_train, cfg.batch_size, shuffle=True,
            pairing=cfg.pairing, generator=generator,
          ):
            optimizer.zero_grad(set_to_none=True)
            with spec.autocast():
                cat_logits, reg_logits = model(x_cat, x_reg)
                cat_loss = cat_criterion(cat_logits, y_cat)
                reg_loss = reg_criterion(reg_logits, y_reg)
                # (1 - w) * region + w * category — the scalarisation the recipe pins.
                loss = (1.0 - cfg.category_weight) * reg_loss + cfg.category_weight * cat_loss
            # Gradient geometry on the FIRST batch of each epoch, matching the reference's cadence
            # so the values are comparable. Taken before the training backward, with its own graph
            # retention, so it neither consumes nor perturbs the step that follows.
            if diagnose is not None and cfg.grad_geometry and batches == 0:
                # Its own forward on its own graph — see `gradient_geometry_sidecar`. Taken before
                # the training backward, and RNG-forked, so it neither consumes nor perturbs the
                # step that follows.
                cosine, n_cat, n_reg, by_group = diag.gradient_geometry_sidecar(
                    model, ((x_cat, y_cat, None), (x_reg, y_reg, None)),
                    cat_criterion, reg_criterion, spec.autocast, shared_params, spec.device,
                    shared_groups)
                diagnose.grad_cosine.append(cosine)
                diagnose.grad_norm_cat.append(n_cat)
                diagnose.grad_norm_reg.append(n_reg)
                diagnose.grad_groups.append(by_group)
            loss.backward()
            total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.optim.max_grad_norm)
            if health is not None:
                health.observe(total_norm.detach())
                cat_running += cat_loss.detach()
                reg_running += reg_loss.detach()
            optimizer.step()
            scheduler.step()
            running += loss.detach()
            batches += 1
        train_losses.append(float(running.item() / max(batches, 1)))
        if diagnose is not None:
            # The two per-task sums ride along in the SAME host read, so the epoch still costs one.
            cat_sum, reg_sum = health.flush(diagnose, [cat_running, reg_running])
            diagnose.learning_rates.append([g["lr"] for g in optimizer.param_groups])
            diagnose.train_loss_cat.append(cat_sum / max(batches, 1))
            diagnose.train_loss_reg.append(reg_sum / max(batches, 1))
            cat_running.zero_(); reg_running.zero_()

        with (diag.Phase(diagnose.val_seconds, spec.device) if diagnose else _null()):
            cat_metrics, reg_metrics = _validate_joint(
                model, cat_eval, reg_eval, cat_criterion, reg_criterion, cfg, spec,
                inputs.n_categories, inputs.n_regions, train_labels,
            )
        for key, value in reg_metrics.pop("_ambiguous", {}).items():
            worst_ambiguity[key] = max(worst_ambiguity.get(key, 0), value)

        # The joint checkpoint is ONE checkpoint, chosen by the selector on the inner split — both
        # reported task metrics must come from it. Tracking per-task bests would describe two
        # virtual models and quietly contradict the "one model, one forward" headline.
        keep.maybe_trajectory(model, epoch + 1)
        if track_best:
            # `reg_f1` is passed even though geom_simple ignores it: the OTHER selector,
            # joint_f1_mean, reads it, and omitting it here made this tracker disagree with
            # `standard_scores` on half of a 2 000-trial fuzz — a sidecar epoch that silently
            # differs from the one result.json reports.
            # `top10_acc` cru: o estimando reportado (§1). Tem de ser a MESMA chave que
            # `standard_scores` usa, senão o cross-check adiante aborta o fold.
            value = scoring.selector_value(cfg.selector.value, cat_metrics.get("f1", 0.0),
                                           reg_metrics.get("top10_acc", 0.0),
                                           reg_f1=reg_metrics.get("f1"))
            if epoch >= cfg.min_best_epoch and value > best_selector:
                best_selector, best_selector_epoch = value, epoch + 1
                best_state = ckpt.snapshot(model)                  # see the dedicated path
        cat_metrics.pop("_ambiguous", None)
        series["cat"].log(cat_metrics)
        series["reg"].log(reg_metrics)
        if on_epoch is not None:
            on_epoch(epoch, cat_metrics, reg_metrics)

    joint_keep_pending = keep.active and best_state is not None

    joint_rows = None
    if capture_predictions:
        if best_state is None:
            raise RuntimeError("no epoch qualified for joint selection; cannot persist predictions")
        base_of(model).load_state_dict(best_state)
        # The one-shot outer evaluation. Both tasks, ONE checkpoint, the sealed streams.
        cat_out, reg_out = _validate_joint(
            model, cat_val, reg_val, cat_criterion, reg_criterion, cfg, spec,
            inputs.n_categories, inputs.n_regions, train_labels, capture_rows=True)
        joint_rows = {"epoch": best_selector_epoch,
                      "cat": cat_out.pop("_rows"), "reg": reg_out.pop("_rows")}

    selection = scoring.standard_scores(
        series["cat"].as_mapping(), series["reg"].as_mapping(),
        selector=cfg.selector.value, min_best_epoch=cfg.min_best_epoch,
    )
    if joint_keep_pending:
        reported_epoch = ((selection or {}).get("joint_best") or {}).get("epoch")
        if reported_epoch != best_selector_epoch:
            raise RuntimeError(
                f"the tracked joint checkpoint (epoch {best_selector_epoch}) disagrees with the "
                f"selector (epoch {reported_epoch}); refusing to retain it.")
        keep.selected(best_state, best_selector_epoch, best_selector)

    if joint_rows is not None:
        # The same cross-check the dedicated path has. Rows persisted from one epoch under a
        # result.json that reports another is the failure this whole capture path exists to avoid,
        # and it would be invisible: both numbers are plausible and neither names the other.
        reported = (selection or {}).get("joint_best") or {}
        if reported.get("epoch") != joint_rows["epoch"]:
            raise RuntimeError(
                f"the tracked joint checkpoint (epoch {joint_rows['epoch']}) disagrees with the "
                f"selector (epoch {reported.get('epoch')}). Persisting rows from the wrong model is "
                f"worse than persisting none, so this fails rather than guesses.")

    diag_summary = {}
    if diagnose:
        diagnose.peak_memory_bytes = diag.peak_memory(spec.device)
        diagnose.compile_counters = diag.compile_counters(compile_before)
        diag_summary = diagnose.summary()
        # Convergence is reported per task: the two heads peak at different epochs, which is the
        # whole reason two selection conventions exist.
        diag_summary["cat_convergence"] = diag.convergence(series["cat"].values.get("f1", []))
        diag_summary["reg_convergence"] = diag.convergence(
            series["reg"].values.get("top10_acc_indist", []))

    empty_cache(spec.device)
    return FoldResult(
        fold=fold.index, seed=seed, epochs=cfg.epochs, wall_seconds=time.time() - started,
        train_loss=train_losses, val=series, selection=selection,
        ambiguous_rows=worst_ambiguity, diagnostics=diag_summary,
        parameter_counts=captured_counts, architecture=captured_arch,
        rows=joint_rows, eval_stream=eval_stream, checkpoints=keep.manifest(),
        flops=captured_flops,
    )


def _joint_optimizer(model, cfg):
    """Three parameter groups at three rates: category head, region head, shared trunk.

    Group ORDER and membership are load-bearing — AdamW applies weight decay per group, so a
    parameter in the wrong group is optimised under a different rule.
    """
    base = model._orig_mod if hasattr(model, "_orig_mod") else model
    groups = [
        {"params": list(base.category_parameters()), "lr": cfg.optim.cat_lr, "name": "cat"},
        {"params": list(base.region_parameters()), "lr": cfg.optim.reg_lr, "name": "reg"},
        {"params": list(base.shared_parameters()), "lr": cfg.optim.shared_lr, "name": "shared"},
    ]
    covered = sum(len(g["params"]) for g in groups)
    total = len(list(base.parameters()))
    if covered != total:
        raise ValueError(
            f"the parameter partition covers {covered} tensors of {total}; a parameter outside "
            f"every group would never be optimised, and one in two groups would be stepped twice"
        )
    return torch.optim.AdamW(groups, weight_decay=cfg.optim.weight_decay,
                             eps=cfg.optim.eps, betas=(0.9, cfg.optim.beta2))


@torch.no_grad()
def _validate_joint(model, cat_val, reg_val, cat_criterion, reg_criterion, cfg, spec,
                    n_categories: int, n_regions: int, train_labels: set[int],
                    capture_rows: bool = False):
    """One joint validation pass. Aligned by construction: both streams are walked in order."""
    model.eval()
    keep = cfg.keep_top_k if capture_rows else 0
    cat_acc = metrics.StreamingMetrics(n_categories, top_k=(3, 5), keep_top_k=keep)
    reg_acc = metrics.StreamingMetrics(n_regions, top_k=(1, 5, 10), keep_top_k=keep)
    cat_loss_total = torch.zeros((), device=spec.device)
    reg_loss_total = torch.zeros((), device=spec.device)
    seen = 0

    for (x_cat, y_cat, _), (x_reg, y_reg, _) in loaders.joint_batches(
        cat_val, reg_val, cfg.batch_size, shuffle=False, pairing=cfg.pairing
    ):
        with spec.autocast():
            cat_logits, reg_logits = model(x_cat, x_reg)
        cat_loss_total += cat_criterion(cat_logits, y_cat).detach() * y_cat.shape[0]
        reg_loss_total += reg_criterion(reg_logits, y_reg).detach() * y_reg.shape[0]
        cat_acc.update(cat_logits.detach(), y_cat)
        reg_acc.update(reg_logits.detach(), y_reg)
        seen += int(y_cat.shape[0])

    cat_metrics = cat_acc.compute()
    cat_metrics["loss"] = float(cat_loss_total.item() / max(seen, 1))

    reg_metrics = reg_acc.compute()
    reg_metrics["loss"] = float(reg_loss_total.item() / max(seen, 1))
    _, targets, rank, hits = reg_acc.concat()
    reg_metrics.update(metrics.in_distribution(targets, rank, hits, train_labels))
    reg_metrics.update(metrics.region_score(reg_metrics))
    reg_metrics["_ambiguous"] = {f"top{k}": v for k, v in reg_acc.ambiguous.items()}

    if capture_rows:
        for accumulator, out in ((cat_acc, cat_metrics), (reg_acc, reg_metrics)):
            preds, targets, rank, _ = accumulator.concat()
            out["_rows"] = {"y_pred": preds.cpu().numpy(), "y_true": targets.cpu().numpy(),
                            "rank_of_true": rank.cpu().numpy(),
                            **{k: v.cpu().numpy() for k, v in accumulator.distribution().items()}}

    return cat_metrics, reg_metrics
