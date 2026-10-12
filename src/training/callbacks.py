"""Training callbacks for epoch-level lifecycle hooks.

Provides a Keras-inspired callback protocol that plugs into the three training
runners (MTL, category, next). All callbacks are optional and additive -- they
never replace existing early-stopping logic in the runners.

Created in Phase 8 of the refactoring plan.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

logger = logging.getLogger(__name__)


@dataclass
class CallbackContext:
    """Read-only snapshot of training state, passed to every callback hook.

    Runners populate the fields they have; unset fields keep defaults.
    Metric keys vary by runner:
        category: val_f1, val_loss, val_acc, train_loss, train_acc
        next:     val_f1, val_loss, val_acc, train_loss, train_acc, train_f1, grad_norm
        mtl:      val_f1_next, val_f1_category, val_loss, train_loss,
                  train_f1_next, train_f1_category
    """

    epoch: int = 0
    epochs_total: int = 0
    fold: int = 0
    num_folds: int = 0
    metrics: dict[str, float] = field(default_factory=dict)


class Callback:
    """Base class for training callbacks.

    Subclasses override the hooks they need. To request training stop,
    set ``self.stop_training = True`` inside any hook.
    """

    def __init__(self):
        self.stop_training: bool = False

    def on_train_begin(self, ctx: CallbackContext) -> None:
        """Called once before the first epoch."""

    def on_epoch_end(self, ctx: CallbackContext) -> None:
        """Called after validation at the end of each epoch."""

    def on_train_end(self, ctx: CallbackContext) -> None:
        """Called once after the last epoch (or after early stop)."""


class CallbackList:
    """Composes multiple callbacks and dispatches hooks in order.

    Aggregates the ``stop_training`` signal: if ANY callback sets it,
    the list reports ``stop_training=True``.
    """

    def __init__(self, callbacks: Optional[Sequence[Callback]] = None):
        self.callbacks: list[Callback] = list(callbacks) if callbacks else []

    @property
    def stop_training(self) -> bool:
        return any(cb.stop_training for cb in self.callbacks)

    def on_train_begin(self, ctx: CallbackContext) -> None:
        for cb in self.callbacks:
            cb.on_train_begin(ctx)

    def on_epoch_end(self, ctx: CallbackContext) -> None:
        for cb in self.callbacks:
            cb.on_epoch_end(ctx)

    def on_train_end(self, ctx: CallbackContext) -> None:
        for cb in self.callbacks:
            cb.on_train_end(ctx)


class EarlyStopping(Callback):
    """Stop training when a monitored metric stops improving.

    Args:
        monitor: Metric key in ``CallbackContext.metrics`` to watch.
        patience: Epochs with no improvement before stopping.
        mode: ``'min'`` or ``'max'`` — direction of improvement.
        min_delta: Minimum change to qualify as improvement.
    """

    def __init__(
        self,
        monitor: str = "val_f1",
        patience: int = 10,
        mode: str = "max",
        min_delta: float = 0.0,
    ):
        super().__init__()
        if mode not in ("min", "max"):
            raise ValueError(f"mode must be 'min' or 'max', got {mode!r}")
        self.monitor = monitor
        self.patience = patience
        self.mode = mode
        self.min_delta = abs(min_delta)
        self.wait: int = 0
        self.best: Optional[float] = None
        self.best_epoch: int = -1

    def _is_improvement(self, current: float, best: float) -> bool:
        if self.mode == "max":
            return current > best + self.min_delta
        return current < best - self.min_delta

    def on_train_begin(self, ctx: CallbackContext) -> None:
        # AUDIT-C3 — reset per-fold state. Without this, stop_training /
        # wait / best persist across folds: if EarlyStopping fires in
        # fold 1, every later fold stops at epoch 1 immediately.
        # Currently dormant (no MTL recipe enables EarlyStopping) but a
        # silent landmine that silently destroyed runs the moment anyone
        # added it.
        self.stop_training = False
        self.wait = 0
        self.best = None
        self.best_epoch = -1

    def on_epoch_end(self, ctx: CallbackContext) -> None:
        current = ctx.metrics.get(self.monitor)
        if current is None:
            logger.warning(
                "EarlyStopping: metric '%s' not found in context. "
                "Available: %s",
                self.monitor,
                list(ctx.metrics.keys()),
            )
            return

        if self.best is None or self._is_improvement(current, self.best):
            self.best = current
            self.best_epoch = ctx.epoch
            self.wait = 0
        else:
            self.wait += 1

        if self.wait >= self.patience:
            self.stop_training = True
            logger.info(
                "EarlyStopping: stopping at epoch %d. "
                "Best %s=%.4f at epoch %d.",
                ctx.epoch + 1,
                self.monitor,
                self.best,
                self.best_epoch + 1,
            )


class ModelCheckpoint(Callback):
    """Save model checkpoints to disk based on a monitored metric.

    The model reference must be injected via :meth:`set_model` before
    training begins (runners do this automatically when callbacks are provided).

    Args:
        save_dir: Directory to write checkpoint files.
        monitor: Metric key in ``CallbackContext.metrics`` to track.
        mode: ``'min'`` or ``'max'`` — direction of improvement.
        save_best_only: If True, only save when monitor improves.
    """

    def __init__(
        self,
        save_dir: str | Path,
        monitor: str = "val_f1",
        mode: str = "max",
        save_best_only: bool = True,
    ):
        super().__init__()
        if mode not in ("min", "max"):
            raise ValueError(f"mode must be 'min' or 'max', got {mode!r}")
        self.save_dir = Path(save_dir)
        self.monitor = monitor
        self.mode = mode
        self.save_best_only = save_best_only
        self.best: Optional[float] = None
        self._model = None

    def set_model(self, model) -> None:
        """Inject the model reference. Called by runners before training."""
        self._model = model

    def _is_improvement(self, current: float, best: float) -> bool:
        if self.mode == "max":
            return current > best
        return current < best

    def on_train_begin(self, ctx: CallbackContext) -> None:
        # AUDIT-C3 — reset per-fold checkpoint baseline. Without this,
        # ``self.best`` persists across folds: fold 2 effectively
        # "competes" against fold 1's best and the saved checkpoint
        # files for fold 2+ are silently inconsistent with the best
        # captured in tracking.fold's BestModelTracker.
        self.best = None

    def on_epoch_end(self, ctx: CallbackContext) -> None:
        if self._model is None:
            return
        current = ctx.metrics.get(self.monitor)
        if current is None:
            return

        should_save = False
        if self.save_best_only:
            if self.best is None or self._is_improvement(current, self.best):
                self.best = current
                should_save = True
        else:
            should_save = True

        if should_save:
            import torch

            self.save_dir.mkdir(parents=True, exist_ok=True)
            path = self.save_dir / f"checkpoint_epoch_{ctx.epoch + 1}.pt"
            torch.save(self._model.state_dict(), path)
            logger.debug("ModelCheckpoint: saved %s (metric=%.4f)", path, current)
