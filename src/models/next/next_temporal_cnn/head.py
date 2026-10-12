"""Temporal CNN next-task head."""

import torch
import torch.nn as nn

from models.registry import register_model


@register_model("next_temporal_cnn")
class NextHeadTemporalCNN(nn.Module):
    """Temporal CNN for next-category prediction using causal convolutions."""

    def __init__(
        self,
        embed_dim: int,
        hidden_channels: int = 128,
        num_classes: int = 7,
        num_layers: int = 4,
        kernel_size: int = 3,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.convs = nn.ModuleList()
        in_channels = embed_dim

        for _ in range(num_layers):
            out_channels = hidden_channels
            padding = kernel_size - 1
            self.convs.append(
                nn.Sequential(
                    nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding),
                    nn.BatchNorm1d(out_channels),
                    nn.GELU(),
                    nn.Dropout(dropout),
                )
            )
            in_channels = out_channels

        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(hidden_channels, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.transpose(1, 2)
        for conv in self.convs:
            x = conv(x)
            x = x[:, :, :x.size(2) - (conv[0].padding[0])]
        return self.classifier(x)


__all__ = ["NextHeadTemporalCNN"]
