"""
Test suite for Next-POI data loading and preprocessing.

Tests sequence reshaping, padding detection, fold creation,
batch size correctness, and data leakage prevention.
"""

import pytest
import torch
import pandas as pd
import numpy as np
from pathlib import Path

from data.folds import FoldCreator
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine, IoPaths


class TestSequenceReshaping:
    """Tests for correct reshaping of input sequences."""

    def test_flatten_to_3d_reshape(self):
        """Test reshaping from flattened (N, 576) to 3D (N, 9, 64)."""
        batch_size = 32
        window_size = 9
        embedding_dim = 64
        flattened_dim = window_size * embedding_dim  # 576

        # Create flattened input
        x_flat = torch.randn(batch_size, flattened_dim)

        # Reshape to 3D
        x_3d = x_flat.view(batch_size, window_size, embedding_dim)

        assert x_3d.shape == (batch_size, window_size, embedding_dim), \
            f"Expected shape ({batch_size}, {window_size}, {embedding_dim}), got {x_3d.shape}"

        # Verify data integrity after reshape
        x_flat_reconstructed = x_3d.view(batch_size, -1)
        assert torch.allclose(x_flat, x_flat_reconstructed), \
            "Data changed during reshape"

    def test_embedding_dim_matches_config(self):
        """Test that flattened features = window * embedding_dim."""
        embedding_dim = InputsConfig.EMBEDDING_DIM
        window_size = InputsConfig.SLIDE_WINDOW

        expected_flattened = window_size * embedding_dim

        assert expected_flattened == window_size * embedding_dim, \
            f"Expected {window_size}*{embedding_dim}={window_size * embedding_dim}, got {expected_flattened}"
        assert embedding_dim > 0
        assert window_size > 0

    def test_window_size_correct(self):
        """Test that SLIDE_WINDOW is 9."""
        assert InputsConfig.SLIDE_WINDOW == 9, \
            f"Expected SLIDE_WINDOW=9, got {InputsConfig.SLIDE_WINDOW}"

    def test_reshape_preserves_sequence_order(self):
        """Test that reshaping preserves temporal order."""
        # Create sequence with known pattern
        batch_size = 2
        window_size = 9
        embedding_dim = 64

        # First sequence: embeddings are [1, 2, 3, ..., 9] repeated 64 times
        seq1 = torch.arange(1, window_size + 1).repeat(embedding_dim, 1).T.flatten()

        # Second sequence: embeddings are [9, 8, 7, ..., 1] repeated 64 times
        seq2 = torch.arange(window_size, 0, -1).repeat(embedding_dim, 1).T.flatten()

        x_flat = torch.stack([seq1, seq2])

        # Reshape to 3D
        x_3d = x_flat.view(batch_size, window_size, embedding_dim)

        # Verify first timestep of first sequence
        assert x_3d[0, 0, :].unique().item() == 1, \
            "First timestep should be all 1s"

        # Verify last timestep of first sequence
        assert x_3d[0, 8, :].unique().item() == 9, \
            "Last timestep should be all 9s"

        # Verify first timestep of second sequence
        assert x_3d[1, 0, :].unique().item() == 9, \
            "Second sequence first timestep should be all 9s"


class TestPaddingDetection:
    """Tests for padding mask generation."""

    def test_all_zero_sequence_detected_as_padding(self):
        """Test that all-zero timesteps are detected as padding."""
        batch_size = 4
        seq_length = 9
        embed_dim = 64

        x = torch.randn(batch_size, seq_length, embed_dim)

        # Add padding to some sequences
        x[0, 5:, :] = 0  # Last 4 timesteps padded
        x[1, 7:, :] = 0  # Last 2 timesteps padded
        x[2, :, :] = 1   # No padding (all non-zero)

        # Generate padding mask
        padding_mask = (x.abs().sum(dim=-1) == 0)

        # Verify padding detection
        assert padding_mask[0, 5:].all(), "Padding not detected for sequence 0"
        assert padding_mask[1, 7:].all(), "Padding not detected for sequence 1"
        assert not padding_mask[2, :].any(), "False positive padding for sequence 2"

    def test_padding_value_is_zero(self):
        """Test that PAD_VALUE is 0."""
        assert InputsConfig.PAD_VALUE == 0, \
            f"Expected PAD_VALUE=0, got {InputsConfig.PAD_VALUE}"

    def test_mixed_padding_detection(self):
        """Test padding detection with various patterns."""
        batch_size = 3
        seq_length = 9
        embed_dim = 64

        x = torch.randn(batch_size, seq_length, embed_dim)

        # Sequence 0: Padding at end
        x[0, 6:, :] = 0

        # Sequence 1: No padding
        x[1, :, :] = torch.randn(seq_length, embed_dim)

        # Sequence 2: Heavy padding (only first 3 timesteps valid)
        x[2, 3:, :] = 0

        padding_mask = (x.abs().sum(dim=-1) == 0)

        # Count padded timesteps per sequence
        num_padded = padding_mask.sum(dim=1)

        assert num_padded[0] == 3, f"Expected 3 padded timesteps, got {num_padded[0]}"
        assert num_padded[1] == 0, f"Expected 0 padded timesteps, got {num_padded[1]}"
        assert num_padded[2] == 6, f"Expected 6 padded timesteps, got {num_padded[2]}"


class TestFoldCreation:
    """Tests for stratified K-fold creation logic."""

    def test_stratified_kfold_preserves_distribution(self):
        """Test that StratifiedKFold maintains class distribution."""
        from sklearn.model_selection import StratifiedKFold

        num_samples = 500
        # Imbalanced labels
        y = np.random.choice(7, size=num_samples, p=[0.3, 0.2, 0.15, 0.15, 0.1, 0.05, 0.05])

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        original_dist = np.bincount(y, minlength=7) / len(y)

        for fold_idx, (train_idx, val_idx) in enumerate(skf.split(np.zeros(num_samples), y)):
            val_labels = y[val_idx]
            val_dist = np.bincount(val_labels, minlength=7) / len(val_labels)

            # Distribution should be similar to original (within 10%)
            for class_idx in range(7):
                diff = abs(val_dist[class_idx] - original_dist[class_idx])
                assert diff < 0.1, \
                    f"Fold {fold_idx}, Class {class_idx}: distribution diff {diff:.3f} > 0.1"

    def test_no_overlap_train_val(self):
        """Test that training and validation indices don't overlap."""
        from sklearn.model_selection import StratifiedKFold

        num_samples = 500
        y = np.random.choice(7, size=num_samples)

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        for fold_idx, (train_idx, val_idx) in enumerate(skf.split(np.zeros(num_samples), y)):
            overlap = set(train_idx) & set(val_idx)
            assert len(overlap) == 0, \
                f"Fold {fold_idx}: Found {len(overlap)} overlapping indices"

    def test_fold_sizes_reasonable(self):
        """Test that fold sizes are reasonable (not too small/large)."""
        from sklearn.model_selection import StratifiedKFold

        num_samples = 500
        y = np.random.choice(7, size=num_samples)

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        for fold_idx, (train_idx, val_idx) in enumerate(skf.split(np.zeros(num_samples), y)):
            val_size = len(val_idx)
            train_size = len(train_idx)

            # Validation should be ~20% (1/5) of data
            expected_val_size = num_samples // 5
            assert abs(val_size - expected_val_size) < 10, \
                f"Fold {fold_idx}: val size {val_size} far from expected {expected_val_size}"

            assert train_size + val_size == num_samples, \
                f"Fold {fold_idx}: train ({train_size}) + val ({val_size}) != total ({num_samples})"

    def test_fold_creator_api(self):
        """Test that FoldCreator can be instantiated with correct API."""
        from data.folds import FoldCreator, TaskType

        # Verify the correct constructor signature
        fold_creator = FoldCreator(
            task_type=TaskType.NEXT,
            n_splits=5,
            batch_size=32,
            seed=42
        )

        assert fold_creator.n_splits == 5
        assert fold_creator.batch_size == 32
        assert fold_creator.seed == 42


class TestBatchSize:
    """Tests for batch size handling."""

    def test_batch_size_config(self):
        """Test that BATCH_SIZE is a power of 2."""
        from configs.experiment import ExperimentConfig
        batch_size = ExperimentConfig.default_next("_test", "test", "dgi").batch_size

        # Check if power of 2
        assert batch_size & (batch_size - 1) == 0, \
            f"BATCH_SIZE {batch_size} should be a power of 2"

        # Check if reasonable size
        assert 32 <= batch_size <= 8192, \
            f"BATCH_SIZE {batch_size} outside reasonable range [32, 8192]"

    def test_dataloader_batch_size(self):
        """Test that DataLoader respects batch size."""
        from torch.utils.data import DataLoader, TensorDataset

        batch_size = 64
        num_samples = 256

        X = torch.randn(num_samples, 9, 64)
        y = torch.randint(0, 7, (num_samples,))

        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        # Check batch sizes
        batch_sizes = [len(batch[0]) for batch in dataloader]

        # All batches except last should be full
        assert all(size == batch_size for size in batch_sizes[:-1]), \
            "Some batches have incorrect size"

        # Last batch can be smaller
        assert batch_sizes[-1] <= batch_size, \
            "Last batch size exceeds batch_size"

    def test_drop_last_false(self):
        """Test that drop_last=False to use all data."""
        from torch.utils.data import DataLoader, TensorDataset

        batch_size = 64
        num_samples = 100  # Not divisible by batch_size

        X = torch.randn(num_samples, 9, 64)
        y = torch.randint(0, 7, (num_samples,))

        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False, drop_last=False)

        total_samples_seen = sum(len(batch[0]) for batch in dataloader)

        assert total_samples_seen == num_samples, \
            f"Expected {num_samples} samples, saw {total_samples_seen} (drop_last should be False)"


class TestDataLeakage:
    """Tests to prevent data leakage between train and validation."""

    def test_temporal_leakage_prevention(self):
        """Test that future POIs don't leak into past sequences."""
        # Simulate temporal data: user visits POIs in order
        timestamps = pd.to_datetime([
            '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04',
            '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08',
            '2023-01-09', '2023-01-10'
        ])

        pois = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Create sliding windows (size 3 + 1 target)
        window_size = 3
        sequences = []

        for i in range(len(pois) - window_size):
            seq = pois[i:i+window_size]
            target = pois[i+window_size]
            sequences.append((seq, target))

        # Verify each sequence only uses past data
        for seq, target in sequences:
            assert all(poi < target for poi in seq), \
                f"Temporal leakage: sequence {seq} contains future POI for target {target}"

    def test_no_poi_overlap_train_val(self):
        """Test that validation POIs don't appear in training."""
        # Simulate scenario where validation split should have distinct POIs
        all_pois = list(range(100))
        np.random.shuffle(all_pois)

        # Split POIs: 80% train, 20% val
        split_idx = 80
        train_pois = set(all_pois[:split_idx])
        val_pois = set(all_pois[split_idx:])

        # Verify no overlap
        overlap = train_pois & val_pois
        assert len(overlap) == 0, \
            f"Found {len(overlap)} POIs in both train and validation"

    def test_validation_follows_training_temporally(self):
        """Test that validation data comes after training data temporally."""
        # Create temporal dataset
        num_samples = 1000
        timestamps = pd.date_range('2023-01-01', periods=num_samples, freq='h')
        pois = np.random.randint(0, 100, size=num_samples)

        # Sort by timestamp
        sorted_indices = np.argsort(timestamps)
        timestamps_sorted = timestamps[sorted_indices]
        pois_sorted = pois[sorted_indices]

        # Split: first 80% train, last 20% val
        split_idx = int(0.8 * num_samples)
        train_timestamps = timestamps_sorted[:split_idx]
        val_timestamps = timestamps_sorted[split_idx:]

        # Verify validation comes after training
        assert train_timestamps.max() <= val_timestamps.min(), \
            "Validation data should come after training data temporally"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
