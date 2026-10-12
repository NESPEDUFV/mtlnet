"""PLE (Progressive Layered Extraction) MTLnet variant — *lite* adaptation.

Reference:
    Tang et al., "Progressive Layered Extraction (PLE): A Novel Multi-Task
    Learning Model for Personalized Recommendations", RecSys 2020.
    https://dl.acm.org/doi/10.1145/3383313.3412236

**Audit caveats (2026-04-29) — disclose in any paper using this:**

1. **Per-task-input adaptation, not single-shared-input.** Canonical PLE feeds
   ONE shared input ``x`` to every expert at level 1. This implementation
   evaluates each shared expert TWICE — once on ``category_x``, once on
   ``next_x`` — because in our heterogeneous-input MTL setting cat input
   is checkin embeddings (sequential, [B, T, D]) and reg input is region
   embeddings (sequential, [B, T, D]) — there is no obvious single shared
   input. **Side effect:** the F49 Layer 2 silent gradient flow that
   plagues ``mtlnet_crossattn`` is absent here — verified ``L_reg.backward()``
   produces ``||grad(category_encoder)|| = 0``. From the F50 hypothesis-test
   standpoint this is the *correct* semantics; from a faithfulness-to-Tang-2020
   standpoint, this is non-canonical PLE.

2. **NOT progressive between levels.** Canonical PLE has an explicit
   "shared gate" output that propagates between levels — ``shared_experts``
   at level L+1 receive the *previous level's shared-gate output*, not the
   task-specific gated outputs. ``PLELiteLayer`` here just stacks
   ``CGCLiteLayer`` blocks where each level's task outputs become next
   level's task inputs — there is NO inter-level shared-gate chain. The
   "Progressive" in the paper title refers exactly to that chain. This is
   essentially **stacked CGC**.

3. **Param count vs cross-attn baseline:** measured at ~8.25M for the
   default config (``num_levels=2, num_shared_experts=2, num_task_experts=2,
   num_shared_layers=4``) vs cross-attn 7.9M — within +4%, so capacity
   parity is OK for the F50 H3-alt comparison.

For the paper, rephrase any "PLE" claim as "PLE-lite (per-task-input
stacked-CGC adaptation)" or rename the registry key. The F50 hypothesis
this tests is "does explicit task-specific structure (with NO F49 leakage)
recover FL Δm?" — which it does test cleanly, modulo the non-canonical
naming.
"""

from __future__ import annotations

from typing import Any, Iterator, Optional, Tuple

import torch
from torch import nn

from configs.model import InputsConfig
from models.mtl._components import PLELiteLayer
from models.mtl.mtlnet.model import MTLnet
from models.registry import register_model
from tasks import LEGACY_CATEGORY_NEXT, TaskSet


@register_model("mtlnet_ple")
class MTLnetPLE(MTLnet):
    """MTLnet variant with stacked CGC layers (Progressive Layered Extraction).

    See :class:`MTLnet` for ``task_set`` semantics.
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
        num_levels: int = 2,
        num_shared_experts: int = 2,
        num_task_experts: int = 2,
        category_head: Optional[str] = None,
        next_head: Optional[str] = None,
        category_head_params: Optional[dict[str, Any]] = None,
        next_head_params: Optional[dict[str, Any]] = None,
        task_set: Optional[TaskSet] = None,
    ):
        self._num_levels = int(num_levels)
        self._num_shared_experts = int(num_shared_experts)
        self._num_task_experts = int(num_task_experts)
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
        self.ple = PLELiteLayer(
            layer_size=shared_layer_size,
            num_shared_layers=num_shared_layers,
            num_levels=self._num_levels,
            num_shared_experts=self._num_shared_experts,
            num_task_experts=self._num_task_experts,
            dropout=shared_dropout,
        )

    @property
    def last_gate_stats(self) -> dict[str, torch.Tensor]:
        return self.ple.last_gate_stats

    def forward(
        self,
        inputs: Tuple[torch.Tensor, torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        category_input, next_input = inputs

        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        if self._task_a_is_sequential:
            mask_a = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask_a.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        enc_next = self.next_encoder(next_input)

        shared_cat, shared_next = self.ple(enc_cat, enc_next)

        # Re-zero at original pad positions before the heads; see MTLnet
        # base class forward() docstring. Non-legacy path only.
        if self._task_set is not LEGACY_CATEGORY_NEXT:
            shared_next = shared_next.masked_fill(mask.unsqueeze(-1), 0)
            if self._task_a_is_sequential:
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
        if self._task_a_is_sequential:
            pad_value = InputsConfig.PAD_VALUE
            mask = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        dummy_next = torch.zeros_like(enc_cat)
        shared_cat, _ = self.ple(enc_cat, dummy_next)
        if self._task_a_is_sequential:
            return self.category_poi(shared_cat)
        return self.category_poi(shared_cat.squeeze(1)).view(-1, self.num_classes_task_a)

    def next_forward(self, next_input: torch.Tensor) -> torch.Tensor:
        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)
        enc_next = self.next_encoder(next_input)
        dummy_cat = torch.zeros(enc_next.size(0), enc_next.size(-1), device=enc_next.device)
        _, shared_next = self.ple(dummy_cat, enc_next)
        return self.next_poi(shared_next)

    def shared_parameters(self) -> Iterator[nn.Parameter]:
        return (
            p
            for name, p in self.named_parameters()
            if "ple.levels" in name and "shared_experts" in name
        )

    def task_specific_parameters(self) -> Iterator[nn.Parameter]:
        return (
            p
            for name, p in self.named_parameters()
            if any(
                key in name
                for key in (
                    "category_encoder",
                    "next_encoder",
                    "category_poi",
                    "next_poi",
                    "category_experts",
                    "next_experts",
                    "category_gate",
                    "next_gate",
                )
            )
        )

    def cat_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Cat-only parameters: cat encoder + cat head + per-level cat-specific
        experts + cat gate. Used by the per-head-LR optimizer (F48-H3) so PLE
        can be benchmarked under the same H3-alt champion config that's the
        reference baseline. Excludes ``shared_experts`` which stay in
        ``shared_parameters``."""
        return (
            p
            for name, p in self.named_parameters()
            if any(
                key in name
                for key in (
                    "category_encoder",
                    "category_poi",
                    "category_experts",
                    "category_gate",
                )
            )
        )

    def reg_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Reg/next-only parameters: next encoder + next head + per-level
        next-specific experts + next gate. Symmetric to ``cat_specific_parameters``."""
        return (
            p
            for name, p in self.named_parameters()
            if any(
                key in name
                for key in (
                    "next_encoder",
                    "next_poi",
                    "next_experts",
                    "next_gate",
                )
            )
        )


__all__ = ["MTLnetPLE"]
