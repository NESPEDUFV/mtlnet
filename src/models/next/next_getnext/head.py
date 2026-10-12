"""GETNext-inspired next-region head with trajectory-flow graph prior.

Reference:
    Yang, Liu, Zhao. "GETNext: Trajectory Flow Map Enhanced Transformer
    for Next POI Recommendation." SIGIR 2022.
    https://arxiv.org/abs/2303.04741

Architecture (adapted for our check2HGI + region-target setup):

    STAN bi-layer self-attention backbone over the 9-step trajectory
    (see ``next_stan``), plus a **trajectory-flow prior** added as a
    residual bias to the final region logits. The prior is derived from a
    pre-computed **region-transition log-probability matrix**
    ``log_T ∈ R^{|R| × |R|}`` (see ``scripts/compute_region_transition.py``):

        log_T[i, j] = log P(next_region = j | last_region = i)

    In the original GETNext paper the prior ``Φ[current_POI]`` is indexed
    by the last observed POI of the trajectory. Our ``next_region.parquet``
    carries only the check2HGI embedding sequence (no explicit per-step
    region index), so we use a **soft region-identity probe** on the
    last-step embedding:

        last_emb      = x[:, -1, :]                    # [B, D]
        region_logits = probe(last_emb)                # [B, |R|]
        region_probs  = softmax(region_logits)         # [B, |R|]
        trans_prior   = region_probs @ log_T           # [B, |R|]
        final_logits  = stan_logits + α * trans_prior  # [B, |R|]

    ``α`` is a learnable scalar (initialized small so the head starts
    close to pure STAN and gradually learns how much weight to give the
    graph prior). The probe is a single ``nn.Linear(D, |R|)`` trained
    jointly — its only signal is its contribution to the final loss.

Why this adaptation, not the exact GETNext formulation:

    - We have no schema field for "last region idx" in ``next_region.parquet``
      without a data-pipeline change. The soft probe gets us to the same
      place without modifying the input file.
    - check2HGI's check-in embeddings already internalize the POI's
      spatio-temporal context; the probe over the last-step embedding is
      a differentiable proxy for the hard "argmax region of poi_8".

Usage::

    # STL (single-task):
    python scripts/p1_region_head_ablation.py --state alabama \\
        --heads next_getnext --input-type region \\
        --folds 5 --epochs 50 \\
        --override-hparams 'transition_path="/tmp/check2hgi_data/check2hgi/alabama/region_transition_log.pt"'

    # MTL (cross-attn):
    python scripts/train.py --task mtl --task-set check2hgi_next_region \\
        --state alabama --engine check2hgi \\
        --model mtlnet_crossattn --mtl-loss pcgrad \\
        --reg-head next_getnext \\
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \\
        --reg-head-param 'transition_path="/tmp/.../region_transition_log.pt"'
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from models.next.next_stan.head import NextHeadSTAN
from models.registry import register_model


@register_model("next_getnext")
class NextHeadGETNext(nn.Module):
    """STAN backbone + GETNext-style trajectory-flow prior.

    Parameters
    ----------
    embed_dim:
        Per-step input feature dimension.
    num_classes:
        Number of regions — must match the rows/cols of the transition
        matrix saved by ``scripts/compute_region_transition.py``.
    seq_length, d_model, num_heads, dropout, bias_init:
        Forwarded to the underlying ``NextHeadSTAN`` encoder.
    transition_path:
        Path to a ``.pt`` file containing a dict with key ``log_transition``
        → ``Tensor[num_classes, num_classes]`` (log-probabilities). If
        ``None``, the transition prior is a zero tensor (head degenerates
        to pure STAN) — useful for ablation.
    alpha_init:
        Initial value of the learnable mixing scalar ``α``. Default 0.1
        starts the model close to pure STAN; the gradient adjusts ``α``
        as training proceeds.
    """

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

        if transition_path is not None:
            payload = torch.load(transition_path, map_location="cpu", weights_only=False)
            log_T = payload["log_transition"] if isinstance(payload, dict) else payload
            log_T = log_T.float()
            # Transition matrix is built from the check2HGI graph which may contain a
            # few more regions than appear as targets in next_region.parquet (graph
            # regions without a POI visit in the 9-window + target window). Slice to
            # the top-left submatrix matching num_classes.
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

        return stan_logits + self.alpha * transition_prior


__all__ = ["NextHeadGETNext"]
