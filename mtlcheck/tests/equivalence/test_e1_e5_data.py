"""E1, E3, E4, E5 — the data layer against the artifacts the v18 numbers were produced from.

The reference artifacts live under `artifacts/reference/`: the on-disk windows, and the label and
userid columns of the two input tables (the 576 embedding columns were left on the A40 — nothing
here needs them). Together they pin the row space every banked Alabama cell trained on.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mtlcheck import paths
from mtlcheck.data import sequences as seq_mod
from mtlcheck.data import splits as split_mod
from mtlcheck.substrate import corpus as corpus_mod

REFERENCE = Path(__file__).resolve().parents[2] / "artifacts" / "reference" / "check2hgi_v18" / "alabama"

# docs/studies/closing_data/v18/AUDIT.md + train_perf_multifold/AUDIT_FINDINGS.md #2
EXPECTED_WINDOWS = 96_326
EXPECTED_USERS = 1_101
EXPECTED_REGION_CLASSES = 1_109      # max(region_idx) + 1 — the head's output width
EXPECTED_REGIONS_PRESENT = 1_052     # how many actually occur in the data
EXPECTED_CATEGORIES = 7


def _ref(name: str) -> pd.DataFrame:
    path = REFERENCE / name
    if not path.exists():
        pytest.skip(f"reference artifact absent: {path}")
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def ref_sequences() -> pd.DataFrame:
    return _ref("sequences_next.parquet")


@pytest.fixture(scope="module")
def ref_next() -> pd.DataFrame:
    return _ref("next_labels.parquet")


@pytest.fixture(scope="module")
def ref_region() -> pd.DataFrame:
    return _ref("next_region_labels.parquet")


# ---------------------------------------------------------------- E5

@pytest.mark.equivalence
def test_e5_windows_reproduce_the_reference_exactly(ref_sequences: pd.DataFrame) -> None:
    """The window builder reproduces `sequences_next.parquet` — contents, not just counts.

    This is the strongest cheap test in the suite. The windows fix the row space of every downstream
    artifact: the labels, the region targets, the fold membership and therefore every banked number
    for this state are indexed by exactly these rows, in exactly this order.
    """
    path = paths.state_checkins("alabama")
    if not path.exists():
        pytest.skip(f"raw corpus absent: {path}")

    built = seq_mod.build(corpus_mod.load("alabama").frame).to_frame()

    assert len(built) == len(ref_sequences), (
        f"built {len(built)} windows, reference has {len(ref_sequences)}"
    )
    for column in ref_sequences.columns:
        left = built[column].to_numpy()
        right = ref_sequences[column].to_numpy()
        if left.dtype != right.dtype:
            left, right = left.astype(np.int64), right.astype(np.int64)
        mismatches = int((left != right).sum())
        assert mismatches == 0, (
            f"column {column!r}: {mismatches} of {len(left)} rows differ "
            f"(first at index {int(np.flatnonzero(left != right)[0])})"
        )


# ---------------------------------------------------------------- E3

@pytest.mark.equivalence
def test_e3_counts(ref_sequences: pd.DataFrame, ref_next: pd.DataFrame,
                   ref_region: pd.DataFrame) -> None:
    assert len(ref_sequences) == EXPECTED_WINDOWS
    assert ref_sequences["userid"].nunique() == EXPECTED_USERS
    assert ref_next["next_category"].nunique() == EXPECTED_CATEGORIES


@pytest.mark.equivalence
def test_e3_region_class_count_is_max_plus_one(ref_region: pd.DataFrame) -> None:
    """The DERIVATION, not just the number.

    `n_regions = max(region_idx) + 1` over the full table — not the count of distinct regions, and
    not a train-only count. At Alabama those differ: the head has 1 109 outputs while only 1 052
    regions ever occur, so 57 output rows are never a target. Deriving it any other way changes the
    head's width, its parameter count, and every ranking metric over it.
    """
    region = ref_region["region_idx"].to_numpy()
    assert int(region.max()) + 1 == EXPECTED_REGION_CLASSES
    assert len(np.unique(region)) == EXPECTED_REGIONS_PRESENT
    assert len(np.unique(region)) < int(region.max()) + 1, "the two derivations coincide here"


# ---------------------------------------------------------------- E4

@pytest.mark.equivalence
def test_e4_row_alignment(ref_next: pd.DataFrame, ref_region: pd.DataFrame) -> None:
    """Row-count parity is necessary but NOT sufficient: the userids must agree row for row.

    A stale region table built from a different windowing can carry the same row count and a
    different per-row user, silently mis-pairing every (window, region-label) pair. The reference
    trainer hard-fails on exactly this; so does this test.
    """
    assert len(ref_next) == len(ref_region)
    assert (ref_next["userid"].to_numpy() == ref_region["userid"].to_numpy()).all()
    assert (ref_next["next_category"].to_numpy() == ref_region["next_category"].to_numpy()).all()


@pytest.mark.equivalence
def test_e4_windows_align_with_labels(ref_sequences: pd.DataFrame, ref_next: pd.DataFrame) -> None:
    """The window table and the label table describe the same rows in the same order.

    They also disagree about the column's TYPE: `sequences_next.parquet` stores `userid` as int64
    and `next.parquet` stores it as a string. Same values, same order — but the string form sorts
    lexicographically, and feeding it to the group-aware splitter silently produces a different
    split (see `splits.as_group_ids`). The assertion below casts deliberately, and the assertion
    after it pins the dtype disagreement so it cannot quietly change.
    """
    assert (ref_sequences["userid"].astype(np.int64).to_numpy()
            == ref_next["userid"].astype(np.int64).to_numpy()).all()

    assert ref_sequences["userid"].dtype == np.int64
    # A propriedade que importa é "é TEXTO", não "o backend é object". No pandas 3 a mesma coluna
    # infere `StringDtype`, e checar `== object` reprovava um artefato correto — a guarda disparava
    # pelo motivo errado. `is_string_dtype` cobre os dois backends e continua pegando o caso real:
    # o artefato ter sido regenerado com `userid` numérico.
    assert pd.api.types.is_string_dtype(ref_next["userid"].dtype), (
        "next.parquet's userid is no longer a string — if the artifacts have been regenerated with "
        "consistent dtypes, that is good news, but the split-order trap this guards is worth "
        "re-verifying before the pin is removed"
    )


# ---------------------------------------------------------------- E1

GOLDEN_FOLDS = Path(__file__).resolve().parent / "reference_folds_alabama.json"


@pytest.mark.equivalence
@pytest.mark.parametrize("seed", [0, 1, 7, 100])
def test_e1_folds_match_the_reference_implementation(ref_next: pd.DataFrame, seed: int) -> None:
    """Fold membership is identical to what the REFERENCE CODE produced.

    The golden file holds SHA-256 digests of the index arrays that the old implementation's own
    `load_next_data` + `StratifiedGroupKFold` emitted, generated on the machine that produced the
    banked cells (`reference_folds_alabama.json`, 4 seeds x 5 folds).

    An earlier version of this test built its "expected" split by calling sklearn inside the test
    with the same coercions the implementation applies — which shares the estimator, the row space
    and the coercions with the thing under test, so it could only ever have caught a change in the
    label map. Comparing against digests of the other implementation's output has no such overlap.
    """
    if not GOLDEN_FOLDS.exists():
        pytest.skip(f"golden fold digests absent: {GOLDEN_FOLDS}")
    golden = json.loads(GOLDEN_FOLDS.read_text())

    assert golden["n_rows"] == len(ref_next), "golden was generated on a different row space"

    folds = split_mod.build(ref_next["next_category"], ref_next["userid"], split_seed=seed)
    assert len(folds) == 5

    for fold, expected in zip(folds, golden[str(seed)]):
        assert fold.n_train == expected["n_train"], f"seed {seed} fold {fold.index + 1}: train size"
        assert fold.n_val == expected["n_val"], f"seed {seed} fold {fold.index + 1}: val size"
        assert _digest(fold.train) == expected["train_sha256"], (
            f"seed {seed} fold {fold.index + 1}: train indices differ from the reference"
        )
        assert _digest(fold.val) == expected["val_sha256"], (
            f"seed {seed} fold {fold.index + 1}: val indices differ from the reference"
        )


def _digest(index: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(index, dtype=np.int64).tobytes()).hexdigest()


# ---------------------------------------------------------------- E2

@pytest.mark.equivalence
@pytest.mark.parametrize("seed", [0, 1, 7, 100])
def test_e2_folds_are_user_disjoint(ref_next: pd.DataFrame, seed: int) -> None:
    folds = split_mod.build(ref_next["next_category"], ref_next["userid"], split_seed=seed)
    split_mod.assert_user_disjoint(folds, ref_next["userid"])


@pytest.mark.equivalence
def test_every_row_is_used_exactly_once_as_validation(ref_next: pd.DataFrame) -> None:
    folds = split_mod.build(ref_next["next_category"], ref_next["userid"], split_seed=0)
    covered = np.concatenate([f.val for f in folds])
    assert len(covered) == len(ref_next)
    assert len(np.unique(covered)) == len(ref_next)
