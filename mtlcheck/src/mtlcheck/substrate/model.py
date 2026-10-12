"""Check2HGI: the pretext model whose check-in vectors become every downstream input.

Four levels — visit, place, region, city — trained by maximising mutual information across each
boundary against corrupted negatives, plus two auxiliaries on the place axis.

## What this is a rewrite of, and what was dropped

The reference class is 1 243 lines, of which 466 are a constructor for variants. It carries every
experiment ever tried on this model — InfoNCE at two boundaries, a Node2Vec head with an alignment
term, check-in-level GraphMAE, two-pass corruption, hard negatives at the visit boundary, learned
place-id embeddings, side features with two injection points, a low-rank per-place attention bias.
All are off in v18. What runs is the path below, and it is roughly a fifth of the code.

The subclass the builder actually instantiates (`Check2HGI_DesignK`) adds a distillation head that is
`None` unless `hgi_poi_target` is passed, which v18 does not pass. It is therefore not a class here:
in v18 it is the parent, exactly.

## The two auxiliaries, and why the place path is detached

The region axis needs spatial structure the visit graph cannot supply, so a learnable place table
initialised from POI2Vec is added to the pooled place vector, diffused over a Delaunay graph, and
regularised back toward its initialisation (`anchor_loss`). The pooled vector is **detached** before
that addition — region-axis gradients never reach the check-in encoder. That detach is what keeps
the category axis reading the same pooled vector it would read with the whole block absent, and it
is why the c2p boundary consumes `pool_pure` rather than the augmented tensor.

The second auxiliary masks 15% of places and reconstructs their category-mix from Delaunay
neighbours. It reads `pool_pure` too, for the same reason.

## S17 — the objective used to change with the size of the state, and here it does not

The reference draws a hard negative at the POI↔region boundary 25% of the time, **but only when the
place count is below 50 000**. Alabama (11 848 places) trains with hard negatives; Florida (76 544),
Texas (160 938) and California (169 145) train without them, and nothing announces it. The cut falls
exactly on the small/large grouping the results are compared across, so a state-size effect and an
objective change are confounded in the banked artifacts.

That gate is not a modelling decision. It exists because the reference's hard path is a Python loop
with a device sync per draw: 72 µs × 42 286 draws = **3.1 s per epoch at California**, half an hour
added to a 500-epoch build. Expensive, not impossible — but expensive enough that someone reached for
a threshold. The mechanism itself is well defined at every state: the (0.6, 0.8) band holds 20–27% of
region pairs at all six, and **no region anywhere lacks a candidate**.

So the fix is to remove the reason rather than the behaviour. `_sample_region_negatives` here is
vectorised through a CSR index of the band, built once: **0.11 ms per epoch at California** against
the loop's 3.1 s, for a 63 MB index. No loop, no sync, no size dependence. Hard negatives are on at
every state by default (`p2r_hard_neg_size_gate=None`); setting the gate to 50 000 reproduces the
reference's split, for anyone re-deriving the banked artifacts.

This does mean a large-state substrate built here is trained on a **different objective** than the
banked one — the one the recipe describes. Recorded in `REFERENCE_DEFECTS.md §R15`.
"""

from __future__ import annotations

import logging

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

from ..config import SubstrateConfig
from .encoders import Checkin2POI, POI2Region, ResidualLNEncoder, region2city

logger = logging.getLogger(__name__)

EPS = 1e-7


class MaskedPlaceDecoder(nn.Module):
    """Mask a fraction of places and predict their category-mix from Delaunay neighbours.

    No learned mask token, deliberately: a masked place is zeroed, so the only route to its target is
    through its neighbours. A learned token would let the decoder answer without them.
    """

    def __init__(self, hidden_channels: int, target_dim: int,
                 mask_rate: float = 0.15, gamma: float = 3.0) -> None:
        super().__init__()
        self.target_dim = target_dim
        self.mask_rate = mask_rate
        self.gamma = gamma
        self.decoder = nn.Sequential(
            nn.Linear(hidden_channels, 2 * hidden_channels),
            nn.PReLU(),
            nn.Linear(2 * hidden_channels, target_dim),
        )

    def forward(self, place_emb: torch.Tensor, edge_index: torch.Tensor,
                target: torch.Tensor) -> torch.Tensor:
        n_places = place_emb.size(0)
        if target.shape != (n_places, self.target_dim):
            raise ValueError(f"target {tuple(target.shape)} != ({n_places}, {self.target_dim})")

        with torch.no_grad():
            mask = torch.rand(n_places, device=place_emb.device) < self.mask_rate
        if not bool(mask.any()):
            return place_emb.new_zeros((), requires_grad=False)

        masked = place_emb.clone()
        masked[mask] = 0.0
        neighbourhood = self._aggregate(masked, edge_index)

        predicted = self.decoder(neighbourhood[mask])
        cosine = F.cosine_similarity(predicted, target[mask], dim=-1, eps=EPS)
        return ((1.0 - cosine).clamp(min=0.0) ** self.gamma).mean()

    def _aggregate(self, place_emb: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Mean of each place's Delaunay neighbours; isolated places keep their own (zeroed) vector."""
        if edge_index.numel() == 0:
            return place_emb

        # The flip assumes a one-directional list. v18 passes an already-symmetric one, so every
        # edge is counted twice — harmless for a mean, and kept because it is what ran.
        both = torch.cat([edge_index, edge_index.flip(0)], dim=1)
        src, dst = both[0], both[1]

        total = torch.zeros_like(place_emb)
        total.index_add_(0, dst, place_emb[src])
        degree = torch.zeros(place_emb.size(0), device=place_emb.device, dtype=place_emb.dtype)
        degree.index_add_(0, dst, torch.ones_like(src, dtype=place_emb.dtype))

        averaged = total / degree.clamp(min=1.0).unsqueeze(-1)
        return torch.where((degree == 0).unsqueeze(-1), place_emb, averaged)


class Check2HGI(nn.Module):
    """The v18 substrate model. One configuration — the one that produced the banked artifacts."""

    def __init__(self, in_channels: int, num_places: int, num_regions: int,
                 poi2vec_table: torch.Tensor, delaunay_edge_index: torch.Tensor,
                 delaunay_edge_weight: torch.Tensor, recon_target_dim: int,
                 config: SubstrateConfig) -> None:
        super().__init__()
        dim = config.dim
        self.config = config
        self.dim = dim
        self.num_places = num_places
        self.num_regions = num_regions

        self.checkin_encoder = ResidualLNEncoder(in_channels, dim, config.num_layers, config.dropout)
        self.checkin2poi = Checkin2POI(dim, config.attention_head)
        self.poi2region = POI2Region(dim, config.attention_head)

        # One bilinear form per boundary, initialised as PyG's `uniform(dim, w)`.
        bound = 1.0 / dim ** 0.5
        self.weight_c2p = nn.Parameter(torch.empty(dim, dim).uniform_(-bound, bound))
        self.weight_p2r = nn.Parameter(torch.empty(dim, dim).uniform_(-bound, bound))
        self.weight_r2c = nn.Parameter(torch.empty(dim, dim).uniform_(-bound, bound))

        # Region-axis place augmentation: learnable table seeded from POI2Vec, kept near it by the
        # anchor term, diffused over Delaunay adjacency.
        if poi2vec_table.shape != (num_places, dim):
            raise ValueError(f"poi2vec table {tuple(poi2vec_table.shape)} != ({num_places}, {dim})")
        self.place_table = nn.Embedding(num_places, dim)
        with torch.no_grad():
            self.place_table.weight.copy_(poi2vec_table.float())
        self.register_buffer("place_anchor", poi2vec_table.float())
        self.register_buffer("delaunay_edge_index", delaunay_edge_index.long())
        self.register_buffer("delaunay_edge_weight", delaunay_edge_weight.float())
        self.place_gamma = nn.Parameter(torch.tensor(float(config.gamma_init)))
        self.place_gcn = GCNConv(dim, dim, cached=True, bias=True)
        self.place_gcn_act = nn.PReLU(dim)

        self.place_decoder = MaskedPlaceDecoder(
            dim, recon_target_dim, config.mae_poi_mask_rate, config.mae_poi_gamma)

        gate = config.p2r_hard_neg_size_gate
        self.hard_negatives = gate is None or num_places < gate
        self._band: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None = None
        logger.info("substrate: %d places, %d regions · region hard negatives %s%s",
                    num_places, num_regions, "ON" if self.hard_negatives else "OFF",
                    f" (legacy size gate at {gate} places — S17)" if gate is not None else "")

    # ------------------------------------------------------------------ forward

    def forward(self, data) -> dict[str, torch.Tensor]:
        """Return every tensor `loss` needs, as a dict.

        The reference returns a 9-tuple that `loss(*model(data))` splats back into 9 positional
        arguments whose order is load-bearing and undocumented at the call site. Two of the nine are
        the same tensor under different expansions. A dict costs nothing and cannot be mis-ordered.
        """
        num_places, num_regions = self.num_places, self.num_regions

        pos_checkin = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)
        neg_checkin = self.checkin_encoder(_corrupt(data.x), data.edge_index, data.edge_weight)

        # The pooled place vectors, before any region-axis augmentation. The visit boundary and both
        # auxiliaries read THESE.
        pos_place_pure = self.checkin2poi(pos_checkin, data.checkin_to_poi, num_places)
        neg_place_pure = self.checkin2poi(neg_checkin, data.checkin_to_poi, num_places)

        pos_place = self._augment_places(pos_place_pure)
        neg_place = self._augment_places(neg_place_pure)

        pos_region = self.poi2region(pos_place, data.poi_to_region, data.region_adjacency,
                                     num_regions)
        neg_region = self.poi2region(neg_place, data.poi_to_region, data.region_adjacency,
                                     num_regions)

        recon_loss = self.place_decoder(pos_place_pure, data.poi_delaunay_edge_index,
                                        data.poi_recon_target)
        city = region2city(pos_region, data.region_area)

        place_negatives = _sample_negatives(data.checkin_to_poi, num_places)
        region_negatives = self._sample_region_negatives(
            data.poi_to_region, num_regions, getattr(data, "coarse_region_similarity", None))

        self.checkin_embedding = pos_checkin
        self.place_embedding = pos_place
        self.region_embedding = pos_region

        return {
            "checkin": pos_checkin,
            "place_of_checkin": pos_place_pure[data.checkin_to_poi],
            "other_place_of_checkin": pos_place_pure[place_negatives],
            "place": pos_place,
            "region_of_place": pos_region[data.poi_to_region],
            "other_region_of_place": pos_region[region_negatives],
            "region": pos_region,
            "corrupted_region": neg_region,
            "city": city,
            "recon_loss": recon_loss,
        }

    def _augment_places(self, pooled: torch.Tensor) -> torch.Tensor:
        """Detach, add the learnable table, diffuse over Delaunay adjacency."""
        pre_gcn = pooled.detach() + self.place_gamma * self.place_table.weight
        return self.place_gcn_act(
            self.place_gcn(pre_gcn, self.delaunay_edge_index, self.delaunay_edge_weight))

    # ------------------------------------------------------------------ negatives

    def _band_index(self, similarity: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Regions inside each region's similarity band, as CSR. Built once, then reused.

        `nonzero` returns row-major order, so the column indices come out already grouped by row and
        the cumulative counts are valid offsets into them.
        """
        if self._band is None:
            low, high = self.config.p2r_hard_neg_sim_range
            mask = (similarity > low) & (similarity < high)
            mask.fill_diagonal_(False)                       # never draw the positive region
            counts = mask.sum(1)
            offsets = torch.zeros(counts.numel() + 1, dtype=torch.long, device=mask.device)
            offsets[1:] = counts.cumsum(0)
            candidates = mask.nonzero(as_tuple=True)[1].to(torch.int32)
            empty = int((counts == 0).sum())
            logger.info("hard negatives: %.1f%% of region pairs in the band%s",
                        100.0 * mask.sum() / mask.numel(),
                        f" · {empty} regions with no candidate keep a uniform negative" if empty else "")
            self._band = (offsets, counts, candidates)
        return self._band

    def _sample_region_negatives(self, assignment: torch.Tensor, num_regions: int,
                                 similarity: torch.Tensor | None) -> torch.Tensor:
        """A different region per place; 25% of them drawn from the similarity band.

        Same distribution as the reference's loop — uniform over the band, positive excluded, falling
        back to the uniform draw when a region has no candidate — computed without a Python loop or a
        device sync, which is what let the reference's version be affordable only on small states.
        """
        negatives = _sample_negatives(assignment, num_regions)
        if similarity is None or not self.hard_negatives or self.config.p2r_hard_neg_prob <= 0.0:
            return negatives

        offsets, counts, candidates = self._band_index(similarity)
        device = assignment.device
        chosen = torch.rand(assignment.size(0), device=device) < self.config.p2r_hard_neg_prob
        available = counts[assignment] > 0
        usable = (chosen & available).nonzero(as_tuple=True)[0]
        if usable.numel() == 0:
            return negatives

        positives = assignment[usable]
        draw = torch.rand(usable.numel(), device=device)
        within = (draw * counts[positives]).long()           # rand is [0, 1), so within < count
        negatives[usable] = candidates[offsets[positives] + within].long()
        return negatives

    # ------------------------------------------------------------------ loss

    def loss(self, out: dict[str, torch.Tensor]) -> torch.Tensor:
        """Three boundary terms, weighted, plus the two place-axis auxiliaries."""
        c2p = _boundary_loss(out["checkin"], out["place_of_checkin"],
                             out["other_place_of_checkin"], self.weight_c2p)
        p2r = _boundary_loss(out["place"], out["region_of_place"],
                             out["other_region_of_place"], self.weight_p2r)
        r2c = _summary_loss(out["region"], out["corrupted_region"], out["city"], self.weight_r2c)

        total = (self.config.alpha_c2p * c2p
                 + self.config.alpha_p2r * p2r
                 + self.config.alpha_r2c * r2c
                 + self.config.mae_poi_lambda * out["recon_loss"]
                 + self.config.anchor_lambda * self.anchor_loss())
        return total

    def anchor_loss(self) -> torch.Tensor:
        """Keep the learnable place table near the POI2Vec geometry it was seeded from."""
        return ((self.place_table.weight - self.place_anchor) ** 2).mean()

    @torch.no_grad()
    def embeddings(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """The three exported levels, from the most recent forward."""
        return (self.checkin_embedding.detach().cpu(),
                self.place_embedding.detach().cpu(),
                self.region_embedding.detach().cpu())


# ---------------------------------------------------------------------- functions


def _corrupt(x: torch.Tensor) -> torch.Tensor:
    """Negatives are the same features under a row permutation.

    This is why adding a near-unique per-row block to the features — a place id, a region id —
    collapses the objective: the discriminator answers "shuffled?" without consulting the graph.
    """
    return x[torch.randperm(x.size(0), device=x.device)]


def _sample_negatives(assignment: torch.Tensor, num_targets: int) -> torch.Tensor:
    """One uniform index per row, excluding the true one, without rejection sampling."""
    draw = torch.randint(0, num_targets - 1, (assignment.size(0),), device=assignment.device)
    return torch.where(draw >= assignment, draw + 1, draw)


def _discriminate(a: torch.Tensor, b: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
    return torch.sigmoid(((a @ weight) * b).sum(dim=1))


def _boundary_loss(source: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor,
                   weight: torch.Tensor) -> torch.Tensor:
    pos = _discriminate(source, positive, weight)
    neg = _discriminate(source, negative, weight)
    return -torch.log(pos + EPS).mean() - torch.log(1 - neg + EPS).mean()


def _summary_loss(region: torch.Tensor, corrupted: torch.Tensor, city: torch.Tensor,
                  weight: torch.Tensor) -> torch.Tensor:
    pos = torch.sigmoid(region @ (weight @ city))
    neg = torch.sigmoid(corrupted @ (weight @ city))
    return -torch.log(pos + EPS).mean() - torch.log(1 - neg + EPS).mean()


__all__ = ["Check2HGI", "MaskedPlaceDecoder", "EPS"]
