"""O corpus é restrito aos lugares que sobreviveram ao join espacial — e é no-op nos EUA.

Por que este arquivo existe: os census tracts do TIGER ladrilham o estado, então nos cinco estados
dos EUA nenhum lugar cai fora e o filtro nunca removeu linha nenhuma. Em Istambul as mahalles do OSM
não ladrilham a região metropolitana e 12 850 dos 42 795 lugares ficam fora — as 80 109 visitas neles
ficariam órfãs, e `_place_indices` recusa (com razão: lugar ausente vira NaN, que o numpy converte em
índice negativo e agrupa as visitas silenciosamente no último lugar).

O teste que mais importa é o do no-op: se este filtro mudasse UMA linha num estado dos EUA, todo
substrato bancado deixaria de reproduzir.
"""
from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd

from mtlcheck.substrate.pipeline import _restrict_to_hierarchy


@dataclasses.dataclass
class _Corpus:
    """Suficiente para o filtro, e **dataclass de propósito**: `_restrict_to_hierarchy` usa
    `dataclasses.replace`, então um stub comum passaria por um motivo errado."""

    frame: pd.DataFrame
    category_codes: np.ndarray
    category_vocab: tuple = ("a", "b")

    @property
    def n_places(self) -> int:
        return int(self.frame["placeid"].nunique())


class _Hierarchy:
    def __init__(self, ids):
        self.place_to_index = {int(i): k for k, i in enumerate(ids)}


def _corpus(placeids):
    frame = pd.DataFrame({"placeid": np.array(placeids, dtype=np.int64),
                          "userid": np.arange(len(placeids))})
    return _Corpus(frame, np.arange(len(placeids), dtype=np.int64))


def test_e_no_op_quando_todo_lugar_sobrevive() -> None:
    """O caso dos EUA. Devolve o MESMO objeto — nem uma cópia, para não haver dúvida."""
    corpus = _corpus([10, 20, 30, 10])
    out = _restrict_to_hierarchy(corpus, _Hierarchy([10, 20, 30]))
    assert out is corpus


def test_descarta_as_visitas_dos_lugares_que_ficaram_de_fora() -> None:
    corpus = _corpus([10, 99, 20, 99, 30])
    out = _restrict_to_hierarchy(corpus, _Hierarchy([10, 20, 30]))
    assert out.frame["placeid"].tolist() == [10, 20, 30]
    assert out.n_places == 3


def test_os_codigos_de_categoria_seguem_as_mesmas_linhas() -> None:
    """Desalinhar aqui trocaria o rótulo de cada visita — o defeito seria silencioso e total."""
    corpus = _corpus([10, 99, 20, 99, 30])
    out = _restrict_to_hierarchy(corpus, _Hierarchy([10, 20, 30]))
    assert out.category_codes.tolist() == [0, 2, 4]
    assert len(out.category_codes) == len(out.frame)


def test_o_vocabulario_de_categorias_nao_muda() -> None:
    """Reajustá-lo deslocaria os códigos e tornaria o substrato irreprodutível."""
    corpus = _corpus([10, 99, 20])
    out = _restrict_to_hierarchy(corpus, _Hierarchy([10, 20]))
    assert out.category_vocab == corpus.category_vocab


def test_o_indice_do_frame_e_reconstruido() -> None:
    """`Corpus.frame` é documentado como indexado 0..n-1 em ordem de visita."""
    out = _restrict_to_hierarchy(_corpus([10, 99, 20]), _Hierarchy([10, 20]))
    assert out.frame.index.tolist() == [0, 1]
