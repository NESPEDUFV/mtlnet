"""Backward-compatible shim for MTL candidate helpers.

Canonical module lives at ``src/ablation/candidates.py``.
"""

import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from ablation.candidates import CANDIDATES, MTLCandidate, get_candidate, iter_candidates

__all__ = [
    "CANDIDATES",
    "MTLCandidate",
    "get_candidate",
    "iter_candidates",
]
