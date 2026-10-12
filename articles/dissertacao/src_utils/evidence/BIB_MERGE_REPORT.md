# BIB_MERGE_REPORT — Phase-4 global bibliography merge (2026-07-23)

Target: `articles/dissertacao/src/references.bib`. Universe: every `\cite` key in the nine
`chapters/*.tex` files (112 distinct keys before consolidation). After consolidation the file
holds **99 entries**; the cited-key set and the bib-key set are identical (0 dangling cites,
0 unused entries). Zero duplicate keys (checked by regex over the written file).

## 1 · Key mapping (old -> canonical; every chapter edit logged)

Consolidation rule: the key the majority of chapters use wins (fewest edits). 22 `\cite`
edits were applied across the chapter files; every one is listed below.

| Old key | Canonical key | Work | Chapter edits (file:line) |
|---|---|---|---|
| `velivckovic2018deep` | `velickovic2019deep` | Deep Graph Infomax (ICLR 2019) | 3_cbic.tex:124 |
| `velickovic2019dgi` | `velickovic2019deep` | (same; DGI triple-key, CBIC ERRATA #8) | 5_mobiwac.tex:47, 106, 229 |
| `navon2022nashmtl` | `nash` | Nash-MTL (ICML 2022) | 2_fundamentals.tex:314; 5_mobiwac.tex:177 |
| `huang2023learning` | `huang2023hgi` | HGI (ISPRS 2023) | 4_courb.tex:55, 169, 190 |
| `lim2022hmtgrn` | `Lim2022` | HMT-GRN (SIGIR 2022) | 5_mobiwac.tex:147, 353, 570 |
| `Cho2011` | `cho2011gowalla` | Cho et al. 2011 (KDD, Gowalla) | 3_cbic.tex:44, 235 |
| `cho2011friendship` | `cho2011gowalla` | (same; triple-key) | 4_courb.tex:18 |
| `SNAP2014` | `jure2014snap` | SNAP dataset collection | 3_cbic.tex:44 |
| `mai2023sphere2vec` | `mai2023sphere2vecgeneralpurposelocationrepresentation` | Sphere2Vec | 1_introduction.tex:50 |
| `zhang2020interactive` | `Zhang2020` | iMTL (IJCAI 2020) | 3_cbic.tex:30 |
| `paiva2026courb` | `paiva2026stmtlnet` | ST-MTLNet (CoUrb 2026) | 5_mobiwac.tex:97 |
| `church2017word2vec` | `mikolov2013word2vec` | skip-gram / word2vec (ERRATA #6) | 4_courb.tex:175 |
| `yu2019mmoe` | `ma2018mmoe` | MMoE (KDD 2018; ERRATA #7, see §3) | 3_cbic.tex:83 |
| `10.1145/2661829.2662002` | `liu2014geographical` | Liu et al. 2014 (CIKM) — raw-DOI key with slashes renamed | 4_courb.tex:226 |

Sphere2Vec direction note: the long key `mai2023sphere2vecgeneralpurposelocationrepresentation`
is the majority key (4 cites in Ch.2/Ch.4 vs 1 in Ch.1) and the only key a donor bib holds, so
Ch.1's short key was mapped onto it (the frame-integration report anticipated an alias; the
majority rule points the other way, and one edit beats four).

Donor keys renamed on entry (content-level, no chapter edit needed):
`zeng2019mhape` (MobiWac) -> `zeng2019next` (the key Ch.3 cites);
`kurin2022defense` (MobiWac) -> `kurin2022scalarization` (the key Ch.2 cites);
`chen2020hmrm` (MobiWac) -> `chen2020modeling` (the key Ch.3 cites).

Nash-MTL slash-key note: the merge instructions mention a Nash-MTL key spelling containing a
slash. No such key exists in the current chapter tree or donor bibs; the only slash-bearing key
found anywhere was the raw-DOI key `10.1145/2661829.2662002` (renamed, above). Recorded here so
the search is not repeated.

## 2 · Provenance summary (99 entries)

| Source | Entries |
|---|---|
| `articles/[mobiwac]/src/references.bib` (verified template, R1-preferred) | 44 |
| `../science/fundamentals/_bib/new_references_ch2.bib` (identifier-verified) | 21 |
| `articles/CBIC___MTL/references.bib` (only chapter-cited keys) | 20 |
| `articles/CoUrb_2026/src_en/references.bib` (only chapter-cited keys) | 14 |

Every entry carries a `% PROVENANCE:` comment; MobiWac entries keep their original
`% verified:` quotes. 19 entries carried from a donor without an identifier had a DOI or arXiv
id **added and resolved this session** (Crossref / arXiv API; each entry's comment names the
record): Halder2021, baxter2000model, belkin2003laplacian, du2019beyond, feng2017poi2vec,
grover2016node2vec, huang2022estimating, lakens2017tost, lin2021ctle, liu2016strnn, liu2019dwa,
perez2018film, rahmani2019category, sener2018mgda, sitzmann2020implicit, sun2020go,
sun2024transtarec, vaswani2017attention, wu2024torchspatial. Entries still without a DOI-class
identifier after the merge carry an arXiv id, a publisher URL, or (holm1979, a 1979 Scand. J.
Statist. article with no registered DOI) a full journal record; none is identifier-free AND
unverifiable.

The frontier set (`new_references_frontier_decollided.bib`) contributes **0 entries**: no
chapter currently cites any of its keys (donor rule 2 conditions inclusion on actual cites).

## 3 · R4 errata applied in the bib (each entry carries an ERRATUM comment)

1. **POI-RGNN** — `capanema2023poirgnn` taken from the MobiWac verified donor; the ERRATA
   `[VERIFY at adaptation]` flag is **RESOLVED this session**: Crossref record for
   10.1016/j.adhoc.2022.103016 opened (Ad Hoc Networks 138:103016, 2023; Capanema, de
   Oliveira, Silva, Silva, Loureiro; title "Combining recurrent and Graph Neural Networks to
   predict the next place's category"). Matches the donor entry.
2. **HMRM / `chen2020modeling`** (CBIC ERRATA #2) — authors corrected per the Crossref source
   of record to **five** authors (Meng Chen, Yan Zhao, Yang Liu, Xiaohui Yu, Kai Zheng); type
   `@article`, TKDE **34(4):1902-1914, 2022**, DOI 10.1109/TKDE.2020.3001025. Note: the ERRATA
   table's row says "34(10):4829-4841, year 2020" and omits Yang Liu — the Crossref record
   (opened this session) governs; the MobiWac donor agreed on vol/pages but also lacked Yang
   Liu, restored here. **The ERRATA #2 row itself should be corrected by the author.**
3. **GAT / `velivckovic2017graph`** (ERRATA #3) — now the ICLR 2018 version of record; arXiv id
   kept as a note.
4. **Cross-Stitch / `misra2016cross`** (ERRATA #4) — DOI 10.1109/CVPR.2016.433; the donor's
   .434 was re-checked this session and indeed resolves to a different paper (Deep Metric
   Learning via Lifted Structured Feature Embedding).
5. **`zhang2021survey`** (ERRATA #5) — DOI 10.1109/TKDE.2021.3070203; the donor DOI
   10.1109/TKDE.2021.3072953 returns 404 on Crossref (re-checked this session).
6. **`church2017word2vec` -> `mikolov2013word2vec`** (ERRATA #6) — Ch.4:175 cite updated; the
   Church commentary entry is not carried.
7. **`yu2019mmoe`** (ERRATA #7) — **confirmed not a distinct resolvable work and dropped**: its
   claimed arXiv id 1904.01038 resolves to "fairseq: A Fast, Extensible Toolkit for Sequence
   Modeling" (Ott et al.) — checked via the arXiv API this session. The Ch.3:83 cite
   `\cite{ma2018mmoe,yu2019mmoe}` was consolidated to `\cite{ma2018mmoe}` (the sentence
   describes MMoE, which ma2018mmoe fully supports).
8. **DGI triple-key** (ERRATA #8) and **Nash-MTL double-key** (ERRATA #9) — consolidated, §1.
9. **`silva2025mtlnet`** (CoUrb ERRATA #3) — venue = Anais do XVII Congresso Brasileiro de
   Inteligência Computacional (CBIC 2025), DOI 10.21528/CBIC2025-1191324, pp. 1-8, no
   "Submetido" note. Seed `[VERIFY]` **RESOLVED**: author list confirmed against the Crossref
   record this session (Silva, Almeida, Paiva, Santos, Silva, Sousa — the seed's 3-author list
   was wrong and is replaced).
10. **`paiva2026stmtlnet`** — seed `[VERIFY]` **RESOLVED** against Crossref
    10.5753/courb.2026.22960: the seed entry was missing 3rd author **Germano B. dos Santos**;
    restored. Pages 323-336 confirmed.
11. **`standley2020tasks`** (found during identifier work, not in any ERRATA file) — the CBIC
    donor gave CVPR as the venue; OpenAlex (keyed request, this session) records the work as
    **ICML 2020**; venue corrected, arXiv:1905.07553 noted, unverifiable CVPR page range
    dropped. Candidate for the CBIC ERRATA list.

## 4 · Unresolved / flagged items

- **None dangling**: all 99 cited keys resolve; no entry was invented. Three benign
  `[VERIFY]` caveat comments are inherited verbatim from the Ch.2 donor's own verification
  notes (kohavi1995crossval: DOI is a Zenodo re-deposit of the DOI-less IJCAI'95 paper;
  wilcoxon1945: OpenAlex truncated the page range, canonical 1(6):80-83 used; yang2015tsmc:
  online-first 2014 vs issue-year 2015). They record verification detail, not open questions;
  no entry is unverified.
- **ERRATA-file corrections suggested to the author** (the bib is right; the registries lag):
  CBIC ERRATA #2's vol/number/pages/year row for HMRM repeats the pre-correction values and
  omits Yang Liu (see §3.2); ERRATA #9's "slash" description matched no live key (see §1);
  `standley2020tasks` venue defect is new (§3.11).
- **Claim-support audit (R3) not performed here**: this merge verified existence and
  attributes (R1/R2). The ≥20%-sample sentence-level audit remains for the pre-handoff
  adversarial pass.

## 5 · Compile state (2026-07-23)

`make defense` (TeX Live 2026 basic, `TEXMFHOME=/Users/vitor/Library/texmf`,
`abntex2cite [num]` + `abntex2-num.bst`) compiles clean: **main_defense.pdf, 83 pages**;
**0 undefined citations**, **0 BibTeX errors**, **0 BibTeX warnings**, **0 LaTeX errors**;
99 `\bibitem`s emitted. Build-machine repairs needed (environment, not source): the usermode
tree at `/Users/vitor/Library/texmf` was missing `abntex2`, `newtx`, `kastrup`, `tex-gyre`,
and `txfonts` — installed via `tlmgr --usermode install` with a writable `TEXMFVAR`, then
`updmap-user`. One bib-format lesson recorded: BibTeX treats a bare `@` inside `%` comment
lines as an entry start, so provenance comments must not contain `@`-prefixed words.
Remaining LaTeX warnings are the pre-existing cosmetic set (2 hyperref token-in-PDF-string,
2 deprecated `brazil` babel name, 2 memoir header-height, 4 pdfTeX `Hfootnote` dest, 1
floats-only page) — none is bibliography-related.
