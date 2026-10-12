import numpy as np
from pathlib import Path
from torch.utils.data import DataLoader
from torchmetrics.functional.classification import multiclass_confusion_matrix
from typing import Optional

from configs.globals import DEVICE, CATEGORIES_MAP
from configs.experiment import ExperimentConfig
from models.registry import create_model
from training.helpers import compute_class_weights, setup_optimizer, setup_scheduler
from training.shared_evaluate import evaluate
from training.runners.next_trainer import train
from utils.flops import calculate_model_flops
from tracking import MLHistory, FlopsMetrics, NeuralParams
from tracking.fold import FoldHistory
from utils.mps import clear_mps_cache

import torch
import torch.nn as nn

def _extract_diagnostics(
        model: nn.Module,
        val_loader: DataLoader,
        device: torch.device,
        best_state: dict,
        fold_history: FoldHistory,
        num_classes: int = 7,
) -> None:
    """Extract confusion matrix and attention weights from the best model."""
    model.eval()
    model.load_state_dict(best_state)

    class_labels = list(range(num_classes))
    class_names = [CATEGORIES_MAP.get(i, f"Class-{i}") for i in class_labels]

    # Check if the model supports return_attention (not all head variants do).
    # Use try/except for robustness with torch.compile'd or wrapped models.
    import inspect
    try:
        _sig = inspect.signature(model.forward)
        supports_attention = "return_attention" in _sig.parameters
    except (ValueError, TypeError):
        supports_attention = False

    preds_list, targets_list = [], []
    attn_list = []

    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch = X_batch.to(device, non_blocking=(device.type == "cuda"))
            if supports_attention:
                logits, attn = model(X_batch, return_attention=True)
                attn_list.append(attn)
            else:
                out = model(X_batch)
                logits = out[0] if isinstance(out, tuple) else out
            preds_list.append(logits.argmax(dim=1))
            targets_list.append(y_batch)

    # Compute confusion matrix on-device, then sync everything to CPU once
    # for the downstream numpy slicing of attention weights.
    preds_t = torch.cat(preds_list)
    targets_t = torch.cat(targets_list)
    cm = multiclass_confusion_matrix(
        preds_t, targets_t.to(preds_t.device),
        num_classes=num_classes,
    ).cpu().tolist()

    all_preds = preds_t.cpu().numpy()
    all_targets = targets_t.cpu().numpy() if targets_t.device.type != 'cpu' else targets_t.numpy()

    fold_history.add_artifact('confusion_matrix', {
        'matrix': cm,
        'labels': class_names,
    })

    if attn_list:
        all_attn = torch.cat(attn_list).cpu().numpy()  # (N, seq)

        # Overall attention weights: mean/std per position
        fold_history.add_artifact('attention_weights', {
            'mean': all_attn.mean(axis=0).tolist(),
            'std': all_attn.std(axis=0).tolist(),
        })

        # Per-class attention: mean/std grouped by target class
        per_class_attn = {}
        for cls_idx, cls_name in zip(class_labels, class_names):
            mask = all_targets == cls_idx
            if mask.sum() > 0:
                cls_attn = all_attn[mask]
                per_class_attn[cls_name] = {
                    'mean': cls_attn.mean(axis=0).tolist(),
                    'std': cls_attn.std(axis=0).tolist(),
                    'count': int(mask.sum()),
                }
        fold_history.add_artifact('attention_per_class', per_class_attn)


def run_cv(
        history: MLHistory,
        folds: list[tuple[DataLoader, DataLoader]],
        config: ExperimentConfig,
        results_path: Optional[Path] = None,
        callbacks: Optional[list] = None,
):
    """Run cross-validation for the model."""
    num_classes = config.model_params.get('num_classes', 7)

    for idx, (train_loader, val_loader) in enumerate(folds):
        model = create_model(config.model_name, **config.model_params).to(DEVICE)
        if config.use_torch_compile and DEVICE.type == 'cuda':
            model = torch.compile(model)

        alpha = compute_class_weights(
            train_loader.dataset.targets, num_classes, DEVICE
        )

        # T1.4: leak-free loss calibration. When config.loss_calibration is set
        # (focal / logit-adjust / tail-loss / label-smoothing), build the
        # CalibratedLoss from TRAIN-fold targets only; otherwise keep the
        # historical class-weighted CrossEntropyLoss (the T1.1 cat ceiling).
        lc = dict(getattr(config, "loss_calibration", None) or {})
        if lc:
            from losses.calibrated import build_calibrated_loss
            criterion = build_calibrated_loss(
                num_classes, train_loader.dataset.targets,
                label_smoothing=lc.get("label_smoothing", 0.0),
                focal_gamma=lc.get("focal_gamma", 0.0),
                logit_adjust_tau=lc.get("logit_adjust_tau", 0.0),
                tail_mode=lc.get("tail_mode", None),
                cb_beta=lc.get("cb_beta", 0.999),
                ldam_max_m=lc.get("ldam_max_m", 0.5),
                ldam_scale=lc.get("ldam_scale", 30.0),
                device=DEVICE,
            )
        else:
            criterion = nn.CrossEntropyLoss(
                reduction='mean',
                weight=alpha if config.use_class_weights else None,
            )

        optimizer = setup_optimizer(model, config.learning_rate, config.weight_decay)
        scheduler = setup_scheduler(optimizer, config.max_lr, config.epochs, len(train_loader))

        history.set_model_arch(str(model))

        history.set_model_parms(
            NeuralParams(
                batch_size=config.batch_size,
                num_epochs=config.epochs,
                learning_rate=config.learning_rate,
                optimizer=optimizer.__class__.__name__,
                optimizer_state=optimizer.state_dict(),
                scheduler=scheduler.__class__.__name__,
                scheduler_state=scheduler.state_dict(),
                criterion={
                    'next': criterion.__class__.__name__},
                criterion_state={
                    'next': criterion.state_dict()
                }
            )
        )

        # Calculate FLOPs only on first fold (architecture is identical across folds)
        if idx == 0:
            sample = next(iter(train_loader))[0].to(DEVICE)
            result = calculate_model_flops(model,
                                           sample_input=sample,
                                           print_report=True,
                                           units='K'
                                           )
            if 'total_flops' in result and 'params' in result:
                history.set_flops(FlopsMetrics(flops=result['total_flops'], params=result['params']['total']))
            else:
                history.set_flops(FlopsMetrics(flops=0, params=0))

        train(
            model,
            train_loader,
            val_loader,
            criterion,
            optimizer,
            scheduler,
            history.get_curr_fold(),
            DEVICE,
            epochs=config.epochs,
            max_grad_norm=config.max_grad_norm,
            early_stopping_patience=config.early_stopping_patience,
            timeout=config.timeout,
            target_cutoff=config.target_cutoff,
            callbacks=callbacks,
        )

        report = evaluate(model, val_loader, DEVICE, best_state=history.fold.task('next').best.best_state)

        _extract_diagnostics(
            model, val_loader, DEVICE,
            best_state=history.fold.task('next').best.best_state,
            fold_history=history.fold,
            num_classes=num_classes,
        )

        history.fold.task('next').report = report
        history.step()

        # Free MPS memory between folds
        if DEVICE.type == 'mps':
            clear_mps_cache()

    # Write run manifest
    if results_path is not None:
        from configs.experiment import RunManifest
        from configs.paths import IoPaths, EmbeddingEngine
        engine = EmbeddingEngine(config.embedding_engine)
        manifest = RunManifest.from_current_env(
            config=config,
            dataset_paths={
                "next_input": IoPaths.get_next(config.state, engine),
            },
        )
        manifest.write(results_path)
