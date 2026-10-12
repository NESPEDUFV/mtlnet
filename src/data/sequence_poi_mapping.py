"""
Materialize sequence → POI mapping from intermediate sequence parquets.

This artifact maps each next-task sample (by row index) to the set of POI IDs
it contains. Required by the split protocol to classify sequences by
their POI overlap with train/val sets.

Usage:
    from data.sequence_poi_mapping import build_sequence_poi_mapping, load_sequence_poi_mapping

    mapping = build_sequence_poi_mapping(state, engine)  # builds from saved sequences
    mapping = load_sequence_poi_mapping(state, engine)    # loads existing artifact
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set

import pandas as pd

from configs.paths import EmbeddingEngine, IoPaths

logger = logging.getLogger(__name__)


def build_sequence_poi_mapping(state: str, engine: EmbeddingEngine) -> Dict[int, Set[int]]:
    """Build and save sequence_index → set(placeids) from intermediate sequences.

    Args:
        state: State name
        engine: Embedding engine

    Returns:
        Dictionary mapping row index to set of POI IDs in that sequence
        (including target).

    Raises:
        FileNotFoundError: If the intermediate sequence parquet doesn't exist.
    """
    seq_path = IoPaths.get_seq_next(state, engine)
    if not seq_path.exists():
        raise FileNotFoundError(
            f"Intermediate sequence parquet not found at {seq_path}. "
            f"Run the input generation pipeline first."
        )

    seq_df = pd.read_parquet(seq_path)
    poi_cols = [c for c in seq_df.columns if c.startswith("poi_") or c == "target_poi"]

    mapping: Dict[int, Set[int]] = {}
    for idx, row in seq_df[poi_cols].iterrows():
        pois = set(int(v) for v in row.values if int(v) != -1)  # exclude padding
        mapping[int(idx)] = pois

    # Save artifact
    output_path = _get_mapping_path(state, engine)
    _save_mapping(mapping, output_path)
    logger.info(f"Sequence→POI mapping: {len(mapping)} sequences → {output_path}")

    return mapping


def _get_mapping_path(state: str, engine: EmbeddingEngine) -> Path:
    """Get the output path for the sequence→POI mapping artifact."""
    base = IoPaths.get_next(state, engine).parent
    return base / "sequence_poi_mapping.json"


def _save_mapping(mapping: Dict[int, Set[int]], path: Path) -> None:
    """Save mapping as JSON (sets serialized as sorted lists)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {str(k): sorted(v) for k, v in mapping.items()}
    with open(path, 'w') as f:
        json.dump(serializable, f)


def load_sequence_poi_mapping(state: str, engine: EmbeddingEngine) -> Dict[int, Set[int]]:
    """Load sequence → set(placeids) mapping from saved artifact.

    Raises:
        FileNotFoundError: If mapping artifact doesn't exist.
    """
    path = _get_mapping_path(state, engine)
    if not path.exists():
        raise FileNotFoundError(
            f"Sequence→POI mapping not found at {path}. "
            f"Run build_sequence_poi_mapping('{state}', {engine}) first."
        )
    with open(path) as f:
        raw = json.load(f)
    return {int(k): set(v) for k, v in raw.items()}


def get_sequence_userids(state: str, engine: EmbeddingEngine) -> pd.Series:
    """Return userid for each sequence row from the intermediate parquet.

    Useful for aligning sequences with user-level splits.
    """
    seq_path = IoPaths.get_seq_next(state, engine)
    if not seq_path.exists():
        raise FileNotFoundError(
            f"Intermediate sequence parquet not found at {seq_path}."
        )
    seq_df = pd.read_parquet(seq_path, columns=["userid"])
    return seq_df["userid"]
