"""Training progress bar with multi-dataloader support."""
import time
from contextlib import contextmanager
from datetime import timedelta
from itertools import cycle
from typing import Iterator, List

from torch.utils.data import DataLoader
from tqdm import tqdm


def zip_longest_cycle(
    *dataloaders: DataLoader,
    strategy: str = "max_size_cycle",
) -> Iterator:
    """Zip dataloaders by joint-loader strategy.

    Strategies (F50 F65 — joint-dataloader cycling ablation):
      * ``max_size_cycle`` (default, legacy): cycle shorter loaders to match
        the longest. Number of joint batches = max(lengths). Synthetic
        re-passes happen on the shorter loader within the same epoch.
      * ``min_size_truncate``: stop at the shortest loader's end. No
        cycling at all. Number of joint batches = min(lengths). Tests
        whether the F50 D5/F50 T3 reg-saturation artifact is driven by
        joint-loader cycling repeatedly re-feeding reg samples.

    The legacy strategy is retained as default so all pre-F65 callers
    keep their semantics bit-exactly.
    """
    if not dataloaders:
        return iter([])

    if len(dataloaders) == 1:
        return iter(dataloaders[0])

    if strategy == "max_size_cycle":
        max_len = max(len(dl) for dl in dataloaders)
        iterators = [
            cycle(dl) if len(dl) < max_len else iter(dl)
            for dl in dataloaders
        ]
        return zip(*iterators)
    if strategy == "min_size_truncate":
        # No cycling; iterate naturally and stop when the shortest loader
        # is exhausted. Equivalent to plain ``zip(*loaders)``.
        return zip(*[iter(dl) for dl in dataloaders])
    raise ValueError(
        f"Unknown joint-loader strategy '{strategy}'; "
        f"expected one of {{'max_size_cycle', 'min_size_truncate'}}"
    )


class TrainingProgressBar(tqdm):
    """Extended tqdm progress bar for training loops."""

    def __init__(
        self,
        num_epochs: int,
        dataloaders: List[DataLoader],
        joint_loader_strategy: str = "max_size_cycle",
        **kwargs,
    ):
        self.num_epochs = num_epochs
        self.dataloaders = dataloaders
        self.joint_loader_strategy = str(joint_loader_strategy)
        if self.joint_loader_strategy == "min_size_truncate":
            self.batches_per_epoch = min(len(dl) for dl in dataloaders)
        else:
            self.batches_per_epoch = max(len(dl) for dl in dataloaders)

        self.epoch_start_time = None
        self.current_epoch = 0
        self.metrics = {}

        super().__init__(
            total=self.batches_per_epoch * num_epochs,
            unit="batch",
            desc=f"Epoch 1/{num_epochs}",
            **kwargs
        )

    def __iter__(self) -> Iterator[int]:
        """Iterate over epochs."""
        for epoch_idx in range(self.num_epochs):
            self.epoch_start_time = time.time()
            self.current_epoch = epoch_idx
            self.set_description(f"Epoch {epoch_idx + 1}/{self.num_epochs}")
            yield epoch_idx
            self.write("")

    def iter_epoch(self) -> Iterator:
        """Iterate over batches in current epoch using configured strategy."""
        for data in zip_longest_cycle(
            *self.dataloaders, strategy=self.joint_loader_strategy,
        ):
            yield data
            self.update(1)

    @contextmanager
    def validation(self):
        """Context manager for validation phase."""
        self.set_description(f"Epoch {self.current_epoch + 1}/{self.num_epochs} [Validating]")
        try:
            yield self
        finally:
            elapsed = timedelta(seconds=int(time.time() - self.epoch_start_time))
            self.set_description(f"Epoch {self.current_epoch + 1}/{self.num_epochs} [{elapsed}]")

    def set_postfix(self, ordered_dict=None, **kwargs):
        """Update metrics and display."""
        self.metrics.update(ordered_dict or {})
        self.metrics.update(kwargs)
        super().set_postfix(**self.metrics)
        return self