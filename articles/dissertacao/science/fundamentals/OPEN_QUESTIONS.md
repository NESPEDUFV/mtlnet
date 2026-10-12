# OPEN_QUESTIONS — what still needs you (plain-language)

<!-- You said the earlier "Open questions for you" was confusing. Here it is again, plainly:
     these are the only things I cannot finish myself. Everything else is done and in this folder. -->

Think of this as a short to-do list. Most items are one decision each. None block you from reading the
section maps; they are the last-mile confirmations before any Ch.2 prose is written.

## 1. One number still needs your eyes: the predictability ceiling
`song2010limits` (Song et al. 2010, Science) is the "how predictable is human movement" paper. It exists and is
cited. But the famous figures (about 93% potential predictability, about 80% for a specific baseline) are behind a
paywall I could not open this session. **Do not let me quote a number from it until you (or I, from a PDF) read it.**
If you can drop the PDF into `science/articles/` like the others, I will close it firsthand. Otherwise it stays a
"cite the paper, but confirm the number before writing it" item.

## 2. Errata in the existing paper bibs — your call to apply (I will not silently edit the papers)
These are known-wrong entries inherited from CBIC/CoUrb. They belong in the single dissertation bib, applied by you
(NORTH_STAR errata policy). The full table with the exact fixes is in `_bib/BIB_NOTES.md §B`. The short list:
- POI-RGNN -> use `capanema2023poirgnn`; HMRM author names; GAT -> ICLR version; `silva2025mtlnet` venue + status.
- Two wrong DOIs verification caught: `misra2016cross` -> 10.1109/CVPR.2016.433; `zhang2021survey` -> 10.1109/TKDE.2021.3070203.
- `yu2019mmoe`: confirm it is a real distinct work or drop it (it looks like a duplicate of `ma2018mmoe`).
- Consolidate the DGI triple-key and the Nash-MTL double-key before compiling.

## 3. Two small confirmations on new entries (I made a defensible choice; confirm or override)
- `pedregosa2011sklearn`: I cite the 2011 paper for the scikit-learn library, and point the specific
  StratifiedGroupKFold splitter to the scikit-learn API docs (that class postdates the paper). Confirm you are happy
  citing the API docs for the splitter, or tell me you prefer a single citation.
- `yang2015tsmc` vs `yang2016cultural`: I kept these as two distinct works to avoid the common Foursquare-origin
  conflation (TSMC2014 is the NYC/Tokyo dataset origin; the 2016 TIST paper is Participatory Cultural Mapping).
  Confirm that split matches how you want the datasets attributed.

## 4. Scope confirmation: frontier stays out of Ch.2
I routed the 24-entry frontier set (hypergraph / LLM-for-POI / contrastive) and the Massive-STEPS
graph-transformer/hypergraph baselines to the paper chapters' related-work and to future-work, keeping Ch.2 thin.
If you actually want any specific frontier work *defined* in Ch.2, name it and I will verify + place it; otherwise
the thin-chapter rule holds.

## 5. Optional next step (only when you approve): draft one section
Per your original instruction, no prose was drafted. When you are ready, tell me which section to start with
(2.1, 2.2, 2.3, or 2.4) and I will draft that one only (<=1,500 words), obeying the writing law, with a
numbers/citation ledger. 2.2 is the natural first draft because it carries the DGI->HGI->check-in spine.

## What is NOT open (already handled this round)
- §2.5 relevance plan, the Δm metric source (Maninis 2019, verified), the class-imbalance rationale, the
  static->contextual hinge (CTLE pulled into 2.2), the frontier key-collisions, the global collision check, the
  search-provenance log, and the CoUrb count (32). See GAP_STATUS.md for the gap-by-gap verdict.
- The HGI claim that §2.2 pivots on is verified firsthand from your downloaded PDF. It was the biggest open flag; it
  is closed.
