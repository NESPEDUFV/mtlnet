"""Collect L2 (STL next-cat) + L3 (MTL) metrics from results/ into a summary.

Run dirs aren't self-describing (config.json absent under --no-checkpoints), so
we use the deterministic driver order: per (engine,state), `next_*` dirs are STL
next-cat; for check2hgi there are two (earlier-timestamp=gru, later=single per the
driver's gru-then-single ordering), every other engine has one (gru). `mtlnet_*`
is the L3 MTL run. Metrics come from summary/full_summary.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
RESULTS = _root / "results"
ENGINES = ["hgi", "check2hgi", "check2hgi_design_b", "check2hgi_resln", "check2hgi_resln_design_b"]
STATES = ["florida", "alabama", "arizona"]
TAGS = ("ep50_20260531_2", "ep50_20260601")  # the sweep + the June-1 HGI AL/AZ top-up


def _runs(base: Path, prefix: str):
    """All run dirs for `prefix` from this study's date tags, sorted by name (=timestamp)."""
    out = [p for p in base.glob(f"{prefix}_*") if any(t in p.name for t in TAGS)]
    return sorted(out, key=lambda p: p.name)


def _summary(run_dir: Path):
    f = run_dir / "summary" / "full_summary.json"
    return json.load(open(f)) if f.exists() else None


def _m(d, *path):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return None
        d = d[p]
    if isinstance(d, dict) and "mean" in d:
        return d["mean"]
    return d


def main():
    stl, mtl, ladder = [], [], []
    for eng in ENGINES:
        for st in STATES:
            base = RESULTS / eng / st
            if not base.exists():
                continue
            nexts = _runs(base, "next")  # name carries timestamp
            mtls = _runs(base, "mtlnet")
            # STL next-cat: gru = earliest; single (check2hgi only) = latest
            if nexts:
                gru = _summary(nexts[0])
                if gru:
                    stl.append((eng, st, "next_gru",
                                _m(gru, "next", "f1"), _m(gru, "next", "accuracy")))
                if eng == "check2hgi" and len(nexts) > 1:
                    sg = _summary(nexts[-1])
                    if sg:
                        ladder.append((st, "next_gru", _m(gru, "next", "f1"), _m(gru, "next", "accuracy")))
                        ladder.append((st, "next_single", _m(sg, "next", "f1"), _m(sg, "next", "accuracy")))
            # L3 MTL
            if mtls:
                d = _summary(mtls[-1])
                if d:
                    mtl.append((eng, st,
                                _m(d, "next_category", "f1"), _m(d, "next_category", "accuracy"),
                                _m(d, "next_region", "accuracy"), _m(d, "next_region", "top5_acc"),
                                _m(d, "next_region", "top10_acc_indist")))

    def fmt(x): return f"{x:.4f}" if isinstance(x, (int, float)) else "—"

    out = ["# L2 / L3 collected metrics (seed 42; sweep 20260531)\n"]
    out.append("\n## L2 — STL next-cat (next_gru), macro-F1 / accuracy\n")
    out.append("| engine | " + " | ".join(STATES) + " |")
    out.append("| --- |" + " --- |" * len(STATES))
    for eng in ENGINES:
        cells = []
        for st in STATES:
            r = [x for x in stl if x[0] == eng and x[1] == st]
            cells.append(f"{fmt(r[0][3])} / {fmt(r[0][4])}" if r else "—")
        out.append(f"| {eng} | " + " | ".join(cells) + " |")

    out.append("\n## L2 — capacity ladder (check2hgi: next_gru vs next_single), F1 / acc\n")
    out.append("| state | next_gru | next_single |")
    out.append("| --- | --- | --- |")
    for st in STATES:
        g = [x for x in ladder if x[0] == st and x[1] == "next_gru"]
        s = [x for x in ladder if x[0] == st and x[1] == "next_single"]
        gc = f"{fmt(g[0][2])} / {fmt(g[0][3])}" if g else "—"
        sc = f"{fmt(s[0][2])} / {fmt(s[0][3])}" if s else "—"
        out.append(f"| {st} | {gc} | {sc} |")

    out.append("\n## L3 — MTL check2hgi_next_region (family only)\n")
    out.append("| engine | state | cat F1 | cat acc | reg acc | reg top5 | reg top10(indist) |")
    out.append("| --- | --- | --- | --- | --- | --- | --- |")
    for eng in ENGINES:
        for st in STATES:
            r = [x for x in mtl if x[0] == eng and x[1] == st]
            if r:
                _, _, cf, ca, ra, r5, r10 = r[0]
                out.append(f"| {eng} | {st} | {fmt(cf)} | {fmt(ca)} | {fmt(ra)} | {fmt(r5)} | {fmt(r10)} |")

    text = "\n".join(out) + "\n"
    dest = _root / "docs/results/embedding_eval/l2l3/summary.md"
    dest.write_text(text)
    print(text)
    print(f"[written] {dest}")


if __name__ == "__main__":
    main()
