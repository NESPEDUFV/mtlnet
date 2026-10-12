"""Variant model components for the check2hgi-up study.

Each variant is a single, isolated change so that the downstream comparison
can attribute effects to a specific intervention. Borrows ideas from HGI
(hard negatives, set-transformer pooling), Time2Vec (explicit time encoding),
and modern self-supervised practice (InfoNCE, uncertainty-weighted MTL).
"""

from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATv2Conv, RGCNConv

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption, EPS


# ---------------------------------------------------------------------------
# T5.3 — Multi-view co-training wrapper (cross-view POI alignment)
# ---------------------------------------------------------------------------


def _cross_view_loss(poi_v1: torch.Tensor, poi_v2: torch.Tensor,
                     loss_type: str = "cosine",
                     temperature: float = 0.2) -> torch.Tensor:
    """T5.3 — cross-view POI-level alignment loss.

    Args:
        poi_v1: View-1 POI embeddings [N_poi, D].
        poi_v2: View-2 POI embeddings [N_poi, D].
        loss_type: "cosine" | "mse" | "infonce".
        temperature: InfoNCE temperature (ignored otherwise).

    Returns:
        Scalar tensor with gradient w.r.t. BOTH inputs.

    Variants:
      * cosine:  ``(1 - cos(v1, v2)).mean()`` — bounded, minimised at 0
                 (per spec, default).
      * mse:     symmetric stop-gradient MSE
                 ``0.5 * (MSE(v1, sg(v2)) + MSE(v2, sg(v1)))`` — BYOL-style,
                 prevents trivial joint collapse to zero.
      * infonce: symmetric temperature-scaled cross-entropy with each
                 (v1_i, v2_i) row pair as positives and all other (i, j)
                 pairs as negatives. Averaged over both directions.
    """
    if poi_v1.shape != poi_v2.shape:
        raise ValueError(
            f"_cross_view_loss: shape mismatch v1={tuple(poi_v1.shape)} "
            f"v2={tuple(poi_v2.shape)}"
        )
    if loss_type == "cosine":
        cos = F.cosine_similarity(poi_v1, poi_v2, dim=-1, eps=EPS)
        return (1.0 - cos).mean()
    if loss_type == "mse":
        v2_sg = poi_v2.detach()
        v1_sg = poi_v1.detach()
        return 0.5 * (F.mse_loss(poi_v1, v2_sg) + F.mse_loss(poi_v2, v1_sg))
    if loss_type == "infonce":
        # Audit T5.3 #1: guard against div-by-zero / negative temperature.
        if float(temperature) <= 0.0:
            raise ValueError(
                f"InfoNCE temperature must be > 0; got {temperature}"
            )
        n = poi_v1.shape[0]
        v1n = F.normalize(poi_v1, dim=-1)
        v2n = F.normalize(poi_v2, dim=-1)
        logits = (v1n @ v2n.t()) / float(temperature)        # [N_poi, N_poi]
        targets = torch.arange(n, device=logits.device)
        return 0.5 * (
            F.cross_entropy(logits, targets)
            + F.cross_entropy(logits.t(), targets)
        )
    raise ValueError(
        f"_cross_view_loss: unknown loss_type '{loss_type}'. "
        f"Choose from cosine / mse / infonce."
    )


class MultiViewWrapper(nn.Module):
    """T5.3 — Multi-view co-training wrapper.

    Holds two ``Check2HGI`` instances:
      * View 1 = canonical (user_sequence + temporal weights + category one-hot
                 + temporal sin/cos).
      * View 2 = same_poi-only edges + category-one-hot features (no temporal).

    Forward runs BOTH encoders and the wrapper exposes a cross-view alignment
    loss at the POI level. Total loss
        ``L = L_c2hgi_v1 + L_c2hgi_v2 + λ_x · L_cross``
    where ``L_c2hgi_v{1,2}`` are the canonical 3-boundary contrastive losses
    on each view and ``L_cross`` is one of cosine / symmetric-MSE / symmetric-
    InfoNCE on the per-POI embeddings.

    Compute cost: ~2× canonical when ``share_encoder=False`` (default) —
    both encoders run a full forward + backward pass per step. With
    ``share_encoder=True`` the View-1 ``checkin_encoder`` is reused for
    View 2 (only the c2p/p2r/r2c discriminators and pooling heads diverge),
    cutting cost back to ~1.2-1.5× canonical at the price of the
    distillation signal at the encoder layer.

    Composability with other T5 mechanisms:
      * Standalone T5.3: TESTED at unit level (test_multiview_wrapper) and
        smoke-tested at AL epoch=3.
      * T5.3 + T5.1 (--use-poi-id-embedding): UNTESTED. Should not error;
        the View-1 encoder picks up the POI-id table. View 2 does not, by
        design (separate encoder instance). Sensible results not verified.
      * T5.3 + T5.2a (--use-node2vec-poi): UNTESTED. The Node2Vec POI-POI
        auxiliary loss attaches to View 1 only (View 2 has no canonical
        edges to walk on). Composition should not error.
      * T5.3 + T5.2b (--use-mae-poi): UNTESTED. MAE is encoder-side; each
        view can opt in independently. Default wires MAE to View 1 only.

    Default: opt-out. Wrapping is gated by `--use-multiview` in the CLI.
    """

    SUPPORTED_LOSSES = ("cosine", "mse", "infonce")

    def __init__(self, model_v1: Check2HGI, model_v2: Check2HGI,
                 cross_lambda: float = 0.3,
                 cross_loss: str = "cosine",
                 cross_temperature: float = 0.2,
                 share_encoder: bool = False):
        super().__init__()
        if cross_loss not in self.SUPPORTED_LOSSES:
            raise ValueError(
                f"MultiViewWrapper: cross_loss must be one of "
                f"{self.SUPPORTED_LOSSES}; got {cross_loss}."
            )
        self.model_v1 = model_v1
        self.model_v2 = model_v2
        self.cross_lambda = float(cross_lambda)
        self.cross_loss = str(cross_loss)
        self.cross_temperature = float(cross_temperature)
        self.share_encoder = bool(share_encoder)
        if self.share_encoder:
            # Share encoder weights only — heads and discriminators stay
            # per-view. PyTorch handles gradient accumulation across both
            # forward calls when the same nn.Module instance is reused.
            self.model_v2.checkin_encoder = self.model_v1.checkin_encoder

    def forward(self, data_v1, data_v2):
        """Run both encoders.

        Returns:
            outs_v1, outs_v2, poi_v1, poi_v2
            where outs_v{1,2} are the raw tuples emitted by
            ``Check2HGI.forward`` (consumable by ``Check2HGI.loss(*outs)``)
            and poi_v{1,2} are the per-POI embedding tensors [N_poi, D]
            used by the cross-view alignment loss.
        """
        outs_v1 = self.model_v1(data_v1)
        outs_v2 = self.model_v2(data_v2)
        # poi embedding lives at tuple position 3 (pos_poi_emb).
        poi_v1 = outs_v1[3]
        poi_v2 = outs_v2[3]
        return outs_v1, outs_v2, poi_v1, poi_v2

    def cross_view_loss(self, poi_v1: torch.Tensor,
                        poi_v2: torch.Tensor) -> torch.Tensor:
        return _cross_view_loss(
            poi_v1, poi_v2,
            loss_type=self.cross_loss,
            temperature=self.cross_temperature,
        )

    def total_loss(self, data_v1, data_v2) -> torch.Tensor:
        """One-call forward + total loss = L_v1 + L_v2 + λ_x · L_cross."""
        outs_v1, outs_v2, poi_v1, poi_v2 = self.forward(data_v1, data_v2)
        l_v1 = self.model_v1.loss(*outs_v1)
        l_v2 = self.model_v2.loss(*outs_v2)
        l_cross = self.cross_view_loss(poi_v1, poi_v2)
        return l_v1 + l_v2 + self.cross_lambda * l_cross

    def get_embeddings(self, which: str = "v1"):
        """Return (checkin_emb, poi_emb, region_emb) on CPU.

        Args:
            which: "v1" (canonical, cat-friendly; default per spec),
                   "v2" (category-only diagnostic), or
                   "ensemble" (mean of the two views' embeddings).
        """
        if which == "v1":
            return self.model_v1.get_embeddings()
        if which == "v2":
            return self.model_v2.get_embeddings()
        if which == "ensemble":
            c1, p1, r1 = self.model_v1.get_embeddings()
            c2, p2, r2 = self.model_v2.get_embeddings()
            return (0.5 * (c1 + c2), 0.5 * (p1 + p2), 0.5 * (r1 + r2))
        raise ValueError(
            f"MultiViewWrapper.get_embeddings: which must be v1 / v2 / "
            f"ensemble; got {which}."
        )


# ---------------------------------------------------------------------------
# T5.2b: Masked POI feature reconstruction decoder
# ---------------------------------------------------------------------------

class MaskedPOIDecoder(nn.Module):
    """T5.2b — Masked POI feature-aggregate decoder (GraphMAE-spirit, POI level).

    Paired-falsification counterpart to T4.1 (GraphMAE at check-in level, which
    falsified at AL+AZ in 2026-05 with no fclass-probe lift). T5.2b operates at
    a DIFFERENT hierarchy and via a DIFFERENT mechanism:

      * T4.1: mask 50 % of CHECK-IN input features (11-d category + temporal),
        feed through the check-in GCN, decode at the check-in level.
        Mechanism = node-feature reconstruction.
      * T5.2b: mask 15 % of POIS post-pool (zero out their pooled embedding),
        aggregate Delaunay POI-POI neighbour embeddings, decode the masked POI's
        feature aggregate (mean category one-hot of check-ins ∨ log visit
        count). Mechanism = neighbourhood feature-aggregate prediction.

    Why this might lift where T4.1 did not: HGI's recipe lift derived (in the
    HGI ablation, 2018) from masked POI reconstruction more than from
    Node2Vec walks. Lifting THAT mechanism into Check2HGI tests whether the
    POI-level masked-recon objective is what carries the spatial-structural
    signal — not the walk-based pre-training and not the check-in-level
    masking.

    Leak class: the targets are functions of the encoder's INPUT (check-in
    category one-hot already lives in ``data.x``), so reconstruction adds
    STRUCTURE (decoder must predict from neighbours) without adding NEW
    information about the held-out fclass label. The user-held-out IJM
    probe is the empirical guardrail (see F62).

    Args:
        hidden_channels: dim D of pooled POI embeddings (typically 64).
        target_dim:      output dim of the decoder = dim of reconstruction
                         target (num_categories for "category_aggregate",
                         1 for "visit_count_log", num_categories+1 for
                         "both").
        mask_rate:       fraction of POIs masked at each step (default 0.15
                         per spec).
        gamma:           SCE exponent (default 3.0; same family as T4.1).
        aggr:            "mean" (default) or "gcn" — neighbour aggregation
                         scheme. "mean" averages neighbour embeddings; "gcn"
                         applies a 1-layer symmetric D^{-1/2} A D^{-1/2}
                         normalisation.
        target_kind:     informational only ("category_aggregate" |
                         "visit_count_log" | "both"); used for repr/debug.
        loss_kind:       "sce" (default; cosine on the recon vs target) or
                         "mse" (raw L2 — recommended only for visit_count
                         alone, where the target is an unbounded scalar).
    """

    def __init__(self, hidden_channels: int, target_dim: int,
                 mask_rate: float = 0.15, gamma: float = 3.0,
                 aggr: str = "mean", target_kind: str = "category_aggregate",
                 loss_kind: str = "sce"):
        super().__init__()
        if hidden_channels <= 0:
            raise ValueError(f"hidden_channels must be > 0; got {hidden_channels}")
        if target_dim <= 0:
            raise ValueError(f"target_dim must be > 0; got {target_dim}")
        if not 0.0 <= mask_rate <= 1.0:
            raise ValueError(f"mask_rate must be in [0, 1]; got {mask_rate}")
        if aggr not in ("mean", "gcn"):
            raise ValueError(f"aggr must be 'mean' or 'gcn'; got {aggr}")
        if loss_kind not in ("sce", "mse"):
            raise ValueError(f"loss_kind must be 'sce' or 'mse'; got {loss_kind}")
        self.hidden_channels = int(hidden_channels)
        self.target_dim = int(target_dim)
        self.mask_rate = float(mask_rate)
        self.gamma = float(gamma)
        self.aggr = aggr
        self.target_kind = target_kind
        self.loss_kind = loss_kind

        # Decoder: small 2-layer MLP, D → 2D → target_dim. Width chosen to
        # mirror T4.1's mae_decoder (2-layer with hidden ≥ input).
        self.decoder = nn.Sequential(
            nn.Linear(self.hidden_channels, 2 * self.hidden_channels),
            nn.PReLU(),
            nn.Linear(2 * self.hidden_channels, self.target_dim),
        )

    def _aggregate_neighbours(self, poi_emb: torch.Tensor,
                              poi_edge_index: torch.Tensor) -> torch.Tensor:
        """Aggregate masked POI embeddings via POI-POI Delaunay edges.

        ``poi_edge_index``: undirected edge list (2, E). We make it
        bidirectional inside this method (cheaper than caching both
        directions; the preprocess stores only (a, b) with a < b).

        Returns: (P, D) per-POI neighbour aggregate. POIs with NO Delaunay
        neighbour fall back to their (possibly zeroed) own embedding to
        avoid degenerate all-zero decoder inputs.
        """
        P = poi_emb.size(0)
        if poi_edge_index.numel() == 0:
            # No graph → degenerate to identity (no neighbours to aggregate).
            return poi_emb
        # Make bidirectional.
        ei = torch.cat([poi_edge_index, poi_edge_index.flip(0)], dim=1)
        src, dst = ei[0], ei[1]

        # Sum aggregation: out[dst] += poi_emb[src].
        out = torch.zeros_like(poi_emb)
        out.index_add_(0, dst, poi_emb[src])

        deg = torch.zeros(P, device=poi_emb.device, dtype=poi_emb.dtype)
        ones = torch.ones(src.size(0), device=poi_emb.device, dtype=poi_emb.dtype)
        deg.index_add_(0, dst, ones)

        if self.aggr == "mean":
            denom = deg.clamp(min=1.0).unsqueeze(-1)
            out = out / denom
        else:  # gcn-style symmetric normalisation D^{-1/2} A D^{-1/2}
            d_inv_sqrt = deg.clamp(min=1.0).pow(-0.5).unsqueeze(-1)
            # Right-normalise dst, left-normalise via per-src factor.
            # For Delaunay graphs (regular-ish degree) the difference vs the
            # "mean" branch is small but the asymptotic GCN scaling is closer.
            src_w = d_inv_sqrt[src]
            weighted_src_emb = poi_emb[src] * src_w
            out = torch.zeros_like(poi_emb)
            out.index_add_(0, dst, weighted_src_emb)
            out = out * d_inv_sqrt

        # POIs with zero degree retain zeros above; fall back to own
        # (masked = 0) embedding to keep the decoder input distribution
        # well-defined. The SCE clamp(min=0) prevents any NaN.
        isolated = (deg == 0).unsqueeze(-1)
        out = torch.where(isolated, poi_emb, out)
        return out

    def forward(self, poi_emb: torch.Tensor,
                poi_edge_index: torch.Tensor,
                target: torch.Tensor,
                generator: torch.Generator | None = None) -> torch.Tensor:
        """Run masked POI reconstruction; return scalar SCE/MSE loss.

        Args:
            poi_emb:        (P, D) pooled POI embeddings (post-Checkin2POI,
                            pre-POI2Region).
            poi_edge_index: (2, E_poi) undirected POI-POI Delaunay edges.
            target:         (P, target_dim) reconstruction target.
            generator:      optional torch.Generator for reproducible masks
                            (used by the unit test for seed-reproducibility).

        Returns: scalar loss tensor. If mask_rate=0 or no POI is sampled,
            returns a zero scalar (no autograd contribution).
        """
        if self.mask_rate <= 0.0:
            return poi_emb.new_zeros((), requires_grad=False)

        P, D = poi_emb.shape
        if target.shape != (P, self.target_dim):
            raise ValueError(
                f"target shape {tuple(target.shape)} != ({P}, {self.target_dim})"
            )

        # Sample mask under no_grad — mask SELECTION must not flow gradient.
        with torch.no_grad():
            if generator is not None:
                u = torch.rand(P, device=poi_emb.device, generator=generator)
            else:
                u = torch.rand(P, device=poi_emb.device)
            mask = u < self.mask_rate

        if not bool(mask.any()):
            return poi_emb.new_zeros((), requires_grad=False)

        # Zero out masked POIs (= 0 vector mask token). We deliberately do
        # NOT learn a [MASK] parameter here, because the masked POI must be
        # RECONSTRUCTED FROM NEIGHBOURS — if the decoder could read a
        # learned token at the masked slot, it could short-circuit the
        # neighbourhood-aggregation signal.
        poi_emb_masked = poi_emb.clone()
        poi_emb_masked[mask] = 0.0

        # Aggregate neighbour embeddings.
        neigh = self._aggregate_neighbours(poi_emb_masked, poi_edge_index)

        # Decode for masked POIs only.
        pred = self.decoder(neigh[mask])     # (M, target_dim)
        tgt = target[mask]                   # (M, target_dim)

        if self.loss_kind == "sce":
            cos = F.cosine_similarity(pred, tgt, dim=-1, eps=EPS)
            loss = ((1.0 - cos).clamp(min=0.0) ** self.gamma).mean()
        else:  # mse
            loss = F.mse_loss(pred, tgt)
        return loss

    def __repr__(self) -> str:
        return (f"MaskedPOIDecoder(D={self.hidden_channels}, "
                f"target_dim={self.target_dim}, mask_rate={self.mask_rate}, "
                f"gamma={self.gamma}, aggr={self.aggr!r}, "
                f"target_kind={self.target_kind!r}, loss_kind={self.loss_kind!r})")


# ---------------------------------------------------------------------------
# V2: Time-aware GAT encoder
# ---------------------------------------------------------------------------

class GATTimeEncoder(nn.Module):
    """GATv2 encoder where attention is (optionally) conditioned on the (1-d)
    temporal edge weight from the user-sequence graph.

    Per the T3.1 advisor (2026-05-15): conditioning attention on the temporal
    edge weight makes the encoder learn to copy the most-recent same-user
    neighbour's category into the output, producing a +11 pp leak-probe
    delta and 99% cat F1 at FL. The leak is structural to the
    (attention × temporal-edge-attr × user-sequence) triangle. Setting
    ``use_edge_attr=False`` breaks one corner of the triangle: attention is
    learned purely from node features, with no temporal conditioning. The
    rest of the architecture is unchanged. This is "fix 1" from the
    T3.1 rehabilitation menu.
    """

    def __init__(self, in_channels, hidden_channels, num_layers=2, heads=4,
                 dropout=0.0, use_edge_attr=True):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.num_layers = num_layers
        self.use_edge_attr = bool(use_edge_attr)

        assert hidden_channels % heads == 0
        head_dim = hidden_channels // heads

        # When use_edge_attr=False, the GATv2Conv is constructed without an
        # edge_dim — it does NOT expect edge_attr at forward time. Attention
        # is then learned purely from node features.
        _edge_dim = 1 if self.use_edge_attr else None

        self.convs = nn.ModuleList()
        # First layer: in_channels -> hidden_channels
        self.convs.append(GATv2Conv(in_channels, head_dim, heads=heads,
                                    edge_dim=_edge_dim, concat=True, add_self_loops=True))
        for _ in range(num_layers - 1):
            self.convs.append(GATv2Conv(hidden_channels, head_dim, heads=heads,
                                        edge_dim=_edge_dim, concat=True, add_self_loops=True))

        self.act = nn.PReLU()
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x, edge_index, edge_weight=None, **kwargs):
        # **kwargs absorbs edge_type plumbed by Check2HGI for R-GCN compatibility.
        if self.use_edge_attr and edge_weight is not None:
            edge_attr = edge_weight.unsqueeze(-1)
        else:
            edge_attr = None
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index, edge_attr=edge_attr)
            if i < len(self.convs) - 1:
                x = self.act(x)
                x = self.dropout(x)
        return x


# ---------------------------------------------------------------------------
# V3: Residual + LayerNorm GCN encoder
# ---------------------------------------------------------------------------

class ResidualLNEncoder(nn.Module):
    """Multi-layer GCN with pre-LN and residual connections from layer 1 onward."""

    def __init__(self, in_channels, hidden_channels, num_layers=3, dropout=0.1):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.num_layers = num_layers

        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()
        self.convs.append(GCNConv(in_channels, hidden_channels, cached=False, bias=True))
        self.norms.append(nn.LayerNorm(hidden_channels))
        for _ in range(num_layers - 1):
            self.convs.append(GCNConv(hidden_channels, hidden_channels, cached=False, bias=True))
            self.norms.append(nn.LayerNorm(hidden_channels))

        self.act = nn.PReLU()
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x, edge_index, edge_weight=None, **kwargs):
        # **kwargs absorbs edge_type plumbed by Check2HGI for R-GCN compatibility.
        # First layer (no residual since dim mismatch)
        x = self.convs[0](x, edge_index, edge_weight)
        x = self.norms[0](x)
        x = self.act(x)
        x = self.dropout(x)
        # Subsequent layers with residual connections
        for i in range(1, self.num_layers):
            h = self.norms[i](x)
            h = self.convs[i](h, edge_index, edge_weight)
            if i < self.num_layers - 1:
                h = self.act(h)
                h = self.dropout(h)
            x = x + h
        return x


# ---------------------------------------------------------------------------
# V6: Time2Vec input-side temporal encoder (T3.4)
# ---------------------------------------------------------------------------

class _SineActivationT2V(nn.Module):
    """Time2Vec sine activation (Kazemi et al. 2019). Replicates the canonical
    formulation from ``research/embeddings/time2vec/model/activations.py``
    without importing it, to avoid pulling in the contrastive Time2Vec module
    (which carries DEVICE auto-detect side effects via `configs.globals`).

    Warm-start option: ``warm_start=True`` initialises the first 4 periodic
    channels to recover the canonical fixed-frequency (hour_sin, hour_cos,
    dow_sin, dow_cos) features identically, so SGD can deviate only as
    needed. Addresses the T3.4 cat-axis −0.56 pp regression (T3.4 advisor
    2026-05-16 §3): random init blurs the 24-hour categorical periodicity.
    """

    def __init__(self, in_features: int, out_features: int,
                 warm_start: bool = False):
        super().__init__()
        self.out_features = out_features
        # One linear channel (Wx + b) + (out_features-1) periodic channels.
        self.w0 = nn.Parameter(torch.randn(in_features, 1))
        self.b0 = nn.Parameter(torch.randn(1))
        self.w = nn.Parameter(torch.randn(in_features, out_features - 1))
        self.b = nn.Parameter(torch.randn(out_features - 1))
        if warm_start:
            self._init_warm_start(in_features, out_features)

    def _init_warm_start(self, in_features: int, out_features: int) -> None:
        """Initialise the first 4 periodic channels so that f(x) returns the
        canonical [hour_sin, hour_cos, dow_sin, dow_cos] features when the
        input x is the same 4-d vector. Remaining channels stay random.

        Recovery math: input ``x = [hs, hc, ds, dc]`` (already the canonical
        sin/cos). Identity per-channel means ``sin(W x + b) = x_i`` for the
        i-th channel. Achieved with W_i selecting the i-th input via a
        large coefficient inside arcsin, but the simpler trick: set the
        learned periodic output's first 4 channels to read x[:, i] directly
        via a near-identity linear mix and zero bias, then SGD refines.
        """
        with torch.no_grad():
            if self.w.shape[1] >= in_features:
                # Linear-channel: small slope, zero bias.
                self.w0.zero_()
                self.b0.zero_()
                # Periodic-channels: copy x verbatim through sin( x · π/2 ),
                # since sin(π/2 · ±1) = ±1 and the canonical sin/cos values
                # are bounded in [-1, 1]. The first 4 periodic channels recover
                # x[:, 0..3] exactly when x is the canonical sin/cos vector
                # (because |hs|, |hc|, |ds|, |dc| ≤ 1).
                self.w.zero_()
                self.b.zero_()
                # Set w[i, j] = π/2 · δ_{ij} for j in 0..in_features-1.
                pi_half = float(math.pi / 2.0)
                for i in range(in_features):
                    self.w[i, i] = pi_half
                # Channels in_features..out_features-2 stay random (small).
                if out_features - 1 > in_features:
                    self.w[:, in_features:].normal_(mean=0.0, std=0.01)

    def forward(self, tau: torch.Tensor) -> torch.Tensor:
        v0 = tau @ self.w0 + self.b0                       # (N, 1)
        vp = torch.sin(tau @ self.w + self.b)              # (N, out-1)
        return torch.cat([v0, vp], dim=-1)                 # (N, out)


class Time2VecCheckinEncoder(nn.Module):
    """T3.4 — Time2Vec replaces the fixed (hour_sin, hour_cos, dow_sin, dow_cos)
    temporal features with a learned periodic encoding before the canonical
    2-layer GCN.

    Input layout (matches preprocess.py:_build_node_features):
        x[..., :num_categories]  category one-hot (preserved)
        x[..., num_categories:]  4 fixed-frequency sin/cos cols → replaced

    The Time2Vec layer projects the 4-d fixed temporal vector to a learned
    d_t-d periodic representation. Category one-hot is untouched. No residual
    or skip path preserves the one-hot verbatim downstream, so this swap does
    NOT enlarge the leak surface (T3.4 advisor pre-launch audit, 2026-05-15).
    """

    def __init__(self, in_channels: int, hidden_channels: int,
                 num_categories: int, num_layers: int = 2,
                 time2vec_dim: int = 8, dropout: float = 0.0,
                 warm_start: bool = False):
        super().__init__()
        if num_categories <= 0 or num_categories >= in_channels:
            raise ValueError(
                f"Time2VecCheckinEncoder: num_categories={num_categories} must "
                f"be in (0, in_channels={in_channels}); last 4 cols of x are "
                f"the temporal sin/cos features."
            )
        n_time_in = in_channels - num_categories
        if n_time_in != 4:
            raise ValueError(
                f"Time2VecCheckinEncoder: expected exactly 4 temporal input "
                f"features (hour_sin, hour_cos, dow_sin, dow_cos); got {n_time_in}."
            )
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.num_categories = num_categories
        self.time2vec_dim = time2vec_dim
        self.num_layers = num_layers

        self.t2v = _SineActivationT2V(in_features=n_time_in,
                                      out_features=time2vec_dim,
                                      warm_start=warm_start)

        post_in = num_categories + time2vec_dim
        self.convs = nn.ModuleList()
        self.convs.append(GCNConv(post_in, hidden_channels, cached=False, bias=True))
        for _ in range(num_layers - 1):
            self.convs.append(GCNConv(hidden_channels, hidden_channels,
                                      cached=False, bias=True))

        self.act = nn.PReLU()
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x, edge_index, edge_weight=None, **kwargs):
        # **kwargs absorbs edge_type plumbed by Check2HGI for R-GCN compatibility.
        x_cat = x[..., :self.num_categories]
        x_time = x[..., self.num_categories:]
        t2v_emb = self.t2v(x_time)
        h = torch.cat([x_cat, t2v_emb], dim=-1)
        for i, conv in enumerate(self.convs):
            h = conv(h, edge_index, edge_weight)
            if i < len(self.convs) - 1:
                h = self.act(h)
                h = self.dropout(h)
        return h


# ---------------------------------------------------------------------------
# V7: Relational GCN (R-GCN) over heterogeneous edge typing (T3.3 Option A)
# ---------------------------------------------------------------------------

class RGCNEncoder(nn.Module):
    """T3.3 — Relational GCN that aggregates separately per edge relation,
    with no attention and no edge_attr conditioning.

    Requires the upstream graph to expose ``edge_type`` as a long tensor of
    length E (relation index per edge). The companion preprocess change
    (`edge_type='both'` augmented to store per-edge type) feeds this encoder
    with K=2 relations: 0 = user_sequence, 1 = same_poi.

    Design rationale (T3.3 advisor pre-launch audit, 2026-05-15):
      * Sum aggregation per relation (no attention coefficient learning).
      * No edge_attr at forward (so the temporal-decay continuous weights
        cannot leak through attention as in the T3.1 GAT triangle).
      * Optional basis decomposition (``num_bases``) to keep the param delta
        vs canonical GCN under the F51 50 % guardrail at D=64.

    `edge_weight` is accepted for API compatibility with the rest of the
    dispatch but is IGNORED (R-GCN aggregation is over relation typing, not
    continuous weight).
    """

    def __init__(self, in_channels: int, hidden_channels: int,
                 num_relations: int = 2, num_layers: int = 2,
                 num_bases: int | None = 2, dropout: float = 0.0,
                 aggr: str = "sum"):
        super().__init__()
        if num_relations < 2:
            raise ValueError(
                f"RGCNEncoder requires num_relations >= 2; got {num_relations}. "
                f"With 1 relation R-GCN degenerates to GCN."
            )
        if aggr not in ("sum", "mean"):
            raise ValueError(f"RGCNEncoder aggr must be 'sum' or 'mean'; got {aggr}.")
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.num_relations = num_relations
        self.num_layers = num_layers
        self.num_bases = num_bases
        self.aggr = aggr

        self.convs = nn.ModuleList()
        self.convs.append(RGCNConv(in_channels, hidden_channels,
                                   num_relations=num_relations,
                                   num_bases=num_bases, aggr=aggr,
                                   root_weight=True, bias=True))
        for _ in range(num_layers - 1):
            self.convs.append(RGCNConv(hidden_channels, hidden_channels,
                                       num_relations=num_relations,
                                       num_bases=num_bases, aggr=aggr,
                                       root_weight=True, bias=True))

        self.act = nn.PReLU()
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x, edge_index, edge_weight=None, edge_type=None):
        if edge_type is None:
            raise ValueError(
                "RGCNEncoder.forward requires edge_type (long tensor of shape [E]). "
                "Caller must wire the per-edge relation index from preprocess."
            )
        h = x
        for i, conv in enumerate(self.convs):
            h = conv(h, edge_index, edge_type)
            if i < len(self.convs) - 1:
                h = self.act(h)
                h = self.dropout(h)
        return h


# ---------------------------------------------------------------------------
# T5.1 — Native learned POI ID embedding (additive post-pool)
# ---------------------------------------------------------------------------

class POIIdMixedPooler(nn.Module):
    """T5.1 — Native per-POI learned identity slot, added to the
    Checkin2POI-pooled embedding.

    Combine rule (additive, NOT concat):

        pool_aug = checkin2poi(checkins) + gamma * poi_table.weight

    Properties enforced by design:
      * Zero or small-Gaussian init (NEVER POI2Vec) — this is the
        "native" candidate in the Tier-5 carve-out; importing HGI's
        POI2Vec is the merge-family path and is OUT OF SCOPE here.
      * Trained only by check2hgi's 3 contrastive boundaries — there
        is NO fclass supervision and no auxiliary head wired here.
      * Default opt-out: when ``gamma == 0`` the output is byte-identical
        to the upstream Checkin2POI module's output (additive identity).
      * ``num_pois`` is taken at construction time and must match the
        preprocessed graph; if a future fold changes the POI inventory
        the table must be rebuilt. Caller is responsible for matching.

    Cold-start risk: a POI with very few check-ins still receives a
    full 64-d learnable slot. If the contrastive signal is too weak
    at that POI the slot stays near init (zero or N(0, 0.01²)),
    contributing negligible noise. Visit-count quantile diagnostics
    should be reported at evaluation time (Phase B). This module
    keeps the table separate so a per-POI hold-out probe can be
    plugged in at audit time without touching the main pipeline.

    Leak risk: a fully learnable per-POI table CAN memorise train-set
    transitions if the c2p discriminator finds a degenerate solution
    where the table row alone carries identity. The +gamma * table
    formulation means the pooled checkin signal stays in the gradient
    chain (the discriminator cannot reach zero loss using only the
    table because the negative POI also contributes its own table row
    plus a different checkin pool). Even so, the leak-probe (IJM /
    F51 sweep gate) and a per-POI hold-out probe (deferred to Phase B)
    are the production gates.
    """

    def __init__(self, checkin2poi: nn.Module, num_pois: int,
                 hidden_channels: int, gamma: float = 0.3,
                 init: str = "zero", init_std: float = 0.01):
        super().__init__()
        if num_pois <= 0:
            raise ValueError(f"POIIdMixedPooler: num_pois must be > 0; got {num_pois}")
        if init not in ("zero", "gaussian"):
            raise ValueError(
                f"POIIdMixedPooler: init must be 'zero' or 'gaussian'; got {init!r}"
            )
        if gamma < 0:
            raise ValueError(f"POIIdMixedPooler: gamma must be >= 0; got {gamma}")
        self.checkin2poi = checkin2poi
        self.num_pois = int(num_pois)
        self.hidden_channels = int(hidden_channels)
        self.gamma = float(gamma)
        self.init = init
        self.init_std = float(init_std)
        # Zero-init or small-Gaussian. EXPLICITLY NOT POI2Vec — the spec
        # says "trained ONLY by c2hgi's 3 boundaries (NOT warm-started
        # from POI2Vec — that would be merge-family)".
        self.poi_table = nn.Embedding(self.num_pois, self.hidden_channels)
        self._reset_table()

    def _reset_table(self):
        with torch.no_grad():
            if self.init == "zero":
                self.poi_table.weight.zero_()
            else:
                # Small Gaussian, std=0.01 by default. Keep the cold-start
                # contribution small relative to the pooled checkin signal
                # (which has unit-ish magnitude after PReLU + residual in
                # Checkin2POI). Larger std risks dominating sparse POIs.
                self.poi_table.weight.normal_(mean=0.0, std=self.init_std)

    def forward(self, x, checkin_to_poi, num_pois):
        """Pool check-ins to POIs, then add the per-POI identity slot.

        Signature matches :class:`Checkin2POI.forward` so this pooler can
        be dropped into Check2HGI as a substitute aggregator.
        """
        pooled = self.checkin2poi(x, checkin_to_poi, num_pois)
        # The table is sized at construction time; if a downstream call
        # passes a different num_pois (e.g. mini-batch sub-sampled POIs)
        # we must error — the additive identity slot is only well-defined
        # at the full POI inventory the table was built against.
        if int(num_pois) != self.num_pois:
            raise ValueError(
                f"POIIdMixedPooler.forward: num_pois={num_pois} != "
                f"self.num_pois={self.num_pois}. Rebuild the pooler."
            )
        if self.gamma == 0.0:
            # Bit-identical pass-through when gamma=0 — defensive identity
            # so an ablation at gamma=0 reproduces the canonical baseline.
            return pooled
        return pooled + self.gamma * self.poi_table.weight


# ---------------------------------------------------------------------------
# V1: Check2HGI with InfoNCE contrastive at C2P boundary
# ---------------------------------------------------------------------------

class Check2HGI_InfoNCE(Check2HGI):
    """Replaces the C2P bilinear-sigmoid-BCE loss with K-negative
    InfoNCE / cross-entropy style contrastive loss.

    For each check-in i: anchor = checkin_emb[i] (projected via W_c2p),
    positive = poi_emb[checkin_to_poi[i]],
    negatives = K random POIs (different from positive).
    Loss = -log( exp(sim_pos/τ) / (exp(sim_pos/τ) + Σ exp(sim_neg/τ)) )
    """

    def __init__(self, *args, num_negatives: int = 32, temperature: float = 0.2,
                 chunk_size: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_negatives = num_negatives
        self.temperature = temperature
        # chunk_size: process N_c in slices when materializing [N_c, K, D]
        # would OOM. None = no chunking. ~256k is safe for 6 GB GPUs at K=32, D=64.
        self.chunk_size = chunk_size

    def forward(self, data):
        num_pois = data.num_pois
        num_regions = data.num_regions

        pos_checkin_emb = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)
        cor_x = self.corruption(data.x)
        neg_checkin_emb = self.checkin_encoder(cor_x, data.edge_index, data.edge_weight)

        pos_poi_emb = self.checkin2poi(pos_checkin_emb, data.checkin_to_poi, num_pois)
        neg_poi_emb = self.checkin2poi(neg_checkin_emb, data.checkin_to_poi, num_pois)

        pos_region_emb = self.poi2region(pos_poi_emb, data.poi_to_region, data.region_adjacency)
        neg_region_emb = self.poi2region(neg_poi_emb, data.poi_to_region, data.region_adjacency)

        city_emb = self.region2city(pos_region_emb, data.region_area)

        self.checkin_embedding = pos_checkin_emb
        self.poi_embedding = pos_poi_emb
        self.region_embedding = pos_region_emb

        pos_region_expanded = pos_region_emb[data.poi_to_region]
        neg_region_indices = self._sample_negative_indices_with_similarity(
            data.poi_to_region, num_regions, data.coarse_region_similarity, data.x.device
        )
        neg_region_expanded = pos_region_emb[neg_region_indices]

        return (
            pos_checkin_emb, pos_poi_emb,
            pos_poi_emb, pos_region_expanded, neg_region_expanded,
            pos_region_emb, neg_region_emb, city_emb,
            data.checkin_to_poi, num_pois,
        )

    def loss(self, pos_checkin, pos_poi,
             pos_poi_again, pos_region_exp, neg_region_exp,
             pos_region, neg_region, city,
             checkin_to_poi, num_pois):
        # ---- Loss 1: InfoNCE for check-in -> POI ----
        # anchor: project checkin embedding via W_c2p, then dot-product with pois
        anchor = torch.matmul(pos_checkin, self.weight_c2p)         # [N_c, D]
        anchor = F.normalize(anchor, dim=-1)
        pois = F.normalize(pos_poi, dim=-1)                          # [N_p, D]

        N_c = anchor.size(0)
        K = self.num_negatives
        device = anchor.device

        pos_idx = checkin_to_poi                                     # [N_c]
        # positive similarity
        sim_pos = (anchor * pois[pos_idx]).sum(dim=-1, keepdim=True) # [N_c, 1]

        # K random negatives (different from positive)
        neg_idx = torch.randint(0, num_pois - 1, (N_c, K), device=device)
        neg_idx = torch.where(neg_idx >= pos_idx.unsqueeze(-1), neg_idx + 1, neg_idx)

        if self.chunk_size is None or N_c <= self.chunk_size:
            # Gather negatives in one shot: [N_c, K, D]
            neg_pois = pois[neg_idx]
            sim_neg = (anchor.unsqueeze(1) * neg_pois).sum(dim=-1)
        else:
            # Chunked + gradient-checkpointed: materialize [chunk, K, D] only
            # transiently and recompute it during backward instead of caching.
            # On Florida-scale data (1.4 M check-ins, K=32, D=64) the full
            # tensor is 11.5 GB; chunking alone saves only peak memory because
            # autograd retains all chunks for backward. Checkpointing trades
            # ~2× compute for ~chunk_size/N_c memory reduction.
            from torch.utils.checkpoint import checkpoint as _checkpoint

            def _sim_chunk(chunk_anchor, chunk_neg_idx, pois_ref):
                chunk_neg_pois = pois_ref[chunk_neg_idx]
                return (chunk_anchor.unsqueeze(1) * chunk_neg_pois).sum(dim=-1)

            sim_neg_chunks = []
            for i in range(0, N_c, self.chunk_size):
                j = i + self.chunk_size
                sim_neg_chunks.append(
                    _checkpoint(
                        _sim_chunk, anchor[i:j], neg_idx[i:j], pois,
                        use_reentrant=False,
                    )
                )
            sim_neg = torch.cat(sim_neg_chunks, dim=0)

        logits = torch.cat([sim_pos, sim_neg], dim=1) / self.temperature  # [N_c, 1+K]
        targets = torch.zeros(N_c, dtype=torch.long, device=device)        # positive at idx 0
        loss_c2p = F.cross_entropy(logits, targets)

        # ---- Loss 2: POI -> Region (bilinear-sigmoid-BCE, unchanged) ----
        pos_p2r = self.discriminate(pos_poi, pos_region_exp, self.weight_p2r)
        neg_p2r = self.discriminate(pos_poi, neg_region_exp, self.weight_p2r)
        loss_p2r = -torch.log(pos_p2r + EPS).mean() - torch.log(1 - neg_p2r + EPS).mean()

        # ---- Loss 3: Region -> City ----
        pos_r2c = self.discriminate_global(pos_region, city, self.weight_r2c)
        neg_r2c = self.discriminate_global(neg_region, city, self.weight_r2c)
        loss_r2c = -torch.log(pos_r2c + EPS).mean() - torch.log(1 - neg_r2c + EPS).mean()

        return (
            self.alpha_c2p * loss_c2p
            + self.alpha_p2r * loss_p2r
            + self.alpha_r2c * loss_r2c
        )


# ---------------------------------------------------------------------------
# V4: Uncertainty-weighted alphas (Kendall et al. 2018)
# ---------------------------------------------------------------------------

class Check2HGI_Uncertainty(Check2HGI):
    """Replaces fixed alpha_{c2p, p2r, r2c} with learnable log-variance
    parameters. Loss_i' = (1/(2σ_i^2)) * L_i + log σ_i.

    log_var is clamped to [-3, 3] (Kendall stability trick) so the smallest
    loss can't pull its log_var to -inf and collapse the head.
    """

    LOGVAR_MIN, LOGVAR_MAX = -3.0, 3.0

    def __init__(self, *args, **kwargs):
        # Drop alphas — they will be ignored.
        super().__init__(*args, **kwargs)
        self.log_var_c2p = nn.Parameter(torch.zeros(1))
        self.log_var_p2r = nn.Parameter(torch.zeros(1))
        self.log_var_r2c = nn.Parameter(torch.zeros(1))

    def _clamp(self, lv):
        return torch.clamp(lv, min=self.LOGVAR_MIN, max=self.LOGVAR_MAX)

    def loss(self, pos_checkin, pos_poi_exp, neg_poi_exp,
             pos_poi, pos_region_exp, neg_region_exp,
             pos_region, neg_region, city):
        pos_c2p = self.discriminate(pos_checkin, pos_poi_exp, self.weight_c2p)
        neg_c2p = self.discriminate(pos_checkin, neg_poi_exp, self.weight_c2p)
        loss_c2p = -torch.log(pos_c2p + EPS).mean() - torch.log(1 - neg_c2p + EPS).mean()

        pos_p2r = self.discriminate(pos_poi, pos_region_exp, self.weight_p2r)
        neg_p2r = self.discriminate(pos_poi, neg_region_exp, self.weight_p2r)
        loss_p2r = -torch.log(pos_p2r + EPS).mean() - torch.log(1 - neg_p2r + EPS).mean()

        pos_r2c = self.discriminate_global(pos_region, city, self.weight_r2c)
        neg_r2c = self.discriminate_global(neg_region, city, self.weight_r2c)
        loss_r2c = -torch.log(pos_r2c + EPS).mean() - torch.log(1 - neg_r2c + EPS).mean()

        lv_c2p = self._clamp(self.log_var_c2p)
        lv_p2r = self._clamp(self.log_var_p2r)
        lv_r2c = self._clamp(self.log_var_r2c)
        prec_c2p = torch.exp(-lv_c2p)
        prec_p2r = torch.exp(-lv_p2r)
        prec_r2c = torch.exp(-lv_r2c)

        return (
            0.5 * prec_c2p * loss_c2p + 0.5 * lv_c2p
            + 0.5 * prec_p2r * loss_p2r + 0.5 * lv_p2r
            + 0.5 * prec_r2c * loss_r2c + 0.5 * lv_r2c
        ).squeeze()


# ---------------------------------------------------------------------------
# T5.2a: Joint Node2Vec POI-POI skip-gram auxiliary head
# ---------------------------------------------------------------------------


class Node2VecPOIHead(nn.Module):
    """T5.2a — Joint Node2Vec skip-gram over a Delaunay POI-POI graph.

    Trains a POI-level embedding table jointly with c2hgi's 3 boundaries via
    a 4th objective: Node2Vec random walks on the Delaunay graph + skip-gram
    contrastive (positive = co-walk neighbours; negative = uniform random POIs).

    Design decisions:
        * **Separate learnable table by default** — keeps T5.2a composable with
          T5.1 (per-POI ID embedding). With ``share_table`` False, the skip-gram
          loss optimises an independent ``nn.Embedding(N_poi, D)``; the c2hgi
          encoder is untouched by this auxiliary. With ``share_table=True``,
          the caller passes the T5.1 table in via ``external_table`` and we
          re-use it (skip-gram gradients flow back into the T5.1 identity
          embeddings — a stronger coupling worth ablating).
        * **Walks generated lazily once per training epoch** — see
          ``generate_walks_once``. Walk sequences are cached on the module
          and re-used across mini-batches within an epoch. This matches the
          spec ("one batch of walks per epoch").
        * **No fclass L2 regularizer** — spec gate: would be a tautological
          leak path into the fclass probe. Pure structural skip-gram only.
        * **Walks live on CPU until needed** — Node2Vec random walks are
          memory-cheap (long tensors); only the embedding lookups go to GPU.

    Args:
        num_pois: total POI count (size of the embedding table)
        embedding_dim: D (typically 64, matching c2hgi hidden_channels)
        edge_index: (2, E) long tensor of POI-POI Delaunay edges (undirected
            edge list; caller is responsible for symmetry or letting
            torch_geometric.nn.Node2Vec handle it via add_self_loops). When
            None, the head still constructs (so the model is loadable) but
            ``compute_loss`` will return a zero tensor.
        walk_length: steps per random walk (default 10 per spec)
        context_size: skip-gram window size (default 5; centered window)
        walks_per_node: walks generated per source POI (default 5 per spec)
        p, q: Node2Vec p (return) and q (in-out) parameters (defaults 1.0).
        num_negatives: random negative POIs per positive (default 5)
        share_table: if True, ``external_table`` must be provided and is used
            as the embedding table (T5.1 coupling mode). Default False keeps
            the auxiliary head's POI table fully separate from any T5.1 table.
        external_table: optional ``nn.Embedding(num_pois, embedding_dim)``
            passed in when ``share_table=True``.

    The skip-gram positive pairs follow torch_geometric.nn.Node2Vec convention
    (center → window-context within each walk). The negative pairs are sampled
    uniformly from [0, num_pois) excluding the positive (vectorised; matches
    the c2hgi negative sampling pattern, not the hard-negative POI2Vec one
    from research/embeddings/hgi/poi2vec.py — that one used non-co-occurring
    fclass-level mining which is forbidden under the no-fclass-leak rule).
    """

    def __init__(
        self,
        num_pois: int,
        embedding_dim: int,
        edge_index: torch.Tensor | None = None,
        walk_length: int = 10,
        context_size: int = 5,
        walks_per_node: int = 5,
        p: float = 1.0,
        q: float = 1.0,
        num_negatives: int = 5,
        share_table: bool = False,
        external_table: nn.Embedding | None = None,
    ):
        super().__init__()
        self.num_pois = int(num_pois)
        self.embedding_dim = int(embedding_dim)
        self.walk_length = int(walk_length)
        self.context_size = int(context_size)
        self.walks_per_node = int(walks_per_node)
        self.p = float(p)
        self.q = float(q)
        self.num_negatives = int(num_negatives)
        self.share_table = bool(share_table)

        if self.share_table:
            if external_table is None:
                raise ValueError(
                    "Node2VecPOIHead(share_table=True) requires external_table "
                    "(typically the T5.1 POI ID embedding table)."
                )
            # Sharing semantics: do NOT register the external table as a
            # child submodule (it is owned by the parent Check2HGI and
            # already in the optimizer's param list). We bypass the
            # ``nn.Module.__setattr__`` auto-registration via the standard
            # ``object.__setattr__`` so optimizer-param-deduplication stays
            # the responsibility of the parent module.
            # Audit cleanup #3: removed the redundant ``_external_table_ref``
            # attribute — it was never read elsewhere and just shadowed the
            # real binding below.
            object.__setattr__(self, "poi_table", external_table)
        else:
            self.poi_table = nn.Embedding(self.num_pois, self.embedding_dim)
            nn.init.xavier_uniform_(self.poi_table.weight)

        # Edge index: stored as a buffer so it moves with .to(device) but is
        # not a learnable parameter. ``None`` is the no-graph fallback.
        if edge_index is not None:
            ei = edge_index if isinstance(edge_index, torch.Tensor) else torch.tensor(edge_index, dtype=torch.long)
            ei = ei.long()
            # Make symmetric: torch_geometric.nn.Node2Vec walks expect a
            # directed adjacency, so add (b,a) for each (a,b).
            if ei.numel() > 0:
                ei = torch.cat([ei, ei.flip(0)], dim=1)
            self.register_buffer("edge_index", ei, persistent=False)
        else:
            self.register_buffer("edge_index", torch.zeros((2, 0), dtype=torch.long), persistent=False)

        # Lazy: built on first call to ``generate_walks_once`` (needs device).
        self._n2v_module = None
        self._walks_cache: torch.Tensor | None = None
        self._last_epoch_id: int | None = None

    # ------------------------------------------------------------------
    # Walk generation
    # ------------------------------------------------------------------
    def _ensure_n2v(self):
        """Construct the torch_geometric.nn.Node2Vec walker on first need."""
        if self._n2v_module is not None:
            return
        if self.edge_index.numel() == 0:
            return
        try:
            from torch_geometric.nn import Node2Vec as _N2V
        except ImportError as e:
            raise ImportError(
                "T5.2a Node2VecPOIHead requires torch_geometric.nn.Node2Vec; "
                "install pyg-lib / torch-cluster or implement a manual walker."
            ) from e
        # We don't use Node2Vec's embedding table — only its walk loader.
        # Construct with embedding_dim=1 to minimise allocation.
        self._n2v_module = _N2V(
            edge_index=self.edge_index,
            embedding_dim=1,
            walk_length=self.walk_length,
            context_size=self.context_size,
            walks_per_node=self.walks_per_node,
            p=self.p,
            q=self.q,
            num_nodes=self.num_pois,
            sparse=False,
        )

    @torch.no_grad()
    def generate_walks_once(self, epoch_id: int) -> torch.Tensor | None:
        """Generate one batch of walks for the given epoch and cache.

        Spec ("one batch of walks per epoch"): if called multiple times with
        the same ``epoch_id`` the cached walks are returned; on a new epoch
        the walker is re-sampled.

        Returns ``(num_walks, walk_length)`` long tensor of POI indices, or
        None if no graph is available.
        """
        if self.edge_index.numel() == 0:
            return None
        if self._last_epoch_id == epoch_id and self._walks_cache is not None:
            return self._walks_cache
        self._ensure_n2v()
        if self._n2v_module is None:
            return None
        # Pull a single batch covering ~all nodes (the loader yields a
        # (pos_rw, neg_rw) tuple; we ignore neg_rw and re-sample later).
        # Batch size = num_pois → exactly walks_per_node walks per node.
        batch_size = max(1, self.num_pois)
        loader = self._n2v_module.loader(batch_size=batch_size, shuffle=False, num_workers=0)
        all_walks = []
        for pos_rw, _ in loader:
            all_walks.append(pos_rw)
        walks = torch.cat(all_walks, dim=0).long()
        self._walks_cache = walks
        self._last_epoch_id = epoch_id
        return walks

    # ------------------------------------------------------------------
    # Skip-gram loss
    # ------------------------------------------------------------------
    def compute_loss(self, epoch_id: int = 0) -> torch.Tensor:
        """Compute the skip-gram contrastive loss over cached walks.

        Returns a scalar tensor. If no walks are available (no graph or
        zero edges), returns ``torch.zeros(())`` on the same device as the
        POI table, with ``requires_grad=False`` — this keeps the auxiliary
        loss safely additive at λ=0 and as a no-op when the data is missing.
        """
        device = self.poi_table.weight.device
        walks = self.generate_walks_once(epoch_id)
        if walks is None or walks.numel() == 0:
            return torch.zeros((), device=device)

        walks = walks.to(device)
        W, L = walks.shape
        if L < 2:
            return torch.zeros((), device=device)

        # Build (anchor, positive) pairs from a window of size context_size.
        # Standard skip-gram: for each position j in [0, L), every position
        # k within window (excluding j) is a positive context. We use the
        # torch_geometric convention of taking contiguous (anchor, context)
        # pairs with offset 1..(context_size-1) — keeps memory linear.
        ctx = min(self.context_size - 1, L - 1)
        anchor_list, pos_list = [], []
        for offset in range(1, ctx + 1):
            anchor_list.append(walks[:, :L - offset].reshape(-1))
            pos_list.append(walks[:, offset:].reshape(-1))
        anchor_ids = torch.cat(anchor_list, dim=0)        # (P,)
        pos_ids = torch.cat(pos_list, dim=0)              # (P,)
        P = anchor_ids.size(0)
        if P == 0:
            return torch.zeros((), device=device)

        # Negative sampling: uniform random POIs, skipping the positive index.
        K = self.num_negatives
        neg_ids = torch.randint(0, self.num_pois - 1, (P, K), device=device)
        neg_ids = torch.where(neg_ids >= pos_ids.unsqueeze(-1), neg_ids + 1, neg_ids)

        anc_emb = self.poi_table(anchor_ids)              # (P, D)
        pos_emb = self.poi_table(pos_ids)                 # (P, D)
        neg_emb = self.poi_table(neg_ids)                 # (P, K, D)

        # Skip-gram log-sigmoid (Mikolov et al. 2013).
        pos_score = (anc_emb * pos_emb).sum(-1)           # (P,)
        log_pos = F.logsigmoid(pos_score)
        neg_score = -torch.bmm(neg_emb, anc_emb.unsqueeze(-1)).squeeze(-1)  # (P, K)
        log_neg = F.logsigmoid(neg_score).sum(-1)         # (P,)

        loss = -(log_pos + log_neg).mean()
        return loss


# ---------------------------------------------------------------------------
# V5: Combined (InfoNCE + GAT-time + skip+LN encoder + uncertainty)
# ---------------------------------------------------------------------------

class Check2HGI_Combined(Check2HGI_InfoNCE):
    """V1 + V4 combined — InfoNCE c2p with uncertainty-weighted multi-loss.
    The encoder is passed in by the caller via checkin_encoder."""

    LOGVAR_MIN, LOGVAR_MAX = -3.0, 3.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_var_c2p = nn.Parameter(torch.zeros(1))
        self.log_var_p2r = nn.Parameter(torch.zeros(1))
        self.log_var_r2c = nn.Parameter(torch.zeros(1))

    def _clamp(self, lv):
        return torch.clamp(lv, min=self.LOGVAR_MIN, max=self.LOGVAR_MAX)

    def loss(self, pos_checkin, pos_poi,
             pos_poi_again, pos_region_exp, neg_region_exp,
             pos_region, neg_region, city,
             checkin_to_poi, num_pois):
        # InfoNCE c2p
        anchor = torch.matmul(pos_checkin, self.weight_c2p)
        anchor = F.normalize(anchor, dim=-1)
        pois = F.normalize(pos_poi, dim=-1)
        N_c = anchor.size(0); K = self.num_negatives; device = anchor.device
        pos_idx = checkin_to_poi
        sim_pos = (anchor * pois[pos_idx]).sum(dim=-1, keepdim=True)
        neg_idx = torch.randint(0, num_pois - 1, (N_c, K), device=device)
        neg_idx = torch.where(neg_idx >= pos_idx.unsqueeze(-1), neg_idx + 1, neg_idx)
        sim_neg = (anchor.unsqueeze(1) * pois[neg_idx]).sum(dim=-1)
        logits = torch.cat([sim_pos, sim_neg], dim=1) / self.temperature
        targets = torch.zeros(N_c, dtype=torch.long, device=device)
        loss_c2p = F.cross_entropy(logits, targets)

        pos_p2r = self.discriminate(pos_poi, pos_region_exp, self.weight_p2r)
        neg_p2r = self.discriminate(pos_poi, neg_region_exp, self.weight_p2r)
        loss_p2r = -torch.log(pos_p2r + EPS).mean() - torch.log(1 - neg_p2r + EPS).mean()

        pos_r2c = self.discriminate_global(pos_region, city, self.weight_r2c)
        neg_r2c = self.discriminate_global(neg_region, city, self.weight_r2c)
        loss_r2c = -torch.log(pos_r2c + EPS).mean() - torch.log(1 - neg_r2c + EPS).mean()

        lv_c2p = self._clamp(self.log_var_c2p)
        lv_p2r = self._clamp(self.log_var_p2r)
        lv_r2c = self._clamp(self.log_var_r2c)
        prec_c2p = torch.exp(-lv_c2p)
        prec_p2r = torch.exp(-lv_p2r)
        prec_r2c = torch.exp(-lv_r2c)

        return (
            0.5 * prec_c2p * loss_c2p + 0.5 * lv_c2p
            + 0.5 * prec_p2r * loss_p2r + 0.5 * lv_p2r
            + 0.5 * prec_r2c * loss_r2c + 0.5 * lv_r2c
        ).squeeze()
