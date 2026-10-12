"""Tests for ``ScheduledStaticWeightLoss`` linear and step modes.

Step mode (F50 B3 / F62) implements the two-phase MTL recipe:
phase 1 (epochs < warmup_epochs) holds cat_weight at ``cat_weight_start``
(use 0.0 for reg-only pretrain), then a hard transition to
``cat_weight_end`` for the rest of training (joint phase).
"""
from __future__ import annotations

import pytest
import torch

from losses.scheduled_static.loss import ScheduledStaticWeightLoss


def _make(mode="linear", **kw):
    defaults = dict(
        n_tasks=2,
        device=torch.device("cpu"),
        cat_weight_start=0.0,
        cat_weight_end=0.75,
        total_epochs=50,
        warmup_epochs=10,
        mode=mode,
    )
    defaults.update(kw)
    return ScheduledStaticWeightLoss(**defaults)


def test_linear_mode_default():
    """Existing linear mode is unchanged: ramps over total_epochs - warmup_epochs."""
    loss = _make(mode="linear", cat_weight_start=0.75, cat_weight_end=0.25, warmup_epochs=0)
    loss.set_epoch(0)
    assert loss._current_cat_weight() == pytest.approx(0.75)
    loss.set_epoch(49)
    assert loss._current_cat_weight() == pytest.approx(0.25)


def test_step_mode_phase_1_reg_only():
    """B3 phase 1: cat_weight=0 for first N1 epochs (reg-only pretrain)."""
    loss = _make(mode="step", cat_weight_start=0.0, cat_weight_end=0.75, warmup_epochs=10)
    for e in range(10):
        loss.set_epoch(e)
        assert loss._current_cat_weight() == 0.0, f"epoch {e} should be cat_weight=0"


def test_step_mode_phase_2_jumps_to_end():
    """B3 phase 2: hard transition at warmup_epochs to cat_weight_end."""
    loss = _make(mode="step", cat_weight_start=0.0, cat_weight_end=0.75, warmup_epochs=10)
    loss.set_epoch(10)
    assert loss._current_cat_weight() == pytest.approx(0.75)
    loss.set_epoch(49)
    assert loss._current_cat_weight() == pytest.approx(0.75)
    # Crucially, no linear ramp between epochs 10-49 in step mode.
    loss.set_epoch(30)
    assert loss._current_cat_weight() == pytest.approx(0.75)


def test_step_mode_get_weighted_loss_phase1_zeros_cat():
    """Sanity: phase 1 with cat_weight=0 produces a weighted loss equal
    to the reg loss alone (cat contribution = 0)."""
    loss = _make(mode="step", cat_weight_start=0.0, cat_weight_end=0.75, warmup_epochs=5)
    loss.set_epoch(2)  # phase 1
    losses = torch.tensor([0.4, 1.5], requires_grad=True)  # [reg, cat]
    out, info = loss.get_weighted_loss(losses)
    # weights = [1-cat_w, cat_w] = [1.0, 0.0] → loss = 0.4
    assert out.item() == pytest.approx(0.4)
    assert info["cat_weight_current"] == 0.0


def test_step_mode_get_weighted_loss_phase2_uses_end():
    loss = _make(mode="step", cat_weight_start=0.0, cat_weight_end=0.75, warmup_epochs=5)
    loss.set_epoch(10)  # phase 2
    losses = torch.tensor([0.4, 1.5], requires_grad=True)
    out, info = loss.get_weighted_loss(losses)
    # weights = [0.25, 0.75] → 0.25*0.4 + 0.75*1.5 = 1.225
    assert out.item() == pytest.approx(1.225, rel=1e-5)
    assert info["cat_weight_current"] == pytest.approx(0.75)


def test_invalid_mode_raises():
    with pytest.raises(ValueError, match="mode must be"):
        _make(mode="cosine")


def test_warmup_zero_in_step_mode_starts_at_end_immediately():
    """Edge case: warmup_epochs=0 in step mode means cat_weight=cat_weight_end
    from epoch 0 — equivalent to plain StaticWeightLoss(cat_weight_end)."""
    loss = _make(
        mode="step",
        cat_weight_start=0.0,
        cat_weight_end=0.75,
        warmup_epochs=0,
        total_epochs=50,
    )
    for e in [0, 5, 25, 49]:
        loss.set_epoch(e)
        assert loss._current_cat_weight() == pytest.approx(0.75)
