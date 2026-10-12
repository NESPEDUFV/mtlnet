"""
Stable integer mapping for alphanumeric venue IDs.

Foursquare and Massive-STEPS datasets use hex/alphanumeric venue identifiers
(e.g. "4b058f49f964a520b04e23e3"). The downstream pipeline requires integer
placeid values for embedding lookups. VenueIndex builds and persists a
deterministic 0-based integer mapping.
"""

from pathlib import Path

import pandas as pd


class VenueIndex:
    """Maps string venue IDs to stable integer place IDs."""

    def __init__(self, mapping: dict[str, int]):
        self._mapping = mapping

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def build(cls, venue_ids: list[str]) -> "VenueIndex":
        """Assign 0-based integer indices to unique venue IDs (insertion order)."""
        seen: dict[str, int] = {}
        for vid in venue_ids:
            if vid not in seen:
                seen[vid] = len(seen)
        return cls(seen)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            {"venue_id": list(self._mapping.keys()), "placeid": list(self._mapping.values())}
        ).to_csv(path, index=False)

    @classmethod
    def load(cls, path: Path) -> "VenueIndex":
        df = pd.read_csv(path, dtype={"venue_id": str, "placeid": int})
        return cls(dict(zip(df["venue_id"], df["placeid"])))

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def map_series(self, venue_ids: pd.Series) -> pd.Series:
        """Map a Series of string venue IDs to integer place IDs.

        Raises KeyError if any venue_id is not in the index. Build the index
        from all venue IDs in the dataset before calling this.
        """
        return venue_ids.map(self._mapping).astype("int64")

    def __len__(self) -> int:
        return len(self._mapping)
