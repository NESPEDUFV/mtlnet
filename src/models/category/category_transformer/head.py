"""Category transformer head variant."""

import torch
from torch import nn

from models.registry import register_model


@register_model("category_transformer")
class CategoryHeadTransformer(nn.Module):
    """Split embedding into tokens, encode with Transformer, classify pooled output."""

    def __init__(
        self,
        input_dim: int,
        num_tokens: int = 4,
        token_dim: int = 16,
        num_layers: int = 2,
        num_heads: int = 8,
        dropout: float = 0.2,
        num_classes: int = 7,
    ):
        super().__init__()
        assert num_tokens * token_dim == input_dim, (
            f"need num_tokens*token_dim==input_dim ({num_tokens}x{token_dim}!={input_dim})"
        )

        self.num_tokens = num_tokens
        self.token_dim = token_dim

        self.token_proj = nn.Linear(input_dim, num_tokens * token_dim)
        self.pos_emb = nn.Parameter(torch.randn(1, num_tokens, token_dim))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=token_dim,
            nhead=num_heads,
            dim_feedforward=token_dim * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers,
            norm=nn.LayerNorm(token_dim),
        )
        self.classifier = nn.Sequential(
            nn.LayerNorm(token_dim),
            nn.GELU(),
            nn.Linear(token_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, _ = x.shape
        tokens = self.token_proj(x)
        tokens = tokens.view(batch_size, self.num_tokens, self.token_dim)
        tokens = tokens + self.pos_emb
        encoded = self.transformer(tokens)
        pooled = encoded.mean(dim=1)
        return self.classifier(pooled)


__all__ = ["CategoryHeadTransformer"]
