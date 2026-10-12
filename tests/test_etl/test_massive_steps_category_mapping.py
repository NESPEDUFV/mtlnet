"""
Unit tests for src/etl/massive_steps/utils/category_mapping.py
"""

import pandas as pd
import pytest

from src.etl.massive_steps.utils.category_mapping import (
    FSQ_TOP_LEVEL_TO_SUPER,
    load_hierarchy,
    map_category,
)
from src.configs.globals import CATEGORIES_MAP

VALID_SUPER_CATEGORIES = set(CATEGORIES_MAP.values()) - {"None"}


class TestFSQTopLevelToSuperDict:
    def test_all_nine_top_level_present(self):
        expected = {
            "Arts & Entertainment", "College & University", "Food",
            "Nightlife Spot", "Outdoors & Recreation", "Professional & Other Places",
            "Residence", "Shop & Service", "Travel & Transport",
        }
        assert set(FSQ_TOP_LEVEL_TO_SUPER.keys()) == expected

    def test_all_values_valid_super_categories(self):
        for raw, sup in FSQ_TOP_LEVEL_TO_SUPER.items():
            assert sup in VALID_SUPER_CATEGORIES, f"'{raw}' → '{sup}' not in taxonomy"

    def test_covers_all_seven_super_categories(self):
        assert set(FSQ_TOP_LEVEL_TO_SUPER.values()) == VALID_SUPER_CATEGORIES


class TestLoadHierarchy:
    def test_top_level_categories_in_hierarchy(self, massive_steps_categories_csv):
        h = load_hierarchy(massive_steps_categories_csv)
        assert h.get("Food") == "Food"
        assert h.get("Arts & Entertainment") == "Entertainment"
        assert h.get("Shop & Service") == "Shopping"

    def test_subcategory_resolved_via_parent(self, massive_steps_categories_csv):
        """'Italian Restaurant' → parent 'Food' → super 'Food'."""
        h = load_hierarchy(massive_steps_categories_csv)
        assert h.get("Italian Restaurant") == "Food"

    def test_returns_dict(self, massive_steps_categories_csv):
        h = load_hierarchy(massive_steps_categories_csv)
        assert isinstance(h, dict)

    def test_all_hierarchy_values_are_valid(self, massive_steps_categories_csv):
        h = load_hierarchy(massive_steps_categories_csv)
        for name, sup in h.items():
            assert sup in VALID_SUPER_CATEGORIES, f"'{name}' → '{sup}' not in taxonomy"


class TestMapCategory:
    def test_top_level_direct_match(self):
        assert map_category("Food") == "Food"
        assert map_category("Shop & Service") == "Shopping"
        assert map_category("Nightlife Spot") == "Nightlife"

    def test_subcategory_via_hierarchy(self, massive_steps_categories_csv):
        h = load_hierarchy(massive_steps_categories_csv)
        assert map_category("Italian Restaurant", h) == "Food"

    def test_unknown_category_returns_none(self):
        assert map_category("Totally Unknown") is None

    def test_empty_string_returns_none(self):
        assert map_category("") is None

    def test_none_hierarchy_uses_comprehensive_mapping(self):
        # The comprehensive shared dict covers subcategories — no hierarchy needed.
        assert map_category("Food", None) == "Food"
        assert map_category("Italian Restaurant", None) == "Food"

    def test_whitespace_stripped(self):
        """map_category strips leading/trailing whitespace."""
        assert map_category("  Food  ") == "Food"
        assert map_category("\tShop & Service\t") == "Shopping"
