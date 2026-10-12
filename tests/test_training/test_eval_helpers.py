"""mtl_eval helpers: _ood_from_streamed (== full-logit OOD) + eval_autocast_ctx gating."""

import contextlib

import torch

from tracking.metrics import _rank_of_target
from training.runners.mtl_eval import (
    _ood_from_streamed,
    _ood_restricted_topk,
    eval_autocast_ctx,
)


def test_ood_from_streamed_equals_full_logit():
    torch.manual_seed(0)
    n, c = 3000, 400
    logits = torch.randn(n, c)
    targets = torch.randint(0, c, (n,))
    # train set = a subset of classes → some val targets are OOD
    train_labels = set(range(0, c, 2))  # even classes only

    full = _ood_restricted_topk(logits, targets, train_labels, ks=(1, 5, 10))

    # streamed accumulators (what evaluate_model builds per-batch)
    rank = _rank_of_target(logits, targets)
    hit = {
        k: (logits.topk(k, dim=-1).indices == targets.unsqueeze(-1)).any(dim=-1)
        for k in (1, 5, 10)
    }
    streamed = _ood_from_streamed(targets, rank, hit, train_labels, ks=(1, 5, 10))

    assert set(streamed) == set(full)
    for key in full:
        assert streamed[key] == full[key], f"{key}: {streamed[key]} != {full[key]}"


def test_ood_all_ood_returns_zeros():
    torch.manual_seed(1)
    n, c = 500, 100
    logits = torch.randn(n, c)
    targets = torch.randint(50, c, (n,))     # all in [50, 100)
    train_labels = set(range(0, 50))          # disjoint → everything is OOD
    rank = _rank_of_target(logits, targets)
    hit = {k: (logits.topk(k, -1).indices == targets.unsqueeze(-1)).any(-1) for k in (1, 5, 10)}
    out = _ood_from_streamed(targets, rank, hit, train_labels)
    assert out["n_indist"] == 0.0 and out["ood_fraction"] == 1.0
    assert all(out[f"top{k}_acc_indist"] == 0.0 for k in (1, 5, 10))
    assert out["mrr_indist"] == 0.0


def test_eval_autocast_ctx_cpu_and_disable():
    # CPU → never autocast (nullcontext)
    ctx = eval_autocast_ctx(torch.device("cpu"))
    assert isinstance(ctx, contextlib.nullcontext)
    # env-forced fp32 → nullcontext even on a (mock) cuda device type
    import os
    old = os.environ.get("MTL_DISABLE_AMP_EVAL")
    os.environ["MTL_DISABLE_AMP_EVAL"] = "1"
    try:
        assert isinstance(eval_autocast_ctx(torch.device("cpu")), contextlib.nullcontext)
    finally:
        if old is None:
            os.environ.pop("MTL_DISABLE_AMP_EVAL", None)
        else:
            os.environ["MTL_DISABLE_AMP_EVAL"] = old
