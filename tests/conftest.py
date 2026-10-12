"""
Shared pytest fixtures for MTL input tests.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

import sys
from pathlib import Path

# Add project root and src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from data.inputs.core import PADDING_VALUE
from configs.model import InputsConfig


@pytest.fixture
def sample_checkins_df():
    """
    Create sample check-ins DataFrame for testing.

    Returns:
        pd.DataFrame with columns: userid, placeid, datetime, category
    """
    return pd.DataFrame({
        'userid': [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
        'placeid': [10, 11, 12, 13, 14, 20, 21, 22, 23, 24],
        'datetime': pd.to_datetime([
            '2023-01-01 10:00', '2023-01-01 11:00', '2023-01-01 12:00',
            '2023-01-01 13:00', '2023-01-01 14:00',
            '2023-01-02 09:00', '2023-01-02 10:00', '2023-01-02 11:00',
            '2023-01-02 12:00', '2023-01-02 13:00'
        ]),
        'category': ['Food', 'Shop', 'Cafe', 'Food', 'Park',
                    'Food', 'Entertainment', 'Shop', 'Food', 'Cafe']
    })


@pytest.fixture
def sample_embeddings_df():
    """
    Create sample POI embeddings DataFrame.

    Returns:
        pd.DataFrame with columns: placeid, 0, 1, ..., 63
    """
    pois = [10, 11, 12, 13, 14, 20, 21, 22, 23, 24]
    embedding_dim = 64

    # Create random embeddings
    embeddings = {str(i): np.random.randn(len(pois)) for i in range(embedding_dim)}
    embeddings['placeid'] = pois

    return pd.DataFrame(embeddings)


@pytest.fixture
def sample_checkin_embeddings_df(sample_checkins_df):
    """
    Create sample check-in-level embeddings DataFrame (like Time2Vec).

    Returns:
        pd.DataFrame with columns: userid, placeid, datetime, category, 0, 1, ..., 63
    """
    embedding_dim = 64
    df = sample_checkins_df.copy()

    # Add random embeddings for each check-in
    for i in range(embedding_dim):
        df[str(i)] = np.random.randn(len(df))

    return df


@pytest.fixture
def sample_sequences_df():
    """
    Create sample sequences DataFrame for testing.

    Returns:
        pd.DataFrame with columns: poi_0, ..., poi_8, target_poi, userid
    """
    window_size = InputsConfig.SLIDE_WINDOW
    return pd.DataFrame({
        **{f'poi_{i}': [10, 11, 20] for i in range(window_size)},
        'target_poi': [14, 13, 24],
        'userid': [1, 1, 2]
    })


@pytest.fixture
def temp_output_dir():
    """
    Create temporary directory for output file tests.

    Yields:
        Path object to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def embedding_lookup_64d():
    """
    Create sample embedding lookup dictionary (64-dimensional).

    Returns:
        Dict[int, np.ndarray] mapping POI ID to embedding
    """
    pois = [10, 11, 12, 13, 14, 20, 21, 22, 23, 24]
    lookup = {poi: np.random.randn(64).astype(np.float32) for poi in pois}
    lookup[PADDING_VALUE] = np.zeros(64, dtype=np.float32)
    return lookup


@pytest.fixture
def category_lookup():
    """
    Create sample category lookup dictionary.

    Returns:
        Dict[int, str] mapping POI ID to category
    """
    return {
        10: 'Food', 11: 'Shop', 12: 'Cafe', 13: 'Food', 14: 'Park',
        20: 'Food', 21: 'Entertainment', 22: 'Shop', 23: 'Food', 24: 'Cafe',
        PADDING_VALUE: 'None'
    }
