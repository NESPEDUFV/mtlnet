"""
Test suite for Next-POI model architecture validation.

Tests model structure, output shapes, positional encoding,
padding masks, and parameter counts.
"""

import pytest
import torch
import torch.nn as nn
from models.next import NextHeadSingle
from models.next import (
    NextHeadHybrid,
    NextHeadGRU,
    NextHeadLSTM,
    NextHeadTransformerOptimized,
    NextHeadTemporalCNN,
    NextHeadConvAttn,
    NextHeadTCNResidual,
    NextHeadTransformerRelPos,
)
from configs.experiment import ExperimentConfig

# Derive defaults from canonical config source
_CFG = ExperimentConfig.default_next("_test", "test", "dgi")
_MP = _CFG.model_params
_NEXT_INPUT_DIM = _MP["embed_dim"]
_NEXT_NUM_HEADS = _MP["num_heads"]
_NEXT_MAX_SEQ_LENGTH = _MP["seq_length"]
_NEXT_NUM_CLASSES = _MP["num_classes"]


class TestNextHeadSingleArchitecture:
    """Tests for NextHeadSingle (current Transformer model)."""

    @pytest.fixture
    def model(self):
        """Create NextHeadSingle model instance."""
        return NextHeadSingle(
            embed_dim=64,
            num_classes=7,
            num_heads=16,  # Current (problematic) setting
            seq_length=9,
            num_layers=4,
            dropout=0.1
        )

    @pytest.fixture
    def model_fixed(self):
        """Create NextHeadSingle with fixed attention heads."""
        return NextHeadSingle(
            embed_dim=64,
            num_classes=7,
            num_heads=4,  # Fixed: 64/4 = 16 dims per head
            seq_length=9,
            num_layers=4,
            dropout=0.2
        )

    def test_output_shape(self, model):
        """Test that model outputs correct shape [batch, num_classes]."""
        batch_size = 32
        seq_length = 9
        embed_dim = 64

        x = torch.randn(batch_size, seq_length, embed_dim)
        output = model(x)

        assert output.shape == (batch_size, 7), \
            f"Expected output shape ({batch_size}, 7), got {output.shape}"

    def test_positional_encoding_shape(self, model):
        """Test learned positional embeddings have correct shape."""
        seq_length = 9
        embed_dim = 64

        assert model.pos_embedding.shape == (1, seq_length, embed_dim), \
            f"Pos embedding shape mismatch: expected (1, {seq_length}, {embed_dim}), got {model.pos_embedding.shape}"

    def test_padding_mask_generation(self, model):
        """Test padding mask correctly identifies zero sequences."""
        batch_size = 16
        seq_length = 9
        embed_dim = 64

        # Create batch with some padding (all-zero timesteps)
        x = torch.randn(batch_size, seq_length, embed_dim)

        # Add padding to some sequences
        x[0, 7:, :] = 0  # Last 2 timesteps padded
        x[1, 5:, :] = 0  # Last 4 timesteps padded

        # Generate padding mask (True where padded)
        padding_mask = (x.abs().sum(dim=-1) == 0)

        # Verify padding detection
        assert padding_mask[0, 7:].all(), "Padding not detected for sequence 0"
        assert padding_mask[1, 5:].all(), "Padding not detected for sequence 1"
        assert not padding_mask[0, :7].any(), "False positive padding for sequence 0"

    def test_model_parameter_count(self, model):
        """Test model has expected number of parameters."""
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        # Expected ~220k parameters for this config
        assert 150_000 < total_params < 300_000, \
            f"Parameter count {total_params:,} outside expected range"
        assert trainable_params == total_params, \
            "Some parameters are frozen (not expected for this model)"

    def test_forward_with_batch(self, model):
        """Test model handles different batch sizes."""
        embed_dim = 64
        seq_length = 9

        for batch_size in [1, 16, 32, 128]:
            x = torch.randn(batch_size, seq_length, embed_dim)
            output = model(x)

            assert output.shape == (batch_size, 7), \
                f"Batch size {batch_size}: expected ({batch_size}, 7), got {output.shape}"


class TestNextHeadHybridArchitecture:
    """Tests for NextHeadHybrid (GRU + Attention)."""

    @pytest.fixture
    def model(self):
        """Create NextHeadHybrid model instance."""
        return NextHeadHybrid(
            embed_dim=64,
            hidden_dim=256,
            num_classes=7,
            num_heads=4,
            num_gru_layers=2,
            dropout=0.3
        )

    def test_output_shape(self, model):
        """Test Hybrid model outputs correct shape."""
        batch_size = 32
        seq_length = 9
        embed_dim = 64

        x = torch.randn(batch_size, seq_length, embed_dim)
        output = model(x)

        assert output.shape == (batch_size, 7), \
            f"Expected output shape ({batch_size}, 7), got {output.shape}"

    def test_gru_output_shape(self, model):
        """Test GRU produces correct hidden dimension."""
        batch_size = 16
        seq_length = 9
        embed_dim = 64
        hidden_dim = 256

        x = torch.randn(batch_size, seq_length, embed_dim)

        # Forward through GRU
        gru_out, _ = model.gru(x)

        assert gru_out.shape == (batch_size, seq_length, hidden_dim), \
            f"Expected GRU output {(batch_size, seq_length, hidden_dim)}, got {gru_out.shape}"

    def test_attention_output_shape(self, model):
        """Test attention mechanism output shape."""
        batch_size = 16
        seq_length = 9
        hidden_dim = 256

        # Create dummy GRU output
        gru_out = torch.randn(batch_size, seq_length, hidden_dim)

        # Apply attention
        attn_out, _ = model.attention(gru_out, gru_out, gru_out)

        assert attn_out.shape == (batch_size, seq_length, hidden_dim), \
            f"Expected attention output {(batch_size, seq_length, hidden_dim)}, got {attn_out.shape}"

    def test_model_parameter_count(self, model):
        """Test Hybrid model has expected parameters (~900k)."""
        total_params = sum(p.numel() for p in model.parameters())

        # Hybrid with hidden_dim=256: ~900k parameters
        assert 500_000 < total_params < 1_500_000, \
            f"Parameter count {total_params:,} outside expected range"

    def test_forward_with_different_batch_sizes(self, model):
        """Test Hybrid handles various batch sizes."""
        embed_dim = 64
        seq_length = 9

        for batch_size in [1, 16, 32, 64]:
            x = torch.randn(batch_size, seq_length, embed_dim)
            output = model(x)

            assert output.shape == (batch_size, 7), \
                f"Batch size {batch_size}: expected ({batch_size}, 7), got {output.shape}"


class TestNextHeadGRUArchitecture:
    """Tests for NextHeadGRU (baseline RNN model)."""

    @pytest.fixture
    def model(self):
        """Create NextHeadGRU model instance."""
        return NextHeadGRU(
            embed_dim=64,
            hidden_dim=256,
            num_classes=7,
            num_layers=2,
            dropout=0.3
        )

    def test_output_shape(self, model):
        """Test GRU model outputs correct shape."""
        batch_size = 32
        seq_length = 9
        embed_dim = 64

        x = torch.randn(batch_size, seq_length, embed_dim)
        output = model(x)

        assert output.shape == (batch_size, 7), \
            f"Expected output shape ({batch_size}, 7), got {output.shape}"

    def test_model_parameter_count(self, model):
        """Test GRU has expected parameters (~640k)."""
        total_params = sum(p.numel() for p in model.parameters())

        # GRU with hidden_dim=256: ~640k parameters
        assert 400_000 < total_params < 1_000_000, \
            f"Parameter count {total_params:,} outside expected range"


class TestNextHeadConvAttnArchitecture:
    """Tests for NextHeadConvAttn (TCN + cross-attention pooling)."""

    @pytest.fixture
    def model(self):
        return NextHeadConvAttn(
            embed_dim=64,
            hidden_channels=128,
            num_classes=7,
            num_conv_layers=3,
            kernel_size=3,
            num_heads=4,
            dropout=0.2,
        )

    def test_output_shape(self, model):
        x = torch.randn(16, 9, 64)
        assert model(x).shape == (16, 7)

    def test_output_finite(self, model):
        x = torch.randn(16, 9, 64)
        assert torch.isfinite(model(x)).all()

    def test_batch_size_one(self, model):
        assert model(torch.randn(1, 9, 64)).shape == (1, 7)

    def test_padded_sequence(self, model):
        x = torch.randn(8, 9, 64)
        x[:, 6:, :] = 0
        out = model(x)
        assert out.shape == (8, 7)
        assert torch.isfinite(out).all()

    def test_learned_query_shape(self, model):
        assert model.query.shape == (1, 1, 128)

    def test_parameter_count(self, model):
        total = sum(p.numel() for p in model.parameters())
        assert 50_000 < total < 500_000, f"Unexpected param count: {total:,}"


class TestNextHeadTCNResidualArchitecture:
    """Tests for NextHeadTCNResidual (canonical TCN with exponential dilation)."""

    @pytest.fixture
    def model(self):
        return NextHeadTCNResidual(
            embed_dim=64,
            hidden_channels=128,
            num_classes=7,
            num_blocks=4,
            kernel_size=3,
            dropout=0.2,
        )

    def test_output_shape(self, model):
        x = torch.randn(16, 9, 64)
        assert model(x).shape == (16, 7)

    def test_output_finite(self, model):
        x = torch.randn(16, 9, 64)
        assert torch.isfinite(model(x)).all()

    def test_batch_size_one(self, model):
        assert model(torch.randn(1, 9, 64)).shape == (1, 7)

    def test_dilation_schedule(self, model):
        """Blocks must have exponential dilation: 1, 2, 4, 8."""
        expected = [1, 2, 4, 8]
        for block, dil in zip(model.network, expected):
            assert block.conv1.dilation == (dil,), (
                f"Expected dilation {dil}, got {block.conv1.dilation}"
            )

    def test_num_blocks(self, model):
        assert len(model.network) == 4

    def test_parameter_count(self, model):
        total = sum(p.numel() for p in model.parameters())
        assert 100_000 < total < 1_000_000, f"Unexpected param count: {total:,}"


class TestNextHeadTransformerOptimizedArchitecture:
    """Tests for NextHeadTransformerOptimized (temporal-decay pooling)."""

    @pytest.fixture
    def model(self):
        return NextHeadTransformerOptimized(
            embed_dim=64,
            num_classes=7,
            num_heads=4,
            num_layers=2,
            seq_length=9,
            dropout=0.1,
            use_temporal_decay=True,
        )

    def test_output_shape(self, model):
        x = torch.randn(16, 9, 64)
        assert model(x).shape == (16, 7)

    def test_output_finite(self, model):
        x = torch.randn(16, 9, 64)
        assert torch.isfinite(model(x)).all()

    def test_batch_size_one(self, model):
        assert model(torch.randn(1, 9, 64)).shape == (1, 7)

    def test_no_nested_tensor_warning(self, model):
        """TransformerEncoder must be constructed with enable_nested_tensor=False."""
        assert not model.transformer.enable_nested_tensor

    def test_temporal_decay_buffer_shape(self, model):
        assert model.temporal_decay.shape == (9,)

    def test_without_temporal_decay(self):
        m = NextHeadTransformerOptimized(
            embed_dim=64, num_classes=7, num_heads=4,
            num_layers=2, seq_length=9, use_temporal_decay=False,
        )
        x = torch.randn(4, 9, 64)
        assert m(x).shape == (4, 7)

    def test_padded_sequence(self, model):
        x = torch.randn(8, 9, 64)
        x[:, 6:, :] = 0
        out = model(x)
        assert out.shape == (8, 7)
        assert torch.isfinite(out).all()


class TestNextHeadTransformerRelPosArchitecture:
    """Tests for NextHeadTransformerRelPos (relative position bias)."""

    @pytest.fixture
    def model(self):
        return NextHeadTransformerRelPos(
            embed_dim=64,
            num_classes=7,
            num_heads=4,
            num_layers=2,
            seq_length=9,
            dropout=0.2,
        )

    def test_output_shape(self, model):
        x = torch.randn(16, 9, 64)
        assert model(x).shape == (16, 7)

    def test_output_finite(self, model):
        x = torch.randn(16, 9, 64)
        assert torch.isfinite(model(x)).all()

    def test_batch_size_one(self, model):
        assert model(torch.randn(1, 9, 64)).shape == (1, 7)

    def test_causal_mask_buffer_shape(self, model):
        assert model.causal_mask.shape == (9, 9)

    def test_causal_mask_is_upper_triangular(self, model):
        # Upper triangle (above diagonal) must all be True (masked)
        mask = model.causal_mask
        for i in range(9):
            for j in range(9):
                if j > i:
                    assert mask[i, j], f"({i},{j}) should be masked"
                else:
                    assert not mask[i, j], f"({i},{j}) should not be masked"

    def test_rel_pos_bias_shape(self, model):
        for layer in model.layers:
            assert layer.rel_pos_bias.shape == (4, 9, 9)

    def test_padded_sequence(self, model):
        x = torch.randn(8, 9, 64)
        x[:, 6:, :] = 0
        out = model(x)
        assert out.shape == (8, 7)
        assert torch.isfinite(out).all()

    def test_num_layers(self, model):
        assert len(model.layers) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
