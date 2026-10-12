"""E9 — metrics and epoch selection against the reference implementations.

Two things are being established here. First, the usual: identical numbers from independently
written code. Second, and specific to this module, that **dropping the reference's dual metric
path is safe** — it computes low-cardinality metrics with torchmetrics and high-cardinality ones
with a hand-rolled accumulator, and this keeps only the second. That simplification is only
legitimate if the two agree at the category head's C=7, so that is asserted directly rather than
argued.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

from ._old_repo import OLD_REPO

OLD_SRC = OLD_REPO / "src"


@pytest.fixture(scope="module")
def old_metrics():
    if not OLD_SRC.exists():
        pytest.skip(f"reference repo absent: {OLD_SRC}")
    if str(OLD_SRC) not in sys.path:
        sys.path.insert(0, str(OLD_SRC))
    try:
        from tracking import metrics as reference
    except Exception as exc:                                   # pragma: no cover
        pytest.skip(f"reference metrics not importable: {exc}")
    return reference


def _logits_and_targets(n: int, c: int, seed: int = 0):
    torch.manual_seed(seed)
    return torch.randn(n, c), torch.randint(0, c, (n,))


# ---------------------------------------------------------------- the simplification

@pytest.mark.equivalence
@pytest.mark.parametrize("num_classes", [7, 20, 200])
def test_handrolled_metrics_agree_with_torchmetrics(old_metrics, num_classes: int) -> None:
    """Below 256 classes the reference uses torchmetrics; this uses one implementation everywhere.

    If these disagree, the simplification is invalid and the category head's macro-F1 — the metric
    that selects its checkpoint — would shift.
    """
    from mtlcheck.train import metrics as mine

    logits, targets = _logits_and_targets(4000, num_classes, seed=3)
    reference = old_metrics.compute_classification_metrics(
        logits, targets, num_classes=num_classes, top_k=(5, 10))

    acc = mine.StreamingMetrics(num_classes, top_k=(5, 10))
    for start in range(0, len(targets), 512):
        acc.update(logits[start:start + 512], targets[start:start + 512])
    ours = acc.compute()

    for key in ("accuracy", "accuracy_macro", "f1", "f1_weighted", "mrr", "top5_acc", "top10_acc"):
        assert abs(ours[key] - reference[key]) < 1e-6, (
            f"C={num_classes} {key}: ours {ours[key]:.10f} vs torchmetrics-backed "
            f"{reference[key]:.10f}"
        )


# ---------------------------------------------------------------- E9 proper

@pytest.mark.equivalence
@pytest.mark.parametrize("num_classes", [1109, 4703])
def test_streaming_matches_the_reference_accumulator(old_metrics, num_classes: int) -> None:
    """At region cardinality, against the reference's own streaming accumulator."""
    from mtlcheck.train import metrics as mine

    logits, targets = _logits_and_targets(3000, num_classes, seed=11)

    theirs = old_metrics.StreamingClsMetrics(num_classes, top_k=(5, 10))
    ours = mine.StreamingMetrics(num_classes, top_k=(5, 10))
    for start in range(0, len(targets), 256):
        chunk = slice(start, start + 256)
        theirs.update(logits[chunk], targets[chunk])
        ours.update(logits[chunk], targets[chunk])

    ref, got = theirs.compute(), ours.compute()
    for key in ("accuracy", "accuracy_macro", "f1", "f1_weighted", "mrr", "top5_acc", "top10_acc",
                "ndcg_5", "ndcg_10"):
        assert abs(got[key] - ref[key]) < 1e-9, f"{key}: ours {got[key]} vs reference {ref[key]}"


@pytest.mark.equivalence
def test_batching_does_not_change_the_result() -> None:
    """Every metric is a per-row reduction, so batch size is irrelevant to the value."""
    from mtlcheck.train import metrics as mine

    logits, targets = _logits_and_targets(2048, 1109, seed=5)
    results = []
    for batch in (2048, 512, 97):
        acc = mine.StreamingMetrics(1109, top_k=(5, 10))
        for start in range(0, len(targets), batch):
            acc.update(logits[start:start + batch], targets[start:start + batch])
        results.append(acc.compute())

    for key in results[0]:
        values = {round(r[key], 12) for r in results}
        assert len(values) == 1, f"{key} varies with batch size: {values}"


@pytest.mark.equivalence
def test_ood_block_matches_the_reference(old_metrics) -> None:
    """The in-distribution restriction, against the reference's own implementation."""
    from mtlcheck.train import metrics as mine

    num_classes = 1109
    logits, targets = _logits_and_targets(3000, num_classes, seed=13)
    train_labels = set(range(0, num_classes, 2))          # half the label space unseen

    sys.path.insert(0, str(OLD_SRC))
    from training.runners.mtl_eval import _ood_restricted_topk

    theirs = _ood_restricted_topk(logits, targets, train_labels, ks=(1, 5, 10))

    acc = mine.StreamingMetrics(num_classes, top_k=(1, 5, 10))
    acc.update(logits, targets)
    _, tgt, rank, hits = acc.concat()
    ours = mine.in_distribution(tgt, rank, hits, train_labels, ks=(1, 5, 10))

    for key in ("n_indist", "n_ood", "ood_fraction", "top1_acc_indist", "top5_acc_indist",
                "top10_acc_indist", "mrr_indist"):
        assert abs(ours[key] - theirs[key]) < 1e-9, f"{key}: ours {ours[key]} vs {theirs[key]}"


@pytest.mark.equivalence
def test_rank_handles_ties_canonically() -> None:
    """A target sharing the top score ranks 1, not 2 — independent of any sort order."""
    from mtlcheck.train import metrics as mine

    logits = torch.tensor([[5.0, 5.0, 1.0], [1.0, 2.0, 3.0]])
    targets = torch.tensor([0, 0])
    rank, tied = mine._rank_and_ties(logits, targets)
    assert rank.tolist() == [1, 3]
    assert tied.tolist() == [2, 1]


@pytest.mark.equivalence
def test_ambiguity_certificate_counts_only_straddling_targets() -> None:
    """Only a target whose tie group crosses k is ambiguous.

    A tie between two non-target classes cannot change any reported number. Counting those too — as
    an earlier version of the reference did — over-reports by orders of magnitude and vetoes changes
    that are provably safe.
    """
    from mtlcheck.train import metrics as mine

    # Row 0: target ties with the class at the k=1 boundary -> genuinely ambiguous at k=1.
    # Row 1: two NON-target classes tie at the boundary; the target is far below -> not ambiguous.
    logits = torch.tensor([[9.0, 9.0, 0.0, 0.0],
                           [9.0, 9.0, 0.0, 0.0]])
    targets = torch.tensor([0, 3])

    acc = mine.StreamingMetrics(4, top_k=(1,))
    acc.update(logits, targets)
    assert acc.ambiguous[1] == 1, f"expected exactly one ambiguous row, got {acc.ambiguous[1]}"


@pytest.mark.equivalence
def test_strict_mode_refuses_an_ambiguous_cell() -> None:
    from mtlcheck.train import metrics as mine

    logits = torch.tensor([[9.0, 9.0, 0.0, 0.0]])
    targets = torch.tensor([0])
    with pytest.raises(RuntimeError, match="ambiguous"):
        mine.StreamingMetrics(4, top_k=(1,), strict=True).update(logits, targets)


@pytest.mark.equivalence
def test_region_score_exposes_both_estimators() -> None:
    """D4 — the joint reports indist x (1-ood); the dedicated family reports plain top-10.

    They are compared directly in the published tables while being different estimators: an unseen
    region still has an output unit and can land in the top ten. Carrying both makes the gap
    measurable.
    """
    from mtlcheck.train import metrics as mine

    metrics = {"top10_acc_indist": 0.80, "ood_fraction": 0.03, "top10_acc": 0.7765}
    out = mine.region_score(metrics)
    assert out["top10_full"] == pytest.approx(0.80 * 0.97)
    assert out["top10_raw"] == 0.7765
    assert out["top10_raw"] >= out["top10_full"], (
        "the raw estimator can only be >= the OOD-discounted one, since OOD rows may hit by chance"
    )


def test_the_cached_label_tensor_is_bit_identical_to_a_fresh_isin() -> None:
    """The cache must be an optimisation only — same `isin`, same operands, same mask.

    `torch.isin` carries ~22-30 ms of FIXED overhead per call, so paying it once per epoch on an
    unchanging pair of inputs cost ~11% of a region fold. Caching the sorted label tensor removes
    the rebuild; this pins that it removes nothing else.
    """
    from mtlcheck.train import metrics

    generator = torch.Generator().manual_seed(19)
    targets = torch.randint(0, 200, (5000,), generator=generator)
    labels = {int(v) for v in torch.randint(0, 200, (140,), generator=generator)}

    expected = torch.isin(targets, torch.as_tensor(sorted(labels), dtype=targets.dtype))
    for _ in range(3):                                   # repeat: a warm cache must not drift
        assert torch.equal(metrics.in_distribution_mask(targets, labels), expected)

    # A different label set must not hit the previous entry. Drop a label that actually OCCURS in
    # the targets — dropping an absent one leaves the mask identical and proves nothing, which is
    # what the first version of this assertion did.
    present = next(v for v in sorted(labels) if bool((targets == v).any()))
    assert not torch.equal(metrics.in_distribution_mask(targets, labels - {present}), expected)
