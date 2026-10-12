"""Dual-tower for BOTH tasks — the B-A3 cat-private-tower ablation (CRITIQUE §6.3).

Subclass of :class:`MTLnetCrossAttnDualTower` that ADDITIONALLY hands the CAT head its
raw `[B,9,64]` check-in sequence (alongside the shared cross-attn output), so the cat
head can run its own private tower — symmetric to what the champion G does for reg.

Purpose: a NARRATIVE confirm-ablation (predicted NULL). Cat is positive-transfer — MTL
cat EXCEEDS its STL ceiling *because* it shares the rising tide; isolating it with a
private tower is predicted to help nothing (and cost params). A cat ≤ G result confirms
the cleanest mechanistic story in the paper: **reg needs a private pathway, cat wants
the shared one.** Run with the cat head = `next_stan_flow_dualtower` (7-class), aux fusion.

Only ``forward`` is overridden (pass ``raw_region_seq=category_input`` to ``category_poi``
when the cat head accepts it). The reg dual-tower path is inherited unchanged; the
parameter partition stays bijective (the cat private tower lives inside ``category_poi``
→ ``cat_specific_parameters`` via the parent's ``yield from self.category_poi.parameters()``).
"""

from __future__ import annotations

from typing import Tuple

import torch

from configs.model import InputsConfig
from models.mtl.mtlnet_crossattn_dualtower.model import MTLnetCrossAttnDualTower
from models.registry import register_model
from tasks import LEGACY_CATEGORY_NEXT


@register_model("mtlnet_crossattn_dualtower_catpriv")
class MTLnetCrossAttnDualTowerCatPriv(MTLnetCrossAttnDualTower):
    """Dual-tower for reg AND cat (cat-private-tower ablation)."""

    def forward(
        self,
        inputs: Tuple[torch.Tensor, torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        category_input, next_input = inputs

        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        mask_a = None
        if self._task_a_is_sequential:
            mask_a = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask_a.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        enc_next = self.next_encoder(next_input)

        a, b = enc_cat, enc_next
        if not self._disable_cross_attn:
            for block in self.crossattn_blocks:
                a, b = block(
                    a, b,
                    a_pad_mask=mask_a if self._task_a_is_sequential else None,
                    b_pad_mask=mask,
                )

        shared_cat = self.cat_final_ln(a)
        shared_next = self.next_final_ln(b)

        if self._task_set is not LEGACY_CATEGORY_NEXT:
            shared_next = shared_next.masked_fill(mask.unsqueeze(-1), 0)
            if self._task_a_is_sequential and mask_a is not None:
                shared_cat = shared_cat.masked_fill(mask_a.unsqueeze(-1), 0)

        # Cat-private tower: hand the cat head its raw [B,9,64] check-in sequence
        # (same role next_input plays for the reg head). The cat head must be a
        # dual-tower head (next_stan_flow_dualtower); a plain head ignores the kwarg.
        if self._task_a_is_sequential:
            if getattr(self.category_poi, "fusion_mode", None) is not None:
                out_cat = self.category_poi(shared_cat, raw_region_seq=category_input)
            else:
                out_cat = self.category_poi(shared_cat)
        else:
            out_cat = self.category_poi(shared_cat.squeeze(1)).view(
                -1, self.num_classes_task_a
            )

        # Reg dual-tower path — unchanged from the parent.
        out_next = self.next_poi(shared_next, raw_region_seq=next_input)
        return out_cat, out_next


__all__ = ["MTLnetCrossAttnDualTowerCatPriv"]
