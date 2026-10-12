"""W6 --freeze-reg-stream contract (the MIRROR of --freeze-cat-stream).

The category-side encoder-isolation probe freezes the REGION stream
(``next_encoder`` + ``next_poi``) so it cannot co-adapt as a cat-helper via
cross-attention K/V, run with ``--category-weight 1.0`` (reg-loss=0). These
tests pin: (1) the config field default; (2) the freeze loop in
``mtl_cv`` is BIJECTIVE — it freezes exactly the region stream and leaves the
category stream trainable (so the cat-win-isolation is clean).

The freeze's *propagation to the optimizer* (0 trainable reg params) is
additionally guarded at runtime in mtl_cv.py (RuntimeError at fold 0 if the
reg group still has trainable params), and the real-model attribute names
(``next_encoder``/``next_poi``) are verified against the champion dualtower.
"""

from types import SimpleNamespace

import torch
import torch.nn as nn

from configs.experiment import ExperimentConfig
from training.runners.mtl_cv import _apply_stream_freezes


def test_config_field_defaults_false():
    cfg = ExperimentConfig.default_mtl("t", "alabama", "check2hgi")
    assert getattr(cfg, "freeze_reg_stream", None) is False
    assert getattr(cfg, "freeze_cat_stream", None) is False


class _MiniDualTower(nn.Module):
    """Minimal stand-in with the four submodules the freeze logic targets,
    matching the champion's attribute names (category_encoder/category_poi =
    cat stream; next_encoder/next_poi = reg stream)."""

    def __init__(self):
        super().__init__()
        self.category_encoder = nn.Linear(8, 8)
        self.category_poi = nn.Linear(8, 7)
        self.next_encoder = nn.Linear(8, 8)
        self.next_poi = nn.Linear(8, 16)


def test_freeze_reg_stream_is_bijective():
    m = _MiniDualTower()
    # Drive the REAL extracted helper (guards against drift in the refactor).
    _apply_stream_freezes(m, SimpleNamespace(freeze_reg_stream=True, freeze_cat_stream=False))
    # region stream frozen
    assert all(not p.requires_grad for p in m.next_encoder.parameters())
    assert all(not p.requires_grad for p in m.next_poi.parameters())
    assert not m.next_encoder.training  # .eval() took → dropout disabled
    # category stream untouched (the cat-win we are isolating must still train)
    assert all(p.requires_grad for p in m.category_encoder.parameters())
    assert all(p.requires_grad for p in m.category_poi.parameters())


def test_freeze_reg_is_mirror_of_freeze_cat():
    """Freezing the cat stream and freezing the reg stream are exact mirrors:
    each freezes its own encoder+head and leaves the other fully trainable."""
    m = _MiniDualTower()
    _apply_stream_freezes(m, SimpleNamespace(freeze_cat_stream=True, freeze_reg_stream=False))
    assert all(not p.requires_grad for p in m.category_encoder.parameters())
    assert all(not p.requires_grad for p in m.category_poi.parameters())
    assert all(p.requires_grad for p in m.next_encoder.parameters())
    assert all(p.requires_grad for p in m.next_poi.parameters())


def test_freeze_noop_when_both_flags_false():
    """The champion path (both flags off) must leave EVERY stream trainable."""
    m = _MiniDualTower()
    _apply_stream_freezes(m, SimpleNamespace(freeze_cat_stream=False, freeze_reg_stream=False))
    assert all(p.requires_grad for p in m.parameters())
