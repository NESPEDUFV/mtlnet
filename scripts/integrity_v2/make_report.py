"""Assemble the study report from the result JSONs, quoting every number from its file and field.

The project's number protocol forbids computing values in prose, so this script is the only place a
number enters the report, and each one carries the file and field it came from. Nothing here decides
anything: the decision table compares measured values against thresholds that were fixed before the
results were read, and prints which branch each comparison lands in.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------------------------
# Thresholds, fixed before any result of this study was read (plan phases 4-5).
# The two-point margin is the dissertation's own registered non-inferiority margin.
# ---------------------------------------------------------------------------------------------
THRESH = {
    "invariance_rel": 1e-5,
    "material_points": 2.0,
    "detectable_points": 0.5,
    "probe_margin_points": 2.0,
}


def ledger_row(value, unit, source_file: str, field: str, meaning: str) -> dict:
    return {"value": value, "unit": unit, "source_file": source_file, "field": field,
            "meaning": meaning}


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def fmt(v, nd=4):
    return "n/a" if v is None else f"{v:.{nd}f}"


def build(state: str, rr: Path) -> tuple[str, list]:
    f0 = load(rr / "f0_structure.json")
    streams = load(rr / "f0_task_streams.json")
    iv = load(rr / state / "intervention.json")
    pl = load(rr / state / "probe_ladder.json")
    cf = load(rr / state / "counterfactual.json")
    led: list = []
    L: list[str] = []

    S = f0["per_state"][state] if f0 and state in f0.get("per_state", {}) else None
    if S:
        f1, f2, f3, f4, f5 = (S["F1_disjoint_user_paths"], S["F2_heldout_exactness"],
                              S["F3_backward_coefficient"], S["F4_receptive_field"],
                              S["F5_truncation_vs_edge_drop"])
        for v, u, fld, mean in [
            (f1["cross_user_edges"], "edges", "F1_disjoint_user_paths.cross_user_edges",
             "cross-user check-in edges"),
            (f2["max_abs_diff_vs_full_graph"], "abs", "F2_heldout_exactness.max_abs_diff_vs_full_graph",
             "held-out user encoded alone vs inside the full graph"),
            (f3["backward_coef_median"], "coefficient",
             "F3_backward_coefficient.backward_coef_median",
             "GCN-normalized weight of the message from the target into the last observed visit"),
            (f3["self_loop_coef_median"], "coefficient",
             "F3_backward_coefficient.self_loop_coef_median", "the same node's self-loop weight"),
            (f4["slot8_rel_change_median"], "relative", "F4_receptive_field.slot8_rel_change_median",
             "movement of the last observed vector when the target's category is zeroed"),
        ]:
            led.append(ledger_row(v, u, f"f0_structure.json :: per_state.{state}", fld, mean))
        L += [
            "## 1. What the graph makes possible",
            "",
            f"The check-in graph of {state} has "
            f"{f1['cross_user_edges']} edges between different users, and every edge joins visits "
            f"that are adjacent in time for one user. The graph is therefore a disjoint union of "
            f"per-user paths, and two consequences follow that shape the rest of this study.",
            "",
            f"First, a user who was absent from representation training can still be encoded "
            f"exactly. Encoding {f2['n_users_encoded_alone']} held-out users alone reproduced their "
            f"vectors from the full-graph pass to within {f2['max_abs_diff_vs_full_graph']:.1e}. "
            f"The earlier audit could not do this and substituted one vector per place, keeping only "
            f"the windows whose places appeared in training; that substitution is no longer needed.",
            "",
            f"Second, the path from the target visit into the history is short and not weak. Under "
            f"two graph convolution layers the target reaches history slots "
            f"{f4['history_slots_reached_by_target']} and no others. The message from the target "
            f"into the last observed visit carries a normalized weight whose median is "
            f"{f3['backward_coef_median']:.4f}, against {f3['self_loop_coef_median']:.4f} for that "
            f"visit's own self-loop.",
            "",
        ]
        pref = f5["R_prefix_cut_at_target"]; fwd = f5["R_fwd_backward_edges_dropped"]
        wind = f5["R_window_nine_nodes_only"]
        L += [
            "### 1.1 Which strict readout to use",
            "",
            "Three ways to withhold the future were measured on the same windows. Cutting the "
            "user's path at the target moves only the slots the removed node can reach: the "
            "fraction of windows in which each slot changes, from the first to the last, is "
            + ", ".join(f"{v:.2f}" for v in pref["per_slot_frac_windows_moved"]) + ". "
            "Keeping only the nine observed visits also deletes the user's earlier history, which "
            f"moves the first slot in {wind['per_slot_frac_windows_moved'][0]:.2f} of windows for a "
            "reason unrelated to the leak. Dropping backward edges across the whole path "
            "recomputes every node's degree normalization and moves every slot "
            f"({fwd['mean_frac_slots_moved']:.2f} of slot-window pairs). The study therefore uses "
            "the cut at the target as its strict readout, and reports the edge-dropping variant "
            "only as a diagnostic.",
            "",
        ]
        for lbl, key in (("prefix", "R_prefix_cut_at_target"),
                         ("window", "R_window_nine_nodes_only"),
                         ("edge_drop", "R_fwd_backward_edges_dropped")):
            led.append(ledger_row(f5[key]["mean_frac_slots_moved"], "fraction",
                                  f"f0_structure.json :: per_state.{state}",
                                  f"F5_truncation_vs_edge_drop.{key}.mean_frac_slots_moved",
                                  f"share of slot-window pairs moved by the {lbl} readout"))

    if streams:
        L += ["## 2. Which task each channel can reach", "",
              "The category stream " + streams["consequence"]["category_stream"]
              .split("consumes", 1)[1].join(["consumes", ""]).rstrip() + ".", "",
              "The region stream " + streams["consequence"]["region_stream"], "",
              "Consequently, " + streams["consequence"]["design_implication"], ""]

    if iv:
        L += ["## 3. Dependence is not carriage", "",
              "A random-weight encoder of the same architecture already moves the last observed "
              "vector when the target's category changes, so movement alone establishes nothing. "
              "Two quantities are therefore separated: how far the vector moves, and whether the "
              "movement encodes which category the target was.", "",
              "Read the unconditional median with care. About half of all windows have a "
              "near-zero temporal edge weight to their target, which is what a long gap between "
              "two visits produces, and those windows cannot move at all. The unconditional "
              "median therefore describes the gap, not the channel; the column that answers the "
              "question is the movement among windows that do move.", "",
              "| arm | windows | share of windows that move | movement, all windows (median) | "
              "movement among those that move | separability by substituted category | "
              "shuffled-label floor |",
              "|---|---:|---:|---:|---:|---:|---:|"]
        for label, a in iv["arms"].items():
            car = a.get("carriage", {})
            zc = a["zero_cat"]
            L.append(f"| {label} | {a['n_windows']} | "
                     f"{zc['frac_windows_moved']:.4f} | "
                     f"{zc['rel_linf_median']:.4f} | "
                     f"{zc['rel_linf_median_among_moved']:.4f} | "
                     f"{car.get('fisher_ratio_by_substituted_class', float('nan')):.4f} | "
                     f"{car.get('fisher_ratio_shuffled_labels_control', float('nan')):.4f} |")
            led += [
                ledger_row(zc["frac_windows_moved"], "fraction", f"{state}/intervention.json",
                           f"arms.{label}.zero_cat.frac_windows_moved",
                           "share of windows whose last observed vector moves when the target "
                           "category is zeroed"),
                ledger_row(zc["rel_linf_median_among_moved"], "relative",
                           f"{state}/intervention.json",
                           f"arms.{label}.zero_cat.rel_linf_median_among_moved",
                           "movement among windows that move (the unconditional median is "
                           "dominated by windows with a near-zero edge weight to the target)"),
                ledger_row(car.get("fisher_ratio_by_substituted_class"), "ratio",
                           f"{state}/intervention.json",
                           f"arms.{label}.carriage.fisher_ratio_by_substituted_class",
                           "separability of the history vector by which category was substituted"),
                ledger_row(car.get("fisher_ratio_shuffled_labels_control"), "ratio",
                           f"{state}/intervention.json",
                           f"arms.{label}.carriage.fisher_ratio_shuffled_labels_control",
                           "the same statistic with labels shuffled: the floor it must beat"),
            ]
        L.append("")

    if pl:
        L += ["## 4. What a probe can decode from one history vector", "",
              "The question here is narrow: given ONE vector, the representation of the last visit a "
              "model is allowed to see, can a classifier read off the category of the NEXT visit? "
              "Every row is a different representation of that same vector, scored on the same "
              "windows with the same labels, so the rows are directly comparable to each other.",
              "",
              "How to read the columns. `linear` and `nonlinear` are the two probes; the verdict "
              "follows the stronger one. The next three columns are the reference points a value "
              "must be judged against, not competitors: `nine-position label history` is a probe "
              "given ONLY the nine observed category labels and no embedding at all, which is the "
              "benchmark that matters, because a representation that cannot beat it adds nothing "
              "over counting what the user already did; `majority floor` is always predicting the "
              "commonest class; `shuffled-label floor` is the same probe on randomized labels, so it "
              "is the value that means no information. The last column is the smallest artificially "
              "injected signal this probe could detect, which bounds what a null result here can "
              "exclude.", "",
              "The arms: `reported` is the configuration the dissertation used. `strict_prefix` is "
              "the same weights with the target visit removed from the graph. `trainonly` trained "
              "the representation without the validation users. `attention_control` is a "
              "graph-attention encoder included as a positive control. Arms ending in `_prefix` "
              "combine their training condition with the target removed.", "",
              "| arm | windows | linear | nonlinear | nine-position label history | majority floor "
              "| shuffled-label floor | smallest detectable injection |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for label, a in pl["arms"].items():
            lo = a["label_only_baselines"]; s8 = a["slot8"]
            L.append(f"| {label} | {a['n_windows']} | {s8['linear']['mean']:.4f} | "
                     f"{s8['mlp']['mean']:.4f} | "
                     f"{lo['nine_position_category_history']['mean']:.4f} | "
                     f"{lo['majority_class']:.4f} | "
                     f"{s8['label_shuffled_floor']['mean']:.4f} | "
                     f"{a['calibration_slot8']['min_detectable_epsilon']} |")
            led.append(ledger_row(s8["mlp"]["mean"], "macro-F1", f"{state}/probe_ladder.json",
                                  f"arms.{label}.slot8.mlp.mean",
                                  "nonlinear probe on the last observed vector"))
            led.append(ledger_row(a["calibration_slot8"]["min_detectable_epsilon"], "epsilon",
                                  f"{state}/probe_ladder.json",
                                  f"arms.{label}.calibration_slot8.min_detectable_epsilon",
                                  "smallest injected signal this probe detects"))
        L += ["", "Every probe split is user-disjoint and every value is the mean over "
              f"{pl['protocol']['probe_seeds']} classifier seeds.", ""]

    if cf:
        L += ["## 5. What the predictor's own metric does", "",
              "**What is compared here.** Each row is the same trained-from-scratch category "
              "predictor fed a DIFFERENT representation of the same validation windows, with the "
              "same labels. The comparison is always row-against-the-reported-row, and the `drop` "
              "columns are that difference in macro-F1 points. A positive drop means the arm is "
              "WORSE than the reported configuration.", "",
              "**These absolute values are not the dissertation's.** The head here is this study's "
              "own small model at one fold, not the tuned `next_gru` at n=20, so the reported row "
              "will not match Chapter 5's table. Only the differences between rows carry, and only "
              "within this table.", "",
              f"The dedicated category model is trained on the reported representation "
              f"({fmt(cf['intact']['mean_macro_f1'])} macro-F1 over "
              f"{len(cf['intact']['per_seed_macro_f1'])} seeds) and then each arm is evaluated in "
              "two regimes. Transfer keeps those frozen weights, so it bounds how much the fitted "
              "predictor leans on the target. Matched retrains on the arm's own representation, "
              "which is the contrast that answers what the reported number becomes under a "
              "protocol that never sees the future.", "",
              "| arm | transfer macro-F1 | transfer drop | matched macro-F1 | matched drop | "
              "matched 95% CI |", "|---|---:|---:|---:|---:|---:|"]
        led.append(ledger_row(cf["intact"]["mean_macro_f1"], "macro-F1",
                              f"{state}/counterfactual.json", "intact.mean_macro_f1",
                              "the reported representation"))
        for label, a in cf["arms"].items():
            t = a["transfer"]; m = a.get("matched")
            L.append(f"| {label} | {t['mean_macro_f1']:.4f} | {t['drop_points']:+.2f} | "
                     f"{fmt(m['mean_macro_f1']) if m else 'n/a'} | "
                     f"{('%+.2f' % m['drop_points']) if m else 'n/a'} | "
                     f"{('%+.2f to %+.2f' % tuple(m['bootstrap_ci95_points'])) if m else 'n/a'} |")
            if m:
                led.append(ledger_row(m["drop_points"], "macro-F1 points",
                                      f"{state}/counterfactual.json",
                                      f"arms.{label}.matched.drop_points",
                                      f"change from the reported representation, {label}, retrained"))
        L.append("")

    return "\n".join(L), led


def causal_section(state: str, rr: Path) -> list[str]:
    """The arm that separates a leak from learned structure.

    Every other arm reads causally from weights trained on a bidirectional graph, which penalises
    the representation for a train/deploy mismatch on top of any leak. This cell trains forward-only,
    so the comparison against the label-only benchmark is finally like for like.
    """
    pc = load(rr / state / "probe_causal.json")
    cc = load(rr / state / "counterfactual_causal.json")
    if not pc:
        return []
    L = ["## 6. Is the loss a leak, or a train-and-deploy mismatch?", "",
         "An objection worth taking seriously: the encoder is supposed to learn transition "
         "structure, and withholding the target at readout from weights that were trained with it "
         "present measures a mismatch between training and deployment as much as it measures a "
         "leak. The arm below removes that objection. It trains the representation on a "
         "forward-only graph, so no visit sees its own future at any point, in training or at "
         "readout. If the check-in-level representation carries transferable structure, this arm "
         "should beat the label-only benchmark.", ""]
    hist = pc["arms"][next(iter(pc["arms"]))]["label_only_baselines"][
        "nine_position_category_history"]["mean"]
    L += ["**What is compared.** Every row is the same probe on the same windows; the rows differ "
          "only in which edges existed when the representation was built (`training graph`) and "
          "which existed when the vectors were read out (`readout`). The last column is the "
          "difference against the label-only benchmark, so a NEGATIVE value means the embedding is "
          "worse than simply counting the nine observed category labels.", "",
          "| arm | training graph | readout | nonlinear probe | vs label-only benchmark |",
          "|---|---|---|---:|---:|"]
    labels = {
        "reported": ("bidirectional", "target present, both directions"),
        "strict_readout_biTrained": ("bidirectional", "path cut at target"),
        "causal_C1_matched": ("forward-only", "cut at target AND forward-only (matched)"),
        "causal_C1_mismatched": ("forward-only", "cut at target only (deliberate mismatch)"),
    }
    for k, a in pc["arms"].items():
        tg, ro = labels.get(k, ("?", "?"))
        v = a["slot8"]["mlp"]["mean"]
        L.append(f"| {k} | {tg} | {ro} | {v:.4f} | {100*(v-hist):+.2f} |")
    L += ["", f"The label-only benchmark is {hist:.4f}, a linear probe on the nine observed "
          "category labels and nothing else.", ""]
    if cc:
        L += ["In the predictor's own metric:", "",
              "| arm | matched macro-F1 | change from reported | 95% CI |", "|---|---:|---:|---:|"]
        L.append(f"| reported | {cc['intact']['mean_macro_f1']:.4f} | reference | |")
        for k, a in cc["arms"].items():
            m = a.get("matched")
            if m:
                lo, hi = m["bootstrap_ci95_points"]
                L.append(f"| {k} | {m['mean_macro_f1']:.4f} | {m['drop_points']:+.2f} | "
                         f"{lo:+.2f} to {hi:+.2f} |")
        L.append("")
    return L


def gates(state: str, rr: Path) -> list[str]:
    """Report which pre-registered branch each measurement lands in. No thresholds are chosen here."""
    out = ["## 7. The pre-registered comparisons", "",
           f"Thresholds fixed before results were read: a change of at least "
           f"{THRESH['material_points']} macro-F1 points is material (the dissertation's own "
           f"registered margin); {THRESH['detectable_points']} to {THRESH['material_points']} "
           f"points is detectable but below that margin; invariance means a relative change at or "
           f"below {THRESH['invariance_rel']:.0e}.", ""]
    cf = load(rr / state / "counterfactual.json")
    if not cf:
        return out + ["_counterfactual results not present_", ""]
    out += ["| comparison | measured | pre-registered branch |", "|---|---:|---|"]
    for label, a in cf["arms"].items():
        m = a.get("matched")
        if not m:
            continue
        d = abs(m["drop_points"])
        branch = ("material" if d >= THRESH["material_points"] else
                  "detectable, below the margin" if d >= THRESH["detectable_points"] else
                  "no material effect detected")
        if label.startswith("placebo_far_future"):
            branch += " (this arm must show no effect; a nonzero value indicts the pipeline)"
        out.append(f"| {label} | {m['drop_points']:+.2f} points | {branch} |")
    out.append("")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--states", nargs="+", default=["alabama", "florida"])
    ap.add_argument("--results-root", default="docs/results/check2hgi_integrity_v2")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rr = REPO / args.results_root

    parts = ["# Links between consecutive visits: a causal audit of the check-in representation",
             "", "_Internal scientific record. Repository paths and operational names appear here "
             "and must not appear in dissertation prose._", ""]
    ledger: list = []
    for st in args.states:
        body, led = build(st, rr)
        if not body.strip():
            continue
        parts += [f"# {st.capitalize()}", "", body] + causal_section(st, rr) + gates(st, rr)
        ledger += [{**r, "state": st} for r in led]

    parts += ["# Numbers ledger", "",
              "| value | unit | file | field | meaning | dataset |", "|---:|---|---|---|---|---|"]
    for r in ledger:
        parts.append(f"| {r['value']} | {r['unit']} | `{r['source_file']}` | `{r['field']}` | "
                     f"{r['meaning']} | {r['state']} |")
    outp = REPO / args.out
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text("\n".join(parts) + "\n")
    print(f"[report] wrote {outp} ({len(ledger)} ledger rows)")


if __name__ == "__main__":
    main()
