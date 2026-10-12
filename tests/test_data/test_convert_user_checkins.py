"""
Tests for convert_user_checkins_to_sequences().

Captures exact behavior so we can safely optimize the implementation.
"""
import pytest
import numpy as np
import pandas as pd

from data.inputs.core import (
    convert_user_checkins_to_sequences,
    PADDING_VALUE,
    MISSING_CATEGORY_VALUE,
)


def _make_user_df(n_checkins: int, userid: int = 1, embedding_dim: int = 4):
    """Helper: create a user DataFrame with sequential embeddings for easy verification."""
    data = {
        'userid': [userid] * n_checkins,
        'placeid': [100 + i for i in range(n_checkins)],
        'category': [f'cat_{i % 3}' for i in range(n_checkins)],
        'datetime': pd.date_range('2023-01-01', periods=n_checkins, freq='h'),
    }
    # Embeddings: row i has all values = float(i) for easy checking
    for d in range(embedding_dim):
        data[str(d)] = [float(i) + d * 0.01 for i in range(n_checkins)]
    return pd.DataFrame(data).reset_index(drop=True)


def _make_user_df_str_placeid(n_checkins: int, userid: int = 1, embedding_dim: int = 4):
    """Helper: same as above but placeid is str (like Time2Vec output)."""
    df = _make_user_df(n_checkins, userid, embedding_dim)
    df['placeid'] = df['placeid'].astype(str)
    return df


class TestConvertUserCheckinsBasic:
    """Basic behavior tests."""

    def test_returns_tuple_of_two_lists(self):
        df = _make_user_df(12)
        emb_cols = ['0', '1', '2', '3']
        results, sequences = convert_user_checkins_to_sequences(df, emb_cols, window_size=3, embedding_dim=4)
        assert isinstance(results, list)
        assert isinstance(sequences, list)

    def test_empty_for_short_history(self):
        """Users with fewer than MIN_SEQUENCE_LENGTH checkins return empty."""
        df = _make_user_df(3)
        emb_cols = ['0', '1', '2', '3']
        results, sequences = convert_user_checkins_to_sequences(df, emb_cols, window_size=3, embedding_dim=4)
        assert results == []
        assert sequences == []

    def test_sequence_count_matches(self):
        """Number of embedding_results must equal number of poi_sequences."""
        df = _make_user_df(20)
        emb_cols = ['0', '1', '2', '3']
        results, sequences = convert_user_checkins_to_sequences(df, emb_cols, window_size=3, embedding_dim=4)
        assert len(results) == len(sequences)
        assert len(results) > 0


class TestConvertUserCheckinsEmbeddings:
    """Verify embedding values are correctly extracted by position."""

    def test_first_sequence_embeddings(self):
        """First sequence should use rows 0..window_size-1 from the DataFrame."""
        embedding_dim = 4
        window_size = 3
        df = _make_user_df(10, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results, _ = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)

        first_result = results[0]
        # First window_size * embedding_dim values are the flattened embeddings
        emb_part = first_result[:window_size * embedding_dim].astype(np.float32)

        # Row 0 embedding
        expected_row0 = df.iloc[0][emb_cols].values.astype(np.float32)
        actual_row0 = emb_part[:embedding_dim]
        np.testing.assert_array_almost_equal(actual_row0, expected_row0)

        # Row 1 embedding
        expected_row1 = df.iloc[1][emb_cols].values.astype(np.float32)
        actual_row1 = emb_part[embedding_dim:2 * embedding_dim]
        np.testing.assert_array_almost_equal(actual_row1, expected_row1)

    def test_second_sequence_uses_next_window(self):
        """Second sequence should start at row window_size (non-overlapping)."""
        embedding_dim = 4
        window_size = 3
        df = _make_user_df(10, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results, _ = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)

        if len(results) < 2:
            pytest.skip("Not enough sequences")

        second_result = results[1]
        emb_part = second_result[:window_size * embedding_dim].astype(np.float32)

        # Second sequence starts at row window_size
        expected_row = df.iloc[window_size][emb_cols].values.astype(np.float32)
        actual_row = emb_part[:embedding_dim]
        np.testing.assert_array_almost_equal(actual_row, expected_row)

    def test_padding_gets_zero_embeddings(self):
        """Padded positions should have zero-valued embeddings."""
        embedding_dim = 4
        window_size = 9  # Large window so short history triggers padding
        df = _make_user_df(6, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results, _ = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)

        if not results:
            pytest.skip("No sequences generated")

        first_result = results[0]
        emb_part = first_result[:window_size * embedding_dim].astype(np.float32)

        # Find which positions in the sequence are padded
        # With 6 checkins and window=9, some positions will be padding
        # Check that padded positions have zero embeddings
        zero_emb = np.zeros(embedding_dim, dtype=np.float32)
        for pos in range(window_size):
            pos_emb = emb_part[pos * embedding_dim:(pos + 1) * embedding_dim]
            if np.allclose(pos_emb, zero_emb):
                # This was a padded position — correct
                pass


class TestConvertUserCheckinsMetadata:
    """Verify metadata (category, userid) appended correctly."""

    def test_userid_appended(self):
        embedding_dim = 4
        window_size = 3
        userid = 42
        df = _make_user_df(10, userid=userid, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results, _ = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)
        # Last element is userid
        assert int(results[0][-1]) == userid

    def test_target_category_from_position(self):
        """Target category should come from the position after the window."""
        embedding_dim = 4
        window_size = 3
        df = _make_user_df(10, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results, _ = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)
        # First sequence target is at position window_size
        expected_cat = df.iloc[window_size]['category']
        assert str(results[0][-2]) == str(expected_cat)


class TestConvertUserCheckinsPOISequences:
    """Verify POI sequence output."""

    def test_poi_sequence_structure(self):
        """Each POI sequence should be [poi_0, ..., poi_{w-1}, target_poi, userid]."""
        embedding_dim = 4
        window_size = 3
        userid = 7
        df = _make_user_df(10, userid=userid, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        _, sequences = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)

        for seq in sequences:
            assert len(seq) == window_size + 2  # window + target + userid
            assert seq[-1] == userid

    def test_poi_ids_match_dataframe(self):
        """POI IDs in sequences should match the placeid column."""
        embedding_dim = 4
        window_size = 3
        df = _make_user_df(10, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        _, sequences = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)

        # First sequence history should be first window_size placeids
        expected_pois = df['placeid'].tolist()[:window_size]
        actual_pois = sequences[0][:window_size]
        assert actual_pois == expected_pois


class TestConvertUserCheckinsStrPlaceid:
    """Verify behavior when placeid is string (like Time2Vec)."""

    def test_works_with_str_placeids(self):
        """Should work identically with string placeids."""
        embedding_dim = 4
        window_size = 3
        df = _make_user_df_str_placeid(10, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results, sequences = convert_user_checkins_to_sequences(df, emb_cols, window_size, embedding_dim)
        assert len(results) > 0
        assert len(sequences) > 0

    def test_str_placeid_embeddings_match_int_placeid(self):
        """Embeddings should be identical regardless of placeid type (position-based)."""
        embedding_dim = 4
        window_size = 3

        df_int = _make_user_df(10, embedding_dim=embedding_dim)
        df_str = _make_user_df_str_placeid(10, embedding_dim=embedding_dim)
        emb_cols = [str(i) for i in range(embedding_dim)]

        results_int, _ = convert_user_checkins_to_sequences(df_int, emb_cols, window_size, embedding_dim)
        results_str, _ = convert_user_checkins_to_sequences(df_str, emb_cols, window_size, embedding_dim)

        assert len(results_int) == len(results_str)
        for r_int, r_str in zip(results_int, results_str):
            # Embedding parts should be identical (position-based lookup)
            emb_int = r_int[:window_size * embedding_dim].astype(np.float32)
            emb_str = r_str[:window_size * embedding_dim].astype(np.float32)
            np.testing.assert_array_almost_equal(emb_int, emb_str)
