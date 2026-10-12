"""Aggregate T1.3 encoder-isolation probe — decompose the §6.4 residual.

Reads the 9 p1_region_head_ablation JSONs (3 configs × AL/AZ/FL, 5f×50ep seed42, v14
region-emb) and reports reg Acc@10 per config + the gap each pre-processing step opens
vs the raw STAN ceiling (cfg1):
  cfg1_raw      = STL next_stan_flow on raw v14 region emb  (the STL ceiling)
  cfg2_mtlenc   = + MTL next_encoder prepended (64->256 Linear+ReLU+LN+Drop)  → isolates suspect (i)
  cfg3_inputln  = + input LayerNorm only (identity-ish control)
Gate: cfg2 << cfg1 (toward the MTL floor) ⇒ the upstream encoder owns the residual ⇒
re-scope T2.1 to encoder-bypass first; cfg2 ≈ cfg1 ⇒ residual is the shared-backbone handoff
⇒ dual-tower justified at full scope.

Usage: .venv/bin/python scripts/mtl_improvement/t13_agg.py
"""
import json
from pathlib import Path

REPO = Path("/home/vitor.oliveira/PoiMtlNet")
RES = REPO / "docs/results/P1"
STATES = ["alabama", "arizona", "florida"]
CFGS = [("cfg1_raw", "raw STAN (ceiling)"),
        ("cfg2_mtlenc", "+MTL next_encoder"),
        ("cfg3_inputln", "+input LN")]


def acc10(state, cfg):
    p = RES / f"region_head_{state}_region_5f_50ep_t13_{cfg}_v14_s42.json"
    if not p.exists():
        return None
    d = json.load(open(p))
    h = d["heads"]["next_stan_flow"]["aggregate"]
    return h["top10_acc_mean"] * 100, h.get("top10_acc_std", 0.0) * 100


print("\nT1.3 — Encoder-isolation probe (reg Acc@10 %, v14 region-emb, 5f×50ep seed42)")
print("=" * 78)
hdr = f"{'state':9} | " + " | ".join(f"{name:>20}" for _, name in CFGS)
print(hdr); print("-" * len(hdr))
for s in STATES:
    cells = []
    vals = {}
    for cfg, _ in CFGS:
        a = acc10(s, cfg)
        vals[cfg] = a[0] if a else None
        cells.append(f"{a[0]:5.2f}±{a[1]:4.2f}" if a else "  pending ")
    print(f"{s:9} | " + " | ".join(f"{c:>20}" for c in cells))
    if vals["cfg1_raw"] is not None:
        for cfg, name in CFGS[1:]:
            if vals[cfg] is not None:
                d = vals["cfg1_raw"] - vals[cfg]
                print(f"{'':9}   gap opened by {name:>18}: {d:+6.2f}pp"
                      + ("  (LARGE → suspect owns residual)" if d >= 3 else "  (small → not the culprit)"))
print("=" * 78)
print("Decision: cfg2≪cfg1 ⇒ encoder owns the residual (cheap encoder-bypass fix);")
print("          cfg2≈cfg1 ⇒ residual is the shared-backbone handoff ⇒ dual-tower (T2.1).\n")
