"""Dual-tower cross-attention MTLnet with a pre-norm + SwiGLU shared backbone — T2.4 combo (F).

The "stack all winners" candidate: the reg-private dual-tower (the +1.51 reg mover)
on top of the pre-norm + SwiGLU shared backbone (the best-cat backbone). Designed to
be run with the prior OFF (``--reg-head-param freeze_alpha=True alpha_init=0.0``) so all
three levers compose: private reg pathway ⊕ SwiGLU shared backbone ⊕ prior-OFF.

Inheritance — diamond-avoiding (per the architecture advisor). We subclass
:class:`MTLnetCrossAttnDualTower` (NOT a multiple-inheritance diamond on
``MTLnetCrossAttn``) and override ONLY ``_build_shared_backbone`` to swap the
post-norm+GELU ``_CrossAttnBlock`` for the pre-norm+SwiGLU ``_CrossAttnBlockSwiGLU``.
The dual-tower's ``forward`` / ``next_forward`` (which feed the reg head the raw
``[B,9,64]`` region sequence) are inherited unchanged — the SwiGLU block keeps the
identical ``forward(a, b, a_pad_mask, b_pad_mask) -> (a, b)`` contract, so routing
is untouched.

Parameter partition stays bijective + exhaustive with zero accessor edits: the
SwiGLU FFN/attention params live inside ``self.crossattn_blocks`` →
``shared_parameters()``; the private STAN tower lives inside ``self.next_poi`` →
``reg_specific_parameters()`` (inherited from the dual-tower). The unit gate asserts
this.

Mechanistic expectation (advisor): SwiGLU is NULL on reg (gated out of the shared
pathway), so reg ≈ the flag-only dual-tower+prior-OFF; the value of THIS variant is
the chance of simultaneously best-cat (SwiGLU bump) AND best-reg (private tower +
prior-OFF) in a single deployable model. A cat-and-joint play, not a new reg lever.
"""

from __future__ import annotations

from torch import nn

from models.mtl.mtlnet_crossattn_dualtower.model import MTLnetCrossAttnDualTower
from models.mtl.mtlnet_crossattn_swiglu.model import _CrossAttnBlockSwiGLU
from models.registry import register_model


@register_model("mtlnet_crossattn_dualtower_swiglu")
class MTLnetCrossAttnDualTowerSwiGLU(MTLnetCrossAttnDualTower):
    """Dual-tower cross-attn with pre-norm + SwiGLU shared-backbone blocks."""

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


__all__ = ["MTLnetCrossAttnDualTowerSwiGLU"]
