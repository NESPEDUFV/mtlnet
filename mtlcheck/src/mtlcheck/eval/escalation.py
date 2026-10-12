"""Os gates de S=2 do §2 — se duas réplicas bastam nos estados grandes.

FL/CA/TX rodaram com 2 sementes e AL/AZ/IST com 4, e a economia foi licenciada por uma promessa: a
banda de réplica medida na ponte governaria os grandes, e três regras mecânicas diriam quando ela
não basta. As regras estavam escritas e não existiam em código.

## Por que isto impõe ordem de leitura

O `sd` calibrado é a banda de réplica dos estados-ponte (§10.3), e ela sai da leitura DELES. Ler os
seis de uma vez torna os gates incomputáveis no momento em que decidem — e depois da leitura já não
há o que decidir. Ponte primeiro não é preferência, é dependência.

## Dois estágios, não um

Um gate que dispara em S=2 **escala** — compra as réplicas que o §7 já orça. Só depois disso um
veredito ainda instável vira "seed-limited at this margin", que o §2 marca como nunca resolvido.
Colapsar os dois abandonaria um veredito que o protocolo mandou comprar.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

from . import compare as compare_mod

#: §2: "|Δ_s0 − Δ_s7| > 3·sd·√2 (~99.7% envelope, known ~0.3% false-trip rate)".
SPREAD_SIGMAS = 3.0
#: §2: o envelope de 2·sd sob o qual uma discordância de sinal não conta.
SIGN_SIGMAS = 2.0


@dataclass(frozen=True)
class Calibration:
    """A banda de réplica medida na ponte, por tarefa."""

    per_state: dict[str, float]
    sd: float
    aggregation: str
    #: A mesma banda sobre um subconjunto de réplicas de fluxo aleatório DISJUNTO, quando a regra de
    #: semente faz duas delas colidirem. Ver `independent_subset`.
    per_state_independent: dict[str, float] = field(default_factory=dict)
    collided: dict[str, tuple[int, ...]] = field(default_factory=dict)

    def describe(self) -> str:
        detalhe = " · ".join(f"{s}={v:.4f}" for s, v in sorted(self.per_state.items()))
        cauda = ""
        if self.collided:
            quais = " · ".join(f"{s}:{list(v)}" for s, v in sorted(self.collided.items()))
            cauda = f" · réplicas de fluxo colidido descartadas em [{quais}]"
        return f"sd={self.sd:.4f} ({self.aggregation} de [{detalhe}]){cauda}"


@dataclass(frozen=True)
class Gates:
    """Os três gates para uma célula de estado grande."""

    state: str
    task: str
    seed_deltas: tuple[float, ...]
    sd: float
    sign_disagreement: bool
    spread_exceeded: bool
    verdict_shifts: bool
    shifted_verdicts: tuple[str, str]
    verdict: str

    @property
    def fired(self) -> bool:
        return self.sign_disagreement or self.spread_exceeded or self.verdict_shifts

    @property
    def outcome(self) -> str:
        """`ok`, `escalate` (comprar as réplicas) ou `seed_limited`.

        Dois estágios, como o §2 escreve: "if it flips, escalate to S=4; if still unstable, report
        'seed-limited at this margin'". Em S=2 um deslocamento que vira o veredito COMPRA as
        sementes que o §7 já orça; `seed_limited` é o desfecho de continuar instável com quatro.
        """
        if not self.fired:
            return "ok"
        if self.verdict_shifts and len(self.seed_deltas) >= 4:
            return "seed_limited"
        return "escalate"

    def describe(self) -> str:
        disparos = [nome for nome, ativo in (("sinal", self.sign_disagreement),
                                             ("dispersão", self.spread_exceeded),
                                             ("veredito", self.verdict_shifts)) if ativo]
        deltas = ", ".join(f"{d:+.4f}" for d in self.seed_deltas)
        cauda = f" · DISPAROU: {', '.join(disparos)}" if disparos else " · ok"
        return (f"  {self.state}/{self.task}: réplicas [{deltas}] contra sd={self.sd:.4f}"
                f"{cauda} → {self.outcome}")


def independent_subset(seeds: tuple[int, ...], folds: int) -> list[int]:
    """Índices de réplicas cujos fluxos aleatórios não se sobrepõem.

    A regra de semente por fold é `seed + fold` (`seeding.fold_seed`), então duas réplicas cujas
    sementes distam menos que o número de folds compartilham fluxo — com 5 folds, as sementes 0 e 1
    treinam 4 dos 5 folds a partir dos MESMOS pesos iniciais. Elas não são réplicas independentes, e
    o desvio entre elas subestima o que deveria medir.

    Guloso pela ordem das sementes: fica a primeira de cada grupo colidido.
    """
    escolhidos: list[int] = []
    ultima: int | None = None
    for i in sorted(range(len(seeds)), key=lambda i: seeds[i]):
        if ultima is None or abs(seeds[i] - ultima) >= folds:
            escolhidos.append(i)
            ultima = seeds[i]
    return escolhidos


def calibrate(bridge: dict[str, tuple[float, ...]], *, aggregation: str = "max",
              seeds: dict[str, tuple[int, ...]] | None = None,
              folds: int | None = None) -> Calibration:
    """A banda de réplica da ponte, para UMA tarefa.

    `bridge` mapeia estado-ponte → deltas por réplica. O desvio é sobre as réplicas dentro de cada
    estado; a agregação entre estados é a escolha que o §2 deixou aberta e que a receita declara.

    Com `seeds` e `folds`, a banda é o MÁXIMO entre o desvio sobre todas as réplicas e o desvio
    sobre um subconjunto de fluxos disjuntos. Réplicas de fluxo colidido subestimam a dispersão, e
    uma banda subestimada faz os gates dispararem menos e a licença de S=2 passar mais fácil — o
    lado errado para errar.
    """
    por_estado, independentes, colididas = {}, {}, {}
    for estado, deltas in bridge.items():
        if len(deltas) >= 2:
            por_estado[estado] = float(statistics.stdev(deltas))
        if seeds is None or folds is None or estado not in seeds:
            continue
        mantidos = independent_subset(seeds[estado], folds)
        if len(mantidos) < len(seeds[estado]):
            colididas[estado] = tuple(s for i, s in enumerate(seeds[estado]) if i not in mantidos)
            if len(mantidos) >= 2:
                independentes[estado] = float(statistics.stdev([deltas[i] for i in mantidos]))

    if not por_estado:
        raise ValueError("nenhum estado-ponte com duas réplicas ou mais; a banda não é estimável")
    escolher = max if aggregation == "max" else (lambda v: float(statistics.fmean(v)))
    sd = escolher(list(por_estado.values()))
    if independentes:
        sd = max(sd, escolher(list(independentes.values())))
    return Calibration(per_state=por_estado, sd=sd, aggregation=aggregation,
                       per_state_independent=independentes, collided=colididas)


def licences_two_replicates(sd: float, *, margin: float, ratio: float) -> tuple[bool, str]:
    """O gate que LICENCIA S=2 (§2), separado dos três que auditam uma célula já lida.

    §2: "S=2 iff calibrated paired seed sd/√2 ≤ ⅓ × min(smallest effect of interest, TOST margin
    slack); otherwise S=4 from the start". O "menor efeito de interesse" não é definido no texto —
    a leitura registrada em §12.4c usa a margem, que é a escala de efeito que um desenho de
    não-inferioridade tem.
    """
    esquerda = sd / math.sqrt(2)
    limite = margin / ratio
    ok = esquerda <= limite
    return ok, (f"sd/√2 = {esquerda:.4f} {'≤' if ok else '>'} δ/{ratio:g} = {limite:.4f}")


def evaluate(*, state: str, task: str, tiers: dict[float, compare_mod.TierA], sd: float,
             margin: float) -> Gates:
    """Os três gates do §2 para uma célula, contra a banda calibrada da ponte."""
    tier = tiers[compare_mod.NI_LEVEL]
    deltas = tuple(tier.seed_deltas)
    if len(deltas) < 2:
        raise ValueError(f"{state}/{task}: {len(deltas)} réplica(s); os gates de S=2 precisam de duas")

    # (i) sinais opostos, e ambos fora do envelope de 2·sd — dois deltas minúsculos de sinais
    # trocados são ruído, não discordância.
    sinais = {d > 0 for d in deltas if abs(d) > SIGN_SIGMAS * sd}
    sign_disagreement = len(sinais) > 1

    # (ii) a dispersão entre réplicas contra o envelope de ~99,7%.
    spread_exceeded = (max(deltas) - min(deltas)) > SPREAD_SIGMAS * sd * math.sqrt(2)

    # (iii) o veredito recomputado com Δ̂ deslocado de ±2·sd/√S.
    passo = SIGN_SIGMAS * sd / math.sqrt(len(deltas))
    base = compare_mod.registered_verdict(tiers, margin).verdict
    deslocados = tuple(compare_mod.registered_verdict(_shift(tiers, sinal * passo), margin).verdict
                       for sinal in (-1.0, 1.0))

    return Gates(state=state, task=task, seed_deltas=deltas, sd=sd,
                 sign_disagreement=sign_disagreement, spread_exceeded=spread_exceeded,
                 verdict_shifts=any(v != base for v in deslocados),
                 shifted_verdicts=deslocados, verdict=base)


def _shift(tiers: dict[float, compare_mod.TierA], by: float) -> dict[float, compare_mod.TierA]:
    """Translada Δ̂ e os intervalos juntos.

    Juntos porque o §2 manda deslocar a ESTIMATIVA: mover o ponto e deixar o intervalo parado
    inventaria um resultado com uma incerteza que não é a dele.
    """
    import dataclasses

    mover = lambda par: (par[0] + by, par[1] + by)
    return {nivel: dataclasses.replace(t, delta=t.delta + by, bca=mover(t.bca),
                                       percentile=mover(t.percentile))
            for nivel, t in tiers.items()}


__all__ = ["Calibration", "Gates", "calibrate", "evaluate", "licences_two_replicates",
           "SIGN_SIGMAS", "SPREAD_SIGMAS"]
