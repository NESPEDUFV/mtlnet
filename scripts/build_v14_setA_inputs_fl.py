#!/usr/bin/env python
"""Build v14 (check2hgi_design_k_resln_mae_l0_1) FL set-a inputs for the CSLSL cascade (Task E).

Mirrors what the M4 did for AL/AZ: generate_next_input_from_checkins (DEFAULT windowing =
set-a stride-9 non-overlap, min_seq=5) + build_next_region_for, into the v14 engine dir, so
b4_cascade (default engine = v14) runs on the SAME base as M4's AL/AZ cascade table. NOT dk_ovl.
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "scripts" / "mtl_improvement"))

from configs.paths import EmbeddingEngine, IoPaths
from data.inputs.builders import generate_next_input_from_checkins
from build_overlap_probe_engine import build_next_region_for

V14 = EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_MAE_L0_1
state = "florida"

print(f"=== build v14 set-a inputs for {state} (stride=9 non-overlap, min_seq=5) ===")
print("[1/2] generate_next_input_from_checkins (checkin windows + sequences)...")
generate_next_input_from_checkins(state, V14)  # defaults: stride=None->9, min_seq=5

print("[2/2] build_next_region_for (region labels)...")
build_next_region_for(state, V14)

n = len(IoPaths.load_next(state, V14))
print(f"DONE: {V14.value}/{state} next.parquet rows={n:,}")
