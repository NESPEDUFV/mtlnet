"""Unit tests for training callback primitives (Phase 8)."""
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from training.callbacks import (
    Callback,
    CallbackContext,
    CallbackList,
    EarlyStopping,
    ModelCheckpoint,
)


# ---------------------------------------------------------------------------
# CallbackContext
# ---------------------------------------------------------------------------

class TestCallbackContext:
    def test_defaults(self):
        ctx = CallbackContext()
        assert ctx.epoch == 0
        assert ctx.epochs_total == 0
        assert ctx.fold == 0
        assert ctx.num_folds == 0
        assert ctx.metrics == {}

    def test_with_metrics(self):
        ctx = CallbackContext(epoch=3, epochs_total=10, metrics={"val_f1": 0.85})
        assert ctx.epoch == 3
        assert ctx.metrics["val_f1"] == 0.85


# ---------------------------------------------------------------------------
# Callback base class
# ---------------------------------------------------------------------------

class TestCallback:
    def test_stop_training_default_false(self):
        cb = Callback()
        assert cb.stop_training is False

    def test_hooks_are_noop(self):
        """All hooks run without error and return None."""
        cb = Callback()
        ctx = CallbackContext()
        assert cb.on_train_begin(ctx) is None
        assert cb.on_epoch_end(ctx) is None
        assert cb.on_train_end(ctx) is None


# ---------------------------------------------------------------------------
# CallbackList
# ---------------------------------------------------------------------------

class _RecordingCallback(Callback):
    """Test helper that records which hooks were called."""

    def __init__(self, name: str = ""):
        super().__init__()
        self.name = name
        self.calls: list[str] = []

    def on_train_begin(self, ctx):
        self.calls.append("train_begin")

    def on_epoch_end(self, ctx):
        self.calls.append("epoch_end")

    def on_train_end(self, ctx):
        self.calls.append("train_end")


class TestCallbackList:
    def test_empty_list(self):
        cl = CallbackList([])
        assert cl.stop_training is False
        ctx = CallbackContext()
        cl.on_train_begin(ctx)
        cl.on_epoch_end(ctx)
        cl.on_train_end(ctx)

    def test_none_argument(self):
        cl = CallbackList(None)
        assert cl.callbacks == []
        assert cl.stop_training is False

    def test_dispatches_in_order(self):
        a = _RecordingCallback("a")
        b = _RecordingCallback("b")
        cl = CallbackList([a, b])
        ctx = CallbackContext()
        cl.on_train_begin(ctx)
        cl.on_epoch_end(ctx)
        cl.on_train_end(ctx)
        assert a.calls == ["train_begin", "epoch_end", "train_end"]
        assert b.calls == ["train_begin", "epoch_end", "train_end"]

    def test_stop_training_any(self):
        a = Callback()
        b = Callback()
        cl = CallbackList([a, b])
        assert cl.stop_training is False
        b.stop_training = True
        assert cl.stop_training is True

    def test_stop_training_all_false(self):
        cl = CallbackList([Callback(), Callback()])
        assert cl.stop_training is False


# ---------------------------------------------------------------------------
# EarlyStopping
# ---------------------------------------------------------------------------

class TestEarlyStopping:
    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="mode must be"):
            EarlyStopping(mode="bad")

    def test_patience_triggers_stop(self):
        es = EarlyStopping(monitor="val_f1", patience=3, mode="max")
        # Epoch 0: best improves
        es.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.8}))
        assert not es.stop_training
        assert es.best == 0.8
        assert es.wait == 0

        # Epochs 1-3: no improvement
        for i in range(1, 4):
            es.on_epoch_end(CallbackContext(epoch=i, metrics={"val_f1": 0.7}))

        assert es.stop_training is True
        assert es.wait == 3

    def test_resets_on_improvement(self):
        es = EarlyStopping(monitor="val_f1", patience=3, mode="max")
        es.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.8}))
        es.on_epoch_end(CallbackContext(epoch=1, metrics={"val_f1": 0.7}))
        assert es.wait == 1

        # Improvement resets counter
        es.on_epoch_end(CallbackContext(epoch=2, metrics={"val_f1": 0.9}))
        assert es.wait == 0
        assert es.best == 0.9
        assert es.best_epoch == 2
        assert not es.stop_training

    def test_mode_min(self):
        es = EarlyStopping(monitor="val_loss", patience=2, mode="min")
        es.on_epoch_end(CallbackContext(epoch=0, metrics={"val_loss": 1.0}))
        assert es.best == 1.0

        es.on_epoch_end(CallbackContext(epoch=1, metrics={"val_loss": 0.5}))
        assert es.best == 0.5
        assert es.wait == 0

        es.on_epoch_end(CallbackContext(epoch=2, metrics={"val_loss": 0.6}))
        assert es.wait == 1

        es.on_epoch_end(CallbackContext(epoch=3, metrics={"val_loss": 0.7}))
        assert es.stop_training is True

    def test_min_delta(self):
        es = EarlyStopping(monitor="val_f1", patience=2, mode="max", min_delta=0.01)
        es.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.8}))

        # Tiny improvement (< min_delta) doesn't count
        es.on_epoch_end(CallbackContext(epoch=1, metrics={"val_f1": 0.805}))
        assert es.wait == 1  # 0.005 < 0.01, not counted as improvement

        # Real improvement (>= min_delta)
        es.on_epoch_end(CallbackContext(epoch=2, metrics={"val_f1": 0.82}))
        assert es.wait == 0  # 0.02 > 0.01, counts

    def test_missing_metric_warns(self, caplog):
        es = EarlyStopping(monitor="nonexistent", patience=2)
        with caplog.at_level(logging.WARNING):
            es.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.8}))
        assert "nonexistent" in caplog.text
        assert not es.stop_training

    def test_first_epoch_always_sets_best(self):
        es = EarlyStopping(monitor="val_f1", patience=5, mode="max")
        assert es.best is None
        es.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.0}))
        assert es.best == 0.0

    def test_on_train_begin_resets_per_fold(self):
        """AUDIT-C3: state must reset between folds. Without the reset,
        EarlyStopping firing in fold 1 would silently kill folds 2-5
        at epoch 1. Runners call ``on_train_begin`` per-fold."""
        es = EarlyStopping(monitor="val_f1", patience=2, mode="max")
        # Fold 1: trigger early stop
        es.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.8}))
        for i in range(1, 3):
            es.on_epoch_end(CallbackContext(epoch=i, metrics={"val_f1": 0.7}))
        assert es.stop_training is True

        # Fold 2 begins — must reset to fresh state
        es.on_train_begin(CallbackContext(epoch=0))
        assert es.stop_training is False
        assert es.wait == 0
        assert es.best is None
        assert es.best_epoch == -1
        assert es.wait == 0


# ---------------------------------------------------------------------------
# ModelCheckpoint
# ---------------------------------------------------------------------------

class TestModelCheckpoint:
    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="mode must be"):
            ModelCheckpoint(save_dir="/tmp", mode="bad")

    def test_no_model_skips(self):
        mc = ModelCheckpoint(save_dir="/tmp/test_ckpt")
        # No model set, should silently skip
        mc.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.9}))
        # No crash, no save

    def test_no_metric_skips(self):
        mc = ModelCheckpoint(save_dir="/tmp/test_ckpt", monitor="val_f1")
        mc.set_model(MagicMock())
        mc.on_epoch_end(CallbackContext(epoch=0, metrics={}))
        # No crash

    def test_save_best_only(self, tmp_path):
        import torch

        model = torch.nn.Linear(2, 2)
        mc = ModelCheckpoint(save_dir=tmp_path / "ckpts", monitor="val_f1", save_best_only=True)
        mc.set_model(model)

        # Epoch 0: first, always saves
        mc.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.7}))
        assert (tmp_path / "ckpts" / "checkpoint_epoch_1.pt").exists()

        # Epoch 1: worse, doesn't save
        mc.on_epoch_end(CallbackContext(epoch=1, metrics={"val_f1": 0.6}))
        assert not (tmp_path / "ckpts" / "checkpoint_epoch_2.pt").exists()

        # Epoch 2: better, saves
        mc.on_epoch_end(CallbackContext(epoch=2, metrics={"val_f1": 0.8}))
        assert (tmp_path / "ckpts" / "checkpoint_epoch_3.pt").exists()

    def test_save_every_epoch(self, tmp_path):
        import torch

        model = torch.nn.Linear(2, 2)
        mc = ModelCheckpoint(save_dir=tmp_path / "ckpts", save_best_only=False)
        mc.set_model(model)

        for i in range(3):
            mc.on_epoch_end(CallbackContext(epoch=i, metrics={"val_f1": 0.5}))

        assert (tmp_path / "ckpts" / "checkpoint_epoch_1.pt").exists()
        assert (tmp_path / "ckpts" / "checkpoint_epoch_2.pt").exists()
        assert (tmp_path / "ckpts" / "checkpoint_epoch_3.pt").exists()

    def test_set_model(self):
        mc = ModelCheckpoint(save_dir="/tmp")
        assert mc._model is None
        mock_model = MagicMock()
        mc.set_model(mock_model)
        assert mc._model is mock_model

    def test_on_train_begin_resets_per_fold(self, tmp_path):
        """AUDIT-C3: ``self.best`` must reset between folds, otherwise
        fold 2 inherits fold 1's high-water mark and may save 0
        checkpoints if its val curve is shifted lower."""
        import torch

        model = torch.nn.Linear(2, 2)
        mc = ModelCheckpoint(save_dir=tmp_path / "ckpts", save_best_only=True)
        mc.set_model(model)

        # Fold 1: saves at epoch 0 (best), then no improvements
        mc.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.9}))
        assert mc.best == 0.9
        mc.on_epoch_end(CallbackContext(epoch=1, metrics={"val_f1": 0.8}))
        assert mc.best == 0.9  # unchanged

        # Fold 2 begins — must reset
        mc.on_train_begin(CallbackContext(epoch=0))
        assert mc.best is None

        # Fold 2's first epoch (val_f1=0.85) must register as the new best
        mc.on_epoch_end(CallbackContext(epoch=0, metrics={"val_f1": 0.85}))
        assert mc.best == 0.85
