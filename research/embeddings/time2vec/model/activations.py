import torch
import torch.nn as nn


def t2v(tau: torch.Tensor, f, out_features: int, w: torch.Tensor,
        b: torch.Tensor, w0: torch.Tensor, b0: torch.Tensor) -> torch.Tensor:
    """
    Time2Vec transformation function.

    Args:
        tau: Input tensor (batch, in_features)
        f: Periodic function (torch.sin or torch.cos)
        out_features: Output dimension (k)
        w: Periodic weights (in_features, k-1)
        b: Periodic bias (k-1,)
        w0: Linear weight (in_features, 1)
        b0: Linear bias (1,)

    Returns:
        Tensor of shape (batch, k) containing periodic and linear components
    """
    v1 = f(torch.matmul(tau, w) + b)
    v2 = torch.matmul(tau, w0) + b0
    return torch.cat([v1, v2], dim=-1)


class SineActivation(nn.Module):
    """Time2Vec with sine periodic activation."""

    def __init__(self, in_features: int, out_features: int):
        super(SineActivation, self).__init__()
        self.out_features = out_features
        self.w0 = nn.Parameter(torch.randn(in_features, 1))
        self.b0 = nn.Parameter(torch.randn(1))
        self.w = nn.Parameter(torch.randn(in_features, out_features - 1))
        self.b = nn.Parameter(torch.randn(out_features - 1))
        self.f = torch.sin

    def forward(self, tau: torch.Tensor) -> torch.Tensor:
        return t2v(tau, self.f, self.out_features, self.w, self.b, self.w0, self.b0)


class CosineActivation(nn.Module):
    """Time2Vec with cosine periodic activation."""

    def __init__(self, in_features: int, out_features: int):
        super(CosineActivation, self).__init__()
        self.out_features = out_features
        self.w0 = nn.Parameter(torch.randn(in_features, 1))
        self.b0 = nn.Parameter(torch.randn(1))
        self.w = nn.Parameter(torch.randn(in_features, out_features - 1))
        self.b = nn.Parameter(torch.randn(out_features - 1))
        self.f = torch.cos

    def forward(self, tau: torch.Tensor) -> torch.Tensor:
        return t2v(tau, self.f, self.out_features, self.w, self.b, self.w0, self.b0)