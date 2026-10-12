
"""
Category mapping for the Foursquare TIST2015 dataset (Yang et al.).

Delegates to the shared comprehensive mapping in src/etl/utils/category_mapping.py.
Re-exports map_category and SUBCATEGORY_TO_SUPER for backward compatibility.
"""

from src.etl.utils.category_mapping import SUBCATEGORY_TO_SUPER, map_category

__all__ = ["SUBCATEGORY_TO_SUPER", "map_category"]
