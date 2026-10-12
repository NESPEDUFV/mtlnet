"""Category gated head variant."""

import torch
from torch import nn

from models.registry import register_model


class _GatedLayer(nn.Module):
    """Single gated layer with GLU-style gating."""

    def __init__(self, input_dim: int, output_dim: int, dropout: float):
        super().__init__()
        self.transform = nn.Sequential(
            nn.Linear(input_dim, output_dim),
            nn.LayerNorm(output_dim),
        )
        self.gate = nn.Sequential(
            nn.Linear(input_dim, output_dim),
            nn.Sigmoid(),
        )
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.transform(x)
        g = self.gate(x)
        return self.dropout(self.activation(h * g))


@register_model("category_gated")
class CategoryHeadGated(nn.Module):
    """MLP with gating mechanism to emphasize important features."""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: tuple[int, ...],
        num_classes: int,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.input_gate = nn.Sequential(
            nn.Linear(input_dim, input_dim),
            nn.Sigmoid(),
        )

        self.layers = nn.ModuleList()
        prev_dim = input_dim
        for h in hidden_dims:
            self.layers.append(_GatedLayer(prev_dim, h, dropout))
            prev_dim = h

        self.classifier = nn.Linear(prev_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = self.input_gate(x)
        x = x * gate
        for layer in self.layers:
            x = layer(x)
        return self.classifier(x)


__all__ = ["CategoryHeadGated"]
