"""
Unit tests for Foursquare category mapping.

Tests the comprehensive shared mapping via src/etl/foursquare/utils/category_mapping.py,
which now delegates to src/etl/utils/category_mapping.py.
"""

import pytest

from src.etl.foursquare.utils.category_mapping import SUBCATEGORY_TO_SUPER, map_category
from src.configs.globals import CATEGORIES_MAP

VALID_SUPER_CATEGORIES = set(CATEGORIES_MAP.values()) - {"None"}


class TestSubcategoryToSuperDict:
    def test_all_fsq_top_level_present(self):
        """The nine Foursquare top-level names must be present in the comprehensive dict."""
        top_level = {
            "Arts & Entertainment",
            "College & University",
            "Food",
            "Nightlife Spot",
            "Outdoors & Recreation",
            "Professional & Other Places",
            "Residence",
            "Shop & Service",
            "Travel & Transport",
        }
        for name in top_level:
            assert name in SUBCATEGORY_TO_SUPER, f"'{name}' not in SUBCATEGORY_TO_SUPER"

    def test_all_values_are_valid_super_categories(self):
        for raw, super_cat in SUBCATEGORY_TO_SUPER.items():
            assert super_cat in VALID_SUPER_CATEGORIES, (
                f"'{raw}' → '{super_cat}' not in {VALID_SUPER_CATEGORIES}"
            )

    def test_covers_all_seven_super_categories(self):
        assert set(SUBCATEGORY_TO_SUPER.values()) == VALID_SUPER_CATEGORIES

    def test_food_top_level_maps_to_food(self):
        assert SUBCATEGORY_TO_SUPER["Food"] == "Food"

    def test_nightlife_top_level_maps_to_nightlife(self):
        assert SUBCATEGORY_TO_SUPER["Nightlife Spot"] == "Nightlife"

    def test_shop_top_level_maps_to_shopping(self):
        assert SUBCATEGORY_TO_SUPER["Shop & Service"] == "Shopping"

    def test_travel_top_level_maps_to_travel(self):
        assert SUBCATEGORY_TO_SUPER["Travel & Transport"] == "Travel"

    def test_outdoors_top_level_maps_to_outdoors(self):
        assert SUBCATEGORY_TO_SUPER["Outdoors & Recreation"] == "Outdoors"

    def test_arts_top_level_maps_to_entertainment(self):
        assert SUBCATEGORY_TO_SUPER["Arts & Entertainment"] == "Entertainment"

    def test_college_top_level_maps_to_community(self):
        assert SUBCATEGORY_TO_SUPER["College & University"] == "Community"


class TestMapCategoryFunction:
    def test_top_level_food(self):
        assert map_category("Food") == "Food"

    def test_subcategory_italian_restaurant(self):
        assert map_category("Italian Restaurant") == "Food"

    def test_subcategory_coffee_shop(self):
        assert map_category("Coffee Shop") == "Food"

    def test_subcategory_bar_is_nightlife(self):
        assert map_category("Bar") == "Nightlife"

    def test_subcategory_nightclub_is_nightlife(self):
        assert map_category("Nightclub") == "Nightlife"

    def test_subcategory_museum_is_entertainment(self):
        assert map_category("Museum") == "Entertainment"

    def test_subcategory_park_is_outdoors(self):
        assert map_category("Park") == "Outdoors"

    def test_subcategory_clothing_store_is_shopping(self):
        assert map_category("Clothing Store") == "Shopping"

    def test_subcategory_hotel_is_travel(self):
        assert map_category("Hotel") == "Travel"

    def test_subcategory_hospital_is_community(self):
        assert map_category("Hospital") == "Community"

    def test_shop_service_maps_to_shopping(self):
        assert map_category("Shop & Service") == "Shopping"

    def test_event_returns_none(self):
        assert map_category("Event") is None

    def test_unknown_string_returns_none(self):
        assert map_category("Totally Unknown Category") is None

    def test_empty_string_returns_none(self):
        assert map_category("") is None

    def test_none_input_returns_none(self):
        assert map_category(None) is None  # type: ignore[arg-type]

    def test_whitespace_stripped(self):
        """map_category strips leading/trailing whitespace."""
        assert map_category("  Food  ") == "Food"
        assert map_category("\tBar\t") == "Nightlife"

    def test_case_sensitive(self):
        assert map_category("food") is None
        assert map_category("FOOD") is None
