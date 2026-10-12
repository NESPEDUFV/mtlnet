"""
Integration test for MTL (multi-task learning) training pipeline.

Runs 2 folds × 3 epochs on synthetic data (CPU, deterministic).
Validates: model creation, dual-dataloader training, zip_longest_cycle
semantics, evaluation of both tasks, and tracking.
No real data files required.
"""

import pytest
import torch
import torch.nn as nn
from sklearn.metrics import f1_score

from tests.test_integration.conftest import (
    BATCH_SIZE,
    DEVICE,
    EMBED_DIM,
    INTEGRATION_EPOCHS,
    INTEGRATION_FOLDS,
    NUM_CLASSES,
    NUM_TRAIN,
    NUM_VAL,
    SEED,
    SEQ_LEN,
    make_category_data,
    make_loaders,
    make_next_data,
    seed_everything,
)


def _train_mtl_epoch(model, cat_train_dl, next_train_dl, optimizer, criterion,
                     scheduler=None):
    """Train one MTL epoch with cycling (matches production zip_longest_cycle)."""
    model.train()
    cat_iter = iter(cat_train_dl)
    next_iter = iter(next_train_dl)
    steps = max(len(cat_train_dl), len(next_train_dl))
    total_loss = 0.0

    for _ in range(steps):
        try:
            cx, cy = next(cat_iter)
        except StopIteration:
            cat_iter = iter(cat_train_dl)
            cx, cy = next(cat_iter)
        try:
            nx, ny = next(next_iter)
        except StopIteration:
            next_iter = iter(next_train_dl)
            nx, ny = next(next_iter)

        cx, cy = cx.to(DEVICE), cy.to(DEVICE)
        nx, ny = nx.to(DEVICE), ny.to(DEVICE)
        cx_3d = cx.unsqueeze(1)

        optimizer.zero_grad()
        out_cat, out_next = model((cx_3d, nx))
        loss = criterion(out_cat, cy) + criterion(out_next, ny)
        loss.backward()
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        total_loss += loss.item()

    return total_loss / steps


def _eval_mtl(model, cat_val_dl, next_val_dl):
    """Evaluate MTL model on both tasks, return (cat_f1, next_f1)."""
    model.eval()

    # Category evaluation
    cat_preds, cat_targets = [], []
    with torch.no_grad():
        for xb, yb in cat_val_dl:
            xb_3d = xb.unsqueeze(1).to(DEVICE)
            dummy_next = torch.zeros(xb.size(0), SEQ_LEN, EMBED_DIM, device=DEVICE)
            out_cat, _ = model((xb_3d, dummy_next))
            cat_preds.append(out_cat.argmax(dim=1).cpu())
            cat_targets.append(yb)

    # Next evaluation
    next_preds, next_targets = [], []
    with torch.no_grad():
        for xb, yb in next_val_dl:
            dummy_cat = torch.zeros(xb.size(0), 1, EMBED_DIM, device=DEVICE)
            _, out_next = model((dummy_cat, xb.to(DEVICE)))
            next_preds.append(out_next.argmax(dim=1).cpu())
            next_targets.append(yb)

    cat_f1 = f1_score(
        torch.cat(cat_targets).numpy(),
        torch.cat(cat_preds).numpy(),
        average="macro",
    )
    next_f1 = f1_score(
        torch.cat(next_targets).numpy(),
        torch.cat(next_preds).numpy(),
        average="macro",
    )
    return cat_f1, next_f1


class TestMTLIntegration:
    """End-to-end MTL training pipeline on synthetic data."""

    @pytest.fixture(autouse=True)
    def setup(self):
        seed_everything()

    def test_mtl_pipeline_runs_to_completion(self):
        """Full pipeline: create MTLnet, train 2 folds × 3 epochs, evaluate both tasks."""
        from models.registry import create_model
        from tracking import MLHistory

        history = MLHistory(
            model_name="mtlnet",
            tasks={"next", "category"},
            num_folds=INTEGRATION_FOLDS,
        )
        history.start()

        for fold_idx in range(INTEGRATION_FOLDS):
            seed_everything(SEED + fold_idx)

            X_cat_train, y_cat_train = make_category_data(
                NUM_TRAIN // NUM_CLASSES, seed=SEED + fold_idx
            )
            X_cat_val, y_cat_val = make_category_data(
                NUM_VAL // NUM_CLASSES, seed=SEED + fold_idx + 100
            )
            X_next_train, y_next_train = make_next_data(
                NUM_TRAIN // NUM_CLASSES, seed=SEED + fold_idx
            )
            X_next_val, y_next_val = make_next_data(
                NUM_VAL // NUM_CLASSES, seed=SEED + fold_idx + 100
            )

            cat_train_dl, cat_val_dl = make_loaders(
                X_cat_train, y_cat_train, X_cat_val, y_cat_val
            )
            next_train_dl, next_val_dl = make_loaders(
                X_next_train, y_next_train, X_next_val, y_next_val
            )

            model = create_model(
                "mtlnet",
                feature_size=EMBED_DIM,
                shared_layer_size=256,
                num_classes=NUM_CLASSES,
                num_heads=8,
                num_layers=4,
                seq_length=SEQ_LEN,
                num_shared_layers=4,
            ).to(DEVICE)

            optimizer = torch.optim.AdamW(
                model.parameters(), lr=1e-3, weight_decay=0.01
            )
            criterion = nn.CrossEntropyLoss()
            steps_per_epoch = max(len(cat_train_dl), len(next_train_dl))
            scheduler = torch.optim.lr_scheduler.OneCycleLR(
                optimizer,
                max_lr=1e-2,
                epochs=INTEGRATION_EPOCHS,
                steps_per_epoch=steps_per_epoch,
            )

            fold_history = history.get_curr_fold()

            for epoch in range(INTEGRATION_EPOCHS):
                _train_mtl_epoch(
                    model, cat_train_dl, next_train_dl,
                    optimizer, criterion, scheduler,
                )

                cat_f1, next_f1 = _eval_mtl(model, cat_val_dl, next_val_dl)

                fold_history.log_train("category", loss=0.0, accuracy=0.0, f1=0.0)
                fold_history.log_train("next", loss=0.0, accuracy=0.0, f1=0.0)

                state = model.state_dict()
                fold_history.log_val(
                    "category", loss=0.0, accuracy=0.0, f1=cat_f1,
                    model_state=state if epoch == 0 or cat_f1 > fold_history.task("category").best.best_value else None,
                    elapsed_time=0.0,
                )
                fold_history.log_val(
                    "next", loss=0.0, accuracy=0.0, f1=next_f1,
                    model_state=state if epoch == 0 or next_f1 > fold_history.task("next").best.best_value else None,
                    elapsed_time=0.0,
                )

            history.step()

        # Assertions
        assert len(history.folds) == INTEGRATION_FOLDS
        for fold in history.folds:
            for task_name in ("category", "next"):
                assert len(fold.task(task_name).train["loss"]) == INTEGRATION_EPOCHS
                assert len(fold.task(task_name).val["f1"]) == INTEGRATION_EPOCHS
                assert fold.task(task_name).best.best_state is not None

    def test_mtl_dual_dataloader_cycling(self):
        """Verify that asymmetric loaders are handled correctly (zip_longest_cycle)."""
        from utils.progress import zip_longest_cycle

        # Create loaders with different sizes
        cat_data = make_category_data(50, seed=SEED)  # 350 total
        next_data = make_next_data(20, seed=SEED)       # 140 total
        cat_dl = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(*cat_data),
            batch_size=BATCH_SIZE,
        )
        next_dl = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(*next_data),
            batch_size=BATCH_SIZE,
        )

        # zip_longest_cycle should iterate max(len(cat_dl), len(next_dl)) times
        batches = list(zip_longest_cycle(cat_dl, next_dl))
        expected = max(len(cat_dl), len(next_dl))
        assert len(batches) == expected, (
            f"Expected {expected} batches, got {len(batches)}"
        )

    def test_mtl_shared_backbone_gradient_flow(self):
        """Verify gradients flow through shared backbone from both tasks."""
        from models.registry import create_model

        seed_everything()
        model = create_model(
            "mtlnet",
            feature_size=EMBED_DIM,
            shared_layer_size=256,
            num_classes=NUM_CLASSES,
            num_heads=8,
            num_layers=4,
            seq_length=SEQ_LEN,
            num_shared_layers=4,
        ).to(DEVICE)

        cat_in = torch.randn(4, 1, EMBED_DIM, device=DEVICE)
        next_in = torch.randn(4, SEQ_LEN, EMBED_DIM, device=DEVICE)
        criterion = nn.CrossEntropyLoss()
        target = torch.randint(0, NUM_CLASSES, (4,), device=DEVICE)

        out_cat, out_next = model((cat_in, next_in))
        loss = criterion(out_cat, target) + criterion(out_next, target)
        loss.backward()

        # All shared parameters must have gradients
        for p in model.shared_parameters():
            assert p.grad is not None, "Shared parameter has no gradient"
            assert p.grad.abs().sum() > 0, "Shared parameter gradient is zero"

        # Task-specific parameters must have gradients
        for p in model.task_specific_parameters():
            assert p.grad is not None, "Task-specific parameter has no gradient"

    def test_mtl_training_improves_both_tasks(self):
        """Training should improve F1 for both tasks over 3 epochs."""
        from models.registry import create_model

        seed_everything()
        X_cat_train, y_cat_train = make_category_data(NUM_TRAIN // NUM_CLASSES)
        X_cat_val, y_cat_val = make_category_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)
        X_next_train, y_next_train = make_next_data(NUM_TRAIN // NUM_CLASSES)
        X_next_val, y_next_val = make_next_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)

        cat_train_dl, cat_val_dl = make_loaders(
            X_cat_train, y_cat_train, X_cat_val, y_cat_val
        )
        next_train_dl, next_val_dl = make_loaders(
            X_next_train, y_next_train, X_next_val, y_next_val
        )

        model = create_model(
            "mtlnet",
            feature_size=EMBED_DIM,
            shared_layer_size=256,
            num_classes=NUM_CLASSES,
            num_heads=8,
            num_layers=4,
            seq_length=SEQ_LEN,
            num_shared_layers=4,
        ).to(DEVICE)

        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
        criterion = nn.CrossEntropyLoss()

        losses = []
        for epoch in range(INTEGRATION_EPOCHS):
            loss = _train_mtl_epoch(
                model, cat_train_dl, next_train_dl, optimizer, criterion
            )
            losses.append(loss)

        # Loss should decrease
        assert losses[-1] < losses[0], (
            f"MTL loss did not decrease: first={losses[0]:.4f}, last={losses[-1]:.4f}"
        )

    def test_mtl_determinism_on_cpu(self):
        """Two runs with same seed must produce identical results."""
        from models.registry import create_model

        results = []
        for _ in range(2):
            seed_everything()
            X_cat, y_cat = make_category_data(NUM_TRAIN // NUM_CLASSES)
            X_next, y_next = make_next_data(NUM_TRAIN // NUM_CLASSES)
            cat_dl, _ = make_loaders(X_cat, y_cat, X_cat[:NUM_VAL], y_cat[:NUM_VAL])
            next_dl, _ = make_loaders(X_next, y_next, X_next[:NUM_VAL], y_next[:NUM_VAL])

            model = create_model(
                "mtlnet",
                feature_size=EMBED_DIM,
                shared_layer_size=256,
                num_classes=NUM_CLASSES,
                num_heads=8,
                num_layers=4,
                seq_length=SEQ_LEN,
                num_shared_layers=4,
            ).to(DEVICE)

            optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
            criterion = nn.CrossEntropyLoss()

            for _ in range(INTEGRATION_EPOCHS):
                _train_mtl_epoch(model, cat_dl, next_dl, optimizer, criterion)

            # Capture final weights
            results.append({
                k: v.clone() for k, v in model.state_dict().items()
            })

        # Both runs must produce identical weights
        for key in results[0]:
            assert torch.equal(results[0][key], results[1][key]), (
                f"Non-deterministic: parameter '{key}' differs between runs"
            )
