"""Check-in level encoder for Check2HGI using Graph Convolutional Networks."""

import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv


class CheckinEncoder(nn.Module):
    """
    Check-in level encoder using multi-layer Graph Convolutional Network.

    This encoder processes check-in features and user-sequence/POI graph structure
    to create check-in level representations.
    """

    def __init__(self, in_channels, hidden_channels, num_layers=2, dropout=0.0):
        """
        Initialize check-in encoder.

        Args:
            in_channels: Input feature dimension (category one-hot + temporal features)
            hidden_channels: Hidden/output dimension
            num_layers: Number of GCN layers
            dropout: Dropout probability between layers
        """
        super(CheckinEncoder, self).__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.num_layers = num_layers
        self.dropout = dropout

        # Build GCN layers
        self.convs = nn.ModuleList()
        self.convs.append(GCNConv(in_channels, hidden_channels, cached=False, bias=True))
        for _ in range(num_layers - 1):
            self.convs.append(GCNConv(hidden_channels, hidden_channels, cached=False, bias=True))

        # Activation and normalization
        self.act = nn.PReLU()
        self.dropout_layer = nn.Dropout(p=dropout) if dropout > 0 else nn.Identity()

    def forward(self, x, edge_index, edge_weight=None, **kwargs):
        """
        Forward pass through check-in encoder.

        Args:
            x: Node features [num_checkins, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            edge_weight: Optional edge weights [num_edges]
            **kwargs: Ignored. Absorbs ``edge_type`` plumbed by Check2HGI for
                R-GCN compatibility (T3.3); the canonical GCN does not use it.

        Returns:
            Check-in embeddings [num_checkins, hidden_channels]
        """
        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index, edge_weight)
            if i < len(self.convs) - 1:  # No activation/dropout on last layer
                x = self.act(x)
                x = self.dropout_layer(x)

        return x

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'in={self.in_channels}, '
                f'hidden={self.hidden_channels}, '
                f'layers={self.num_layers})')
