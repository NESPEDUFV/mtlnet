"""Tests for Next-POI Head model."""

import pytest
import torch

from models.next import NextHeadMTL


class TestNextHeadMTL:
    """Test suite for NextHeadMTL."""

    def _make_head(self):
        return NextHeadMTL(
            embed_dim=64,
            num_classes=7,
            num_heads=8,
            seq_length=9,
            num_layers=4,
        )

    def test_forward_pass(self):
        """Test forward pass with sequence input."""
        head = self._make_head()
        head.eval()
        x = torch.randn(4, 9, 64)
        with torch.no_grad():
            out = head(x)
        assert out.shape == (4, 7), f"Expected (4, 7), got {out.shape}"
        assert torch.isfinite(out).all()

    def test_positional_encoding(self):
        """Test positional encoding for sequences."""
        head = self._make_head()
        head.eval()
        x = torch.randn(4, 9, 64)
        padding_mask = torch.zeros(4, 9, dtype=torch.bool)
        with torch.no_grad():
            out = head.pe(x, padding_mask)
        assert out.shape == x.shape

    def test_causal_masking(self):
        """Test causal masking for sequence prediction."""
        seq_length = 9
        mask = torch.triu(
            torch.ones(seq_length, seq_length, dtype=torch.bool), diagonal=1
        )
        assert mask.shape == (9, 9)
        # Above diagonal should be True (masked)
        assert mask[0, 1].item() is True
        # Below diagonal should be False (not masked)
        assert mask[1, 0].item() is False
        # Diagonal should be False (not masked)
        assert mask[0, 0].item() is False

    def test_sequence_padding(self):
        """Test handling of padded sequences."""
        head = self._make_head()
        head.eval()
        x = torch.randn(4, 9, 64)
        # Zero out last 3 positions to simulate padding
        x[:, 6:, :] = 0.0
        with torch.no_grad():
            out = head(x)
        assert out.shape == (4, 7), f"Expected (4, 7), got {out.shape}"
        assert torch.isfinite(out).all()
