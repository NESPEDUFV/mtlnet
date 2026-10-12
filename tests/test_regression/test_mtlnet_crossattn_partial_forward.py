"""Regression test for CROSSATTN_PARTIAL_FORWARD_CRASH.

Before the fix, ``MTLnetCrossAttn`` inherited ``MTLnet.cat_forward`` /
``MTLnet.next_forward`` — both reference ``self.film`` and
``self.shared_layers`` which do not exist on the cross-attn subclass.
Calling either method raised ``AttributeError: 'MTLnetCrossAttn' object
has no attribute 'film'``, breaking every call site in
``scripts/evaluate.py`` that tries to evaluate a cross-attn checkpoint.

After the fix, both methods are overridden on ``MTLnetCrossAttn`` with
a deterministic zero-opposite-stream approximation. They return tensors
of the correct shape without raising. See
``docs/issues/check2hgi/CROSSATTN_PARTIAL_FORWARD_CRASH.md``.
"""

from __future__ import annotations

import pytest
import torch

from tests.test_integration.conftest import (
    EMBED_DIM,
    NUM_CLASSES,
    SEQ_LEN,
    seed_everything,
)


def _build_crossattn_legacy():
    from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn

    return MTLnetCrossAttn(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
    )


def _build_crossattn_check2hgi():
    from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn
    from tasks import CHECK2HGI_NEXT_REGION
    from tasks.presets import resolve_task_set

    task_set = resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=NUM_CLASSES,
    )
    return MTLnetCrossAttn(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
        task_set=task_set,
    )


def test_crossattn_cat_forward_does_not_crash_legacy():
    """Legacy task_set: A is flat, so cat_forward takes ``[B, 1, D]``."""
    seed_everything()
    model = _build_crossattn_legacy()
    model.eval()
    cat_in = torch.randn(4, 1, EMBED_DIM)
    out = model.cat_forward(cat_in)
    assert out.shape == (4, NUM_CLASSES)


def test_crossattn_next_forward_does_not_crash_legacy():
    seed_everything()
    model = _build_crossattn_legacy()
    model.eval()
    next_in = torch.randn(4, SEQ_LEN, EMBED_DIM)
    out = model.next_forward(next_in)
    assert out.shape == (4, NUM_CLASSES)


def test_crossattn_cat_forward_does_not_crash_check2hgi():
    """check2HGI preset: both slots sequential, A is ``[B, T, D]``."""
    seed_everything()
    model = _build_crossattn_check2hgi()
    model.eval()
    cat_in = torch.randn(4, SEQ_LEN, EMBED_DIM)
    out = model.cat_forward(cat_in)
    assert out.shape[0] == 4


def test_crossattn_next_forward_does_not_crash_check2hgi():
    seed_everything()
    model = _build_crossattn_check2hgi()
    model.eval()
    next_in = torch.randn(4, SEQ_LEN, EMBED_DIM)
    out = model.next_forward(next_in)
    assert out.shape[0] == 4


def test_crossattn_partial_forward_is_deterministic():
    """Calling ``cat_forward`` twice on the same input (eval mode) must
    return identical tensors — the zero-B-stream approximation has no
    RNG source once dropout is disabled."""
    seed_everything()
    model = _build_crossattn_legacy()
    model.eval()
    cat_in = torch.randn(4, 1, EMBED_DIM)
    out1 = model.cat_forward(cat_in)
    out2 = model.cat_forward(cat_in)
    torch.testing.assert_close(out1, out2)
