"""Tier A, the equivalence test, and multiplicity — the inference layer.

The tests that matter here are the ones that would catch a bootstrap which looks plausible and is
wrong: a permutation that never permutes, an interval that ignores the pairing, an "equivalent"
verdict read off a non-significant superiority test.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mtlcheck.eval import compare, estimands, multiplicity


def _arm(users, hits_per_user, windows_per_user=10, seed=0):
    """Region rows where each user has a controlled number of top-10 hits."""
    rows = []
    for user, hits in zip(users, hits_per_user):
        ranks = [1] * hits + [50] * (windows_per_user - hits)
        for window, rank in enumerate(ranks):
            rows.append({"userid": user, "fold": user % 5, "window_id": window, "task": "reg",
                         "y_true": 0, "y_pred": 0, "rank_of_true": rank})
    return pd.DataFrame(rows)


def test_the_permutation_actually_permutes() -> None:
    """A swapped delta must differ from the observed one — an earlier version's weights cancelled.

    The first implementation built per-user weights that summed to 1 everywhere, so every "permuted"
    statistic equalled the observed statistic and the p-value was structurally 1.0. It looked
    entirely reasonable.
    """
    users = np.arange(60)
    a = _arm(users, [4] * 60)
    b = _arm(users, [7] * 60)

    aligned = compare._align(a, b, "reg", None, 10)
    ones = np.ones(len(aligned.users))
    observed = aligned.delta(ones)

    all_swapped = aligned.swapped_delta(np.ones(len(aligned.users), dtype=bool), ones)
    assert observed == pytest.approx(30.0), "b hits 7/10, a hits 4/10 -> +30 pp"
    assert all_swapped == pytest.approx(-observed), "swapping every user must flip the sign"

    half = np.zeros(len(aligned.users), dtype=bool)
    half[::2] = True
    assert aligned.swapped_delta(half, ones) != pytest.approx(observed)


def test_the_bootstrap_fixture_is_actually_sensitive_to_the_weights() -> None:
    """Guards the OTHER tests, not the code.

    Every user in the first fixtures had the SAME hit rate, so `top_k_accuracy` was invariant to the
    resampling weights: every replicate returned the identical number and the interval collapsed to a
    point. Those tests passed against a bootstrap that never resampled anything. Heterogeneity across
    users is the property that makes a user-cluster interval measure something, so it is asserted.
    """
    users = np.arange(40)
    frame = _arm(users, [2 * (u % 6) for u in users])
    counts = estimands.region_counts(frame, k=10)

    ones = np.ones(len(counts.users))
    lean = ones.copy()
    lean[: len(ones) // 2] = 0.0                       # drop half the users
    assert estimands.top_k_accuracy(counts, ones) != pytest.approx(
        estimands.top_k_accuracy(counts, lean)), "a weight-invariant fixture cannot test a bootstrap"


def test_tier_a_detects_a_real_effect_and_reports_a_small_p() -> None:
    users = np.arange(120)
    # Heterogeneous baselines, a uniform +2/10 improvement. The delta is constant; the LEVEL is not,
    # so the resampling has something to move.
    base = [(u % 5) + 2 for u in users]
    a = _arm(users, base)
    b = _arm(users, [h + 2 for h in base])

    result = compare.tier_a(a, b, task="reg", replicates=400, permutations=400, seed=1)
    assert result.delta == pytest.approx(20.0)
    assert result.percentile[0] > 0, "a uniform +20 pp effect must exclude zero"
    assert result.p_permutation < 0.01
    assert result.n_users == 120


def test_tier_a_does_not_separate_a_null_effect() -> None:
    """The failure mode that matters: an interval that excludes zero when nothing is happening.

    The arms differ per user with mean zero — not identical arms, which would make the delta
    structurally 0.0 and the test unfalsifiable.
    """
    rng = np.random.default_rng(4)
    users = np.arange(150)
    hits = rng.integers(2, 8, 150)
    jitter = rng.choice([-1, 0, 1], 150)
    a = _arm(users, hits)
    b = _arm(users, np.clip(hits + jitter, 0, 10))

    result = compare.tier_a(a, b, task="reg", replicates=600, permutations=600, seed=2)
    assert abs(result.delta) < 3.0
    assert result.percentile[0] < 0 < result.percentile[1]
    assert result.percentile[1] - result.percentile[0] > 0.1, "a real interval has width"
    assert result.p_permutation > 0.05


def test_the_interval_level_is_carried_not_assumed() -> None:
    """A 90% TOST read off a 95% interval is a different test, and the printed line said neither."""
    users = np.arange(80)
    base = [(u % 5) + 2 for u in users]
    a = _arm(users, base)
    b = _arm(users, [h + 1 for h in base])

    wide = compare.tier_a(a, b, task="reg", replicates=400, permutations=0, seed=3, level=0.95)
    narrow = compare.tier_a(a, b, task="reg", replicates=400, permutations=0, seed=3, level=0.90)
    assert narrow.level == 0.90 and "90%" in narrow.describe()
    assert (narrow.percentile[1] - narrow.percentile[0]) <= (wide.percentile[1] - wide.percentile[0])

    verdict = compare.equivalence_from(narrow, margin=0.4)
    assert verdict.level == 0.90, "the verdict must inherit the level it was computed at"
    with pytest.raises(ValueError):
        compare.tier_a(a, b, task="reg", replicates=10, permutations=0, level=1.5)


def test_bca_agrees_with_scipy_on_a_case_both_can_do() -> None:
    """BCa was written from the paper and never checked against an implementation.

    The check has to be on a statistic scipy can also express, so the comparison is of the INTERVAL
    machinery rather than of two different estimands: here, the mean per-user hit rate of one arm,
    which is what the paired delta reduces to when the other arm is a constant zero.
    """
    scipy_stats = pytest.importorskip("scipy.stats")
    rng = np.random.default_rng(11)
    values = rng.gamma(2.0, 1.0, 200)

    ours = compare._bca_interval(
        draws=np.array([float(np.mean(rng.choice(values, 200, replace=True))) for _ in range(4000)]),
        observed=float(values.mean()),
        aligned=_ScalarAligned(values), level=0.95)
    theirs = scipy_stats.bootstrap((values,), np.mean, n_resamples=4000, method="BCa",
                                   random_state=np.random.default_rng(12)).confidence_interval

    # Both are Monte Carlo at 4 000 resamples, so they agree to within resampling noise, not exactly.
    assert ours[0] == pytest.approx(theirs.low, abs=0.05)
    assert ours[1] == pytest.approx(theirs.high, abs=0.05)


class _ScalarAligned:
    """The minimum `_bca_interval` needs: a delete-one series over `users`."""

    def __init__(self, values):
        self.users = np.arange(len(values))
        self._values = np.asarray(values, dtype=np.float64)

    def jackknife(self):
        total = self._values.sum()
        n = len(self._values)
        return (total - self._values) / (n - 1)


def test_a_class_carried_by_a_handful_of_users_is_refused() -> None:
    """Blocker: macro-F1's cluster bootstrap over a 3-user class is a step function in a suit."""
    rows = []
    for user in range(60):
        for window in range(4):
            label = 0 if user > 2 else 3          # class 3 lives in three users only
            rows.append({"userid": user, "fold": 0, "window_id": window, "task": "cat",
                         "y_true": label, "y_pred": label, "rank_of_true": 1})
    frame = pd.DataFrame(rows)

    with pytest.raises(ValueError, match="fewer than 15 users"):
        compare.tier_a(frame, frame.copy(), task="cat", replicates=50, permutations=0)
    # Disabling it is allowed, and is a decision the caller makes in the open.
    compare.tier_a(frame, frame.copy(), task="cat", replicates=50, permutations=0,
                   min_users_per_class=None)


def test_equivalence_is_not_the_absence_of_superiority() -> None:
    """The inference this whole layer exists to prevent.

    A wide interval straddling zero is INCONCLUSIVE, not equivalent. Reading it as equivalence is
    how "no significant difference" becomes "no measured cost" without evidence.
    """
    wide = compare.equivalence((-2.0, 2.0), delta=0.1, margin=0.4)
    assert not wide.superior
    assert not wide.equivalent, "a +/-2 pp interval cannot establish equivalence at +/-0.4"
    assert "INCONCLUSIVE" in wide.describe()

    # `p_superiority` explícito desde 2026-08-19: sem ele a superioridade é irreivindicável por
    # construção, e o `not tight.superior` abaixo passaria pelo motivo errado.
    tight = compare.equivalence((-0.15, 0.20), delta=0.02, margin=0.4, p_superiority=0.9)
    assert tight.equivalent and not tight.superior

    clear = compare.equivalence((0.25, 0.55), delta=0.40, margin=0.4, p_superiority=0.001)
    assert clear.superior


def test_holm_is_more_conservative_than_raw_and_ordered() -> None:
    adjusted = multiplicity.holm({"a": 0.001, "b": 0.02, "c": 0.30}, alpha=0.05)
    assert all(adj >= raw for raw, adj in zip(adjusted.raw, adjusted.adjusted))
    assert adjusted.rejected() == ("a", "b")


def test_partial_conjunction_answers_in_how_many_datasets() -> None:
    """The cross-state statement: "real in at least u of these", not "real on average".

    An arm that wins in five states and collapses in one is the case that already occurred in this
    project, and pooling would hide it.
    """
    five_good_one_bad = [0.001, 0.002, 0.003, 0.004, 0.005, 0.90]
    assert multiplicity.partial_conjunction(five_good_one_bad, u=5) < 0.05
    assert multiplicity.partial_conjunction(five_good_one_bad, u=6) > 0.05, (
        "requiring all six must fail when one state plainly disagrees")


def test_an_interval_below_zero_is_inferior_not_superior() -> None:
    """The wrong-direction bug: `low > 0 or high < 0` called a clearly worse arm SUPERIOR.

    It survived because every other test exercised positive effects. This is the only place in the
    layer where a conclusion could be printed backwards.
    """
    clearly_worse = compare.equivalence((-0.90, -0.60), delta=-0.75, margin=0.4)
    assert clearly_worse.verdict == "inferior"
    assert not clearly_worse.superior
    assert "INFERIOR" in clearly_worse.describe()

    # Acima do piso de re-execução E com o teste de permutação corrido — as duas condições que o
    # §3 exige para a palavra "superior". Antes de 19-08 o intervalo sozinho bastava.
    clearly_better = compare.equivalence((0.30, 0.60), delta=0.45, margin=0.4, p_superiority=0.001)
    assert clearly_better.verdict == "superior" and clearly_better.superior

    # Non-inferiority gatekeeps superiority: inside the margin but not above zero.
    tie = compare.equivalence((-0.20, 0.15), delta=-0.02, margin=0.4)
    assert tie.verdict == "non_inferior" and tie.equivalent and not tie.superior

    straddling = compare.equivalence((-2.0, 2.0), delta=0.1, margin=0.4)
    assert straddling.verdict == "inconclusive" and not straddling.equivalent


def test_a_joint_cells_two_row_sets_are_never_mixed() -> None:
    """A joint prediction file holds cat AND reg rows; `task="reg"` over both is silently wrong.

    Category rows have rank_of_true <= 7 <= 10, so every one counts as a region hit and Acc@10 drifts
    toward the mixture. Nothing crashes and nothing looks odd.
    """
    users = np.arange(40)
    reg = _arm(users, [(u % 5) + 2 for u in users])
    cat = reg.copy()
    cat["task"] = "cat"
    cat["rank_of_true"] = 1
    mixed = pd.concat([reg, cat], ignore_index=True)

    with pytest.raises(ValueError, match="the rows contain"):
        compare.tier_a(mixed, mixed.copy(), task="reg", replicates=20, permutations=0)
    compare.tier_a(reg, reg.copy(), task="reg", replicates=20, permutations=0)


def test_a_class_one_arm_never_touches_is_not_exempt() -> None:
    """The exemption hole: min(0, 3) read as "absent everywhere" and waved a 3-user class through.

    Arm A never predicts and never sees class 3; arm B rests it on three users. The class is a
    constant 0 in A and a step function in B — an asymmetric, bootstrap-unstable term in the delta,
    measured at 0.37 pp against a 0.4 pp margin. Exemption belongs to classes BOTH arms leave empty.
    """
    def frame(rare_users: int) -> pd.DataFrame:
        rows = []
        for user in range(60):
            for window in range(4):
                label = 3 if user < rare_users else 0
                rows.append({"userid": user, "fold": 0, "window_id": window, "task": "cat",
                             "y_true": label, "y_pred": label, "rank_of_true": 1})
        return pd.DataFrame(rows)

    with pytest.raises(ValueError, match="fewer than 15 users"):
        compare.tier_a(frame(0), frame(3), task="cat", replicates=20, permutations=0)
    # Both arms empty on every rare class: exempt, and it runs.
    compare.tier_a(frame(0), frame(0), task="cat", replicates=20, permutations=0)


@pytest.mark.parametrize("task", ["reg", "cat"])
def test_the_fast_jackknife_equals_the_naive_one(task) -> None:
    """The O(n) rewrite must be arithmetically identical, not merely close.

    It replaces n full rescans with `total - row_i`. The counts are integers, so this is exact — and
    a test that only checked "close" would let a genuinely different estimator through.
    """
    rng = np.random.default_rng(7)
    users = np.arange(50)
    if task == "reg":
        a = _arm(users, [(u % 7) + 1 for u in users])
        b = _arm(users, [(u % 5) + 3 for u in users])
    else:
        rows = []
        for user in users:
            for window in range(6):
                rows.append({"userid": user, "fold": 0, "window_id": window, "task": "cat",
                             "y_true": int(rng.integers(0, 7)), "y_pred": int(rng.integers(0, 7)),
                             "rank_of_true": 1})
        a = pd.DataFrame(rows)
        b = a.copy()
        b["y_pred"] = rng.integers(0, 7, len(b))

    aligned = compare._align(a, b, task, None, 10)
    ones = np.ones(len(aligned.users))
    naive = np.array([aligned.delta(np.where(np.arange(len(ones)) == i, 0.0, ones))
                      for i in range(len(ones))])
    assert np.allclose(aligned.jackknife(), naive, rtol=0, atol=1e-12)


def test_replicates_are_averaged_inside_the_draw_not_pooled_as_extra_users() -> None:
    """Protocol §3: "take the paired Δ, average across seeds inside the replicate".

    Pooling two replicates' rows into one bag instead would double every user's weight and read as
    2n independent users — the interval would narrow by ~sqrt(2) for no new data. The check: two
    replicates of the SAME comparison must not narrow the interval relative to one.
    """
    users = np.arange(90)
    base = [(u % 6) + 2 for u in users]
    a = _arm(users, base)
    b = _arm(users, [h + 2 for h in base])

    def with_seed(frame, seed):
        out = frame.copy()
        out["model_seed"] = seed
        return out

    single = compare.tier_a(with_seed(a, 0), with_seed(b, 0), task="reg",
                            replicates=500, permutations=0, seed=3)
    doubled = compare.tier_a(pd.concat([with_seed(a, 0), with_seed(a, 1)], ignore_index=True),
                             pd.concat([with_seed(b, 0), with_seed(b, 1)], ignore_index=True),
                             task="reg", replicates=500, permutations=0, seed=3)

    assert doubled.n_replicates_fit == 2 and single.n_replicates_fit == 1
    assert doubled.n_users == single.n_users, "replicates are not extra users"
    width = lambda t: t.percentile[1] - t.percentile[0]
    assert width(doubled) == pytest.approx(width(single), rel=1e-9), (
        "an identical second replicate carries no new information and must not narrow the interval")


def test_the_permutation_is_studentized_and_reports_both() -> None:
    """§3 pre-registers the studentized statistic; the raw one rides along as a diagnostic.

    For a paired sign-flip the two agree to first order — the flip leaves the sum of squared per-user
    contributions unchanged — so what this pins is that both are computed and both are reported,
    and that they do agree on a well-behaved case rather than being the same number by construction.
    """
    users = np.arange(100)
    base = [(u % 5) + 2 for u in users]
    result = compare.tier_a(_arm(users, base), _arm(users, [h + 2 for h in base]),
                            task="reg", replicates=200, permutations=500, seed=5)

    assert result.p_permutation is not None and result.p_permutation_raw is not None
    assert result.p_permutation < 0.01 and result.p_permutation_raw < 0.01
    assert "studentized" in result.describe()


# ── §3: o piso de re-execução e o gate de permutação (2026-08-19) ───────────────────────────────

def test_a_delta_inside_the_rerun_floor_is_never_called_superior() -> None:
    """§3, literal: "|Δ| ≤ 0,05 pp … is never claimed in either direction, regardless of p".

    O caso que a auditoria reproduziu: `equivalence((0.01, 0.05), 0.03, 0.4)` devolvia SUPERIOR. Em
    Texas a meia-largura de bootstrap medida é 0,02–0,08 pp, então o teste certificaria como superior
    um efeito que uma re-execução apagaria.
    """
    e = compare.equivalence((0.01, 0.05), delta=0.03, margin=0.4, p_superiority=0.0001)
    assert e.verdict == "non_inferior", "um Δ dentro do ruído de re-execução não é superioridade"
    assert e.within_rerun_floor is True, "a razão do rebaixamento tem de viajar no veredito"


def test_the_floor_does_not_invent_a_fifth_verdict() -> None:
    """O §3 define exatamente QUATRO. Um veredito 'abaixo-do-piso' quebraria a taxonomia
    pré-registrada — o rebaixamento vai para o veredito imediatamente abaixo, e a razão vira flag."""
    e = compare.equivalence((0.01, 0.05), delta=0.03, margin=0.4, p_superiority=0.0001)
    assert e.verdict in {"superior", "non_inferior", "inferior", "inconclusive"}


def test_superiority_requires_the_permutation_test() -> None:
    """§3: superioridade é NI **e** o teste de permutação, com o intervalo como requisito ADICIONAL.

    O código usava só o intervalo. Não invertia a ordem — deixava cair uma das duas condições, o que
    torna 'superior' estritamente mais fraco que a definição registrada.
    """
    sem_p = compare.equivalence((0.10, 0.30), delta=0.20, margin=0.4)
    assert sem_p.verdict == "non_inferior", (
        "sem o teste de permutação a superioridade é irreivindicável — um chamador que não o correu "
        "não pode reivindicá-la")

    p_alto = compare.equivalence((0.10, 0.30), delta=0.20, margin=0.4, p_superiority=0.30)
    assert p_alto.verdict == "non_inferior"

    com_p = compare.equivalence((0.10, 0.30), delta=0.20, margin=0.4, p_superiority=0.001)
    assert com_p.verdict == "superior", (
        "o contrapeso: acima do piso e com p significativo, superior continua alcançável — sem isto "
        "uma implementação que nunca devolve superior passaria nos dois testes acima")


def test_no_banked_sealed_verdict_changes() -> None:
    """A pergunta que decide se isto é conserto ou reinterpretação de resultado selado.

    Os seis vereditos da primeira leitura selada, recomputados sob as duas regras novas. O menor
    |Δ| é 0,1201 — 2,4× o piso — e o único 'superior' (Istambul categoria) passa no gate com
    p = 0,0032. Se este teste falhar um dia, a mudança deixou de ser 'completar a análise
    pré-registrada' e virou reinterpretação: adendo datado, nunca edição silenciosa.
    """
    import json
    from pathlib import Path

    evidencia = (Path(__file__).resolve().parents[2]
                 / "studies/porting_validation/evidence/sealed_bridge_tier_a.json")
    if not evidencia.exists():
        pytest.skip("evidência da leitura selada ausente")

    esperado = {("alabama", "cat"): "inconclusive", ("alabama", "reg"): "inferior",
                ("arizona", "cat"): "non_inferior", ("arizona", "reg"): "inconclusive",
                ("istanbul", "cat"): "superior", ("istanbul", "reg"): "non_inferior"}
    for r in json.loads(evidencia.read_text()):
        got = compare.equivalence(tuple(r["bca"]), delta=r["delta"], margin=r["margin"],
                                  p_superiority=r["p_studentized"]).verdict
        assert got == esperado[(r["state"], r["task"])], (
            f"{r['state']}/{r['task']}: veredito selado era "
            f"{esperado[(r['state'], r['task'])]} e agora resolve para {got}")


# ── os dois níveis registrados (§3) ─────────────────────────────────────────────────────────────


def _duas_amostras(n=400, shift=0.0, seed=0):
    """Duas urnas pareadas por usuário, com um deslocamento controlado em pp."""
    rng = np.random.default_rng(seed)
    users = np.repeat(np.arange(n), 5)
    base = rng.random(len(users)) < 0.5
    extra = rng.random(len(users)) < (shift / 100.0)
    frame = lambda hits: pd.DataFrame({
        "task": "reg", "userid": users, "y_true": 0, "fold": users % 5,
        "window_id": np.tile(np.arange(5), n),
        "rank_of_true": np.where(hits, 1, 50), "model_seed": 0})
    return frame(base), frame(base | extra)


def test_um_bootstrap_so_produz_os_dois_niveis_e_o_de_90_e_mais_estreito() -> None:
    """Dois bootstraps separados podem se cruzar por ruído de Monte Carlo, e aí o veredito depende
    de qual sorteio caiu onde. Os dois níveis têm de sair dos MESMOS replicates."""
    a, b = _duas_amostras(shift=2.0)
    tiers = compare.tier_a_levels(a, b, task="reg", replicates=400, permutations=0)

    assert set(tiers) == {compare.NI_LEVEL, compare.SUPERIORITY_LEVEL}
    assert tiers[0.90].delta == tiers[0.95].delta, "o mesmo Δ observado nos dois"
    assert tiers[0.90].half_width < tiers[0.95].half_width, (
        "o de 90% é estritamente mais estreito; se não for, não vieram do mesmo bootstrap")


def test_o_veredito_registrado_le_NI_do_intervalo_de_90() -> None:
    """O limite inferior bilateral de 90% É o unilateral de 95% que o §3 pede para a NI.

    Um efeito nulo com meia-largura entre os dois níveis é não-inferior sob a regra registrada e
    inconclusivo sob a leitura antiga de 95% — que é o poder de equivalência que se perdia.
    """
    ni = compare.TierA(delta=0.0, percentile=(-0.30, 0.30), bca=(-0.30, 0.30),
                       p_permutation=0.9, level=0.90)
    sup = compare.TierA(delta=0.0, percentile=(-0.36, 0.36), bca=(-0.36, 0.36),
                        p_permutation=0.9, level=0.95)
    veredito = compare.registered_verdict({0.90: ni, 0.95: sup}, margin=0.4)

    assert veredito.verdict == "non_inferior"
    assert veredito.equivalent and veredito.tost_claimable
    assert veredito.level == 0.90, "o veredito tem de declarar de qual intervalo saiu"


def test_superioridade_exige_TAMBEM_o_intervalo_de_95_excluindo_zero() -> None:
    """A condição adicional do §3. Sem ela, um efeito que o IC de 90% separa de zero e o de 95% não
    seria chamado de superior a um α que o protocolo não registra."""
    ni = compare.TierA(delta=0.5, percentile=(0.05, 0.95), bca=(0.05, 0.95),
                       p_permutation=0.01, level=0.90)
    apertado = compare.TierA(delta=0.5, percentile=(-0.02, 1.02), bca=(-0.02, 1.02),
                             p_permutation=0.01, level=0.95)
    folgado = compare.TierA(delta=0.5, percentile=(0.02, 0.98), bca=(0.02, 0.98),
                            p_permutation=0.01, level=0.95)

    assert compare.registered_verdict({0.90: ni, 0.95: apertado}, 0.4).verdict == "non_inferior"
    assert compare.registered_verdict({0.90: ni, 0.95: folgado}, 0.4).verdict == "superior"


def test_o_gate_de_meia_largura_declara_impotencia_em_vez_de_deixar_calado() -> None:
    """§3: "claimable only if the realized 90% half-width < δ".

    Uma metade do gate é aritmética e não precisa de código: um intervalo contido em (−δ, +δ) tem
    meia-largura < δ por construção. A metade que PRECISA de código é a outra — quando a
    meia-largura passa de δ, o dado não decide nesta margem, e isso tem de ser DITO. Sem a frase, o
    caso sai como "inconclusive" e um leitor lê discordância entre os braços onde houve só falta de
    precisão. O §3 separa as duas coisas de propósito: "TOST fail + superiority fail = undetermined
    at margin δ, reported as such, never collapsed into either verdict".
    """
    impreciso = compare.TierA(delta=0.0, percentile=(-0.55, 0.55), bca=(-0.55, 0.55),
                              p_permutation=0.9, level=0.90)
    sup = compare.TierA(delta=0.0, percentile=(-0.66, 0.66), bca=(-0.66, 0.66),
                        p_permutation=0.9, level=0.95)

    veredito = compare.registered_verdict({0.90: impreciso, 0.95: sup}, margin=0.4)
    assert not veredito.equivalent, "o intervalo não cabe em ±δ"
    assert not veredito.tost_claimable and veredito.half_width == pytest.approx(0.55)
    assert "TOST NÃO reivindicável" in veredito.describe(), (
        "a impotência tem de aparecer na linha, senão vira silêncio")


def test_um_intervalo_que_cabe_na_margem_tem_o_gate_satisfeito_por_aritmetica() -> None:
    """A outra metade, fixada para que ninguém 'conserte' o gate invertendo-o."""
    ni = compare.TierA(delta=0.0, percentile=(-0.39, 0.39), bca=(-0.39, 0.39),
                       p_permutation=0.9, level=0.90)
    sup = compare.TierA(delta=0.0, percentile=(-0.45, 0.45), bca=(-0.45, 0.45),
                        p_permutation=0.9, level=0.95)

    veredito = compare.registered_verdict({0.90: ni, 0.95: sup}, margin=0.4)
    assert veredito.equivalent and veredito.tost_claimable
    assert "TOST NÃO reivindicável" not in veredito.describe()


def test_o_veredito_registrado_recusa_um_nivel_faltando() -> None:
    ni = compare.TierA(delta=0.0, percentile=(-0.1, 0.1), bca=(-0.1, 0.1), p_permutation=0.5,
                       level=0.90)
    with pytest.raises(ValueError, match="precisa dos níveis"):
        compare.registered_verdict({0.90: ni}, margin=0.4)


def test_os_deltas_por_semente_ficam_expostos_para_os_gates_do_paragrafo_2() -> None:
    """Os três gates de escalonamento são funções destes números. Enquanto não saíam do `_Panel`,
    eram incomputáveis fora do módulo."""
    a, b = _duas_amostras(shift=1.0)
    a["model_seed"] = np.where(np.arange(len(a)) % 2, 7, 0)
    b["model_seed"] = a["model_seed"]

    tier = compare.tier_a_levels(a, b, task="reg", replicates=100, permutations=0)[0.90]
    assert tier.seeds == (0, 7)
    assert len(tier.seed_deltas) == 2
    assert abs(float(np.mean(tier.seed_deltas)) - tier.delta) < 1e-9, (
        "o Δ do painel é a média dos deltas por réplica — §3, 'average across seeds'")


def test_o_p_de_NI_e_o_intervalo_concordam_por_construcao() -> None:
    """A propriedade que justifica inverter o BCa em vez de calcular o p à parte.

    `p_ni < α` tem de ser exatamente `limite inferior BCa a (1−α) unilateral > −δ`. Dois estimadores
    independentes da mesma coisa se cruzariam perto da margem — que é onde a decisão acontece — e aí
    a tabela diria "não-inferior" e o p diria o contrário na mesma linha.
    """
    for shift in (-1.0, -0.4, 0.0, 0.6):
        a, b = _duas_amostras(shift=abs(shift), seed=3)
        if shift < 0:
            a, b = b, a
        tiers = compare.tier_a_levels(a, b, task="reg", replicates=3000, permutations=0,
                                      margin=0.4, levels=(0.90,))
        tier = tiers[0.90]
        # O IC bilateral de 90% tem 5% em cada cauda, logo o limite inferior é o unilateral de 95%.
        pelo_intervalo = tier.bca[0] > -0.4
        pelo_p = tier.p_ni < 0.05
        assert pelo_intervalo == pelo_p, (
            f"shift={shift}: intervalo diz NI={pelo_intervalo} (low {tier.bca[0]:+.4f}) e "
            f"p_ni={tier.p_ni:.4f} diz NI={pelo_p}")


def test_o_p_de_NI_e_monotono_na_margem() -> None:
    """Margem maior é hipótese nula mais fraca, logo mais fácil de rejeitar."""
    a, b = _duas_amostras(shift=0.5, seed=5)
    ps = [compare.tier_a_levels(a, b, task="reg", replicates=2000, permutations=0,
                                margin=m, levels=(0.90,))[0.90].p_ni
          for m in (0.1, 0.4, 1.0)]
    assert ps[0] >= ps[1] >= ps[2]


def test_sem_margem_nao_ha_p_de_NI() -> None:
    """`None` em vez de um default: um p de NI contra uma margem que ninguém declarou não é teste."""
    a, b = _duas_amostras(shift=0.5)
    assert compare.tier_a_levels(a, b, task="reg", replicates=200,
                                 permutations=0)[0.90].p_ni is None


# ── o pareamento é por janela, não só por usuário ───────────────────────────────────────────────

def test_dois_bracos_sobre_janelas_diferentes_sao_recusados() -> None:
    """`window_id` era persistido desde sempre e não era lido em lugar nenhum.

    O pareamento intersecta usuários, e a métrica de cada usuário soma sobre as janelas que aquele
    braço tiver — então um braço com menos janelas por usuário produz um delta sobre denominadores
    diferentes, com todas as demais guardas verdes. Latente nas 54 células da campanha; a guarda é
    para wave morta e sync parcial.
    """
    users = np.arange(40)
    a = _arm(users, [5] * 40, windows_per_user=10)
    b = _arm(users, [5] * 40, windows_per_user=8)

    with pytest.raises(ValueError, match="janela DIFERENTES"):
        compare._align(a, b, "reg", None, 10)


def test_as_mesmas_janelas_em_ordem_trocada_passam() -> None:
    """A conferência é de conjunto, não de ordem de linha — senão um sort a mais viraria recusa."""
    users = np.arange(40)
    a = _arm(users, [5] * 40)
    b = _arm(users, [7] * 40).sample(frac=1.0, random_state=3).reset_index(drop=True)

    aligned = compare._align(a, b, "reg", None, 10)
    assert len(aligned.users) == 40


# ── δ crítico: a margem em que o veredito vira ──────────────────────────────────────────────────

def _tiers(low, high, *, p=0.001):
    meio = (low + high) / 2
    return {lvl: compare.TierA(delta=meio, percentile=(low, high), bca=(low, high),
                               p_permutation=p, n_users=400)
            for lvl in (compare.NI_LEVEL, compare.SUPERIORITY_LEVEL)}


def test_o_delta_critico_e_exatamente_onde_o_veredito_vira() -> None:
    """δ* não é escolha nem aproximação: é `−limite inferior`, e o veredito vira ali.

    Publicá-lo resume a curva inteira de sensibilidade num número, e mostra a célula que passa
    raspando — que três pontos amostrados em {0,2 · 0,4 · 1,0} escondem.
    """
    tiers = _tiers(-0.37, +0.12)
    critico = compare.critical_margins(tiers).non_inferiority
    assert critico == pytest.approx(0.37)

    assert compare.registered_verdict(tiers, critico + 1e-9).verdict == "non_inferior"
    assert compare.registered_verdict(tiers, critico - 1e-9).verdict == "inconclusive"


def test_o_delta_critico_de_inferioridade_e_o_outro_extremo() -> None:
    tiers = _tiers(-0.90, -0.50)
    c = compare.critical_margins(tiers)
    assert c.inferiority == pytest.approx(0.50)
    assert compare.registered_verdict(tiers, 0.50 - 1e-9).verdict == "inferior"
    assert compare.registered_verdict(tiers, 0.50 + 1e-9).verdict == "inconclusive"


def test_um_intervalo_todo_acima_de_zero_e_nao_inferior_a_qualquer_margem() -> None:
    """δ* negativo é a leitura correta de "nenhuma margem positiva derruba esta célula"."""
    c = compare.critical_margins(_tiers(+0.20, +0.60))
    assert c.non_inferiority < 0
    assert compare.registered_verdict(_tiers(+0.20, +0.60), 1e-9).verdict == "superior"


def test_o_delta_critico_do_TOST_e_a_meia_largura() -> None:
    tiers = _tiers(-0.30, +0.30)
    assert compare.critical_margins(tiers).tost == pytest.approx(0.30)
    assert compare.registered_verdict(tiers, 0.31).tost_claimable
    assert not compare.registered_verdict(tiers, 0.29).tost_claimable


def test_o_delta_critico_e_o_p_de_NI_concordam_por_construcao() -> None:
    """Na margem crítica o p unilateral de NI vale exatamente o α do nível — os dois saem do MESMO
    endpoint BCa, e uma discordância aqui significaria que o Holm decide sobre um p que não é o do
    intervalo impresso ao lado dele."""
    rng = np.random.default_rng(3)
    users = np.arange(300)
    base = rng.integers(0, 9, 300)
    a = _arm(users, base)
    b = _arm(users, np.minimum(base + rng.integers(0, 2, 300), 10))

    niveis = compare.tier_a_levels(a, b, task="reg", levels=(0.90, 0.95), replicates=400,
                                   permutations=0, seed=0)
    critico = compare.critical_margins(niveis).non_inferiority
    de_novo = compare.tier_a_levels(a, b, task="reg", levels=(0.90, 0.95), replicates=400,
                                    permutations=0, seed=0, margin=critico)
    assert de_novo[compare.NI_LEVEL].p_ni == pytest.approx(0.05, abs=5e-3)


# ── a variante de combinação do §4a ─────────────────────────────────────────────────────────────

def test_bonferroni_nunca_e_mais_permissivo_que_simes() -> None:
    """Simes exige independência ou PRDS entre os conjuntos; Bonferroni vale sob dependência
    arbitrária. A precondição do §4a rodou e falhou (§12.6c), então o preço é este."""
    ps = [0.001, 0.004, 0.01, 0.02, 0.30, 0.61]
    for u in range(1, 7):
        simes = multiplicity.partial_conjunction(ps, u, "simes")
        bonf = multiplicity.partial_conjunction(ps, u, "bonferroni")
        assert bonf >= simes - 1e-12, f"u={u}: bonferroni {bonf} < simes {simes}"


def test_bonferroni_e_o_p_de_ordem_u_vezes_a_cauda() -> None:
    ps = [0.001, 0.004, 0.01, 0.02, 0.30, 0.61]
    assert multiplicity.partial_conjunction(ps, 3, "bonferroni") == pytest.approx(4 * 0.01)
    assert multiplicity.partial_conjunction(ps, 6, "bonferroni") == pytest.approx(0.61)


def test_a_conjuncao_crua_NAO_e_monotona_e_por_isso_a_curva_e_corrigida() -> None:
    """Sem o máximo corrente, "vale em pelo menos 6" rejeitaria com "pelo menos 5" falhando.

    O multiplicador `n − u + 1` encolhe enquanto `p_(u)` cresce, e o produto pode cair: aqui o cru dá
    1,20 em u=5 e 0,70 em u=6. Não é uma afirmação que alguém possa fazer.
    """
    ps = [0.001, 0.002, 0.003, 0.004, 0.60, 0.70]
    cru = [min(1.0, (6 - u + 1) * sorted(ps)[u - 1]) for u in range(1, 7)]
    assert cru[4] > cru[5], "o cru realmente cai de u=5 para u=6"

    valores = multiplicity.curve(ps, "bonferroni")
    assert valores == sorted(valores)
    assert valores[5] == pytest.approx(1.0), "u=6 herda o máximo de u=5, não o 0,70 do cru"


def test_u_estrela_e_o_maior_que_rejeita() -> None:
    ps = [0.001, 0.002, 0.003, 0.004, 0.60, 0.70]
    u = multiplicity.largest_u(ps, "bonferroni")
    assert u == 4, "quatro conjuntos sustentam o efeito; o quinto p mata a partir de u=5"
    assert multiplicity.partial_conjunction(ps, u, "bonferroni") <= 0.05
    assert multiplicity.partial_conjunction(ps, u + 1, "bonferroni") > 0.05


def test_um_combinador_desconhecido_e_recusado() -> None:
    with pytest.raises(ValueError, match="combiner desconhecido"):
        multiplicity.partial_conjunction([0.1, 0.2], 1, "fisher")
