"""A escada de escalada: quantas execuções este conjunto precisa, decidido pelo próprio conjunto.

Substitui a ponte. A ponte media a dispersão em três conjuntos pequenos e a transferia para calibrar
os grandes; media o regime errado, dava ao menor conjunto veto sobre o maior, e não tem precedente
publicado em ML (protocolo §12.10). Aqui cada conjunto mede a si mesmo.

## A unidade é a EXECUÇÃO, não a semente

Uma execução é um par `(split_seed, model_seed)` — **os dois sorteados juntos**. Não se repete uma
semente de modelo entre partições: isso cravaria o desvio daquele sorteio na média, onde ele nunca se
dissolveria ao crescer P, e o esconderia da dispersão observada. Com os dois botões frescos, as P
execuções são i.i.d. e a dispersão entre elas é exatamente o que o estimando marginal precisa.

⚠ Isto **é** o desenho que o `NOMENCLATURE.md` §1 chama de confundido — partição e inicialização
movendo juntas. O confundimento é fatal para ATRIBUIR variância a um dos eixos e inofensivo para
estimar o efeito MARGINAL, que é o que a manchete afirma. O que estava errado no sistema legado era a
contabilidade (um campo para dois fatores) e o rótulo da análise, não a randomização.

## Por que a escada só cresce em partições

Com orçamento fixo `N = P·S`, a variância da média é `σ²_P/P + σ²_S/(P·S)`. O segundo termo vale
`σ²_S/N` — depende só de N, indiferente a como se fatia. O primeiro só encolhe adicionando
PARTIÇÕES. Logo `P=N, S=1` domina fracamente para qualquer razão entre as componentes, inclusive
`σ_P = 0`.

A exceção seria custo fixo por partição: a alocação ótima de amostragem em dois estágios dá
`S* ≈ sqrt((custo_partição/custo_fit) · (σ²_S/σ²_P))`. Aqui uma partição nova custa o mesmo que um
fit — o substrato não depende dela — então `S = 1`. A fórmula fica registrada em vez da conclusão:
se algum dia um artefato caro passar a depender da partição, a regra se recalcula sozinha.

## Por que o piso nunca licencia parar

O gate usa o limite superior de confiança do desvio, não o ponto (Browne 1995): dimensionar pela
estimativa pontual de um piloto subdimensiona com probabilidade alta. Com 1 grau de liberdade o
fator é 3,95×, o que na prática já inviabiliza a parada em P=2 — mas não a impede: com dispersão
observada exatamente zero o fator multiplica zero. Por isso o piso é fechado por uma regra
EXPLÍCITA (`GL_MINIMO`), a mesma que o protocolo já registra para bandas ("nenhuma abaixo de três"),
estendida ao eixo de execução. Duas execuções idênticas não provam dispersão baixa; provam uma
amostra de um grau de liberdade.

## O que este módulo NÃO decide

Ele decide **quantas execuções existem antes da leitura**. O intervalo publicado sai dos deltas
EXTERNOS por execução, com os graus de liberdade do P final, dentro da leitura única. Por isso a
premissa "a dispersão interna prediz a externa" não é portante: se ela subestimar, escala-se de menos
e o intervalo final sai mais largo; se superestimar, gasta-se GPU à toa. **Os dois modos de falha
custam orçamento, nunca a alegação** — que é o que dispensa o gasto de α na adaptação por parâmetro
de perturbação (Kieser & Friede 2000; FDA 2019).
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

#: Fator do limite superior de confiança unilateral de 80 % para o desvio, por graus de liberdade
#: (Browne 1995). Tabelado em vez de calculado para que a regra seja legível num diff — e porque a
#: alternativa exige scipy num caminho que roda dentro da wave.
UCL80 = {1: 3.9472, 2: 2.1169, 3: 1.7276, 4: 1.5576, 5: 1.461,
         6: 1.398, 7: 1.3533, 8: 1.3197, 9: 1.2934, 10: 1.2721}

#: t de Student bilateral a 95 %, por graus de liberdade. O `stats.py` já carrega esta tabela pelo
#: mesmo motivo; aqui ela indexa execuções em vez de réplicas.
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
       7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}

#: Os degraus, em número de execuções. O piso é 2 e o teto é 6; além disso o desfecho honesto é
#: "partition-limited nesta margem", não mais GPU.
ESCADA = (2, 3, 4, 6)

#: Graus de liberdade mínimos para que uma parada seja licenciada. É a guarda que o protocolo já
#: registra para bandas ("nenhuma abaixo de três"), estendida ao eixo de execução — e ela é
#: ESTRUTURAL, não emergente da aritmética: com dispersão observada exatamente zero, o fator de
#: Browne multiplica zero e a projeção caberia na margem. Duas execuções idênticas não provam
#: dispersão baixa; provam uma amostra de um grau de liberdade.
GL_MINIMO = 2


@dataclass(frozen=True)
class Degrau:
    """O veredito da escada para um conjunto × tarefa."""

    execucoes: int
    #: Desvio observado entre as execuções, na validação interna.
    sd: float
    #: O desvio inflado pelo limite superior — é ele que decide, não o `sd`.
    sd_ucl: float
    #: Meia-largura projetada do intervalo da média, `t · sd_ucl / √P`.
    meia_largura: float
    margem: float
    #: `None` quando a escada acabou: aí o desfecho é o carimbo, não mais execuções.
    proximo: int | None

    @property
    def para(self) -> bool:
        return self.proximo is None and self.meia_largura < self.margem

    @property
    def limitado(self) -> bool:
        """Chegou ao teto e ainda não resolve — o carimbo, e ele não é um quinto veredito."""
        return self.proximo is None and self.meia_largura >= self.margem

    def describe(self) -> str:
        if self.para:
            fim = "PARA"
        elif self.limitado:
            fim = "TETO — partition-limited nesta margem"
        else:
            fim = f"escala para P={self.proximo}"
        return (f"P={self.execucoes} · sd={self.sd:.4f} → UCL80 {self.sd_ucl:.4f} · "
                f"meia-largura {self.meia_largura:.4f} contra δ={self.margem} · {fim}")


def sd_maximo(execucoes: int, *, margem: float) -> float:
    """O maior desvio observado que ainda RESOLVE neste degrau.

    É a condição de parada resolvida para σ̂ em vez de para a meia-largura, e serve para responder
    antes de gastar GPU: "com a dispersão que esta máquina consegue medir, algum degrau é
    alcançável?" Em 25-08 a resposta era não para P=3 e ninguém tinha perguntado.
    """
    gl = execucoes - 1
    if gl not in UCL80 or gl not in T95:
        raise ValueError(f"{execucoes} execuções: {gl} graus de liberdade fora das tabelas")
    return margem * math.sqrt(execucoes) / (T95[gl] * UCL80[gl])


def avalia(deltas: list[float], *, margem: float, escada: tuple[int, ...] = ESCADA) -> Degrau:
    """O degrau seguinte, a partir dos deltas por execução medidos na validação interna.

    `deltas` é um delta pareado (joint − dedicado) por execução — uma execução, um número.

    Com duas execuções há 1 grau de liberdade, e `GL_MINIMO` fecha a parada ali: o piso é triagem.
    O fator de Browne já a inviabiliza na prática, mas não com dispersão observada zero — e uma
    regra que depende de "isso não acontece" não é uma regra.
    """
    p = len(deltas)
    if p < 2:
        raise ValueError(f"a escada precisa de pelo menos duas execuções; recebeu {p}")
    if margem <= 0:
        raise ValueError(f"margem tem de ser positiva; recebeu {margem}")

    gl = p - 1
    sd = statistics.stdev(deltas)
    if gl not in UCL80 or gl not in T95:
        # Recuar para 1,0 e 1,96 seria voltar à estimativa pontual que Browne proíbe, em silêncio, e
        # a um multiplicador normal onde o t é maior. Anticonservador nos dois eixos.
        raise ValueError(f"a escada não tem fatores tabelados para {gl} graus de liberdade "
                         f"(tabelados: {sorted(UCL80)}); estenda as tabelas antes de usar {p} "
                         f"execuções")
    sd_ucl = sd * UCL80[gl]
    meia = T95[gl] * sd_ucl / math.sqrt(p)
    acima = [n for n in escada if n > p]
    resolve = meia < margem and gl >= GL_MINIMO
    return Degrau(execucoes=p, sd=sd, sd_ucl=sd_ucl, meia_largura=meia, margem=margem,
                  proximo=(None if resolve or not acima else acima[0]))


def sementes(execucoes: int, *, base: int = 0) -> list[tuple[int, int]]:
    """Os pares `(split_seed, model_seed)` de uma escada de N execuções.

    Os dois botões andam juntos e nenhum valor se repete entre execuções — repetir uma semente de
    modelo entre partições cravaria o desvio daquele sorteio na média e o esconderia da dispersão.
    A sequência é determinística para que um manifesto seja reproduzível a partir do número.
    """
    if execucoes < 1:
        raise ValueError(f"execuções tem de ser ≥ 1; recebeu {execucoes}")
    # 42 NÃO entra. O §10.1 tirou o congelamento da partição de 42 justamente por ser o sorteio
    # de DESENVOLVIMENTO -- as receitas foram afinadas nele, e o overshoot de +3/+8 pp em CA/TX
    # é o sintoma confundido. No teto ele valeria 1/6 da média confirmatória.
    valores = [0, 7, 1, 100, 13, 3, 21, 5, 77, 11]
    if execucoes > len(valores):
        raise ValueError(f"a escada não vai além de {len(valores)} execuções sem valores novos")
    return [(v + base, v + base) for v in valores[:execucoes]]


__all__ = ["Degrau", "avalia", "sementes", "ESCADA", "UCL80", "T95"]
