"""Synthetic tests for the AUDIT-C1 fix in ``p1_region_head_ablation``.

Audit finding C1 (`F50_T3_AUDIT_FINDINGS.md`): the STL per-fold trainer
selected by ``top10_acc`` and reported every other metric at THAT
epoch. Mirror image of the MTL F1-vs-top10 mismatch — biased every
MTL-vs-STL paired comparison by 3-4 pp.

The fix introduces ``_new_per_metric_tracker`` /
``_update_per_metric_best`` which track each canonical metric's best
epoch independently, attached to the legacy output as
``per_metric_best``. These tests pin the contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_REPO / "scripts"))

from p1_region_head_ablation import (
    CANONICAL_METRICS,
    _new_per_metric_tracker,
    _update_per_metric_best,
)


def test_tracker_initial_state():
    t = _new_per_metric_tracker()
    assert set(t.keys()) == set(CANONICAL_METRICS)
    for m in CANONICAL_METRICS:
        assert t[m]["value"] == -1.0
        assert t[m]["snapshot"] == {}


def test_tracker_records_first_epoch_for_every_metric():
    t = _new_per_metric_tracker()
    metrics = {"accuracy": 0.5, "top5_acc": 0.6, "top10_acc": 0.7, "mrr": 0.55, "f1": 0.4}
    _update_per_metric_best(t, metrics, epoch=1)
    for m in CANONICAL_METRICS:
        assert t[m]["value"] == metrics[m]
        assert t[m]["snapshot"]["best_epoch"] == 1


def test_tracker_keeps_best_per_metric_independently():
    """Core C1 mechanism: two metrics may peak at DIFFERENT epochs.
    Pre-fix, STL collapsed to a single "top10-best" snapshot for all
    metrics. Post-fix, each metric tracks its own best."""
    t = _new_per_metric_tracker()

    # Epoch 1 — top10 peaks here
    _update_per_metric_best(
        t, {"accuracy": 0.50, "top5_acc": 0.60, "top10_acc": 0.85, "mrr": 0.55, "f1": 0.30},
        epoch=1,
    )
    # Epoch 2 — F1 / accuracy / top5 / mrr peak here
    _update_per_metric_best(
        t, {"accuracy": 0.55, "top5_acc": 0.65, "top10_acc": 0.83, "mrr": 0.58, "f1": 0.40},
        epoch=2,
    )

    assert t["top10_acc"]["value"] == 0.85
    assert t["top10_acc"]["snapshot"]["best_epoch"] == 1

    # The F1 reported at top10-best epoch (legacy bug) was 0.30; the
    # actual F1 max is 0.40 at a DIFFERENT epoch.
    assert t["f1"]["value"] == 0.40
    assert t["f1"]["snapshot"]["best_epoch"] == 2

    assert t["accuracy"]["snapshot"]["best_epoch"] == 2
    assert t["mrr"]["snapshot"]["best_epoch"] == 2

    # The MTL bug magnitude direction: F1 at top10-best ≠ F1's actual peak
    f1_at_top10_best = t["top10_acc"]["snapshot"]["f1"]
    f1_at_f1_best = t["f1"]["snapshot"]["f1"]
    assert f1_at_f1_best > f1_at_top10_best


def test_tracker_handles_missing_keys_gracefully():
    """If a metric is missing from the dict, default to 0.0 (won't
    overwrite a positive best). Defensive: in case downstream
    compute_classification_metrics ever drops a key."""
    t = _new_per_metric_tracker()
    _update_per_metric_best(t, {"accuracy": 0.7, "f1": 0.6}, epoch=1)
    assert t["accuracy"]["value"] == 0.7
    assert t["f1"]["value"] == 0.6
    # Missing keys: top10_acc, top5_acc, mrr → got 0.0, which beats -1.0
    assert t["top10_acc"]["value"] == 0.0
    assert t["top10_acc"]["snapshot"]["best_epoch"] == 1


def test_tracker_no_overwrite_on_lower_value():
    t = _new_per_metric_tracker()
    _update_per_metric_best(t, {"f1": 0.8}, epoch=1)
    _update_per_metric_best(t, {"f1": 0.5}, epoch=2)
    assert t["f1"]["value"] == 0.8
    assert t["f1"]["snapshot"]["best_epoch"] == 1
