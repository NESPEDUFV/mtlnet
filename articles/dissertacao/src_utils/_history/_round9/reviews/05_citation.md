# 05 · Citation auditor — Gate G2 (R1–R5), round 9

- **Persona:** `reviewers/05_citation_auditor.md` (citation-integrity gate, rules R1–R5). Fresh eyes:
  I wrote none of this text and read it cold.
- **Build commit:** `03b53d16`
- **Volume read:** `src/build/main.pdf`, **102 pp** (defense build). Bibliography occupies the pages
  from p. 82 (`References`) to the end; I extracted pp. 82–102 as text. `main_academico.pdf` (99 pp),
  `main_ppgc.pdf` (103 pp) and `main_extra.pdf` (20 pp) were **not** read — see UNFINISHED.
- **Date:** 2026-07-30.
- **Read first, in order:** `AGENT_GUARDRAILS.md` §0–§4b, `WRITING_LAW.md`, `GLOSSARY.md`,
  `NORTH_STAR.md` §4 (inherited errata), then the persona file.
- **No build was run.** No source, tracker or gate file was edited. This report is the only file I wrote.

## Commands run

Working directory `articles/dissertacao/` unless stated. Greps over LaTeX strip comment lines from the
**file** before matching, per §4b V4.

```bash
git rev-parse --short HEAD                                    # -> 03b53d16
wc -l AGENT_GUARDRAILS.md WRITING_LAW.md GLOSSARY.md NORTH_STAR.md src/references.bib
grep -c '^@' src/references.bib                               # -> 99 active entries
grep -rIn "bruna\|scarselli\|1312.6203\|2005605" .            # whole tree, any file type
grep -rn "velickovic\|velivckovic" src --include='*.tex' --include='*.bib'
# key-level cross-check (python, in src/): \cite key extraction with file-level comment strip,
# diffed against @-keys in references.bib and \bibitem keys in build/main.bbl and build/main-aux/main.bbl
# attribute check (python): api.crossref.org/works/<doi> for 25 entries; export.arxiv.org/api/query
#   for 1312.6203, 1609.02907, 1809.10341, 2509.12350, 2505.11239; api.datacite.org for the arXiv DOI;
#   api.openalex.org (api_key) for 10.1109/tnn.2008.2005605
# PDF text extraction (python, pypdfium2): pages 82-102 of build/main.pdf; reference-number sweep
for f in $(find src/chapters -name '*.tex'); do grep -vn '^[[:space:]]*%' "$f" | grep -in "venue"; done
```
Publisher fetch attempted for the one closed-access entry: `fetch_article_fulltext(10.1007/s11227-025-07643-7)`
→ `found: false`, `oa_status: closed`, Unpaywall "no OA location", Springer 404, Elsevier 403.

## Verdict

**GATE PASS, with one open content dependency (finding 2).** Nothing in the bibliography is fabricated
or unresolvable, no `\cite` key fails to resolve, no entry is orphaned, and every R4 erratum I could
check is fixed. The single item that keeps this from being unconditional is a sentence in Chapter 5
whose content claim rests on a paper nobody in this round could open.

## Coverage statement

**26 of 99 entries (26%) checked at the attribute level against a source of record opened this
session** — 25 via Crossref by DOI, plus `sun2025kgtb` via DataCite and the arXiv API after Crossref
returned 404 for its arXiv DOI. Chosen as: the three own-work entries, the two entries this run was
told to prioritise, every entry whose provenance comment claims an erratum or a correction, and all
journal entries carrying volume/issue/page fields (the fields where partial attribute corruption
hides). **Four citation sites audited for claim support**, each against a source opened this session.
**100% of the run's named priorities.** The 73 unchecked entries are named as unchecked; I do not
claim them.

---

## Priority (a) — `bruna2014spectral` and `scarselli2009gnn`, re-checked independently

Both identifiers are real and both resolve. I re-resolved them from scratch rather than reading the
round's ledger first:

- **arXiv:1312.6203** → title *Spectral Networks and Locally Connected Networks on Graphs*; authors
  Joan Bruna, Wojciech Zaremba, Arthur Szlam, Yann LeCun; `<published>` 2013-12-21; **no `journal_ref`**.
  Abstract, verbatim: "we propose two constructions, one based upon a hierarchical clustering of the
  domain, and another based on the spectrum of the graph Laplacian."
- **Crossref 10.1109/tnn.2008.2005605** → *The Graph Neural Network Model*, IEEE Transactions on Neural
  Networks, vol. 20, iss. 1, pp. 61–80, issued 2009-01, `journal-article`, **five** authors:
  F. Scarselli, M. Gori, Ah Chung Tsoi, M. Hagenbuchner, G. Monfardini. OpenAlex abstract, verbatim:
  "we propose a new neural network model, called graph neural network (GNN) model, that extends
  existing neural network methods for processing the data represented in graph domains."
  OpenAlex `publication_year` is **2008**; Crossref issues it as **2009**.

Both confirm what `src_utils/_history/_round9/36_source_ledger.md` records, including the five-author list and
the 2008/2009 discrepancy. **The finding is what the priority did not anticipate:** neither key exists
in `src/references.bib`, and neither is cited anywhere in `src/`. Whole-tree grep puts `bruna` and
`scarselli` in exactly three places — Germano's precedent dissertation under `exemples/` (different
keys: `bruna2013spectral`, `scarselli2008graph`), `src_utils/CONSIDERATIONS.md`, and the round-9
ledger. So **there is no citation of either work in the defense build to audit**, and the ledger's
"Not yet inserted — Wave B" is accurate. See finding 9 for the one thing a future insertion must fix.

**Is Chapter 2's sentence supported by each source?** The sentence the request points at is
`src/chapters/2_fundamentals.tex:143-145`: "The graph convolutional network combines a node's features
with those of its neighbors through a localized spectral rule \cite{kipf2017gcn}". That sentence cites
**Kipf**, not Bruna or Scarselli, and Kipf's own abstract (arXiv:1609.02907, opened this session)
reads "We motivate the choice of our convolutional architecture via a localized first-order
approximation of spectral graph convolutions." **SUPPORTED as it stands.** The prose is therefore not
waiting on Bruna/Scarselli to become true; GER-01 adds attribution depth, not correctness.

## Priority (c) — duplicate keys for one work: none survive

`velickovic2019dgi` and `velivckovic2018deep` appear **only** inside bib comments and the errata table.
All six prose sites use the single consolidated key `velickovic2019deep`
(`2_fundamentals.tex:158`, `3_cbic/method.tex:29`, `4_courb/related.tex:18`, `4_courb/methodology.tex:89`,
`5_mobiwac/01_introduction.tex:25`, `5_mobiwac/02_related.tex:38`, `5_mobiwac/04_method.tex:18`, plus
`tables/frame/lineage.tex:24`). A programmatic sweep for two entries sharing a normalized title, a DOI,
or an arXiv `eprint` returns **zero pairs** across all 99 entries. R4's DGI consolidation erratum is
**fixed**. Nothing to report at any severity.

## Cross-checks (persona §5) — all clean, stated as a result

- 99 entries defined, **99 distinct keys cited, 0 undefined, 0 orphans.**
- `grep -c "Citation.*undefined" src/build/main.log` → **0**. `main.blg` carries no warning lines.
- Rendered bibliography numbers **[1] through [99] with no gaps** and no duplicate numbers (swept from
  the extracted text of pp. 82–102).
- **R5:** no AI output cited anywhere. The round's own ledger records refusing a Semantic Scholar
  machine-generated TLDR for `wang2025hamtl` on R5 grounds; I found no citation laundering a model
  claim. Clean.
- **R4 errata:** `capanema2023poirgnn` (replaces the wrong POI-RGNN paper) present and DOI-confirmed
  (Ad Hoc Netw. 138:103016, 2023); `chen2020modeling` five authors incl. Yang Liu, TKDE 34(4):1902–1914
  2022, DOI-confirmed; GAT cited as ICLR 2018 with the arXiv id in a note; `silva2025mtlnet` venue reads
  *Anais do XVII Congresso Brasileiro de Inteligência Computacional* and carries no "Submetido" note —
  both halves of the CoUrb erratum fixed, Crossref-confirmed; `misra2016cross` DOI is `.433`
  (Crossref: Cross-Stitch Networks, CVPR 2016, pp. 3994–4003) not the donor's `.434`;
  `zhang2021survey` DOI `10.1109/TKDE.2021.3070203` resolves to TKDE 34(12):5586–5609 2022. **No
  unfixed erratum found.**

## Claim-support audit (4 sites)

| Site | Verdict |
|---|---|
| `2_fundamentals.tex:143-145` → `kipf2017gcn` | **SUPPORTED** — arXiv:1609.02907 abstract, "localized first-order approximation of spectral graph convolutions". |
| `2_fundamentals.tex:156-158` → `velickovic2019deep` | **SUPPORTED** — arXiv:1809.10341 abstract, "maximizing mutual information between patch representations and corresponding high-level summaries of graphs", unsupervised. The prose's "local patch representations and a global graph summary" tracks the source's own wording without overstating it. |
| `5_mobiwac/02_related.tex:94` → `wang2025hamtl` | **UNSUPPORTED IN SESSION** — see finding 2. |
| `2_fundamentals.tex:159-161` → `huang2023hgi` | **NOT VERIFIED.** Crossref carries no abstract for `10.1016/j.isprsjprs.2022.11.021` and I did not reach the publisher page inside the checkpoint. I make no claim either way. |

---

# Findings

## 1. SHOULD-FIX — `moura2025mobilityaware` booktitle contradicts the entry's own verification note

**WHERE:** `src/references.bib:761` (field); `src/references.bib:747` (the note it contradicts);
renders in `main.pdf` p. 88, reference [93].

**WHAT:** the field, verbatim:
```
  booktitle = {Proc. IEEE/ACM MSWiM},
```
The entry's own provenance comment, verbatim (`references.bib:747-748`): "the container title carries
no \"IEEE\" prefix, per the PDF header and Crossref". Crossref for
`10.1109/MSWiM67937.2025.11308734` returns `container-title` = **"2025 International Conference on
Modeling, Analysis and Simulation of Wireless and Mobile Systems (MSWiM)"** — no "IEEE", no "ACM".
The PDF renders "In: **Proc. IEEE/ACM MSWiM**. [S.l.: s.n.], 2025. p. 667–674."

**WHY:** R2 (attribute fidelity): "venue … copied from the source of record". This is also the §4b V6
pattern — a value was corrected in the comment and the field it describes kept the old string, so the
entry documents its own defect and ships it anyway.

**FIX:** either set `booktitle = {Proc. MSWiM}` (matching the note and Crossref) or, if the author
prefers to keep a sponsor prefix as a house convention for readability, amend the comment so the entry
stops asserting the opposite. **The choice of convention is the author's;** the contradiction is not.

## 2. SHOULD-FIX — a content claim about `wang2025hamtl` is unflagged, and its source was unreachable again this round

**WHERE:** `src/chapters/5_mobiwac/02_related.tex:92-95` (the only citing site in the whole document —
key-level sweep returns exactly one). Bib entry `src/references.bib:1153`; its verification note
`src/references.bib:1149-1152`.

**WHAT:** the citing sentence, verbatim:
> "MCARNN \cite{Liao2018} jointly predicts activity and
> location, and a recent hierarchy-aware model continues the
> pattern \cite{wang2025hamtl}; in both, the location target is
> the exact place."

**WHY:** the sentence asserts two facts *about the content* of `wang2025hamtl` — that it is
hierarchy-aware, and that its location target is the exact place. R1(c) requires the cited claim to be
located in the source. This round could not open the source: I re-attempted independently of the
round's own attempt and got `found: false`, `oa_status: closed`, Unpaywall "no OA location", Springer
404, Elsevier 403. `36_source_ledger.md` §2 records the same wall (Springer key 401 on four endpoints,
`link.springer.com` redirecting to an authentication gate) and an **unresolved author-count
disagreement** (OpenAlex 6, Semantic Scholar 7). Attributes are sound — Crossref gives exactly the
committed seven-author list, *The Journal of Supercomputing* 81(11), 2025 — so this is **not** a
fabrication finding and the entry is admissible under R1's donor-carry provision, which lets it inherit
the MobiWac campaign's dated 2026-07-06 firsthand reading.

The finding is the **flagging gap** this run was asked to check. The round's ledger concludes that the
*absence* claim in §2.3 (FAB-28) is blocked and correctly declines to re-assert it. But the §5 sentence
above already rests on the paper's content, it carries no `[VERIFY]`, and the bib comment states
"Verified against the Springer article page, 2026-07-06" — so a reader of the bibliography is told the
work is verified while the current round's own ledger says its abstract was never obtained. The two
records disagree with nothing to signal it.

**FIX:** three options, author's call. (i) Preferred: get the publisher PDF through institutional
access and locate the two asserted facts, then the sentence stands unchanged and the ledger closes.
(ii) Weaken to what the title alone supports — a hierarchy-aware multi-task model for user location
prediction — and drop "in both, the location target is the exact place" for HAMTL, keeping it for
MCARNN where `Liao2018` is open. (iii) Keep the sentence and add a `[VERIFY: wang2025hamtl content not
re-verified; entry inherits a 2026-07-06 reading]` marker at the site so the two records stop
disagreeing. **Do not** resolve it from the Semantic Scholar TLDR — R5 bars it, and the ledger was
right to refuse.

## 3. SHOULD-FIX — `Xu2023` renders an article number as a page number

**WHERE:** `src/references.bib:1246`; renders in `main.pdf` p. 82, reference [4].

**WHAT:** the entry carries `pages = {112}` alongside `articleno = {112}` and `numpages = {24}`. It
renders, verbatim from the PDF: "ACM Trans. Inf. Syst., v. 41, n. 4, **p. 112**, 2023." Crossref for
`10.1145/3582553` gives `page` = **"1-24"**. Article 112 is not page 112.

**WHY:** R2 — page range copied from the source of record. As rendered, a reader looking for page 112
of TOIS 41(4) will not find the paper.

**FIX:** `pages = {1--24}` (Crossref), keeping `articleno = {112}`. This is exactly what the sibling
entry `zhu2022drrgnn` does — it carries `articleno = {116}` with `pages = {1--23}` and renders
correctly as "v. 16, n. 6, p. 1–23, 2022".

## 4. SHOULD-FIX — `wang2025hamtl` renders with no page or article locator

**WHERE:** `src/references.bib:1153-1161`; renders in `main.pdf` p. 87–88, reference [96].

**WHAT:** rendered verbatim: "Hierarchy aware-based multi-task learning for user location prediction.
The Journal of Supercomputing, **v. 81, n. 11, 2025.**" Nothing stands between "n. 11" and "2025".
The entry has `articleno = {1196}` and **no `pages` field**; `abntex2-num.bst` does not emit
`articleno` on its own. Only 4 DOI strings appear anywhere in the rendered bibliography, so the DOI
does not compensate.

**WHY:** R2, and practically: this is the one reference in the volume a reader is most likely to want
to check (finding 2), and it is the one with the least locating information printed.

**FIX:** add `pages = {1196}` beside the existing `articleno`, per the `Xu2023`/`zhu2022drrgnn`
pattern. Verify by rebuild — I did not rebuild.

## 5. NIT — `sun2024mcmg` year: 2024 (bib) vs 2023 (Crossref issued)

**WHERE:** `src/references.bib:1033-1043`; renders p. 88, reference [94], as "v. 42, n. 1, p. 1–28, **2024**".

**WHAT:** bib `year = {2024}`; Crossref `10.1145/3592789` returns `issued` = **2023**, with volume 42,
issue 1, page 1-28. Both values reported as required.

**WHY / FIX:** TOIS 42(1) is the January-2024 issue and Crossref's `issued` is the online-first date,
so the entry's value is the issue year — the same convention the bibliography already applies
deliberately at `yang2015tsmc` (bib 2015, OpenAlex 2014, flagged in-comment) and would apply at
`scarselli2009gnn` (Crossref 2009, OpenAlex 2008). **No change needed if the convention is
deliberate;** if so, the entry should say so in its comment as its two siblings do. Author's call.

## 6. NIT — two `[VERIFY]` tokens ship inside the bibliography, both already resolved in the same comment

**WHERE:** `src/references.bib:1178` (`wilcoxon1945`) and `src/references.bib:1259` (`yang2015tsmc`).

**WHAT:** verbatim, `references.bib:1178`: "%   [VERIFY] OpenAlex truncated last_page to 80; canonical
Biometrics Bull. 1(6):80-83 confirmed via issue". And `references.bib:1259`: "%   [VERIFY] DOI
10.1109/TSMC.2014.2327053; OpenAlex publication_year=2014 (online-first), issue year 2015 (vol 45 no 1)".
Each sentence resolves its own flag. I confirmed both independently: Crossref returns
`page` = "80" for `10.2307/3001968` (truncated exactly as described) and 45(1):129–142, issued 2015,
for the TSMC DOI — the committed fields are right in both entries.

**WHY:** `36_source_ledger.md` §4 states "The number that matters for the handoff: **1 open
`[VERIFY]`**". A grep for `[VERIFY]` in the shipped bib returns **three** hits, so the next auditor
either re-does this work or reports a false count. Stale marker, not a defect in a reference.

**FIX:** rewrite both as `RESOLVED:` (or `verified:`) notes keeping the identical explanatory text, so
the token count matches the ledger's claim.

## 7. NIT — one co-author appears under three name forms

**WHERE:** `src/references.bib:951` (`silva2025mtlnet`), `:788` (`paiva2026stmtlnet`), and the
`santos2024urban` entry at the end of the file.

**WHAT:** "Germano B. Santos", "Germano B. dos Santos", "Germano Barcelos dos Santos". Each is
defensible against its own source of record — Crossref for the CBIC DOI returns "Germano Santos",
Crossref for the CoUrb DOI returns "Germano B. dos Santos", and the precedent dissertation's title
page gives the full form. The printed bibliography therefore lists one person under two surnames
("SANTOS, G. B." and "SANTOS, G. B. dos").

**WHY:** R2 is satisfied literally; consistency is not. This is a presentation judgment, **the
author's to settle** — he knows how his co-author cites himself.

**FIX:** if unifying, "Germano B. dos Santos" is the form the person's own first-author records use.

## 8. NIT — stale `build/main.bbl` carries a phantom 100th reference; the shipped PDF is clean

**WHERE:** `src/build/main.bbl:385-390` (mtime Jul 29 16:11, **100** `\bibitem`s) versus
`src/build/main-aux/main.bbl` (mtime Jul 30 04:50, **99** `\bibitem`s, no Maninis).
`src/build/main_academico.bbl` has the same 100.

**WHAT:** the stale file renders `\bibitem{maninis2019attentive}` — "MANINIS, K.-K.; RADOSAVOVIC, I.;
KOKKINOS, I. Attentive single-tasking of multiple tasks…" — and the matching stale `build/main.aux`
numbers it `[65]`. The entry is deliberately commented out in `references.bib` (retired under COD-015d,
with the at-sign written `(at)` so BibTeX cannot see it) and is cited nowhere.

**WHY / FIX:** **no document defect.** The live build reads `build/main-aux/`, and I confirmed against
the PDF itself: a text sweep of pp. 82–102 for "MANINIS" returns zero hits, [65] is GAMBS et al., and
numbering runs 1–99 with no gaps. Neither stale file is tracked by git. Recorded only because an
auditor who greps `build/main.bbl` — the obvious path — gets a phantom entry and 100 shifted numbers.
Deleting the two untracked stale artifacts would remove the trap; I did not touch them (read-only).

## 9. NIT — forward-looking: `bruna2014spectral`'s key and year are not supported by the record that was opened

**WHERE:** not in the document. `src_utils/_history/_round9/36_source_ledger.md` §1 and
`src_utils/CONSIDERATIONS.md` §4, for the pending GER-01 insertion.

**WHAT:** the key says 2014 and the ledger's attribute line says "arXiv:1312.6203v3 … v3 2014-05-21",
but the arXiv record carries **no `journal_ref`** and `<published>` 2013-12-21. The ledger's own
`[VERIFY]` says it: "Cite as ICLR 2014 only if the ICLR record is opened". I could not confirm the
v3-2014 date either — my query returned a feed-level timestamp, not the version date, so **I verified
the base record only and claim nothing about v3**.

**WHY:** R1(a)+(b) — the year would be the one attribute in the entry tracing to nothing opened.

**FIX:** before insertion, either open the ICLR 2014 record and cite the conference version, or name
the entry for what was opened (`bruna2013spectral`, `year = {2013}`, `eprint = {1312.6203}`) — which is
also the key Germano's own precedent dissertation uses. For `scarselli2009gnn`, 2009 is correct and
its five-author list is confirmed; no change needed there.

---

## Per-entry results (26 checked against a source of record opened this session)

**OK — attributes match the source of record:** `chen2020modeling`, `zhang2021survey`, `wilcoxon1945`,
`yang2015tsmc`, `huang2024cslsl`, `silva2025mtlnet`, `paiva2026stmtlnet`, `misra2016cross`,
`Halder2022`, `Halder2021`, `zhu2022drrgnn`, `capanema2023poirgnn`, `li2025rehdm`, `sun2024transtarec`,
`kokkinos2016ubernet`, `lakens2017tost`, `yu2020catdm`, `ye2013nextmove`, `lin2021ctle`,
`luca2021mobilitysurvey`, `sun2025kgtb` (Crossref 404s on the arXiv DOI; DataCite confirms publisher
arXiv, 2025, creators Sun/Xu, title matches, and the arXiv record still shows no `journal_ref`, so the
entry's "preprint" framing is right), `wongso2025massivesteps` (arXiv record confirms three authors and
no `journal_ref` — still a preprint, as the entry says), `kipf2017gcn`, `velickovic2019deep`.

**CORRECTED-ATTRIBUTES (correction specified, author applies):** `Xu2023` (finding 3),
`moura2025mobilityaware` (finding 1), `sun2024mcmg` (finding 5, if not a deliberate convention).

**UNVERIFIABLE:** `wang2025hamtl` — attributes verified, **content not obtainable** (finding 2).

**Not checked, and not claimed as verified (73 entries),** including `holm1979` (no DOI in the entry;
I did not look for one), `pedregosa2011sklearn`, `kohavi1995crossval` (the round's ledger also declines
to re-claim it), `baxter2000model`, `caruana1997multitask`, `song2010limits`, `cho2011gowalla`,
`huang2023hgi`, and every `_bib/new_references_ch2.bib` donor entry carrying an arXiv `eprint` but no DOI.

## `[VERIFY]` list for the author

1. `wang2025hamtl` — content of the paper, for `5_mobiwac/02_related.tex:94`. **The only substantive
   open item.** Needs institutional access to the publisher PDF.
2. `bruna2014spectral` — the ICLR-2014 form, before GER-01 inserts it (finding 9).
3. `huang2023hgi` — the HGI claim at `2_fundamentals.tex:159-161` was **not** checked by me; Crossref
   carries no abstract. Not a flag against the entry, a gap in my coverage.

## COUNTS

**blockers 0 / should-fix 4 / nits 5**

## UNFINISHED

1. **73 of 99 entries were not checked at the attribute level.** I sampled 26% by the criteria in the
   coverage statement; R3's ≥20% floor is met for a handoff sample but this is not a full-bibliography
   audit.
2. **Claim-support sampling reached 4 sites, far short of R3's ≥20% of citation sites.** The document
   has 99 distinct cited keys with 38 keys cited exactly once. Chapter 2 §2.3 alone (MTL, the
   Pareto/balancer paragraphs at `2_fundamentals.tex:388-548`) carries roughly 30 citation sites,
   including the newly added Pareto material this round was told about, and **I audited none of them**.
   That is the largest gap in this report and the place I would send the next pass first: the
   Pareto-stationarity attributions at lines 431–448 (`sener2018mgda`, `nash`, `liu2021cagrad`,
   `senushkin2023aligned`, `yu2020pcgrad`) are exactly the strength-drift shape R3 targets — a
   guarantee stated for convex losses becoming a claim about a deep network.
3. **Only `main.pdf` (102 pp) was read.** `main_academico.pdf` (99 pp), `main_ppgc.pdf` (103 pp) and
   `main_extra.pdf` (20 pp) were not opened; `main_academico.bbl` shares the stale-100 defect of
   finding 8 but I did not verify its rendered numbering.
4. **`huang2023hgi` claim support** — see `[VERIFY]` 3.
5. **Self-citation posture** (persona §5, last clause) was not audited — I did not read the
   introduction's framing of the three own papers for whether the delta over prior own work is stated
   once and never as the intro's sentence subject.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
