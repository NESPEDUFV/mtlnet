"""O ambiente que o `uv sync` entrega é o ambiente onde a ciência roda.

Até 2026-08-19 não era: o `pyproject` pedia `pandas>=2.2` e o `uv.lock` entregava **3.0.5 com Python
3.14**, enquanto todo número deste projeto saiu do A40 sob Python 3.12 / pandas 2.2.3 / numpy 2.0.2.
`uv sync` dava um ambiente que nenhum artefato bancado conhece.

Não era teórico: o bump entrou sem ninguém rodar a suíte contra ele e carregou por um dia um
`TypeError` que travava **todo** build de substrato.

Este teste não checa versão exata — checa a FAIXA declarada, que é o contrato. Se ele falhar, ou o
`pyproject` mudou sem decisão, ou o ambiente saiu do que a dissertação consegue reproduzir.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
import sklearn


def _parts(version: str, n: int = 2) -> tuple[int, ...]:
    return tuple(int(x) for x in version.split(".")[:n])


def test_python_is_in_the_declared_range() -> None:
    """`>=3.12,<3.14`. O 3.14 saiu porque foi o que o lock escolheu sozinho e trouxe pandas 3."""
    assert (3, 12) <= sys.version_info[:2] < (3, 14), (
        f"Python {sys.version_info.major}.{sys.version_info.minor} está fora da faixa declarada")


def test_pandas_is_below_3() -> None:
    """`<3` porque o pandas 3 infere `StringDtype` para colunas de texto, e o código do porte —
    escrito e validado sob `object` — tinha pelo menos dois pontos que assumiam o backend antigo.
    Os dois estão corrigidos, mas a faixa é a decisão registrada."""
    assert _parts(pd.__version__) < (3, 0), f"pandas {pd.__version__} está acima do teto declarado"


def test_numpy_is_below_2_5() -> None:
    assert _parts(np.__version__) < (2, 5), f"numpy {np.__version__} está acima do teto declarado"


def test_scikit_learn_has_no_ceiling_on_purpose() -> None:
    """A exceção deliberada.

    Verificado em 19-08: os cinco hashes de fold são IDÊNTICOS entre 1.8 e 1.9 sobre os mesmos
    dados, então a versão não é parâmetro científico. E o 1.9 recusa um `StratifiedGroupKFold` cujo
    `n_splits` excede a contagem de grupos — recusa que o 1.8 não fazia, e que achou uma fixture
    degenerada onde cinco testes passavam sobre um split impossível.
    """
    assert _parts(sklearn.__version__) >= (1, 8), (
        f"scikit-learn {sklearn.__version__} está abaixo do piso; o 1.9 traz a recusa de split "
        f"degenerado e não há motivo para voltar")


def test_the_fold_split_does_not_depend_on_the_sklearn_version() -> None:
    """A verificação que autorizou deixar o sklearn sem teto.

    Se um dia isto falhar, a versão do sklearn passou a ser parâmetro CIENTÍFICO — todo o pareamento
    do projeto assume que a partição é função de (dados, semente) e de nada mais — e o teto tem de
    voltar.
    """
    import hashlib
    from pathlib import Path

    from mtlcheck.data import splits as sp

    fixture = Path(__file__).resolve().parent / "fixtures/alabama_head2000/input/next.parquet"
    if not fixture.exists():
        import pytest
        pytest.skip("fixture ausente")

    t = pd.read_parquet(fixture, columns=["userid", "next_category"])
    folds = sp.build(sp.encode_categories(t["next_category"].to_numpy()),
                     sp.as_group_ids(t["userid"].to_numpy()), split_seed=0, n_splits=5)
    got = [hashlib.sha256(np.ascontiguousarray(np.sort(f.val))).hexdigest()[:16] for f in folds]
    # Medidos sob sklearn 1.8.0 E 1.9.0 em 2026-08-19 — idênticos nas duas.
    assert got == ["6c77c902f6317a5d", "fe8f1912006c8e99", "3f14f1dd34a75672",
                   "2ad22fc803adf85f", "39438544025dc0c1"], (
        "a partição mudou. Ou os dados da fixture mudaram, ou o splitter passou a depender da "
        "versão da biblioteca — e nesse caso ela virou parâmetro científico e precisa de teto.")
