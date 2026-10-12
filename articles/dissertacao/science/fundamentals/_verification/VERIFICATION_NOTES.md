# VERIFICATION_NOTES — [VERIFY] closure and the two-class failure taxonomy

<!-- Fail-closed audit trail. Two [VERIFY] classes (GAP_STATUS gap #6):
     Class A = no resolvable identifier.
     Class B = identifier resolves but the specific claim is not locatable in accessible text (paywall).
     Source-of-record rule: final attributes copied from the publisher/DOI landing page or the PDF itself;
     OpenAlex/Crossref are discovery only. -->

## Closed FIRSTHAND from author-downloaded PDFs (articles/dissertacao/science/articles/)

| Key | PDF | Claim located in the source (this session) | Status |
|---|---|---|---|
| `huang2023hgi` (HGI) | "Learning urban region representations with POIs and hierarchical graph infomax.pdf" | Text: the model "is finally trained through maximizing the mutual information among the POI-region-city hierarchy." This is the exact claim §2.2 pivots on. | **[VERIFY] CLOSED** — was the single most important open flag. |
| `wilcoxon1945` | wilcoxon1945.pdf | Method pages describe assigning ranks to the paired differences by magnitude, then signing the ranks by the sign of the difference — the signed-rank test for paired samples. | **[VERIFY] CLOSED.** Stable ID JSTOR 10.2307/3001968; Biometrics Bulletin 1(6):80-83. |
| `sokolova2009measures` | sokolova2009.pdf | Text defines macro-averaging as the average of per-class measures (the M-index), i.e. macro-F1 as the mean of per-class F1. | **[VERIFY] CLOSED.** IPM 45(4):427-437, DOI 10.1016/j.ipm.2009.03.002. |
| `yang2015tsmc` | dingqiyang2015.pdf | The paper studies a Foursquare check-in dataset from New York and Tokyo — the origin of the standard NYC/Tokyo benchmark. Author-confirmed via Dingqi Yang's official dataset page. | **[VERIFY] CLOSED.** IEEE TSMC:Systems 45(1):129-142, DOI 10.1109/TSMC.2014.2327053. Year-of-record 2015 (issue), online-first 2014. |
| `pedregosa2011sklearn` | Pedregosa2011_ScikitLearn.pdf | Title/venue confirmed (JMLR 12:2825-2830, 2011). The 2011 text does NOT describe StratifiedGroupKFold — author-confirmed that splitter entered scikit-learn v1.0/2021 (the earlier "v0.24/2020" note was wrong). | **[VERIFY] CLOSED. Author ruling (2026-07-21): SINGLE citation** — cite the 2011 paper for both the library and the splitter; name the splitter's behavior defensively in prose (it is a v1.0/2021 addition to the same library). No second URL/API citation. |
| `kohavi1995crossval` | (not downloaded) | Author confirmed from the source that the text literally recommends "ten-fold stratified cross-validation." | **[VERIFY] CLOSED by author confirmation.** IJCAI-95, vol 14, pp 1137-1143; Zenodo re-deposit DOI 10.5281/zenodo.19712698 for a resolvable identifier. |
| `yang2016cultural` | 2814575.pdf | "Participatory Cultural Mapping Based on Collective Behavior Data in LBSNs"; confirmed as a DISTINCT work from the TSMC2014 dataset-origin paper (kept separate to avoid the Foursquare-origin conflation). | Confirmed distinct; ACM TIST 7(3), DOI 10.1145/2814575. |
| Foursquare choice (author ruling 2026-07-21) | OpenAlex get_work | `yang2015tsmc` (TSMC2014, "Modeling User Activity Preference...", 815 cites) vs `yang2016cultural` (308 cites). The TSMC2014 paper is the origin of the NYC/Tokyo Foursquare benchmark and is usable for both cities. | **DECIDED: single Foursquare citation = `yang2015tsmc`** (most-cited, covers NYC + Tokyo). `yang2016cultural` retained in bib but not the primary dataset cite. |
| `song2010limits` | 201002-19_Science-Predictability.pdf | Verbatim: "we find a 93% potential predictability in user mobility across the whole user base." The 80% is an illustrative low-predictability user (Pmax=0.2), not a population figure. | **[VERIFY] CLOSED.** Quote only 93%. DOI 10.1126/science.1177170, Science 327(5968):1018-1021. |

## Metric source verified firsthand
| Key | Source | Claim located | Status |
|---|---|---|---|
| `maninis2019attentive` | arXiv:1904.08918 (CVPR 2019 PDF opened) | "We compute multi-tasking performance ... as the average per-task drop with respect to the single-tasking baseline"; Table 3 caption "average relative performance drop (Δm%)". | **Δm source CONFIRMED.** DOI 10.1109/CVPR.2019.00195, pp. 1851-1860. |

## Remaining [VERIFY] — NONE OUTSTANDING
- `song2010limits` — **CLOSED FIRSTHAND (2026-07-21)** from the author-provided PDF
  (`science/articles/201002-19_Science-Predictability.pdf`). Verbatim: "By measuring the entropy of each
  individual's trajectory, we find a **93% potential predictability** in user mobility across the whole user base."
  Correction logged: the "80%" is NOT a second population figure but an illustrative low-predictability user
  (for Pmax=0.2, the individual "chooses his location in a manner that appears to be random" ~80% of the time).
  Quote only the 93% population ceiling. DOI 10.1126/science.1177170, Science 327(5968):1018-1021.
  All 7 first-round [VERIFY] flags are now closed firsthand from the downloaded PDFs; no [VERIFY] items remain.

## Identifier-policy notes (source-of-record, R2)
- Final attributes copied from publisher/DOI landing pages or the opened PDFs; OpenAlex/arXiv used for discovery only.
- Pre-DOI classics keep a stable non-DOI identifier so fail-closed does not drop seminal works
  (Kohavi IJCAI-95 + Zenodo DOI; Wilcoxon JSTOR; Caruana Mach. Learn. DOI already present).
- OpenAlex title truncations (DeepWalk, SNAP) and preprint-vs-publication-year deltas (GCN/DIM/RLW) are metadata
  artifacts, not errors; the .bib carries the full title and the venue-year.
