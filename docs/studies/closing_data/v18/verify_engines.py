#!/usr/bin/env python
"""Run the charter §6 self-checks over every v18 engine and emit AUDIT.md + data/v18_audit.json.

Fail closed: a silent wrong number is far worse than a crash. Every check reports its MEASURED
value, not just a verdict, so the audit is readable rather than a wall of PASS.

Checks (charter §6):
  2. feature width matches the checkpoint       -> 9 x 64 flat columns, in_channels 15
  3. enrichment actually landed                 -> build.json layout + in_channels
  4. row pairing across arms                    -> ids, labels AND userids, >=95% retention
  5. held-out user encodability                 -> --self-test ran at build/readout time
  +  forward-only graph                         -> edges halved, causal_graph.forward_only
  +  readout equivalence                        -> recorded max abs diff, where measured
  +  engine completeness                        -> the four artifacts a v18 engine needs

Usage:  .venv/bin/python docs/studies/closing_data/v18/verify_engines.py [--write]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[4]
BASE = REPO / "docs/studies/closing_data/v18"
ENG = "check2hgi_v18"
SRC = "check2hgi_dk_ovl"
STATES = ["istanbul", "alabama", "arizona", "florida", "texas", "california"]


def check_state(st: str) -> dict:
    res: dict = {"state": st, "checks": [], "ok": True}

    def add(name: str, ok: bool | None, measured: str) -> None:
        res["checks"].append({"check": name, "ok": ok, "measured": measured})
        if ok is False:
            res["ok"] = False

    d = REPO / "output" / ENG / st
    s = REPO / "output" / SRC / st

    # --- engine completeness: the four artifacts -------------------------------------------
    for rel, kind in (("input/next.parquet", "file"), ("input/next_region.parquet", "file"),
                      ("temp/sequences_next.parquet", "file"),
                      ("region_embeddings.parquet", "symlink")):
        p = d / rel
        if kind == "symlink":
            add(f"engine has {rel}", p.is_symlink(),
                "symlink -> " + (str(Path(p).resolve().parent.parent.name) if p.exists() else "MISSING"))
        else:
            add(f"engine has {rel}", p.exists(),
                f"{p.stat().st_size/2**20:.0f} MiB" if p.exists() else "MISSING")
    if not (d / "input/next.parquet").exists():
        return res

    # --- build manifest: enrichment + forward-only ------------------------------------------
    run = REPO / "results" / ENG / st / "V18" / "build.json"
    if run.exists():
        b = json.loads(run.read_text())
        lay = (b.get("node_enrichment") or {}).get("layout")
        add("node layout", lay == ["canonical_11", "continuous_time_4"], str(lay))
        w = (b.get("node_feature_schema") or {}).get("width")
        add("in_channels == 15", w == 15, str(w))
        cg = b.get("causal_graph") or {}
        add("causal_graph.forward_only", cg.get("forward_only") is True, str(cg.get("forward_only")))
        eb, ea, dr = cg.get("edges_before"), cg.get("edges_after"), cg.get("dropped_backward")
        add("backward edges dropped", (eb is not None and ea == eb - dr and ea * 2 == eb),
            f"{eb} -> {ea} (dropped {dr})")
        add("repr seed / epochs / encoder",
            b.get("repr_seed") == 42 and b.get("epochs") == 500 and b.get("encoder") == "resln",
            f"seed={b.get('repr_seed')} epochs={b.get('epochs')} encoder={b.get('encoder')} "
            f"best_epoch={b.get('best_epoch')}")
    else:
        add("build.json present", False, f"missing at {run}")

    # --- readout provenance + equivalence ----------------------------------------------------
    mj = d / "materialize.json"
    if mj.exists():
        m = json.loads(mj.read_text())
        meth = m.get("method") or (
            f"per-window npz via materialize_engine.py ({Path(m['arm_npz']).name})"
            if m.get("arm_npz") else "unknown")
        add("materialization method", True, meth[:75])
        eq = m.get("equivalence_vs_per_window_npz")
        if eq:
            add("readout equivalence vs per-window npz",
                eq["max_abs_diff"] <= eq.get("tolerance", 1e-4),
                f"max {eq['max_abs_diff']:.3e} (slot8 {eq['slot8_max_abs_diff']:.3e}, "
                f"mean {eq['mean_abs_diff']:.3e}) over {eq['n_windows_compared']} windows")
        else:
            add("readout equivalence vs per-window npz", None,
                "not measured for this state (identity established at alabama/arizona/istanbul "
                "over every window; forward_only guard enforced in code)")
    meta = REPO / "results" / ENG / st / "V18" / "win_matched.npz.meta.json"
    if meta.exists():
        mm = json.loads(meta.read_text())
        add("readout matches training graph", mm.get("readout") == "prefix_forward_only",
            str(mm.get("readout")))
        add("held-out user encodability (--self-test)", mm.get("self_test") is True,
            str(mm.get("self_test")))
    else:
        add("held-out user encodability (--self-test)", None,
            "no per-window npz for this state; F2 verified at the states that ran the readout")

    # --- row pairing + feature width ---------------------------------------------------------
    n_eng = pq.ParquetFile(d / "input/next.parquet").metadata.num_rows
    n_src = pq.ParquetFile(s / "input/next.parquet").metadata.num_rows
    add("retention >= 95% of source windows", n_eng / n_src >= 0.95,
        f"{n_eng}/{n_src} = {n_eng/n_src:.4f}")

    cols = pq.ParquetFile(d / "input/next.parquet").schema_arrow.names
    nf = len([c for c in cols if c.isdigit()])
    add("feature width 9 x 64", nf == 576, f"{nf} = 9 x {nf//9}")

    a = pd.read_parquet(d / "input/next.parquet", columns=["userid", "next_category"])
    r = pd.read_parquet(d / "input/next_region.parquet", columns=["userid"])
    c = pd.read_parquet(s / "input/next.parquet", columns=["userid", "next_category"])
    add("next/next_region userid alignment", a["userid"].equals(r["userid"]),
        f"{len(a)} vs {len(r)} rows")
    add("labels match the source row space", a["next_category"].equals(c["next_category"]),
        "identical" if a["next_category"].equals(c["next_category"]) else "DIFFER")
    add("userids match the source row space", a["userid"].equals(c["userid"]),
        "identical" if a["userid"].equals(c["userid"]) else "DIFFER")
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--states", nargs="*", default=STATES)
    args = ap.parse_args()

    out = []
    for st in args.states:
        if not (REPO / "output" / ENG / st).exists():
            print(f"[skip] {st}: no engine dir yet")
            continue
        r = check_state(st)
        out.append(r)
        print(f"\n=== {st}: {'ALL PASS' if r['ok'] else 'HAS FAILURES'}")
        for c in r["checks"]:
            mark = {True: "PASS", False: "FAIL", None: "n/a "}[c["ok"]]
            print(f"  [{mark}] {c['check']:<42} {c['measured']}")

    if not args.write:
        return

    L = ["# v18 — AUDIT\n",
         "> The charter §6 self-checks, with their **measured values**. Regenerate with "
         "`verify_engines.py --write`.\n",
         f"> Generated {datetime.now(timezone.utc).isoformat()}.\n",
         "Fail closed: a silent wrong number is far worse than a crash. `n/a` marks a check that "
         "does not apply to how this state was materialized, with the reason given.\n"]
    allok = all(r["ok"] for r in out)
    L.append(f"**Overall: {'all states pass' if allok else 'FAILURES PRESENT — see below'}** "
             f"({len(out)} states checked).\n")
    for r in out:
        L.append(f"\n## {r['state']} — {'ALL PASS' if r['ok'] else '**HAS FAILURES**'}\n")
        L.append("| check | verdict | measured |")
        L.append("|---|---|---|")
        for c in r["checks"]:
            mark = {True: "PASS", False: "**FAIL**", None: "n/a"}[c["ok"]]
            L.append(f"| {c['check']} | {mark} | `{c['measured']}` |")
    (BASE / "AUDIT.md").write_text("\n".join(L) + "\n")
    (BASE / "data").mkdir(exist_ok=True)
    (BASE / "data/v18_audit.json").write_text(json.dumps(
        {"generated_utc": datetime.now(timezone.utc).isoformat(), "states": out}, indent=1))
    print(f"\n[verify] wrote AUDIT.md + data/v18_audit.json ({len(out)} states, "
          f"{'all pass' if allok else 'FAILURES'})")


if __name__ == "__main__":
    main()
