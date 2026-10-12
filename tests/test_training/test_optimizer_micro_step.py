"""Deterministic coverage for the extracted optimizer micro-step
(``_optimizer_micro_step`` in mtl_cv — the ``should_step`` body: partial-trailing-group
rescale → alternating-SGD inactive-zero → grad-clip → finite-guard → optimizer/scheduler
step → zero_grad).

The AL champion parity runs grad-accum=1 and no alternating, so it does NOT exercise the
partial-group rescale or the alt-inactive-zero branches. These tests pin those branches
with SGD(lr=1) so the post-step param value is a closed-form function of the (possibly
rescaled / zeroed) gradient.
"""

import math

import torch
import torch.nn as nn

from training.runners.mtl_cv import _optimizer_micro_step


class _TwoParam(nn.Module):
    def __init__(self, a=1.0, b=1.0):
        super().__init__()
        self.a = nn.Parameter(torch.tensor([float(a)]))
        self.b = nn.Parameter(torch.tensor([float(b)]))


class _NoParamLoss:
    """Stub MTL criterion with no learnable parameters (→ _criterion_parameters == [])."""


def _sgd1(model):
    opt = torch.optim.SGD(model.parameters(), lr=1.0)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda _e: 1.0)  # constant lr
    return opt, sched


def _set_grads(model, ga=0.5, gb=0.5):
    model.a.grad = torch.tensor([float(ga)])
    model.b.grad = torch.tensor([float(gb)])


def _call(model, opt, sched, *, loss, ga_steps, accumulated, alt=None,
          already_bp=False, max_gn=0.0, strict=False):
    _optimizer_micro_step(
        model, opt, sched, _NoParamLoss(),
        loss=loss, gradient_accumulation_steps=ga_steps,
        accumulated_in_group=accumulated, already_backpropagated=already_bp,
        alt_inactive_params=alt, max_grad_norm=max_gn,
        epoch_idx=0, batch_idx=0, strict=strict, nanguard=False,
    )


def test_full_group_no_rescale():
    # accumulated == ga_steps → no rescale; SGD(lr=1): p -= grad.
    m = _TwoParam(a=1.0); opt, sched = _sgd1(m); _set_grads(m, ga=0.5)
    _call(m, opt, sched, loss=torch.tensor(0.3), ga_steps=2, accumulated=2)
    assert math.isclose(m.a.item(), 1.0 - 0.5, abs_tol=1e-7)
    assert m.a.grad is None or float(m.a.grad) == 0.0  # zero_grad(set_to_none) ran


def test_partial_trailing_group_rescales():
    # accumulated(1) != ga_steps(2) → grad *= 2/1 = 2 BEFORE step → p -= 2*grad.
    m = _TwoParam(a=1.0); opt, sched = _sgd1(m); _set_grads(m, ga=0.5)
    _call(m, opt, sched, loss=torch.tensor(0.3), ga_steps=2, accumulated=1)
    assert math.isclose(m.a.item(), 1.0 - 2.0 * 0.5, abs_tol=1e-7)  # = 0.0


def test_already_backpropagated_skips_rescale():
    # already_backpropagated → the rescale guard is False even on a partial group.
    m = _TwoParam(a=1.0); opt, sched = _sgd1(m); _set_grads(m, ga=0.5)
    _call(m, opt, sched, loss=torch.tensor(0.3), ga_steps=2, accumulated=1, already_bp=True)
    assert math.isclose(m.a.item(), 1.0 - 0.5, abs_tol=1e-7)  # no doubling


def test_alt_inactive_params_zeroed():
    # alt_inactive_params=[b] → b.grad zeroed → b frozen this step; a still updates.
    m = _TwoParam(a=1.0, b=2.0); opt, sched = _sgd1(m); _set_grads(m, ga=0.5, gb=0.5)
    _call(m, opt, sched, loss=torch.tensor(0.3), ga_steps=1, accumulated=1, alt=[m.b])
    assert math.isclose(m.a.item(), 1.0 - 0.5, abs_tol=1e-7)
    assert math.isclose(m.b.item(), 2.0, abs_tol=1e-7)  # unchanged (grad zeroed)


def test_nonfinite_loss_skips_step():
    # NaN loss → guard_finite_step returns False (strict off) → step SKIPPED, params held,
    # but grads are still cleared.
    m = _TwoParam(a=1.0); opt, sched = _sgd1(m); _set_grads(m, ga=0.5)
    _call(m, opt, sched, loss=torch.tensor(float("nan")), ga_steps=1, accumulated=1)
    assert math.isclose(m.a.item(), 1.0, abs_tol=1e-7)  # no step taken
    assert m.a.grad is None or float(m.a.grad) == 0.0   # zero_grad still ran


def test_grad_clip_caps_update():
    # max_grad_norm=0.1 on a grad of norm 0.5 → clip coef 0.2 → effective grad 0.1 → p -= 0.1.
    m = _TwoParam(a=1.0); opt, sched = _sgd1(m)
    m.a.grad = torch.tensor([0.5]); m.b.grad = torch.tensor([0.0])
    _call(m, opt, sched, loss=torch.tensor(0.3), ga_steps=1, accumulated=1, max_gn=0.1)
    assert math.isclose(m.a.item(), 1.0 - 0.1, abs_tol=1e-6)
