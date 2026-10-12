"""Uma célula que não saiu de uma wave é recusada no CONSUMO, não avisada na criação.

O princípio, que este repositório já tinha descoberto para o lacre e não tinha aplicado à linhagem:
**guarda em tempo de criação é disciplina, e disciplina falha; guarda em tempo de consumo é prova.**
A docstring de `assert_comparable` diz por que — "um aviso é o instrumento errado… uma linha de log
passa batido; isto não".

O que motivou: em 2026-08-19 uma campanha de medição inteira rodou de scripts de shell FORA do
repositório. O `test_studies_contract.py` não pegou porque ele guarda o conteúdo de `studies/`, e um
driver fora do repo não é conteúdo de lugar nenhum. Só apareceu numa auditoria, um dia depois.
"""

from __future__ import annotations

import pytest

from mtlcheck.eval import predictions as pred


class _Cell:
    """O mínimo que `assert_comparable` lê."""

    def __init__(self, arm: str, produced_by: str | None, sealed: bool = True) -> None:
        self.sealed = sealed
        self.meta = {"arm": arm, "partition_hash": "h0"}
        if produced_by is not None:
            self.meta["lineage"] = {"produced_by": produced_by}


def test_a_cell_from_a_shell_driver_is_refused() -> None:
    with pytest.raises(ValueError, match="manifesto de wave"):
        pred.assert_comparable([_Cell("cat", "train"), _Cell("joint", "wave")])


def test_a_cell_from_a_wave_passes() -> None:
    """O contrapeso: sem ele, uma implementação que recusa tudo passaria no teste acima."""
    pred.assert_comparable([_Cell("cat", "wave"), _Cell("joint", "wave")])


def test_a_cell_banked_before_the_field_existed_is_not_refused() -> None:
    """Migração, pela mesma regra assimétrica do substrato: ausente não invalida.

    Toda célula bancada antes deste campo — as SELADAS inclusive — não tem linhagem. Recusá-las
    exigiria retreiná-las, o que gastaria uma segunda leitura do teste externo.
    """
    pred.assert_comparable([_Cell("cat", None), _Cell("joint", None)])


def test_exploratory_reading_stays_available() -> None:
    """A saída existe e é explícita — é assim que alguém assume a responsabilidade."""
    pred.assert_comparable([_Cell("cat", "train")], confirmatory=False)


def test_digest_recusa_um_dicionario_sem_chaves_de_identidade() -> None:
    """O mau uso silencioso: `digest(of(dir))` em vez de `digest(manifest)`.

    Sem a guarda, todas as `_IDENTITY_KEYS` viram None e o hash é **constante** — Alabama e Arizona
    saíam com o mesmo fingerprint (2026-08-21). Num módulo cujo propósito é detectar mudança, um
    hash que nunca muda é o pior modo de falha, e ele *parece* um fingerprint legítimo.
    """
    import pytest

    from mtlcheck.substrate import identity

    resumo = {"engine": "check2hgi_v18", "state": "alabama", "identity": "696ac00419d287d3"}
    with pytest.raises(ValueError, match="sem nenhuma chave de identidade"):
        identity.digest(resumo)


def test_dois_manifestos_diferentes_nao_colidem() -> None:
    """A propriedade que a guarda protege, afirmada diretamente."""
    from mtlcheck.substrate import identity

    a = {"recipe": {"engine": "x"}, "counts": {"places": 1}, "training": {"best_loss": 0.1}}
    b = {"recipe": {"engine": "x"}, "counts": {"places": 2}, "training": {"best_loss": 0.1}}
    assert identity.digest(a) != identity.digest(b)
