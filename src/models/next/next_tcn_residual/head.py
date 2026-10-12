"""Canonical TCN with residual blocks and exponential dilation scheduling.

Reference:
    Bai et al., "An Empirical Evaluation of Generic Convolutional and
    Recurrent Networks for Sequence Modeling", 2018.
    https://arxiv.org/abs/1803.01271
"""

import torch
import torch.nn as nn

from models.registry import register_model


class _TCNResidualBlock(nn.Module):
    """Single TCN residual block: two dilated causal convolutions + skip."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        dilation: int,
        dropout: float,
    ):
        super().__init__()
        padding1 = (kernel_size - 1) * dilation
        self.conv1 = nn.Conv1d(
            in_channels, out_channels, kernel_size,
            padding=padding1, dilation=dilation,
        )
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(
            out_channels, out_channels, kernel_size,
            padding=padding1, dilation=dilation,
        )
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.act = nn.GELU()
        self.dropout = nn.Dropout(dropout)
        self.pad1 = padding1

        self.skip = (
            nn.Conv1d(in_channels, out_channels, 1)
            if in_channels != out_channels
            else nn.Identity()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.skip(x)

        out = self.conv1(x)
        out = out[:, :, :out.size(2) - self.pad1]  # causal trim
        out = self.act(self.bn1(out))
        out = self.dropout(out)

        out = self.conv2(out)
        out = out[:, :, :out.size(2) - self.pad1]  # causal trim
        out = self.act(self.bn2(out))
        out = self.dropout(out)

        return self.act(out + residual)


@register_model("next_tcn_residual")
class NextHeadTCNResidual(nn.Module):
    """TCN with residual blocks and exponential dilation for next-category prediction.

    Dilation schedule: [1, 2, 4, 8, ...] covering a receptive field much
    larger than the 9-step window. Each block contains two dilated causal
    convolutions with a skip connection.
    """

    def __init__(
        self,
        embed_dim: int,
        hidden_channels: int = 128,
        num_classes: int = 7,
        num_blocks: int = 4,
        kernel_size: int = 3,
        dropout: float = 0.2,
    ):
        super().__init__()
        blocks = []
        in_ch = embed_dim
        for i in range(num_blocks):
            dilation = 2 ** i
            blocks.append(
                _TCNResidualBlock(in_ch, hidden_channels, kernel_size, dilation, dropout)
            )
            in_ch = hidden_channels
        self.network = nn.Sequential(*blocks)

        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(hidden_channels, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, S, D] -> [B, D, S] for Conv1d
        x = x.transpose(1, 2)
        x = self.network(x)
        return self.classifier(x)


__all__ = ["NextHeadTCNResidual"]
