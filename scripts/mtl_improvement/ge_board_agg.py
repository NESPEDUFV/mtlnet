"""Aggregate the GE board (T0.2/T0.3) — v14 vs matched canonical at Georgia.

Reuses the proven metric extraction from scripts/_v14_run/aggregate.py:
  - DIAG  = per-task diagnostic-best epoch (§0.1 convention, selector-independent)
  - JGEOM = geom_simple deployable selector = argmax(cat_macroF1 · reg_Acc@10) (C21 default)
GE uses H3-alt (constant scheduler, min_best_epoch=0 — handled by _min_epoch_for via the
"/georgia/" path not matching "/florida/").

Usage: .venv/bin/python scripts/mtl_improvement/ge_board_agg.py
Reads /tmp/ge_board/manifest.tsv (rows: tag<TAB>seed<TAB>rundir; tag in {v14, canon}).
"""
import importlib.util
import statistics as st
from pathlib import Path

REPO = Path("/home/vitor.oliveira/PoiMtlNet")
spec = importlib.util.spec_from_file_location("agg", REPO / "scripts/_v14_run/aggregate.py")
# aggregate.py runs its report at import; suppress by reading only the funcs we need.
src = (REPO / "scripts/_v14_run/aggregate.py").read_text()
# Execute only up to the `load` definition (cut the module-level report at the v14 = load(...) line).
cut = src.index("\nv14 = load(")
ns = {}
exec(compile(src[:cut], "aggregate_funcs", "exec"), ns)
metrics, load = ns["metrics"], ns["load"]

MAN = "/tmp/ge_board/manifest.tsv"
data = load(MAN)  # keyed by tag: {"v14": {...}, "canon": {...}}


def cell(tag, key):
    xs = data.get(tag, {}).get(key, [])
    if not xs:
        return "  pending "
    return f"{st.mean(xs):5.2f}±{(st.pstdev(xs) if len(xs)>1 else 0.0):4.2f}"


def delta(key):
    v = data.get("v14", {}).get(key, [])
    c = data.get("canon", {}).get(key, [])
    if not v or not c:
        return "  n/a "
    return f"{st.mean(v)-st.mean(c):+6.2f}"


nv = len(data.get("v14", {}).get("seeds", []))
nc = len(data.get("canon", {}).get("seeds", []))
print(f"\nGE board — v14 vs matched canonical (KD off, H3-alt, seeds {data.get('v14',{}).get('seeds')})")
print(f"v14 seeds={nv}  canon seeds={nc}  (n_regions=2283, middle band)")
print("=" * 92)
for basis, rk, ck in [("DIAGNOSTIC-BEST (per-task own-best epoch)", "diag_reg", "diag_cat"),
                      ("JOINT-GEOM-SIMPLE (deployable, C21 default)", "jgeom_reg", "jgeom_cat"),
                      ("JOINT-LEGACY (v11 broken selector, ref)", "joint_reg", "joint_cat")]:
    print(f"\n{basis}")
    print(f"  reg@10: v14 {cell('v14',rk)}  canon {cell('canon',rk)}  Δreg {delta(rk)}")
    print(f"  catF1 : v14 {cell('v14',ck)}  canon {cell('canon',ck)}  Δcat {delta(ck)}")
print("=" * 92)
print("Δ>0 ⇒ v14 beats matched canonical. Reg=top10_acc_indist, Cat=macro-F1.\n")
