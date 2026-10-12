"""DSelect-k-lite MTLnet variant."""

from __future__ import annotations

from typing import Any, Iterator, Optional, Tuple

import torch
from torch import nn

from configs.model import InputsConfig
from models.mtl._components import DSelectKLiteLayer
from models.mtl.mtlnet.model import MTLnet
from models.registry import register_model
from tasks import LEGACY_CATEGORY_NEXT, TaskSet


@register_model("mtlnet_dselectk")
class MTLnetDSelectK(MTLnet):
    """MTLnet variant with DSelect-k style sparse expert selection.

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
        num_experts: int = 4,
        num_selectors: int = 2,
        temperature: float = 0.5,
        lora_rank: int = 8,
        category_head: Optional[str] = None,
        next_head: Optional[str] = None,
        category_head_params: Optional[dict[str, Any]] = None,
        next_head_params: Optional[dict[str, Any]] = None,
        task_set: Optional[TaskSet] = None,
    ):
        self._num_experts = int(num_experts)
        self._num_selectors = int(num_selectors)
        self._temperature = float(temperature)
        self._lora_rank = int(lora_rank)
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
        self.dselect = DSelectKLiteLayer(
            layer_size=shared_layer_size,
            num_shared_layers=num_shared_layers,
            num_experts=self._num_experts,
            num_selectors=self._num_selectors,
            dropout=shared_dropout,
            temperature=self._temperature,
        )
        # Learnable skip-α (per-task; kept for reference / comparison).
        self.skip_alpha_cat = nn.Parameter(torch.zeros(1))
        self.skip_alpha_next = nn.Parameter(torch.zeros(1))

        # Per-task LoRA adapters (MTLoRA, CVPR 2024). Each task gets a
        # rank-r additive adapter on top of the shared DSelect-K output,
        # giving the task-specific path dedicated low-rank capacity
        # without modifying the shared backbone. B is initialised to
        # zero so step-0 contribution is identical to baseline (bit-
        # exact), but gradients flow through A and B from the start
        # (unlike the scalar α-gate which could get stuck at 0). Guarded
        # in forward() on non-legacy task_set.
        #
        # Rank set via class-level LORA_RANK (default 8). Params per
        # task: 2 × rank × layer_size (~2-8K depending on rank).
        lora_rank = getattr(self, "_lora_rank", 8)
        self.lora_A_cat = nn.Linear(shared_layer_size, lora_rank, bias=False)
        self.lora_B_cat = nn.Linear(lora_rank, shared_layer_size, bias=False)
        self.lora_A_next = nn.Linear(shared_layer_size, lora_rank, bias=False)
        self.lora_B_next = nn.Linear(lora_rank, shared_layer_size, bias=False)
        nn.init.zeros_(self.lora_B_cat.weight)
        nn.init.zeros_(self.lora_B_next.weight)

    @property
    def last_gate_stats(self) -> dict[str, torch.Tensor]:
        return self.dselect.last_gate_stats

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

        shared_cat, shared_next = self.dselect(enc_cat, enc_next)

        # Per-task MTLoRA adapter (CVPR 2024) on top of shared DSelect-K.
        # Adds rank-r dedicated capacity per task. B initialised to 0
        # so step-0 contribution = baseline (bit-exact), but gradients
        # flow through A,B so the adapter is *active* from step 1 —
        # unlike the scalar α-gate variant (ablation step 3) which got
        # stuck at α=0 throughout. The α-gated skip is kept in this
        # forward path as an additional learnable contribution; α=0 init
        # means it starts as "MTLoRA only" and the optimizer can learn
        # to use the scalar skip if it helps.
        if self._task_set is not LEGACY_CATEGORY_NEXT:
            lora_cat = self.lora_B_cat(self.lora_A_cat(enc_cat))
            lora_next = self.lora_B_next(self.lora_A_next(enc_next))
            shared_cat = shared_cat + lora_cat + self.skip_alpha_cat * enc_cat
            shared_next = shared_next + lora_next + self.skip_alpha_next * enc_next

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
        """Run only the category subgraph through DSelect-k experts."""
        if self._task_a_is_sequential:
            pad_value = InputsConfig.PAD_VALUE
            mask = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        dummy_next = torch.zeros_like(enc_cat)
        shared_cat, _ = self.dselect(enc_cat, dummy_next)
        if self._task_a_is_sequential:
            return self.category_poi(shared_cat)
        return self.category_poi(shared_cat.squeeze(1)).view(-1, self.num_classes_task_a)

    def next_forward(self, next_input: torch.Tensor) -> torch.Tensor:
        """Run only the next-POI subgraph through DSelect-k experts."""
        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)
        enc_next = self.next_encoder(next_input)
        dummy_cat = torch.zeros(enc_next.size(0), enc_next.size(-1), device=enc_next.device)
        _, shared_next = self.dselect(dummy_cat, enc_next)
        return self.next_poi(shared_next)

    def shared_parameters(self) -> Iterator[nn.Parameter]:
        return (
            p
            for name, p in self.named_parameters()
            if "dselect.experts" in name
        )

    def task_specific_parameters(self) -> Iterator[nn.Parameter]:
        # LoRA A/B and skip_alpha are per-task adapters on top of the
        # shared DSelect-K output; they must appear in this bucket so
        # gradient-surgery losses (PCGrad / CAGrad / AlignedMTL) actually
        # set their .grad. Missing them causes a silent freeze — see
        # docs/issues/check2hgi/MTL_PARAM_PARTITION_BUG.md.
        #
        # The LoRA branch is **gated off** on the legacy ``task_set``
        # (see forward() line 139) — those parameters are not in the
        # autograd graph there. Including them in this iterator on the
        # legacy path causes ``torch.autograd.grad`` in PCGrad to raise
        # "One of the differentiated Tensors appears to not have been
        # used in the graph." So we only enumerate the LoRA / α-skip
        # params when the forward pass actually uses them.
        base_keys = (
            "category_encoder",
            "next_encoder",
            "category_poi",
            "next_poi",
            "dselect.category_selector",
            "dselect.next_selector",
            "dselect.category_selector_weights",
            "dselect.next_selector_weights",
        )
        lora_keys = (
            "lora_A_cat",
            "lora_B_cat",
            "lora_A_next",
            "lora_B_next",
            "skip_alpha_cat",
            "skip_alpha_next",
        )
        keys = base_keys + lora_keys if self._task_set is not LEGACY_CATEGORY_NEXT else base_keys
        return (
            p
            for name, p in self.named_parameters()
            if any(key in name for key in keys)
        )


__all__ = ["MTLnetDSelectK"]
