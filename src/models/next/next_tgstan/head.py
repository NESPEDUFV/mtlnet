"""TGSTAN-inspired next-region head with per-sample dynamic gating.

Reference:
    Liu, Gao, Chen. "Improving the spatial-temporal aware attention network
    with dynamic trajectory graph learning for next Point-Of-Interest
    recommendation." Information Processing & Management, 2023.
    https://www.sciencedirect.com/science/article/pii/S0306457323000729

Architecture (adapted for our check2HGI + region-target setup):

    final_logits = STAN(x)
                 + α × gate(last_emb) ⊙ (softmax(probe(last_emb)) @ log_T)

where ``gate ∈ [0, 1]^|R|`` is a per-sample dynamic weighting over regions,
produced by a small MLP on the last-step embedding. The gate lets the model
*amplify or suppress* specific transitions per-sample based on context.

Differences from ``next_getnext``:

- Adds a **dynamic per-sample gate** applied element-wise to the transition
  prior. Captures TGSTAN's key contribution: the transition graph is not
  static but modulated by current trajectory context.
- Otherwise identical to GETNext (same STAN backbone, same log_T matrix,
  same soft region probe).

Adaptation note — TGSTAN's key original innovations:

1. TDGCN (Trajectory-aware Dynamic Graph Convolution Network) — a GCN
   whose normalized adjacency is element-wise multiplied with
   self-attentive POI representations per batch.
2. Bilinear-interpolated spatio-temporal interval embedding (2-D lookup
   over Δt × Δd bins).
3. Local batch-level trajectory graph respecting causality.

Our ``next_region.parquet`` lacks raw POI IDs per step and raw Δt/Δd, so
we cannot implement (1)/(2)/(3) faithfully. We preserve the *spirit* —
"the graph prior is dynamically reweighted per-sample" — via the MLP
gate. This is a pragmatic approximation, not a faithful reproduction.
"""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from models.next.next_stan.head import NextHeadSTAN
from models.registry import register_model


@register_model("next_tgstan")
class NextHeadTGSTAN(nn.Module):
    """STAN + GETNext graph prior + TGSTAN per-sample dynamic gate."""

    def __init__(
        self,
        embed_dim: int,
        num_classes: int,
        seq_length: int = 9,
        d_model: int = 128,
        num_heads: int = 4,
        dropout: float = 0.3,
        bias_init: str = "gaussian",
        transition_path: Optional[str] = None,
        alpha_init: float = 0.1,
        gate_hidden: int = 64,
    ):
        super().__init__()
        self.stan = NextHeadSTAN(
            embed_dim=embed_dim,
            num_classes=num_classes,
            seq_length=seq_length,
            d_model=d_model,
            num_heads=num_heads,
            dropout=dropout,
            bias_init=bias_init,
        )
        self.region_probe = nn.Linear(embed_dim, num_classes)
        self.alpha = nn.Parameter(torch.tensor(float(alpha_init)))

        # Per-sample dynamic gate over regions
        self.dynamic_gate = nn.Sequential(
            nn.Linear(embed_dim, gate_hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(gate_hidden, num_classes),
            nn.Sigmoid(),
        )

        if transition_path is not None:
            payload = torch.load(transition_path, map_location="cpu", weights_only=False)
            log_T = payload["log_transition"] if isinstance(payload, dict) else payload
            log_T = log_T.float()
            if log_T.shape[0] < num_classes or log_T.shape[1] < num_classes:
                raise ValueError(
                    f"Transition matrix shape {tuple(log_T.shape)} is smaller than "
                    f"num_classes={num_classes}. Rebuild the matrix for this state."
                )
            log_T = log_T[:num_classes, :num_classes].contiguous()
            self.register_buffer("log_T", log_T)
        else:
            self.register_buffer("log_T", torch.zeros(num_classes, num_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        stan_logits = self.stan(x)

        padding_mask = (x.abs().sum(dim=-1) == 0)
        seq_lengths = (~padding_mask).sum(dim=1).clamp(min=1)
        last_idx = (seq_lengths - 1)
        batch_idx = torch.arange(x.size(0), device=x.device)
        last_emb = x[batch_idx, last_idx]

        region_logits = self.region_probe(last_emb)
        region_probs = F.softmax(region_logits, dim=-1)
        transition_prior = region_probs @ self.log_T

        gate = self.dynamic_gate(last_emb)

        return stan_logits + self.alpha * gate * transition_prior


__all__ = ["NextHeadTGSTAN"]
