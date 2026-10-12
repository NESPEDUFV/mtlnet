"""Hybrid GRU + attention next-task head."""

import torch
import torch.nn as nn

from models.registry import register_model


@register_model("next_hybrid")
class NextHeadHybrid(nn.Module):
    """Hybrid GRU + self-attention next-category predictor."""

    def __init__(
        self,
        embed_dim: int,
        hidden_dim: int = 256,
        num_classes: int = 7,
        num_heads: int = 4,
        num_gru_layers: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.gru = nn.GRU(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_gru_layers,
            dropout=dropout if num_gru_layers > 1 else 0.0,
            batch_first=True,
        )
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.norm1 = nn.LayerNorm(hidden_dim)
        self.norm2 = nn.LayerNorm(hidden_dim)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        padding_mask = (x.abs().sum(dim=-1) == 0)
        gru_out, _ = self.gru(x)
        gru_out = self.norm1(gru_out)

        attn_out, _ = self.attention(
            gru_out,
            gru_out,
            gru_out,
            key_padding_mask=padding_mask,
            need_weights=True,
        )
        out = self.norm2(gru_out + attn_out)

        seq_lengths = (~padding_mask).sum(dim=1)
        batch_size = x.size(0)
        last_outputs = []
        for i in range(batch_size):
            last_idx = seq_lengths[i] - 1
            last_outputs.append(out[i, last_idx])

        last_output = torch.stack(last_outputs)
        return self.classifier(last_output)


__all__ = ["NextHeadHybrid"]
