#!/usr/bin/env python3
"""Rewrite the per-fold results table in TX_CELL.md from a h100_matched_score.json.

Usage: python update_tx_cell.py <score_json> <tx_cell_md>
Replaces the region between <!--TXTABLE_START--> and <!--TXTABLE_END--> markers.
"""
import json
import sys

score_json, doc = sys.argv[1], sys.argv[2]
d = json.load(open(score_json))
cat = d["cat_per_fold"]; cep = d["cat_best_epochs"]
reg = d["reg_per_fold"]; rep = d["reg_best_epochs"]
n = d["n_folds"]

rows = ["| fold | cat macro-F1 | cat best-ep | reg FULL top10 | reg best-ep |",
        "|---|---|---|---|---|"]
for i in range(n):
    rows.append(f"| fold{i+1} | {cat[i]:.4f} | {cep[i]} | {reg[i]:.4f} | {rep[i]} |")
mean = (f"\n**Running mean (n={n}):** cat **{d['cat_macro_f1_mean']:.4f}** "
        f"±{d['cat_macro_f1_std']:.4f} | reg **{d['reg_full_top10_mean']:.4f}** "
        f"±{d['reg_full_top10_std']:.4f}")
block = "<!--TXTABLE_START-->\n" + "\n".join(rows) + "\n" + mean + "\n<!--TXTABLE_END-->"

txt = open(doc).read()
a = txt.index("<!--TXTABLE_START-->")
b = txt.index("<!--TXTABLE_END-->") + len("<!--TXTABLE_END-->")
open(doc, "w").write(txt[:a] + block + txt[b:])
print(f"updated {doc}: n={n} cat={d['cat_macro_f1_mean']:.2f} reg={d['reg_full_top10_mean']:.2f}")
