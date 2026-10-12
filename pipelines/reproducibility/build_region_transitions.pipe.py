#!/usr/bin/env python3
"""Stable CLI for building full-data or leakage-free per-fold region priors.

The implementation lives in :mod:`src.data.region_transitions`.  This pipeline is
the durable entrypoint cited by the dissertation; experimental launchers under
``scripts/`` may call it but are not sources of record.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data.region_transitions import main


if __name__ == "__main__":
    main()
