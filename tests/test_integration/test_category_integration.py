"""
Integration test for category-only training pipeline.

Runs 2 folds × 3 epochs on synthetic data (CPU, deterministic).
Validates the full pipeline: model creation → training → evaluation → tracking.
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
    make_category_data,
    make_loaders,
    seed_everything,
)


class TestCategoryIntegration:
    """End-to-end category training pipeline on synthetic data."""

    @pytest.fixture(autouse=True)
    def setup(self):
        seed_everything()

    def test_category_pipeline_runs_to_completion(self):
        """Full pipeline: create model, train 2 folds × 3 epochs, evaluate."""
        from models.registry import create_model
        from tracking import MLHistory

        history = MLHistory(
            model_name="category_ensemble",
            tasks={"category"},
            num_folds=INTEGRATION_FOLDS,
        )
        history.start()

        for fold_idx in range(INTEGRATION_FOLDS):
            seed_everything(SEED + fold_idx)

            X_train, y_train = make_category_data(
                NUM_TRAIN // NUM_CLASSES, seed=SEED + fold_idx
            )
            X_val, y_val = make_category_data(
                NUM_VAL // NUM_CLASSES, seed=SEED + fold_idx + 100
            )
            train_dl, val_dl = make_loaders(X_train, y_train, X_val, y_val)

            model = create_model(
                "category_ensemble",
                input_dim=EMBED_DIM,
                hidden_dim=64,
                num_classes=NUM_CLASSES,
                dropout=0.1,
            ).to(DEVICE)

            optimizer = torch.optim.AdamW(
                model.parameters(), lr=1e-3, weight_decay=0.01
            )
            criterion = nn.CrossEntropyLoss()
            scheduler = torch.optim.lr_scheduler.OneCycleLR(
                optimizer,
                max_lr=1e-2,
                epochs=INTEGRATION_EPOCHS,
                steps_per_epoch=len(train_dl),
            )

            fold_history = history.get_curr_fold()

            for epoch in range(INTEGRATION_EPOCHS):
                model.train()
                for xb, yb in train_dl:
                    xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                    optimizer.zero_grad()
                    out = model(xb)
                    loss = criterion(out, yb)
                    loss.backward()
                    optimizer.step()
                    scheduler.step()

                # Validation
                model.eval()
                val_preds, val_targets = [], []
                with torch.no_grad():
                    for xb, yb in val_dl:
                        out = model(xb.to(DEVICE))
                        val_preds.append(out.argmax(dim=1).cpu())
                        val_targets.append(yb)

                preds = torch.cat(val_preds).numpy()
                targets = torch.cat(val_targets).numpy()
                val_f1 = f1_score(targets, preds, average="macro")

                fold_history.log_train("category", loss=loss.item(), accuracy=0.0, f1=0.0)
                fold_history.log_val(
                    "category",
                    loss=0.0,
                    accuracy=0.0,
                    f1=val_f1,
                    model_state=model.state_dict() if epoch == 0 or val_f1 > fold_history.task("category").best.best_value else None,
                    elapsed_time=0.0,
                )

            history.step()

        # Assertions
        assert len(history.folds) == INTEGRATION_FOLDS
        for fold in history.folds:
            assert len(fold.task("category").train["loss"]) == INTEGRATION_EPOCHS
            assert len(fold.task("category").val["f1"]) == INTEGRATION_EPOCHS
            assert fold.task("category").best.best_state is not None

    def test_category_model_registry_roundtrip(self):
        """Model registry creates correct architecture."""
        from models.registry import create_model

        model = create_model(
            "category_ensemble",
            input_dim=EMBED_DIM,
            hidden_dim=64,
            num_classes=NUM_CLASSES,
            dropout=0.1,
        )
        x = torch.randn(BATCH_SIZE, EMBED_DIM)
        out = model(x)
        assert out.shape == (BATCH_SIZE, NUM_CLASSES)

    def test_category_training_improves_loss(self):
        """Training should decrease loss over 3 epochs."""
        from models.registry import create_model

        seed_everything()
        X_train, y_train = make_category_data(NUM_TRAIN // NUM_CLASSES)
        X_val, y_val = make_category_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)
        train_dl, _ = make_loaders(X_train, y_train, X_val, y_val)

        model = create_model(
            "category_ensemble",
            input_dim=EMBED_DIM,
            hidden_dim=64,
            num_classes=NUM_CLASSES,
            dropout=0.1,
        ).to(DEVICE)

        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()

        losses = []
        for epoch in range(INTEGRATION_EPOCHS):
            model.train()
            epoch_loss = 0.0
            count = 0
            for xb, yb in train_dl:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                optimizer.zero_grad()
                out = model(xb)
                loss = criterion(out, yb)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
                count += 1
            losses.append(epoch_loss / count)

        # Loss should decrease (last < first)
        assert losses[-1] < losses[0], (
            f"Loss did not decrease: first={losses[0]:.4f}, last={losses[-1]:.4f}"
        )
