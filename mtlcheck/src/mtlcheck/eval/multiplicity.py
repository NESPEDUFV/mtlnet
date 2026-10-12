"""Multiplicity control — because a sweep compares many arms and reports the best one.

Selecting the maximum of many noisy comparisons and reporting its nominal p-value is the
"selection on a noisy criterion" failure Cawley & Talbot (2010) describe, and a sweep is that failure
by construction. These are the corrections the protocol names, kept in one place so a family is
declared rather than assumed.

**A family must be declared before the tests are run.** The correction is only meaningful relative to
the set of comparisons that COULD have been reported, not the set that happened to look interesting.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Adjusted:
    labels: tuple[str, ...]
    raw: tuple[float, ...]
    adjusted: tuple[float, ...]
    method: str
    alpha: float

    def rejected(self) -> tuple[str, ...]:
        return tuple(l for l, p in zip(self.labels, self.adjusted) if p <= self.alpha)

    def describe(self) -> str:
        kept = self.rejected()
        return (f"{self.method} at alpha={self.alpha}: {len(kept)}/{len(self.labels)} rejected"
                + (f" ({', '.join(kept)})" if kept else ""))


def holm(pvalues: dict[str, float], alpha: float = 0.05) -> Adjusted:
    """Holm-Bonferroni step-down: controls the family-wise error rate, no independence assumption.

    The protocol's choice for the HEADLINE family (few comparisons, a false positive is expensive).
    Uniformly more powerful than Bonferroni and valid under any dependence.
    """
    labels = tuple(pvalues)
    raw = np.array([pvalues[l] for l in labels], dtype=float)
    order = np.argsort(raw)
    m = len(raw)

    running = 0.0
    out = np.empty(m)
    for rank, index in enumerate(order):
        running = max(running, (m - rank) * raw[index])
        out[index] = min(running, 1.0)
    return Adjusted(labels, tuple(raw), tuple(out), "Holm-Bonferroni", alpha)


def benjamini_hochberg(pvalues: dict[str, float], q: float = 0.10) -> Adjusted:
    """BH step-up: controls the false discovery rate.

    The protocol's choice for the SCREENING stage, where the cost of a false positive is one wasted
    confirmatory cell rather than a wrong claim, and FWER control would reject almost everything.
    """
    labels = tuple(pvalues)
    raw = np.array([pvalues[l] for l in labels], dtype=float)
    order = np.argsort(raw)[::-1]
    m = len(raw)

    running = 1.0
    out = np.empty(m)
    for position, index in enumerate(order):
        rank = m - position
        running = min(running, raw[index] * m / rank)
        out[index] = min(running, 1.0)
    return Adjusted(labels, tuple(raw), tuple(out), "Benjamini-Hochberg", q)


COMBINERS = ("simes", "bonferroni")


def partial_conjunction(pvalues: list[float], u: int, combiner: str = "simes") -> float:
    """"The effect is real in at least `u` of these datasets" — Benjamini & Heller (2008).

    This is the cross-state statement the author actually wants, and it is not the same as pooling.
    Pooling asks "is there an average effect"; this asks "does it hold in at least u places", which
    survives one state behaving differently — the case that already occurred here when an arm won at
    Florida and collapsed at Alabama.

    Both variants combine the `n - u + 1` largest p-values. **Simes needs independence or PRDS
    across the datasets; Bonferroni holds under arbitrary dependence and costs power.** Which one is
    valid is a property of the corpora, not a preference — §4a pre-registered the user-overlap
    intersection as the precondition that decides it, and for this project it FAILED (§12.6c: 24.5%
    of users appear in more than one US state, and travellers carry 51% of Texas check-ins). So the
    caller passes the combiner and the analysis recipe declares it; there is no safe default here,
    only a default that is safe for someone else's corpus.
    """
    p = np.sort(np.asarray(pvalues, dtype=float))
    n = len(p)
    if not 1 <= u <= n:
        raise ValueError(f"u must be in 1..{n}; got {u}")
    return curve(pvalues, combiner)[u - 1]


def curve(pvalues: list[float], combiner: str) -> list[float]:
    """A conjunção parcial para todo u, MONÓTONA — o que se reporta como "vale em pelo menos u".

    A combinação crua não é monótona em u: o multiplicador `n − u + 1` encolhe enquanto a estatística
    de ordem `p_(u)` cresce, e para Bonferroni o produto pode cair. Com p = [.001 .002 .003 .004 .60
    .70] o cru dá 1,20 em u=5 e 0,70 em u=6 — o que licenciaria "vale em pelo menos 6" com "vale em
    pelo menos 5" rejeitado, que não é uma afirmação que alguém possa fazer.

    O máximo corrente é o conserto padrão e só aumenta p, então continua válido.
    """
    if combiner not in COMBINERS:
        raise ValueError(f"combiner desconhecido {combiner!r}; use um de {list(COMBINERS)}")
    p = np.sort(np.asarray(pvalues, dtype=float))
    n = len(p)

    saida, corrente = [], 0.0
    for u in range(1, n + 1):
        tail = p[u - 1:]
        m = len(tail)
        cru = m * tail[0] if combiner == "bonferroni" else np.min(tail * m / np.arange(1, m + 1))
        corrente = max(corrente, min(float(cru), 1.0))
        saida.append(corrente)
    return saida


def largest_u(pvalues: list[float], combiner: str, alpha: float = 0.05) -> int:
    """u*: o maior u cuja conjunção parcial rejeita. Zero quando nem u=1 rejeita.

    É o que o §4a manda reportar — "non-inferior in at least u of 6 states". Bem definido porque
    `curve` é monótona: os u que rejeitam são um prefixo, então contá-los É o maior deles.
    """
    valores = curve(pvalues, combiner)
    return sum(1 for v in valores if v <= alpha)


__all__ = ["Adjusted", "holm", "benjamini_hochberg", "partial_conjunction", "curve", "largest_u",
           "COMBINERS"]
