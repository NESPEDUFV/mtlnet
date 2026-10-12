"""Tests for PCGrad (Project Conflicting Gradients)."""

import pytest
import torch
import torch.nn as nn

from losses.pcgrad import PCGrad


class TestPCGrad:
    """Test suite for PCGrad."""

    def test_initialization(self):
        """Test PCGrad initialization."""
        device = torch.device('cpu')

        pc = PCGrad(n_tasks=2, device=device)
        assert pc.n_tasks == 2
        assert pc.reduction == 'sum'  # default

        pc_mean = PCGrad(n_tasks=3, device=device, reduction='mean')
        assert pc_mean.n_tasks == 3
        assert pc_mean.reduction == 'mean'

    def test_gradient_projection(self):
        """Test gradient projection: shared params receive gradients after backward."""
        torch.manual_seed(42)
        device = torch.device('cpu')

        shared = nn.Linear(4, 4)
        head1 = nn.Linear(4, 2)
        head2 = nn.Linear(4, 2)

        x = torch.randn(8, 4)
        out = shared(x)
        logits1 = head1(out)
        logits2 = head2(out)
        targets = torch.randint(0, 2, (8,))

        loss1 = nn.CrossEntropyLoss()(logits1, targets)
        loss2 = nn.CrossEntropyLoss()(logits2, targets)
        losses = torch.stack([loss1, loss2])

        pc = PCGrad(n_tasks=2, device=device)
        pc.backward(losses, shared_parameters=list(shared.parameters()))

        # After backward, shared parameters should have gradients
        for p in shared.parameters():
            assert p.grad is not None

    def test_non_conflicting_gradients(self):
        """Test that backward returns (None, {})."""
        torch.manual_seed(1)
        device = torch.device('cpu')

        shared = nn.Linear(4, 4)
        head1 = nn.Linear(4, 2)
        head2 = nn.Linear(4, 2)

        x = torch.randn(8, 4)
        out = shared(x)
        logits1 = head1(out)
        logits2 = head2(out)
        targets = torch.randint(0, 2, (8,))

        loss1 = nn.CrossEntropyLoss()(logits1, targets)
        loss2 = nn.CrossEntropyLoss()(logits2, targets)
        losses = torch.stack([loss1, loss2])

        pc = PCGrad(n_tasks=2, device=device)
        result = pc.backward(losses, shared_parameters=list(shared.parameters()))

        assert result == (None, {})

    def test_orthogonal_gradients(self):
        """Test behavior with orthogonal gradients: param.grad is not None after backward."""
        device = torch.device('cpu')

        # param[0] only used by loss1, param[1] only used by loss2 → orthogonal gradients
        param = nn.Parameter(torch.tensor([1.0, 0.0]))

        loss1 = param[0] ** 2          # gradient only on dim 0
        loss2 = (param[1] - 1.0) ** 2  # gradient only on dim 1
        losses = torch.stack([loss1, loss2])

        pc = PCGrad(n_tasks=2, device=device)
        pc.backward(losses, shared_parameters=[param])

        assert param.grad is not None
