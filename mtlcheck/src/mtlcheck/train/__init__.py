"""Layer 3 — tensors to metrics.

    losses.py   the three criteria this system uses
    metrics.py  streamed, device-independent validation metrics
    scoring.py  the two epoch-selection conventions
    runner.py   THE training loop — one loop, three families

One runner, because the reference had three and the copy that drifted cost two months.
"""

from . import losses, metrics, runner, scoring

__all__ = ["losses", "metrics", "scoring", "runner"]
