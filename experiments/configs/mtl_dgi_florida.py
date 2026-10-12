"""Declarative config constructor: MTL + DGI + Florida.

Exports config() -> ExperimentConfig. No training logic. No side effects.
"""
from __future__ import annotations

import sys
from pathlib import Path

_src = str(Path(__file__).resolve().parent.parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.experiment import ExperimentConfig


def config() -> ExperimentConfig:
    """MTL baseline: DGI embeddings, Florida dataset."""
    return ExperimentConfig.default_mtl(
        name="mtl_dgi_florida",
        state="florida",
        embedding_engine="dgi",
    )
