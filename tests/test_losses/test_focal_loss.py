"""Tests for Focal Loss implementation."""

import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F

from losses.focal import FocalLoss


class TestFocalLoss:
    """Test suite for Focal Loss."""

    def test_initialization(self):
        """Test FocalLoss initialization with different parameters."""
        # Default initialization
        loss_fn = FocalLoss()
        assert loss_fn.gamma == 2.0
        assert loss_fn.reduction == 'mean'
        assert loss_fn.alpha is None

        # Custom initialization
        loss_fn_custom = FocalLoss(alpha=0.25, gamma=1.0, reduction='sum')
        assert loss_fn_custom.alpha == 0.25
        assert loss_fn_custom.gamma == 1.0
        assert loss_fn_custom.reduction == 'sum'

        # Per-class alpha as Tensor
        alpha_tensor = torch.tensor([0.1, 0.3, 0.6])
        loss_fn_tensor = FocalLoss(alpha=alpha_tensor)
        assert isinstance(loss_fn_tensor.alpha, torch.Tensor)
        assert loss_fn_tensor.alpha.shape == (3,)

        # reduction='none'
        loss_fn_none = FocalLoss(reduction='none')
        assert loss_fn_none.reduction == 'none'

    def test_balanced_classes(self):
        """Test focal loss with gamma=0 equals CrossEntropyLoss (within 1e-5)."""
        torch.manual_seed(42)
        n_samples, n_classes = 32, 4
        logits = torch.randn(n_samples, n_classes)
        targets = torch.randint(0, n_classes, (n_samples,))

        focal_fn = FocalLoss(gamma=0.0, reduction='mean')
        ce_fn = nn.CrossEntropyLoss(reduction='mean')

        focal_val = focal_fn(logits, targets)
        ce_val = ce_fn(logits, targets)

        # When gamma=0, focal_weight = (1 - pt)^0 = 1, so focal == CE
        assert abs(focal_val.item() - ce_val.item()) < 1e-5

    def test_imbalanced_classes(self):
        """Test focal loss with imbalanced classes runs without error and returns finite positive scalar."""
        torch.manual_seed(0)
        # Heavily skewed targets (mostly class 0)
        n_samples, n_classes = 100, 5
        logits = torch.randn(n_samples, n_classes)
        targets = torch.zeros(n_samples, dtype=torch.long)
        targets[95:] = torch.randint(1, n_classes, (5,))

        loss_fn = FocalLoss(gamma=2.0, reduction='mean')
        result = loss_fn(logits, targets)

        assert result.ndim == 0  # scalar
        assert torch.isfinite(result)
        assert result.item() > 0

    def test_gamma_parameter(self):
        """Test effect of gamma parameter: higher gamma → lower loss for high-confidence logits."""
        torch.manual_seed(7)
        n_samples, n_classes = 16, 3
        # Create high-confidence logits: very large values on correct class
        targets = torch.randint(0, n_classes, (n_samples,))
        logits = torch.zeros(n_samples, n_classes)
        logits[range(n_samples), targets] = 10.0  # high confidence on correct class

        loss_low_gamma = FocalLoss(gamma=0.5, reduction='mean')(logits, targets)
        loss_high_gamma = FocalLoss(gamma=4.0, reduction='mean')(logits, targets)

        # With high confidence, pt ≈ 1, so (1-pt)^gamma is tiny.
        # Higher gamma → even smaller focal weight → lower loss
        assert loss_high_gamma.item() < loss_low_gamma.item()

    def test_alpha_parameter(self):
        """Test effect of alpha parameter: works with scalar alpha and per-class Tensor alpha."""
        torch.manual_seed(3)
        n_samples, n_classes = 20, 3
        logits = torch.randn(n_samples, n_classes)
        targets = torch.randint(0, n_classes, (n_samples,))

        # Scalar alpha
        loss_scalar = FocalLoss(alpha=0.5, gamma=2.0)(logits, targets)
        assert torch.isfinite(loss_scalar)
        assert loss_scalar.item() > 0

        # Per-class Tensor alpha
        alpha_tensor = torch.tensor([0.2, 0.3, 0.5])
        loss_tensor = FocalLoss(alpha=alpha_tensor, gamma=2.0)(logits, targets)
        assert torch.isfinite(loss_tensor)
        assert loss_tensor.item() > 0

        # Scalar alpha=1.0 should scale uniformly (loss != 0)
        loss_alpha1 = FocalLoss(alpha=1.0, gamma=2.0)(logits, targets)
        loss_no_alpha = FocalLoss(alpha=None, gamma=2.0)(logits, targets)
        # alpha=1.0 multiplies focal_weight by 1 → same as no alpha
        assert abs(loss_alpha1.item() - loss_no_alpha.item()) < 1e-5


class TestFocalLossComparison:
    """Compare Focal Loss with CrossEntropyLoss."""

    def test_convergence_rate(self):
        """Test focal(gamma=2) <= CE for same inputs (focal_weight ≤ 1, alpha=None)."""
        torch.manual_seed(99)
        n_samples, n_classes = 64, 5
        logits = torch.randn(n_samples, n_classes)
        targets = torch.randint(0, n_classes, (n_samples,))

        focal_fn = FocalLoss(gamma=2.0, alpha=None, reduction='mean')
        ce_fn = nn.CrossEntropyLoss(reduction='mean')

        focal_val = focal_fn(logits, targets)
        ce_val = ce_fn(logits, targets)

        # focal_weight = (1 - pt)^gamma <= 1, so focal_loss <= CE per sample
        # The means preserve this inequality
        assert focal_val.item() <= ce_val.item() + 1e-6
