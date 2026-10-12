"""POI-level encoder for HGI using Graph Convolutional Networks."""

import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv


class POIEncoder(nn.Module):
    """
    POI-level encoder using Graph Convolutional Network.

    This encoder processes POI features and spatial graph structure to create
    POI-level representations.
    """

    def __init__(self, in_channels, hidden_channels):
        """
        Initialize POI encoder.

        Args:
            in_channels: Input feature dimension
            hidden_channels: Hidden dimension
        """
        super(POIEncoder, self).__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels

        # Graph convolutional layer
        self.conv = GCNConv(in_channels, hidden_channels, cached=True, bias=True)

        # PReLU activation (channelwise — matches canonical RightBank/HGI)
        self.prelu = nn.PReLU(hidden_channels)

    def forward(self, x, edge_index, edge_weight):
        """
        Forward pass through POI encoder.

        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            edge_weight: Edge weights [num_edges]

        Returns:
            POI embeddings [num_nodes, hidden_channels]
        """
        # Apply graph convolution
        x = self.conv(x, edge_index, edge_weight)

        # Apply PReLU activation
        x = self.prelu(x)

        return x

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'in={self.in_channels}, '
                f'hidden={self.hidden_channels})')
