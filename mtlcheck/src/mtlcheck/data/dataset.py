"""Assembly — the substrate's files become the tensors one training cell consumes.

This is the layer-2 entry point and the only place that reads the substrate directory. It:

1. loads the two input tables and **hard-fails** unless they are row-aligned (invariant S9),
2. derives the region label space from the label column (not from the place/region map),
3. builds the two input tensors, caching the expensive one,
4. hands out per-fold streams for whichever task family is being trained.

The alignment check is not paranoia. Row-count parity is necessary but not sufficient: a region
table built from a different windowing can carry the same row count and a different per-row user,
which mis-pairs every (window, region-label) pair while every shape stays valid. The reference
trainer hard-fails on exactly this, and the check belongs at runtime, not only in a test.
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .. import ids, paths
from ..config import DataConfig, TaskFamily
from ..substrate import identity as substrate_identity
from . import loaders, splits, tensors

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Inputs:
    """Everything one state's cells share, built once."""

    state: str
    engine: str
    checkin: np.ndarray            # [N, 9, 64]
    region: np.ndarray | None      # [N, 9, 64] — None when no family needs it
    y_category: np.ndarray         # [N] int64, 0..6
    y_region: np.ndarray           # [N] int64
    last_region: np.ndarray        # [N] int64 — the flow head's auxiliary input
    userid: np.ndarray             # [N] int64
    n_categories: int
    n_regions: int
    #: Qual substrato foi lido, por nível. `None` num nível significa "sem manifesto", que é o caso
    #: dos diretórios do engine canônico ANTIGO. Registrado na célula para que um resume consiga
    #: perceber que o substrato mudou — antes de 2026-08-19 ele não conseguia.
    provenance: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.y_category)


def load(state: str, engine: str, config: DataConfig, *, need_region_tower: bool,
         substrate_dir: Path | None = None,
         region_embeddings_path: Path | None = None,
         graph_path: Path | None = None,
         cache_dir: Path | None = None) -> Inputs:
    """Read one state's inputs and build the tensors the requested family needs."""
    base = substrate_dir or paths.substrate_dir(engine, state)

    next_path = base / "input" / "next.parquet"
    # Only the label columns come into pandas; the 576 embedding columns are streamed straight into
    # the tensor, which halves the peak.
    next_table = pd.read_parquet(next_path, columns=["userid", "next_category"])
    region_table = pd.read_parquet(base / "input" / "next_region.parquet",
                                   columns=["userid", "next_category", "region_idx",
                                            "last_region_idx"])

    _assert_row_aligned(next_table, region_table, state)

    y_category = splits.encode_categories(next_table["next_category"])
    y_region = region_table["region_idx"].to_numpy(dtype=np.int64)
    last_region = region_table["last_region_idx"].to_numpy(dtype=np.int64)
    userid = ids.as_int64(next_table["userid"], name="userid")

    n_regions = tensors.label_space(y_region)
    checkin = tensors.checkin_tensor(next_path, window=config.window)

    region = None
    if need_region_tower:
        region = _region_tower(
            state=state, config=config, n_rows=len(next_table),
            substrate_dir=base,
            region_embeddings_path=region_embeddings_path,
            graph_path=graph_path,
            cache_dir=cache_dir,
        )

    logger.info(
        "%s/%s: %d rows · %d categories · %d region classes (%d observed)",
        state, engine, len(next_table), len(splits.CATEGORY_ORDER), n_regions,
        len(np.unique(y_region)),
    )
    # Qual substrato foi lido, por nível. O de região pode ser um diretório diferente (v18 lia um
    # substrato bidirecional separado) ou o mesmo (v19 unificou), e os dois casos têm de ficar
    # legíveis na célula sem que o leitor precise saber qual receita rodou.
    provenance = {"checkin": substrate_identity.of(base)}
    if region is not None:
        region_dir = (Path(region_embeddings_path).parent if region_embeddings_path
                      else paths.substrate_dir(config.region_engine, state))
        provenance["region"] = substrate_identity.of(region_dir)

    return Inputs(
        state=state, engine=engine, checkin=checkin, region=region,
        y_category=y_category, y_region=y_region, last_region=last_region, userid=userid,
        n_categories=len(splits.CATEGORY_ORDER), n_regions=n_regions, provenance=provenance,
    )


def _assert_row_aligned(next_table: pd.DataFrame, region_table: pd.DataFrame, state: str) -> None:
    """Invariant S9 — the two tables must describe the same rows in the same order."""
    if len(next_table) != len(region_table):
        raise ValueError(
            f"{state}: next.parquet has {len(next_table)} rows and next_region.parquet has "
            f"{len(region_table)}. Rebuild both from the same sequences."
        )
    left = ids.as_int64(next_table["userid"], name="userid")
    right = ids.as_int64(region_table["userid"], name="userid")
    if not np.array_equal(left, right):
        differing = int((left != right).sum())
        raise ValueError(
            f"{state}: the two input tables have the same row count but differ on {differing} "
            f"per-row userids — a stale or cross-windowing region table. Every (window, "
            f"region-label) pair would be mis-paired while every shape stayed valid."
        )
    if not np.array_equal(next_table["next_category"].to_numpy(),
                          region_table["next_category"].to_numpy()):
        raise ValueError(f"{state}: the two tables disagree on next_category despite aligned users")


def _region_tower(*, state: str, config: DataConfig, n_rows: int, substrate_dir: Path,
                  region_embeddings_path: Path | None, graph_path: Path | None,
                  cache_dir: Path | None) -> np.ndarray:
    """Build (or reuse) the [N, 9, 64] region tensor.

    Cached because it is the one input that is computed rather than read: without a cache the same
    lookup runs once per family, per seed, per state. The key covers everything that can change the
    result, so a stale cache is not reachable by changing a config value.
    """
    sequences_path = substrate_dir / "temp" / "sequences_next.parquet"
    region_path = region_embeddings_path or paths.substrate_dir(config.region_engine, state) / "region_embeddings.parquet"

    # THE SUBSTRATE'S OWN maps, when it has them. `export.py` writes place_index.parquet and
    # poi_to_region.parquet into every substrate this package builds, and `check2hgi verify`
    # already requires both — but the only reader was `from_graph`, which unpickles an artifact of
    # the OLD canonical engine. So a substrate built entirely by `mtlcheck` still reached back into
    # `check2hgi/<state>/temp/checkin_graph.pt` for its region tower, and would have gone on doing
    # so even if that pickle described a different build. The pickle stays as the explicit fallback
    # (`--graph-path`, and the old artifacts), never as the silent default.
    parquet_maps = substrate_dir / "place_index.parquet"
    use_parquet = graph_path is None and parquet_maps.exists()
    graph = graph_path or paths.substrate_dir("check2hgi", state) / "temp" / "checkin_graph.pt"
    # The FILES, never the directory: `_cache_key` stats what it is given, and a directory's mtime
    # does not move when a file inside it is rewritten — so keying on the directory would serve a
    # stale tensor after a substrate rebuild, which is the failure the key exists to prevent.
    sources = ([parquet_maps, substrate_dir / "poi_to_region.parquet"] if use_parquet else [graph])

    key = _cache_key(state, config.region_engine, sequences_path, region_path, *sources,
                     n_rows, config.window)
    cached = (cache_dir or paths.runs_root() / "_cache") / f"region_tower_{key}.npy"
    if cached.exists():
        logger.info("region tower: reusing %s", cached.name)
        return np.load(cached)

    sequences = pd.read_parquet(sequences_path)
    if len(sequences) != n_rows:
        raise ValueError(
            f"{state}: sequences_next.parquet has {len(sequences)} rows, the input tables have "
            f"{n_rows} — the region tower would be built over a different row space"
        )
    history = sequences[[f"poi_{i}" for i in range(config.window)]].to_numpy()
    if use_parquet:
        logger.info("region tower: place->region from the substrate's own parquets")
        maps = tensors.PlaceRegionMaps.from_parquet(substrate_dir)
    else:
        logger.info("region tower: place->region from the legacy graph pickle %s", graph)
        maps = tensors.PlaceRegionMaps.from_graph(graph)
    out = tensors.region_tensor(history, maps, pd.read_parquet(region_path))

    cached.parent.mkdir(parents=True, exist_ok=True)
    # Atomic: fold fan-out runs several processes against one cell, and a direct write lets two
    # writers interleave, a reader see a torn file, or a crash leave a permanently poisoned entry.
    staging = cached.with_suffix(f".{os.getpid()}.tmp.npy")
    np.save(staging, out)
    os.replace(staging, cached)
    logger.info("region tower: built and cached %s %s", out.shape, cached.name)
    return out


def _cache_key(*parts) -> str:
    """A digest over everything that determines the tensor, including source mtimes."""
    material = []
    for part in parts:
        if isinstance(part, Path):
            stat = part.stat() if part.exists() else None
            material.append(f"{part}:{stat.st_mtime_ns if stat else 'missing'}:{stat.st_size if stat else 0}")
        else:
            material.append(str(part))
    return hashlib.sha256("|".join(material).encode()).hexdigest()[:16]


def fold_streams(inputs: Inputs, fold: splits.Fold, family: TaskFamily,
                 device: torch.device) -> tuple[loaders.TaskStream, loaders.TaskStream]:
    """The (train, val) streams for a dedicated family, or the category half of the joint.

    Returned as device-resident tensors: the whole split lives on the accelerator and a batch is an
    `index_select`, so there is no per-step host-to-device copy and no worker process.
    """
    if family is TaskFamily.CAT:
        x, y, aux = inputs.checkin, inputs.y_category, None
    elif family is TaskFamily.REG:
        if inputs.region is None:
            raise ValueError("the region family needs the region tower; load with need_region_tower=True")
        x, y, aux = inputs.region, inputs.y_region, inputs.last_region
    else:
        raise ValueError(f"{family} has two streams; use joint_streams")

    return (_stream(x, y, aux, fold.train, device), _stream(x, y, aux, fold.val, device))


def selection_stream(inputs: Inputs, fold: splits.Fold, family: TaskFamily,
                     device: torch.device) -> loaders.TaskStream | None:
    """The stream the checkpoint is chosen on: inner validation when sealed, else None.

    None rather than a silent fallback to the outer fold — the caller must decide. It does NOT
    "fail closed": the runner deliberately falls back to the outer fold so legacy cells keep
    running, which is the whole point of the bridge wave. What makes that safe is not this function
    but the record: the fallback stamps `FoldResult.eval_stream = "outer_fold"`, the aggregate and
    the index carry it, and `score.compare` refuses to pair the two streams. The seal is a recorded
    property, not a promise made in a docstring.
    """
    if fold.inner_val is None:
        return None
    if family is TaskFamily.CAT:
        x, y, aux = inputs.checkin, inputs.y_category, None
    elif family is TaskFamily.REG:
        x, y, aux = inputs.region, inputs.y_region, inputs.last_region
    else:
        raise ValueError(f"{family} has two streams; use joint_streams")
    return _stream(x, y, aux, fold.inner_val, device)


def joint_streams(inputs: Inputs, fold: splits.Fold, device: torch.device):
    """The four streams the joint model needs: (cat_train, cat_val, reg_train, reg_val).

    Both tasks index the SAME rows — that is what makes the MTL-vs-ceiling comparison paired.
    """
    if inputs.region is None:
        raise ValueError("the joint family needs the region tower; load with need_region_tower=True")
    return (
        _stream(inputs.checkin, inputs.y_category, None, fold.train, device),
        _stream(inputs.checkin, inputs.y_category, None, fold.val, device),
        _stream(inputs.region, inputs.y_region, inputs.last_region, fold.train, device),
        _stream(inputs.region, inputs.y_region, inputs.last_region, fold.val, device),
    )


def joint_selection_streams(inputs: Inputs, fold: splits.Fold, device: torch.device):
    """The (cat, reg) streams the joint checkpoint is chosen on, or None when not sealed.

    The joint runner needed this separately from `joint_streams` and did not have it, so while the
    dedicated arms selected on the inner split the joint arm still selected on the outer fold. That
    is worse than leaving both on the legacy rule: a joint-vs-STL comparison would then put an
    optimistic arm against unbiased ones and inflate the joint's advantage by the selection bias —
    measured at ~0.66 pp on one Alabama fold, well above the 0.4 pp equivalence margin.
    """
    if fold.inner_val is None:
        return None
    return (
        _stream(inputs.checkin, inputs.y_category, None, fold.inner_val, device),
        _stream(inputs.region, inputs.y_region, inputs.last_region, fold.inner_val, device),
    )


def _stream(x: np.ndarray, y: np.ndarray, aux: np.ndarray | None,
            index: np.ndarray, device: torch.device) -> loaders.TaskStream:
    return loaders.TaskStream(
        x=torch.from_numpy(np.ascontiguousarray(x[index])).to(device),
        y=torch.from_numpy(np.ascontiguousarray(y[index])).to(device),
        aux=None if aux is None else torch.from_numpy(np.ascontiguousarray(aux[index])).to(device),
    )


__all__ = ["Inputs", "load", "fold_streams", "joint_streams"]
