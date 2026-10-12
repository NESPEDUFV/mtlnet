"""Byte-identity guards for the perf P1 mask simplifications (train_perf_multifold).

P1 removed two data-dependent ``.any()`` guards (host syncs + torch.compile graph
breaks) from the STAN reg head, replacing them with unconditional, vectorised ops.
These tests pin the claim that the rewrite is *mathematically* byte-identical to the
old guarded logic (any residual difference under ``--compile`` is FP-reduction-order
drift from the compiler, not a logic change).
"""

import torch


def _old_forward_features_mask(pm: torch.Tensor) -> torch.Tensor:
    """The pre-P1 guarded all-padded fixup (next_stan/head.py)."""
    pm = pm.clone()
    all_padded = pm.all(dim=1)
    if all_padded.any():
        pm = pm.clone()
        pm[all_padded, -1] = False
    return pm


def _new_forward_features_mask(pm: torch.Tensor) -> torch.Tensor:
    """The P1 vectorised, unconditional rewrite (no .any(), no graph break)."""
    pm = pm.clone()
    all_padded = pm.all(dim=1)
    pm[:, -1] = pm[:, -1] & ~all_padded
    return pm


def test_forward_features_mask_equivalence():
    torch.manual_seed(0)
    B, S = 96, 9
    pm = torch.rand(B, S) < 0.4
    pm[3] = True          # fully-padded row
    pm[17] = True         # fully-padded row
    pm[5, :] = False      # fully-valid row
    assert torch.equal(_old_forward_features_mask(pm), _new_forward_features_mask(pm))


def test_forward_features_mask_equivalence_no_fully_padded():
    # The common case: no row is fully padded → the old guard was a no-op; the new
    # unconditional write must leave the mask unchanged.
    torch.manual_seed(1)
    pm = torch.rand(64, 9) < 0.3
    pm[(pm.all(dim=1)), 0] = False  # ensure no fully-padded row
    assert torch.equal(_old_forward_features_mask(pm), _new_forward_features_mask(pm))


def test_apply_prior_masked_fill_equivalence():
    # masked_fill is the identity for an all-False mask → unconditional == guarded.
    torch.manual_seed(2)
    B, C = 80, 128
    for pad in (torch.zeros(B, 1, dtype=torch.bool), torch.rand(B, 1) < 0.25):
        tp = torch.randn(B, C)
        guarded = tp.clone()
        if pad.any():
            guarded = guarded.masked_fill(pad, 0.0)
        unconditional = tp.masked_fill(pad, 0.0)
        assert torch.equal(guarded, unconditional)
