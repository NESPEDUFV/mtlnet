"""Lane 1 scorer — read champion-G arm captures and compute the same-code A/B deltas.

Gate metrics (diagnostic per-task-best, selector-independent — ref_mtl_metric_field):
  cat = per_metric_best['next_category']['f1']         (macro-F1; board cat metric)
  reg = per_metric_best['next_region']['top10_acc_indist']  (Acc@10; board reg metric)

Δ = treatment − baseline, per head, per state. ≥0.3 pp either head → v17 candidate → STOP for user.

Usage:
    python scripts/pre_freeze_gates/lane1_score.py            # all captures under results/lane1_g01
    python scripts/pre_freeze_gates/lane1_score.py --gate 0.3
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPROOT = ROOT / "results" / "lane1_g01"


def read_arm(cap: Path):
    fs = cap / "full_summary.json"
    if not fs.exists():
        return None
    s = json.loads(fs.read_text())
    pmb = s.get("per_metric_best", {})
    cat = pmb.get("next_category", {}).get("f1", {})
    reg = pmb.get("next_region", {}).get("top10_acc_indist", {})
    g = lambda d: (d.get("mean") if isinstance(d, dict) else d)
    return {"cat_f1": g(cat), "reg_acc10": g(reg)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", type=float, default=0.3, help="pp threshold (either head) → STOP")
    args = ap.parse_args()

    # group captures: {state_seed: {arm: metrics}}
    arms = {}
    for cap in sorted(CAPROOT.glob("*__*")):
        if not cap.is_dir():
            continue
        key, _, arm = cap.name.partition("__")
        m = read_arm(cap)
        arms.setdefault(key, {})[arm] = m

    fired = []
    for key, byarm in sorted(arms.items()):
        base = byarm.get("baseline")
        print(f"\n=== {key} ===")
        if not base or base["cat_f1"] is None:
            print("  baseline: MISSING/incomplete");
        else:
            print(f"  baseline      cat-F1={base['cat_f1']*100:.2f}  reg@10={base['reg_acc10']*100:.2f}")
        for arm, m in sorted(byarm.items()):
            if arm == "baseline":
                continue
            if m is None or m["cat_f1"] is None:
                print(f"  {arm:12} : incomplete (no full_summary yet)"); continue
            if not base or base["cat_f1"] is None:
                print(f"  {arm:12} cat-F1={m['cat_f1']*100:.2f}  reg@10={m['reg_acc10']*100:.2f}  (no baseline to diff)"); continue
            dcat = (m["cat_f1"] - base["cat_f1"]) * 100
            dreg = (m["reg_acc10"] - base["reg_acc10"]) * 100
            hit = "  <<< ≥gate" if (abs(dcat) >= args.gate or abs(dreg) >= args.gate) else ""
            print(f"  {arm:12} cat-F1={m['cat_f1']*100:.2f} (Δ{dcat:+.2f})  reg@10={m['reg_acc10']*100:.2f} (Δ{dreg:+.2f}){hit}")
            if dcat >= args.gate or dreg >= args.gate:
                fired.append((key, arm, dcat, dreg))

    print("\n" + "=" * 56)
    if fired:
        print(f"GATE FIRED (≥{args.gate} pp, positive) — STOP for user (v17 candidate):")
        for key, arm, dcat, dreg in fired:
            print(f"  {key} {arm}: Δcat={dcat:+.2f} Δreg={dreg:+.2f}")
    else:
        print(f"No arm ≥+{args.gate} pp either head on captured runs → trending NULL (exclude on record).")


if __name__ == "__main__":
    main()
