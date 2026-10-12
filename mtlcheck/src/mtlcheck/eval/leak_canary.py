"""§1 — o canário de vazamento, que era código morto.

## O que a regra diz, literal

> `ood_hit_rate = (raw − full)/ood_fraction`. The last is a **leak canary**, not a courtesy: a
> never-trained output unit essentially cannot rank top-10 of 1,109–8,501 classes, so
> `ood_hit_rate > 1%` **fails the run** (this guards the stale-log_T failure class already
> documented at +8–12 pp).

"Fails the run" — recusa, não rebaixamento. É diferente do piso de re-execução e do gate de
permutação, que são regras de *reivindicação* e vivem no `equivalence()`.

## Por que ele não estava valendo

Três coisas somadas, cada uma inócua sozinha:

1. `estimands.ood_diagnostics` tinha **um** chamador: o próprio teste.
2. `compare._align_one` chama `region_counts(frame, k=k)` **sem** `train_labels`, então os arrays de
   OOD saem zerados na origem.
3. `_Aligned.metric` reconstrói `RegionCounts` com `np.zeros_like` nos dois campos de OOD.

Resultado: o caminho de comparação **não conseguia ver OOD nem se quisesse**. Reproduzido com
vazamento de 100 %: `warnings = []` e veredito SUPERIOR.

## Por fold, nunca agrupado

Os `train_labels` são bancados por `(tarefa, fold)` justamente porque o conjunto de treino difere
entre folds. Agrupar os folds sob a UNIÃO dos rótulos de treino **subestima** o OOD: um rótulo
ausente do fold 2 mas presente no fold 3 deixaria de contar como fora de distribuição no fold 2.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

#: §1: `ood_hit_rate > 1%` reprova a execução.
OOD_HIT_RATE_LIMIT = 0.01


class LeakCanaryFired(RuntimeError):
    """O canário disparou. A execução não é válida sob o protocolo — §1, pré-registrado."""


@dataclass(frozen=True)
class FoldCanary:
    arm: str
    state: str
    fold: int
    ood_fraction: float
    ood_hit_rate: float
    n_windows: int

    @property
    def fired(self) -> bool:
        return self.ood_hit_rate > OOD_HIT_RATE_LIMIT

    def describe(self) -> str:
        marca = "DISPAROU" if self.fired else "ok"
        return (f"{self.arm}/{self.state}/fold{self.fold}: ood_fraction={self.ood_fraction:.4f} "
                f"ood_hit_rate={self.ood_hit_rate:.4f} ({marca})")


def per_fold(frame, meta: dict[str, Any], *, task: str = "reg", k: int = 10,
             strict: bool = False) -> list[FoldCanary]:
    """Um canário por fold, com os `train_labels` DAQUELE fold.

    `strict` recusa o fold que não pode ser avaliado, em vez de pulá-lo. O §1 diz "fails the run", e
    um fold sem `train_labels` não é um canário que passou — é um canário que não foi ligado. Sob
    leitura confirmatória, um aviso num log é indistinguível de um canário silencioso.
    """
    from . import estimands

    rotulos = meta.get("train_labels") or {}
    saida: list[FoldCanary] = []
    for fold in sorted(frame["fold"].unique().tolist()):
        chave = f"{task}/{fold}"
        if chave not in rotulos:
            if strict:
                raise LeakCanaryFired(
                    f"{meta.get('arm')}/{meta.get('state')}: sem train_labels bancados para "
                    f"{chave}, então o canário do §1 NÃO PODE ser avaliado neste fold. Um canário "
                    f"que não roda não é um canário que passou.")
            logger.warning("%s/%s: sem train_labels bancados para %s — o canário não pode ser "
                           "avaliado neste fold", meta.get("arm"), meta.get("state"), chave)
            continue
        sub = frame[(frame["fold"] == fold) & (frame["task"] == task)]
        if sub.empty:
            continue
        contagens = estimands.region_counts(sub, k=k, train_labels=frozenset(rotulos[chave]))
        d = estimands.ood_diagnostics(contagens)
        saida.append(FoldCanary(
            arm=str(meta.get("arm")), state=str(meta.get("state")), fold=int(fold),
            ood_fraction=d["ood_fraction"], ood_hit_rate=d["ood_hit_rate"],
            n_windows=int(d["n_windows"])))
    return saida


def assert_no_leak(canarios: list[FoldCanary], *, confirmatory: bool = True) -> None:
    """Recusa se algum fold estourar o limite. §1 pré-comprometeu a consequência ANTES do lacre.

    `confirmatory=False` degrada para aviso, pela mesma razão que existe no `assert_comparable`:
    leitura exploratória continua possível, e dizê-lo é como se assume a responsabilidade. O que
    não é possível é ler como confirmatório sem passar por aqui.
    """
    disparados = [c for c in canarios if c.fired]
    if not disparados:
        return
    detalhe = "\n  ".join(c.describe() for c in disparados)
    mensagem = (
        f"o canário de vazamento do §1 disparou em {len(disparados)} de {len(canarios)} folds "
        f"(limite ood_hit_rate = {OOD_HIT_RATE_LIMIT:.0%}):\n  {detalhe}\n"
        f"Uma unidade de saída nunca treinada essencialmente não consegue ranquear no top-10 de "
        f"1 109 a 8 501 classes, então uma taxa não-trivial significa que informação sobre o rótulo "
        f"retido alcançou o modelo. §1 pré-registrou 'fails the run' ANTES do lacre.")
    if confirmatory:
        raise LeakCanaryFired(mensagem)
    logger.warning("%s Lendo como EXPLORATÓRIO.", mensagem)


__all__ = ["FoldCanary", "LeakCanaryFired", "OOD_HIT_RATE_LIMIT", "per_fold", "assert_no_leak"]
