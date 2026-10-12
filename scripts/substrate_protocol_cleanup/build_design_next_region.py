"""Build per-design ``next_region.parquet`` for Designs B / J / L.

The Tier B substrate designs (B, J, L) copy canonical c2hgi's
``checkin_graph.pt`` and ``sequences_next.parquet`` verbatim. Their
``next.parquet`` already exists once the design's MTL pipeline runs
``generate_next_input_from_checkins`` (i.e. after the engine is
registered in ``_CHECKIN_LEVEL_ENGINES``).

This helper builds the substrate's ``input/next_region.parquet`` by
joining the substrate's ``next.parquet`` columns with the canonical
graph's region labels (which are byte-identical between substrates).

Usage::

    .venv/bin/python scripts/substrate_protocol_cleanup/build_design_next_region.py \
        --state alabama --engine check2hgi_design_b
"""

from __future__ import annotations

import argparse
import pickle as pkl
import sys
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from configs.paths import EmbeddingEngine, IoPaths  # noqa: E402


def _load_canonical_graph_maps(state: str) -> Tuple[dict, np.ndarray]:
    """Load placeid_to_idx + poi_to_region from canonical c2hgi (substrates copy these verbatim)."""
    graph_path = IoPaths.CHECK2HGI.get_graph_data_file(state)
    with open(graph_path, "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    return placeid_to_idx, np.asarray(poi_to_region, dtype=np.int64)


def _load_canonical_sequences(state: str) -> pd.DataFrame:
    """Load canonical sequences_next.parquet — identical to substrate's copy."""
    seq_path = IoPaths.CHECK2HGI.get_temp_dir(state) / "sequences_next.parquet"
    if not seq_path.exists():
        raise FileNotFoundError(f"canonical sequences_next.parquet missing at {seq_path}")
    return pd.read_parquet(seq_path)


def build(state: str, engine: EmbeddingEngine) -> Path:
    next_df = IoPaths.load_next(state, engine)
    seq_df = _load_canonical_sequences(state)

    if len(next_df) != len(seq_df):
        raise ValueError(
            f"substrate next.parquet rows ({len(next_df)}) and canonical sequences_next.parquet "
            f"rows ({len(seq_df)}) disagree for {state}/{engine.name}. Verify the substrate's "
            f"next.parquet was generated from canonical c2hgi sequences."
        )
    next_uid = next_df["userid"].astype(str).reset_index(drop=True)
    seq_uid = seq_df["userid"].astype(str).reset_index(drop=True)
    if not (next_uid == seq_uid).all():
        raise ValueError(
            f"userid columns of substrate next.parquet and canonical sequences_next.parquet "
            f"disagree for {state}/{engine.name} — the two files are not row-aligned."
        )

    placeid_to_idx, poi_to_region = _load_canonical_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1

    target_placeid = seq_df["target_poi"].astype(np.int64).to_numpy()
    placeid_keys = set(placeid_to_idx.keys())
    unmapped_mask = ~np.isin(target_placeid, list(placeid_keys))
    if unmapped_mask.any():
        sample = target_placeid[unmapped_mask][:10].tolist()
        raise ValueError(f"{int(unmapped_mask.sum())} target_poi unmapped; sample: {sample}")
    poi_idx = pd.Series(target_placeid).map(placeid_to_idx).to_numpy(dtype=np.int64)
    region_idx = poi_to_region[poi_idx]
    if (region_idx < 0).any():
        raise ValueError(f"{int((region_idx < 0).sum())} rows have no region assignment")

    poi_cols = [f"poi_{i}" for i in range(9)]
    poi_mat = seq_df[poi_cols].astype(np.int64).to_numpy()
    valid = poi_mat >= 0
    last_pos = np.where(
        valid.any(axis=1),
        valid.shape[1] - 1 - valid[:, ::-1].argmax(axis=1),
        -1,
    )
    N = poi_mat.shape[0]
    last_poi = np.where(
        last_pos >= 0,
        poi_mat[np.arange(N), np.clip(last_pos, 0, None)],
        -1,
    )
    unmapped_valid = (last_poi >= 0) & ~np.isin(last_poi, list(placeid_keys))
    if unmapped_valid.any():
        raise ValueError(f"{int(unmapped_valid.sum())} last_poi unmapped")
    last_region_idx = np.full(N, -1, dtype=np.int64)
    valid_mask = last_poi >= 0
    if valid_mask.any():
        last_poi_idx = (
            pd.Series(last_poi[valid_mask]).map(placeid_to_idx).to_numpy(dtype=np.int64)
        )
        last_region_idx[valid_mask] = poi_to_region[last_poi_idx]
        if (last_region_idx[valid_mask] < 0).any():
            raise ValueError("last_poi entries resolve to unassigned regions")

    out = next_df.drop(columns=["next_category"]).copy()
    out["region_idx"] = region_idx.astype(np.int64)
    out["last_region_idx"] = last_region_idx.astype(np.int64)

    out_path = IoPaths.get_next_region(state, engine)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)
    print(f"[{state}/{engine.name}] wrote {out_path} rows={len(out)} n_regions={n_regions}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument(
        "--engine",
        required=True,
        choices=[
            "check2hgi_design_b", "check2hgi_design_j", "check2hgi_design_l",
            "check2hgi_lever4_canonical", "check2hgi_lever4_design_b",
            "check2hgi_resln", "check2hgi_resln_design_b", "check2hgi_resln_design_j",
            "check2hgi_design_k_l0_1", "check2hgi_design_k_resln_l0_1",
            "check2hgi_design_k_resln_mae_l0_1",
        ],
    )
    args = parser.parse_args()
    engine = EmbeddingEngine(args.engine)
    build(args.state, engine)


if __name__ == "__main__":
    main()
