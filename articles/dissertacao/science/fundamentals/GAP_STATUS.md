# GAP_STATUS — evaluation of the 8 structural gaps raised in review

<!-- Direct answer to: "eval if the follow gaps has already been closed or we need to handle some of them".
     Each gap: verdict (CLOSED / CLOSED THIS ROUND / OPEN-AUTHOR) + exactly what was done or what remains. -->

Legend: **CLOSED** = was already handled in the first pass · **CLOSED THIS ROUND** = fixed now ·
**AUTHOR ACTION** = needs a decision or edit only the author can make (in the paper bibs / prose).

---

## 1. §2.5 "Relevance" was dropped — **CLOSED THIS ROUND**
The first pass mapped only 2.1-2.4 because 2.5 needs no new literature. That was left implicit, which is the
valid complaint. Now explicit: **2.5 is a synthesis section, argument-only, no fresh citations**, ending with the
three-clause "pressing need" hinge that pre-motivates Ch.3/4/5. Written as `2.5_relevance/2.5_relevance_plan.md`
with the hinge structure taken verbatim from NORTH_STAR §3.

## 2. "Fundamentals ≠ frontier" scope boundary was unstated — **CLOSED THIS ROUND**
Now a stated rule (`README.md` + `_bib/BIB_NOTES.md`): the 24-entry frontier set (hypergraph / LLM-for-POI /
contrastive) is routed to the **paper chapters' related-work and the dissertation's future-work, not Ch.2**.
Per-theme anchor budget recorded (≈10-20 works/theme; the chapter is deliberately thin, ~8-12pp). This is also
why the Massive-STEPS graph-transformer/hypergraph baselines (STHGCN, TGAT, ROTAN) are *not* pulled into Ch.2.

## 3. Theme D missing the MTL evaluation metric the project uses (Δm, floors, OOD, selector, imbalance) — **CLOSED THIS ROUND**
- **Δm** now has its canonical source: **Maninis et al. 2019, CVPR (DOI 10.1109/CVPR.2019.00195)** —
  verified firsthand from the opened PDF (defines "average relative per-task performance drop, Δm%").
  Added to the new bib as `maninis2019attentive`.
- **Majority-class floor, Markov-1 floor, OOD-discounted Acc@10, joint checkpoint selector**: given **defensive
  definitions** (formula + plain reading + boundary, WRITING_LAW §5) in `2.4_datasets_and_evaluation/2.4_metrics_addendum.md`.
  No citations invented for the project constructs.
- **Class-imbalance rationale** (Food ≈32-34%; weighted cross-entropy justifies macro-F1) written up, with
  `sokolova2009measures` as the macro-F1 anchor and `lin2017focal` offered as the optional focal-loss alternative.

## 4. Theme B didn't target the "static across visits" claim — **CLOSED THIS ROUND**
`lin2021ctle` (CTLE) is now **pulled forward from 2.1 to 2.2** as the explicit static->contextual evidence, and
the pivot sentence ("a single static per-place vector cannot represent a visit") is named as a claim needing
citation support. See `2.2_representations_for_mobility/2.2_citations.md` row 17 and its notes.

## 5. Known CBIC/CoUrb citation errata not handled (R4) — **AUTHOR ACTION** (documented, not auto-applied)
The errata are the author's to apply to the dissertation bib (I do not silently rewrite the papers' .bib files).
All four are now tabulated with the fix in `_bib/BIB_NOTES.md`:
- POI-RGNN cites the wrong paper -> use `capanema2023poirgnn`.
- HMRM author names wrong -> correct from source of record.
- GAT -> cite the ICLR version.
- `silva2025mtlnet` venue bug ("Brazilian Conference on Intelligent Systems (CBIC)") + stale "Submetido".
Plus the two wrong DOIs verification caught: `misra2016cross` -> 10.1109/CVPR.2016.433; `zhang2021survey` ->
10.1109/TKDE.2021.3070203; and `yu2019mmoe` confirm-or-drop.

## 6. Verification realism — abstract ≠ claim support — **CLOSED THIS ROUND**
The failure taxonomy now has the second class the review asked for. `_verification/VERIFICATION_NOTES.md` records
two [VERIFY] classes: (A) **no resolvable identifier**; (B) **identifier resolves but the specific claim is not
locatable in accessible text** (paywall). The 6 author-downloaded PDFs let me **close class B firsthand** for
Wilcoxon, Kohavi (author-confirmed), Sokolova, Yang-2015, Pedregosa, and **HGI** — the last was the single most
important open [VERIFY]. Final attributes are taken from the publisher/DOI landing page or the PDF itself
(source-of-record), with OpenAlex/Crossref used only for discovery. Pre-DOI classics keep a stable non-DOI
identifier (IJCAI/DBLP/official PDF; Kohavi also carries a Zenodo re-deposit DOI) so fail-closed does not drop them.

## 7. New-key collision + naming convention — **CLOSED THIS ROUND**
- Every new key checked against the **union of all four existing bibs** (128 keys): **0 key collisions, 0 DOI
  collisions**.
- The 6 frontier collisions (Wang_2023 x2, Liu_2023 x2, Lai_2024 x2) are **disambiguated** by first-author +
  method + year in `_bib/new_references_frontier_decollided.bib` (e.g. `lai2024disentangled` vs `lai2024adaptive`).

## 8. Search-provenance log — **CLOSED THIS ROUND**
`_verification/SEARCH_PROVENANCE.md` records, per theme, the databases queried (OpenAlex, arXiv, Crossref via
landing pages, publisher pages), the inclusion rule, and the resulting counts. It is deliberately lighter than full
PRISMA (a coletânea fundamentals chapter, not a systematic review) but is enough to reproduce the search and to
feed the mandatory AI-use disclosure appendix (AGENT_GUARDRAILS §6).

## Minor: "CoUrb 33" vs repo "32" — **CLOSED THIS ROUND**
Reconciled: **CoUrb references.bib has 32 entries** (`grep -c '^@'` = 32). The earlier 33 was a parser false
positive from an `@` inside a field; the DOI+title dedup was unaffected, so the **92-distinct already-cited total
is unchanged**.
