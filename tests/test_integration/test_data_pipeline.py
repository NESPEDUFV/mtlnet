"""
Integration tests for the data pipeline: embedding alignment, fusion, and sequence generation.

Tests the full flow from synthetic DataFrames through core/fusion functions to output arrays.
No real data files required. No IoPaths mocking needed — we test core functions directly.

Covers gaps identified in the test suite:
- EmbeddingAligner.align_checkin_level (was skipped in test_mtl_input_fusion.py)
- Mixed POI + checkin fusion -> sequence generation
- Fusion alignment invariants (same POI = same embedding in POI-level, varies in checkin-level)
- End-to-end: fusion data feeds correctly into convert_sequences_to_poi_embeddings / convert_user_checkins_to_sequences
"""

import numpy as np
import pandas as pd
import pytest

from configs.embedding_fusion import EmbeddingLevel, EmbeddingSpec, FusionConfig
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine
from data.inputs.core import (
    PADDING_VALUE,
    MISSING_CATEGORY_VALUE,
    convert_sequences_to_poi_embeddings,
    convert_user_checkins_to_sequences,
    create_category_lookup,
    create_embedding_lookup,
    generate_sequences,
)
from data.inputs.fusion import EmbeddingAligner, EmbeddingFuser

SEED = 42
WINDOW_SIZE = InputsConfig.SLIDE_WINDOW  # 9
CATEGORIES = ["Food", "Shop", "Cafe", "Park", "Entertainment"]


# ---------------------------------------------------------------------------
# Synthetic data factory
# ---------------------------------------------------------------------------

def make_pipeline_data(
    n_users: int = 3,
    n_pois: int = 8,
    checkins_per_user: int = 40,
    embedding_dim: int = 64,
    seed: int = SEED,
) -> dict:
    """
    Build synthetic DataFrames mimicking real pipeline data.

    Returns dict with keys:
        checkins_df          - (userid, placeid, datetime, category)
        poi_embeddings_hgi   - (placeid, 0..dim-1) — one per POI, deterministic
        poi_embeddings_space - (placeid, 0..dim-1) — different values from HGI
        checkin_embeddings_time - (userid, placeid, datetime, category, 0..dim-1) — unique per row
        poi_ids              - list of POI IDs
        categories           - category mapping {placeid: category}
        embedding_dim        - dimension used
    """
    rng = np.random.RandomState(seed)
    poi_ids = list(range(100, 100 + n_pois))
    cat_map = {pid: CATEGORIES[i % len(CATEGORIES)] for i, pid in enumerate(poi_ids)}

    # Build checkins: each user visits POIs cyclically with repeated visits
    rows = []
    base_time = pd.Timestamp("2023-01-01 08:00")
    for uid in range(1, n_users + 1):
        for ci in range(checkins_per_user):
            pid = poi_ids[ci % n_pois]  # cyclic → guarantees repeated visits
            dt = base_time + pd.Timedelta(hours=uid * 1000 + ci)
            rows.append({"userid": uid, "placeid": pid, "datetime": dt, "category": cat_map[pid]})

    checkins_df = pd.DataFrame(rows).sort_values(["userid", "datetime"]).reset_index(drop=True)

    # POI-level embeddings (HGI): deterministic per POI
    hgi_embs = {}
    for pid in poi_ids:
        hgi_embs[pid] = rng.randn(embedding_dim).astype(np.float32)
    poi_hgi_df = pd.DataFrame(
        [{"placeid": pid, **{str(d): hgi_embs[pid][d] for d in range(embedding_dim)}} for pid in poi_ids]
    )

    # POI-level embeddings (Space2Vec): different seed offset
    rng2 = np.random.RandomState(seed + 999)
    space_embs = {}
    for pid in poi_ids:
        space_embs[pid] = rng2.randn(embedding_dim).astype(np.float32)
    poi_space_df = pd.DataFrame(
        [{"placeid": pid, **{str(d): space_embs[pid][d] for d in range(embedding_dim)}} for pid in poi_ids]
    )

    # Check-in-level embeddings (Time2Vec): unique per row, encodes row index
    checkin_time_rows = []
    rng3 = np.random.RandomState(seed + 777)
    for idx, row in checkins_df.iterrows():
        # Encode row index in the embedding so we can verify position-based lookup
        emb = rng3.randn(embedding_dim).astype(np.float32)
        emb[0] = float(idx)  # first dim encodes global row index
        checkin_time_rows.append({
            "userid": row["userid"],
            "placeid": row["placeid"],
            "datetime": row["datetime"],
            "category": row["category"],
            **{str(d): emb[d] for d in range(embedding_dim)},
        })
    checkin_time_df = pd.DataFrame(checkin_time_rows)

    return {
        "checkins_df": checkins_df,
        "poi_embeddings_hgi": poi_hgi_df,
        "poi_embeddings_space": poi_space_df,
        "checkin_embeddings_time": checkin_time_df,
        "poi_ids": poi_ids,
        "categories": cat_map,
        "embedding_dim": embedding_dim,
        "hgi_embs": hgi_embs,
        "space_embs": space_embs,
    }


@pytest.fixture
def data():
    return make_pipeline_data()


@pytest.fixture
def small_data():
    """Small embedding dim for readable assertions."""
    return make_pipeline_data(embedding_dim=8)


# ---------------------------------------------------------------------------
# Single-engine POI-level next tests
# ---------------------------------------------------------------------------

class TestSingleEngineNextPoiLevel:
    """Test generate_sequences -> create_embedding_lookup -> convert_sequences_to_poi_embeddings."""

    def test_sequences_then_poi_lookup_shapes(self, data):
        dim = data["embedding_dim"]
        checkins_df = data["checkins_df"]
        poi_hgi_df = data["poi_embeddings_hgi"]

        embedding_lookup = create_embedding_lookup(poi_hgi_df, dim)
        category_lookup = create_category_lookup(checkins_df)

        # Generate sequences for all users
        all_seqs = []
        for uid, udf in checkins_df.groupby("userid"):
            places = udf["placeid"].tolist()
            seqs = generate_sequences(places, window_size=WINDOW_SIZE)
            for s in seqs:
                all_seqs.append(s + [uid])

        seq_cols = [f"poi_{i}" for i in range(WINDOW_SIZE)] + ["target_poi", "userid"]
        sequences_df = pd.DataFrame(all_seqs, columns=seq_cols)

        results = convert_sequences_to_poi_embeddings(
            sequences_df, embedding_lookup, category_lookup,
            WINDOW_SIZE, dim, show_progress=False,
        )

        assert len(results) > 0
        assert len(results) == len(sequences_df)
        # Each result: flattened (WINDOW_SIZE * dim) + target_category + userid
        expected_len = WINDOW_SIZE * dim + 2
        for r in results:
            assert len(r) == expected_len

    def test_same_poi_same_embedding(self, data):
        """Same POI in different positions/sequences must produce identical embedding."""
        dim = data["embedding_dim"]
        poi_hgi_df = data["poi_embeddings_hgi"]
        hgi_embs = data["hgi_embs"]

        embedding_lookup = create_embedding_lookup(poi_hgi_df, dim)

        # Pick a POI that appears multiple times
        poi_id = data["poi_ids"][0]
        expected = hgi_embs[poi_id]

        # Lookup should always return the same vector
        result = embedding_lookup[poi_id]
        np.testing.assert_array_almost_equal(result, expected)

    def test_padding_gets_zero_embedding(self, data):
        dim = data["embedding_dim"]
        poi_hgi_df = data["poi_embeddings_hgi"]
        embedding_lookup = create_embedding_lookup(poi_hgi_df, dim)

        pad_emb = embedding_lookup[PADDING_VALUE]
        np.testing.assert_array_equal(pad_emb, np.zeros(dim, dtype=np.float32))

    def test_all_users_produce_sequences(self, data):
        """Every user with enough checkins must produce at least one sequence."""
        checkins_df = data["checkins_df"]
        users_with_seqs = set()

        for uid, udf in checkins_df.groupby("userid"):
            places = udf["placeid"].tolist()
            seqs = generate_sequences(places, window_size=WINDOW_SIZE)
            if seqs:
                users_with_seqs.add(uid)

        # All 3 users have 40 checkins each (>> MIN_SEQUENCE_LENGTH=5)
        assert len(users_with_seqs) == 3


# ---------------------------------------------------------------------------
# Single-engine checkin-level next tests
# ---------------------------------------------------------------------------

class TestSingleEngineNextCheckinLevel:
    """Test convert_user_checkins_to_sequences with checkin-level embeddings."""

    def test_position_based_lookup(self, data):
        """Sequence N position i must map to user_df.iloc[N * WINDOW_SIZE + i]."""
        dim = data["embedding_dim"]
        checkin_df = data["checkin_embeddings_time"]
        emb_cols = [str(d) for d in range(dim)]

        # Process user 1
        user_df = checkin_df[checkin_df["userid"] == 1].reset_index(drop=True)
        results, sequences = convert_user_checkins_to_sequences(
            user_df, emb_cols, WINDOW_SIZE, dim
        )

        assert len(results) > 1  # At least 2 sequences from 40 checkins

        # Check sequence 1, position 2
        seq_idx = 1
        pos_in_seq = 2
        expected_row_idx = seq_idx * WINDOW_SIZE + pos_in_seq
        expected_emb = user_df.iloc[expected_row_idx][emb_cols].values.astype(np.float32)

        # Extract embedding from flattened result
        result_flat = results[seq_idx][:WINDOW_SIZE * dim]
        start = pos_in_seq * dim
        actual_emb = result_flat[start:start + dim].astype(np.float32)

        np.testing.assert_array_almost_equal(actual_emb, expected_emb)

    def test_same_poi_different_times_different_embeddings(self, data):
        """Two visits to same POI must produce different embeddings (checkin-level)."""
        dim = data["embedding_dim"]
        checkin_df = data["checkin_embeddings_time"]
        emb_cols = [str(d) for d in range(dim)]

        user_df = checkin_df[checkin_df["userid"] == 1].reset_index(drop=True)

        # Find two visits to the same POI
        poi_counts = user_df["placeid"].value_counts()
        repeated_poi = poi_counts[poi_counts > 1].index[0]
        visits = user_df[user_df["placeid"] == repeated_poi]

        emb_first = visits.iloc[0][emb_cols].values.astype(np.float32)
        emb_second = visits.iloc[1][emb_cols].values.astype(np.float32)

        # They must differ (row index encoded in dim 0)
        assert not np.array_equal(emb_first, emb_second)

    def test_target_category_from_correct_position(self, data):
        """Target category must come from position N * WINDOW_SIZE + WINDOW_SIZE."""
        dim = data["embedding_dim"]
        checkin_df = data["checkin_embeddings_time"]
        emb_cols = [str(d) for d in range(dim)]

        user_df = checkin_df[checkin_df["userid"] == 1].reset_index(drop=True)
        results, sequences = convert_user_checkins_to_sequences(
            user_df, emb_cols, WINDOW_SIZE, dim
        )

        # For sequence 0, target should be at position WINDOW_SIZE
        target_idx = WINDOW_SIZE
        if target_idx < len(user_df):
            expected_cat = user_df.iloc[target_idx]["category"]
            # Target category is second-to-last element
            actual_cat = results[0][-2]
            assert str(actual_cat) == str(expected_cat)


# ---------------------------------------------------------------------------
# Fusion category pipeline tests
# ---------------------------------------------------------------------------

class TestFusionCategoryPipeline:
    """Test EmbeddingAligner.align_poi_level + EmbeddingFuser for category task."""

    def _make_specs(self, dim):
        return (
            EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim),
            EmbeddingSpec(EmbeddingEngine.SPACE2VEC, EmbeddingLevel.POI, dim),
        )

    def test_two_poi_engines_alignment_and_fusion(self, data):
        dim = data["embedding_dim"]
        spec_hgi, spec_space = self._make_specs(dim)

        base_df = data["poi_embeddings_hgi"][["placeid"]].copy()
        base_df["category"] = base_df["placeid"].map(data["categories"])

        aligned = EmbeddingAligner.align_poi_level(
            base_df,
            [data["poi_embeddings_hgi"], data["poi_embeddings_space"]],
            [spec_hgi, spec_space],
        )

        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space])

        # Should have 2 * dim fused columns
        fused_cols = [f"fused_{i}" for i in range(2 * dim)]
        for col in fused_cols:
            assert col in fused.columns, f"Missing column {col}"

        assert len(fused) == len(data["poi_ids"])

    def test_fused_category_all_pois_present(self, data):
        dim = data["embedding_dim"]
        spec_hgi, spec_space = self._make_specs(dim)

        base_df = data["poi_embeddings_hgi"][["placeid"]].copy()
        base_df["category"] = base_df["placeid"].map(data["categories"])

        aligned = EmbeddingAligner.align_poi_level(
            base_df,
            [data["poi_embeddings_hgi"], data["poi_embeddings_space"]],
            [spec_hgi, spec_space],
        )
        assert set(aligned["placeid"].tolist()) == set(data["poi_ids"])

    def test_fused_values_match_sources(self, small_data):
        """fused_0..dim-1 must match HGI, fused_dim..2*dim-1 must match Space2Vec."""
        d = small_data
        dim = d["embedding_dim"]
        spec_hgi, spec_space = self._make_specs(dim)

        base_df = d["poi_embeddings_hgi"][["placeid"]].copy()
        base_df["category"] = base_df["placeid"].map(d["categories"])

        aligned = EmbeddingAligner.align_poi_level(
            base_df,
            [d["poi_embeddings_hgi"], d["poi_embeddings_space"]],
            [spec_hgi, spec_space],
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space])

        for pid in d["poi_ids"]:
            row = fused[fused["placeid"] == pid].iloc[0]
            expected_hgi = d["hgi_embs"][pid]
            expected_space = d["space_embs"][pid]

            for i in range(dim):
                assert abs(row[f"fused_{i}"] - expected_hgi[i]) < 1e-5, \
                    f"HGI mismatch for POI {pid} dim {i}"
                assert abs(row[f"fused_{dim + i}"] - expected_space[i]) < 1e-5, \
                    f"Space2Vec mismatch for POI {pid} dim {i}"


# ---------------------------------------------------------------------------
# Fusion next (POI-only) tests
# ---------------------------------------------------------------------------

class TestFusionNextPoiOnly:
    """Test fusion of two POI-level engines through sequence generation."""

    def test_two_poi_engines_next_pipeline(self, data):
        dim = data["embedding_dim"]
        total_dim = 2 * dim
        spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
        spec_space = EmbeddingSpec(EmbeddingEngine.SPACE2VEC, EmbeddingLevel.POI, dim)

        # Align + fuse at POI level
        base_df = data["poi_embeddings_hgi"][["placeid"]].copy()
        aligned = EmbeddingAligner.align_poi_level(
            base_df,
            [data["poi_embeddings_hgi"], data["poi_embeddings_space"]],
            [spec_hgi, spec_space],
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space])

        # Rename fused to numeric for create_embedding_lookup
        fused_renamed = fused.rename(columns={f"fused_{i}": str(i) for i in range(total_dim)})

        embedding_lookup = create_embedding_lookup(fused_renamed, total_dim)
        category_lookup = create_category_lookup(data["checkins_df"])

        # Generate sequences
        all_seqs = []
        for uid, udf in data["checkins_df"].groupby("userid"):
            for s in generate_sequences(udf["placeid"].tolist(), WINDOW_SIZE):
                all_seqs.append(s + [uid])

        seq_cols = [f"poi_{i}" for i in range(WINDOW_SIZE)] + ["target_poi", "userid"]
        sequences_df = pd.DataFrame(all_seqs, columns=seq_cols)

        results = convert_sequences_to_poi_embeddings(
            sequences_df, embedding_lookup, category_lookup,
            WINDOW_SIZE, total_dim, show_progress=False,
        )

        assert len(results) == len(sequences_df)
        expected_len = WINDOW_SIZE * total_dim + 2
        for r in results:
            assert len(r) == expected_len

    def test_same_poi_same_fused_embedding(self, small_data):
        """Dictionary lookup must return same fused vector for same POI."""
        d = small_data
        dim = d["embedding_dim"]
        total_dim = 2 * dim
        spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
        spec_space = EmbeddingSpec(EmbeddingEngine.SPACE2VEC, EmbeddingLevel.POI, dim)

        base_df = d["poi_embeddings_hgi"][["placeid"]].copy()
        aligned = EmbeddingAligner.align_poi_level(
            base_df,
            [d["poi_embeddings_hgi"], d["poi_embeddings_space"]],
            [spec_hgi, spec_space],
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space])
        fused_renamed = fused.rename(columns={f"fused_{i}": str(i) for i in range(total_dim)})

        embedding_lookup = create_embedding_lookup(fused_renamed, total_dim)

        # Same POI must always return identical vector
        pid = d["poi_ids"][0]
        emb1 = embedding_lookup[pid]
        emb2 = embedding_lookup[pid]
        np.testing.assert_array_equal(emb1, emb2)

        # And it should be the concatenation of HGI + Space2Vec
        expected = np.concatenate([d["hgi_embs"][pid], d["space_embs"][pid]])
        np.testing.assert_array_almost_equal(emb1, expected)


# ---------------------------------------------------------------------------
# Fusion next (mixed POI + checkin) tests — THE CRITICAL GAP
# ---------------------------------------------------------------------------

class TestFusionNextMixed:
    """Test mixed POI + checkin-level fusion through sequence generation.

    This is the most important test class — align_checkin_level was completely
    untested (skipped) in the existing test suite.
    """

    def _align_and_fuse(self, data):
        dim = data["embedding_dim"]
        spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
        spec_time = EmbeddingSpec(EmbeddingEngine.TIME2VEC, EmbeddingLevel.CHECKIN, dim)

        aligned = EmbeddingAligner.align_checkin_level(
            data["checkins_df"],
            [data["poi_embeddings_hgi"], data["checkin_embeddings_time"]],
            [spec_hgi, spec_time],
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_time])
        return fused, spec_hgi, spec_time

    def test_checkin_level_alignment_row_count(self, data):
        """Alignment must preserve original checkin row count."""
        fused, _, _ = self._align_and_fuse(data)
        assert len(fused) == len(data["checkins_df"])

    def test_checkin_level_alignment_hgi_consistent_for_same_poi(self, data):
        """HGI columns must be identical for all rows with the same placeid."""
        dim = data["embedding_dim"]
        fused, _, _ = self._align_and_fuse(data)
        hgi_cols = [f"fused_{i}" for i in range(dim)]

        for pid in data["poi_ids"]:
            rows = fused[fused["placeid"] == pid][hgi_cols]
            if len(rows) > 1:
                # All rows for same POI must have identical HGI embeddings
                first = rows.iloc[0].values
                for i in range(1, len(rows)):
                    np.testing.assert_array_almost_equal(
                        rows.iloc[i].values, first,
                        err_msg=f"HGI inconsistent for POI {pid} row {i}",
                    )

    def test_checkin_level_alignment_time2vec_varies_for_same_poi(self, data):
        """Time2Vec columns must differ for different visits to the same POI."""
        dim = data["embedding_dim"]
        fused, _, _ = self._align_and_fuse(data)
        time_cols = [f"fused_{dim + i}" for i in range(dim)]

        # Find a POI with multiple visits
        poi_counts = fused["placeid"].value_counts()
        repeated_poi = poi_counts[poi_counts > 1].index[0]

        rows = fused[fused["placeid"] == repeated_poi][time_cols]
        # At least two rows should differ (they encode different row indices)
        emb_first = rows.iloc[0].values
        emb_second = rows.iloc[1].values
        assert not np.array_equal(emb_first, emb_second), \
            f"Time2Vec should differ for different visits to POI {repeated_poi}"

    def test_mixed_fusion_then_sequence_generation(self, data):
        """After alignment+fusion, convert_user_checkins_to_sequences must work correctly."""
        dim = data["embedding_dim"]
        total_dim = 2 * dim
        fused, _, _ = self._align_and_fuse(data)
        fused_cols = [f"fused_{i}" for i in range(total_dim)]

        # Process user 1
        user_fused = fused[fused["userid"] == 1].reset_index(drop=True)
        results, sequences = convert_user_checkins_to_sequences(
            user_fused, fused_cols, WINDOW_SIZE, total_dim
        )

        assert len(results) > 0

        # Verify position-based lookup: seq 0, pos 2 should match user_fused.iloc[2]
        expected_emb = user_fused.iloc[2][fused_cols].values.astype(np.float32)
        result_flat = results[0][:WINDOW_SIZE * total_dim]
        actual_emb = result_flat[2 * total_dim:3 * total_dim].astype(np.float32)
        np.testing.assert_array_almost_equal(actual_emb, expected_emb)

    def test_hgi_part_consistent_in_fused_sequences(self, small_data):
        """In generated sequences, HGI portion must be same for same POI."""
        d = small_data
        dim = d["embedding_dim"]
        total_dim = 2 * dim

        spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
        spec_time = EmbeddingSpec(EmbeddingEngine.TIME2VEC, EmbeddingLevel.CHECKIN, dim)

        aligned = EmbeddingAligner.align_checkin_level(
            d["checkins_df"],
            [d["poi_embeddings_hgi"], d["checkin_embeddings_time"]],
            [spec_hgi, spec_time],
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_time])
        fused_cols = [f"fused_{i}" for i in range(total_dim)]

        user_fused = fused[fused["userid"] == 1].reset_index(drop=True)
        results, sequences = convert_user_checkins_to_sequences(
            user_fused, fused_cols, WINDOW_SIZE, total_dim
        )

        # Collect HGI sub-vectors per POI across all sequences
        poi_hgi_vectors = {}
        for seq_idx, (seq, result) in enumerate(zip(sequences, results)):
            flat = result[:WINDOW_SIZE * total_dim].astype(np.float32)
            for pos in range(WINDOW_SIZE):
                poi_id = seq[pos]
                if poi_id == PADDING_VALUE:
                    continue
                start = pos * total_dim
                hgi_part = flat[start:start + dim]

                if poi_id not in poi_hgi_vectors:
                    poi_hgi_vectors[poi_id] = hgi_part
                else:
                    np.testing.assert_array_almost_equal(
                        hgi_part, poi_hgi_vectors[poi_id],
                        err_msg=f"HGI inconsistent for POI {poi_id} in seq {seq_idx} pos {pos}",
                    )

    def test_time2vec_part_varies_in_fused_sequences(self, small_data):
        """In generated sequences, Time2Vec portion must differ for different visits to same POI."""
        d = small_data
        dim = d["embedding_dim"]
        total_dim = 2 * dim

        spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
        spec_time = EmbeddingSpec(EmbeddingEngine.TIME2VEC, EmbeddingLevel.CHECKIN, dim)

        aligned = EmbeddingAligner.align_checkin_level(
            d["checkins_df"],
            [d["poi_embeddings_hgi"], d["checkin_embeddings_time"]],
            [spec_hgi, spec_time],
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_time])
        fused_cols = [f"fused_{i}" for i in range(total_dim)]

        user_fused = fused[fused["userid"] == 1].reset_index(drop=True)
        results, sequences = convert_user_checkins_to_sequences(
            user_fused, fused_cols, WINDOW_SIZE, total_dim
        )

        # Collect Time2Vec sub-vectors per POI
        poi_time_vectors = {}  # poi_id -> list of time2vec vectors
        for seq_idx, (seq, result) in enumerate(zip(sequences, results)):
            flat = result[:WINDOW_SIZE * total_dim].astype(np.float32)
            for pos in range(WINDOW_SIZE):
                poi_id = seq[pos]
                if poi_id == PADDING_VALUE:
                    continue
                start = pos * total_dim + dim  # skip HGI part
                time_part = flat[start:start + dim]
                poi_time_vectors.setdefault(poi_id, []).append(time_part)

        # At least one POI must have varying Time2Vec embeddings
        found_variation = False
        for pid, vecs in poi_time_vectors.items():
            if len(vecs) > 1:
                if not np.array_equal(vecs[0], vecs[1]):
                    found_variation = True
                    break

        assert found_variation, "Expected Time2Vec to vary for same POI across different visits"


# ---------------------------------------------------------------------------
# Fusion alignment invariants
# ---------------------------------------------------------------------------

class TestFusionAlignmentInvariants:
    """Cross-cutting invariant checks for alignment correctness."""

    def test_alignment_no_nan_when_all_pois_present(self, data):
        """When all POIs have embeddings, aligned result should have no NaN."""
        dim = data["embedding_dim"]
        spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
        spec_time = EmbeddingSpec(EmbeddingEngine.TIME2VEC, EmbeddingLevel.CHECKIN, dim)

        aligned = EmbeddingAligner.align_checkin_level(
            data["checkins_df"],
            [data["poi_embeddings_hgi"], data["checkin_embeddings_time"]],
            [spec_hgi, spec_time],
        )

        hgi_cols = [f"hgi_{i}" for i in range(dim)]
        time_cols = [f"time2vec_{i}" for i in range(dim)]
        all_emb_cols = hgi_cols + time_cols

        nan_count = aligned[all_emb_cols].isna().sum().sum()
        assert nan_count == 0, f"Found {nan_count} NaN values in aligned embeddings"

    def test_poi_level_fusion_groupby_invariant(self, data):
        """For POI-only fusion: group by placeid, all fused embeddings in group must be identical."""
        dim = data["embedding_dim"]
        total_dim = 2 * dim
        spec_hgi = EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, dim)
        spec_space = EmbeddingSpec(EmbeddingEngine.SPACE2VEC, EmbeddingLevel.POI, dim)

        # Merge POI embeddings onto checkins (to get repeated POIs)
        checkins = data["checkins_df"].copy()
        aligned = EmbeddingAligner.align_poi_level(
            checkins,
            [data["poi_embeddings_hgi"], data["poi_embeddings_space"]],
            [spec_hgi, spec_space],
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space])
        fused_cols = [f"fused_{i}" for i in range(total_dim)]

        # Group by placeid: all rows in each group must have identical fused embeddings
        for pid, group in fused.groupby("placeid"):
            if len(group) > 1:
                first_row = group.iloc[0][fused_cols].values
                for i in range(1, len(group)):
                    np.testing.assert_array_almost_equal(
                        group.iloc[i][fused_cols].values, first_row,
                        err_msg=f"Fused embedding inconsistent for POI {pid}",
                    )
