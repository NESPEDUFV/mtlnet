"""
Category mapping for the Massive-STEPS dataset.

Massive-STEPS stores Foursquare subcategory names in the ``venue_category``
column (e.g. "Italian Restaurant", "Coffee Shop"). This module maps them to
the project's 7-class taxonomy using the comprehensive shared mapping.

A ``load_hierarchy()`` helper is retained for forward-compatibility in case
a dataset-specific categories.csv is provided, but the shared SUBCATEGORY_TO_SUPER
dict already covers all ~617 unique category names found across the 15 STEPS cities.
"""

from pathlib import Path

import pandas as pd

from src.etl.utils.category_mapping import SUBCATEGORY_TO_SUPER, map_category as _base_map

# The nine Foursquare top-level names and their mapping — used by load_hierarchy()
# to resolve subcategories via their parent column.
FSQ_TOP_LEVEL_TO_SUPER: dict[str, str] = {
    "Arts & Entertainment": "Entertainment",
    "College & University": "Community",
    "Food": "Food",
    "Nightlife Spot": "Nightlife",
    "Outdoors & Recreation": "Outdoors",
    "Professional & Other Places": "Community",
    "Residence": "Community",
    "Shop & Service": "Shopping",
    "Travel & Transport": "Travel",
}

__all__ = ["FSQ_TOP_LEVEL_TO_SUPER", "load_hierarchy", "map_category"]


def load_hierarchy(categories_csv: Path) -> dict[str, str]:
    """Build a subcategory → super-category lookup from a categories.csv file.

    Parameters
    ----------
    categories_csv:
        Path to the ``categories.csv`` shipped with Massive-STEPS.
        Expected columns: ``category_name``, ``parent_name`` (or similar).

    Returns
    -------
    dict mapping category names (including top-level) → super-category string.
    The result is the comprehensive shared mapping augmented with any entries
    resolvable through the parent hierarchy in the CSV.
    """
    df = pd.read_csv(categories_csv, dtype=str).fillna("")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    name_col = _find_col(df, ["category_name", "name"])
    parent_col = _find_col(df, ["parent_name", "parent_category_name", "top_category"])

    # Start from the comprehensive shared mapping
    mapping: dict[str, str] = dict(SUBCATEGORY_TO_SUPER)

    if name_col is None:
        return mapping

    for _, row in df.iterrows():
        cat_name = row[name_col].strip()
        # Already mapped — skip
        if cat_name in mapping:
            continue
        # Try to resolve via parent
        parent_name = row[parent_col].strip() if parent_col else ""
        if parent_name in FSQ_TOP_LEVEL_TO_SUPER:
            mapping[cat_name] = FSQ_TOP_LEVEL_TO_SUPER[parent_name]
        elif parent_name in mapping:
            mapping[cat_name] = mapping[parent_name]

    return mapping


def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def map_category(
    venue_category_name: str,
    hierarchy: dict[str, str] | None = None,
) -> str | None:
    """Return the 7-class super-category for a raw Massive-STEPS category name.

    Parameters
    ----------
    venue_category_name:
        Raw category string from the CSV.
    hierarchy:
        Optional dict from ``load_hierarchy()``. When provided, names not in
        the shared mapping are looked up here too.
    """
    name = venue_category_name.strip() if venue_category_name else ""
    if not name:
        return None

    # Primary: shared comprehensive mapping
    result = _base_map(name)
    if result is not None:
        return result

    # Fallback: hierarchy lookup (e.g. from categories.csv)
    if hierarchy:
        return hierarchy.get(name)

    return None
