"""
Set Transformer implementation for POI-to-region aggregation.

Based on "Set Transformer: A Framework for Attention-based Permutation-Invariant Neural Networks"
https://arxiv.org/abs/1810.00825

Modified from the original implementation: https://github.com/juho-lee/set_transformer
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class MAB(nn.Module):
    """Multihead Attention Block."""

    def __init__(self, dim_Q, dim_K, dim_V, num_heads, ln=False):
        """
        Initialize MAB.

        Args:
            dim_Q: Dimension of queries
            dim_K: Dimension of keys
            dim_V: Dimension of values
            num_heads: Number of attention heads
            ln: Whether to use layer normalization
        """
        super(MAB, self).__init__()
        self.dim_V = dim_V
        self.num_heads = num_heads
        self.fc_q = nn.Linear(dim_Q, dim_V)
        self.fc_k = nn.Linear(dim_K, dim_V)
        self.fc_v = nn.Linear(dim_K, dim_V)
        if ln:
            self.ln0 = nn.LayerNorm(dim_V)
            self.ln1 = nn.LayerNorm(dim_V)
        self.fc_o = nn.Linear(dim_V, dim_V)

    def forward(self, Q, K):
        """
        Forward pass.

        Args:
            Q: Query tensor
            K: Key tensor

        Returns:
            Output tensor
        """
        Q = self.fc_q(Q)
        K, V = self.fc_k(K), self.fc_v(K)

        dim_split = self.dim_V // self.num_heads
        Q_ = torch.cat(Q.split(dim_split, 2), 0)
        K_ = torch.cat(K.split(dim_split, 2), 0)
        V_ = torch.cat(V.split(dim_split, 2), 0)

        A = torch.softmax(Q_.bmm(K_.transpose(1, 2)) / math.sqrt(self.dim_V), 2)
        O = torch.cat((Q_ + A.bmm(V_)).split(Q.size(0), 0), 2)
        O = O if getattr(self, 'ln0', None) is None else self.ln0(O)
        O = O + F.relu(self.fc_o(O))
        O = O if getattr(self, 'ln1', None) is None else self.ln1(O)
        return O


class SAB(nn.Module):
    """Self-Attention Block."""

    def __init__(self, dim_in, dim_out, num_heads, ln=False):
        """
        Initialize SAB.

        Args:
            dim_in: Input dimension
            dim_out: Output dimension
            num_heads: Number of attention heads
            ln: Whether to use layer normalization
        """
        super(SAB, self).__init__()
        self.mab = MAB(dim_in, dim_in, dim_out, num_heads, ln=ln)

    def forward(self, X):
        """Forward pass."""
        return self.mab(X, X)


class PMA(nn.Module):
    """
    Pooling by Multihead Attention.

    Aggregates a set of POI embeddings into a fixed number of seed vectors
    (typically 1 for region aggregation).
    """

    def __init__(self, dim, num_heads, num_seeds, ln=False):
        """
        Initialize PMA.

        Args:
            dim: Embedding dimension
            num_heads: Number of attention heads
            num_seeds: Number of seed vectors (output size)
            ln: Whether to use layer normalization
        """
        super(PMA, self).__init__()
        self.S = nn.Parameter(torch.Tensor(1, num_seeds, dim))
        nn.init.xavier_uniform_(self.S)
        self.mab = MAB(dim, dim, dim, num_heads, ln=ln)

    def forward(self, X):
        """
        Aggregate POI embeddings using attention.

        Args:
            X: Input tensor [batch_size, num_pois, dim]

        Returns:
            Aggregated tensor [batch_size, num_seeds, dim]
        """
        return self.mab(self.S.repeat(X.size(0), 1, 1), X)
