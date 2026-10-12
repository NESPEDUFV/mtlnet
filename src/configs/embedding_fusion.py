"""
Multi-Embedding Fusion Configuration

This module provides configuration classes for fusing multiple embedding sources
into combined feature vectors for MTLnet training.

Key concepts:
- EmbeddingLevel: POI-level (one per POI) vs check-in-level (one per visit)
- EmbeddingSpec: Specification for a single embedding source
- FusionConfig: Defines which embeddings to combine for each task
- FUSION_PRESETS: Pre-configured fusion patterns
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from configs.paths import EmbeddingEngine


class EmbeddingLevel(Enum):
    """
    Embedding granularity level.

    POI: One embedding per unique POI (same POI = same embedding across all visits)
          Examples: DGI, HGI, Space2Vec, Sphere2Vec, POI2HGI

    CHECKIN: One embedding per check-in event (same POI at different times = different embeddings)
             Examples: Time2Vec, Check2HGI
    """
    POI = "poi"
    CHECKIN = "checkin"


@dataclass
class EmbeddingSpec:
    """
    Specification for a single embedding source.

    Attributes:
        engine: Embedding engine type (DGI, HGI, Time2Vec, etc.)
        level: Granularity level (POI or CHECKIN)
        dimension: Embedding dimensionality (typically 64)

    Raises:
        AssertionError: If engine type doesn't match expected level
    """
    engine: EmbeddingEngine
    level: EmbeddingLevel
    dimension: int

    def __post_init__(self):
        """Validate that engine type matches embedding level."""
        # Check-in level engines
        if self.engine in [EmbeddingEngine.CHECK2HGI, EmbeddingEngine.TIME2VEC]:
            assert self.level == EmbeddingLevel.CHECKIN, \
                f"{self.engine.value} must use EmbeddingLevel.CHECKIN"

        # POI-level engines
        elif self.engine in [
            EmbeddingEngine.HGI,
            EmbeddingEngine.DGI,
            EmbeddingEngine.SPACE2VEC,
            EmbeddingEngine.SPHERE2VEC,
            EmbeddingEngine.POI2HGI,
            EmbeddingEngine.HMRM
        ]:
            assert self.level == EmbeddingLevel.POI, \
                f"{self.engine.value} must use EmbeddingLevel.POI"

        # Unknown engine - allow but warn
        else:
            import logging
            logging.getLogger(__name__).warning("Unknown engine %s, validation skipped", self.engine.value)

    def __repr__(self) -> str:
        return f"EmbeddingSpec({self.engine.value}, {self.level.value}, {self.dimension}D)"


@dataclass
class FusionConfig:
    """
    Configuration for multi-embedding fusion.

    Defines which embeddings to combine for category and next-POI tasks.

    Attributes:
        category_embeddings: List of embeddings for category task (must be POI-level)
        next_embeddings: List of embeddings for next-POI task (can mix POI and check-in level)

    Raises:
        AssertionError: If category task uses check-in-level embeddings
    """
    category_embeddings: List[EmbeddingSpec]
    next_embeddings: List[EmbeddingSpec]

    def __post_init__(self):
        """Validate that category task only uses POI-level embeddings."""
        for spec in self.category_embeddings:
            assert spec.level == EmbeddingLevel.POI, \
                f"Category task requires POI-level embeddings, got {spec}"

    def get_category_dim(self) -> int:
        """Get total dimension for category task (sum of all sources)."""
        return sum(spec.dimension for spec in self.category_embeddings)

    def get_next_dim(self) -> int:
        """Get total dimension for next-POI task (sum of all sources)."""
        return sum(spec.dimension for spec in self.next_embeddings)

    def get_category_engines(self) -> List[str]:
        """Get list of engine names for category task."""
        return [spec.engine.value for spec in self.category_embeddings]

    def get_next_engines(self) -> List[str]:
        """Get list of engine names for next-POI task."""
        return [spec.engine.value for spec in self.next_embeddings]

    def __repr__(self) -> str:
        cat_str = " + ".join([f"{s.engine.value}({s.dimension})" for s in self.category_embeddings])
        next_str = " + ".join([f"{s.engine.value}({s.dimension})" for s in self.next_embeddings])
        return (
            f"FusionConfig(\n"
            f"  category: {cat_str} = {self.get_category_dim()}D\n"
            f"  next:     {next_str} = {self.get_next_dim()}D\n"
            f")"
        )


# ============================================================================
# Preset Configurations
# ============================================================================

FUSION_PRESETS = {
    "space_hgi_time": FusionConfig(
        category_embeddings=[
            EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, 64),
            EmbeddingSpec(EmbeddingEngine.SPHERE2VEC, EmbeddingLevel.POI, 64),
        ],
        next_embeddings=[
            EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, 64),
            EmbeddingSpec(EmbeddingEngine.TIME2VEC, EmbeddingLevel.CHECKIN, 64),
        ],
    ),

    "hgi_time": FusionConfig(
        category_embeddings=[
            EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, 64),
            EmbeddingSpec(EmbeddingEngine.SPHERE2VEC, EmbeddingLevel.POI, 64),
        ],
        next_embeddings=[
            EmbeddingSpec(EmbeddingEngine.HGI, EmbeddingLevel.POI, 64),
            EmbeddingSpec(EmbeddingEngine.TIME2VEC, EmbeddingLevel.CHECKIN, 64),
        ],
    ),

    "space_time": FusionConfig(
        category_embeddings=[
            EmbeddingSpec(EmbeddingEngine.SPHERE2VEC, EmbeddingLevel.POI, 64),
        ],
        next_embeddings=[
            EmbeddingSpec(EmbeddingEngine.SPHERE2VEC, EmbeddingLevel.POI, 64),
            EmbeddingSpec(EmbeddingEngine.TIME2VEC, EmbeddingLevel.CHECKIN, 64),
        ],
    ),
}


def get_preset(name: str) -> FusionConfig:
    """
    Get a preset fusion configuration by name.

    Args:
        name: Preset name (e.g., 'space_hgi_time')

    Returns:
        FusionConfig instance

    Raises:
        KeyError: If preset name doesn't exist
    """
    if name not in FUSION_PRESETS:
        available = ", ".join(FUSION_PRESETS.keys())
        raise KeyError(f"Unknown preset '{name}'. Available: {available}")

    return FUSION_PRESETS[name]
