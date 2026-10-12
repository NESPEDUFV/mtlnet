"""Per-item embedding + label loading for the embedding-eval ladder (L0/L1).

Builds a single per-item table ``(emb, placeid, category, region, poi)`` for an
engine/state, at either ``poi`` (mean-pooled per placeid — the cross-engine
comparable granularity) or ``checkin`` (native rows) granularity.

Region labels come from the *shared* geographic partition stored in
``check2hgi/<state>/temp/checkin_graph.pt`` (keys ``placeid_to_idx`` +
``poi_to_region``) so every engine is scored against the SAME regions
(Protocol invariant §5). Category labels come from each engine's own
``category`` column mapped through ``CATEGORIES_MAP``.

``poi`` (the placeid itself, densified to ``[0, n_poi)``) is exposed as a label
axis so the future next-poi task needs no new plumbing in L0/L1.
"""
from __future__ import annotations

import pickle as pkl
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional

import numpy as np
import pandas as pd

from configs.globals import CATEGORIES_MAP
from configs.paths import EmbeddingEngine, IoPaths

# Inverse category map: "Food" -> 2. Excludes nothing; rows whose category is
# not a key (rare/garbage) map to -1 and are dropped per-task by callers.
_CAT_TO_IDX: Dict[str, int] = {v: k for k, v in CATEGORIES_MAP.items()}


@dataclass
class ItemTable:
    """A per-item embedding table with aligned label axes (np arrays, len N)."""

    engine: str
    state: str
    granularity: str
    emb: np.ndarray          # [N, D] float32
    placeid: np.ndarray      # [N] int64
    category: np.ndarray     # [N] int64, -1 = unmapped
    region: np.ndarray       # [N] int64, -1 = unmapped
    poi: np.ndarray          # [N] int64, densified placeid in [0, n_poi)

    def labels(self, task: str) -> np.ndarray:
        return {"cat": self.category, "reg": self.region, "poi": self.poi}[task]

    def valid_mask(self, task: str) -> np.ndarray:
        return self.labels(task) >= 0


@lru_cache(maxsize=8)
def _region_lookup(state: str) -> Dict[int, int]:
    """placeid -> region_idx, from the shared check2hgi geographic partition.

    Callers pass ``state.lower()`` so the lru_cache key is canonical; the source
    engine is always CHECK2HGI (Protocol invariant §5). Lowercased again here as
    a defensive no-op in case of a direct call.
    """
    state = state.lower()
    graph_path = IoPaths.CHECK2HGI.get_graph_data_file(state)
    with open(graph_path, "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    poi_to_region = np.asarray(poi_to_region, dtype=np.int64)
    return {int(pid): int(poi_to_region[idx]) for pid, idx in placeid_to_idx.items()}


def _numeric_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if str(c).isdigit()]


def load_item_table(
    state: str,
    engine: EmbeddingEngine,
    granularity: str = "poi",
    max_items: Optional[int] = None,
    seed: int = 0,
) -> ItemTable:
    """Load an aligned per-item table for ``engine``/``state``.

    granularity:
      * ``poi``     — one row per placeid (embedding mean-pooled over check-ins).
                      The cross-engine comparable view; HGI is already POI-level.
      * ``checkin`` — native rows (POI-level engines collapse to their POIs).

    ``max_items`` subsamples rows (after pooling) with a fixed seed — use it to
    keep check-in-level L0 (kNN is O(N^2)) tractable on the 1.4M-row substrates.
    """
    if granularity not in ("poi", "checkin"):
        raise ValueError(f"granularity must be 'poi' or 'checkin', got {granularity!r}")

    df = IoPaths.load_embedd(state, engine)
    num = _numeric_cols(df)
    if "placeid" not in df.columns:
        raise ValueError(f"{engine.value}/{state} embeddings have no placeid column")
    if "category" not in df.columns:
        raise ValueError(f"{engine.value}/{state} embeddings have no category column")

    if granularity == "poi":
        # mean-pool embeddings per placeid; category is constant per placeid.
        agg = {c: "mean" for c in num}
        agg["category"] = "first"
        df = df.groupby("placeid", as_index=False, sort=False).agg(agg)

    placeid = df["placeid"].to_numpy(dtype=np.int64)
    emb = df[num].to_numpy(dtype=np.float32)

    category = (
        df["category"].map(_CAT_TO_IDX).fillna(-1).to_numpy(dtype=np.int64)
    )

    reg_map = _region_lookup(state.lower())  # lowercased so the lru_cache key is canonical
    region = (
        df["placeid"].map(reg_map).fillna(-1).to_numpy(dtype=np.int64)
    )

    # densify placeid -> [0, n_poi) for the next-poi label axis
    uniq, poi = np.unique(placeid, return_inverse=True)
    poi = poi.astype(np.int64)

    if max_items is not None and len(emb) > max_items:
        rng = np.random.default_rng(seed)
        sel = rng.choice(len(emb), size=max_items, replace=False)
        sel.sort()
        emb, placeid, category, region, poi = (
            emb[sel], placeid[sel], category[sel], region[sel], poi[sel]
        )

    return ItemTable(
        engine=engine.value, state=state, granularity=granularity,
        emb=emb, placeid=placeid, category=category, region=region, poi=poi,
    )
