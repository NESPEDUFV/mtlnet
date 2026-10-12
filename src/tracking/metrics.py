"""Classification metric computation for POI tasks.

A single pure function converts a batch of logits + targets into a flat dict
of scalar Python floats. The dict keys are stable names (optionally prefixed)
that downstream ``MetricStore.log(**kwargs)`` calls can consume directly.

Metric choices are grounded in ``docs/LITERATURE_SURVEY_POI_METRICS.md`` and
``docs/POI_RELATED_WORK_METRICS.md``:

  * ``accuracy`` (micro) and ``f1`` (macro) — unchanged primary metrics.
  * ``accuracy_macro`` — balanced accuracy, complements micro under imbalance.
  * ``f1_weighted`` — robustness-to-imbalance secondary signal.
  * ``top{k}_acc`` for k in ``top_k`` — bridge to the next-POI recommendation
    literature (Acc@K / Recall@K in the single-label case).
  * ``mrr`` — mean reciprocal rank over the full class ranking.
  * ``ndcg_{k}`` — NDCG@K with binary single-item relevance (reduces to the
    well-defined single-label form used by ranking papers).

The ``'f1'`` key stays identical to the previous
``multiclass_f1_score(..., average='macro')`` value so existing
``BestModelTracker(monitor='f1')`` behaviour is byte-identical.
"""

from __future__ import annotations

import os
from typing import Dict, Iterable

import torch
from torchmetrics.functional.classification import (
    multiclass_accuracy,
    multiclass_f1_score,
)


def _handrolled_cls_metrics(
    preds: torch.Tensor,
    targets: torch.Tensor,
    num_classes: int,
) -> tuple[float, float, float, float]:
    """Memory-O(N + num_classes) Acc / macro-F1 for high-cardinality heads.

    torchmetrics' ``multiclass_accuracy`` / ``multiclass_f1_score``
    build an internal confusion matrix of size ``num_classes**2``
    via ``bincount(minlength=num_classes**2)``. That allocation is
    ~30GB for 1K classes × 6K batch and OOMs on any device.

    This implementation uses per-class TP / FP / FN counts via
    ``torch.bincount`` on the 1-D predicted and target class streams —
    no ``num_classes**2`` tensor anywhere. Matches torchmetrics output
    for micro-accuracy, macro-accuracy (balanced) and macro/weighted F1
    on single-label multi-class data.
    """
    n = preds.numel()
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0

    correct = (preds == targets).to(torch.float32)
    acc_micro = correct.mean().item()

    # Per-class TP / (TP + FN) = recall; we also need precision via FP.
    # ``bincount(targets, weights=correct)`` → per-class TP counts.
    # ``bincount(targets)``                 → per-class support (TP + FN).
    # ``bincount(preds)``                   → per-class predicted (TP + FP).
    tp = torch.bincount(targets, weights=correct, minlength=num_classes)
    support = torch.bincount(targets, minlength=num_classes).to(torch.float32)
    predicted = torch.bincount(preds, minlength=num_classes).to(torch.float32)

    # macro-accuracy = mean over per-class recall on classes with support.
    recall_per_class = torch.where(
        support > 0, tp / support.clamp_min(1.0), torch.zeros_like(tp),
    )
    precision_per_class = torch.where(
        predicted > 0, tp / predicted.clamp_min(1.0), torch.zeros_like(tp),
    )
    # F1 = 2PR/(P+R), 0 when P+R==0.
    denom = precision_per_class + recall_per_class
    f1_per_class = torch.where(
        denom > 0,
        2 * precision_per_class * recall_per_class / denom.clamp_min(1e-12),
        torch.zeros_like(denom),
    )
    # AUDIT-C5 fix — both macro metrics (acc_macro = mean recall,
    # f1_macro) divide by the count of "relevant" classes: those with
    # support OR predictions. Pre-fix used ``support > 0`` only, which
    # silently dropped FP-only classes (predicted but never targeted)
    # from the average. torchmetrics' macro path INCLUDES them (with
    # contribution 0), so on high-cardinality region (4702 classes;
    # model often predicts >> 1500 distinct classes) handrolled
    # produced 1.5-3× larger macro values than torchmetrics. Now they
    # agree to within float tolerance.
    relevant = (support > 0) | (predicted > 0)
    n_relevant = int(relevant.sum().item())
    acc_macro = float(recall_per_class.sum().item() / max(n_relevant, 1))
    f1_macro = float(f1_per_class[relevant].mean().item()) if n_relevant > 0 else 0.0
    # Weighted F1 — weights = support / total support.
    total_support = support.sum().clamp_min(1.0)
    f1_weighted = float((f1_per_class * (support / total_support)).sum().item())

    return acc_micro, acc_macro, f1_macro, f1_weighted


def _top_k_accuracy(logits: torch.Tensor, targets: torch.Tensor, k: int) -> float:
    """Fraction of samples whose true class is in the top-k predictions.

    Caller must pass ``k >= 2`` — the main API skips ``k == 1`` since that
    would duplicate ``accuracy``.
    """
    k_eff = min(k, logits.shape[-1])
    top_k = logits.topk(k_eff, dim=-1).indices  # (N, k_eff)
    hit = (top_k == targets.unsqueeze(-1)).any(dim=-1)
    return hit.float().mean().item()


def _rank_and_ties(logits: torch.Tensor, targets: torch.Tensor):
    """``(rank, n_eq)`` in ONE chunked pass — ``n_eq`` counts classes tied with the target.

    Split out of ``_rank_of_target`` because the two quantities answer the same question and read
    the same memory. ``n_gt = rank - 1`` says how many classes beat the target; ``n_eq`` says how
    large the target's tie group is. Together they decide hit@k **exactly**::

        n_gt >= k             -> miss, for every valid top-k
        n_gt + n_eq <= k      -> hit,  for every valid top-k
        otherwise             -> AMBIGUOUS: the tie group straddles k and the answer depends on
                                 which tied element the kernel happens to pick

    So when nothing is ambiguous, ``hit@k == (rank <= k)`` — an integer comparison, with no
    ``topk`` and therefore no dependence on sort order, tie order, or the device's kernel. That
    is what makes rank-derived hits bit-identical across CPU and CUDA, which ``topk``-derived
    hits are not.

    Computing ``==`` in the same chunk as ``>`` is close to free: the chunk is already resident.
    """
    orig_device = logits.device
    if orig_device.type == 'mps':          # same MPS INT_MAX guard as _rank_of_target
        logits = logits.cpu()
        targets = targets.cpu()
    target_scores = logits.gather(dim=-1, index=targets.unsqueeze(-1))
    n = logits.size(0)
    chunk = 4096
    higher = torch.empty(n, dtype=torch.long, device=logits.device)
    equal = torch.empty(n, dtype=torch.long, device=logits.device)
    for i in range(0, n, chunk):
        block = logits[i:i + chunk]
        ts = target_scores[i:i + chunk]
        higher[i:i + chunk] = (block > ts).sum(dim=-1)
        equal[i:i + chunk] = (block == ts).sum(dim=-1)
    return higher + 1, equal


def _rank_of_target(logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """1-indexed "best-case" rank of the true class in each row.

    Computed as ``1 + #{classes with a strictly higher logit than the target}``.
    This is the canonical tie-handling for ranking metrics: if two classes
    share the top score and one of them is the target, the target ranks 1,
    not 2. An ``argsort``-based implementation would break ties by the
    platform's sort stability, which is an implementation detail the caller
    shouldn't depend on.

    Returns an int64 tensor of shape ``(N,)``.
    """
    # On MPS, the chunked comparison's MPSGraph backing op fails with
    # "MPSGaph does not support tensor dims larger than INT_MAX" when
    # N × C > 2^31 (e.g. CA train fold: 286K × 8497 ≈ 2.4B). Fall back
    # to CPU for the rank computation; downstream reductions (mrr, ndcg)
    # work on the resulting (N,) int64 tensor on either device.
    orig_device = logits.device
    if orig_device.type == 'mps':
        logits = logits.cpu()
        targets = targets.cpu()
    # (N, 1) gather — score of the true class per row
    target_scores = logits.gather(dim=-1, index=targets.unsqueeze(-1))
    # Chunked computation: the naive (logits > target_scores) materialises
    # an [N × C] boolean tensor that, on FL (127K samples × 4702 regions
    # × 1 byte ≈ 600 MB *expanded to 4.46 GB during the .sum reduction*),
    # OOM-killed the T4 mid-validation. Process in row-chunks so peak
    # allocation is bounded by chunk × C ≈ 80 MB on FL.
    n = logits.size(0)
    chunk = 4096
    higher = torch.empty(n, dtype=torch.long, device=logits.device)
    for i in range(0, n, chunk):
        higher[i:i + chunk] = (logits[i:i + chunk] > target_scores[i:i + chunk]).sum(dim=-1)
    return higher + 1


def _mrr_from_rank(rank: torch.Tensor) -> float:
    return (1.0 / rank.float()).mean().item()


def _ndcg_from_rank(rank: torch.Tensor, k: int) -> float:
    """NDCG@K with single-relevant-item binary relevance, given precomputed rank."""
    hit = rank <= k
    # Use float math; add 1 so rank=1 -> log2(2) = 1 -> DCG=1.
    dcg = torch.where(
        hit,
        1.0 / torch.log2(rank.float() + 1.0),
        torch.zeros_like(rank, dtype=torch.float32),
    )
    return dcg.mean().item()


def _streamed_cls_metrics(preds, tgts, rank, hit, num_classes, top_k=(3, 5)) -> dict:
    """Reconstruct the hand-rolled (C>256) classification-metric dict from streamed
    per-row accumulators: ``preds``/``tgts``/``rank`` concatenated, ``hit`` a
    ``{k: bool tensor}`` dict (must contain every k in ``top_k``).

    Byte-identical to ``compute_classification_metrics(full logits, top_k)`` on the
    hand-rolled path — same helpers, keys and order; the reductions are per-row /
    additive so they are device-independent. Shared by the S1 streaming TRAIN metric
    (``mtl_cv``, CPU tensors) and the S2 chunked VAL metric (``mtl_eval``, GPU tensors).
    """
    acc_micro, acc_macro, f1_macro, f1_weighted = _handrolled_cls_metrics(preds, tgts, num_classes)
    metrics = {
        "accuracy": acc_micro,
        "accuracy_macro": acc_macro,
        "f1": f1_macro,
        "f1_weighted": f1_weighted,
        "mrr": _mrr_from_rank(rank),
    }
    for k in top_k:
        metrics[f"top{k}_acc"] = hit[k].float().mean().item()
        metrics[f"ndcg_{k}"] = _ndcg_from_rank(rank, k)
    return metrics


def _mean_reciprocal_rank(logits: torch.Tensor, targets: torch.Tensor) -> float:
    return _mrr_from_rank(_rank_of_target(logits, targets))


def _ndcg_at_k(logits: torch.Tensor, targets: torch.Tensor, k: int) -> float:
    """NDCG@K with single-relevant-item binary relevance.

    IDCG is 1 (one relevant item, perfectly ranked). DCG is
    ``1 / log2(rank + 1)`` if the true class falls in the top-k, else 0.
    """
    return _ndcg_from_rank(_rank_of_target(logits, targets), k)


# Above this class count, `compute_classification_metrics` switches from torchmetrics to the
# hand-rolled per-class accumulation (torchmetrics' confusion-matrix path allocates
# num_classes**2 * batch floats internally — ~30 GB at 1K classes x 6K batch, on any device).
# Module-level so callers that reconstruct the hand-rolled dict — `_streamed_cls_metrics` and its
# users in mtl_eval.py / p1_region_head_ablation.py — can gate on the SAME cutoff instead of
# duplicating the literal and silently diverging if it ever moves.
_CARDINALITY_HAND_ROLLED_THRESHOLD = 256


def ambiguity_strict() -> bool:
    """Should an ambiguous row ABORT the run?

    One function because there are two gates — the accumulator's (here) and p1's per-epoch one —
    and when they read the environment independently they drifted: `MTL_AMBIGUITY_STRICT` was
    added to this file and p1's copy kept reading `MTL_STRICT`, so disabling the abort disabled
    only half of it and the cell died anyway at the other gate. Same question, one answer.

    `MTL_AMBIGUITY_STRICT` wins when set; otherwise this follows `MTL_STRICT`, so existing
    recipes are unaffected.
    """
    v = os.environ.get("MTL_AMBIGUITY_STRICT")
    if v is not None:
        return v.strip() in ("1", "true", "True")
    return os.environ.get("MTL_STRICT", "0").strip() in ("1", "true", "True")


class StreamingClsMetrics:
    """Accumulate the inputs of the hand-rolled metric dict one batch at a time.

    Motivation: the "keep only per-row reductions, never materialise ``[N, C]``" trick was
    reimplemented independently in THREE places — the S2 val metric (``mtl_eval``), the S1 train
    metric (``mtl_cv``) and the p1 region ablation — each with its own copy of the same four
    accumulators and its own copy of the ``> 256`` literal. Three copies of a loop is three
    chances to get it subtly wrong, and the p1 copy shipped with a read-before-assignment that
    made every streamed run die on ``UnboundLocalError``; it was caught only by running it, since
    a unit test of ``_streamed_cls_metrics`` never touches the caller's loop. This class is the
    one implementation they now share, so a fix lands everywhere and a new caller cannot invent a
    fourth variant.

    Equivalence: ``compute()`` is **byte-identical** to
    ``compute_classification_metrics(full_logits, top_k)`` on the hand-rolled path, because every
    metric is a per-row reduction (``argmax`` / ``topk`` hit / strict-``>`` rank) or an additive
    per-class count. Two documented exceptions, neither reachable from the current call sites:
    at ``k <= 1`` the full path omits ``top{k}_acc``/``ndcg_{k}`` while this one emits them, and
    at ``N == 0`` the full path returns a zeros dict while ``compute()`` raises on ``torch.cat``
    of an empty list (guard the empty-loader case at the call site, as ``mtl_eval`` does). Batching cannot change a per-row quantity, so batch size is irrelevant to the
    result. Pinned by ``tests/test_tracking/test_streaming_cls_metrics.py``, which also carries
    the pre-refactor inline loops verbatim as golden references.

    Two INDEPENDENT device knobs, because the existing callers genuinely differ and collapsing
    them into one flag would silently change behaviour:

    * ``move_logits_to`` — where the per-row ops RUN. ``None`` keeps them on the logits' device.
      Setting ``"cpu"`` moves each batch's logits before reducing (p1's default, which preserves
      the CPU-scored path every banked reg cell used). This is the one knob that is **not**
      bit-identical across settings: ``topk``'s tie-break at the k-boundary is a kernel detail.
      Measured on real region logits: 0 boundary ties in 100 448 rows and a worst cross-device
      delta of 5.96e-08, but use ``diagnose_ties`` rather than assuming it.
    ``hits_from_rank`` is the DEFAULT (2026-08-10). It removes ``topk`` from the scoring path:
    ``hit@k == (rank <= k)`` whenever no row is ambiguous, which is an integer comparison and is
    therefore the same on CPU and CUDA — unlike ``topk``, whose tie-break is a kernel detail. That
    is what let the val metric move back onto the GPU, which is worth more than the arithmetic it
    saves: the per-batch ``logits.to("cpu")`` it replaces was synchronising the host every
    iteration and serialising the GPU (measured: removing it cut 6.4 s from a wall whose scoring
    was only 2.87 s). Pass ``hits_from_rank=False`` for the historical topk semantics.

    * ``store_on`` — where the tiny ``[N]`` accumulators are KEPT. ``"cpu"`` reduces on the GPU
      and parks the results in host memory (mtl_cv's S1 behaviour). Pure memory placement: moving
      an int64 rank vector between devices cannot change its value.

    ``diagnose_ties`` counts, per k, the rows whose reported hit@k is genuinely AMBIGUOUS — the
    only condition under which the tie-break (and therefore ``move_logits_to``, or any change to
    how top-k is obtained) can alter a reported number. A row is ambiguous iff the target sits in
    a tie group straddling the k boundary::

        n_gt < k < n_gt + n_eq        n_gt = #{strictly greater}, n_eq = #{equal, incl. target}

    An earlier version counted instead how often the k-th and (k+1)-th LOGITS were equal, which
    is a different and much larger set: a tie between two non-target classes cannot change any
    reported number. Measured on 4096x6553 with mildly-rounded logits, that version fired on
    48-62 rows while the true ambiguous count — and the observed divergence — were both **0**;
    with heavy ties it fired on all 4096 rows against 90 truly ambiguous and 1 actually divergent.
    A gate that over-reports by three orders of magnitude will veto changes that are provably
    safe, which is exactly what it did.

    Cost: ``n_gt`` is already known (``rank - 1``), so this adds ONE equality pass over the batch
    rather than the ``topk(max_k + 1)`` the old version needed.
    """

    def __init__(self, num_classes: int, top_k: Iterable[int] = (3, 5),
                 move_logits_to=None, store_on=None, diagnose_ties: bool = False,
                 hits_from_rank: bool = True, strict: bool | None = None):
        self.num_classes = int(num_classes)
        self.top_k = tuple(top_k)
        self.move_logits_to = move_logits_to
        self.store_on = store_on
        # Deriving hits from the rank REQUIRES the ambiguity count — it is the certificate that
        # the derivation matches what topk would have returned, so it is not optional there.
        self.hits_from_rank = bool(hits_from_rank)
        self.diagnose_ties = bool(diagnose_ties) or self.hits_from_rank
        # MTL_AMBIGUITY_STRICT decouples THIS abort from MTL_STRICT. They were the same switch,
        # which forced an all-or-nothing choice: keep MTL_STRICT and lose the cell to a single
        # ambiguous row, or drop it and also disarm the canon-recipe and overlap-provenance guards
        # that have nothing to do with tie-breaks. Both texas and california trip the certificate
        # at ~1 row in 766k (0.00013 pp, at the edge of the 4-dp quantum), so the study needs to
        # be able to accept that deliberately while keeping every other guard armed.
        self.strict = bool(strict) if strict is not None else ambiguity_strict()
        self._preds, self._tgts, self._rank = [], [], []
        self._hit = {k: [] for k in self.top_k}
        self.tie_counts = {k: 0 for k in self.top_k}
        self.n_rows = 0
        self.compute_device = None   # filled on first update, for logging
        self._cat = None             # memoised concat; invalidated by update()

    @staticmethod
    def should_stream(num_classes) -> bool:
        """Is streaming equivalent at this cardinality?

        ``_streamed_cls_metrics`` rebuilds the HAND-ROLLED dict, so it only matches
        ``compute_classification_metrics`` above the same cutoff that function uses to leave
        torchmetrics. Callers must gate on this instead of re-typing the literal.
        """
        return num_classes is not None and int(num_classes) > _CARDINALITY_HAND_ROLLED_THRESHOLD

    def update(self, logits: torch.Tensor, targets: torch.Tensor) -> "StreamingClsMetrics":
        logits = logits.detach()
        if self.move_logits_to is not None:
            logits = logits.to(self.move_logits_to)
            targets = targets.to(self.move_logits_to)
        self.compute_device = logits.device
        keep = (lambda t: t.to(self.store_on)) if self.store_on is not None else (lambda t: t)
        # `preds` stays an honest argmax. Taking it from topk position 0 is NOT covered by the
        # ambiguity predicate: a tie for the row maximum between two NON-target classes leaves the
        # predicate at zero while changing which class is predicted — and `preds` feeds the
        # per-class bincounts behind macro-F1, which selects checkpoints in `_single_task_train`.
        self._preds.append(keep(logits.argmax(dim=-1)))
        self._tgts.append(keep(targets))
        if self.hits_from_rank or self.diagnose_ties:
            rank, n_eq = _rank_and_ties(logits, targets)
        else:
            rank, n_eq = _rank_of_target(logits, targets), None
        self._rank.append(keep(rank))
        n_cls = logits.shape[-1]
        if self.hits_from_rank:
            # hit@k == (rank <= k) whenever nothing is ambiguous — see `_rank_and_ties`. No topk,
            # so no sort order, no tie order, no kernel dependence: this is the same integer on
            # CPU and CUDA. `min(k, C)` mirrors the topk path's clamp for C < k (there every
            # class is in the top-k, and rank <= C always holds, so both say "hit").
            for k in self.top_k:
                self._hit[k].append(keep(rank <= min(k, n_cls)))
        else:
            for k in self.top_k:
                ke = min(k, n_cls)
                self._hit[k].append(
                    keep((logits.topk(ke, dim=-1).indices == targets.unsqueeze(-1)).any(dim=-1)))
        if self.diagnose_ties:
            self._record_ambiguous(rank, n_eq, n_cls)
        self.n_rows += int(logits.shape[0])
        self._cat = None
        return self

    def _record_ambiguous(self, rank: torch.Tensor, n_eq: torch.Tensor, n_cls: int) -> None:
        """Rows where the target's own hit@k depends on an arbitrary tie-break.

        Both inputs come from the single `_rank_and_ties` pass, so this costs no extra read of
        the logits. Under `strict`, a non-zero count raises immediately: with `hits_from_rank`
        the count is the certificate of equivalence, so continuing past it would bank a number
        that silently uses tie-optimistic semantics where its siblings used the kernel's
        arbitrary pick.
        """
        n_gt = rank - 1
        for k in self.top_k:
            if k < n_cls:
                hits = int(((n_gt < k) & (k < n_gt + n_eq)).sum())
                self.tie_counts[k] += hits
                # Strict aborts ONLY when the certificate is load-bearing, i.e. when hits are
                # derived from the rank. With the topk path the count is informational: the
                # arbitrary tie-break is what every banked sibling used, so ambiguity is not an
                # error there. Raising regardless would kill every joint cell in the lane
                # (run_lane.sh sets MTL_STRICT=1) the moment fp16 eval produced a single tie.
                if hits and self.strict and self.hits_from_rank:
                    raise RuntimeError(
                        f"[StreamingClsMetrics] {hits} rows are AMBIGUOUS at the {k}/{k + 1} "
                        f"boundary (the target sits in a tie group straddling k). "
                        f"hits_from_rank={self.hits_from_rank}: the metric would use "
                        f"tie-optimistic semantics on those rows while a topk-scored sibling "
                        f"cell used the kernel's arbitrary pick. To reproduce the banked "
                        f"semantics exactly, re-run with P1_HITS_FROM_RANK=0 P1_STREAM_GPU=0 "
                        f"(streamed, so no [N, C] buffer, but CPU + topk as the siblings used). "
                        f"To accept the tie-optimistic value deliberately, unset MTL_STRICT.")

    @property
    def has_ties(self) -> bool:
        return any(v > 0 for v in self.tie_counts.values())

    def tie_summary(self) -> str:
        return "; ".join(
            f"top{k} (target ambiguous at the {k}/{k + 1} boundary): "
            f"{self.tie_counts[k]}/{self.n_rows} "
            f"({100.0 * self.tie_counts[k] / max(self.n_rows, 1):.4f}%)"
            for k in self.top_k)

    def concat(self):
        """The concatenated ``(preds, targets, rank, hit)`` accumulators.

        Exposed because the metric dict is not the only consumer: ``mtl_eval`` feeds the same
        ``targets``/``rank``/``hit`` into the OOD-restricted Acc@K block and the opt-in val-pred
        dump. Those must read the SAME tensors the metrics were computed from — recomputing them
        from a second pass would be both wasteful and a chance to drift.
        """
        # Memoised: `mtl_eval` needs the tensors for the OOD block AND calls compute(), which
        # concatenates too. Without this that is a second full O(N) allocation and pass for no
        # reason, and the two copies are only value-identical, not the same objects. Invalidated
        # by update() so a caller that accumulates further cannot read a stale concat.
        if self._cat is None:
            self._cat = (torch.cat(self._preds), torch.cat(self._tgts), torch.cat(self._rank),
                         {k: torch.cat(v) for k, v in self._hit.items()})
        return self._cat

    def compute(self, top_k: Iterable[int] | None = None,
                num_classes: int | None = None) -> Dict[str, float]:
        """``top_k`` narrows the REPORTED ks to a subset of the accumulated ones.

        ``mtl_eval`` accumulates hits at (1, 3, 5, 10) — the union of what the metric dict needs
        and what the OOD block needs — but reports only (3, 5). Accumulating the union once is
        cheaper than a second pass, so reporting has to be able to ask for less than was kept.

        ``num_classes`` overrides the count used for the per-class F1 accumulation. The class is
        constructed inside the eval loop, where the caller may only have the *gate* cardinality;
        the authoritative value can be resolved later. Passing it here keeps the resolution at
        the call site instead of mutating the attribute behind the reader's back.
        """
        ks = self.top_k if top_k is None else tuple(top_k)
        nc = self.num_classes if num_classes is None else int(num_classes)
        missing = [k for k in ks if k not in self._hit]
        if missing:
            raise KeyError(f"top_k={missing} was never accumulated (have {sorted(self._hit)})")
        preds, tgts, rank, hit = self.concat()
        return _streamed_cls_metrics(preds, tgts, rank, hit, nc, top_k=ks)


def compute_classification_metrics(
    logits: torch.Tensor,
    targets: torch.Tensor,
    num_classes: int,
    top_k: Iterable[int] = (3, 5),
    prefix: str = "",
) -> Dict[str, float]:
    """Compute every classification/ranking metric we track, in one pass.

    Args:
        logits: ``(N, C)`` float tensor. May live on CPU, CUDA or MPS.
        targets: ``(N,)`` int tensor of class indices.
        num_classes: Number of classes ``C``. Required by torchmetrics.
        top_k: K values to report Top-K accuracy and NDCG@K for. ``k=1`` is
            skipped because it would duplicate ``accuracy``.
        prefix: Optional key prefix (e.g. ``"val_"``). Applied to every
            returned key.

    Returns:
        ``dict[str, float]``: every value is a plain Python float, safe to
        pass straight into ``MetricStore.log(**kwargs)``.

    Empty batch (``N == 0``) is tolerated and returns zeros for every key
    the non-empty path would have produced — this keeps test harnesses with
    degenerate loaders happy without forcing a guard at every call site.
    """
    if logits.ndim != 2:
        raise ValueError(f"logits must be 2-D (N, C); got shape {tuple(logits.shape)}")
    if targets.ndim != 1:
        raise ValueError(f"targets must be 1-D (N,); got shape {tuple(targets.shape)}")
    if logits.shape[0] != targets.shape[0]:
        raise ValueError(
            f"logits N={logits.shape[0]} != targets N={targets.shape[0]}"
        )

    def _key(name: str) -> str:
        return f"{prefix}{name}"

    # Degenerate batch — return zeros for every key we would have produced.
    if logits.shape[0] == 0:
        out: Dict[str, float] = {
            _key("accuracy"): 0.0,
            _key("accuracy_macro"): 0.0,
            _key("f1"): 0.0,
            _key("f1_weighted"): 0.0,
            _key("mrr"): 0.0,
        }
        for k in top_k:
            if k > 1:
                out[_key(f"top{k}_acc")] = 0.0
                out[_key(f"ndcg_{k}")] = 0.0
        return out

    # Targets and logits must share a device for torchmetrics / torch ops.
    if targets.device != logits.device:
        targets = targets.to(logits.device)

    # torchmetrics expects integer predictions for the top-1 path.
    preds = logits.argmax(dim=-1)

    # High-cardinality heads (e.g. next_region with ~10^3 classes) blow up
    # **any** device in torchmetrics' confusion-matrix path — bincount
    # allocates ``num_classes**2 * batch_size`` floats internally. For
    # 1K classes × 6K batch that's ~30GB regardless of CPU/MPS/CUDA.
    # Above the threshold, use hand-rolled per-class accumulation via
    # ``torch.bincount`` on 1-D inputs, which stays O(N + num_classes)
    # memory and is numerically equivalent to torchmetrics for the
    # micro/macro-averaged accuracy and F1 we report.
    if num_classes > _CARDINALITY_HAND_ROLLED_THRESHOLD:
        acc_micro, acc_macro, f1_macro, f1_weighted = _handrolled_cls_metrics(
            preds, targets, num_classes,
        )
    else:
        acc_micro = multiclass_accuracy(
            preds, targets, num_classes=num_classes, average="micro"
        ).item()
        acc_macro = multiclass_accuracy(
            preds, targets, num_classes=num_classes, average="macro"
        ).item()
        f1_macro = multiclass_f1_score(
            preds, targets, num_classes=num_classes, average="macro", zero_division=0
        ).item()
        f1_weighted = multiclass_f1_score(
            preds, targets, num_classes=num_classes, average="weighted", zero_division=0
        ).item()

    # Compute rank-of-target once and reuse for MRR + NDCG@k. The chunked
    # `[N × C]` comparison inside `_rank_of_target` is the dominant cost on
    # high-cardinality heads (FL: 31 chunks × ~80 MB each per validation
    # pass) — without caching, MRR + NDCG@3 + NDCG@5 each rebuild it,
    # tripling the work.
    rank = _rank_of_target(logits, targets)
    metrics: Dict[str, float] = {
        _key("accuracy"): acc_micro,
        _key("accuracy_macro"): acc_macro,
        _key("f1"): f1_macro,
        _key("f1_weighted"): f1_weighted,
        _key("mrr"): _mrr_from_rank(rank),
    }

    for k in top_k:
        if k <= 1:
            continue
        metrics[_key(f"top{k}_acc")] = _top_k_accuracy(logits, targets, k)
        metrics[_key(f"ndcg_{k}")] = _ndcg_from_rank(rank, k)

    return metrics


__all__ = ["compute_classification_metrics", "StreamingClsMetrics", "ambiguity_strict"]
