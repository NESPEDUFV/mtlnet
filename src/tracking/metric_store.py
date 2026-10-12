from __future__ import annotations

from typing import Any

import pandas as pd


class MetricStore:
    """Dict-of-lists metric container. Accepts arbitrary metric names.

    Usage:
        store = MetricStore()
        store.log(loss=0.5, accuracy=0.9)
        store.log(loss=0.3, accuracy=0.95)
        store['loss']        # [0.5, 0.3]
        store.latest('loss') # 0.3
        store.best('accuracy') # (1, 0.95)
    """

    def __init__(self):
        self._data: dict[str, list[float]] = {}

    def log(self, **kwargs: float) -> None:
        """Log one epoch's worth of metrics."""
        for key, value in kwargs.items():
            self._data.setdefault(key, []).append(value)

    def __getitem__(self, key: str) -> list[float]:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> list[float] | None:
        return self._data.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def __len__(self) -> int:
        return len(self._data)

    def latest(self, key: str) -> float:
        """Get the most recent value for a metric."""
        return self._data[key][-1]

    def best(self, key: str, mode: str = 'max') -> tuple[int, float]:
        """Return (epoch_index, value) of the best value for a metric.

        Args:
            key: Metric name.
            mode: 'max' or 'min'.
        """
        vals = self._data[key]
        if mode == 'max':
            best_val = max(vals)
        else:
            best_val = min(vals)
        best_idx = vals.index(best_val)
        return best_idx, best_val

    def num_epochs(self) -> int:
        """Number of epochs recorded (length of longest series)."""
        if not self._data:
            return 0
        return max(len(v) for v in self._data.values())

    def to_dataframe(self) -> pd.DataFrame:
        """Export to pandas DataFrame with an epoch column."""
        n = self.num_epochs()
        return pd.DataFrame({'epoch': range(1, n + 1), **self._data})
