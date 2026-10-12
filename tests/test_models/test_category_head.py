"""Tests for Category Head model."""

import pytest
import torch
import torch.nn as nn

from models.category import CategoryHeadEnsemble, CategoryHeadTransformer


class TestCategoryHeadEnsemble:
    """Test suite for CategoryHeadEnsemble."""

    def test_forward_pass(self):
        """Test forward pass with embedding input."""
        head = CategoryHeadEnsemble(input_dim=64, hidden_dim=128, num_paths=3, num_classes=7)
        head.eval()
        x = torch.randn(8, 64)
        with torch.no_grad():
            out = head(x)
        assert out.shape == (8, 7)
        assert torch.isfinite(out).all()

    def test_multi_path_ensemble(self):
        """Test multi-path ensemble architecture."""
        head = CategoryHeadEnsemble(input_dim=64, hidden_dim=128, num_paths=3, num_classes=7)
        head.eval()
        B = 4
        x = torch.randn(B, 64)
        # Each path should produce the same output shape
        with torch.no_grad():
            shapes = [path(x).shape for path in head.paths]
            assert all(s == shapes[0] for s in shapes), f"Path output shapes differ: {shapes}"
        # Combined via concat of 3 paths -> (B, hidden_dim * 3)
        assert len(head.paths) == 3

    def test_output_shape(self):
        """Test output shape matches number of categories."""
        head_eval = lambda nc: CategoryHeadEnsemble(input_dim=64, hidden_dim=128, num_paths=3, num_classes=nc)
        x = torch.randn(4, 64)
        for num_classes in [5, 7, 10]:
            head = head_eval(num_classes)
            head.eval()
            with torch.no_grad():
                out = head(x)
            assert out.shape == (4, num_classes), f"Expected (4, {num_classes}), got {out.shape}"


class TestCategoryHeadEnhanced:
    """Test suite for enhanced category head with transformer."""

    def test_transformer_integration(self):
        """Test transformer encoder integration."""
        head = CategoryHeadTransformer(
            input_dim=64,
            num_tokens=4,
            token_dim=16,
            num_layers=2,
            num_heads=8,
            num_classes=7,
        )
        head.eval()
        x = torch.randn(8, 64)
        with torch.no_grad():
            out = head(x)
        assert out.shape == (8, 7), f"Expected (8, 7), got {out.shape}"
        assert torch.isfinite(out).all()
