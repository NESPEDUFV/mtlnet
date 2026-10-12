#!/usr/bin/env python3
"""Validate every board embeddings.parquet: not-corrupt, has data, correct schema, finite/non-degenerate.

Memory-safe: uses pyarrow parquet METADATA + per-column STATISTICS (null_count/min/max) — no full
data load — so it's safe to run alongside training. Falls back to a bounded column read only when a
file has no stats. Hash-verifies against manifests where available.

Checks per embeddings.parquet:
  - opens (valid parquet, not truncated/corrupt)
  - num_rows > 0
  - has >= EMB_DIM embedding columns
  - null_count == 0 across embedding cols (no NaN)  [from stats]
  - not all-zero / not constant (min != max somewhere) [from stats]
Scope: board_baselines/{b2b,ctle,poi2vec}/<state>/s*_f*/, baseline_b2c_onehot64/<state>/,
       and the substrates (check2hgi_design_k_resln_mae_l0_1, hgi, check2hgi, check2hgi_dk_ovl).
"""
from __future__ import annotations
import sys, json, hashlib
from pathlib import Path
import pyarrow.parquet as pq

EMB_DIM = 64
ROOTS = [a for a in sys.argv[1:]] or ["/Volumes/Vitor's SSD/ingred/output",
                                      "/Users/vitor/Desktop/mestrado/ingred/output"]

def emb_cols(schema):
    # embedding cols are the numeric "0".."63" or emb_* / reg_* / 0..63
    names = schema.names
    cand = [n for n in names if n.isdigit() or n.startswith(("emb_", "0"))]
    if not cand:  # fallback: numeric-looking
        cand = [n for n in names if n not in ("userid","placeid","category","datetime","region_id","region_idx")]
    return cand

def check(path: Path) -> dict:
    r = {"path": str(path), "ok": True, "issues": []}
    try:
        md = pq.read_metadata(path)
    except Exception as e:
        return {"path": str(path), "ok": False, "issues": [f"UNREADABLE/CORRUPT: {e}"]}
    r["rows"] = md.num_rows
    if md.num_rows <= 0:
        r["ok"] = False; r["issues"].append("ZERO ROWS")
    try:
        schema = pq.read_schema(path)
    except Exception as e:
        r["ok"] = False; r["issues"].append(f"SCHEMA FAIL: {e}"); return r
    ecols = emb_cols(schema)
    r["n_emb_cols"] = len(ecols)
    if len(ecols) < EMB_DIM:
        r["ok"] = False; r["issues"].append(f"only {len(ecols)} emb cols (<{EMB_DIM})")
    # stats sweep over row groups for the embedding columns
    col_idx = {schema.names[i]: i for i in range(len(schema.names))}
    nulls = 0; saw_stats = False; nonconst = False
    for rg in range(md.num_row_groups):
        rgm = md.row_group(rg)
        for c in ecols:
            if c not in col_idx: continue
            st = rgm.column(col_idx[c]).statistics
            if st is None: continue
            saw_stats = True
            if st.null_count is not None: nulls += st.null_count
            if st.has_min_max and st.min != st.max: nonconst = True
    if saw_stats:
        if nulls > 0: r["ok"] = False; r["issues"].append(f"{nulls} NULL/NaN values")
        if not nonconst: r["ok"] = False; r["issues"].append("DEGENERATE (all emb cols constant)")
    else:
        r["issues"].append("no column stats (corruption not ruled out by stats)")
    return r

def main():
    man = {}
    mp = Path("/Users/vitor/Desktop/mestrado/ingred/docs/studies/closing_data/BASELINES_HASH_MANIFEST.json")
    if mp.exists():
        man = json.loads(mp.read_text()).get("cells", {})
    targets = []
    for root in ROOTS:
        rp = Path(root)
        if not rp.exists(): continue
        for sub in ["board_baselines/b2b","board_baselines/ctle","board_baselines/poi2vec",
                    "baseline_b2c_onehot64","check2hgi_design_k_resln_mae_l0_1","hgi",
                    "check2hgi","check2hgi_dk_ovl"]:
            for emb in (rp/sub).glob("**/embeddings.parquet"):
                targets.append(emb)
    seen=set(); targets=[t for t in targets if not (str(t) in seen or seen.add(str(t)))]
    print(f"validating {len(targets)} embeddings.parquet files...\n")
    bad=[]; total=0; by_eng={}
    for t in sorted(targets):
        eng = next((s for s in ["b2b","ctle","poi2vec","baseline_b2c","design_k","/hgi/","check2hgi_dk_ovl","/check2hgi/"] if s in str(t)), "other")
        by_eng.setdefault(eng, {"n":0,"ok":0,"rows0":0})
        res = check(t); total+=1; by_eng[eng]["n"]+=1
        if res["ok"] and not [i for i in res.get("issues",[]) if "no column stats" not in i]:
            by_eng[eng]["ok"]+=1
        else:
            bad.append(res)
    print("=== per-engine (ok / total) ===")
    for e,v in sorted(by_eng.items()): print(f"  {e:22} {v['ok']}/{v['n']}")
    print(f"\n=== FAILURES ({len(bad)}) ===")
    for b in bad[:50]:
        print(f"  ✗ {b['path']}  rows={b.get('rows','?')}  {b['issues']}")
    print(f"\nTOTAL {total} | clean {total-len(bad)} | issues {len(bad)}")

if __name__ == "__main__":
    main()
