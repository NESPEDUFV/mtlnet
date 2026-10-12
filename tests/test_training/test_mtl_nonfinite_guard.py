"""Regression test for the DEFAULT-ON non-finite guard in the MTL trainer.

Background: the CUDA MTL trainer runs forward+loss under fp16 autocast with NO GradScaler.
At large class count (CA 8501 regions) the wide reg logits overflow fp16's 65504 ceiling ->
inf/NaN. `clip_grad_norm_` then returns total_norm=inf -> clip_coef = max_norm/inf = 0, which
zeros every finite grad AND turns the offending grad into inf*0 = NaN; `optimizer.step()` writes
that NaN into the SHARED backbone -> both heads permanently collapse to a degenerate floor (the
deterministic "CA ep30 collapse"; docs/studies/closing_data/CA_MTL_DIVERGENCE.md).

The real fix is precision (bf16 autocast `MTL_AUTOCAST_BF16=1`, or fp32 `MTL_DISABLE_AMP=1`).
`guard_finite_step` is the defense-in-depth that PINS the invariant so a silent collapse can
never recur even if some future state/precision overflows:
  1. healthy (finite) step -> proceed (no-op; byte-identical to pre-guard behaviour);
  2. non-finite loss/grad -> SKIP the optimizer step by default (weights stay finite, no poison);
  3. non-finite under MTL_STRICT=1 -> RAISE (fail-loud; board runs use MTL_STRICT=1).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from training.runners.mtl_cv import guard_finite_step  # noqa: E402


def test_finite_step_proceeds_python_and_tensor():
    # property 1: a healthy step proceeds (no skip, no raise) — keeps the trainer byte-identical
    assert guard_finite_step(1.0, 0.5) is True
    assert guard_finite_step(torch.tensor(2.2), torch.tensor(0.31)) is True
    # boundary: large-but-finite grad norm (e.g. pre-clip ~3.5 seen in healthy bf16) still proceeds
    assert guard_finite_step(3.9, 7.0) is True


@pytest.mark.parametrize("total_norm,loss", [
    (float("inf"), 0.5),         # inf grad norm (the clip-by-inf-norm poison path)
    (float("nan"), 0.5),         # nan grad norm
    (1.0, float("nan")),         # nan loss
    (1.0, float("inf")),         # inf loss
    (torch.tensor(float("inf")), torch.tensor(0.5)),  # tensor inputs (as called in the loop)
])
def test_nonfinite_skips_by_default(total_norm, loss):
    # property 2: non-finite -> SKIP (return False), do NOT raise without strict
    assert guard_finite_step(total_norm, loss, epoch=30, batch=7, strict=False) is False


@pytest.mark.parametrize("total_norm,loss", [
    (float("inf"), 0.5),
    (1.0, float("nan")),
    (torch.tensor(float("nan")), torch.tensor(0.5)),
])
def test_nonfinite_raises_under_strict(total_norm, loss):
    # property 3: non-finite under MTL_STRICT=1 -> fail-loud (board runs use MTL_STRICT=1)
    with pytest.raises(RuntimeError, match="non-finite"):
        guard_finite_step(total_norm, loss, epoch=30, batch=7, strict=True)


def test_clip_by_inf_norm_poison_is_what_we_guard_against():
    """Document+pin the actual failure mechanism. clip_grad_norm_ over a param set containing one
    inf grad returns total_norm=inf -> clip_coef = max_norm/inf = 0. Multiplying by 0 ZEROES the
    finite grads and turns the inf grad into inf*0 = NaN; `optimizer.step()` would then write that
    NaN into the SHARED backbone. guard_finite_step sees the inf total_norm and skips BEFORE step."""
    p_ok = torch.nn.Parameter(torch.ones(3))
    p_bad = torch.nn.Parameter(torch.ones(3))
    p_ok.grad = torch.ones(3)
    p_bad.grad = torch.full((3,), float("inf"))
    total_norm = torch.nn.utils.clip_grad_norm_([p_ok, p_bad], 1.0)
    assert not math.isfinite(float(total_norm))            # the poison signal the guard sees (inf)
    assert (p_ok.grad == 0).all()                          # finite grad got ZEROED by clip-by-inf
    assert torch.isnan(p_bad.grad).any()                   # offending grad became NaN (inf*0) -> poison
    assert guard_finite_step(total_norm, 0.5) is False     # -> guard skips the poisoning step
