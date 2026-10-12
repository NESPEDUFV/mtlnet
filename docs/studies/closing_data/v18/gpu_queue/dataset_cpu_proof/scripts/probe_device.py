"""Probe: with vs without MTL_DATASET_CPU=1, where do the fold-0 loader tensors live? (AL v18, lazy single-task path = train.py --only-fold)"""
import os
from configs.paths import EmbeddingEngine
from data.folds import FoldCreator, TaskType, _dataset_device
fr = FoldCreator(TaskType.NEXT, n_splits=5, batch_size=8192, seed=0, lazy_single_task=True).create_folds("alabama", EmbeddingEngine("check2hgi_v18"))
f0 = fr[0].next
ds_tr, ds_va = f0.train.dataloader.dataset, f0.val.dataloader.dataset
print(f"MTL_DATASET_CPU={os.environ.get('MTL_DATASET_CPU','<unset>')} _dataset_device(0)={_dataset_device(0)} "
      f"train.features.device={ds_tr.features.device} val.features.device={ds_va.features.device}")
