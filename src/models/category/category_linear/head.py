"""Linear probe category head — single linear layer, no hidden layers.

Diagnostic head: if this matches deeper heads, it proves the shared
backbone is doing all the representational work, which is exactly what
you want in MTL.
"""

import torch
from torch import nn

from models.registry import register_model


@register_model("category_linear")
class CategoryHeadLinear(nn.Module):
    """Single linear layer for category classification (diagnostic probe)."""

    def __init__(
        self,
        input_dim: int,
        num_classes: int = 7,
    ):
        super().__init__()
        self.classifier = nn.Linear(input_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(x)


__all__ = ["CategoryHeadLinear"]
