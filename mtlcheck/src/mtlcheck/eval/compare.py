"""Comparing two arms: Tier A over users, Tier B over replicates, and the equivalence test.

The two tiers answer different questions with different `n`, and the protocol requires every
published number to say which one it is:

**Tier A — user generalisation.** "Would this delta hold on another sample of users from this state?"
The resampling unit is the USER, via a paired cluster bootstrap over pooled out-of-fold predictions.
Each user falls in exactly one fold, so resampling a user carries all their windows, both arms and
every replicate together. This tier carries the headline claims.

**Tier B — conditional configuration comparison.** "Given exactly the data and fits I already ran,
does this version beat that one?" The unit is the REPLICATE — the partition is frozen and only
the model seed moves (NOMENCLATURE §2). It resolves 0.05-0.15 pp effects, and
it is never quoted as a generalisation interval. Delegated to `train/stats.py`, which already does
it, rather than reimplemented here.

The rice-sack analogy from the method guide, because it is the thing people get wrong: Tier B weighs
the same sack twice on two scales. Tier A weighs several sacks from the supplier's stock.

## Why the bootstrap is paired at the user

Both arms predicted the same users. Resampling users independently per arm would discard that and
inflate the interval by the between-user variance the pairing removes — the same mistake, one level
down, as comparing unpaired fold means.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from . import estimands

logger = logging.getLogger(__name__)

DEFAULT_REPLICATES = 10_000

#: Below this many contributing users, a class's F1 is a step function of a handful of clusters and
#: the macro average carries that discreteness into the interval. See `_assert_class_support`.
MIN_USERS_PER_CLASS = 15



def banda_por_execucao(deltas, *, margem: float | None = None) -> dict | None:
    """A banda sobre o eixo de EXECUÇÃO: `t₀.₉₇₅,P−₁ · s / √P` sobre os deltas externos.

    É a quantidade que o §10.2 promete ao revisor que pergunta "seu delta se moveria sob outro
    sorteio?" — e que o código não publicava. O intervalo manchete é, e continua sendo, o bootstrap
    por usuário do §3, com as execuções promediadas dentro de cada réplica; ele não encolhe com P.
    Esta banda é a única quantidade que encolhe, e é o que as execuções extras compram.

    A forma é deliberadamente a MESMA que a escada projeta (`t · UCL₈₀(σ̂) / √P`, §2a), com o desvio
    externo no lugar do interno inflado. Assim o confronto que o §3 manda fazer — meia-largura
    realizada contra projetada — é uma subtração e não uma tradução.

    ⚠ Reportada AO LADO, nunca no lugar. Qual das duas é manchete foi decidido antes de qualquer
    leitura, que é o único momento em que a escolha não é enviesada pelo resultado.
    """
    import statistics

    from . import pilot

    p_ = len(deltas)
    gl = p_ - 1
    if gl < 2 or gl not in pilot.T95:
        return None
    s_ = statistics.stdev(deltas)
    meia = pilot.T95[gl] * s_ / math.sqrt(p_)
    media = statistics.fmean(deltas)
    saida = {"execucoes": p_, "graus_de_liberdade": gl, "sd": s_, "meia_largura": meia,
             "intervalo": [media - meia, media + meia]}
    if margem is not None:
        saida["dentro_da_margem"] = meia < margem
    return saida


@dataclass
class TierA:
    """A paired user-cluster bootstrap result."""

    delta: float
    percentile: tuple[float, float]
    bca: tuple[float, float]
    #: Studentized (Chung & Romano 2013) — the pre-registered statistic.
    p_permutation: float | None
    #: The same test WITHOUT studentization, carried as a diagnostic. For a paired sign-flip the two
    #: agree to first order (the flip leaves Σ of the squared per-user contributions unchanged), so
    #: a gap between them says the linearization is straining and the interval deserves more weight
    #: than the p-value.
    p_permutation_raw: float | None = None
    n_users: int = 0
    n_replicates: int = 0
    #: Quantas RÉPLICAS foram promediadas dentro de cada sorteio do bootstrap (§3). Réplica e
    #: não repetição: a partição está congelada e só a semente de modelo se move.
    n_replicates_fit: int = 1
    #: Two-sided coverage of both intervals. Carried rather than assumed: TOST is registered at 90%
    #: and superiority at 95%, and an interval that does not say which it is invites a reader to
    #: apply the wrong one. `equivalence()` refuses a level it was not given.
    level: float = 0.95
    warnings: list[str] = field(default_factory=list)
    #: O delta pooled-OOF por réplica, na ordem de `seeds` — a entrada dos gates do §2.
    seed_deltas: tuple[float, ...] = ()
    seeds: tuple[int, ...] = ()
    #: p unilateral de H0: Δ ≤ −δ, invertido deste mesmo BCa. Só existe quando a margem foi dada.
    p_ni: float | None = None

    @property
    def half_width(self) -> float:
        """Meia-largura do BCa, a que o §3 condiciona o TOST."""
        return (self.bca[1] - self.bca[0]) / 2.0

    @property
    def intervals_disagree(self) -> bool:
        """Percentile and BCa disagreeing is reported, never resolved by picking one.

        Disagreement means the bootstrap distribution is skewed or the statistic is biased, and the
        honest response is to say so — the protocol requires both intervals precisely so a reader
        can see it.
        """
        width = lambda i: i[1] - i[0]
        if width(self.percentile) <= 0:
            return False
        centre_shift = abs((self.bca[0] + self.bca[1]) / 2 - (self.percentile[0] + self.percentile[1]) / 2)
        return centre_shift > 0.25 * width(self.percentile)

    def describe(self) -> str:
        flag = " · percentile and BCa disagree" if self.intervals_disagree else ""
        p = (f" · studentized permutation p={self.p_permutation:.4f}"
             if self.p_permutation is not None else "")
        p += f" · S={self.n_replicates_fit}" if self.n_replicates_fit > 1 else ""
        pct = f"{self.level * 100:g}%"
        return (f"Tier A: {self.delta:+.4f} · {pct} percentile [{self.percentile[0]:+.4f}, "
                f"{self.percentile[1]:+.4f}] · BCa [{self.bca[0]:+.4f}, {self.bca[1]:+.4f}] "
                f"· n={self.n_users} users{p}{flag}")


@dataclass(frozen=True)
class _Aligned:
    """Both arms' per-user sufficient statistics on ONE user index.

    Kept as arrays rather than as closures because the permutation test has to MIX the arms per user
    — arm A takes user i's B-counts and vice versa — and a closure over one arm's counts cannot
    express that. An earlier version tried, and its weights cancelled to a no-op that silently
    returned the observed statistic every time.
    """

    users: np.ndarray
    task: str
    a: tuple[np.ndarray, ...]
    b: tuple[np.ndarray, ...]

    def metric(self, parts: tuple[np.ndarray, ...], weights: np.ndarray) -> float:
        if self.task == "cat":
            tp, fp, fn = parts
            counts = estimands.CategoryCounts(self.users, tp, fp, fn)
            return estimands.macro_f1(counts, weights)
        hits, windows = parts
        counts = estimands.RegionCounts(self.users, hits, windows,
                                        np.zeros_like(hits), np.zeros_like(hits))
        return estimands.top_k_accuracy(counts, weights)

    def delta(self, weights: np.ndarray) -> float:
        return (self.metric(self.b, weights) - self.metric(self.a, weights)) * 100.0

    def _pooled(self, pooled: tuple[np.ndarray, ...]) -> float:
        """The metric from ALREADY-POOLED counts, skipping the per-user weighting."""
        if self.task == "cat":
            tp, fp, fn = (np.asarray(v, dtype=np.float64) for v in pooled)
            denominator = 2 * tp + fp + fn
            return float(np.divide(2 * tp, denominator, out=np.zeros_like(denominator),
                                   where=denominator > 0).mean())
        hits, windows = (float(v) for v in pooled)
        return hits / windows if windows > 0 else float("nan")

    def jackknife(self) -> np.ndarray:
        """Every delete-one delta, in O(n·C) rather than O(n²·C).

        The metrics are functions of POOLED counts, so dropping user i is `total - row_i`, not a
        rescan of the other n-1 users. The naive loop called `delta()` n times and each call summed
        every user again; at Texas-scale user counts that is minutes per interval, for an
        arithmetically identical answer. Exact, not approximate — the counts are integers, so the
        subtraction loses nothing.
        """
        totals_a = tuple(np.asarray(p).sum(axis=0) for p in self.a)
        totals_b = tuple(np.asarray(p).sum(axis=0) for p in self.b)
        out = np.empty(len(self.users))
        for i in range(len(self.users)):
            left = tuple(t - np.asarray(p)[i] for t, p in zip(totals_a, self.a))
            right = tuple(t - np.asarray(p)[i] for t, p in zip(totals_b, self.b))
            out[i] = (self._pooled(right) - self._pooled(left)) * 100.0
        return out

    def swapped_delta(self, swap: np.ndarray, weights: np.ndarray) -> float:
        """The delta with the two arms' bundles exchanged for the users in `swap`."""
        mix = lambda x, y: tuple(np.where(swap.reshape((-1,) + (1,) * (p.ndim - 1)), q, p)
                                 for p, q in zip(x, y))
        return (self.metric(mix(self.b, self.a), weights)
                - self.metric(mix(self.a, self.b), weights)) * 100.0


@dataclass(frozen=True)
class _Panel:
    """One or more REPLICATES of the same comparison, on one shared user index.

    Protocol §3 is explicit about the order of operations: "resample users with replacement,
    recompute each arm's global metric from summed sufficient statistics, take the paired Δ,
    **average across seeds inside the replicate**." Averaging the *metrics* across seeds and then
    differencing, or pooling all seeds' rows into one bag, are both different statistics — the
    second also multiplies each user's weight by R and pretends the replicates are extra users.

    So a replicate is drawn ONCE and every seed is evaluated under it. That is also what makes the
    seeds comparable: the same resampled users for all of them.
    """

    users: np.ndarray
    task: str
    seeds: tuple[int, ...]
    parts: tuple[_Aligned, ...]

    def delta(self, weights: np.ndarray) -> float:
        return float(np.mean([p.delta(weights) for p in self.parts]))

    def swapped_delta(self, swap: np.ndarray, weights: np.ndarray) -> float:
        return float(np.mean([p.swapped_delta(swap, weights) for p in self.parts]))

    def jackknife(self) -> np.ndarray:
        return np.mean([p.jackknife() for p in self.parts], axis=0)


def _assert_single_task(frame: pd.DataFrame, task: str, who: str) -> None:
    """A prediction file holds one row per task per window, and a joint cell holds BOTH tasks.

    Handing the unfiltered frame to `task="reg"` is silently wrong rather than loudly wrong: the
    category rows carry `rank_of_true <= 7 <= 10`, so every one of them counts as a region hit and
    Acc@10 rises toward the mixture. (`task="cat"` happens to crash on the closed-label-space check,
    which is luck, not design.) So the frame must say which task it is, and agree.
    """
    if "task" not in frame.columns:
        raise ValueError(f"{who}: prediction rows carry no `task` column; refusing to guess which "
                         f"of a joint cell's two row sets was meant")
    present = set(frame["task"].unique())
    if present != {task}:
        raise ValueError(f"{who}: asked for task {task!r} but the rows contain {sorted(present)}. "
                         f"Filter the frame — a joint cell banks both tasks in one file.")


def _assert_class_support(aligned: _Aligned, minimum: int) -> None:
    """Refuse a macro-F1 bootstrap whose classes rest on a handful of users.

    A user-cluster bootstrap resamples USERS, so a class whose entire support sits in a few of them
    has an effective n of that few — the class's F1 then jumps between a small set of values, the
    macro average inherits the jumps, and the interval is neither narrow-because-precise nor
    wide-because-honest. It is a discrete distribution wearing a continuous interval's clothes, and
    nothing downstream can see that from the number.

    A class with NO support and NO predictions in BOTH arms is exempt: it contributes a constant 0
    to each under every resample, so it cannot distort the delta. The dangerous case is
    1 <= users < minimum in EITHER arm.

    The distinction is not pedantry. Taking the elementwise MINIMUM of the two arms' counts — which
    is what this did first — exempts a class that one arm never touches while the other rests it on
    three users: min(0, 3) = 0 reads as "absent everywhere". That class contributes a constant 0 to
    one arm and a jumpy per-class F1 to the other, which is precisely an asymmetric, bootstrap-
    unstable term in the delta. Measured distortion on a 3-user class: 0.37 pp against a 0.4 pp
    margin. So the test is on the MAXIMUM: exempt only when both arms are empty.
    """
    contributing = lambda parts: ((parts[0] + parts[1] + parts[2]) > 0).sum(axis=0)
    a_counts, b_counts = contributing(aligned.a), contributing(aligned.b)
    counts = np.maximum(a_counts, b_counts)
    thin = [(int(c), int(a_counts[c]), int(b_counts[c]))
            for c in range(len(counts)) if 0 < counts[c] < minimum]
    if thin:
        raise ValueError(
            f"classes {thin} (class, users_a, users_b) rest on fewer than {minimum} users; "
            f"a user-cluster bootstrap of macro-F1 over them reports an interval it cannot support. "
            f"Report per-class F1 with counts instead, or pass min_users_per_class=None knowingly.")


def _align(frame_a: pd.DataFrame, frame_b: pd.DataFrame, task: str,
           num_classes: int | None, k: int) -> _Panel:
    """Both arms, every shared replicate, on one shared user index."""
    seeds_a = _replicates(frame_a)
    seeds_b = _replicates(frame_b)
    seeds = tuple(sorted(set(seeds_a) & set(seeds_b)))
    if not seeds:
        raise ValueError(f"the arms share no model_seed: {sorted(seeds_a)} vs {sorted(seeds_b)}")
    if set(seeds_a) != set(seeds_b):
        logger.warning("arms carry different replicate sets (%s vs %s); comparing the %d they "
                       "share", sorted(seeds_a), sorted(seeds_b), len(seeds))

    parts = [_align_one(frame_a[frame_a["model_seed"] == s] if "model_seed" in frame_a else frame_a,
                        frame_b[frame_b["model_seed"] == s] if "model_seed" in frame_b else frame_b,
                        task, num_classes, k) for s in seeds]
    # One user index for every replicate — a replicate that saw a different user set would make the
    # per-replicate deltas incomparable and the resampling weights meaningless.
    shared = parts[0].users
    for part in parts[1:]:
        shared = np.intersect1d(shared, part.users)
    parts = [_restrict(part, shared) for part in parts]
    return _Panel(users=shared, task=task, seeds=seeds, parts=tuple(parts))


def _replicates(frame: pd.DataFrame) -> tuple[int, ...]:
    if "model_seed" not in frame.columns:
        return (0,)
    return tuple(int(v) for v in sorted(frame["model_seed"].unique()))


def _restrict(aligned: _Aligned, users: np.ndarray) -> _Aligned:
    if len(users) == len(aligned.users):
        return aligned
    index = np.searchsorted(aligned.users, users)
    return _Aligned(users, aligned.task,
                    tuple(p[index] for p in aligned.a), tuple(p[index] for p in aligned.b))


def _windows(frame: pd.DataFrame) -> np.ndarray:
    """As janelas de um braço, em ordem canônica: (fold, usuário, janela)."""
    cols = [frame[c].to_numpy(dtype=np.int64) for c in ("fold", "userid", "window_id")]
    order = np.lexsort(cols[::-1])
    return np.stack([c[order] for c in cols])


def _assert_paired_windows(frame_a: pd.DataFrame, frame_b: pd.DataFrame, task: str) -> None:
    """Os dois braços pontuaram exatamente as MESMAS janelas.

    A métrica de cada usuário soma sobre as janelas que aquele braço tiver, então conjuntos de
    janela diferentes comparam denominadores diferentes — e nada a jusante percebe, porque
    `window_id` era persistido desde sempre e não era lido em lugar nenhum.

    As 54 células da `v19_defence` foram conferidas e concordam: a guarda é para wave morta e sync
    parcial, não resgate.
    """
    faltando = {"fold", "window_id"} - (set(frame_a.columns) & set(frame_b.columns))
    if faltando:
        raise ValueError(f"{task}: as linhas não carregam {sorted(faltando)}; o pareamento por "
                         f"janela não é verificável")
    a, b = _windows(frame_a), _windows(frame_b)
    if a.shape != b.shape or not np.array_equal(a, b):
        como = (f"{a.shape[1]} contra {b.shape[1]} linhas" if a.shape != b.shape
                else f"as mesmas {a.shape[1]} linhas, janelas distintas")
        raise ValueError(
            f"{task}: os dois braços pontuaram conjuntos de janela DIFERENTES ({como}). A métrica "
            f"soma sobre as janelas de cada braço, então o delta sairia sobre denominadores "
            f"diferentes.")


def _align_one(frame_a: pd.DataFrame, frame_b: pd.DataFrame, task: str,
               num_classes: int | None, k: int) -> _Aligned:
    """Reduce both arms to per-user statistics on the users they share.

    The shared index is the point: both arms predicted the same users, and pairing at the user is
    what removes the between-user variance an independent resample would re-admit.
    """
    _assert_paired_windows(frame_a, frame_b, task)
    if task == "cat":
        a = estimands.category_counts(frame_a, num_classes)
        b = estimands.category_counts(frame_b, num_classes)
        users = np.intersect1d(a.users, b.users)
        ia, ib = np.searchsorted(a.users, users), np.searchsorted(b.users, users)
        # Both arms are reduced against the SAME closed label space, so a width mismatch here means
        # one of them was reduced under a different num_classes — which would compare two macro
        # averages over different denominators.
        if a.tp.shape[1] != b.tp.shape[1]:
            raise ValueError(f"arms were reduced over {a.tp.shape[1]} and {b.tp.shape[1]} classes; "
                             f"their macro averages have different denominators")
        pad = lambda m: m
        return _Aligned(users, task,
                        (pad(a.tp)[ia], pad(a.fp)[ia], pad(a.fn)[ia]),
                        (pad(b.tp)[ib], pad(b.fp)[ib], pad(b.fn)[ib]))

    a = estimands.region_counts(frame_a, k=k)
    b = estimands.region_counts(frame_b, k=k)
    users = np.intersect1d(a.users, b.users)
    ia, ib = np.searchsorted(a.users, users), np.searchsorted(b.users, users)
    return _Aligned(users, task, (a.hits[ia], a.windows[ia]), (b.hits[ib], b.windows[ib]))


def tier_a(frame_a: pd.DataFrame, frame_b: pd.DataFrame, *, task: str, level: float = 0.95,
           **kwargs) -> TierA:
    """Um nível só. Ver `tier_a_levels`, que é onde o bootstrap acontece."""
    return tier_a_levels(frame_a, frame_b, task=task, levels=(level,), **kwargs)[level]


def tier_a_levels(frame_a: pd.DataFrame, frame_b: pd.DataFrame, *, task: str,
                  num_classes: int | None = None, k: int = 10,
                  replicates: int = DEFAULT_REPLICATES, seed: int = 0,
                  permutations: int | None = 10_000,
                  levels: tuple[float, ...] = (0.90, 0.95), margin: float | None = None,
                  min_users_per_class: int | None = MIN_USERS_PER_CLASS) -> dict[float, TierA]:
    """Paired user-cluster bootstrap of `metric(b) - metric(a)`, in percentage points.

    Vários níveis de UM bootstrap só: intervalos de duas amostragens podem se cruzar por ruído de
    Monte Carlo — o de 90% saindo mais largo que o de 95% — e aí o veredito depende do sorteio.

    `min_users_per_class` guards the category branch (see `_assert_class_support`); pass None to
    disable it deliberately, which is a decision that belongs in a log rather than in a default.
    """
    for level in levels:
        if not 0.5 < level < 1.0:
            raise ValueError(f"level={level} is not a two-sided coverage in (0.5, 1)")
    _assert_single_task(frame_a, task, "arm A")
    _assert_single_task(frame_b, task, "arm B")
    aligned = _align(frame_a, frame_b, task, num_classes, k)
    n = len(aligned.users)
    if n < 2:
        raise ValueError(f"{n} shared users; a user bootstrap needs a population")
    if task == "cat" and min_users_per_class is not None:
        for part in aligned.parts:
            _assert_class_support(part, min_users_per_class)

    ones = np.ones(n)
    observed = aligned.delta(ones)

    rng = np.random.default_rng(seed)
    draws = np.empty(replicates)
    for i in range(replicates):
        # Multiplicities, not index arrays: the metrics are weighted sums over users, so a replicate
        # is a dot product rather than a rescan of the rows.
        draws[i] = aligned.delta(rng.multinomial(n, ones / n).astype(np.float64))

    # Studentized sign-flip permutation (Chung & Romano 2013), which §3 pre-registers: exact under
    # the sharp null and still valid under the weak null of metric equality. The numerator is the
    # EXACT swapped delta; the scale comes from jackknife pseudo-values, which give each user a
    # contribution the flip can act on without an O(n) refit per permutation.
    p_value = p_raw = None
    if permutations:
        jack = aligned.jackknife()
        pseudo = n * observed - (n - 1) * jack
        scale = float(np.std(pseudo, ddof=1)) / math.sqrt(n) if n > 1 else float("nan")
        observed_t = observed / scale if scale > 0 else float("inf")

        exceed = exceed_raw = 0
        for _ in range(permutations):
            swap = rng.random(n) < 0.5
            sign = np.where(swap, -1.0, 1.0)
            flipped = aligned.swapped_delta(swap, ones)
            scale_star = float(np.std(sign * pseudo, ddof=1)) / math.sqrt(n) if n > 1 else 0.0
            if scale_star > 0 and abs(flipped / scale_star) >= abs(observed_t):
                exceed += 1
            if abs(flipped) >= abs(observed):
                exceed_raw += 1
        p_value = (exceed + 1) / (permutations + 1)
        p_raw = (exceed_raw + 1) / (permutations + 1)

    warnings = []
    if n < 200:
        warnings.append(f"only {n} users; the interval is wide and BCa acceleration is unstable")

    p_ni = None if margin is None else _ni_pvalue(draws, observed, aligned, margin)

    saida = {}
    for level in levels:
        tail = 100.0 * (1.0 - level) / 2.0
        percentile = (float(np.percentile(draws, tail)), float(np.percentile(draws, 100.0 - tail)))
        saida[level] = TierA(
            delta=observed, percentile=percentile,
            bca=_bca_interval(draws, observed, aligned, level),
            p_permutation=p_value, p_permutation_raw=p_raw, n_users=n, n_replicates=replicates,
            n_replicates_fit=len(aligned.seeds), level=level, warnings=list(warnings),
            seed_deltas=tuple(float(part.delta(ones)) for part in aligned.parts),
            seeds=aligned.seeds, p_ni=p_ni)
    return saida


def _bca_params(draws: np.ndarray, observed: float, aligned: _Aligned) -> tuple[float, float] | None:
    """`z0` e a aceleração. None quando a correção é indefinida e o percentil é o recuo."""
    from scipy import stats as scipy_stats

    # Mid-p for ties. With a discrete statistic — and per-user hit counts are discrete — replicates
    # land exactly on the observed value often enough that `< observed` alone biases z0 downward and
    # shifts BOTH endpoints in the same direction.
    proportion = float((draws < observed).mean() + 0.5 * (draws == observed).mean())
    if proportion <= 0 or proportion >= 1:
        return None
    jack = aligned.jackknife()
    centred = jack.mean() - jack
    denominator = 6.0 * float((centred ** 2).sum()) ** 1.5
    return (float(scipy_stats.norm.ppf(proportion)),
            float((centred ** 3).sum() / denominator) if denominator > 0 else 0.0)


def _bca_endpoint(draws: np.ndarray, params: tuple[float, float], alpha: float) -> float:
    from scipy import stats as scipy_stats

    z0, acceleration = params
    z = scipy_stats.norm.ppf(alpha)
    adjusted = z0 + (z0 + z) / (1 - acceleration * (z0 + z))
    return float(np.percentile(draws, 100 * scipy_stats.norm.cdf(adjusted)))


def _bca_interval(draws: np.ndarray, observed: float, aligned: _Aligned,
                  level: float = 0.95) -> tuple[float, float]:
    """Bias-corrected and accelerated interval (Efron 1987).

    The percentile interval is only correct when the bootstrap distribution is unbiased and of
    constant variance; BCa corrects both, at the cost of a jackknife. Reported alongside rather than
    instead, so a disagreement stays visible.
    """
    tail = (1.0 - level) / 2.0
    params = _bca_params(draws, observed, aligned)
    if params is None:
        return (float(np.percentile(draws, 100 * tail)), float(np.percentile(draws, 100 * (1 - tail))))
    return (_bca_endpoint(draws, params, tail), _bca_endpoint(draws, params, 1.0 - tail))


def _ni_pvalue(draws: np.ndarray, observed: float, aligned: _Aligned, margin: float) -> float:
    """O p unilateral de não-inferioridade, H0: Δ ≤ −δ, invertendo o MESMO BCa.

    Invertido em vez de calculado à parte para que o veredito por intervalo e o veredito por p não
    possam discordar: por construção, `p < α` ⟺ o limite inferior BCa a (1−α) unilateral excede −δ.
    Dois estimadores independentes da mesma coisa se cruzariam perto da margem, que é exatamente
    onde a decisão acontece.

    O endpoint BCa a α é `Q(Φ(z0 + (z0+z_α)/(1 − a(z0+z_α))))`. Igualando a −δ e resolvendo para α:
    com `v = z_q − z0`, onde `q` é a posição empírica de −δ nos replicates, sai
    `z_α = v/(1 + a·v) − z0`.
    """
    from scipy import stats as scipy_stats

    q = float((draws < -margin).mean() + 0.5 * (draws == -margin).mean())
    params = _bca_params(draws, observed, aligned)
    if params is None:
        return float(min(max(q, 0.0), 1.0))
    z0, acceleration = params
    q = min(max(q, 1e-12), 1 - 1e-12)
    v = float(scipy_stats.norm.ppf(q)) - z0
    denominator = 1.0 + acceleration * v
    if denominator <= 0:
        # −δ está fora do alcance do endpoint. `v` grande positivo põe a margem acima do teto
        # alcançável — nenhum α rejeita, p = 1; `v` muito negativo põe abaixo do piso, p = 0.
        return 0.0 if v < 0 else 1.0
    return float(scipy_stats.norm.cdf(v / denominator - z0))


# ---------------------------------------------------------------- equivalence


#: §3, verbatim: "|Δ| ≤ 0.05 pp is indistinguishable from re-running the same configuration
#: (measured re-run noise 0.02–0.05 pp) and is never claimed in either direction, regardless of p".
#: Tabela §5: "Reporting floor | |Δ| ≤ 0.05 pp = re-run noise; never claimed".
#:
#: É regra de REIVINDICAÇÃO, não de cálculo — o intervalo continua sendo reportado. O que ela proíbe
#: é chamar de superior um efeito que uma re-execução apagaria. Até 2026-08-19 não existia em código
#: nenhum: `equivalence((0.01, 0.05), 0.03, 0.4)` devolvia SUPERIOR, e em Texas a meia-largura de
#: bootstrap medida é 0,02–0,08 pp — ou seja, certificaria como superior algo dentro do próprio ruído.
RERUN_FLOOR = 0.05

#: α do teste de superioridade. §5: "α = 0.05 two-sided".
SUPERIORITY_ALPHA = 0.05


@dataclass(frozen=True)
class Equivalence:
    """A four-way verdict against a pre-specified margin.

    Four, not two. The first version carried a boolean `superior` computed as `low > 0 or high < 0`,
    which reports SUPERIOR for an interval entirely BELOW zero — a significantly *inferior* result
    printed as a win. It is the only place in this layer where a wrong-direction conclusion could be
    produced, and it survived because both tests exercised positive effects.

    The protocol's primary hypothesis is non-inferiority, gatekeeping superiority: an arm must first
    clear -margin, and only then may it be called superior.
    """

    delta: float
    margin: float
    interval: tuple[float, float]
    verdict: str          # "superior" | "non_inferior" | "inferior" | "inconclusive"
    #: |Δ| caiu no piso de re-execução do §3. O veredito já foi rebaixado; isto existe para que o
    #: relatório NÃO possa omitir a razão.
    #:
    #: ⚠ Fica entre os campos COM default. Pôr um campo defaultado antes de um sem quebra a
    #: dataclass na definição — cometi esse erro duas vezes em 19-08, e da segunda o
    #: `tests/test_every_module_imports.py` pegou em menos de um segundo.
    within_rerun_floor: bool = False
    #: p do teste de permutação estudentizado. `None` = o teste não foi corrido, e então superior é
    #: irreivindicável.
    p_superiority: float | None = None
    #: The coverage of `interval`, carried so the printed verdict states it. A TOST read off a 95%
    #: interval is conservative; read off a 99% one it is very conservative; read off an interval
    #: whose level nobody recorded it is not a test.
    level: float = 0.95
    #: Falso = o dado não decide nesta margem, o que não é o mesmo que "os dois são equivalentes".
    tost_claimable: bool = True
    half_width: float = float("nan")

    @property
    def equivalent(self) -> bool:
        """Both bounds inside the margin — practical equivalence, not merely a null test."""
        return bool(self.interval[0] > -self.margin and self.interval[1] < self.margin)

    @property
    def non_inferior(self) -> bool:
        return bool(self.interval[0] > -self.margin)

    @property
    def superior(self) -> bool:
        return self.verdict == "superior"

    def describe(self) -> str:
        equivalente = self.equivalent and self.tost_claimable
        wording = {
            "superior": "SUPERIOR (non-inferior AND interval above 0)",
            "non_inferior": f"NON-INFERIOR within ±{self.margin}"
                            + (" (and equivalent)" if equivalente else ""),
            "inferior": f"INFERIOR (interval below −{self.margin})",
            "inconclusive": "INCONCLUSIVE — neither non-inferior nor shown worse",
        }[self.verdict]
        # Sem esta linha, largura vira evidência.
        gate = ("" if self.tost_claimable
                else f" · TOST NÃO reivindicável: meia-largura {self.half_width:.4f} ≥ δ")
        return (f"{self.delta:+.4f} [{self.interval[0]:+.4f}, {self.interval[1]:+.4f}] "
                f"({self.level * 100:g}%) vs margin ±{self.margin}: {wording}{gate}")


def equivalence(interval: tuple[float, float], delta: float, margin: float, *,
                p_superiority: float | None = None, rerun_floor: float = RERUN_FLOOR,
                level: float = 0.95) -> Equivalence:
    """Two one-sided tests, via the interval-inclusion form (Schuirmann 1987; Lakens 2017).

    The 90% interval inside ±margin is the usual TOST statement; the protocol uses the 95% interval,
    which is conservative for equivalence and lets ONE interval serve both questions rather than
    computing two and inviting a mismatch.

    A non-significant superiority test is NOT equivalence — that inference is the reason this
    function exists. Both verdicts are reported; they are not mutually exclusive by construction and
    "inconclusive" is a real, common, honest outcome.
    """
    low, high = interval
    if high < -margin:
        verdict = "inferior"
    elif low > -margin:
        verdict = "superior" if low > 0 else "non_inferior"
    else:
        verdict = "inconclusive"

    # ── as duas condições do §3 que faltavam, aplicadas SÓ à superioridade ────────────────────────
    #
    # Nenhuma das duas mexe no intervalo nem no Δ: as duas restringem o que se pode CHAMAR de
    # superior. O `inferior` não passa por aqui de propósito — ele exige o intervalo inteiro abaixo
    # de −δ, o que é incompatível com |Δ| ≤ 0,05, então a regra é inalcançável daquele lado.
    floored = abs(delta) <= rerun_floor
    if verdict == "superior":
        if floored:
            # Rebaixa para o veredito imediatamente abaixo, NÃO para um quinto veredito: o §3 define
            # exatamente quatro, e inventar "abaixo-do-piso" quebraria a taxonomia pré-registrada.
            # O intervalo continua inteiramente acima de −δ, então a não-inferioridade se sustenta.
            verdict = "non_inferior"
        elif p_superiority is None or p_superiority >= SUPERIORITY_ALPHA:
            # §3 define superioridade como NI **e** o teste de permutação estudentizado, com o
            # intervalo como requisito ADICIONAL. O código usava só o intervalo — não invertia a
            # ordem, deixava cair uma das duas condições, o que torna "superior" estritamente mais
            # fraco que a definição registrada. `None` quebra alto de propósito: um chamador que não
            # correu o teste não pode reivindicar superioridade.
            verdict = "non_inferior"

    return Equivalence(delta=delta, margin=margin, interval=interval, verdict=verdict, level=level,
                       within_rerun_floor=floored, p_superiority=p_superiority)


def equivalence_from(tier: TierA, margin: float, *, interval: str = "bca") -> Equivalence:
    """The verdict for a Tier A result, taking its level from the result rather than a default.

    The only reason this exists: `equivalence(t.bca, t.delta, margin)` silently defaults to 95% even
    when `t` was computed at 90%, and the mismatch is invisible in the printed line. Passing the
    whole result makes that unrepresentable.
    """
    chosen = tier.bca if interval == "bca" else tier.percentile
    # O p viaja junto automaticamente: deixá-lo opcional aqui reintroduziria, pelo caminho fácil, a
    # superioridade sem teste que o §3 proíbe.
    return equivalence(chosen, tier.delta, margin, level=tier.level,
                       p_superiority=getattr(tier, "p_permutation", None))


#: Bilateral 90%: o limite inferior dele É o unilateral de 95% que o §3 pede para a NI.
NI_LEVEL = 0.90
#: O requisito ADICIONAL de superioridade — o IC que tem de excluir zero.
SUPERIORITY_LEVEL = 0.95


@dataclass(frozen=True)
class CriticalMargins:
    """As margens em que o veredito MARGINAL vira. Subtração do intervalo, não escolha.

    O veredito do §3 é função de δ por duas travessias e nada mais: abaixo de `inferiority` o
    intervalo inteiro fica sob −δ, acima de `non_inferiority` ele fica todo acima, e entre as duas é
    inconclusivo. Publicar os dois números diz ao leitor onde a conclusão dele cairia sem que ele
    precise refazer conta nenhuma — e torna visível a célula que passa raspando.

    São do veredito MARGINAL, coerente com o §12.6d: o Holm move o p, não o intervalo.
    """

    non_inferiority: float
    inferiority: float
    #: O TOST só é reivindicável com meia-largura abaixo de δ, então a meia-largura É o δ crítico dele.
    tost: float


def critical_margins(tiers: dict[float, TierA]) -> CriticalMargins:
    ni = tiers[NI_LEVEL]
    return CriticalMargins(non_inferiority=-ni.bca[0], inferiority=-ni.bca[1], tost=ni.half_width)


def registered_verdict(tiers: dict[float, TierA], margin: float) -> Equivalence:
    """O veredito do §3, montado dos DOIS níveis registrados.

    A regra, na ordem em que o protocolo a escreve:

    * **não-inferioridade** e **TOST** saem do IC bilateral de 90%;
    * **superioridade** exige, além da NI, o p estudentizado < 0,05 **e** o IC de 95% excluindo zero;
    * **inferioridade** é o intervalo inteiro abaixo de −δ;
    * o piso de re-execução rebaixa superioridade a não-inferioridade;
    * o TOST só é reivindicável se a meia-largura de 90% ficar abaixo de δ.
    """
    faltando = [lvl for lvl in (NI_LEVEL, SUPERIORITY_LEVEL) if lvl not in tiers]
    if faltando:
        raise ValueError(f"o veredito registrado precisa dos níveis {faltando}; recebeu "
                         f"{sorted(tiers)}. Use `tier_a_levels`, que produz os dois de um bootstrap.")
    ni, sup = tiers[NI_LEVEL], tiers[SUPERIORITY_LEVEL]

    base = equivalence(ni.bca, ni.delta, margin, level=NI_LEVEL,
                       p_superiority=ni.p_permutation)
    # `equivalence` já aplicou NI, piso e p. Falta a condição do IC de 95%, que ele não podia ver.
    verdict = base.verdict
    if verdict == "superior" and not (sup.bca[0] > 0 or sup.bca[1] < 0):
        verdict = "non_inferior"

    return Equivalence(delta=ni.delta, margin=margin, interval=ni.bca, verdict=verdict,
                       level=NI_LEVEL, within_rerun_floor=base.within_rerun_floor,
                       p_superiority=ni.p_permutation,
                       tost_claimable=ni.half_width < margin, half_width=ni.half_width)


__all__ = ["TierA", "Equivalence", "CriticalMargins", "critical_margins",
           "tier_a", "tier_a_levels", "equivalence", "equivalence_from",
           "registered_verdict", "NI_LEVEL", "SUPERIORITY_LEVEL",
           "DEFAULT_REPLICATES",
           "MIN_USERS_PER_CLASS"]
