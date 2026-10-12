"""Shared training helpers.

Deduplicates compute_class_weights / setup_optimizer / setup_fold patterns
that were copy-pasted across category, next, and MTL cross-validation files.
"""

import os
from typing import Iterable, Optional, Union

import numpy as np
import torch
from sklearn.utils import compute_class_weight
from torch.optim import AdamW
from torch.optim.lr_scheduler import (
    ConstantLR,
    CosineAnnealingLR,
    LambdaLR,
    LinearLR,
    OneCycleLR,
    SequentialLR,
)


def compute_class_weights(
    targets: Union[np.ndarray, torch.Tensor],
    num_classes: int,
    device: torch.device,
) -> torch.Tensor:
    """Compute balanced class weights from training targets.

    Uses sklearn's 'balanced' mode: n_samples / (n_classes * bincount).

    Accepts either a numpy array or a ``torch.Tensor`` (any device).
    Tensors are routed through ``.cpu().numpy()`` exactly once at this
    boundary — sklearn requires CPU numpy and several call sites have
    targets pre-loaded onto MPS by PR #8's on-device-tensor optimization.
    Centralizing the conversion here means future call sites cannot
    silently re-introduce the ``can't convert mps:0 device type tensor
    to numpy`` bug.

    Args:
        targets: 1D class labels. Either ``np.ndarray`` or ``torch.Tensor``
            (CPU/MPS/CUDA — handled transparently).
        num_classes: Total number of classes.
        device: Device to place the resulting weight tensor on.

    Returns:
        Float32 tensor of shape (num_classes,) on the given device.
    """
    if isinstance(targets, torch.Tensor):
        targets = targets.detach().cpu().numpy()
    # sklearn's ``compute_class_weight`` requires every class in ``classes``
    # to appear in ``y``. That's fine for 7-class category labels but fails
    # for high-cardinality heads (e.g. next_region with ~10^3 classes, many
    # of which are absent from any given train fold). Fill weights only
    # for observed classes and default to 1.0 for absent classes — the
    # head will never predict an absent class as positive, so its weight
    # is inert; keeping it at 1.0 preserves CE normalisation.
    present = np.unique(targets)
    weights_full = np.ones(num_classes, dtype=np.float32)
    if present.size > 0:
        weights_present = compute_class_weight('balanced', classes=present, y=targets)
        weights_full[present] = weights_present
    return torch.tensor(weights_full, dtype=torch.float32, device=device)


def setup_optimizer(
    model: torch.nn.Module,
    learning_rate: float,
    weight_decay: float,
    eps: float = 1e-8,
    extra_parameters: Iterable[torch.nn.Parameter] | None = None,
    betas: tuple[float, float] = (0.9, 0.999),
) -> AdamW:
    """Create an AdamW optimizer matching the project's conventions.

    Args:
        model: Model whose parameters to optimize.
        learning_rate: Base learning rate.
        weight_decay: L2 regularization weight.
        eps: Adam epsilon for numerical stability.
        extra_parameters: Optional non-model parameters, such as learnable
            MTL loss weights.
        betas: AdamW (beta1, beta2). Lowering beta2 (e.g. 0.95) adapts the
            2nd-moment faster — a standard large-batch stabilizer.

    Returns:
        Configured AdamW optimizer.
    """
    parameters = [p for p in model.parameters() if p.requires_grad]
    if extra_parameters is not None:
        parameters.extend(p for p in extra_parameters if p.requires_grad)

    return AdamW(
        parameters,
        lr=learning_rate,
        weight_decay=weight_decay,
        eps=eps,
        betas=betas,
    )


def setup_per_head_optimizer(
    model: torch.nn.Module,
    cat_lr: float,
    reg_lr: float,
    shared_lr: float,
    weight_decay: float,
    eps: float = 1e-8,
    extra_parameters: Iterable[torch.nn.Parameter] | None = None,
    reg_encoder_lr: float | None = None,
    reg_head_lr: float | None = None,
    alpha_no_weight_decay: bool = False,
    betas: tuple[float, float] = (0.9, 0.999),
) -> AdamW:
    """Build an AdamW with three param groups (per-head LR).

    Requires the model to expose ``cat_specific_parameters``,
    ``reg_specific_parameters`` and ``shared_parameters``. Currently
    implemented by ``MTLnetCrossAttn`` only — scoped to the
    cross-attention MTL backbone.

    Group layout:
      * ``cat``    — cat encoder + cat head  → ``cat_lr``
      * ``reg``    — next encoder + next head → ``reg_lr``
      * ``shared`` — cross-attn blocks + cat/next final_ln → ``shared_lr``

    ``extra_parameters`` (e.g. learnable MTL loss weights) ride along
    with the ``reg`` group since they are typically tied to reg-loss
    backward dynamics.
    """
    for required in ("cat_specific_parameters", "reg_specific_parameters",
                     "shared_parameters"):
        if not hasattr(model, required):
            raise ValueError(
                f"Per-head LR optimizer requires model.{required}(); "
                f"{type(model).__name__} does not expose it. "
                f"Currently supported: MTLnetCrossAttn."
            )
    # Filter out frozen params before constructing AdamW. Without this,
    # AdamW applies `weight_decay * theta` to params with grad=None on
    # every step, silently shrinking frozen weights toward zero across
    # training (matters for any freeze-based ablation). Reg-side
    # `extra_parameters` are typically learnable scalars; we still filter
    # them for consistency.
    cat_params = [p for p in model.cat_specific_parameters() if p.requires_grad]
    reg_params = [p for p in model.reg_specific_parameters() if p.requires_grad]
    shared_params = [p for p in model.shared_parameters() if p.requires_grad]
    if extra_parameters is not None:
        reg_params.extend(p for p in extra_parameters if p.requires_grad)

    # When ``alpha_no_weight_decay``, peel α (a single scalar learnable
    # in ``next_getnext_hard*`` heads) out of the reg group into its own
    # zero-WD group: AdamW WD=0.05 applies a constant pull-toward-zero
    # every step, which for the single α scalar fights the gradient-driven
    # growth needed for the late-window α reach.
    alpha_params: list[torch.nn.Parameter] = []
    if alpha_no_weight_decay and hasattr(model, "next_poi"):
        alpha = getattr(model.next_poi, "alpha", None)
        if isinstance(alpha, torch.nn.Parameter) and alpha.requires_grad:
            alpha_params = [alpha]
            alpha_id = id(alpha)
            reg_params = [p for p in reg_params if id(p) != alpha_id]

    # Same treatment for the dual-tower fusion scalar β
    # (`priv + β·aux_proj(shared)`, init 0.1): WD=0.05 pulls it toward 0,
    # suppressing the shared→reg pathway. Env-gated probe MTL_BETA_NO_WD=1
    # peels β into the zero-WD group (folded into alpha_no_wd, so no new
    # scheduler group is needed). Default unset → no-op.
    if os.environ.get("MTL_BETA_NO_WD") == "1" and hasattr(model, "next_poi"):
        beta = getattr(model.next_poi, "beta", None)
        if isinstance(beta, torch.nn.Parameter) and beta.requires_grad:
            beta_id = id(beta)
            reg_params = [p for p in reg_params if id(p) != beta_id]
            alpha_params = alpha_params + [beta]

    # Split reg_params into encoder vs head when EITHER reg_encoder_lr or
    # reg_head_lr is set (lets the α scalar in the reg head run a higher
    # effective LR than the encoder; under cat_weight=0.75 α's gradient is
    # shrunk 4x and otherwise never grows enough).
    # If only one is set, the other defaults to reg_lr.
    if (reg_encoder_lr is not None or reg_head_lr is not None) and hasattr(model, "next_encoder"):
        _enc_lr = float(reg_encoder_lr) if reg_encoder_lr is not None else float(reg_lr)
        _head_lr = float(reg_head_lr) if reg_head_lr is not None else float(reg_lr)
        encoder_param_ids = {id(p) for p in model.next_encoder.parameters()}
        reg_encoder_params = [p for p in reg_params if id(p) in encoder_param_ids]
        reg_head_params = [p for p in reg_params if id(p) not in encoder_param_ids]
        groups = [
            {"name": "cat",         "params": cat_params,         "lr": cat_lr},
            {"name": "reg_encoder", "params": reg_encoder_params, "lr": _enc_lr},
            {"name": "reg_head",    "params": reg_head_params,    "lr": _head_lr},
            {"name": "shared",      "params": shared_params,      "lr": shared_lr},
        ]
        if alpha_params:
            groups.append({
                "name": "alpha_no_wd", "params": alpha_params,
                "lr": _head_lr, "weight_decay": 0.0,
            })
        return AdamW(groups, weight_decay=weight_decay, eps=eps, betas=betas)
    groups = [
        {"name": "cat",    "params": cat_params,    "lr": cat_lr},
        {"name": "reg",    "params": reg_params,    "lr": reg_lr},
        {"name": "shared", "params": shared_params, "lr": shared_lr},
    ]
    if alpha_params:
        groups.append({
            "name": "alpha_no_wd", "params": alpha_params,
            "lr": reg_lr, "weight_decay": 0.0,
        })
    return AdamW(groups, weight_decay=weight_decay, eps=eps, betas=betas)


def _build_reg_head_warmup_decay_lambda(
    warmup_end_step: int,
    plateau_end_step: int,
    total_steps: int,
    peak_mult: float,
):
    """Warmup-decay multiplier shape on reg_head LR.

    Returns a closure step → multiplier in [1.0, peak_mult]:
      0..warmup_end:     linear ramp 1.0 → peak_mult
      warmup_end..peak:  hold peak_mult
      peak..total:       linear decay peak_mult → 1.0

    Applied as a per-group factor on top of AdamW's base LR for the
    reg_head (and α-no-WD if peeled out) groups; other groups keep
    multiplier ≡ 1.0.
    """
    if not (0 < warmup_end_step <= plateau_end_step <= total_steps):
        raise ValueError(
            f"reg_head_warmup_decay shape invalid: warmup={warmup_end_step} "
            f"plateau_end={plateau_end_step} total={total_steps}"
        )
    peak = max(1.0, float(peak_mult))

    def _fn(step: int) -> float:
        if step < warmup_end_step:
            return 1.0 + (peak - 1.0) * (step / warmup_end_step)
        if step < plateau_end_step:
            return peak
        # decay phase
        decay_span = max(1, total_steps - plateau_end_step)
        progress = min(1.0, (step - plateau_end_step) / decay_span)
        return peak - (peak - 1.0) * progress

    return _fn


def _overwrite_base_lr(optimizer, max_lr, multi_group_per_head: bool) -> None:
    """Set every param-group's base lr to ``max_lr`` (single-group / legacy mode only).

    The constant / cosine / warmup_constant schedulers start from the optimizer's base
    lr, so it must be lifted from AdamW's 1e-4 default to ``max_lr``. Per-head mode keeps
    its own per-group LRs, so this is a no-op there.
    """
    if not multi_group_per_head:
        for pg in optimizer.param_groups:
            pg["lr"] = max_lr


def _build_warmup_constant_scheduler(optimizer, max_lr, epochs, steps_per_epoch,
                                     pct_start, multi_group_per_head):
    """Linear warmup over ``pct_start * total_steps`` (default 1/3) from ~3% of target,
    then hold constant at ``max_lr`` forever. Gives cat a stable warmup (no day-1 3e-3
    collapse) and reg a long high-LR plateau. ``pct_start`` doubles as the warmup fraction."""
    _overwrite_base_lr(optimizer, max_lr, multi_group_per_head)
    warmup_frac = float(pct_start) if pct_start is not None else (1.0 / 3.0)
    if not (0 < warmup_frac < 1):
        raise ValueError(f"warmup_constant pct_start must be in (0,1), got {warmup_frac}")
    total_steps = int(epochs * steps_per_epoch)
    warmup_steps = max(1, int(warmup_frac * total_steps))
    warmup = LinearLR(
        optimizer, start_factor=0.033, end_factor=1.0, total_iters=warmup_steps,
    )
    plateau = ConstantLR(optimizer, factor=1.0, total_iters=1)
    return SequentialLR(
        optimizer, schedulers=[warmup, plateau], milestones=[warmup_steps],
    )


def _build_reg_head_warmup_decay_scheduler(optimizer, epochs, steps_per_epoch, peak_mult,
                                           warmup_epochs, plateau_epochs, multi_group_per_head):
    """Per-group warmup-decay LR: only the ``reg_head`` / ``alpha_no_wd`` groups ride the
    base→peak→base shape (warmup_epochs → plateau_epochs → final); all other groups stay at
    base LR. Requires the per-head (multi-group) optimizer."""
    if not multi_group_per_head:
        raise ValueError(
            "reg_head_warmup_decay requires per-head optimizer "
            "(--cat-lr/--reg-lr/--shared-lr); single-group mode unsupported"
        )
    total_steps = int(epochs * steps_per_epoch)
    warmup_end_step = int(warmup_epochs * steps_per_epoch)
    plateau_end_step = int(plateau_epochs * steps_per_epoch)
    warmup_decay_fn = _build_reg_head_warmup_decay_lambda(
        warmup_end_step=max(1, warmup_end_step),
        plateau_end_step=max(warmup_end_step + 1, plateau_end_step),
        total_steps=max(plateau_end_step + 1, total_steps),
        peak_mult=peak_mult,
    )
    identity_fn = lambda _: 1.0
    lambdas = []
    for pg in optimizer.param_groups:
        name = pg.get("name", "")
        lambdas.append(warmup_decay_fn if name in ("reg_head", "alpha_no_wd") else identity_fn)
    return LambdaLR(optimizer, lr_lambda=lambdas)


def setup_scheduler(
    optimizer: AdamW,
    max_lr: float,
    epochs: int,
    steps_per_epoch: int,
    scheduler_type: str = "onecycle",
    pct_start: Optional[float] = None,
    reg_head_warmup_decay_peak_mult: float = 10.0,
    reg_head_warmup_decay_warmup_epochs: int = 5,
    reg_head_warmup_decay_plateau_epochs: int = 15,
    eta_min: float = 0.0,
):
    """Create an LR scheduler matching the project's conventions.

    Args:
        optimizer: The optimizer to schedule.
        max_lr: Peak learning rate. For ``onecycle`` this is the peak;
            for ``constant`` / ``cosine`` this is the initial/reference LR.
        epochs: Total training epochs.
        steps_per_epoch: Number of optimizer steps per epoch.
        scheduler_type: One of ``{"onecycle", "constant", "cosine"}``.
            Default ``onecycle`` preserves legacy behaviour bit-exactly.
        pct_start: For ``onecycle``, fraction of training spent on warmup.
            ``None`` → PyTorch default (0.3). Smaller values push peak LR
            earlier and leave more epochs in the annealing phase.

    Returns:
        Configured scheduler (OneCycleLR / ConstantLR / CosineAnnealingLR).
    """
    if scheduler_type == "onecycle":
        # By default OneCycleLR gets a SCALAR max_lr → PyTorch broadcasts it to every
        # param group, which SILENTLY OVERWRITES the per-head LRs that
        # setup_per_head_optimizer set (cat/reg/shared all peak at the same max_lr).
        # Opt-in MTL_ONECYCLE_PER_HEAD_LR=1 passes max_lr as a per-group LIST (each
        # group's own lr as its peak) so the per-head LRs actually take effect.
        # Default OFF preserves the byte-identical champion (uniform max_lr). See
        # docs/future_works/per_head_lr_onecycle_fix.md.
        _per_head_onecycle = (
            os.environ.get("MTL_ONECYCLE_PER_HEAD_LR") == "1"
            and len(optimizer.param_groups) > 1
        )
        _max_lr = (
            [pg["lr"] for pg in optimizer.param_groups]
            if _per_head_onecycle else max_lr
        )
        kwargs = dict(
            optimizer=optimizer,
            max_lr=_max_lr,
            epochs=epochs,
            steps_per_epoch=steps_per_epoch,
        )
        if pct_start is not None:
            kwargs["pct_start"] = float(pct_start)
        return OneCycleLR(**kwargs)
    # Per-head LR mode builds an optimizer with multiple param groups
    # already at their target LRs. Detect and skip the single-LR overwrite
    # below — otherwise `setup_per_head_optimizer`'s per-group LRs would be
    # silently flattened to `max_lr` here.
    multi_group_per_head = len(optimizer.param_groups) > 1
    if scheduler_type == "constant":
        # Hold LR fixed at `max_lr` for the entire run (no warmup, no
        # annealing). Isolates "more epochs" from "stretched OneCycleLR
        # schedule" when paired with a higher --epochs value.
        # The optimizer's base `lr` must be overwritten to `max_lr`
        # before ConstantLR(factor=1.0) locks it — but only in single-
        # group (legacy) mode. Per-head mode preserves its own LRs.
        _overwrite_base_lr(optimizer, max_lr, multi_group_per_head)
        return ConstantLR(optimizer=optimizer, factor=1.0, total_iters=1)
    if scheduler_type == "cosine":
        # Warmup-free cosine decay from `max_lr` → 0 over total steps.
        # First set the optimizer's base lr to max_lr so CosineAnnealingLR
        # starts at max_lr (not at AdamW's lr=1e-4 default).
        _overwrite_base_lr(optimizer, max_lr, multi_group_per_head)
        return CosineAnnealingLR(
            optimizer=optimizer,
            T_max=int(epochs * steps_per_epoch),
            eta_min=float(eta_min),
        )
    if scheduler_type == "warmup_constant":
        return _build_warmup_constant_scheduler(
            optimizer, max_lr, epochs, steps_per_epoch, pct_start, multi_group_per_head,
        )
    if scheduler_type == "reg_head_warmup_decay":
        return _build_reg_head_warmup_decay_scheduler(
            optimizer, epochs, steps_per_epoch,
            peak_mult=reg_head_warmup_decay_peak_mult,
            warmup_epochs=reg_head_warmup_decay_warmup_epochs,
            plateau_epochs=reg_head_warmup_decay_plateau_epochs,
            multi_group_per_head=multi_group_per_head,
        )
    raise ValueError(
        f"Unknown scheduler_type '{scheduler_type}'; "
        f"expected one of {{'onecycle', 'constant', 'cosine', "
        f"'warmup_constant', 'reg_head_warmup_decay'}}."
    )
