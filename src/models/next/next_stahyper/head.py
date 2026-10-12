"""STA-Hyper-inspired next-region head with learned cluster priors.

Reference:
    *STA-Hyper: Hypergraph-Based Spatio-Temporal Attention Network for Next
    Point-of-Interest Recommendation.* KSEM 2025.
    https://link.springer.com/chapter/10.1007/978-981-96-8725-1_19

Architecture (adapted for our check2HGI + region-target setup):

    final_logits = STAN(x)
                 + α_trans × (softmax(probe(last_emb)) @ log_T)      # GETNext prior
                 + α_cluster × (softmax(cluster_probe(last_emb)) @ C) # hypergraph prior

where ``C ∈ R^{K × |R|}`` is a learned matrix of **cluster-specific region
preferences**: row ``C[k]`` represents the "typical next-region distribution"
(as log-space bias) for cluster/hyperedge ``k``. The cluster assignment is
soft, predicted per-sample from the last-step embedding.

Interpretation: we approximate STA-Hyper's hypergraph structure by
treating "users that cluster together in embedding space" as implicit
hyperedges. Each cluster owns a region-preference bias that rides on top
of the global transition prior.

Adaptation note — STA-Hyper's key original innovations:

1. True hypergraph construction (each user-trajectory = hyperedge).
2. Hypergraph convolution layers that propagate info across hyperedges.
3. Higher-order collaborative signal beyond pairwise edges.

Our adapted version uses K learnable cluster priors as a proxy — a very
light-weight hypergraph approximation that doesn't require constructing
or storing the full hypergraph. We keep the *role* of hyperedges (giving
each cluster its own region prior) without paying for full hypergraph
convolution.
"""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from models.next.next_stan.head import NextHeadSTAN
from models.registry import register_model


@register_model("next_stahyper")
class NextHeadSTAHyper(nn.Module):
    """STAN + GETNext graph prior + STA-Hyper-inspired learned cluster prior."""

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
        n_clusters: int = 8,
        cluster_hidden: int = 64,
        alpha_cluster_init: float = 0.1,
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
        self.alpha_cluster = nn.Parameter(torch.tensor(float(alpha_cluster_init)))

        # Cluster assignment probe
        self.cluster_probe = nn.Sequential(
            nn.Linear(embed_dim, cluster_hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(cluster_hidden, n_clusters),
        )
        # Learned cluster region priors
        self.cluster_priors = nn.Parameter(torch.zeros(n_clusters, num_classes))
        nn.init.normal_(self.cluster_priors, std=0.01)

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

        # GETNext transition prior
        region_logits = self.region_probe(last_emb)
        region_probs = F.softmax(region_logits, dim=-1)
        transition_prior = region_probs @ self.log_T

        # STA-Hyper cluster prior
        cluster_logits = self.cluster_probe(last_emb)
        cluster_probs = F.softmax(cluster_logits, dim=-1)
        cluster_prior = cluster_probs @ self.cluster_priors

        return stan_logits + self.alpha * transition_prior + self.alpha_cluster * cluster_prior


__all__ = ["NextHeadSTAHyper"]
