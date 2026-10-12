import torch
from sklearn.metrics import classification_report

from utils.progress import zip_longest_cycle
from configs.globals import DEVICE
from training.runners.mtl_eval import eval_autocast_ctx

def validation_best_model(data_next,
                          data_category,
                          best_next,
                          best_category,
                          model):
    """Validate best models for both tasks using zip_longest_cycle (matches training coverage)."""

    all_pred_next = []
    all_truth_next = []
    all_pred_category = []
    all_truth_category = []

    # Same fp32-eval escape hatch as mtl_eval.evaluate_model (MTL_DISABLE_AMP_EVAL=1).
    _autocast_ctx = eval_autocast_ctx(DEVICE)

    with torch.no_grad():
        if best_next is best_category:
            # pipeline_audit 2026-07-01 (V10) — fast path for the standard
            # caller (mtl_cv passes the SAME joint_best_state for both slots):
            # ONE pass, both heads' argmax collected from the same forwards.
            # Byte-identical to the two-pass path: same fresh iterators over
            # shuffle=False val loaders → same batches in the same order, same
            # weights, same autocast ctx; the second pass's out_category was
            # the same forward on the same inputs. Saves one full joint val
            # pass per fold (~5 s at TX, ~1 s at AL).
            model.load_state_dict(best_next)
            model.eval()
            for batch_next, batch_category in zip_longest_cycle(data_next, data_category):
                x_next, y_next = batch_next
                if x_next.device != DEVICE:
                    x_next = x_next.to(DEVICE, non_blocking=True)
                    y_next = y_next.to(DEVICE, non_blocking=True)
                x_category, y_category = batch_category
                if x_category.device != DEVICE:
                    x_category = x_category.to(DEVICE, non_blocking=True)
                    y_category = y_category.to(DEVICE, non_blocking=True)
                with _autocast_ctx:
                    out_category, out_next = model((x_category, x_next))
                # Accumulate on-device; single bulk transfer after the loop
                all_pred_next.append(torch.argmax(out_next, dim=1))
                all_truth_next.append(y_next)
                all_pred_category.append(torch.argmax(out_category, dim=1))
                all_truth_category.append(y_category)
        else:
            model.load_state_dict(best_next)
            model.eval()
            for batch_next, batch_category in zip_longest_cycle(data_next, data_category):
                x_next, y_next = batch_next
                if x_next.device != DEVICE:
                    x_next = x_next.to(DEVICE, non_blocking=True)
                    y_next = y_next.to(DEVICE, non_blocking=True)
                x_category, _ = batch_category
                if x_category.device != DEVICE:
                    x_category = x_category.to(DEVICE, non_blocking=True)
                with _autocast_ctx:
                    out_category, out_next = model((x_category, x_next))
                pred_next_class = torch.argmax(out_next, dim=1)
                # Accumulate on-device; single bulk transfer after the loop
                all_pred_next.append(pred_next_class)
                all_truth_next.append(y_next)

            model.load_state_dict(best_category)
            model.eval()
            for batch_next, batch_category in zip_longest_cycle(data_next, data_category):
                x_next, _ = batch_next
                if x_next.device != DEVICE:
                    x_next = x_next.to(DEVICE, non_blocking=True)
                x_category, y_category = batch_category
                if x_category.device != DEVICE:
                    x_category = x_category.to(DEVICE, non_blocking=True)
                    y_category = y_category.to(DEVICE, non_blocking=True)
                with _autocast_ctx:
                    out_category, out_next = model((x_category, x_next))
                pred_category_class = torch.argmax(out_category, dim=1)
                all_pred_category.append(pred_category_class)
                all_truth_category.append(y_category)

    # Single GPU→CPU transfer for sklearn
    pred_next = torch.cat(all_pred_next).cpu()
    truth_next = torch.cat(all_truth_next).cpu()
    pred_category = torch.cat(all_pred_category).cpu()
    truth_category = torch.cat(all_truth_category).cpu()

    # Generate classification reports
    report_next = classification_report(truth_next, pred_next, output_dict=True, zero_division=0)
    report_category = classification_report(truth_category, pred_category, output_dict=True, zero_division=0)
    return report_next, report_category
