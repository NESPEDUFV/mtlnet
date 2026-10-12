"""External-baseline trainers for the PoiMtlNet board.

Each baseline is a standalone, NON-CONFLICTING module (one file per baseline)
that REUSES the frozen fold split + leak protocol + scored metrics of the
champion, but never edits ``src/`` or ``scripts/train.py``. See the per-file
docstrings for the class (A: substrate-column, B: e2e-trainer, C: cascade) and
its documented deviations from the cited paper.
"""
