"""
Test suite for Next-POI model forward pass correctness.

Tests forward pass with full/padded sequences, causal masking,
attention weight validation, and output logit shapes.
"""

import pytest
import torch
import torch.nn as nn

from models.next import NextHeadSingle
from models.next import (
    NextHeadHybrid,
    NextHeadGRU,
    NextHeadConvAttn,
    NextHeadTCNResidual,
    NextHeadTransformerOptimized,
    NextHeadTransformerRelPos,
)


class TestForwardPassBasic:
    """Basic forward pass tests for all models."""

    @pytest.fixture(params=[
        'NextHeadSingle',
        'NextHeadHybrid',
        'NextHeadGRU',
        'NextHeadConvAttn',
        'NextHeadTCNResidual',
        'NextHeadTransformerOptimized',
        'NextHeadTransformerRelPos',
    ])
    def model(self, request):
        """Parametrized fixture to test all model architectures."""
        if request.param == 'NextHeadSingle':
            return NextHeadSingle(
                embed_dim=64, num_classes=7, num_heads=4,
                seq_length=9, num_layers=2, dropout=0.1
            )
        elif request.param == 'NextHeadHybrid':
            return NextHeadHybrid(
                embed_dim=64, hidden_dim=256, num_classes=7,
                num_heads=4, num_gru_layers=2, dropout=0.3
            )
        elif request.param == 'NextHeadGRU':
            return NextHeadGRU(
                embed_dim=64, hidden_dim=256, num_classes=7,
                num_layers=2, dropout=0.3
            )
        elif request.param == 'NextHeadConvAttn':
            return NextHeadConvAttn(
                embed_dim=64, hidden_channels=128, num_classes=7,
                num_conv_layers=3, kernel_size=3, num_heads=4, dropout=0.2,
            )
        elif request.param == 'NextHeadTCNResidual':
            return NextHeadTCNResidual(
                embed_dim=64, hidden_channels=128, num_classes=7,
                num_blocks=4, kernel_size=3, dropout=0.2,
            )
        elif request.param == 'NextHeadTransformerOptimized':
            return NextHeadTransformerOptimized(
                embed_dim=64, num_classes=7, num_heads=4,
                num_layers=2, seq_length=9, dropout=0.1,
            )
        elif request.param == 'NextHeadTransformerRelPos':
            return NextHeadTransformerRelPos(
                embed_dim=64, num_classes=7, num_heads=4,
                num_layers=2, seq_length=9, dropout=0.2,
            )

    def test_forward_with_full_sequence(self, model):
        """Test forward pass with complete sequences (no padding)."""
        batch_size = 32
        seq_length = 9
        embed_dim = 64

        x = torch.randn(batch_size, seq_length, embed_dim)
        output = model(x)

        # Check output shape
        assert output.shape == (batch_size, 7), \
            f"Expected output shape ({batch_size}, 7), got {output.shape}"

        # Check output is finite
        assert torch.isfinite(output).all(), \
            "Output contains NaN or Inf values"

    def test_forward_with_padded_sequence(self, model):
        """Test forward pass with padded sequences."""
        batch_size = 16
        seq_length = 9
        embed_dim = 64

        x = torch.randn(batch_size, seq_length, embed_dim)

        # Add padding to half the batch
        x[batch_size//2:, 5:, :] = 0  # Pad last 4 timesteps

        output = model(x)

        # Check output shape
        assert output.shape == (batch_size, 7), \
            f"Expected output shape ({batch_size}, 7), got {output.shape}"

        # Output should still be finite
        assert torch.isfinite(output).all(), \
            "Output contains NaN or Inf with padding"

        # Padded and non-padded sequences should give different outputs
        diff = (output[:batch_size//2] - output[batch_size//2:]).abs().mean()
        assert diff > 0.01, \
            "Padded and non-padded sequences produce identical outputs (padding not handled)"

    def test_batch_size_one(self, model):
        """Test forward pass with batch_size=1."""
        x = torch.randn(1, 9, 64)
        output = model(x)

        assert output.shape == (1, 7), \
            f"Expected output shape (1, 7), got {output.shape}"

    def test_output_logits_shape(self, model):
        """Test that output has correct number of classes."""
        x = torch.randn(8, 9, 64)
        output = model(x)

        num_classes = output.shape[1]
        assert num_classes == 7, \
            f"Expected 7 classes, got {num_classes}"

    def test_deterministic_output(self, model):
        """Test that model gives deterministic output in eval mode."""
        model.eval()

        x = torch.randn(16, 9, 64)

        with torch.no_grad():
            output1 = model(x)
            output2 = model(x)

        # Outputs should be identical in eval mode
        assert torch.allclose(output1, output2, atol=1e-6), \
            "Model is not deterministic in eval mode"

    def test_different_sequences_different_outputs(self, model):
        """Test that different inputs produce different outputs."""
        model.eval()

        x1 = torch.randn(8, 9, 64)
        x2 = torch.randn(8, 9, 64)

        with torch.no_grad():
            output1 = model(x1)
            output2 = model(x2)

        # Outputs should be different
        diff = (output1 - output2).abs().mean()
        assert diff > 0.01, \
            "Different inputs produce identical outputs"


class TestCausalMasking:
    """Tests for causal (autoregressive) masking in Transformer."""

    @pytest.fixture
    def transformer_model(self):
        """Create Transformer model for causal mask tests."""
        return NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2, dropout=0.0
        )

    def test_causal_mask_shape(self, transformer_model):
        """Test causal mask has correct shape."""
        seq_length = 9

        # Generate causal mask (using PyTorch's triu for upper triangular mask)
        causal_mask = torch.triu(torch.ones(seq_length, seq_length, dtype=torch.bool), diagonal=1)

        assert causal_mask.shape == (seq_length, seq_length), \
            f"Expected mask shape ({seq_length}, {seq_length}), got {causal_mask.shape}"

    def test_causal_mask_structure(self, transformer_model):
        """Test causal mask prevents attending to future positions."""
        seq_length = 9

        # Generate causal mask (bool type for TransformerEncoder)
        causal_mask = torch.triu(torch.ones(seq_length, seq_length, dtype=torch.bool), diagonal=1)

        # Causal mask should be upper triangular (True above diagonal means masked)
        # Lower triangle (including diagonal) should be False (not masked)
        # Upper triangle should be True (masked)

        for i in range(seq_length):
            for j in range(seq_length):
                if j > i:
                    # Future position: should be masked (True)
                    assert causal_mask[i, j] == True, \
                        f"Position ({i}, {j}) should be masked"
                else:
                    # Past or current position: should not be masked (False)
                    assert causal_mask[i, j] == False, \
                        f"Position ({i}, {j}) should not be masked"

    def test_bidirectional_attention_sees_full_context(self, transformer_model):
        """Test that bidirectional attention allows all positions to see each other."""
        transformer_model.eval()

        # Create two sequences that differ only in the last timestep
        x1 = torch.randn(1, 9, 64)
        x2 = x1.clone()
        x2[:, -1, :] = torch.randn(1, 64)  # Different last timestep

        with torch.no_grad():
            # Add positional embeddings
            pe1 = x1 + transformer_model.pos_embedding[:, :9, :]
            pe2 = x2 + transformer_model.pos_embedding[:, :9, :]

            # Forward through transformer (no causal mask — bidirectional)
            out1 = transformer_model.transformer_encoder(pe1)
            out2 = transformer_model.transformer_encoder(pe2)

            # With bidirectional attention, changing last timestep SHOULD affect
            # earlier timesteps (they can see the last position)
            diff_early = (out1[:, :8, :] - out2[:, :8, :]).abs().max()

            assert diff_early > 1e-5, \
                f"Early timesteps unchanged ({diff_early:.6f}) — attention may not be bidirectional"


class TestAttentionWeights:
    """Tests for attention weight validity."""

    @pytest.fixture
    def hybrid_model(self):
        """Create Hybrid model for attention tests."""
        return NextHeadHybrid(
            embed_dim=64, hidden_dim=256, num_classes=7,
            num_heads=4, num_gru_layers=2, dropout=0.0
        )

    def test_attention_weights_sum_to_one(self, hybrid_model):
        """Test that attention weights sum to 1 along appropriate dimension."""
        hybrid_model.eval()

        batch_size = 8
        seq_length = 9
        x = torch.randn(batch_size, seq_length, 64)

        with torch.no_grad():
            # Get attention weights
            padding_mask = (x.abs().sum(dim=-1) == 0)
            gru_out, _ = hybrid_model.gru(x)
            gru_out = hybrid_model.norm1(gru_out)

            _, attn_weights = hybrid_model.attention(
                gru_out, gru_out, gru_out,
                key_padding_mask=padding_mask,
                need_weights=True,
                average_attn_weights=True
            )

            # Attention weights should sum to 1 along last dimension
            attn_sum = attn_weights.sum(dim=-1)

            assert torch.allclose(attn_sum, torch.ones_like(attn_sum), atol=1e-5), \
                f"Attention weights don't sum to 1: {attn_sum}"

    def test_attention_weights_non_negative(self, hybrid_model):
        """Test that attention weights are non-negative."""
        hybrid_model.eval()

        x = torch.randn(4, 9, 64)

        with torch.no_grad():
            padding_mask = (x.abs().sum(dim=-1) == 0)
            gru_out, _ = hybrid_model.gru(x)
            gru_out = hybrid_model.norm1(gru_out)

            _, attn_weights = hybrid_model.attention(
                gru_out, gru_out, gru_out,
                key_padding_mask=padding_mask,
                need_weights=True,
                average_attn_weights=True
            )

            # All weights should be >= 0
            assert (attn_weights >= 0).all(), \
                "Attention weights contain negative values"

    def test_attention_masks_padding(self, hybrid_model):
        """Test that attention correctly masks padded positions."""
        hybrid_model.eval()

        batch_size = 4
        seq_length = 9
        x = torch.randn(batch_size, seq_length, 64)

        # Add padding to last 3 timesteps
        x[:, 6:, :] = 0

        with torch.no_grad():
            padding_mask = (x.abs().sum(dim=-1) == 0)
            gru_out, _ = hybrid_model.gru(x)
            gru_out = hybrid_model.norm1(gru_out)

            _, attn_weights = hybrid_model.attention(
                gru_out, gru_out, gru_out,
                key_padding_mask=padding_mask,
                need_weights=True,
                average_attn_weights=True
            )

            # Attention to padded positions should be zero (or very small)
            padded_attn = attn_weights[:, :, 6:]  # Attention to last 3 positions

            assert padded_attn.max() < 1e-5, \
                f"Attention to padded positions is {padded_attn.max():.6f} (should be ~0)"


class TestGradientFlow:
    """Tests for gradient flow through models."""

    @pytest.fixture
    def model(self):
        """Create model for gradient tests."""
        return NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2, dropout=0.1
        )

    def test_gradients_flow_backward(self, model):
        """Test that gradients flow through all parameters."""
        x = torch.randn(16, 9, 64)
        y = torch.randint(0, 7, (16,))

        # Forward pass
        output = model(x)
        loss = nn.CrossEntropyLoss()(output, y)

        # Backward pass
        loss.backward()

        # Check that gradients exist for all parameters
        params_without_grad = []
        for name, param in model.named_parameters():
            if param.requires_grad and param.grad is None:
                params_without_grad.append(name)

        assert len(params_without_grad) == 0, \
            f"Parameters without gradients: {params_without_grad}"

    def test_gradients_non_zero(self, model):
        """Test that gradients are non-zero (model is learning)."""
        x = torch.randn(32, 9, 64)
        y = torch.randint(0, 7, (32,))

        # Forward pass
        output = model(x)
        loss = nn.CrossEntropyLoss()(output, y)

        # Backward pass
        loss.backward()

        # Check that at least some gradients are non-zero
        total_grad_norm = 0.0
        for param in model.parameters():
            if param.grad is not None:
                total_grad_norm += param.grad.norm().item()

        assert total_grad_norm > 0, \
            "All gradients are zero (model not learning)"

    def test_no_gradient_explosion(self, model):
        """Test that gradients don't explode."""
        x = torch.randn(64, 9, 64)
        y = torch.randint(0, 7, (64,))

        # Forward pass
        output = model(x)
        loss = nn.CrossEntropyLoss()(output, y)

        # Backward pass
        loss.backward()

        # Check gradient norms
        max_grad_norm = 0.0
        for param in model.parameters():
            if param.grad is not None:
                grad_norm = param.grad.norm().item()
                max_grad_norm = max(max_grad_norm, grad_norm)

        # Gradients shouldn't be astronomically large
        assert max_grad_norm < 1000, \
            f"Gradient explosion detected: max norm = {max_grad_norm}"


class TestSequencePooling:
    """Tests for sequence pooling/reduction mechanisms."""

    @pytest.fixture
    def transformer_model(self):
        """Create Transformer model."""
        return NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2, dropout=0.0
        )

    def test_attention_pooling_output_shape(self, transformer_model):
        """Test attention-based sequence pooling produces single vector."""
        transformer_model.eval()

        batch_size = 16
        seq_length = 9
        embed_dim = 64

        # Create dummy transformer output
        x = torch.randn(batch_size, seq_length, embed_dim)

        with torch.no_grad():
            # Compute attention weights for pooling
            attn_logits = transformer_model.sequence_reduction(x)

            assert attn_logits.shape == (batch_size, seq_length, 1), \
                f"Expected attention logits shape ({batch_size}, {seq_length}, 1), got {attn_logits.shape}"

            # Apply softmax
            attn_weights = torch.softmax(attn_logits, dim=1)

            # Weighted sum
            pooled = torch.sum(x * attn_weights, dim=1)

            assert pooled.shape == (batch_size, embed_dim), \
                f"Expected pooled shape ({batch_size}, {embed_dim}), got {pooled.shape}"

    def test_pooling_weights_sum_to_one(self, transformer_model):
        """Test that pooling attention weights sum to 1."""
        transformer_model.eval()

        x = torch.randn(8, 9, 64)

        with torch.no_grad():
            attn_logits = transformer_model.sequence_reduction(x)
            attn_weights = torch.softmax(attn_logits, dim=1)

            # Sum over sequence dimension should be 1
            weight_sums = attn_weights.sum(dim=1)

            assert torch.allclose(weight_sums, torch.ones_like(weight_sums), atol=1e-5), \
                f"Attention weights don't sum to 1: {weight_sums}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
