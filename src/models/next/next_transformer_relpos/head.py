"""Lightweight Transformer with relative position bias for next-category prediction.

Uses a learned relative position bias matrix (like ALiBi / T5) instead of
absolute positional encodings. For a fixed 9-step window, "how far apart
are two check-ins" is more informative than absolute position index.

References:
    Press et al., "Train Short, Test Long: Attention with Linear Biases
    Enables Input Length Extrapolation" (ALiBi), ICLR 2022.
    Shaw et al., "Self-Attention with Relative Position Representations",
    NAACL 2018.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from models.registry import register_model


class _RelPosTransformerLayer(nn.Module):
    """Single Transformer layer with additive relative position bias."""

    def __init__(self, d_model: int, num_heads: int, seq_length: int, dropout: float):
        super().__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        self.head_dim = d_model // num_heads

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)

        # Learned relative position bias: one scalar per (head, relative_distance).
        # Shape: [num_heads, seq_length, seq_length]
        self.rel_pos_bias = nn.Parameter(torch.zeros(num_heads, seq_length, seq_length))
        self._init_rel_pos_bias(seq_length)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 4, d_model),
            nn.Dropout(dropout),
        )
        self.attn_dropout = nn.Dropout(dropout)
        self.dropout = nn.Dropout(dropout)

    def _init_rel_pos_bias(self, seq_length: int) -> None:
        """Initialize bias from relative distance (ALiBi-inspired)."""
        with torch.no_grad():
            positions = torch.arange(seq_length).float()
            rel_dist = (positions.unsqueeze(0) - positions.unsqueeze(1)).abs()
            for h in range(self.num_heads):
                slope = 1.0 / (2 ** ((h + 1) * 8.0 / self.num_heads))
                self.rel_pos_bias.data[h] = -slope * rel_dist

    def forward(
        self, x: torch.Tensor, causal_mask: torch.Tensor, padding_mask: torch.Tensor | None,
    ) -> torch.Tensor:
        B, S, D = x.shape

        # Pre-norm
        normed = self.norm1(x)

        # QKV projection
        qkv = self.qkv(normed).reshape(B, S, 3, self.num_heads, self.head_dim)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # [3, B, H, S, head_dim]
        q, k, v = qkv[0], qkv[1], qkv[2]

        # Scaled dot-product attention + relative position bias
        scale = self.head_dim ** -0.5
        attn = (q @ k.transpose(-2, -1)) * scale  # [B, H, S, S]
        attn = attn + self.rel_pos_bias[:, :S, :S].unsqueeze(0)  # broadcast over batch

        # Causal mask
        attn = attn.masked_fill(causal_mask[:S, :S].unsqueeze(0).unsqueeze(0), float("-inf"))

        # Padding mask
        if padding_mask is not None:
            attn = attn.masked_fill(padding_mask.unsqueeze(1).unsqueeze(2), float("-inf"))

        attn = F.softmax(attn, dim=-1)
        attn = torch.nan_to_num(attn, nan=0.0)
        attn = self.attn_dropout(attn)

        out = (attn @ v).transpose(1, 2).reshape(B, S, D)
        out = self.out_proj(out)
        x = x + self.dropout(out)

        # FFN with pre-norm + residual
        x = x + self.ffn(self.norm2(x))
        return x


@register_model("next_transformer_relpos")
class NextHeadTransformerRelPos(nn.Module):
    """Lightweight Transformer with learned relative position bias."""

    def __init__(
        self,
        embed_dim: int,
        num_classes: int = 7,
        num_heads: int = 4,
        num_layers: int = 2,
        seq_length: int = 9,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        self.layers = nn.ModuleList([
            _RelPosTransformerLayer(embed_dim, num_heads, seq_length, dropout)
            for _ in range(num_layers)
        ])

        # Attention-weighted pooling
        self.sequence_reduction = nn.Linear(embed_dim, 1)
        self.norm = nn.LayerNorm(embed_dim)
        self.classifier = nn.Linear(embed_dim, num_classes)

        # Causal mask buffer
        causal = torch.triu(torch.ones(seq_length, seq_length, dtype=torch.bool), diagonal=1)
        self.register_buffer("causal_mask", causal)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        padding_mask = (x.abs().sum(dim=-1) == 0)

        x = self.dropout(x)

        for layer in self.layers:
            x = layer(x, self.causal_mask, padding_mask)

        x = self.norm(x)

        # Attention-weighted pooling
        attn_logits = self.sequence_reduction(x).squeeze(-1)  # [B, S]
        attn_logits = attn_logits.masked_fill(padding_mask, float("-inf"))
        attn_weights = torch.softmax(attn_logits, dim=1)
        attn_weights = torch.nan_to_num(attn_weights, nan=0.0).unsqueeze(-1)
        pooled = torch.sum(x * attn_weights, dim=1)  # [B, D]

        return self.classifier(pooled)


__all__ = ["NextHeadTransformerRelPos"]
