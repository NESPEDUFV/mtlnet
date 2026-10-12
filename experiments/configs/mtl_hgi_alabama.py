"""Declarative config constructor: MTL + HGI + Alabama.

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
    """MTL baseline: HGI embeddings, Alabama dataset."""
    return ExperimentConfig.default_mtl(
        name="mtl_hgi_alabama",
        state="alabama",
        embedding_engine="hgi",
    )
