# Proposed errata rows — Chapter 5 (MobiWac 2026), claim-scoping round

> **Written 2026-07-26 by the Ch.5 claim-scoping/layout track.** The orchestrator applies these to
> `src/chapters/apx_b_errata.tex`; this track does not write that file. The four items below are
> changes to REPRODUCED prose in `src/chapters/5_mobiwac.tex` (version of record: the EDAS
> submission, under review). Layout items B1/B2/B3 are mechanical and carry no errata row.
>
> Appendix B currently gives the MobiWac article a **prose section** (`apx_b_errata.tex:175-194`),
> not a table: one content correction (B.1, the CBIC misattribution) plus a sentence listing three
> marked additions. Two shapes are offered below; pick one, do not apply both.
>
> **Precedent for the shape:** Table B.2 (`apx_b_errata.tex:101-129`) records eight wording
> substitutions in reproduced CBIC prose under the banner "writing-rule conformance; claim strength
> unchanged". These four are **not** that banner. Three of them change claim SCOPE (A1, A2, A4) and
> one changes the comparison BASIS of a reported number (A3), so they need their own banner:
> *claim-scope narrowing and comparison-basis disclosure; no experimental result altered*.

---

## Option 1 (recommended) — a new table in the MobiWac section

Insert after the existing prose paragraph at `apx_b_errata.tex:194`, with a lead sentence such as:
"Table~\ref{tab:apx:mobiwac-scope} lists four scope corrections applied to the reproduced prose;
none alters an experimental result, and each narrows a claim or names the basis of a comparison."

```latex
\begin{table}[htb]
\caption{Claim-scope corrections in the reproduced MobiWac 2026 prose (claim-scope narrowing and
comparison-basis disclosure; no experimental result altered).}
\label{tab:apx:mobiwac-scope}
\centering
\small
\begin{tabular}{@{}p{0.30\textwidth}p{0.64\textwidth}@{}}
\toprule
\textbf{Submitted claim} & \textbf{Correction in the chapter} \\
\midrule
The representation ``passes no usable information about the test visits, on three grounds.'' &
The universal negative is replaced by a bounded statement over named channels. The first ground is
scoped to the training objective, with the note that each visit's category is a node input feature;
a fourth ground is added, reporting the development audit that probes the forward-edge channel
between consecutive visits (per-step next-category probe against the last-visited-category
autocorrelation ceiling), with its three limits stated: linear probe, Florida at one random
initialization, ancestor builds of the representation. Every number already in the paragraph is
unchanged. \\
\addlinespace
``none of the balancers that we tried, including the two named above, improved on a tuned fixed
task weighting'' &
``none of the balancers that we tried \emph{at their default configurations}, including the two
named above, ...''. The internal audit records that only one of the two named methods was validly
wired under the dual-tower architecture, so the claim is narrowed to the configurations actually
screened. \\
\addlinespace
The region-pathway control lands ``within $0.3$ of the joint model.'' &
The control is restated against the single-task category score it was measured on
($+7.63$, $+6.54$, $+4.64$ points at Alabama, Arizona, and Florida), and the ``within $0.3$''
figure is retained with its basis named: the joint scores of the development configuration current
when the control was run, not the joint cells of Table~\ref{tab:mobiwac:results}. The control's
single random initialization over five folds is disclosed. The finding is unchanged. \\
\addlinespace
Limitations name two limits. &
A third limit is added, naming the consequence of the two-way split already disclosed twice in the
chapter: epoch selection consults the fold the score is read on, so the absolute scores are
optimistic. The joint-versus-dedicated comparison is affected far less, because the rule is applied
identically to both arms on the same folds and the dedicated arm receives the wider search, which
makes the reported difference conservative. Exact cancellation is not claimed. \\
\bottomrule
\end{tabular}
\end{table}
```

## Option 2 — one paragraph appended to the existing MobiWac prose section

If the orchestrator prefers to keep the MobiWac section table-free, append after
`apx_b_errata.tex:194`:

> Four further corrections narrow the scope of claims in the reproduced prose without altering any
> experimental result. The statement that the representation passes no usable information about the
> test visits, given on three grounds, is replaced by a bounded statement over named channels: the
> label-free training objective is scoped to the objective rather than to the inputs, since each
> visit's category is a node input feature, and a fourth ground is added that reports the
> development audit of the forward-edge channel between consecutive visits, together with its
> limits. The summary of the gradient-balancing screen is narrowed to the default configurations
> actually tested, since the internal audit finds that one of the two named methods was not validly
> wired under this architecture. The region-pathway control is restated against the single-task
> score it was measured on, with the earlier comparison to the joint model kept and its basis named
> as the development configuration current at the time, and with its single random initialization
> disclosed. Finally, the limitations gain a third entry naming the consequence of the two-way
> split that the chapter already discloses: epoch selection consults the evaluation fold, so the
> absolute scores are optimistic, while the joint-versus-dedicated comparison is affected far less
> because the rule is applied identically to both arms and the dedicated arm receives the wider
> search.

---

## Source ledger (one line per item; every value quoted, none computed)

| # | Review id | Chapter site | Evidence file, location | What was quoted |
|---|---|---|---|---|
| A1 | REV-008 | `5_mobiwac.tex:343` (Integrity of the representation) | `docs/results/embedding_eval/rescreen_cat/RESCREEN.md:56` (channel name), `:86-87` (gate + "clean control ceiling (~0.41)"), `:94-95` (linear-probe blind spot); `leak_sniff_fl.csv`; `leak_sniff_resln_fl.csv`; `scripts/embedding_eval/leak_sniff.py`; four-decimal rounding as printed at `src_utils/_history/_archive/reviews_v1/dissertation_review_v1.md:221-223` | ceiling ~0.41; GCN-control lineage 0.4090 / 0.4074; ResLN ancestor 0.4197 / 0.4182; GAT 0.4976 / 0.4863 (LEAK) |
| A2 | REV-011 | `5_mobiwac.tex:185-186` | `docs/results/mtl_improvement/T4_audit_and_verdict.md:26-31` (gradient surgery does not count), `:37-39` (Nash-MTL validly wired), `:8-17` (defaults, seed 0, AL+FL) | no number; wording only |
| A3 | NEW-2 | `5_mobiwac.tex:573-574` | `docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md:20-24` (§2 table), `:54` (n=5 provisional, seed 0) | probe 63.50 / 63.67 / 79.79; deltas +7.63 / +6.54 / +4.64; full-MTL comparand 63.56 / 63.39 / 79.82 |
| A4 | REV-003 | `5_mobiwac.tex:620-621` (Limitations) | drafted wording `src_utils/_history/_review_v1/09_stats_leakage_skeptic_report.md:294-307`; identical rule `src/training/runners/category_cv.py:97` + `next_cv.py:195`; wider dedicated sweep `docs/studies/closing_data/v17_completion/CEILINGS_N20_FINAL.md:41-53` | no number introduced |

## Flags for the author

1. **A2 is applied as instructed and the qualifier does not cover PCGrad.** PCGrad's exclusion in
   the audit is a WIRING result (`T4:26-31`: under the dual tower the private region tower trains
   at unit weight regardless, so the method collapses to approximately equal weighting), and a
   wiring result is invariant to configuration. "At their default configurations" answers the
   GradNorm/DWA/FairGrad objection but not this one. Nash-MTL, the other named method, is sound
   (`T4:37-39`). **Recommendation, not applied:** delete `PCGrad \cite{yu2020pcgrad}, ` from the
   citing sentence at `5_mobiwac.tex:183` and let Nash-MTL carry the named evidence; the preceding
   sentence already reports the literature claim in general terms via `\cite{xin2022domtl}`. The
   author's instruction governs, so the name stays until he rules. The recommendation is also
   recorded as a comment in the chapter source beside the edit.
2. **A3, second-order disclosure not surfaced.** `W6_ENCODER_ISOLATION.md:64` records a
   2026-07-01 audit note that dropout remained active in the fixed stream during training. W6
   states the directional conclusions stand. Not mentioned in the chapter; raise only if the
   examiner asks for the control's exact protocol.
3. **A1, coverage.** The forward-edge audit exists at Florida only, at seed 0, on ancestor builds
   of the representation. The chapter now says so. Running `scripts/embedding_eval/leak_sniff.py`
   at the remaining five datasets on the shipped embeddings would let the sentence widen; it needs
   no retraining.
4. **A2 secondary.** The balancer screen is seed 0 at two states (Alabama and Florida),
   `T4:8-17`. The chapter does not state the footing. Left alone, since the sentence sits in
   related work as a confirmation of published literature rather than as a result of this study.

---

## Layout changes (B1/B2/B3) — no errata rows, but verify these on the rebuild

Presentation only; no claim, number, or word of reproduced prose was altered by any of them.

1. **All seven floats relaxed from `[!t]` to `[htbp]`** (Chapter 4's convention), and the two
   declarations that sat inside a running paragraph were moved to the nearest paragraph boundary:
   Figure 6 (embedding quality) now follows its pointer sentence across a blank line, and Table 3
   plus Figure 7 moved out of the head of Section 5.6.2 down to the paragraph boundary that closes
   each one's first reference. **Declaration order is unchanged**, so every float keeps its number;
   verified against `\label` order and all nine `\ref{tab:mobiwac:results}` sites.
2. **Table 3 split into its two task blocks inside the one float** (the split is at the `cmidrule`
   the table already carried). One caption, one `\label`, one footnote block; the Dataset and
   Regions columns repeat so each block reads alone. Estimated natural widths are 377 pt
   (category, 6 columns) and 408 pt (region, 7 columns) against a 455 pt text block, so neither
   half needs scaling and the body should render at full 11.96 pt instead of the measured 8.00 pt.
   A `max width=\textwidth` adjustbox is retained on each half as a no-op guard. **Fidelity check
   run and passed:** all 66 body cells compare character-for-character against the pre-split
   table, and the marker census is unchanged (24 `\sd{}`, 4 `$^{\uparrow}$`, 2 `$^{\approx}$`,
   3 `$^{\dagger}$`, 3 `$^{\ddagger}$`, the `\footnotesize` note block, all bold marks).
3. **Table 1 tightened rather than scaled**: the four two-word headers (Check-ins, Max len, Avg
   len, Density (%), Majority (%)) are stacked onto two lines with `\shortstack[r]`, and
   `\tabcolsep` drops to 3 pt inside that float. Estimated natural width falls from about 667 pt
   to about 538 pt, so the adjustbox should now scale to roughly 10.1 pt rather than 8.13 pt. No
   column removed, no value or header word changed. Body rows verified identical to `HEAD`.
4. **Figure 6 axis label** `"Score (0–1)"` to `"Score"` in
   `src/figures/mobiwac/fig3_embquality_diss.py:119`, and the figure was regenerated with the
   project interpreter (`.venv/bin/python`). The committed
   `src/figures/mobiwac/fig3_embquality.pdf` is updated. **Verified:** the regenerated PDF's page
   content stream differs from the committed one in exactly two places, the label text operator
   and the `cm` matrix that vertically centers that label; every bar, error bar, tick, gridline,
   legend entry, and numeric annotation is byte-identical.

**Rebuild checklist for the orchestrator** (I cannot build; no TeX binary is reachable from this
sandbox, and the brief forbids running the build):

- [ ] Table 3 renders as two stacked blocks, both unscaled and at body size. If either overfulls,
      the guard adjustbox will shrink that half instead; drop `\tabcolsep` to 4 pt in that float
      before touching anything else.
- [ ] Both `\shortstack` headers and the 3 pt `\tabcolsep` in Table 1 render cleanly. `\tabcolsep`
      is set inside the float, so it does not leak, but confirm Table 2 (same page region) is
      unaffected.
- [ ] Float numbers unchanged: Table 1/2/3 and Figures 4/5/6/7 in the same order as before.
- [ ] The three reported defects are gone: no sentence split by Figure 4 or 5, Table 1 no longer
      above the Section 5.5 headings, no floats-only page, Table 3 no longer ahead of Section
      5.6.2.
- [ ] `make check` lint and the undefined-reference count stay at their previous values.
