"""pre_freeze_gates — generate HGI downstream inputs for the A2 cat arm.

create_embedding() builds only the HGI embeddings; it does NOT run stage-5 input
generation. The A2 cat arm (train.py-style next-category via the p1 harness with
--engine-override hgi) needs:
  • output/hgi/<state>/input/next.parquet      (POI-level windows + next_category)
  • output/hgi/<state>/input/category.parquet
  • output/hgi/<state>/input/next_region.parquet  (region labels; substrate-independent)

Region labels are identical across substrates (same windows). We VERIFY the HGI and
check2hgi sequences_next.parquet are row-identical, then reuse check2hgi's next_region.
"""
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))

from configs.paths import EmbeddingEngine, IoPaths
from data.inputs.builders import generate_category_input, generate_next_input_from_poi


def main():
    ap = ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    state = args.state
    state_lc = state.lower()

    print(f"[setup_hgi] {state}: generate_category_input + generate_next_input_from_poi")
    generate_category_input(state, EmbeddingEngine.HGI)
    generate_next_input_from_poi(state, EmbeddingEngine.HGI)

    # Verify row-identity of HGI vs check2hgi sequences, then reuse region labels.
    cols = [f"poi_{i}" for i in range(9)] + ["target_poi", "userid"]
    h = pd.read_parquet(IoPaths.get_seq_next(state, EmbeddingEngine.HGI))[cols].astype(str).to_numpy()
    c = pd.read_parquet(IoPaths.get_seq_next(state, EmbeddingEngine.CHECK2HGI))[cols].astype(str).to_numpy()
    if h.shape != c.shape or not (h == c).all():
        raise AssertionError(
            f"{state}: HGI and check2hgi sequences are NOT row-identical "
            f"(shapes {h.shape} vs {c.shape}). Cannot reuse region labels — investigate."
        )
    src = IoPaths.CHECK2HGI.get_state_dir(state) / "input" / "next_region.parquet"
    dst = Path("output/hgi") / state_lc / "input" / "next_region.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    print(f"[setup_hgi] {state}: sequences row-identical ✓  copied next_region -> {dst}")


if __name__ == "__main__":
    main()
