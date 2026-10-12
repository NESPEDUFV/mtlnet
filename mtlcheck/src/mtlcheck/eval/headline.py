"""A família manchete de UM estado — a unidade em que o protocolo decide.

O `compare` por (estado, tarefa) não conseguia produzir duas coisas que o protocolo obriga, e não
por falta de código: por falta de escopo. Holm é *dentro* da família de um estado (§5) e a
reivindicação co-primária é a interseção das duas tarefas no mesmo contrato de checkpoint (§3) —
nenhuma das duas existe olhando uma célula por vez.

## Onde Holm entra, e os três lugares onde NÃO entra

Entra entre as CADEIAS de um estado, no p de entrada de cada uma (o de não-inferioridade). Não entra
dentro da cadeia NI→superioridade, que é sequência fixa ao mesmo α (§3, o switching do EMA); não
entra entre estados, que o §5 proíbe em texto; e não entra entre os componentes da co-primária, que
o §3 quer a α cheio (Berger 1982).

## A reconciliação entre §3 e §5

Os dois convivem, mas a leitura precisa ser dita: a **tabela marginal por tarefa** — onde cada
tarefa é reivindicada sozinha — é a família de m=2 sob Holm; a **frase-manchete conjuntiva** é UMA
reivindicação, testada por interseção-união com cada componente a α cheio. Registrada em nota datada
no §12 antes da leitura, porque decide se o p da tarefa mais fraca é comparado a α ou a α/2.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from . import compare as compare_mod
from . import estimands, multiplicity
from .analysis import Analysis, HeadlineTest

ALPHA = 0.05


@dataclass(frozen=True)
class TaskReading:
    """Uma cadeia da família: uma tarefa, dois braços, NI e depois superioridade."""

    test: HeadlineTest
    tiers: dict[float, compare_mod.TierA]
    marginal: compare_mod.Equivalence
    pooled: dict[str, float]
    p_ni: float
    p_ni_adjusted: float
    #: O α local desta cadeia depois de Holm. A superioridade herda ele, não gasta um novo.
    alpha_local: float
    verdict: str
    #: As margens em que o veredito marginal vira — uma subtração do intervalo, não uma escolha.
    critical: compare_mod.CriticalMargins
    sensitivity: dict[str, str]
    #: Os relatórios que o §1/§3/§5 obrigam a sair NA leitura: tabela por classe, mínimo de usuários
    #: contribuintes, diagnósticos de região, meia-largura realizada contra a projetada, e a MDE.
    diagnostics: dict

    @property
    def task(self) -> str:
        return self.test.task

    @property
    def ni_holds(self) -> bool:
        return self.verdict in ("superior", "non_inferior")

    def describe(self) -> str:
        tier = self.tiers[compare_mod.NI_LEVEL]
        ajuste = ("" if self.p_ni_adjusted == self.p_ni
                  else f" (Holm {self.p_ni:.4f} → {self.p_ni_adjusted:.4f})")
        return (f"  {self.task:3s} {self.test.arm_b} vs {self.test.arm_a}: "
                f"{tier.delta:+.4f} [{tier.bca[0]:+.4f}, {tier.bca[1]:+.4f}] 90% · "
                f"p_NI={self.p_ni_adjusted:.4f}{ajuste} · {self.verdict.upper()} · "
                f"δ*={self.critical.non_inferiority:+.4f}")


@dataclass(frozen=True)
class StateReading:
    state: str
    analysis: Analysis
    tasks: tuple[TaskReading, ...]
    co_primary: str
    co_primary_reason: str

    def task(self, name: str) -> TaskReading:
        for reading in self.tasks:
            if reading.task == name:
                return reading
        raise KeyError(f"{self.state}: sem leitura para {name!r}")


def read_state(*, state: str, analysis: Analysis,
               frame_for: Callable[[HeadlineTest], tuple[pd.DataFrame, pd.DataFrame]],
               train_labels_for: Callable[[HeadlineTest], dict[str, list[int]]] | None = None,
               alpha: float = ALPHA) -> StateReading:
    """A leitura da família manchete de um estado. `frame_for` entrega as linhas dos dois braços."""
    tiers_por_teste, pooled_por_teste, diag_por_teste = {}, {}, {}
    for test in analysis.tests:
        frame_a, frame_b = frame_for(test)
        tiers_por_teste[test.label] = compare_mod.tier_a_levels(
            frame_a, frame_b, task=test.task, levels=analysis.levels, margin=analysis.delta,
            replicates=analysis.replicates, permutations=analysis.permutations, seed=analysis.seed)
        pooled_por_teste[test.label] = {
            test.arm_a: estimands.pooled_metric(frame_a, test.task) * 100,
            test.arm_b: estimands.pooled_metric(frame_b, test.task) * 100}
        rotulos = None if train_labels_for is None else train_labels_for(test)
        diag_por_teste[test.label] = _diagnostics(
            test, frame_a, frame_b, tiers_por_teste[test.label], analysis, rotulos)

    ps = {label: tiers[compare_mod.NI_LEVEL].p_ni for label, tiers in tiers_por_teste.items()}
    ajustados, locais = _corrigir(ps, analysis.correction, alpha)

    leituras = []
    for test in analysis.tests:
        tiers = tiers_por_teste[test.label]
        bruto, ajustado = ps[test.label], ajustados[test.label]
        alpha_local = locais[test.label]
        leituras.append(TaskReading(
            test=test, tiers=tiers,
            marginal=compare_mod.registered_verdict(tiers, analysis.delta),
            pooled=pooled_por_teste[test.label], p_ni=bruto, p_ni_adjusted=ajustado,
            alpha_local=alpha_local,
            critical=compare_mod.critical_margins(tiers),
            verdict=_verdict_under(tiers, analysis.delta, ajustado, alpha_local, alpha),
            sensitivity={str(m): compare_mod.registered_verdict(tiers, m).verdict
                         for m in analysis.sensitivity},
            diagnostics=diag_por_teste[test.label]))

    veredito, motivo = _co_primary(leituras, analysis.delta)
    return StateReading(state=state, analysis=analysis, tasks=tuple(leituras),
                        co_primary=veredito, co_primary_reason=motivo)


def _diagnostics(test: HeadlineTest, frame_a: pd.DataFrame, frame_b: pd.DataFrame,
                 tiers: dict[float, compare_mod.TierA], analysis: Analysis,
                 train_labels: dict[str, list[int]] | None) -> dict:
    """Os relatórios obrigatórios. Nenhum deles move o Δ; todos mudam o que é reportável.

    A MDE sai da LARGURA e só dela — cega a sinal e a centro — então publicá-la ao lado do veredito
    não é a espiada que o §5 proíbe ao mandá-la sair antes dos testes.
    """
    from scipy import stats as scipy_stats

    tier = tiers[compare_mod.NI_LEVEL]
    # O erro-padrão vem da largura do intervalo em que ela foi medida; a MDE é reportada na
    # convenção do §6, "α = 0.05 two-sided", que é a da tabela de poder e não a do nível de NI.
    z_intervalo = scipy_stats.norm.ppf(1 - (1 - tier.level) / 2)
    z_alpha = scipy_stats.norm.ppf(1 - ALPHA / 2)
    z_power = scipy_stats.norm.ppf(analysis.mde_power)
    erro_padrao = tier.half_width / z_intervalo if z_intervalo else float("nan")
    baixo, alto = analysis.projected_half_width

    saida = {
        "half_width": tier.half_width,
        "half_width_projected": [baixo, alto],
        "half_width_within_projection": baixo <= tier.half_width <= alto,
        "unpaired_benchmark": analysis.unpaired_benchmark,
        "pairing_gain": (analysis.unpaired_benchmark / tier.half_width
                         if tier.half_width > 0 else float("nan")),
        "mde": (z_alpha + z_power) * erro_padrao,
        "mde_power": analysis.mde_power,
        "n_users": tier.n_users,
    }
    if test.task == "cat":
        por_classe = estimands.per_class_delta(frame_a, frame_b)
        saida["per_class"] = por_classe
        saida["min_users_per_class"] = min((linha["users"] for linha in por_classe
                                            if linha["users"] > 0), default=0)
    elif train_labels is not None:
        saida["region"] = {test.arm_a: estimands.region_report(frame_a, train_labels[test.arm_a]),
                           test.arm_b: estimands.region_report(frame_b, train_labels[test.arm_b])}
    return saida


def _corrigir(ps: dict[str, float], correction: str,
              alpha: float) -> tuple[dict[str, float], dict[str, float]]:
    """Os p ajustados e o α LOCAL de cada cadeia.

    O α local vem da POSIÇÃO no step-down — α/(m−rank) — e não da razão `ajustado/bruto`. A razão
    parece equivalente e não é em duas bordas: com `bruto` zero ela devolve multiplicador 1 e dá α
    cheio à cadeia que o Holm rejeitou a α/2, e quando o máximo cumulativo do Holm morde (p muito
    próximos) ela cai entre α/2 e α, que não é nível de teste nenhum.

    A superioridade herda este α: a sequência fixa dentro da cadeia não gasta α novo (§3).
    """
    if correction != "holm":
        return dict(ps), {label: alpha for label in ps}

    ajustados = dict(zip(*(lambda a: (a.labels, a.adjusted))(multiplicity.holm(ps, alpha=alpha))))
    m = len(ps)
    ordem = sorted(ps, key=lambda label: ps[label])
    locais = {label: alpha / (m - rank) for rank, label in enumerate(ordem)}
    return ajustados, locais


def _verdict_under(tiers: dict[float, compare_mod.TierA], delta: float, p_ni_adjusted: float,
                   alpha_local: float, alpha: float) -> str:
    """O veredito da cadeia depois de Holm.

    A NI passa a ser decidida pelo p AJUSTADO — é o que a correção significa. O intervalo continua
    sendo o de 90% e continua sendo reportado: ele carrega o tamanho do efeito, que a correção não
    move. A superioridade herda o α local da cadeia.
    """
    bruto = compare_mod.registered_verdict(tiers, delta)
    if p_ni_adjusted > alpha:
        return "inferior" if bruto.verdict == "inferior" else "inconclusive"
    if bruto.verdict != "superior":
        return bruto.verdict
    p = tiers[compare_mod.NI_LEVEL].p_permutation
    return "superior" if (p is not None and p <= alpha_local) else "non_inferior"


def _co_primary(leituras: list[TaskReading], delta: float) -> tuple[str, str]:
    """§3: "reg NI ∧ cat superior-or-NI at the same checkpoint contract", cada componente a α cheio.

    Interseção-união, então SEM Holm — os vereditos marginais não-ajustados são os componentes
    (Berger 1982). Uma reivindicação conjuntiva não paga multiplicidade: exigir as duas ao mesmo
    tempo já é mais difícil que exigir uma.
    """
    por_tarefa = {r.task: r for r in leituras}
    if not {"cat", "reg"} <= set(por_tarefa):
        return "not_applicable", "a família não tem as duas tarefas"

    reg, cat = por_tarefa["reg"].marginal, por_tarefa["cat"].marginal
    reg_ok = reg.verdict in ("superior", "non_inferior")
    cat_ok = cat.verdict in ("superior", "non_inferior")
    if reg_ok and cat_ok:
        return "held", f"reg {reg.verdict} ∧ cat {cat.verdict}, ambos a α cheio"
    faltou = [f"reg {reg.verdict}"] if not reg_ok else []
    faltou += [f"cat {cat.verdict}"] if not cat_ok else []
    return "not_held", " e ".join(faltou)


__all__ = ["ALPHA", "TaskReading", "StateReading", "read_state"]
