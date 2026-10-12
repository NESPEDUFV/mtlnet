"""
Input Generation Module (canonical location since Phase 5).

Modular, maintainable input generation for MTLnet training.

- core.py: Pure logic functions (generate_sequences, create_*_lookup)
- loaders.py: Data loading with caching (EmbeddingLoader)
- builders.py: Input generation functions (generate_category_input, generate_next_input_*)
- fusion.py: Multi-embedding fusion (EmbeddingAligner, EmbeddingFuser, MultiEmbeddingInputGenerator)

Usage:
    from data.inputs import generate_sequences, create_embedding_lookup
    from data.inputs import EmbeddingLoader
    from data.inputs import generate_category_input, generate_next_input_from_poi
    from data.inputs import MultiEmbeddingInputGenerator
"""
from __future__ import annotations

import importlib
import sys

__all__ = [
    # Core functions
    'generate_sequences',
    'create_embedding_lookup',
    'create_category_lookup',
    'get_zero_embedding',
    'parse_and_sort_checkins',
    'save_parquet',
    'save_next_input_dataframe',
    'convert_sequences_to_poi_embeddings',
    # Constants
    'PADDING_VALUE',
    'MIN_SEQUENCE_LENGTH',
    'DEFAULT_BATCH_SIZE',
    'MISSING_CATEGORY_VALUE',
    # Loaders
    'EmbeddingLoader',
    # Builders
    'generate_category_input',
    'generate_next_input_from_poi',
    'generate_next_input_from_checkins',
    # Fusion
    'EmbeddingAligner',
    'EmbeddingFuser',
    'MultiEmbeddingInputGenerator',
]

__version__ = '2.0.0'

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # core
    'generate_sequences': ('data.inputs.core', 'generate_sequences'),
    'create_embedding_lookup': ('data.inputs.core', 'create_embedding_lookup'),
    'create_category_lookup': ('data.inputs.core', 'create_category_lookup'),
    'get_zero_embedding': ('data.inputs.core', 'get_zero_embedding'),
    'parse_and_sort_checkins': ('data.inputs.core', 'parse_and_sort_checkins'),
    'save_parquet': ('data.inputs.core', 'save_parquet'),
    'save_next_input_dataframe': ('data.inputs.core', 'save_next_input_dataframe'),
    'convert_sequences_to_poi_embeddings': ('data.inputs.core', 'convert_sequences_to_poi_embeddings'),
    'PADDING_VALUE': ('data.inputs.core', 'PADDING_VALUE'),
    'MIN_SEQUENCE_LENGTH': ('data.inputs.core', 'MIN_SEQUENCE_LENGTH'),
    'DEFAULT_BATCH_SIZE': ('data.inputs.core', 'DEFAULT_BATCH_SIZE'),
    'MISSING_CATEGORY_VALUE': ('data.inputs.core', 'MISSING_CATEGORY_VALUE'),
    # loaders
    'EmbeddingLoader': ('data.inputs.loaders', 'EmbeddingLoader'),
    # builders
    'generate_category_input': ('data.inputs.builders', 'generate_category_input'),
    'generate_next_input_from_poi': ('data.inputs.builders', 'generate_next_input_from_poi'),
    'generate_next_input_from_checkins': ('data.inputs.builders', 'generate_next_input_from_checkins'),
    # fusion
    'EmbeddingAligner': ('data.inputs.fusion', 'EmbeddingAligner'),
    'EmbeddingFuser': ('data.inputs.fusion', 'EmbeddingFuser'),
    'MultiEmbeddingInputGenerator': ('data.inputs.fusion', 'MultiEmbeddingInputGenerator'),
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module_name, attr = _LAZY_IMPORTS[name]
        mod = importlib.import_module(module_name)
        value = getattr(mod, attr)
        setattr(sys.modules[__name__], name, value)
        return value
    raise AttributeError(f"module 'data.inputs' has no attribute {name!r}")
