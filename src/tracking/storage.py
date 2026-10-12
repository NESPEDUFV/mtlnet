from pathlib import Path
import json
import logging
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from statistics import mean, stdev

logger = logging.getLogger(__name__)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')

if TYPE_CHECKING:
    from tracking.experiment import MLHistory


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


class _SafeEncoder(json.JSONEncoder):
    """JSON encoder that handles non-serializable types gracefully."""

    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        try:
            import torch
            if isinstance(obj, torch.Tensor):
                return obj.detach().cpu().tolist()
            if isinstance(obj, torch.dtype):
                return str(obj)
        except ImportError:
            pass
        return str(obj)


def save_json(data: Any, path: Path) -> None:
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, cls=_SafeEncoder)


def save_text(data: str, path: Path) -> None:
    with path.open('w', encoding='utf-8') as f:
        f.write(data)


def save_csv(df: pd.DataFrame, path: Path, **kwargs) -> None:
    df.to_csv(path, index=False, **kwargs)


def map_category(key: Union[int, float, str], label_map: Dict = None) -> str:
    """Convert numeric or string keys to category names using label_map."""
    if label_map is None:
        return str(key)
    try:
        idx = int(float(key))
        return label_map.get(idx, f"Unknown-{key}")
    except Exception:
        return str(key)


class SummaryGenerator:
    """Generate overall and per-category performance summaries."""

    def __init__(self, history: 'MLHistory', label_map: Optional[Dict] = None):
        self.history = history
        self.label_map = label_map or {}

    def generate(self, out_dir: Path) -> None:
        out = ensure_dir(out_dir)
        perf = self._collect_performance()
        diagnostic_perf = self._collect_task_best_performance()
        per_metric_perf = self._collect_per_metric_best_performance()
        cat_metrics = self._collect_category_metrics()

        # Stamp every aggregate with its aggregation_basis so downstream readers
        # know which best-epoch convention produced each block. Three bases coexist:
        #   joint_best        — model-level joint score selection (MTL)
        #   per_task_f1_best  — each task's own F1-best epoch
        #   per_metric_best   — each (task, metric) at its own best epoch
        primary_basis = 'joint_best' if self._has_joint_selection() else 'per_task_f1_best'
        stats: Dict[str, Any] = {
            task: {
                'aggregation_basis': primary_basis,
                **{metric: self._stats(vals) for metric, vals in metrics.items()},
            }
            for task, metrics in perf.items()
        }
        if diagnostic_perf:
            stats['_selection'] = {
                'primary': 'joint_score' if self._has_joint_selection() else 'task_best',
                'primary_basis': primary_basis,
                'diagnostic_task_best': 'per-task best validation f1',
                'diagnostic_basis': 'per_task_f1_best',
                'per_metric_best': 'each (task,metric) aggregated at its own best epoch',
                'per_metric_basis': 'per_metric_best',
            }
            stats['diagnostic_task_best'] = {
                task: {
                    'aggregation_basis': 'per_task_f1_best',
                    **{metric: self._stats(vals) for metric, vals in metrics.items()},
                }
                for task, metrics in diagnostic_perf.items()
            }
        if per_metric_perf:
            stats['per_metric_best'] = {
                task: {
                    'aggregation_basis': 'per_metric_best',
                    **{metric: self._stats(vals) for metric, vals in metrics.items()},
                }
                for task, metrics in per_metric_perf.items()
            }
        # Fan-out guard: under --run-id this process may have run only a SUBSET of folds.
        # The per-fold artifacts are named by real id, but this full_summary aggregates only
        # THIS process's folds and is overwritten last-writer-wins in the shared rundir. Stamp
        # it so a partial can't masquerade as the complete run (default path is unaffected).
        if getattr(self.history, 'run_id', None) is not None:
            stats['_fanout'] = {
                'run_id': self.history.run_id,
                'folds_in_this_process': list(self.history.fold_ids) if self.history.fold_ids else None,
                'warning': 'fan-out (--run-id): this summary may cover only a SUBSET of the folds and '
                           'is overwritten per-process. For the complete run, use '
                           'scripts/aggregate_folds.py <rundir> → fold_aggregate.json.',
            }
        save_json(stats, out / 'full_summary.json')

        # Category summaries
        for task, cats in cat_metrics.items():
            df = pd.DataFrame([
                {
                    'Category': cat,
                    **{m: mean(vals) if vals else 0 for m, vals in metrics.items()},
                }
                for cat, metrics in cats.items()])
            df_fmt = pd.DataFrame([{
                'Category': cat,
                **{
                    m: (f"{mean(vals) * 100:.2f} ± {stdev(vals) * 100:.2f}"
                        if len(vals) > 1
                        else f"{mean(vals) * 100:.2f}")
                    for m, vals in metrics.items()
                },
            } for cat, metrics in cats.items()])

            if not df.empty:
                save_csv(df, out / f'summary_{task}_metrics.csv', float_format='%.4f')

            if not df_fmt.empty:
                save_csv(df_fmt, out / f'summary_{task}_metrics_formatted.csv', float_format='%.4f')

    @staticmethod
    def _stats(values: List[float]) -> Dict[str, float]:
        if not values:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        return {
            'mean': mean(values),
            'std': stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
        }

    def _collect_performance(self) -> Dict[str, Dict[str, List[float]]]:
        """Collect primary checkpoint metrics dynamically from val MetricStore.

        For MTL folds, the primary checkpoint is the model-level joint score.
        Per-task best epochs are intentionally handled separately as diagnostics.
        For single-task runs, this falls back to each task's own best epoch.
        """
        perf: Dict[str, Dict[str, List[float]]] = {}
        for fold in self.history.folds:
            joint_epoch = -1
            if fold.model_task is not None and fold.model_task.best.best_epoch >= 0:
                joint_epoch = fold.model_task.best.best_epoch
                model_perf = perf.setdefault('model', {})
                model_perf.setdefault('joint_score', []).append(
                    fold.model_task.best.best_value
                )
                loss_vals = fold.model_task.val.get('loss')
                if loss_vals and joint_epoch < len(loss_vals):
                    model_perf.setdefault('loss', []).append(loss_vals[joint_epoch])

            for task in self.history.tasks:
                th = fold.tasks.get(task)
                if not th:
                    continue
                if task not in perf:
                    perf[task] = {}
                best_epoch = joint_epoch if joint_epoch >= 0 else th.best.best_epoch
                if best_epoch < 0:
                    continue
                for metric_name, values in th.val.items():
                    if best_epoch < len(values):
                        perf[task].setdefault(metric_name, []).append(values[best_epoch])
        return perf

    def _collect_task_best_performance(self) -> Dict[str, Dict[str, List[float]]]:
        """Collect diagnostic per-task best-epoch metrics."""
        if not self._has_joint_selection():
            return {}

        perf: Dict[str, Dict[str, List[float]]] = {}
        for fold in self.history.folds:
            for task in self.history.tasks:
                th = fold.tasks.get(task)
                if not th:
                    continue
                best_epoch = th.best.best_epoch
                if best_epoch < 0:
                    continue
                task_perf = perf.setdefault(task, {})
                for metric_name, values in th.val.items():
                    if best_epoch < len(values):
                        task_perf.setdefault(metric_name, []).append(values[best_epoch])
        return perf

    def _collect_per_metric_best_performance(self) -> Dict[str, Dict[str, List[float]]]:
        """Collect each (task, metric) at its OWN best epoch across folds.

        Companion to the per-fold ``per_metric_best`` block written into
        ``fold_info.json``. Aggregates the per-metric-best value series so
        ``full_summary.json`` carries a third aggregate basis next to
        ``joint_best`` and ``per_task_f1_best``.
        """
        perf: Dict[str, Dict[str, List[float]]] = {}
        for fold in self.history.folds:
            for task in self.history.tasks:
                th = fold.tasks.get(task)
                if not th:
                    continue
                task_perf = perf.setdefault(task, {})
                for metric_name, values in th.val.items():
                    if not values:
                        continue
                    best_value = max(values)
                    task_perf.setdefault(metric_name, []).append(best_value)
        return perf

    def _has_joint_selection(self) -> bool:
        return any(
            fold.model_task is not None and fold.model_task.best.best_epoch >= 0
            for fold in self.history.folds
        )

    def _collect_category_metrics(self) -> Dict[str, Dict[str, Dict[str, List[float]]]]:
        result: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
        for fold in self.history.folds:
            for task in self.history.tasks:
                th = fold.tasks.get(task)
                if not th or not th.report:
                    continue
                for cat, vals in th.report.items():
                    if not isinstance(vals, dict) or cat in ('accuracy', 'weighted avg'):
                        continue
                    name = cat if cat == 'macro avg' else map_category(cat, self.label_map)
                    task_dict = result.setdefault(task, {})
                    metrics = task_dict.setdefault(name, {'precision': [], 'recall': [], 'f1-score': [], 'support': []})
                    for m in metrics:
                        if m in vals:
                            metrics[m].append(vals[m])
        return result


class HistoryStorage:
    """Save model configuration, metrics, reports, summaries, and plots."""

    def __init__(self, history: 'MLHistory') -> None:
        self.history = history
        self._label_map: Dict = {}

    def save(self, path: Union[str, Path], label_map: Optional[Dict[int, str]] = None) -> Path:
        """Save all results.

        Args:
            path: Output directory.
            label_map: Optional mapping of class indices to display names.
                       Replaces the old CATEGORIES_MAP coupling.
        """
        self._label_map = label_map or {}
        base = ensure_dir(Path(path) / self._folder_name())
        dirs = {k: ensure_dir(base / k) for k in ('model', 'metrics', 'folds', 'summary', 'plots', 'diagnostics')}

        self._save_params(dirs['model'])
        self._save_metrics(dirs['metrics'])
        self._save_reports(dirs['folds'])
        SummaryGenerator(self.history, self._label_map).generate(dirs['summary'])
        self._save_plots(dirs['plots'])
        self._save_diagnostics(dirs['diagnostics'])

        return base

    def save_fold_partial(
        self,
        fold_idx: int,
        path: Union[str, Path],
        label_map: Optional[Dict[int, str]] = None,
    ) -> Path:
        """Persist *just* the completed fold's artefacts to disk.

        Called from ``MLHistory.step()`` after each fold finishes so that a
        mid-CV crash (e.g. OOM SIGKILL on long MPS runs) doesn't wipe every
        completed fold. Writes ``fold{i}_info.json``, per-task report JSON +
        CSV, and per-task train/val metrics CSV for fold ``fold_idx`` (0-based).

        Idempotent: re-invoking on the same fold rewrites the files. The
        end-of-CV ``save()`` runs the full pipeline (params, plots, summary,
        diagnostics) and is the canonical artefact for downstream analysis;
        this partial save only guarantees per-fold data survives a crash.

        Args:
            fold_idx: 0-based index of the fold that just completed.
            path: Same ``path`` that would be passed to ``save()``.
            label_map: Optional class-index → display-name mapping.

        Returns:
            The per-run directory path (same ``base`` the full ``save()`` would
            return).
        """
        self._label_map = label_map or {}
        base = ensure_dir(Path(path) / self._folder_name())
        dirs = {k: ensure_dir(base / k) for k in ('folds', 'metrics')}

        # Inline the fold-level subset of _save_metrics / _save_reports for just
        # this fold, rather than touching those end-of-CV methods.
        try:
            self._save_fold_metrics(dirs['metrics'], fold_idx)
            self._save_fold_report(dirs['folds'], fold_idx)
        except Exception as exc:
            # Partial save is best-effort; never raise from a fold-end hook.
            logger.warning("save_fold_partial(%d) failed: %s", fold_idx, exc)

        # Standard-scores export (self-guarded; never raises).
        self._save_fold_standard_scores(dirs['metrics'], fold_idx)

        return base

    def _save_fold_standard_scores(self, path: Path, fold_idx: int) -> None:
        """Write ``fold{i}_standard_scores.json`` — BOTH epoch-selection conventions
        (per-task diag-best + single-checkpoint joint-best) for one MTL fold.

        Write-only artifact (scoring-standardization fix, 2026-07): zero effect on
        metrics, checkpoints, or selector behavior; any exception is swallowed so it
        can never crash a run. Skipped silently for runs where a (cat, reg) task pair
        cannot be identified (single-task runs). Named by REAL fold id (fan-out safe).
        Contract + schema: ``tracking/scoring.py`` docstring and
        ``docs/studies/closing_data/JOINT_BEST_SCORING.md``.
        """
        try:
            from tracking.scoring import fold_standard_scores, identify_cat_reg_tasks
            history = self.history
            fold = history.folds[fold_idx]
            pair = getattr(history, 'scoring_task_names', None)  # (cat, reg), set by mtl_cv
            if pair is None:
                pair = identify_cat_reg_tasks(fold, list(history.tasks))
            if pair is None:
                return
            cat_task, reg_task = pair
            payload = fold_standard_scores(
                fold,
                cat_task=cat_task,
                reg_task=reg_task,
                selector_name=str(getattr(history, 'checkpoint_selector', None) or 'geom_simple'),
                min_best_epoch=int(getattr(history, 'min_epoch', 0) or 0),
            )
            if payload is None:
                return
            i = history.fold_label(fold_idx)
            payload['fold'] = i
            payload['cat_task'] = cat_task
            payload['reg_task'] = reg_task
            save_json(payload, path / f'fold{i}_standard_scores.json')
        except Exception as exc:
            logger.warning("standard-scores export failed for fold %d: %s", fold_idx, exc)

    def _save_fold_metrics(self, path: Path, fold_idx: int) -> None:
        """Save train/val metrics CSVs for a single fold only."""
        fold = self.history.folds[fold_idx]
        i = self.history.fold_label(fold_idx)  # 1-based; real fold id under a fan-out run
        for task in self.history.tasks:
            th = fold.tasks.get(task)
            if not th:
                continue
            if th.train.num_epochs() > 0:
                save_csv(th.train.to_dataframe(), path / f'fold{i}_{task}_train.csv')
            if th.val.num_epochs() > 0:
                save_csv(th.val.to_dataframe(), path / f'fold{i}_{task}_val.csv')

    def _save_fold_report(self, path: Path, fold_idx: int) -> None:
        """Save the ``fold{i}_info.json`` + per-task reports for one fold.

        Mirrors the per-fold body of ``_save_reports`` but operates on just
        ``history.folds[fold_idx]``. Keeping the logic in one place would be
        cleaner; for now the duplication is acceptable because ``_save_reports``
        also runs at end-of-CV and must keep working for all completed folds
        when partial persistence is disabled or skipped.
        """
        fold = self.history.folds[fold_idx]
        i = self.history.fold_label(fold_idx)

        joint_epoch = -1
        joint_score = None
        joint_time = 0.0
        joint_loss = None
        if fold.model_task is not None and fold.model_task.best.best_epoch >= 0:
            joint_epoch = fold.model_task.best.best_epoch
            joint_score = fold.model_task.best.best_value
            joint_time = fold.model_task.best.best_time
            joint_loss_vals = fold.model_task.val.get('loss')
            if joint_loss_vals and joint_epoch < len(joint_loss_vals):
                joint_loss = joint_loss_vals[joint_epoch]

        fold_info: Dict[str, Any] = {
            'fold_number': i,
            'duration': fold.timer.get_duration() if fold.timer.duration else 0,
            'primary_checkpoint': {
                'selection_metric': 'joint_score' if joint_epoch >= 0 else 'task_best_f1',
                'epoch': joint_epoch if joint_epoch >= 0 else None,
                'joint_score': joint_score,
                'loss': joint_loss,
                'time': joint_time,
                'task_metrics': {},
            },
            'diagnostic_best_epochs': {},
        }
        for task in self.history.tasks:
            th = fold.tasks.get(task)
            if not th or not th.report:
                continue
            report = {
                map_category(k, self._label_map): v
                for k, v in th.report.items()
                if isinstance(v, dict)
            }
            save_json(report, path / f'fold{i}_{task}_report.json')
            df = pd.DataFrame([{'Category': k, **v} for k, v in report.items()])

            be = th.best.best_epoch
            metrics_at_best: Dict[str, Any] = {}
            if be >= 0:
                for metric_name, values in th.val.items():
                    if be < len(values):
                        metrics_at_best[metric_name] = values[be]
            fold_info['diagnostic_best_epochs'][task] = {
                'epoch': be,
                'time': th.best.best_time,
                'metrics': metrics_at_best,
                'accuracy': metrics_at_best.get('accuracy'),
                'f1': metrics_at_best.get('f1'),
            }

            # Track best epoch PER metric, not just per F1 (the BestModelTracker's
            # monitor): the F1-best epoch ≠ top10/MRR-best epoch, so reporting
            # top10/MRR/accuracy at the F1-best epoch under-reports them. Purely
            # additive (`per_metric_best` sub-dict); legacy keys preserved.
            CANONICAL_BEST_METRICS = (
                'top10_acc_indist', 'top5_acc_indist', 'top3_acc_indist',
                'mrr_indist',
                'top10_acc', 'top5_acc', 'top3_acc', 'mrr',
                'accuracy', 'accuracy_macro', 'f1_weighted',
            )
            per_metric_best: Dict[str, Any] = {}
            for metric_name in CANONICAL_BEST_METRICS:
                values = list(th.val.get(metric_name, []))
                if not values:
                    continue
                best_ep = max(range(len(values)), key=lambda i: values[i])
                metrics_at_this_best: Dict[str, Any] = {}
                for m_name, m_values in th.val.items():
                    if best_ep < len(m_values):
                        metrics_at_this_best[m_name] = m_values[best_ep]
                per_metric_best[metric_name] = {
                    'epoch': best_ep,
                    'best_value': values[best_ep],
                    'metrics': metrics_at_this_best,
                }
            fold_info['diagnostic_best_epochs'][task]['per_metric_best'] = per_metric_best

            primary_epoch = joint_epoch if joint_epoch >= 0 else be
            if joint_epoch < 0 and fold_info['primary_checkpoint']['epoch'] is None:
                fold_info['primary_checkpoint']['epoch'] = be if be >= 0 else None
                fold_info['primary_checkpoint']['time'] = th.best.best_time
            acc_vals = list(th.val.get('accuracy', []))
            f1_vals = list(th.val.get('f1', []))
            primary_acc = (
                acc_vals[primary_epoch]
                if acc_vals and primary_epoch >= 0 and primary_epoch < len(acc_vals)
                else None
            )
            primary_f1 = (
                f1_vals[primary_epoch]
                if f1_vals and primary_epoch >= 0 and primary_epoch < len(f1_vals)
                else None
            )
            fold_info['primary_checkpoint']['task_metrics'][task] = {
                'accuracy': primary_acc,
                'f1': primary_f1,
            }

            save_csv(df, path / f'fold{i}_{task}_report.csv', float_format='%.4f')
        if joint_epoch < 0:
            fold_info['best_epochs'] = fold_info['diagnostic_best_epochs']
        save_json(fold_info, path / f'fold{i}_info.json')

    def _folder_name(self) -> str:
        p = self.history.model_parms
        parts = [self.history.model_name, f"lr{p.learning_rate:.1e}", f"bs{p.batch_size}", f"ep{p.num_epochs}",
                 self.history.start_date]
        return "_".join(str(x).lower() for x in parts)

    def _save_params(self, path: Path) -> None:
        datasets_list = []
        if self.history.datasets:
            datasets_list = [ds.to_json() for ds in self.history.datasets]

        params = {
            'model': {'name': self.history.model_name, 'type': self.history.model_type},
            'training': {
                'folds': self.history.num_folds,
                'tasks': list(self.history.tasks),
                'dates': {'start': self.history.start_date, 'end': self.history.end_date}
            },
            'datasets': datasets_list,
            "flops": self.history.flops.to_dict() if self.history.flops is not None else None,
            'hyperparameters': {k: v for k, v in vars(self.history.model_parms).items() if not k.startswith('_')}
        }

        try:
            save_json(params, path / 'model_params.json')
        except Exception as e:
            logger.error("Error saving model parameters: %s", e)
            save_text(str(params), path / 'model_params.txt')

        if self.history.model_arch:
            with open(path / 'arch.txt', 'w') as f:
                f.write(self.history.model_arch)

    def _save_metrics(self, path: Path) -> None:
        """Save train/val metrics dynamically from MetricStore."""
        for _pos, fold in enumerate(self.history.folds):
            i = self.history.fold_label(_pos)
            for task in self.history.tasks:
                th = fold.tasks.get(task)
                if not th:
                    continue

                # Train metrics
                if th.train.num_epochs() > 0:
                    df = th.train.to_dataframe()
                    save_csv(df, path / f'fold{i}_{task}_train.csv')

                # Validation metrics
                if th.val.num_epochs() > 0:
                    df = th.val.to_dataframe()
                    save_csv(df, path / f'fold{i}_{task}_val.csv')

            # Standard-scores export (idempotent rewrite; self-guarded, never raises).
            self._save_fold_standard_scores(path, _pos)

    def _save_reports(self, path: Path) -> None:
        for _pos, fold in enumerate(self.history.folds):
            i = self.history.fold_label(_pos)
            joint_epoch = -1
            joint_score = None
            joint_time = 0.0
            joint_loss = None
            if fold.model_task is not None and fold.model_task.best.best_epoch >= 0:
                joint_epoch = fold.model_task.best.best_epoch
                joint_score = fold.model_task.best.best_value
                joint_time = fold.model_task.best.best_time
                joint_loss_vals = fold.model_task.val.get('loss')
                if joint_loss_vals and joint_epoch < len(joint_loss_vals):
                    joint_loss = joint_loss_vals[joint_epoch]

            fold_info: Dict[str, Any] = {
                'fold_number': i,
                'duration': fold.timer.get_duration() if fold.timer.duration else 0,
                'primary_checkpoint': {
                    'selection_metric': 'joint_score' if joint_epoch >= 0 else 'task_best_f1',
                    'epoch': joint_epoch if joint_epoch >= 0 else None,
                    'joint_score': joint_score,
                    'loss': joint_loss,
                    'time': joint_time,
                    'task_metrics': {},
                },
                'diagnostic_best_epochs': {},
            }
            for task in self.history.tasks:
                th = fold.tasks.get(task)
                if not th or not th.report:
                    continue
                report = {
                    map_category(k, self._label_map): v
                    for k, v in th.report.items()
                    if isinstance(v, dict)
                }
                save_json(report, path / f'fold{i}_{task}_report.json')
                df = pd.DataFrame([{'Category': k, **v} for k, v in report.items()])

                be = th.best.best_epoch
                # Export every metric present in the val MetricStore at the
                # best epoch — no hardcoded (f1, accuracy) list, so new
                # metrics (f1_weighted, top3_acc, mrr, ndcg_*) flow into
                # fold_info.json automatically.
                metrics_at_best: Dict[str, Any] = {}
                if be >= 0:
                    for metric_name, values in th.val.items():
                        if be < len(values):
                            metrics_at_best[metric_name] = values[be]
                fold_info['diagnostic_best_epochs'][task] = {
                    'epoch': be,
                    'time': th.best.best_time,
                    'metrics': metrics_at_best,
                    'accuracy': metrics_at_best.get('accuracy'),
                    'f1': metrics_at_best.get('f1'),
                }

                # Track best epoch PER metric (see the same patch in
                # _save_fold_report) to avoid the F1-vs-other-metric epoch
                # mismatch. Backward-compatible additive `per_metric_best`
                # sub-dict; readers who don't know about it get legacy F1-best.
                CANONICAL_BEST_METRICS = (
                    'top10_acc_indist', 'top5_acc_indist', 'top3_acc_indist',
                    'mrr_indist',
                    'top10_acc', 'top5_acc', 'top3_acc', 'mrr',
                    'accuracy', 'accuracy_macro', 'f1_weighted',
                )
                per_metric_best: Dict[str, Any] = {}
                for metric_name in CANONICAL_BEST_METRICS:
                    values = list(th.val.get(metric_name, []))
                    if not values:
                        continue
                    best_ep = max(range(len(values)), key=lambda i: values[i])
                    metrics_at_this_best: Dict[str, Any] = {}
                    for m_name, m_values in th.val.items():
                        if best_ep < len(m_values):
                            metrics_at_this_best[m_name] = m_values[best_ep]
                    per_metric_best[metric_name] = {
                        'epoch': best_ep,
                        'best_value': values[best_ep],
                        'metrics': metrics_at_this_best,
                    }
                fold_info['diagnostic_best_epochs'][task]['per_metric_best'] = per_metric_best

                primary_epoch = joint_epoch if joint_epoch >= 0 else be
                if joint_epoch < 0 and fold_info['primary_checkpoint']['epoch'] is None:
                    fold_info['primary_checkpoint']['epoch'] = be if be >= 0 else None
                    fold_info['primary_checkpoint']['time'] = th.best.best_time
                acc_vals = list(th.val.get('accuracy', []))
                f1_vals = list(th.val.get('f1', []))
                primary_acc = (
                    acc_vals[primary_epoch]
                    if acc_vals and primary_epoch >= 0 and primary_epoch < len(acc_vals)
                    else None
                )
                primary_f1 = (
                    f1_vals[primary_epoch]
                    if f1_vals and primary_epoch >= 0 and primary_epoch < len(f1_vals)
                    else None
                )
                fold_info['primary_checkpoint']['task_metrics'][task] = {
                    'accuracy': primary_acc,
                    'f1': primary_f1,
                }

                save_csv(df, path / f'fold{i}_{task}_report.csv', float_format='%.4f')
            # Single-task runs (no model_task / no joint checkpoint) expose
            # diagnostic_best_epochs under the legacy 'best_epochs' key so
            # downstream consumers that read fold_info['best_epochs'] keep
            # working without a shim.
            if joint_epoch < 0:
                fold_info['best_epochs'] = fold_info['diagnostic_best_epochs']
            save_json(fold_info, path / f'fold{i}_info.json')

    def _save_plots(self, path: Path) -> None:
        """Auto-generate plots for every metric found in train/val MetricStores."""
        # Collect all unique metric names across all folds/tasks
        all_metrics = set()
        for fold in self.history.folds:
            for task in self.history.tasks:
                th = fold.tasks.get(task)
                if th:
                    all_metrics.update(th.train.keys())
                    all_metrics.update(th.val.keys())

        for metric in sorted(all_metrics):
            for task in self.history.tasks:
                has_data = False
                plt.figure()
                for i, fold in enumerate(self.history.folds, start=1):
                    th = fold.tasks.get(task)
                    if not th:
                        continue
                    train_data = th.train.get(metric)
                    val_data = th.val.get(metric)
                    if train_data:
                        x = range(1, len(train_data) + 1)
                        plt.plot(x, train_data, label=f'Fold{i} Train')
                        has_data = True
                    if val_data:
                        x = range(1, len(val_data) + 1)
                        plt.plot(x, val_data, linestyle='--', label=f'Fold{i} Val')
                        has_data = True
                if has_data:
                    plt.title(f'{metric.replace("_", " ").title()} over Epochs - {task}')
                    plt.legend()
                    plt.grid(True)
                    save_path = ensure_dir(path / task) / f"{metric}.png"
                    plt.savefig(save_path)
                plt.close()

            # Model-level metrics (MTL combined)
            has_model_data = False
            plt.figure()
            for i, fold in enumerate(self.history.folds, start=1):
                if fold.model_task is None:
                    continue
                train_data = fold.model_task.train.get(metric)
                val_data = fold.model_task.val.get(metric)
                if train_data:
                    x = range(1, len(train_data) + 1)
                    plt.plot(x, train_data, label=f'Fold{i} Train')
                    has_model_data = True
                if val_data:
                    x = range(1, len(val_data) + 1)
                    plt.plot(x, val_data, linestyle='--', label=f'Fold{i} Val')
                    has_model_data = True
            if has_model_data:
                plt.title(f'{metric.replace("_", " ").title()} over Epochs - model')
                plt.legend()
                plt.grid(True)
                save_path = ensure_dir(path / 'model') / f"{metric}.png"
                plt.savefig(save_path)
            plt.close()

    def _save_diagnostics(self, path: Path) -> None:
        """Save diagnostics from fold.diagnostics (MetricStore) and fold.artifacts (dict)."""
        for i, fold in enumerate(self.history.folds, start=1):

            # Epoch-series diagnostics from MetricStore
            if fold.diagnostics.num_epochs() > 0:
                df = fold.diagnostics.to_dataframe()
                save_csv(df, path / f'fold{i}_diagnostics.csv', float_format='%.6f')

                # Auto-plot each diagnostic metric
                for metric_name in fold.diagnostics.keys():
                    vals = fold.diagnostics[metric_name]
                    plt.figure(figsize=(10, 5))
                    plt.plot(range(1, len(vals) + 1), vals, linewidth=1.5)
                    plt.xlabel('Epoch')
                    plt.ylabel(metric_name.replace('_', ' ').title())
                    plt.title(f'{metric_name.replace("_", " ").title()} — Fold {i}')
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()
                    plt.savefig(path / f'fold{i}_{metric_name}.png', dpi=150)
                    plt.close()

            # Special handling for well-known artifacts
            artifacts = fold.artifacts

            # Confusion matrix
            if 'confusion_matrix' in artifacts:
                cm_data = artifacts['confusion_matrix']
                labels = cm_data['labels']
                matrix = np.array(cm_data['matrix'])
                df_cm = pd.DataFrame(matrix, index=labels, columns=labels)
                df_cm.to_csv(path / f'fold{i}_confusion_matrix.csv')
                self._plot_confusion_matrices(matrix, labels, path / f'fold{i}_confusion_matrix.png', fold_num=i)

            # Attention weights
            if 'attention_weights' in artifacts:
                save_json(artifacts['attention_weights'], path / f'fold{i}_attention_weights.json')

            # Per-class attention
            if 'attention_per_class' in artifacts:
                save_json(artifacts['attention_per_class'], path / f'fold{i}_attention_per_class.json')
                self._plot_attention_heatmaps(
                    artifacts.get('attention_weights', {}),
                    artifacts['attention_per_class'],
                    path, fold_num=i,
                )

            # Any other artifacts: save as JSON
            for key, value in artifacts.items():
                if key in ('confusion_matrix', 'attention_weights', 'attention_per_class'):
                    continue  # already handled above
                try:
                    save_json(value, path / f'fold{i}_{key}.json')
                except (TypeError, ValueError):
                    save_text(str(value), path / f'fold{i}_{key}.txt')

    @staticmethod
    def _plot_confusion_matrices(matrix: np.ndarray, labels: List[str], save_path: Path, fold_num: int) -> None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        im1 = ax1.imshow(matrix, interpolation='nearest', cmap='Blues')
        ax1.set_title(f'Confusion Matrix (Counts) — Fold {fold_num}')
        ax1.set_xticks(range(len(labels)))
        ax1.set_yticks(range(len(labels)))
        ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax1.set_yticklabels(labels, fontsize=8)
        ax1.set_xlabel('Predicted')
        ax1.set_ylabel('True')
        fig.colorbar(im1, ax=ax1, shrink=0.8)

        for r in range(len(labels)):
            for c in range(len(labels)):
                ax1.text(c, r, str(matrix[r, c]), ha='center', va='center', fontsize=7)

        row_sums = matrix.sum(axis=1, keepdims=True)
        norm_matrix = np.divide(matrix, row_sums, where=row_sums != 0, out=np.zeros_like(matrix, dtype=float))

        im2 = ax2.imshow(norm_matrix, interpolation='nearest', cmap='Blues', vmin=0, vmax=1)
        ax2.set_title(f'Confusion Matrix (Normalized) — Fold {fold_num}')
        ax2.set_xticks(range(len(labels)))
        ax2.set_yticks(range(len(labels)))
        ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax2.set_yticklabels(labels, fontsize=8)
        ax2.set_xlabel('Predicted')
        ax2.set_ylabel('True')
        fig.colorbar(im2, ax=ax2, shrink=0.8)

        for r in range(len(labels)):
            for c in range(len(labels)):
                ax2.text(c, r, f'{norm_matrix[r, c]:.2f}', ha='center', va='center', fontsize=7)

        fig.tight_layout()
        fig.savefig(save_path, dpi=150)
        plt.close(fig)

    @staticmethod
    def _plot_attention_heatmaps(
            overall_attn: Dict,
            per_class_attn: Dict[str, Dict],
            out_dir: Path,
            fold_num: int,
    ) -> None:
        if per_class_attn:
            class_names = list(per_class_attn.keys())
            means = np.array([per_class_attn[c]['mean'] for c in class_names])
            seq_len = means.shape[1]

            fig, ax = plt.subplots(figsize=(max(8, seq_len), max(4, len(class_names) * 0.6)))
            im = ax.imshow(means, aspect='auto', cmap='YlOrRd')
            ax.set_xticks(range(seq_len))
            ax.set_xticklabels([f't-{seq_len - 1 - j}' for j in range(seq_len)], fontsize=8)
            ax.set_yticks(range(len(class_names)))
            ax.set_yticklabels(class_names, fontsize=8)
            ax.set_xlabel('Sequence Position')
            ax.set_ylabel('Category')
            ax.set_title(f'Attention per Class x Position — Fold {fold_num}')
            fig.colorbar(im, ax=ax, shrink=0.8)
            fig.tight_layout()
            fig.savefig(out_dir / f'fold{fold_num}_attention_heatmap.png', dpi=150)
            plt.close(fig)

        if overall_attn and 'mean' in overall_attn:
            attn_mean = np.array(overall_attn['mean'])
            attn_std = np.array(overall_attn['std'])
            seq_len = len(attn_mean)
            positions = range(seq_len)

            fig, ax = plt.subplots(figsize=(max(8, seq_len), 5))
            ax.bar(positions, attn_mean, yerr=attn_std, capsize=3, color='steelblue', alpha=0.8)
            ax.set_xticks(positions)
            ax.set_xticklabels([f't-{seq_len - 1 - j}' for j in range(seq_len)], fontsize=8)
            ax.set_xlabel('Sequence Position')
            ax.set_ylabel('Attention Weight')
            ax.set_title(f'Mean Attention per Position — Fold {fold_num}')
            ax.grid(True, alpha=0.3, axis='y')
            fig.tight_layout()
            fig.savefig(out_dir / f'fold{fold_num}_attention_distribution.png', dpi=150)
            plt.close(fig)
