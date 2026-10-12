"""MTL transformer next-task head."""

import torch
import torch.nn as nn

from models.components.positional import PositionalEncoding
from models.registry import register_model


@register_model("next_mtl")
class NextHeadMTL(nn.Module):
    """Transformer next-task head used inside MTLnet."""

    def __init__(self, embed_dim, num_classes, num_heads, seq_length, num_layers, dropout=0.35):
        super().__init__()
        self.embed_dim = embed_dim
        self.seq_length = seq_length

        self.pe = PositionalEncoding(embed_dim, max_seq_length=seq_length, dropout=dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True,
            norm_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)

        self.sequence_reduction = nn.Linear(embed_dim, 1)
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.classifier = nn.Linear(embed_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, seq_length, _ = x.size()
        device = x.device

        padding_mask = (x.abs().sum(dim=-1) == 0)
        x = self.pe(x, padding_mask)

        causal_mask = torch.triu(
            torch.ones(seq_length, seq_length, dtype=torch.bool, device=device),
            diagonal=1,
        )

        x = self.transformer_encoder(x, mask=causal_mask, src_key_padding_mask=padding_mask)
        x = self.layer_norm(x)

        attn_logits = self.sequence_reduction(x).squeeze(-1)
        attn_logits = attn_logits.masked_fill(padding_mask, float("-inf"))

        attn_weights = torch.softmax(attn_logits, dim=1)
        attn_weights = torch.nan_to_num(attn_weights, nan=0.0).unsqueeze(-1)

        pooled = torch.sum(x * attn_weights, dim=1)
        out = self.classifier(pooled)
        return out


__all__ = ["NextHeadMTL"]
