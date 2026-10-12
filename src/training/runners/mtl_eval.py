import contextlib
import logging
import os

import torch

logger = logging.getLogger(__name__)

from tracking.metrics import (
    StreamingClsMetrics,
    compute_classification_metrics,
    _rank_of_target,
)
from utils.precision import check_amp_dtype
from utils.progress import zip_longest_cycle


def _ood_restricted_topk(
    logits: torch.Tensor,
    targets: torch.Tensor,
    train_label_set: set[int],
    ks: tuple[int, ...] = (1, 5, 10),
) -> dict[str, float]:
    """Acc@K restricted to in-distribution samples (target in train set).

    Returns keys ``top{k}_acc_indist`` for each k, plus ``n_indist``
    (count of in-distribution samples) and ``n_ood`` (count of OOD).
    If all samples are OOD, returns 0.0 for every metric.
    """
    # Vectorised membership test: building the mask via Python iteration with
    # `.item()` per target forces an N-element host↔device sync — on FL val
    # (~31K rows) that's ~31K syncs per validation pass, ≈1–2s wasted per
    # epoch × 50 epochs × 5 folds. `torch.isin` does it in one kernel.
    train_labels_t = torch.as_tensor(
        sorted(train_label_set), dtype=targets.dtype, device=targets.device,
    )
    in_dist_mask = torch.isin(targets, train_labels_t)
    n_indist = int(in_dist_mask.sum().item())
    n_ood = len(targets) - n_indist

    result: dict[str, float] = {
        "n_indist": float(n_indist),
        "n_ood": float(n_ood),
        "ood_fraction": float(n_ood / max(len(targets), 1)),
    }

    if n_indist == 0:
        for k in ks:
            result[f"top{k}_acc_indist"] = 0.0
        result["mrr_indist"] = 0.0
        return result

    logits_id = logits[in_dist_mask]
    targets_id = targets[in_dist_mask]

    for k in ks:
        k_eff = min(k, logits_id.shape[-1])
        topk = logits_id.topk(k_eff, dim=-1).indices
        hit = (topk == targets_id.unsqueeze(-1)).any(dim=-1)
        result[f"top{k}_acc_indist"] = float(hit.float().mean().item())

    # MRR on in-distribution subset (_rank_of_target imported at module top)
    rank = _rank_of_target(logits_id, targets_id).float()
    result["mrr_indist"] = float((1.0 / rank).mean().item())

    return result


def _ood_from_streamed(tgts, rank, hit, train_labels, ks=(1, 5, 10)) -> dict:
    """OOD-restricted Acc@K / MRR from streamed accumulators (the S2 chunked val path).

    Byte-identical to ``_ood_restricted_topk`` on the same data: hit/rank are per-row, so
    ``hit[k][mask] == top-k hit on logits[mask]``; one ``.float().mean()`` (NOT a running
    int count — that drifts at the last ULP).
    """
    train_t = torch.as_tensor(sorted(train_labels), dtype=tgts.dtype, device=tgts.device)
    mask = torch.isin(tgts, train_t)
    n_indist = int(mask.sum().item())
    n_ood = len(tgts) - n_indist
    out = {
        "n_indist": float(n_indist), "n_ood": float(n_ood),
        "ood_fraction": float(n_ood / max(len(tgts), 1)),
    }
    if n_indist == 0:
        for k in ks:
            out[f"top{k}_acc_indist"] = 0.0
        out["mrr_indist"] = 0.0
    else:
        for k in ks:
            out[f"top{k}_acc_indist"] = float(hit[k][mask].float().mean().item())
        out["mrr_indist"] = float((1.0 / rank[mask].float()).mean().item())
    return out


def eval_autocast_ctx(device):
    """fp16 eval autocast on CUDA; fp32 (nullcontext) when MTL_DISABLE_AMP_EVAL=1 or
    MTL_DISABLE_AMP=1. Shared by evaluate_model + validation_best_model so the fp32-eval
    escape hatch is byte-identical across both eval paths."""
    disable = (
        os.environ.get("MTL_DISABLE_AMP_EVAL") == "1"
        or os.environ.get("MTL_DISABLE_AMP") == "1"
    )
    if device.type == "cuda" and not disable:
        check_amp_dtype("mtl_eval.evaluate_model (val)", torch.float16)
        return torch.autocast(device.type, dtype=torch.float16)
    return contextlib.nullcontext()


def _decide_chunk_val(dataloaders, nc_b_gate) -> bool:
    """Whether to use the chunked/streaming S2 val-metric for the reg head.

    The full path cats the whole val epoch's [N, n_regions] reg logits on GPU (OOMs the
    A40 at CA/TX overlap scale). Chunking streams per-batch reductions and assembles a
    byte-identical metric dict, so we enable it when explicitly requested
    (``MTL_CHUNK_VAL_METRIC=1``) OR auto-enable it (one-time WARN) when the full logit
    would exceed ``MTL_S2_AUTO_BUDGET_GB`` (default 4 GB). Reg-only (C > 256, the
    hand-rolled metric path); selecting it never changes the scored numbers.
    """
    s2_env = os.environ.get("MTL_CHUNK_VAL_METRIC", "").strip() in ("1", "true", "True")
    full_logit_gb, n_val = 0.0, -1
    try:
        n_val = len(dataloaders[0].dataset)
        full_logit_gb = n_val * int(nc_b_gate or 0) * 4 / (1024 ** 3)
    except Exception:
        pass
    budget_gb = float(os.environ.get("MTL_S2_AUTO_BUDGET_GB", "4"))
    auto_chunk = full_logit_gb > budget_gb
    if auto_chunk and not s2_env:
        logger.warning(
            "[S2 auto] full val reg-logit ≈ %.1f GB (N_val=%d × C=%d) exceeds the %.1f GB "
            "budget — auto-enabling the chunked val metric (byte-identical) to avoid a GPU OOM. "
            "Set MTL_CHUNK_VAL_METRIC=1 to silence, or MTL_S2_AUTO_BUDGET_GB to tune.",
            full_logit_gb, n_val, int(nc_b_gate or 0), budget_gb,
        )
    # Gate on the SHARED cutoff: streaming rebuilds the hand-rolled dict, so it is only
    # equivalent above the same cardinality where compute_classification_metrics leaves
    # torchmetrics. Re-typing 256 here is how the two silently drift apart.
    return (s2_env or auto_chunk) and StreamingClsMetrics.should_stream(nc_b_gate)


@torch.no_grad()
def evaluate_model(
    model,
    dataloaders,
    next_criterion,
    category_criterion,
    mtl_criterion,
    device,
    num_classes: int | None = None,
    task_b_num_classes: int | None = None,
    task_a_num_classes: int | None = None,
    train_labels_b: set[int] | None = None,
    train_labels_a: set[int] | None = None,
):
    """Unified MTL validation pass — computes loss and the full metric dict per task.

    Uses ``zip_longest_cycle`` to match training coverage — the shorter loader
    is cycled so all samples from both loaders are evaluated. Logits are kept
    on-device through ``compute_classification_metrics``, which produces the
    legacy ``f1``/``accuracy`` keys **plus** ``f1_weighted``, ``accuracy_macro``,
    ``top{k}_acc``, ``mrr`` and ``ndcg_{k}``. Each per-task metric dict also
    carries its own ``'loss'`` key so the caller can forward the whole dict
    via ``**`` straight into ``log_val`` without hand-wiring scalars.

    Args:
        model: The MTLPOI model.
        dataloaders: List of ``[next_dataloader, category_dataloader]``.
        next_criterion: Loss function for the next task.
        category_criterion: Loss function for the category task.
        mtl_criterion: MTL loss (unused for validation loss — kept for API compat).
        device: Device to run evaluation on.

    Returns:
        Tuple ``(metrics_next, metrics_category, loss_combined)``:
            * ``metrics_next`` / ``metrics_category`` — dicts from
              ``compute_classification_metrics`` with an added
              per-task ``'loss'`` key.
            * ``loss_combined`` — scalar average of
              ``(next_loss + category_loss) / 2`` across batches, kept
              for the MTL-level ``model_task`` tracking store.
    """
    model.eval()
    combined_running_loss = torch.tensor(0.0, device=device)
    next_running_loss = torch.tensor(0.0, device=device)
    category_running_loss = torch.tensor(0.0, device=device)
    logits_next_list, truths_next_list = [], []
    logits_cat_list, truths_cat_list = [], []
    batches = 0

    # Chunked/streaming val metric for the high-cardinality reg head: byte-identical to the
    # full-logit path but avoids the A40 GPU-OOM from cat-ing the whole val epoch's
    # [N, n_regions] logits at CA/TX scale (4.7k-8.5k regions). Every reg metric (incl. the
    # SCORED top10_acc_indist) is a per-row reduction or per-class count, streamed on GPU
    # (rank-derived hits since 2026-08-10, so no topk tie-break to match — NEVER CPU-moved). Reg only; cat (C=7)
    # keeps the full path. Gated by MTL_CHUNK_VAL_METRIC (default OFF). See _decide_chunk_val.
    _nc_b_gate = task_b_num_classes if task_b_num_classes is not None else (
        num_classes if num_classes is not None else getattr(model, "num_classes", 0)
    )
    _chunk_val = _decide_chunk_val(dataloaders, _nc_b_gate)
    _S2_KS = (1, 3, 5, 10)  # union of metrics_next top_k=(3,5) and ood ks=(1,5,10)
    # Shared accumulator (tracking.metrics) — same per-row reductions this loop used inline,
    # now in the one place mtl_cv and p1 also call, so the pattern has a single implementation.
    # diagnose_ties ON because this is the SCORED MTL reg path: the certificate has to be
    # measured where the number is produced, not inferred from another state or another family.
    # (An earlier version of this comment justified it by fp16 tie-manufacturing. That was the
    # wrong reason: every v18 cell pins fp32 via MTL_DISABLE_AMP=1, so fp16 is not a live path
    # here — it is a defect the protocol excludes, see utils/precision.py.)
    _s2 = StreamingClsMetrics(_nc_b_gate or 0, top_k=_S2_KS, diagnose_ties=True)

    # Opt-in per-sample val-prediction dump (MTL_DUMP_VAL_PREDS=1). Feeds the
    # geographic near-miss metric (articles/[mobiwac]/MOBILITY_PLAN.md §3,
    # analysis/near_miss_distance.py); mtl_cv.py writes the actual parquet file
    # on a reg diagnostic-best improvement. Strict no-op when unset: the extra
    # top-10-index accumulator below is only ever appended to under this gate,
    # and the dict key this function adds to metrics_next (see the end of this
    # function) is only added under this gate — no shape/value change to any
    # existing computation when MTL_DUMP_VAL_PREDS is unset.
    _dump_env = os.environ.get("MTL_DUMP_VAL_PREDS") == "1"
    _dump_top10_list: list[torch.Tensor] = []

    # Eval-precision escape hatch. MTL eval autocasts fp16 on CUDA unconditionally, but the
    # STL ceiling harness evaluates in fp32; over ~5-9k region logits fp16 quantisation creates
    # more exact ties → _rank_of_target scores MTL ranks tie-optimistically vs the fp32 ceiling.
    # Set MTL_DISABLE_AMP_EVAL=1 (or the training hatch MTL_DISABLE_AMP=1) to force fp32 eval.
    # Default (unset) keeps canonical fp16 eval untouched.
    _autocast_ctx = eval_autocast_ctx(device)

    # Cross-attn pairing roll probe. The two MTL train loaders draw independent shuffles, so
    # cross-attn mixes RANDOMLY-paired cat↔reg rows at train time while val is aligned. Probe:
    # roll the task-b (reg / `x_next`) stream by 1 along the batch dim at EVAL only → cat row i
    # cross-attends reg row i−1. If cat-F1 is unchanged the model ignores per-sample pairing.
    # (reg metric is meaningless under the roll — read cat-F1 only.) Gate MTL_ROLL_TASKB_EVAL=1.
    _roll_taskb = os.environ.get("MTL_ROLL_TASKB_EVAL") == "1"

    # pipeline_audit 2026-07-01 (V9) — when the two VAL loaders differ in
    # length (legacy task pairs only; never the check2hgi track, where both
    # tasks share val_idx → equal lengths), zip_longest_cycle re-feeds the
    # shorter loader's leading batches and their outputs are counted AGAIN in
    # the scored metrics, over-weighting a deterministic subset of that task's
    # val samples. WARN loudly rather than silently over-count.
    _len_next, _len_cat = len(dataloaders[0]), len(dataloaders[1])
    if _len_next != _len_cat:
        logger.warning(
            "[val-cycle] val loaders differ in length (next=%d, cat=%d): "
            "zip_longest_cycle double-counts the shorter task's leading val "
            "samples in the scored metrics (legacy-pair behavior; the "
            "check2hgi track is immune). Interpret that task's val F1/Acc "
            "with caution.", _len_next, _len_cat,
        )

    for data_next, data_cat in zip_longest_cycle(*dataloaders):
        x_next, y_next = data_next
        if x_next.device != device:
            x_next = x_next.to(device, non_blocking=True)
            y_next = y_next.to(device, non_blocking=True)
        x_category, y_category = data_cat
        if x_category.device != device:
            x_category = x_category.to(device, non_blocking=True)
            y_category = y_category.to(device, non_blocking=True)

        if _roll_taskb and x_next.shape[0] > 1:
            x_next = torch.roll(x_next, shifts=1, dims=0)

        with _autocast_ctx:
            cat_out, next_out = model((x_category, x_next))
            next_loss = next_criterion(next_out, y_next)
            category_loss = category_criterion(cat_out, y_category)
        # Accumulate on-device; single .item() sync after the loop.
        next_running_loss += next_loss.detach()
        category_running_loss += category_loss.detach()
        combined_running_loss += (next_loss.detach() + category_loss.detach()) / 2

        # cat (task_a) — low-card, always full path.
        logits_cat_list.append(cat_out.detach())
        truths_cat_list.append(y_category)
        if _chunk_val:
            # reg (task_b) — STREAM per-row reductions ON GPU (canonical fp16 tie-break);
            # discard the [batch, n_regions] logits so the full [N, C] is never materialized.
            _no = next_out.detach()
            _s2.update(_no, y_next)
            if _dump_env:
                # Real top-10 predicted indices (not just the hit boolean
                # above) — only materialized under the opt-in dump flag; the
                # scored metrics above never read this.
                _ke10 = min(10, _no.shape[-1])
                _dump_top10_list.append(_no.topk(_ke10, dim=-1).indices.cpu())
            del _no
        else:
            logits_next_list.append(next_out.detach())
            truths_next_list.append(y_next)
        batches += 1

    if batches == 0:
        empty = compute_classification_metrics(
            torch.zeros(0, model.num_classes, device=device),
            torch.zeros(0, dtype=torch.long, device=device),
            num_classes=model.num_classes,
        )
        empty['loss'] = 0.0
        return empty, dict(empty), 0.0

    loss_combined = combined_running_loss.item() / batches
    loss_next = next_running_loss.item() / batches
    loss_category = category_running_loss.item() / batches

    all_logits_category = torch.cat(logits_cat_list)
    all_truths_category = torch.cat(truths_cat_list)

    if num_classes is None:
        num_classes = model.num_classes
    # Default: use the same num_classes for both (legacy 2-task path).
    # For non-legacy task_sets (e.g. check2HGI: cat=7, region~1109) the
    # caller passes per-task values to avoid torchmetrics OOM at
    # num_classes^2 on the large-cardinality head.
    nc_b = task_b_num_classes if task_b_num_classes is not None else num_classes
    nc_a = task_a_num_classes if task_a_num_classes is not None else num_classes

    if _chunk_val:
        # Reg metrics_next from the streamed accumulators (byte-identical to
        # compute_classification_metrics(full reg logits, top_k=(3,5)) on the C>256
        # handrolled path: same helpers, same keys/order; preds/rank/hit per-row, on-GPU).
        # _T/_R/_HIT are reused by the OOD block and the val-pred dump below, so they come from
        # the SAME accumulators the metrics are built from rather than a second pass.
        _, _T, _R, _HIT = _s2.concat()
        metrics_next = _s2.compute(top_k=(3, 5), num_classes=nc_b)
    else:
        all_logits_next = torch.cat(logits_next_list)
        all_truths_next = torch.cat(truths_next_list)
        metrics_next = compute_classification_metrics(
            all_logits_next, all_truths_next, num_classes=nc_b,
        )
    metrics_category = compute_classification_metrics(
        all_logits_category, all_truths_category, num_classes=nc_a,
    )
    metrics_next['loss'] = loss_next
    metrics_category['loss'] = loss_category

    # OOD-restricted Acc@K for CH06. When the caller provides the set of
    # labels seen in the current training fold, we filter val samples to
    # those whose target label is in-distribution and compute ranking
    # metrics on that subset. Keys are suffixed ``_indist``. This guards
    # against the artefact where a model scores well on train-overlap
    # POIs but 0 on OOD POIs, and the raw Acc@K averages across both.
    if train_labels_b is not None:
        if _chunk_val:
            ood_b = _ood_from_streamed(_T, _R, _HIT, train_labels_b)
        else:
            ood_b = _ood_restricted_topk(all_logits_next, all_truths_next, train_labels_b)
        metrics_next.update(ood_b)
    if train_labels_a is not None:
        ood_a = _ood_restricted_topk(all_logits_category, all_truths_category, train_labels_a)
        metrics_category.update(ood_a)

    # Opt-in per-sample val-prediction dump (MTL_DUMP_VAL_PREDS=1) — stash the
    # payload under a leading-underscore key so it rides evaluate_model's
    # existing 3-tuple return without changing its arity; mtl_cv.py pops this
    # key BEFORE forwarding **metrics_next to fold_history.log_val (which
    # forwards straight into a scalar MetricStore/CSV writer — a raw tensor
    # entry would corrupt it). Absent entirely when the env var is unset, so
    # every existing consumer of metrics_next (incl. tests/test_training/
    # test_mtl_eval.py, which checks an exact key allowlist) is untouched.
    if _dump_env:
        if _chunk_val:
            _dump_true = _T
            _dump_top10 = (
                torch.cat(_dump_top10_list) if _dump_top10_list
                else _T.new_empty((0, 0))
            )
        else:
            _dump_true = all_truths_next
            _k10 = min(10, all_logits_next.shape[-1])
            _dump_top10 = all_logits_next.topk(_k10, dim=-1).indices
        if train_labels_b:
            _train_t = torch.as_tensor(
                sorted(train_labels_b), dtype=_dump_true.dtype, device=_dump_true.device,
            )
            _dump_is_ood = ~torch.isin(_dump_true, _train_t)
        else:
            # No train-label set available (e.g. a low-cardinality legacy
            # task_b) — OOD can't be determined; treat every sample as
            # in-distribution rather than silently mis-flagging it.
            _dump_is_ood = torch.zeros_like(_dump_true, dtype=torch.bool)
        metrics_next['_dump_val_preds'] = {
            'true_region_idx': _dump_true.detach().to('cpu', torch.int32),
            'top10_pred_region_idx': _dump_top10.detach().to('cpu', torch.int32),
            'is_ood': _dump_is_ood.detach().cpu(),
        }

    return metrics_next, metrics_category, loss_combined
