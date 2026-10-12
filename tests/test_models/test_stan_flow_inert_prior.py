"""Inert α·log_T prior skip (MTL_SKIP_INERT_PRIOR) — byte-identity + gating.

The v18 dedicated-reg and joint cells run the STAN-flow heads with
``freeze_alpha=True alpha_init=0.0`` and no live transition prior, yet the
forward still paid a [B, C] gather + masked_fill + mul + add per batch to add an
exact zero. ``_inert_prior`` skips that work. These tests pin:

  1. skip vs legacy path is BITWISE identical (same weights, same aux), with a
     zeros log_T *and* with a non-trivial finite log_T;
  2. a learnable α (freeze_alpha=False) is never skipped and still receives grad;
  3. a frozen α != 0 is never skipped (the prior is live);
  4. the dualtower's ``_apply_prior`` honours the same contract.
"""

import copy

import pytest
import torch

import models.next.next_stan_flow.head as sf_head
import models.next.next_stan_flow_dualtower.head as dt_head
from data.aux_side_channel import _clear_aux, _publish_aux


B, S, D, C = 8, 9, 16, 37


@pytest.fixture(autouse=True)
def _aux_cleanup():
    yield
    _clear_aux()


def _stan_flow_pair(monkeypatch, **kwargs):
    """Two NextHeadStanFlow with identical weights: one skip-enabled, one legacy."""
    torch.manual_seed(0)
    monkeypatch.setattr(sf_head, "_SKIP_INERT_PRIOR", True)
    fast = sf_head.NextHeadStanFlow(embed_dim=D, num_classes=C, **kwargs)
    monkeypatch.setattr(sf_head, "_SKIP_INERT_PRIOR", False)
    legacy = sf_head.NextHeadStanFlow(embed_dim=D, num_classes=C, **kwargs)
    legacy.load_state_dict(copy.deepcopy(fast.state_dict()))
    return fast.eval(), legacy.eval()


def test_inert_skip_bitwise_identical_zeros_logT(monkeypatch):
    fast, legacy = _stan_flow_pair(monkeypatch, freeze_alpha=True, alpha_init=0.0)
    assert fast._inert_prior and not legacy._inert_prior
    x = torch.randn(B, S, D)
    _publish_aux(torch.randint(0, C, (B,)))
    with torch.no_grad():
        out_fast = fast(x)
        out_legacy = legacy(x)
    assert torch.equal(out_fast, out_legacy)


def test_inert_skip_bitwise_identical_real_logT(monkeypatch):
    """Even with a non-trivial finite log_T loaded, frozen α=0 output is bitwise equal."""
    fast, legacy = _stan_flow_pair(monkeypatch, freeze_alpha=True, alpha_init=0.0)
    log_T = torch.randn(C, C)
    with torch.no_grad():
        fast.log_T.copy_(log_T)
        legacy.log_T.copy_(log_T)
    x = torch.randn(B, S, D)
    _publish_aux(torch.randint(0, C, (B,)))
    with torch.no_grad():
        assert torch.equal(fast(x), legacy(x))


def test_learnable_alpha_not_skipped_and_gets_grad(monkeypatch):
    monkeypatch.setattr(sf_head, "_SKIP_INERT_PRIOR", True)
    torch.manual_seed(0)
    head = sf_head.NextHeadStanFlow(
        embed_dim=D, num_classes=C, freeze_alpha=False, alpha_init=0.0,
    )
    assert not head._inert_prior
    assert isinstance(head.alpha, torch.nn.Parameter)
    with torch.no_grad():
        head.log_T.copy_(torch.randn(C, C))
    _publish_aux(torch.randint(0, C, (B,)))
    head.train()
    out = head(torch.randn(B, S, D))
    out.sum().backward()
    assert head.alpha.grad is not None


def test_frozen_nonzero_alpha_not_skipped(monkeypatch):
    monkeypatch.setattr(sf_head, "_SKIP_INERT_PRIOR", True)
    torch.manual_seed(0)
    head = sf_head.NextHeadStanFlow(
        embed_dim=D, num_classes=C, freeze_alpha=True, alpha_init=0.1,
    ).eval()
    assert not head._inert_prior
    with torch.no_grad():
        head.log_T.copy_(torch.randn(C, C))
    x = torch.randn(B, S, D)
    _clear_aux()
    with torch.no_grad():
        bare = head(x)          # aux None → stan + α·0
    _publish_aux(torch.randint(0, C, (B,)))
    with torch.no_grad():
        primed = head(x)        # live prior must actually move the logits
    assert not torch.equal(bare, primed)


def test_dualtower_apply_prior_inert_skip(monkeypatch):
    torch.manual_seed(0)
    monkeypatch.setattr(dt_head, "_SKIP_INERT_PRIOR", True)
    fast = dt_head.NextHeadStanFlowDualTower(
        embed_dim=64, num_classes=C, raw_embed_dim=D,
        freeze_alpha=True, alpha_init=0.0,
    )
    monkeypatch.setattr(dt_head, "_SKIP_INERT_PRIOR", False)
    legacy = dt_head.NextHeadStanFlowDualTower(
        embed_dim=64, num_classes=C, raw_embed_dim=D,
        freeze_alpha=True, alpha_init=0.0,
    )
    legacy.load_state_dict(copy.deepcopy(fast.state_dict()))
    assert fast._inert_prior and not legacy._inert_prior
    logits = torch.randn(B, C)
    _publish_aux(torch.randint(0, C, (B,)))
    with torch.no_grad():
        assert torch.equal(fast._apply_prior(logits), legacy._apply_prior(logits))
