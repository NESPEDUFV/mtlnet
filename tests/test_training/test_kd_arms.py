"""Unit coverage for the R1/R3 log_C co-location KD arms extracted out of
``train_model``'s batch loop (``_log_c_kd_loss`` / ``_cat_kd_loss``).

The champion runs both arms OFF (weight 0 → the no-op fast path), so the AL
metric-parity harness only proves the no-op branch is byte-identical. These
tests exercise the ACTIVE math: each helper is compared term-for-term against an
inline reference replicating the pre-extraction block (so a future edit to the
dense tensor math is caught), plus the no-op gates (weight, warmup, missing/ill-
shaped buffer).
"""

import torch
import torch.nn as nn

from training.runners import mtl_cv
from training.runners.mtl_cv import _log_c_kd_loss, _cat_kd_loss


class _StubReg(nn.Module):
    def __init__(self, log_C=None, log_C_rev=None):
        super().__init__()
        if log_C is not None:
            self.register_buffer("log_C", log_C)
        if log_C_rev is not None:
            self.register_buffer("log_C_rev", log_C_rev)


class _StubModel(nn.Module):
    def __init__(self, next_poi):
        super().__init__()
        self.next_poi = next_poi


def _ref_log_c(pred_a, pred_b, truth_b, log_C, tau, ec):
    """Inline reference = the pre-extraction forward-arm block."""
    ncr = pred_b.shape[-1]
    nca = pred_a.shape[-1]
    phat = torch.softmax(pred_a.float(), dim=-1).detach()
    P = log_C[:ncr, :].float().exp()
    prior = (phat @ P.transpose(0, 1)).clamp_min(1e-12)
    teacher = torch.softmax(torch.log(prior) / tau, dim=-1)
    if ec > 0.0:
        oh = torch.zeros_like(teacher)
        yb = truth_b.clamp(0, ncr - 1).long().unsqueeze(-1)
        oh.scatter_(1, yb, 1.0)
        teacher = (1.0 - ec) * teacher + ec * oh
    slog = torch.log_softmax(pred_b.float() / tau, dim=-1)
    kld = (slog.exp() * (slog - torch.log(teacher.clamp_min(1e-12)))).sum(dim=-1)
    return kld.mean() * (tau * tau)


def _ref_cat(pred_a, pred_b, truth_a, log_C_rev, tau, ec):
    """Inline reference = the pre-extraction reverse-arm block."""
    ncr = pred_b.shape[-1]
    nca = pred_a.shape[-1]
    phat_reg = torch.softmax(pred_b.float(), dim=-1).detach()
    P = log_C_rev[:ncr, :].float().exp()
    prior = (phat_reg @ P).clamp_min(1e-12)
    teacher = torch.softmax(torch.log(prior) / tau, dim=-1)
    if ec > 0.0:
        oh = torch.zeros_like(teacher)
        ya = truth_a.clamp(0, nca - 1).long().unsqueeze(-1)
        oh.scatter_(1, ya, 1.0)
        teacher = (1.0 - ec) * teacher + ec * oh
    slog = torch.log_softmax(pred_a.float() / tau, dim=-1)
    kld = (slog.exp() * (slog - torch.log(teacher.clamp_min(1e-12)))).sum(dim=-1)
    return kld.mean() * (tau * tau)


def _fixture(seed, B=6, n_reg=11, n_cat=7):
    g = torch.Generator().manual_seed(seed)
    pred_a = torch.randn(B, n_cat, generator=g)
    pred_b = torch.randn(B, n_reg, generator=g)
    truth_a = torch.randint(0, n_cat, (B,), generator=g)
    truth_b = torch.randint(0, n_reg, (B,), generator=g)
    log_C = torch.randn(n_reg, n_cat, generator=g)        # P(reg|c) = exp(log_C)
    log_C_rev = torch.randn(n_reg, n_cat, generator=g)    # P(cat|r) = exp(log_C_rev)
    return pred_a, pred_b, truth_a, truth_b, log_C, log_C_rev


def setup_function(_):
    # The one-shot FIRED diagnostics use module globals — reset so each test
    # exercises the same (firing) path and never leaks across tests.
    mtl_cv._LOGC_FIRED = False
    mtl_cv._CATKD_FIRED = False


def test_log_c_arm_matches_reference():
    pa, pb, ta, tb, log_C, _ = _fixture(0)
    m = _StubModel(_StubReg(log_C=log_C))
    for ec in (0.0, 0.3):
        mtl_cv._LOGC_FIRED = False
        got = _log_c_kd_loss(pa, pb, tb, m, weight=0.5, tau=2.0,
                             warmup_epochs=0, ec_lambda=ec, epoch_idx=0)
        ref = _ref_log_c(pa, pb, tb, log_C, tau=2.0, ec=ec)
        assert torch.equal(got, ref), f"log_C arm drift at ec={ec}"


def test_cat_arm_matches_reference():
    pa, pb, ta, tb, _, log_C_rev = _fixture(1)
    m = _StubModel(_StubReg(log_C_rev=log_C_rev))
    for ec in (0.0, 0.3):
        mtl_cv._CATKD_FIRED = False
        got = _cat_kd_loss(pa, pb, ta, m, weight=0.5, tau=1.5,
                           warmup_epochs=0, ec_lambda=ec, epoch_idx=0)
        ref = _ref_cat(pa, pb, ta, log_C_rev, tau=1.5, ec=ec)
        assert torch.equal(got, ref), f"cat arm drift at ec={ec}"


def test_noop_paths_return_none():
    pa, pb, ta, tb, log_C, log_C_rev = _fixture(2)
    m = _StubModel(_StubReg(log_C=log_C, log_C_rev=log_C_rev))
    # weight 0 → no-op
    assert _log_c_kd_loss(pa, pb, tb, m, 0.0, 2.0, 0, 0.0, 0) is None
    assert _cat_kd_loss(pa, pb, ta, m, 0.0, 2.0, 0, 0.0, 0) is None
    # before the R3 warmup → no-op
    assert _log_c_kd_loss(pa, pb, tb, m, 0.5, 2.0, 5, 0.0, 2) is None
    assert _cat_kd_loss(pa, pb, ta, m, 0.5, 2.0, 5, 0.0, 2) is None
    # missing buffer → no-op
    bare = _StubModel(_StubReg())
    assert _log_c_kd_loss(pa, pb, tb, bare, 0.5, 2.0, 0, 0.0, 0) is None
    assert _cat_kd_loss(pa, pb, ta, bare, 0.5, 2.0, 0, 0.0, 0) is None
    # no next_poi at all → no-op
    empty = nn.Module()
    assert _log_c_kd_loss(pa, pb, tb, empty, 0.5, 2.0, 0, 0.0, 0) is None
    assert _cat_kd_loss(pa, pb, ta, empty, 0.5, 2.0, 0, 0.0, 0) is None


def test_shape_mismatch_returns_none():
    pa, pb, ta, tb, _, _ = _fixture(3)
    # log_C with too-few region rows / wrong cat cols → no-op (defensive guard)
    short = _StubModel(_StubReg(log_C=torch.randn(pb.shape[-1] - 1, pa.shape[-1])))
    assert _log_c_kd_loss(pa, pb, tb, short, 0.5, 2.0, 0, 0.0, 0) is None
    wrongcat = _StubModel(_StubReg(log_C=torch.randn(pb.shape[-1], pa.shape[-1] + 1)))
    assert _log_c_kd_loss(pa, pb, tb, wrongcat, 0.5, 2.0, 0, 0.0, 0) is None
