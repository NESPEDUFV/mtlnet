"""Regression tests for F49 — λ=0.0 isolation gradient flow.

The F49 study (`docs/findings/F49_LAMBDA0_DECOMPOSITION_GAP.md`)
relies on two load-bearing claims about ``MTLnetCrossAttn``:

(4a) **Loss-side λ=0 is NOT a clean architectural isolation.** Under
     ``static_weight(category_weight=0.0)`` the cat ENCODER still receives
     gradient, because the reg stream queries cat-encoder outputs as K/V
     via ``_CrossAttnBlock.cross_ba(Q=b, K=a, V=a)``. The cat HEAD and
     ``cat_final_ln`` get zero gradient (their only consumer is
     ``out_cat`` which is zero-weighted in the loss). This test is the
     smoke alarm for any future refactor that breaks the K/V gradient
     path — without it, the F49 decomposition argument silently
     collapses into the original (now-known-flawed) 2-way decomposition.

(4b) **Encoder-frozen + AdamW must not silently decay frozen weights.**
     ``setup_per_head_optimizer`` filters ``requires_grad=False`` from
     every param group so AdamW's ``weight_decay·θ`` term cannot fire
     on frozen params. This test snapshots ``category_encoder.weight``'s
     norm before and after ``optimizer.step()`` to catch a regression
     where someone removes the filter and AdamW silently shrinks the
     frozen cat encoder weights toward zero across training.
"""

from __future__ import annotations

import torch
from torch.nn import CrossEntropyLoss

from tests.test_integration.conftest import (
    EMBED_DIM,
    NUM_CLASSES,
    SEQ_LEN,
    seed_everything,
)


def _build_check2hgi_model():
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


def _make_batch(batch_size: int = 4):
    """Synthetic (cat_input, next_input, cat_target, next_target) tuple
    matching the check2HGI preset's expected shapes. Both heads are
    sequential under CHECK2HGI_NEXT_REGION but their factory
    (`_build_next_head`) returns a single class prediction per sequence,
    so targets are 1D ``[B]``."""
    cat_in = torch.randn(batch_size, SEQ_LEN, EMBED_DIM)
    next_in = torch.randn(batch_size, SEQ_LEN, EMBED_DIM)
    cat_target = torch.randint(0, NUM_CLASSES, (batch_size,))
    next_target = torch.randint(0, NUM_CLASSES, (batch_size,))
    return cat_in, next_in, cat_target, next_target


def _joint_loss(
    cat_logits: torch.Tensor,
    next_logits: torch.Tensor,
    cat_target: torch.Tensor,
    next_target: torch.Tensor,
    category_weight: float,
) -> torch.Tensor:
    """static_weight(category_weight) joint loss for the test.

    Mirrors ``StaticWeightLoss.get_weighted_loss``: total =
    (1 - category_weight) * L_next + category_weight * L_cat.
    """
    ce = CrossEntropyLoss()
    cat_loss = ce(cat_logits, cat_target)
    next_loss = ce(next_logits, next_target)
    return (1.0 - category_weight) * next_loss + category_weight * cat_loss


def test_lossside_lambda0_cat_encoder_receives_gradient():
    """(4a) Under loss-side λ=0, cat encoder's gradient through cross-attn
    K/V must be non-zero. This is the load-bearing claim of F49."""
    seed_everything()
    model = _build_check2hgi_model()
    model.train()  # need dropout active so BN-style stuff is realistic
    cat_in, next_in, cat_target, next_target = _make_batch()
    cat_logits, next_logits = model((cat_in, next_in))
    loss = _joint_loss(
        cat_logits, next_logits, cat_target, next_target, category_weight=0.0,
    )
    loss.backward()

    # The cat encoder MUST receive gradient through cross_ba(Q=b, K=a, V=a)
    # in each `_CrossAttnBlock`. This is the load-bearing assertion of F49.
    cat_enc_grads_nonzero = [
        (n, p.grad.abs().sum().item())
        for n, p in model.category_encoder.named_parameters()
        if p.grad is not None
    ]
    assert cat_enc_grads_nonzero, (
        "category_encoder has no parameters with .grad — gradient flow "
        "through cross_ba's K/V is broken; F49 decomposition is invalid."
    )
    total_cat_enc_grad = sum(g for _, g in cat_enc_grads_nonzero)
    assert total_cat_enc_grad > 0, (
        f"category_encoder gradient sum is {total_cat_enc_grad}; expected "
        f"non-zero gradient via cross_ba K/V. F49's gradient-flow claim "
        f"silently false."
    )


def test_lossside_lambda0_cat_head_receives_no_gradient():
    """(4a, complement) The cat HEAD (category_poi) should receive zero
    gradient under loss-side λ=0 — its only consumer is ``out_cat`` which
    is zero-weighted in the joint loss. The loss-side ablation freezes
    the head implicitly via the loss, but the encoder is what F49 needs
    to control explicitly."""
    seed_everything()
    model = _build_check2hgi_model()
    model.train()
    cat_in, next_in, cat_target, next_target = _make_batch()
    cat_logits, next_logits = model((cat_in, next_in))
    loss = _joint_loss(
        cat_logits, next_logits, cat_target, next_target, category_weight=0.0,
    )
    loss.backward()

    cat_head_grads = [
        (n, p.grad.abs().sum().item() if p.grad is not None else 0.0)
        for n, p in model.category_poi.named_parameters()
    ]
    # Either grad is None (PyTorch may skip allocation if there's no path)
    # or grad sum is exactly 0.0 (path exists but all upstream weights → 0).
    for n, g in cat_head_grads:
        assert g == 0.0, (
            f"category_poi.{n} grad sum = {g}; expected 0 under loss-side "
            f"λ=0. cat head should be cleanly silenced by zero loss weight."
        )


def test_encoder_frozen_lambda0_weights_unchanged_after_step():
    """(4b) Encoder-frozen variant: after applying requires_grad=False on
    category_encoder + category_poi, building the per-head optimizer (which
    must filter frozen params), running forward + backward + step, the
    cat encoder weights must be unchanged within fp32 epsilon. Catches the
    AdamW silent-decay bug if anyone removes the requires_grad filter from
    setup_per_head_optimizer."""
    from training.helpers import setup_per_head_optimizer

    seed_everything()
    model = _build_check2hgi_model()
    # F49 freeze logic — same as mtl_cv.py applies.
    for p in model.category_encoder.parameters():
        p.requires_grad_(False)
    for p in model.category_poi.parameters():
        p.requires_grad_(False)
    model.category_encoder.eval()

    optimizer = setup_per_head_optimizer(
        model,
        cat_lr=1e-3, reg_lr=3e-3, shared_lr=1e-3,
        weight_decay=0.05,  # project default; this is what would trigger silent decay
        eps=1e-8,
    )

    # Snapshot every frozen cat-encoder param's norm before training.
    snapshots = {
        n: p.detach().clone()
        for n, p in model.category_encoder.named_parameters()
    }
    cat_head_snapshots = {
        n: p.detach().clone()
        for n, p in model.category_poi.named_parameters()
    }

    # One full training step, mimicking the actual training loop.
    cat_in, next_in, cat_target, next_target = _make_batch()
    model.train()
    # category_encoder.eval() was called above — that toggles the cat
    # encoder's dropout off without affecting the rest of the model.
    cat_logits, next_logits = model((cat_in, next_in))
    loss = _joint_loss(
        cat_logits, next_logits, cat_target, next_target, category_weight=0.0,
    )
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Frozen params: must be bit-exact unchanged. AdamW with weight_decay=0.05
    # applied to a param with grad=None would shift the weights by exactly
    # `lr * wd * theta` per step — this assertion catches that.
    for n, before in snapshots.items():
        after = dict(model.category_encoder.named_parameters())[n].detach()
        torch.testing.assert_close(
            after, before,
            rtol=0.0, atol=1e-7,
            msg=lambda m: (
                f"category_encoder.{n} changed after optimizer.step() "
                f"despite requires_grad=False. Likely cause: "
                f"setup_per_head_optimizer is not filtering requires_grad=False "
                f"from the param groups, so AdamW's weight_decay decays "
                f"the frozen weights silently. Original message: {m}"
            ),
        )
    for n, before in cat_head_snapshots.items():
        after = dict(model.category_poi.named_parameters())[n].detach()
        torch.testing.assert_close(
            after, before, rtol=0.0, atol=1e-7,
            msg=lambda m: f"category_poi.{n} changed after step: {m}",
        )


def test_encoder_frozen_optimizer_groups_have_no_frozen_params():
    """(4b, structural) After the freeze + per-head optimizer construction,
    each AdamW param group must contain only ``requires_grad=True`` params.
    The encoder-frozen variant's 'cat' group must therefore be empty."""
    from training.helpers import setup_per_head_optimizer

    seed_everything()
    model = _build_check2hgi_model()
    for p in model.category_encoder.parameters():
        p.requires_grad_(False)
    for p in model.category_poi.parameters():
        p.requires_grad_(False)

    optimizer = setup_per_head_optimizer(
        model,
        cat_lr=1e-3, reg_lr=3e-3, shared_lr=1e-3,
        weight_decay=0.05,
    )

    for pg in optimizer.param_groups:
        for p in pg["params"]:
            assert p.requires_grad, (
                f"optimizer param_group '{pg.get('name', '?')}' contains a "
                f"param with requires_grad=False. The setup_per_head_optimizer "
                f"filter is not active. AdamW will silently decay this param "
                f"via weight_decay across training, invalidating any "
                f"freeze-based ablation."
            )

    # The 'cat' group should be empty in the encoder-frozen variant.
    cat_group = next(
        pg for pg in optimizer.param_groups if pg.get("name") == "cat"
    )
    assert len(cat_group["params"]) == 0, (
        f"Expected 0 trainable cat-specific params under encoder-freeze; "
        f"got {len(cat_group['params'])}. Either the freeze did not "
        f"propagate or the optimizer filter is broken."
    )
