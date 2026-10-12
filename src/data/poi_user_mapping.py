"""
Materialize POI → set(userids) mapping from raw checkins.

This artifact is required by the MTL split protocol (SPLIT_PROTOCOL.md Section 3)
to classify POIs as train-exclusive, val-exclusive, or ambiguous per fold.

Usage:
    from data.poi_user_mapping import build_poi_user_mapping, load_poi_user_mapping

    mapping = build_poi_user_mapping(state, engine)  # builds and saves
    mapping = load_poi_user_mapping(state, engine)    # loads existing
"""

import json
import logging
from pathlib import Path
from typing import Dict, Set

import pandas as pd

from configs.paths import EmbeddingEngine, IoPaths

logger = logging.getLogger(__name__)


def build_poi_user_mapping(state: str, engine: EmbeddingEngine) -> Dict[int, Set[int]]:
    """Build and save POI → set(userids) mapping from raw checkins.

    Args:
        state: State name (e.g., 'alabama')
        engine: Embedding engine (determines output directory)

    Returns:
        Dictionary mapping placeid to set of userids who visited it.
    """
    checkins_df = IoPaths.load_city(state)
    mapping = _build_mapping_from_df(checkins_df)

    # Save artifact
    output_path = _get_mapping_path(state, engine)
    _save_mapping(mapping, output_path)
    logger.info(f"POI→users mapping: {len(mapping)} POIs → {output_path}")

    return mapping


def _build_mapping_from_df(checkins_df: pd.DataFrame) -> Dict[int, Set[int]]:
    """Build POI → set(userids) from a checkins DataFrame."""
    mapping: Dict[int, Set[int]] = {}
    for placeid, userid in zip(checkins_df['placeid'], checkins_df['userid']):
        mapping.setdefault(placeid, set()).add(userid)
    return mapping


def _get_mapping_path(state: str, engine: EmbeddingEngine) -> Path:
    """Get the output path for the POI→users mapping artifact."""
    base = IoPaths.get_next(state, engine).parent
    return base / "poi_user_mapping.json"


def _save_mapping(mapping: Dict[int, Set[int]], path: Path) -> None:
    """Save mapping as JSON (sets serialized as sorted lists)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {str(k): sorted(v) for k, v in mapping.items()}
    with open(path, 'w') as f:
        json.dump(serializable, f)


def load_poi_user_mapping(state: str, engine: EmbeddingEngine) -> Dict[int, Set[int]]:
    """Load POI → set(userids) mapping from saved artifact.

    Returns:
        Dictionary mapping placeid to set of userids.

    Raises:
        FileNotFoundError: If mapping artifact doesn't exist.
    """
    path = _get_mapping_path(state, engine)
    if not path.exists():
        raise FileNotFoundError(
            f"POI→users mapping not found at {path}. "
            f"Run build_poi_user_mapping('{state}', {engine}) first."
        )
    with open(path) as f:
        raw = json.load(f)
    return {int(k): set(v) for k, v in raw.items()}
