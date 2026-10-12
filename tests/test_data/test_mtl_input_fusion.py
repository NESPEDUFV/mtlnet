"""
Integration tests for multi-embedding fusion.

Tests:
- EmbeddingAligner (POI-level and check-in-level)
- EmbeddingFuser
- End-to-end category fusion
- End-to-end next-POI fusion (both POI-level and check-in-level paths)
- Bug regression tests
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from pathlib import Path

from data.inputs.fusion import EmbeddingAligner, EmbeddingFuser, MultiEmbeddingInputGenerator
from data.inputs.core import (
    generate_sequences,
    convert_sequences_to_poi_embeddings,
    convert_user_checkins_to_sequences,
    create_embedding_lookup,
    create_category_lookup,
    PADDING_VALUE,
    MISSING_CATEGORY_VALUE,
)
from configs.embedding_fusion import EmbeddingSpec, EmbeddingLevel, FusionConfig
from configs.paths import EmbeddingEngine


# ============================================================================
# Synthetic Data Helpers
# ============================================================================

def make_checkins_df(user_visits):
    """
    Create a check-ins DataFrame from user visit specifications.

    Args:
        user_visits: dict of {userid: [(placeid, category, datetime_str), ...]}

    Returns:
        DataFrame with columns [userid, placeid, category, datetime],
        sorted by (userid, datetime).
    """
    rows = []
    for userid, visits in user_visits.items():
        for placeid, category, dt_str in visits:
            rows.append({
                'userid': userid,
                'placeid': placeid,
                'category': category,
                'datetime': pd.Timestamp(dt_str),
            })
    df = pd.DataFrame(rows)
    df = df.sort_values(['userid', 'datetime']).reset_index(drop=True)
    return df


def make_poi_embedding_df(poi_values, dim):
    """
    Create a POI-level embedding DataFrame.

    Args:
        poi_values: dict of {placeid: [emb_0, emb_1, ...]}
        dim: embedding dimension

    Returns:
        DataFrame with columns [placeid, category, 0, 1, ..., dim-1]
    """
    rows = []
    for placeid, values in poi_values.items():
        row = {'placeid': placeid, 'category': f'cat_{placeid}'}
        for j in range(dim):
            row[str(j)] = float(values[j])
        rows.append(row)
    return pd.DataFrame(rows)


def make_checkin_embedding_df(checkins_df, dim, seed=0):
    """
    Create a check-in-level embedding DataFrame aligned to checkins_df.

    Embeddings encode row position: emb[row][j] = seed + row*100 + j
    This makes it trivial to trace which row's embedding ended up where.

    Args:
        checkins_df: base check-ins DataFrame
        dim: embedding dimension
        seed: offset for embedding values

    Returns:
        DataFrame with columns [userid, placeid, datetime, category, 0, 1, ..., dim-1]
    """
    df = checkins_df[['userid', 'placeid', 'datetime', 'category']].copy()
    for j in range(dim):
        df[str(j)] = [float(seed + row * 100 + j) for row in range(len(df))]
    return df


# ============================================================================
# EmbeddingAligner Tests — POI Level
# ============================================================================

class TestEmbeddingAlignerPOI:
    """Test suite for EmbeddingAligner.align_poi_level."""

    def test_align_poi_level_basic(self):
        """Should align multiple POI-level embeddings by placeid."""
        base_df = pd.DataFrame({
            'placeid': [10, 11, 12],
            'category': ['Food', 'Shop', 'Cafe']
        })

        emb1_df = pd.DataFrame({
            'placeid': [10, 11, 12],
            '0': [1.0, 2.0, 3.0],
            '1': [4.0, 5.0, 6.0]
        })

        emb2_df = pd.DataFrame({
            'placeid': [10, 11, 12],
            '0': [7.0, 8.0, 9.0],
            '1': [10.0, 11.0, 12.0]
        })

        spec1 = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)
        spec2 = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=2, level=EmbeddingLevel.POI)

        result = EmbeddingAligner.align_poi_level(
            base_df, [emb1_df, emb2_df], [spec1, spec2]
        )

        assert len(result) == 3
        assert 'hgi_0' in result.columns
        assert 'hgi_1' in result.columns
        assert 'space2vec_0' in result.columns
        assert 'space2vec_1' in result.columns

    def test_align_poi_level_missing_data(self):
        """Should handle missing POIs gracefully (NaN for unmatched)."""
        base_df = pd.DataFrame({
            'placeid': [10, 11, 12, 13],
            'category': ['Food', 'Shop', 'Cafe', 'Park']
        })

        emb_df = pd.DataFrame({
            'placeid': [10, 11, 12],
            '0': [1.0, 2.0, 3.0]
        })

        spec = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        result = EmbeddingAligner.align_poi_level(base_df, [emb_df], [spec])

        assert len(result) == 4
        assert pd.isna(result[result['placeid'] == 13]['hgi_0'].iloc[0])

    def test_align_poi_level_preserves_order(self):
        """Should preserve order from base DataFrame."""
        base_df = pd.DataFrame({
            'placeid': [12, 10, 11],
            'category': ['Cafe', 'Food', 'Shop']
        })

        emb_df = pd.DataFrame({
            'placeid': [10, 11, 12],
            '0': [1.0, 2.0, 3.0]
        })

        spec = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        result = EmbeddingAligner.align_poi_level(base_df, [emb_df], [spec])

        assert result['placeid'].tolist() == [12, 10, 11]
        assert result['hgi_0'].iloc[0] == 3.0  # placeid 12
        assert result['hgi_0'].iloc[1] == 1.0  # placeid 10
        assert result['hgi_0'].iloc[2] == 2.0  # placeid 11

    def test_align_poi_level_deduplicates_identical_rows(self):
        """Identical duplicate rows should be silently deduplicated."""
        base_df = pd.DataFrame({
            'placeid': [10, 11],
            'category': ['Food', 'Shop']
        })

        emb_df = pd.DataFrame({
            'placeid': [10, 10, 11],  # duplicate POI 10 with SAME embedding
            '0': [1.0, 1.0, 2.0]
        })

        spec = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        # Should succeed (identical duplicates are deduplicated)
        result = EmbeddingAligner.align_poi_level(base_df, [emb_df], [spec])
        assert len(result) == 2
        assert result[result['placeid'] == 10]['hgi_0'].iloc[0] == 1.0

    def test_align_poi_level_rejects_conflicting_duplicate_placeids(self):
        """Bug 3: Should reject embeddings with same placeid but different values."""
        base_df = pd.DataFrame({
            'placeid': [10, 11],
            'category': ['Food', 'Shop']
        })

        emb_df = pd.DataFrame({
            'placeid': [10, 10, 11],  # duplicate POI 10 with DIFFERENT embeddings
            '0': [1.0, 1.5, 2.0]
        })

        spec = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        with pytest.raises(ValueError, match="duplicate"):
            EmbeddingAligner.align_poi_level(base_df, [emb_df], [spec])


# ============================================================================
# EmbeddingAligner Tests — Check-in Level
# ============================================================================

class TestEmbeddingAlignerCheckin:
    """Test suite for EmbeddingAligner.align_checkin_level."""

    def test_align_checkin_level_poi_and_checkin_mixed(self):
        """Mixed POI + CHECKIN: same POI at different times gets same HGI but different Time2Vec."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
                (10, 'Food', '2023-01-01 12:00'),  # same POI, different time
            ]
        })

        # HGI: POI-level (same embedding regardless of time)
        hgi_df = pd.DataFrame({
            'placeid': [10, 11],
            '0': [1.0, 2.0],
            '1': [3.0, 4.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)

        # Time2Vec: check-in-level (unique per visit)
        t2v_df = make_checkin_embedding_df(checkins_df, dim=2, seed=100)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        result = EmbeddingAligner.align_checkin_level(
            checkins_df, [hgi_df, t2v_df], [spec_hgi, spec_t2v]
        )

        assert len(result) == 3  # no row multiplication

        # POI 10 at row 0 and row 2: same HGI, different Time2Vec
        row0 = result.iloc[0]
        row2 = result.iloc[2]

        # Same HGI embedding (POI 10)
        assert row0['hgi_0'] == 1.0
        assert row2['hgi_0'] == 1.0
        assert row0['hgi_1'] == 3.0
        assert row2['hgi_1'] == 3.0

        # Different Time2Vec embeddings (different check-in times)
        assert row0['time2vec_0'] != row2['time2vec_0']

    def test_align_checkin_level_preserves_sort_order(self):
        """After merge, chronological order must be preserved."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
                (12, 'Cafe', '2023-01-01 12:00'),
            ],
            2: [
                (10, 'Food', '2023-01-01 09:00'),
                (13, 'Park', '2023-01-01 10:00'),
            ]
        })

        t2v_df = make_checkin_embedding_df(checkins_df, dim=2, seed=0)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        original_order = checkins_df[['userid', 'placeid', 'datetime']].values.tolist()

        result = EmbeddingAligner.align_checkin_level(
            checkins_df, [t2v_df], [spec_t2v]
        )

        result_order = result[['userid', 'placeid', 'datetime']].values.tolist()
        assert original_order == result_order

    def test_align_checkin_level_no_duplicate_rows(self):
        """N input rows must produce exactly N output rows."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        t2v_df = make_checkin_embedding_df(checkins_df, dim=2, seed=0)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        hgi_df = pd.DataFrame({
            'placeid': [10, 11],
            '0': [1.0, 2.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        result = EmbeddingAligner.align_checkin_level(
            checkins_df, [t2v_df, hgi_df], [spec_t2v, spec_hgi]
        )

        assert len(result) == len(checkins_df)

    def test_align_checkin_level_missing_checkin(self):
        """Missing check-in in embedding → NaN in those columns."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
                (12, 'Cafe', '2023-01-01 12:00'),
            ]
        })

        # Time2Vec only has 2 of the 3 check-ins
        t2v_df = make_checkin_embedding_df(checkins_df.iloc[:2], dim=2, seed=0)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        result = EmbeddingAligner.align_checkin_level(
            checkins_df, [t2v_df], [spec_t2v]
        )

        assert len(result) == 3
        # Row 2 (missing) should have NaN
        assert pd.isna(result.iloc[2]['time2vec_0'])
        assert pd.isna(result.iloc[2]['time2vec_1'])
        # Rows 0,1 should have values
        assert not pd.isna(result.iloc[0]['time2vec_0'])
        assert not pd.isna(result.iloc[1]['time2vec_0'])

    def test_align_checkin_level_deduplicates_identical_composite_keys(self):
        """Identical duplicate check-in rows should be silently deduplicated."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        # Duplicate row 0 with identical embeddings
        t2v_df = make_checkin_embedding_df(checkins_df, dim=2, seed=0)
        t2v_df = pd.concat([t2v_df, t2v_df.iloc[[0]]], ignore_index=True)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        # Should succeed (identical duplicates are deduplicated)
        result = EmbeddingAligner.align_checkin_level(
            checkins_df, [t2v_df], [spec_t2v]
        )
        assert len(result) == 2

    def test_align_checkin_level_rejects_conflicting_composite_keys(self):
        """Bug 3: Should reject check-in embeddings with same key but different values."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        t2v_df = make_checkin_embedding_df(checkins_df, dim=2, seed=0)
        # Add a row with same key but different embedding values
        conflict_row = t2v_df.iloc[[0]].copy()
        conflict_row['0'] = 999.0  # different value
        t2v_df = pd.concat([t2v_df, conflict_row], ignore_index=True)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        with pytest.raises(ValueError, match="DIFFERENT"):
            EmbeddingAligner.align_checkin_level(
                checkins_df, [t2v_df], [spec_t2v]
            )

    def test_align_checkin_level_deduplicates_identical_poi_placeids(self):
        """Identical duplicate POI rows should be silently deduplicated."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        hgi_df = pd.DataFrame({
            'placeid': [10, 10, 11],  # duplicate with SAME embedding
            '0': [1.0, 1.0, 2.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        result = EmbeddingAligner.align_checkin_level(
            checkins_df, [hgi_df], [spec_hgi]
        )
        assert len(result) == 2

    def test_align_checkin_level_rejects_conflicting_poi_placeids(self):
        """Bug 3: Should reject POI embeddings with same placeid but different values."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        hgi_df = pd.DataFrame({
            'placeid': [10, 10, 11],  # duplicate with DIFFERENT embeddings
            '0': [1.0, 1.5, 2.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        with pytest.raises(ValueError, match="DIFFERENT"):
            EmbeddingAligner.align_checkin_level(
                checkins_df, [hgi_df], [spec_hgi]
            )


# ============================================================================
# EmbeddingFuser Tests
# ============================================================================

class TestEmbeddingFuser:
    """Test suite for EmbeddingFuser class."""

    def test_fuse_embeddings_basic(self):
        """Should concatenate embeddings from multiple sources."""
        df = pd.DataFrame({
            'placeid': [10, 11, 12],
            'hgi_0': [1.0, 2.0, 3.0],
            'hgi_1': [4.0, 5.0, 6.0],
            'space2vec_0': [7.0, 8.0, 9.0],
            'space2vec_1': [10.0, 11.0, 12.0]
        })

        spec1 = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)
        spec2 = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=2, level=EmbeddingLevel.POI)

        result = EmbeddingFuser.fuse_embeddings(df, [spec1, spec2], output_prefix='fused')

        assert 'fused_0' in result.columns
        assert 'fused_1' in result.columns
        assert 'fused_2' in result.columns
        assert 'fused_3' in result.columns

        assert result['fused_0'].iloc[0] == 1.0  # hgi_0
        assert result['fused_2'].iloc[0] == 7.0  # space2vec_0

    def test_fuse_handles_missing_values(self):
        """Should fill missing values with zeros."""
        df = pd.DataFrame({
            'hgi_0': [1.0, 2.0, np.nan],
            'hgi_1': [4.0, 5.0, 6.0]
        })

        spec = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)

        result = EmbeddingFuser.fuse_embeddings(df, [spec], output_prefix='fused')
        assert result['fused_0'].iloc[2] == 0.0

    def test_fuse_concatenation_order(self):
        """Should concatenate in the order of specs."""
        df = pd.DataFrame({
            'hgi_0': [1.0],
            'space2vec_0': [2.0],
            'time2vec_0': [3.0]
        })

        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)
        spec_space = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=1, level=EmbeddingLevel.POI)
        spec_time = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=1, level=EmbeddingLevel.CHECKIN)

        # Order: time2vec, hgi, space2vec
        result = EmbeddingFuser.fuse_embeddings(
            df, [spec_time, spec_hgi, spec_space], output_prefix='fused'
        )

        assert result['fused_0'].iloc[0] == 3.0  # time2vec_0
        assert result['fused_1'].iloc[0] == 1.0  # hgi_0
        assert result['fused_2'].iloc[0] == 2.0  # space2vec_0

    def test_fuse_preserves_non_embedding_columns(self):
        """Should preserve original non-embedding columns."""
        df = pd.DataFrame({
            'placeid': [10, 11, 12],
            'category': ['Food', 'Shop', 'Cafe'],
            'hgi_0': [1.0, 2.0, 3.0],
            'hgi_1': [4.0, 5.0, 6.0]
        })

        spec = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)

        result = EmbeddingFuser.fuse_embeddings(df, [spec], output_prefix='fused')

        assert 'placeid' in result.columns
        assert 'category' in result.columns
        assert result['placeid'].tolist() == [10, 11, 12]

    def test_fuse_drops_original_embedding_columns(self):
        """Original embedding columns should be renamed (not present under old name)."""
        df = pd.DataFrame({
            'placeid': [10],
            'hgi_0': [1.0],
            'hgi_1': [2.0]
        })

        spec = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)

        result = EmbeddingFuser.fuse_embeddings(df, [spec], output_prefix='fused')

        assert 'hgi_0' not in result.columns
        assert 'hgi_1' not in result.columns
        assert 'fused_0' in result.columns
        assert 'fused_1' in result.columns

    def test_fuse_different_dimensions(self):
        """Should handle embeddings with different dimensions."""
        df = pd.DataFrame({
            'hgi_0': [1.0],
            'hgi_1': [2.0],
            'hgi_2': [3.0],
            'space2vec_0': [4.0],
            'space2vec_1': [5.0]
        })

        spec1 = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=3, level=EmbeddingLevel.POI)
        spec2 = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=2, level=EmbeddingLevel.POI)

        result = EmbeddingFuser.fuse_embeddings(df, [spec1, spec2], output_prefix='fused')

        assert 'fused_4' in result.columns
        assert 'fused_5' not in result.columns

        assert result['fused_0'].iloc[0] == 1.0  # hgi_0
        assert result['fused_2'].iloc[0] == 3.0  # hgi_2
        assert result['fused_3'].iloc[0] == 4.0  # space2vec_0

    def test_fuse_empty_specs_returns_original(self):
        """Should return original DataFrame if no specs provided."""
        df = pd.DataFrame({'placeid': [10], 'category': ['Food']})
        result = EmbeddingFuser.fuse_embeddings(df, [], output_prefix='fused')
        assert result.equals(df)


# ============================================================================
# Category Fusion End-to-End Tests
# ============================================================================

class TestCategoryFusionEndToEnd:
    """End-to-end tests for category task fusion."""

    def test_category_fusion_exact_values(self):
        """Verify exact concatenated embedding values for each POI."""
        # HGI: dim=2
        hgi_df = make_poi_embedding_df({
            10: [1.0, 2.0],
            11: [3.0, 4.0],
            12: [5.0, 6.0],
        }, dim=2)

        # Space2Vec: dim=2
        space_df = make_poi_embedding_df({
            10: [7.0, 8.0],
            11: [9.0, 10.0],
            12: [11.0, 12.0],
        }, dim=2)

        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)
        spec_space = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=2, level=EmbeddingLevel.POI)

        # Step 1: Align
        base_df = hgi_df[['placeid', 'category']].copy()
        aligned = EmbeddingAligner.align_poi_level(
            base_df, [hgi_df, space_df], [spec_hgi, spec_space]
        )

        # Step 2: Fuse
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space])

        # Step 3: Extract final columns (like generate_category_input does)
        total_dim = 4
        final_cols = ['placeid', 'category'] + [f'fused_{i}' for i in range(total_dim)]
        output = fused[final_cols]

        # Verify POI 10: [hgi_0=1.0, hgi_1=2.0, space_0=7.0, space_1=8.0]
        poi10 = output[output['placeid'] == 10].iloc[0]
        assert poi10['fused_0'] == 1.0
        assert poi10['fused_1'] == 2.0
        assert poi10['fused_2'] == 7.0
        assert poi10['fused_3'] == 8.0

        # Verify POI 12: [hgi_0=5.0, hgi_1=6.0, space_0=11.0, space_1=12.0]
        poi12 = output[output['placeid'] == 12].iloc[0]
        assert poi12['fused_0'] == 5.0
        assert poi12['fused_1'] == 6.0
        assert poi12['fused_2'] == 11.0
        assert poi12['fused_3'] == 12.0

    def test_category_fusion_missing_poi_in_secondary(self):
        """POI missing in secondary embedding gets zero-filled."""
        hgi_df = make_poi_embedding_df({
            10: [1.0, 2.0],
            11: [3.0, 4.0],
            12: [5.0, 6.0],
        }, dim=2)

        space_df = make_poi_embedding_df({
            10: [7.0, 8.0],
            11: [9.0, 10.0],
            # POI 12 missing from Space2Vec
        }, dim=2)

        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)
        spec_space = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=2, level=EmbeddingLevel.POI)

        base_df = hgi_df[['placeid', 'category']].copy()
        aligned = EmbeddingAligner.align_poi_level(
            base_df, [hgi_df, space_df], [spec_hgi, spec_space]
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space])

        assert len(fused) == 3  # All 3 POIs present

        # POI 12: HGI values preserved, Space2Vec zero-filled
        poi12 = fused[fused['placeid'] == 12].iloc[0]
        assert poi12['fused_0'] == 5.0  # hgi_0
        assert poi12['fused_1'] == 6.0  # hgi_1
        assert poi12['fused_2'] == 0.0  # space_0 (zero-filled)
        assert poi12['fused_3'] == 0.0  # space_1 (zero-filled)

    def test_category_fusion_missing_poi_in_primary(self):
        """POI only in secondary is dropped (left join on first embedding)."""
        hgi_df = make_poi_embedding_df({
            10: [1.0, 2.0],
            11: [3.0, 4.0],
            # POI 12 NOT in primary
        }, dim=2)

        space_df = make_poi_embedding_df({
            10: [7.0, 8.0],
            11: [9.0, 10.0],
            12: [11.0, 12.0],  # POI 12 only in secondary
        }, dim=2)

        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)
        spec_space = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=2, level=EmbeddingLevel.POI)

        base_df = hgi_df[['placeid', 'category']].copy()
        aligned = EmbeddingAligner.align_poi_level(
            base_df, [hgi_df, space_df], [spec_hgi, spec_space]
        )

        # Only 2 POIs (12 dropped because it's not in the base/primary)
        assert len(aligned) == 2
        assert 12 not in aligned['placeid'].values


# ============================================================================
# Next-POI Fusion End-to-End — POI Level Path
# ============================================================================

class TestNextPOILevelEndToEnd:
    """End-to-end tests for next-POI fusion with all POI-level embeddings."""

    def test_next_poi_level_end_to_end(self):
        """
        Full trace: alignment → fusion → sequence → lookup → verify exact output vectors.

        Uses window_size=3, 2 POI engines (HGI dim=2, Space2Vec dim=1), total dim=3.
        """
        window_size = 3
        total_dim = 3

        # User 1: visits POIs 10, 11, 12, 10 (7 visits total for 2 sequences)
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
                (12, 'Cafe', '2023-01-01 12:00'),
                (10, 'Food', '2023-01-01 13:00'),
                (13, 'Park', '2023-01-01 14:00'),
                (14, 'Gym',  '2023-01-01 15:00'),
                (15, 'Bar',  '2023-01-01 16:00'),
            ]
        })

        # HGI: dim=2
        hgi_df = pd.DataFrame({
            'placeid': [10, 11, 12, 13, 14, 15],
            '0': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            '1': [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)

        # Space2Vec: dim=1
        space_df = pd.DataFrame({
            'placeid': [10, 11, 12, 13, 14, 15],
            '0': [100.0, 200.0, 300.0, 400.0, 500.0, 600.0],
        })
        spec_space = EmbeddingSpec(engine=EmbeddingEngine.SPACE2VEC, dimension=1, level=EmbeddingLevel.POI)

        # Step 1: Align (checkin-level aligner with all-POI specs)
        aligned = EmbeddingAligner.align_checkin_level(
            checkins_df, [hgi_df, space_df], [spec_hgi, spec_space]
        )

        # Step 2: Fuse
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi, spec_space], output_prefix='fused')

        # Step 3: Build POI embedding lookup (like _generate_next_input_poi_level does)
        fused_cols = [f'fused_{i}' for i in range(total_dim)]
        poi_embeddings = fused.groupby('placeid')[fused_cols].first()
        renamed = poi_embeddings.rename(columns={
            f'fused_{i}': str(i) for i in range(total_dim)
        }).reset_index()

        embedding_lookup = create_embedding_lookup(renamed, total_dim)
        category_lookup = create_category_lookup(fused)

        # Step 4: Generate sequences
        user_seqs = []
        for userid, user_df in fused.groupby('userid'):
            places = user_df['placeid'].tolist()
            seqs = generate_sequences(places, window_size=window_size)
            for seq in seqs:
                user_seqs.append(seq + [userid])

        seq_cols = [f'poi_{i}' for i in range(window_size)] + ['target_poi', 'userid']
        seq_df = pd.DataFrame(user_seqs, columns=seq_cols)

        # Step 5: Convert to embeddings
        results = convert_sequences_to_poi_embeddings(
            seq_df, embedding_lookup, category_lookup,
            window_size, total_dim, show_progress=False
        )

        assert len(results) > 0

        # Verify first sequence
        first = results[0]
        emb_part = first[:window_size * total_dim].astype(np.float32)

        # First sequence should be [POI 10, POI 11, POI 12], target=POI 10
        # POI 10 fused: [hgi_0=1.0, hgi_1=10.0, space_0=100.0]
        # POI 11 fused: [hgi_0=2.0, hgi_1=20.0, space_0=200.0]
        # POI 12 fused: [hgi_0=3.0, hgi_1=30.0, space_0=300.0]
        expected = np.array([1.0, 10.0, 100.0, 2.0, 20.0, 200.0, 3.0, 30.0, 300.0], dtype=np.float32)
        np.testing.assert_array_almost_equal(emb_part, expected)

    def test_next_poi_level_same_poi_same_embedding(self):
        """Same POI appearing in multiple sequences must get identical embedding."""
        window_size = 3
        total_dim = 2

        # POI 10 appears in both windows
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
                (12, 'Cafe', '2023-01-01 12:00'),
                (10, 'Food', '2023-01-01 13:00'),  # repeat
                (13, 'Park', '2023-01-01 14:00'),
                (14, 'Gym',  '2023-01-01 15:00'),
                (15, 'Bar',  '2023-01-01 16:00'),
            ]
        })

        hgi_df = pd.DataFrame({
            'placeid': [10, 11, 12, 13, 14, 15],
            '0': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            '1': [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)

        aligned = EmbeddingAligner.align_checkin_level(
            checkins_df, [hgi_df], [spec_hgi]
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi], output_prefix='fused')

        fused_cols = [f'fused_{i}' for i in range(total_dim)]
        poi_emb = fused.groupby('placeid')[fused_cols].first()
        renamed = poi_emb.rename(columns={
            f'fused_{i}': str(i) for i in range(total_dim)
        }).reset_index()

        embedding_lookup = create_embedding_lookup(renamed, total_dim)
        category_lookup = create_category_lookup(fused)

        user_seqs = []
        for userid, user_df in fused.groupby('userid'):
            places = user_df['placeid'].tolist()
            seqs = generate_sequences(places, window_size=window_size)
            for seq in seqs:
                user_seqs.append(seq + [userid])

        seq_cols = [f'poi_{i}' for i in range(window_size)] + ['target_poi', 'userid']
        seq_df = pd.DataFrame(user_seqs, columns=seq_cols)

        results = convert_sequences_to_poi_embeddings(
            seq_df, embedding_lookup, category_lookup,
            window_size, total_dim, show_progress=False
        )

        # POI 10 in seq 0 pos 0 and seq 1 pos 0 should have identical embeddings
        seq0_emb = results[0][:total_dim].astype(np.float32)
        seq1_emb = results[1][:total_dim].astype(np.float32)
        np.testing.assert_array_equal(seq0_emb, seq1_emb)


# ============================================================================
# Next-POI Fusion End-to-End — Check-in Level Path
# ============================================================================

class TestNextCheckinLevelEndToEnd:
    """End-to-end tests for next-POI fusion with check-in-level embeddings."""

    def test_next_checkin_level_end_to_end(self):
        """
        Full trace with mixed POI + check-in embeddings.

        POI 10 appears at different times with DIFFERENT Time2Vec embeddings.
        Position-based lookup must give different fused vectors for each occurrence.
        """
        window_size = 3
        total_dim = 2  # HGI dim=1 + Time2Vec dim=1

        # User visits POI 10 at t1 and t4 (repeated POI, different times)
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),   # row 0
                (11, 'Shop', '2023-01-01 11:00'),   # row 1
                (12, 'Cafe', '2023-01-01 12:00'),   # row 2
                (10, 'Food', '2023-01-01 13:00'),   # row 3 (repeat POI 10!)
                (13, 'Park', '2023-01-01 14:00'),   # row 4
                (14, 'Gym',  '2023-01-01 15:00'),   # row 5
                (15, 'Bar',  '2023-01-01 16:00'),   # row 6
            ]
        })

        # HGI (POI-level, dim=1): same embedding regardless of visit time
        hgi_df = pd.DataFrame({
            'placeid': [10, 11, 12, 13, 14, 15],
            '0': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        # Time2Vec (check-in-level, dim=1): unique per visit
        # emb[row][0] = row * 10.0 for easy tracing
        t2v_df = checkins_df[['userid', 'placeid', 'datetime', 'category']].copy()
        t2v_df['0'] = [row * 10.0 for row in range(len(t2v_df))]
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=1, level=EmbeddingLevel.CHECKIN)

        # Step 1: Align
        aligned = EmbeddingAligner.align_checkin_level(
            checkins_df, [hgi_df, t2v_df], [spec_hgi, spec_t2v]
        )
        assert len(aligned) == 7  # no row multiplication

        # Step 2: Fuse
        fused = EmbeddingFuser.fuse_embeddings(
            aligned, [spec_hgi, spec_t2v], output_prefix='fused'
        )

        # Verify fused values at row 0 and row 3 (both POI 10)
        row0 = fused.iloc[0]
        row3 = fused.iloc[3]
        assert row0['fused_0'] == 1.0   # HGI for POI 10
        assert row3['fused_0'] == 1.0   # HGI for POI 10 (same)
        assert row0['fused_1'] == 0.0   # Time2Vec for row 0 = 0*10
        assert row3['fused_1'] == 30.0  # Time2Vec for row 3 = 3*10

        # Step 3: Position-based conversion per user
        fused_cols = [f'fused_{i}' for i in range(total_dim)]
        all_results = []
        for userid, user_df in fused.groupby('userid'):
            user_df = user_df.reset_index(drop=True)
            results, sequences = convert_user_checkins_to_sequences(
                user_df, fused_cols, window_size, total_dim
            )
            all_results.extend(results)

        assert len(all_results) >= 2

        # Sequence 0: rows 0,1,2 → target at row 3
        seq0 = all_results[0]
        emb0 = seq0[:window_size * total_dim].astype(np.float32)
        # Expected: [hgi(POI10), t2v(row0), hgi(POI11), t2v(row1), hgi(POI12), t2v(row2)]
        #         = [1.0, 0.0, 2.0, 10.0, 3.0, 20.0]
        expected0 = np.array([1.0, 0.0, 2.0, 10.0, 3.0, 20.0], dtype=np.float32)
        np.testing.assert_array_almost_equal(emb0, expected0)

        # Sequence 1: rows 3,4,5 → target at row 6
        seq1 = all_results[1]
        emb1 = seq1[:window_size * total_dim].astype(np.float32)
        # Expected: [hgi(POI10), t2v(row3), hgi(POI13), t2v(row4), hgi(POI14), t2v(row5)]
        #         = [1.0, 30.0, 4.0, 40.0, 5.0, 50.0]
        expected1 = np.array([1.0, 30.0, 4.0, 40.0, 5.0, 50.0], dtype=np.float32)
        np.testing.assert_array_almost_equal(emb1, expected1)

        # CRITICAL: POI 10 at seq0 pos0 vs seq1 pos0 has DIFFERENT Time2Vec
        poi10_seq0 = emb0[:total_dim]  # [1.0, 0.0]
        poi10_seq1 = emb1[:total_dim]  # [1.0, 30.0]
        assert poi10_seq0[0] == poi10_seq1[0]  # Same HGI
        assert poi10_seq0[1] != poi10_seq1[1]  # Different Time2Vec

    def test_next_checkin_level_temporal_order(self):
        """Position i in sequence must correspond to i-th chronological check-in."""
        window_size = 3
        total_dim = 1

        # Deliberately create check-ins in non-chronological order
        raw_checkins = pd.DataFrame({
            'userid': [1, 1, 1, 1, 1, 1],
            'placeid': [10, 11, 12, 13, 14, 15],
            'category': ['A', 'B', 'C', 'D', 'E', 'F'],
            'datetime': pd.to_datetime([
                '2023-01-01 15:00',  # out of order!
                '2023-01-01 11:00',
                '2023-01-01 12:00',
                '2023-01-01 13:00',
                '2023-01-01 14:00',
                '2023-01-01 10:00',  # earliest
            ]),
        })

        # Sort (as generate_next_input does)
        checkins_df = raw_checkins.sort_values(['userid', 'datetime']).reset_index(drop=True)

        # After sort: order should be POI 15(10:00), 11(11:00), 12(12:00), 13(13:00), 14(14:00), 10(15:00)
        expected_order = [15, 11, 12, 13, 14, 10]
        assert checkins_df['placeid'].tolist() == expected_order

        # Time2Vec: unique per position after sort
        t2v_df = make_checkin_embedding_df(checkins_df, dim=1, seed=0)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=1, level=EmbeddingLevel.CHECKIN)

        aligned = EmbeddingAligner.align_checkin_level(
            checkins_df, [t2v_df], [spec_t2v]
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_t2v], output_prefix='fused')

        fused_cols = ['fused_0']
        user_df = fused.reset_index(drop=True)

        results, sequences = convert_user_checkins_to_sequences(
            user_df, fused_cols, window_size, total_dim
        )

        # First sequence: positions 0,1,2 → POIs 15, 11, 12 (chronological)
        assert sequences[0][:window_size] == [15, 11, 12]

    def test_next_checkin_level_unique_checkins_in_window(self):
        """Non-overlapping windows: each check-in row appears in at most one window."""
        window_size = 3
        total_dim = 1

        checkins_df = make_checkins_df({
            1: [
                (10, 'A', '2023-01-01 10:00'),
                (11, 'B', '2023-01-01 11:00'),
                (12, 'C', '2023-01-01 12:00'),
                (13, 'D', '2023-01-01 13:00'),
                (14, 'E', '2023-01-01 14:00'),
                (15, 'F', '2023-01-01 15:00'),
                (16, 'G', '2023-01-01 16:00'),
            ]
        })

        t2v_df = make_checkin_embedding_df(checkins_df, dim=1, seed=0)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=1, level=EmbeddingLevel.CHECKIN)

        aligned = EmbeddingAligner.align_checkin_level(
            checkins_df, [t2v_df], [spec_t2v]
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_t2v], output_prefix='fused')

        fused_cols = ['fused_0']
        user_df = fused.reset_index(drop=True)

        results, sequences = convert_user_checkins_to_sequences(
            user_df, fused_cols, window_size, total_dim
        )

        # Collect all embedding values across all sequences to verify non-overlap
        all_emb_values = set()
        for r in results:
            emb_part = r[:window_size * total_dim].astype(np.float32)
            for val in emb_part:
                if val != 0.0:  # skip padding zeros
                    assert val not in all_emb_values, f"Embedding value {val} appears in multiple windows"
                    all_emb_values.add(val)


# ============================================================================
# Bug Regression Tests
# ============================================================================

class TestBugRegressions:
    """Regression tests for identified bugs."""

    def test_position_alignment_after_skipped_sequence(self):
        """
        Bug 1: If generate_sequences skips a window, position-based lookup
        must still map to the correct rows (not use enumerate index * window_size).
        """
        # We test generate_sequences with return_start_indices=True
        # to verify the returned indices are correct even if sequences were skippable
        window_size = 3

        # 7 visits: generates sequences at start_idx=0 and start_idx=3
        places = [10, 11, 12, 13, 14, 15, 16]
        sequences_with_idx = generate_sequences(
            places, window_size=window_size, return_start_indices=True
        )

        assert len(sequences_with_idx) >= 2

        # Verify start indices match actual window positions
        for start_idx, seq in sequences_with_idx:
            # The history POIs should match places at [start_idx:start_idx+window_size]
            history = seq[:window_size]
            for i, poi in enumerate(history):
                if poi != PADDING_VALUE:
                    assert poi == places[start_idx + i], \
                        f"At start_idx={start_idx}, position {i}: expected {places[start_idx + i]}, got {poi}"

    def test_generate_sequences_return_start_indices_backward_compat(self):
        """generate_sequences default behavior (no start indices) is unchanged."""
        places = [10, 11, 12, 13, 14, 15, 16]
        sequences = generate_sequences(places, window_size=3)

        # Should return plain lists, not tuples
        assert len(sequences) > 0
        assert isinstance(sequences[0], list)

    def test_generate_sequences_with_start_indices(self):
        """generate_sequences with return_start_indices=True returns (idx, seq) tuples."""
        places = [10, 11, 12, 13, 14, 15, 16]
        sequences_with_idx = generate_sequences(
            places, window_size=3, return_start_indices=True
        )

        assert len(sequences_with_idx) > 0
        assert isinstance(sequences_with_idx[0], tuple)
        assert isinstance(sequences_with_idx[0][0], int)  # start_idx
        assert isinstance(sequences_with_idx[0][1], list)  # sequence

    def test_row_multiplication_prevented_conflicting_checkin(self):
        """Bug 3: Conflicting duplicate composite keys must raise ValueError."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        t2v_df = make_checkin_embedding_df(checkins_df, dim=2, seed=0)
        # Introduce conflicting duplicate (same key, different embedding)
        conflict = t2v_df.iloc[[0]].copy()
        conflict['0'] = 999.0
        t2v_df = pd.concat([t2v_df, conflict], ignore_index=True)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        with pytest.raises(ValueError, match="DIFFERENT"):
            EmbeddingAligner.align_checkin_level(
                checkins_df, [t2v_df], [spec_t2v]
            )

    def test_identical_duplicates_are_deduplicated(self):
        """Bug 3: Identical duplicate rows should be safely deduplicated, not raise."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        t2v_df = make_checkin_embedding_df(checkins_df, dim=2, seed=0)
        # Add identical duplicate
        t2v_df = pd.concat([t2v_df, t2v_df.iloc[[0]]], ignore_index=True)
        spec_t2v = EmbeddingSpec(engine=EmbeddingEngine.TIME2VEC, dimension=2, level=EmbeddingLevel.CHECKIN)

        # Should succeed — identical duplicates are deduplicated
        result = EmbeddingAligner.align_checkin_level(
            checkins_df, [t2v_df], [spec_t2v]
        )
        assert len(result) == 2

    def test_row_multiplication_prevented_conflicting_poi(self):
        """Bug 3: Conflicting duplicate placeids in POI embedding must raise."""
        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
            ]
        })

        hgi_df = pd.DataFrame({
            'placeid': [10, 10, 11],  # duplicate POI 10 with DIFFERENT embeddings
            '0': [1.0, 1.5, 2.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=1, level=EmbeddingLevel.POI)

        with pytest.raises(ValueError, match="DIFFERENT"):
            EmbeddingAligner.align_checkin_level(
                checkins_df, [hgi_df], [spec_hgi]
            )

    def test_output_path_used_for_saving(self):
        """Bug 2: _generate_next_input_* must save to the caller-specified path."""
        window_size = 3
        total_dim = 2

        checkins_df = make_checkins_df({
            1: [
                (10, 'Food', '2023-01-01 10:00'),
                (11, 'Shop', '2023-01-01 11:00'),
                (12, 'Cafe', '2023-01-01 12:00'),
                (13, 'Park', '2023-01-01 13:00'),
                (14, 'Gym',  '2023-01-01 14:00'),
                (15, 'Bar',  '2023-01-01 15:00'),
                (16, 'Pub',  '2023-01-01 16:00'),
            ]
        })

        hgi_df = pd.DataFrame({
            'placeid': [10, 11, 12, 13, 14, 15, 16],
            '0': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
            '1': [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0],
        })
        spec_hgi = EmbeddingSpec(engine=EmbeddingEngine.HGI, dimension=2, level=EmbeddingLevel.POI)

        aligned = EmbeddingAligner.align_checkin_level(
            checkins_df, [hgi_df], [spec_hgi]
        )
        fused = EmbeddingFuser.fuse_embeddings(aligned, [spec_hgi], output_prefix='fused')

        # Track what path save_parquet receives
        saved_paths = []
        original_save = __import__('data.inputs.core', fromlist=['save_parquet']).save_parquet

        def tracking_save(df, path, **kwargs):
            saved_paths.append(str(path))

        with patch('data.inputs.fusion.save_parquet', side_effect=tracking_save):
            from data.inputs.fusion import MultiEmbeddingInputGenerator
            gen = MultiEmbeddingInputGenerator.__new__(MultiEmbeddingInputGenerator)
            gen.state = 'test'
            gen.config = FusionConfig(
                category_embeddings=[spec_hgi],
                next_embeddings=[spec_hgi],
            )

            gen._generate_next_input_poi_level(
                fused, '/tmp/test_seq.parquet', '/tmp/test_emb.parquet'
            )

        # The embeddings output path should be the one we specified
        assert '/tmp/test_emb.parquet' in saved_paths
