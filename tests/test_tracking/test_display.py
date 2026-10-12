"""Regression tests for src/tracking/display.py.

Coverage focus: the `_safe_stdev` helper that unblocks `--folds 1` runs.
The original `statistics.stdev` call in `display.py:end_training` raised
`StatisticsError("stdev requires at least two data points")` on single-fold
training, crashing the entire end-of-training summary display. This module
pins the contract so a future refactor cannot silently regress it.
"""
import statistics

import pytest

from tracking.display import _safe_stdev


class TestSafeStdev:
    """Regression coverage for the single-fold display bug."""

    def test_single_element_returns_zero(self):
        # The exact failure mode from --folds 1 runs: a metric list with
        # one observation. statistics.stdev() raises here; _safe_stdev
        # must return 0.0.
        assert _safe_stdev([0.5]) == 0.0

    def test_empty_returns_zero(self):
        # Defensive: even an empty list (theoretically possible if a fold
        # had no validation predictions) must not raise.
        assert _safe_stdev([]) == 0.0

    def test_two_elements_matches_stdev(self):
        # Two-point case: must delegate to statistics.stdev to preserve
        # the existing multi-fold display numbers byte-for-byte.
        xs = [0.4, 0.6]
        assert _safe_stdev(xs) == pytest.approx(statistics.stdev(xs))

    def test_many_elements_matches_stdev(self):
        # Five-fold case (the canonical CV configuration). Multi-fold
        # behavior must be unchanged from the original `stdev()` path.
        xs = [0.41, 0.43, 0.42, 0.45, 0.44]
        assert _safe_stdev(xs) == pytest.approx(statistics.stdev(xs))

    def test_does_not_raise_for_single_element(self):
        # The headline regression: previously this raised
        # statistics.StatisticsError. Make the no-raise contract explicit.
        try:
            _safe_stdev([0.123])
        except statistics.StatisticsError as exc:
            pytest.fail(f"_safe_stdev should not raise on single element, raised: {exc}")
