"""O livro de leituras do teste externo — quais pares (receita, conjunto) já foram lidos.

## O problema que ele resolve

Até 2026-08-21 o número do teste externo só saía do `mtlcheck compare`. Isso protegia a leitura, e
tinha um custo real: quem rodava um modelo recebia o número de **validação interna**, que o §8 do
guia diz para nunca citar. O default entregava algo com cara de resultado que não era.

A saída não é abrir a leitura para todo mundo. É notar que **duas situações diferentes** estavam
sendo tratadas como uma:

* **primeira leitura** de um par (receita, conjunto) — o ato racionado, que gasta;
* **reprodução** de um par já lido e publicado — não gasta nada, porque o número já é fato público.

Este módulo é a memória que distingue as duas. Sem ela, a distinção mora na cabeça de quem roda, que
é onde ela não sobrevive.

## O que conta como "o mesmo par"

A **identidade científica da receita** (`Resolved.science_fingerprint()`) mais o conjunto. Telemetria
não entra — ligar a sonda de gradiente não cria um par novo. Mas trocar substrato, cabeça, taxa de
aprendizado ou família **cria**, e é o comportamento que se quer: uma receita diferente rodando num
conjunto já lido é **primeira leitura**, não reprodução.

## Por que ele nasce vazio, e por que isso está certo

Nenhum `compare` rodou ainda sob este protocolo. Pré-registrar pares como "já lidos" para poupar
trabalho seria declarar gasto o que não foi — e, pior, liberaria a leitura de conjuntos que nunca
foram lidos. O livro só cresce quando um `compare` confirmatório de fato acontece.

## ⚠ O que "ausente do livro" NÃO significa

**Não significa "nunca lido".** O livro passou a existir em 2026-08-21. A primeira leitura selada
aconteceu em **2026-08-18** — alabama, arizona e istanbul, sob receitas v18
(`studies/porting_validation/SEALED_BRIDGE_READ.md`) — e **não está aqui**, porque aquelas células
antecedem o campo `science_fingerprint` e registrá-las exigiria inventar a identidade que elas não
gravaram.

Isso é uma lacuna declarada, não um descuido: preencher o livro com identidades reconstruídas
tornaria a reprodução livre para pares que talvez não sejam os que foram lidos. A recusa do
`--confirmatory` aponta para o documento da leitura, e quem for tratar um daqueles três como "nunca
lido" tem de conferir lá primeiro.

## O que ele NÃO é

Não é uma proteção criptográfica. O arquivo é editável e o `git` é a única loja à prova de
adulteração que este projeto tem — por isso ele vive versionado, e uma leitura aparece como um commit
datado. A garantia é auditabilidade, não impossibilidade.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

#: Versionado de propósito: uma leitura tem de aparecer como um commit datado.
LEDGER = Path("studies/READ_LEDGER.json")


@dataclass(frozen=True)
class Read:
    """Uma leitura do teste externo, já ocorrida."""

    fingerprint: str        # science_fingerprint da receita lida
    state: str
    study: str
    on: str                 # ISO date
    recipe: str             # o caminho, para humanos — a identidade é o fingerprint
    arms: tuple[str, ...]

    def key(self) -> tuple[str, str, str]:
        """A chave do EVENTO. Inclui o estudo, e a inclusão é o conserto.

        Sem ela, uma campanha nova cuja receita de treino não mudou colide com a antiga: as células
        `(0,0)` da `v19_ladder` resolvem para o mesmo `science_fingerprint` das da campanha da ponte,
        que o livro registra como lidas em 24-08. O `record` era idempotente por `(fingerprint,
        state)`, então a leitura nova NÃO entraria -- o livro afirmaria para sempre que aqueles seis
        pares foram lidos pela ponte, e uma reconciliação acharia 30 registros onde houve 36 células.
        Verificado em 25-08 nos seis pares de AL e IST.
        """
        return (self.fingerprint, self.state, self.study)


def _path(root: Path | None = None) -> Path:
    from .. import paths
    return (root or paths.repo_root()) / LEDGER


def load(root: Path | None = None) -> list[Read]:
    path = _path(root)
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return [Read(fingerprint=r["fingerprint"], state=r["state"], study=r["study"],
                 on=r["on"], recipe=r["recipe"], arms=tuple(r.get("arms", ())))
            for r in payload.get("reads", [])]


def was_read(fingerprint: str, state: str, *, study: str | None = None,
             root: Path | None = None) -> Read | None:
    """A leitura registrada para este par, ou None. `None` significa PRIMEIRA leitura.

    Sem `study` a pergunta é a CIENTÍFICA -- "o teste externo deste estado já foi olhado sob esta
    receita, por quem quer que seja?" -- e é ela que governa as guardas. Com `study`, a pergunta é a
    contábil: "este evento já está no livro?", que é o que o `record` precisa para não engolir uma
    leitura nova como se fosse a antiga.
    """
    for entry in load(root):
        if entry.fingerprint == fingerprint and entry.state == state:
            if study is None or entry.study == study:
                return entry
    return None


def record(fingerprint: str, state: str, *, study: str, recipe: str,
           arms: tuple[str, ...], root: Path | None = None, on: str | None = None) -> Read:
    """Registra uma leitura que ACABOU de acontecer. Idempotente por par.

    Chamado pelo `compare`, nunca pelo `train`: quem gasta a leitura é quem lê, e registrar antes de
    ler seria declarar gasto o que não foi.
    """
    existing = was_read(fingerprint, state, study=study, root=root)
    anterior = was_read(fingerprint, state, root=root)
    if existing is None and anterior is not None:
        # Mesmo par, OUTRO estudo: é uma leitura nova do mesmo teste externo, e o livro tem de ter
        # as duas. Registrar, e dizer -- porque "segunda olhada" é uma ressalva que o relatório
        # precisa carregar, e ela some se o livro esconder o evento.
        logger.warning(
            "(%s, %s) já foi lido em %s pelo estudo %s. Este é um evento NOVO e vai para o livro; "
            "quem reportar %s tem de declarar que é segunda olhada nos mesmos usuários.",
            fingerprint[:12], state, anterior.on, anterior.study, state)
    if existing is not None:
        logger.info("leitura de (%s, %s) já registrada em %s", fingerprint[:12], state, existing.on)
        return existing

    entry = Read(fingerprint=fingerprint, state=state, study=study,
                 on=on or date.today().isoformat(), recipe=recipe, arms=tuple(arms))
    path = _path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = json.loads(path.read_text()) if path.exists() else {
        "_": ("Quais pares (receita, conjunto) já tiveram o teste externo lido. Um par aqui pode ser "
              "reproduzido à vontade (`train --confirmatory`); um par ausente exige um `compare`, "
              "que é o ato racionado. Ver eval/ledger.py."),
        "reads": [],
    }
    payload["reads"].append({"fingerprint": entry.fingerprint, "state": entry.state,
                             "study": entry.study, "on": entry.on, "recipe": entry.recipe,
                             "arms": list(entry.arms)})
    path.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    logger.warning("LEITURA REGISTRADA: (%s, %s) em %s — o teste externo deste par está gasto",
                   entry.fingerprint[:12], state, entry.on)
    return entry


__all__ = ["Read", "load", "was_read", "record", "LEDGER"]
