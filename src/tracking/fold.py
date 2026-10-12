from __future__ import annotations

from typing import Any, Mapping, Optional

from tracking.best_tracker import BestModelTracker
from tracking.metric_store import MetricStore
from tracking.utils.time_history import TimeHistory


class TaskHistory:
    """Per-task tracking within a fold.

    Holds separate train/val MetricStores, a BestModelTracker,
    and an optional classification report.

    Usage:
        th = TaskHistory(monitor='f1', mode='max')
        th.log_train(loss=0.5, accuracy=0.8, f1=0.6)
        th.log_val(loss=0.4, accuracy=0.85, f1=0.7, model_state=state)
        th.report = classification_report_dict
    """

    def __init__(self, monitor: str = 'f1', mode: str = 'max', min_epoch: int = 0):
        self.train = MetricStore()
        self.val = MetricStore()
        self.best = BestModelTracker(monitor=monitor, mode=mode, min_epoch=min_epoch)
        self.report: dict = {}

    def log_train(self, **kwargs: float) -> None:
        """Log training metrics for one epoch."""
        self.train.log(**kwargs)

    def log_val(
        self,
        model_state: dict | None = None,
        elapsed_time: float = 0.0,
        **kwargs: float,
    ) -> None:
        """Log validation metrics for one epoch. Optionally update best model."""
        self.val.log(**kwargs)
        if model_state is not None and self.best.monitor in kwargs:
            self.best.update(
                epoch=self.val.num_epochs() - 1,
                metric_value=kwargs[self.best.monitor],
                model_state=model_state,
                elapsed_time=elapsed_time,
            )


class FoldHistory:
    """Per-fold tracking. Contains task histories and fold-level diagnostics.

    Replaces the old 4-level hierarchy:
    FoldHistory -> FoldHistoryMetric -> TaskTrainMetric/TaskOutcome

    Now it's just: FoldHistory -> TaskHistory (with MetricStore inside).

    Usage:
        fold = FoldHistory(0, {'next', 'category'})
        fold.start()

        # Per-epoch:
        fold.log_train('next', loss=0.5, f1=0.6)
        fold.log_val('next', loss=0.3, f1=0.8, model_state=state)
        fold.log_diagnostic(grad_norm=1.2, learning_rate=1e-3)

        # Post-training:
        fold.task('next').report = report_dict
        fold.add_artifact('confusion_matrix', {...})
        fold.end()
    """

    def __init__(
        self,
        fold_number: int,
        tasks: set[str],
        monitor: str = 'f1',
        mode: str = 'max',
        task_monitors: Optional[Mapping[str, str]] = None,
        min_epoch: int = 0,
    ):
        """
        Parameters
        ----------
        monitor:
            Default monitor metric for tasks not listed in ``task_monitors``.
        task_monitors:
            AUDIT-C2 fix — per-task monitor override. Maps task name to
            metric key (e.g. ``{"next_region": "accuracy"}``). Tasks not
            in the map fall back to ``monitor``. The trainer derives this
            from ``TaskConfig.primary_metric``; default ``None`` preserves
            the legacy single-metric (F1) behaviour.
        min_epoch:
            F50 B1 — earliest epoch eligible to be selected as best by
            any of this fold's BestModelTracker instances. Defends
            against init-artifact peaks (e.g. GETNext α_init=2.0 epoch
            1 is the prior alone, not learned signal — ``min_epoch=2``
            forces the selector past it).
        """
        self.fold_number = fold_number
        self.timer = TimeHistory()
        per_task = dict(task_monitors or {})
        self.tasks: dict[str, TaskHistory] = {
            task: TaskHistory(
                monitor=per_task.get(task, monitor), mode=mode, min_epoch=min_epoch,
            )
            for task in tasks
        }
        self.diagnostics = MetricStore()
        self.artifacts: dict[str, Any] = {}
        self.model_task: TaskHistory | None = None

    def task(self, name: str) -> TaskHistory:
        """Get task history by name."""
        if name not in self.tasks:
            available = list(self.tasks.keys())
            raise ValueError(
                f"Task '{name}' not found in fold {self.fold_number}. "
                f"Available: {available}"
            )
        return self.tasks[name]

    def log_train(self, task_name: str, **kwargs: float) -> None:
        """Convenience: log training metrics for a task."""
        self.task(task_name).log_train(**kwargs)

    def log_val(
        self,
        task_name: str,
        model_state: dict | None = None,
        elapsed_time: float = 0.0,
        **kwargs: float,
    ) -> None:
        """Convenience: log validation metrics for a task."""
        self.task(task_name).log_val(
            model_state=model_state, elapsed_time=elapsed_time, **kwargs
        )

    def log_diagnostic(self, **kwargs: float) -> None:
        """Log epoch-level diagnostics (grad_norms, learning_rates, etc.)."""
        self.diagnostics.log(**kwargs)

    def add_artifact(self, key: str, value: Any) -> None:
        """Store a one-shot artifact (confusion_matrix, attention_weights, etc.)."""
        self.artifacts[key] = value

    def start(self):
        self.timer.start()

    def end(self):
        self.timer.stop()

    @classmethod
    def standalone(cls, tasks: set[str], **kwargs) -> FoldHistory:
        """Create a standalone FoldHistory (for single-fold usage without MLHistory)."""
        history = cls(fold_number=0, tasks=tasks, **kwargs)
        history.start()
        return history
