"""
Hierarchical Graph Infomax (HGI) module.

Based on the implementation by Weiming Huang, Daokun Zhang, and Gengchen Mai
"""

import random
import torch
import torch.nn as nn
from torch_geometric.nn.inits import reset, uniform

from embeddings.hgi.model.POIEncoder import POIEncoder
from embeddings.hgi.model.RegionEncoder import POI2Region


EPS = 1e-7


def corruption(x):
    """
    Corruption function to generate negative POIs through random permutation.

    Args:
        x: POI features [num_pois, dim]

    Returns:
        Corrupted features (randomly permuted)
    """
    return x[torch.randperm(x.size(0))]


class HierarchicalGraphInfomax(nn.Module):
    """
    The Hierarchical Graph Infomax Module for learning region representations.

    This model learns hierarchical representations across three levels:
    1. POI level: Individual points of interest
    2. Region level: Aggregated POIs within geographic regions
    3. City level: Aggregated regions for the entire city

    The model maximizes mutual information across these hierarchical levels.
    """

    def __init__(
        self,
        hidden_channels,
        poi_encoder,
        poi2region,
        region2city,
        corruption,
        alpha,
        hard_neg_prob=0.25,
    ):
        """
        Initialize HGI module.

        Args:
            hidden_channels: Hidden dimension
            poi_encoder: POI-level encoder
            poi2region: POI-to-region aggregation module
            region2city: Region-to-city aggregation function
            corruption: Corruption function for negative sampling
            alpha: Balance parameter between POI-region and region-city loss (0 to 1)
            hard_neg_prob: Probability of drawing a hard negative from the
                coarse_region_similarity-based candidate pool. Default 0.25
                matches the reference implementation. Set to 0.0 for purely
                uniform random negatives (leakage ablation arm B).
        """
        super(HierarchicalGraphInfomax, self).__init__()

        self.hidden_channels = hidden_channels
        self.poi_encoder = poi_encoder
        self.poi2region = poi2region
        self.region2city = region2city
        self.corruption = corruption
        self.alpha = alpha
        self.hard_neg_prob = hard_neg_prob

        # Bilinear transformation weights for discrimination
        self.weight_poi2region = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))
        self.weight_region2city = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))

        # Store embeddings for extraction
        self.region_embedding = torch.tensor(0)
        self.poi_embedding = torch.tensor(0)

        self.reset_parameters()

    def reset_parameters(self):
        """Reset model parameters."""
        reset(self.poi_encoder)
        reset(self.poi2region)
        reset(self.region2city)
        uniform(self.hidden_channels, self.weight_poi2region)
        uniform(self.hidden_channels, self.weight_region2city)

    def forward(self, data):
        """
        Forward pass to generate POI, region, and city representations.

        Returns a 7-tuple matching the original reference semantics:
            (pos_poi_idx, pos_target_region, neg_poi_idx, neg_target_region,
             pos_poi_emb, region_emb, neg_region_emb, city_emb)

        The negative POI-region pairs follow the ORIGINAL formulation:
            For each region R, sample another region R' (with hard-negative
            strategy), then take ALL POIs from R' and pair them with R's
            embedding. This is equivalent to the loop in reference hgi.py
            lines 83-112.
        """
        # POI-level encoding (positive samples)
        pos_poi_emb = self.poi_encoder(data.x, data.edge_index, data.edge_weight)

        # POI-level encoding (negative samples with corrupted features)
        cor_x = self.corruption(data.x)
        neg_poi_emb = self.poi_encoder(cor_x, data.edge_index, data.edge_weight)

        # Region-level encoding (positive)
        region_emb = self.poi2region(pos_poi_emb, data.region_id, data.region_adjacency)

        # Store for later extraction
        self.poi_embedding = pos_poi_emb
        self.region_embedding = region_emb

        # Region-level encoding (negative, from corrupted POIs)
        neg_region_emb = self.poi2region(neg_poi_emb, data.region_id, data.region_adjacency)

        # City-level encoding (area-weighted aggregation of regions)
        city_emb = self.region2city(region_emb, data.region_area)

        # ----- Hard negative sampling (matches reference hgi.py:86-107) -----
        # Original behavior: 25% probability for hard negatives (similarity 0.6-0.8)
        #                    75% probability for random negatives
        #
        # We keep the per-region Python loop here because each iteration consumes
        # exactly two calls into Python's `random` module (one random.random() and
        # one random.choice()), in a deterministic order. The reference equivalence
        # tests in tests/test_embeddings/test_hgi_reference_equivalence.py rely on
        # this exact RNG consumption pattern to compare loss values bit-for-bit.
        # The expensive parts of the loop (similarity slicing, candidate listing)
        # are PRECOMPUTED ONCE per data object and cached on `data` itself.
        num_regions = int(torch.max(data.region_id).item()) + 1
        hard_neg_prob = self.hard_neg_prob
        device = data.x.device

        if not hasattr(data, "_hgi_neg_cache") or data._hgi_neg_cache.get("R") != num_regions:
            # First call (or num_regions changed): build cached lookup tables.
            #   hard_candidates_per_region: list[list[int]] of foreign regions
            #     with coarse_region_similarity in (0.6, 0.8), excluding self.
            #     If empty, the per-region loop falls back to all_other.
            #   all_other_per_region: list[list[int]] of every other region.
            #   region_id_cpu / sort_idx / region_offsets: enable the fully
            #     vectorized "for each region, gather its POIs" build below.
            sim_full = data.coarse_region_similarity
            hard_mask = (sim_full > 0.6) & (sim_full < 0.8)
            # Drop self from candidate sets via diagonal mask.
            eye = torch.eye(num_regions, dtype=torch.bool, device=device)
            hard_mask = hard_mask & ~eye

            # CPU lists are what random.choice expects; convert once.
            hard_lists = [row.nonzero(as_tuple=True)[0].tolist() for row in hard_mask.cpu()]
            all_regions_per_region = [
                [j for j in range(num_regions) if j != r] for r in range(num_regions)
            ]

            # POI grouping by region: sort POIs by region_id once, store
            # offsets so any region's POI block is sort_idx[off:off+size].
            region_id_cpu = data.region_id.cpu()
            sort_idx = torch.argsort(region_id_cpu, stable=True)
            sizes = torch.bincount(region_id_cpu, minlength=num_regions)
            region_offsets = torch.zeros(num_regions + 1, dtype=torch.long)
            region_offsets[1:] = sizes.cumsum(0)

            data._hgi_neg_cache = {
                "R": num_regions,
                "hard_lists": hard_lists,
                "all_regions_per_region": all_regions_per_region,
                "sort_idx": sort_idx.to(device),
                "sizes": sizes.to(device),
                "region_offsets": region_offsets.to(device),
            }

        cache = data._hgi_neg_cache
        hard_lists = cache["hard_lists"]
        all_regions_per_region = cache["all_regions_per_region"]
        sort_idx = cache["sort_idx"]
        sizes = cache["sizes"]
        region_offsets = cache["region_offsets"]

        # Pick negative region per region. Build as a Python list, then
        # tensorize once at the end (avoids 1108 individual writes through
        # tensor indexing which were ~1108 dispatches under the old code).
        # Each iteration consumes exactly one random.random() and one
        # random.choice() call so the RNG sequence matches the reference.
        # `candidates` falls back from hard_lists to all_regions_per_region
        # whenever the hard candidate set is empty for that region.
        neg_region_list = [0] * num_regions
        for region in range(num_regions):
            if random.random() < hard_neg_prob:
                candidates = hard_lists[region] or all_regions_per_region[region]
            else:
                candidates = all_regions_per_region[region]
            neg_region_list[region] = random.choice(candidates)
        neg_region_indices = torch.as_tensor(
            neg_region_list, dtype=torch.long, device=device
        )

        # ----- Build (poi_idx, target_region) pairs -----
        # Positive pairs: every POI i scored against region region_id[i]
        # Negative pairs: for every region R, ALL POIs from neg_R scored against R
        #
        # Vectorized construction:
        #   neg_sizes[R]      = number of POIs in the negative region picked for R
        #   neg_target_region = repeat_interleave(arange(R), neg_sizes)
        #   src_pos[i]        = region_offsets[neg_R] + (i - cumulative_start)
        #   neg_poi_idx       = sort_idx[src_pos]
        # The loop in the previous implementation did N×R==13M region_id
        # comparisons per epoch. The vectorized form is O(num_regions + neg_total).
        N = pos_poi_emb.size(0)
        pos_poi_idx = torch.arange(N, device=device)
        pos_target_region = data.region_id

        neg_sizes = sizes[neg_region_indices]                  # [R]
        neg_total = int(neg_sizes.sum().item())

        if neg_total == 0:
            neg_poi_idx = torch.empty(0, dtype=torch.long, device=device)
            neg_target_region = torch.empty(0, dtype=torch.long, device=device)
        else:
            arange_R = torch.arange(num_regions, device=device)
            neg_target_region = torch.repeat_interleave(arange_R, neg_sizes)
            # Output starts: cumulative offsets within neg_poi_idx for each R
            out_starts = torch.zeros(num_regions, dtype=torch.long, device=device)
            out_starts[1:] = neg_sizes[:-1].cumsum(0)
            # within[i] = i - out_starts[neg_target_region[i]]
            within = torch.arange(neg_total, device=device) - out_starts[neg_target_region]
            # Source positions in sort_idx
            src_starts = region_offsets[neg_region_indices]    # [R]
            src_pos = src_starts[neg_target_region] + within   # [neg_total]
            neg_poi_idx = sort_idx[src_pos]                    # [neg_total]

        return (
            pos_poi_idx, pos_target_region,
            neg_poi_idx, neg_target_region,
            pos_poi_emb, region_emb, neg_region_emb, city_emb,
        )

    def discriminate_poi2region(self, poi_emb, region_emb, sigmoid=True):
        """
        Vectorized bilinear discriminator: score_i = poi_i @ W @ region_i.

        Args:
            poi_emb:    [N, D] POI embeddings
            region_emb: [N, D] Region embeddings (one per POI, aligned)
        """
        projected_poi = torch.matmul(poi_emb, self.weight_poi2region)  # [N, D]
        scores = (projected_poi * region_emb).sum(dim=1)               # [N]
        return torch.sigmoid(scores) if sigmoid else scores

    def discriminate_region2city(self, region_emb, city_emb, sigmoid=True):
        """Bilinear: region @ W @ city  →  [num_regions]."""
        value = torch.matmul(region_emb, torch.matmul(self.weight_region2city, city_emb))
        return torch.sigmoid(value) if sigmoid else value

    def loss(
        self,
        pos_poi_idx, pos_target_region,
        neg_poi_idx, neg_target_region,
        pos_poi_emb, region_emb, neg_region_emb, city_emb,
    ):
        """
        Hierarchical mutual information maximization objective.

        Matches the original reference formulation exactly:
            pos_loss = -log(σ(POI_i @ W @ region[region_id[i]]))   for each POI
            neg_loss = -log(1 - σ(POI_j @ W @ region[R]))
                       for each (R, j) where region_id[j] == neg_R[R]
        """
        # Gather embeddings for the pairs
        pos_pois = pos_poi_emb[pos_poi_idx]              # [N, D]
        pos_regs = region_emb[pos_target_region]         # [N, D]
        neg_pois = pos_poi_emb[neg_poi_idx]              # [M, D]
        neg_regs = region_emb[neg_target_region]         # [M, D]

        # POI-to-Region contrastive loss
        pos_scores = self.discriminate_poi2region(pos_pois, pos_regs, sigmoid=True)
        pos_loss_region = -torch.log(pos_scores + EPS).mean()

        neg_scores = self.discriminate_poi2region(neg_pois, neg_regs, sigmoid=True)
        neg_loss_region = -torch.log(1 - neg_scores + EPS).mean()

        loss_poi2region = pos_loss_region + neg_loss_region

        # Region-to-City contrastive loss
        pos_loss_city = -torch.log(
            self.discriminate_region2city(region_emb, city_emb, sigmoid=True) + EPS
        ).mean()

        neg_loss_city = -torch.log(
            1 - self.discriminate_region2city(neg_region_emb, city_emb, sigmoid=True) + EPS
        ).mean()

        loss_region2city = pos_loss_city + neg_loss_city

        # Combined loss with alpha balancing
        return loss_poi2region * self.alpha + loss_region2city * (1 - self.alpha)

    def get_region_emb(self):
        """
        Get the current region and POI embeddings.

        Returns:
            Tuple of (region_embedding, poi_embedding) on CPU
        """
        return (
            self.region_embedding.clone().cpu().detach(),
            self.poi_embedding.clone().cpu().detach()
        )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.hidden_channels})'
