"""Tests for src/data/inputs/next_region.py.

Covers the join-from-raw-placeid path introduced in commit a8a977e:

  sequences_next.parquet (target_poi = raw placeid int)
      → placeid_to_idx (from checkin_graph.pt)
      → poi_to_region (from checkin_graph.pt)
      → next_region.parquet (region_idx column)

Synthetic graph + sequences simulate the schema; the real loader is
called end-to-end.
"""

from __future__ import annotations

import pickle as pkl
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from configs.paths import EmbeddingEngine, IoPaths


@pytest.fixture
def synthetic_check2hgi_state(tmp_path, monkeypatch):
    """Materialise a small fake check2HGI output tree for a synthetic state.

    Structure:
      data/checkins/<State>.parquet        — required by load_next_data
      output/check2hgi/<state>/
        input/next.parquet                 — 576 emb cols + next_category + userid
        temp/sequences_next.parquet        — 9 poi cols + target_poi + userid
        temp/checkin_graph.pt              — pickled dict with placeid_to_idx + poi_to_region
    """
    from configs.paths import IoPaths

    state = "Synthtown"
    state_l = state.lower()

    # IoPaths.CHECK2HGI captures OUTPUT_DIR at class-definition time, so a
    # monkey-patch on the module-level OUTPUT_DIR would be invisible.
    # Instead, override the class-level ``_check2hgi_dir`` attribute that
    # its lookups flow through.
    monkeypatch.setattr(
        IoPaths.CHECK2HGI, "_check2hgi_dir", tmp_path / "output" / "check2hgi",
    )
    # get_next / load_next route through IoPaths.get_input_dir which uses
    # the module-level OUTPUT_DIR — patch that too so the synthetic
    # next.parquet is found.
    monkeypatch.setattr("configs.paths.OUTPUT_DIR", tmp_path / "output")

    n_seq = 20
    emb_dim = 64
    seq_len = 9
    n_pois = 10
    n_regions = 5

    placeid_to_idx = {100 + i: i for i in range(n_pois)}
    poi_to_region = np.array([i % n_regions for i in range(n_pois)], dtype=np.int64)

    # Graph artefact
    temp_dir = tmp_path / "output" / "check2hgi" / state_l / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    graph = {
        "placeid_to_idx": placeid_to_idx,
        "poi_to_region": poi_to_region,
        "num_pois": n_pois,
        "num_regions": n_regions,
        "num_checkins": n_seq,
    }
    with open(temp_dir / "checkin_graph.pt", "wb") as f:
        pkl.dump(graph, f)

    # sequences_next.parquet — target_poi is a raw placeid
    rng = np.random.default_rng(0)
    placeids = list(placeid_to_idx.keys())
    seq_cols = {f"poi_{i}": rng.choice(placeids, size=n_seq) for i in range(seq_len)}
    seq_cols["target_poi"] = rng.choice(placeids, size=n_seq)
    seq_cols["userid"] = rng.integers(0, 5, size=n_seq)
    seq_df = pd.DataFrame(seq_cols)
    seq_df.to_parquet(temp_dir / "sequences_next.parquet")

    # next.parquet — 576 emb cols + next_category + userid, row-aligned with sequences
    input_dir = tmp_path / "output" / "check2hgi" / state_l / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    emb_cols = {str(i): rng.standard_normal(n_seq).astype(np.float32) for i in range(seq_len * emb_dim)}
    next_df = pd.DataFrame(emb_cols)
    next_df["next_category"] = rng.choice(["Food", "Shopping", "Travel"], size=n_seq)
    next_df["userid"] = seq_df["userid"].astype(str).values
    next_df.to_parquet(input_dir / "next.parquet")

    return state, n_seq, n_regions


def test_build_next_region_frame_happy_path(synthetic_check2hgi_state):
    from data.inputs.next_region import build_next_region_frame

    state, n_seq, n_regions = synthetic_check2hgi_state
    df, n_regions_out = build_next_region_frame(state)

    assert len(df) == n_seq
    assert n_regions_out == n_regions
    assert "region_idx" in df.columns
    assert "next_category" not in df.columns, "next_category must be dropped on the region track"
    assert df["region_idx"].between(0, n_regions - 1).all()
    # userid stays — required downstream by StratifiedGroupKFold.
    assert "userid" in df.columns
    # Embedding columns preserved.
    assert all(str(i) in df.columns for i in range(0, 576, 64))


def test_build_next_region_frame_fails_on_unmapped_placeid(synthetic_check2hgi_state, tmp_path):
    """Inject a placeid not present in placeid_to_idx and check loud failure."""
    from data.inputs.next_region import build_next_region_frame

    state, _, _ = synthetic_check2hgi_state
    state_l = state.lower()
    # Corrupt sequences_next.parquet with a bogus placeid
    seq_path = tmp_path / "output" / "check2hgi" / state_l / "temp" / "sequences_next.parquet"
    df = pd.read_parquet(seq_path)
    df.loc[0, "target_poi"] = 999_999_999
    df.to_parquet(seq_path)

    with pytest.raises(ValueError, match="not in placeid_to_idx"):
        build_next_region_frame(state)


def test_build_next_region_frame_fails_on_row_count_mismatch(synthetic_check2hgi_state, tmp_path):
    """If next.parquet and sequences_next.parquet disagree on row count,
    the loader must refuse — silent truncation would corrupt labels."""
    from data.inputs.next_region import build_next_region_frame

    state, _, _ = synthetic_check2hgi_state
    state_l = state.lower()
    next_path = tmp_path / "output" / "check2hgi" / state_l / "input" / "next.parquet"
    df = pd.read_parquet(next_path)
    df.iloc[:10].to_parquet(next_path)  # truncate to 10 rows

    with pytest.raises(ValueError, match="disagree"):
        build_next_region_frame(state)
