"""Category residual head variant."""

import torch
from torch import nn

from models.registry import register_model


class _CategoryResidualBlock(nn.Module):
    """Single residual block with expansion."""

    def __init__(self, dim: int, hidden_dim: int, output_dim: int, dropout: float):
        super().__init__()
        self.needs_projection = dim != output_dim

        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, output_dim),
            nn.Dropout(dropout),
        )

        if self.needs_projection:
            self.shortcut = nn.Linear(dim, output_dim)
        else:
            self.shortcut = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x) + self.shortcut(x)


@register_model("category_residual")
class CategoryHeadResidual(nn.Module):
    """MLP with residual connections for deeper, more stable training."""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: tuple[int, ...],
        num_classes: int,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, hidden_dims[0])

        self.blocks = nn.ModuleList()
        for i in range(len(hidden_dims)):
            current_dim = hidden_dims[i]
            next_dim = hidden_dims[i + 1] if i + 1 < len(hidden_dims) else current_dim
            self.blocks.append(
                _CategoryResidualBlock(
                    dim=current_dim,
                    hidden_dim=current_dim * 2,
                    output_dim=next_dim,
                    dropout=dropout,
                )
            )

        final_dim = hidden_dims[-1]
        self.classifier = nn.Sequential(
            nn.LayerNorm(final_dim),
            nn.Linear(final_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.input_proj(x)
        for block in self.blocks:
            x = block(x)
        return self.classifier(x)


__all__ = ["CategoryHeadResidual"]
