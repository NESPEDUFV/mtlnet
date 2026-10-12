"""Cross-stitch → cross-attention hybrid MTLnet — T2.4 speculative hybrid.

Composes the two sharing mechanisms in series WITHIN each block: a learned
cross-stitch linear mix of the two streams (per-task FFN + a 2×2 α matrix, à la
Misra et al. CVPR 2016) FEEDS the bidirectional cross-attention (content-based
mix). Per block::

    a ← LN( a + FFN_cs_a(a) ) ; b ← LN( b + FFN_cs_b(b) )      # per-task transform
    a', b' = α00·a + α01·b , α10·a + α11·b                      # cross-stitch mix
    a ← LN( a' + CrossAttn(Q=a', K=b', V=b') )                  # then cross-attention
    b ← LN( b' + CrossAttn(Q=b', K=a', V=a') )
    a ← LN( a + FFN_a(a) ) ; b ← LN( b + FFN_b(b) )

Unlike the standalone ``mtlnet_crossstitch`` (which puts the per-task FFNs/α in the
TASK-specific partition), here the ENTIRE hybrid block is part of the shared
backbone — α is initialised near identity (self 0.9 / cross 0.1) so it starts as a
mild pre-mix. Keeping the whole block shared avoids the two-partition-philosophy
clash the architecture advisor flagged (cross-stitch's task-specific FFNs vs
cross-attn's whole-block-shared), so this is a clean ``MTLnetCrossAttn`` subclass
overriding only ``_build_shared_backbone``; forward / partial-forwards / parameter
partition are inherited (all block params → ``shared_parameters()``).

Mechanistic expectation (advisor): NULL on reg — composing two shared-pathway
mixers is still the shared-capacity lever (twice falsified). Run for completeness.
"""

from __future__ import annotations

from typing import Optional, Tuple

import torch
from torch import nn

from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn
from models.registry import register_model


class _CrossAttnBlockXStitch(nn.Module):
    """Cross-stitch (FFN + α-mix) → bidirectional cross-attention → per-task FFN."""

    def __init__(
        self, dim: int, num_heads: int, ffn_dim: int, dropout: float,
        init_self: float = 0.9, init_cross: float = 0.1,
    ):
        super().__init__()
        # Cross-stitch stage: per-task transform + learned 2x2 mix.
        self.cs_ffn_a = nn.Sequential(
            nn.Linear(dim, ffn_dim), nn.GELU(), nn.Dropout(dropout), nn.Linear(ffn_dim, dim),
        )
        self.cs_ffn_b = nn.Sequential(
            nn.Linear(dim, ffn_dim), nn.GELU(), nn.Dropout(dropout), nn.Linear(ffn_dim, dim),
        )
        self.ln_csa = nn.LayerNorm(dim)
        self.ln_csb = nn.LayerNorm(dim)
        self.alpha = nn.Parameter(
            torch.tensor([[init_self, init_cross], [init_cross, init_self]], dtype=torch.float32)
        )
        # Cross-attention stage (matches the baseline block).
        self.cross_ab = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.cross_ba = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.ln_a1 = nn.LayerNorm(dim)
        self.ln_b1 = nn.LayerNorm(dim)
        self.ffn_a = nn.Sequential(
            nn.Linear(dim, ffn_dim), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(ffn_dim, dim), nn.Dropout(dropout),
        )
        self.ffn_b = nn.Sequential(
            nn.Linear(dim, ffn_dim), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(ffn_dim, dim), nn.Dropout(dropout),
        )
        self.ln_a2 = nn.LayerNorm(dim)
        self.ln_b2 = nn.LayerNorm(dim)

    def forward(
        self,
        a: torch.Tensor,
        b: torch.Tensor,
        a_pad_mask: Optional[torch.Tensor] = None,
        b_pad_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # Cross-stitch stage: per-task transform (residual+LN) then α-mix.
        a = self.ln_csa(a + self.cs_ffn_a(a))
        b = self.ln_csb(b + self.cs_ffn_b(b))
        a, b = (self.alpha[0, 0] * a + self.alpha[0, 1] * b,
                self.alpha[1, 0] * a + self.alpha[1, 1] * b)
        # Cross-attention stage (late bidirectional pattern).
        a_upd, _ = self.cross_ab(a, b, b, key_padding_mask=b_pad_mask)
        a = self.ln_a1(a + a_upd)
        b_upd, _ = self.cross_ba(b, a, a, key_padding_mask=a_pad_mask)
        b = self.ln_b1(b + b_upd)
        # Per-stream FFN.
        a = self.ln_a2(a + self.ffn_a(a))
        b = self.ln_b2(b + self.ffn_b(b))
        return a, b


@register_model("mtlnet_crossattn_xstitch")
class MTLnetCrossAttnXStitch(MTLnetCrossAttn):
    """``MTLnetCrossAttn`` with cross-stitch→cross-attention hybrid blocks."""

    def _build_shared_backbone(
        self, shared_layer_size: int, num_shared_layers: int, shared_dropout: float,
    ) -> None:
        self.crossattn_blocks = nn.ModuleList(
            [
                _CrossAttnBlockXStitch(
                    dim=shared_layer_size,
                    num_heads=self._num_crossattn_heads,
                    ffn_dim=self._crossattn_ffn_dim,
                    dropout=shared_dropout,
                )
                for _ in range(self._num_crossattn_blocks)
            ]
        )
        self.cat_final_ln = nn.LayerNorm(shared_layer_size)
        self.next_final_ln = nn.LayerNorm(shared_layer_size)


__all__ = ["MTLnetCrossAttnXStitch"]
