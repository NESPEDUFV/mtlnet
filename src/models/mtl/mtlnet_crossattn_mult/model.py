"""MulT-faithful cross-attention MTLnet — T2.4 speculative hybrid.

Canonical MulT (Tsai et al., ACL 2019, arXiv:1906.00295) interleaves a
per-stream **self-attention** sublayer BEFORE the bidirectional cross-attention
in every block. Our baseline ``mtlnet_crossattn`` block has cross-attention +
per-task FFN but NO intra-stream self-attention; this variant adds it, making the
shared backbone a faithful MulT block:

    a ← LN( a + SelfAttn_a(a) )            # NEW: intra-stream self-attention
    b ← LN( b + SelfAttn_b(b) )
    a ← LN( a + CrossAttn(Q=a, K=b, V=b) ) # bidirectional cross (late pattern)
    b ← LN( b + CrossAttn(Q=b, K=a, V=a) )
    a ← LN( a + FFN_a(a) ) ; b ← LN( b + FFN_b(b) )

Post-norm + GELU FFN, matching the baseline block's conventions so the only
change is the added self-attention. The block keeps the baseline's
``forward(a, b, a_pad_mask, b_pad_mask) -> (a, b)`` contract, so only
``_build_shared_backbone`` is overridden; the parent's forward / partial-forwards
/ parameter-partition accessors are inherited (the self-attn params live inside
``self.crossattn_blocks`` → ``shared_parameters()``).

Mechanistic expectation (advisor): NULL on reg. This is a shared-pathway
capacity/quality upgrade — the same lever class (MoE, SwiGLU) twice confirmed null
on reg under the cross-attn MTL regime. Run for completeness; expected cat-only.
"""

from __future__ import annotations

from typing import Optional, Tuple

import torch
from torch import nn

from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn
from models.registry import register_model


class _CrossAttnBlockMulT(nn.Module):
    """Self-attention → bidirectional cross-attention → per-task FFN (post-norm)."""

    def __init__(self, dim: int, num_heads: int, ffn_dim: int, dropout: float):
        super().__init__()
        self.self_a = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.self_b = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.ln_sa = nn.LayerNorm(dim)
        self.ln_sb = nn.LayerNorm(dim)
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
        # Intra-stream self-attention (the MulT addition). key_padding_mask skips
        # padded steps; sequences always have ≥1 real step (no all-masked row).
        sa, _ = self.self_a(a, a, a, key_padding_mask=a_pad_mask)
        a = self.ln_sa(a + sa)
        sb, _ = self.self_b(b, b, b, key_padding_mask=b_pad_mask)
        b = self.ln_sb(b + sb)
        # Bidirectional cross-attention (late pattern: b queries the updated a).
        a_upd, _ = self.cross_ab(a, b, b, key_padding_mask=b_pad_mask)
        a = self.ln_a1(a + a_upd)
        b_upd, _ = self.cross_ba(b, a, a, key_padding_mask=a_pad_mask)
        b = self.ln_b1(b + b_upd)
        # Per-stream FFN.
        a = self.ln_a2(a + self.ffn_a(a))
        b = self.ln_b2(b + self.ffn_b(b))
        return a, b


@register_model("mtlnet_crossattn_mult")
class MTLnetCrossAttnMulT(MTLnetCrossAttn):
    """``MTLnetCrossAttn`` with MulT-faithful self+cross-attention blocks."""

    def _build_shared_backbone(
        self, shared_layer_size: int, num_shared_layers: int, shared_dropout: float,
    ) -> None:
        self.crossattn_blocks = nn.ModuleList(
            [
                _CrossAttnBlockMulT(
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


__all__ = ["MTLnetCrossAttnMulT"]
