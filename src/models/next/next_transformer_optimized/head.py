"""Optimized transformer next-task head."""

import torch
import torch.nn as nn

from models.registry import register_model


@register_model("next_transformer_optimized")
class NextHeadTransformerOptimized(nn.Module):
    """Optimized Transformer for short sequences with temporal-decay pooling."""

    def __init__(
        self,
        embed_dim: int,
        num_classes: int,
        num_heads: int = 8,
        num_layers: int = 2,
        seq_length: int = 9,
        dropout: float = 0.3,
        use_temporal_decay: bool = True,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.seq_length = seq_length
        self.use_temporal_decay = use_temporal_decay

        self.pos_embedding = nn.Parameter(torch.randn(1, seq_length, embed_dim))
        self.dropout = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers, enable_nested_tensor=False)

        if use_temporal_decay:
            decay = torch.exp(-torch.arange(seq_length - 1, -1, -1).float() * 0.5)
            self.register_buffer("temporal_decay", decay)

        self.norm = nn.LayerNorm(embed_dim)
        self.classifier = nn.Linear(embed_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, _ = x.size()
        device = x.device

        padding_mask = (x.abs().sum(dim=-1) == 0)

        x = x + self.pos_embedding[:, :seq_len, :]
        x = self.dropout(x)

        causal_mask = torch.triu(
            torch.ones(seq_len, seq_len, dtype=torch.bool, device=device),
            diagonal=1,
        )

        x = self.transformer(x, mask=causal_mask, src_key_padding_mask=padding_mask)
        x = self.norm(x)

        if self.use_temporal_decay:
            decay_weights = self.temporal_decay[:seq_len].unsqueeze(0).unsqueeze(-1)
            weighted_x = x * decay_weights
            mask = (~padding_mask).unsqueeze(-1).float()
            weighted_x = weighted_x * mask
            pooled = weighted_x.sum(dim=1) / (mask.sum(dim=1) + 1e-9)
        else:
            seq_lengths = (~padding_mask).sum(dim=1)
            last_outputs = []
            for i in range(batch_size):
                last_idx = seq_lengths[i] - 1
                last_outputs.append(x[i, last_idx])
            pooled = torch.stack(last_outputs)

        return self.classifier(pooled)


__all__ = ["NextHeadTransformerOptimized"]
