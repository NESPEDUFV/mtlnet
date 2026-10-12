"""Re-derive a wave's numbers from what it banked, without touching a GPU.

Two jobs, both consequences of defects in the reference.

**Re-scoring.** The reference's scorer was invoked in a way that swallowed failures, so the
joint-best lane sat entirely empty and nobody noticed (R10). Scoring is therefore a separate,
cheap, re-runnable step here: if a selection rule changes, the answer comes from the banked
per-epoch series rather than from another week of GPU time.

**Comparing.** The acceptance question — "is this arm the same as that one?" — was being judged
against the between-fold spread, which is the wrong yardstick: folds differ for reasons that hit
both arms identically, and pairing cancels exactly that. This module reports the paired delta with
a band computed over SEEDS, because folds within a seed share ~80% of their training data and are
not replicates.

Nothing here trains. If a number can be obtained from `result.json`, it is obtained from
`result.json`.
"""

from __future__ import annotations

import json
import logging
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import stats

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Banked:
    """One cell's banked result, reduced to what scoring needs."""

    path: Path
    family: str
    state: str
    seed: int
    fingerprint: str
    per_fold: list[float]
    fold_ids: list[int]
    metric: str
    lane: str
    wall_seconds: float
    diagnostics: list[dict[str, Any]]
    epochs: int = 0                   # schedule length: two arms can differ ONLY by this
    #: `"inner_val"` (sealed), `"outer_fold"` (legacy), or `"unknown"` for a cell banked before the
    #: field existed. Not cosmetic: a legacy number was read off the same fold that chose its epoch,
    #: e o otimismo disso é **sugerido em ~0,66 pp por UM fold de Alabama**, não medido
    #: (`waves/sealed_bridge.toml:9`) — já acima da margem de equivalência de 0,4 pp, então parear os
    #: dois streams reporta esse viés como efeito. A medição própria é o §8a
    #: (`eval/optimism.py`), que existe, tem testes e **nunca rodou** porque exige
    #: `retain_checkpoints != "none"`. `"unknown"` is its own value rather than a
    #: default of `"outer_fold"`, because a SEALED cell banked in that window would then be labelled
    #: legacy and allowed to pair with real legacy cells — the exact mistake, wearing the guard.
    eval_stream: str = "unknown"
    #: The partition this cell trained on. None for cells banked before the two seeds were split —
    #: which is itself the confounded case, and is what `band_over` reports.
    split_seed: int | None = None

    @property
    def mean(self) -> float:
        return statistics.fmean(self.per_fold) if self.per_fold else float("nan")


def collect(run_root: str | Path) -> list[Banked]:
    """Every parseable `result.json` under a run root, in a stable order."""
    run_root = Path(run_root)
    banked: list[Banked] = []
    for path in sorted(run_root.rglob("result.json")):
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            logger.warning("unreadable, skipped: %s", path)
            continue
        aggregate = payload.get("aggregate", {})
        folds = payload.get("folds", []) or []
        family = str(payload.get("family", "?"))
        epochs = int(payload.get("config", {}).get("train", {}).get("epochs", 0))

        # A joint cell banks NO single aggregate, because it has two metrics. Split it into two
        # pseudo-arms read from each fold's selection, so `joint:cat` can be paired against `cat` —
        # which is the comparison the whole study is about. Without this a joint cell scored as a
        # NaN and took the summary down with it.
        if family == "joint" and not aggregate.get("per_fold"):
            banked += _split_joint(path, payload, folds)
            continue
        # The schema keeps identity and wall-clock in specific places, and reading them from the
        # wrong one produced a performance report of all zeros that looked like a finished report.
        # So the reads are pinned to the real schema and a missing wall is a loud zero, not a
        # silent one.
        banked.append(Banked(
            path=path,
            family=family,
            state=str(payload.get("state", "?")),
            seed=int(payload.get("seed", -1)),
            fingerprint=str(payload.get("config_fingerprint", "")),
            per_fold=[v * 100 for v in aggregate.get("per_fold", [])],
            # Fall back to the folds block for cells banked before the aggregate carried ids; only
            # position is lost, and only for those.
            fold_ids=list(aggregate.get("fold_ids")
                          or [int(f.get("fold", i)) for i, f in enumerate(folds)]),
            metric=str(aggregate.get("metric", "?")),
            lane=str(aggregate.get("lane", "?")),
            eval_stream=str(aggregate.get("eval_stream", "unknown")),
            split_seed=payload.get("config", {}).get("data", {}).get("split_seed"),
            wall_seconds=sum(float(f.get("wall_seconds", 0.0)) for f in folds),
            diagnostics=[f["diagnostics"] for f in folds if isinstance(f.get("diagnostics"), dict)],
            epochs=epochs,
        ))
    if banked and not any(c.wall_seconds for c in banked):
        logger.warning("no wall-clock in any result: the performance report will be empty. Either "
                       "the schema moved or these cells recorded none.")
    return banked


def _split_joint(path: Path, payload: dict, folds: list[dict]) -> list[Banked]:
    """One joint cell -> two arms: `joint:cat` (macro-F1) and `joint:reg` (Acc@10).

    The lane is the per-task DIAGNOSTIC best, which is what the v18 evidence tables report and what
    makes `cat` and `joint:cat` comparable — both are "the best this task reached".
    """
    wall = sum(float(f.get("wall_seconds", 0.0)) for f in folds)
    diagnostics = [f["diagnostics"] for f in folds if isinstance(f.get("diagnostics"), dict)]
    common = dict(path=path, state=str(payload.get("state", "?")),
                  seed=int(payload.get("seed", -1)),
                  fingerprint=str(payload.get("config_fingerprint", "")),
                  lane="diag_best", wall_seconds=wall, diagnostics=diagnostics,
                  eval_stream=str(_joint_eval_stream(folds)),
                  split_seed=payload.get("config", {}).get("data", {}).get("split_seed"),
                  epochs=int(payload.get("config", {}).get("train", {}).get("epochs", 0)))

    def series(task: str, key: str) -> tuple[list[float], list[int]]:
        """Values and their REAL fold ids. A fold missing the key is skipped, which compresses the
        list — so the ids travel with it rather than being re-derived from position."""
        values, ids = [], []
        for index, fold in enumerate(folds):
            best = (fold.get("selection") or {}).get(f"{task}_diag_best") or {}
            if key in best:
                values.append(best[key] * 100)
                ids.append(int(fold.get("fold", index)))
        return values, ids

    arms = []
    cat, cat_ids = series("cat", "f1")
    if cat:
        arms.append(Banked(family="joint:cat", per_fold=cat, fold_ids=cat_ids, metric="f1",
                           **common))
    reg, reg_ids = series("reg", "top10_full")
    if reg:
        arms.append(Banked(family="joint:reg", per_fold=reg, fold_ids=reg_ids,
                           metric="top10_full", **common))
    return arms


def _joint_eval_stream(folds: list[dict]) -> str:
    """A joint cell banks no aggregate, so the stream is read off its folds."""
    streams = {str(f.get("eval_stream", "unknown")) for f in folds} or {"unknown"}
    if len(streams) > 1:
        raise ValueError(f"one joint cell's folds report different streams {sorted(streams)}")
    return streams.pop()


def summarise(banked: list[Banked]) -> dict[str, Any]:
    """Per (family, state): the mean over seeds, the spread, and what is missing.

    Reports the spread over SEED MEANS, not over pooled folds. Pooling folds into one standard
    deviation answers "how much do folds differ", which nobody is asking and which is several times
    larger than the quantity that matters.
    """
    # A schedule gate banks two arms that differ ONLY in epochs, so the arm name has to carry it —
    # otherwise the 20-epoch and 50-epoch cells average together into one meaningless row.
    by_pair: dict[tuple[str, str], set[int]] = {}
    for cell in banked:
        by_pair.setdefault((cell.family, cell.state), set()).add(cell.epochs)

    groups: dict[tuple[str, str], list[Banked]] = {}
    for cell in banked:
        family = cell.family
        if len(by_pair[(cell.family, cell.state)]) > 1:
            family = f"{cell.family}@{cell.epochs}ep"
        groups.setdefault((family, cell.state), []).append(cell)

    out: dict[str, Any] = {}
    for (family, state), cells in sorted(groups.items()):
        seed_means = sorted((c.seed, c.mean) for c in cells)
        values = [m for _, m in seed_means if m == m]      # drop NaN rather than crash on it
        if not values:
            out[f"{family}/{state}"] = {"metric": cells[0].metric, "lane": cells[0].lane,
                                        "seeds": [s for s, _ in seed_means], "seed_means": [],
                                        "mean": float("nan"), "std_over_seeds": float("nan"),
                                        "n_seeds": 0, "n_folds_total": 0,
                                        "wall_seconds": sum(c.wall_seconds for c in cells)}
            continue
        out[f"{family}/{state}"] = {
            "metric": cells[0].metric,
            "lane": cells[0].lane,
            "seeds": [s for s, _ in seed_means],
            "seed_means": values,
            "mean": statistics.fmean(values),
            "std_over_seeds": statistics.stdev(values) if len(values) > 1 else 0.0,
            "n_seeds": len(values),
            "n_folds_total": sum(len(c.per_fold) for c in cells),
            "wall_seconds": sum(c.wall_seconds for c in cells),
        }
    return out


def compare(banked: list[Banked], arm_a: str, arm_b: str, *, state: str | None = None):
    """Paired comparison between two families, over the cells they share.

    The pairing unit is (seed, fold): the SAME fold of the SAME seed in both arms, which is
    legitimate here because all three families train on one split.
    """
    def cells_for(family: str) -> tuple[list[stats.Cell], set[str]]:
        """`family` may be a plain name or `name@<n>ep` to pick one arm of a schedule gate."""
        name, _, epochs = family.partition("@")
        wanted = int(epochs.rstrip("ep")) if epochs else None
        out, streams = [], set()
        for entry in banked:
            if entry.family != name or (state and entry.state != state):
                continue
            if wanted is not None and entry.epochs != wanted:
                continue
            streams.add(entry.eval_stream)
            # REAL fold ids, not enumerate(). A cell run with --only-folds banks a short list, and
            # positional pairing then compares its fold 3 against the other arm's fold 0 with no
            # warning — the dropped-cells guard cannot see a mis-pairing, only an absence.
            out += [stats.Cell(seed=entry.seed, fold=f, value=v, state=entry.state)
                    for f, v in zip(entry.fold_ids, entry.per_fold)]
        return out, streams

    def metrics_for(family: str) -> set[str]:
        name, _, epochs = family.partition("@")
        return {e.metric for e in banked
                if e.family == name and (not state or e.state == state)}

    cells_a, streams_a = cells_for(arm_a)
    cells_b, streams_b = cells_for(arm_b)
    metrics = metrics_for(arm_a) | metrics_for(arm_b)
    if len(metrics) > 1:
        # The region axis has TWO estimators and they are both called Acc@10: `top10_acc` counts
        # every held-out row against the full vocabulary, `top10_full` discounts the in-distribution
        # rate by the OOD share. A dedicated cell banks the first and a joint cell's diag-best banks
        # the second, so `reg` vs `joint:reg` — the comparison this whole study is about — would pair
        # two different definitions and read the difference as a model effect.
        raise ValueError(
            f"{arm_a} reports {sorted(metrics_for(arm_a))} and {arm_b} reports "
            f"{sorted(metrics_for(arm_b))}. These are different estimators; re-score one arm in the "
            f"other's convention before pairing them.")
    streams = streams_a | streams_b
    if "unknown" in streams:
        raise ValueError(
            f"{sorted(streams)}: at least one cell predates the eval_stream record, so whether it "
            f"was selected on the fold it reports is not knowable from the artifact. Re-run it, or "
            f"read it by hand — do not let a guess decide which estimand it is.")
    if len(streams) > 1:
        # The one comparison this function must refuse. Under sealing the reported number comes from
        # the inner split; under the legacy rule it comes from the fold that also chose the epoch.
        # Their difference is dominated by selection optimism, so a delta across them measures the
        # protocol change and reads as a model effect.
        raise ValueError(
            f"{arm_a} was scored on {sorted(streams_a)} and {arm_b} on {sorted(streams_b)}. These "
            f"are different estimands — the legacy stream carries selection optimism suggested at "
            f"~0.66 pp by ONE Alabama fold — "
            f"so their paired delta would report a protocol change as a model effect. Re-run one "
            f"arm under the other's protocol.")
    # Which factor the replicates index. `score` reads banked cells whose partition is pinned by
    # the manifest, so under a frozen split they are model-seed replicates; when the partition moved
    # with the seed (the legacy shape) the band confounds both and must say so.
    factor = ("model_seed" if len({c.split_seed for c in banked if c.split_seed is not None}) <= 1
              else "confounded_legacy")
    return stats.compare(cells_a, cells_b, label=f"{arm_b} - {arm_a}", band_over=factor)


def performance(banked: list[Banked]) -> dict[str, Any]:
    """What the wave cost, and where the time went.

    Kept beside the metrics on purpose. "Which change is worth making?" is answered by the same
    artifact that answers "did the change help?", and the reference had to re-run cells to recover
    exactly this — the phase timings existed but were thrown away with the process.
    """
    rows = []
    for cell in banked:
        train_total = sum(d.get("train_seconds_total", 0.0) for d in cell.diagnostics)
        val_total = sum(d.get("val_seconds_total", 0.0) for d in cell.diagnostics)
        accounted = train_total + val_total
        peak = max((d.get("peak_memory_gb", 0.0) for d in cell.diagnostics), default=0.0)
        best_epochs = [d.get("best_epoch") for d in cell.diagnostics if d.get("best_epoch")]
        rows.append({
            "cell": f"{cell.family}/{cell.state}/seed{cell.seed}",
            "wall_seconds": cell.wall_seconds,
            "train_seconds": train_total,
            "val_seconds": val_total,
            # A gap means time is going where the phase timers cannot see it — data movement,
            # compilation, checkpoint writes — and is worth knowing before optimising a phase. It is
            # None when the cell simply ran without --diagnostics, which is not the same thing as
            # 100% unaccounted and should not read like it.
            "unaccounted_share": ((1 - accounted / cell.wall_seconds)
                                  if cell.wall_seconds and cell.diagnostics else None),
            "has_diagnostics": bool(cell.diagnostics),
            "peak_memory_gb": peak,
            "mean_best_epoch": statistics.fmean(best_epochs) if best_epochs else None,
        })
    total = sum(r["wall_seconds"] for r in rows)
    return {"cells": rows, "total_wall_seconds": total,
            "total_train_seconds": sum(r["train_seconds"] for r in rows),
            "total_val_seconds": sum(r["val_seconds"] for r in rows)}


__all__ = ["Banked", "collect", "summarise", "compare", "performance"]
