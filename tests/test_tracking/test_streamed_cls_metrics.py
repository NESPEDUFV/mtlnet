"""`_streamed_cls_metrics` must equal the full-logit hand-rolled metric path.

The S1 (train) + S2 (val) streaming paths reconstruct the C>256 metric dict from
per-row accumulators instead of the full [N, C] logit tensor. This pins that the
shared reconstruction is numerically identical to computing the same metrics from
the full logits (the value that would otherwise be scored).
"""

import torch

from tracking.metrics import (
    compute_classification_metrics,
    _rank_of_target,
    _streamed_cls_metrics,
)


def test_streamed_equals_full_logit_handrolled():
    torch.manual_seed(0)
    n, c = 4000, 300  # C > 256 → the hand-rolled path
    logits = torch.randn(n, c)
    targets = torch.randint(0, c, (n,))

    full = compute_classification_metrics(logits, targets, num_classes=c)

    # streamed accumulators (what S1/S2 build per-batch, here in one shot)
    preds = logits.argmax(dim=-1)
    rank = _rank_of_target(logits, targets)
    hit = {
        k: (logits.topk(k, dim=-1).indices == targets.unsqueeze(-1)).any(dim=-1)
        for k in (3, 5)
    }
    streamed = _streamed_cls_metrics(preds, targets, rank, hit, c, top_k=(3, 5))

    for key in ("accuracy", "accuracy_macro", "f1", "f1_weighted", "mrr",
                "top3_acc", "top5_acc", "ndcg_3", "ndcg_5"):
        assert key in streamed, f"missing {key}"
        assert streamed[key] == full[key], f"{key}: streamed {streamed[key]} != full {full[key]}"


def test_streamed_top_k_subset_indexes_hit():
    # The helper only indexes hit[k] for k in top_k — extra hit keys are ignored.
    torch.manual_seed(1)
    n, c = 1000, 300
    logits = torch.randn(n, c)
    targets = torch.randint(0, c, (n,))
    preds = logits.argmax(dim=-1)
    rank = _rank_of_target(logits, targets)
    hit = {k: (logits.topk(k, dim=-1).indices == targets.unsqueeze(-1)).any(dim=-1)
           for k in (1, 3, 5, 10)}
    out = _streamed_cls_metrics(preds, targets, rank, hit, c, top_k=(3, 5))
    assert set(k for k in out if k.startswith("top")) == {"top3_acc", "top5_acc"}
