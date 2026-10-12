# SOURCE_LEDGER.md — round 6, every reference, every changed number, every open flag

**Built 2026-07-28 by the ledger track.** State measured at `01915ba7` and re-anchored at
`4e84cf7a` (the per-section chapter split, which lands after every other track and whose render is
byte-identical). This file is the audit trail for the round, not a review of it: it maps each
reference to its identifier and to the claim it carries, each changed number to the file and field
it was quoted from, and each `[VERIFY]` to its owner.

**Provenance rule this file obeys.** Every row says **who** verified it. `LEDGER` means I resolved
the identifier or reproduced the number myself, this session, from the source named in the row.
`INHERITED` means the verdict rests on another pass's report and I did not re-derive it; those rows
are usable as a map, not as verification. The distinction is the point of the file: the author does
not trust self-reported success, and a ledger that prints another agent's "verified" as its own is
worse than no ledger.

**Coordinates.** Line numbers are as of **2026-07-28 at `4e84cf7a`**, after the split. The phrase in
each row is the stable key; a bare `file:line` in this repository has a shelf life of about one
commit (`ANCHORS.md` §5). Every coordinate below was re-resolved by phrase against the split tree,
not carried forward from the source reports.

---

## 0 · What the round actually changed, and what I measured myself

`git log 870f882c..HEAD` is 18 commits (17 to `01915ba7`, plus the split). The diff touches
**23 `.tex` files, `GLOSSARY.md`, `references.bib` (in the earlier `9893a2c1`), four `src_utils`
documents and four checkers.** Measured over the whole round window `7343c8ad^..HEAD`:

| What | Measured |
|---|---|
| Net-new `\cite` keys in prose | **zero** — no key enters or leaves the document this round |
| Citation instances whose **sentence** changed | **3** (`standley2020tasks`, `nash`, `paiva2026stmtlnet`) |
| Bibliography entries re-typed | **2** (`kokkinos2016ubernet`, `mai2023sphere2vec…`), at `9893a2c1` |
| Prose lines carrying a numeral, added | **24** (797 further numerals are inside `%` comments and do not render) |
| Errata rows added | **2** (one B.1, one B.3) + **2** bibliography rows (B.4) |
| `[NEEDS SIGN-OFF]` markers now in `src/` | **43** across 18 files |
| `[VERIFY]` markers now in `src/` | **8** across 6 files |

**Build, measured by me in an isolated `git archive` tree, not taken from a commit message:**
`make defense` 108 pp, `make final` 105 pp, `make ppgc` 109 pp; on all three logs
`tex_errors=0`, `overfull_hbox=0`, `overfull_vbox=0`, `Float too large=0`, `undef_cite=0`,
`undef_ref=0`. Reproduced at both `01915ba7` and `4e84cf7a` with identical page counts.

**`make check` exits 1**, at `4e84cf7a` and equally at `01915ba7` and at the round's starting point
`870f882c`, on one gate: `'this paper' / 'this article' inside chapters`, hitting
`chapters/apx_b_errata.tex:307` ("This article differs from the other two in a way that changes what
this section has to record"). The sentence entered at `d1911c0a`, before this round. **The round's
"`make check` all gates pass" claim is therefore not reproducible as stated** (finding L-1 below);
the page-count gate that earlier reports flagged is now green.

---

## A · Every new or changed reference this round

Twenty-seven rows in three tables, covering 30 key instances (two rows pair adjacent instances of
the same defect): the two bibliography entries re-typed to their versions of record, the three
citation instances whose sentence changed, and every reference a round-6 verdict turned on. **No
reference was added to or removed from `references.bib` after `9893a2c1`**, and no citing site
gained or lost a key, so the table is short by design.

### A.1 · Entries whose bibliography record changed (identifier re-resolved by me)

| Bib key | Identifier | Where opened, by which pass | Claim it supports (file + phrase) | Verdict |
|---|---|---|---|---|
| `kokkinos2016ubernet` | DOI `10.1109/CVPR.2017.579`; preprint `arXiv:1609.02132` | **LEDGER**: Crossref REST this session → `proceedings-article`, "2017 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)", 2017, pp. 5454-5463, sole author Iasonas Kokkinos; arXiv API → same title/author, submitted 2016-09-07, **no `journal_ref`, no DOI on the preprint**. Originally by the citation pass (`11_citation_claims.md` §6.1) | `chapters/3_cbic/basis.tex` — UberNet as the hard-sharing exemplar; **metadata only, no claim depends on the venue** | **corrected** (`@article` preprint → `@inproceedings` CVPR 2017). Crossref renders the title without the quotation marks around `Universal`; the bib keeps the author's own typography, which is defensible and is disclosed in the entry comment |
| `mai2023sphere2vecgeneralpurposelocationrepresentation` | DOI `10.1016/j.isprsjprs.2023.06.016`; preprint `arXiv:2306.17624` | **LEDGER**: Crossref REST this session → `journal-article`, ISPRS J. Photogramm. Remote Sens., 2023, v.202, pp. 439-462, ISSN 0924-2716, eight authors in the bib's order; arXiv API → `journal_ref` "ISPRS Journal of Photogrammetry and Remote Sensing, 2023" and comment "Accepted to ISPRS…". Originally by the citation pass (§6.2) | `chapters/1_introduction.tex:48-50` — "was first validated on geospatial tasks such as species recognition and remote sensing classification"; four further sites in Ch.2/Ch.4 | **corrected** (`@misc` → `@article` with volume, pages, DOI). Identifier fully resolved; **the claim at the Ch.1 site is separately PARTIAL**, see A.3 row 15 |

Both rows carry an Appendix B bibliography erratum (`tables/frame/bib_errata.tex`, rows 17 and 18
of B.4). The Sphere2Vec row **names the work rather than printing the key**, because a 52-character
`\texttt` key does not line-break and produced `Overfull \hbox (113.58371pt too wide)` — the only
overfull box in either build at the time. I confirm **0 overfull boxes in all three builds now**.

### A.2 · Citation instances whose sentence changed this round

| Bib key | Identifier | Where opened, by which pass | Claim now made (file:line + phrase) | Verdict |
|---|---|---|---|---|
| `standley2020tasks` | `arXiv:1905.07553v4`, comment field "Presented to ICML 2020" | **LEDGER**: arXiv API record + **PDF v4 and v3 both downloaded and read this session (13 pp. each)**; nine quotations re-checked by exact substring match after normalizing the extractor's soft-hyphen codepoint (`U+FFFE`). Originally by the protocol pass (`10_protocol_recovery.md` §4) and the claim-scoping pass (`15_claim_scoping_applied.md` §5) | `chapters/3_cbic/method.tex:92` — "In practice, sharing one network across tasks reduces inference cost, since a single network is evaluated rather than one network per task", with a footnote reproducing the published sentence | **corrected**, and **I confirm the correction independently**: the surviving inference-cost half is p.1 abstract verbatim; the removed accuracy half is contradicted on p.1 ("this often leads to inferior overall performance as task objectives can compete") and p.2 ("multi-task learning is often inferior to single task learning with multiple networks"); "faster training" occurs **0** times, while "reduced training time" occurs once on p.1 inside a list the paper hedges "in theory". **One page attribution in the applied comment is wrong**, see finding L-2 |
| `nash` (Navon et al., Nash-MTL) | `arXiv:2202.01017v2`, comment field "ICML 2022"; DBLP `conf/icml/NavonSAMKCF22` (Semantic Scholar) | **LEDGER**: arXiv API + **PDF downloaded and read this session (19 pp.)**; Semantic Scholar `paper/arXiv:2202.01017` for the venue record. Originally by the protocol pass (§3) | `chapters/4_courb/methodology.tex:36` — "Away from a Pareto-stationary point … and under the method's assumption that the gradients are linearly independent there, that direction is a descent direction for every task" | **corrected** (published "ensures that the update is beneficial for all tasks simultaneously" → conditional form), and **I confirm both conditions at source**: p.1 abstract "Under certain as-sumptions"; p.3 "Our main assumption, besides the ones used by Nash, is that if θ is not Pareto stationary then the gradients are linearly independent"; p.6 "Since our update rule is a descent direction for all tasks". **Page range still UNRESOLVED**, see A.4 |
| `paiva2026stmtlnet` | DOI `10.5753/courb.2026.22960` | **LEDGER**: Crossref REST this session → "Anais do X Workshop de Computação Urbana (CoUrb 2026)", 2026, pp. 323-336, four authors (Tarik S. Paiva, Vitor H. O. Silva, Germano B. dos Santos, Fabrício A. Silva), publisher SBC | `chapters/4_courb.tex:18` — the chapter preface's venue, page range and DOI | **supported**; the sentence changed only by re-wrapping, and the bib entry matches Crossref field for field (authors, venue, pages, year, DOI) |

### A.3 · References carrying a round-6 verdict of PARTIAL, NOT-SUPPORTED or UNVERIFIABLE

Twenty-five key instances out of 265 audited. **These verdicts are INHERITED from
`11_citation_claims.md` and its seven per-chapter reports**; what I did myself is (a) resolve each
identifier at Crossref/arXiv/OpenAlex, and (b) re-anchor every site into the split tree. I did not
re-read every source, so the "verdict" column is that pass's judgment, not mine, except where the
row says LEDGER.

| # | Load | Verdict | Site (2026-07-28, `4e84cf7a`) | Key | Identifier — resolved by | Claim it is cited for |
|---|---|---|---|---|---|---|
| 1 | high | NOT-SUPPORTED | `chapters/3_cbic/method.tex:91` | `ruder2017sluice` | `arXiv:1705.08142` — **LEDGER** (arXiv API: title of record "Latent Multi-task Architecture Learning", comment "To appear in Proceedings of AAAI 2019"; the AAAI version of record is DOI `10.1609/aaai.v33i01.33014822`, v.33 pp. 4822-4829, **also LEDGER**) | "hard sharing acts as a regularizer" — the cited work proposes *learning* what to share, a soft-sharing alternative. **The bib entry still carries the preprint title "Sluice Networks…" and no DOI**, which is a second, separate defect (finding L-3) |
| 2 | high | NOT-SUPPORTED → **corrected this round** | `chapters/3_cbic/method.tex:92` | `standley2020tasks` | see A.2 | now the inference-cost claim only |
| 3 | high | NOT-SUPPORTED | `chapters/4_courb/methodology.tex:126` | `sun2020go` | DOI `10.1609/aaai.v34i01.5353` — **LEDGER** (Crossref: AAAI v.34, 2020, pp. 214-221) | temporal cycles carry information about the *functional nature* of places; LSTPM is long/short-term preference for next-POI recommendation |
| 4 | high | NOT-SUPPORTED | `chapters/4_courb/methodology.tex:184` | `belkin2003laplacian` | DOI `10.1162/089976603321780317` — **LEDGER** (Crossref: Neural Computation, 2003, pp. 1373-1396) | an L2 penalty pulling a subcategory embedding toward its parent; Laplacian eigenmaps is manifold dimensionality reduction |
| 5 | high | PARTIAL | `chapters/5_mobiwac/01_introduction.tex:16` | `caruana1997multitask` | DOI `10.1023/A:1007379606734` — INHERITED (Crossref, plus a PDF in the repo) | the compromise-optimal-for-neither mechanism; the abstract states the positive direction |
| 6 | medium | NOT-SUPPORTED | `chapters/3_cbic/basis.tex:33` | `zhang2021survey` | DOI `10.1109/TKDE.2021.3070203` — **LEDGER** (Crossref: TKDE, 2022, pp. 5586-5609) | the five methodological dimensions, which are `yu2024survey`'s five areas |
| 7-8 | medium | NOT-SUPPORTED | `chapters/3_cbic/basis.tex:50` | `nash`, `standley2020tasks` | see A.2 | "Data Heterogeneity" bullet; both keys belong to the gradient-conflict bullet above |
| 9 | medium | PARTIAL | `chapters/3_cbic/method.tex:207` | `nash` | see A.2 | "task weights can be updated less frequently, significantly reducing runtime". **I read the paper this session and did not locate this claim either**; the paper's §4 caps the CCP iteration count, which is a different statement. Stays open as `[VERIFY]` V-1 |
| 10 | medium | PARTIAL | `chapters/3_cbic/results.tex:119` | `chen2020modeling` | DOI `10.1109/TKDE.2020.3001025` — **LEDGER** (Crossref: TKDE, **2022**, pp. 1902-1914; the bib year 2022 matches the record, the prose says "Chen et al. (2020)") | "is designed for POI category classification"; HMRM is a general trajectory-attribute representation model |
| 11-12 | medium | PARTIAL | `chapters/4_courb/methodology.tex:99` and `:118` | `russwurm2024geographiclocationencodingspherical` | `arXiv:2310.06743` — INHERITED (arXiv API; ICLR 2024 per the paper's own header) | "SIREN" names only the sinusoidal half of a paper that proposes spherical harmonics **combined with** SirenNets |
| 13 | medium | PARTIAL | `chapters/5_mobiwac/02_related.tex:78` | `Lim2022` | DOI `10.1145/3477495.3531989` — **LEDGER** (Crossref: SIGIR 2022, pp. 1133-1143) | region as an "auxiliary signal"; in HMT-GRN region is a trained target, subordinate to next POI. Disposition: leave |
| 14 | low | NOT-SUPPORTED | `chapters/3_cbic/basis.tex:59` | `Zhang2020` | DOI `10.24963/ijcai.2020/491` — **LEDGER** (Crossref: IJCAI 2020, pp. 3551-3557) | "uses an LSTM architecture"; iMTL's encoders are a temporal-aware activity encoder and a spatial-aware location preference encoder |
| 15 | low | PARTIAL | `chapters/1_introduction.tex:48-50` | `wu2024torchspatial` | `arXiv:2406.15658` — INHERITED (arXiv API) | "**first** validated on geospatial tasks"; TorchSpatial benchmarks 15 existing encoders. The published CoUrb introduction carries the same attribution, so the two sites should take one decision |
| 16 | low | PARTIAL | `chapters/3_cbic/basis.tex:38` | `caruana1997multitask` | as row 5 | "the simplest and most popular baseline" is a bibliometric claim a 1997 paper cannot carry |
| 17-18 | low | PARTIAL | `chapters/3_cbic/basis.tex:51` | `zhang2021survey`, `yu2024survey` | `arXiv:2404.18961` for `yu2024survey` — INHERITED | "grow **super-linearly**"; neither abstract states the shape |
| 19 | low | PARTIAL | `chapters/3_cbic/basis.tex:59` | `Liao2018` | DOI `10.24963/ijcai.2018/477` — **LEDGER** (Crossref: IJCAI 2018, pp. 3435-3441) | "temporal attention mechanisms"; MCARNN's mechanism is a context-aware recurrent unit |
| 20 | low | PARTIAL | `chapters/3_cbic/basis.tex:61` | `Xia2020` | DOI `10.3390/app10196664` — **LEDGER** (Crossref: Applied Sciences, 2020, art. 6664) | "combines LSTMs"; not in the abstract. The citing sentence is also ungrammatical in the published text |
| 21 | low | PARTIAL | `chapters/3_cbic/basis.tex:63` | `Xu2023` | DOI `10.1145/3582553` — **LEDGER** (Crossref: TOIS, 2023, art. 112) | "graph-based encoders"; TME is a tree-guided multi-task embedding |
| 22 | low | PARTIAL | `chapters/4_courb/related.tex:16` | `rahmani2019category` | DOI `10.1145/3341981.3344240` — **LEDGER** (Crossref: ICTIR 2019, pp. 173-176) | the sequential/temporal-order half is not visible in the truncated Crossref abstract. `[VERIFY]` V-3 |
| 23 | low | PARTIAL | `chapters/4_courb/related.tex:38` | `Xia2020` | as row 20 | same defect as row 20, in the other chapter. Fix both or neither |
| 24 | low | PARTIAL | `chapters/5_mobiwac/02_related.tex:105` | `caruana1997multitask` | as row 5 | "with a fixed loss weighting is standard practice"; `kurin2022scalarization` / `xin2022domtl`, cited two lines later, do establish it |
| 25 | low | UNVERIFIABLE | `chapters/3_cbic/method.tex:23` | `huang2022estimating` | DOI `10.1080/13658816.2022.2040510` — **LEDGER** (Crossref: IJGIS, 2022, pp. 1905-1930) | the edge-weight formula `w_ij = log((1+D^1.5)/(1+d_ij^1.5))` is attributed to the cited work; the abstract cannot confirm a formula. `[VERIFY]` V-2 |

**Twenty-one of the 25 are in reproduced published prose** (15 Ch.3, 6 Ch.4), so they are
errata-policy decisions and not free edits. Chapter 2, the most heavily cited unit at 70 key
instances, carries **none**; the frame chapters carry **one** between them (row 15). That asymmetry
is the shape of the citation risk in this document and it is worth carrying forward.

### A.4 · UNRESOLVED — identifiers I could not resolve myself

| Bib key | What is missing | What I did | What would close it |
|---|---|---|---|
| `nash` | The `pages = {16428--16446}` field. **No source of record I can reach carries a page range.** | Crossref has no DOI for the ICML version; OpenAlex returns only the arXiv preprint (`W4225981399`, `biblio.first_page = null`); Semantic Scholar confirms the venue (DBLP `conf/icml/NavonSAMKCF22`, ICML 2022) but no pages; `proceedings.mlr.press` and `dblp.org` are both outside the network allowlist (proxy 403, one attempt each). | One look at `proceedings.mlr.press/v162/navon22a.html`. The precedent set in this same bibliography was to **drop** an unverifiable page range (`standley2020tasks`), so consistency argues for dropping it or verifying it. |
| `ruder2017sluice` | The entry's **title and type are the preprint's**, and the work has a version of record the entry does not name. | arXiv API: the v3 title of record is "Latent Multi-task Architecture Learning" (not "Sluice Networks…"), comment "To appear in Proceedings of AAAI 2019"; Crossref `10.1609/aaai.v33i01.33014822` gives AAAI v.33 pp. 4822-4829, 2019, same four authors. Both resolved by **LEDGER**. | An author decision: this is the same preprint-to-version-of-record upgrade already applied to UberNet and Sphere2Vec, and it interacts with the row-1 claim defect. See finding L-3. |
| `santos2024urban` | No external identifier, and there will not be one (a UFV master's dissertation). | Not re-checked by me. INHERITED: the citation pass verified it against the PDF in `exemples/germano/`. | Nothing; it needs a bib comment saying so, or a future existence checker reads the absence as a defect. |
| `chen2018gradnorm`, `holm1979`, `jure2014snap`, `kohavi1995crossval`, `kurin2022scalarization`, `liu2023famo`, `pedregosa2011sklearn`, `senushkin2023aligned`, `velickovic2019deep`, `wongso2025massivesteps`, `xin2022domtl`, `yu2020pcgrad` | **No identifier field in the bib entry** (12 entries). | Not re-resolved by me this round; none of them changed. INHERITED: the citation pass resolved each against OpenAlex or the arXiv API and reports the record it returned. | Adding the resolved identifier to each entry, which is a bib edit no round-6 track owned. |
| `capanema2023poirgnn`, `wang2025hamtl`, `zeng2019next`, `Halder2021` | **No abstract at any reachable source**, so the claim check for these four ran on title and record only. | Not re-attempted by me (Elsevier/Springer landing pages are outside the allowlist). INHERITED and explicitly declared in `11_citation_claims.md` §11 item 2. | Reading those four papers. Every citing site is an identity-of-baseline pointer, so no mechanism claim rests on them. |

---

## B · Every changed number this round

**Method.** I extracted every numeral from the added lines of `git diff 870f882c..HEAD -- '*.tex'`
and split them by whether the line renders. **24 numerals are on prose lines; 797 are inside `%`
comments** and never reach the reader. The table covers the 24, plus the four numbers that changed
inside `articles/[mobiwac]/src/` and the counts inside Appendix B's own reconciliation header.
"Quoted" means the value appears in the named source with the named field; "recomputed" means I
re-derived it from primary data this session.

| # | Number, as it now appears | Where it appears (2026-07-28) | Source file → field | Convention | Quoted / recomputed |
|---|---|---|---|---|---|
| 1 | `0.4, 0.5, 0.6, and 0.7` (the HGI sweep grid) | `chapters/2_fundamentals.tex:172` | `research/embeddings/hgi/README.md:548-551` → the four `w_r` rows | four settings, one per row | **quoted; reproduced by me** — the four rows are literally 0.4 / 0.5 / 0.6 / **0.7** |
| 2 | `0.7388 \pm 0.0205` | `chapters/2_fundamentals.tex:174` | same, `:548` → `Cat F1` | Alabama, 5 folds × 50 epochs, 0-1 scale, spread across folds | **quoted; reproduced by me** verbatim |
| 3 | `0.8186 \pm 0.0123` | same line | same, `:551` → `Cat F1` at the adopted `w_r`=0.7 | as above | **quoted; reproduced by me** verbatim |
| 4 | `50` epochs | `chapters/2_fundamentals.tex:173` | same, `:544` → the sweep header "(5 folds × 50 epochs…)" | budget per fold | **quoted; reproduced by me** |
| — | *(what this replaced)* | — | the prose previously read "rose monotonically from **0.74 to 0.82**" | the round's NUM-4 fix: a rounded restatement replaced by the record's own values plus the convention | the word "monotonically" is the **source's own** (`hgi/CLAUDE.md:117`), not a computed judgment |
| 5 | `0.4 / 0.3 / 0.3` (Check2HGI loss weights) | `chapters/2_fundamentals.tex:246`, Eq. `eq:fund:check2hgi` | `docs/context/check2hgi_overview.tex:215` → the displayed objective; **and** `research/embeddings/check2hgi/model/Check2HGIModule.py:51-53` → `alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3`, summed at `:1192-1195` | fixed weights, one per hierarchy boundary | **quoted; reproduced by me at both sources**, which agree |
| 6 | `0` and `1` (the discriminator's range) | `chapters/2_fundamentals.tex:250` | property of the logistic function, stated in the same sentence that defines σ | definitional, not measured | not a data number |
| 7 | `284` and `365` (fine-class values per state) | `chapters/apx_b_static_scope.tex:19` | `data/checkins_by_state/{Alabama…Texas}.parquet` → `spot` column, `nunique` after `drop_duplicates("placeid")` | POI-level (deduplicated by `placeid`), five Gowalla states, min and max of the five | **RECOMPUTED BY ME FROM THE PARQUET FILES**: AL 11,848 POIs / 284 values, AZ 20,666 / 305, FL 76,544 / 324, CA 169,145 / 333, TX 160,938 / 365; **0 spot values spanning more than one category in any state**. All five rows and the "every one of them maps to" claim reproduce exactly |
| 8 | `42` (partition seed) | `chapters/apx_a_contributions.tex:107` | `docs/context/DATA_SPLITS.md:16` → `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`; `:20` "Random seed = 42 (fold-id seed)" | fold-id seed, fixed across model-init seeds | **quoted; reproduced by me** |
| 9 | `0, 1, 7, and 100` (seeds) | `chapters/apx_a_contributions.tex:113` | `DATA_SPLITS.md:65` → "**Seeds {0, 1, 7, 100}** … Combined with 5 folds → n=20" | four random initializations over ONE fixed partition; n = 20 fitted models, n = 4 inferential unit | **quoted; reproduced by me** |
| 10 | `5` folds, `80%` / `20%` | `chapters/4_courb/results.tex:14` (re-wrapped, value unchanged) | the published CoUrb table conventions | published prose; the round added only the split-axis and checkpoint clauses around it | quoted (unchanged) |
| 11 | `0.68` and `0.19` (balancer margins) | `chapters/5_mobiwac/02_related.tex:114-115` and `articles/[mobiwac]/src/sections/02_related.tex` | `docs/results/mtl_improvement/T4_full_screen.json` → `alabama.{nash_mtl,scale_norm}.cat` minus `alabama.equal_weight.cat` | macro-F1 points against equal weighting, registry defaults, **seed 0, Alabama and Florida only** | **RECOMPUTED BY ME**: Nash-MTL `+0.6805`, scale normalization `+0.1931`. Both round correctly. The "collapsing on next-region" clause also holds: scale_norm at Florida is `−37.59` reg points |
| 12 | `nineteen` balancers | same sentence | `T4_full_screen.json` → 19 keys under each of `alabama` and `florida` | count of screened arms per dataset | **RECOMPUTED BY ME**: 19 arms, both states, names enumerated |
| 13 | `+0.001` (gradient cosine) | `chapters/5_mobiwac/02_related.tex:161`, `articles/[mobiwac]/src/sections/02_related.tex:99` | `docs/studies/archive/mtl_improvement/WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:29-31` → "pooled mean **+0.0008** over the 16 champion-G runs (4 states × 4 seeds {0,1,7,100}), n = 3,797 epoch-fold points"; restated at `docs/results/mtl_improvement/T4_audit_and_verdict.md:47-49` | mean over training, four seeds each on **four** Gowalla states | **quoted; the pooled value reproduces** (+0.0008 → +0.001). **The round's parity fix holds**: the paper read "three of our six datasets", which both undercounted the pool and implied every state in it is one this study reports; both texts now name the four states, and I verified `grep` for "three of our six" / "three of six" over `src/` and the paper source returns **zero prose hits**. **But see finding L-8 — the `±0.003` bound in the same parenthesis is false, and my first pass through this row marked the cosine `INHERITED` and did not re-derive it, which is exactly how the bound survived** |
| 14 | `5,3 a 9,4` / `5.3 to 9.4` macro-F1 points | `0_main.tex:249` (Resumo), `0_main.tex:332` (Abstract), `chapters/6_conclusion.tex:75` | `docs/studies/closing_data/v17_completion/stats_n20/RESULTS.md` §1 → Δcat column | macro-F1 points, MTL minus the dedicated ceiling, joint-best selection, seed-level paired *t*, n = 4 | **quoted; reproduced by me**: FL **+5.34** is the low end, AZ **+9.40** the high; AL +7.73, Istanbul +8.59, CA +6.45, TX +7.45 all inside |
| 15 | "at all six" (category) | Resumo, Abstract, `6_conclusion.tex` | same file, rev-4 header table → six rows, all `reject ✅` at α = 0.05, Holm m = 6 | Holm-corrected paired *t* on per-seed means | **quoted; reproduced by me** — and this is the withdrawn flag, see C-W1 |
| 16 | "four of them" / "four of six" (region) | Resumo, Abstract, `1_introduction.tex:132`, `6_conclusion.tex:21,75` | `tables/mobiwac/results.tex:47-52` → four `$^{\uparrow}$` (Istanbul, FL, TX, CA) against two `$^{\approx}$` (AL, AZ) | Acc@10, 4 seeds × 5 folds; caption defines ↑ as supported improvement, ≈ as TOST non-inferiority within ±2 pp | **quoted; reproduced by me** from the table's own marks |
| 17 | `two-point` Acc@10 margin (TOST) | Resumo, Abstract, `5_mobiwac/05_setup.tex:76` | `stats_n20/RESULTS.md` §1 region table; `GLOSSARY.md` §4 | δ_reg = 2 pp, pre-registered; 90% CI inside ±2 | **quoted; reproduced by me**. AZ's CI lower bound is `+0.001` and the record says "do NOT upgrade to beats"; **the pair does not upgrade it** |
| 18 | `2.664/2026` (CNPq Portaria) | `chapters/apx_c_ai_disclosure.tex:56` | `AGENT_GUARDRAILS.md` §6 → "CNPq Portaria nº 2.664/2026" | policy identifier | quoted; the number did not change, only the sentence it sits in |
| 19 | Resumo `310` / Abstract `271` words | `15_resumo_abstract.md` §2, and the round's commit messages | measured on the **rendered pages** with `src_utils/_history/_round6/_measure_abs.py` | words = letter/digit tokens, hyphenated compound = one word, UFV header and keyword block stripped | **RECOMPUTED BY ME on the rendered PDF with that same instrument: Resumo 310 (11 sentences, mean 28.2) — exact. Abstract 272, not 271** (11 sentences, mean 24.7). The one-word gap is a hyphenation artifact: p.3 carries two soft-hyphen breaks (`Rep-resentations`, `multi-task`); joining across them gives 271, treating them as breaks gives 272. **Neither is wrong, but the report's own §1 rule 7 says hyphenation is undone before matching, so 271 is the value its stated convention yields and the instrument as shipped returns 272.** See finding L-4 |
| 20 | `8 + 13 + 4 + 18 = 43` itemized errata rows | `chapters/apx_b_errata.tex` reconciliation header (comment) | the four tables' own bodies | two-column data rows between `\midrule`/`\endlastfoot` and the table end, comments stripped | **RECOMPUTED BY ME with that method: B.1 = 8, B.2 = 13, B.3 = 4, B.4 = 18, total 43.** Exact. The previous header claim "6 + 13 + 3 + 14 = 36" had two stale terms before this round |
| 21 | CoUrb additions `eight → nine` | `chapters/apx_b_errata.tex:262` | the chapter's own declared-addition comments | count of marked additions in Ch.4 | quoted; INHERITED, not independently enumerated by me |
| 22 | Appendix C `374 → 303` words | `16_frame_numbers.md` §5 | measured on `apx_c_ai_disclosure.tex`, comments stripped | word count of the appendix body | INHERITED; not re-measured by me |
| 23 | pages `108 / 105 / 109` | `CLAUDE.md:36-37`, `PLAN.md:17-18`, commit messages | `build/main.log`, `build/main_final.log`, `build/main_ppgc.log` → `Output written on … (N pages` | pdflatex's own count, three-pass build | **RECOMPUTED BY ME in an isolated tree at both `01915ba7` and `4e84cf7a`: 108 / 105 / 109, `tex_errors=0` on all three.** The `make check` page-count gate agrees |
| 24 | `0.001` decimals in the `\vspace*{2cm}` and column widths (`0.42`, `0.52`) | `0_main.tex`, `tables/*/errata.tex` | layout parameters, not data | typesetting | not data numbers |

**Numbers I could not trace to a file:** none in prose. Every rendered numeral added this round
resolves to a named source file and field. **Two numbers in durable records do not reproduce**: the
Abstract word count (row 19) and the page attribution in the Standley comment (finding L-2).

---

## C · Every `[VERIFY]` flag still open, deduplicated

Fourteen open, one withdrawn. Sources: the four flags of `11_citation_claims.md` §10, the four of
`10_protocol_recovery.md` §6, the five of `15_claim_scoping_applied.md` §10, the eight of
`15_resumo_abstract.md` §7, the two blocking GLOSSARY entries of `16_frame_numbers.md`, and the
eight `[VERIFY]` markers physically in `src/`. Deduplicated: the Nash page range appears in three
reports, the joint-model column in two, the page-count gate in three.

| ID | Flag | Owner | Status | What would close it |
|---|---|---|---|---|
| V-1 | `chapters/3_cbic/method.tex:207`, `nash`: "task weights can be updated less frequently, significantly reducing runtime while maintaining performance" | citation pass; **re-checked by me** | **open, and I confirm it** — I read the 19-page PDF this session and did not locate the claim; the paper caps its CCP iterations at 20, which is a different statement | The passage in `arXiv:2202.01017`, or restating the clause as this chapter's own engineering choice |
| V-2 | `chapters/3_cbic/method.tex:23`, `huang2022estimating`: the edge-weight formula attributed to the cited work | citation pass | open (UNVERIFIABLE, not refuted) | Locating the formula in the paper body, or presenting it as this work's own construction |
| V-3 | `chapters/4_courb/related.tex:16`, `rahmani2019category`: the sequential/temporal-order half | citation pass | open | The paper body; Crossref deposits only a four-sentence abstract |
| V-4 | `chapters/5_mobiwac/…`, `huang2024cslsl`: the sentence cites CSLSL's own ablation | citation pass | open | The paper's results section; an abstract cannot carry an ablation |
| V-5 | `nash` page range `16428--16446` | protocol pass, claim-scoping pass, **and me** | **open; escalated** — I exhausted Crossref, OpenAlex and Semantic Scholar; PMLR and DBLP are outside the allowlist | One look at `proceedings.mlr.press/v162/navon22a.html`, or drop the field per the `standley2020tasks` precedent |
| V-6 | The published CBIC joint-model next-category column reproduces from **no** artifact in this repository (0 of 21 cells) | protocol pass | open **by decision**, registered as `LEFT_OUT.md` LO-2 | Nothing; the constraint it imposes is that no sentence may claim the CBIC numbers are reproducible from this repository without excluding that column |
| V-7 | The CBIC/CoUrb tuning budget is not recoverable | protocol pass | open **by decision**, registered as `LEFT_OUT.md` LO-1 | Nothing; the number is not available, and `N1` forbids writing one |
| V-8 | `chapters/2_fundamentals.tex:601-602`: "Chapter 3 reports five-fold cross-validation without identifying the split axis" is **false** now that the Ch.3 protocol sentence has landed | claim-scoping pass → **frame owner** | **open, and I confirm it in the RENDER, not only the source**: the false clause prints on **p. 23** and the Ch.3 addition that contradicts it prints on **p. 36** (`chapters/3_cbic/results.tex:30`). The clause wraps across two source lines, so a single-line `grep` misses it — use a whole-file string search | The repair drafted in the comment at the Ch.3 site: "Chapters 3 and 4 both stratify by sample rather than by user … and only Chapter 5 splits by user" |
| V-9 | `make check` page-count gate | figures pass, citation pass, claim-scoping pass | **CLOSED by me** — the gate is green at `4e84cf7a`: "all recorded page counts agree with the build". `make check` still exits 1, but on a different gate (finding L-1) | — |
| V-10 | GLOSSARY: **bilinear discriminator** and **logistic function** used in the new Ch.2 Check2HGI paragraph, neither registered | frame-numbers pass → **glossary owner** | **open and blocking** by the fail-closed rule. I confirm both terms are absent from `GLOSSARY.md` and present in the rendered paragraph | The author approving the two proposed entries (`16_frame_numbers.md` §4) |
| V-11 | GLOSSARY: **Pareto-stationary point**, used in the narrowed Ch.4 Nash sentence | claim-scoping pass → **glossary owner** | **open and blocking**, same rule. The term is live at `chapters/4_courb/methodology.tex:36` | The author approving the proposed entry (`15_claim_scoping_applied.md` §9) |
| V-12 | GLOSSARY §6: "modelos ajustados" and four further PT phrasings used in the Resumo | resumo pass → **glossary owner** | **partly closed**: `01915ba7` registered nine PT rows including `vinte modelos ajustados`, `usuários disjuntos entre treino e teste`, `partição`, `média por inicialização`, `seleção joint-best`. I confirm all nine are now in `GLOSSARY.md` | Nothing further for those five; the flag closes |
| V-13 | The pair is above the defended envelope (Resumo 310 vs 282 max, Abstract 271/272 vs 250) | resumo pass → **author** | open by decision, reported rather than smoothed | An author ruling on whether to spend the last 20-30 words |
| V-14 | The averaging convention of the HGI sweep's "Cat F1" (macro or weighted) is named nowhere | frame-numbers pass | open; the prose says "category F1" and not "macro-F1" for exactly this reason | The HGI run configuration |
| V-15 | `chapters/apx_a_contributions.tex:185,195`: whether `METRICS.md`'s Δm variants and F51 extraction rule should be disclosed; whether a package-version manifest exists | frame-numbers pass → **author** | open | An author decision plus, for the manifest, its existence |
| **C-W1** | **WITHDRAWN** — "The CA and TX category cells are provisional in the statistical record, and no frame text says so", raised as flag 1 of `15_resumo_abstract.md` §7 | resumo pass; withdrawn by the round supervisor at `35fe46cc` | **Withdrawn, and I re-verified the withdrawal independently.** `stats_n20/RESULTS.md` is at **rev 4, 2026-07-13**; its header table reports all six datasets rejecting at α = 0.05 (CA Δcat **+6.45**, TX **+7.45**, both Holm-adjusted p = 8.9e-07, m = 6) and states that A1 landed the CA/TX n=20 runs on 2026-07-11. The material the flag quoted sits under a heading that reads literally `## 1b · CA / TX — seed-0 paired analysis (✅ A1 n=20 now COMPLETE — supersede via M1-full re-run)`, and §1b's own banner says the n=20 "**confirms** the provisional seed-0 verdicts". **So "at all six" is correct and carries no undisclosed provisional footing.** Recorded here so it is not re-raised: the lesson is that this record keeps its superseded revisions inline, so **anchor on the revision header, not on the first matching line** | Nothing; it is closed. Recorded so it is not re-raised |

**One flag adjacent to C-W1 that is NOT withdrawn and is not in any report as a flag.** The same
record's §1b correction of 2026-07-27 establishes that **next-region superiority was never
pre-registered** and that the four region gains are post-hoc secondary results. Chapter 5 discloses
this at `chapters/5_mobiwac/05_setup.tex:76` ("did not cover next-region superiority, so the four
next-region gains … are secondary results outside it"). **The Resumo, the Abstract, Chapter 1 and
Chapter 6 all state "outperforms … at four of six" with no such qualifier.** That is a scoping
question for the author, not a number error, and I raise it as finding L-5 rather than as a flag,
because no round-6 pass owned it.

---

## D · Findings this track raises

| ID | Severity | Anchor | Measured | Conclusion | Closes when |
|---|---|---|---|---|---|
| **L-1** | **MAJOR** | `make check`; `chapters/apx_b_errata.tex:307` "This article differs from the other two" | I ran `bash ../src_utils/check.sh` in isolated `git archive` trees at `870f882c`, `01915ba7` and `4e84cf7a`. **All three exit 1**, all three on the `'this paper' / 'this article' inside chapters` gate, hitting that one line. The sentence entered at `d1911c0a`, before this round. `make check` on the live tree also exits nonzero | The round state given to me says "`make check` all gates pass", and the split commit's own message repeats it. That is **not reproducible**; one gate has been red across the whole round window. It is a false-negative in a *report*, not in the document, and the offending sentence is arguably a legitimate use ("this article" refers to the MobiWac manuscript, not to the dissertation) — but a gate that is known-red and reported green is exactly the failure mode `AGENT_GUARDRAILS` §7 names | Either the sentence is rephrased, or the gate gains a documented exemption for that file (as it already has for `apx_b_errata` in the banned-words gate), and the build claim is restated as "all gates pass except X, exempted because Y" |
| **L-7** | **MAJOR** | `chapters/2_fundamentals.tex:601-602` "reports five-fold cross-validation without identifying the split axis" vs `chapters/3_cbic/results.tex:30` "The folds are formed by a stratified splitter over the samples" | Both printed in the defense PDF: the false clause on **p. 23**, the sentence that falsifies it on **p. 36**. Verified on the rendered text layer, not only in the source. The clause wraps across two source lines, which is why a line-anchored `grep` reports it absent | The claim-scoping pass named this as owed and drafted the repair; **it was not applied, and it is now a contradiction a reader can see thirteen pages apart** — the frame says a chapter does not state something the chapter states. Raised as `[VERIFY]` V-8 by that pass, but it is a defect in the document rather than an open question, which is why it is also a finding here | The Ch.2 clause is replaced by the drafted repair, and the whole-file string search returns nothing |
| **L-8** | **BLOCKER** (raised by the number/claim pass at `09d48ac5` as N-1; **re-derived and confirmed here, and my own row is where it slipped through**) | `chapters/5_mobiwac/02_related.tex:161` and `articles/[mobiwac]/src/sections/02_related.tex:99`: "per-dataset means within $\pm0.003$" | I read the source of record myself: `WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:29-31` gives per-state cosine means **FL +0.0007, AL +0.0032, AZ −0.0005, GE −0.0004** over the widened 16-run measurement (4 states × 4 seeds, n = 3,797 epoch-fold points), restated at `T4_audit_and_verdict.md:47-49`. `abs(+0.0032) > 0.003`, so the bound is **false for Alabama, the first state the sentence names**. The pooled `+0.001` is correct (+0.0008 rounds to it) | The round rescoped the pool from three datasets to four and **carried the bound across unchanged**; the bound is correct only against the superseded two-run seed-0 figures (AL +0.0026). **My table B row 13 marked this number `INHERITED` and said in terms that I did not re-derive the cosine — that is the row the defect passed through, and the mechanism is worth naming: a ledger that records provenance honestly still does not catch a number it declines to re-derive.** A false bound, not a false conclusion: +0.0032 is still ≈ 0 and the orthogonality argument stands | The clause states a bound the source supports (`\pm0.004`, or the four per-state values named outright), applied in **both** files with the `articles/[mobiwac]/ERRATA.md` line the Ch.5 parity regime requires |
| **L-9** | **MAJOR** | `chapters/apx_b_errata.tex`, **rendered p. 95**: "normalized to the second form at all 25 places where the name appears in the printed chapter: 21 in prose, one in a subsection heading, one in a figure caption, and two in table headings" | I enumerated every `MTLnet` occurrence in the rendered Chapter 4 sources (`4_courb.tex` plus `4_courb/*.tex` plus the two CoUrb tables, `%` comments stripped, the registered `ST-MTLNet` form excluded): **21 prose, TWO subsection headings, 1 figure caption, 2 table headings = 26**. The two headings are `chapters/4_courb/methodology.tex:87` (`\subsection{Baseline: MTLnet with DGI}`) and `chapters/4_courb/related.tex:42` (`\subsection{The MTLnet framework}`). The chapter's own source comment at `chapters/4_courb.tex:7` says "**26 sites** … (24 printed, 2 in comments)", and `12_figures.md:469` calls it "the 26-site MTLnet normalization" | Three records give three different counts for one normalization, and **the wrong one is the one that prints**: the appendix's own breakdown sums to its stated 25 only by counting one subsection heading where there are two. The count is not load-bearing for any result, but it is a printed number in the errata appendix — the one place in the document whose whole function is to be exactly right about what was changed. Also held open as a `fail`-level reviewer finding against the pass that wrote it | The appendix reads 26 with "two in subsection headings", or its scope is stated so that 25 is what the scope yields; and `4_courb.tex:7`'s "24 printed" is reconciled with it |
| **L-2** | MINOR | `chapters/3_cbic/method.tex:136` comment: "p.7 reports that at a matched parameter budget" | I read `arXiv:1905.07553` v4 **and** v3. The matched-budget sentence and "Nevertheless, two-task networks still do not compare favorably" are both on **p.4** in both versions; p.7 carries the 45-versus-95-percent training-time comparison, which is the *other* claim the same comment cites correctly | One page attribution in an applied audit comment is off by three pages. The claim itself is right and the errata row does not print a page, so nothing the reader sees is wrong; but the comment is the audit trail a future checker will use | The comment reads p.4 for the matched-budget result |
| **L-3** | MINOR | `references.bib`, `ruder2017sluice`: `title = {Sluice Networks: Learning What to Share Between Loosely Related Tasks}`, `journal = {arXiv preprint arXiv:1705.08142}` | arXiv API: the title of record at v3 is **"Latent Multi-task Architecture Learning"**, comment "To appear in Proceedings of AAAI 2019". Crossref `10.1609/aaai.v33i01.33014822`: AAAI v.33, pp. 4822-4829, 2019, same four authors | The entry names a superseded preprint title and no version of record — the same defect this round **fixed** for UberNet and Sphere2Vec, left in place for a third entry, which is also the key carrying the round's highest-load NOT-SUPPORTED verdict. Two decisions on one entry are cheaper than two passes over it | The entry is re-typed to the AAAI record (or the claim decision at row 1 is taken and the entry updated in the same commit), with a B.4 row |
| **L-4** | MINOR | `15_resumo_abstract.md` §2 table, "Abstract, after **271**" | I ran the report's own instrument (`_measure_abs.py`) on p.3 of the rendered defense PDF: **272** words, 11 sentences, mean 24.7. The Resumo reproduces exactly at 310/11/28.2. The one-word gap is two soft-hyphen breaks on p.3 (`Rep-resentations`, `multi-task`); joining across them yields 271 | The instrument as shipped does not apply the hyphenation normalization its own §1 rule 7 declares, so the reported 271 and the reproducible 272 differ by one. Immaterial to the envelope argument; material to a ledger, because the number is quoted in a durable record and does not reproduce | The instrument normalizes soft hyphens before counting, or the report states which of the two conventions its figure is on |
| **L-5** | MINOR | `chapters/5_mobiwac/05_setup.tex:76` "did not cover next-region superiority, so the four next-region gains … are secondary results"; against `0_main.tex:249,332`, `chapters/1_introduction.tex:132`, `chapters/6_conclusion.tex:21,75` | Chapter 5 discloses that region superiority is outside the pre-registered plan. The Resumo, the Abstract, Chapter 1 and Chapter 6 all say the joint model "outperforms" on region "at four of six" with no such qualifier. The statistics record's own 2026-07-27 correction confirms the registered primary test for **every** region cell is TOST non-inferiority | A scope that Chapter 5 states and the frame does not. Not a number error and not a verb error (the four gains do pass a paired test), but the frame's four claims are one hedge weaker in the chapter than in the summary. No round-6 track owned this | An author ruling: either the frame adds "as a secondary result" once, or the asymmetry is recorded as deliberate in `LEFT_OUT.md` |
| **L-6** | MINOR | 443 `file:line` coordinates across the fifteen `_history/_round6/*.md` reports | Resolved every one against the live tree: **279 of 443 (63%) now land past the end of the file they name**, because `3_cbic.tex`, `4_courb.tex` and `5_mobiwac.tex` are 55, 42 and 50 lines long after the split. `11_citation_claims.md` (anexo, sec. `11_claims_3_cbic.md`) alone carries 77 such coordinates, `11_citation_claims.md` (anexo, sec. `11_claims_5_mobiwac.md`) 56, `11_citation_claims.md` (anexo, sec. `11_claims_4_courb.md`) 54, `11_citation_claims.md` 48, `10_protocol_recovery.md` 23 | The round's own reports are now largely un-navigable by coordinate, which is the exact failure `ANCHORS.md` was written to stop. The findings survive; the addresses do not. Every load-bearing coordinate is re-resolved in tables A and B above and in `VERIFY_LIST.md` | Nothing needs editing in those reports; this ledger and `VERIFY_LIST.md` are the current address book. Future reports cite the phrase |

**What holds.** The two bibliography upgrades are correct field for field at Crossref. The Standley
correction is right at source on all nine quotations, including the one an earlier draft got wrong.
The Nash narrowing states exactly the two conditions the paper states, in the paper's own terms. The
HGI sweep values, the Check2HGI weights, the seeds, the partition seed, the 5.3-to-9.4 range, the
four-of-six region count, the two balancer margins, the nineteen arms, the 284-to-365 fine-class
counts and the 43-row errata reconciliation **all reproduce exactly** — several of them recomputed
from primary data rather than re-read from a report. The withdrawn flag was correctly withdrawn.
Three builds are clean at 108/105/109 with every counter zero.

---

## E · Durable-record counts that do not reconcile with the file they describe

Four more, all verified by me, all small, none affecting a result. They are collected here rather
than as findings because each is a self-description in a comment or a commit message rather than a
claim to the reader. They are listed because a number ledger that records only the numbers a reader
sees is not a number ledger, and because three of them are held open as reviewer findings against
the passes that wrote them.

| Where | It says | I measure | Note |
|---|---|---|---|
| `src/main_ppgc.tex:7`, `src/main.tex:11`, `src/Makefile:35` | "deliberately **four** lines of content" / "a **four-line** file" | **2** content lines (`\def\APPROVALSHEET{}` and `\input{main.tex}`), comments and blanks excluded | Three durable files carry the same wrong description; the commit message that introduced them says "two lines of content", so the file comments contradict their own commit |
| the commit message of `1ef83867` | the new checker "covers **twelve** reference-like macros" | `check_doubled_macro.py` defines **13** (`ref, cite, citeonline, eqref, autoref, pageref, nameref, citet, citep, textcite, input, include, label`) | Off by one in the commit record; the checker's behavior is unaffected and its self-test passes in both directions, which I re-ran |
| `src/tables/cbic/errata.tex:14` | "the distance from **the 106/101 that a pristine HEAD checkout produces**" | A pristine checkout of the commit that figure was measured on (`870f882c`) gives 106/101; a pristine checkout of HEAD gives **108/105**, which the same comment states two lines earlier from its own revert-to-HEAD build | The label names the wrong tree. The conclusion it supports (about one page per variant for that track) is unaffected |
| `src/chapters/apx_b_errata.tex:207` (CoUrb banner) | **already corrected**: "The **first two** corrections … replace the published numbers … The **third** substitutes a verdict verb … and the fourth narrows one claim" | `tables/courb/errata.tex` row 3 is indeed a verdict-verb substitution with no number | Recorded as **closed**: an earlier form of this banner said "the first three … replace the published numbers", which row 3 is not. The live text distinguishes all four correctly |

---

## F · What this track could not confirm

1. **Twenty-one of the 25 citation verdicts in table A.3 are INHERITED.** I resolved every
   identifier myself and re-anchored every site, but I re-read the source for only three keys
   (`standley2020tasks`, `nash`, and the four Crossref-checkable attribute sets). The
   claim-support judgments for the other rows are `11_citation_claims.md`'s.
2. **The fan-out that report describes did not happen** (its own §11 item 1): one agent ran all
   seven per-chapter units. So the 265-instance audit is one pair of eyes, not seven, and this
   ledger is a second pair over its identifiers and its numbers — not over its readings.
3. **I did not re-derive the gradient-cosine `+0.001`**, the Appendix C word counts, the CoUrb
   additions count, or the figure-geometry measurements of `12_figures.md`. Those rows are marked
   INHERITED.
4. **The `nash` page range is unresolved and cannot be resolved from this sandbox** (PMLR and DBLP
   are outside the allowlist; one attempt each, both proxy-refused).
5. **I did not audit the render beyond the front matter and the page counts.** The figure label
   sizes, the float placements and the Chapter 5 diagram geometry are `12_figures.md`'s
   measurements and I did not repeat them.
6. **I built in the live tree once**, which rewrote the tracked `src/dissertacao.pdf`; I restored it
   with `git checkout` and confirmed the working tree is clean at the HEAD blob hash. Every
   measurement reported above comes from isolated `git archive` trees under `/tmp`, not from that
   build.

---

# Addendum: the eleven changes made AFTER this ledger was written

**Appended 2026-07-28.** This ledger was written at `c5c6789d`, before the eight review tracks
landed. Everything below happened after, and every row here is a change to the document that the
tables above do not cover. Same rules: an identifier I did not resolve myself is marked as inherited,
and a number I did not trace to a file is marked as untraced.

## D. Numbers changed after `c5c6789d`

| # | The number, as it now reads | Where | Source file and field | Convention | Quoted or recomputed | Who verified |
|---|---|---|---|---|---|---|
| D1 | "the largest per-dataset mean in absolute value is $+0.0032$" | `5_mobiwac/02_related.tex:161` **and** `articles/[mobiwac]/src/sections/02_related.tex:99` | `docs/studies/archive/mtl_improvement/WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:30`, restated `T4_audit_and_verdict.md:48`: FL +0.0007, AL +0.0032, AZ −0.0005, GE −0.0004 | pooled mean over the 16 champion runs, 4 states x 4 seeds {0,1,7,100}, n = 3,797 epoch-fold points | **quoted** | fact gate found it; **I read the source file myself** before editing. Replaces a false ±0.003 envelope |
| D2 | "all 28 places ... 23 in prose, two in subsection headings, one in a figure caption, and two in table headings" | `apx_b_errata.tex:234` | Re-enumerated by occurrence over `chapters/4_courb.tex`, `chapters/4_courb/*.tex`, `tables/courb/*.tex`: `MTLnet` not preceded by `ST-`, non-comment lines only | count of printed occurrences in the chapter and its tables | **recomputed** (a count, not a measurement; the protocol permits counting) | ledger pass found the sum failed; **I re-enumerated myself**. Headings at `related.tex:42`, `methodology.tex:87` |
| D3 | "nos três estados testados" / "in the three states tested" | `0_main.tex:241` and `:326` | Ch.6's own wording; CoUrb tested FL, CA, TX | scope of the CoUrb category result | **quoted** from Ch.6 | Resumo/Abstract pass (M-2) |
| D4 | `\finalbuildfirstpage` = **8** | `main.tex:53` | Measured: the deposit build has 7 pre-textual pages; UFV_COMPLIANCE §4.4 requires first body page = pre-textual + 1 | printed page number of the first body page | **recomputed from the render** in all three builds | UFV persona (C-1); **I re-measured all three builds myself** |

## E. Reference changes after `c5c6789d`

**None.** No reference was added, removed, or re-keyed after this ledger was written. The six fix
commits touched prose, one integer, one hyperref option, and 24 magic comments.

## F. `[VERIFY]` flags: what changed

| flag | State at `c5c6789d` | State now |
|---|---|---|
| V-8 (Ch.2 asserts a split-axis gap Ch.3 fills) | open, filed as `[VERIFY]` | **CLOSED.** The ledger was right that this is a defect and not a verification question. Repaired at `fecc7fb1` |
| the ±0.003 cosine bound | flagged INHERITED, then corrected by the ledger pass itself to a live BLOCKER | **CLOSED** at `fecc7fb1`, in both files |
| `\finalbuildfirstpage` "tune against the RASCUNHO PDF" | live `[VERIFY]` on the line | **PARTLY CLOSED.** The value was wrong on its own terms and is now derived (8). The flag's original request — confirm against the AcademicoPG RASCUNHO after upload — remains, and is `PENDENCIAS.md` §3 |
| the CBIC joint-model next-category column | open, does not reproduce from any committed artifact | **still open**, `LEFT_OUT.md` LO-2, `PENDENCIAS.md` §2.5 |
| the CoUrb sub-area selection rule | open, unrecorded | **still open**, `LEFT_OUT.md` LO-7 |
| the tuning budget for Ch.3/Ch.4 | NOT RECOVERABLE | unchanged, `PENDENCIAS.md` §2.6 |
| CA/TX "provisional" | raised, then **WITHDRAWN** | withdrawn stands. The flag read `stats_n20/RESULTS.md` §1b, which sits under a heading reading "(superseded)"; rev 4 is authoritative and its six-dataset Holm family rejects at all six. Recorded so it is not re-raised: **anchor on the revision header, not the first matching line** |

## G. Claims of the round corrected after this ledger

The ledger's own §"claims that do not reproduce" listed three. Five more were found and corrected
after it:

| claim | Corrected to | Who caught it |
|---|---|---|
| "make check: all gates pass", in six commit messages | The gate exited **2** for the whole round, on two false positives now exempted with their reasoning. Exits 0 as of `6ee23ca7` | source-ledger pass (L-1), independently confirmed by the LaTeX persona (E-1) |
| "the three builds are byte-identical ... same SHA" (`4e84cf7a`) | The PDFs are **not** byte-identical and their SHAs differ — pdflatex writes a creation timestamp and a document ID. What is identical byte for byte is the **extracted text layer**, which is what was actually measured | style pass |
| my Appendix B claim that a place's label "never enters its own representation" in Ch.3 | False. Reproduced on a 4-node graph: absent from the input feature (0.000), present in the embedding after one hop (0.667), because the graph is undirected and the convolution adds self-loops | domain panel (D-01) |
| `LEFT_OUT.md` LO-6, recording only the Ch.4 figure's label size | Both rasters are about 45 percent of body and are the two **smallest** in the document; the two the audit tracked are the two largest | visual pass (V-1) |
| my first test that the trapped-prose gate catches a reintroduced defect | **Invalid.** I copied the fixed PDF into the scratch tree, and the detector compares source against the rendered artifact, so it correctly found the sentence present and skipped. Rebuilt from the broken source, the gate fires exactly as designed | caught by me, recorded because the failure mode generalizes: a detector that compares source against a render must be tested against the render built **from that source** |

## H. Provenance of this addendum

Every row above rests on a check I ran in this session, not on another pass's report, **except** where
the "Who verified" column names the pass that found it — and in each of those cases I re-ran the
measurement myself before editing the document. The four numbers in table D were each read from their
source file or re-derived from the render. The 26 commit hashes cited in `CODEX_AUDIT.md`'s outcome
section were verified to resolve as commits in this repository. Where I could not verify something, it
is in table F as still open, with its owner.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
