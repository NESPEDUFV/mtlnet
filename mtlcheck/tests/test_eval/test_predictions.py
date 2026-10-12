"""The persistence contract — the one artifact that cannot be rebuilt after the fact.

These tests exist because `predictions.py` had none. It is the module whose failure is unrecoverable:
every other part of the protocol is post-processing over these rows, so a defect here is only visible
after the training that produced them is gone.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from mtlcheck.eval import predictions as P

from conftest import extra_valido

from conftest import extra_valido


class _Fold:
    def __init__(self, val):
        self.val = np.asarray(val)


def _pred(**over):
    base = dict(
        state="alabama", arm="cat", task="cat", split_seed=0, partition_hash="abc123def456",
        model_seed=0, fold=0, selected_epoch=12,
        userid=np.array([1, 1, 2, 3]), window_id=np.array([0, 1, 2, 3]),
        y_true=np.array([0, 1, 2, 3]), y_pred=np.array([0, 1, 1, 3]),
        rank_of_true=np.array([1, 1, 4, 1]), train_labels=frozenset({0, 1, 2, 3}),
        sealed=True,
    )
    base.update(over)
    return P.FoldPredictions(**base)


def _write(directory, banked, **extra):
    """`P.write` com o mínimo que o contrato do sidecar exige.

    O contrato existe para que uma célula sem identidade não possa ser escrita; escrevê-la aqui à
    mão, teste a teste, só reintroduziria a divergência entre fixture e produção.
    """
    return P.write(directory, banked, extra=extra_valido(arm=banked[0].arm, **extra))


def test_round_trip_preserves_every_column_and_the_sidecar(tmp_path) -> None:
    written = _write(tmp_path, [_pred(fold=0), _pred(fold=1, selected_epoch=9)],
                     study="t", n_categories=7)
    assert written.exists()

    loaded = P.read(tmp_path)
    assert list(loaded.frame.columns) == list(P.COLUMNS)
    assert len(loaded.frame) == 8
    assert loaded.sealed is True
    # train_labels and the selected epoch are per (task, fold) and are NOT derivable from the rows.
    assert loaded.train_labels("cat", 0) == frozenset({0, 1, 2, 3})
    assert loaded.meta["selected_epoch"]["cat/1"] == 9
    assert loaded.meta["n_categories"] == 7


def test_a_ragged_row_set_is_refused_rather_than_truncated() -> None:
    """Silently zipping mismatched arrays would attribute one user's prediction to another."""
    with pytest.raises(ValueError, match="rows against"):
        _pred(userid=np.array([1, 2])).to_frame()


def test_predictions_without_a_sidecar_cannot_be_read(tmp_path) -> None:
    _write(tmp_path, [_pred()])
    (tmp_path / "predictions_meta.json").unlink()
    with pytest.raises(ValueError, match="cannot be interpreted"):
        P.read(tmp_path)


def test_a_sidecar_that_disagrees_with_its_rows_is_refused(tmp_path) -> None:
    _write(tmp_path, [_pred()])
    meta = json.loads((tmp_path / "predictions_meta.json").read_text())
    meta["partition_hash"] = "0000deadbeef"
    (tmp_path / "predictions_meta.json").write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="rows carry partition"):
        P.read(tmp_path)


def test_one_cell_must_come_from_one_partition(tmp_path) -> None:
    with pytest.raises(ValueError, match="ONE partition"):
        _write(tmp_path, [_pred(fold=0), _pred(fold=1, partition_hash="999999999999")])


def test_partition_hash_is_of_the_assignment_not_the_seed() -> None:
    """Two runs claiming one split_seed are the same experiment only if the users landed alike."""
    a = P.partition_hash([_Fold([0, 1, 2]), _Fold([3, 4])])
    same = P.partition_hash([_Fold([0, 1, 2]), _Fold([3, 4])])
    moved = P.partition_hash([_Fold([0, 1, 3]), _Fold([2, 4])])
    reordered = P.partition_hash([_Fold([3, 4]), _Fold([0, 1, 2])])
    assert a == same
    assert a != moved, "one user moving folds must change the hash"
    assert a != reordered, "fold ORDER is part of the assignment"


def test_a_confirmatory_comparison_refuses_unsealed_cells(tmp_path) -> None:
    """It used to warn. The measured optimism is ~0.66 pp — larger than the 0.4 pp margin, so a
    warning here is a bias bigger than the effect, scrolling past in a log."""
    sealed_dir, legacy_dir = tmp_path / "a", tmp_path / "b"
    _write(sealed_dir, [_pred(arm="a", sealed=True)])
    _write(legacy_dir, [_pred(arm="b", sealed=False)])
    cells = [P.read(sealed_dir), P.read(legacy_dir)]

    with pytest.raises(ValueError, match="selection optimism|ALSO selected"):
        P.assert_comparable(cells)
    P.assert_comparable(cells, confirmatory=False)          # explicit, and allowed


def test_cells_from_different_partitions_are_never_paired(tmp_path) -> None:
    one, two = tmp_path / "one", tmp_path / "two"
    _write(one, [_pred(arm="a")])
    _write(two, [_pred(arm="b", partition_hash="ffffffffffff")])
    with pytest.raises(ValueError, match="span 2 partitions"):
        P.assert_comparable([P.read(one), P.read(two)])


def test_collect_skips_an_unreadable_cell_without_losing_the_rest(tmp_path, caplog) -> None:
    good, broken = tmp_path / "good", tmp_path / "broken"
    _write(good, [_pred()])
    _write(broken, [_pred()])
    (broken / "predictions_meta.json").unlink()

    found = P.collect(tmp_path)
    assert len(found) == 1 and found[0].meta["arm"] == "cat"


def test_bracos_sobre_vocabularios_diferentes_nao_sao_comparaveis(tmp_path) -> None:
    """§1: "every compared arm's head covers the identical full vocabulary".

    `n_regions` era gravado desde sempre e não era lido em lugar nenhum. Com catálogos diferentes a
    Acc@10 de um braço é sobre outro conjunto de candidatos, e nada mais a jusante percebe.
    """
    one, two = tmp_path / "one", tmp_path / "two"
    _write(one, [_pred(arm="a")], n_regions=520)
    _write(two, [_pred(arm="b")], n_regions=1109)
    with pytest.raises(ValueError, match="n_regions diferentes"):
        P.assert_comparable([P.read(one), P.read(two)])


def test_o_mesmo_vocabulario_passa(tmp_path) -> None:
    one, two = tmp_path / "one", tmp_path / "two"
    _write(one, [_pred(arm="a")], n_regions=520, n_categories=7)
    _write(two, [_pred(arm="b")], n_regions=520, n_categories=7)
    P.assert_comparable([P.read(one), P.read(two)])
