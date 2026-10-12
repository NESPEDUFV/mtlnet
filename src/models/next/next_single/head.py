"""Standalone Transformer next-task head."""

import torch
import torch.nn as nn

from models.registry import register_model


@register_model("next_single")
class NextHeadSingle(nn.Module):
    """Transformer encoder with attention pooling for next-category prediction."""

    def __init__(self, embed_dim, num_classes, num_heads, seq_length, num_layers, dropout=0.2):
        super().__init__()
        self.embed_dim = embed_dim
        self.seq_length = seq_length

        # Learned positional embeddings (better than sinusoidal for short fixed-length sequences).
        self.pos_embedding = nn.Parameter(torch.randn(1, seq_length, embed_dim) * 0.02)
        self.dropout = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True,
            norm_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers, enable_nested_tensor=False)

        self.sequence_reduction = nn.Linear(embed_dim, 1)
        self.layer_norm = nn.LayerNorm(embed_dim)
        self.classifier = nn.Linear(embed_dim, num_classes)

        # Temporal decay bias for attention pooling (recent visits weighted more).
        self.temporal_bias = nn.Parameter(torch.linspace(-2.0, 0.0, seq_length))

    def forward(self, x, return_attention=False):
        """
        Args:
            x: Tensor of shape ``[batch_size, seq_length, embed_dim]``.
            return_attention: When true, returns ``(logits, attention_weights)``.
        """
        _, seq_length, _ = x.size()

        padding_mask = (x.abs().sum(dim=-1) == 0)

        mask = (~padding_mask).unsqueeze(-1).float()
        x = (x + self.pos_embedding[:, :seq_length, :]) * mask
        x = self.dropout(x)

        x = self.transformer_encoder(x, src_key_padding_mask=padding_mask)
        x = self.layer_norm(x)

        attn_logits = self.sequence_reduction(x).squeeze(-1)
        attn_logits = attn_logits + self.temporal_bias[:seq_length].unsqueeze(0)
        attn_logits = attn_logits.masked_fill(padding_mask, float("-inf"))

        attn_weights = torch.softmax(attn_logits, dim=1)
        attn_weights = torch.nan_to_num(attn_weights, nan=0.0)

        pooled = torch.sum(x * attn_weights.unsqueeze(-1), dim=1)
        out = self.classifier(pooled)

        if return_attention:
            return out, attn_weights
        return out


__all__ = ["NextHeadSingle"]
