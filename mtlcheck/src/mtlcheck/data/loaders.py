"""Batching — including the one decision that silently changes what the joint model learns.

**Cross-task pairing (invariant S13).** The joint model's cross-attention consumes a category row and
a region row together. In the reference the two training loaders draw **independent shuffles**, so
at train time the two rows are unrelated windows, while validation walks both streams in order and
pairs them correctly. Every banked v18 joint cell trained that way. Aligned pairing exists there only
as a flag that is off by default and that no driver passes, on a gate that was never closed.

The natural clean implementation — one dataset yielding `(x_cat, x_reg, y_cat, y_reg)` per row — is
the ALIGNED variant. It is a different training distribution for the shared trunk, and none of the
headline conclusions would detect the swap. So the modes are explicit, the v18-faithful one is the
default, and choosing the other is a decision recorded in the run's configuration.

Batching itself is deliberately plain: the tensors live on the accelerator and a batch is an
`index_select`. No worker processes, no host-to-device copy per step, no collate function.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterator

import torch

from ..config import Pairing

logger = logging.getLogger(__name__)


@dataclass
class TaskStream:
    """One task's tensors for one split, resident on the compute device."""

    x: torch.Tensor        # [N, 9, D]
    y: torch.Tensor        # [N]
    aux: torch.Tensor | None = None    # [N] — e.g. last_region_idx for the flow head

    def __len__(self) -> int:
        return self.y.shape[0]

    def to(self, device: torch.device) -> "TaskStream":
        return TaskStream(
            x=self.x.to(device, non_blocking=True),
            y=self.y.to(device, non_blocking=True),
            aux=None if self.aux is None else self.aux.to(device, non_blocking=True),
        )

    def take(self, index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor | None]:
        return (
            self.x.index_select(0, index),
            self.y.index_select(0, index),
            None if self.aux is None else self.aux.index_select(0, index),
        )


def batches(stream: TaskStream, batch_size: int, *, shuffle: bool,
            generator: torch.Generator | None = None) -> Iterator[tuple]:
    """Single-task batches over a device-resident stream."""
    n = len(stream)
    order = (torch.randperm(n, generator=generator, device="cpu").to(stream.y.device)
             if shuffle else torch.arange(n, device=stream.y.device))
    for start in range(0, n, batch_size):
        yield stream.take(order[start : start + batch_size])


def joint_batches(cat: TaskStream, reg: TaskStream, batch_size: int, *,
                  shuffle: bool, pairing: Pairing,
                  generator: torch.Generator | None = None) -> Iterator[tuple[tuple, tuple]]:
    """Batches of (category, region) pairs for the joint model.

    `shuffle=False` (validation) always walks both streams in order, so the pairing mode is
    irrelevant there — validation is aligned by construction, in both implementations.
    """
    n = len(cat)
    if len(reg) != n:
        # The reference tolerates unequal lengths by cycling the shorter loader, which re-feeds and
        # DOUBLE-COUNTS its leading rows in the scored metrics. That path exists for legacy task
        # pairs; on this task pair both tasks index the same rows, so unequal lengths mean something
        # upstream is broken and silently over-weighting a subset is the wrong response.
        raise ValueError(
            f"category stream has {n} rows and region stream has {len(reg)}; on this task pair both "
            f"tasks index the same windows, so they must match"
        )

    if not shuffle:
        order_cat = order_reg = torch.arange(n, device=cat.y.device)
    elif pairing is Pairing.ALIGNED:
        order_cat = order_reg = torch.randperm(n, generator=generator).to(cat.y.device)
    else:
        # Two independent draws — the v18-faithful mode.
        order_cat = torch.randperm(n, generator=generator).to(cat.y.device)
        order_reg = torch.randperm(n, generator=generator).to(reg.y.device)

    for start in range(0, n, batch_size):
        window = slice(start, start + batch_size)
        yield cat.take(order_cat[window]), reg.take(order_reg[window])


def steps_per_epoch(n_rows: int, batch_size: int) -> int:
    """Optimizer steps in one epoch — what the LR schedule must be built against.

    Trivial arithmetic, given its own name because getting it wrong is invisible: the schedule
    finishes mid-cycle and every learning rate after the first epoch is off, with no error and no
    shape mismatch. The reference had to correct exactly this when a loader-length rule changed.
    """
    return -(-n_rows // batch_size)      # ceil


__all__ = ["TaskStream", "batches", "joint_batches", "steps_per_epoch"]
