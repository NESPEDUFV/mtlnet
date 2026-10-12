"""Ajuda compartilhada para escrever células de predição em teste.

Existe porque `predictions.write` passou a exigir o contrato do sidecar
(`META_EXTRA_REQUIRED`), e a exigência é o ponto: até 23-08 um teste conseguia escrever uma célula
com `extra={"arm": arm}` e nada mais, o que a tornava mais pobre que qualquer célula de produção — e
foi assim que o caminho quebrado do livro de leituras ficou verde por dias.

O `extra` daqui é o mínimo VÁLIDO. Quem precisa do `extra` REAL, montado pelo mesmo código da
produção, usa `cli._cell_extra` — ver `test_sidecar_contract.py`.
"""

from __future__ import annotations

import pytest

from mtlcheck import paths


def extra_valido(arm: str = "cat", **over) -> dict:
    base = {
        "arm": arm,
        "study": "teste",
        "recipe": f"recipes/v19/{arm}.toml",
        "science_fingerprint": f"{arm[:3]}0000000000000"[:16],
        "lineage": {"produced_by": "wave", "manifest": "waves/teste.toml", "substrate": {}},
    }
    base.update(over)
    return base


@pytest.fixture
def livro_fora_do_repo(tmp_path_factory, monkeypatch):
    """Desvia o livro de leituras para fora da árvore.

    Um `compare` confirmatório ESCREVE em `paths.repo_root()/studies/READ_LEDGER.json`. Sem o
    desvio, a suíte declararia gasta — num arquivo versionado — uma leitura do teste externo que
    nunca aconteceu.
    """
    falso = tmp_path_factory.mktemp("repo")
    monkeypatch.setattr(paths, "repo_root", lambda: falso)
    return falso
