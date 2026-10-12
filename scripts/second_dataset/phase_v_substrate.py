"""Phase V — train the FROZEN Gowalla-bit-identical Check2HGI substrate for a city,
CONSUMING the existing structural graph (no rebuild → index-aligned with the
folds/priors/labels built in Phase E).

Why this exists: the vanilla check2hgi.pipe.py runs create_embedding with
force_preprocess=True, which rebuilds the graph from a shapefile (point-in-polygon)
and yields DIFFERENT POI/region indices than the city's mahalle checkin_graph.pt.
That would silently desync the substrate from the Phase-E folds/priors/labels. This
driver pins force_preprocess=False so create_embedding takes the
"Using existing graph data" branch (check2hgi.py:950) and trains on YOUR
output/check2hgi/<city>/temp/checkin_graph.pt.

FROZEN recipe (canonical check2hgi GCN, Gowalla-identical):
  dim=64, num_layers=2, attention_head=4, alpha_c2p=0.4/p2r=0.3/r2c=0.3,
  lr=1e-3, max_norm=0.9, epoch=500, edge_type=user_sequence, temporal_decay=3600.
Precision: fp32 (use_amp=False) — Istanbul is small (board small-state decision).

After substrate: also generates the embedding-bearing next-POI input parquet via the
repo's generate_next_input_from_checkins (check-in-level path). The region/category
task parquets are derived downstream by train.py from next_region_labels.parquet.

Run (with board-safe env):
  TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_istanbul \
  python scripts/second_dataset/phase_v_substrate.py --city istanbul --device cuda

CPU/GPU: substrate trains on GPU; seed-independent (build once). NEVER MTL_DATASET_GPU=1.
"""
from __future__ import annotations

import argparse
import pickle as pkl
import sys
from argparse import Namespace
from pathlib import Path

_root = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from configs.paths import IoPaths, EmbeddingEngine  # noqa: E402
from configs.model import InputsConfig  # noqa: E402
from cities import get as get_city  # noqa: E402

# Expected index cardinality of the city's PRIMARY (mahalle) graph — alignment guard.
EXPECTED = {"istanbul": {"pois": 29945, "regions": 520}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--no-compile", action="store_true")
    args = ap.parse_args()
    get_city(args.city)

    graph_file = IoPaths.CHECK2HGI.get_graph_data_file(args.city)
    if not graph_file.exists():
        raise SystemExit(f"MISSING graph {graph_file} — run build_graph.py first.")

    # ---- alignment guard: the substrate MUST consume the mahalle graph ----
    with open(graph_file, "rb") as f:
        g = pkl.load(f)
    n_pois = int(g["num_pois"]); n_regions = int(g["num_regions"])
    print(f"[align] graph {graph_file}: POIs={n_pois} regions={n_regions} "
          f"checkins={int(g['num_checkins'])}")
    exp = EXPECTED.get(args.city)
    if exp:
        assert n_pois == exp["pois"], f"POI count {n_pois} != expected {exp['pois']}"
        assert n_regions == exp["regions"], f"region count {n_regions} != expected {exp['regions']}"
        print(f"[align] OK — matches expected POIs={exp['pois']} regions={exp['regions']}")
    del g

    from embeddings.check2hgi.check2hgi import create_embedding
    from data.inputs.builders import generate_next_input_from_checkins

    cfg = Namespace(
        dim=InputsConfig.EMBEDDING_DIM, num_layers=2, attention_head=4,
        alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3,
        lr=0.001, gamma=1.0, max_norm=0.9, epoch=args.epochs,
        mini_batch_threshold=5_000_000, batch_size=2 ** 13, num_neighbors=10,
        device=args.device, shapefile=None,
        force_preprocess=False,          # CRITICAL: consume existing graph, do NOT rebuild
        edge_type="user_sequence", temporal_decay=3600.0,
        use_compile=not args.no_compile, use_amp=False,   # fp32
    )

    state_token = args.city  # IoPaths.get_graph_data_file lower-cases internally
    print(f"[substrate] training Check2HGI GCN {args.epochs}ep on {args.device} (fp32) ...")
    create_embedding(state=state_token, args=cfg)

    print("[inputs] generating embedding-bearing next-POI parquet ...")
    generate_next_input_from_checkins(state_token, EmbeddingEngine.CHECK2HGI)

    emb = IoPaths.get_embedd(state_token, EmbeddingEngine.CHECK2HGI)
    nxt = IoPaths.get_next(state_token, EmbeddingEngine.CHECK2HGI)
    print(f"[done] embeddings -> {emb}")
    print(f"[done] next parquet -> {nxt}")


if __name__ == "__main__":
    main()
