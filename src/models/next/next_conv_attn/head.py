"""Conv-Attention hybrid: TCN encoder + single cross-attention pooling.

Combines TCN's local feature extraction with attention's ability to learn
which timesteps matter for the final prediction. Avoids full self-attention
while keeping adaptive pooling.

Inspired by the Conformer pattern (Gulati et al., Interspeech 2020).
"""

import torch
import torch.nn as nn

from models.registry import register_model


@register_model("next_conv_attn")
class NextHeadConvAttn(nn.Module):
    """TCN encoder followed by single cross-attention pooling for classification."""

    def __init__(
        self,
        embed_dim: int,
        hidden_channels: int = 128,
        num_classes: int = 7,
        num_conv_layers: int = 3,
        kernel_size: int = 3,
        num_heads: int = 4,
        dropout: float = 0.2,
    ):
        super().__init__()
        # --- TCN encoder ---
        convs = []
        in_ch = embed_dim
        for _ in range(num_conv_layers):
            padding = kernel_size - 1  # causal
            convs.append(nn.Sequential(
                nn.Conv1d(in_ch, hidden_channels, kernel_size, padding=padding),
                nn.BatchNorm1d(hidden_channels),
                nn.GELU(),
                nn.Dropout(dropout),
            ))
            in_ch = hidden_channels
        self.convs = nn.ModuleList(convs)

        # --- Cross-attention pooling ---
        # Learned query token attends over TCN output (keys/values).
        self.query = nn.Parameter(torch.randn(1, 1, hidden_channels))
        self.attn = nn.MultiheadAttention(
            embed_dim=hidden_channels,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.norm = nn.LayerNorm(hidden_channels)
        self.classifier = nn.Linear(hidden_channels, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)

        # TCN: [B, S, D] -> [B, D, S]
        h = x.transpose(1, 2)
        for conv in self.convs:
            h = conv(h)
            h = h[:, :, :h.size(2) - (conv[0].padding[0])]  # causal trim

        # Back to [B, S', C] for attention
        h = h.transpose(1, 2)

        # Cross-attention: learned query attends over TCN features
        query = self.query.expand(batch_size, -1, -1)  # [B, 1, C]
        pooled, _ = self.attn(query, h, h)  # [B, 1, C]
        pooled = self.norm(pooled.squeeze(1))  # [B, C]

        return self.classifier(pooled)


__all__ = ["NextHeadConvAttn"]
