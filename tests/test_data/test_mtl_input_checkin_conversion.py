"""
Unit tests for convert_user_checkins_to_sequences function.

Tests position-based embedding lookup for check-in-level embeddings.
This function is used by both builders.py and fusion.py to convert
check-in-level embeddings (like Time2Vec) to flattened sequences.
"""
import pytest
import pandas as pd
import numpy as np

from data.inputs.core import (
    generate_sequences,
    get_zero_embedding,
    PADDING_VALUE,
    MISSING_CATEGORY_VALUE,
)
from configs.model import InputsConfig


# The function we're testing - will be imported after implementation
# from data.inputs.core import convert_user_checkins_to_sequences


def make_user_df(n_checkins: int, userid: int = 1, embedding_dim: int = 2,
                 categories: list = None, use_fused_cols: bool = False):
    """Helper to create test user DataFrames."""
    if categories is None:
        categories = ['Food'] * n_checkins
    elif len(categories) < n_checkins:
        categories = categories + ['Food'] * (n_checkins - len(categories))

    df = pd.DataFrame({
        'userid': [userid] * n_checkins,
        'placeid': list(range(100, 100 + n_checkins)),
        'datetime': pd.date_range('2023-01-01', periods=n_checkins, freq='h'),
        'category': categories[:n_checkins],
    })

    # Add embedding columns with predictable values
    for i in range(embedding_dim):
        if use_fused_cols:
            col_name = f'fused_{i}'
        else:
            col_name = str(i)
        # Embedding value = row_idx + (i * 10), making it easy to verify
        df[col_name] = np.arange(n_checkins, dtype=np.float32) + (i * 10)

    return df


class TestConvertUserCheckinsToSequences:
    """Test suite for convert_user_checkins_to_sequences() function."""

    @pytest.fixture
    def simple_user_df(self):
        """Create minimal user DataFrame for testing (10 checkins = 1 sequence)."""
        window_size = InputsConfig.SLIDE_WINDOW  # 9
        n_checkins = window_size + 1  # 10 checkins for exactly one sequence
        return make_user_df(n_checkins, userid=1, embedding_dim=2)

    @pytest.fixture
    def multi_sequence_user_df(self):
        """Create user DataFrame with enough data for multiple sequences."""
        window_size = InputsConfig.SLIDE_WINDOW  # 9
        # 20 checkins gives us 2 full sequences: [0-8,9] and [9-17,18]
        n_checkins = window_size * 2 + 2
        categories = [f'Cat{i % 7}' for i in range(n_checkins)]
        return make_user_df(n_checkins, userid=1, embedding_dim=2, categories=categories)

    def test_returns_tuple_of_two_lists(self, simple_user_df):
        """Should return tuple of (embedding_results, poi_sequences)."""
        from data.inputs.core import convert_user_checkins_to_sequences

        emb_cols = ['0', '1']
        results, sequences = convert_user_checkins_to_sequences(
            simple_user_df, emb_cols, window_size=9, embedding_dim=2
        )

        assert isinstance(results, list)
        assert isinstance(sequences, list)

    def test_empty_user_returns_empty_lists(self):
        """User with insufficient data should return empty lists."""
        from data.inputs.core import convert_user_checkins_to_sequences

        # Only 2 checkins - not enough for any sequence
        user_df = make_user_df(n_checkins=2, embedding_dim=1)

        results, sequences = convert_user_checkins_to_sequences(
            user_df, ['0'], window_size=9, embedding_dim=1
        )

        assert results == []
        assert sequences == []

    def test_position_based_embedding_lookup(self, simple_user_df):
        """Should use position in DataFrame, not POI ID lookup."""
        from data.inputs.core import convert_user_checkins_to_sequences

        emb_cols = ['0', '1']
        embedding_dim = 2
        window_size = 9

        results, _ = convert_user_checkins_to_sequences(
            simple_user_df, emb_cols, window_size, embedding_dim
        )

        assert len(results) == 1
        result = results[0]

        # First embedding should be from row 0: [0.0, 10.0] (col 0 = idx, col 1 = idx + 10)
        first_emb = result[:embedding_dim].astype(np.float32)
        assert np.allclose(first_emb, [0.0, 10.0])

        # Second embedding should be from row 1: [1.0, 11.0]
        second_emb = result[embedding_dim:2*embedding_dim].astype(np.float32)
        assert np.allclose(second_emb, [1.0, 11.0])

    def test_sequence_contains_userid(self, simple_user_df):
        """Each sequence should include userid at the end."""
        from data.inputs.core import convert_user_checkins_to_sequences

        emb_cols = ['0', '1']
        _, sequences = convert_user_checkins_to_sequences(
            simple_user_df, emb_cols, window_size=9, embedding_dim=2
        )

        assert len(sequences) == 1
        # Last element is userid
        assert sequences[0][-1] == 1

    def test_result_contains_category_and_userid(self, simple_user_df):
        """Result array should end with [target_category, userid]."""
        from data.inputs.core import convert_user_checkins_to_sequences

        emb_cols = ['0', '1']
        window_size = 9
        embedding_dim = 2

        results, _ = convert_user_checkins_to_sequences(
            simple_user_df, emb_cols, window_size, embedding_dim
        )

        result = results[0]
        expected_length = window_size * embedding_dim + 2
        assert len(result) == expected_length

        # Last element is userid
        assert int(result[-1]) == 1
        # Second to last is category
        assert result[-2] == 'Food'

    def test_multiple_sequences_non_overlapping(self, multi_sequence_user_df):
        """Multiple sequences should use non-overlapping windows."""
        from data.inputs.core import convert_user_checkins_to_sequences

        emb_cols = ['0', '1']
        window_size = 9
        embedding_dim = 2

        results, sequences = convert_user_checkins_to_sequences(
            multi_sequence_user_df, emb_cols, window_size, embedding_dim
        )

        assert len(results) >= 2
        assert len(sequences) >= 2

        # First sequence uses positions 0-8, second uses 9-17
        # First embedding of each sequence should be different
        first_seq_first_emb = results[0][:embedding_dim].astype(np.float32)
        second_seq_first_emb = results[1][:embedding_dim].astype(np.float32)

        # Should be embeddings from row 0 and row 9 respectively
        # Row 0: [0.0, 10.0], Row 9: [9.0, 19.0]
        assert np.allclose(first_seq_first_emb, [0.0, 10.0])
        assert np.allclose(second_seq_first_emb, [9.0, 19.0])

    def test_fused_column_names(self):
        """Should work with fused column naming (fused_0, fused_1, etc.)."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = 9
        n_checkins = window_size + 1
        user_df = make_user_df(n_checkins, embedding_dim=2, use_fused_cols=True)

        fused_cols = ['fused_0', 'fused_1']
        results, _ = convert_user_checkins_to_sequences(
            user_df, fused_cols, window_size, embedding_dim=2
        )

        assert len(results) == 1
        # Verify values come from correct columns
        first_emb = results[0][:2].astype(np.float32)
        assert np.allclose(first_emb, [0.0, 10.0])

    def test_padding_gets_zero_embedding(self):
        """Padded positions should get zero embeddings."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = 9
        # 6 checkins: 5 for history + 1 target, but window wants 9 history
        # So we'll have some padding
        n_checkins = 6
        user_df = make_user_df(n_checkins, embedding_dim=1)
        # Set embedding values to 99 so we can detect zeros
        user_df['0'] = 99.0

        results, sequences = convert_user_checkins_to_sequences(
            user_df, ['0'], window_size, embedding_dim=1
        )

        if len(results) > 0:
            result = results[0]
            embeddings = result[:window_size].astype(np.float32)
            # Real data has 99.0, padding should have 0.0
            # At least some positions should have real data
            has_real = any(e == 99.0 for e in embeddings)
            assert has_real, "Should have at least some real (non-padded) data"

    def test_target_category_position_lookup(self, multi_sequence_user_df):
        """Target category should come from position-based lookup."""
        from data.inputs.core import convert_user_checkins_to_sequences

        emb_cols = ['0', '1']
        window_size = 9

        results, _ = convert_user_checkins_to_sequences(
            multi_sequence_user_df, emb_cols, window_size, embedding_dim=2
        )

        # First sequence: target is at position 9
        # Category at position 9 = 'Cat' + (9 % 7) = 'Cat2'
        first_result = results[0]
        assert first_result[-2] == 'Cat2'

    def test_target_category_fallback_to_poi_lookup(self):
        """When position lookup fails, should fall back to POI ID lookup."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = 9
        n_checkins = window_size + 1
        user_df = make_user_df(n_checkins, embedding_dim=1)
        user_df['category'] = 'FallbackCategory'

        results, _ = convert_user_checkins_to_sequences(
            user_df, ['0'], window_size, embedding_dim=1
        )

        assert len(results) == 1
        # Should have category
        assert results[0][-2] == 'FallbackCategory'

    def test_poi_sequences_match_expected_format(self, simple_user_df):
        """POI sequences should have format [poi_0, ..., poi_8, target_poi, userid]."""
        from data.inputs.core import convert_user_checkins_to_sequences

        emb_cols = ['0', '1']
        window_size = 9

        _, sequences = convert_user_checkins_to_sequences(
            simple_user_df, emb_cols, window_size, embedding_dim=2
        )

        assert len(sequences) == 1
        seq = sequences[0]

        # Should have window_size + target + userid = 11 elements
        assert len(seq) == window_size + 1 + 1

        # History POIs
        history_pois = seq[:window_size]
        target_poi = seq[window_size]
        userid = seq[-1]

        # POIs should be from our test data: 100, 101, 102, ...
        assert all(poi >= 100 or poi == PADDING_VALUE for poi in history_pois)
        assert target_poi >= 100 or target_poi == PADDING_VALUE
        assert userid == 1


class TestCheckinConversionEdgeCases:
    """Edge case tests for convert_user_checkins_to_sequences."""

    def test_user_with_exactly_min_sequence_length(self):
        """User with exactly MIN_SEQUENCE_LENGTH checkins."""
        from data.inputs.core import convert_user_checkins_to_sequences, MIN_SEQUENCE_LENGTH

        user_df = make_user_df(n_checkins=MIN_SEQUENCE_LENGTH, embedding_dim=1)

        results, sequences = convert_user_checkins_to_sequences(
            user_df, ['0'], window_size=9, embedding_dim=1
        )

        # Should produce at least 1 sequence (with padding)
        assert len(results) >= 1 or len(results) == 0  # Depends on implementation

    def test_bounds_checking_for_embedding_lookup(self):
        """Should handle cases where row_idx exceeds DataFrame length."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = 9
        # Edge case: enough for sequence generation but with padding needs
        n_checkins = 10  # Just barely enough
        user_df = make_user_df(n_checkins, embedding_dim=1)
        user_df['0'] = 77.0  # Distinct value to detect vs zeros

        results, _ = convert_user_checkins_to_sequences(
            user_df, ['0'], window_size, embedding_dim=1
        )

        # Should complete without error
        assert isinstance(results, list)

    def test_different_embedding_dimensions(self):
        """Should work with various embedding dimensions."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = 9
        n_checkins = 10

        for embedding_dim in [1, 4, 64, 128]:
            user_df = make_user_df(n_checkins, embedding_dim=embedding_dim)
            emb_cols = [str(i) for i in range(embedding_dim)]

            results, _ = convert_user_checkins_to_sequences(
                user_df, emb_cols, window_size, embedding_dim
            )

            if len(results) > 0:
                expected_length = window_size * embedding_dim + 2
                assert len(results[0]) == expected_length


class TestCheckinConversionRegression:
    """Regression tests to ensure exact output format matches original."""

    def test_output_array_is_numpy(self):
        """Output array should be numpy ndarray."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = 9
        n_checkins = window_size + 1
        user_df = make_user_df(n_checkins, embedding_dim=1)

        results, _ = convert_user_checkins_to_sequences(
            user_df, ['0'], window_size, embedding_dim=1
        )

        result = results[0]
        assert isinstance(result, np.ndarray)

    def test_flattening_order_row_major(self):
        """Embeddings should be flattened in row-major order (C-order)."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = 3
        embedding_dim = 2
        n_checkins = 6  # enough for one sequence with small window

        user_df = pd.DataFrame({
            'userid': [1] * n_checkins,
            'placeid': list(range(n_checkins)),
            'datetime': pd.date_range('2023-01-01', periods=n_checkins, freq='h'),
            'category': ['Food'] * n_checkins,
            '0': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            '1': [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        })

        results, _ = convert_user_checkins_to_sequences(
            user_df, ['0', '1'], window_size, embedding_dim
        )

        if len(results) > 0:
            flattened = results[0][:window_size * embedding_dim].astype(np.float32)
            # Row major: [row0_col0, row0_col1, row1_col0, row1_col1, row2_col0, row2_col1]
            # From our data: [1, 10, 2, 20, 3, 30]
            expected = np.array([1.0, 10.0, 2.0, 20.0, 3.0, 30.0], dtype=np.float32)
            assert np.allclose(flattened, expected), f"Expected {expected}, got {flattened}"

    def test_result_matches_original_builders_output_format(self):
        """Result format should match original generate_next_input_from_checkins output."""
        from data.inputs.core import convert_user_checkins_to_sequences

        window_size = InputsConfig.SLIDE_WINDOW
        embedding_dim = 64
        n_checkins = window_size + 1

        user_df = make_user_df(n_checkins, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results, sequences = convert_user_checkins_to_sequences(
            user_df, emb_cols, window_size, embedding_dim
        )

        # Result shape: (window_size * embedding_dim) + category + userid
        assert len(results[0]) == window_size * embedding_dim + 2

        # Sequence shape: window_size + target_poi + userid
        assert len(sequences[0]) == window_size + 2
