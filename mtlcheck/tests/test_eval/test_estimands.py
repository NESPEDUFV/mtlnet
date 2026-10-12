"""The metrics, from rows. One implementation, so these tests are the definition.

Every number the protocol reports comes through `eval/estimands.py`. The training loop keeps its own
streaming metric for checkpoint selection, and that one never reports — so these two implementations
are allowed to coexist only because they answer different questions. Where they overlap, this file
pins the overlap.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mtlcheck.eval import estimands


def _rows(y_true, y_pred=None, ranks=None, users=None, folds=None) -> pd.DataFrame:
    n = len(y_true)
    return pd.DataFrame({
        "userid": np.arange(n) if users is None else np.asarray(users),
        "fold": np.zeros(n, dtype=int) if folds is None else np.asarray(folds),
        "y_true": np.asarray(y_true),
        "y_pred": np.asarray(y_true if y_pred is None else y_pred),
        "rank_of_true": np.ones(n, dtype=int) if ranks is None else np.asarray(ranks),
    })


def test_macro_f1_matches_sklearn_on_the_pinned_convention() -> None:
    """The convention is pinned against a reference implementation, not against itself.

    Two non-equivalent definitions of macro-F1 circulate (Opitz & Burst 2019). This asserts the one
    the protocol chose: per-class F1 from pooled counts, averaged unweighted, zero for a class with
    no support and no predictions.
    """
    sklearn_metrics = pytest.importorskip("sklearn.metrics")

    rng = np.random.default_rng(3)
    y_true = rng.integers(0, 7, 500)
    y_pred = np.where(rng.random(500) < 0.6, y_true, rng.integers(0, 7, 500))

    ours = estimands.macro_f1(estimands.category_counts(_rows(y_true, y_pred), 7))
    theirs = sklearn_metrics.f1_score(y_true, y_pred, average="macro", zero_division=0)
    assert ours == pytest.approx(theirs, abs=1e-12)


def test_pooling_differs_from_averaging_folds_under_imbalance() -> None:
    """The estimand choice, pinned as a number rather than asserted in prose.

    The protocol requires pooled out-of-fold because the mean of per-fold macro-F1 is biased under
    class imbalance: a rare class missing from one fold contributes a 0 to that fold's mean instead
    of pooling its counts. If this test ever passes with equality, the estimand distinction has
    silently stopped mattering and §1 of the protocol needs re-reading.
    """
    rng = np.random.default_rng(11)
    n = 600
    # class 6 is rare and concentrated in one fold, which is what creates the divergence
    y_true = np.where(rng.random(n) < 0.03, 6, rng.integers(0, 5, n))
    y_pred = np.where(rng.random(n) < 0.7, y_true, rng.integers(0, 6, n))
    folds = np.repeat(np.arange(5), n // 5)

    frame = _rows(y_true, y_pred, folds=folds, users=np.arange(n))
    pooled = estimands.pooled_metric(frame, "cat", num_classes=7)
    averaged = estimands.mean_of_folds(frame, "cat", num_classes=7)

    assert pooled != pytest.approx(averaged, abs=1e-6), (
        "pooling and fold-averaging returned the same value; the fixture no longer exercises the "
        "imbalance that makes them differ")


def test_top_k_counts_every_row_including_unreachable_targets() -> None:
    """`top10_raw` is deployment-faithful: a row the model cannot get right is still a row."""
    ranks = np.array([1, 5, 10, 11, 999])
    frame = _rows(np.arange(5), ranks=ranks, users=np.arange(5))
    assert estimands.top_k_accuracy(estimands.region_counts(frame, k=10)) == pytest.approx(3 / 5)


def test_the_ood_hit_rate_is_a_leak_canary() -> None:
    """A never-trained region ranking top-10 of thousands means the label leaked."""
    y_true = np.array([0, 1, 2, 3])
    ranks = np.array([1, 1, 1, 1])          # everything ranks first, including the unseen labels
    frame = _rows(y_true, ranks=ranks, users=np.arange(4))

    counts = estimands.region_counts(frame, k=10, train_labels=frozenset({0, 1}))
    diagnostics = estimands.ood_diagnostics(counts)

    assert diagnostics["ood_fraction"] == pytest.approx(0.5)
    assert diagnostics["ood_hit_rate"] == pytest.approx(1.0), (
        "two of four rows had targets absent from training and both ranked first — the canary must "
        "read 1.0, which is the signature the protocol fails a run on")


def test_counts_are_additive_over_users() -> None:
    """The property that makes the bootstrap a dot product rather than a rescan."""
    rng = np.random.default_rng(5)
    y_true = rng.integers(0, 7, 300)
    y_pred = np.where(rng.random(300) < 0.5, y_true, rng.integers(0, 7, 300))
    users = rng.integers(0, 40, 300)
    frame = _rows(y_true, y_pred, users=users)

    counts = estimands.category_counts(frame, 7)
    weights = np.ones(len(counts.users))
    assert estimands.macro_f1(counts, weights) == pytest.approx(estimands.macro_f1(counts))

    # Doubling every user must leave a ratio metric unchanged.
    assert estimands.macro_f1(counts, 2 * weights) == pytest.approx(estimands.macro_f1(counts))


def test_rows_reproduce_the_training_time_metric() -> None:
    """The contract's whole point: the persisted rows must reconstruct the number the run reported.

    Verified end to end on the A40 (alabama, cat, fold 1): the training loop reported macro-F1
    31.9452 and `pooled_metric` over the 19 265 persisted rows returns 31.9452. Two independent
    implementations — the streaming accumulator that decides checkpoints and the pooled estimand that
    reports — agreeing to the fourth decimal is what licenses stage 2 to never re-train.

    This test pins the property on synthetic data, since the A40 artifact is not committed.
    """
    rng = np.random.default_rng(17)
    n = 4000
    y_true = rng.integers(0, 7, n)
    y_pred = np.where(rng.random(n) < 0.45, y_true, rng.integers(0, 7, n))
    frame = _rows(y_true, y_pred, users=rng.integers(0, 300, n))

    from_rows = estimands.pooled_metric(frame, "cat", num_classes=7)
    counts = estimands.category_counts(frame, 7)
    from_counts = float(estimands.per_class_f1(counts).mean())
    assert from_rows == pytest.approx(from_counts, abs=1e-12), (
        "the macro average and the per-class vector must come from the same pooled counts")


def test_the_inner_split_is_user_disjoint_and_leaves_the_outer_fold_untouched() -> None:
    """Protocol §2: 70/10/20, and the outer fold must be byte-identical to the legacy one.

    If carving the inner set changed the outer fold, the sealed protocol would not be comparable to
    the legacy numbers at all, and the bridge that measures the selection bias would be measuring
    two changes at once.
    """
    from mtlcheck.data import splits

    rng = np.random.default_rng(0)
    y = rng.integers(0, 7, 6000)
    users = rng.integers(0, 600, 6000)

    legacy = splits.build(y, users, split_seed=0)
    sealed = splits.build_inner(legacy, y, users, inner_split_seed=99)

    for before, after in zip(legacy, sealed):
        assert np.array_equal(before.val, after.val), "the outer fold moved"
        assert after.sealed and not before.sealed
        assert len(np.intersect1d(np.unique(users[after.train]),
                                  np.unique(users[after.inner_val]))) == 0
        total = len(after.train) + len(after.inner_val) + len(after.val)
        assert 0.08 < len(after.inner_val) / total < 0.13, "inner set should be ~10% of rows"


def test_the_inner_seed_is_independent_of_the_outer_seed() -> None:
    """Two integers, two partitions — the confound NOMENCLATURE §1 exists to prevent."""
    from mtlcheck.data import splits

    rng = np.random.default_rng(1)
    y = rng.integers(0, 7, 4000)
    users = rng.integers(0, 400, 4000)
    legacy = splits.build(y, users, split_seed=0)

    a = splits.build_inner(legacy, y, users, inner_split_seed=1)
    b = splits.build_inner(legacy, y, users, inner_split_seed=2)

    assert not np.array_equal(a[0].inner_val, b[0].inner_val), "the inner seed did nothing"
    assert np.array_equal(a[0].val, b[0].val), "the inner seed must not move the outer fold"


def test_both_runners_select_on_the_inner_split_when_sealed() -> None:
    """The joint arm must be sealed too, or a joint-vs-STL comparison is rigged.

    While the dedicated runner selected on the inner split, the joint runner still validated on the
    outer fold. That is worse than leaving both on the legacy rule: it puts an optimistic arm
    against unbiased ones and inflates the joint's advantage by the selection bias, measured at
    ~0.66 pp on one Alabama fold against a 0.4 pp equivalence margin.

    Asserted on the source, because the alternative is a full joint training run in a unit suite.
    """
    from pathlib import Path

    runner_source = (Path(__file__).resolve().parents[2]
                     / "src" / "mtlcheck" / "train" / "runner.py").read_text()

    assert "dataset.joint_selection_streams" in runner_source, (
        "the joint runner does not build a selection stream — it is still scoring epochs on the "
        "outer fold")
    joint_body = runner_source[runner_source.index("def train_joint_fold"):]
    epoch_call = joint_body[:joint_body.index("_validate_joint(") + 400]
    assert "cat_eval, reg_eval" in epoch_call, (
        "the joint epoch loop must validate on the selection streams, not on cat_val/reg_val")
