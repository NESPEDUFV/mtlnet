"""Contract tests for ``training.runners.mtl_eval.evaluate_model``.

Focuses on the post-review regression: the MTL validation pass must return
per-task losses inside the per-task metric dicts so ``mtl_cv.py`` can
forward them to ``fold_history.log_val('next', **metrics, ...)`` without
hand-wiring ``loss=...``. Previously the per-task stores recorded
``loss=0`` for every epoch, which silently stripped the validation loss
signal from ``fold{i}_{task}_val.csv``.
"""

from __future__ import annotations

import pytest
import torch
import torch.nn as nn

from training.runners.mtl_eval import evaluate_model


class _FakeMTL(nn.Module):
    """Minimal two-head model mimicking MTLnet's forward signature."""

    def __init__(self, embed_dim: int = 4, num_classes: int = 3) -> None:
        super().__init__()
        self.num_classes = num_classes
        self.cat_head = nn.Linear(embed_dim, num_classes)
        # Next head eats sequences; flatten inside forward to keep the
        # test plumbing trivial.
        self.next_head = nn.Linear(embed_dim, num_classes)

    def forward(self, inputs):
        x_cat, x_next = inputs
        if x_next.ndim == 3:
            x_next = x_next.mean(dim=1)  # collapse sequence dim
        return self.cat_head(x_cat), self.next_head(x_next)


def _make_loader(n: int, shape, num_classes: int, seed: int):
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(n, *shape, generator=g)
    y = torch.randint(0, num_classes, (n,), generator=g)
    return torch.utils.data.DataLoader(
        list(zip(x, y)), batch_size=4, shuffle=False
    )


class TestEvaluateModelContract:

    @pytest.fixture
    def setup(self):
        torch.manual_seed(0)
        embed_dim = 4
        num_classes = 3
        model = _FakeMTL(embed_dim=embed_dim, num_classes=num_classes)
        model.eval()

        cat_loader = _make_loader(16, (embed_dim,), num_classes, seed=1)
        next_loader = _make_loader(12, (2, embed_dim), num_classes, seed=2)

        criterion = nn.CrossEntropyLoss()
        return model, [next_loader, cat_loader], criterion

    def test_per_task_loss_is_inside_metric_dict(self, setup):
        model, loaders, criterion = setup
        metrics_next, metrics_cat, loss_combined = evaluate_model(
            model, loaders, criterion, criterion, None, torch.device("cpu"),
        )

        # Per-task loss keys present and strictly positive (cross-entropy
        # on random weights can't be zero on non-empty batches).
        assert "loss" in metrics_next
        assert "loss" in metrics_cat
        assert metrics_next["loss"] > 0.0
        assert metrics_cat["loss"] > 0.0

    def test_combined_loss_is_mean_of_per_task_losses(self, setup):
        model, loaders, criterion = setup
        metrics_next, metrics_cat, loss_combined = evaluate_model(
            model, loaders, criterion, criterion, None, torch.device("cpu"),
        )
        # combined_loss = mean over batches of (next + cat) / 2.
        # When both running sums share the same denominator that reduces
        # to the same as (mean(next) + mean(cat)) / 2.
        expected = (metrics_next["loss"] + metrics_cat["loss"]) / 2
        assert loss_combined == pytest.approx(expected, rel=1e-6)

    def test_metric_dict_contains_classification_keys(self, setup):
        model, loaders, criterion = setup
        metrics_next, metrics_cat, _ = evaluate_model(
            model, loaders, criterion, criterion, None, torch.device("cpu"),
        )
        for d in (metrics_next, metrics_cat):
            for key in ("loss", "accuracy", "accuracy_macro", "f1",
                        "f1_weighted", "mrr", "top3_acc", "ndcg_3"):
                assert key in d, f"missing {key}"
                assert isinstance(d[key], float)


class TestTrainFallbackSchemaStability:
    """Regression: ``_single_task_train``'s ``compute_train_f1=False``
    fallback must still emit an ``f1`` key (=0.0) so
    ``fold{i}_{task}_train.csv`` columns stay stable across runs with and
    without ``compute_train_f1``."""

    def test_fallback_train_store_has_f1_key(self):
        from training.runners._single_task_train import train_single_task
        from tracking.fold import FoldHistory

        torch.manual_seed(0)
        embed_dim = 4
        num_classes = 3
        model = nn.Linear(embed_dim, num_classes)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)

        train_loader = _make_loader(16, (embed_dim,), num_classes, seed=3)
        val_loader = _make_loader(8, (embed_dim,), num_classes, seed=4)

        fold = FoldHistory.standalone(tasks={"next"})
        fold.start()

        train_single_task(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            criterion=criterion,
            optimizer=optimizer,
            scheduler=None,
            device=torch.device("cpu"),
            history=fold,
            task_name="next",
            num_classes=num_classes,
            epochs=1,
            compute_train_f1=False,  # exercise the fallback branch
        )
        fold.end()

        train_keys = set(fold.task("next").train.keys())
        assert "f1" in train_keys, (
            "compute_train_f1=False must still log f1 (as 0.0) for CSV "
            f"schema stability; got keys={train_keys}"
        )
        assert "accuracy" in train_keys
        assert "loss" in train_keys
        # And f1 is exactly 0.0 when compute_train_f1 is off.
        assert fold.task("next").train["f1"] == [0.0]
