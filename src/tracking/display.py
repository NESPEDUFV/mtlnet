import logging
from statistics import mean, stdev
from typing import Dict, Optional, Sequence, TYPE_CHECKING


def _safe_stdev(xs: Sequence[float]) -> float:
    """stdev() that returns 0.0 for a single data point instead of raising.

    Needed because `--folds 1` runs produce single-element metric lists, and
    `statistics.stdev` hard-errors with `StatisticsError: stdev requires at
    least two data points`. A single observation has no sample dispersion, so
    0.0 is the meaningful value to display.
    """
    return stdev(xs) if len(xs) > 1 else 0.0


if TYPE_CHECKING:
    from tracking.experiment import MLHistory
    from tracking.records import RecordComparison

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)-5s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


class ClassColorFormatter(logging.Formatter):
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def format(self, record):
        msg = super().format(record)
        if record.name == HistoryDisplay.LOGGER_NAME:
            return f"{self.CYAN}{self.BOLD}{msg}{self.RESET}"
        return msg


class HistoryDisplay:
    LOGGER_NAME = "ml.history.display"

    # Headline metric names shown in the end-of-fold summary table, in
    # display order. Override via constructor to surface extra metrics
    # (e.g. ``top3_acc``, ``f1_weighted``) in the terminal output.
    DEFAULT_HEADLINE_METRICS = ("f1", "accuracy", "top3_acc")

    def __init__(
        self,
        history: "MLHistory",
        label_map: Optional[Dict[int, str]] = None,
        show_report: bool = False,
        headline_metrics: Optional[Sequence[str]] = None,
    ):
        self.h = history
        self.label_map = label_map or {}
        self.show_report = show_report
        self.headline_metrics = tuple(headline_metrics) if headline_metrics else self.DEFAULT_HEADLINE_METRICS
        self.log = logging.getLogger(self.LOGGER_NAME)

        if not any(isinstance(h, logging.StreamHandler) for h in self.log.handlers):
            handler = logging.StreamHandler()
            handler.setFormatter(
                ClassColorFormatter(
                    "%(asctime)s - %(levelname)-5s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            self.log.addHandler(handler)
            self.log.propagate = False

    def set_label_map(self, label_map: Dict[int, str]):
        """Set or update the label map for category display."""
        self.label_map = label_map

    def _sep(self, title: str, width: int = 60, sep: str = "=") -> str:
        pad = max(0, (width - len(title) - 2) // 2)
        return f"{sep * pad} {title} {sep * pad}"

    def _time_stats(self, fold_idx: int):
        elapsed_total = self.h.timer.timer()
        last_fold = self.h.folds[fold_idx].timer.get_duration()
        past = [f.timer.get_duration() for f in self.h.folds[:fold_idx + 1]]
        remaining = (mean(past) if past else 0) * (self.h.num_folds - fold_idx - 1)
        return elapsed_total, last_fold, remaining

    def _format_time(self, seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.2f}s"
        minutes = seconds / 60
        return f"{minutes:.2f}m"

    @staticmethod
    def _format_si(value: float) -> str:
        """Format a number with K/M/G SI suffix."""
        if value >= 1e9:
            return f"{value / 1e9:.2f}G"
        if value >= 1e6:
            return f"{value / 1e6:.2f}M"
        if value >= 1e3:
            return f"{value / 1e3:.2f}K"
        return f"{value:.0f}"

    def _format_metric(self, value, is_percentage: bool = True, width: int = 8) -> str:
        if isinstance(value, (int, float)):
            if is_percentage:
                return f"{value * 100:>{width}.2f}%"
            return f"{value:>{width}}"
        return f"{value:>{width}}"

    def _map_category(self, key) -> str:
        """Map a category key to its display name."""
        if not self.label_map:
            return str(key)
        try:
            idx = int(float(key))
            return self.label_map.get(idx, f"Class {key}")
        except (ValueError, TypeError):
            return str(key)

    def start_fold(self):
        text = f"FOLD {self.h.curr_i_fold + 1}/{self.h.num_folds}"
        self.log.info(self._sep(text))

    def end_fold(self, fold_idx: Optional[int] = None):
        idx = fold_idx if fold_idx is not None else self.h.curr_i_fold
        elapsed, elapsed_fold, remaining = self._time_stats(idx)
        self.log.info(
            f"Fold {idx + 1}/{self.h.num_folds} completed in {elapsed_fold:.2f}s | "
            f"Total: {self._format_time(elapsed)} | Remaining: {self._format_time(remaining)}"
        )
        self.log.info(self._sep(f"Summary Fold {idx + 1}", width=60, sep='-'))
        # Column widths are unified at 10 chars so header and row cells
        # line up regardless of how many headline metrics are configured.
        col = 10
        header_cells = [f"{'Task':<{col}}", f"{'Best Epoch':<{col}}"]
        for metric in self.headline_metrics:
            header_cells.append(f"{metric.replace('_', ' ').title():<{col}}")
        self.log.info(" | ".join(header_cells) + " |")
        for t in self.h.tasks:
            th = self.h.folds[idx].task(t)
            be = th.best.best_epoch
            row = [f"{t:<{col}}", f"{be:^{col}d}"]
            for metric in self.headline_metrics:
                vals = th.val.get(metric)
                v = vals[be] if vals and be >= 0 and be < len(vals) else 0.0
                # Reserve one char for '%', leave col-1 for the number.
                row.append(f"{v * 100:>{col - 1}.2f}%")
            self.log.info(" | ".join(row) + " |")

        if self.show_report:
            for t in self.h.tasks:
                report = self.h.folds[idx].task(t).report
                if report:
                    self.log.info(self._sep(f"Report for {t}", width=60, sep='-'))
                    self.display_report(report)

        self.log.info(self._sep("End of Fold", width=60))

    def display_report(self, report: dict):
        self.log.info(
            f"{'Category':<12} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<10}"
        )

        for class_idx, metrics in report.items():
            if class_idx in ('macro avg', 'accuracy', 'weighted avg'):
                continue
            category = self._map_category(class_idx)
            prec_str = self._format_metric(metrics.get('precision', ''), is_percentage=True)
            rec_str = self._format_metric(metrics.get('recall', ''), is_percentage=True)
            f1_str = self._format_metric(metrics.get('f1-score', ''), is_percentage=True)
            support = metrics.get('support', '')
            support_str = f"{support:>10}"
            self.log.info(f"{category:<12} | {prec_str} | {rec_str} | {f1_str} | {support_str}")

        if 'macro avg' in report:
            macro = report['macro avg']
            p_str = self._format_metric(macro.get('precision', ''), is_percentage=True)
            r_str = self._format_metric(macro.get('recall', ''), is_percentage=True)
            f_str = self._format_metric(macro.get('f1-score', ''), is_percentage=True)
            self.log.info(
                f"{'macro avg':<12} | {p_str} | {r_str} | {f_str} | {'':>10}"
            )

    def _collect_best_epoch_metrics(self) -> Dict[str, Dict[str, list]]:
        """Collect headline metric values at each fold's best epoch, per task.

        Returns ``{task: {metric_name: [val_fold0, val_fold1, ...]}}``.
        """
        result: Dict[str, Dict[str, list]] = {}
        for fold in self.h.folds:
            for task in self.h.tasks:
                th = fold.tasks.get(task)
                if not th:
                    continue
                be = th.best.best_epoch
                if be < 0:
                    continue
                task_dict = result.setdefault(task, {})
                for metric in self.headline_metrics:
                    vals = th.val.get(metric)
                    if vals and be < len(vals):
                        task_dict.setdefault(metric, []).append(vals[be])
        return result

    def _display_final_results(self) -> None:
        """Print a compact "Final Results" table across all folds.

        Always shown — this is the first thing a researcher looks at after a
        run finishes. For N > 1 folds, values are ``mean +- stdev``.
        """
        perf = self._collect_best_epoch_metrics()
        if not perf:
            return

        n_folds = self.h.num_folds
        title = f"Final Results ({n_folds} fold{'s' if n_folds > 1 else ''})"
        self.log.info(self._sep(title, width=60, sep='-'))

        # Decide column width: "mean +- std" needs more room than a bare value.
        col_val = 18 if n_folds > 1 else 10
        col_task = 10
        header = [f"{'Task':<{col_task}}"]
        for m in self.headline_metrics:
            header.append(f"{m.replace('_', ' ').title():<{col_val}}")
        self.log.info(" | ".join(header) + " |")

        for task in self.h.tasks:
            task_metrics = perf.get(task, {})
            row = [f"{task:<{col_task}}"]
            for m in self.headline_metrics:
                values = task_metrics.get(m, [])
                if not values:
                    row.append(f"{'N/A':>{col_val}}")
                elif n_folds > 1:
                    avg = mean(values) * 100
                    std = _safe_stdev(values) * 100
                    cell = f"{avg:.2f} ± {std:.2f}%"
                    row.append(f"{cell:>{col_val}}")
                else:
                    row.append(f"{values[0] * 100:>{col_val - 1}.2f}%")
            self.log.info(" | ".join(row) + " |")

    def end_training(self):
        self.log.info(self._sep("Training Complete"))
        self.log.info(self._sep("Summary", width=60, sep='-'))
        self.log.info(
            f"Model: {self.h.model_name} | "
            f"Folds: {self.h.num_folds} | "
            f"End at: {self.h.end_date}"
        )
        if self.h.model_parms:
            self.log.info(
                f"Tr. Time: {self._format_time(self.h.timer.get_duration())} | "
                f"Lrn. Rate: {self.h.model_parms.learning_rate} | "
                f"N. Epochs: {self.h.model_parms.num_epochs} | "
                f"Batch Size: {self.h.model_parms.batch_size}"
            )

        # Always show the compact aggregate results table — this is the
        # first thing a researcher cares about after a training run.
        self._display_final_results()

        # Execution stats below the metric table — total wall time + model
        # complexity so runs are easy to compare at a glance.
        duration = self.h.timer.get_duration() if hasattr(self.h.timer, 'get_duration') else 0
        stats_parts = [f"Total Time: {self._format_time(duration)}"]
        if self.h.flops:
            flops_val = self.h.flops.flops
            params_val = self.h.flops.params
            if isinstance(flops_val, (int, float)) and flops_val > 0:
                stats_parts.append(f"FLOPs: {self._format_si(flops_val)}")
            if isinstance(params_val, (int, float)) and params_val > 0:
                stats_parts.append(f"Params: {self._format_si(params_val)}")
        self.log.info(" | ".join(stats_parts))

        if self.show_report:
            for task in self.h.tasks:
                self.log.info(self._sep(f"Avg. Task: {task}", width=60, sep='-'))

                aggregated = {}
                for fold in self.h.folds:
                    report = fold.task(task).report
                    for cls, metrics in report.items():
                        if cls not in aggregated:
                            aggregated[cls] = {'precision': [], 'recall': [], 'f1-score': [], 'support': []}
                        if cls not in ('accuracy', 'weighted avg'):
                            aggregated[cls]['precision'].append(metrics['precision'])
                            aggregated[cls]['recall'].append(metrics['recall'])
                            aggregated[cls]['f1-score'].append(metrics['f1-score'])
                            if 'support' in metrics:
                                aggregated[cls]['support'].append(metrics['support'])

                final_report = {}
                for cls, arrs in aggregated.items():
                    if cls in ('accuracy', 'weighted avg'):
                        continue
                    final_report[cls] = {
                        'precision': f"{(mean(arrs['precision'])*100):.2f} ± {(_safe_stdev(arrs['precision'])*100):.2f}",
                        'recall': f"{(mean(arrs['recall'])*100):.2f} ± {(_safe_stdev(arrs['recall'])*100):.2f}",
                        'f1-score': f"{(mean(arrs['f1-score'])*100):.2f} ± {(_safe_stdev(arrs['f1-score'])*100):.2f}",
                        'support': sum(arrs['support']),
                    }

                self.display_report(final_report)

        self.log.info(self._sep("End of all folds", width=60))

    def display_records(self, comparison: "RecordComparison") -> None:
        """Show per-task record comparison after training ends."""
        if not comparison.tasks:
            return

        self.log.info(self._sep("Record Comparison", width=60, sep="-"))

        for tr in comparison.tasks:
            f1_pct = tr.current_f1 * 100
            if tr.previous_best_run == "":
                # First run ever for this task in this engine+state.
                self.log.info(
                    f"  {tr.task:<12} F1: {f1_pct:6.2f}%  |  "
                    f"First run - baseline established"
                )
            elif tr.is_new_record:
                prev_pct = tr.previous_best_f1 * 100
                self.log.info(
                    f"  {tr.task:<12} F1: {f1_pct:6.2f}%  |  "
                    f"NEW RECORD  (prev: {prev_pct:.2f}%)"
                )
            else:
                prev_pct = tr.previous_best_f1 * 100
                run_short = tr.previous_best_run[:35]
                if len(tr.previous_best_run) > 35:
                    run_short += "..."
                self.log.info(
                    f"  {tr.task:<12} F1: {f1_pct:6.2f}%  |  "
                    f"Previous best: {prev_pct:.2f}% ({run_short})"
                )

        self.log.info("-" * 60)

    def flops(self):
        if self.h.flops:
            self.log.info(f"FLOPS: {self.h.flops.flops} | Params: {self.h.flops.params}")
        else:
            self.log.warning("FLOPS not calculated.")
