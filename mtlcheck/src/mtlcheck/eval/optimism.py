"""§8a — quanto da diferença medida é otimismo de seleção, e quanto é custo de um checkpoint único.

## O que este módulo responde, e por que ele deixou de ser opcional

A primeira leitura selada mediu Δ = joint − dedicado e registrou que o número **não é decomponível**
com o que estava bancado (`SEALED_BRIDGE_READ.md` §2):

    Δ medido = (interferência entre tarefas) + (custo de se comprometer com um checkpoint único)

O braço dedicado é avaliado na época que a validação interna daquela tarefa escolheu; o braço joint,
na única época que o `geom_simple` escolheu. Os dois termos vivem juntos no mesmo número, e o §8a do
protocolo diz que a assimetria **corre contra o joint**. Enquanto não forem separados, a frase
defensável é "o checkpoint joint único entrega X pp a menos que dois dedicados, cada um no seu
melhor" — e **não** "a MTL custa X pp".

## Os três estimadores, co-registrados na MESMA trajetória

Todos saem do mesmo fold, da mesma semente, da mesma execução — é isso que faz a variância de fold
(~1,2 pp) e a de semente cancelarem exatamente, em vez de entrarem no erro-padrão.

| | definição | o que é |
|---|---|---|
| **a1** | máximo sobre épocas ≥ 5 do escore no stream retido | a regra LEGADA, por tarefa |
| **b1** | escore na época que a val interna escolheu **para aquela tarefa** | limpo, por tarefa |
| **b2** | escore na única época do `geom_simple` | limpo, checkpoint único |

E as duas diferenças, **reportadas separadamente e nunca somadas**:

* **a1 − b1** = otimismo de seleção-no-teste (o que a regra legada comprava de graça);
* **b1 − b2** = custo de deployability de se comprometer com um checkpoint.

## A quarentena, que é mecânica e não disciplinar

O §8a exige processo separado, sink append-only **fora** do rundir, e recusa a rodar antes de todas
as sementes × folds do estado terminarem. Os três são checados aqui, e o último é o que impede a
utilidade mais óbvia e mais errada: rodar isto no meio de um estudo e olhar.

⚠ **Este módulo NÃO lê o teste externo por conta própria.** Ele pontua o stream que os checkpoints
retidos descrevem. Durante o desenvolvimento isso é a validação interna e não custa nada; num ciclo
confirmatório é o fold externo, e aí a leitura é o ato datado de sempre.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

#: O §8a fixa "épocas ≥ 5" para a1. Não é arbitrário: as primeiras épocas de um OneCycle ainda estão
#: na rampa e o máximo cairia num ponto que nenhuma regra de seleção real escolheria, inflando o
#: otimismo medido por um motivo que não é seleção.
MIN_EPOCH = 5


class QuarantineViolated(RuntimeError):
    """A passagem post-hoc foi pedida antes de ser legítima."""


@dataclass(frozen=True)
class Estimators:
    """a1/b1/b2 de UM (fold, semente, tarefa), no mesmo stream."""

    state: str
    task: str
    fold: int
    seed: int
    a1: float
    b1: float
    b2: float | None          # None numa célula dedicada: não existe seletor conjunto
    a1_epoch: int
    b1_epoch: int
    b2_epoch: int | None
    stream: str

    @property
    def selection_optimism(self) -> float:
        """a1 − b1. O que a regra legada ganhava só por poder escolher olhando o resultado."""
        return self.a1 - self.b1

    @property
    def single_checkpoint_cost(self) -> float | None:
        """b1 − b2. O que custa entregar UM modelo em vez de um por tarefa."""
        return None if self.b2 is None else self.b1 - self.b2

    def to_row(self) -> dict[str, Any]:
        return {
            "state": self.state, "task": self.task, "fold": self.fold, "seed": self.seed,
            "stream": self.stream,
            "a1": self.a1, "b1": self.b1, "b2": self.b2,
            "a1_epoch": self.a1_epoch, "b1_epoch": self.b1_epoch, "b2_epoch": self.b2_epoch,
            "selection_optimism": self.selection_optimism,
            "single_checkpoint_cost": self.single_checkpoint_cost,
        }


def estimators_from_curve(curve: dict[int, float], *, inner_epoch: int,
                          joint_epoch: int | None, state: str, task: str,
                          fold: int, seed: int, stream: str) -> Estimators:
    """Os três estimadores de UMA curva `{época: escore no stream retido}`.

    Separado da leitura de disco de propósito: é a única parte com aritmética, e é onde um teste
    consegue mostrar que a1 ≥ b1 sempre, que b2 usa a época do seletor conjunto e não a da tarefa, e
    que o corte em `MIN_EPOCH` está do lado certo.
    """
    eligible = {e: v for e, v in curve.items() if e >= MIN_EPOCH}
    if not eligible:
        raise ValueError(f"{state}/{task}/fold{fold}/seed{seed}: nenhuma época >= {MIN_EPOCH} na "
                         f"curva (épocas presentes: {sorted(curve)})")
    a1_epoch = max(eligible, key=lambda e: eligible[e])
    if inner_epoch not in curve:
        raise ValueError(f"{state}/{task}/fold{fold}: a val interna escolheu a época {inner_epoch} "
                         f"e ela não foi retida — a1/b1 sairiam de trajetórias diferentes, que é "
                         f"exatamente o que o §8a existe para evitar")
    if joint_epoch is not None and joint_epoch not in curve:
        raise ValueError(f"{state}/{task}/fold{fold}: a época do seletor conjunto ({joint_epoch}) "
                         f"não foi retida")
    return Estimators(
        state=state, task=task, fold=fold, seed=seed, stream=stream,
        a1=eligible[a1_epoch], b1=curve[inner_epoch],
        b2=None if joint_epoch is None else curve[joint_epoch],
        a1_epoch=a1_epoch, b1_epoch=inner_epoch, b2_epoch=joint_epoch,
    )


def assert_quarantine(cells: list[Path], *, expected_seeds: int, expected_folds: int,
                      sink: Path, rundir_root: Path) -> None:
    """As três condições mecânicas do §8a, checadas antes de qualquer escore.

    Nenhuma delas é conselho. A terceira — recusar antes do estado estar completo — é a que impede a
    utilidade mais óbvia e mais errada: rodar no meio de um estudo para dar uma olhada.
    """
    sink, rundir_root = Path(sink).resolve(), Path(rundir_root).resolve()
    if sink == rundir_root or rundir_root in sink.parents:
        raise QuarantineViolated(
            f"o sink {sink} está dentro do rundir {rundir_root}. O §8a exige um destino append-only "
            f"FORA dele, para que a passagem post-hoc não possa ser confundida com um artefato da "
            f"execução nem alcançada pelo caminho de seleção.")

    seen = {(c.name, ) for c in cells}
    if len(cells) < expected_seeds * expected_folds:
        raise QuarantineViolated(
            f"{len(cells)} trajetórias contra as {expected_seeds * expected_folds} esperadas "
            f"({expected_seeds} sementes × {expected_folds} folds). O §8a recusa rodar antes do "
            f"estado estar completo: uma passagem parcial mede o otimismo de um subconjunto "
            f"escolhido por quem terminou primeiro. ({len(seen)} células distintas encontradas)")


def summarise(rows: list[Estimators]) -> dict[str, Any]:
    """Agrega por tarefa, com sementes MEDIADAS DENTRO do fold antes do erro-padrão.

    A ordem importa e o §8a a especifica: n = 5 folds, não 20 células. Tratar semente e fold como
    réplicas independentes divide o erro-padrão por ~2 e produz uma decisão confiante sobre uma
    diferença que os dados não sustentam.
    """
    import statistics as st

    out: dict[str, Any] = {}
    for task in sorted({r.task for r in rows}):
        by_fold: dict[int, list[Estimators]] = {}
        for r in rows:
            if r.task == task:
                by_fold.setdefault(r.fold, []).append(r)
        opt = [st.mean([x.selection_optimism for x in v]) for v in by_fold.values()]
        cost = [st.mean([x.single_checkpoint_cost for x in v])
                for v in by_fold.values() if all(x.single_checkpoint_cost is not None for x in v)]
        entry: dict[str, Any] = {
            "n_folds": len(opt),
            "selection_optimism": {
                "mean": st.mean(opt),
                "stderr": (st.stdev(opt) / len(opt) ** 0.5) if len(opt) > 1 else None,
            },
        }
        if cost:
            entry["single_checkpoint_cost"] = {
                "mean": st.mean(cost),
                "stderr": (st.stdev(cost) / len(cost) ** 0.5) if len(cost) > 1 else None,
            }
        # Nunca somados. O §8a diz isso em texto; aqui fica dito no artefato, para que quem ler o
        # json não precise ter lido o protocolo.
        entry["_"] = ("a1-b1 e b1-b2 medem coisas diferentes e NÃO se somam: a primeira é otimismo "
                      "de seleção, a segunda é custo de entregar um modelo só.")
        out[task] = entry
    return out


def append_to_sink(sink: Path, payload: dict[str, Any]) -> Path:
    """Append-only, uma linha JSON por passagem. Nunca reescreve, nunca trunca."""
    sink = Path(sink)
    sink.parent.mkdir(parents=True, exist_ok=True)
    with sink.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")
    logger.info("§8a: passagem anexada em %s", sink)
    return sink


__all__ = ["Estimators", "QuarantineViolated", "MIN_EPOCH", "estimators_from_curve",
           "assert_quarantine", "summarise", "append_to_sink"]
