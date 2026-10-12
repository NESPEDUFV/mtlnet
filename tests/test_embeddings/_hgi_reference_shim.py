"""
Shim that imports the ACTUAL original HGI source from
region-embedding-benchmark-main and exposes its module objects.

We do not modify the original source. We only:
  1. monkey-patch out its `print(...)` debug call inside discriminate_poi2region
     so test output is not flooded.
  2. Insert its `model/` directory into sys.path so its
     `from model.set_transformer import PMA` import works.

This file lives under tests/ and is only loaded by the equivalence test.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

REFERENCE_REPO = Path(
    "/Users/vitor/Desktop/mestrado/temp/tarik-new/"
    "region-embedding-benchmark-main/region-embedding-benchmark-main/"
    "region-embedding/baselines/HGI/model"
)


def load_original_hgi():
    """
    Load the original HGI module objects.

    Returns:
        SimpleNamespace with: HierarchicalGraphInfomax, POIEncoder,
        POI2Region, PMA, corruption
    """
    if not REFERENCE_REPO.exists():
        raise RuntimeError(f"Reference repo not found at {REFERENCE_REPO}")

    # Make sure the reference's `model/` directory is importable so
    # `from model.set_transformer import PMA` works.
    if str(REFERENCE_REPO.parent) not in sys.path:
        sys.path.insert(0, str(REFERENCE_REPO.parent))

    # Load set_transformer first (it has no relative imports)
    st_path = REFERENCE_REPO / "set_transformer.py"
    spec_st = importlib.util.spec_from_file_location("model.set_transformer", st_path)
    mod_st = importlib.util.module_from_spec(spec_st)
    sys.modules["model.set_transformer"] = mod_st
    # Also create a fake `model` package entry
    if "model" not in sys.modules:
        import types
        pkg = types.ModuleType("model")
        pkg.__path__ = [str(REFERENCE_REPO)]
        sys.modules["model"] = pkg
    spec_st.loader.exec_module(mod_st)

    # Now load hgi.py from the reference
    hgi_path = REFERENCE_REPO / "hgi.py"
    src = hgi_path.read_text()

    # Strip the debug print that floods stdout every forward pass
    src = src.replace(
        'print(self.weight_poi2region, self.weight_region2city)',
        'pass  # original print stripped for tests',
    )

    # Compile and exec into a fresh module namespace
    import types
    mod = types.ModuleType("reference_hgi")
    mod.__file__ = str(hgi_path)
    code = compile(src, str(hgi_path), "exec")
    exec(code, mod.__dict__)
    sys.modules["reference_hgi"] = mod

    from types import SimpleNamespace
    return SimpleNamespace(
        HierarchicalGraphInfomax=mod.HierarchicalGraphInfomax,
        POIEncoder=mod.POIEncoder,
        POI2Region=mod.POI2Region,
        PMA=mod_st.PMA,
        corruption=mod.corruption,
    )