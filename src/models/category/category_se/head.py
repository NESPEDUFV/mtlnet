"""Category squeeze-and-excitation head."""

import torch
from torch import nn

from models.registry import register_model


@register_model("category_se")
class SEHead(nn.Module):
    """SE-style reweighting followed by MLP classifier."""

    def __init__(self, input_dim, reduction=8, hidden_dims=(128, 64), num_classes=7):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, input_dim // reduction)
        self.fc2 = nn.Linear(input_dim // reduction, input_dim)
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.GELU(), nn.Dropout(0.1)]
            prev = h
        self.deep = nn.Sequential(*layers)
        self.classifier = nn.Linear(prev, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        s = torch.relu(self.fc1(x))
        g = torch.sigmoid(self.fc2(s))
        x = x * g
        x = self.deep(x)
        return self.classifier(x)


__all__ = ["SEHead"]
