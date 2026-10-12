"""pre_freeze_gates — rebuild the canonical HGI substrate locally (M4 Pro).

A2 needs HGI embeddings as the comparator base (and as the Delaunay-edge / POI2Vec /
POI-target source for the v14 design_k rebuild). HGI is absent from this machine
(`output/hgi/` is empty); the handoff's rsync list omitted it. The user chose to rebuild
locally — CARRY THE MACHINE-DRIFT CAVEAT and validate the rebuild against the saved
canonical STL numbers (FINAL_SYNTHESIS / RESULTS_TABLE §0.3) before trusting A2.

Recipe = the frozen canonical HGI config (research/embeddings/hgi/CLAUDE.md + hgi.pipe.py):
dim=64, epoch=2000, poi2vec_epochs=100, lr=0.006, warmup=40, w_r=0.7, device=cpu
(HGI inner loop is ~176x slower on MPS — CPU is correct, not a shortcut).

Usage:
    ./.venv/bin/python scripts/pre_freeze_gates/build_hgi.py --state Alabama
"""
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

from configs.paths import Resources
from configs.model import InputsConfig
from embeddings.hgi.hgi import create_embedding

SHAPEFILES = {
    "alabama": Resources.TL_AL,
    "arizona": Resources.TL_AZ,
    "florida": Resources.TL_FL,
}


def main():
    ap = ArgumentParser()
    ap.add_argument("--state", required=True, help="Alabama | Arizona | Florida")
    args = ap.parse_args()

    state_lc = args.state.lower()
    if state_lc not in SHAPEFILES:
        raise SystemExit(f"Unsupported state {args.state}; expected one of {list(SHAPEFILES)}")

    cfg = Namespace(
        dim=InputsConfig.EMBEDDING_DIM,  # 64
        alpha=0.5,
        attention_head=4,
        lr=0.006,
        gamma=1.0,
        max_norm=0.9,
        epoch=2000,
        warmup_period=40,
        poi2vec_epochs=100,
        force_preprocess=True,
        cross_region_weight=0.7,
        device="cpu",
        shapefile=str(SHAPEFILES[state_lc]),
    )
    print(f"[build_hgi] state={args.state} shapefile={cfg.shapefile} "
          f"epoch={cfg.epoch} w_r={cfg.cross_region_weight} device={cfg.device}")
    create_embedding(state=args.state, args=cfg)
    print(f"[build_hgi] DONE {args.state}")


if __name__ == "__main__":
    main()
