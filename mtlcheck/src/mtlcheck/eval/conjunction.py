"""§4a — a frase cross-state, montada dos payloads que as leituras por estado já produziram.

Post-processing puro: entra p por estado, sai u*. Nenhum parquet é aberto aqui, então rodar isto não
gasta leitura de teste selado nenhuma — o que também significa que ele pode rodar quantas vezes for
preciso depois que os seis estados foram lidos.

## Por que ele é um comando separado

Porque a pergunta é de outra ordem. `compare --state X` responde "o efeito vale em X"; esta camada
responde "em quantos dos seis ele vale", que é a afirmação que a dissertação faz no título. Juntar as
duas num comando só obrigaria a ler os seis estados numa invocação — e o §2 manda ler a ponte
primeiro, calibrar, e só então os grandes.

## O que ela pode e não pode dizer

O §12.6c mediu a dependência entre os conjuntos e ela é grande: 24,5 % dos usuários aparecem em mais
de um estado americano, e nos dois estados-ponte passa de 70 %. **Istanbul é o único conjunto
genuinamente independente.** Isso não invalida leitura nenhuma por estado — cada uma é condicional
aos usuários daquele estado, e o bootstrap reamostra dentro dele — mas é o motivo de o combinador ser
Bonferroni, e de "replicado em seis conjuntos" não ser seis observações independentes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import multiplicity
from .analysis import Analysis

#: Vereditos que contam como "o efeito se sustenta" para cada sub-família do §4a.
SUSTENTA = {"non_inferiority": ("non_inferior", "superior"), "superiority": ("superior",)}


@dataclass(frozen=True)
class Conjunction:
    task: str
    family: str
    combiner: str
    states: tuple[str, ...]
    pvalues: tuple[float, ...]
    #: u*: em quantos conjuntos, no mínimo, o efeito se sustenta.
    u: int
    curve: tuple[float, ...]
    #: Quantos estados atingem o veredito olhando um a um. u* NUNCA passa disto, e a folga entre os
    #: dois é o preço da afirmação conjunta.
    marginal: int

    def describe(self) -> str:
        return (f"  {self.task:3s} {self.family:15s} u* = {self.u}/{len(self.states)} "
                f"(marginal {self.marginal}/{len(self.states)}) · "
                f"p = [{', '.join(f'{v:.4f}' for v in self.curve)}]")


def read_payloads(paths: list[str | Path]) -> list[dict]:
    """Os payloads de `compare --json`, conferidos contra a receita e entre si."""
    lidos = []
    for path in paths:
        payload = json.loads(Path(path).read_text())
        if "tasks" not in payload or "state" not in payload:
            raise ValueError(f"{path} não é um payload de `compare --json`")
        lidos.append(payload)
    if not lidos:
        raise ValueError("nenhum payload; a conjunção parcial precisa dos estados lidos")

    estados = [p["state"] for p in lidos]
    if len(set(estados)) != len(estados):
        raise ValueError(f"o mesmo estado entra duas vezes: {sorted(estados)}. Cada conjunto é UMA "
                         f"observação na conjunção, e repetir um o conta duas vezes.")
    return lidos


def compose(payloads: list[dict], analysis: Analysis, alpha: float = 0.05) -> list[Conjunction]:
    """u* por tarefa e por sub-família, no combinador que a receita declara."""
    _assert_same_analysis(payloads, analysis)
    saida = []
    for test in analysis.tests:
        leituras = [(p["state"], _task(p, test.task, p["state"])) for p in payloads]
        for family, aceitos in SUSTENTA.items():
            ps = [_pvalue(t, family) for _, t in leituras]
            saida.append(Conjunction(
                task=test.task, family=family, combiner=analysis.conjunction,
                states=tuple(s for s, _ in leituras), pvalues=tuple(ps),
                u=multiplicity.largest_u(ps, analysis.conjunction, alpha),
                curve=tuple(multiplicity.curve(ps, analysis.conjunction)),
                marginal=sum(1 for _, t in leituras if t["verdict_marginal"] in aceitos)))
    return saida


def excede_o_marginal(resultados: list[Conjunction]) -> list[Conjunction]:
    """Onde `u*` passou da contagem marginal — o que a docstring de `Conjunction` proíbe.

    Em não-inferioridade isto NUNCA deveria acontecer: o veredito marginal e o p saem do mesmo
    endpoint BCa. Em superioridade pode acontecer por motivo legítimo, porque o §3 exige do veredito
    duas condições que o p não carrega (o piso de re-execução e o IC de 95% excluindo zero) — mas
    então é uma folga que o leitor tem de ver, não uma que o relatório engole.
    """
    return [c for c in resultados if c.u > c.marginal]


def _task(payload: dict, task: str, state: str) -> dict:
    for entry in payload["tasks"]:
        if entry["task"] == task:
            return entry
    raise ValueError(f"{state} não traz a tarefa {task!r}; a conjunção exige o mesmo conjunto de "
                     f"tarefas em todos os estados")


def _pvalue(task: dict, family: str) -> float:
    """O p do estado na direção da sub-família.

    O §4a combina num NULO COMUM, e os dois nulos são DIRECIONAIS: H0_s: δ_s ≤ −δ para a
    não-inferioridade, H0_s: δ_s ≤ 0 para a superioridade. Duas conjunções, não uma.

    ⚠ O p de permutação é **bilateral** (`compare._tier_a`: `abs(flipped/scale) >= abs(observed_t)`),
    então ele responde "Δ ≠ 0?" e não "Δ > 0?". Alimentar a superioridade com ele cru inverte a
    frase: um Δ grande e NEGATIVO dá p minúsculo. Medido em 24-08 sobre os três payloads da ponte —
    região saía `u* = 3/3` com o veredito marginal em `0/3`, sobre conjuntos em que o joint é
    inferior. Daí a conversão pelo sinal do efeito.

    O p BRUTO, não o ajustado por Holm: o §5 põe Holm DENTRO do estado, sobre a família de duas
    tarefas daquele estado. Combinar o ajustado corrigiria duas vezes pelo mesmo motivo.
    """
    if family == "non_inferiority":
        valor = task.get("p_ni")
        if valor is None:
            raise ValueError(f"a tarefa {task['task']!r} não traz p_ni; sem ele a conjunção parcial "
                             f"não tem entrada para este estado")
        return float(valor)

    bilateral = task.get("p_studentized")
    if bilateral is None:
        raise ValueError(f"a tarefa {task['task']!r} não traz p_studentized; sem ele a conjunção "
                         f"parcial não tem entrada para este estado")
    delta = task.get("delta")
    if delta is None:
        raise ValueError(f"a tarefa {task['task']!r} não traz delta; sem o sinal do efeito o p "
                         f"bilateral não vira direcional")
    metade = float(bilateral) / 2.0
    return metade if float(delta) > 0 else 1.0 - metade


def _assert_same_analysis(payloads: list[dict], analysis: Analysis) -> None:
    """Todos os estados foram lidos pela MESMA receita congelada.

    Combinar p de duas receitas produziria um u* sobre margens ou níveis diferentes por conjunto —
    a afirmação "vale em pelo menos u" deixaria de ter um u do quê.
    """
    aceitos = {analysis.fingerprint, *analysis.accepts_bridge_from}
    fingerprints = {p["analysis"]["fingerprint"] for p in payloads}
    if not fingerprints <= aceitos:
        raise ValueError(
            f"os payloads vêm das receitas {sorted(fingerprints)} e esta aceita {sorted(aceitos)}. "
            f"Cada p foi computado contra a margem e os níveis da SUA receita, então combiná-los "
            f"daria um u* sem um u de quê.")
    divergem = sorted(p["state"] for p in payloads
                      if (p["analysis"].get("delta") is not None
                          and p["analysis"]["delta"] != analysis.delta))
    if divergem:
        raise ValueError(f"os conjuntos {divergem} foram lidos contra outra margem; a escada de "
                         f"escalada do §12.7 permite trocar a tabela de compra, não o δ.")
    exploratorios = sorted(p["state"] for p in payloads if not p.get("confirmatory"))
    if exploratorios:
        raise ValueError(f"os estados {exploratorios} foram lidos em modo exploratório; a frase "
                         f"cross-state do §4a é confirmatória e não se monta sobre eles")


__all__ = ["Conjunction", "compose", "read_payloads", "excede_o_marginal", "SUSTENTA"]
