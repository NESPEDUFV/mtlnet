"""Positional encoding components shared across model heads.

Extracted from src/model/next/next_head.py in Phase 4a.
"""

import math

import torch
import torch.nn as nn


class PositionalEncoding(nn.Module):
    def __init__(self, embed_dim, max_seq_length=5000, dropout=0.1):
        """
        Args:
            embed_dim: The dimensionality of the embedding space.
            max_seq_length: The maximum sequence length to handle.
            dropout: Dropout rate applied to positional encodings.
        """
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Precompute the positional encodings once
        pe = torch.zeros(max_seq_length, embed_dim)
        pos = torch.arange(0, max_seq_length, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, embed_dim, 2).float() * (-math.log(10000.0) / embed_dim)
        )

        pe[:, 0::2] = torch.sin(pos * div_term)
        pe[:, 1::2] = torch.cos(pos * div_term)
        pe = pe.unsqueeze(0)  # shape (1, max_seq_length, embed_dim)

        self.register_buffer('positional_encoding', pe)
        self.eps = 1e-12

    def forward(self, x, padding_mask=None):
        """
        x: (batch_size, seq_length, embed_dim)
        padding_mask: (batch_size, seq_length), True for padding positions
        """
        seq_length = x.size(1)
        pos_enc = self.positional_encoding[:, :seq_length, :]

        if padding_mask is not None:
            # zero out both x and pos_enc where padding_mask == True
            mask = (~padding_mask).unsqueeze(-1).float() + self.eps
            x = x * mask
            pos_enc = pos_enc * mask

        x = x + pos_enc
        return self.dropout(x)
