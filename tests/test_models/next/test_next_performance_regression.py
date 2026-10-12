"""
Test suite for Next-POI performance regression testing.

Tests forward pass speed, training epoch time, and memory usage
to establish performance baselines.
"""

import pytest
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import time
import psutil
import os

from models.next import NextHeadSingle
from models.next import NextHeadHybrid, NextHeadGRU


class TestForwardPassSpeed:
    """Tests for forward pass inference speed."""

    @pytest.fixture(params=[
        ('NextHeadSingle', {'embed_dim': 64, 'num_classes': 7, 'num_heads': 4,
                            'seq_length': 9, 'num_layers': 2, 'dropout': 0.1}),
        ('NextHeadHybrid', {'embed_dim': 64, 'hidden_dim': 256, 'num_classes': 7,
                            'num_heads': 4, 'num_gru_layers': 2, 'dropout': 0.3}),
        ('NextHeadGRU', {'embed_dim': 64, 'hidden_dim': 256, 'num_classes': 7,
                         'num_layers': 2, 'dropout': 0.3})
    ], ids=['Transformer', 'Hybrid', 'GRU'])
    def model_spec(self, request):
        """Parametrized fixture for all model types."""
        return request.param

    def test_single_forward_pass_speed(self, model_spec):
        """Test that single forward pass completes in reasonable time."""
        model_name, model_kwargs = model_spec

        # Create model
        if model_name == 'NextHeadSingle':
            model = NextHeadSingle(**model_kwargs)
        elif model_name == 'NextHeadHybrid':
            model = NextHeadHybrid(**model_kwargs)
        elif model_name == 'NextHeadGRU':
            model = NextHeadGRU(**model_kwargs)

        model.eval()

        # Create input
        x = torch.randn(32, 9, 64)

        # Warmup (first pass may be slower)
        with torch.no_grad():
            _ = model(x)

        # Measure time for 100 forward passes
        start_time = time.time()

        with torch.no_grad():
            for _ in range(100):
                _ = model(x)

        end_time = time.time()
        avg_time_ms = (end_time - start_time) / 100 * 1000

        # Single forward pass should be < 50ms on CPU
        assert avg_time_ms < 50, \
            f"{model_name} forward pass takes {avg_time_ms:.2f}ms (expected < 50ms)"

        print(f"\n{model_name} avg forward pass time: {avg_time_ms:.2f}ms")

    def test_batch_processing_speed(self, model_spec):
        """Test that batch processing is efficient."""
        model_name, model_kwargs = model_spec

        # Create model
        if model_name == 'NextHeadSingle':
            model = NextHeadSingle(**model_kwargs)
        elif model_name == 'NextHeadHybrid':
            model = NextHeadHybrid(**model_kwargs)
        elif model_name == 'NextHeadGRU':
            model = NextHeadGRU(**model_kwargs)

        model.eval()

        # Test different batch sizes
        batch_sizes = [1, 32, 128]
        times = []

        for batch_size in batch_sizes:
            x = torch.randn(batch_size, 9, 64)

            # Warmup
            with torch.no_grad():
                _ = model(x)

            # Measure
            start_time = time.time()

            with torch.no_grad():
                for _ in range(50):
                    _ = model(x)

            end_time = time.time()
            avg_time = (end_time - start_time) / 50

            times.append(avg_time)

        # Larger batches should be more efficient per sample
        # Time per sample should decrease with batch size
        time_per_sample_small = times[0] / batch_sizes[0]
        time_per_sample_large = times[2] / batch_sizes[2]

        assert time_per_sample_large < time_per_sample_small, \
            f"{model_name}: Batch processing not efficient (small={time_per_sample_small:.6f}s, " \
            f"large={time_per_sample_large:.6f}s per sample)"


class TestTrainingEpochTime:
    """Tests for training epoch time benchmarks."""

    @pytest.fixture
    def training_setup(self):
        """Setup model, data, optimizer for training tests."""
        model = NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2, dropout=0.1
        )

        # Create synthetic dataset
        num_samples = 1000
        X = torch.randn(num_samples, 9, 64)
        y = torch.randint(0, 7, (num_samples,))

        dataset = TensorDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

        optimizer = optim.AdamW(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        return model, dataloader, optimizer, criterion

    def test_training_epoch_time(self, training_setup):
        """Test that one training epoch completes in reasonable time."""
        model, dataloader, optimizer, criterion = training_setup

        model.train()

        # Warmup epoch
        for X_batch, y_batch in dataloader:
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()

        # Measure epoch time
        start_time = time.time()

        for X_batch, y_batch in dataloader:
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()

        end_time = time.time()
        epoch_time = end_time - start_time

        # 1000 samples with batch_size=64 should complete in < 10 seconds on CPU
        assert epoch_time < 10.0, \
            f"Training epoch took {epoch_time:.2f}s (expected < 10s for 1000 samples)"

        print(f"\nTraining epoch time: {epoch_time:.2f}s for 1000 samples")

    def test_gradient_computation_time(self, training_setup):
        """Test that gradient computation is reasonably fast."""
        model, dataloader, optimizer, criterion = training_setup

        # Get one batch
        X_batch, y_batch = next(iter(dataloader))

        model.train()

        # Measure forward + backward time
        start_time = time.time()

        for _ in range(50):
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()

        end_time = time.time()
        avg_time_ms = (end_time - start_time) / 50 * 1000

        # Forward + backward should be < 200ms per batch
        assert avg_time_ms < 200, \
            f"Forward + backward takes {avg_time_ms:.2f}ms (expected < 200ms)"

        print(f"\nAvg forward + backward time: {avg_time_ms:.2f}ms")


class TestMemoryUsage:
    """Tests for memory consumption."""

    def get_memory_mb(self):
        """Get current process memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024

    @pytest.fixture
    def memory_baseline(self):
        """Record baseline memory before test."""
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return self.get_memory_mb()

    def test_model_memory_footprint(self, memory_baseline):
        """Test that model doesn't consume excessive memory."""
        # Create model
        model = NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2, dropout=0.1
        )

        # Memory after model creation
        memory_after_model = self.get_memory_mb()
        model_memory = memory_after_model - memory_baseline

        # Model should use < 50MB (typical: ~10-20MB for this size)
        assert model_memory < 50, \
            f"Model consumes {model_memory:.1f}MB (expected < 50MB)"

        print(f"\nModel memory footprint: {model_memory:.1f}MB")

    def test_forward_pass_memory(self, memory_baseline):
        """Test memory usage during forward pass."""
        model = NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2, dropout=0.1
        )

        model.eval()

        # Forward pass with batch
        x = torch.randn(128, 9, 64)

        with torch.no_grad():
            _ = model(x)

        memory_after_forward = self.get_memory_mb()
        total_memory = memory_after_forward - memory_baseline

        # Total memory (model + forward) should be < 100MB
        assert total_memory < 100, \
            f"Forward pass consumes {total_memory:.1f}MB (expected < 100MB)"

        print(f"\nTotal memory (model + forward): {total_memory:.1f}MB")

    def test_training_memory(self, memory_baseline):
        """Test memory usage during training."""
        model = NextHeadSingle(
            embed_dim=64, num_classes=7, num_heads=4,
            seq_length=9, num_layers=2, dropout=0.1
        )

        optimizer = optim.AdamW(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        model.train()

        # Training step
        x = torch.randn(64, 9, 64)
        y = torch.randint(0, 7, (64,))

        for _ in range(10):  # Multiple steps to stabilize memory
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()

        memory_after_training = self.get_memory_mb()
        total_memory = memory_after_training - memory_baseline

        # Training (model + optimizer + gradients) should be < 150MB
        assert total_memory < 150, \
            f"Training consumes {total_memory:.1f}MB (expected < 150MB)"

        print(f"\nTotal training memory: {total_memory:.1f}MB")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])  # -s to show print statements
