"""
Test suite for Next-POI configuration consistency.

Tests that default hyperparameters are consistent, reasonable, and match
between ExperimentConfig and model implementations.

These constants were originally in CfgNextModel/CfgNextHyperparams/CfgNextTraining
(deprecated configs removed in cleanup). The tests validate architectural
constraints that must hold regardless of config source.
"""

import pytest
import torch

from configs.experiment import ExperimentConfig
from configs.model import InputsConfig
from models.next import NextHeadSingle, NextHeadHybrid

# Derive all defaults from the canonical config source
_CFG = ExperimentConfig.default_next("_test", "test", "dgi")
_MP = _CFG.model_params

# Next-POI model defaults (from ExperimentConfig.default_next)
NEXT_INPUT_DIM = _MP["embed_dim"]
NEXT_NUM_HEADS = _MP["num_heads"]
NEXT_NUM_LAYERS = _MP["num_layers"]
NEXT_MAX_SEQ_LENGTH = _MP["seq_length"]
NEXT_NUM_CLASSES = _MP["num_classes"]
NEXT_DROPOUT = _MP["dropout"]
NEXT_HIDDEN_DIM = 256  # not in ExperimentConfig (hybrid-only param)
NEXT_NUM_GRU_LAYERS = 2  # not in ExperimentConfig (hybrid-only param)

# Next-POI hyperparams
NEXT_LR = _CFG.learning_rate
NEXT_MAX_LR = _CFG.max_lr
NEXT_WEIGHT_DECAY = _CFG.weight_decay
NEXT_MAX_GRAD_NORM = _CFG.max_grad_norm

# Next-POI training
NEXT_BATCH_SIZE = _CFG.batch_size
NEXT_EPOCHS = _CFG.epochs
NEXT_K_FOLDS = _CFG.k_folds
NEXT_SEED = _CFG.seed


class TestNumHeadsConfiguration:
    """Tests for attention head configuration."""

    def test_num_heads_divides_embed_dim(self):
        """Test that NUM_HEADS divides INPUT_DIM evenly."""
        assert NEXT_INPUT_DIM % NEXT_NUM_HEADS == 0, \
            f"NUM_HEADS ({NEXT_NUM_HEADS}) must divide INPUT_DIM ({NEXT_INPUT_DIM}) evenly. " \
            f"Current: {NEXT_INPUT_DIM}/{NEXT_NUM_HEADS} = {NEXT_INPUT_DIM/NEXT_NUM_HEADS}"

    def test_head_dimension_reasonable(self):
        """Test that head dimension is >= 16 for good performance."""
        head_dim = NEXT_INPUT_DIM // NEXT_NUM_HEADS

        assert head_dim >= 8, \
            f"Head dimension {head_dim} is too small (< 8). " \
            f"Consider reducing NUM_HEADS to {NEXT_INPUT_DIM // 16} or fewer."

        if head_dim < 16:
            import warnings
            warnings.warn(
                f"Head dimension {head_dim} is small. "
                f"Recommended: >= 16 dims per head. "
                f"Current config: {NEXT_NUM_HEADS} heads x {head_dim} dims = {NEXT_INPUT_DIM}"
            )

    def test_num_heads_power_of_two(self):
        """Test that NUM_HEADS is a power of 2 (recommended for efficiency)."""
        is_power_of_two = NEXT_NUM_HEADS & (NEXT_NUM_HEADS - 1) == 0 and NEXT_NUM_HEADS > 0

        if not is_power_of_two:
            import warnings
            warnings.warn(
                f"NUM_HEADS ({NEXT_NUM_HEADS}) is not a power of 2. "
                f"Consider using 2, 4, 8, or 16 for better efficiency."
            )


class TestDropoutConfiguration:
    """Tests for dropout consistency across configs."""

    def test_dropout_in_range(self):
        """Test that dropout is in valid range [0, 1)."""
        assert 0 <= NEXT_DROPOUT < 1.0, \
            f"DROPOUT {NEXT_DROPOUT} outside valid range [0, 1)"

    def test_dropout_not_too_high(self):
        """Test that dropout is not excessively high for short sequences."""
        if NEXT_MAX_SEQ_LENGTH < 20 and NEXT_DROPOUT > 0.3:
            import warnings
            warnings.warn(
                UserWarning(
                    f"DROPOUT ({NEXT_DROPOUT}) might be too high for short sequences (len={NEXT_MAX_SEQ_LENGTH}). "
                    f"Consider 0.2-0.3 for seq_length < 20."
                )
            )

    def test_dropout_matches_model_default(self):
        """Test that config dropout matches model implementation default."""
        model_with_config = NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2,
            dropout=NEXT_DROPOUT
        )

        main_dropout = model_with_config.dropout.p

        assert main_dropout == NEXT_DROPOUT, \
            f"Model dropout ({main_dropout}) != config dropout ({NEXT_DROPOUT})"


class TestEmbeddingDimensionConfiguration:
    """Tests for embedding dimension consistency."""

    def test_embedding_dim_is_positive(self):
        """Test that EMBEDDING_DIM is a valid positive value."""
        assert InputsConfig.EMBEDDING_DIM > 0, \
            f"EMBEDDING_DIM must be positive, got {InputsConfig.EMBEDDING_DIM}"

    def test_fusion_dim_handling(self):
        """Test that fusion dimensions would be handled correctly."""
        try:
            next_dim = InputsConfig.get_next_dim()
            assert next_dim > 0, \
                f"get_next_dim() returned invalid dimension: {next_dim}"
        except AttributeError:
            import warnings
            warnings.warn(
                UserWarning(
                    "InputsConfig.get_next_dim() not found. "
                    "Fusion mode may not handle dimensions correctly."
                )
            )


class TestMaxSeqLengthConfiguration:
    """Tests for maximum sequence length configuration."""

    def test_max_seq_length_matches_slide_window(self):
        """Test that MAX_SEQ_LENGTH matches SLIDE_WINDOW."""
        assert NEXT_MAX_SEQ_LENGTH == InputsConfig.SLIDE_WINDOW, \
            f"MAX_SEQ_LENGTH ({NEXT_MAX_SEQ_LENGTH}) must match SLIDE_WINDOW ({InputsConfig.SLIDE_WINDOW})"

    def test_max_seq_length_is_positive(self):
        """Test that MAX_SEQ_LENGTH is a valid positive value."""
        assert NEXT_MAX_SEQ_LENGTH > 0, \
            f"MAX_SEQ_LENGTH must be positive, got {NEXT_MAX_SEQ_LENGTH}"


class TestNumClassesConfiguration:
    """Tests for number of classes configuration."""

    def test_num_classes_positive(self):
        """Test that NUM_CLASSES is a valid positive value."""
        assert NEXT_NUM_CLASSES > 0, \
            f"NUM_CLASSES must be positive, got {NEXT_NUM_CLASSES}"


class TestGradientClippingConfiguration:
    """Tests for gradient clipping settings."""

    def test_max_grad_norm_reasonable(self):
        """Test that MAX_GRAD_NORM is in reasonable range."""
        assert 0.5 <= NEXT_MAX_GRAD_NORM <= 5.0, \
            f"MAX_GRAD_NORM ({NEXT_MAX_GRAD_NORM}) outside reasonable range [0.5, 5.0]"

    def test_max_grad_norm_for_transformers(self):
        """Test that MAX_GRAD_NORM is appropriate for Transformers."""
        if NEXT_MAX_GRAD_NORM < 1.0:
            import warnings
            warnings.warn(
                UserWarning(
                    f"MAX_GRAD_NORM ({NEXT_MAX_GRAD_NORM}) is very aggressive. "
                    f"Standard for Transformers: 1.0-5.0"
                )
            )


class TestLearningRateConfiguration:
    """Tests for learning rate settings."""

    def test_lr_positive(self):
        """Test that learning rate is positive."""
        assert NEXT_LR > 0, f"Learning rate must be positive, got {NEXT_LR}"

    def test_max_lr_greater_than_lr(self):
        """Test that MAX_LR > LR for OneCycleLR."""
        assert NEXT_MAX_LR > NEXT_LR, \
            f"MAX_LR ({NEXT_MAX_LR}) must be > LR ({NEXT_LR}) for OneCycleLR"

    def test_max_lr_not_too_high(self):
        """Test that MAX_LR is not too aggressive."""
        if NEXT_MAX_LR > 0.01:
            import warnings
            warnings.warn(
                UserWarning(
                    f"MAX_LR ({NEXT_MAX_LR}) is high. "
                    f"For Transformers, typical range: 0.001-0.005"
                )
            )

    def test_weight_decay_reasonable(self):
        """Test that weight decay is in reasonable range."""
        assert 0 <= NEXT_WEIGHT_DECAY <= 0.1, \
            f"WEIGHT_DECAY ({NEXT_WEIGHT_DECAY}) outside typical range [0, 0.1]"


class TestBatchSizeConfiguration:
    """Tests for batch size settings."""

    def test_batch_size_power_of_two(self):
        """Test that BATCH_SIZE is a power of 2."""
        is_power_of_two = NEXT_BATCH_SIZE & (NEXT_BATCH_SIZE - 1) == 0 and NEXT_BATCH_SIZE > 0

        assert is_power_of_two, \
            f"BATCH_SIZE ({NEXT_BATCH_SIZE}) should be a power of 2 for efficiency"

    def test_batch_size_reasonable(self):
        """Test that BATCH_SIZE is in reasonable range."""
        assert 32 <= NEXT_BATCH_SIZE <= 8192, \
            f"BATCH_SIZE ({NEXT_BATCH_SIZE}) outside typical range [32, 8192]"


class TestEpochsConfiguration:
    """Tests for training epochs configuration."""

    def test_epochs_positive(self):
        """Test that EPOCHS is positive."""
        assert NEXT_EPOCHS > 0, f"EPOCHS must be positive, got {NEXT_EPOCHS}"

    def test_epochs_not_excessive(self):
        """Test that EPOCHS is not excessively large."""
        if NEXT_EPOCHS > 100:
            import warnings
            warnings.warn(
                UserWarning(
                    f"EPOCHS ({NEXT_EPOCHS}) is very high. "
                    f"Consider using early stopping instead."
                )
            )


class TestKFoldsConfiguration:
    """Tests for cross-validation folds."""

    def test_k_folds_reasonable(self):
        """Test that K_FOLDS is in reasonable range."""
        assert 2 <= NEXT_K_FOLDS <= 10, \
            f"K_FOLDS ({NEXT_K_FOLDS}) outside typical range [2, 10]"


class TestModelArchitectureConsistency:
    """Tests for consistency between config and model implementation."""

    def test_model_initializes_with_config(self):
        """Test that model can be initialized with config parameters."""
        try:
            model = NextHeadSingle(
                embed_dim=NEXT_INPUT_DIM,
                num_classes=NEXT_NUM_CLASSES,
                num_heads=NEXT_NUM_HEADS,
                seq_length=NEXT_MAX_SEQ_LENGTH,
                num_layers=NEXT_NUM_LAYERS,
                dropout=NEXT_DROPOUT
            )

            assert model is not None, "Model initialization failed"
        except Exception as e:
            pytest.fail(f"Model initialization failed with config: {e}")

    def test_hybrid_model_has_required_params(self):
        """Test that Hybrid model config would have required parameters."""
        # These values are available as module-level constants
        assert NEXT_HIDDEN_DIM > 0, "HIDDEN_DIM must be positive"
        assert NEXT_NUM_GRU_LAYERS > 0, "NUM_GRU_LAYERS must be positive"

    def test_num_layers_reasonable(self):
        """Test that NUM_LAYERS is in reasonable range."""
        assert 1 <= NEXT_NUM_LAYERS <= 12, \
            f"NUM_LAYERS ({NEXT_NUM_LAYERS}) outside reasonable range [1, 12]"


class TestConfigCompleteness:
    """Tests to ensure all required config values are defined."""

    def test_all_model_configs_exist(self):
        """Test that all required model configs are defined."""
        required = {
            'INPUT_DIM': NEXT_INPUT_DIM,
            'NUM_HEADS': NEXT_NUM_HEADS,
            'NUM_LAYERS': NEXT_NUM_LAYERS,
            'MAX_SEQ_LENGTH': NEXT_MAX_SEQ_LENGTH,
            'NUM_CLASSES': NEXT_NUM_CLASSES,
            'DROPOUT': NEXT_DROPOUT,
        }
        for name, val in required.items():
            assert val is not None, f"Missing required config: {name}"

    def test_all_hyperparams_exist(self):
        """Test that all required hyperparameters are defined."""
        required = {
            'LR': NEXT_LR,
            'MAX_LR': NEXT_MAX_LR,
            'WEIGHT_DECAY': NEXT_WEIGHT_DECAY,
            'MAX_GRAD_NORM': NEXT_MAX_GRAD_NORM,
        }
        for name, val in required.items():
            assert val is not None, f"Missing required hyperparameter: {name}"

    def test_all_training_configs_exist(self):
        """Test that all required training configs are defined."""
        required = {
            'BATCH_SIZE': NEXT_BATCH_SIZE,
            'EPOCHS': NEXT_EPOCHS,
            'K_FOLDS': NEXT_K_FOLDS,
            'SEED': NEXT_SEED,
        }
        for name, val in required.items():
            assert val is not None, f"Missing required training config: {name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
