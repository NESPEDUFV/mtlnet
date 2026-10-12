"""STAN-Flow: STAN-attention backbone + α·log_T region-trajectory-flow prior.

Paper-facing class name `NextHeadStanFlow`; legacy alias `NextHeadGETNextHard`
retained for back-compat with imports and JSON keys (this class was previously
called "next_getnext_hard" / `NextHeadGETNextHard`).

The trajectory-flow prior is inspired by GETNext (Yang et al. SIGIR 2022) but
this is **not** a faithful reproduction — STAN-Flow predicts next *region*
(TIGER tracts, ~1-9K classes), uses STAN's attention backbone, and operates
on our pre-trained substrate. GETNext is a next-POI method with friendship +
check-in graph priors over POI ids. See `PAPER_BASELINES_STRATEGY.md` §
"STAN-Flow naming".

Mechanism:

    final_logits = stan_logits + α · log_T[last_region_idx]

where ``last_region_idx`` is the region of the **observed** last-step POI,
not a learned probe output. Compare to ``NextHeadGETNext`` (soft probe)
which approximates this via ``softmax(probe(last_emb)) @ log_T``.

Our inference-time ablation
(``docs/findings/B5_HARD_VS_SOFT_INFERENCE.md``) showed
hard-index recovery of +3 to +9 pp Acc@10 at near-convergence over the
soft-probe adaptation we currently ship. This head tests whether that
gap widens, stays, or narrows when the STAN backbone is allowed to
co-adapt against the sharper prior.

Aux-channel plumbing
--------------------
The head reads ``last_region_idx`` via the thread-local
``src/data/aux_side_channel.py``, populated by ``AuxPublishingLoader``
before each ``forward`` call. This keeps the MTL training loop
(``mtl_cv.py``) unchanged — a shared hot path we do NOT want to touch
while partition-bugfix reruns are live.
"""

from __future__ import annotations

import os
from typing import Optional

import torch
import torch.nn as nn

from data.aux_side_channel import get_current_aux
from models.next.next_stan.head import NextHeadSTAN, _LEGACY_STAN_MASK
from models.registry import register_model

# Skip the α·log_T gather when the prior is provably inert (frozen α == 0.0): the
# forward otherwise pays a [B, C] gather + masked_fill + mul + add per batch — ~3-4
# extra [B, C] passes at region cardinality (CA C=8501: ~70 MB each) — to add an exact
# zero. Byte-identical: with a frozen zero α, ``logits + 0.0 * prior == logits``
# bitwise for any finite prior (and the v18 dedicated-reg / joint cells run exactly
# this config: ``freeze_alpha=True alpha_init=0.0``, log_T = zeros). The learnable-α
# path is never skipped (α must stay in the autograd graph), and log_T-KD is
# unaffected (it reads the ``log_T`` buffer directly, never this forward path).
# MTL_SKIP_INERT_PRIOR=0 restores the legacy always-gather forward.
_SKIP_INERT_PRIOR = os.environ.get("MTL_SKIP_INERT_PRIOR", "1").strip() not in ("0", "false", "False")


@register_model("next_stan_flow")
@register_model("next_getnext_hard")  # legacy alias (renamed 2026-05-01)
class NextHeadStanFlow(nn.Module):
    """STAN-Flow: STAN-attention backbone + α·log_T trajectory-flow prior.

    Uses a **hard** ``last_region_idx`` gather in place of a soft probe
    (compare ``NextHeadGETNext``).

    Parameters
    ----------
    embed_dim, num_classes, seq_length, d_model, num_heads, dropout, bias_init:
        Forwarded to the underlying ``NextHeadSTAN``.
    transition_path:
        Path to a ``.pt`` file with key ``log_transition`` — the
        pre-computed region-transition log-probability matrix. Same
        format as ``NextHeadGETNext``.
    alpha_init:
        Initial value for the learnable ``α`` scalar. Default ``0.1``,
        same as the soft variant, so that training dynamics start from
        the same point before diverging.
    """

    def __init__(
        self,
        embed_dim: int,
        num_classes: int,
        seq_length: int = 9,
        d_model: int = 128,
        num_heads: int = 4,
        dropout: float = 0.3,
        bias_init: str = "alibi",
        transition_path: Optional[str] = None,
        alpha_init: float = 0.1,
        freeze_alpha: bool = False,
    ):
        super().__init__()
        self.stan = NextHeadSTAN(
            embed_dim=embed_dim,
            num_classes=num_classes,
            seq_length=seq_length,
            d_model=d_model,
            num_heads=num_heads,
            dropout=dropout,
            bias_init=bias_init,
        )
        # F50 D1 — when ``freeze_alpha=True``, register alpha as a buffer
        # (not a Parameter) so gradient descent cannot move it from its
        # initial value. Combined with ``alpha_init=0.0``, this disables
        # the α·log_T graph prior entirely — output = stan_logits alone.
        # Tests how much of the 82.44 STL ceiling comes from the prior vs
        # the encoder.
        if bool(freeze_alpha):
            self.register_buffer("alpha", torch.tensor(float(alpha_init)))
        else:
            self.alpha = nn.Parameter(torch.tensor(float(alpha_init)))
        self._num_classes = int(num_classes)
        # Frozen α == 0.0 ⇒ the prior term is exactly zero for every batch; skip the
        # gather entirely (see _SKIP_INERT_PRIOR above). Decided once at construction —
        # a frozen buffer cannot change during training.
        self._inert_prior = (
            _SKIP_INERT_PRIOR and bool(freeze_alpha) and float(alpha_init) == 0.0
        )

        if transition_path is not None:
            payload = torch.load(transition_path, map_location="cpu", weights_only=False)
            log_T = payload["log_transition"] if isinstance(payload, dict) else payload
            log_T = log_T.float()
            if log_T.shape[0] < num_classes or log_T.shape[1] < num_classes:
                raise ValueError(
                    f"Transition matrix shape {tuple(log_T.shape)} is smaller "
                    f"than num_classes={num_classes}. Rebuild for this state."
                )
            log_T = log_T[:num_classes, :num_classes].contiguous()
            self.register_buffer("log_T", log_T)
        else:
            self.register_buffer("log_T", torch.zeros(num_classes, num_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        stan_logits = self.stan(x)

        if self._inert_prior:
            # Frozen α == 0.0: the prior contributes an exact bitwise zero
            # (``logits + 0.0 * prior == logits`` for finite priors), so skip the
            # [B, C] gather/masked_fill/mul/add. α is a buffer here, never a
            # Parameter, so there is no autograd-graph obligation to keep.
            return stan_logits

        aux = get_current_aux()  # [B] int64 last_region_idx, or None
        if aux is None:
            # Defensive: eval outside AuxPublishingLoader (e.g. isolated
            # unit tests, FLOPs probe, or a misconfigured training run
            # where the aux loader wasn't wired up). Fall back to pure
            # STAN, but keep ``alpha`` in the autograd graph (via a
            # zero-coefficient multiply) so gradient-surgery losses like
            # PCGrad that enumerate ``task_specific_parameters`` don't
            # crash with "unused in graph" when a batch reaches this
            # branch.
            return stan_logits + self.alpha * 0.0

        if aux.device != stan_logits.device:
            aux = aux.to(stan_logits.device)
        # Zero the prior for pad / out-of-bounds rows; clamp index so the
        # gather never crashes even on bad data.
        pad_mask = (aux < 0) | (aux >= self._num_classes)
        safe_idx = aux.clamp(min=0, max=self._num_classes - 1)
        transition_prior = self.log_T[safe_idx]  # [B, num_classes]
        # masked_fill is the identity for an all-False mask → apply unconditionally (byte-identical
        # value, no .any() host sync / graph break). MTL_STAN_LEGACY_MASK=1 restores the guard.
        if _LEGACY_STAN_MASK:
            if pad_mask.any():
                transition_prior = transition_prior.masked_fill(pad_mask.unsqueeze(-1), 0.0)
        else:
            transition_prior = transition_prior.masked_fill(pad_mask.unsqueeze(-1), 0.0)

        return stan_logits + self.alpha * transition_prior


# Legacy class-name alias retained for code-level back-compat. Existing imports
# `from models.next.next_stan_flow.head import NextHeadGETNextHard` (or via the
# package __init__) keep working.
NextHeadGETNextHard = NextHeadStanFlow

__all__ = ["NextHeadStanFlow", "NextHeadGETNextHard"]
