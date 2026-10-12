"""The baselines' OOD reg metric, streamed, must equal the full-logit one they used before.

`flashback_e2e`, `poi2vec_e2e` and `ctle_e2e` used to cat the whole `[N_val, n_regions]` reg
logit and hand it to `_ood_restricted_topk`. At california (8501 regions) / texas (6553) that is
~20 GB and the call would simply OOM. They now accumulate per-row reductions with
`StreamingClsMetrics` and call `_ood_from_streamed`.

`b3_hmt_grn` was a fourth case with its own twist: it already streamed, by hand, and computed the
OOD rates with running INTEGER counts (`hits[k] / n_indist`) instead of the shared
`hit[k][mask].float().mean()`. So the baseline table had two different implementations of one
metric. It now uses the shared path too, which shifts its numbers by the float64-vs-float32
division difference — pinned below to be far under the reporting quantum.

The masking order is the subtle part and is tested explicitly: the old code masked the logits and
THEN took top-k, the new code takes top-k on every row and masks the resulting hit vector. Those
agree only because top-k of row i does not depend on any other row.
"""
import pytest
import torch

from tracking.metrics import StreamingClsMetrics
from training.runners.mtl_eval import _ood_from_streamed, _ood_restricted_topk

KS = (1, 5, 10)
KEYS = ("top1_acc_indist", "top5_acc_indist", "top10_acc_indist", "mrr_indist",
        "n_indist", "n_ood", "ood_fraction")


def _fixture(n, c, n_train_labels, seed=0, kind="float"):
    g = torch.Generator().manual_seed(seed)
    if kind == "ties":
        logits = torch.randint(0, 7, (n, c), generator=g).float()
    else:
        logits = torch.randn(n, c, generator=g)
    targets = torch.randint(0, c, (n,), generator=g)
    labels = set(range(n_train_labels))          # a contiguous prefix leaves real OOD rows
    return logits, targets, labels


def _streamed(logits, targets, labels, c, bs, move_to=None, hits_from_rank=False):
    acc = StreamingClsMetrics(c, top_k=KS, move_logits_to=move_to, hits_from_rank=hits_from_rank)
    for i in range(0, logits.shape[0], bs):
        acc.update(logits[i:i + bs], targets[i:i + bs])
    _, tgts, rank, hit = acc.concat()
    return _ood_from_streamed(tgts, rank, hit, labels, ks=KS)


# (n, c, n_train_labels, batch) — includes a batch that does not divide n, and batch 1
CASES = [
    (4000, 1109, 800, 512),
    (4000, 6553, 4000, 512),      # texas-shaped
    (3000, 8501, 2000, 997),      # california-shaped, ragged batch
    (2000, 520, 400, 1),          # istanbul-shaped, batch 1
    (2000, 1547, 1547, 256),      # no OOD rows at all
]


@pytest.mark.parametrize("n,c,ntl,bs", CASES)
def test_streamed_ood_equals_full_logit_ood(n, c, ntl, bs):
    logits, targets, labels = _fixture(n, c, ntl)
    want = _ood_restricted_topk(logits, targets, labels, ks=KS)
    got = _streamed(logits, targets, labels, c, bs)
    for k in KEYS:
        assert float(got[k]) == pytest.approx(float(want[k]), abs=1e-12), f"{k} diverged"


def test_masking_after_topk_equals_masking_before():
    """The old code sliced the logits by the OOD mask and then took top-k; the new one takes
    top-k on every row and slices the hit vector. Equal only because top-k is per-row."""
    logits, targets, labels = _fixture(3000, 1109, 600)
    mask = torch.isin(targets, torch.tensor(sorted(labels)))
    masked_first = _ood_restricted_topk(logits[mask], targets[mask], labels, ks=KS)
    topk_first = _streamed(logits, targets, labels, 1109, 512)
    for k in ("top1_acc_indist", "top5_acc_indist", "top10_acc_indist", "mrr_indist"):
        assert float(topk_first[k]) == pytest.approx(float(masked_first[k]), abs=1e-12)


def test_exact_ties_do_not_break_equivalence_on_one_device():
    """Ties change which index top-k returns, but both paths ask the same kernel on the same
    tensor, so they must still agree. Pinned against the TOPK semantics on purpose: the
    rank-derived default is deliberately different on ambiguous rows (tie-optimistic), and that
    difference is covered by its own bounded test in test_streaming_cls_metrics.py."""
    logits, targets, labels = _fixture(2500, 1109, 500, kind="ties")
    want = _ood_restricted_topk(logits, targets, labels, ks=KS)
    got = _streamed(logits, targets, labels, 1109, 384)
    for k in KEYS:
        assert float(got[k]) == pytest.approx(float(want[k]), abs=1e-12)


def test_b3_int_count_formula_agrees_with_the_shared_one_under_the_quantum():
    """b3 divided integer counts in float64; the shared path takes a float32 mean. The switch is
    a real numeric change to banked numbers, so bound it rather than assert equality."""
    logits, targets, labels = _fixture(20000, 1109, 900, seed=3)
    shared = _streamed(logits, targets, labels, 1109, 1024)
    mask = torch.isin(targets, torch.tensor(sorted(labels)))
    n_indist = int(mask.sum())
    li, ti = logits[mask], targets[mask]
    for k in KS:
        ke = min(k, li.shape[-1])
        hits = int((li.topk(ke, dim=-1).indices == ti.unsqueeze(-1)).any(dim=-1).sum())
        b3_style = hits / max(n_indist, 1)
        assert abs(b3_style - float(shared[f"top{k}_acc_indist"])) < 1e-6, f"k={k} over the quantum"


def test_move_logits_to_cpu_matches_default_on_a_cpu_run():
    """b3 passes move_logits_to='cpu' to preserve its per-batch CPU reduction. On a CPU-only run
    that must be a no-op, so the flag cannot be the thing that changes its numbers."""
    logits, targets, labels = _fixture(2000, 1109, 500)
    assert _streamed(logits, targets, labels, 1109, 512) == \
           _streamed(logits, targets, labels, 1109, 512, move_to="cpu")
