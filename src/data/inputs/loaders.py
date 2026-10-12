"""
Data loading classes with caching.

Moved from etl/embedding_fusion.py for better organization.
"""

import logging
from typing import Dict
import pandas as pd
import gc

logger = logging.getLogger(__name__)

from configs.paths import IoPaths, EmbeddingEngine
from configs.embedding_fusion import EmbeddingSpec


class EmbeddingLoader:
    """
    Loads and caches embedding DataFrames.

    Caching avoids redundant I/O when multiple tasks use the same embedding source.
    """

    def __init__(self, state: str):
        """
        Initialize loader for a specific state.

        Args:
            state: State name (e.g., 'florida', 'alabama')
        """
        self.state = state
        self._cache: Dict[EmbeddingEngine, pd.DataFrame] = {}

    def load(self, spec: EmbeddingSpec) -> pd.DataFrame:
        """
        Load embedding DataFrame, using cache if available.

        Args:
            spec: Embedding specification

        Returns:
            DataFrame with embedding data
        """
        if spec.engine not in self._cache:
            df = IoPaths.load_embedd(self.state, spec.engine)
            self._cache[spec.engine] = df
            logger.info("  Loaded %s: %s", spec.engine.value, df.shape)

        return self._cache[spec.engine]

    def clear_cache(self):
        """Free memory by clearing cache."""
        self._cache.clear()
        gc.collect()
