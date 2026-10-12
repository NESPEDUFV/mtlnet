"""Cross-Stitch MTLnet variant (Misra et al., CVPR 2016).

Reference:
    Misra et al., "Cross-Stitch Networks for Multi-Task Learning",
    CVPR 2016. https://arxiv.org/abs/1604.03539

Each task gets its own parallel backbone (per-task FFN + LayerNorm).
A learned 2x2 alpha matrix per cross-stitch unit mixes the two streams
between blocks:

    a' = alpha[0, 0] * a + alpha[0, 1] * b
    b' = alpha[1, 0] * a + alpha[1, 1] * b

alpha is initialised near identity (high self-weight ~0.9, low cross
~0.1) so the model starts near "two parallel STLs in a trenchcoat" and
learns how much to share at each depth.

**Important caveat (audit 2026-04-29):** unconstrained alpha[1, 0] couples
``a`` (cat stream) into ``b`` (reg stream), so under L_reg.backward
gradients still flow back to the cat encoder via the off-diagonal mix —
the same F49 Layer 2 leakage mechanism cross-attn has, in milder form.
For a CLEAN test of "does eliminating F49 leakage recover FL?" use
``detach_cross_stream=True`` which .detach()s the off-diagonal
contribution (analogous to mtlnet_crossattn's ``detach_crossattn_kv``).
The default (``detach_cross_stream=False``) tests "does *learned*
sharing recover FL when the *forced sharing* of cross-attn does not?".

Implementation choices vs the original Misra paper:
- Original uses one alpha PER channel (alpha is ``(C, 2, 2)`` for C
  channels). We use **one global alpha per block** (just ``(2, 2)``).
- Original places cross-stitch between *every* conv layer in two
  AlexNet-like backbones with no per-task transform inside the unit.
  We package a per-task FFN + LayerNorm INSIDE each block (so each
  block is "FFN-with-residual then cross-stitch mix"). This is a
  deliberate capacity choice to match cross-attn's parameter count —
  vanilla cross-stitch over raw embeddings would be too low-capacity
  to compete with H3-alt's 7.9M params at FL.
- We use ``num_crossstitch_blocks`` units (default 2, matching
  ``num_crossattn_blocks`` so model depth is comparable across F50
  variants).

**Constraint:** both task streams must have the same rank (both ``[B, T, D]``
or both ``[B, D]``). The alpha multiplication broadcasts and would silently
mis-shape if the streams differ in rank — guarded with an explicit check.
"""

from __future__ import annotations

from typing import Any, Iterator, Optional, Tuple

import torch
from torch import nn

from configs.model import InputsConfig
from models.mtl.mtlnet.model import MTLnet
from models.registry import register_model
from tasks import LEGACY_CATEGORY_NEXT, TaskSet


class _CrossStitchBlock(nn.Module):
    """One per-task FFN block + cross-stitch unit.

    Forward:
        a ← LN_a(a + FFN_a(a))   # per-task transform with residual
        b ← LN_b(b + FFN_b(b))
        a' = alpha[0, 0] * a + alpha[0, 1] * b
        b' = alpha[1, 0] * a + alpha[1, 1] * b
    """

    def __init__(
        self,
        dim: int,
        ffn_dim: int,
        dropout: float,
        init_self: float = 0.9,
        init_cross: float = 0.1,
        detach_cross_stream: bool = False,
    ):
        super().__init__()
        self.detach_cross_stream = bool(detach_cross_stream)
        self.ffn_a = nn.Sequential(
            nn.Linear(dim, ffn_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ffn_dim, dim),
            nn.Dropout(dropout),
        )
        self.ffn_b = nn.Sequential(
            nn.Linear(dim, ffn_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ffn_dim, dim),
            nn.Dropout(dropout),
        )
        self.ln_a = nn.LayerNorm(dim)
        self.ln_b = nn.LayerNorm(dim)
        # Cross-stitch matrix; init near identity. Learned during training.
        self.alpha = nn.Parameter(
            torch.tensor([
                [init_self, init_cross],
                [init_cross, init_self],
            ], dtype=torch.float32)
        )

    def forward(
        self,
        a: torch.Tensor,
        b: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # Both streams must have matching rank for alpha mix to broadcast
        # correctly. Catch heterogeneous ranks (e.g. legacy task_set with
        # flat task_a + sequential task_b) at the boundary, not as silent
        # mis-shape downstream.
        if a.dim() != b.dim() or a.shape != b.shape:
            raise RuntimeError(
                f"Cross-Stitch requires both streams to have matching shape "
                f"(both [B, T, D] or both [B, D]); got a.shape={tuple(a.shape)} "
                f"b.shape={tuple(b.shape)}."
            )
        # Per-task transforms with residual + LN
        a = self.ln_a(a + self.ffn_a(a))
        b = self.ln_b(b + self.ffn_b(b))
        # Cross-stitch mix. alpha is (2, 2); broadcasts over [B, T, D].
        # detach_cross_stream=True severs the F49 Layer 2 leakage path:
        # gradients from L_reg do NOT flow through the off-diagonal back
        # into the cat stream's encoder, and vice versa.
        if self.detach_cross_stream:
            kv_b = b.detach()
            kv_a = a.detach()
            a_new = self.alpha[0, 0] * a + self.alpha[0, 1] * kv_b
            b_new = self.alpha[1, 0] * kv_a + self.alpha[1, 1] * b
        else:
            a_new = self.alpha[0, 0] * a + self.alpha[0, 1] * b
            b_new = self.alpha[1, 0] * a + self.alpha[1, 1] * b
        return a_new, b_new


@register_model("mtlnet_crossstitch")
class MTLnetCrossStitch(MTLnet):
    """MTLnet variant with Cross-Stitch units between parallel task streams.

    Construction inherits encoder+head infrastructure from MTLnet.
    `_build_shared_backbone` is overridden to register cross-stitch
    blocks in place of FiLM + shared_layers.
    """

    def __init__(
        self,
        feature_size: int,
        shared_layer_size: int,
        num_classes: int,
        num_heads: int,
        num_layers: int,
        seq_length: int,
        num_shared_layers: int,
        encoder_layer_size: int = 256,
        num_encoder_layers: int = 2,
        encoder_dropout: float = 0.1,
        shared_dropout: float = 0.15,
        num_crossstitch_blocks: int = 2,
        crossstitch_ffn_dim: Optional[int] = None,
        crossstitch_init_self: float = 0.9,
        crossstitch_init_cross: float = 0.1,
        detach_cross_stream: bool = False,
        category_head: Optional[str] = None,
        next_head: Optional[str] = None,
        category_head_params: Optional[dict[str, Any]] = None,
        next_head_params: Optional[dict[str, Any]] = None,
        task_set: Optional[TaskSet] = None,
    ):
        self._num_crossstitch_blocks = int(num_crossstitch_blocks)
        self._crossstitch_ffn_dim = (
            int(crossstitch_ffn_dim) if crossstitch_ffn_dim is not None else int(shared_layer_size)
        )
        self._crossstitch_init_self = float(crossstitch_init_self)
        self._crossstitch_init_cross = float(crossstitch_init_cross)
        self._detach_cross_stream = bool(detach_cross_stream)
        super().__init__(
            feature_size=feature_size,
            shared_layer_size=shared_layer_size,
            num_classes=num_classes,
            num_heads=num_heads,
            num_layers=num_layers,
            seq_length=seq_length,
            num_shared_layers=num_shared_layers,
            encoder_layer_size=encoder_layer_size,
            num_encoder_layers=num_encoder_layers,
            encoder_dropout=encoder_dropout,
            shared_dropout=shared_dropout,
            category_head=category_head,
            next_head=next_head,
            category_head_params=category_head_params,
            next_head_params=next_head_params,
            task_set=task_set,
        )

    def _build_shared_backbone(
        self,
        shared_layer_size: int,
        num_shared_layers: int,
        shared_dropout: float,
    ) -> None:
        """Override MTLnet's FiLM + shared_layers with cross-stitch blocks."""
        self.crossstitch_blocks = nn.ModuleList(
            [
                _CrossStitchBlock(
                    dim=shared_layer_size,
                    ffn_dim=self._crossstitch_ffn_dim,
                    dropout=shared_dropout,
                    init_self=self._crossstitch_init_self,
                    init_cross=self._crossstitch_init_cross,
                    detach_cross_stream=self._detach_cross_stream,
                )
                for _ in range(self._num_crossstitch_blocks)
            ]
        )
        self.cat_final_ln = nn.LayerNorm(shared_layer_size)
        self.next_final_ln = nn.LayerNorm(shared_layer_size)

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

        # Cross-Stitch requires matching ranks (both [B, T, D] or both
        # [B, D]). The check2hgi task_set guarantees this; the legacy
        # task_set has a flat-A vs sequential-B mismatch that would silently
        # broadcast — _CrossStitchBlock raises if ranks differ.
        a, b = enc_cat, enc_next
        for block in self.crossstitch_blocks:
            a, b = block(a, b)

        shared_cat = self.cat_final_ln(a)
        shared_next = self.next_final_ln(b)

        # Re-zero at original pad positions (mirrors mtlnet_crossattn)
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
        out_next = self.next_poi(shared_next)
        return out_cat, out_next

    def cat_forward(self, category_input: torch.Tensor) -> torch.Tensor:
        """Eval-only partial forward; mirrors mtlnet_crossattn semantics.

        Cross-stitch with a zero B stream is exact for the diagonal alpha
        but not for off-diagonal: alpha[0, 1] * 0 = 0 contribution from B
        per definition, so a' = alpha[0, 0] * a is a SCALED version of A.
        With init_self ≈ 0.9 the scaling is close to (but not exactly)
        identity. This is **not** bit-exact with ``forward((cat, real_b))[0]``
        — it's a deterministic "cat-only" approximation. Callers needing
        the joint output must call ``forward((cat, next))[0]`` directly.
        """
        pad_value = InputsConfig.PAD_VALUE
        mask_a = None
        if self._task_a_is_sequential:
            mask_a = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask_a.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        enc_next_zero = torch.zeros_like(enc_cat)

        a, b = enc_cat, enc_next_zero
        for block in self.crossstitch_blocks:
            a, b = block(a, b)
        shared_cat = self.cat_final_ln(a)

        if self._task_set is not LEGACY_CATEGORY_NEXT and mask_a is not None:
            shared_cat = shared_cat.masked_fill(mask_a.unsqueeze(-1), 0)

        if self._task_a_is_sequential:
            return self.category_poi(shared_cat)
        return self.category_poi(shared_cat.squeeze(1)).view(
            -1, self.num_classes_task_a
        )

    def next_forward(self, next_input: torch.Tensor) -> torch.Tensor:
        """Eval-only partial forward — see ``cat_forward`` caveat."""
        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        enc_next = self.next_encoder(next_input)
        enc_cat_zero = torch.zeros_like(enc_next)

        a, b = enc_cat_zero, enc_next
        for block in self.crossstitch_blocks:
            a, b = block(a, b)
        shared_next = self.next_final_ln(b)

        if self._task_set is not LEGACY_CATEGORY_NEXT:
            shared_next = shared_next.masked_fill(mask.unsqueeze(-1), 0)

        return self.next_poi(shared_next)

    def shared_parameters(self) -> Iterator[nn.Parameter]:
        """Cross-stitch alpha matrices + final LNs.

        Per the Misra paper, alpha is the only shared parameter — it
        controls the cross-task information flow. Per-task FFNs and per-
        task LNs live in cat_specific_parameters / reg_specific_parameters.
        """
        for block in self.crossstitch_blocks:
            yield block.alpha
        yield from self.cat_final_ln.parameters()
        yield from self.next_final_ln.parameters()

    def task_specific_parameters(self) -> Iterator[nn.Parameter]:
        """All per-task params: encoders + heads + per-task FFNs/LNs."""
        yield from self.category_encoder.parameters()
        yield from self.next_encoder.parameters()
        yield from self.category_poi.parameters()
        yield from self.next_poi.parameters()
        for block in self.crossstitch_blocks:
            yield from block.ffn_a.parameters()
            yield from block.ln_a.parameters()
            yield from block.ffn_b.parameters()
            yield from block.ln_b.parameters()

    def cat_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Cat-only params: cat encoder + cat head + per-block ffn_a/ln_a."""
        yield from self.category_encoder.parameters()
        yield from self.category_poi.parameters()
        for block in self.crossstitch_blocks:
            yield from block.ffn_a.parameters()
            yield from block.ln_a.parameters()

    def reg_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Reg-only params: next encoder + next head + per-block ffn_b/ln_b."""
        yield from self.next_encoder.parameters()
        yield from self.next_poi.parameters()
        for block in self.crossstitch_blocks:
            yield from block.ffn_b.parameters()
            yield from block.ln_b.parameters()


__all__ = ["MTLnetCrossStitch"]
