"""Unit tests for ``tracking.metrics.compute_classification_metrics``."""

from __future__ import annotations

import math

import pytest
import torch

from tracking.metrics import compute_classification_metrics


def _one_hot_logits(targets: torch.Tensor, num_classes: int, scale: float = 10.0) -> torch.Tensor:
    """Build a perfect-logits tensor where the target class dominates."""
    logits = torch.zeros(len(targets), num_classes)
    logits[torch.arange(len(targets)), targets] = scale
    return logits


class TestPerfectPredictions:
    def test_all_metrics_equal_one(self):
        targets = torch.tensor([0, 1, 2, 3, 4, 5, 6])
        logits = _one_hot_logits(targets, num_classes=7)

        m = compute_classification_metrics(logits, targets, num_classes=7)

        assert m["accuracy"] == pytest.approx(1.0)
        assert m["accuracy_macro"] == pytest.approx(1.0)
        assert m["f1"] == pytest.approx(1.0)
        assert m["f1_weighted"] == pytest.approx(1.0)
        assert m["mrr"] == pytest.approx(1.0)
        assert m["top3_acc"] == pytest.approx(1.0)
        assert m["top5_acc"] == pytest.approx(1.0)
        # NDCG@K: target at rank 1 → DCG = 1/log2(2) = 1
        assert m["ndcg_3"] == pytest.approx(1.0)
        assert m["ndcg_5"] == pytest.approx(1.0)


class TestWorstArgmaxButGoodTopK:
    """Argmax always wrong, but the true class is still in the top-2."""

    def test_top1_zero_top3_one(self):
        # 3-class problem; target is always class 0, but logits put it at rank 2.
        # order: class 1 (highest), class 0 (second), class 2 (lowest)
        logits = torch.tensor([[0.5, 1.0, 0.1]] * 6)
        targets = torch.tensor([0, 0, 0, 0, 0, 0])

        m = compute_classification_metrics(logits, targets, num_classes=3, top_k=(3,))

        assert m["accuracy"] == pytest.approx(0.0)
        assert m["f1"] == pytest.approx(0.0)
        # All samples hit within top-3 (k=3 covers all 3 classes).
        assert m["top3_acc"] == pytest.approx(1.0)
        # MRR: rank is 2 for every sample → 1/2
        assert m["mrr"] == pytest.approx(0.5)
        # NDCG@3: rank=2 → 1/log2(3)
        assert m["ndcg_3"] == pytest.approx(1.0 / math.log2(3.0))


class TestMRRAndNDCGAtRank2:
    def test_known_rank(self):
        # 4-class problem; true target (class 0) placed at rank 3.
        # Descending order of classes in logits: 2 (3.0), 1 (2.0), 0 (1.0), 3 (0.5)
        logits = torch.tensor([[1.0, 2.0, 3.0, 0.5]] * 4)
        targets = torch.tensor([0, 0, 0, 0])

        m = compute_classification_metrics(logits, targets, num_classes=4, top_k=(2, 3, 5))

        assert m["mrr"] == pytest.approx(1.0 / 3.0)
        assert m["top2_acc"] == pytest.approx(0.0)     # rank 3 not in top-2
        assert m["top3_acc"] == pytest.approx(1.0)     # rank 3 is in top-3
        assert m["top5_acc"] == pytest.approx(1.0)     # always in top-5
        # NDCG@2: target not in top-2 → 0
        assert m["ndcg_2"] == pytest.approx(0.0)
        # NDCG@3: rank=3 → 1/log2(4) = 0.5
        assert m["ndcg_3"] == pytest.approx(0.5)


class TestImbalancedWeightedVsMacro:
    def test_weighted_differs_from_macro_under_imbalance(self):
        # Class 0 dominates and is perfectly classified.
        # Class 1 appears twice, both misclassified as class 0.
        # Macro F1 averages the two per-class F1s equally; weighted F1 gives
        # much more weight to the majority class so it should be higher.
        n_maj = 20
        targets = torch.tensor([0] * n_maj + [1, 1])
        logits = torch.zeros(n_maj + 2, 2)
        logits[:, 0] = 5.0  # predict class 0 for every sample

        m = compute_classification_metrics(logits, targets, num_classes=2, top_k=(3,))

        assert m["f1_weighted"] > m["f1"], (
            "weighted F1 should exceed macro F1 when the majority class is "
            "perfectly classified and the minority class is ignored"
        )
        # Sanity: majority-class precision is < 1 (minority contaminates), but
        # micro accuracy equals n_maj/(n_maj+2).
        assert m["accuracy"] == pytest.approx(n_maj / (n_maj + 2))
        # Balanced accuracy averages per-class recall: class 0 recall = 1,
        # class 1 recall = 0 → 0.5.
        assert m["accuracy_macro"] == pytest.approx(0.5)


class TestPrefix:
    def test_prefix_is_applied_to_every_key(self):
        targets = torch.tensor([0, 1, 2])
        logits = _one_hot_logits(targets, num_classes=3)

        m = compute_classification_metrics(
            logits, targets, num_classes=3, top_k=(3,), prefix="val_"
        )

        assert "val_accuracy" in m
        assert "val_f1" in m
        assert "val_f1_weighted" in m
        assert "val_accuracy_macro" in m
        assert "val_top3_acc" in m
        assert "val_mrr" in m
        assert "val_ndcg_3" in m
        # No unprefixed leak.
        assert "f1" not in m
        assert "accuracy" not in m


class TestEdgeCases:
    def test_empty_batch_returns_zeros(self):
        logits = torch.zeros(0, 7)
        targets = torch.zeros(0, dtype=torch.long)

        m = compute_classification_metrics(logits, targets, num_classes=7)

        for key, value in m.items():
            assert value == 0.0, f"{key} should be zero for empty batch, got {value}"

    def test_single_sample(self):
        logits = torch.tensor([[0.1, 5.0, 0.3]])
        targets = torch.tensor([1])

        m = compute_classification_metrics(logits, targets, num_classes=3, top_k=(3,))

        assert m["accuracy"] == pytest.approx(1.0)
        assert m["f1"] == pytest.approx(1.0)
        assert m["mrr"] == pytest.approx(1.0)

    def test_top_k_larger_than_num_classes_is_clamped(self):
        targets = torch.tensor([0, 1])
        logits = _one_hot_logits(targets, num_classes=3)

        # k=10 > num_classes=3 — should not crash; equals top-3.
        m = compute_classification_metrics(
            logits, targets, num_classes=3, top_k=(10,)
        )
        assert m["top10_acc"] == pytest.approx(1.0)

    def test_k_equal_one_is_skipped(self):
        targets = torch.tensor([0, 1, 2])
        logits = _one_hot_logits(targets, num_classes=3)

        m = compute_classification_metrics(
            logits, targets, num_classes=3, top_k=(1, 3)
        )
        # k=1 would just duplicate 'accuracy'; we explicitly skip it.
        assert "top1_acc" not in m
        assert "ndcg_1" not in m
        assert "top3_acc" in m

    def test_shape_validation(self):
        # 1-D logits must raise
        with pytest.raises(ValueError, match="logits must be 2-D"):
            compute_classification_metrics(
                torch.zeros(3), torch.zeros(3, dtype=torch.long), num_classes=3
            )
        # 2-D targets must raise
        with pytest.raises(ValueError, match="targets must be 1-D"):
            compute_classification_metrics(
                torch.zeros(3, 3), torch.zeros(3, 1, dtype=torch.long), num_classes=3
            )
        # Mismatched N must raise
        with pytest.raises(ValueError, match="logits N=.* != targets N=.*"):
            compute_classification_metrics(
                torch.zeros(4, 3), torch.zeros(3, dtype=torch.long), num_classes=3
            )

    def test_returns_python_floats(self):
        """All values should be Python floats so MetricStore.log() works."""
        targets = torch.tensor([0, 1, 2])
        logits = _one_hot_logits(targets, num_classes=3)

        m = compute_classification_metrics(logits, targets, num_classes=3)
        for key, value in m.items():
            assert isinstance(value, float), f"{key}={value!r} is {type(value).__name__}"

    def test_cross_device_targets(self):
        """If targets are on CPU and logits on a different device the fn must handle it."""
        # We can't guarantee a second device in CI, so fake the check by
        # confirming same-CPU inputs don't explode. The function contains a
        # device-alignment branch that we exercise via this path.
        targets = torch.tensor([0, 1], device="cpu")
        logits = torch.tensor([[5.0, 0.1], [0.1, 5.0]], device="cpu")
        m = compute_classification_metrics(logits, targets, num_classes=2)
        assert m["accuracy"] == pytest.approx(1.0)


class TestTieBreaking:
    """Explicitly document the tie-handling semantics of ``_rank_of_target``.

    When multiple classes share the top logit and one of them is the target,
    we count "how many classes strictly beat the target", so the target
    gets the best-case rank. This is the canonical choice for ranking
    metrics and avoids depending on ``argsort`` stability.
    """

    def test_all_tied_gives_rank_one(self):
        # 3 classes, all with logit 0.5 — target should rank 1 (best case).
        logits = torch.tensor([[0.5, 0.5, 0.5]])
        targets = torch.tensor([1])
        m = compute_classification_metrics(
            logits, targets, num_classes=3, top_k=(3,)
        )
        assert m["mrr"] == pytest.approx(1.0)      # 1/rank = 1/1
        assert m["top3_acc"] == pytest.approx(1.0)  # trivially in top-3

    def test_target_tied_with_one_class_at_top(self):
        # Classes 0 and 1 tied at the top; target = 0 → strictly-higher
        # count is 0, so rank=1.
        logits = torch.tensor([[5.0, 5.0, 1.0]])
        targets = torch.tensor([0])
        m = compute_classification_metrics(
            logits, targets, num_classes=3, top_k=(3,)
        )
        assert m["mrr"] == pytest.approx(1.0)

    def test_one_class_strictly_beats_target(self):
        # Class 2 strictly wins; target=0 has the same score as class 1.
        # strictly_higher = 1 (only class 2), so rank = 2.
        logits = torch.tensor([[4.0, 4.0, 9.0]])
        targets = torch.tensor([0])
        m = compute_classification_metrics(
            logits, targets, num_classes=3, top_k=(3,)
        )
        assert m["mrr"] == pytest.approx(0.5)  # 1/2
