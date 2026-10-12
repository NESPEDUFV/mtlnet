#!/usr/bin/env python3
"""Assert every input the three v18_2 cells read. Exit non-zero naming what is missing.

Derived from real failures, one file per launch:
  next_region.parquet        joint  -- FileNotFoundError after 39 s of GPU time
  region_embeddings.parquet  joint  -- read from the ENGINE ROOT, not input/
  checkin_graph.pt           joint+reg -- via region_sequence.py / p1_region_head_ablation.py
The cat cell needs none of the last three, so a cat-only gate passes while the others fail.
"""
import argparse, pathlib, sys

CELLS = {
    "cat": ["output/{eng}/{st}/input/next.parquet"],
    # sequences_next.parquet ADDED 2026-08-10: the reg cell reads it in
    # _build_region_sequence_tensor (p1_region_head_ablation.py:281) but it was listed only under
    # "joint", so a reg-only gate printed "PREFLIGHT OK (3 inputs)" and the cell then died ~50 s
    # later on FileNotFoundError -- which is the exact failure this gate exists to prevent, and
    # worse than no gate because the green line invites you to trust it.
    "reg": ["output/{eng}/{st}/input/next.parquet",
            "output/{eng}/{st}/temp/sequences_next.parquet",
            "output/{v14}/{st}/region_embeddings.parquet",
            "output/check2hgi/{st}/temp/checkin_graph.pt"],
    "joint": ["output/{eng}/{st}/input/next.parquet",
              "output/{eng}/{st}/input/next_region.parquet",
              "output/{eng}/{st}/region_embeddings.parquet",
              "output/{eng}/{st}/temp/sequences_next.parquet",
              "output/{v14}/{st}/region_embeddings.parquet",
              "output/check2hgi/{st}/temp/checkin_graph.pt"],
}

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--state", required=True)
    a.add_argument("--engine", default="check2hgi_v18")
    a.add_argument("--v14", default="check2hgi_design_k_resln_mae_l0_1")
    a.add_argument("--cells", default="cat,reg,joint")
    args = a.parse_args()

    want = []
    for c in args.cells.split(","):
        want += CELLS.get(c.strip(), [])
    want = sorted(set(p.format(st=args.state, eng=args.engine, v14=args.v14) for p in want))

    missing = []
    for rel in want:
        f = pathlib.Path(rel)
        if not f.exists() or f.stat().st_size == 0:
            missing.append(rel)
        else:
            print(f"  OK   {rel}  ({f.stat().st_size/2**20:.1f} MiB)")
    if missing:
        print("PREFLIGHT FAILED -- missing or empty:")
        for m in missing:
            print(f"  MISS {m}")
        sys.exit(1)
    print(f"PREFLIGHT OK ({len(want)} inputs for cells: {args.cells})")

if __name__ == "__main__":
    main()
