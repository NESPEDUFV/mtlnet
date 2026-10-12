"""The region tower's input path, and the pairing invariant.

The region tensor is the one model input that is not materialised anywhere: it is built by walking
`window -> place -> region -> region embedding`, joining two substrates. Nothing on disk can be
diffed against it, so it is validated through an invariant instead — the reference's own label
columns are derived from the same chain, so they must agree with it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from mtlcheck.config import Pairing
from mtlcheck.data import loaders, tensors

from ._old_repo import OLD_REPO

REFERENCE = Path(__file__).resolve().parents[2] / "artifacts" / "reference" / "check2hgi_v18" / "alabama"
GRAPH = OLD_REPO / "output" / "check2hgi" / "alabama" / "temp" / "checkin_graph.pt"
REGION_EMB = OLD_REPO / "output" / "check2hgi_design_k_resln_mae_l0_1" / "alabama" / "region_embeddings.parquet"


def _maps():
    if not GRAPH.exists():
        pytest.skip(f"graph maps absent: {GRAPH}")
    return tensors.PlaceRegionMaps.from_graph(GRAPH)


def _sequences() -> pd.DataFrame:
    path = REFERENCE / "sequences_next.parquet"
    if not path.exists():
        pytest.skip(f"reference windows absent: {path}")
    return pd.read_parquet(path)


def _region_labels() -> pd.DataFrame:
    path = REFERENCE / "next_region_labels.parquet"
    if not path.exists():
        pytest.skip(f"reference region labels absent: {path}")
    return pd.read_parquet(path)


@pytest.mark.artifacts
@pytest.mark.equivalence
def test_target_region_matches_the_label_column() -> None:
    """`region_idx` is the region of `target_poi`.

    Validates the place->region chain against the reference's own label column: if the map, its
    orientation, or the row order were wrong, this disagrees immediately.
    """
    maps, seq, labels = _maps(), _sequences(), _region_labels()
    derived = tensors.region_of(seq["target_poi"].to_numpy(), maps)
    expected = labels["region_idx"].to_numpy()

    mismatches = int((derived != expected).sum())
    assert mismatches == 0, (
        f"{mismatches} of {len(expected)} target regions disagree with the label column "
        f"(first at row {int(np.flatnonzero(derived != expected)[0])})"
    )


@pytest.mark.artifacts
@pytest.mark.equivalence
def test_last_history_region_matches_the_aux_column() -> None:
    """`last_region_idx` is the region of the LAST historical visit (`poi_8`).

    This column feeds the flow head through the auxiliary side channel. Getting the position wrong —
    reading the target instead of the last history slot — would hand the head the answer, which is
    the exact class of leak this project exists to keep out.
    """
    maps, seq, labels = _maps(), _sequences(), _region_labels()
    derived = tensors.region_of(seq["poi_8"].to_numpy(), maps)
    expected = labels["last_region_idx"].to_numpy()

    mismatches = int((derived != expected).sum())
    assert mismatches == 0, f"{mismatches} of {len(expected)} last-history regions disagree"

    # And it must NOT be the target's region, or the head would be reading its own label.
    target_region = tensors.region_of(seq["target_poi"].to_numpy(), maps)
    assert (expected != target_region).any(), "last_region_idx never differs from the target region"


@pytest.mark.artifacts
def test_region_tensor_shape_and_lookup() -> None:
    maps, seq = _maps(), _sequences()
    if not REGION_EMB.exists():
        pytest.skip(f"region embeddings absent: {REGION_EMB}")
    table = pd.read_parquet(REGION_EMB)

    history = seq[[f"poi_{i}" for i in range(9)]].to_numpy()[:2000]
    out = tensors.region_tensor(history, maps, table)

    assert out.shape == (2000, 9, 64)
    assert out.dtype == np.float32

    # Position 8 of the tensor must be the embedding of the region `last_region_idx` names.
    last_region = tensors.region_of(history[:, 8], maps)
    matrix = tensors._region_embedding_matrix(table)
    assert np.allclose(out[:, 8, :], matrix[last_region])

    # No window at stride 1 contains padding, so no row is the zero vector by construction.
    assert (np.abs(out).sum(axis=-1) > 0).all(), "a zero-vector position appeared where none can"


# ---------------------------------------------------------------- S13 pairing

def _stream(n: int, value: int) -> loaders.TaskStream:
    return loaders.TaskStream(
        x=torch.full((n, 9, 4), float(value)),
        y=torch.arange(n),
    )


def test_random_pairing_decouples_the_two_streams() -> None:
    """S13 — under the v18-faithful mode the two streams are shuffled independently.

    The check is on the LABELS: with independent draws, the category row and the region row in a
    batch position come from different windows, so their row ids disagree almost everywhere. Under
    aligned pairing they agree everywhere. That difference is the whole invariant.
    """
    cat, reg = _stream(2000, 1), _stream(2000, 2)
    gen = torch.Generator().manual_seed(0)

    same = 0
    total = 0
    for (_, y_cat, _), (_, y_reg, _) in loaders.joint_batches(
        cat, reg, batch_size=256, shuffle=True, pairing=Pairing.RANDOM, generator=gen
    ):
        same += int((y_cat == y_reg).sum())
        total += len(y_cat)

    assert total == 2000
    # Two independent permutations of 2000 rows agree in ~1 position on average.
    assert same < 20, f"{same} of {total} positions are aligned — the streams are not independent"


def test_aligned_pairing_couples_them_exactly() -> None:
    cat, reg = _stream(2000, 1), _stream(2000, 2)
    gen = torch.Generator().manual_seed(0)

    for (_, y_cat, _), (_, y_reg, _) in loaders.joint_batches(
        cat, reg, batch_size=256, shuffle=True, pairing=Pairing.ALIGNED, generator=gen
    ):
        assert (y_cat == y_reg).all(), "aligned pairing produced mismatched rows"


def test_validation_is_aligned_under_both_modes() -> None:
    """Validation walks both streams in order, so the mode cannot affect a reported number."""
    cat, reg = _stream(500, 1), _stream(500, 2)
    for pairing in (Pairing.RANDOM, Pairing.ALIGNED):
        seen = []
        for (_, y_cat, _), (_, y_reg, _) in loaders.joint_batches(
            cat, reg, batch_size=64, shuffle=False, pairing=pairing
        ):
            assert (y_cat == y_reg).all()
            seen.append(y_cat)
        assert torch.equal(torch.cat(seen), torch.arange(500))


def test_unequal_streams_are_refused() -> None:
    """Cycling the shorter stream would double-count its leading rows in the scored metrics."""
    with pytest.raises(ValueError, match="must match"):
        list(loaders.joint_batches(_stream(100, 1), _stream(90, 2), batch_size=16,
                                   shuffle=False, pairing=Pairing.RANDOM))


def test_steps_per_epoch_counts_the_partial_batch() -> None:
    assert loaders.steps_per_epoch(96_326, 8192) == 12
    assert loaders.steps_per_epoch(8192, 8192) == 1
    assert loaders.steps_per_epoch(8193, 8192) == 2
