import logging
import numpy as np
import torch
from pathlib import Path
from torch import nn

logger = logging.getLogger(__name__)
from torch_geometric.data import DataLoader
from typing import Optional

from configs.globals import DEVICE
from configs.experiment import ExperimentConfig
from models.registry import create_model
from training.helpers import compute_class_weights, setup_optimizer, setup_scheduler
from training.shared_evaluate import evaluate
from training.runners.category_trainer import train
from utils.flops import calculate_model_flops
from tracking import MLHistory, FlopsMetrics, NeuralParams
from utils.mps import clear_mps_cache


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
                    'category': criterion.__class__.__name__},
                criterion_state={
                    'category': criterion.state_dict()
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
            if 'total_flops' in result:
                history.set_flops(FlopsMetrics(flops=result['total_flops'], params=result['params']['total']))
            else:
                logger.warning("FLOPs calculation failed: %s", result.get('error', 'Unknown error'))

        train(
            model,
            train_loader,
            val_loader,
            criterion,
            optimizer,
            scheduler,
            DEVICE,
            history=history.get_curr_fold(),
            num_classes=num_classes,
            epochs=config.epochs,
            max_grad_norm=config.max_grad_norm,
            timeout=config.timeout,
            target_cutoff=config.target_cutoff,
            callbacks=callbacks,
        )

        report = evaluate(model, val_loader, DEVICE, best_state=history.fold.task('category').best.best_state)

        history.fold.task('category').report = report
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
                "category_input": IoPaths.get_category(config.state, engine),
            },
        )
        manifest.write(results_path)
