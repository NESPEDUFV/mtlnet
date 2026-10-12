"""pre_freeze_gates — v14 substrate postbuild (M4 local equivalent of
substrate_protocol_cleanup/postbuild_design_substrate.sh, which has A40-hardcoded paths).

After build_design_k_delaunay.py writes the v14 substrate, generate its downstream inputs:
  1. next.parquet  (check-in-level, via generate_next_input_from_checkins)
  2. next_region.parquet (region labels + last_region_idx, via build_design_next_region)
log_T is NOT copied here — A2/A4 build seeded per-fold train-only log_T separately.
"""
import sys
from argparse import ArgumentParser
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "scripts"))

from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins
from substrate_protocol_cleanup.build_design_next_region import build as build_next_region

ENGINE = EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_MAE_L0_1


def main():
    ap = ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    print(f"[postbuild_v14] {args.state}: generate_next_input_from_checkins")
    generate_next_input_from_checkins(args.state, ENGINE)
    print(f"[postbuild_v14] {args.state}: build_design_next_region")
    out = build_next_region(args.state, ENGINE)
    print(f"[postbuild_v14] DONE {args.state} -> {out}")


if __name__ == "__main__":
    main()
