"""`--confirmatory` reproduz o que já foi lido, e recusa a primeira leitura.

O desenho existe porque duas situações estavam sendo tratadas como uma:

* **primeira leitura** de um par (receita, conjunto) — o ato racionado, que gasta;
* **reprodução** de um par já lido e publicado — não gasta, porque o número já é fato público.

Sem a distinção, ou se nega o número a quem só quer reproduzir (e ele cita a validação interna por
engano), ou se abre a leitura para todo mundo (e a primeira execução acidental gasta o conjunto).
"""

from __future__ import annotations

import json

import pytest

from mtlcheck.eval import ledger


def test_o_livro_so_contem_conjuntos_que_foram_mesmo_lidos() -> None:
    """Antes de 2026-08-24 este teste exigia livro VAZIO, e isso era proxy do invariante de verdade.

    A ponte foi lida naquele dia, então "vazio" deixou de ser verificável — mas o que ele protegia
    continua sendo: um par no livro declara o teste externo daquele conjunto como GASTO. Pré-registrar
    um par que ninguém leu declara gasto o que não foi, e libera `train --confirmatory` sobre um
    conjunto virgem. A forma que sobrevive à primeira leitura é esta: o livro só pode nomear conjuntos
    cuja leitura aconteceu, e os três grandes ainda não aconteceram.
    """
    from mtlcheck import paths

    # A LISTA FIXA era proxy, e envelheceu: até 26-08 só AL/AZ/IST tinham sido lidos, e em 27-08 os
    # seis foram. O invariante que ela aproximava é este — todo conjunto que o livro nomeia tem de
    # ter um payload de leitura em disco. Pré-registrar um par que ninguém leu declara gasto um
    # conjunto virgem e libera `train --confirmatory` sobre ele.
    lidos = {r.state for r in ledger.load()}
    com_payload = {json.loads(p.read_text())["state"]
                   for p in (paths.repo_root() / "studies").glob("**/leitura/*.json")}
    sem_evidencia = sorted(lidos - com_payload)
    assert not sem_evidencia, (
        f"o livro nomeia {sem_evidencia}, e não há payload de leitura para eles. Um par "
        f"pré-registrado declara gasto um conjunto virgem e libera a leitura dele.")


def test_an_unread_pair_is_not_found(tmp_path) -> None:
    assert ledger.was_read("f" * 16, "texas", root=tmp_path) is None


def test_recording_then_finding(tmp_path) -> None:
    ledger.record("f" * 16, "texas", study="e", recipe="r.toml", arms=("cat",), root=tmp_path)
    found = ledger.was_read("f" * 16, "texas", root=tmp_path)
    assert found is not None and found.state == "texas"


def test_recording_is_idempotent_per_pair(tmp_path) -> None:
    """Um segundo `compare` do MESMO estudo não cria entrada nova — mas outro estudo cria.

    ⚠ Revertido em 25-08. A versão anterior deste teste engolia a segunda leitura em qualquer caso,
    com o argumento de que contá-la duas vezes "faria o livro mentir sobre quantas vezes o conjunto
    foi visto". É o contrário: se foram dois eventos, quem mente é contar um.

    O que forçou a revisão foi concreto. As células `(0,0)` da campanha `v19_ladder` resolvem para o
    mesmo `science_fingerprint` das da campanha da ponte — a receita de TREINO não mudou — e o livro
    já registra esses seis pares como lidos em 24-08. Com a chave antiga, a leitura confirmatória
    nova NÃO entraria: o livro afirmaria para sempre que foram lidos pela ponte, e uma reconciliação
    acharia 30 registros onde a campanha teve 36 células.

    A idempotência que interessava — re-rodar o mesmo `compare` e não duplicar — continua valendo,
    e é a de dentro do estudo.
    """
    primeiro = ledger.record("a" * 16, "florida", study="e", recipe="r", arms=(), root=tmp_path,
                             on="2026-08-21")
    repetido = ledger.record("a" * 16, "florida", study="e", recipe="r", arms=(), root=tmp_path,
                             on="2026-09-01")
    assert repetido.on == primeiro.on == "2026-08-21"
    assert len(ledger.load(tmp_path)) == 1

    outro = ledger.record("a" * 16, "florida", study="OUTRO", recipe="r", arms=(), root=tmp_path,
                          on="2026-09-01")
    assert outro.on == "2026-09-01"
    assert len(ledger.load(tmp_path)) == 2, "segunda olhada nos mesmos usuários é um EVENTO"


def test_a_different_recipe_on_a_read_state_is_a_NEW_pair(tmp_path) -> None:
    """A peça que o desenho anterior não tinha.

    Uma receita congelada rodando num conjunto já lido POR OUTRA RECEITA é primeira leitura, não
    reprodução — o número daquele par nunca existiu. Se o par fosse só o conjunto, alguém apontaria
    uma v21 para um estado lido na v19 e obteria leitura nova sem `compare`.
    """
    ledger.record("v19fingerprint00", "texas", study="e", recipe="v19", arms=(), root=tmp_path)
    assert ledger.was_read("v19fingerprint00", "texas", root=tmp_path) is not None
    assert ledger.was_read("v21fingerprint00", "texas", root=tmp_path) is None


def test_the_state_matters_too(tmp_path) -> None:
    """Mesma receita, conjunto nunca lido: primeira leitura."""
    ledger.record("f" * 16, "alabama", study="e", recipe="r", arms=(), root=tmp_path)
    assert ledger.was_read("f" * 16, "texas", root=tmp_path) is None


def test_the_refusal_names_what_to_do(tmp_path, monkeypatch) -> None:
    """Recusar sem instruir empurra para o contorno errado."""
    import logging

    from mtlcheck import cli
    from mtlcheck.config import load_recipe

    monkeypatch.setattr(ledger, "was_read", lambda *a, **k: None)
    resolved = load_recipe("recipes/v19/cat.toml", state="texas", seed=0, split_seed=0)
    with pytest.raises(SystemExit) as excinfo:
        cli._assert_reproduction_not_first_read(resolved, logging.getLogger("t"))
    message = str(excinfo.value)
    assert "PRIMEIRA leitura" in message
    assert "compare" in message and "sem o flag" in message


def test_a_known_pair_passes(tmp_path, monkeypatch) -> None:
    """O contrapeso: se recusasse sempre, o teste acima passaria com uma implementação inútil."""
    import logging

    from mtlcheck import cli
    from mtlcheck.config import load_recipe

    resolved = load_recipe("recipes/v19/cat.toml", state="texas", seed=0, split_seed=0)
    monkeypatch.setattr(ledger, "was_read", lambda *a, **k: ledger.Read(
        fingerprint="x", state="texas", study="e", on="2026-08-21", recipe="r", arms=()))
    cli._assert_reproduction_not_first_read(resolved, logging.getLogger("t"))   # não levanta
