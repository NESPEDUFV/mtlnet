"""
Phase 0 regression fixtures — safety net for all subsequent refactoring phases.

Three fixtures (category, next, MTL) × three layers each:
  Layer 1 — Deterministic: shapes, param counts. Must pass exactly.
  Layer 2 — Artifact: dataloader structure, batch shapes. Must pass exactly.
  Layer 3 — Metric: F1 macro within calibrated tolerance after short training.

Calibration protocol (run once during Phase 0 setup):
  Run `_train_and_evaluate` 5× per fixture with SEED on CPU.
  Tolerance = 3 × observed std dev.  Values documented in comments below.

All tests force CPU to avoid MPS non-determinism.

Phase 7: data generators imported from tests.test_integration.conftest
(shared synthetic data infrastructure).
"""

import pytest
import torch
import torch.nn as nn
from sklearn.metrics import f1_score

from tests.test_integration.conftest import (
    BATCH_SIZE,
    DEVICE,
    EMBED_DIM,
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

# ---------------------------------------------------------------------------
# Regression-specific constants
# ---------------------------------------------------------------------------
TRAIN_EPOCHS = 10


# ---------------------------------------------------------------------------
# Regression-specific helpers (train loops with specific epoch counts)
# ---------------------------------------------------------------------------
def _train_and_evaluate(model, train_dl, val_dl, epochs=TRAIN_EPOCHS, lr=1e-3):
    """Train model, return val F1 macro."""
    model.to(DEVICE).train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    criterion = nn.CrossEntropyLoss()

    for _ in range(epochs):
        for xb, yb in train_dl:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            opt.zero_grad()
            out = model(xb)
            loss = criterion(out, yb)
            loss.backward()
            opt.step()

    model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for xb, yb in val_dl:
            out = model(xb.to(DEVICE))
            all_preds.append(out.argmax(dim=1).cpu())
            all_targets.append(yb)
    preds = torch.cat(all_preds).numpy()
    targets = torch.cat(all_targets).numpy()
    return f1_score(targets, preds, average="macro")


def _train_mtl_and_evaluate(model, cat_train_dl, cat_val_dl,
                            next_train_dl, next_val_dl,
                            epochs=TRAIN_EPOCHS, lr=1e-3):
    """Train MTL model, return (cat_f1, next_f1)."""
    model.to(DEVICE).train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    criterion = nn.CrossEntropyLoss()

    for _ in range(epochs):
        cat_iter = iter(cat_train_dl)
        next_iter = iter(next_train_dl)
        # Cycle through both loaders
        for _ in range(max(len(cat_train_dl), len(next_train_dl))):
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
            # Category input needs unsqueeze to [B, 1, D]
            cx_3d = cx.unsqueeze(1)

            opt.zero_grad()
            out_cat, out_next = model((cx_3d, nx))
            loss = criterion(out_cat, cy) + criterion(out_next, ny)
            loss.backward()
            opt.step()

    model.eval()
    # Evaluate category
    cat_preds, cat_targets = [], []
    with torch.no_grad():
        for xb, yb in cat_val_dl:
            xb_3d = xb.unsqueeze(1).to(DEVICE)
            # Dummy next input (not used for category eval, but model needs both)
            dummy_next = torch.zeros(xb.size(0), SEQ_LEN, EMBED_DIM, device=DEVICE)
            out_cat, _ = model((xb_3d, dummy_next))
            cat_preds.append(out_cat.argmax(dim=1).cpu())
            cat_targets.append(yb)

    # Evaluate next
    next_preds, next_targets = [], []
    with torch.no_grad():
        for xb, yb in next_val_dl:
            dummy_cat = torch.zeros(xb.size(0), 1, EMBED_DIM, device=DEVICE)
            _, out_next = model((dummy_cat, xb.to(DEVICE)))
            next_preds.append(out_next.argmax(dim=1).cpu())
            next_targets.append(yb)

    cat_f1 = f1_score(torch.cat(cat_targets).numpy(), torch.cat(cat_preds).numpy(), average="macro")
    next_f1 = f1_score(torch.cat(next_targets).numpy(), torch.cat(next_preds).numpy(), average="macro")
    return cat_f1, next_f1


# ===================================================================
# CATEGORY FIXTURE
# ===================================================================
# Calibration (5 runs, seed=42, CPU, 10 epochs, torch==2.9.1, 2026-03-26):
#   F1 values: [0.9492, 0.9492, 0.9492, 0.9492, 0.9492]
#   mean=0.9492, std=0.000000, floor(mean-3*std)=0.9492
#   CPU determinism → std=0. Floor set to 0.94 for PyTorch version margin.
CATEGORY_F1_FLOOR = 0.94
CATEGORY_PARAM_COUNT = 19335

class TestCategoryRegression:
    """Regression fixture for standalone CategoryHeadSingle."""

    @pytest.fixture(autouse=True)
    def setup(self):
        seed_everything()

    # --- Layer 1: deterministic shapes ---
    def test_category_output_shape(self):
        from models.category import CategoryHeadSingle
        model = CategoryHeadSingle(input_dim=EMBED_DIM, hidden_dims=(128, 64, 32),
                                   num_classes=NUM_CLASSES, dropout=0.1)
        x = torch.randn(BATCH_SIZE, EMBED_DIM)
        out = model(x)
        assert out.shape == (BATCH_SIZE, NUM_CLASSES)

    def test_category_param_count(self):
        from models.category import CategoryHeadSingle
        model = CategoryHeadSingle(input_dim=EMBED_DIM, hidden_dims=(128, 64, 32),
                                   num_classes=NUM_CLASSES, dropout=0.1)
        total = sum(p.numel() for p in model.parameters())
        assert total == CATEGORY_PARAM_COUNT, f"param count {total} != expected {CATEGORY_PARAM_COUNT}"

    # --- Layer 2: artifact structure ---
    def test_category_dataloader_shapes(self):
        X_train, y_train = make_category_data(NUM_TRAIN // NUM_CLASSES, seed=SEED)
        X_val, y_val = make_category_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)
        train_dl, val_dl = make_loaders(X_train, y_train, X_val, y_val)
        xb, yb = next(iter(train_dl))
        assert xb.shape == (BATCH_SIZE, EMBED_DIM)
        assert yb.shape == (BATCH_SIZE,)
        assert set(yb.numpy().tolist()).issubset(set(range(NUM_CLASSES)))

    # --- Layer 3: coarse metric ---
    def test_category_f1_within_tolerance(self):
        from models.category import CategoryHeadSingle
        seed_everything()
        X_train, y_train = make_category_data(NUM_TRAIN // NUM_CLASSES, seed=SEED)
        X_val, y_val = make_category_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)
        train_dl, val_dl = make_loaders(X_train, y_train, X_val, y_val)
        model = CategoryHeadSingle(input_dim=EMBED_DIM, hidden_dims=(128, 64, 32),
                                   num_classes=NUM_CLASSES, dropout=0.1)
        f1 = _train_and_evaluate(model, train_dl, val_dl)
        assert f1 >= CATEGORY_F1_FLOOR, (
            f"Category F1={f1:.4f} below floor {CATEGORY_F1_FLOOR:.4f}"
        )


# ===================================================================
# NEXT-POI FIXTURE
# ===================================================================
# Calibration (5 runs, seed=42, CPU, 10 epochs, torch==2.9.1, 2026-03-26):
#   F1 values: [1.0, 1.0, 1.0, 1.0, 1.0]
#   mean=1.0000, std=0.000000, floor(mean-3*std)=1.0000
#   CPU determinism → std=0. Floor set to 0.99 for PyTorch version margin.
NEXT_F1_FLOOR = 0.99
NEXT_PARAM_COUNT = 101201

class TestNextRegression:
    """Regression fixture for standalone NextHeadSingle."""

    @pytest.fixture(autouse=True)
    def setup(self):
        seed_everything()

    # --- Layer 1: deterministic shapes ---
    def test_next_output_shape(self):
        from models.next import NextHeadSingle
        model = NextHeadSingle(embed_dim=EMBED_DIM, num_classes=NUM_CLASSES,
                               num_heads=4, seq_length=SEQ_LEN, num_layers=2, dropout=0.1)
        x = torch.randn(BATCH_SIZE, SEQ_LEN, EMBED_DIM)
        out = model(x)
        assert out.shape == (BATCH_SIZE, NUM_CLASSES)

    def test_next_param_count(self):
        from models.next import NextHeadSingle
        model = NextHeadSingle(embed_dim=EMBED_DIM, num_classes=NUM_CLASSES,
                               num_heads=4, seq_length=SEQ_LEN, num_layers=2, dropout=0.1)
        total = sum(p.numel() for p in model.parameters())
        assert total == NEXT_PARAM_COUNT, f"param count {total} != expected {NEXT_PARAM_COUNT}"

    # --- Layer 2: artifact structure ---
    def test_next_dataloader_shapes(self):
        X_train, y_train = make_next_data(NUM_TRAIN // NUM_CLASSES, seed=SEED)
        X_val, y_val = make_next_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)
        train_dl, val_dl = make_loaders(X_train, y_train, X_val, y_val)
        xb, yb = next(iter(train_dl))
        assert xb.shape == (BATCH_SIZE, SEQ_LEN, EMBED_DIM)
        assert yb.shape == (BATCH_SIZE,)

    # --- Layer 3: coarse metric ---
    def test_next_f1_within_tolerance(self):
        from models.next import NextHeadSingle
        seed_everything()
        X_train, y_train = make_next_data(NUM_TRAIN // NUM_CLASSES, seed=SEED)
        X_val, y_val = make_next_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)
        train_dl, val_dl = make_loaders(X_train, y_train, X_val, y_val)
        model = NextHeadSingle(embed_dim=EMBED_DIM, num_classes=NUM_CLASSES,
                               num_heads=4, seq_length=SEQ_LEN, num_layers=2, dropout=0.1)
        f1 = _train_and_evaluate(model, train_dl, val_dl)
        assert f1 >= NEXT_F1_FLOOR, (
            f"Next F1={f1:.4f} below floor {NEXT_F1_FLOOR:.4f}"
        )


# ===================================================================
# MTL FIXTURE
# ===================================================================
# Calibration (5 runs, seed=42, CPU, 10 epochs):
#   torch==2.9.1, sklearn==1.6.1, 2026-03-26:
#     cat_f1: [0.9286] × 5   next_f1: [1.0] × 5
#   torch==2.11.0, sklearn==1.8.0, 2026-04-14:
#     cat_f1: [0.8925] × 5   next_f1: [1.0] × 5
#   CPU determinism → std=0. Floors set with PyTorch version margin.
#   Floor shifted 0.92 -> 0.88 on 2026-04-14 after torch 2.9.1 -> 2.11.0 bump
#   changed the optimization trajectory on this synthetic fixture
#   (3.6 pp drop; next-task F1 and all other regression fixtures unaffected).
MTL_CAT_F1_FLOOR = 0.88
MTL_NEXT_F1_FLOOR = 0.99
MTL_PARAM_COUNT = 4307855

class TestMTLRegression:
    """Regression fixture for MTLnet (joint training)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        seed_everything()

    # --- Layer 1: deterministic shapes ---
    def test_mtl_output_shapes(self):
        from models.mtlnet import MTLnet
        model = MTLnet(
            feature_size=EMBED_DIM, shared_layer_size=256,
            num_classes=NUM_CLASSES, num_heads=8, num_layers=4,
            seq_length=SEQ_LEN, num_shared_layers=4,
        )
        cat_in = torch.randn(BATCH_SIZE, 1, EMBED_DIM)
        next_in = torch.randn(BATCH_SIZE, SEQ_LEN, EMBED_DIM)
        out_cat, out_next = model((cat_in, next_in))
        assert out_cat.shape == (BATCH_SIZE, NUM_CLASSES)
        assert out_next.shape == (BATCH_SIZE, NUM_CLASSES)

    def test_mtl_shared_vs_task_params(self):
        from models.mtlnet import MTLnet
        model = MTLnet(
            feature_size=EMBED_DIM, shared_layer_size=256,
            num_classes=NUM_CLASSES, num_heads=8, num_layers=4,
            seq_length=SEQ_LEN, num_shared_layers=4,
        )
        shared_ids = {id(p) for p in model.shared_parameters()}
        task_ids = {id(p) for p in model.task_specific_parameters()}
        all_ids = {id(p) for p in model.parameters()}
        # No overlap between shared and task-specific
        assert shared_ids & task_ids == set()
        # Together they cover all parameters
        assert shared_ids | task_ids == all_ids

    # --- Layer 2: artifact structure ---
    def test_mtl_different_batch_sizes(self):
        """MTL must handle different batch sizes for category and next tasks."""
        from models.mtlnet import MTLnet
        model = MTLnet(
            feature_size=EMBED_DIM, shared_layer_size=256,
            num_classes=NUM_CLASSES, num_heads=8, num_layers=4,
            seq_length=SEQ_LEN, num_shared_layers=4,
        )
        model.eval()
        # Different batch sizes (as happens in real MTL training)
        cat_in = torch.randn(32, 1, EMBED_DIM)
        next_in = torch.randn(48, SEQ_LEN, EMBED_DIM)
        out_cat, out_next = model((cat_in, next_in))
        assert out_cat.shape == (32, NUM_CLASSES)
        assert out_next.shape == (48, NUM_CLASSES)

    # --- Layer 3: coarse metric ---
    def test_mtl_f1_within_tolerance(self):
        from models.mtlnet import MTLnet
        seed_everything()
        X_cat_train, y_cat_train = make_category_data(NUM_TRAIN // NUM_CLASSES, seed=SEED)
        X_cat_val, y_cat_val = make_category_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)
        X_next_train, y_next_train = make_next_data(NUM_TRAIN // NUM_CLASSES, seed=SEED)
        X_next_val, y_next_val = make_next_data(NUM_VAL // NUM_CLASSES, seed=SEED + 1)

        cat_train_dl, cat_val_dl = make_loaders(X_cat_train, y_cat_train,
                                                  X_cat_val, y_cat_val)
        next_train_dl, next_val_dl = make_loaders(X_next_train, y_next_train,
                                                    X_next_val, y_next_val)

        model = MTLnet(
            feature_size=EMBED_DIM, shared_layer_size=256,
            num_classes=NUM_CLASSES, num_heads=8, num_layers=4,
            seq_length=SEQ_LEN, num_shared_layers=4,
        )
        cat_f1, next_f1 = _train_mtl_and_evaluate(
            model, cat_train_dl, cat_val_dl, next_train_dl, next_val_dl
        )
        assert cat_f1 >= MTL_CAT_F1_FLOOR, (
            f"MTL category F1={cat_f1:.4f} below floor {MTL_CAT_F1_FLOOR:.4f}"
        )
        assert next_f1 >= MTL_NEXT_F1_FLOOR, (
            f"MTL next F1={next_f1:.4f} below floor {MTL_NEXT_F1_FLOOR:.4f}"
        )
