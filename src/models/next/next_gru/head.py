"""GRU next-task head."""

import torch
import torch.nn as nn

from models.registry import register_model


@register_model("next_gru")
class NextHeadGRU(nn.Module):
    """GRU-based next-category predictor."""

    def __init__(
        self,
        embed_dim: int,
        hidden_dim: int = 256,
        num_classes: int = 7,
        num_layers: int = 2,
        dropout: float = 0.3,
        grm_state: bool = False,
    ):
        super().__init__()
        self.gru = nn.GRU(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0.0,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )
        # R10 P5 (mtl_frontier, "as a head") — Gated Residual Memory READ on the GRU's
        # last-valid hidden state (the closest the stack has to the paper's RNN-state
        # primitive; next_gru is the only real RNN). γ=σ(W·masked-mean(input)) per-dim
        # gates the read: last ← γ⊙last. Default OFF (champion G bit-identical). Bias-init
        # +2 → γ≈0.88 ≈ full read at init. NOTE (audit): the length-9 fixed window has no
        # segments/growing-memory, so this is the gated-read primitive only, not the
        # paper's caching mechanism — expected regime-bounded (cat already lifted).
        self.grm_state = bool(grm_state)
        if self.grm_state:
            self.grm_gate = nn.Linear(embed_dim, hidden_dim)
            nn.init.zeros_(self.grm_gate.weight)
            nn.init.constant_(self.grm_gate.bias, 2.0)

    def _grm_apply(self, x: torch.Tensor, last: torch.Tensor, padding_mask: torch.Tensor) -> torch.Tensor:
        """Gate the last-valid GRU hidden by γ=σ(W·masked-mean_seq(x)). Identity-ish at init."""
        valid = (~padding_mask).float().unsqueeze(-1)
        mp = (x * valid).sum(dim=1) / valid.sum(dim=1).clamp_min(1.0)  # [B, embed_dim]
        gamma = torch.sigmoid(self.grm_gate(mp))  # [B, hidden_dim]
        return gamma * last

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        """Pre-classifier penultimate [B, hidden_dim] (the last-valid GRU hidden).
        Exposed for conditional coupling (mtl_frontier): a richer cat-condition
        than the 7-dim posterior."""
        padding_mask = (x.abs().sum(dim=-1) == 0)
        seq_lengths = (~padding_mask).sum(dim=1)
        output, _ = self.gru(x)
        last_idx = (seq_lengths - 1).clamp(min=0)
        batch_idx = torch.arange(x.size(0), device=output.device)
        last = output[batch_idx, last_idx]
        if self.grm_state:
            last = self._grm_apply(x, last, padding_mask)
        return last

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        padding_mask = (x.abs().sum(dim=-1) == 0)
        seq_lengths = (~padding_mask).sum(dim=1)
        output, _ = self.gru(x)

        # Vectorised last-valid-timestep extraction. The previous version
        # had a Python for loop over batch_size (~2048 iterations/forward);
        # on FL (127k rows) this added ~6M Python iterations per 50-epoch
        # run and slowed MPS training from ~35min (Transformer head) to
        # ~2h. This advanced-index fetch runs entirely on-device.
        # Clamp handles the pathological all-padded row (seq_lengths=0 →
        # idx=-1 wraps; clamp to 0 for safety — those rows get zeroed in
        # the MTL forward pre-head anyway, so the 0-index read is a no-op
        # downstream).
        batch_size = x.size(0)
        last_idx = (seq_lengths - 1).clamp(min=0)
        batch_idx = torch.arange(batch_size, device=output.device)
        last_output = output[batch_idx, last_idx]
        if self.grm_state:
            last_output = self._grm_apply(x, last_output, padding_mask)
        return self.classifier(last_output)


__all__ = ["NextHeadGRU"]
