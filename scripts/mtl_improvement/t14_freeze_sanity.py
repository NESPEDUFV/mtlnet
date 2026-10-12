#!/usr/bin/env python
"""Freeze-sanity guard for the T1.4 (c)/(d) ceilings (standing guard, re-advisor 2026-06-03).

The original cat-ceiling bug (--cat-head silently dropped on --task next -> ran next_single,
not next_gru) reached a freeze AND passed an advisor because (a) nobody verified the head that
actually ran, and (b) nobody asserted the cross-harness invariant "an STL ceiling must sit >= the
MTL number it bounds." This script encodes both checks so the next silent-flag regression is loud:

  1. ARCH CHECK — read model/arch.txt for each cat-ceiling rundir; assert the head class matches
     the intended head (NextHeadGRU). Catches the next_single-class bug instantly.
  2. ORDERING CHECK — assert each frozen ceiling >= the MTL number it claims to bound:
       (c)-cat  >= MTL deployable cat        (the invariant the bug violated)
       (c)-reg  >= MTL deployable reg
       (d)-reg  >= (c)-reg                    (composite uses the best substrate)
     Diagnostic-best MTL is reported as INFO (it is an oracle per-task epoch + multi-seed, so a
     single-seed deployable ceiling may dip below it within sigma — not a hard bound).

Run: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t14_freeze_sanity.py
Exit 0 if all asserts pass, 1 otherwise.
"""
import json
import sys
from pathlib import Path

MAN = Path("docs/results/mtl_improvement/t14_manifests")

# Frozen (c)/(d) values (the immutable yardstick).
C_CAT = {"alabama": 49.97, "arizona": 51.01, "georgia": 58.12, "florida": 69.97}
C_REG = {"alabama": 62.88, "arizona": 55.11, "georgia": 58.45, "florida": 73.31}
D_REG = {"alabama": 63.58, "arizona": 55.11, "georgia": 58.76, "florida": 73.62}
# MTL deployable (geom_simple) — the numbers the ceilings must bound.
MTL_DEPLOY_CAT = {"alabama": 46.50, "arizona": 48.52, "georgia": 56.13, "florida": 66.73}
MTL_DEPLOY_REG = {"alabama": 50.14, "arizona": 37.78, "georgia": 42.64, "florida": 61.21}
# MTL diagnostic-best (oracle epoch, multi-seed) — INFO only, not a hard bound.
MTL_DIAG_CAT = {"alabama": 46.78, "arizona": 48.75, "georgia": 57.07, "florida": 70.26}

INTENDED_CAT_HEAD = "NextHeadGRU"


def _la05_rundir(state: str):
    man = MAN / f"manifest_catrepin_{state}.tsv"
    if not man.exists():
        return None
    for line in man.read_text().splitlines():
        p = line.split("\t")
        if len(p) >= 4 and p[1] == "g_la05" and p[3] == "ok":
            return p[2]
    return None


def main() -> int:
    fails = []
    print("== ARCH CHECK (cat ceiling must be the intended head) ==")
    for st in C_CAT:
        rd = _la05_rundir(st)
        arch = Path(rd) / "model" / "arch.txt" if rd else None
        head = "MISSING"
        if arch and arch.exists():
            txt = arch.read_text()
            head = next((h for h in ("NextHeadGRU", "NextHeadSingle", "NextHeadLSTM")
                         if h + "(" in txt), txt.split("(", 1)[0].strip()[:24])
        ok = head == INTENDED_CAT_HEAD
        print(f"  {st:<9} head={head:<16} {'OK' if ok else 'FAIL (expected '+INTENDED_CAT_HEAD+')'}")
        if not ok:
            fails.append(f"arch {st}: {head} != {INTENDED_CAT_HEAD}")

    print("\n== ORDERING CHECK (ceiling >= bounded MTL) ==")
    for st in C_CAT:
        for name, ceil, mtl in (
            ("(c)-cat >= MTL_deploy_cat", C_CAT[st], MTL_DEPLOY_CAT[st]),
            ("(c)-reg >= MTL_deploy_reg", C_REG[st], MTL_DEPLOY_REG[st]),
            ("(d)-reg >= (c)-reg",        D_REG[st], C_REG[st]),
        ):
            ok = ceil >= mtl - 1e-6
            print(f"  {st:<9} {name:<28} {ceil:6.2f} vs {mtl:6.2f}  {'OK' if ok else 'FAIL'}")
            if not ok:
                fails.append(f"{st} {name}: {ceil} < {mtl}")

    print("\n== INFO: (c)-cat vs MTL diagnostic-best (oracle epoch, multi-seed — not a hard bound) ==")
    for st in C_CAT:
        d = C_CAT[st] - MTL_DIAG_CAT[st]
        note = "" if d >= 0 else "  <- ceiling below diag-best (seed/metric confound; see TIER01 footnote)"
        print(f"  {st:<9} (c)-cat {C_CAT[st]:.2f} - diag {MTL_DIAG_CAT[st]:.2f} = {d:+.2f}{note}")

    print()
    if fails:
        print("FREEZE SANITY: FAIL\n  - " + "\n  - ".join(fails))
        return 1
    print("FREEZE SANITY: ALL HARD CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
