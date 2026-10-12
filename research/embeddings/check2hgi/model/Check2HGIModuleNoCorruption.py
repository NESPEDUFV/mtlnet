"""
Check2HGI: Check-in Hierarchical Graph Infomax module.

4-level hierarchy: Check-in -> POI -> Region -> City
Based on HGI by Weiming Huang, Daokun Zhang, and Gengchen Mai
"""

import torch
import torch.nn as nn
from torch_geometric.nn.inits import reset, uniform


EPS = 1e-7


def corruption(x):
    """
    Corruption function to generate negative samples through random permutation.

    Args:
        x: Features [num_nodes, dim]

    Returns:
        Corrupted features (randomly permuted)
    """
    return x[torch.randperm(x.size(0))]


class Check2HGI(nn.Module):
    """
    Check-in Hierarchical Graph Infomax Module.

    This model learns hierarchical representations across four levels:
    1. Check-in level: Individual check-in events
    2. POI level: Aggregated check-ins within each POI
    3. Region level: Aggregated POIs within geographic regions
    4. City level: Aggregated regions for the entire city

    The model maximizes mutual information across these hierarchical levels.
    """

    def __init__(
        self,
        hidden_channels,
        checkin_encoder,
        checkin2poi,
        poi2region,
        region2city,
        alpha_c2p=0.4,
        alpha_p2r=0.3,
        alpha_r2c=0.3,
    ):
        """
        Initialize Check2HGI module.

        OPTIMIZED: Removed corruption parameter - now using embedding-level
        corruption instead of feature-level (single encoder pass).

        Args:
            hidden_channels: Hidden dimension
            checkin_encoder: Check-in level encoder (GCN)
            checkin2poi: Check-in to POI aggregation module
            poi2region: POI to region aggregation module (reused from HGI)
            region2city: Region to city aggregation function
            alpha_c2p: Weight for check-in to POI loss
            alpha_p2r: Weight for POI to region loss
            alpha_r2c: Weight for region to city loss
        """
        super(Check2HGI, self).__init__()

        self.hidden_channels = hidden_channels
        self.checkin_encoder = checkin_encoder
        self.checkin2poi = checkin2poi
        self.poi2region = poi2region
        self.region2city = region2city

        # Loss weights (should sum to 1)
        self.alpha_c2p = alpha_c2p
        self.alpha_p2r = alpha_p2r
        self.alpha_r2c = alpha_r2c

        # Bilinear transformation weights for discrimination at each boundary
        self.weight_c2p = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))
        self.weight_p2r = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))
        self.weight_r2c = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))

        # Store embeddings for extraction
        self.checkin_embedding = torch.tensor(0)
        self.poi_embedding = torch.tensor(0)
        self.region_embedding = torch.tensor(0)

        self.reset_parameters()

    def reset_parameters(self):
        """Reset model parameters."""
        reset(self.checkin_encoder)
        reset(self.checkin2poi)
        reset(self.poi2region)
        uniform(self.hidden_channels, self.weight_c2p)
        uniform(self.hidden_channels, self.weight_p2r)
        uniform(self.hidden_channels, self.weight_r2c)

    def forward(self, data):
        """
        Forward pass to generate check-in, POI, region, and city representations.

        OPTIMIZED: Single encoder pass with embedding-level corruption.
        Instead of running encoder twice (positive + negative), we run once
        and shuffle embeddings for negative samples.

        Args:
            data: PyTorch Geometric Data object with:
                - x: Check-in features [num_checkins, dim]
                - edge_index: Check-in graph connectivity [2, num_edges]
                - edge_weight: Edge weights [num_edges]
                - checkin_to_poi: POI assignment for each check-in [num_checkins]
                - poi_to_region: Region assignment for each POI [num_pois]
                - region_adjacency: Region adjacency graph [2, num_region_edges]
                - region_area: Area of each region [num_regions]
                - coarse_region_similarity: Region similarity matrix
                - num_pois: Number of unique POIs
                - num_regions: Number of unique regions

        Returns:
            Tuple of embeddings and negative samples for loss computation
        """
        num_pois = data.num_pois
        num_regions = data.num_regions

        # Level 1: Check-in encoding - SINGLE PASS (major optimization)
        pos_checkin_emb = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)

        # Level 2: POI encoding (aggregate check-ins to POIs)
        pos_poi_emb = self.checkin2poi(pos_checkin_emb, data.checkin_to_poi, num_pois)

        # Level 3: Region encoding (aggregate POIs to regions)
        pos_region_emb = self.poi2region(pos_poi_emb, data.poi_to_region, data.region_adjacency)

        # Negative region embeddings via shuffling (embedding-level corruption)
        # This is faster than running encoder twice with corrupted features
        neg_region_emb = pos_region_emb[torch.randperm(pos_region_emb.size(0), device=pos_region_emb.device)]

        # Level 4: City encoding (aggregate regions)
        city_emb = self.region2city(pos_region_emb, data.region_area)

        # Store for later extraction
        self.checkin_embedding = pos_checkin_emb
        self.poi_embedding = pos_poi_emb
        self.region_embedding = pos_region_emb

        # Prepare outputs for loss computation
        # Check-in to POI: each check-in vs its POI
        pos_poi_expanded = pos_poi_emb[data.checkin_to_poi]

        # Generate negative POI assignments for check-ins (vectorized)
        neg_poi_indices = self._sample_negative_indices(
            data.checkin_to_poi, num_pois, data.x.device
        )
        neg_poi_expanded = pos_poi_emb[neg_poi_indices]

        # POI to Region: each POI vs its region
        pos_region_expanded = pos_region_emb[data.poi_to_region]

        # Generate negative region assignments for POIs (vectorized, no loop)
        neg_region_indices = self._sample_negative_indices_fast(
            data.poi_to_region, num_regions, data.x.device
        )
        neg_region_expanded = pos_region_emb[neg_region_indices]

        return (
            pos_checkin_emb, pos_poi_expanded, neg_poi_expanded,
            pos_poi_emb, pos_region_expanded, neg_region_expanded,
            pos_region_emb, neg_region_emb, city_emb
        )

    def _sample_negative_indices(self, assignment, num_targets, device):
        """Sample negative indices (different from positive assignment) - VECTORIZED."""
        batch_size = assignment.size(0)

        # Generate random indices in [0, num_targets-1]
        neg_indices = torch.randint(0, num_targets - 1, (batch_size,), device=device)

        # Shift indices >= assignment to avoid collision
        # If neg >= pos, then neg = neg + 1 (skips the positive index)
        neg_indices = torch.where(neg_indices >= assignment, neg_indices + 1, neg_indices)

        return neg_indices

    def _sample_negative_indices_fast(self, assignment, num_targets, device):
        """
        Fast vectorized negative sampling - no Python loops.

        OPTIMIZED: Removed hard negative sampling loop for ~1.1x speedup.
        Random negatives are sufficient and O(1) time complexity.
        """
        batch_size = assignment.size(0)

        # Pure vectorized random negative (different from positive)
        neg_indices = torch.randint(0, num_targets - 1, (batch_size,), device=device)
        neg_indices = torch.where(neg_indices >= assignment, neg_indices + 1, neg_indices)

        return neg_indices

    def discriminate(self, emb1, emb2, weight, sigmoid=True):
        """
        Bilinear discrimination between two embedding sets.

        Args:
            emb1: First embeddings [N, D]
            emb2: Second embeddings [N, D] (aligned with emb1)
            weight: Bilinear weight matrix [D, D]
            sigmoid: Whether to apply sigmoid

        Returns:
            Discrimination scores [N]
        """
        projected = torch.matmul(emb1, weight)
        scores = (projected * emb2).sum(dim=1)
        return torch.sigmoid(scores) if sigmoid else scores

    def discriminate_global(self, emb, summary, weight, sigmoid=True):
        """
        Bilinear discrimination between embeddings and global summary.

        Args:
            emb: Embeddings [N, D]
            summary: Global summary [D]
            weight: Bilinear weight matrix [D, D]
            sigmoid: Whether to apply sigmoid

        Returns:
            Discrimination scores [N]
        """
        value = torch.matmul(emb, torch.matmul(weight, summary))
        return torch.sigmoid(value) if sigmoid else value

    def loss(self, pos_checkin, pos_poi_exp, neg_poi_exp,
             pos_poi, pos_region_exp, neg_region_exp,
             pos_region, neg_region, city):
        """
        Compute the hierarchical mutual information maximization objective.

        3 boundary losses:
        1. Check-in ↔ POI
        2. POI ↔ Region
        3. Region ↔ City
        """
        # Loss 1: Check-in to POI
        pos_c2p = self.discriminate(pos_checkin, pos_poi_exp, self.weight_c2p)
        neg_c2p = self.discriminate(pos_checkin, neg_poi_exp, self.weight_c2p)
        loss_c2p = -torch.log(pos_c2p + EPS).mean() - torch.log(1 - neg_c2p + EPS).mean()

        # Loss 2: POI to Region
        pos_p2r = self.discriminate(pos_poi, pos_region_exp, self.weight_p2r)
        neg_p2r = self.discriminate(pos_poi, neg_region_exp, self.weight_p2r)
        loss_p2r = -torch.log(pos_p2r + EPS).mean() - torch.log(1 - neg_p2r + EPS).mean()

        # Loss 3: Region to City
        pos_r2c = self.discriminate_global(pos_region, city, self.weight_r2c)
        neg_r2c = self.discriminate_global(neg_region, city, self.weight_r2c)
        loss_r2c = -torch.log(pos_r2c + EPS).mean() - torch.log(1 - neg_r2c + EPS).mean()

        # Combined loss
        total_loss = (
            self.alpha_c2p * loss_c2p +
            self.alpha_p2r * loss_p2r +
            self.alpha_r2c * loss_r2c
        )

        return total_loss

    def get_embeddings(self):
        """
        Get the current embeddings at all levels.

        Returns:
            Tuple of (checkin_embedding, poi_embedding, region_embedding)
        """
        return (
            self.checkin_embedding.clone().cpu().detach(),
            self.poi_embedding.clone().cpu().detach(),
            self.region_embedding.clone().cpu().detach()
        )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.hidden_channels})'
