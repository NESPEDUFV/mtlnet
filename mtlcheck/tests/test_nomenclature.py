"""The nomenclature rules, enforced where they can be.

`docs/NOMENCLATURE.md` is an enforcing document, and a document nothing checks is a suggestion. These
tests cover the two rules that are mechanically checkable and that the project has already broken
once: reporting a sample size that multiplies correlated cells, and letting an interval exist without
its unit.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "NOMENCLATURE.md"


def test_the_nomenclature_document_exists_and_names_the_confound() -> None:
    assert DOC.exists()
    text = DOC.read_text()
    for required in ("repetition", "replicate", "split_seed", "model_seed"):
        assert required in text, f"the vocabulary must define {required}"
    assert "R × K" in text or "R x K" in text, "the forbidden sample size must be named"


def test_the_paired_band_uses_repetitions_not_cells() -> None:
    """n for a paired comparison is the number of repetitions, and R=1 must refuse to answer.

    The reference published "paired Wilcoxon over n=20" for 20 cells sharing 75-80% of their
    training data. The band here is over per-repetition deltas, and at R=1 there is no spread to
    estimate — so it returns NaN rather than a confident zero.
    """
    import math

    from mtlcheck.train.stats import Cell, compare

    one = compare([Cell(seed=0, fold=f, value=70.0) for f in range(5)],
                  [Cell(seed=0, fold=f, value=70.2) for f in range(5)])
    assert one.n_pairs == 5, "five folds were paired"
    assert len(one.seed_deltas) == 1, "but they belong to ONE repetition"
    assert math.isnan(one.stderr), "R=1 has no spread; the band must refuse rather than say 0"
    assert not one.separated()

    four = compare([Cell(seed=s, fold=f, value=70.0) for s in (0, 1, 7, 100) for f in range(5)],
                   [Cell(seed=s, fold=f, value=70.2) for s in (0, 1, 7, 100) for f in range(5)])
    assert len(four.seed_deltas) == 4, "one delta per repetition, not per cell"


def test_a_paired_result_states_its_unit() -> None:
    """An interval without its unit is not a result (rule 4)."""
    from mtlcheck.train.stats import Cell, compare

    arms = ([Cell(seed=s, fold=f, value=70.0 + f) for s in (0, 1) for f in range(5)],
            [Cell(seed=s, fold=f, value=70.3 + f) for s in (0, 1) for f in range(5)])

    described = compare(*arms, band_over="model_seed").describe()
    assert "réplicas" in described, "a descrição tem de dizer sobre o que a banda é"
    assert "model_seed replicates" in described, "and which FACTOR those replicates index"
    assert "seeds" not in described, ("`seeds` é a palavra que o §7 depreca; com a partição "
                                      "congelada estes são réplicas")
    assert "NOT independent" in described, "the correlation warning must survive into the text"

    # Protocol §10.5: a band whose factor nobody named is not interpretable, so it is not printed.
    with pytest.raises(ValueError, match="band_over"):
        compare(*arms).describe()


@pytest.mark.parametrize("forbidden", ["n=20", "n = 20", "20 independent"])
def test_no_source_file_claims_the_multiplied_sample_size(forbidden: str) -> None:
    """Rule 2, checked over the package: R x K is never an inferential n.

    Scoped to src/ deliberately. Docs quote the reference's own wording when describing the defect,
    and a check that forbade the string everywhere would forbid documenting it.
    """
    offenders = []
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text()
        for number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if forbidden in line and not stripped.startswith("#"):
                offenders.append(f"{path.relative_to(ROOT)}:{number}")
    assert not offenders, f"{forbidden!r} used as a sample size in: {offenders}"


def test_predictions_default_on_with_split_seed_off_without() -> None:
    """`train` guarda as predições do fold externo por padrão quando a partição é explícita.

    Guardar linhas não é ler o teste — a época já saiu do inner-val e o que fica em disco são
    predições, não escore. O ato racionado é o `compare`. O default era desligado e o custo disso
    foi concreto: a campanha de 19-08 não guardou as linhas, então ler o teste sobre ela exigiria
    retreinar tudo.
    """
    import inspect

    from mtlcheck import cli

    # O contrato está no resolvedor, não no argparse: None significa "decida pelo split_seed".
    sig = inspect.signature(cli._train_cell)
    assert sig.parameters["capture_predictions"].default is None, (
        "o default tem de ser None para que _train_cell possa decidir pelo split_seed; "
        "False voltaria a nunca guardar")


def test_the_wave_cell_default_is_frozen_data() -> None:
    """⚠ O default do manifesto NÃO acompanha o do `train`, e isso é deliberado.

    O resume re-executa uma célula que DECLARA predições e não as tem em disco. Inverter este
    default invalidaria toda célula bancada cujo manifesto omite o campo — inclusive as SELADAS,
    gastando uma segunda leitura do teste externo. É a mesma armadilha que
    `test_recipe_immutability.py` pina do outro lado.
    """
    from mtlcheck.train.wave import Cell

    cell = Cell(recipe="r.toml", state="alabama", seed=0)
    assert cell.save_predictions is False, (
        "harmonizar este default com o do `train` re-executaria as células seladas")
