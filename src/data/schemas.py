"""
Parquet column schemas for MTLnet data contracts.

Defines the expected column structure for category and next-POI input parquets.
Schemas are parameterized by embedding_dim and window_size so they adapt to
any engine configuration (single-embedding or fusion).

Usage:
    from data.schemas import CATEGORY_SCHEMA, NEXT_SCHEMA
    from data.schemas import category_columns, next_columns, validate_dataframe
"""

from typing import List


# ---------------------------------------------------------------------------
# Column builders (parameterized by dimensions)
# ---------------------------------------------------------------------------

def category_columns(embedding_dim: int) -> List[str]:
    """Return expected columns for a category-task parquet.

    Schema: [placeid, category, 0, 1, ..., embedding_dim-1]
    """
    return ["placeid", "category"] + [str(i) for i in range(embedding_dim)]


def next_columns(embedding_dim: int, window_size: int) -> List[str]:
    """Return expected columns for a next-task parquet.

    Schema: [0, 1, ..., (window_size*embedding_dim)-1, next_category, userid]
    """
    num_features = window_size * embedding_dim
    return [str(i) for i in range(num_features)] + ["next_category", "userid"]


def sequence_columns(window_size: int) -> List[str]:
    """Return expected columns for intermediate sequence parquets.

    Schema: [poi_0, ..., poi_{window_size-1}, target_poi, userid]
    """
    return [f"poi_{i}" for i in range(window_size)] + ["target_poi", "userid"]


def poi_user_mapping_columns() -> List[str]:
    """Return expected columns for the POI-to-users mapping artifact.

    Schema: [placeid, userids]
    Where userids is a JSON-encoded list of user IDs.
    """
    return ["placeid", "userids"]


# ---------------------------------------------------------------------------
# Default schemas (EMBEDDING_DIM=64, SLIDE_WINDOW=9)
# ---------------------------------------------------------------------------

CATEGORY_SCHEMA = category_columns(embedding_dim=64)
NEXT_SCHEMA = next_columns(embedding_dim=64, window_size=9)
SEQUENCE_SCHEMA = sequence_columns(window_size=9)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_dataframe(df, expected_columns: List[str], name: str = "DataFrame") -> None:
    """Validate that a DataFrame has the expected columns.

    Raises ValueError with a clear message listing missing/extra columns.
    """
    actual = set(df.columns)
    expected = set(expected_columns)

    missing = expected - actual
    if missing:
        raise ValueError(
            f"{name} is missing columns: {sorted(missing)}. "
            f"Expected {len(expected_columns)} columns, got {len(df.columns)}."
        )
