"""Faithful ReHDM model (Li et al., IJCAI 2025).

Implements:
- Embedding layer: 6 ID features → concat to d = 6 * d_id  (paper §4.2 / Eq. 3)
- POI-Level module: stacked Transformer block (MSA + FFN, Pre/Post-LN)        (§4.3)
- Trajectory-Level module: HG Transformer (vertex→hyperedge then L−1 layers
  hyperedge↔hyperedge with collaborative messages and gated residual)        (§4.4)
- Predictor: linear → softmax over the **region** label space.                (§4.5)

The only deviation from the published architecture is the predictor's output
domain: paper predicts `n_pois`; we predict `n_regions` so the result is
directly comparable to the check2HGI study's region table. Inputs and the
hypergraph machinery are unchanged.

Hypergraph batching contract
----------------------------
Each forward pass receives a *target* trajectory plus a set of *collaborative*
trajectories that satisfy `end(s_m) < start(s_target)` and are either
intra-user (`r=0`) or inter-user with a shared POI (`r=1`). Hyperedges are the
trajectories; vertices are check-ins of those trajectories. The collaborative
sub-hypergraph is built per batch by `train.build_subhypergraph` (see train.py).
"""
from __future__ import annotations

from dataclasses import dataclass
import os

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class ReHDMConfig:
    n_users: int
    n_pois: int
    n_categories: int
    n_quadkeys: int
    n_regions: int
    n_hours: int = 24
    n_days: int = 7
    d_id: int = 32          # paper notation: d_id; total d = 6 * d_id
    n_heads: int = 4
    d_ff: int = 256
    n_hg_layers: int = 2    # L (number of HG-Transformer layers)
    dropout: float = 0.2
    beta: float = 0.5       # gated-residual mix between layer ℓ and ℓ+1
    # Spatio-temporal message buckets (paper Eq. 9 t_ij / s_ij, see A2 in
    # REHDM_AUDIT_CHANGES.md). Bucketized log-Δt and log-Δd → learned embeddings
    # added into the hyperedge message. 0 disables the term (used by the v2e
    # aggregation layer, which has no inter-trajectory Δt/Δd).
    n_time_buckets: int = 32
    n_dist_buckets: int = 32


class EmbeddingLayer(nn.Module):
    """Six categorical-ID embedding tables; output is their concatenation."""

    def __init__(self, cfg: ReHDMConfig):
        super().__init__()
        self.user = nn.Embedding(cfg.n_users, cfg.d_id)
        self.poi = nn.Embedding(cfg.n_pois, cfg.d_id)
        self.cat = nn.Embedding(cfg.n_categories, cfg.d_id)
        self.hour = nn.Embedding(cfg.n_hours, cfg.d_id)
        self.day = nn.Embedding(cfg.n_days, cfg.d_id)
        self.qk = nn.Embedding(cfg.n_quadkeys, cfg.d_id)
        self.d_model = 6 * cfg.d_id

    def forward(self, ids: dict) -> torch.Tensor:
        return torch.cat(
            [
                self.user(ids["user_idx"]),
                self.poi(ids["poi_idx"]),
                self.cat(ids["category_idx"]),
                self.hour(ids["hour_idx"]),
                self.day(ids["day_idx"]),
                self.qk(ids["quadkey_idx"]),
            ],
            dim=-1,
        )


class POILevelEncoder(nn.Module):
    """One MSA + FFN block over the target check-in sequence (paper §4.3)."""

    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.ln1 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model),
        )
        self.ln2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, key_padding_mask: torch.Tensor | None = None) -> torch.Tensor:
        a, _ = self.attn(x, x, x, key_padding_mask=key_padding_mask, need_weights=False)
        x = self.ln1(x + self.drop(a))
        x = self.ln2(x + self.drop(self.ff(x)))
        return x


class HGTransformerLayer(nn.Module):
    """One Hypergraph Transformer layer.

    Operates either as `vertex → hyperedge` aggregation (initial trajectory
    representation, Eq. 12) or `hyperedge → hyperedge` propagation with edge
    types `r ∈ {intra, inter}` (Eq. 14). The two modes share parameters; the
    incidence/adjacency tensor that the caller supplies determines the mode.
    """

    def __init__(
        self,
        d_model: int,
        n_heads: int,
        dropout: float,
        n_time_buckets: int = 0,
        n_dist_buckets: int = 0,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        assert d_model % n_heads == 0
        self.d_head = d_model // n_heads
        self.q = nn.Linear(d_model, d_model)
        self.k = nn.Linear(d_model, d_model)
        self.v = nn.Linear(d_model, d_model)
        self.o = nn.Linear(d_model, d_model)
        self.edge_type = nn.Embedding(2, d_model)  # r ∈ {intra=0, inter=1}
        # A2 (faithfulness): spatio-temporal message terms t_ij, s_ij (paper
        # Eq. 9). Present only when this layer carries inter-trajectory edges
        # (the e2e propagation layers); the v2e aggregation layer instantiates
        # with 0 buckets and behaves exactly as before.
        self.use_st = n_time_buckets > 0 and n_dist_buckets > 0
        if self.use_st:
            self.time_emb = nn.Embedding(n_time_buckets, d_model)
            self.dist_emb = nn.Embedding(n_dist_buckets, d_model)
            # A2 init FIX (2026-07-08 investigation, docs REHDM_AUDIT_CHANGES.md §A2-init):
            # zero-init the Eq.9 st-embeddings by DEFAULT so the message starts as
            # h_j+r_ij (identity) and t_ij/s_ij are LEARNED from 0. The default random
            # N(0,1) init injected two 192-d noise vectors into every message from step 1
            # and cost ~4.8pp at AL (60.16 → 64.41, ≈ the A2-off 64.97 → Eq.9 done right is
            # NEUTRAL, not harmful; the standard additive-residual pattern, cf. the
            # cascade's zero-init cond_proj). REHDM_ST_RANDOM_INIT=1 restores the old
            # (buggy) random init for reproduction only.
            if os.environ.get("REHDM_ST_RANDOM_INIT") != "1":
                nn.init.zeros_(self.time_emb.weight)
                nn.init.zeros_(self.dist_emb.weight)
        self.drop = nn.Dropout(dropout)

    def forward(
        self,
        h_target: torch.Tensor,           # [Bt, d]    — target trajectory reps
        h_neigh: torch.Tensor,            # [Bn, d]    — collaborator reps
        adjacency: torch.Tensor,          # [Bt, Bn]   — 0/1 mask
        edge_types: torch.Tensor,         # [Bt, Bn]   — long, ∈ {0,1}
        time_buckets: torch.Tensor | None = None,   # [Bt, Bn] long, log-Δt bucket
        dist_buckets: torch.Tensor | None = None,   # [Bt, Bn] long, log-Δd bucket
    ) -> torch.Tensor:
        Bt, d = h_target.shape
        Bn, _ = h_neigh.shape
        # A2 (faithfulness): message m_ij = h_j + r_ij + t_ij + s_ij (paper Eq. 9).
        # The prior implementation dropped t_ij/s_ij claiming they were "not
        # defined for hyperedge messages"; the cited STHGCN ancestor (open-code
        # layer/st_encoder.py, DistanceEncoderSimple + TimeEncoder) DOES define
        # them as bucketed time-diff / distance → nn.Embedding. We restore that.
        # TODO(verify): ReHDM itself does not fix the encoder family (paper
        # ambiguity #4) nor the exact bucketization; we use log-width buckets on
        # inter-trajectory Δt (target.start − collab.end) and haversine Δd of the
        # trajectory centroids (see train._time_bucket / _dist_bucket). Confirm
        # against the authors' released code before treating as canonical.
        msg = h_neigh.unsqueeze(0).expand(Bt, Bn, d) + self.edge_type(edge_types)
        if self.use_st and time_buckets is not None and dist_buckets is not None:
            msg = msg + self.time_emb(time_buckets) + self.dist_emb(dist_buckets)

        q = self.q(h_target).view(Bt, self.n_heads, self.d_head)
        k = self.k(msg).view(Bt, Bn, self.n_heads, self.d_head)
        v = self.v(msg).view(Bt, Bn, self.n_heads, self.d_head)

        # A5 (faithfulness note): paper Eq. 5 literally writes the denominator as
        # √d (full model dim), but that is flagged as a likely typo; the STHGCN
        # open-code and standard MHA convention use √d_head, which we follow.
        scores = torch.einsum("bhd,bnhd->bhn", q, k) / (self.d_head ** 0.5)
        # -1e9 (not -inf) so rows with zero neighbors get uniform soft weights
        # over zero-valued v positions — output is 0, no NaN gradient.
        mask = adjacency.unsqueeze(1) == 0
        scores = scores.masked_fill(mask, -1e9)
        attn = F.softmax(scores, dim=-1)
        # Zero attention weights at masked positions to keep contribution exactly zero
        attn = attn.masked_fill(mask, 0.0)
        attn = self.drop(attn)
        out = torch.einsum("bhn,bnhd->bhd", attn, v).reshape(Bt, d)
        return self.o(out)

    def attn_local(
        self,
        target: torch.Tensor,           # [d]   — shared query across batch
        vertex_reps: torch.Tensor,      # [B, T, d]
        vertex_mask: torch.Tensor,      # [B, T]
        edge_types: torch.Tensor,       # [B, T] long
    ) -> torch.Tensor:
        """Per-target attention: each batch member queries its own T vertices.

        Mathematically equivalent to the block-diagonal `forward()` path used
        for `initial_trajectory_rep`, but avoids the [B, B*T] flattening and
        the Python for-loop that produced 2*B sequential MPS launches.
        """
        B, T, d = vertex_reps.shape
        msg = vertex_reps + self.edge_type(edge_types)
        q = self.q(target).view(self.n_heads, self.d_head)
        k = self.k(msg).view(B, T, self.n_heads, self.d_head)
        v = self.v(msg).view(B, T, self.n_heads, self.d_head)
        scores = torch.einsum("hd,bthd->bht", q, k) / (self.d_head ** 0.5)
        mask = vertex_mask.unsqueeze(1) == 0
        scores = scores.masked_fill(mask, -1e9)
        attn = F.softmax(scores, dim=-1).masked_fill(mask, 0.0)
        attn = self.drop(attn)
        out = torch.einsum("bht,bthd->bhd", attn, v).reshape(B, d)
        return self.o(out)

    def attn_local_perbatch(
        self,
        query: torch.Tensor,            # [B, d] — per-batch query (e.g. last-pos vertex)
        vertex_reps: torch.Tensor,      # [B, T, d]
        vertex_mask: torch.Tensor,      # [B, T]
        edge_types: torch.Tensor,       # [B, T] long
    ) -> torch.Tensor:
        """Per-batch attention: each batch row gets its own query.

        Used by ReHDMSTL with last-position-as-query pooling (the next-step
        prediction inductive bias). Same projections / scoring as `attn_local`
        but the query is broadcast per-batch rather than shared globally.
        """
        B, T, d = vertex_reps.shape
        msg = vertex_reps + self.edge_type(edge_types)
        q = self.q(query).view(B, self.n_heads, self.d_head)
        k = self.k(msg).view(B, T, self.n_heads, self.d_head)
        v = self.v(msg).view(B, T, self.n_heads, self.d_head)
        scores = torch.einsum("bhd,bthd->bht", q, k) / (self.d_head ** 0.5)
        mask = vertex_mask.unsqueeze(1) == 0
        scores = scores.masked_fill(mask, -1e9)
        attn = F.softmax(scores, dim=-1).masked_fill(mask, 0.0)
        attn = self.drop(attn)
        out = torch.einsum("bht,bthd->bhd", attn, v).reshape(B, d)
        return self.o(out)


class ReHDM(nn.Module):
    """End-to-end ReHDM with a region-classifier head."""

    def __init__(self, cfg: ReHDMConfig):
        super().__init__()
        self.cfg = cfg
        self.embed = EmbeddingLayer(cfg)
        self.d_model = self.embed.d_model
        self.poi_block = POILevelEncoder(self.d_model, cfg.n_heads, cfg.d_ff, cfg.dropout)

        self.theta = nn.Parameter(torch.zeros(self.d_model))
        nn.init.trunc_normal_(self.theta, std=0.02)

        self.v2e = HGTransformerLayer(self.d_model, cfg.n_heads, cfg.dropout)
        self.v2e_mlp = nn.Sequential(
            nn.Linear(self.d_model, self.d_model),
            nn.ReLU(),
            nn.Linear(self.d_model, self.d_model),
        )
        self.v2e_ln = nn.LayerNorm(self.d_model)
        # A4 (faithfulness): the V→E output uses an explicit L2 step (paper
        # Eq. 13, `h = L2(ReLU(...))`) applied inline in `initial_trajectory_rep`
        # — not a LayerNorm. The old `self.v2e_post = LayerNorm` was removed.

        L_e2e = max(0, cfg.n_hg_layers - 1)
        self.e2e_layers = nn.ModuleList(
            [HGTransformerLayer(self.d_model, cfg.n_heads, cfg.dropout,
                                cfg.n_time_buckets, cfg.n_dist_buckets)
             for _ in range(L_e2e)]
        )
        self.e2e_mlp = nn.ModuleList(
            [nn.Sequential(nn.Linear(self.d_model, self.d_model), nn.ReLU(),
                           nn.Linear(self.d_model, self.d_model))
             for _ in range(L_e2e)]
        )
        self.e2e_align = nn.ModuleList(
            [nn.Linear(self.d_model, self.d_model) for _ in range(L_e2e)]
        )
        # A4 note: Eq. 14's `Norm` is genuinely ambiguous (LN or L2) in the paper.
        # We keep LayerNorm here for training stability at large region domains.
        # TODO(verify): if the authors' code uses L2 at the e2e stage, swap this
        # for `F.normalize(..., dim=-1)` and A/B; kept as LN pending confirmation.
        self.e2e_post = nn.ModuleList([nn.LayerNorm(self.d_model) for _ in range(L_e2e)])

        self.classifier = nn.Linear(self.d_model, cfg.n_regions)

    def encode_pois(self, ids_seq: dict, key_padding_mask: torch.Tensor) -> torch.Tensor:
        """Return contextualized check-in reps E0(s_u^t) ∈ [B, T, d]."""
        x = self.embed(ids_seq)
        return self.poi_block(x, key_padding_mask=key_padding_mask)

    def initial_trajectory_rep(
        self, vertex_reps: torch.Tensor, vertex_mask: torch.Tensor
    ) -> torch.Tensor:
        """Aggregate per-trajectory vertices into one representation (Eq. 12-13).

        Vectorised: per-target attention on [B, T, d] using `attn_local`.
        """
        B, T, d = vertex_reps.shape
        edge_types = torch.zeros(B, T, dtype=torch.long, device=vertex_reps.device)
        targets = self.theta.unsqueeze(0).expand(B, d)
        h = self.v2e.attn_local(self.theta, vertex_reps, vertex_mask, edge_types)
        h = self.v2e_ln(targets + h)
        # A4 (faithfulness): Eq. 13 L2-normalises the V→E hidden state.
        h = F.normalize(F.relu(self.v2e_mlp(h)), dim=-1)
        return h

    def forward(
        self,
        target_ids: dict,                     # each: [B, T]
        target_mask: torch.Tensor,            # [B, T] — 1 = real, 0 = pad
        collab_ids: dict | None = None,       # each: [Bn, Tn]
        collab_mask: torch.Tensor | None = None,  # [Bn, Tn]
        adjacency: torch.Tensor | None = None,    # [B, Bn]
        edge_types: torch.Tensor | None = None,   # [B, Bn]
        time_buckets: torch.Tensor | None = None,  # [B, Bn] long (A2)
        dist_buckets: torch.Tensor | None = None,  # [B, Bn] long (A2)
    ) -> torch.Tensor:
        kpm = target_mask == 0
        target_rep = self.encode_pois(target_ids, kpm)
        h_target = self.initial_trajectory_rep(target_rep, target_mask)

        if collab_ids is None or adjacency is None or adjacency.numel() == 0:
            h_final = h_target
        else:
            # A3 (faithfulness): the POI-level self-attention refinement is applied
            # ONLY to the target trajectory (paper §4.3, trap #2). Collaborators
            # keep their raw E(q) embeddings until the V→E stage — do NOT run them
            # through `poi_block` (`encode_pois`).
            collab_rep = self.embed(collab_ids)
            h_collab = self.initial_trajectory_rep(collab_rep, collab_mask)

            h_l = h_target
            for layer, mlp, align, post in zip(
                self.e2e_layers, self.e2e_mlp, self.e2e_align, self.e2e_post
            ):
                g = layer(h_l, h_collab, adjacency, edge_types,
                          time_buckets, dist_buckets)
                gated = self.cfg.beta * align(h_l) + (1 - self.cfg.beta) * g
                h_l = post(F.relu(mlp(gated)))
            h_final = h_l

        return self.classifier(h_final)
