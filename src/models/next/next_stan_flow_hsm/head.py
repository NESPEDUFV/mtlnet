"""F50 T1.2 — GETNext-hard with hierarchical-additive softmax head.

Tests the F50 T1.2 hypothesis: *the FL architectural cost is partly an
artefact of the 4,702-class flat softmax. A hierarchical inductive bias on
the reg head reduces the head-side parameter explosion / gradient noise.*

Mechanism (additive hierarchical bias, NOT a true hierarchical softmax):

    final_logits[r] = parent_logit[c(r)] + child_logit[r] + α · log_T[last][r]

where ``c(r)`` is the cluster id of region ``r`` (precomputed by k-means
in ``scripts/build_region_hierarchy.py``), ``parent_logit ∈ R^{n_clusters}``
and ``child_logit ∈ R^{n_regions}`` are produced by two separate linear
heads on top of STAN's pre-classifier features.

This is an **architectural** hierarchical bias on the same flat-softmax
loss path. The model can choose to use the parent term (cluster-level
information) or the child term (within-cluster discrimination) freely.
The hypothesis is that this decomposition of capacity helps long-tail
discrimination at FL scale (4.7K regions) more than the flat
``Linear(d_model, 4702)`` of ``next_getnext_hard``.

If T1.2 confirms the hypothesis, a follow-up F-experiment can implement
true hierarchical softmax (decomposed loss: ``-log P(parent) - log P(region | parent)``)
for stronger architectural separation.

Trainer-compatibility note: the head returns logits of shape
``[B, num_classes]`` exactly like ``next_getnext_hard``, so the
``CrossEntropyLoss`` path in ``mtl_cv.py`` and the eval pipeline are
untouched.

Hierarchy file format
---------------------
Pre-built via ``scripts/build_region_hierarchy.py``:

    {
      "n_regions": int,
      "n_clusters": int,
      "region_to_cluster": LongTensor[n_regions],
      ...
    }

Loaded via the ``hierarchy_path`` constructor argument — symmetric to how
``next_getnext_hard`` loads ``transition_path``.
"""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn

from data.aux_side_channel import get_current_aux
from models.next.next_stan.head import NextHeadSTAN
from models.registry import register_model


@register_model("next_stan_flow_hsm")
@register_model("next_getnext_hard_hsm")  # legacy alias (renamed 2026-05-01)
class NextHeadStanFlowHSM(nn.Module):
    """Hierarchical-additive variant of STAN-Flow.

    Parameters mirror ``NextHeadStanFlow`` plus:
        hierarchy_path: path to ``region_hierarchy.pt`` (built by
            ``scripts/build_region_hierarchy.py``).
        n_clusters: optional override (otherwise read from the hierarchy file).

    The STAN backbone, transition matrix, and ``α`` parameter are
    instantiated identically to STAN-Flow so the only architectural delta
    is the parent + child classifier decomposition.
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
        hierarchy_path: Optional[str] = None,
        alpha_init: float = 0.1,
    ):
        super().__init__()
        if hierarchy_path is None:
            raise ValueError(
                "next_getnext_hard_hsm requires hierarchy_path. Build it with "
                "`python scripts/build_region_hierarchy.py --state <state>`."
            )

        # STAN backbone with the matched pre-classifier features.
        self.stan = NextHeadSTAN(
            embed_dim=embed_dim,
            num_classes=num_classes,
            seq_length=seq_length,
            d_model=d_model,
            num_heads=num_heads,
            dropout=dropout,
            bias_init=bias_init,
        )
        self._num_classes = int(num_classes)
        self._d_model = int(d_model)

        # Load hierarchy. The hierarchy's n_regions may exceed num_classes if
        # the embedding pipeline stored extra rows (e.g. padding index). Allow
        # `hierarchy.n_regions >= num_classes` and truncate — symmetric to how
        # `next_getnext_hard` handles `log_T` (truncates to num_classes).
        h = torch.load(hierarchy_path, map_location="cpu", weights_only=False)
        if h["n_regions"] < num_classes:
            raise ValueError(
                f"Hierarchy n_regions ({h['n_regions']}) is smaller than head "
                f"num_classes ({num_classes}). Rebuild for this state."
            )
        n_clusters = int(h["n_clusters"])
        region_to_cluster = h["region_to_cluster"].long()
        if region_to_cluster.numel() < num_classes:
            raise ValueError(
                f"region_to_cluster size {region_to_cluster.numel()} < num_classes={num_classes}."
            )
        region_to_cluster = region_to_cluster[:num_classes].contiguous()
        self.register_buffer("region_to_cluster", region_to_cluster)

        # Hierarchical-additive classifiers (replace STAN's flat classifier path).
        # We re-use STAN's `forward_features` to get the [B, d_model] pre-classifier
        # representation, then apply parent + child classifiers in parallel.
        #
        # STAN's `self.stan.classifier = Sequential(LayerNorm, Dropout, Linear)` is
        # entirely unused on this forward path. Replace the inner Linear with
        # Identity to drop the ~1.2M unused-parameter waste at FL scale; keep
        # STAN's LayerNorm + Dropout as the regularisation we apply BEFORE the
        # parent/child classifiers (matches STAN's own pattern).
        stan_pre = self.stan.classifier  # Sequential(LayerNorm, Dropout, Linear)
        self.feat_norm = stan_pre[0]     # LayerNorm(d_model) — share weights, train as part of STAN
        self.feat_dropout = stan_pre[1]  # Dropout
        # Drop the unused Linear by replacing it with Identity so STAN forward
        # still works and parameter count drops to (STAN encoder + parent + child).
        self.stan.classifier[2] = nn.Identity()

        self.parent_classifier = nn.Linear(d_model, n_clusters)
        self.child_classifier = nn.Linear(d_model, num_classes)
        self._n_clusters = n_clusters

        # α + log_T graph prior — identical to next_getnext_hard
        self.alpha = nn.Parameter(torch.tensor(float(alpha_init)))
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
        # Run STAN's encoder to get [B, d_model] pooled features.
        features = self.stan.forward_features(x)
        # Apply STAN's LayerNorm + Dropout (the regularisation it would have applied
        # before its flat classifier) before the parent + child classifiers.
        features = self.feat_dropout(self.feat_norm(features))

        # Hierarchical-additive logit decomposition
        parent_logits = self.parent_classifier(features)              # [B, n_clusters]
        child_logits = self.child_classifier(features)                # [B, n_regions]
        # Broadcast parent_logit to per-region: parent_for_region[b, r] = parent_logits[b, c(r)]
        parent_for_region = parent_logits.index_select(1, self.region_to_cluster)  # [B, n_regions]

        base_logits = parent_for_region + child_logits

        # GETNext-hard graph prior — identical to next_getnext_hard
        aux = get_current_aux()
        if aux is None:
            return base_logits + self.alpha * 0.0

        if aux.device != base_logits.device:
            aux = aux.to(base_logits.device)
        pad_mask = (aux < 0) | (aux >= self._num_classes)
        safe_idx = aux.clamp(min=0, max=self._num_classes - 1)
        transition_prior = self.log_T[safe_idx]  # [B, num_classes]
        if pad_mask.any():
            transition_prior = transition_prior.masked_fill(
                pad_mask.unsqueeze(-1), 0.0
            )

        return base_logits + self.alpha * transition_prior


# Legacy class-name alias retained for code-level back-compat.
NextHeadGETNextHardHSM = NextHeadStanFlowHSM

__all__ = ["NextHeadStanFlowHSM", "NextHeadGETNextHardHSM"]
