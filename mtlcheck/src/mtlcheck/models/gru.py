"""The category head: a GRU over the nine historical visits, read at the last valid step.

Faithful to the reference (`next_gru`): two GRU layers of width 256, dropout 0.3, and a
LayerNorm -> Dropout -> Linear classifier over the last valid hidden state.

One deliberate change. The reference locates the last valid step by COUNTING unpadded positions
(`last_idx = num_valid - 1`), which is correct only when padding is strictly trailing. This uses the
position of the last valid step instead, which agrees wherever the reference is right and stays
right where it is not. On v18 data the two are identical — stride-1 windows contain no padding at
all — so this changes no number; it removes a dependency on an invariant nothing checks. Recorded as
R11 in docs/REFERENCE_DEFECTS.md.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class CategoryHead(nn.Module):
    """[B, S, D] -> [B, num_classes]."""

    def __init__(self, embed_dim: int, num_classes: int, *, hidden_dim: int = 256,
                 num_layers: int = 2, dropout: float = 0.3) -> None:
        super().__init__()
        self.gru = nn.GRU(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))

    def features(self, x: torch.Tensor) -> torch.Tensor:
        """The pre-classifier state — the last valid step's hidden vector."""
        output, _ = self.gru(x)
        index = last_valid_index(x)
        rows = torch.arange(x.size(0), device=output.device)
        return output[rows, index]


def last_valid_index(x: torch.Tensor) -> torch.Tensor:
    """Position of the last non-padded step in each row of [B, S, D].

    A step is padding when its whole feature vector is zero — the convention every head in this
    system shares. An all-padding row (which cannot occur at stride 1) clamps to 0 rather than
    wrapping to -1.

    Computed as the last True position rather than `count - 1`, so interior or trailing-only
    assumptions do not silently decide the answer.
    """
    valid = x.abs().sum(dim=-1) != 0                      # [B, S]
    steps = torch.arange(x.size(1), device=x.device)
    return torch.where(valid, steps, torch.zeros_like(steps)).max(dim=1).values


__all__ = ["CategoryHead", "last_valid_index"]
