"""Thread-local side-channel for passing per-batch auxiliary tensors
to a model's head WITHOUT modifying the training-loop forward signature.

Motivation
----------
The ``next_getnext_hard`` head (B5 faithful GETNext) needs a per-sample
``last_region_idx`` tensor inside its forward pass. The existing MTL
training loop (``src/training/runners/mtl_cv.py``) is hot code shared by
every run family — changing its forward signature to thread aux through
every layer would be invasive and risky (the partition-bugfix rerun is
actively hitting that loop as this module is being written).

Design
------
1. ``POIDatasetWithAux`` yields ``(x, y, aux)`` 3-tuples.
2. ``AuxPublishingLoader`` wraps an ordinary ``DataLoader`` — on each
   iteration it **publishes** ``aux`` to a thread-local and yields
   ``(x, y)`` 2-tuples, so the training loop sees the same shape as
   today.
3. The head reads the published aux via ``get_current_aux()`` inside
   its ``forward`` method. Null-safe: if no aux has been published
   (e.g. evaluation outside the wrapped loader), the head falls back
   to pure STAN.

Caveats
-------
* Thread-local only works when the model's forward runs on the SAME
  thread that iterated the dataloader. PyTorch's default DataLoader
  behaviour (``num_workers=0``) and the training loop's synchronous
  ``for batch in loader`` structure both satisfy this.
* If ``num_workers > 0`` is introduced, the aux side-channel must be
  updated — workers serialise the batch (without the thread-local
  state), and the main thread's publish must happen after yield.
  The current design publishes in the main thread's iterator wrapper,
  which works for both ``num_workers=0`` and ``>0``.
* A single thread-local slot means only ONE aux-carrying head can be
  active per forward pass. For the B5 use case (only ``next_getnext_hard``
  on task_b, ``category`` head is aux-agnostic) this is sufficient.
"""

from __future__ import annotations

import threading
from typing import Iterator, Tuple

import torch
from torch.utils.data import DataLoader


_CURRENT_AUX = threading.local()


def get_current_aux() -> torch.Tensor | None:
    """Return the aux tensor published for the current batch, or ``None``
    if no aux has been published.

    Used inside head ``forward`` methods to access per-sample auxiliary
    data without threading it through the model signature.
    """
    return getattr(_CURRENT_AUX, "value", None)


def _publish_aux(aux: torch.Tensor | None) -> None:
    _CURRENT_AUX.value = aux


def _clear_aux() -> None:
    _CURRENT_AUX.value = None


class AuxPublishingLoader:
    """DataLoader wrapper that strips ``aux`` from ``(x, y, aux)`` batches
    and publishes it to the aux side-channel, yielding ``(x, y)`` to the
    training loop.

    Works with any downstream code that iterates the loader with
    ``for x, y in loader``. The wrapped loader MUST yield 3-tuples;
    a 2-tuple yield raises (misconfiguration — the dataset should be
    ``POIDatasetWithAux``).
    """

    def __init__(self, dataloader: DataLoader):
        self._loader = dataloader
        # Expose batch_size for callers that introspect it
        self.batch_size = getattr(dataloader, "batch_size", None)
        # Expose dataset attribute so `len(loader.dataset)` works through the wrapper
        self.dataset = getattr(dataloader, "dataset", None)

    def __iter__(self) -> Iterator[Tuple[torch.Tensor, torch.Tensor]]:
        for batch in self._loader:
            if len(batch) != 3:
                _clear_aux()
                raise ValueError(
                    "AuxPublishingLoader expected 3-tuple (x, y, aux) batches "
                    f"but got a tuple of length {len(batch)}. The underlying "
                    f"dataset must be POIDatasetWithAux."
                )
            x, y, aux = batch
            _publish_aux(aux)
            yield x, y
        _clear_aux()

    def __len__(self) -> int:
        return len(self._loader)


__all__ = [
    "AuxPublishingLoader",
    "get_current_aux",
]
