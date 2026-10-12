"""Tests for the T1.4 calibrated STL loss (logit-adjust + focal + tail-loss).

The load-bearing properties for the T1.4 gate:
  1. All-default == plain CrossEntropyLoss (no silent behaviour change).
  2. focal_gamma=0 == CE; logit_adjust_tau=0 adds no offset.
  3. The class prior / counts come from the TRAIN labels passed in only
     (leak guard — the factory never sees val).
  4. Every config produces a finite scalar with a finite gradient.
"""

import pytest
import torch
import torch.nn.functional as F

from losses.calibrated import CalibratedLoss, build_calibrated_loss


def _logits_targets(n=64, c=7, seed=0):
    g = torch.Generator().manual_seed(seed)
    logits = torch.randn(n, c, generator=g, requires_grad=True)
    targets = torch.randint(0, c, (n,), generator=g)
    return logits, targets


class TestCalibratedLoss:
    def test_default_equals_cross_entropy(self):
        logits, targets = _logits_targets()
        crit = CalibratedLoss(num_classes=7)
        got = crit(logits, targets)
        exp = F.cross_entropy(logits, targets)
        assert torch.allclose(got, exp, atol=1e-6), (got.item(), exp.item())

    def test_label_smoothing_matches_torch(self):
        logits, targets = _logits_targets()
        crit = CalibratedLoss(num_classes=7, label_smoothing=0.1)
        got = crit(logits, targets)
        exp = F.cross_entropy(logits, targets, label_smoothing=0.1)
        assert torch.allclose(got, exp, atol=1e-6)

    def test_focal_gamma_zero_equals_ce(self):
        logits, targets = _logits_targets()
        crit = CalibratedLoss(num_classes=7, focal_gamma=0.0)
        assert torch.allclose(crit(logits, targets), F.cross_entropy(logits, targets), atol=1e-6)

    def test_focal_reduces_loss_on_easy_examples(self):
        # Confident-correct logits -> focal down-weights -> loss < CE.
        c = 5
        logits = torch.full((16, c), -5.0)
        targets = torch.arange(16) % c
        logits[torch.arange(16), targets] = 5.0
        logits.requires_grad_(True)
        ce = F.cross_entropy(logits, targets)
        focal = CalibratedLoss(num_classes=c, focal_gamma=2.0)(logits, targets)
        assert focal < ce

    def test_logit_adjust_tau_zero_is_noop(self):
        logits, targets = _logits_targets()
        y_train = torch.randint(0, 7, (200,))
        crit = build_calibrated_loss(7, y_train, logit_adjust_tau=0.0)
        assert crit.la_offset is None
        assert torch.allclose(crit(logits, targets), F.cross_entropy(logits, targets), atol=1e-6)

    def test_logit_adjust_offset_is_train_prior(self):
        # Build a skewed train distribution; la_offset must equal tau*log(prior).
        y_train = torch.cat([torch.zeros(900, dtype=torch.long),
                             torch.ones(100, dtype=torch.long)])  # 2 classes, 9:1
        tau = 1.0
        crit = build_calibrated_loss(2, y_train, logit_adjust_tau=tau)
        prior = torch.tensor([0.9, 0.1])
        expected = tau * torch.log(prior + 1e-12)
        assert torch.allclose(crit.la_offset, expected, atol=1e-4), crit.la_offset

    def test_logit_adjust_uses_train_only_not_val(self):
        # Factory only receives y_train; a different val distribution cannot
        # change the offset (the leak guard is "pass train labels only").
        y_train = torch.cat([torch.zeros(800, dtype=torch.long),
                             torch.ones(200, dtype=torch.long)])
        crit_a = build_calibrated_loss(2, y_train, logit_adjust_tau=1.0)
        # Same train labels, shuffled -> identical offset (order-invariant counts).
        crit_b = build_calibrated_loss(2, y_train[torch.randperm(1000)], logit_adjust_tau=1.0)
        assert torch.allclose(crit_a.la_offset, crit_b.la_offset, atol=1e-6)

    def test_balanced_weight_matches_sklearn_formula(self):
        # 'balanced' must equal N/(C*n_c) — the compute_class_weights formula
        # that the next_cv.py cat ceiling uses.
        y_train = torch.cat([torch.zeros(900, dtype=torch.long),
                             torch.ones(100, dtype=torch.long)])
        crit = build_calibrated_loss(2, y_train, tail_mode="balanced")
        N, C = 1000, 2
        expected = torch.tensor([N / (C * 900), N / (C * 100)])
        assert torch.allclose(crit.cb_weight, expected, atol=1e-5), crit.cb_weight

    def test_cb_weight_upweights_rare_class(self):
        y_train = torch.cat([torch.zeros(900, dtype=torch.long),
                             torch.ones(100, dtype=torch.long)])
        crit = build_calibrated_loss(2, y_train, tail_mode="cb", cb_beta=0.999)
        assert crit.cb_weight is not None
        # rare class (1) gets the larger weight
        assert crit.cb_weight[1] > crit.cb_weight[0]
        # normalised to mean 1
        assert torch.allclose(crit.cb_weight.mean(), torch.tensor(1.0), atol=1e-5)

    def test_ldam_margins_larger_for_rare(self):
        y_train = torch.cat([torch.zeros(900, dtype=torch.long),
                             torch.ones(100, dtype=torch.long)])
        crit = build_calibrated_loss(2, y_train, tail_mode="ldam", ldam_max_m=0.5)
        assert crit.ldam_m is not None
        assert crit.ldam_m[1] > crit.ldam_m[0]  # rare -> bigger margin
        assert pytest.approx(crit.ldam_m.max().item(), abs=1e-5) == 0.5

    @pytest.mark.parametrize("cfg", [
        {"label_smoothing": 0.1},
        {"focal_gamma": 2.0},
        {"logit_adjust_tau": 1.0},
        {"tail_mode": "cb"},
        {"tail_mode": "ldam"},
        {"focal_gamma": 2.0, "logit_adjust_tau": 0.5, "label_smoothing": 0.05},
        {"tail_mode": "ldam", "focal_gamma": 1.0},
    ])
    def test_finite_loss_and_grad(self, cfg):
        logits, targets = _logits_targets(c=7)
        y_train = torch.randint(0, 7, (500,))
        crit = build_calibrated_loss(7, y_train, **cfg)
        loss = crit(logits, targets)
        assert torch.isfinite(loss)
        loss.backward()
        assert torch.isfinite(logits.grad).all()

    def test_many_class_region_scale(self):
        # region target is ~1-5k classes; ensure no shape/overflow issue.
        c = 1500
        logits, targets = _logits_targets(n=128, c=c)
        y_train = torch.randint(0, c, (5000,))
        for cfg in ({"logit_adjust_tau": 1.0}, {"tail_mode": "cb"}, {"tail_mode": "ldam"}):
            crit = build_calibrated_loss(c, y_train, **cfg)
            loss = crit(logits, targets)
            assert torch.isfinite(loss)

    def test_missing_counts_raises(self):
        with pytest.raises(ValueError):
            build_calibrated_loss(7, None, logit_adjust_tau=1.0)
        with pytest.raises(ValueError):
            build_calibrated_loss(7, None, tail_mode="cb")
