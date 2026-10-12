#!/usr/bin/env python
"""Build the Istanbul STRIDE-1 (overlap) base for the §6.3 champion @ stride-1 (H100 task).

OVERWRITES the on-disk set-a istanbul base IN PLACE (recoverable: set-a numbers are committed in
docs/results/second_dataset/istanbul + PHASE_V_ISTANBUL_S0.md; the set-a base regenerates from the
default windowing). Substrate (520-mahalle checkin_graph + embeddings) is unchanged — only the
windowing differs (stride-1, min_seq-10). Per BASELINE_M4.md §2b prerequisite #1.
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "scripts" / "mtl_improvement"))

from configs.paths import EmbeddingEngine, IoPaths
from data.inputs.builders import generate_next_input_from_checkins
from build_overlap_probe_engine import build_next_region_for

ENG = EmbeddingEngine.CHECK2HGI
state = "istanbul"

print(f"=== build istanbul STRIDE-1 base (stride=1, min_seq=10) — OVERWRITES set-a in place ===")
print("[1/2] generate_next_input_from_checkins (stride=1, min_seq=10)...")
generate_next_input_from_checkins(state, ENG, stride=1, min_sequence_length=10)

print("[2/2] build_next_region_for...")
build_next_region_for(state, ENG)

n = len(IoPaths.load_next(state, ENG))
print(f"DONE: {ENG.value}/{state} stride-1 next.parquet rows={n:,}  (set-a was 58,297; expect ~271,666)")
