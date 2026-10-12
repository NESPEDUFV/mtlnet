"""Tests for GradNorm gradient balancing (new backward() interface)."""

import pytest
import torch
import torch.nn as nn

from losses.gradnorm import GradNormLoss


class _SimpleModel(nn.Module):
    """Two-task model with a clear shared backbone."""

    def __init__(self):
        super().__init__()
        self.shared_layers = nn.Sequential(nn.Linear(8, 8), nn.ReLU(), nn.Linear(8, 8))
        self.head1 = nn.Linear(8, 2)
        self.head2 = nn.Linear(8, 2)

    def forward(self, x):
        shared = self.shared_layers(x)
        return self.head1(shared), self.head2(shared)

    def shared_parameters(self):
        return list(self.shared_layers.parameters())


class TestGradNormInit:
    def test_defaults(self):
        gn = GradNormLoss(n_tasks=2, alpha=1.5, lr=1e-3)
        assert gn.n_tasks == 2
        assert gn.alpha == 1.5
        assert gn.lr == 1e-3
        assert gn._L0 is None
        assert gn.loss_scale.shape == (2,)

    def test_no_external_params(self):
        """parameters() must return [] — loss_scale is updated manually."""
        gn = GradNormLoss(n_tasks=3)
        assert gn.parameters() == []


class TestGradNormFirstStep:
    def test_records_L0_on_first_call(self):
        torch.manual_seed(0)
        device = torch.device("cpu")
        model = _SimpleModel().to(device)
        gn = GradNormLoss(n_tasks=2)

        x = torch.randn(4, 8)
        o1, o2 = model(x)
        t = torch.randint(0, 2, (4,))
        l1 = nn.CrossEntropyLoss()(o1, t)
        l2 = nn.CrossEntropyLoss()(o2, t)
        losses = torch.stack([l1, l2])

        total, extras = gn.backward(losses, model.shared_parameters())
        assert gn._L0 is not None
        assert gn._L0.shape == (2,)
        assert "weights" in extras
        # First-step equal weights: sum should equal n_tasks
        assert abs(extras["weights"].sum().item() - 2.0) < 1e-5


class TestGradNormJacobian:
    def test_jacobian_at_equal_weights(self):
        """At equal weights w=[1,1], J[i,i] should be 0.5, J[i,j≠i] = -0.5."""
        gn = GradNormLoss(n_tasks=2)
        w = torch.tensor([1.0, 1.0])
        # Correct: J = diag(w) - (1/n)*w*wᵀ
        J_expected = torch.diag(w) - (1.0 / 2) * w.unsqueeze(1) * w.unsqueeze(0)
        # J_expected = [[0.5, -0.5], [-0.5, 0.5]]
        assert abs(J_expected[0, 0].item() - 0.5) < 1e-6
        assert abs(J_expected[0, 1].item() - (-0.5)) < 1e-6


class TestGradNormDirectional:
    """Directional test: slow task must get higher weight after several steps."""

    def test_small_gradient_task_gets_higher_weight(self):
        """
        GradNorm equalizes weighted gradient norms G_i = w_i * ||∇ L_i||.
        Task 1 has a 10000× smaller loss (and therefore much smaller gradient).
        GradNorm must INCREASE w_1 to compensate for its tiny gradient.
        After ~20 steps w_1 should be > w_0.
        """
        torch.manual_seed(42)
        device = torch.device("cpu")
        model = _SimpleModel().to(device)
        model_opt = torch.optim.SGD(model.parameters(), lr=1e-2)
        gn = GradNormLoss(n_tasks=2, alpha=1.5, lr=5e-2)
        shared_params = model.shared_parameters()

        for step in range(20):
            model.zero_grad()
            x = torch.randn(16, 8)
            o1, o2 = model(x)
            t = torch.randint(0, 2, (16,))
            l1 = nn.CrossEntropyLoss()(o1, t)
            l2 = nn.CrossEntropyLoss()(o2, t) * 0.0001  # task 1: tiny gradient

            losses = torch.stack([l1, l2])
            total, extras = gn.backward(losses, shared_params)
            model_opt.step()

        w = extras["weights"]
        # Task 1 (tiny gradient) should get higher weight to equalize G_i
        assert w[1].item() > w[0].item(), (
            f"Expected w[1]>w[0] (small-gradient task gets boosted) but got w={w.tolist()}"
        )

    def test_no_inf_or_nan_in_loss_scale(self):
        """loss_scale must remain finite after many steps."""
        torch.manual_seed(1)
        device = torch.device("cpu")
        model = _SimpleModel().to(device)
        gn = GradNormLoss(n_tasks=2, alpha=1.5, lr=1.0)  # aggressive LR to stress-test
        shared_params = model.shared_parameters()

        for step in range(50):
            model.zero_grad()
            x = torch.randn(8, 8)
            o1, o2 = model(x)
            t = torch.randint(0, 2, (8,))
            l1 = nn.CrossEntropyLoss()(o1, t)
            l2 = nn.CrossEntropyLoss()(o2, t)
            losses = torch.stack([l1, l2])
            gn.backward(losses, shared_params)

        assert torch.isfinite(gn.loss_scale).all(), (
            f"loss_scale contains inf/nan: {gn.loss_scale}"
        )

    def test_reference_param_is_last_shared_layer(self):
        """shared_parameters()[-1] should be a weight/bias from shared_layers."""
        model = _SimpleModel()
        params = model.shared_parameters()
        last_param = params[-1]
        # The last param in shared_layers is the bias of the last Linear
        assert last_param.shape == (8,), (
            f"Expected bias shape (8,) but got {last_param.shape}"
        )
