"""Synthetic unit tests for ``scripts/compute_region_transition.py``.

Audit finding C4 (`F50_T3_AUDIT_FINDINGS.md`): the legacy log_T is built
from ALL rows of ``sequences_next.parquet`` — including the val rows of
every fold the trainer later runs. The new
``build_transition_matrix_from_userids`` filters to a supplied train-user
set, eliminating the leakage.

These tests pin the contract:

  1. The pure helper ``_log_probs_from_rows`` correctly counts and
     row-normalises with Laplace smoothing.
  2. ``build_transition_matrix_from_userids(all_users)`` matches the
     legacy ``build_transition_matrix`` (zero regression).
  3. Filtering to a strict subset of users actually changes log_T —
     and the change is in the predictable direction (cells that
     drop transitions move toward the Laplace floor).

We monkey-patch the data loaders so the test runs without any real
checkins or graph artefacts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_REPO / "scripts"))

import compute_region_transition as crt


@pytest.fixture
def synth_state(monkeypatch):
    """Build a 4-region / 3-user synthetic state and patch loaders.

    Layout:
      - 4 regions, 6 POIs (placeids 100-105, two POIs per region 0/1/2/3)
      - 3 users (userid 1, 2, 3), 2 transitions each
      - User 3's transitions go to a region NO OTHER user transits to
        (region 3 → region 3) — so dropping user 3 from train should
        flatten that row to the Laplace prior.
    """
    placeid_to_idx = {100: 0, 101: 1, 102: 2, 103: 3, 104: 4, 105: 5}
    poi_to_region = np.array([0, 0, 1, 1, 2, 3], dtype=np.int64)

    rows = pd.DataFrame({
        "poi_8": [100, 102, 100, 102, 105, 105],
        "target_poi": [101, 103, 103, 101, 105, 105],
        "userid": [1, 1, 2, 2, 3, 3],
    })

    monkeypatch.setattr(crt, "_load_sequences", lambda state: rows)
    monkeypatch.setattr(crt, "_load_graph_maps", lambda state: (placeid_to_idx, poi_to_region))
    return rows, placeid_to_idx, poi_to_region


def test_log_probs_from_rows_basic(synth_state):
    rows, placeid_to_idx, poi_to_region = synth_state
    n_regions = int(poi_to_region.max()) + 1  # 4

    log_probs = crt._log_probs_from_rows(
        last_placeids=rows["poi_8"].to_numpy(np.int64),
        target_placeids=rows["target_poi"].to_numpy(np.int64),
        placeid_to_idx=placeid_to_idx,
        poi_to_region=poi_to_region,
        n_regions=n_regions,
        smoothing_eps=0.01,
    )

    assert log_probs.shape == (4, 4)
    assert log_probs.dtype == np.float32

    # Each row of probs must sum to 1 (so log-probs exponentiate to 1).
    row_sums = np.exp(log_probs).sum(axis=1)
    np.testing.assert_allclose(row_sums, np.ones(4), rtol=1e-5)

    # Region 3 was the destination of TWO transitions from region 3
    # (user 3's two rows: 105→105 maps to region 3 → region 3).
    # So log_T[3, 3] should be far above the Laplace floor.
    expected_floor = np.log(0.01 / (3 * 0.01 + 0))  # only floor cells contribute
    assert log_probs[3, 3] > expected_floor + 1.0  # well above floor


def test_full_matches_from_all_userids(synth_state):
    """Regression guard: passing ALL userids must produce log_T identical
    to the legacy full-data build (within float32 noise)."""
    full_log_T, n = crt.build_transition_matrix("synth_state", smoothing_eps=0.01)
    rows, _, _ = synth_state
    all_users = set(rows["userid"].astype(int).tolist())
    sub_log_T, n2 = crt.build_transition_matrix_from_userids(
        "synth_state", train_userids=all_users, smoothing_eps=0.01
    )

    assert n == n2
    np.testing.assert_array_equal(full_log_T, sub_log_T)


def test_subset_diverges_from_full(synth_state):
    """C4 mechanism: dropping user 3 from train_userids must remove their
    transitions from log_T. user 3 is the ONLY contributor to region 3 →
    region 3, so log_T[3, 3] should plummet to the Laplace floor when
    train_userids = {1, 2}."""
    full_log_T, _ = crt.build_transition_matrix("synth_state", smoothing_eps=0.01)
    sub_log_T, _ = crt.build_transition_matrix_from_userids(
        "synth_state", train_userids={1, 2}, smoothing_eps=0.01
    )

    # user 3's region-3 transitions are gone → row 3 is now uniform Laplace.
    np.testing.assert_allclose(
        np.exp(sub_log_T[3]),
        np.full(4, 0.25),  # 4 cells of 0.01 → row sum 0.04 → each = 0.25
        rtol=1e-5,
    )
    # Full version was strongly peaked at (3, 3); subset must have shrunk.
    assert full_log_T[3, 3] - sub_log_T[3, 3] > 1.0


def test_empty_train_userids_raises(synth_state):
    with pytest.raises(ValueError, match="No rows match"):
        crt.build_transition_matrix_from_userids(
            "synth_state", train_userids={9999}, smoothing_eps=0.01
        )


def test_per_fold_partition_disjoint_when_user_isolated(synth_state):
    """If train_userids partitions cleanly (no user appears in two folds'
    train sets unanimously), per-fold log_T entries differ in the rows
    where the heldout user contributed. This is the property the C4 fix
    relies on for paired tests."""
    full_log_T, _ = crt.build_transition_matrix("synth_state", smoothing_eps=0.01)
    train_minus_3, _ = crt.build_transition_matrix_from_userids(
        "synth_state", train_userids={1, 2}, smoothing_eps=0.01
    )
    train_minus_2, _ = crt.build_transition_matrix_from_userids(
        "synth_state", train_userids={1, 3}, smoothing_eps=0.01
    )
    # The two per-fold log_Ts must differ from each other AND from full.
    assert not np.allclose(train_minus_3, train_minus_2)
    assert not np.allclose(train_minus_3, full_log_T)
    assert not np.allclose(train_minus_2, full_log_T)
