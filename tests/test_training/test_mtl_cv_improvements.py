"""Focused tests for MTL CV runner improvements."""

import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from configs.globals import DEVICE
from data.folds import FoldData, TaskFoldData
from losses.registry import create_loss
from tracking.fold import FoldHistory
from training.runners.mtl_cv import train_model


class _TinyMTL(nn.Module):
    def __init__(self, feature_size: int = 4, hidden_size: int = 6, num_classes: int = 3):
        super().__init__()
        self.shared = nn.Linear(feature_size, hidden_size)
        self.cat_head = nn.Linear(hidden_size, num_classes)
        self.next_head = nn.Linear(hidden_size, num_classes)

    def forward(self, inputs):
        category_input, next_input = inputs
        category_rep = self.shared(category_input.squeeze(1))
        next_rep = self.shared(next_input.mean(dim=1))
        return self.cat_head(category_rep), self.next_head(next_rep)

    def shared_parameters(self):
        return self.shared.parameters()

    def task_specific_parameters(self):
        return list(self.cat_head.parameters()) + list(self.next_head.parameters())


class _CountingScheduler:
    def __init__(self):
        self.step_count = 0

    def step(self):
        self.step_count += 1


def _task_data(features: torch.Tensor, targets: torch.Tensor, batch_size: int) -> TaskFoldData:
    train_loader = DataLoader(TensorDataset(features, targets), batch_size=batch_size)
    val_loader = DataLoader(TensorDataset(features[:6], targets[:6]), batch_size=batch_size)
    return TaskFoldData(
        train=FoldData(train_loader, features, targets),
        val=FoldData(val_loader, features[:6], targets[:6]),
    )


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_mtl_train_model_accumulates_gradients_and_tracks_joint_best():
    torch.manual_seed(42)
    batch_size = 2
    num_samples = 10
    num_classes = 3

    category_x = torch.randn(num_samples, 1, 4)
    next_x = torch.randn(num_samples, 3, 4)
    targets = torch.arange(num_samples) % num_classes

    category_data = _task_data(category_x, targets, batch_size)
    next_data = _task_data(next_x, targets, batch_size)

    model = _TinyMTL(num_classes=num_classes).to(DEVICE)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    scheduler = _CountingScheduler()
    step_calls = {"count": 0}
    original_step = optimizer.step

    def counted_step(*args, **kwargs):
        step_calls["count"] += 1
        return original_step(*args, **kwargs)

    optimizer.step = counted_step

    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=next_data,
        dataloader_category=category_data,
        next_criterion=criterion,
        category_criterion=criterion,
        mtl_criterion=mtl_criterion,
        num_epochs=1,
        num_classes=num_classes,
        fold_history=fold_history,
        gradient_accumulation_steps=2,
    )

    assert step_calls["count"] == 3
    assert scheduler.step_count == 3
    assert fold_history.model_task.best.best_state
    assert fold_history.model_task.best.best_value > float("-inf")
    assert "pareto_front" in fold_history.artifacts
    assert "grad_cosine_shared" in fold_history.diagnostics


class _TinyMTLWithAlpha(nn.Module):
    """TinyMTL variant exposing `next_poi.alpha` for F63 logging tests."""

    def __init__(self, feature_size: int = 4, hidden_size: int = 6, num_classes: int = 3,
                 alpha_init: float = 0.37):
        super().__init__()
        self.shared = nn.Linear(feature_size, hidden_size)
        self.cat_head = nn.Linear(hidden_size, num_classes)
        self.next_poi = nn.Linear(hidden_size, num_classes)
        self.next_poi.alpha = nn.Parameter(torch.tensor(float(alpha_init)))

    def forward(self, inputs):
        category_input, next_input = inputs
        category_rep = self.shared(category_input.squeeze(1))
        next_rep = self.shared(next_input.mean(dim=1))
        return self.cat_head(category_rep), self.next_poi(next_rep) + self.next_poi.alpha * 0.0

    def shared_parameters(self):
        return self.shared.parameters()

    def task_specific_parameters(self):
        return (
            list(self.cat_head.parameters())
            + list(self.next_poi.parameters())
        )


class _TinyMTLWithEncoders(nn.Module):
    """TinyMTL variant exposing `next_encoder` + `category_encoder` for D5."""

    def __init__(self, feature_size: int = 4, hidden_size: int = 6, num_classes: int = 3):
        super().__init__()
        self.next_encoder = nn.Linear(feature_size, hidden_size)
        self.category_encoder = nn.Linear(feature_size, hidden_size)
        self.shared = nn.Linear(hidden_size, hidden_size)
        self.cat_head = nn.Linear(hidden_size, num_classes)
        self.next_head = nn.Linear(hidden_size, num_classes)

    def forward(self, inputs):
        category_input, next_input = inputs
        category_rep = self.shared(self.category_encoder(category_input.squeeze(1)))
        next_rep = self.shared(self.next_encoder(next_input.mean(dim=1)))
        return self.cat_head(category_rep), self.next_head(next_rep)

    def shared_parameters(self):
        return self.shared.parameters()

    def task_specific_parameters(self):
        return (
            list(self.cat_head.parameters())
            + list(self.next_head.parameters())
            + list(self.next_encoder.parameters())
            + list(self.category_encoder.parameters())
        )


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_d5_logs_encoder_trajectory_when_encoders_present():
    """D5 — Frobenius norm + drift logged per epoch when both encoders exist."""
    torch.manual_seed(0)
    batch_size = 2
    num_samples = 10
    num_classes = 3

    category_x = torch.randn(num_samples, 1, 4)
    next_x = torch.randn(num_samples, 3, 4)
    targets = torch.arange(num_samples) % num_classes

    category_data = _task_data(category_x, targets, batch_size)
    next_data = _task_data(next_x, targets, batch_size)

    model = _TinyMTLWithEncoders(num_classes=num_classes).to(DEVICE)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    scheduler = _CountingScheduler()
    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=next_data,
        dataloader_category=category_data,
        next_criterion=criterion,
        category_criterion=criterion,
        mtl_criterion=mtl_criterion,
        num_epochs=3,
        num_classes=num_classes,
        fold_history=fold_history,
        gradient_accumulation_steps=1,
    )

    diags = fold_history.diagnostics
    for key in (
        "reg_encoder_l2norm", "reg_encoder_drift_from_init", "reg_encoder_step_drift",
        "cat_encoder_l2norm", "cat_encoder_drift_from_init", "cat_encoder_step_drift",
    ):
        assert key in diags, f"D5 should log {key}"
        assert len(list(diags[key])) == 3, f"{key}: expected 3 entries (one per epoch)"

    # Drift-from-init must be monotonically non-decreasing (encoder is moving
    # away from its starting point under SGD with lr>0).
    drift = list(diags["reg_encoder_drift_from_init"])
    assert drift[0] <= drift[1] <= drift[2], drift
    # Step drift is non-zero (encoder is actually updating).
    step_drift = list(diags["reg_encoder_step_drift"])
    assert all(d > 0 for d in step_drift), step_drift


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_d5_silent_no_op_when_encoders_absent():
    """D5 logger must not crash on models without next_encoder/category_encoder."""
    torch.manual_seed(0)
    batch_size = 2
    num_samples = 10
    num_classes = 3

    category_x = torch.randn(num_samples, 1, 4)
    next_x = torch.randn(num_samples, 3, 4)
    targets = torch.arange(num_samples) % num_classes

    category_data = _task_data(category_x, targets, batch_size)
    next_data = _task_data(next_x, targets, batch_size)

    model = _TinyMTL(num_classes=num_classes).to(DEVICE)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    scheduler = _CountingScheduler()
    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=next_data,
        dataloader_category=category_data,
        next_criterion=criterion,
        category_criterion=criterion,
        mtl_criterion=mtl_criterion,
        num_epochs=1,
        num_classes=num_classes,
        fold_history=fold_history,
        gradient_accumulation_steps=1,
    )

    # No encoder keys logged when the model has no encoders.
    for key in ("reg_encoder_l2norm", "cat_encoder_l2norm"):
        assert key not in fold_history.diagnostics


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_f63_logs_head_alpha_when_present():
    torch.manual_seed(0)
    batch_size = 2
    num_samples = 10
    num_classes = 3

    category_x = torch.randn(num_samples, 1, 4)
    next_x = torch.randn(num_samples, 3, 4)
    targets = torch.arange(num_samples) % num_classes

    category_data = _task_data(category_x, targets, batch_size)
    next_data = _task_data(next_x, targets, batch_size)

    model = _TinyMTLWithAlpha(num_classes=num_classes, alpha_init=0.42).to(DEVICE)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.0)  # lr=0 → α stays put
    scheduler = _CountingScheduler()

    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=next_data,
        dataloader_category=category_data,
        next_criterion=criterion,
        category_criterion=criterion,
        mtl_criterion=mtl_criterion,
        num_epochs=2,
        num_classes=num_classes,
        fold_history=fold_history,
        gradient_accumulation_steps=2,
    )

    # F63: head_alpha logged once per epoch in diagnostics
    assert "head_alpha" in fold_history.diagnostics, (
        "F63 should log head_alpha when model.next_poi has an `alpha` tensor"
    )
    alphas = list(fold_history.diagnostics["head_alpha"])
    assert len(alphas) == 2, f"expected 2 entries (one per epoch), got {len(alphas)}"
    # With lr=0, α can't move
    assert all(abs(a - 0.42) < 1e-5 for a in alphas), alphas


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_b4_alpha_frozen_until_epoch_toggles_requires_grad():
    """B4 — α should be requires_grad=False until epoch N, then True."""
    torch.manual_seed(0)
    batch_size = 2
    num_samples = 10
    num_classes = 3

    category_x = torch.randn(num_samples, 1, 4)
    next_x = torch.randn(num_samples, 3, 4)
    targets = torch.arange(num_samples) % num_classes

    category_data = _task_data(category_x, targets, batch_size)
    next_data = _task_data(next_x, targets, batch_size)

    model = _TinyMTLWithAlpha(num_classes=num_classes, alpha_init=0.5).to(DEVICE)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    scheduler = _CountingScheduler()
    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    # Train 3 epochs with alpha_frozen_until_epoch=2
    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=next_data,
        dataloader_category=category_data,
        next_criterion=criterion,
        category_criterion=criterion,
        mtl_criterion=mtl_criterion,
        num_epochs=3,
        num_classes=num_classes,
        fold_history=fold_history,
        gradient_accumulation_steps=2,
        alpha_frozen_until_epoch=2,
    )

    # By the end of training, α should be unfrozen (requires_grad=True).
    # The unfreeze fires AT epoch 2 (the 3rd epoch, 0-indexed).
    assert model.next_poi.alpha.requires_grad is True


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_b4_alpha_stays_frozen_during_warmup():
    """When alpha_frozen_until_epoch > num_epochs, α never unfreezes."""
    torch.manual_seed(0)
    category_x = torch.randn(10, 1, 4)
    next_x = torch.randn(10, 3, 4)
    targets = torch.arange(10) % 3
    category_data = _task_data(category_x, targets, 2)
    next_data = _task_data(next_x, targets, 2)
    model = _TinyMTLWithAlpha(num_classes=3, alpha_init=0.5).to(DEVICE)
    optimizer = torch.optim.SGD(model.parameters(), lr=1.0)  # high LR
    scheduler = _CountingScheduler()
    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    initial_alpha = float(model.next_poi.alpha)
    train_model(
        model=model, optimizer=optimizer, scheduler=scheduler,
        dataloader_next=next_data, dataloader_category=category_data,
        next_criterion=criterion, category_criterion=criterion,
        mtl_criterion=mtl_criterion, num_epochs=3, num_classes=3,
        fold_history=fold_history, gradient_accumulation_steps=2,
        alpha_frozen_until_epoch=10,  # never unfreezes within 3 epochs
    )

    # α frozen → requires_grad False, value unchanged
    assert model.next_poi.alpha.requires_grad is False
    assert abs(float(model.next_poi.alpha) - initial_alpha) < 1e-6, (
        f"α should be unchanged; got {float(model.next_poi.alpha)} vs {initial_alpha}"
    )


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_f63_silent_when_no_alpha():
    """F63 hook must not error or pollute diagnostics on heads without α."""
    torch.manual_seed(0)
    batch_size = 2
    num_samples = 10
    num_classes = 3

    category_x = torch.randn(num_samples, 1, 4)
    next_x = torch.randn(num_samples, 3, 4)
    targets = torch.arange(num_samples) % num_classes

    category_data = _task_data(category_x, targets, batch_size)
    next_data = _task_data(next_x, targets, batch_size)

    model = _TinyMTL(num_classes=num_classes).to(DEVICE)  # no `next_poi`, no `alpha`
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    scheduler = _CountingScheduler()

    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=next_data,
        dataloader_category=category_data,
        next_criterion=criterion,
        category_criterion=criterion,
        mtl_criterion=mtl_criterion,
        num_epochs=1,
        num_classes=num_classes,
        fold_history=fold_history,
        gradient_accumulation_steps=2,
    )

    assert "head_alpha" not in fold_history.diagnostics


@pytest.mark.skipif(
    DEVICE.type == "mps",
    reason="MPS corrupts tiny integer tensors in unit-test-sized batches",
)
def test_ga2_first_step_gradient_is_mean_of_group(monkeypatch):
    """pipeline_audit 2026-07-01 — pins gradient CONTENT under ga=2.

    The pre-fix loop ran ``optimizer.zero_grad`` on EVERY batch, wiping the
    first micro-batch's gradients, so each boundary step applied only the LAST
    micro-batch scaled 1/ga. The step-count test above cannot detect that (it
    passes either way). This test asserts the FIRST optimizer step's gradient
    equals the accumulated (g0+g1)/ga closed form computed from the initial
    weights — it FAILS on the pre-fix code.
    """
    monkeypatch.setenv("MTL_DISABLE_AMP", "1")  # fp32 forward → exact reference
    torch.manual_seed(42)
    batch_size = 2
    num_samples = 10
    num_classes = 3

    category_x = torch.randn(num_samples, 1, 4)
    next_x = torch.randn(num_samples, 3, 4)
    targets = torch.arange(num_samples) % num_classes

    category_data = _task_data(category_x, targets, batch_size)
    next_data = _task_data(next_x, targets, batch_size)

    model = _TinyMTL(num_classes=num_classes).to(DEVICE)
    init_state = {k: v.detach().clone() for k, v in model.state_dict().items()}

    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    captured = []
    original_step = optimizer.step

    def capture_step(*args, **kwargs):
        captured.append(model.shared.weight.grad.detach().clone())
        return original_step(*args, **kwargs)

    optimizer.step = capture_step

    fold_history = FoldHistory.standalone({"next", "category"})
    criterion = nn.CrossEntropyLoss()
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=_CountingScheduler(),
        dataloader_next=next_data,
        dataloader_category=category_data,
        next_criterion=criterion,
        category_criterion=criterion,
        mtl_criterion=mtl_criterion,
        num_epochs=1,
        num_classes=num_classes,
        fold_history=fold_history,
        gradient_accumulation_steps=2,
        max_grad_norm=0.0,  # disable clipping so the closed form is exact
    )

    # Reference: g0+g1 of (CE_next + CE_cat)/ga from the INITIAL weights
    # (equal_weight = plain sum; loaders are unshuffled so batches are 0,1).
    ref = _TinyMTL(num_classes=num_classes).to(DEVICE)
    ref.load_state_dict(init_state)
    expected = None
    for k in (0, 1):
        ref.zero_grad(set_to_none=True)
        sl = slice(2 * k, 2 * k + 2)
        cat_b = category_x[sl].to(DEVICE)
        next_b = next_x[sl].to(DEVICE)
        t = targets[sl].to(DEVICE)
        out_cat, out_next = ref((cat_b, next_b))
        loss = criterion(out_next, t) + criterion(out_cat, t)
        (loss / 2).backward()
        g = ref.shared.weight.grad.detach().clone()
        expected = g if expected is None else expected + g

    assert captured, "optimizer.step never fired"
    torch.testing.assert_close(captured[0], expected, rtol=1e-5, atol=1e-6)
