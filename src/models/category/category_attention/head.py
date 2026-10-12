"""Category attention-pooling head."""

import torch
from torch import nn

from models.registry import register_model


@register_model("category_attention")
class CategoryHeadAttentionPooling(nn.Module):
    """MLP with attention-based pooling over feature dimensions."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        num_classes: int = 7,
        dropout: float = 0.5,
    ):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.attention_weights = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.proj(x)
        att_scores = self.attention_weights(h)
        att_weights = torch.sigmoid(att_scores)
        weighted_h = h * att_weights
        return self.classifier(weighted_h)


__all__ = ["CategoryHeadAttentionPooling"]
