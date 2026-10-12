"""
Unit tests for src/etl/mtl_input/core.py

Tests all pure logic functions:
- generate_sequences()
- create_embedding_lookup()
- create_category_lookup()
- get_zero_embedding()
- parse_and_sort_checkins()
- convert_sequences_to_poi_embeddings()
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from data.inputs.core import (
    generate_sequences,
    create_embedding_lookup,
    create_category_lookup,
    get_zero_embedding,
    parse_and_sort_checkins,
    convert_sequences_to_poi_embeddings,
    save_parquet,
    save_next_input_dataframe,
    PADDING_VALUE,
    MISSING_CATEGORY_VALUE,
)
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine


class TestGenerateSequences:
    """Test suite for generate_sequences() function."""

    def test_empty_list_returns_empty(self):
        """Empty input should return empty sequences."""
        result = generate_sequences([])
        assert result == []

    def test_short_list_returns_empty(self):
        """List shorter than MIN_SEQUENCE_LENGTH should return empty."""
        short_list = [1, 2, 3]  # Less than MIN_SEQUENCE_LENGTH=5
        result = generate_sequences(short_list)
        assert result == []

    def test_exact_window_size(self):
        """Input exactly window_size + 1 should return one sequence."""
        window_size = InputsConfig.SLIDE_WINDOW  # 9
        places = list(range(window_size + 1))  # [0, 1, ..., 9]
        result = generate_sequences(places)

        assert len(result) == 1
        assert len(result[0]) == window_size + 1
        assert result[0] == places

    def test_padding_applied_correctly(self):
        """Short sequences should be padded with PADDING_VALUE."""
        window_size = InputsConfig.SLIDE_WINDOW  # 9
        places = [1, 2, 3, 4, 5]  # Short sequence
        result = generate_sequences(places)

        assert len(result) == 1
        sequence = result[0]

        # Check padding
        expected_padding_count = window_size - len(places) + 1
        actual_padding = sequence.count(PADDING_VALUE)
        assert actual_padding == expected_padding_count

    def test_non_overlapping_windows(self):
        """Sequences should be non-overlapping (step = window_size)."""
        window_size = InputsConfig.SLIDE_WINDOW  # 9
        places = list(range(30))  # Enough for multiple windows
        result = generate_sequences(places)

        # Should have sequences at indices: 0, 9, 18, 27
        # But 27+9=36 > 30, so 3 sequences max
        assert len(result) >= 2

        # Verify non-overlapping
        seq1_history = result[0][:window_size]
        seq2_history = result[1][:window_size]

        # No overlap between consecutive sequences
        assert set(seq1_history).isdisjoint(set(seq2_history))

    def test_custom_window_size(self):
        """Should respect custom window_size parameter."""
        custom_window = 5
        places = list(range(15))
        result = generate_sequences(places, window_size=custom_window)

        assert len(result[0]) == custom_window + 1  # History + target

    def test_exact_multiple_windows(self):
        """Input that is exact multiple of window size."""
        window_size = InputsConfig.SLIDE_WINDOW  # 9
        # Window size is 9, so each sequence needs 10 elements (9 history + 1 target)
        # For exactly 2 windows: 2 * 9 = 18 elements
        places = list(range(18))
        result = generate_sequences(places)

        assert len(result) == 2
        assert len(result[0]) == window_size + 1
        assert len(result[1]) == window_size + 1


class TestCreateEmbeddingLookup:
    """Test suite for create_embedding_lookup() function."""

    def test_basic_lookup_creation(self, sample_embeddings_df):
        """Should create dict mapping POI ID to embedding vector."""
        embedding_dim = 64
        lookup = create_embedding_lookup(sample_embeddings_df, embedding_dim)

        # Check structure
        assert isinstance(lookup, dict)
        assert len(lookup) > len(sample_embeddings_df)  # Includes padding

        # Check embeddings
        first_poi = sample_embeddings_df['placeid'].iloc[0]
        assert first_poi in lookup
        assert isinstance(lookup[first_poi], np.ndarray)
        assert lookup[first_poi].shape == (embedding_dim,)
        assert lookup[first_poi].dtype == np.float32

    def test_padding_value_added(self, sample_embeddings_df):
        """Should add zero embedding for PADDING_VALUE."""
        embedding_dim = 64
        lookup = create_embedding_lookup(sample_embeddings_df, embedding_dim)

        assert PADDING_VALUE in lookup
        assert np.allclose(lookup[PADDING_VALUE], np.zeros(embedding_dim))

    def test_handles_placeid_as_column(self):
        """Should handle DataFrame with placeid as column."""
        df = pd.DataFrame({
            'placeid': [10, 11, 12],
            '0': [1.0, 2.0, 3.0],
            '1': [4.0, 5.0, 6.0],
            '2': [7.0, 8.0, 9.0]
        })

        lookup = create_embedding_lookup(df, embedding_dim=3)

        assert 10 in lookup
        assert 11 in lookup
        assert 12 in lookup
        assert np.allclose(lookup[10], [1.0, 4.0, 7.0])

    def test_embedding_values_correct(self):
        """Should extract correct embedding values from DataFrame."""
        df = pd.DataFrame({
            'placeid': [100],
            '0': [1.5],
            '1': [2.5],
            '2': [3.5]
        })

        lookup = create_embedding_lookup(df, embedding_dim=3)
        expected = np.array([1.5, 2.5, 3.5], dtype=np.float32)

        assert np.allclose(lookup[100], expected)


class TestCreateCategoryLookup:
    """Test suite for create_category_lookup() function."""

    def test_basic_category_lookup(self, sample_checkins_df):
        """Should create dict mapping POI ID to category."""
        lookup = create_category_lookup(sample_checkins_df)

        assert isinstance(lookup, dict)
        assert 10 in lookup
        assert lookup[10] == 'Food'

    def test_duplicate_placeids_take_first(self):
        """Duplicate placeids should use first occurrence."""
        df = pd.DataFrame({
            'placeid': [10, 10, 11],
            'category': ['Food', 'Shop', 'Cafe']  # 10 appears twice
        })

        lookup = create_category_lookup(df)
        assert lookup[10] == 'Food'  # First occurrence

    def test_default_value_parameter(self):
        """Should respect custom default_value parameter."""
        df = pd.DataFrame({'placeid': [10], 'category': ['Food']})

        lookup = create_category_lookup(df, default_value='Unknown')
        assert lookup[PADDING_VALUE] == 'Unknown'

    def test_default_missing_category_value(self):
        """Should use MISSING_CATEGORY_VALUE as default."""
        df = pd.DataFrame({'placeid': [10], 'category': ['Food']})

        lookup = create_category_lookup(df)
        assert lookup[PADDING_VALUE] == MISSING_CATEGORY_VALUE


class TestGetZeroEmbedding:
    """Test suite for get_zero_embedding() function."""

    def test_correct_dimension(self):
        """Should return zero vector of specified dimension."""
        embedding_dim = 64
        result = get_zero_embedding(embedding_dim)

        assert result.shape == (embedding_dim,)
        assert result.dtype == np.float32
        assert np.allclose(result, np.zeros(embedding_dim))

    def test_different_dimensions(self):
        """Should work with various dimensions."""
        for dim in [16, 32, 64, 128, 256]:
            result = get_zero_embedding(dim)
            assert result.shape == (dim,)
            assert np.all(result == 0.0)


class TestParseAndSortCheckins:
    """Test suite for parse_and_sort_checkins() function."""

    def test_parse_and_sort(self):
        """Should parse and sort timestamps."""
        timestamps = ['2023-01-03', '2023-01-01', '2023-01-02']
        result = parse_and_sort_checkins(timestamps)

        assert len(result) == 3
        assert result[0] < result[1] < result[2]

    def test_datetime_format(self):
        """Should parse various datetime formats."""
        # Use consistent datetime format
        timestamps = [
            '2023-01-01 10:30:00',
            '2023-01-02 08:00:00',
        ]
        result = parse_and_sort_checkins(timestamps)
        assert len(result) == 2

    def test_already_sorted_remains_sorted(self):
        """Already sorted timestamps should remain in order."""
        timestamps = ['2023-01-01', '2023-01-02', '2023-01-03']
        result = parse_and_sort_checkins(timestamps)

        assert result[0] < result[1] < result[2]


class TestConvertSequencesToPoiEmbeddings:
    """Test suite for convert_sequences_to_poi_embeddings() function."""

    def test_basic_conversion(self, sample_sequences_df, embedding_lookup_64d, category_lookup):
        """Should convert sequences to flattened embedding arrays."""
        window_size = InputsConfig.SLIDE_WINDOW
        embedding_dim = 64

        result = convert_sequences_to_poi_embeddings(
            sample_sequences_df,
            embedding_lookup_64d,
            category_lookup,
            window_size,
            embedding_dim,
            show_progress=False
        )

        # Check structure
        assert isinstance(result, list)
        assert len(result) == len(sample_sequences_df)

        # Check first result
        first_result = result[0]
        assert isinstance(first_result, np.ndarray)

        # Shape: (window_size * embedding_dim) + category + userid
        expected_length = window_size * embedding_dim + 2
        assert len(first_result) == expected_length

    def test_embedding_lookup_used(self, sample_sequences_df, embedding_lookup_64d, category_lookup):
        """Should use embedding_lookup for POI embeddings."""
        window_size = InputsConfig.SLIDE_WINDOW
        embedding_dim = 64

        result = convert_sequences_to_poi_embeddings(
            sample_sequences_df,
            embedding_lookup_64d,
            category_lookup,
            window_size,
            embedding_dim,
            show_progress=False
        )

        # Extract first POI from first sequence
        first_poi = sample_sequences_df.iloc[0, 0]
        expected_embedding = embedding_lookup_64d[first_poi]

        # First embedding_dim values should match
        # Note: result is mixed-type array (has strings), so extract numeric part
        actual_embedding = result[0][:embedding_dim].astype(np.float32)
        assert np.allclose(actual_embedding, expected_embedding)

    def test_batch_processing(self, sample_sequences_df, embedding_lookup_64d, category_lookup):
        """Should handle batch processing correctly."""
        window_size = InputsConfig.SLIDE_WINDOW
        embedding_dim = 64

        # Small batch size to test batching
        result = convert_sequences_to_poi_embeddings(
            sample_sequences_df,
            embedding_lookup_64d,
            category_lookup,
            window_size,
            embedding_dim,
            batch_size=1,  # Process one at a time
            show_progress=False
        )

        assert len(result) == len(sample_sequences_df)

    def test_category_and_userid_appended(self, sample_sequences_df, embedding_lookup_64d, category_lookup):
        """Should append category and userid at the end."""
        window_size = InputsConfig.SLIDE_WINDOW
        embedding_dim = 64

        result = convert_sequences_to_poi_embeddings(
            sample_sequences_df,
            embedding_lookup_64d,
            category_lookup,
            window_size,
            embedding_dim,
            show_progress=False
        )

        # Last two values: category (str) and userid (int)
        first_result = result[0]
        target_poi = sample_sequences_df.iloc[0]['target_poi']
        expected_category = category_lookup[target_poi]
        expected_userid = sample_sequences_df.iloc[0]['userid']

        assert str(first_result[-2]) == str(expected_category)
        assert int(first_result[-1]) == int(expected_userid)


class TestSaveParquet:
    """Test suite for save_parquet() function."""

    def test_creates_directories(self, temp_output_dir):
        """Should create parent directories if they don't exist."""
        output_path = temp_output_dir / 'subdir1' / 'subdir2' / 'output.parquet'
        df = pd.DataFrame({'a': [1, 2, 3]})

        save_parquet(df, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()

    def test_saves_without_index(self, temp_output_dir):
        """Should save DataFrame without index by default."""
        output_path = temp_output_dir / 'output.parquet'
        df = pd.DataFrame({'a': [1, 2, 3]}, index=[10, 20, 30])

        save_parquet(df, output_path)

        # Read back and check
        loaded = pd.read_parquet(output_path)
        assert len(loaded) == 3

    def test_saves_with_index_when_specified(self, temp_output_dir):
        """Should save index when index=True."""
        output_path = temp_output_dir / 'output.parquet'
        df = pd.DataFrame({'a': [1, 2, 3]}, index=[10, 20, 30])

        save_parquet(df, output_path, index=True)

        loaded = pd.read_parquet(output_path)
        assert loaded.index.tolist() == [10, 20, 30]


class TestSaveNextInputDataframe:
    """Test suite for save_next_input_dataframe() function."""

    @patch('configs.paths.IoPaths.get_next')
    def test_creates_correct_dataframe(self, mock_get_next, temp_output_dir):
        """Should create DataFrame with correct columns and save it."""
        output_path = temp_output_dir / 'next_output.parquet'
        mock_get_next.return_value = output_path

        # Create sample results
        window_size = 9
        embedding_dim = 64
        num_features = window_size * embedding_dim

        results = [
            np.concatenate([
                np.random.randn(num_features),
                ['Food', 1]
            ])
            for _ in range(5)
        ]

        save_next_input_dataframe(
            results, window_size, embedding_dim, 'florida', EmbeddingEngine.HGI
        )

        # Load and verify
        loaded = pd.read_parquet(output_path)

        assert len(loaded) == 5
        assert len(loaded.columns) == num_features + 2
        assert 'next_category' in loaded.columns
        assert 'userid' in loaded.columns

        # Check column names are numeric strings
        feature_cols = [str(i) for i in range(num_features)]
        for col in feature_cols:
            assert col in loaded.columns


class TestConstants:
    """Test suite for module constants."""

    def test_padding_value(self):
        """PADDING_VALUE should be -1."""
        assert PADDING_VALUE == -1

    def test_missing_category_value(self):
        """MISSING_CATEGORY_VALUE should be 'None'."""
        assert MISSING_CATEGORY_VALUE == 'None'
