"""Validation metrics — streamed, device-independent, and one implementation instead of two.

Every quantity reported here is a **per-row** reduction (argmax, rank of the target, hit@k) or an
additive per-class count. That is what makes streaming exact rather than approximate: accumulating
per batch and concatenating the O(N) results is the same arithmetic as computing on the full
[N, C] matrix, which at region cardinality would be ~20 GB.

Two properties inherited deliberately from the reference, both hard-won there:

* **Hits come from the rank, not from topk.** `hit@k == (rank <= k)` whenever no row is ambiguous,
  and that is an integer comparison — identical on CPU and CUDA. `topk`'s tie-break at the k
  boundary is a kernel detail, which is what forced validation scoring onto the host and made the
  dedicated-region cell the one family that ran *slower* on faster hardware.
* **The ambiguity certificate is measured, not assumed.** A row is ambiguous exactly when the
  target's tie group straddles k. Counting anything broader — say, ties between two non-target
  classes — over-reports by orders of magnitude and vetoes changes that are provably safe.

**One simplification versus the reference.** It keeps two metric implementations and switches
between them at 256 classes: torchmetrics below, hand-rolled above (torchmetrics' confusion-matrix
path allocates `num_classes**2` and is unusable at region scale). Two implementations of one
definition is two chances to disagree. This keeps the hand-rolled one for every cardinality, and
`tests/equivalence/test_metrics.py` pins it against torchmetrics at the category head's C=7 — so the
simplification is verified, not assumed.
"""

from __future__ import annotations

import functools

import logging
from dataclasses import dataclass, field
from typing import Iterable

import torch

logger = logging.getLogger(__name__)

RANK_CHUNK = 4096


@dataclass
class StreamingMetrics:
    """Accumulate per-row reductions one batch at a time."""

    num_classes: int
    top_k: tuple[int, ...] = (5, 10)
    strict: bool = False

    #: When set, also retain the top-K predicted ids with their probabilities, plus the true
    #: class's probability and the fp32 logsumexp. Off during training — this is for the ONE
    #: sealed outer pass, where those columns make the metric recomputable at any k, at any
    #: threshold, and the softmax over the stored entries exactly recoverable.
    keep_top_k: int = 0

    _preds: list = field(default_factory=list, repr=False)
    _targets: list = field(default_factory=list, repr=False)
    _rank: list = field(default_factory=list, repr=False)
    _hits: dict = field(default_factory=dict, repr=False)
    _top_ids: list = field(default_factory=list, repr=False)
    _top_log_probs: list = field(default_factory=list, repr=False)
    _true_prob: list = field(default_factory=list, repr=False)
    _logsumexp: list = field(default_factory=list, repr=False)
    ambiguous: dict = field(default_factory=dict, repr=False)
    n_rows: int = 0

    def __post_init__(self) -> None:
        self._hits = {k: [] for k in self.top_k}
        self.ambiguous = {k: 0 for k in self.top_k}

    @torch.no_grad()
    def update(self, logits: torch.Tensor, targets: torch.Tensor) -> "StreamingMetrics":
        logits = logits.detach()
        rank, tied = _rank_and_ties(logits, targets)
        n_classes = logits.shape[-1]

        self._preds.append(logits.argmax(dim=-1))
        self._targets.append(targets)
        self._rank.append(rank)

        n_greater = rank - 1
        for k in self.top_k:
            self._hits[k].append(rank <= min(k, n_classes))
            if k < n_classes:
                straddling = int(((n_greater < k) & (k < n_greater + tied)).sum())
                self.ambiguous[k] += straddling
                if straddling and self.strict:
                    raise RuntimeError(
                        f"{straddling} rows are ambiguous at the {k}/{k + 1} boundary: the target "
                        f"sits in a tie group straddling k, so hit@{k} depends on an arbitrary "
                        f"tie-break and this cell would not be comparable with its siblings"
                    )
        if self.keep_top_k:
            self._retain_distribution(logits, targets)
        self.n_rows += int(logits.shape[0])
        return self

    def _retain_distribution(self, logits: torch.Tensor, targets: torch.Tensor) -> None:
        """Top-K ids and probabilities, the true class's probability, and the fp32 logsumexp.

        The logsumexp is what makes this lossless for anything computable from the retained
        entries: `p_j = exp(logit_j - logsumexp)`, so the true softmax over the stored classes is
        recoverable exactly rather than renormalised over a truncated set. Without it, storing K of
        C probabilities silently changes the denominator.

        In fp32 regardless of the run's precision, because a logsumexp is a sum over the whole
        vocabulary — 8,501 classes at Texas — and fp16 loses the tail that makes it worth storing.
        """
        wide = logits.float()
        k = min(self.keep_top_k, wide.shape[-1])
        values, indices = wide.topk(k, dim=-1)
        lse = torch.logsumexp(wide, dim=-1)
        self._top_ids.append(indices.to(torch.int32))
        # LOG-probabilities in fp16, not probabilities. Same two bytes, and it cannot underflow:
        # fp16 flushes any probability below 2.98e-8 to exactly zero and quantises the whole
        # subnormal band below 6.1e-5 to ~20-100% error, so a retained entry in the tail was
        # destroyed rather than approximated. A log-probability of -17 is represented to ~0.008
        # absolute, i.e. under 1% on the probability, everywhere the model can reach.
        self._top_log_probs.append((values - lse.unsqueeze(-1)).to(torch.float16))
        self._true_prob.append((wide.gather(-1, targets.unsqueeze(-1)).squeeze(-1) - lse).exp())
        self._logsumexp.append(lse)

    @property
    def has_ambiguity(self) -> bool:
        return any(v > 0 for v in self.ambiguous.values())

    def concat(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict]:
        return (torch.cat(self._preds), torch.cat(self._targets), torch.cat(self._rank),
                {k: torch.cat(v) for k, v in self._hits.items()})

    def distribution(self) -> dict[str, torch.Tensor]:
        """The retained top-K block, empty when `keep_top_k` is 0."""
        if not self._top_ids:
            return {}
        return {"top_ids": torch.cat(self._top_ids),
                "top_log_probs": torch.cat(self._top_log_probs),
                "true_prob": torch.cat(self._true_prob), "logsumexp": torch.cat(self._logsumexp)}

    def compute(self) -> dict[str, float]:
        if self.n_rows == 0:
            raise ValueError("no rows accumulated")
        preds, targets, rank, hits = self.concat()
        out = classification_metrics(preds, targets, rank, self.num_classes)
        for k in self.top_k:
            out[f"top{k}_acc"] = float(hits[k].float().mean())
            out[f"ndcg_{k}"] = _ndcg(rank, k)
        return out


def classification_metrics(preds: torch.Tensor, targets: torch.Tensor,
                           rank: torch.Tensor, num_classes: int) -> dict[str, float]:
    """Micro accuracy, balanced accuracy, macro-F1, weighted-F1 and MRR.

    Memory is O(N + C): per-class true-positive / support / predicted counts via `bincount` on the
    1-D streams. No confusion matrix is ever materialised.
    """
    correct = (preds == targets).to(torch.float32)
    tp = torch.bincount(targets, weights=correct, minlength=num_classes)
    support = torch.bincount(targets, minlength=num_classes).to(torch.float32)
    predicted = torch.bincount(preds, minlength=num_classes).to(torch.float32)

    recall = torch.where(support > 0, tp / support.clamp_min(1.0), torch.zeros_like(tp))
    precision = torch.where(predicted > 0, tp / predicted.clamp_min(1.0), torch.zeros_like(tp))
    denom = precision + recall
    f1 = torch.where(denom > 0, 2 * precision * recall / denom.clamp_min(1e-12),
                     torch.zeros_like(denom))

    # Both macro averages divide by the classes that are RELEVANT — those with support OR with
    # predictions. Dividing by supported classes alone silently drops the classes the model predicts
    # but never sees, which at region cardinality inflated the macro figures by 1.5-3x.
    relevant = (support > 0) | (predicted > 0)
    n_relevant = max(int(relevant.sum()), 1)

    total_support = support.sum().clamp_min(1.0)
    return {
        "accuracy": float(correct.mean()),
        "accuracy_macro": float(recall.sum() / n_relevant),
        "f1": float(f1[relevant].mean()) if int(relevant.sum()) else 0.0,
        "f1_weighted": float((f1 * (support / total_support)).sum()),
        "mrr": float((1.0 / rank.float()).mean()),
    }


def _rank_and_ties(logits: torch.Tensor, targets: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """1-indexed best-case rank of the target, and the size of its tie group.

    Rank is `1 + #{classes scoring strictly higher}` — the canonical tie handling for ranking
    metrics: if the target shares the top score, it ranks 1, not 2. An argsort-based rank would
    break ties by the platform's sort stability, which is an implementation detail no reported
    number should depend on.

    Chunked because the naive comparison materialises an [N, C] boolean, which OOM-killed a GPU
    mid-validation at region scale.
    """
    device = logits.device
    if device.type == "mps" and logits.numel() > 2 ** 31:
        # MPSGraph rejects tensors above INT_MAX elements. A platform limit, not a choice.
        logits, targets = logits.cpu(), targets.cpu()

    target_scores = logits.gather(dim=-1, index=targets.unsqueeze(-1))
    n = logits.size(0)
    higher = torch.empty(n, dtype=torch.long, device=logits.device)
    equal = torch.empty(n, dtype=torch.long, device=logits.device)
    for start in range(0, n, RANK_CHUNK):
        stop = start + RANK_CHUNK
        block, scores = logits[start:stop], target_scores[start:stop]
        higher[start:stop] = (block > scores).sum(dim=-1)
        equal[start:stop] = (block == scores).sum(dim=-1)
    return (higher + 1).to(device), equal.to(device)


def _ndcg(rank: torch.Tensor, k: int) -> float:
    """NDCG@k with a single relevant item: 1/log2(rank+1) when the target is inside k, else 0."""
    hit = rank <= k
    gain = torch.where(hit, 1.0 / torch.log2(rank.float() + 1.0),
                       torch.zeros(1, dtype=torch.float32, device=rank.device))
    return float(gain.mean())


@functools.lru_cache(maxsize=8)
def _known_tensor(labels: tuple[int, ...], dtype: torch.dtype, device: torch.device) -> torch.Tensor:
    return torch.as_tensor(labels, dtype=dtype, device=device)


def in_distribution_mask(targets: torch.Tensor, train_labels: set[int] | frozenset[int]) -> torch.Tensor:
    """Which validation rows have a target the training split contained.

    The label set is fixed for a fold and the validation targets are a fixed slice, so the sorted
    tensor is built once per (labels, dtype, device) and reused. Bit-identical: same `isin`, same
    operands, verified in `test_e9_metrics`.

    On the size of the win, because a review claimed it was large: measured on the A40 at region
    scale (19 000 targets, 1 050 labels), 0.256 ms uncached against 0.228 ms cached — **1.4 ms over
    a 50-epoch fold**, not the ~1.1-1.5 s that was reported. The change is kept because it is free
    and correct, not because it is a speedup worth naming.
    """
    known = _known_tensor(tuple(sorted(train_labels)), targets.dtype, targets.device)
    return torch.isin(targets, known)


def in_distribution(targets: torch.Tensor, rank: torch.Tensor, hits: dict,
                    train_labels: set[int], ks: Iterable[int] = (1, 5, 10)) -> dict[str, float]:
    """Ranking metrics restricted to validation rows whose target was seen in TRAINING.

    The reported region figure is `top10_acc_indist * (1 - ood_fraction)`, which counts every
    out-of-distribution row as a miss. Note that this is not identical to plain top-10 accuracy over
    all rows: an unseen region still has an output unit and can, in principle, land in the top ten.
    Both are reported (see `region_score`) so the asymmetry is visible rather than assumed away.
    """
    mask = in_distribution_mask(targets, train_labels)
    n_indist = int(mask.sum())
    n_total = int(targets.numel())

    out = {
        "n_indist": float(n_indist),
        "n_ood": float(n_total - n_indist),
        "ood_fraction": float((n_total - n_indist) / max(n_total, 1)),
    }
    if n_indist == 0:
        out.update({f"top{k}_acc_indist": 0.0 for k in ks})
        out["mrr_indist"] = 0.0
        return out

    for k in ks:
        out[f"top{k}_acc_indist"] = float(hits[k][mask].float().mean())
    out["mrr_indist"] = float((1.0 / rank[mask].float()).mean())
    return out


def region_score(metrics: dict[str, float]) -> dict[str, float]:
    """The two forms of the reported region figure, side by side.

    `top10_full` is the reference's definition — in-distribution accuracy scaled by the
    in-distribution fraction, i.e. every OOD row treated as a miss. `top10_raw` is plain top-10 over
    all rows, which is what the dedicated-region family reports. The two are compared directly in
    the published tables while being subtly different estimators; carrying both makes the gap
    measurable instead of invisible.
    """
    indist = metrics.get("top10_acc_indist")
    if indist is None:
        return {}
    ood = metrics.get("ood_fraction", 0.0)
    return {
        "top10_full": indist * (1.0 - ood),
        "top10_raw": metrics.get("top10_acc", float("nan")),
    }


__all__ = ["StreamingMetrics", "classification_metrics", "in_distribution", "region_score"]
