"""Category deep-and-cross head."""

import torch
from torch import nn

from models.registry import register_model


@register_model("category_dcn")
class DCNHead(nn.Module):
    """Deep & Cross Network head for category classification."""

    def __init__(self, input_dim, hidden_dims, num_classes, cross_layers=2, dropout=0.0):
        super().__init__()
        self.cross_layers = nn.ModuleList([
            nn.Linear(input_dim, 1, bias=True)
            for _ in range(cross_layers)
        ])
        prev = input_dim
        deep = []
        for h in hidden_dims:
            deep += [nn.Linear(prev, h), nn.GELU(), nn.LayerNorm(h), nn.Dropout(dropout)]
            prev = h
        self.deep = nn.Sequential(*deep)
        self.classifier = nn.Linear(prev + input_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x0 = x
        x_cross = x
        for layer in self.cross_layers:
            scalar = layer(x_cross)
            x_cross = x0 * scalar + x_cross
        x_deep = self.deep(x)
        return self.classifier(torch.cat([x_cross, x_deep], dim=-1))


__all__ = ["DCNHead"]
