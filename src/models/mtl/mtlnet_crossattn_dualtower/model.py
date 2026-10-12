"""Cross-attention MTLnet with a reg-private dual-tower head — T2.1.

Thin subclass of :class:`MTLnetCrossAttn`. The ONLY behavioral change is that
the reg head (``next_poi``, a :class:`NextHeadStanFlowDualTower`) is handed the
**raw post-pad-mask region sequence** ``next_input`` (``[B, 9, 64]``) alongside
the shared cross-attn output, so its private STAN backbone can process the
un-mixed region pathway exactly as the STL reg head does. Everything else — task
encoders, the bidirectional cross-attention stack, the cat path, the four
parameter-partition accessors — is inherited unchanged.

Why a subclass rather than reusing the ``_uses_residual`` / ``residual_input``
hook: that hook is the *thin residual-skip* contract (falsified, −0.59pp AZ); a
distinct ``raw_region_seq`` kwarg keeps the dual-tower cleanly separate and
auditable. ``next_forward`` is overridden too, because the disjoint
diagnostic-best reg metric (the T2.1 headline) is evaluated through it — without
the override it would silently run the head's shared-only fallback and
under-report the private tower.

Param partition: the private tower lives inside ``self.next_poi`` →
``reg_specific_parameters()`` and ``task_specific_parameters()`` (both
``yield from self.next_poi.parameters()`` in the parent) cover it automatically;
``shared_parameters()`` (cross-attn blocks + final LNs) excludes it. The
partition stays bijective + exhaustive with zero edits to the accessors — the
unit-test gate asserts this.

See ``docs/studies/mtl_improvement/T2.1_DUALTOWER_DESIGN.md``.
"""

from __future__ import annotations

from typing import Tuple

import torch

from configs.model import InputsConfig
from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn
from models.registry import register_model
from tasks import LEGACY_CATEGORY_NEXT


@register_model("mtlnet_crossattn_dualtower")
class MTLnetCrossAttnDualTower(MTLnetCrossAttn):
    """``MTLnetCrossAttn`` that feeds the reg head the raw region sequence."""

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

        if self._task_a_is_sequential:
            out_cat = self.category_poi(shared_cat)
        else:
            out_cat = self.category_poi(shared_cat.squeeze(1)).view(
                -1, self.num_classes_task_a
            )

        # Dual-tower: hand the reg head the raw region sequence so its private
        # STAN backbone runs on the un-mixed [B,9,64] pathway. ``next_input`` is
        # the post-pad-mask raw region-embedding sequence (same tensor STL feeds
        # its STAN). NOT the falsified thin residual-skip — a full private tower.
        #
        # Conditional coupling (mtl_frontier): when the reg head opts in
        # (cond_coupling != none), pass the cat head's posterior as an input
        # feature so the region prediction is conditioned on the predicted
        # category (iMTL/GETNext). Champion G (cond_coupling="none") is
        # bit-identical — the softmax + kwarg are skipped entirely.
        _cc = getattr(self.next_poi, "cond_coupling", "none")
        if _cc != "none":
            if _cc == "features" and hasattr(self.category_poi, "forward_features"):
                # richer cat-condition: the cat head's penultimate [B, hidden]
                cat_cond = self.category_poi.forward_features(shared_cat)
            else:
                # R-CC+ signal transform (the head declares which; defaults to the
                # original posterior so champion-cc is bit-identical).
                _sig = getattr(self.next_poi, "cond_signal", "softmax")
                if _sig == "argmax":
                    # discrete one-hot of the predicted category (GETNext form);
                    # the selection is non-differentiable but the cat→reg gradient
                    # still flows through the learned embedding (cond_proj weight).
                    cat_cond = torch.zeros_like(out_cat).scatter_(
                        -1, out_cat.argmax(dim=-1, keepdim=True), 1.0
                    )
                else:
                    _temp = float(getattr(self.next_poi, "cond_temp", 1.0))
                    cat_cond = torch.softmax(out_cat / _temp, dim=-1)
                    if _sig == "topk":
                        _k = int(getattr(self.next_poi, "cond_topk", 0))
                        if 0 < _k < cat_cond.size(-1):
                            _, idx = cat_cond.topk(_k, dim=-1)
                            keep = torch.zeros_like(cat_cond).scatter_(-1, idx, 1.0)
                            cat_cond = cat_cond * keep
                            cat_cond = cat_cond / cat_cond.sum(
                                dim=-1, keepdim=True
                            ).clamp_min(1e-9)
            out_next = self.next_poi(
                shared_next, raw_region_seq=next_input, cat_cond=cat_cond
            )
        else:
            out_next = self.next_poi(shared_next, raw_region_seq=next_input)
        return out_cat, out_next

    def next_forward(self, next_input: torch.Tensor) -> torch.Tensor:
        """Isolated reg subgraph (zero-A cross-attn stream) — passes the raw
        region sequence to the dual-tower head. Mirrors the parent's zero-A
        approximation; see ``MTLnetCrossAttn.next_forward`` for the partial-
        forward caveat. Used by the disjoint diagnostic-best reg evaluation."""
        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        enc_next = self.next_encoder(next_input)
        t_a = enc_next.size(1) if self._task_a_is_sequential else 1
        enc_cat = torch.zeros(
            enc_next.size(0), t_a, enc_next.size(-1),
            device=enc_next.device, dtype=enc_next.dtype,
        )

        a, b = enc_cat, enc_next
        if not self._disable_cross_attn:
            for block in self.crossattn_blocks:
                a, b = block(a, b, a_pad_mask=None, b_pad_mask=mask)
        shared_next = self.next_final_ln(b)

        if self._task_set is not LEGACY_CATEGORY_NEXT:
            shared_next = shared_next.masked_fill(mask.unsqueeze(-1), 0)

        return self.next_poi(shared_next, raw_region_seq=next_input)


__all__ = ["MTLnetCrossAttnDualTower"]
