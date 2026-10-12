"""Paired statistics — the layer that turns two columns of numbers into a verdict.

This exists as its own module because a naive reimplementation moves verdicts without changing a
single line of training code, and the reference has already been bitten by it: a Delta was once
printed beside an `n` and a p-value computed over a different set of cells.

Three rules, all of them corrections the reference had to make:

1. **Pair on the common cells.** A Delta between two arms is computed over the (seed, fold) pairs that
   BOTH arms have — not between two means taken over whatever each arm happens to have run. If the
   arms differ in coverage, the difference is reported over the intersection and the dropped cells
   are named.
2. **Report `n` per column.** The published table once carried an `n` read from the category field
   while the region column had run fewer seeds. Every figure here carries its own count.
3. **Say what the unit is.** The reference pools (seed, fold) pairs as if independent, but the five
   folds of one partition share ~80% of their training data. The honest independent unit is the
REPLICATE — or the REPETITION, when the partition moves too (NOMENCLATURE §2).
   Both are computed; the pooled p-value is labelled anti-conservative wherever it appears, because
   the source study labels it so and a rewrite must not launder that away.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field


#: Que fator o `band_over` faz variar, no vocabulário do NOMENCLATURE §2 — a unidade inferencial
#: sai daqui em vez de ser a palavra deprecada "seed".
_UNIDADE = {"model_seed": "replicate", "split_seed": "repetition",
            "confounded_legacy": "repetition+replicate (confounded)"}


@dataclass(frozen=True)
class Cell:
    """One measurement: an arm's value for one (state, model_seed, fold).

    `state` is part of the key, not metadata. Without it two states' cells share `(seed, fold)`
    coordinates, the arm dictionaries collapse, and whichever result sorted last wins — silently, no
    warning, with a plausible delta and a plausible `n`. Measured on a two-state study the reported
    delta was one state's, the other having vanished entirely.
    """

    seed: int
    fold: int
    value: float
    state: str = ""

    @property
    def key(self) -> tuple[str, int, int]:
        return (self.state, self.seed, self.fold)


@dataclass
class PairedComparison:
    """A Delta between two arms over their common cells."""

    label: str
    n_pairs: int
    n_seeds: int
    mean_a: float
    mean_b: float
    delta: float
    delta_std: float
    #: Which factor the band's replicates index: `model_seed`, `split_seed`, or `confounded_legacy`
    #: (protocol §10.5). Required, because the three cover different things and a band that does not
    #: say which is not interpretable — the confound this project paid for was one word doing two
    #: jobs. `describe()` refuses to print a band without it.
    band_over: str = "unspecified"
    seed_deltas: list[float] = field(default_factory=list)
    dropped: list[tuple[int, int]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def stderr(self) -> float:
        """Standard error of the Delta, over SEEDS — the independent replicate.

        Not over (seed, fold) pairs. Folds within a seed share ~80% of their training data, so
        treating them as replicates shrinks the interval by a factor the data does not earn.
        """
        n = len(self.seed_deltas)
        if n < 2:
            return float("nan")
        return statistics.stdev(self.seed_deltas) / math.sqrt(n)

    @property
    def band(self) -> float:
        """The half-width a difference must exceed to be worth a claim. NaN with a single observation
    of whatever factor `band_over` names.

        Student's t, not 2.0. With S replicates there are S-1 degrees of freedom, and the normal
        approximation is badly optimistic at the R this project runs: t(0.975) is 3.18 at R=4 and
        12.71 at R=2, against the 2.0 I used. That made every band ~37% too narrow at R=4 and
        flipped one banked verdict — the Arizona joint region delta at 30 epochs read "separated"
        at +0.148 +/- 0.141 and is not, at +/- 0.224.

        The multiplier is the whole reason a small-R design must not borrow large-sample intuition.
        """
        if self.stderr != self.stderr:
            return float("nan")
        return _t_critical(len(self.seed_deltas)) * self.stderr

    def separated(self) -> bool:
        """Is the Delta outside its own uncertainty band?"""
        return bool(abs(self.delta) > self.band) if self.band == self.band else False

    def describe(self) -> str:
        unit = (f"{self.n_pairs} pares (réplica,fold) sobre S={self.n_seeds} réplicas · "
                f"n inferencial = {self.n_seeds}")
        note = " · pooled across folds, so the pairs are NOT independent" if self.n_pairs > self.n_seeds else ""
        tail = ""
        if self.band == self.band:
            if self.band_over == "unspecified":
                # Protocol §10.5. A band over model seeds covers optimisation noise; over split
                # seeds it covers partition noise; the legacy band confounds both. Printing one
                # without saying which invites the reader to assume the widest — or the narrowest.
                raise ValueError(
                    f"{self.label}: refusing to print a band without band_over. Say which factor "
                    f"its replicates index: one of {BAND_FACTORS}.")
            tail = (f" · ±{self.band:.4f} band over {len(self.seed_deltas)} {self.band_over} "
                    f"replicates (t) → "
                    f"{'separated' if self.separated() else 'NOT separated'} from zero")
        return (f"{self.label}: {self.mean_b:.4f} - {self.mean_a:.4f} = {self.delta:+.4f} "
                f"± {self.delta_std:.4f} [{unit}{note}]{tail}")


# Two-sided 95% Student-t critical values by number of replicates (S). Tabulated rather than pulled
# from scipy so the statistics layer keeps no heavy dependency, and so the values are auditable here.
_T_95 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306,
         10: 2.262, 11: 2.228, 12: 2.201, 13: 2.179, 14: 2.160, 15: 2.145, 16: 2.131, 17: 2.120,
         18: 2.110, 19: 2.101, 20: 2.093, 21: 2.086, 22: 2.080, 23: 2.074, 24: 2.069, 25: 2.064,
         26: 2.060, 27: 2.056, 28: 2.052, 29: 2.048, 30: 2.045, 40: 2.023, 60: 2.001, 120: 1.980}


def _t_critical(n: int) -> float:
    """Two-sided 95% t on n-1 df, tabulated. Interpolation is DOWNWARD only.

    The old fallback `1.96 + 2.4/n` is anti-conservative in the range it covered: at n=11 it gives
    2.178 against the true 2.228, so a band is reported narrower than it is at exactly the sizes a
    real sweep produces. Now every n up to 30 is exact, and above that the next SMALLER tabulated
    entry is used — which errs wide.
    """
    if n < 2:
        return float("nan")
    if n in _T_95:
        return _T_95[n]
    below = [k for k in _T_95 if k < n]
    return _T_95[max(below)] if below else float("nan")


def _index(cells: list[Cell], who: str) -> dict:
    """Cells by key, refusing a collision rather than keeping the last one.

    A duplicate key means two measurements claim to be the same cell — different states sharing a
    coordinate, or one cell banked twice. Overwriting is the wrong answer to both: the survivor is
    whichever the filesystem happened to sort last.
    """
    out: dict = {}
    for cell in cells:
        if cell.key in out and out[cell.key] != cell.value:
            raise ValueError(
                f"{who}: two different values for cell {cell.key} ({out[cell.key]} and "
                f"{cell.value}). Keys must be unique — if these are different states, pass `state`; "
                f"if the cell was banked twice, say which run to read.")
        out[cell.key] = cell.value
    return out


BAND_FACTORS = ("model_seed", "split_seed", "confounded_legacy")


def compare(arm_a: list[Cell], arm_b: list[Cell], *, label: str = "delta",
            band_over: str = "unspecified") -> PairedComparison:
    """Paired difference between two arms, over the cells they share."""
    by_key_a = _index(arm_a, f"{label} (arm A)")
    by_key_b = _index(arm_b, f"{label} (arm B)")
    common = sorted(set(by_key_a) & set(by_key_b))

    if not common:
        raise ValueError(f"{label}: the two arms share no (seed, fold) cell")

    dropped = sorted((set(by_key_a) | set(by_key_b)) - set(common))
    warnings: list[str] = []
    if dropped:
        warnings.append(
            f"{len(dropped)} cell(s) present in one arm only and excluded from the pairing: "
            f"{dropped[:6]}{'...' if len(dropped) > 6 else ''}"
        )

    diffs = [by_key_b[k] - by_key_a[k] for k in common]
    seeds = {(state, seed) for state, seed, _ in common}
    if len(common) > len(seeds):
        warnings.append(
            "folds within a seed share ~80% of their training data, so these pairs are not "
            "independent replicates; read any p-value computed over them as descriptive"
        )

    # One delta per seed: fold deltas averaged within a seed, because folds are not replicates.
    by_seed: dict[tuple[str, int], list[float]] = {}
    for (state, seed, _), diff in zip(common, diffs):
        by_seed.setdefault((state, seed), []).append(diff)
    seed_deltas = [statistics.fmean(v) for _, v in sorted(by_seed.items())]

    if band_over not in BAND_FACTORS + ("unspecified",):
        raise ValueError(f"band_over={band_over!r}; expected one of {BAND_FACTORS}")
    return PairedComparison(
        label=label,
        band_over=band_over,
        n_pairs=len(common),
        n_seeds=len(seeds),
        seed_deltas=seed_deltas,
        mean_a=statistics.fmean(by_key_a[k] for k in common),
        mean_b=statistics.fmean(by_key_b[k] for k in common),
        delta=statistics.fmean(diffs),
        # ddof=1, matching the reference, so dispersion is comparable across pipelines.
        delta_std=statistics.stdev(diffs) if len(diffs) > 1 else 0.0,
        dropped=dropped,
        warnings=warnings,
    )


def summarise(cells: list[Cell], *, label: str = "arm") -> dict:
    """Mean and dispersion of one arm, per fold and per model seed.

    The per-seed figure treats each model seed's fold-mean as one observation, which is the
    aggregation whose `n` matches the number of independent refits — replicates under a frozen
    partition (NOMENCLATURE §2).
    """
    if not cells:
        raise ValueError(f"{label}: no cells")
    values = [c.value for c in cells]

    by_seed: dict[int, list[float]] = {}
    for cell in cells:
        by_seed.setdefault(cell.seed, []).append(cell.value)
    seed_means = [statistics.fmean(v) for v in by_seed.values()]

    return {
        "label": label,
        "n_cells": len(values),
        "n_seeds": len(by_seed),
        "mean": statistics.fmean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "seed_means": dict(zip(sorted(by_seed), [statistics.fmean(by_seed[s]) for s in sorted(by_seed)])),
        "mean_of_seed_means": statistics.fmean(seed_means),
        "std_of_seed_means": statistics.stdev(seed_means) if len(seed_means) > 1 else 0.0,
        # Nomeia o FATOR agrupado, não o desenho: `summarise` só vê `cell.seed`. Com a partição
        # congelada isso são réplicas; se ela também se mover, repetições (NOMENCLATURE §2).
        "independent_unit": "model_seed",
    }


def geometric_joint(cat: float, reg: float) -> float:
    """`sqrt(cat macro-F1 * region top10)` — the joint scalar, on the two headline metrics.

    Both operands are bounded in [0, 1], so neither head dominates by scale. That is the property
    the earlier arithmetic-mean selector lacked across a 7-class and a 1109-class head.
    """
    return math.sqrt(max(cat, 0.0) * max(reg, 0.0))


__all__ = ["Cell", "PairedComparison", "compare", "summarise", "geometric_joint"]
