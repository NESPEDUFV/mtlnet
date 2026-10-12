"""The three encoders of the substrate hierarchy: check-in → POI → region.

Level 1 is a graph convolution over the check-in graph. Levels 2 and 3 are **the same operation**:
pool a ragged set of children into each parent by attention against a single learned seed vector.
The reference implements that operation twice, in two files, under two different names, with two
different sets of parameter names — `Checkin2POI` in this engine and `POI2Region` borrowed from HGI,
where it is a hand-inlined rewrite of a Set-Transformer `PMA` whose comments still argue with
themselves about what the original did. Here it is written once (`SeedAttentionPool`) and used twice.

The two levels differ only in what wraps the pooling, and both differences are load-bearing:

- POI level: a **scalar** PReLU.
- Region level: a graph convolution over region adjacency, then a **channel-wise** PReLU.

Both end in `nan_to_num`, kept because it is part of the reference forward.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.utils import scatter
from torch_geometric.utils import softmax as segment_softmax


class ResidualLNEncoder(nn.Module):
    """The `resln` check-in encoder: pre-LN graph convolutions, residual from layer 1 on.

    The first layer takes no residual because it changes width. Layers 1..n-1 normalise, convolve,
    and add — the activation is applied inside the branch and skipped on the last layer, which is
    what leaves the output unsquashed for the bilinear discriminators downstream.
    """

    def __init__(self, in_channels: int, hidden_channels: int,
                 num_layers: int = 2, dropout: float = 0.1) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.num_layers = num_layers

        self.convs = nn.ModuleList([GCNConv(in_channels, hidden_channels, cached=False, bias=True)])
        self.norms = nn.ModuleList([nn.LayerNorm(hidden_channels)])
        for _ in range(num_layers - 1):
            self.convs.append(GCNConv(hidden_channels, hidden_channels, cached=False, bias=True))
            self.norms.append(nn.LayerNorm(hidden_channels))

        self.act = nn.PReLU()
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_weight: torch.Tensor | None = None) -> torch.Tensor:
        x = self.dropout(self.act(self.norms[0](self.convs[0](x, edge_index, edge_weight))))
        for i in range(1, self.num_layers):
            h = self.convs[i](self.norms[i](x), edge_index, edge_weight)
            if i < self.num_layers - 1:
                h = self.dropout(self.act(h))
            x = x + h
        return x

    def extra_repr(self) -> str:
        return f"in={self.in_channels}, hidden={self.hidden_channels}, layers={self.num_layers}"


class SeedAttentionPool(nn.Module):
    """Pool children into parents by attention against one learned seed, shared by all parents.

    Because the query is the same vector everywhere, the attention reduces to a dot product per
    child followed by a softmax **segmented by parent** — no dense [parents, children] matrix is ever
    built. That is what makes the operation affordable at 3.8M check-ins, and it is the one place
    where the reference's inlined rewrite of `PMA` was right to abandon the original.

    Scaling is by `sqrt(hidden)`, not `sqrt(hidden / heads)` — the Set-Transformer convention, which
    the reference inherited and which is kept here for equivalence.
    """

    def __init__(self, hidden_channels: int, num_heads: int) -> None:
        super().__init__()
        if hidden_channels % num_heads:
            raise ValueError(f"hidden {hidden_channels} not divisible by {num_heads} heads")
        self.hidden_channels = hidden_channels
        self.num_heads = num_heads
        self.scale = math.sqrt(hidden_channels)

        self.fc_q = nn.Linear(hidden_channels, hidden_channels)
        self.fc_k = nn.Linear(hidden_channels, hidden_channels)
        self.fc_v = nn.Linear(hidden_channels, hidden_channels)
        self.fc_o = nn.Linear(hidden_channels, hidden_channels)

        self.seed = nn.Parameter(torch.empty(1, hidden_channels))
        nn.init.xavier_uniform_(self.seed)

    def forward(self, x: torch.Tensor, parent: torch.Tensor, num_parents: int) -> torch.Tensor:
        heads, split = self.num_heads, self.hidden_channels // self.num_heads
        query = self.fc_q(self.seed).view(1, heads, split)

        scores = (self.fc_k(x).view(-1, heads, split) * query).sum(-1) / self.scale
        alpha = segment_softmax(scores, parent, num_nodes=num_parents)

        weighted = self.fc_v(x).view(-1, heads, split) * alpha.unsqueeze(-1)
        pooled = scatter(weighted, parent, dim=0, dim_size=num_parents, reduce="add")
        pooled = pooled.view(num_parents, self.hidden_channels)

        out = query.view(1, self.hidden_channels) + pooled  # residual against the broadcast query
        return out + F.relu(self.fc_o(out))

    def extra_repr(self) -> str:
        return f"hidden={self.hidden_channels}, heads={self.num_heads}"


class Checkin2POI(nn.Module):
    """Level 2: the visits of a place, pooled into the place."""

    def __init__(self, hidden_channels: int, num_heads: int = 4) -> None:
        super().__init__()
        self.pool = SeedAttentionPool(hidden_channels, num_heads)
        self.prelu = nn.PReLU()

    def forward(self, x: torch.Tensor, checkin_to_poi: torch.Tensor,
                num_pois: int) -> torch.Tensor:
        out = self.prelu(self.pool(x, checkin_to_poi, num_pois))
        return torch.nan_to_num(out, nan=0.0)


class POI2Region(nn.Module):
    """Level 3: the places of a region, pooled into the region, then diffused over adjacency.

    `num_regions` is required. The reference derives it as `zone.max() + 1`, which silently drops
    trailing regions that contain no POI and would then mismatch `region_area` in the city
    aggregation. On every state built so far the two agree, so this is a trap disarmed rather than a
    defect observed — but a count that must equal `region_area`'s length should come from the data,
    not from a maximum.
    """

    def __init__(self, hidden_channels: int, num_heads: int = 4) -> None:
        super().__init__()
        self.pool = SeedAttentionPool(hidden_channels, num_heads)
        # cached=True is safe only because training is full-batch on a fixed adjacency.
        self.conv = GCNConv(hidden_channels, hidden_channels, cached=True, bias=True)
        self.prelu = nn.PReLU(hidden_channels)

    def forward(self, x: torch.Tensor, poi_to_region: torch.Tensor,
                region_adjacency: torch.Tensor, num_regions: int) -> torch.Tensor:
        pooled = self.pool(x, poi_to_region, num_regions)
        out = self.prelu(self.conv(pooled, region_adjacency))
        return torch.nan_to_num(out, nan=0.0)


def region2city(region_emb: torch.Tensor, region_area: torch.Tensor) -> torch.Tensor:
    """Level 4: an area-weighted sum of regions, squashed. The whole city is one vector."""
    return torch.sigmoid((region_emb.transpose(0, 1) * region_area).sum(dim=1))


__all__ = ["ResidualLNEncoder", "SeedAttentionPool", "Checkin2POI", "POI2Region", "region2city"]
