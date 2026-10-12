# Chapter 6 — claim and number ledger (draft 1, 2026-07-23)

> The Conclusion cites no external literature (synthesis chapter, like §2.5); every number is an
> internal result and must trace to its source of truth. This ledger is that trace. Fail-closed:
> before compile, each number below is re-verified against the named source.

## Numbers and their sources

| Number in the draft | Source of truth | Convention / note |
|---|---|---|
| CoUrb category gain "+20.2 to 22.0 percentage points across the three states tested" | NORTH_STAR §2 table (audited means, `slides/judge_feedback.md`) | AUDITED values, not the paper's published text (the .tex says 16/21; the audit recounted 15/21 strict + 1 tie; the chapter uses the audited pp-gains, per NORTH_STAR §4 Ch.4 errata rule) |
| Category joint gain "+5.3 to 9.4 macro-F1 points, all six datasets" | NORTH_STAR §2 table / MobiWac §8; per-state values in CEILINGS_N20_FINAL.md | n=20, macro-F1, f1-best epoch convention |
| Region verbs "outperforms at four of six (Istanbul, Florida, California, Texas); non-inferior TOST ±2pp at Alabama, Arizona" | NORTH_STAR §1/§2; MobiWac §8 | verbs bound: outperforms = paired superiority (Holm); matches = TOST within 2pp; AL/AZ NEVER upgraded |
| Freeze control "gain survives at Alabama, Arizona, Florida" | MobiWac `06_results.tex` L92–94 | in-paper finding; three named datasets; "stronger shared trunk, not the region task teaching the category one" |
| Capacity baseline: joint ~4.2M vs dedicated 0.6M (cat, AL); best wide arm 56.16 (n=20); ceiling 56.82; joint 64.54 | storyline/audit/capacity_baseline_experiment.md §5.1–5.3 (param audit + A40 jobs c0cc0edd/d38a1382); raw JSONs in artifact al_capmatch_summary.json | POST-SUBMISSION frame analysis — the draft SAYS so in the text ("run after the Chapter 5 manuscript was submitted"). 56.82 ±0.03 = CEILINGS_N20_FINAL.md; 0.6M = 644,359 (param audit) |
| California partial "fifteen of twenty repetitions, same direction" | experiment_design.md §5.4 (job 4cff4b00, first arm, seeds 0/1/7) | explicitly marked partial in the text ("at the time of writing"); REPLACE with the final n=20 best-arm value + full verdict when the job completes |
| Gradient cosine "+0.001, four seeds, three of six datasets, earlier data preparation, directional only, this pair not a general rule" | MobiWac `02_related.tex` (full scope verbatim, per N3 signed-off beat) | the FULL scope travels with the number, always |
| "twenty repetitions per configuration" | DATA_SPLITS.md / MobiWac §5 | n = 4 seeds × 5 folds |
| Gowalla vintage "2009 and 2010" | DATASETS.md / MobiWac §5 | |
| "seven top-level classes" | GLOSSARY / TASKS.md | |

## Signed-off beats rendered (and where)

- **Per-chapter contribution paragraphs** (§6.1) → beat 1–2 of the Ch.6 spine.
- **Consolidated answer with bound verbs** (§6.2) → category "outperforms everywhere"; region
  "outperforms or matches"; AL/AZ non-inferiority named with TOST.
- **N3 mechanism beats** (§6.2, two paragraphs): freeze control with its three named datasets;
  "sharing stopped hurting"; cosine number with FULL scope; NO parameter-count credit (the
  capacity paragraph explicitly denies it: "Parameter count alone ... buys nothing here"); no
  "knowledge gate" vocabulary; cross-attention named as sharing-by-exchange with private spatial
  path.
- **D1 licensing contract honored** (§6.2): capacity-matched baseline reported as post-submission
  frame analysis; never presented as a Ch.5 result; reading (i) stated with its scope (AL full,
  CA partial). Prominence = one paragraph; the author may shrink it to a sentence but not remove
  it (suppression bar, AGENT_GUARDRAILS §7).
- **Task-pair confound concession** (§6.3 limitation 6) → the signed-off storyline/02 §3.4 text,
  tied 1:1 to its future-work item (§6.4, fixed-pair ablation).
- **Time-indexing** (§6.1): CBIC conclusion "held for the configuration of its time"; CoUrb
  "at that stage of the research".
- **F3 cost guard**: no compute-savings claim anywhere; the joint model's larger size appears as
  disclosed context in §6.2; final remarks say "one deployable model / single forward pass"
  (operational), not "cheaper".
- **Honest-arc close** (§6.5): negative result as the contribution's first half.

## What must change before this draft is final

1. **California completion**: replace the partial sentence with the final verdict (job 4cff4b00).
2. **MobiWac status**: if a decision arrives before the defense build, update "reported in
   Chapter 5" framing and the under-review wording here and in Ch.1.
3. **Author decision**: prominence of the capacity-baseline paragraph (keep / shrink to one
   sentence). Marked in the .tex header.
4. **Fact gate**: run the number re-verification pass (persona 05/06/07) against the sources in
   the table above before compile.