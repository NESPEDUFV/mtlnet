"""Tests for lightweight MTL loss weighting baselines."""

import torch

from losses.registry import create_loss, list_losses


def _toy_losses(param: torch.nn.Parameter) -> torch.Tensor:
    next_loss = (param[0] - 2.0).pow(2) + 0.1
    category_loss = (param[1] + 3.0).pow(2) + 0.2
    return torch.stack([next_loss, category_loss])


def test_mtl_baseline_losses_are_registered():
    losses = list_losses()
    assert "equal_weight" in losses
    assert "static_weight" in losses
    assert "uncertainty_weighting" in losses
    assert "uw_so" in losses
    assert "random_weight" in losses
    assert "rlw" in losses
    assert "famo" in losses
    assert "fairgrad" in losses
    assert "bayesagg_mtl" in losses
    assert "bayesagg" in losses
    assert "go4align" in losses
    assert "excess_mtl" in losses
    assert "stch" in losses
    assert "db_mtl" in losses
    assert "cagrad" in losses
    assert "aligned_mtl" in losses
    assert "dwa" in losses


def test_mtl_baseline_losses_backward_with_stable_weights():
    for loss_name, kwargs in [
        ("equal_weight", {}),
        ("static_weight", {"category_weight": 0.75}),
        ("uncertainty_weighting", {}),
        ("uw_so", {"temperature": 1.0}),
        ("random_weight", {"alpha": 1.0}),
        ("rlw", {"alpha": [1.0, 2.0]}),
        ("famo", {}),
        ("fairgrad", {"alpha": 1.0, "solver_steps": 8}),
        ("bayesagg_mtl", {}),
        ("go4align", {"temperature": 1.0, "window_size": 4}),
        ("excess_mtl", {"robust_step_size": 0.01}),
        ("stch", {"mu": 0.5, "warmup_epochs": 0}),
        ("db_mtl", {"beta": 0.9, "beta_sigma": 0.5}),
        ("dwa", {"temperature": 2.0}),
    ]:
        param = torch.nn.Parameter(torch.tensor([1.0, -1.0]))
        criterion = create_loss(loss_name, n_tasks=2, device=torch.device("cpu"), **kwargs)

        weighted_loss, extra = criterion.backward(
            _toy_losses(param),
            shared_parameters=[param],
            task_specific_parameters=[],
        )

        assert torch.isfinite(weighted_loss)
        assert param.grad is not None
        assert torch.isfinite(param.grad).all()
        assert "weights" in extra
        assert extra["weights"].shape == (2,)
        assert torch.isfinite(extra["weights"]).all()


def test_uncertainty_weighting_exposes_learnable_parameters():
    criterion = create_loss(
        "uncertainty_weighting",
        n_tasks=2,
        device=torch.device("cpu"),
    )
    params = list(criterion.parameters())
    assert len(params) == 1
    assert params[0].shape == (2,)


def test_gradient_manipulating_losses_set_grads():
    """CAGrad and Aligned-MTL set .grad directly (like PCGrad)."""
    for loss_name, kwargs in [
        ("cagrad", {"c": 0.4}),
        ("aligned_mtl", {}),
    ]:
        param = torch.nn.Parameter(torch.tensor([1.0, -1.0]))
        criterion = create_loss(loss_name, n_tasks=2, device=torch.device("cpu"), **kwargs)

        _, extra = criterion.backward(
            _toy_losses(param),
            shared_parameters=[param],
            task_specific_parameters=[],
        )

        assert param.grad is not None, f"{loss_name}: grad not set"
        assert torch.isfinite(param.grad).all(), f"{loss_name}: non-finite grad"
        assert "weights" in extra, f"{loss_name}: no weights in extra"
        assert extra["weights"].shape == (2,), f"{loss_name}: wrong weights shape"


def test_dwa_adapts_weights_after_warmup():
    """DWA returns equal weights for first 2 steps, then adapts."""
    criterion = create_loss("dwa", n_tasks=2, device=torch.device("cpu"), temperature=2.0)
    param = torch.nn.Parameter(torch.tensor([1.0, -1.0]))

    # Step 1 & 2: equal weights (warmup).
    for _ in range(2):
        criterion.backward(
            _toy_losses(param),
            shared_parameters=[param],
            task_specific_parameters=[],
        )
        param.grad = None

    # Step 3: should produce non-trivial weights if losses changed.
    # Shift param so losses are different from before.
    param.data = torch.tensor([2.0, 0.0])
    _, extra = criterion.backward(
        _toy_losses(param),
        shared_parameters=[param],
        task_specific_parameters=[],
    )
    assert extra["weights"].shape == (2,)
    assert torch.isfinite(extra["weights"]).all()


def test_random_weight_samples_simplex_weights():
    criterion = create_loss(
        "random_weight",
        n_tasks=2,
        device=torch.device("cpu"),
        alpha=1.0,
    )
    param = torch.nn.Parameter(torch.tensor([1.0, -1.0]))

    _, extra = criterion.backward(
        _toy_losses(param),
        shared_parameters=[param],
        task_specific_parameters=[],
    )

    assert torch.all(extra["weights"] > 0)
    assert torch.isclose(torch.sum(extra["weights"]), torch.tensor(1.0), atol=1e-6)
