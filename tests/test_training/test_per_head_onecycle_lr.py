"""Regression tests for the per-head-LR-under-OneCycle fix + AdamW beta2 wiring.

Pins two behaviors a future setup_scheduler/optimizer refactor could silently revert:
  1. MTL_ONECYCLE_PER_HEAD_LR — without it, OneCycleLR broadcasts a SCALAR max_lr to every
     param group (the bug: --cat-lr/--reg-lr/--shared-lr inert). With it=1, max_lr is a
     per-group LIST = each group's own lr, so the per-head LRs actually apply.
  2. AdamW betas=(0.9, beta2) wiring from setup_optimizer / setup_per_head_optimizer.
"""
import os

import torch

from src.training.helpers import (
    setup_optimizer,
    setup_per_head_optimizer,
    setup_scheduler,
)


def _two_group_opt():
    m = torch.nn.Linear(4, 4)
    groups = [
        {"name": "cat", "params": [m.weight], "lr": 1e-3},
        {"name": "reg", "params": [m.bias], "lr": 3e-3},
    ]
    return torch.optim.AdamW([dict(g) for g in groups])


def _max_lrs(opt):
    return [pg["max_lr"] for pg in opt.param_groups]


def test_onecycle_per_head_lr_off_is_uniform(monkeypatch):
    """Flag OFF (default) → scalar max_lr broadcast → every head peaks at max_lr (the inert path)."""
    monkeypatch.delenv("MTL_ONECYCLE_PER_HEAD_LR", raising=False)
    opt = _two_group_opt()
    setup_scheduler(opt, max_lr=3e-3, epochs=2, steps_per_epoch=10, scheduler_type="onecycle")
    assert _max_lrs(opt) == [3e-3, 3e-3], "default onecycle must broadcast the scalar max_lr (byte-identical champion)"


def test_onecycle_per_head_lr_on_is_per_group(monkeypatch):
    """Flag ON → per-group max_lr list = each group's own lr → per-head LRs actually apply."""
    monkeypatch.setenv("MTL_ONECYCLE_PER_HEAD_LR", "1")
    opt = _two_group_opt()
    setup_scheduler(opt, max_lr=3e-3, epochs=2, steps_per_epoch=10, scheduler_type="onecycle")
    assert _max_lrs(opt) == [1e-3, 3e-3], "MTL_ONECYCLE_PER_HEAD_LR=1 must give per-group peaks [cat 1e-3, reg 3e-3]"


def test_onecycle_per_head_lr_single_group_untouched(monkeypatch):
    """Flag ON but a single-group optimizer → unchanged (the guard requires >1 group)."""
    monkeypatch.setenv("MTL_ONECYCLE_PER_HEAD_LR", "1")
    m = torch.nn.Linear(4, 4)
    opt = setup_optimizer(m, learning_rate=1e-4, weight_decay=0.05)
    setup_scheduler(opt, max_lr=3e-3, epochs=2, steps_per_epoch=10, scheduler_type="onecycle")
    assert _max_lrs(opt) == [3e-3]


def test_adam_beta2_default_and_override():
    m = torch.nn.Linear(4, 4)
    assert setup_optimizer(m, 1e-4, 0.05).param_groups[0]["betas"] == (0.9, 0.999)
    assert setup_optimizer(m, 1e-4, 0.05, betas=(0.9, 0.95)).param_groups[0]["betas"] == (0.9, 0.95)
    # per-head builder threads betas onto every group
    g = setup_per_head_optimizer(
        type("M", (), {
            "cat_specific_parameters": lambda s: [m.weight],
            "reg_specific_parameters": lambda s: [m.bias],
            "shared_parameters": lambda s: [],
        })(),
        cat_lr=1e-3, reg_lr=3e-3, shared_lr=1e-3, weight_decay=0.05, betas=(0.9, 0.95),
    )
    assert all(pg["betas"] == (0.9, 0.95) for pg in g.param_groups)
