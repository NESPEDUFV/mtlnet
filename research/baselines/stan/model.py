"""Faithful STAN model for next-region prediction.

Architecture (Luo, Liu, Liu — STAN, WWW 2021; reference impl
https://github.com/yingtaoluo/Spatial-Temporal-Attention-Network-for-POI-Recommendation):

    1. Multi-modal input embedding: ``e_trajectory[k] = e_loc(poi_k) + e_time(hour_of_week_k)``.
       Reference: ``layers.py:104-108`` (``MultiEmbed``); paper §4.1.1.
       NOTE: STAN's third additive term ``e_user(uid)`` is intentionally
       OMITTED here because we evaluate under cold-user (group-)CV — the
       user embedding cannot be fit at train time for held-out users and
       would just be random noise at val. This is documented in
       ``research/FAITHFUL_STAN_FINDINGS.md`` as a deliberate adaptation.
    2. Trajectory aggregation layer: bare single-head self-attention over
       the 9-window trajectory with a pairwise spatio-temporal bias
       added directly to the QK^T logits. Bias = ``Sum_d`` of the
       interpolated interval-embedding tables (one for Δt minutes, one
       for Δd haversine km), per the paper's Eq. 4-5 and reference
       ``layers.py:39-59`` (``SelfAttn``). NO LayerNorm, NO residual,
       NO feed-forward — STAN's encoder is a bare attention block.
    3. Matching layer: attention from candidate region embeddings to
       trajectory states, biased by the candidate-side Δd from each
       region centroid (TIGER tract centroid) to each trajectory check-in.
       Aggregates trajectory positions via softmax-weighted mean and
       returns one logit per candidate region. Mirrors STAN's matching
       attention (paper Eq. 8-9, reference ``layers.py:17-36``).
    4. Output is logits over ``n_regions``.

Adaptations vs the published architecture (all task-driven):
    - Output dim is ``n_regions`` (~1.1–1.5K), not ``n_pois`` — STAN's
      published target is next-POI candidate matching; we're predicting
      next-region (the published task is not what our table reports).
    - Cross-entropy loss instead of negative-sampled BPR — the closed
      candidate set (~1.5K regions) makes negative sampling unnecessary.
    - User embedding dropped (see note in #1).
    - Multi-head attention removed (single head, paper-faithful).
    - Window=9, stride=window — matched to our in-house pipeline so
      cross-method comparisons in the paper table are apples-to-apples.
      STAN's published max_len is 100 with prefix-expansion training;
      that protocol is documented as deferred.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

EARTH_RADIUS_KM = 6371.0
HOURS_OF_WEEK = 168


def haversine_km(lat1: torch.Tensor, lon1: torch.Tensor,
                 lat2: torch.Tensor, lon2: torch.Tensor) -> torch.Tensor:
    """Pairwise haversine distance in km. Inputs in degrees."""
    lat1r = lat1 * (math.pi / 180.0)
    lat2r = lat2 * (math.pi / 180.0)
    dlat = (lat2 - lat1) * (math.pi / 180.0)
    dlon = (lon2 - lon1) * (math.pi / 180.0)
    a = torch.sin(dlat / 2) ** 2 + torch.cos(lat1r) * torch.cos(lat2r) * torch.sin(dlon / 2) ** 2
    a = torch.clamp(a, min=0.0, max=1.0)
    c = 2 * torch.asin(torch.sqrt(a))
    return EARTH_RADIUS_KM * c


def _interp_scalar(table: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
    """Linear-interpolation lookup into a 1-D scalar table of shape ``[K]``.

    ``x`` is a tensor of bin positions in ``[0, K-1]``. Returns same shape.
    The scalar parameterisation is paper-faithful: the bias added to
    attention logits is a scalar (paper Eq. 5; reference ``layers.SelfAttn``
    does not multiply or sum across an embedding dim — the bias is
    additive scalar). A ``[K, D]`` table with ``Sum_d`` reduction (as in
    the reference's ``MultiEmbed`` for the input-embedding case) would
    be functionally equivalent to ``[K]`` for the bias-only case.
    """
    K = table.shape[0]
    x = x.clamp(min=0.0, max=K - 1 - 1e-6)
    k = x.floor().long()
    frac = x - k.float()
    # Use F.embedding (optimized embedding_dense_backward), NOT table[k] advanced
    # indexing — the latter dispatches the generic indexing_backward atomic kernel
    # that the profiler found = 97% of the backward time. Numerically identical gather.
    tbl = table.unsqueeze(-1)                                          # [K, 1]
    lo = F.embedding(k, tbl).squeeze(-1)
    hi = F.embedding((k + 1).clamp(max=K - 1), tbl).squeeze(-1)
    return (1.0 - frac) * lo + frac * hi


class _PairwiseBias(nn.Module):
    """Scalar bias = Sum_d of (E_t[Δt] + E_d[Δd]).

    Paper Eq. 5 / reference ``layers.py:54`` add a ``[B, n, n]`` scalar
    bias directly to the QK^T attention logits. The interpolated interval
    embedding is summed across the embedding dimension to produce that
    scalar (paper Eq. 5 ``Sum`` aggregation).
    """

    def __init__(self, d_model: int, k_t: int = 64, k_d: int = 64,
                 t_max_minutes: float = 7 * 24 * 60.0, d_max_km: float = 200.0):
        super().__init__()
        del d_model  # not used — bias is scalar; kept for signature compat
        self.k_t = k_t
        self.k_d = k_d
        self.t_max = t_max_minutes
        self.d_max = d_max_km
        self.E_t = nn.Parameter(torch.zeros(k_t))
        self.E_d = nn.Parameter(torch.zeros(k_d))
        nn.init.normal_(self.E_t, std=0.1)
        nn.init.normal_(self.E_d, std=0.1)

    def forward(self, dt_minutes: torch.Tensor, dd_km: torch.Tensor) -> torch.Tensor:
        """``dt_minutes, dd_km``: same shape ``[..., S, S]`` or ``[..., S, R]``.
        Returns ``[..., S, S]`` (or ``[..., S, R]``) — scalar bias per pair.
        """
        t_bin = (dt_minutes.clamp(min=0.0, max=self.t_max) / self.t_max) * (self.k_t - 1)
        d_bin = (dd_km.clamp(min=0.0, max=self.d_max) / self.d_max) * (self.k_d - 1)
        return _interp_scalar(self.E_t, t_bin) + _interp_scalar(self.E_d, d_bin)


class _SelfAttn(nn.Module):
    """Single-head bare self-attention with additive scalar bias.

    Faithful to reference ``layers.SelfAttn`` (no LN, no residual, no FFN,
    no multi-head). The only deviation is dividing by ``√d`` (paper Eq. 7
    shows the divisor; the reference repo silently omits it — see audit).
    """

    def __init__(self, d_model: int, dropout: float):
        super().__init__()
        self.d = d_model
        self.q = nn.Linear(d_model, d_model, bias=False)
        self.k = nn.Linear(d_model, d_model, bias=False)
        self.v = nn.Linear(d_model, d_model, bias=False)
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, bias: torch.Tensor,
                key_padding_mask: torch.Tensor | None) -> torch.Tensor:
        # x: [B, S, D]; bias: [B, S, S]; key_padding_mask: [B, S] True=pad.
        Q = self.q(x)
        K = self.k(x)
        V = self.v(x)
        # Audit fix #3 (2026-06-26): reference layers.SelfAttn adds the scalar
        # spatio-temporal bias directly to the raw QKᵀ logits with NO 1/√d divisor.
        scores = (Q @ K.transpose(-2, -1)) + bias
        if key_padding_mask is not None:
            scores = scores.masked_fill(key_padding_mask[:, None, :], float("-inf"))
        attn = torch.nan_to_num(F.softmax(scores, dim=-1), nan=0.0)
        attn = self.drop(attn)
        return attn @ V


class _MatchingLayer(nn.Module):
    """STAN's matching layer adapted to next-region prediction.

    Paper Eq. 8-9 / reference ``layers.Attn``. Given trajectory states
    ``S ∈ [B, n, D]`` and candidate region embeddings ``E_R ∈ [R, D]``,
    plus a candidate-side bias ``B_match ∈ [B, n, R]`` derived from
    Δd (km) between each candidate region's centroid and each
    trajectory-position lat/lon:

        score[b, n, r] = (S[b, n, :] · E_R[r, :]) / √d  +  B_match[b, n, r]
        attn[b, n, r]  = softmax_n(score[b, n, r])     # softmax over trajectory dim
        logit[b, r]    = sum_n attn[b, n, r] * score[b, n, r]

    Pad-trajectory positions are masked out of the softmax. The bias
    module here is **separate** from the trajectory-aggregation layer's
    bias (each layer in STAN has its own learned interval-embedding
    tables — paper §4 / reference ``MultiEmbed`` vs ``Embed``).
    """

    def __init__(self, d_model: int, seq_length: int, k_d: int = 64, d_max_km: float = 200.0):
        super().__init__()
        self.E_d_match = nn.Parameter(torch.zeros(k_d))
        nn.init.normal_(self.E_d_match, std=0.1)
        self.k_d = k_d
        self.d_max = d_max_km
        self.d = d_model
        # Audit fix #1 (2026-06-26): STAN's matching layer (reference layers.Attn)
        # collapses the trajectory-position dimension with a LEARNED Linear(max_len, 1),
        # NOT a parameter-free softmax-mean. The previous additive-bias + softmax over
        # positions collapsed to a distance/proximity prior. Restored here.
        self.collapse = nn.Linear(seq_length, 1, bias=False)

    def bias_per_poi(self, dd_poi: torch.Tensor) -> torch.Tensor:
        """Interp the learned Δd interval embedding into a [n_pois+1, R] bias table,
        ONCE per forward. dd_poi (POI->region km) is FIXED, so the bias depends only
        on (POI, region). Computing it here (13M for AL) instead of per (batch,pos,region)
        triple (114M) cuts the interval-bias work + its atomic-scatter backward ~9x —
        the matching-layer bottleneck the observers found (10 s/batch -> see profile)."""
        d_bin = (dd_poi.clamp(min=0.0, max=self.d_max) / self.d_max) * (self.k_d - 1)
        return _interp_scalar(self.E_d_match, d_bin)                   # [n_pois+1, R]

    def forward(self, S: torch.Tensor, region_emb: torch.Tensor,
                bias_match: torch.Tensor,
                key_padding_mask: torch.Tensor) -> torch.Tensor:
        # S:                 [B, n, D]
        # region_emb:        [R, D]
        # bias_match:        [B, n, R]  per-POI Δd interval bias, gathered (see bias_per_poi)
        # key_padding_mask:  [B, n]   bool, True=pad
        B, n, D = S.shape
        R = region_emb.shape[0]

        # Audit fix #3: reference omits the 1/√d scaling. Content dot-product on the
        # same scale as the gate so it can't be drowned out.
        content = torch.einsum("bnd,rd->bnr", S, region_emb)          # [B, n, R]
        # Audit fix #1: MULTIPLICATIVE Δd gate (reference `torch.mul`), not additive —
        # content≈0 ⇒ gated≈0, so a region cannot be scored from distance alone.
        gated = content * bias_match                                   # [B, n, R]
        # Mask pad trajectory positions to zero so they contribute nothing to the
        # learned position collapse.
        gated = gated.masked_fill(key_padding_mask[:, :, None], 0.0)   # [B, n, R]
        # Learned collapse of the trajectory-position dim (reference Linear(max_len,1)).
        return self.collapse(gated.transpose(1, 2)).squeeze(-1)        # [B, R]


class FaithfulSTAN(nn.Module):
    def __init__(
        self,
        n_pois: int,
        n_regions: int,
        d_model: int = 128,
        dropout: float = 0.3,
        k_t: int = 64,
        k_d: int = 64,
        t_max_minutes: float = 7 * 24 * 60.0,
        d_max_km: float = 200.0,
        seq_length: int = 9,
    ):
        super().__init__()
        # POI embedding (paper §4.1.1 e_loc). Idx n_pois reserved for PAD.
        self.poi_emb = nn.Embedding(n_pois + 1, d_model, padding_idx=n_pois)
        # Hour-of-week embedding (paper §4.1.1 e_time). Idx 0 = pad.
        self.time_emb = nn.Embedding(HOURS_OF_WEEK + 1, d_model, padding_idx=0)
        # Audit fix #2 (2026-06-26): the reference leaves nn.Embedding at the default
        # ~N(0,1). With std-0.02 + the (removed) 1/√d the learned content channel was
        # ~25x smaller than the distance bias at init -> born dead -> proximity collapse.
        # Scale init to ~1/√d so content and the interval bias are on the same order.
        emb_std = d_model ** -0.5
        for emb in (self.poi_emb, self.time_emb):
            nn.init.normal_(emb.weight, std=emb_std)
        with torch.no_grad():
            self.poi_emb.weight[n_pois].zero_()
            self.time_emb.weight[0].zero_()
        self.pad_poi = n_pois

        self.bias_traj = _PairwiseBias(d_model, k_t, k_d, t_max_minutes, d_max_km)
        self.attn_traj = _SelfAttn(d_model, dropout)

        # Matching-layer candidate-side: region embeddings + candidate Δd bias.
        self.region_emb = nn.Embedding(n_regions, d_model)
        nn.init.normal_(self.region_emb.weight, std=emb_std)
        self.matching = _MatchingLayer(d_model, seq_length, k_d, d_max_km)

        self.seq_length = seq_length
        # Opt-D: interp the Δd bias only over the batch's distinct POIs (bit-identical;
        # big win at large n_pois). Uses torch.unique -> dynamic shape, so it is
        # INCOMPATIBLE with CUDA-graph compile (mode="reduce-overhead"); disable for that.
        self.distinct_poi = True

    def forward(self,
                poi_idx: torch.Tensor,            # [B, S] int64; pad = -1
                hour_of_week: torch.Tensor,       # [B, S] int64; pad = 0; real 1..168
                lat: torch.Tensor,                # [B, S] float
                lon: torch.Tensor,                # [B, S] float
                t_min: torch.Tensor,              # [B, S] int/float (minutes)
                dd_poi: torch.Tensor,             # [n_pois+1, n_regions] precomputed POI->region km
                ) -> torch.Tensor:                # [B, n_regions]
        pad_mask = poi_idx < 0
        poi_safe = torch.where(pad_mask, torch.full_like(poi_idx, self.pad_poi), poi_idx)
        hour_safe = torch.where(pad_mask, torch.zeros_like(hour_of_week), hour_of_week)

        # Multi-modal input: e_loc + e_time.
        x = self.poi_emb(poi_safe) + self.time_emb(hour_safe)          # [B, S, D]

        # Trajectory-side pairwise (Δt, Δd), zeroed across pad pairs.
        t_f = t_min.float()
        dt = (t_f.unsqueeze(2) - t_f.unsqueeze(1)).abs()
        dd = haversine_km(lat.unsqueeze(2), lon.unsqueeze(2),
                          lat.unsqueeze(1), lon.unsqueeze(1))
        valid = (~pad_mask).float()
        valid_pair = valid.unsqueeze(2) * valid.unsqueeze(1)
        dt = dt * valid_pair
        dd = dd * valid_pair

        bias = self.bias_traj(dt, dd)                                  # [B, S, S]
        S = self.attn_traj(x, bias, pad_mask)                          # [B, S, D]

        # Δd interval bias. Opt-D (distinct-POI, bit-identical): interp only over the
        # DISTINCT POIs in this batch (U <= n_pois; far fewer at large n_pois) instead of
        # all n_pois every forward, then scatter back via the inverse map. Both paths use
        # F.embedding (fast embedding_dense_backward, NOT the slow generic indexing_backward).
        if self.distinct_poi:
            flat = poi_safe.reshape(-1)                                # [B*S]
            uniq, inv = torch.unique(flat, return_inverse=True)        # [U], [B*S]
            bias_u = self.matching.bias_per_poi(dd_poi.index_select(0, uniq))   # [U, R]
            bias_match = F.embedding(inv.view(poi_safe.shape), bias_u)  # [B, S, R]
        else:
            bias_per_poi = self.matching.bias_per_poi(dd_poi)          # [n_pois+1, R]
            bias_match = F.embedding(poi_safe, bias_per_poi)           # [B, S, R]
        return self.matching(
            S, self.region_emb.weight, bias_match, pad_mask,
        )                                                              # [B, n_regions]
