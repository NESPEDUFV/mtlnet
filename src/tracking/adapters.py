"""Optional external tracking adapters (W&B, MLflow).

All adapters are opt-in. When no adapter is configured, tracking remains
purely local (file-based via HistoryStorage). Adapters hook into MLHistory
at fold boundaries and run completion to push metrics externally.

Usage:
    # Enable via environment variable:
    TRACKING_BACKEND=wandb python scripts/train.py ...

    # Or programmatically:
    from tracking.adapters import create_adapter
    adapter = create_adapter("wandb", project="my-project")
    history = MLHistory(...)
    history.set_adapter(adapter)

Created in Phase 8 of the refactoring plan.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TrackingAdapter:
    """Base class for external tracking integrations.

    Subclasses override hooks to push data to external services.
    All methods are no-ops by default — safe to call even if the
    external service is unavailable.
    """

    def on_run_start(self, config: dict) -> None:
        """Called when training begins. Receives experiment config as dict."""

    def log_metrics(self, metrics: dict[str, float], step: int = 0) -> None:
        """Log scalar metrics at a given step (epoch or fold)."""

    def log_artifact(self, name: str, path: str) -> None:
        """Log a file artifact (model checkpoint, report, etc.)."""

    def on_fold_end(self, fold_idx: int, fold_metrics: dict[str, Any]) -> None:
        """Called after each fold completes."""

    def on_run_end(self, summary: dict[str, Any]) -> None:
        """Called when training finishes. Receives summary statistics."""

    def close(self) -> None:
        """Clean up resources (finalize run, close connections)."""


class WandBAdapter(TrackingAdapter):
    """Weights & Biases tracking adapter.

    Requires ``wandb`` to be installed. Import is deferred to first use.

    Args:
        project: W&B project name.
        entity: W&B entity (team or user). None uses default.
        run_name: Optional run name. None auto-generates.
        tags: Optional list of tags for the run.
        kwargs: Additional arguments passed to ``wandb.init()``.
    """

    def __init__(
        self,
        project: str = "mtlnet",
        entity: Optional[str] = None,
        run_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        **kwargs,
    ):
        super().__init__()
        self.project = project
        self.entity = entity
        self.run_name = run_name
        self.tags = tags
        self.init_kwargs = kwargs
        self._run = None

    def _ensure_init(self, config: Optional[dict] = None) -> None:
        """Lazily initialize the W&B run."""
        if self._run is not None:
            return
        try:
            import wandb

            self._run = wandb.init(
                project=self.project,
                entity=self.entity,
                name=self.run_name,
                tags=self.tags,
                config=config or {},
                **self.init_kwargs,
            )
            logger.info("W&B run initialized: %s", self._run.url)
        except Exception as e:
            logger.warning("W&B initialization failed: %s", e)
            self._run = None

    def on_run_start(self, config: dict) -> None:
        self._ensure_init(config)

    def log_metrics(self, metrics: dict[str, float], step: int = 0) -> None:
        if self._run is None:
            return
        import wandb

        wandb.log(metrics, step=step)

    def log_artifact(self, name: str, path: str) -> None:
        if self._run is None:
            return
        import wandb

        artifact = wandb.Artifact(name, type="model")
        artifact.add_file(path)
        self._run.log_artifact(artifact)

    def on_fold_end(self, fold_idx: int, fold_metrics: dict[str, Any]) -> None:
        if self._run is None:
            return
        import wandb

        prefixed = {f"fold_{fold_idx}/{k}": v for k, v in fold_metrics.items()}
        wandb.log(prefixed)

    def on_run_end(self, summary: dict[str, Any]) -> None:
        if self._run is None:
            return
        import wandb

        for key, value in summary.items():
            wandb.run.summary[key] = value

    def close(self) -> None:
        if self._run is not None:
            import wandb

            wandb.finish()
            self._run = None


def create_adapter(
    backend: Optional[str] = None, **kwargs
) -> Optional[TrackingAdapter]:
    """Factory function to create a tracking adapter.

    Args:
        backend: ``"wandb"``, ``"mlflow"``, or ``None`` (disabled).
            If not provided, reads from ``TRACKING_BACKEND`` env var.
        **kwargs: Passed to the adapter constructor.

    Returns:
        A TrackingAdapter instance, or None if tracking is disabled.
    """
    if backend is None:
        backend = os.environ.get("TRACKING_BACKEND", "").lower().strip()

    if not backend:
        return None

    if backend == "wandb":
        return WandBAdapter(**kwargs)

    logger.warning("Unknown tracking backend: %r. Tracking disabled.", backend)
    return None
