"""The region head: a STAN-style attention backbone over the nine historical visits.

Faithful to the reference `next_stan_flow` as v18 configures it. Module names are kept identical so
a reference checkpoint transplants directly — which is how this port is tested.

Shape of the thing: project to d_model=128, one pre-norm block (attention + FFN), then a second
attention pass read at the last valid step, then LayerNorm -> Dropout -> Linear.

**The trajectory-flow prior is absent, not disabled.** The reference head can add
`alpha * log_T[last_region_idx]` to its logits, and v18 runs it with `freeze_alpha=True,
alpha_init=0.0` — so the term is an exact zero at every batch. The reference still registers a
[C, C] buffer for it (289 MB at California) and, until a 2026 patch, still paid a [B, C] gather, a
masked_fill and a multiply per forward to add that zero. Here an inactive prior means no buffer and
no branch; an active one is a different object with its leak guards intact. Recorded as R6.

Two details that look incidental and are not:

* **The attention mask hides KEYS, not queries.** A padded step is unattendable, but every step
  still produces an output row.
* **An all-padding row would make the softmax see a row of -inf and emit NaN**, so the last step of
  such a row is force-unmasked. Unreachable at stride 1 (no padding exists), kept because it is a
  correctness guard rather than a tuning choice.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from .gru import last_valid_index


class _Attention(nn.Module):
    """Multi-head self-attention with a learned per-head pairwise position bias."""

    def __init__(self, d_model: int, num_heads: int, seq_length: int, dropout: float) -> None:
        super().__init__()
        if d_model % num_heads:
            raise ValueError(f"d_model={d_model} must be divisible by num_heads={num_heads}")
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads

        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.pair_bias = nn.Parameter(_alibi_bias(num_heads, seq_length))
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, padding_mask: torch.Tensor | None = None,
                last_query_only: bool = False) -> torch.Tensor:
        batch, steps, _ = x.shape
        qkv = self.qkv(x).reshape(batch, steps, 3, self.num_heads, self.head_dim)
        q, k, v = qkv.permute(2, 0, 3, 1, 4)

        attn = (q @ k.transpose(-2, -1)) * (self.head_dim ** -0.5)
        attn = attn + self.pair_bias[:, :steps, :steps].unsqueeze(0)
        if padding_mask is not None:
            # [B, S] over KEYS: broadcast across heads and query positions.
            attn = attn.masked_fill(padding_mask.unsqueeze(1).unsqueeze(1), float("-inf"))
        attn = self.attn_dropout(F.softmax(attn, dim=-1))

        out = (attn @ v).permute(0, 2, 1, 3).reshape(batch, steps, -1)
        out = self.resid_dropout(self.out_proj(out))

        if not last_query_only:
            return out
        if padding_mask is None:
            return out[:, -1]
        index = last_valid_index_from_mask(padding_mask)
        return out[torch.arange(batch, device=out.device), index]


def _alibi_bias(num_heads: int, seq_length: int) -> torch.Tensor:
    """ALiBi-style recency decay: head h gets slope 2^(-8(h+1)/H), bias -slope*|i-j|.

    A regularised prior rather than a free parameter table: the unconstrained Gaussian
    initialisation it replaced was overfit-prone at this sequence length. It stays learnable — the
    initialisation is the prior, not a constraint.
    """
    positions = torch.arange(seq_length, dtype=torch.float32)
    distance = (positions.unsqueeze(0) - positions.unsqueeze(1)).abs()
    slopes = torch.tensor([1.0 / (2.0 ** ((h + 1) * 8.0 / num_heads)) for h in range(num_heads)])
    return -slopes.view(-1, 1, 1) * distance.unsqueeze(0)


class _Block(nn.Module):
    """Pre-norm attention + feed-forward, both residual."""

    def __init__(self, d_model: int, num_heads: int, seq_length: int, dropout: float) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.attn = _Attention(d_model, num_heads, seq_length, dropout)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model * 4, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor, padding_mask: torch.Tensor | None = None) -> torch.Tensor:
        x = x + self.attn(self.norm1(x), padding_mask=padding_mask)
        return x + self.ffn(self.norm2(x))


class StanBackbone(nn.Module):
    """[B, S, embed_dim] -> [B, num_classes]."""

    def __init__(self, embed_dim: int, num_classes: int, *, seq_length: int = 9,
                 d_model: int = 128, num_heads: int = 4, dropout: float = 0.3) -> None:
        super().__init__()
        self.input_proj = nn.Linear(embed_dim, d_model)
        self.input_norm = nn.LayerNorm(d_model)
        self.input_dropout = nn.Dropout(dropout)
        self.trajectory_block = _Block(d_model, num_heads, seq_length, dropout)
        self.matching_norm = nn.LayerNorm(d_model)
        self.matching_attn = _Attention(d_model, num_heads, seq_length, dropout)
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Dropout(dropout),
            nn.Linear(d_model, num_classes),
        )

    def features(self, x: torch.Tensor) -> torch.Tensor:
        padding_mask = _padding_mask(x)
        h = self.input_dropout(self.input_norm(self.input_proj(x)))
        h = self.trajectory_block(h, padding_mask=padding_mask)
        return self.matching_attn(self.matching_norm(h), padding_mask=padding_mask,
                                  last_query_only=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


def _padding_mask(x: torch.Tensor) -> torch.Tensor:
    """True where a step is padding, with the all-padding row's last step force-unmasked.

    Without the exception, a fully padded row hands the softmax a row of -inf and the output is NaN,
    which then poisons the batch. Unreachable at stride 1; kept because it is a guard.
    """
    mask = x.abs().sum(dim=-1) == 0
    all_padded = mask.all(dim=1)
    mask = mask.clone()
    mask[:, -1] = mask[:, -1] & ~all_padded
    return mask


def last_valid_index_from_mask(padding_mask: torch.Tensor) -> torch.Tensor:
    """Position of the last valid step, given a padding mask.

    The reference counts valid steps and subtracts one, which is right only for strictly trailing
    padding. This takes the last valid POSITION, which agrees there and stays correct elsewhere
    (R11). Identical on v18 data, where no window contains padding at all.
    """
    valid = ~padding_mask
    steps = torch.arange(padding_mask.shape[1], device=padding_mask.device)
    return torch.where(valid, steps, torch.zeros_like(steps)).max(dim=1).values


class RegionHead(nn.Module):
    """The dedicated region head as v18 runs it: the STAN backbone, no prior.

    Wraps the backbone under the attribute name `stan` so a reference `next_stan_flow` checkpoint
    loads without a key map — the transplant test depends on that.
    """

    def __init__(self, embed_dim: int, num_classes: int, *, seq_length: int = 9,
                 d_model: int = 128, num_heads: int = 4, dropout: float = 0.3) -> None:
        super().__init__()
        self.stan = StanBackbone(embed_dim, num_classes, seq_length=seq_length,
                                 d_model=d_model, num_heads=num_heads, dropout=dropout)

    def forward(self, x: torch.Tensor, aux: torch.Tensor | None = None) -> torch.Tensor:
        """`aux` (last_region_idx) is accepted and unused: with the prior absent it cannot enter the
        computation. It stays in the signature so the runner's plumbing is uniform across heads and
        a head that DOES consume it is a drop-in, rather than something the loop has to special-case.
        """
        return self.stan(x)


__all__ = ["RegionHead", "StanBackbone", "last_valid_index_from_mask"]
