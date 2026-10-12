"""Shared building blocks for MTL model variants."""

from __future__ import annotations

from typing import Tuple

import torch
from torch import nn


class ResidualBlock(nn.Module):
    """Residual block with LayerNorm and Dropout for deep shared layers."""

    def __init__(self, hidden_size: int, dropout_rate: float = 0.3):
        super().__init__()
        self.norm1 = nn.LayerNorm(hidden_size)
        self.layer1 = nn.Linear(hidden_size, hidden_size)
        self.dropout1 = nn.Dropout(dropout_rate)

        self.norm2 = nn.LayerNorm(hidden_size)
        self.layer2 = nn.Linear(hidden_size, hidden_size)
        self.dropout2 = nn.Dropout(dropout_rate)

        self.activation = nn.LeakyReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = self.norm1(x)
        out = self.activation(self.layer1(out))
        out = self.dropout1(out) + residual

        residual = out
        out = self.norm2(out)
        out = self.activation(self.layer2(out))
        out = self.dropout2(out) + residual
        return out


class FiLMLayer(nn.Module):
    """Feature-wise linear modulation: ``gamma * x + beta``."""

    def __init__(self, emb_dim: int, layer_size: int):
        super().__init__()
        self.gamma = nn.Linear(emb_dim, layer_size)
        self.beta = nn.Linear(emb_dim, layer_size)

    def forward(self, x: torch.Tensor, task_emb: torch.Tensor) -> torch.Tensor:
        gamma = self.gamma(task_emb)
        beta = self.beta(task_emb)

        for _ in range(x.dim() - gamma.dim()):
            gamma = gamma.unsqueeze(1)
            beta = beta.unsqueeze(1)
        return gamma * x + beta


class CGCLiteLayer(nn.Module):
    """Single-level CGC block with shared and task-specific experts."""

    def __init__(
        self,
        layer_size: int,
        num_shared_layers: int,
        num_shared_experts: int = 2,
        num_task_experts: int = 1,
        dropout: float = 0.15,
    ):
        super().__init__()
        if num_shared_experts < 1:
            raise ValueError("num_shared_experts must be >= 1")
        if num_task_experts < 1:
            raise ValueError("num_task_experts must be >= 1")

        self.num_shared_experts = num_shared_experts
        self.num_task_experts = num_task_experts

        self.shared_experts = nn.ModuleList(
            [
                self._build_expert(layer_size, num_shared_layers, dropout)
                for _ in range(num_shared_experts)
            ]
        )
        self.category_experts = nn.ModuleList(
            [
                self._build_expert(layer_size, num_shared_layers, dropout)
                for _ in range(num_task_experts)
            ]
        )
        self.next_experts = nn.ModuleList(
            [
                self._build_expert(layer_size, num_shared_layers, dropout)
                for _ in range(num_task_experts)
            ]
        )

        gate_outputs = num_shared_experts + num_task_experts
        self.category_gate = nn.Linear(layer_size, gate_outputs)
        self.next_gate = nn.Linear(layer_size, gate_outputs)
        self.last_gate_stats: dict[str, torch.Tensor] = {}

    @staticmethod
    def _build_expert(layer_size: int, num_blocks: int, dropout: float) -> nn.Sequential:
        layers = [
            nn.Linear(layer_size, layer_size),
            nn.LeakyReLU(),
            nn.LayerNorm(layer_size),
            nn.Dropout(dropout),
        ]
        for _ in range(num_blocks - 1):
            layers.append(ResidualBlock(layer_size, dropout))
        return nn.Sequential(*layers)

    @staticmethod
    def _gate_entropy(weights: torch.Tensor) -> torch.Tensor:
        log_weights = torch.log(weights.clamp_min(1e-8))
        return -(weights * log_weights).sum(dim=-1).mean()

    def _mix(
        self,
        x: torch.Tensor,
        shared_outputs: list[torch.Tensor],
        task_experts: nn.ModuleList,
        gate: nn.Linear,
        task_name: str,
    ) -> torch.Tensor:
        task_outputs = [expert(x) for expert in task_experts]
        expert_outputs = shared_outputs + task_outputs
        stacked = torch.stack(expert_outputs, dim=-2)
        weights = torch.softmax(gate(x), dim=-1)
        mixed = torch.sum(stacked * weights.unsqueeze(-1), dim=-2)

        with torch.no_grad():
            flat_weights = weights.reshape(-1, weights.size(-1))
            self.last_gate_stats[f"{task_name}_entropy"] = self._gate_entropy(weights).detach()
            self.last_gate_stats[f"{task_name}_mean_weights"] = flat_weights.mean(dim=0).detach()

        return mixed

    def forward(
        self,
        category_x: torch.Tensor,
        next_x: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        shared_cat = [expert(category_x) for expert in self.shared_experts]
        shared_next = [expert(next_x) for expert in self.shared_experts]

        category_out = self._mix(
            category_x, shared_cat, self.category_experts, self.category_gate, "category"
        )
        next_out = self._mix(
            next_x, shared_next, self.next_experts, self.next_gate, "next"
        )
        return category_out, next_out


class MMoELiteLayer(nn.Module):
    """Multi-gate mixture-of-experts block for category and next tasks."""

    def __init__(
        self,
        layer_size: int,
        num_shared_layers: int,
        num_experts: int = 4,
        dropout: float = 0.15,
    ):
        super().__init__()
        if num_experts < 2:
            raise ValueError("num_experts must be >= 2")

        self.num_experts = num_experts
        self.experts = nn.ModuleList(
            [
                CGCLiteLayer._build_expert(layer_size, num_shared_layers, dropout)
                for _ in range(num_experts)
            ]
        )
        self.category_gate = nn.Linear(layer_size, num_experts)
        self.next_gate = nn.Linear(layer_size, num_experts)
        self.last_gate_stats: dict[str, torch.Tensor] = {}

    def _mix(
        self,
        x: torch.Tensor,
        expert_outputs: list[torch.Tensor],
        gate: nn.Linear,
        task_name: str,
    ) -> torch.Tensor:
        stacked = torch.stack(expert_outputs, dim=-2)
        weights = torch.softmax(gate(x), dim=-1)
        mixed = torch.sum(stacked * weights.unsqueeze(-1), dim=-2)

        with torch.no_grad():
            flat_weights = weights.reshape(-1, weights.size(-1))
            self.last_gate_stats[f"{task_name}_entropy"] = CGCLiteLayer._gate_entropy(weights).detach()
            self.last_gate_stats[f"{task_name}_mean_weights"] = flat_weights.mean(dim=0).detach()

        return mixed

    def forward(
        self,
        category_x: torch.Tensor,
        next_x: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        shared_cat = [expert(category_x) for expert in self.experts]
        shared_next = [expert(next_x) for expert in self.experts]

        category_out = self._mix(
            category_x, shared_cat, self.category_gate, "category"
        )
        next_out = self._mix(next_x, shared_next, self.next_gate, "next")
        return category_out, next_out


class DSelectKLiteLayer(nn.Module):
    """K-selector multi-softmax expert mixer for category and next tasks.

    Historical name retained — "DSelect-k" is misleading. The original
    DSelect-k (Hazimeh et al., 2021) uses a Gumbel-top-k routing that
    selects **exactly k** experts with a sparse posterior. This
    implementation is a **dense convex combination** over all N experts:
    each of ``num_selectors`` soft gates produces a softmax over all
    experts, and ``selector_weights`` (another softmax) mixes the K
    gates. The output is a full N-dim simplex, not a sparse top-k
    selection. Behaviourally this is closer to multi-gate MMoE with an
    extra learnable mixture step than to DSelect-k. See
    docs/issues/check2hgi/MODEL_DESIGN_REVIEW_2026-04-22.md §3.
    """

    def __init__(
        self,
        layer_size: int,
        num_shared_layers: int,
        num_experts: int = 4,
        num_selectors: int = 2,
        dropout: float = 0.15,
        temperature: float = 0.5,
    ):
        super().__init__()
        if num_experts < 2:
            raise ValueError("num_experts must be >= 2")
        if num_selectors < 1:
            raise ValueError("num_selectors must be >= 1")
        if num_selectors > num_experts:
            raise ValueError("num_selectors must be <= num_experts")
        if temperature <= 0:
            raise ValueError("temperature must be > 0")

        self.num_experts = num_experts
        self.num_selectors = num_selectors
        self.temperature = float(temperature)

        self.experts = nn.ModuleList(
            [
                CGCLiteLayer._build_expert(layer_size, num_shared_layers, dropout)
                for _ in range(num_experts)
            ]
        )

        selector_dim = num_selectors * num_experts
        self.category_selector = nn.Linear(layer_size, selector_dim)
        self.next_selector = nn.Linear(layer_size, selector_dim)

        # Global selector mixture per task (k selectors).
        self.category_selector_weights = nn.Parameter(torch.zeros(num_selectors))
        self.next_selector_weights = nn.Parameter(torch.zeros(num_selectors))

        self.last_gate_stats: dict[str, torch.Tensor] = {}

    @staticmethod
    def _entropy_from_probs(probs: torch.Tensor) -> torch.Tensor:
        log_probs = torch.log(probs.clamp_min(1e-8))
        return -(probs * log_probs).sum(dim=-1)

    def _mix(
        self,
        x: torch.Tensor,
        expert_outputs: list[torch.Tensor],
        selector: nn.Linear,
        selector_weights: torch.nn.Parameter,
        task_name: str,
    ) -> torch.Tensor:
        stacked = torch.stack(expert_outputs, dim=-2)

        selector_logits = selector(x).view(
            *x.shape[:-1],
            self.num_selectors,
            self.num_experts,
        )
        selector_expert_probs = torch.softmax(
            selector_logits / self.temperature,
            dim=-1,
        )

        selector_mix = torch.softmax(selector_weights, dim=-1).to(
            dtype=x.dtype,
            device=x.device,
        )
        selector_view_shape = (1,) * (selector_expert_probs.dim() - 2) + (
            self.num_selectors,
            1,
        )
        selector_mix = selector_mix.view(selector_view_shape)

        weights = torch.sum(selector_expert_probs * selector_mix, dim=-2)
        weights = weights / weights.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        mixed = torch.sum(stacked * weights.unsqueeze(-1), dim=-2)

        with torch.no_grad():
            flat_weights = weights.reshape(-1, weights.size(-1))
            self.last_gate_stats[f"{task_name}_entropy"] = CGCLiteLayer._gate_entropy(weights).detach()
            self.last_gate_stats[f"{task_name}_mean_weights"] = flat_weights.mean(dim=0).detach()
            selector_probs = torch.softmax(selector_weights, dim=-1)
            self.last_gate_stats[f"{task_name}_selector_entropy"] = self._entropy_from_probs(selector_probs).detach()
            self.last_gate_stats[f"{task_name}_selector_weights"] = selector_probs.detach()

        return mixed

    def forward(
        self,
        category_x: torch.Tensor,
        next_x: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        shared_cat = [expert(category_x) for expert in self.experts]
        shared_next = [expert(next_x) for expert in self.experts]

        category_out = self._mix(
            category_x,
            shared_cat,
            self.category_selector,
            self.category_selector_weights,
            "category",
        )
        next_out = self._mix(
            next_x,
            shared_next,
            self.next_selector,
            self.next_selector_weights,
            "next",
        )
        return category_out, next_out


class PLELiteLayer(nn.Module):
    """Progressive Layered Extraction: stacked CGC levels with inter-level gating.

    Each level is a CGCLiteLayer. The gated outputs of level L become the
    inputs to level L+1, enabling progressive refinement of shared and
    task-specific representations.
    """

    def __init__(
        self,
        layer_size: int,
        num_shared_layers: int,
        num_levels: int = 2,
        num_shared_experts: int = 2,
        num_task_experts: int = 2,
        dropout: float = 0.15,
    ):
        super().__init__()
        if num_levels < 1:
            raise ValueError("num_levels must be >= 1")

        self.num_levels = num_levels
        self.levels = nn.ModuleList(
            [
                CGCLiteLayer(
                    layer_size=layer_size,
                    num_shared_layers=num_shared_layers,
                    num_shared_experts=num_shared_experts,
                    num_task_experts=num_task_experts,
                    dropout=dropout,
                )
                for _ in range(num_levels)
            ]
        )
        self.last_gate_stats: dict[str, torch.Tensor] = {}

    def forward(
        self,
        category_x: torch.Tensor,
        next_x: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        cat_h, next_h = category_x, next_x
        for i, level in enumerate(self.levels):
            cat_h, next_h = level(cat_h, next_h)

        # Aggregate gate stats from all levels (report last level stats
        # directly, and prefix earlier levels).
        self.last_gate_stats.clear()
        for i, level in enumerate(self.levels):
            for key, val in level.last_gate_stats.items():
                prefix = f"L{i}_" if i < self.num_levels - 1 else ""
                self.last_gate_stats[f"{prefix}{key}"] = val

        return cat_h, next_h


__all__ = [
    "ResidualBlock",
    "FiLMLayer",
    "CGCLiteLayer",
    "MMoELiteLayer",
    "DSelectKLiteLayer",
    "PLELiteLayer",
]

