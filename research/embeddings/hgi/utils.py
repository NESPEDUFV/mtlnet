"""Utility functions for HGI preprocessing."""

import numpy as np
import scipy.spatial


class SpatialUtils:
    """Utility functions for spatial operations."""

    @staticmethod
    def haversine_np(lon1, lat1, lon2, lat2):
        """Calculate great circle distance between two points (in meters)."""
        lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        return 6378137 * c  # Earth radius in meters

    @staticmethod
    def diagonal_length_bbox(bbox):
        """Calculate diagonal length of a bounding box (min_x, min_y, max_x, max_y)."""
        x1, y1, x2, y2 = bbox
        dist_x = scipy.spatial.distance.euclidean((x1, y1), (x2, y1))
        dist_y = scipy.spatial.distance.euclidean((x1, y1), (x1, y2))
        return np.sqrt(dist_x ** 2 + dist_y ** 2)


def mode_or_first(series):
    """Get mode of a series, or first value if no clear mode."""
    if len(series) == 0:
        return None
    mode = series.mode()
    return mode.iloc[0] if len(mode) > 0 else series.iloc[0]
