"""Stage 2 — everything that turns persisted predictions into a verdict.

Deliberately separate from `train/`: stage 1 writes rows and never judges, stage 2 judges and never
trains. The seal on the outer fold is then a property of the data flow rather than of discipline —
there is no outer-test number to look at while a wave runs, so there is no looking early.
"""

from . import compare, estimands, multiplicity, predictions

__all__ = ["compare", "estimands", "multiplicity", "predictions"]
