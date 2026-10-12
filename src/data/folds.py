"""
Unified Fold Creation Module for POI Classification Tasks.

Usage:
    # When using weighted CrossEntropyLoss for class imbalance (recommended)
    creator = FoldCreator(TaskType.MTL, use_weighted_sampling=False)
    folds = creator.create_folds("florida", EmbeddingEngine.DGI)

    # Save/Load
    path = creator.save(Path("./folds"))
    folds = FoldCreator.load(path)

Note:
    Choose ONE approach for class imbalance:
    - use_weighted_sampling=True  -> unweighted CrossEntropyLoss
    - use_weighted_sampling=False -> weighted CrossEntropyLoss (recommended)
    Using both causes over-correction.
"""

import gc
import json
import logging
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import DataLoader, Dataset, TensorDataset, WeightedRandomSampler

from configs.globals import CATEGORIES_MAP, DEVICE
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine, IoPaths, MTL_CHECK2HGI_ALLOWED_ENGINES

logger = logging.getLogger(__name__)


# ============================================================
# ENUMS & DATACLASSES
# ============================================================
class TaskType(Enum):
    CATEGORY = "category"
    NEXT = "next"
    MTL = "mtl"
    # Check2HGI 2-task MTL: both heads sequential, shared X rows across
    # next_category (labels from next.parquet) and next_region (labels
    # from next_region.parquet). No POI-exclusivity protocol — user-level
    # StratifiedGroupKFold only.
    MTL_CHECK2HGI = "mtl_check2hgi"


@dataclass
class FoldConfig:
    n_splits: int
    batch_size: int
    seed: int
    use_weighted_sampling: bool
    embedding_dim: int
    slide_window: int


@dataclass
class FoldIndices:
    fold_idx: int
    train_indices: np.ndarray
    val_indices: np.ndarray


@dataclass
class TaskTensors:
    task_type: TaskType
    x: torch.Tensor
    y: torch.Tensor


@dataclass
class SerializableFolds:
    task_tensors: Dict[TaskType, TaskTensors]
    fold_indices: Dict[TaskType, List[FoldIndices]]
    config: FoldConfig
    created_at: str


@dataclass
class FoldData:
    dataloader: DataLoader
    # x is the materialized feature slice. It is NOT read by the MTL training
    # path (the runner only uses ``.dataloader`` and ``.y``; verified), so the
    # check2hgi-MTL builder passes ``None`` to avoid a second full per-fold copy
    # of the [N,9,D] tensor (the host-RAM blowup on CA/TX overlap). Other paths
    # still pass the tensor.
    x: Optional[torch.Tensor]
    y: torch.Tensor


@dataclass
class TaskFoldData:
    train: FoldData
    val: FoldData


@dataclass
class FoldResult:
    next: Optional[TaskFoldData] = None
    category: Optional[TaskFoldData] = None
    # G0.1 aligned-pairing: when set, a single train loader that yields
    # ``((x_reg, y_reg), (x_cat, y_cat))`` per batch under ONE shared
    # permutation (cat-window k paired with reg-window k), and publishes the
    # reg aux side-channel. mtl_cv drives the progress bar from this single
    # loader instead of the two independent ``.next``/``.category`` train
    # loaders. None = legacy independent-shuffle path.
    joint_train_loader: Optional[object] = None


class _LazyFoldMapping:
    """Lazy, single-pass ``Mapping[int, FoldResult]`` for memory-bounded CV.

    The check2hgi-MTL CV runner consumes folds ONE AT A TIME, in order, via
    ``dataloaders.items()`` and never re-reads a prior fold (``mtl_cv.py``). The
    old eager ``Dict[int, FoldResult]`` instead materialized ALL ``n_splits``
    folds' fancy-index slices up front and held them for the whole run — at CA
    stride-1 overlap (2.9M rows × 5 folds × 2 towers) that is ~113 GB and
    OOM-kills the box.

    This wrapper builds each ``FoldResult`` ON DEMAND via ``build(i)`` and does
    not cache it, so only the fold currently being trained is resident; the prior
    fold is freed when the runner reassigns its loop variable. Behaviour is
    byte-identical (same split indices, same loaders, same seeds — only the build
    *timing* changes). Implements just the dict surface the runner + callers use:
    ``len``, ``iter``, ``keys``, ``items``, ``values``, ``[]``, ``in``.
    """

    def __init__(self, n_splits: int, build, n_regions=None):
        self._n = int(n_splits)
        self._build = build
        # Global region count (max region id + 1 over ALL rows) — equal to the per-fold
        # train∪val max across every fold, but precomputed so a caller need not iterate
        # (and transiently materialise) every fold just to size the model output dim.
        self.n_regions = n_regions

    def __len__(self):
        return self._n

    def __iter__(self):
        return iter(range(self._n))

    def __contains__(self, k):
        return isinstance(k, int) and 0 <= k < self._n

    def keys(self):
        return range(self._n)

    def __getitem__(self, i):
        if not (isinstance(i, int) and 0 <= i < self._n):
            raise KeyError(i)
        return self._build(i)

    def items(self):
        for i in range(self._n):
            yield i, self._build(i)

    def values(self):
        for i in range(self._n):
            yield self._build(i)


class _RestrictedFoldMapping:
    """Lazy, id-preserving subset view over a fold mapping (same dict surface
    as ``_LazyFoldMapping``).

    pipeline_audit 2026-07-01 (V5): ``--only-folds a,b`` / ``--folds N`` used
    plain dict subsetting (``dict(list(items())[:N])`` / a dict comprehension),
    which EAGERLY materialized every selected fold's loaders + slices at once —
    exactly the all-folds-resident pattern ``_LazyFoldMapping`` was built to
    remove (at TX overlap ≥3 selected folds OOM-kills the host past the
    single-fold-peak RAM-guard model). This view keeps the REAL fold ids (the
    per-fold log_T naming + fan-out artifact naming depend on them) and defers
    each build to first access, one fold resident at a time.
    """

    def __init__(self, base, keys):
        self._base = base
        self._keys = [int(k) for k in keys]
        self.n_regions = getattr(base, "n_regions", None)

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(self._keys)

    def __contains__(self, k):
        return k in self._keys

    def keys(self):
        return list(self._keys)

    def __getitem__(self, k):
        if k not in self._keys:
            raise KeyError(k)
        return self._base[k]

    def items(self):
        for k in self._keys:
            yield k, self._base[k]

    def values(self):
        for k in self._keys:
            yield self._base[k]


# ============================================================
# DATASET
# ============================================================
class POIDataset(Dataset):
    def __init__(
            self,
            features: torch.Tensor,
            targets: torch.Tensor,
            device: Optional[torch.device] = None,
    ):
        # When `device` is provided, pre-move the underlying tensors so that
        # __getitem__ returns slices that already live on the target device.
        # This eliminates the per-batch host->device copy in the training loop
        # — safe on MPS because the datasets fit comfortably in unified memory.
        # When `device` is None, tensors are kept on CPU so they can be shared
        # safely with forked DataLoader workers.
        if device is not None:
            self.features = features.to(device) if features.device != device else features
            self.targets = targets.to(device) if targets.device != device else targets
        else:
            self.features = features if features.device.type == 'cpu' else features.cpu()
            self.targets = targets if targets.device.type == 'cpu' else targets.cpu()

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.targets[idx]

    def __getitems__(self, indices):
        # Batched fetch: one `index_select` per tensor instead of len(batch)
        # per-sample __getitem__ slices + a default_collate stack. With a
        # GPU-resident dataset + workers=0 that collapses ~2048 tiny CUDA index
        # kernels/batch into one. Rows/order come from the sampler →
        # byte-identical batches. Pair with ``_batched_collate``.
        idx = torch.as_tensor(indices, dtype=torch.long, device=self.features.device)
        return self.features.index_select(0, idx), self.targets.index_select(0, idx)


class POIDatasetWithAux(Dataset):
    """POIDataset variant that yields 3-tuples ``(features, labels, aux)``.

    Used by the B5 faithful-GETNext path (``next_getnext_hard``). The aux
    tensor is an ``int64`` per-sample ``last_region_idx``. Wrapped by
    ``AuxPublishingLoader`` so the training loop sees 2-tuples — see
    ``src/data/aux_side_channel.py``.
    """

    def __init__(
        self,
        features: torch.Tensor,
        targets: torch.Tensor,
        aux: torch.Tensor,
        device: Optional[torch.device] = None,
    ):
        if device is not None:
            self.features = features.to(device) if features.device != device else features
            self.targets = targets.to(device) if targets.device != device else targets
            self.aux = aux.to(device) if aux.device != device else aux
        else:
            self.features = features if features.device.type == 'cpu' else features.cpu()
            self.targets = targets if targets.device.type == 'cpu' else targets.cpu()
            self.aux = aux if aux.device.type == 'cpu' else aux.cpu()
        if not (len(self.features) == len(self.targets) == len(self.aux)):
            raise ValueError(
                f"length mismatch: features={len(self.features)} "
                f"targets={len(self.targets)} aux={len(self.aux)}"
            )

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.features[idx], self.targets[idx], self.aux[idx]

    def __getitems__(self, indices):
        # Batched fetch — see POIDataset.__getitems__.
        idx = torch.as_tensor(indices, dtype=torch.long, device=self.features.device)
        return (self.features.index_select(0, idx),
                self.targets.index_select(0, idx),
                self.aux.index_select(0, idx))


def _batched_collate(batch):
    """Passthrough collate for the ``__getitems__`` batched-fetch path: the
    dataset already returns the stacked batch tensors via ``index_select``, so
    the DataLoader must NOT re-collate them. Byte-identical to default_collate of
    per-sample ``__getitem__`` outputs (same rows, same order from the sampler)."""
    return batch


# ============================================================
# UTILITIES
# ============================================================
def _get_num_workers() -> int:
    # num_workers=0 everywhere. Each worker forks + pickles the tensor over IPC
    # per epoch — pure overhead when the dataset is a torch tensor on-device (and
    # on CUDA, forking the GPU-pre-moved tensor OOM'd the cgroup).
    #
    # ⚠ num_workers>0 is NOT quality-neutral: the per-task train loaders
    # (_create_dataloader / _create_aux_dataloader) shuffle with NO explicit
    # `generator=` → they consume the GLOBAL torch RNG, and worker plumbing
    # perturbs the consumption order (measured shift vs the byte-identical
    # workers=0 baseline). Adding a seeded generator would itself change the
    # frozen baseline numbers, so we keep workers=0. The VRAM win for large states
    # comes from CPU-residency alone (MTL_DATASET_CPU; byte-identical on CUDA, and on MPS
    # only for the single-task path with the blocking copy of D2b, MTL path not covered —
    # see ``_dataset_device``), NOT from workers — so there's no quality-neutral reason to
    # enable them.
    return 0


def _dataset_device(num_workers: int, tensor_nbytes: int | None = None):
    """Device the dataset tensors are pre-moved to.

    Pre-moving the whole dataset to ``DEVICE`` (so __getitem__ returns device slices)
    is fastest — zero per-batch host→device copy — and is the right choice whenever
    the dataset fits on the GPU alongside the model+activations. ``None`` keeps tensors
    on CPU (the training loop transfers each batch via ``.to(DEVICE)``), trading speed
    for GPU memory — needed only when the dataset would not fit.

    AUTO-FIT (default on CUDA): when ``tensor_nbytes`` is known, pre-move to GPU only if
    it fits in (free VRAM − headroom); else keep it CPU-resident. Decisions are made
    per-loader as loaders are built, so ``cuda.mem_get_info()`` already reflects tensors
    pre-moved by earlier loaders (cumulative-aware). This removes the manual guessing
    that caused the FL-overlap OOM and is robust across machines. **Byte-identical on
    CUDA**: there the dataset's device never changes the computation (verified on CUDA:
    CPU-resident vs GPU-pre-move produce identical metrics) — only throughput/VRAM. The
    CHOICE may vary with GPU occupancy (non-deterministic), but the trained model + scored
    numbers do not. **On MPS a CPU-resident dataset is byte-identical only through the
    blocking single-task batch copy** (``non_blocking`` only on CUDA in
    ``_single_task_train`` / ``shared_evaluate`` / ``next_cv``, D2b, 2026-10-04): a
    non-blocking CPU→MPS copy from the pageable ``index_select`` temporary corrupted the
    labels (AL proof, ``docs/studies/closing_data/v18/gpu_queue/dataset_cpu_proof/``). The
    MTL loops (``mtl_cv`` / ``mtl_eval`` / ``mtl_validation``) still copy with
    ``non_blocking=True`` and are NOT covered: do not use MTL_DATASET_CPU=1 for MTL on MPS.

    Overrides: ``MTL_DATASET_CPU=1`` forces CPU-resident; ``MTL_DATASET_GPU=1`` forces
    pre-move; ``MTL_GPU_HEADROOM_GB`` (default 16) reserves VRAM for model+activations.
    MPS/CPU always pre-move (unified / host memory). ``num_workers>0`` ⇒ CPU (workers
    can't share a pre-moved GPU tensor).
    """
    import os as _os
    if _os.environ.get("MTL_DATASET_CPU", "").strip() in ("1", "true", "True"):
        return None
    if _os.environ.get("MTL_DATASET_GPU", "").strip() in ("1", "true", "True"):
        return DEVICE if num_workers == 0 else None
    if num_workers != 0:
        return None
    if DEVICE.type != "cuda":
        return DEVICE  # MPS unified memory / CPU: pre-move as before
    if tensor_nbytes is None:
        return DEVICE  # unknown size → legacy pre-move (callers that don't pass a size)
    try:
        free, _total = torch.cuda.mem_get_info()
    except Exception:
        return DEVICE
    headroom = int(_os.environ.get("MTL_GPU_HEADROOM_GB", "16")) * (1024 ** 3)
    return DEVICE if (int(tensor_nbytes) + headroom) < free else None


def _nbytes(*tensors) -> int:
    """Total bytes of the given tensors (for the dataset auto-fit decision)."""
    return sum(int(t.numel()) * int(t.element_size()) for t in tensors if hasattr(t, "numel"))


def _worker_init_fn(worker_id: int) -> None:
    worker_seed = torch.initial_seed() % 2 ** 32 + worker_id
    np.random.seed(worker_seed)


def _map_categories(y: pd.Series) -> pd.Series:
    inv_categories = {v: k for k, v in CATEGORIES_MAP.items()}
    return y.map(inv_categories)


def _get_class_distribution(y: np.ndarray) -> Dict[int, int]:
    unique, counts = np.unique(y, return_counts=True)
    return dict(zip(unique.astype(int), counts.astype(int)))


def _convert_to_tensors(
        X: np.ndarray,
        y: np.ndarray,
        task_type: TaskType,
        embedding_dim: int,
        slide_window: int = InputsConfig.SLIDE_WINDOW,
) -> Tuple[torch.Tensor, torch.Tensor]:
    x_values = np.ascontiguousarray(X, dtype=np.float32)
    y_values = np.ascontiguousarray(y, dtype=np.int64)

    # from_numpy shares memory (zero-copy) since arrays are already contiguous
    x_tensor = torch.from_numpy(x_values)
    y_tensor = torch.from_numpy(y_values)

    if task_type == TaskType.NEXT:
        # Reshape to (num_samples, slide_window, embedding_dim) for sequence models
        x_tensor = x_tensor.view(-1, slide_window, embedding_dim)
    # CATEGORY: keep as (num_samples, embedding_dim) - no reshape needed

    return x_tensor, y_tensor


def _json_default(obj):
    """JSON serializer for numpy types."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _compute_overlap_seq_fraction(
    ambiguous_pois: List[int],
    val_next_idx: np.ndarray,
    seq_poi_mapping: Dict[int, set],
) -> float:
    """Compute fraction of val next-task sequences that touch ambiguous POIs.

    Uses the materialized sequence→POI mapping artifact to determine which
    val sequences contain ambiguous POIs (i.e., POIs that are in category
    training but appear in next-task validation through val-user sequences).
    """
    if not ambiguous_pois:
        return 0.0

    ambiguous_set = set(ambiguous_pois)
    affected = 0
    total_val = len(val_next_idx)

    for idx in val_next_idx:
        seq_pois = seq_poi_mapping.get(int(idx), set())
        if seq_pois & ambiguous_set:
            affected += 1

    return affected / max(total_val, 1)


def _create_weighted_sampler(y: np.ndarray, seed: int) -> WeightedRandomSampler:
    classes = np.unique(y)
    class_weights = compute_class_weight('balanced', classes=classes, y=y)
    weight_per_class = dict(zip(classes, class_weights))
    sample_weights = torch.tensor(
        [weight_per_class[label] for label in y],
        dtype=torch.float32
    )
    generator = torch.Generator()
    generator.manual_seed(seed)
    return WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True,
        generator=generator
    )


def _create_dataloader(
        x: torch.Tensor,
        y: torch.Tensor,
        batch_size: int,
        shuffle: bool,
        use_weighted_sampling: bool,
        seed: int,
) -> DataLoader:
    num_workers = _get_num_workers()

    # Pre-move tensors to DEVICE only when not using DataLoader workers.
    # Forked workers cannot share GPU/MPS memory with the parent process —
    # but with num_workers=0 (the MPS path), we can keep the dataset entirely
    # on-device and skip the per-batch host->device copy.
    dataset_device = _dataset_device(num_workers, _nbytes(x, y))

    sampler = None
    if use_weighted_sampling:
        y_np = y.numpy() if isinstance(y, torch.Tensor) else y
        sampler = _create_weighted_sampler(y_np, seed)
        shuffle = False

    return DataLoader(
        POIDataset(x, y, device=dataset_device),
        batch_size=batch_size,
        shuffle=shuffle if sampler is None else False,
        sampler=sampler,
        num_workers=num_workers,
        collate_fn=_batched_collate,
        pin_memory=torch.cuda.is_available() and dataset_device is None,
        persistent_workers=num_workers > 0,
        prefetch_factor=2 if num_workers > 0 else None,
        worker_init_fn=_worker_init_fn if num_workers > 0 else None,
    )


def _create_aux_dataloader(
        x: torch.Tensor,
        y: torch.Tensor,
        aux: torch.Tensor,
        batch_size: int,
        shuffle: bool,
        use_weighted_sampling: bool,
        seed: int,
):
    """Build a DataLoader over ``POIDatasetWithAux``, wrapped in
    ``AuxPublishingLoader`` so the aux tensor is published to a
    thread-local (read by the ``next_getnext_hard`` head) and the training
    loop sees normal ``(x, y)`` 2-tuples.

    Gated behind the ``next_getnext_hard`` head factory in
    ``_create_check2hgi_mtl_folds``; other code paths continue to use
    ``_create_dataloader``.
    """
    # Lazy import to avoid a circular import at module load time.
    from data.aux_side_channel import AuxPublishingLoader

    num_workers = _get_num_workers()
    dataset_device = _dataset_device(num_workers, _nbytes(x, y, aux))

    sampler = None
    if use_weighted_sampling:
        y_np = y.numpy() if isinstance(y, torch.Tensor) else y
        sampler = _create_weighted_sampler(y_np, seed)
        shuffle = False

    base = DataLoader(
        POIDatasetWithAux(x, y, aux, device=dataset_device),
        batch_size=batch_size,
        shuffle=shuffle if sampler is None else False,
        sampler=sampler,
        num_workers=num_workers,
        collate_fn=_batched_collate,
        pin_memory=torch.cuda.is_available() and dataset_device is None,
        persistent_workers=num_workers > 0,
        prefetch_factor=2 if num_workers > 0 else None,
        worker_init_fn=_worker_init_fn if num_workers > 0 else None,
    )
    return AuxPublishingLoader(base)


class AlignedJointLoader:
    """G0.1 aligned-pairing: a SINGLE train loader over a joint dataset so the
    cat and reg streams share ONE per-epoch permutation (cat-window k trains
    paired with reg-window k — the same window — instead of the two loaders'
    independent shuffles). Yields ``((x_reg, y_reg), (x_cat, y_cat))`` so the
    MTL training loop's ``(data_task_b, data_task_a)`` unpacking is unchanged,
    and publishes the reg aux (``last_region_idx``) to the side-channel each
    batch (kept aligned; inert under champion G where KD is off + alpha frozen,
    but correct should a log_T-aware head read it).
    """

    def __init__(self, dataloader: DataLoader, has_aux: bool):
        self._loader = dataloader
        self._has_aux = has_aux
        self.batch_size = getattr(dataloader, "batch_size", None)
        self.dataset = getattr(dataloader, "dataset", None)
        # pipeline_audit pairing decomposition (2026-07-01) — DERANGED control:
        # keep the joint-loader machinery + shared permutation IDENTICAL to the
        # aligned arm, but roll the task-b (reg) triple by 1 within each batch
        # so row i pairs with row i-1 (a different window of the same batch).
        # Separates the two confounded axes of the aligned-vs-default A/B:
        #   aligned vs deranged  → pure per-sample pairing SEMANTICS
        #   deranged vs default  → loader structure / per-step sample diversity
        #     (a joint batch feeds bs distinct windows to BOTH losses; the
        #     default independent loaders feed 2×bs distinct windows per step).
        # The rolled (x_b, y_b, aux) stays a valid reg sample set — only the
        # cross-task pairing changes. Opt-in via MTL_ALIGNED_DERANGE=1.
        import os as _os_d
        self._derange = _os_d.environ.get("MTL_ALIGNED_DERANGE", "0") == "1"

    def __iter__(self):
        from data.aux_side_channel import _publish_aux, _clear_aux
        for batch in self._loader:
            if self._has_aux:
                x_b, y_b, x_a, y_a, aux = batch
            else:
                x_b, y_b, x_a, y_a = batch
                aux = None
            if self._derange and x_b.shape[0] > 1:
                x_b = torch.roll(x_b, 1, 0)
                y_b = torch.roll(y_b, 1, 0)
                if aux is not None:
                    aux = torch.roll(aux, 1, 0)
            _publish_aux(aux if self._has_aux else None)
            yield (x_b, y_b), (x_a, y_a)
        _clear_aux()

    def __len__(self) -> int:
        return len(self._loader)


def _create_aligned_joint_loader(x_b, y_b, x_a, y_a, aux, batch_size: int, seed: int):
    """Build the single shared-permutation train loader for G0.1 aligned-pairing.

    ``x_b/y_b`` (reg) and ``x_a/y_a`` (cat) are row-aligned (both indexed by the
    same ``train_idx`` off the same ``next.parquet`` rows), so one shuffle over a
    joint ``TensorDataset`` pairs window k with window k across tasks. ``aux`` is
    the per-sample reg ``last_region_idx`` (or None when the reg head needs none).
    """
    num_workers = _get_num_workers()
    dataset_device = _dataset_device(num_workers, _nbytes(x_b, y_b, x_a, y_a, aux))

    def _mv(t):
        if dataset_device is not None and isinstance(t, torch.Tensor) and t.device != dataset_device:
            return t.to(dataset_device)
        return t

    tensors = [_mv(x_b), _mv(y_b), _mv(x_a), _mv(y_a)]
    has_aux = aux is not None
    if has_aux:
        tensors.append(_mv(aux))

    g = torch.Generator()
    g.manual_seed(seed)
    base = DataLoader(
        TensorDataset(*tensors),
        batch_size=batch_size,
        shuffle=True,
        generator=g,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available() and dataset_device is None,
        persistent_workers=num_workers > 0,
        prefetch_factor=2 if num_workers > 0 else None,
        worker_init_fn=_worker_init_fn if num_workers > 0 else None,
    )
    return AlignedJointLoader(base, has_aux)


# ============================================================
# DATA LOADING
# ============================================================
def load_category_data(state: str, embedding_engine: EmbeddingEngine) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], int]:
    """Load category data. Returns (X, y, placeids, embedding_dim).

    placeids is None when the parquet predates Phase 2 (no 'placeid' column).
    Callers that require placeids (MTL user-level splits) must handle None by
    falling back to independent StratifiedKFold splits.
    """
    logger.info(f"Loading category data: {state}/{embedding_engine.value}")
    df = IoPaths.load_category(state, embedding_engine)

    df['label'] = _map_categories(df['category'])
    if 'placeid' in df.columns:
        placeids = df['placeid'].values.copy()
    else:
        logger.warning(
            "Category parquet for %s/%s has no 'placeid' column (pre-Phase-2 data). "
            "MTL user-level splits require regenerating input with the Phase 2 pipeline. "
            "Falling back to independent StratifiedKFold splits.",
            state, embedding_engine.value,
        )
        placeids = None
    df = df.drop(columns=['category'])

    # Infer embedding_dim from numeric columns in the artifact
    feature_cols = sorted([c for c in df.columns if c.isdigit()], key=int)
    embedding_dim = len(feature_cols)
    X = df[feature_cols].values.astype(np.float32)
    y = df['label'].values.astype(np.int64)

    logger.info(f"Category data: {X.shape} (dim={embedding_dim}), distribution: {_get_class_distribution(y)}")
    return X, y, placeids, embedding_dim


def _guard_cpu_resident_ram(n_rows: int, num_features: int, *, where: str) -> None:
    """Fail-loud CPU-RAM guard for loading a CPU-resident next/MTL dataset.

    Estimates ~2x the [N, num_features] float32 matrix (the ``.values`` copy plus
    the parquet-backed DataFrame / downstream tensors) and raises a clear error if
    it would exceed available RAM minus head-room, rather than OOM-killing the box.
    No-op when psutil is unavailable or the estimate fits. Head-room is the env
    ``MTL_RAM_HEADROOM_GB`` (default 16 GB) — the SAME knob the build guard uses.
    """
    try:
        import psutil
    except Exception:
        return
    headroom_gb = float(os.environ.get("MTL_RAM_HEADROOM_GB", "16"))
    est_gb = 2 * n_rows * num_features * 4 / (1024 ** 3)
    avail_gb = psutil.virtual_memory().available / (1024 ** 3)
    if est_gb > (avail_gb - headroom_gb):
        raise MemoryError(
            f"{where}: CPU-resident next dataset needs ~{est_gb:.1f} GB "
            f"(n_rows={n_rows}, num_features={num_features}) but only "
            f"{avail_gb:.1f} GB is available (head-room {headroom_gb:.1f} GB). "
            f"This usually means an oversized (e.g. stride-1 large-state) build. "
            f"Use a smaller config or rebuild at the default stride. Override "
            f"head-room via MTL_RAM_HEADROOM_GB."
        )


def _guard_mtl_check2hgi_ram(
    n_rows: int, num_features: int, n_region_towers: int, *, where: str
) -> None:
    """Fail-loud CPU-RAM guard for the check2hgi-MTL dataset construction.

    Unlike ``_guard_cpu_resident_ram`` (which models only the single ``load_next_data``
    matrix), this path holds, SIMULTANEOUSLY and with no ``del`` between them: the ``X``
    matrix, the ``x_checkin`` tensor, one ``[N, 9, D]`` region tensor per region tower
    (``task_a``/``task_b`` set to "region"/"concat"), AND a per-fold train+val slice of
    each. We model the peak as ``matrix × (1 + 2.5·(1 + n_region_towers))`` float32
    copies (X + checkin + region towers + ~1.5× per-fold slices) and raise BEFORE the
    big tensors are built if it would exceed available RAM minus head-room — so an
    oversized (e.g. stride-1 large-state, 2.9M-row CA) overlap load FAILS LOUD with a
    clear message instead of OOM-killing the box. Head-room via ``MTL_RAM_HEADROOM_GB``.
    """
    try:
        import psutil
    except Exception:
        return
    headroom_gb = float(os.environ.get("MTL_RAM_HEADROOM_GB", "16"))
    matrix_gb = n_rows * num_features * 4 / (1024 ** 3)
    # Post-fix model (lazy per-fold construction + FoldData.x dropped). The
    # resident set is now: the base master tensors (X + one region tower per
    # "region"/"concat" slot ⇒ matrix × (1+towers)) PLUS exactly ONE fold's
    # train+val slices live at a time (≈ matrix × (1+towers), since train+val
    # together ≈ full N once). With a temporaries margin: matrix × (1+towers) × 2.5.
    # Calibrated to the MEASURED post-fix peak: CA overlap (matrix 6.3 GB, towers=1,
    # auto dataset-device) peaked at 49 GB host RSS while training fold-1 → coefficient
    # ≈ 49/(6.3·2) ≈ 3.9; use 4.0. ⇒ CA ≈ 50 GB, TX ≈ 66 GB, FL ≈ 22 GB, non-overlap
    # ≈ 5-6 GB. (Pre-fix this path held ALL n_splits folds at once → ~126 GB at CA →
    # OOM-killed the box; the lazy build + dropped FoldData.x removed that.)
    # Err toward over-estimating: a false raise never kills the box, a false PASS can.
    est_gb = matrix_gb * (1 + max(0, n_region_towers)) * 4.0
    avail_gb = psutil.virtual_memory().available / (1024 ** 3)
    logger.info(
        "check2hgi-MTL host-RAM estimate: ~%.1f GB (n_rows=%d, feat=%d, "
        "region_towers=%d), avail=%.1f GB, head-room=%.1f GB",
        est_gb, n_rows, num_features, n_region_towers, avail_gb, headroom_gb,
    )
    if est_gb > (avail_gb - headroom_gb):
        raise MemoryError(
            f"{where}: check2hgi-MTL dataset construction would need ~{est_gb:.1f} GB "
            f"peak host RAM (n_rows={n_rows}, feat={num_features}, "
            f"region_towers={n_region_towers}) but only {avail_gb:.1f} GB is available "
            f"(head-room {headroom_gb:.1f} GB). This is the stride-1 large-state overlap "
            f"load (CA/TX ~3M rows). Run with MTL_DATASET_CPU=1 on a host with more RAM, "
            f"subsample the engine, or use the non-overlap build. The GPU is NOT the "
            f"limit here (per-batch footprint is N-independent) — this is host memory. "
            f"Override head-room via MTL_RAM_HEADROOM_GB."
        )


def _warn_if_ungated_overlap(state, embedding_engine) -> None:
    """Train-time guard: the overlap windowing (stride==1) is GATED by default
    (``emit_tail=False``). A *manual* ungated rebuild (``emit_tail=True``) can be
    left stale on disk and silently train on the wrong windowing. Read the
    build-provenance sidecar and WARN loudly if an overlap engine is ungated;
    ``MTL_STRICT=1`` hard-fails. No-op for non-overlap / missing sidecar.
    """
    try:
        sidecar = IoPaths.get_next(state, embedding_engine).parent / "next_build_provenance.json"
        if not sidecar.exists():
            return
        prov = json.loads(sidecar.read_text())
        if prov.get("stride") == 1:
            problems = []
            if prov.get("emit_tail") is True:
                problems.append("emit_tail=True (ungated — board windowing is GATED)")
            if prov.get("min_sequence_length") not in (None, 10):
                problems.append(
                    f"min_sequence_length={prov.get('min_sequence_length')} "
                    f"(board overlap windowing is min_seq=10)"
                )
            if problems:
                msg = (
                    f"non-board overlap engine {embedding_engine.value}/{state}: "
                    + "; ".join(problems)
                    + f". Rebuild board-correct with "
                    f"`python scripts/mtl_improvement/build_overlap_probe_engine.py {state} 1` "
                    f"(stride=1, gated, min_seq=10) unless intentionally testing a variant."
                )
                if os.environ.get("MTL_STRICT") == "1":
                    raise ValueError(msg)
                logger.warning("[board-overlap guard] %s", msg)
    except ValueError:
        raise
    except Exception:
        pass  # provenance check is best-effort; never break a load


def load_next_data(
    state: str, embedding_engine: EmbeddingEngine
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Load next-POI data. Returns (X, y, userids, embedding_dim)."""
    logger.info(f"Loading next-POI data: {state}/{embedding_engine.value}")
    _warn_if_ungated_overlap(state, embedding_engine)
    df = IoPaths.load_next(state, embedding_engine)

    df['label'] = _map_categories(df['next_category'])
    # Ensure userid is int (may be stored as string in parquet)
    userids = df['userid'].astype(int).values.copy()
    df = df.drop(columns=['userid', 'next_category'])

    nan_count = df['label'].isna().sum()
    if nan_count > 0:
        logger.warning(f"Dropping {nan_count} rows with NaN labels")
        valid_mask = ~df['label'].isna()
        df = df[valid_mask]
        userids = userids[valid_mask.values]

    # Infer dimensions from numeric columns in the artifact
    feature_cols = sorted([c for c in df.columns if c.isdigit()], key=int)
    num_features = len(feature_cols)
    slide_window = InputsConfig.SLIDE_WINDOW
    embedding_dim = num_features // slide_window

    # CPU-RAM guard (fail-loud): the .values.astype(float32) below materialises a
    # second full [N, num_features] float32 matrix alongside the parquet-backed
    # DataFrame; downstream fold tensors hold another copy. A too-big CPU-resident
    # next dataset (e.g. an accidental stride-1 large-state build) would OOM the
    # box silently. Estimate ~2x the float32 matrix and raise a clear error rather
    # than letting the host run out of RAM. Headroom via MTL_RAM_HEADROOM_GB.
    _guard_cpu_resident_ram(len(df), num_features, where="load_next_data")

    X = df[feature_cols].values.astype(np.float32)
    y = df['label'].values.astype(np.int64)

    logger.info(f"Next-POI data: {X.shape} (dim={embedding_dim}, window={slide_window}), distribution: {_get_class_distribution(y)}")
    return X, y, userids, embedding_dim


# ============================================================
# SERIALIZATION
# ============================================================
def save_folds(serializable: SerializableFolds, save_dir: Path) -> Path:
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    filename = f"folds_{time.strftime('%Y%m%d_%H%M%S')}.pt"
    save_path = save_dir / filename

    save_dict = {
        'created_at': serializable.created_at,
        'config': serializable.config.__dict__,
        'task_tensors': {
            task.value: {'x': t.x, 'y': t.y}
            for task, t in serializable.task_tensors.items()
        },
        'fold_indices': {
            task.value: [
                {'fold_idx': idx.fold_idx, 'train': idx.train_indices, 'val': idx.val_indices}
                for idx in indices
            ]
            for task, indices in serializable.fold_indices.items()
        },
    }

    torch.save(save_dict, save_path)
    logger.info(f"Folds saved to {save_path}")
    return save_path


def load_folds(path: Path) -> SerializableFolds:
    save_dict = torch.load(path, weights_only=False)
    config = FoldConfig(**save_dict['config'])

    task_tensors = {
        TaskType(task): TaskTensors(TaskType(task), t['x'], t['y'])
        for task, t in save_dict['task_tensors'].items()
    }

    fold_indices = {
        TaskType(task): [
            FoldIndices(idx['fold_idx'], idx['train'], idx['val'])
            for idx in indices
        ]
        for task, indices in save_dict['fold_indices'].items()
    }

    logger.info(f"Folds loaded from {path}")
    return SerializableFolds(task_tensors, fold_indices, config, save_dict['created_at'])


def rebuild_dataloaders(
        serialized: SerializableFolds,
        batch_size: Optional[int] = None,
        use_weighted_sampling: Optional[bool] = None,
) -> Dict[int, FoldResult]:
    config = serialized.config
    batch_size = batch_size or config.batch_size
    use_weighted = use_weighted_sampling if use_weighted_sampling is not None else config.use_weighted_sampling

    fold_results: Dict[int, FoldResult] = {}
    tasks = list(serialized.task_tensors.keys())
    n_folds = len(serialized.fold_indices[tasks[0]])

    for fold_idx in range(n_folds):
        fold_result = FoldResult()

        for task in tasks:
            tensors = serialized.task_tensors[task]
            indices = serialized.fold_indices[task][fold_idx]

            train_x, train_y = tensors.x[indices.train_indices], tensors.y[indices.train_indices]
            val_x, val_y = tensors.x[indices.val_indices], tensors.y[indices.val_indices]

            task_data = TaskFoldData(
                train=FoldData(
                    _create_dataloader(train_x, train_y, batch_size, True, use_weighted, config.seed),
                    train_x, train_y
                ),
                val=FoldData(
                    _create_dataloader(val_x, val_y, batch_size, False, False, config.seed),
                    val_x, val_y
                ),
            )

            if task == TaskType.NEXT:
                fold_result.next = task_data
            else:
                fold_result.category = task_data

        fold_results[fold_idx] = fold_result
        gc.collect()

    return fold_results


def _classify_pois(poi_users, train_users, val_users):
    """Partition POIs by which user-set(s) visited them (legacy-MTL category split).

    A POI seen by both a train user and a val user is ``ambiguous``; otherwise it is
    ``train_exclusive`` / ``val_exclusive``. This is the user-isolation leak guard:
    category-val POIs are val-exclusive only, so a val POI never leaks into train.
    Returns ``(train_exclusive, val_exclusive, ambiguous)`` lists in ``poi_users``
    iteration order.
    """
    train_exclusive, val_exclusive, ambiguous = [], [], []
    for poi, visitors in poi_users.items():
        in_train = bool(visitors & train_users)
        in_val = bool(visitors & val_users)
        if in_train and in_val:
            ambiguous.append(poi)
        elif in_train:
            train_exclusive.append(poi)
        elif in_val:
            val_exclusive.append(poi)
    return train_exclusive, val_exclusive, ambiguous


def _resolve_task_input(input_type, state, embedding_engine, x_checkin,
                        expect_userids=None):
    """Pick a task slot's input tensor for the check2hgi-MTL fold creator.

    ``checkin`` → the shared ``x_checkin`` (no region-sequence build → bit-equivalent to the
    legacy checkin-only path when both slots are checkin); ``region`` → the region-embedding
    sequence (``REGION_EMB_ENGINE`` env overrides the region engine while ``embedding_engine``
    drives the windowing); ``concat`` → checkin ⊕ region. Lazy region-sequence import so
    non-region engines don't pay the cost. ``expect_userids`` (pipeline_audit
    2026-07-01, V2) threads next.parquet's userids into the region-sequence
    builder for a per-row alignment guard against a stale sequences_next.parquet.
    """
    if input_type == "checkin":
        return x_checkin
    from data.inputs.region_sequence import (
        build_region_sequence_tensor,
        build_concat_sequence_tensor,
    )
    if input_type == "region":
        import os as _os
        _re = _os.environ.get("REGION_EMB_ENGINE")
        _reg_eng = EmbeddingEngine(_re) if _re else embedding_engine
        return build_region_sequence_tensor(state, region_engine=_reg_eng,
                                            seq_engine=embedding_engine,
                                            expect_userids=expect_userids)
    if input_type == "concat":
        return build_concat_sequence_tensor(state, x_checkin,
                                            seq_engine=embedding_engine,
                                            expect_userids=expect_userids)
    raise ValueError(f"Unknown input_type: {input_type}")


def _load_and_validate_check2hgi_data(state, embedding_engine, task_set):
    """Load + validate the check2hgi-MTL inputs (next.parquet + next_region.parquet).

    Returns ``(X, y_cat, userids, next_dim, y_region, y_last_region|None, use_aux)``.
    The userid CONTENT-equality guard is load-bearing: row-count parity is necessary but
    NOT sufficient — a stale next_region.parquet from a different windowing can have the
    same row count yet a different per-row user/order, silently mis-pairing every (X,region)
    row. ``use_aux`` fires for the ``next_getnext_hard*`` / ``next_stan_flow*`` heads (which
    read ``last_region_idx`` via aux_side_channel); the champion-G ``next_stan_flow_dualtower``
    MUST be listed or use_aux=False → the α·log_T prior + log_T-KD branch silently no-op.
    """
    X, y_cat, userids, next_dim = load_next_data(state, embedding_engine)

    region_df = IoPaths.load_next_region(state, embedding_engine)
    if len(region_df) != len(X):
        raise ValueError(
            f"next_region.parquet rows ({len(region_df)}) disagree with "
            f"next.parquet rows ({len(X)}) for {state}. Regenerate both."
        )
    if "userid" not in region_df.columns:
        # pipeline_audit 2026-07-01 (V7) — hard-fail instead of silently
        # degrading to row-count-only parity: a stale next_region.parquet
        # lacking userid but matching the row count would mis-pair every
        # (X, region-label) row — the exact failure this guard exists for.
        # Every current on-disk artifact carries userid (verified 18/18).
        raise ValueError(
            f"next_region.parquet for {state} has no 'userid' column — cannot "
            f"verify row alignment with next.parquet (row-count parity alone "
            f"is NOT sufficient). Regenerate via "
            f"`python scripts/regenerate_next_region.py --state {state}`."
        )
    region_uids = region_df["userid"].astype(int).to_numpy()
    if not np.array_equal(region_uids, userids):
        raise ValueError(
            f"next_region.parquet userid column is not row-aligned with "
            f"next.parquet for {state} (same row count but different "
            f"per-row userids — a stale/cross-windowing region file). "
            f"Regenerate both from the SAME sequences via "
            f"`python scripts/regenerate_next_region.py --state {state}`."
        )
    y_region = region_df["region_idx"].to_numpy(dtype=np.int64)

    task_b_head = (
        getattr(getattr(task_set, "task_b", None), "head_factory", None)
        if task_set is not None else None
    )
    # Keep in sync with _HEADS_REQUIRING_AUX in scripts/p1_region_head_ablation.py.
    _HEADS_REQUIRING_AUX_MTL = {
        "next_getnext_hard", "next_getnext_hard_hsm",       # legacy aliases
        "next_stan_flow", "next_stan_flow_hsm",             # paper-facing names
        "next_stan_flow_dualtower",                         # champion-G dual-tower
    }
    use_aux = task_b_head in _HEADS_REQUIRING_AUX_MTL
    y_last_region = None
    if use_aux:
        if "last_region_idx" not in region_df.columns:
            raise ValueError(
                f"next_region.parquet for {state} is missing the "
                f"'last_region_idx' column required by head "
                f"{task_b_head!r}. Regenerate via "
                f"`python scripts/regenerate_next_region.py --state {state}`."
            )
        y_last_region = region_df["last_region_idx"].to_numpy(dtype=np.int64)

    # Free the (large) region DataFrame before the [N,9,D] tensors (CA overlap ~7.6 GB).
    del region_df
    return X, y_cat, userids, next_dim, y_region, y_last_region, use_aux


# ============================================================
# FOLD CREATOR
# ============================================================
class FoldCreator:
    def __init__(
            self,
            task_type: TaskType,
            n_splits: int = 5,
            batch_size: int = 2048,
            seed: int = 42,
            use_weighted_sampling: bool = False,
            task_set: Optional[object] = None,
            task_a_input_type: str = "checkin",
            task_b_input_type: str = "checkin",
            aligned_pairing: bool = False,
            lazy_single_task: bool = False,
    ):
        self.task_type = task_type
        self.n_splits = n_splits
        self.batch_size = batch_size
        self.seed = seed
        self.use_weighted_sampling = use_weighted_sampling
        # Single-task (CATEGORY / NEXT) only. False (default) = the eager loop, unchanged:
        # every fold's tensor slices + loaders are built up front. True = build each fold
        # on demand via ``_LazyFoldMapping`` (the pattern the check2hgi-MTL path already
        # uses). Set by ``scripts/train.py`` only for ``--only-fold`` / ``--only-folds``, so
        # the unselected folds are never materialised (on MPS every fold's train+val
        # tensors are pre-moved to unified memory, 5x the dataset at FL). Same split
        # indices, same loaders, same seeds; fold construction draws no RNG.
        self.lazy_single_task = bool(lazy_single_task)
        # G0.1 aligned-pairing — only consumed by ``_create_check2hgi_mtl_folds``.
        # When True the cat + reg train loaders share one per-epoch permutation
        # (a single joint loader on FoldResult.joint_train_loader). Default
        # False = strict no-op (independent shuffles, the legacy behaviour).
        self.aligned_pairing = bool(aligned_pairing)
        # Optional ``TaskSet`` (``src/tasks/presets.py``) used to select
        # which label column loads into task_a slot on the MTL_CHECK2HGI
        # path. ``Optional[object]`` keeps this module free of a
        # cross-package import; the attribute is duck-typed inside
        # ``_create_check2hgi_mtl_folds``. Default ``None`` preserves the
        # legacy next_category-as-task_a behaviour.
        self.task_set = task_set
        # Per-task input modality — only consumed by ``_create_check2hgi_mtl_folds``.
        # Valid values: ``"checkin"`` (9-window of check-in embeddings, the
        # default and bit-exact-legacy), ``"region"`` (9-window of region
        # embeddings, one per step via placeid→poi→region→emb lookup), or
        # ``"concat"`` (the two stacked along the feature dim → 2D per step).
        # Setting either task to anything other than ``"checkin"`` triggers the
        # region-sequence builder and may extend the fold-generation time; the
        # default preserves the legacy checkin-only behaviour exactly.
        valid_inputs = {"checkin", "region", "concat"}
        if task_a_input_type not in valid_inputs:
            raise ValueError(
                f"task_a_input_type must be one of {valid_inputs}, got {task_a_input_type}"
            )
        if task_b_input_type not in valid_inputs:
            raise ValueError(
                f"task_b_input_type must be one of {valid_inputs}, got {task_b_input_type}"
            )
        self.task_a_input_type = task_a_input_type
        self.task_b_input_type = task_b_input_type

        self._config = FoldConfig(
            n_splits=n_splits,
            batch_size=batch_size,
            seed=seed,
            use_weighted_sampling=use_weighted_sampling,
            embedding_dim=0,  # set from artifact in create_folds()
            slide_window=InputsConfig.SLIDE_WINDOW,
        )
        self._task_tensors: Dict[TaskType, TaskTensors] = {}
        self._fold_indices: Dict[TaskType, List[FoldIndices]] = {}

        random.seed(seed)
        torch.manual_seed(seed)
        np.random.seed(seed)

    def create_folds(
            self,
            state: str,
            embedding_engine: EmbeddingEngine,
    ) -> Dict[int, FoldResult]:
        logger.info(f"Creating {self.n_splits}-fold CV for {self.task_type.value}")

        if self.task_type == TaskType.MTL:
            return self._create_mtl_folds(state, embedding_engine)
        if self.task_type == TaskType.MTL_CHECK2HGI:
            return self._create_check2hgi_mtl_folds(state, embedding_engine)
        return self._create_single_task_folds(state, embedding_engine)

    def _create_single_task_folds(
            self,
            state: str,
            embedding_engine: EmbeddingEngine,
    ) -> Dict[int, FoldResult]:
        task = self.task_type
        userids = None

        if task == TaskType.CATEGORY:
            X, y, _placeids, embedding_dim = load_category_data(state, embedding_engine)
        else:
            # For NEXT task we load userids alongside so we can enforce
            # user-disjoint folds via StratifiedGroupKFold below. Without
            # groups, the same user's check-ins can end up in both train
            # and val, which is a leakage bug for sequence prediction —
            # the model can effectively memorise a user's taste instead
            # of generalising. See CONCERNS.md §C11.
            X, y, userids, embedding_dim = load_next_data(state, embedding_engine)

        x_tensor, y_tensor = _convert_to_tensors(X, y, task, embedding_dim=embedding_dim)
        self._task_tensors[task] = TaskTensors(task, x_tensor, y_tensor)
        self._fold_indices[task] = []

        # NEXT: user-disjoint (StratifiedGroupKFold on userid). CATEGORY:
        # stratified on category label (flat POI-level task; no user grouping).
        if task == TaskType.NEXT and userids is not None:
            skf = StratifiedGroupKFold(n_splits=self.n_splits, shuffle=True, random_state=self.seed)
            split_iter = skf.split(X, y, groups=userids)
            logger.info("NEXT single-task: user-disjoint folds via StratifiedGroupKFold.")
        else:
            skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.seed)
            split_iter = skf.split(X, y)

        if self.lazy_single_task:
            # Same split indices, fold records and log lines as the eager loop below; only
            # the per-fold tensor slices + loaders are deferred to first access.
            splits = list(split_iter)
            for fold_idx, (train_idx, val_idx) in enumerate(splits):
                self._fold_indices[task].append(FoldIndices(fold_idx, train_idx, val_idx))
                logger.info(f"Fold {fold_idx + 1}/{self.n_splits}: train={len(train_idx)}, val={len(val_idx)}")

            def _build_fold(fold_idx: int) -> FoldResult:
                train_idx, val_idx = splits[fold_idx]
                train_x, train_y = x_tensor[train_idx], y_tensor[train_idx]
                val_x, val_y = x_tensor[val_idx], y_tensor[val_idx]
                task_data = TaskFoldData(
                    train=FoldData(
                        _create_dataloader(train_x, train_y, self.batch_size, True, self.use_weighted_sampling, self.seed),
                        train_x, train_y
                    ),
                    val=FoldData(
                        _create_dataloader(val_x, val_y, self.batch_size, False, False, self.seed),
                        val_x, val_y
                    ),
                )
                fold_result = FoldResult()
                if task == TaskType.NEXT:
                    fold_result.next = task_data
                else:
                    fold_result.category = task_data
                gc.collect()
                return fold_result

            return _LazyFoldMapping(self.n_splits, _build_fold)

        fold_results: Dict[int, FoldResult] = {}

        for fold_idx, (train_idx, val_idx) in enumerate(split_iter):
            self._fold_indices[task].append(FoldIndices(fold_idx, train_idx, val_idx))
            logger.info(f"Fold {fold_idx + 1}/{self.n_splits}: train={len(train_idx)}, val={len(val_idx)}")

            train_x, train_y = x_tensor[train_idx], y_tensor[train_idx]
            val_x, val_y = x_tensor[val_idx], y_tensor[val_idx]

            task_data = TaskFoldData(
                train=FoldData(
                    _create_dataloader(train_x, train_y, self.batch_size, True, self.use_weighted_sampling, self.seed),
                    train_x, train_y
                ),
                val=FoldData(
                    _create_dataloader(val_x, val_y, self.batch_size, False, False, self.seed),
                    val_x, val_y
                ),
            )

            fold_result = FoldResult()
            if task == TaskType.NEXT:
                fold_result.next = task_data
            else:
                fold_result.category = task_data

            fold_results[fold_idx] = fold_result
            gc.collect()

        return fold_results

    def _create_mtl_folds(
            self,
            state: str,
            embedding_engine: EmbeddingEngine,
    ) -> Dict[int, FoldResult]:
        """Create MTL folds using user-isolation split protocol (SPLIT_PROTOCOL.md).

        Algorithm:
        1. Split users via StratifiedGroupKFold(groups=userid, y=next_category)
        2. Build POI→users mapping to classify POIs per fold
        3. Next-task: train = train-user sequences, val = val-user sequences
        4. Category-task: train = train-exclusive + ambiguous POIs,
                          val = val-exclusive POIs
        """
        # Load data
        X_next, y_next, next_userids, next_dim = load_next_data(state, embedding_engine)
        X_cat, y_cat, cat_placeids, cat_dim = load_category_data(state, embedding_engine)

        x_next_tensor, y_next_tensor = _convert_to_tensors(X_next, y_next, TaskType.NEXT, embedding_dim=next_dim)
        x_cat_tensor, y_cat_tensor = _convert_to_tensors(X_cat, y_cat, TaskType.CATEGORY, embedding_dim=cat_dim)

        self._task_tensors[TaskType.NEXT] = TaskTensors(TaskType.NEXT, x_next_tensor, y_next_tensor)
        self._task_tensors[TaskType.CATEGORY] = TaskTensors(TaskType.CATEGORY, x_cat_tensor, y_cat_tensor)
        self._fold_indices[TaskType.NEXT] = []
        self._fold_indices[TaskType.CATEGORY] = []

        # Determine whether we can run the full user-isolation protocol.
        # cat_placeids is None when the category parquet predates Phase 2.
        use_poi_protocol = cat_placeids is not None

        if use_poi_protocol:
            # Build POI→users mapping from raw checkins
            from data.poi_user_mapping import build_poi_user_mapping
            poi_users = build_poi_user_mapping(state, embedding_engine)

            # Build sequence→POI mapping for overlap diagnostics
            from data.sequence_poi_mapping import build_sequence_poi_mapping
            seq_poi_mapping = build_sequence_poi_mapping(state, embedding_engine)
        else:
            logger.warning(
                "MTL split: no placeid data available; "
                "falling back to independent StratifiedKFold for category splits."
            )
            poi_users = {}
            seq_poi_mapping = {}
            # Pre-compute category splits so they align by fold index
            from sklearn.model_selection import StratifiedKFold
            _skf_cat = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.seed)
            _cat_fold_splits = list(_skf_cat.split(X_cat, y_cat))

        # Step 1: Split users with StratifiedGroupKFold on next-task data
        sgkf = StratifiedGroupKFold(n_splits=self.n_splits, shuffle=True, random_state=self.seed)

        fold_results: Dict[int, FoldResult] = {}
        self._fold_manifests: List[dict] = []

        for fold_idx, (train_next_idx, val_next_idx) in enumerate(
                sgkf.split(X_next, y_next, groups=next_userids)
        ):
            train_users = set(next_userids[train_next_idx])
            val_users = set(next_userids[val_next_idx])

            logger.info(
                f"Fold {fold_idx + 1}/{self.n_splits}: "
                f"train_users={len(train_users)}, val_users={len(val_users)}"
            )

            if use_poi_protocol:
                # Step 2: Classify POIs (user-isolation leak guard) — see _classify_pois.
                train_exclusive, val_exclusive, ambiguous = _classify_pois(
                    poi_users, train_users, val_users,
                )

                logger.info(
                    f"  POIs: train_excl={len(train_exclusive)}, "
                    f"val_excl={len(val_exclusive)}, ambiguous={len(ambiguous)}"
                )

                # Step 3: Derive category fold indices
                # Category train = train-exclusive + ambiguous POIs
                # Category val = val-exclusive POIs only
                cat_train_pois = set(train_exclusive) | set(ambiguous)
                cat_val_pois = set(val_exclusive)

                # Coerce both sides to str before set membership.
                # `cat_placeids` dtype depends on the upstream embedding engine:
                #   - space2vec / sphere2vec / notebook-style engines store
                #     `placeid` as Python str (object dtype) in category.parquet
                #   - fusion (and any engine that preserves the raw int64) stores
                #     it as int64
                # `poi_users` (built from raw checkins via build_poi_user_mapping)
                # always has int keys, so without this coercion `np.isin` returns
                # all-False whenever the embedding engine cast placeid to str —
                # producing empty category folds and a downstream
                # `num_samples=0` crash in DataLoader.
                cat_placeids_str = cat_placeids.astype(str)
                cat_train_pois_str = {str(p) for p in cat_train_pois}
                cat_val_pois_str = {str(p) for p in cat_val_pois}

                train_cat_idx = np.where(np.isin(cat_placeids_str, list(cat_train_pois_str)))[0]
                val_cat_idx = np.where(np.isin(cat_placeids_str, list(cat_val_pois_str)))[0]
            else:
                # Fallback: use pre-computed StratifiedKFold splits for category
                train_exclusive, val_exclusive, ambiguous = [], [], []
                train_cat_idx, val_cat_idx = _cat_fold_splits[fold_idx]

            logger.info(
                f"  Category: train={len(train_cat_idx)}, val={len(val_cat_idx)}"
            )
            logger.info(
                f"  Next: train={len(train_next_idx)}, val={len(val_next_idx)}"
            )

            self._fold_indices[TaskType.NEXT].append(
                FoldIndices(fold_idx, train_next_idx, val_next_idx)
            )
            self._fold_indices[TaskType.CATEGORY].append(
                FoldIndices(fold_idx, train_cat_idx, val_cat_idx)
            )

            # Build fold manifest data
            self._fold_manifests.append({
                'fold_idx': fold_idx,
                'train_users': sorted(train_users),
                'val_users': sorted(val_users),
                'train_exclusive_pois': sorted(train_exclusive),
                'val_exclusive_pois': sorted(val_exclusive),
                'ambiguous_pois': sorted(ambiguous),
                'split_mode': 'strict' if use_poi_protocol else 'legacy_stratified',
                'category_train_count': len(train_cat_idx),
                'category_val_count': len(val_cat_idx),
                'next_train_count': len(train_next_idx),
                'next_val_count': len(val_next_idx),
                'overlap': {
                    'ambiguous_poi_count': len(ambiguous),
                    'ambiguous_poi_fraction': len(ambiguous) / max(len(poi_users), 1),
                    'cat_train_next_val_poi_count': len(ambiguous),
                    'cat_train_next_val_seq_fraction': (
                        _compute_overlap_seq_fraction(ambiguous, val_next_idx, seq_poi_mapping)
                        if use_poi_protocol else 0.0
                    ),
                },
                'seed': self.seed,
            })

            fold_results[fold_idx] = FoldResult(
                next=TaskFoldData(
                    train=FoldData(
                        _create_dataloader(x_next_tensor[train_next_idx], y_next_tensor[train_next_idx],
                                           self.batch_size, True, self.use_weighted_sampling, self.seed),
                        x_next_tensor[train_next_idx], y_next_tensor[train_next_idx]
                    ),
                    val=FoldData(
                        _create_dataloader(x_next_tensor[val_next_idx], y_next_tensor[val_next_idx],
                                           self.batch_size, False, False, self.seed),
                        x_next_tensor[val_next_idx], y_next_tensor[val_next_idx]
                    ),
                ),
                category=TaskFoldData(
                    train=FoldData(
                        _create_dataloader(x_cat_tensor[train_cat_idx], y_cat_tensor[train_cat_idx],
                                           self.batch_size, True, self.use_weighted_sampling, self.seed),
                        x_cat_tensor[train_cat_idx], y_cat_tensor[train_cat_idx]
                    ),
                    val=FoldData(
                        _create_dataloader(x_cat_tensor[val_cat_idx], y_cat_tensor[val_cat_idx],
                                           self.batch_size, False, False, self.seed),
                        x_cat_tensor[val_cat_idx], y_cat_tensor[val_cat_idx]
                    ),
                ),
            )
            gc.collect()

        return fold_results

    def _create_check2hgi_mtl_folds(
            self,
            state: str,
            embedding_engine: EmbeddingEngine,
    ) -> Dict[int, FoldResult]:
        """Check2HGI 2-task MTL fold creation.

        Both tasks (next_category + next_region) share the same X rows
        from ``next.parquet`` — only the label column differs. A single
        StratifiedGroupKFold on userids (stratified on next_category)
        assigns the same fold indices to both tasks.

        Returns a ``FoldResult`` where ``.category`` carries the
        next_category task (task_a slot, 7 classes) and ``.next``
        carries the next_region task (task_b slot, ~1K-5K classes).
        """
        # MTL counterfactual permits HGI provided next_region.parquet has been
        # pre-built by scripts/probe/build_hgi_next_region.py. Designs B/J/L (Lever 5)
        # + the Lever-4 stack reuse canonical c2hgi sequences/folds verbatim (only
        # substrate embeddings differ); next.parquet + next_region.parquet are
        # pre-built by scripts/substrate_protocol_cleanup/postbuild_design_substrate.sh.
        if embedding_engine not in MTL_CHECK2HGI_ALLOWED_ENGINES:
            raise ValueError(
                f"MTL_CHECK2HGI requires engine in {MTL_CHECK2HGI_ALLOWED_ENGINES}; "
                f"got {embedding_engine}."
            )

        # Load X + next_category labels from next.parquet.
        X, y_cat, userids, next_dim, y_region, y_last_region, use_aux = (
            _load_and_validate_check2hgi_data(state, embedding_engine, self.task_set)
        )

        # Host-RAM fail-loud guard BEFORE building the big tensors: this path holds
        # X + x_checkin + one region tensor per "region"/"concat" tower + per-fold
        # slices, all at once. An oversized stride-1 large-state load (CA/TX ~3M rows)
        # would otherwise OOM-kill the box. The GPU is not the limit (per-batch
        # footprint is N-independent); this is host memory.
        _n_region_towers = sum(
            1 for t in (self.task_a_input_type, self.task_b_input_type)
            if t in ("region", "concat")
        )
        _num_features = int(X.shape[1])
        _guard_mtl_check2hgi_ram(
            len(X), _num_features, _n_region_towers, where="mtl_check2hgi",
        )

        slide_window = InputsConfig.SLIDE_WINDOW
        x_checkin, y_cat_tensor = _convert_to_tensors(
            X, y_cat, TaskType.NEXT, embedding_dim=next_dim, slide_window=slide_window,
        )
        y_region_tensor = torch.from_numpy(np.ascontiguousarray(y_region, dtype=np.int64))
        aux_tensor = (
            torch.from_numpy(np.ascontiguousarray(y_last_region, dtype=np.int64))
            if use_aux else None
        )

        # Per-task modality: task_a = next_category (CATEGORY slot), task_b = next_region
        # (NEXT slot). Each slot picks its own X (checkin / region / concat); when both are
        # "checkin" (the default) x_checkin is shared and no region-sequence build runs
        # (bit-equivalent to the legacy checkin-only path). See _resolve_task_input.
        x_task_a = _resolve_task_input(self.task_a_input_type, state, embedding_engine, x_checkin,
                                       expect_userids=userids)
        x_task_b = _resolve_task_input(self.task_b_input_type, state, embedding_engine, x_checkin,
                                       expect_userids=userids)
        logger.info(
            "MTL_CHECK2HGI input modality: task_a=%s (%s), task_b=%s (%s)",
            self.task_a_input_type, tuple(x_task_a.shape),
            self.task_b_input_type, tuple(x_task_b.shape),
        )

        # Store under legacy TaskType keys: NEXT = region (task_b),
        # CATEGORY = next_category (task_a). Each slot carries its own
        # X tensor — they may be the same object if both are "checkin".
        self._task_tensors[TaskType.NEXT] = TaskTensors(
            TaskType.NEXT, x_task_b, y_region_tensor,
        )
        self._task_tensors[TaskType.CATEGORY] = TaskTensors(
            TaskType.CATEGORY, x_task_a, y_cat_tensor,
        )
        self._fold_indices[TaskType.NEXT] = []
        self._fold_indices[TaskType.CATEGORY] = []

        sgkf = StratifiedGroupKFold(
            n_splits=self.n_splits, shuffle=True, random_state=self.seed,
        )
        self._fold_manifests: List[dict] = []

        # Compute the split index arrays EAGERLY (cheap — just int64 index arrays,
        # ~N×8 B per fold) and record fold indices/manifests. The expensive part —
        # materializing each fold's [N_fold,9,D] fancy-index slices and loaders —
        # is deferred to ``_build_fold`` and produced ONE FOLD AT A TIME by the
        # _LazyFoldMapping below. This keeps host-RAM at ~base + one fold instead of
        # base + all n_splits folds (the CA/TX overlap OOM). Byte-identical: same
        # split indices, same loaders, same seeds — only the build *timing* changes.
        splits = list(sgkf.split(X, y_cat, groups=userids))
        for fold_idx, (train_idx, val_idx) in enumerate(splits):
            logger.info(
                f"Fold {fold_idx + 1}/{self.n_splits}: "
                f"train={len(train_idx)} val={len(val_idx)} "
                f"(users train={len(set(userids[train_idx]))} "
                f"val={len(set(userids[val_idx]))})"
            )
            self._fold_indices[TaskType.NEXT].append(
                FoldIndices(fold_idx, train_idx, val_idx)
            )
            self._fold_indices[TaskType.CATEGORY].append(
                FoldIndices(fold_idx, train_idx, val_idx)
            )
            self._fold_manifests.append({
                'fold_idx': fold_idx,
                'train_count': int(len(train_idx)),
                'val_count': int(len(val_idx)),
                'split_mode': 'check2hgi_mtl_user_group',
                'seed': self.seed,
            })

        def _build_fold(fold_idx: int) -> FoldResult:
            train_idx, val_idx = splits[fold_idx]

            # Task-b (region) dataloader: aux-aware if head needs last_region_idx.
            if use_aux:
                train_loader_b = _create_aux_dataloader(
                    x_task_b[train_idx], y_region_tensor[train_idx],
                    aux_tensor[train_idx],
                    self.batch_size, True, self.use_weighted_sampling, self.seed,
                )
                val_loader_b = _create_aux_dataloader(
                    x_task_b[val_idx], y_region_tensor[val_idx],
                    aux_tensor[val_idx],
                    self.batch_size, False, False, self.seed,
                )
            else:
                train_loader_b = _create_dataloader(
                    x_task_b[train_idx], y_region_tensor[train_idx],
                    self.batch_size, True, self.use_weighted_sampling, self.seed,
                )
                val_loader_b = _create_dataloader(
                    x_task_b[val_idx], y_region_tensor[val_idx],
                    self.batch_size, False, False, self.seed,
                )

            # G0.1 aligned-pairing: one shared-permutation joint TRAIN loader so
            # cat-window k trains paired with reg-window k (both indexed by the
            # same train_idx → same window). Val stays the independent (already
            # aligned) loaders. Seed is fold-offset so each fold reshuffles
            # distinctly yet reproducibly. Weighted sampling is incompatible
            # with the shared permutation (champion G uses none).
            joint_train_loader = None
            if self.aligned_pairing:
                if self.use_weighted_sampling:
                    raise ValueError(
                        "aligned_pairing is incompatible with use_weighted_sampling "
                        "(the shared permutation cannot also weight-sample)."
                    )
                joint_train_loader = _create_aligned_joint_loader(
                    x_task_b[train_idx], y_region_tensor[train_idx],
                    x_task_a[train_idx], y_cat_tensor[train_idx],
                    aux_tensor[train_idx] if use_aux else None,
                    self.batch_size, self.seed + fold_idx,
                )

            # FoldData.x is None: the MTL runner never reads it (only .dataloader
            # and .y) — keeping it would re-materialize a second full per-fold copy
            # of the [N_fold,9,D] tensor (the CA/TX overlap host-RAM blowup).
            result = FoldResult(
                next=TaskFoldData(
                    train=FoldData(
                        train_loader_b, None, y_region_tensor[train_idx],
                    ),
                    val=FoldData(
                        val_loader_b, None, y_region_tensor[val_idx],
                    ),
                ),
                category=TaskFoldData(
                    train=FoldData(
                        _create_dataloader(
                            x_task_a[train_idx], y_cat_tensor[train_idx],
                            self.batch_size, True, self.use_weighted_sampling, self.seed,
                        ),
                        None, y_cat_tensor[train_idx],
                    ),
                    val=FoldData(
                        _create_dataloader(
                            x_task_a[val_idx], y_cat_tensor[val_idx],
                            self.batch_size, False, False, self.seed,
                        ),
                        None, y_cat_tensor[val_idx],
                    ),
                ),
                joint_train_loader=joint_train_loader,
            )
            gc.collect()
            return result

        # n_regions = max region id + 1 over ALL rows. The union of every fold's
        # (train ∪ val) is exactly all rows, so this equals the per-fold-scan result
        # but without materialising any fold.
        _n_regions = int(y_region_tensor.max().item()) + 1 if y_region_tensor.numel() else None
        return _LazyFoldMapping(self.n_splits, _build_fold, n_regions=_n_regions)

    def save(self, save_dir: Path) -> Path:
        if not self._task_tensors:
            raise ValueError("No folds created yet. Call create_folds() first.")

        serializable = SerializableFolds(
            task_tensors=self._task_tensors,
            fold_indices=self._fold_indices,
            config=self._config,
            created_at=datetime.now().isoformat(),
        )
        return save_folds(serializable, save_dir)

    def save_split_manifests(self, output_dir: Path) -> List[Path]:
        """Emit split_manifest_fold*.json for each fold + a top-level
        fold_set_digest.json so paired statistical tests can verify they're
        comparing the same partition.

        Only available after _create_mtl_folds() has been called.
        Returns list of paths written.
        """
        if not hasattr(self, '_fold_manifests') or not self._fold_manifests:
            logger.warning("No fold manifests to save (not an MTL split or create_folds not called)")
            return []

        from data.fold_digest import compute_fold_set_digest

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []

        digest = compute_fold_set_digest(self._fold_manifests)

        for manifest in self._fold_manifests:
            fold_idx = manifest['fold_idx']
            path = output_dir / f"split_manifest_fold{fold_idx}.json"
            # Embed the run-level digest in each per-fold manifest so a
            # single fold file is self-describing for paired-test code
            # that may not have access to the sibling digest.json.
            stamped = dict(manifest)
            stamped['fold_set_digest'] = digest
            with open(path, 'w') as f:
                json.dump(stamped, f, indent=2, default=_json_default)
            paths.append(path)
            logger.info(f"Split manifest written: {path}")

        digest_path = output_dir / "fold_set_digest.json"
        with open(digest_path, 'w') as f:
            json.dump({
                'fold_set_digest': digest,
                'n_folds': len(self._fold_manifests),
                'seed': self.seed,
                'state': getattr(self, 'state', None),
                'engine': getattr(self, '_engine_value', None),
            }, f, indent=2, default=_json_default)
        paths.append(digest_path)
        logger.info(f"Fold-set digest written: {digest_path} ({digest[:12]}...)")

        return paths

    @classmethod
    def load(cls, path: Path) -> Dict[int, FoldResult]:
        serialized = load_folds(path)
        return rebuild_dataloaders(serialized)
