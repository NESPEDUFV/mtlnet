"""Tests for training progress bar utilities."""

import io
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

from utils.progress import TrainingProgressBar, zip_longest_cycle


def make_dl(n, batch_size=1):
    """Helper: create a DataLoader of length n with batch_size=batch_size."""
    return DataLoader(TensorDataset(torch.arange(n)), batch_size=batch_size)


class TestTrainingProgressBar:
    """Test suite for TrainingProgressBar."""

    def test_initialization(self):
        """Test progress bar initialization."""
        dl = make_dl(5)
        bar = TrainingProgressBar(10, [dl], file=io.StringIO())
        assert bar.num_epochs == 10
        assert bar.batches_per_epoch == 5
        assert bar.desc.startswith("Epoch 1/")
        bar.close()

    def test_single_dataloader(self):
        """Test zip_longest_cycle with a single dataloader of length 5."""
        dl = make_dl(5)
        it = zip_longest_cycle(dl)
        # Should produce 5 items (same as iterating the DL)
        items = list(it)
        assert len(items) == 5

    def test_multi_dataloader(self):
        """Test zip_longest_cycle with two dataloaders of lengths 3 and 5."""
        dl_short = make_dl(3)
        dl_long = make_dl(5)
        items = list(zip_longest_cycle(dl_short, dl_long))
        # Length == max(3, 5) == 5
        assert len(items) == 5
        # Each item is a tuple (batch_from_dl_short, batch_from_dl_long)
        for item in items:
            assert len(item) == 2

    def test_metric_updates(self):
        """Test updating metrics in progress bar."""
        dl = make_dl(3)
        bar = TrainingProgressBar(2, [dl], file=io.StringIO())
        bar.set_postfix(loss=0.5)
        assert "loss" in bar.metrics
        assert bar.metrics["loss"] == 0.5

        bar.set_postfix({"acc": 0.9})
        assert "acc" in bar.metrics
        assert bar.metrics["acc"] == 0.9
        bar.close()


class TestZipLongestCycle:
    """Test suite for zip_longest_cycle utility."""

    def test_equal_length_iterables(self):
        """Test with two dataloaders of equal length."""
        dl_a = make_dl(4)
        dl_b = make_dl(4)
        items = list(zip_longest_cycle(dl_a, dl_b))
        assert len(items) == 4
        for item in items:
            assert len(item) == 2

    def test_different_length_iterables(self):
        """Test [1,2,3] and [10,20] → 3 tuples, second list cycles."""
        dl_long = make_dl(3)
        dl_short = make_dl(2)
        items = list(zip_longest_cycle(dl_long, dl_short))
        assert len(items) == 3

    def test_cycling_behavior(self):
        """Test that shorter dataloader truly cycles (element repeats)."""
        dl_long = make_dl(4)
        dl_short = make_dl(2)
        items = list(zip_longest_cycle(dl_long, dl_short))
        # dl_short has 2 batches; cycling over 4 steps means it repeats
        assert len(items) == 4
        # Extract the tensors from the short dataloader column
        short_vals = [item[1][0].tolist() for item in items]
        # The first two values should repeat in the second two
        assert short_vals[:2] == short_vals[2:]


class TestF65MinSizeTruncate:
    """F65 — joint-dataloader cycling ablation. The min_size_truncate
    strategy stops at the shortest loader's end with no cycling."""

    def test_min_size_truncate_returns_min_length(self):
        dl_long = make_dl(5)
        dl_short = make_dl(3)
        items = list(
            zip_longest_cycle(dl_long, dl_short, strategy="min_size_truncate"))
        assert len(items) == 3

    def test_min_size_truncate_no_cycling(self):
        """No element from the longer loader past index 2 should appear,
        and the shorter loader should not be re-fed."""
        dl_long = make_dl(5)
        dl_short = make_dl(3)
        items = list(
            zip_longest_cycle(dl_long, dl_short, strategy="min_size_truncate"))
        long_vals = [item[0][0].item() for item in items]
        short_vals = [item[1][0].item() for item in items]
        assert long_vals == [0, 1, 2]
        assert short_vals == [0, 1, 2]

    def test_unknown_strategy_raises(self):
        dl = make_dl(3)
        with pytest.raises(ValueError, match="Unknown joint-loader strategy"):
            list(zip_longest_cycle(dl, dl, strategy="bogus"))

    def test_progress_bar_min_size_truncate_batches_per_epoch(self):
        dl_long = make_dl(5)
        dl_short = make_dl(3)
        bar = TrainingProgressBar(
            2, [dl_long, dl_short],
            joint_loader_strategy="min_size_truncate",
            file=io.StringIO(),
        )
        assert bar.batches_per_epoch == 3
        bar.close()
