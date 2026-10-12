#!/usr/bin/env python3
"""Majority-class-floor macro-F1 per Ch. 5 dataset, from the published Majority (%) column.

Closed form for a classifier that always predicts the majority class m (Food, in every Ch. 5
dataset) over C=7 categories, on a test set where m occurs with frequency p:
  Recall_m = 1, Precision_m = p  =>  F1_m = 2p / (1+p)
  every other class: Recall = 0  =>  F1 = 0
  macro-F1 = F1_m / C = 2p / (C * (1+p))

Input (p, as Majority %) is quoted verbatim from src/tables/mobiwac/datasets.tex:30-35
(Table 8, "Majority (%)" column) -- not recomputed from raw data. See
MAJORITY_CLASS_FLOOR_PER_STATE.md for full provenance and caveats (in particular the Istanbul
precision caveat noted in that table's own hidden comment).

Run: python3 majority_class_floor.py
"""

C = 7

MAJORITY_PCT = {
    "FL": 24.7,
    "TX": 31.0,
    "CA": 32.7,
    "Istanbul": 33.4,
    "AZ": 34.0,
    "AL": 34.2,
}


def majority_floor_macro_f1(majority_pct):
    p = majority_pct / 100.0
    return 100.0 * (2 * p) / (C * (1 + p))


def main():
    rows = sorted(MAJORITY_PCT.items(), key=lambda kv: kv[1])
    print(f"{'Dataset':<10}{'Majority (%)':>14}{'Majority-floor macro-F1 (%)':>30}")
    for state, pct in rows:
        f1 = majority_floor_macro_f1(pct)
        print(f"{state:<10}{pct:>14.1f}{f1:>30.2f}")


if __name__ == "__main__":
    main()
