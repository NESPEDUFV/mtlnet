"""Acquire raw inputs for a Massive-STEPS city ETL (Phase E0). City-generic.

Downloads (idempotent):
  1. HF dataset parquets for the city (tabular = flat check-ins [used]; data = LLM
     variant [split audit]) + README -> data/massive_steps_<city>/raw/
  2. The shared FSQ v1 category tree -> data/massive_steps_<city>/fsq_v1_tree.json
  3. region source: tiger cities -> NY/etc. TIGER shapefile (NY auto-download here);
     h3 cities -> nothing (H3 cells generated at graph time from the bbox).

Run:  python scripts/second_dataset/acquire.py --city istanbul
Then: build_category_map.py, parse_city.py, build_graph.py, build_inputs.py (all --city).
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cities import get as get_city, data_dir  # noqa: E402

FSQ_TREE = ("MettiHoof/3circles", "master", "Metti/data/category_tree/4sq_categories.json")
TIGER_NY = ("https://www2.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_36_tract.zip",
            Path("data/miscellaneous/tl_2022_36_tract_NY"))


def hf_download(city: str, repo: str) -> None:
    from huggingface_hub import hf_hub_download
    raw = data_dir(city) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    files = ["README.md"] + [f"{sub}/{s}-00000-of-00001.parquet"
                             for sub in ("tabular", "data")
                             for s in ("train", "validation", "test")]
    for f in files:
        hf_hub_download(repo_id=repo, repo_type="dataset", filename=f, local_dir=str(raw))
    print(f"[{city}] hf: {len(files)} files -> {raw}")


def fsq_tree(city: str) -> None:
    repo, branch, path = FSQ_TREE
    r = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={branch}", "--jq", ".content"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api failed for FSQ tree: {r.stderr[:200]}")
    data = json.loads(base64.b64decode(r.stdout).decode("utf-8", "replace"))
    # The 4sq_categories.json is the raw Foursquare API dump: {"meta":..,"response":{"categories":[..]}}.
    # Unwrap response.categories (older code assumed a top-level "categories" key and iterated the
    # dict's KEYS -> "meta".get() AttributeError). Fall back to top-level "categories" or a bare list.
    if isinstance(data, dict) and "response" in data and "categories" in data["response"]:
        cats = data["response"]["categories"]
    elif isinstance(data, dict) and "categories" in data:
        cats = data["categories"]
    else:
        cats = data
    flat = {}

    def walk(node, root):
        root = root or node.get("name")
        if node.get("id"):
            flat[node["id"]] = {"name": node.get("name"), "root": root}
        for c in (node.get("categories") or []):
            walk(c, root)
    for top in cats:
        walk(top, None)
    out = data_dir(city) / "fsq_v1_tree.json"
    out.write_text(json.dumps(flat))
    print(f"[{city}] fsq tree leaves={len(flat)} -> {out}")


def tiger_ny() -> None:
    url, dest = TIGER_NY
    if (dest / "tl_2022_36_tract.shp").exists():
        print(f"tiger: present {dest}"); return
    dest.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    with zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(req, timeout=120).read())) as z:
        z.extractall(dest)
    print(f"tiger: extracted -> {dest}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    args = ap.parse_args()
    cfg = get_city(args.city)
    hf_download(args.city, cfg["hf_repo"])
    fsq_tree(args.city)
    if cfg["region_mode"] == "tiger" and args.city == "nyc":
        tiger_ny()


if __name__ == "__main__":
    main()
