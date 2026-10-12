"""Mamba-lite (selective state-space) next-task head — Tier-S Prong-B new build.

A dependency-free, pure-PyTorch selective SSM in the spirit of Mamba (Gu & Dao 2023):
a diagonal state-space recurrence with **input-dependent** Δ, B, C (the "selective"
mechanism that lets the model gate what enters/persists in the hidden state), plus a
SiLU output gate and residual. The official mamba-ssm CUDA kernel is NOT installed and
its hardware-aware parallel scan is unnecessary here — the sequence length is 9, so a
plain sequential scan over time steps is cheap and exact (no approximation).

Shapes mirror the other coded heads: input [B, L, embed_dim] check-in/region sequence,
output [B, num_classes] from the last valid timestep. Registered as ``next_mamba``.

Faithfulness notes (vs the paper): diagonal real A (S4D-Real init), softplus Δ, the
B/C/Δ input projections, the gated SiLU branch, and per-channel D skip are all present;
omitted are the conv1d short-filter and the hardware parallel scan (both irrelevant at
L=9). This is a faithful *selective-SSM block*, not a drop-in for the full Mamba repo.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from models.registry import register_model


class _SelectiveSSM(nn.Module):
    """One diagonal selective state-space layer (Mamba-style), sequential scan."""

    def __init__(self, d_model: int, d_state: int = 16, dt_rank: int = 0):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.dt_rank = dt_rank or max(1, d_model // 16)
        # Input-dependent Δ (low-rank), B, C projections (the selectivity).
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * d_state, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, d_model, bias=True)
        # Diagonal state matrix A (negative, S4D-real init), per (channel, state).
        A = torch.arange(1, d_state + 1, dtype=torch.float32).repeat(d_model, 1)
        self.A_log = nn.Parameter(torch.log(A))           # learn log(-A) > 0
        self.D = nn.Parameter(torch.ones(d_model))         # skip connection

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # x: [B, L, d_model]
        B_, L, D_ = x.shape
        A = -torch.exp(self.A_log)                         # [D, N] negative
        proj = self.x_proj(x)                              # [B, L, dt_rank+2N]
        dt, Bm, Cm = torch.split(proj, [self.dt_rank, self.d_state, self.d_state], dim=-1)
        dt = F.softplus(self.dt_proj(dt))                  # [B, L, D] > 0
        h = x.new_zeros(B_, D_, self.d_state)              # hidden state
        ys = []
        for t in range(L):
            dt_t = dt[:, t]                                # [B, D]
            # discretise: Ā = exp(Δ A), B̄ = Δ B  (ZOH, diagonal)
            dA = torch.exp(dt_t.unsqueeze(-1) * A.unsqueeze(0))        # [B, D, N]
            dBx = (dt_t.unsqueeze(-1) * Bm[:, t].unsqueeze(1)) * x[:, t].unsqueeze(-1)  # [B,D,N]
            h = dA * h + dBx
            y = (h * Cm[:, t].unsqueeze(1)).sum(-1)        # [B, D]
            ys.append(y)
        y = torch.stack(ys, dim=1)                         # [B, L, D]
        return y + x * self.D


@register_model("next_mamba")
class NextHeadMamba(nn.Module):
    """Selective-SSM (Mamba-lite) next predictor: in-proj → N×(SSM block) → last-step → cls."""

    def __init__(
        self,
        embed_dim: int,
        num_classes: int = 7,
        hidden_dim: int = 256,
        num_layers: int = 2,
        d_state: int = 16,
        dropout: float = 0.3,
        **_ignore,
    ):
        super().__init__()
        self.in_proj = nn.Linear(embed_dim, hidden_dim)
        self.blocks = nn.ModuleList()
        for _ in range(num_layers):
            self.blocks.append(nn.ModuleDict({
                "norm": nn.LayerNorm(hidden_dim),
                "ssm": _SelectiveSSM(hidden_dim, d_state=d_state),
                "gate": nn.Linear(hidden_dim, hidden_dim),
                "out": nn.Linear(hidden_dim, hidden_dim),
                "drop": nn.Dropout(dropout),
            }))
        self.classifier = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # x: [B, L, embed_dim]
        padding_mask = (x.abs().sum(dim=-1) == 0)          # [B, L]
        seq_lengths = (~padding_mask).sum(dim=1).clamp(min=1)
        h = self.in_proj(x)
        for blk in self.blocks:
            res = h
            u = blk["norm"](h)
            y = blk["ssm"](u)
            y = y * F.silu(blk["gate"](u))                 # gated (Mamba SiLU branch)
            h = res + blk["drop"](blk["out"](y))           # residual
        # last valid timestep
        idx = (seq_lengths - 1)
        last = h[torch.arange(h.size(0), device=h.device), idx]
        return self.classifier(last)


__all__ = ["NextHeadMamba"]
