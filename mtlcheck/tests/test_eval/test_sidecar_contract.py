"""O contrato do `predictions_meta.json`, verificado sobre o código-fonte.

Existe por um bug concreto: o escritor gravava `config_fingerprint`, o `compare` lia
`science_fingerprint`, e o desencontro não tinha sintoma nenhum — `meta.get` devolvia `None`, o
filtro vinha vazio, e a leitura ÚNICA E IRREVERSÍVEL do teste externo era gasta sem entrar no livro
de leituras. 476 testes passavam.

`predictions.py` já resolvia exatamente este problema para as colunas do parquet: `COLUMNS` é
declarada uma vez e `read()` valida contra ela, "a missing column is an error, never a default". O
sidecar era o único artefato do módulo fora dessa disciplina. Este arquivo fecha o lado que a
validação em `write()`/`read()` não alcança — um LEITOR novo pedindo chave que escritor nenhum
grava, que é como a chave órfã nasceu (o leitor veio depois do escritor).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from mtlcheck.eval import predictions as P

SRC = Path(__file__).resolve().parents[2] / "src" / "mtlcheck"
FONTES = sorted(SRC.rglob("*.py"))

DECLARADAS = (set(P.META_SELF) | set(P.META_SELF_OVERRIDABLE)
              | set(P.META_EXTRA_REQUIRED) | set(P.META_OPTIONAL))


def _e_meta(node: ast.AST) -> bool:
    """`meta` ou `<algo>.meta` — os dois jeitos de chegar no sidecar.

    Casa pelo NOME, então um dicionário não-sidecar chamado `meta` é falso positivo. É o lado certo
    para errar: o falso positivo aparece na hora e custa um rename; o falso negativo é o bug.
    """
    return ((isinstance(node, ast.Name) and node.id == "meta")
            or (isinstance(node, ast.Attribute) and node.attr == "meta"))


def _leituras(tree: ast.AST):
    """Todo `meta.get("k")` e `meta["k"]`, com o nó da chave."""
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and _e_meta(node.func.value) and node.args):
            yield node, node.args[0]
        elif isinstance(node, ast.Subscript) and _e_meta(node.value):
            yield node, node.slice


#: O módulo que DECLARA o contrato precisa iterar sobre ele (`for k in META_EXTRA_REQUIRED`), então
#: chave dinâmica é legítima só ali. Em qualquer outro arquivo ela é um leitor escapando da varredura.
DONO_DO_CONTRATO = SRC / "eval" / "predictions.py"


@pytest.mark.parametrize("path", FONTES, ids=lambda p: str(p.relative_to(SRC)))
def test_toda_chave_lida_do_sidecar_esta_declarada(path: Path) -> None:
    for node, chave in _leituras(ast.parse(path.read_text())):
        if not (isinstance(chave, ast.Constant) and isinstance(chave.value, str)):
            # Um `meta.get(f"{x}_fingerprint")` é exatamente a forma que esta varredura não
            # conseguiria ver, então ela é recusada em vez de ignorada.
            assert path == DONO_DO_CONTRATO, (
                f"{path.name}:{node.lineno} lê o sidecar com uma chave que não é literal — o "
                f"contrato não enxerga isso. Use uma chave literal declarada em predictions.META_*.")
            continue
        assert chave.value in DECLARADAS, (
            f"{path.name}:{node.lineno} lê meta[{chave.value!r}], que escritor nenhum declara.\n"
            f"Se `write()` grava a chave, declare-a em predictions.META_SELF/META_EXTRA_REQUIRED/"
            f"META_OPTIONAL. Se NÃO grava, este é o bug de 23-08 outra vez: o leitor receberia "
            f"None em silêncio no caminho irreversível.")


def test_as_tres_tuplas_do_contrato_nao_se_sobrepoem() -> None:
    """Uma chave em duas tuplas tem dois donos, e a validação de colisão passaria a mentir."""
    tuplas = {"META_SELF": set(P.META_SELF),
              "META_SELF_OVERRIDABLE": set(P.META_SELF_OVERRIDABLE),
              "META_EXTRA_REQUIRED": set(P.META_EXTRA_REQUIRED),
              "META_OPTIONAL": set(P.META_OPTIONAL)}
    for a, chaves_a in tuplas.items():
        for b, chaves_b in tuplas.items():
            if a < b:
                assert not chaves_a & chaves_b, f"{a} e {b} disputam {sorted(chaves_a & chaves_b)}"


def test_o_que_a_producao_grava_cobre_o_que_o_contrato_exige() -> None:
    """`_cell_extra` é o único produtor de `extra` da produção; ele tem de satisfazer o contrato.

    Sem isto, exigir uma chave em `META_EXTRA_REQUIRED` que a produção não grava transformaria todo
    treino num `ValueError` — o contrato tem de descrever a produção, não contradizê-la.
    """
    from types import SimpleNamespace

    from mtlcheck import cli, config as cfg

    resolved = cfg.load_recipe("recipes/v19/cat.toml", state="alabama", seed=0, split_seed=0)
    extra = cli._cell_extra(
        resolved, study="t", arm="cat", eval_stream="inner_val",
        inputs=SimpleNamespace(provenance={}, n_categories=7, n_regions=1109))

    assert not [k for k in P.META_EXTRA_REQUIRED if not extra.get(k)]
    assert not set(extra) & set(P.META_SELF), "a produção sobrescreveria um campo computado"
    assert extra["science_fingerprint"] == resolved.science_fingerprint()
    assert extra["science_fingerprint"] != extra["config_fingerprint"], (
        "as duas identidades têm de ser distinguíveis — confundi-las é o bug original")
