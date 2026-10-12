"""What a run leaves behind for a human, beside the `result.json` a machine reads.

The organising principle, and the only one:

> **Record what, without it, would require re-running.**

That is not abstract. This project has now produced four defects of one shape — a decorative
`repr_seed`, a source package outside version control, diagnostics computed and dropped at
serialisation, a scorer reading fields that were not there — and every one of them survived because
nothing written down could contradict it. The reference's own history is the same story: its
capacity audit reported a model that was never built, and the ONE artifact that made that findable
was an `arch.txt` nobody thought was important.

So this writes three things next to `result.json`:

    arch.txt          the module tree and the parameter count PER PATH
    report.md         model, data, recipe, per fold, final, and what was anomalous
    folds/fold{k}.csv the per-epoch series, one row per epoch

## What is deliberately NOT here

The reference's tracking layer is 3 478 lines across 11 modules, and one object in it is
simultaneously a context manager, a fold iterator, a metric accumulator, a plot generator and a file
writer. What it *produces* is valuable; how it is arranged is what made it the largest source of
training slowdown in the old code — which is why the baseline in
`studies/porting_validation/BASELINE_1FOLD.md` was banked BEFORE this module existed.

Also absent, on purpose: plots (the v18 driver disables them, so the protocol does not use them),
W&B/MLflow adapters (no v18 cell uses one), and a second formatted copy of the CSV (two files with
the same content at different precisions is a source of disagreement, not convenience).

**Nothing here runs inside the training loop.** Everything is written once, after the folds are
done, from data the runner already had. That is the property the old module lost.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def write(directory: Path, resolved, fold_results, aggregate: dict, *,
          seal_outer: bool = False) -> list[Path]:
    """Write the human-facing artifacts. Returns what it wrote."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    first = next((f for f in fold_results if getattr(f, "parameter_counts", None)), None)
    if first is not None:
        written.append(_write_architecture(directory, first))
    written += _write_fold_series(directory, fold_results)
    # Under the sealed protocol the outer-test number does not belong in a report written while a
    # wave runs: a number the operator can see is a number the operator can act on, and audit
    # criterion 7 turns any run altered after viewing outer-test into an exploratory one. Stage 2
    # computes it, deliberately and after the fact.
    written.append(_write_report(directory, resolved, fold_results,
                                 {} if seal_outer else aggregate, sealed=seal_outer))
    return written


# ---------------------------------------------------------------- architecture

def parameter_counts(model) -> dict[str, int]:
    """Parameters per PATH, not just the total.

    This is the number the reference's capacity audit got wrong: it counted a category head built
    from its module defaults (644 359) while the run used the head the task factory configured
    (1 433 863), and the audit's conclusion about a capacity-matched control went into a
    dissertation. A total alone would not have caught it — the split by path is what makes a wrong
    head visible.
    """
    counts: dict[str, int] = {}
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        head = name.split(".")[0]
        counts[head] = counts.get(head, 0) + parameter.numel()
    counts["total"] = sum(v for k, v in counts.items() if k != "total")
    return counts


def _write_architecture(directory: Path, fold) -> Path:
    path = directory / "arch.txt"
    counts = fold.parameter_counts
    lines = [
        "# The model as CONSTRUCTED, not as configured.",
        "# Reading a head's source tells you nothing: in the reference the head class comes from",
        "# --model while every hyperparameter comes from the task factory, so the module defaults",
        "# describe a model less than half the size of the one that runs.",
        "",
        fold.architecture,
        "",
        "# parameters by path",
    ]
    for name, count in sorted(counts.items(), key=lambda kv: (kv[0] == "total", -kv[1])):
        lines.append(f"{name:40} {count:>12,}")
    path.write_text("\n".join(lines) + "\n")
    return path


# ---------------------------------------------------------------- per-fold series

def _write_fold_series(directory: Path, fold_results) -> list[Path]:
    """One CSV per fold: an epoch per row, every recorded metric a column.

    On disk rather than only inside `result.json` because "plot the val curve of fold 3" should not
    require a JSON parser, and because the epoch series is what makes a selection rule re-derivable
    without re-training.
    """
    folds_dir = directory / "folds"
    folds_dir.mkdir(exist_ok=True)
    written = []

    for fold in fold_results:
        columns: dict[str, list] = {}
        if getattr(fold, "train_loss", None):
            columns["train_loss"] = list(fold.train_loss)
        for task, series in getattr(fold, "val", {}).items():
            for metric, values in series.values.items():
                columns[f"val_{task}_{metric}"] = list(values)
        if not columns:
            continue

        n = max(len(v) for v in columns.values())
        header = ["epoch", *columns]
        rows = [",".join(header)]
        for i in range(n):
            cells = [str(i + 1)]
            for name in columns:
                values = columns[name]
                cells.append(f"{values[i]:.6f}" if i < len(values) else "")
            rows.append(",".join(cells))

        path = folds_dir / f"fold{fold.fold}.csv"
        path.write_text("\n".join(rows) + "\n")
        written.append(path)
    return written


# ---------------------------------------------------------------- the report

def _write_report(directory: Path, resolved, fold_results, aggregate: dict, *,
                  sealed: bool = False) -> Path:
    cfg = resolved.train
    lines = [
        f"# {resolved.cell_id}",
        "",
        f"`{resolved.fingerprint()}` from `{resolved.recipe}`",
        "",
        "## Recipe",
        "",
        f"- family **{cfg.family.value}** · state **{cfg.state}** · "
        f"model_seed **{cfg.seed}** · split_seed **{resolved.data.split_seed}** · "
        f"engine `{cfg.engine}`",
        f"- {cfg.epochs} epochs · batch {cfg.batch_size} · {cfg.folds} folds · "
        f"precision {cfg.precision.value}",
        f"- scheduler {cfg.optim.scheduler} · max_lr {cfg.optim.max_lr}",
    ]
    if cfg.cat_head:
        lines.append(f"- cat head `{cfg.cat_head.name}` {cfg.cat_head.params or ''}")
    if cfg.reg_head:
        lines.append(f"- reg head `{cfg.reg_head.name}` {cfg.reg_head.params or ''}")

    lines += ["", "## Result", ""]
    if sealed:
        lines += ["**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads",
                  "the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.", ""]
    if aggregate:
        lines += [
            f"**{aggregate['metric']} = {aggregate['mean'] * 100:.4f} "
            f"± {aggregate['std'] * 100:.4f}** over {aggregate['n_folds']} folds "
            f"(lane `{aggregate['lane']}`)",
            "",
            "| fold | value | best epoch | wall |",
            "|---:|---:|---:|---:|",
        ]
        for fold, value in zip(fold_results, aggregate.get("per_fold", [])):
            epoch = (fold.selection or {}).get("epoch", "?")
            lines.append(f"| {fold.fold} | {value * 100:.4f} | {epoch} | {fold.wall_seconds:.0f}s |")
    else:
        # The joint family banks no single aggregate: it has two metrics and averaging them would
        # invent a number nobody selected on.
        lines += ["Joint cell — two metrics, no single aggregate.", "",
                  "| fold | cat macro-F1 | reg Acc@10 | wall |", "|---:|---:|---:|---:|"]
        for fold in fold_results:
            selection = fold.selection or {}
            cat = (selection.get("cat_diag_best") or {}).get("f1")
            reg = (selection.get("reg_diag_best") or {}).get("top10_full")
            lines.append(f"| {fold.fold} | {cat * 100:.4f} | {reg * 100:.4f} | "
                         f"{fold.wall_seconds:.0f}s |" if cat is not None and reg is not None
                         else f"| {fold.fold} | ? | ? | {fold.wall_seconds:.0f}s |")

    anomalies = _anomalies(fold_results, cfg)
    lines += ["", "## Worth a look", ""]
    lines += [f"- {a}" for a in anomalies] if anomalies else ["Nothing flagged."]

    diagnostics = [f.diagnostics for f in fold_results if getattr(f, "diagnostics", None)]
    if diagnostics:
        lines += ["", "## Diagnostics", "", "```json",
                  json.dumps(diagnostics[0], indent=1, sort_keys=True), "```"]

    path = directory / "report.md"
    path.write_text("\n".join(lines) + "\n")
    return path


def _anomalies(fold_results, cfg) -> list[str]:
    """The things a reader should be told without having to look for them.

    Every entry here exists because its absence cost something once: an epoch on the boundary means
    the schedule is mis-sized (Alabama peaked at 13 of 50 and its banked numbers were 0.35 pp worse
    than they needed to be), and ambiguous rows mean the metric is reporting a tie as a decision.
    """
    out = []
    edges = [f.fold for f in fold_results
             if (f.selection or {}).get("epoch") in (1, cfg.epochs)]
    if edges:
        out.append(f"selection landed on the FIRST or LAST epoch in fold(s) {edges} — the schedule "
                   f"is probably mis-sized ({cfg.epochs} epochs)")

    ambiguous = [(f.fold, f.ambiguous_rows) for f in fold_results
                 if any((f.ambiguous_rows or {}).values())]
    if ambiguous:
        out.append(f"ties at the decision boundary: {ambiguous}")

    # Peaked early. Alabama's category cell peaked at epoch 13 of 50 and its banked numbers were
    # 0.35 pp worse than a 20-epoch schedule's, measured over 4 seeds — the anneal was banking a
    # mid-ramp checkpoint. Nothing in the artifact said so; a reader had to notice. Now it says so.
    early = [(f.fold, (f.selection or {}).get("epoch")) for f in fold_results
             if isinstance((f.selection or {}).get("epoch"), int)
             and (f.selection or {}).get("epoch") <= cfg.epochs / 3]
    if early and len(early) == len(fold_results):
        worst = max(e for _, e in early)
        out.append(f"every fold peaked in the first third of the schedule (latest was epoch {worst} "
                   f"of {cfg.epochs}) — a shorter schedule may score HIGHER, not just faster; at "
                   f"alabama that was worth +0.35 pp")

    walls = [f.wall_seconds for f in fold_results]
    if len(walls) > 1 and max(walls) > 2 * min(walls):
        out.append(f"fold wall-clock spread {min(walls):.0f}s to {max(walls):.0f}s — one fold took "
                   f"more than twice another, which is usually contention, not data")
    return out


__all__ = ["write", "parameter_counts"]
