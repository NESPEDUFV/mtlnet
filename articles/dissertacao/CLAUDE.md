# CLAUDE.md — Dissertação de Mestrado (UFV / PPGCC) — working folder

> **What this folder is.** The working folder for Vitor H. O. Silva's **master's dissertation** at
> UFV / PPGCC (Ciência da Computação, Campus Florestal / NESPeD-LAB), advisor Fabrício A. Silva.
> Format: **coletânea de artigos** (UFV Normas §2.3(iii)/§2.6), **English frame**.
> **Status: DEFENDED AND APPROVED 2026-08-28. Now DEPOSITING.** The text is frozen; changes reach it
> only as erratas, at the final deposit.
>
> 🔴 **DEPOSIT DEADLINE: 2026-11-28** — "Enviar" must happen by then; three months after the
> defense, monthly fine afterwards, and the portal states the date itself.
>
> **The clock SUSPENDS at "Enviar"** while the advisor reviews, so his turnaround does not consume the
> window. **But if he rejects, the suspension collapses and the count runs from the defense date** —
> retroactively, straight into a fine if it happens late. **The binding risk is a formal rejection,
> not a slow advisor**. An informal advisor read before "Enviar" was proposed and **declined by the
> author (2026-09-29)**: the advisor already read the text and his remarks came in with the banca's
> and are applied, so what remains is touch-ups. Verbatim clauses: `UFV_COMPLIANCE.md` §4 item 7.
>
> Remaining sequence: decisions → apply → rebuild → re-attach → re-emit the RASCUNHO → full manual
> pass → BBT (~7 days) → attach the ficha → "Enviar" → advisor → PPG.
>
> *This deadline was absent from every governance document in this folder until 2026-09-29, when
> the project resumed after twenty days with no commits. The first version of this block, written
> that same day, framed the advisor's unmeasured turnaround as the constraint — built on the
> compliance doc's half-quoted rule. The `academico` session read the manual and found the
> suspension clause; corrected within the hour, and the manual re-read here before trusting it.*
>
> Title, exactly as the folha de rosto prints it:
> *Multitask Learning for Point-of-Interest Classification and Prediction Tasks: The Role of the
> Check-in-Level Representation.*

---

> **Before this section: [`VEREDITOS.md`](VEREDITOS.md).** It answers the recurring questions by
> question ("does chapter 3 leak?", "is RESULTS_BOARD usable?", "can `_round*` be deleted?"), each
> closed with proof. Anything under a leading-underscore directory (`_round*`, `_review*`,
> `_specialists*`, `_archive`) is a **closed round with no authority** — provenance for what was
> discussed, never a source for a current fact.

## 0 · Read this section before you write any number

The recurring failure in this project has never been the science. It is **pulling a number from the
wrong generation of the experiment**, or from the wrong one of two volumes that both have an
"Appendix B". Three rules, and then the map.

> **Rule 1 — the delivered numbers are v18, joint-best convention. Nothing else.**
> **Rule 2 — a next-category macro-F1 outside 30–38 is a leaked pre-v18 number. Stop.**
> **Rule 3 — "Appendix B" is ambiguous in this project. Always say *of which volume*.**

### 0.1 · Where the delivered numbers come from

| what you want | the ONE source | not this |
|---|---|---|
| any printed cell of Ch. 5 | the table file itself, `src/tables/mobiwac/*.tex` — each value carries its provenance in a comment beside it, and that comment is what the fact gate follows | never re-derive from a JSON without reading the comment first |
| joint (multi-task) per-fold cells | `docs/results/closing_data/v18/joint_best_perfold.json`, `cells['<state>_s<seed>_joint'].folds[<fold>].joint_best` | `V18_RESULTS.md` §1 — it tabulates **diag-best**, a different and more flattering convention |
| dedicated (single-task) per-fold cells | `docs/studies/closing_data/v18/data/v18_results.json`, `per_run[].stl_cat_folds` / `stl_reg_folds` | — |
| full-precision ladder (all statistics) | `wrapup/evidence/ladder_recompute.json` — the only file in the repo carrying more than two decimals | — |
| the aggregation rule | mean the 5 folds inside a seed, **then** mean the 4 seeds. The printed ± is the sd **across the 4 per-seed means**, not across folds | — |
| CBIC (Ch. 3) / CoUrb (Ch. 4) numbers | the published tables in `../CBIC___MTL/` and `../CoUrb_2026/` — reproduce, never recompute | — |

**`docs/studies/closing_data/RESULTS_BOARD.md` is DEAD for this dissertation.** It calls itself a
single source of truth, and it is one — for **v17**, whose category cells are leak-inflated by 25–45
points (it prints AL 63.56 / FL 79.85 / CA 77.05 against the delivered 30.59 / 37.55 / 35.63). It
was last touched 2026-07-20 and never mentions v18. If any document still routes you there,
**this table wins.** (`AGENT_GUARDRAILS.md` §N1 was repointed on 2026-08-20, commit `401c45ab`, and
now warns against the board itself; until 2026-10-02 this paragraph still called that pointer stale.)

### 0.2 · Why the generation matters so much

`v18` closed a label leak in the consecutive-visit graph (it is now forward-only, `src < tgt`, in
training *and* at readout). At Alabama the leak was worth **28.63 macro-F1**. That is why every
category number moved so far, and why the range check in Rule 2 works. Region barely moved (< 2 pp),
so **the range check does not protect the region axis — check the file path instead.**

Methodology of record: `docs/studies/closing_data/v18/METHODOLOGY.md`; the frozen recipe (author-
approved 2026-08-09): `docs/studies/closing_data/v18/FINAL_SETTINGS.md`.

> ⚠ **A bare `python scripts/train.py --task mtl` does NOT reproduce this dissertation.**
> Since 2026-09-08 `DEFAULT_CANON` is `v18` (it was `v17`, on the leaked substrate), so a bare run no
> longer lands on a leaked build — but it still does not reproduce a delivered cell: `--cat-lr` is
> per state, fp32 is env-only, and the reported seeds are {0,1,7,100}. To reproduce a
> delivered cell, copy the command verbatim from `cell_joint()` in
> `docs/studies/closing_data/v18/run_wave.sh`. Ignore the B9 recipe block in the repo-root
> `/CLAUDE.md`; it is three generations old.

### 0.3 · The delivered verdict ladder — the exact wording the law allows

| axis | verdict |
|---|---|
| **next-category** | **outperforms at Florida only** (+0.19, Holm *p* 0.011). The other five differences are **unresolved** — never "matches", never "empata", never "everywhere". |
| **next-region** | **non-inferior at all six** (TOST at the registered 2-point margin), with **Texas +1.21** (Holm *p* 0.00013) and **California +1.06** (*p* 0.0000063) **outperforming**. |

The equivalence margin is registered for the **region** axis only; category equivalence is expressed
as the derived bound "within half a point". Word-level law: [`WRITING_LAW.md`](WRITING_LAW.md) §3.

> ⚠ **Este aviso apodreceu e foi corrigido duas vezes no mesmo dia, 2026-09-08. Leia a segunda.**
>
> **O que dizia (v1):** que o `NORTH_STAR.md` carregava a escada superada nas **linhas 26, 43, 175,
> 330 e 394**. Os cinco números apontam hoje para outro conteúdo — o ficheiro cresceu. Verdadeiro, e
> é a lição sobre citar por número de linha.
>
> **O que a v2 acrescentou, e estava errado:** *"nenhuma dessas quatro frases existe no ficheiro
> (0 ocorrências de cada)"*. **Existem.** Medido: `category everywhere` **2×**, `region at four of
> six` **2×**, `+28` **2×**.
>
> **O que se passa de facto, e é o oposto de um problema.** O `NORTH_STAR.md` **já foi tratado, a
> 2026-08-20**, e pelo padrão exacto que este projecto adoptou: as frases ficam, marcadas. Tem um
> banner no topo com a tabela do veredicto ENTREGUE, seguido de *"Onde aparecer `+28…+40 macro-F1`,
> `category everywhere` ou `region at four of six`, é a tese de quando o arco foi desenhado — não o
> resultado entregue"*; e a ocorrência no corpo leva `[SUPERADO 2026-08-20]` ao lado, com a razão de
> não se reescrever o corpo: **apagaria o registo de qual era a tese na altura**.
>
> ⚠ **Consequência para quem lê: ao encontrar uma dessas frases no `NORTH_STAR`, NÃO é contaminação
> nova e NÃO se corrige apagando.** As marcas são o mecanismo. Quem acreditasse na v2 leria uma
> ocorrência marcada como defeito e "consertá-la-ia" destruindo o registo histórico — que é o dano
> que a v1 nunca teria causado. **Um guarda superado engana quem o lê e quem o obedece.**
>
> **A regra de fundo, sem ponteiros:** o `NORTH_STAR.md` é documentação de **receita** e é citado por
> dezenas de scripts vivos; os seus números de resultado são de gerações anteriores. **Não copie um
> número dali para texto entregue** (os entregues estão em `docs/studies/closing_data/v18/`) e **não
> copie aquelas frases para prosa nova**. E não cite ficheiros por número de linha nem por contagem
> que alguém tenha de manter: âncore em conteúdo — o nome de um estudo, uma geração, uma data.

---

## 1 · Two volumes, and the appendix letters collide

The banca received **two** documents. Both have an Appendix B, an Appendix D and an Appendix E, and
they are different texts. **Never write "Appendix B" without naming the volume.**

| | **main volume** (deposited) | **supplement** (defense support only) |
|---|---|---|
| built from | `src/` | `wrapup/material_extra/` |
| PDF **entregue** (congelado) | `src/banca.pdf` — **119 pp**, md5 `5be69d1b…` | `wrapup/material_extra/main_extra.pdf` — **27 pp**, md5 `512b372c…` |
| A | Other Scientific Contributions | — |
| **B** | **AI-Use Disclosure** | **Errata to the Reproduced Articles** |
| C | Data Ethics and Governance | — |
| **D** | **Why the Two Tasks Do Not Compete on the Shared Trunk** | **A Label-History Benchmark for the Next-Category Task** |
| **E** | **How Check2HGI and the Joint Model Work** | **The Human-Subjects Question** |
| F | — | Adaptation of the HGI Baseline |
| G | — | A Parameter-Count Control for Next-Category Prediction |

The deposited text **deliberately does not point at the supplement**: it cites only itself and the
repository. That is the document's policy, not an omission (`wrapup/erratas/README.md`, "Q24").

### 1.1 · The builds

One source, three builds, from `src/`:

| command | output | pages | what it is |
|---|---|---|---|
| `make defense` | `build/main.pdf` → copied to `dissertacao.pdf` | **120** ⚠ | **119 was stale, and the cell conflated two things.** 119 is what the frozen `banca.pdf` holds; the build produces **120** as of 2026-09-04 17:34 (measured here). They were equal when this row was written and the erratas have since separated them. |
| `make academico` | `build/main_academico.pdf` | **116** ⚠ | the AcademicoPG deposit body. **114 was two generations stale** — measured 115 on 2026-09-04 and 116 on 2026-09-06 (`academico`, 0 TeX errors), after the 04–06/09 erratas. Re-measure rather than quote this cell. |
| `make ppgc` | `build/main_ppgc.pdf` | **120** ❓ | defense document + approval sheet. **Not on disk**, so this number is unverified and predates the erratas; expect it to have moved with `make defense`. |
| `cd ../wrapup/material_extra && make extra` | `build/main_extra.pdf` | **27** | the supplement |

> ⚠ **WHY THESE NUMBERS GO STALE — and I got the mechanism wrong first, so here it is measured.**
> `src_utils/sync_page_counts.py` gates the recorded counts and is wired into `check.sh`. It does
> **not** pass silently when a build is missing: it exits **1** and `check.sh` records FAIL
> (verified — `sys.exit("no …log")` returns 1). The real problem is subtler and worse. It exits on
> the **first** missing build, `main_ppgc.pdf` is routinely absent, and so the run ends **before any
> count is compared**. Its "you did not build ppgc" is indistinguishable from its "a recorded number
> is wrong", and noise that always fires is noise people learn to skip. That is how `114` survived
> two generations. **Measure before quoting any cell in the table below.**
>
> ✅ **`\finalbuildfirstpage` now has a real gate** — `src_utils/check_first_body_page.py`, in
> `check.sh` since 2026-09-06. Until then it had **none**, while its own comment claimed
> "check.sh runs it, which is how this was caught" (verified false by listing every script
> `check.sh` invokes). That false claim was load-bearing: it is why four successive values
> (11→8→9→10) each felt verified and all four were wrong. The gate separates **exit 1 = wrong**
> from **exit 2 = could not check**, precisely so it never becomes the noise above.

> 🔴 **FIVE make targets overwrite `dissertacao.pdf`** (the current build — `banca.pdf` is safe from them): `defense`, the default `all`
> (so a bare `make`), `all3`, `fast` / `fast-defense`, and `fast3` — each ends in
> `cp build/main.pdf dissertacao.pdf`. **Never "just run make" to check something.** Use
> `make check` (runs no build) or `make academico` / `make ppgc` (they do not copy).
> To verify a rebuild, compare `pdftotext` output, **not** md5: there is no `SOURCE_DATE_EPOCH`, so
> every rebuild differs in `/CreationDate` and md5 can never match.

### 1.2 · Erratas already applied to the source

`src/` is the delivered text, but it is **not byte-frozen**: corrections for the final deposit are
applied here as they are decided, each one registered in `wrapup/erratas/`. The delivered
**`src/banca.pdf` is never rebuilt** — it is the frozen record of what the banca received
(md5 `5be69d1b…`, 119 pp). The current build, **with the erratas applied**, is `src/dissertacao.pdf`,
which `make defense` produces. Two artifacts, on purpose: one is the record, the other is the current
text. (The file uploaded to AcademicoPG is neither: it is `build/main_academico.pdf`, from
`make academico` — see the STALE block below. Until 2026-10-02 this sentence called
`dissertacao.pdf` "what will be deposited".)

| applied | what changed | errata |
|---|---|---|
| 2026-08-21 | The Portuguese Resumo said the joint model outperformed the dedicated models on next-category **"em todos os conjuntos"**. The delivered result is superiority at **one** dataset (Florida, Holm *p* 0.011). The defect was isolated — the English Abstract, §2.5, Ch.5 and Ch.6 all said "at one dataset". The Portuguese now mirrors the English. | [`wrapup/erratas/errata_resumo_escopo_categoria.tex`](wrapup/erratas/errata_resumo_escopo_categoria.tex) |
| 2026-09-01 · **AUT-35** | MobiWac status: "submitted / under review" → "accepted for publication" (accepted 2026-08-26). Five prose sites plus the header comments of the eight Ch. 5 files. The sixth site was §3 of this file, fixed 2026-09-02. | commit `e1f9b8c0` |
| 2026-09-01 · **ERR-3** | The `note` field of `liu2019dwa` was printing inside the bibliography entry (reference [52], p. 95) — a working annotation, not part of the citation. Moved to a comment **above** the entry, content preserved. ⚠ The first attempt put the comment **inside** the braces and broke BibTeX: `%` is not a comment character to BibTeX, which scans for `@`. Any comment near a `.bib` entry must contain no at-sign. | commit `e1f9b8c0` |
| 2026-09-02 · **ERR-5** | Missing identifiers. `senushkin2023aligned` and `liu2023famo` gained a `doi` (`liu2023famo` also `pages`). `holm1979` was closed **fail-closed**: the DOI the audit proposed does not resolve (doi.org 404, Crossref "Resource not found"; Holm 1979 is not in Crossref at all). OpenAlex asserts a JSTOR-id DOI inherited from MAG and never registered — **do not restore it from there.** The entry carries the JSTOR `url` instead. | commit `e1f9b8c0` |
| 2026-09-01 · **ERR-6/7** | `5_mobiwac/05_setup.tex`: "and on fewer folds at Florida and Texas" → "and on a single fold at Texas"; the following clause now names the large-dataset value and says only the single-fold Texas screen tested it. | commit `e1f9b8c0` |
| 2026-09-01 · **Table 8** | Caption now states that check-ins, users and POIs are counts over the **full corpus, before** the ten-visit filter, and that the Windows column is computed **after** it. | commit `e1f9b8c0` |
| 2026-09-01 · **Ch. 1** | The Theoretical bullet no longer asserts that the studies determine that MTL helps; it says they analyse how MTL behaves. The controlled comparisons identify the input representation as one condition of the outcome; the sharing-topology effect was not isolated from it. Aligns Ch. 1 with Ch. 6. | commit `e1f9b8c0` |
| 2026-09-02 · **B-05 / B-06 / B-27** | Three responses to the banca's annotated PDF ([`wrapup/REVISAO_BANCA_PDF.md`](wrapup/REVISAO_BANCA_PDF.md)). B-05: Ch. 1 defines the check-in level before the example and drops a personification the WRITING_LAW bans. B-06: §2.1.1.1 gains concrete instances for the four sets ("for example" did not occur once in all of Ch. 2). B-27: the Table 10 caption now says in writing that bold does **not** mark the largest value in a column — the document uses bold with the other sense in Table 2, which is what misled the reader. | commit `e1f9b8c0`, record in `wrapup/REVISAO_BANCA_PDF.md` |
| 2026-09-02 · **parameter counts** | The dedicated-category counts were low by ~2.2× in **both** volumes — see Trap 6. Appendix G's two rows, its percentages and its framing ("matched" → over-capacity); the main volume's two sums. No macro-F1 changes. | commit history + `research/reproducibility/mobiwac_v18/param_counts.py` |
| 2026-09-04 · **logit adjustment** | Ch. 5 applies logit adjustment by name and formula and **cited nothing** for it; the results section leans on it again as a controlled constant. Now cites Menon et al. (ICLR 2021). Reproduced text → declared as a row of **Table B.5 of the supplement**, and in the article's own `ERRATA.md` as a both-texts correction. ⚠ The `.bib` entry has **no DOI and that is not an omission** — Crossref has none registered. Verified at the arXiv record. Do not restore one from an aggregator. | commit `30621bce` |
| 2026-09-04 · **B.5 count** | The supplement's Article-3 section says the scope table "lists **two** further departures" and enumerates them; the table holds **eight**. It also still calls the article "under review" (accepted 2026-08-26 — a sixth AUT-35 site). Both fixed: the prose now counts eight and enumerates them in two classes (the two that predate acceptance, the six applied after), and the mechanism paragraph moved to the past tense, closing with the rule that after acceptance every correction is declared here. `src_utils/count_errata_rows.py` now covers B.5 and is **green**. | guard in `30621bce`, prose in `0c4f6f2f` |
| 2026-09-04 · **Ch. 6 objectives** | The introduction states four specific objectives and the conclusion never revisited them by name (live count of "objective" in `6_conclusion.tex`: **0**). Three sentences now name them at the end of the per-chapter paragraphs whose existing content meets each one, in the introduction's order — objective 4 as the introduction states it **since 2026-09-03** (protocol differences + verdict reading), not the older "consolidate the evidence". No claim, number or verdict added. Closes the last open item on the advisor's list. | commit `07a6e79e` |
| 2026-09-06 · **ladder probes** | The verdict ladder is the document's central claim, copied **by hand at twelve live sites across eight files**, and no probe watched any of them — the 2026-08-21 Resumo errata was exactly this drift, in one language only. Four `LADDER-*` probes now pin scope + count + bound in one match, at both abstracts and Chs. 1 and 6; **not** Ch. 5, whose sentences are reproduced text. Each sabotage-validated against the specific drift it must catch. Gate 220/236 → **224/240**. | commit `03774545` |
| 2026-09-06 · **ERR-2 ratified** | Chapter headings read "Multitask" while the prefaces cite the article titles hyphenated. **No change**, ratified by the author after a check: 73 "multitask" vs 3 "multi-task" live, and all three hyphenated ones quote a title of record. The governing rule is citation fidelity, not house style — a title is reproduced as published, in APA and IEEE alike. All seven ERR are now closed. | `wrapup/open_points/LACUNAS.md` §ERR-2 |
| 2026-09-06 · **Ch. 2 window** | The chapter never stated the windowing: live count of "window" in Ch. 2 was **0** while Ch. 5 uses it 34 times, in a subsection titled "Preparation and data split" that had no preparation. New opening paragraph. **ℓ=9 is universal** (`L_h=9` at Chs. 3 and 4, "nine visits" at Ch. 5) — an earlier claim of mine that the three disagreed on ℓ was **wrong**; what varies is stride (non-overlapping vs. overlapping), the minimum history (5 vs. 10 visits) and short-history handling (zero-pad vs. full-length-only), each splitting the first two studies against the third. Frame, no errata; every value quoted from delivered text. | commit `b6b569e4` |
| 2026-09-08 onward | **Not copied here; this ledger stops at 2026-09-06.** Every later correction to Ch. 5 is a row of **Table B.5 of the supplement** (`src/tables/mobiwac/errata_scope.tex`, 31 rows on 2026-10-02) and every later one to Ch. 3 a row of **B.1** (`src/tables/cbic/errata.tex`, 14); `git log -- src/` gives the commit of each. | B.5 / B.1 + `git log` |

> ✅ **DEPOSIT NUMBERING AND FORMATTING: VERIFIED CONFORMANT ON THE SYSTEM-EMITTED FILE (2026-09-06).**
> Not on our build — on the RASCUNHO the portal emitted after the corrected body was re-attached
> (127 sheets, md5 `92638ff1…`, the same file the author holds). Read off that file: sheet 21
> (Introduction) prints **20**; sheet 127 (last) prints **126**; sheets 1–20 print **nothing**;
> the sequence is continuous by sampling. Formatting measured by bounding box on the unwatermarked
> build (the DRAFT layer covers the whole sheet and contaminates any measurement taken on the
> RASCUNHO): margins 3.00 / 2.01 / ≥1.96 cm, leading 17.9–18.0 pt = 1.5 × 12 pt, number top-right at
> 2.01 cm, A4, TeX Gyre Termes 12 pt, and the §6 order Figures → Tables → siglas → Contents → body.
> ~~**Only the BBT submission remains, and it is the author's to make.**~~ *(Superseded
> 2026-10-02: true of the 09-06 file, but erratas kept landing after it, so the uploaded body is
> behind the source again. The remaining sequence is the one in the banner at the top of this file:
> decisions → apply → rebuild → re-attach → re-emit the RASCUNHO → manual pass → BBT → ficha →
> "Enviar". The verification above has to be redone on the next RASCUNHO.)*
>
> ⚠ **THE WATERMARK TRAP, because it produces false negatives on arbitrary pages.** A line-anchored
> regex (`^\d+$`) over a watermarked PDF reports "no page number" on sheets where the DRAFT glyphs
> land on the number's line — it did so on sheets 22, 23 and 126 while their neighbours read fine.
> Extract every integer from the region instead. `check_first_body_page.py` was hardened for this on
> 2026-09-06: under the strict match it would have reported the first numbered page as LATER than it
> is, which is the one quantity it exists to certify.
>
> 🔴 **THE DEPOSIT PORTAL IS BEHIND THE SOURCE, IN TWO SEPARATE WAYS (2026-09-06).** They have
> different causes and different fixes, and conflating them is how the first one survived a check:
>
> 1. **The Resumo field carries the PRE-APPROVAL text.** The Resumo was rewritten and approved by
>    the author in commit `8fe5a10d` (2026-09-02 **13:29**); the extraction that was typed into the
>    form was taken from a `content.tex` whose mtime was 2026-09-02 **12:24**, an hour earlier. The
>    missing sentence is not cosmetic — it is the scope claim that distinguishes the work:
>    *"A próxima região… é tratada como alvo final de mesmo peso que a próxima categoria, e não como
>    sinal auxiliar; os modelos publicados mais próximos não estudam esse par…"* (verified present
>    once in the live `content.tex`).
>    ⚠ **The md5 check that passed did not test this.** It compared the portal against the same
>    scratchpad extraction that had produced the pasted text — circular. A verification must re-read
>    the SOURCE, not the artifact that came from it. (Cf. `feedback_validar_artefato_nao_preview`:
>    validating the preview is not validating the delivery.)
> 2. **The uploaded body PDF is the 2026-09-04 build.** Seven `.tex` files plus `references.bib`
>    have changed since: `2_fundamentals.tex`, `5_mobiwac/04_method.tex`, `5_mobiwac/07_discussion.tex`,
>    `6_conclusion.tex`, `apx_h_check2hgi_joint_model.tex`, `content.tex`, `tables/mobiwac/errata_scope.tex`.
>
> **Both were closed the same day**: the Resumo field was re-saved from a fresh read of `content.tex` (byte-compared against what the portal returns, 3144 / 2797 chars) and the body was re-attached as the 116-page build. The block above records the verification that followed.

> ⚠ **`src/dissertacao.pdf` is STALE — measured 2026-09-06, and this warning was itself stale.**
> It said "built 2026-08-21, carries only the Resumo errata". It was in fact rebuilt **2026-09-04
> 17:34** (by the author) and is **120 pp**. It is still behind: **ten** files under `src/` had
> changed since that build on 2026-09-06 — `2_fundamentals.tex`, `5_mobiwac/{04_method,05_setup,07_discussion}.tex`,
> `6_conclusion.tex`, `apx_h_check2hgi_joint_model.tex`, `content.tex`, `main.tex`, `references.bib`,
> `tables/mobiwac/errata_scope.tex`.
>
> *Re-measured 2026-10-02.* The build is still the 2026-09-04 17:34 one (`pdfinfo` CreationDate). What
> happened on 2026-09-08 is that this build was **committed** (`ec9a191d`; the tracked copy until then
> was the 119-pp build of 08-21), which is why the file's mtime reads 09-08. It was not rebuilt.
> Commits since the build have touched **27** `.tex`/`.bib` files under `src/`
> (`git log --since='2026-09-04 17:34' -- src/`), including the Ch. 5 corrections of 09-29 to 10-02.
>
> ✅ **It is NOT a deposit artifact, so nothing is blocked on it.** The AcademicoPG body is
> `build/main_academico.pdf`; `UFV_COMPLIANCE.md` never mentions `dissertacao.pdf`. It is the
> convenience copy of the current build — its only risk is that a reader who opens the tracked file
> gets pre-errata text. `make defense` rebuilds it, and remember five targets overwrite it, so never
> run a bare `make` to check something (§1.1). **Rebuild it once the text settles, not before**:
> while erratas are still landing, every rebuild is obsolete on arrival.

**Consequence for anyone verifying:** a rebuild of `src/` no longer reproduces
`src/banca.pdf`. That is expected and is the point of the two names. **To see what the banca
received, read `src/banca.pdf`; to see the current text, read `src/dissertacao.pdf`** (or rebuild it
with `make defense`). The deposit body is `build/main_academico.pdf` (`make academico`).

---

## 2 · Folder map — and whether each part is still live

| folder | what it is | still live? |
|---|---|---|
| [`src/`](src/) | **THE delivered dissertation.** LaTeX source + `chapters/` + `figures/` + `tables/` + two tracked PDFs: `banca.pdf` (frozen record) and `dissertacao.pdf` (current build, erratas applied) | **yes.** Prose changes reach it only as a registered errata — see §1.2 for the applied ledger |
| [`wrapup/`](wrapup/) | everything that happened **after** the submission: the supplement, the erratas, the open points, the post-submission studies, the rescued evidence | **yes — this is the front line.** Start here for anything defense-related |
| [`src_utils/`](src_utils/) | the build + gate toolchain at the top; `evidence/` holds the provenance reports the delivered text cites; `_history/` holds the closed audit rounds (`_round6`..`_round14`, reviews, specialists, `_archive/`) | **yes, load-bearing.** `check.sh` executes `_history/_round9/35_wave_a_render_check.py` and the probes in `check_audit_claims.py` pin content inside `_history/` -- move nothing there without running the gates |
| [`science/`](science/) | internal scientific records (integrity studies, trunk-gain attribution, the technical appendix, the record of the label leak) | yes. The delivered source cites it as provenance, in comments; nothing builds from it |
| [`reviewers/research/`](reviewers/research/) | the 2026-07 research records behind the reviewer personas and the banca guide (were `docs/research/` until 2026-09-30); `wrapup/CONFERENCE_VENUES.md` came from the same folder | reference |
| [`reviewers/`](reviewers/) | 19 invocable reviewer personas | yes — several fire again before the defense and the deposit |
| [`science/fundamentals/`](science/fundamentals/), [`science/storyline/`](science/storyline/) | the citation ledgers, `DEFINITIONS.md` and the storyline record of chapters 1, 2 and 6 (the superseded `.tex` drafts left on 2026-09-30) | yes. `DEFINITIONS.md` is pinned by probes |
| [`archive/`](archive/) | spent planning + single-use scaffolding | **no — nothing here is a source.** See its README |
| `exemples/` | exemplar dissertations (Viegas, Germano, …) used as the quality bar | **not in the repository** -- removed from disk 2026-08-28; the author keeps a local backup |

**The boundary rule**, which is what makes this folder navigable:

> `wrapup/` is what came **after** the submission. `archive/` is what was left **behind** it.
> Everything outside those two is the live document.

### 2.1 · The law documents

| doc | what it governs |
|---|---|
| [`WRITING_LAW.md`](WRITING_LAW.md) | register, canonical names, honesty rules, the verdict ladder's permitted wording, AI-tell bans |
| [`GLOSSARY.md`](GLOSSARY.md) | the term registry. **Fail-closed: a term not in the registry may not be used** |
| [`AGENT_GUARDRAILS.md`](AGENT_GUARDRAILS.md) | process law: citation / number / claim protocols, review gates, and **§4b**, the meta-claim protocol — the most valuable text in this folder |
| [`NORTH_STAR.md`](NORTH_STAR.md) | thesis question, the three-paper arc, chapter map. ⚠ carries the superseded ladder (see §0.3) |
| [`UFV_COMPLIANCE.md`](UFV_COMPLIANCE.md) | UFV/PPGCC norms, defense prerequisites, the AcademicoPG deposit pipeline |

---

## 3 · The three articles (the coletânea)

Chapters 3, 4 and 5 are re-typeset reproductions of three papers. **Each has its own folder**, and
the delivered `references.bib` cites all three as provenance of record.

| ch. | paper | venue / status | folder |
|---|---|---|---|
| 3 | *An Investigation into Multi-Task Learning for POI Category Classification and Next-POI Prediction* | **CBIC 2025, published.** DOI `10.21528/CBIC2025-1191324`. **Satisfies Art. 21** | [`../CBIC___MTL/`](../CBIC___MTL/) |
| 4 | *ST-MTLNet: Representações Espaço-Temporais de POIs para Aprendizado Multitarefa* | **CoUrb 2026 (SBRC), published.** DOI `10.5753/courb.2026.22960`. Tarik S. Paiva 1st author, Vitor 2nd + presenter. Translated to EN for the chapter | [`../CoUrb_2026/`](../CoUrb_2026/) (see `src_en/`) |
| 5 | *Predicting the Next Category and Region of a Visit* | **MobiWac 2026, accepted for publication** (accepted 2026-08-26; EDAS #1571313639) | [`../[mobiwac]/`](../%5Bmobiwac%5D/) — the paper of record is **`src/`**. ⚠ This cell said `src_fix/` until 2026-09-08; that tree was consolidated into `src/` and **no longer exists**. Corrected the day it went, after a Fable audit found the pointer still standing. |

Each article folder carries its own `ERRATA.md`, which is the subject matter of **Appendix B of the
supplement**. BRACIS 2026 is **not** a chapter: rejected, superseded by MobiWac.

---

## 4 · What is still open

The live registry is [`wrapup/open_points/LACUNAS.md`](wrapup/open_points/LACUNAS.md) — 42 items,
each remedied against the live source and the built PDF. **6 blocks are open** as of 2026-10-02
(was 10; 17 before the seven ERRATA closed on 2026-09-06), in four classes. ⚠ LACUNAS's own block
headers still read `[ABERTO]` for GAPS-D, NSO-46, LO-11 and LO-13, and the table below names the
records that close them.

| class | open | what closes it |
|---|---:|---|
| **ERRATA** — changes at the final deposit | **0** | ERR-1…ERR-7 all closed 2026-09-06. ERR-1 was **not a defect** (the diagnosis was wrong: the errata table is not in the deposit PDF); ERR-2 **ratified without change** (chapter headings may differ from a cited title — the rule is citation fidelity, not house style); ERR-3/6/7 applied; ERR-4 decided (keep the orphans, with an archive note); ERR-5 closed **fail-closed** on `holm1979`, whose proposed DOI does not resolve |
| **DECISÃO DO AUTOR** — no agent closes these | 0 | All closed by 2026-10-06: LO-12 on 2026-08-03 ("Vamos de B", `src_utils/LEFT_OUT.md`); AUT-26 (name MTVisitNet, text unchanged), LO-6 (both raster figures stay as published) and GAPS §7.1 (text stays as it is) on 2026-10-06. *Corrected 2026-10-02, was 7:* LO-11 (authorship credit on the CoUrb article) was decided by the author on 2026-07-30 and LO-13 on 2026-08-04 (both in `src_utils/LEFT_OUT.md`); NSO-46 is moot, because its paragraph lives in `apx_b_static_scope.tex`, which no live `\input` builds (LACUNAS's own block measures this) |
| **EXECUÇÃO** — only an experiment closes it | 2 | P4, P6. P1 is **closed** (2026-08-13). *Corrected 2026-10-02, was 3:* GAPS-D closed on 2026-08-11 (`docs/studies/closing_data/v18/GAPS.md` §4: every `reg` cell now carries `scoring_path`). ⚠ Neither blocks the deposit; both are answerable standing up from the record already written into each entry |
| **ORAL** — answered standing up, text untouched | 0 open | three answers drafted in `wrapup/erratas/RESPOSTAS_ORAIS.md` (Q13, Q14, Q15; this cell said six until 2026-10-02) |

Two more registries: [`wrapup/NEW_VERSION.md`](wrapup/NEW_VERSION.md) (the `mtlcheck` rewrite — see
§5) and `src_utils/PENDENCIAS.md` (the older author queue).

> **The sign-off marker count does not live in one place any more.** Measured 2026-08-20:
> `src/` **24** + `wrapup/material_extra/` **9** + `wrapup/erratas/` **1** = **34**. A command that
> greps only the main tree misses ten, **including NSO-46, the one annotated open** (moot, since no
> build includes its file; see the table above).

---

## 5 · Traps — each one has already cost a session

1. **Strip LaTeX comments before grepping this source.** Every rewritten table and appendix carries
   a dated `EVIDENCE BASE REPLACED` header that **quotes the superseded values verbatim**, so an
   unfiltered grep always over-reports. Filter the *file* (`grep -vn '^[[:space:]]*%'`), not the
   grep output.
2. **Read the exit code, not the output.** `make check` prints a green-looking table and then exits
   2. This has produced a full day of commit messages claiming gates pass. The folder's own history
   records it twice; this session hit it a third time.
3. **The POI-RGNN column once mixed two implementations, and this trap said the opposite.**
   Until 2026-10-01 this item claimed the reimplementation's JSONs
   (`docs/results/baselines/faithful_poi_rgnn_*.json`) were a "pre-bugfix draw" and the printed FL/CA/TX
   values (34.49 / 31.78 / 33.03) were correct. **That was false.** Those three came from the
   October-2025 runs of the older TF implementation (`results/baselines/rgnn/*_2025100*`), with folds
   split within each user, 3-visit windows and a 1,500-user sample. The reimplementation ran on all six
   datasets, user-disjoint, and its JSONs are right: FL 33.35 / CA 30.71 / TX 32.08, printed since
   2026-10-01. There was never a bug. The label began as a guess ("JSONs may be pre-bugfix", a32bfdc4,
   2026-05-02) and two docs-only commits restated it as fact. The fact gate flagged the mixture in August
   and was overruled by that banner (`wrapup/REVISION_PLAN.md`). The author caught it. **Lesson: a
   provenance banner is a claim, not evidence; re-derive before overruling a gate.**
4. **The post-submission studies are NOT in either delivered PDF.** Q13 (concatenation) and P1
   (capacity) were verified absent by text extraction. They are oral-defense material with drafted
   erratas. And **P1's own record cites `+2.12 / +2.05` from a superseded substrate** — the
   delivered margins are **TX +1.21 / CA +1.06**. Quote the delivered ones.
5. **Never mix an `mtlcheck` number with a dissertation number.** (⚠ `mtlcheck` is a rewrite of the
   **code**, not a separate **repository**: `/Users/vitor/Desktop/mestrado/mtlcheck` is a **git worktree
   of this very repository** (its `.git` is `gitdir: …/ingred/.git/worktrees/mtlcheck`, branch
   `rewrite/mtlcheck`), so it shares refs, tags and config. That was corrected 2026-10-01: it had been
   recorded here as "another clone". The department repo will be a NEW repo from the final commit,
   without history (author, 2026-10-01). See `wrapup/ACHADOS.md §A12`.) The rewrite uses a different
   evaluation protocol (nested 70/10/20 user splits, out-of-fold pooled metrics, a derived 0.4 pp
   margin instead of the registered 2 pp). Under it, **Alabama/region flips to inferior.** Those
   numbers answer defense questions; they do not correct Chapter 5. Read `wrapup/NEW_VERSION.md`
   §2 first.
6. **The parameter counts were wrong in BOTH volumes, and are now corrected in both** (2026-09-02).
   Appendix G of the supplement printed 644,359 / 4,207,399 "100.2%" / 5,249,719 "101.9%"; the real
   counts are 1,433,863 / 9,634,471 (**229.5%**) / 12,044,791 (**233.8%**), and the main volume's two
   sums moved from 1.1 / 2.0 million to 1.9 / 2.8. The audit built the head at the MODULE default
   depth instead of the config's, so every dedicated-category count was low by about 2.2×, and the arm
   labelled "capacity-matched" in fact carried **over twice** the joint model's budget. The macro-F1
   results are untouched and the conclusion **strengthens** — the joint model wins against an
   over-capacity opponent, not a matched one. **Do not say "100.2%" aloud**: it survives in the
   provenance comments of `apx_i_parameter_count_control.tex`, which quote the withdrawn values
   verbatim, so an unfiltered grep still finds it. The correction is reproducible without a GPU:
   `PYTHONPATH=src python research/reproducibility/mobiwac_v18/param_counts.py`, which recomputes every
   count and exits non-zero if the cross-dataset 465,297 identity breaks.
7. **`git status` does not see `docs/results/`.** `.git/info/exclude` carries a bare `results`
   pattern. Before deleting anything, run **`git check-ignore --no-index -v <path>`** — the bare
   `-v` form consults the index and reports "not ignored" for any path that is *already tracked*,
   which is the opposite of the answer you asked for. To see what exists on disk that git hides,
   use `git status --ignored`. (Corrected 2026-08-28; the old form was in this file and produced
   contradictory readings during the cleanup.)

---

## 6 · Version history of this folder

| when | what |
|---|---|
| 2026-08-11 | `src_fix/` branched from `src/` at `de040d3c` as the revision working copy |
| 2026-08-16 | delivery build (`264c7996`); the supplement moved to `wrapup/material_extra/` |
| **2026-08-20** | **the folder went from three copies of the text to one.** `src_fix/` → `src/`; the pre-revision v1 `src/` and the comment-stripped mirror `src_clean/` were deleted |

**Recovering the pre-reorg state:** `git checkout dissertacao-pre-reorg -- articles/dissertacao/src`

What the 2026-08-20 reorg established, measured rather than assumed: `src_clean/` was prose-identical
to the delivered tree in **54 of 54** shared `.tex` files after comment stripping, so it held no text
of its own; the seven files the old `src/` had and the delivered tree lacked are all preserved under
`wrapup/` (four identical, three in corrected newer form). The one edit where the old `src/` was
newer — `content.tex`, made inside the delivery commit itself — **reinstated a retracted claim** and
was discarded deliberately.

It also fixed a live defect: `check.sh` (a linha `SRCROOT=` que resolve `../src`) and `fastbuild.sh` (o fallback `SRC="$(cd "$UTILS/../src" ...)"`) resolve `../src` by construction, so
from 2026-08-11 to 2026-08-20 **every `make check` and `make fast` run from `src_fix/` gated and
built the v1 tree, not the delivered one.** Nine days of green gates on the wrong document.
