"""Cross-attention MTLnet with pre-norm + SwiGLU FFN blocks — T2.4 hybrid.

Thin subclass of :class:`MTLnetCrossAttn`. The ONLY change is the shared
backbone block: the post-norm + GELU-FFN ``_CrossAttnBlock`` is swapped for
a **pre-norm + SwiGLU-FFN** ``_CrossAttnBlockSwiGLU``. The block keeps the
exact ``forward(a, b, a_pad_mask, b_pad_mask) -> (a, b)`` contract, so the
parent's ``forward`` / ``cat_forward`` / ``next_forward`` and all four
parameter-partition accessors are inherited verbatim (the FFN + attention
params live inside ``self.crossattn_blocks``, which ``shared_parameters()``
already walks).

Two modern-transformer ingredients, isolated as a hybrid against the
cross-attn baseline (T2.4):

1. **Pre-norm** — normalise the streams *before* attention / FFN and add the
   raw residual back. Pre-norm gives a clean identity gradient path through
   the residual (Xiong et al., "On Layer Normalization in the Transformer
   Architecture", ICML 2020, arXiv:2002.04745); the baseline block is
   post-norm. Bidirectional attention here uses the **parallel** pattern
   (both queries see the pre-update other stream) rather than the parent's
   "late" pattern (``b`` queries the *updated* ``a``) — pre-norm composes
   more naturally with the symmetric form and it removes the extra
   normalisation the late pattern would need on the updated-``a`` K/V.

2. **SwiGLU FFN** — ``W2( SiLU(W1 x) ⊙ (W3 x) )`` (Shazeer, "GLU Variants
   Improve Transformer", 2020, arXiv:2002.05202; the Llama/PaLM FFN). The
   gated form is the standard upgrade over the 2-matrix GELU FFN. Hidden
   width is set to ``h = round(2/3 · ffn_dim)`` so the 3-matrix SwiGLU has
   ~the same parameter count as the 2-matrix baseline FFN (``2·d·ffn_dim``
   vs ``3·d·h``), keeping the comparison capacity-matched.

LOW-risk hybrid: no change to the task encoders, heads, cross-attention
wiring, parameter partition, or the run recipe — only the residual-norm
placement and the FFN nonlinearity. See
``docs/studies/mtl_improvement/`` (T2.4 stretch).
"""

from __future__ import annotations

from typing import Optional, Tuple

import torch
from torch import nn
from torch.nn import functional as F

from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn
from models.registry import register_model


class _SwiGLU(nn.Module):
    """SwiGLU feed-forward: ``W2( SiLU(W1 x) ⊙ (W3 x) )``.

    ``hidden`` defaults to ``round(2/3 · ffn_dim)`` so the 3 projections
    (``W1, W3: dim→hidden``; ``W2: hidden→dim``) total ~``2·dim·ffn_dim``
    params — parity with the baseline 2-matrix GELU FFN of width
    ``ffn_dim``. Dropout is applied on the gated hidden activation and on
    the output, mirroring the baseline FFN's two dropout sites.
    """

    def __init__(self, dim: int, ffn_dim: int, dropout: float):
        super().__init__()
        hidden = max(1, round((2.0 / 3.0) * ffn_dim))
        self.w1 = nn.Linear(dim, hidden)  # gate pre-activation
        self.w3 = nn.Linear(dim, hidden)  # value
        self.w2 = nn.Linear(hidden, dim)  # projection back
        self.drop_h = nn.Dropout(dropout)
        self.drop_o = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.drop_h(F.silu(self.w1(x)) * self.w3(x))
        return self.drop_o(self.w2(h))


class _CrossAttnBlockSwiGLU(nn.Module):
    """Pre-norm bidirectional cross-attention + SwiGLU FFN block.

    Forward takes two streams ``a`` and ``b`` of shape ``[B, T, D]`` and
    keeps the SAME signature as the baseline ``_CrossAttnBlock`` so the
    parent model routes through it unchanged::

        na, nb = ln_a1(a), ln_b1(b)               # pre-norm
        a = a + CrossAttn(Q=na, K=nb, V=nb)       # parallel bidirectional
        b = b + CrossAttn(Q=nb, K=na, V=na)
        a = a + SwiGLU(ln_a2(a))                  # pre-norm FFN
        b = b + SwiGLU(ln_b2(b))

    ``detach_kv`` mirrors the baseline F50-P2 ablation (stop gradient on the
    cross-stream K/V). ``identity_attn`` (F52-P5) and ``zero_cat_kv``
    (substrate-cleanup C3) are accepted for constructor-signature parity
    with the baseline block and implemented identically, so the model
    composes with the same ablation flags; none are used by the T2.4 run.
    """

    def __init__(
        self,
        dim: int,
        num_heads: int,
        ffn_dim: int,
        dropout: float,
        detach_kv: bool = False,
        identity_attn: bool = False,
        zero_cat_kv: bool = False,
    ):
        super().__init__()
        self.detach_kv = bool(detach_kv)
        self.identity_attn = bool(identity_attn)
        self.zero_cat_kv = bool(zero_cat_kv)
        self.cross_ab = nn.MultiheadAttention(
            dim, num_heads, dropout=dropout, batch_first=True
        )
        self.cross_ba = nn.MultiheadAttention(
            dim, num_heads, dropout=dropout, batch_first=True
        )
        # Pre-norm: one LN before attention, one before the FFN, per stream.
        self.ln_a1 = nn.LayerNorm(dim)
        self.ln_b1 = nn.LayerNorm(dim)
        self.ln_a2 = nn.LayerNorm(dim)
        self.ln_b2 = nn.LayerNorm(dim)
        self.ffn_a = _SwiGLU(dim, ffn_dim, dropout)
        self.ffn_b = _SwiGLU(dim, ffn_dim, dropout)

    def forward(
        self,
        a: torch.Tensor,
        b: torch.Tensor,
        a_pad_mask: Optional[torch.Tensor] = None,
        b_pad_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        na = self.ln_a1(a)
        nb = self.ln_b1(b)
        if self.identity_attn:
            # F52-P5 parity: skip the cross-attention mixing entirely; the
            # streams pass through pre-norm + per-task SwiGLU FFN only.
            pass
        else:
            # Parallel bidirectional cross-attention on the pre-normed
            # streams (both queries see the pre-update other stream).
            kv_b = nb.detach() if self.detach_kv else nb
            a_upd, _ = self.cross_ab(
                query=na, key=kv_b, value=kv_b, key_padding_mask=b_pad_mask
            )
            kv_a = na.detach() if self.detach_kv else na
            if self.zero_cat_kv:
                kv_a = torch.zeros_like(kv_a)
            b_upd, _ = self.cross_ba(
                query=nb, key=kv_a, value=kv_a, key_padding_mask=a_pad_mask
            )
            a = a + a_upd
            b = b + b_upd
        # Pre-norm SwiGLU FFN with residual add.
        a = a + self.ffn_a(self.ln_a2(a))
        b = b + self.ffn_b(self.ln_b2(b))
        return a, b


@register_model("mtlnet_crossattn_swiglu")
class MTLnetCrossAttnSwiGLU(MTLnetCrossAttn):
    """``MTLnetCrossAttn`` with pre-norm + SwiGLU FFN shared-backbone blocks.

    Inherits the entire model unchanged except ``_build_shared_backbone``,
    which registers ``_CrossAttnBlockSwiGLU`` blocks in place of the
    post-norm + GELU baseline. The block keeps the baseline's forward
    contract, so ``forward`` / ``cat_forward`` / ``next_forward`` and the
    four parameter-partition accessors need no override.
    """

    def _build_shared_backbone(
        self,
        shared_layer_size: int,
        num_shared_layers: int,
        shared_dropout: float,
    ) -> None:
        self.crossattn_blocks = nn.ModuleList(
            [
                _CrossAttnBlockSwiGLU(
                    dim=shared_layer_size,
                    num_heads=self._num_crossattn_heads,
                    ffn_dim=self._crossattn_ffn_dim,
                    dropout=shared_dropout,
                    detach_kv=self._detach_crossattn_kv,
                    identity_attn=self._identity_cross_attn,
                    zero_cat_kv=self._zero_cat_kv,
                )
                for _ in range(self._num_crossattn_blocks)
            ]
        )
        self.cat_final_ln = nn.LayerNorm(shared_layer_size)
        self.next_final_ln = nn.LayerNorm(shared_layer_size)


__all__ = ["MTLnetCrossAttnSwiGLU"]
