"""GRU + SimGCL auxiliary contrastive loss — Tier-S Prong-B orthogonal-mechanism bolt-on.

SimGCL (Yu et al., SIGIR'22) is an *auxiliary* regularizer, not an encoder swap: it
perturbs the representation with norm-bounded random noise to form two augmented views and
adds an InfoNCE (NT-Xent) consistency term to the task loss. Here it bolts onto the incumbent
GRU cat encoder (the frozen floor) — the encoder is unchanged; the only addition is the
contrastive aux. This isolates "does a contrastive regularizer help?" — orthogonal to the
encoder-architecture axis that Prong A/B already exhausted.

Integration contract: in training mode the head computes its own aux and exposes it via the
``self.aux_loss`` attribute; the trainer adds ``model.aux_loss`` to the task loss (a one-line,
attribute-guarded hook in next_cv.py / p1). In eval mode aux_loss is None and forward is a
plain GRU pass (identical to next_gru), so val metrics are uncontaminated.

SimGCL perturbation (Yu et al. eq. 4): e' = e + Δ, Δ = sign(e) ⊙ (ū · ε), ū ~ U(0,1)
L2-normalised — a norm-bounded, sign-preserving noise on the input embeddings.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from models.registry import register_model


@register_model("next_gru_simgcl")
class NextHeadGRUSimGCL(nn.Module):
    def __init__(
        self,
        embed_dim: int,
        hidden_dim: int = 256,
        num_classes: int = 7,
        num_layers: int = 2,
        dropout: float = 0.3,
        cl_weight: float = 0.1,
        cl_temp: float = 0.2,
        noise_eps: float = 0.1,
        proj_dim: int = 128,
        **_ignore,
    ):
        super().__init__()
        self.cl_weight = float(cl_weight)
        self.cl_temp = float(cl_temp)
        self.noise_eps = float(noise_eps)
        self.gru = nn.GRU(
            input_size=embed_dim, hidden_size=hidden_dim, num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0, batch_first=True,
        )
        self.proj = nn.Sequential(nn.Linear(hidden_dim, proj_dim), nn.ReLU(),
                                  nn.Linear(proj_dim, proj_dim))
        self.classifier = nn.Sequential(
            nn.LayerNorm(hidden_dim), nn.Dropout(dropout), nn.Linear(hidden_dim, num_classes),
        )
        self.aux_loss = None

    def _pool(self, x: torch.Tensor) -> torch.Tensor:
        padding_mask = (x.abs().sum(dim=-1) == 0)
        seq_lengths = (~padding_mask).sum(dim=1)
        out, _ = self.gru(x)
        last_idx = (seq_lengths - 1).clamp(min=0)
        return out[torch.arange(x.size(0), device=out.device), last_idx]

    def _augment(self, x: torch.Tensor) -> torch.Tensor:
        u = F.normalize(torch.rand_like(x), dim=-1)        # ū ~ U(0,1), L2-normalised
        return x + torch.sign(x) * u * self.noise_eps      # norm-bounded, sign-preserving

    def _infonce(self, z1: torch.Tensor, z2: torch.Tensor) -> torch.Tensor:
        z1 = F.normalize(z1, dim=-1); z2 = F.normalize(z2, dim=-1)
        n = z1.size(0)
        logits = (z1 @ z2.t()) / self.cl_temp              # [N, N]
        labels = torch.arange(n, device=z1.device)
        return 0.5 * (F.cross_entropy(logits, labels) + F.cross_entropy(logits.t(), labels))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.training and self.cl_weight > 0:
            f1 = self._pool(self._augment(x))
            f2 = self._pool(self._augment(x))
            self.aux_loss = self.cl_weight * self._infonce(self.proj(f1), self.proj(f2))
            return self.classifier(f1)
        self.aux_loss = None
        return self.classifier(self._pool(x))


__all__ = ["NextHeadGRUSimGCL"]
