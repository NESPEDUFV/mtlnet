"""Category multi-path ensemble head."""

import torch
from torch import nn

from models.registry import register_model


@register_model("category_ensemble")
class CategoryHeadEnsemble(nn.Module):
    """Multi-path architecture that combines parallel pathways."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        num_paths: int = 3,
        num_classes: int = 7,
        dropout: float = 0.5,
    ):
        super().__init__()
        self.num_paths = num_paths

        self.paths = nn.ModuleList([
            self._make_path(input_dim, hidden_dim, depth=i + 2, dropout=dropout)
            for i in range(num_paths)
        ])

        self.combiner = nn.Sequential(
            nn.Linear(hidden_dim * num_paths, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def _make_path(self, input_dim: int, hidden_dim: int, depth: int, dropout: float) -> nn.Module:
        layers = []
        prev_dim = input_dim
        for i in range(depth):
            current_hidden = hidden_dim if i == depth - 1 else hidden_dim // (2 ** (depth - i - 1))
            current_hidden = max(current_hidden, hidden_dim)
            layers.extend([
                nn.Linear(prev_dim, current_hidden),
                nn.LayerNorm(current_hidden),
                nn.GELU(),
                nn.Dropout(dropout) if i < depth - 1 else nn.Identity(),
            ])
            prev_dim = current_hidden
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Support [B, 1, D] (MTL) and [B, D] (standalone).
        x = x.squeeze(1)
        path_outputs = [path(x) for path in self.paths]
        combined = torch.cat(path_outputs, dim=-1)
        return self.combiner(combined)


__all__ = ["CategoryHeadEnsemble"]
