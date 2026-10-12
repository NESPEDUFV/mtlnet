# 08 · Translation fidelity — the L5 gate (CoUrb PT → EN), round 6

**Persona:** `reviewers/08_translation_fidelity.md`. **Gate:** L5, mandatory for the CoUrb chapter
(`AGENT_GUARDRAILS.md` §4). **Read-only.** Written 2026-07-28.

**Verdict: L5 PASS WITH FINDINGS.** No claim-strength drift, no number mismatch, no silent
omission, and no unsanctioned addition survives in the translated chapter. Every departure from
the published Portuguese is declared and traceable. The findings below are two accounting errors
in Appendix B's self-description, one undisclosed spelling departure that lives in a raster, and
one pre-existing gate failure I tripped over. None of them changes a result.

---

## 0 · Which source of record I used, and why

The persona names "the published PT article" as the source of record. Three candidate texts exist,
so I established the relationship between them before comparing anything.

| Candidate | On disk | Status |
|---|---|---|
| Published article | not in the repo | **Fetched this session** from SBC SOL and used as the source of record |
| `articles/CoUrb_2026/src/` (PT) | 6 `.tex` + 3 table files | The PT LaTeX source. **Measured equal to the published text** (below) |
| `articles/CoUrb_2026/src_en/` (EN) | mirror + `main.pdf` (14 pp) | The verified translation; the chapter's immediate parent |

**The published record.** `https://doi.org/10.5753/courb.2026.22960` resolves to the SBC SOL
landing page for article 42559. Its Highwire metadata gives `citation_doi`
`10.5753/courb.2026.22960`, `citation_firstpage` **323**, `citation_lastpage` **336**,
`citation_date` **2026/05/25**, and the title as the chapter's preface quotes it. I downloaded the
galley PDF (`citation_pdf_url` → `.../download/42559/42326`, 1,172,363 bytes, 14 pages) and
extracted its text. Note for whoever repeats this: `sol.sbc.org.br` is not on the sandbox
allowlist by default and the direct `/article/view/22960` path returns HTTP 500; the DOI redirect
works.

**Why this mattered, and the trap I avoided.** The PT tree's git history shows commit `2f333e2b`
(2026-07-20, *"revise src/ paper — acknowledgments, limitations, ablation caveat"*) landing
**two months after** the 2026-05-25 publication date, adding an Acknowledgments section, a
Gowalla-vintage limitation, a dimensionality-control caveat and a Travel-complementarity
paragraph. Read from git alone, that looks like post-publication drift, which would mean the local
PT tree is *not* the published text and every comparison against it is contaminated.

**It is not drift. I measured it.** All six content changes of `2f333e2b` are present in the
published galley PDF, and all three pre-revision phrasings it replaced are absent:

| `2f333e2b` change | In the published PDF? |
|---|---|
| `\section*{Agradecimentos}` (MCTI, Manna, Araucária, Softex, CNPq 421548/2022-3, FAPEMIG, CAPES) | **yes** |
| Gowalla vintage limitation, "coletados entre fevereiro de 2009 e outubro de 2010" | **yes** |
| "a diferença na dimensionalidade de entrada pode influenciar parte dos ganhos observados" | **yes** |
| "um controle experimental adicional igualando a dimensionalidade das representações" | **yes** |
| Travel complementarity, "capturam aspectos complementares da mobilidade" | **yes** |
| "decomposição em três componentes **especializados**" | **yes** |
| *pre-revision* "três componentes." (no "especializados") | absent |
| *pre-revision* old Travel explanation ("cujo grafo espacial captura conexões estruturais") | absent |
| *pre-revision* capacity sentence without "entre os modelos avaliados" | absent |

So `2f333e2b` was a **sync-forward of the camera-ready into the repo**, not a revision of it. A
sentence-level sweep confirms the whole tree: after normalizing accents, the extractor's
hyphenation artifacts and LaTeX markup, **113 of 113** prose sentences of the PT tree appear
verbatim in the published PDF (the residue is markup, `\cite`/`\ref` shells and math). The local PT
tree is therefore usable as the source of record, and I used it for sentence-level work, with the
galley PDF as the authority for anything load-bearing.

**Note on the ERRATA record.** `articles/CoUrb_2026/ERRATA.md` is untracked (`git status` shows
`?? articles/CoUrb_2026/ERRATA.md`). Its content is consistent with `NORTH_STAR.md` §4 and with
`slides/judge_feedback.md`, so I used it, but it is not committed and a reader cannot cite it.

---

## 1 · Finding 1 — the Nash-MTL sentence: the ORIGINAL overclaimed. The erratum is correct.

This is the round's headline question, and the persona brief is explicit that the answer decides
whether the Appendix B row is right. I established it from the source, not from the drafted
rationale.

**The published Portuguese, verbatim** (galley PDF p. 5, top of the block that ends
`"Anais do X Workshop de Computação Urbana (CoUrb 2026) 5"`; PT source
`src/sections/metodology.tex:26`):

> "o Nash-MTL busca a direção de atualização que maximiza o produto das utilidades de todas as
> tarefas, **o que garante que a atualização seja benéfica para todas as tarefas simultaneamente**,
> evitando a dominância de uma tarefa sobre a outra."

**The EN translation, verbatim** (`src_en/sections/metodology.tex:26`):

> "Nash-MTL seeks the update direction that maximizes the product of the utilities of all tasks,
> **which ensures that the update is beneficial for all tasks simultaneously**, avoiding the
> dominance of one task over the other."

`garante que ... seja benéfica` → `ensures that ... is beneficial` is a **faithful** translation.
Same modality, same unconditional force, no hedge added or removed. **The overclaim is the
published article's own**, and the translation reproduced it correctly.

**Therefore this is an erratum, not a translation defect, and Appendix B must carry it — which it
does.** `src/tables/courb/errata.tex:28-36` (Table B.3, row 4) states the defect as *"The
methodology states that maximizing the product of the task utilities 'ensures that the update is
beneficial for all tasks simultaneously'. The guarantee is unconditional as written."* That is an
accurate quotation of the published claim and an accurate characterization of its defect. Rendered
on **p. 96** of the defense build; the phrase "ensures that the update is beneficial" appears
**nowhere else** in the 108-page render, so the published wording survives only inside the errata
row, which is the correct disposition.

**The replacement clause is also correct against the method's own paper.** Chapter text now reads
(`chapters/4_courb/methodology.tex:36`, renders p. 47):

> "Away from a Pareto-stationary point, meaning a point at which some convex combination of the
> task gradients is zero, and under the method's assumption that the gradients are linearly
> independent there, that direction is a descent direction for every task, avoiding the dominance
> of one task over the other."

I fetched arXiv:2202.01017 (*Multi-Task Learning as a Bargaining Game*; Navon, Shamsian, Achituve,
Maron, Kawaguchi, Chechik, Fetaya; 19 pp.) and located each component:

- **"descent direction for every task"** — p. 6: "Since our update rule is a descent direction for
  all tasks, we can reasonably assume that our algorithm avoids local maxima points." The
  chapter's wording is the authors' own property, not a paraphrase.
- **linear independence** — p. 6, Assumption 5.1: the gradients "are linearly independent unless
  that point is a Pareto stationary point." Restated p. 18 (D.5): "we assume that the task
  gradients are linearly independent for each point θ that is not Pareto stationary."
- **the Pareto-stationary condition** — p. 3, Claim 3.1 is introduced with "we now show that if θ
  is not on the Pareto front"; the solution form `G>Gα = 1/α` is stated under that condition.
- **the gloss** — p. 2: "a point is called Pareto stationary if there exists a convex combination
  of the gradients at this point that equals zero." The chapter's gloss is this sentence.
- **the retained clause** — p. 3, on Axiom 2.4: without scale invariance "the solution can easily
  be dominated by a single direction," which independently supports keeping "avoiding the dominance
  of one task over the other."

The narrowing is faithful to the cited method and does not weaken the claim below what the authors
derive. **This item passes.** The one asymmetry worth the author's eye is that the errata row's
closing sentence, *"The claim is weaker than the published one, and no result depends on it,"* is
true but understates the row: the published claim was not merely stronger, it was unconditional
where the method's guarantee is conditional. That is a wording preference, not a defect, and I am
not raising it as a finding.

---

## 2 · Finding 2 — the additions this round are correctly marked as additions, not as translation

An addition to a published chapter is not a translation of anything, so the gate is whether each is
declared. I enumerated every printed sentence of the chapter (wrapper + the five section files +
the three table files), normalized away the sanctioned mechanical changes (`\cite`/`\ref` shells,
`this work` → `this chapter`, `MTLNet` → `MTLnet`, cross-reference renumbering), and diffed against
the union of `src_en/main.tex`, `sections/*.tex` and `resultados/*.tex`.

**Result: 8 printed sentences or blocks exist in the chapter and not in the published source.** All
eight carry an explicit declaration in the chapter source, and all eight are covered by the
Appendix B additions paragraph:

| # | Addition | Today's anchor | Class |
|---|---|---|---|
| 1 | italic `chapterpreface` paragraph | `4_courb.tex:18` | frame device |
| 2 | subsection "The MTLnet framework", 2 paragraphs | `4_courb/related.tex:42-47` | frame device |
| 3 | Figure 4.2 reading-instruction sentence | `4_courb/results.tex:68` | frame device |
| 4 | split-axis protocol sentence | `4_courb/results.tex:14` | protocol |
| 5 | single-seed protocol sentence | `4_courb/results.tex:14` | protocol |
| 6 | **checkpoint-rule sentence (NEW this round)** | `4_courb/results.tex:14` | protocol |
| 7 | Table 4.1 dataset lead sentence | `4_courb/results.tex:63` | table lead |
| 8 | Table 4.3 appended clause ("...retains six of them") | `4_courb/results.tex:101` | table lead |

**The new one specifically.** The checkpoint rule ("Within a fold, training runs for the full
number of epochs configured, without early stopping, and each task is read at the epoch of its own
highest validation macro-F1, measured on the same fold the score is reported on") is at
`4_courb/results.tex:14`, renders on **p. 52**, and is declared in the source comment immediately
below as *"Second declared ADDITION at this site: the checkpoint rule, which the published paper
leaves implicit. Not a correction of any published claim."* It is absent from `src_en` (verified by
8-gram diff). It is **not** presented as translated text: it sits after the two previously declared
protocol additions, in the same register, and Appendix B §B.2 states it in prose to the reader
("that training runs for the full configured number of epochs without early stopping, with each
task read at the epoch of its own highest validation macro-F1 on the fold the score is reported
on"). **This item passes.**

**Finding 2 (MINOR).** Appendix B's additions paragraph prints **nine**; I measure **eight**. The
count is right in the aggregate for the first two groups (three frame devices, three protocol
facts) and wrong in the third. `apx_b_errata.tex:275` reads:

> "The remaining three are the lead sentences that introduce the three tables, one each for
> Tables 4.1, 4.2, and 4.3."

There are only **two** dissertation-authored table leads. The category-table lead
(`4_courb/results.tex:77`) is now the **published sentence verbatim** — "The results of the POI
Category Classification task are presented in Table 4.2." — matching
`src_en/sections/results.tex` label-for-label. The dissertation clause that used to sit there
("the two ST-MTLNet variants reach higher mean F1 ... in every category and state") was **dropped**
in the v2 L5 repair, and the chapter comment at `results.tex:79-90` records the drop. Confirmed by
string search: "reach higher mean F1", "in every category and state", "higher mean F1" and
"retains a few categories" each occur **zero** times in the chapter. So the third group is two
leads, not three, and the total is eight, not nine.

*Closes when* `apx_b_errata.tex:262` says "eight" and `:275` says "The remaining two are the lead
sentences that introduce Tables 4.1 and 4.3" (or equivalent). Note the neighbouring history: this
paragraph has been re-counted twice already (three → eight → nine); the ledger's section C also
still lists a C5 row for the dropped category lead, which is where the ninth came from.

---

## 3 · Finding 3 — the chapter preface pointer to Appendix B resolves and is honest

`4_courb.tex:18`, last sentence of the preface: *"Appendix~\ref{apx:errata} records what we
established after publication about the scope of this chapter's static task, and that record
should be read alongside the category results reported here."*

- `\label{apx:errata}` is declared once, at `apx_b_errata.tex:95`. Not dangling.
- The sentence renders on **p. 42**; the section it points at ("The scope of the static task in
  Chapter 4") renders on **p. 98** and in the TOC on p. 10.
- The deliberate indirection is sound and the source comment explains it: the pointer targets the
  **appendix**, not `\label{apx:errata:static-scope}`, so that suppressing the section (one
  commented `\input` at `apx_b_errata.tex:407`) leaves the sentence true and produces no dangling
  reference. The comment also warns that the sentence must then be deleted. That is the right
  engineering.
- Fidelity: the sentence makes no claim about the article's results. It says a record exists and
  should be read alongside. The record itself (`apx_b_static_scope.tex`) is measured, states three
  qualifications, and explicitly protects the sequential-task claims ("Every claim
  Chapter~\ref{ch:courb} makes about the sequential task ... stands as published"). Nothing here
  strengthens or weakens the published article.
- It carries `[NEEDS SIGN-OFF]` with the co-author notice logged. Correct: it is a public pointer
  to a statement about a co-authored result.

**This item passes.**

---

## 4 · Numbers: digit-identical, and every delta explained

I compared every numeral in the chapter's prose against the published PT prose, after normalizing
locale (decimal comma → point, thousands point → comma). Nine deltas, all accounted for:

| Numeral | Direction | Explanation |
|---|---|---|
| `0.15`, `0.5` | chapter only | Locale: PT writes `0{,}15`, `0{,}5`. Values identical. |
| `2013` ×2 | chapter only | Inside `\cite{mikolov2013word2vec,mikolov2013negsampling}`, not prose. |
| `20.2` ×3, `22.0` ×3 | chapter only | Sanctioned erratum A2. |
| `0.02` | chapter only | Sanctioned erratum A1 (the technical-tie gap). |
| `24` ×2 | published only | The `20–24` the erratum replaces. Correct that it is gone. |
| `10.1145`, `2661829.2662002` | published only | A raw bib key inside `\cite{}`; the chapter cites `cho2011gowalla,jure2014snap`. |

**Tables.** All three re-typeset tables are cell-identical to the published tables: `dataset` 9/9
numerals, `category` and `next` each with **zero** cells present in one and not the other, and
`\textbf` counts equal (27 = 27) in both F1 tables. The two "published only" numerals in each F1
table are `\vspace{0.3cm}` and `\multicolumn{2}` — typesetting, not data. The published bolding of
the Florida *Outdoors* baseline cell (`\textbf{21.61 $\pm$ 0.99}`, `next.tex:15`) is preserved, as
the ledger and Appendix B both promise.

**I reproduced the audited counts from the chapter's own table before accepting them** (persona
README §10, reproduce-first). Parsing `tables/courb/next.tex`: best-of-two-encoders beats the
baseline mean in **15 of 21** rows; the baseline holds 6. Of those 6, the gap is within the
baseline's own SD in **two** rows — Florida *Outdoors* (21.61 vs 21.59, gap 0.02, SD 0.99) and
California *Outdoors* (25.01 vs 24.84, gap 0.17, SD 0.81). The chapter names only the Florida one
as a technical tie, which matches `slides/judge_feedback.md` §2 exactly ("O caso ambíguo é Florida
Outdoors: baseline 21,61 vs Sphere 21,59"). The chapter's "15 of the 21 ... with one additional
technical tie" is the audited claim, correctly scoped, and does **not** silently promote the
California row. Good.

**Claim-strength spot checks on the results/contribution sentences** (published → chapter):

| Published (PT) | Chapter (EN) | Drift |
|---|---|---|
| "supera o MTLNet em todas as combinações ... avaliadas" | "outperforms MTLnet in all evaluated category-state combinations" | none (universal preserved) |
| "vence na maioria dos cenários" | "outperforms the \textit{baseline} in most scenarios" | verb substitution only, scope "most" preserved (ledger A3) |
| "em 16 das 21 combinações" | "in 15 of the 21 ... with one additional technical tie" | **sanctioned erratum**, weaker than published, declared |
| "ganhos médios de 20 a 24 pp" | "average gains per state of 20.2 to 22.0 pp, considering the better of the two spatial encoders" | **sanctioned erratum + added disclosure**, narrower than published, declared |
| "não há um único encoder espacial universalmente superior" | "there is no single universally superior spatial encoder" | none |
| "os resultados devem ser interpretados com cautela" | "the results should be interpreted with caution" | none |

No sentence in the chapter is stronger than its published counterpart. Two are weaker, both by
sanctioned erratum. The frame chapter that repeats the CoUrb figure (p. 76) carries the
width-confound caveat in the same breath ("The comparison is not width-matched, however"), so the
hedge survives the trip into the frame.

---

## 5 · Finding 4 — the architecture figure: translations are faithful; one term is
## undisclosed and the raster still says `MTLNet`

`12_figures.md` records six labels translated in both the `.drawio` source and the raster. I
verified this by **decoding the PNG and looking at it**, not by searching the PDF text layer:
`arquitetura_modelo.png` is a raster and page 47's text layer contains **zero** occurrences of any
of its labels.

**Pixel diff against the pre-edit raster** (`git show 1a29b545:...`, 90,932 bytes, 1102×348 RGBA)
versus the current file (53,768 bytes, same dimensions): **5,396 of 383,496 pixels changed
(1.407%)**, in exactly **six** connected regions, and every region falls inside one of the six
label rectangles:

| region (x, y) | changed px | label |
|---|---|---|
| 97-215, 15-34 | 791 | Encoder Espacial → Spatial Encoder |
| 31-120, 50-84 | 895 | Coordenadas → Coordinates |
| 98-224, 141-159 | 841 | Encoder Temporal → Temporal Encoder |
| 34-116, 173-207 | 963 | (hora, dia) → (hour, day) |
| 92-229, 255-273 | 960 | Encoder Categórico → Categorical Encoder |
| 37-115, 289-323 | 946 | Categorias → Categories |

So the "zero pixels changed outside the six label rectangles" claim holds, measured. Nothing else
in the diagram moved.

**Translation fidelity, label by label**, checked against the terms the chapter's own English
prose and headings use:

| was | now | chapter's own usage |
|---|---|---|
| Encoder Espacial | **Spatial Encoder** | `\subsection{Spatial Encoder}` at `methodology.tex:97`; 8 hits in prose |
| Coordenadas (lat, lon) | **Coordinates (lat, lon)** | "geographic coordinates" throughout; 13 hits |
| Encoder Temporal | **Temporal Encoder** | `\subsection{Temporal Encoder}` at `methodology.tex:124` |
| Timestamps (hora, dia) | **Timestamps (hour, day)** | "hour of day and day of week" (`methodology.tex`, the Time2Vec paragraph); `timestamp` is a registered term (GLOSSARY §4 protocol terms via the paper's own usage, and used twice in the chapter) |
| Encoder Categórico | **Categorical Encoder** | `\subsection{Categorical Encoder}` at `methodology.tex:139` |
| Categorias (POI graph) | **Categories (POI graph)** | "Categories"/"category" throughout; 16 hits |

All six are faithful and all six land on the registered term. `hora, dia` → `hour, day` is the one
that could have drifted (a literal "hour, day" is terser than the prose's "hour of day and day of
week"), and it does not: it is the compressed form of the chapter's own sentence, inside a
diagram box where the long form would not fit, and the prose defines it.

**Finding 4 (MINOR), and it is the reason to look at the image.** The figure's central box label
reads **`MTLNet`**, capital N — the published spelling, not the dissertation's canonical
`MTLnet` (`GLOSSARY.md:41`). Measured, not eyeballed: the label's ink bounding box is x 759-804,
y 42-50; rendering candidates in Helvetica Bold 13 px and matching by IoU gives **0.530 for
`MTLNet`** against **0.442 for `MTLnet`**, and the fourth glyph's bitmap is a full-height N
(9 rows, x-height ascender present) rather than an x-height n. The `.drawio` source confirms it:
its cell value is `<b>MTLNet</b>`.

This is not a translation defect and it is not wrong on its own terms — the raster is part of a
published, co-authored figure, and leaving it alone is defensible. The finding is a **disclosure
gap**: Appendix B's normalization paragraph (`apx_b_errata.tex:234`) tells the reader the name was
normalized "at all 25 places where the name appears in the printed chapter: 21 in prose, one in a
subsection heading, one in a figure caption, and two in table headings" — and the figure's own
raster label is not in that inventory, so a reader comparing the two documents finds
`MTLnet` in the Figure 4.1 **caption** and `MTLNet` inside the **image the caption describes**,
one line apart on p. 47, with the appendix accounting for the first and silent about the second.

**Finding 5 (NIT), same paragraph — and a correction to my own first measurement of it.**

> **Corrected 2026-07-28, after an audit caught my own contradiction.** My first pass raised this as
> a MINOR defect asserting "**2** subsection headings ... The appendix counts **one**; there are
> two." **That was wrong, and Appendix B's "one in a subsection heading" is right.** I had counted
> both `\subsection` lines that print the name without asking which of them was ever *published*.
> Measured: `\subsection{Baseline: MTLnet with DGI}` (`methodology.tex:87`) **is** in
> `src_en/sections/metodology.tex`, so it is reproduced text and was normalized;
> `\subsection{The MTLnet framework}` (`related.tex:42`) is **not** in `src_en` — it is the
> dissertation-authored recap subsection, ledger row C2 and addition #2 of §2 above, so it never
> carried the published spelling and there was nothing there to normalize. A paragraph about "places
> where the reproduced text departs from the published article" is correct to exclude it. The same
> test also removes four prose sentences and both table headings from the normalized set, because
> they are dissertation-authored or errata-rewritten rather than reproduced. My error was applying a
> "does it print the name" filter where the paragraph's own subject requires a "was it published"
> filter.

What survives is a much smaller point about the total. The paragraph's four rows are not all
counted under one convention, so `25` is not reproducible from any single reading:

| Counting convention | prose | subsec. | caption | tables | total |
|---|---|---|---|---|---|
| every printed lowercase site | 23 | 2 | 1 | 2 | **28** |
| every printed lowercase site, minus the preface | 21 | 2 | 1 | 2 | **26** |
| only sites normalized from a published `MTLNet` | 18 | 1 | 1 | 2 | **22** |
| **Appendix B prints** | **21** | **1** | **1** | **2** | **25** |

The claimed `21 in prose` matches the middle convention exactly; the claimed `one in a subsection
heading` matches the bottom one exactly. Each row is defensible on its own; the sum of rows counted
under two different conventions is not a quantity. Nothing in the reproduced text is wrong, no
reader is misled about a departure, and the count has already been re-measured once this project
(24 → 25, after persona 12 caught the first tally) — which is why this is a NIT and not a defect.

*Closes when* the paragraph states its counting convention in the same sentence (for example "at
every place in the reproduced text where the published article printed the name: 18 in prose, one
in a subsection heading, one in a figure caption, and two in table headings", noting separately
that the preface and the recap subsection are dissertation-authored and so are not departures), or
the author rules that the approximate total is adequate for the purpose and the row stands. The
disclosure gap of Finding 4 is the item in this paragraph actually worth an edit.

---

## 6 · Finding 6 — `make check` FAILS, and the cause is not Chapter 4

The task brief states `make check` all gates pass. It does not, at `01915ba7`:

```
== 'this paper' / 'this article' inside chapters ==
chapters/apx_b_errata.tex:307:This article differs from the other two in a way that changes what this section has to record.
...
make: *** [check] Error 1
```

**This is not a regression from today's per-section split, and not mine.** The sentence entered at
commit `d1911c0a`, and it is present in `apx_b_errata.tex:307` at `1ef83867` (the revision the
brief measured) — I extracted that blob and ran the old gate's own grep against it, which matches.
So the gate was failing before the split too; the split changed `CH` from `chapters/*.tex` to
`"chapters/*.tex chapters/*/*.tex"` but `apx_b_errata.tex` was always in scope.

The sentence itself is defensible prose: it is the Article 3 section explaining that the MobiWac
manuscript is under review rather than published. The gate is a blunt instrument that cannot tell
"this article" the deictic from "this article" meaning the reproduced paper. Either the sentence is
reworded ("The third article differs...") or `apx_b_errata` is added to that gate's exclusion list,
which is already done for the banned-words gate on the grounds that this appendix quotes published
text.

I also confirmed the split did not damage Chapter 4: reconstructing the chapter by inlining the
five `\input`s and comparing to the `1ef83867` blob gives **byte-identical printed prose**
(39,410 characters both sides); the only differences in the full byte stream are the five new
provenance comment headers. The "purely mechanical, render byte-identical" claim holds for this
chapter, measured rather than trusted. The verdict-verb sweep's four hits (including
`4_courb/methodology.tex:36`) are the word "Pareto", which that gate greps for review rather than
failure, and it does not set `FAIL`.

---

## 7 · Terminology landing report

Every PT term maps to the registry's canonical EN name, at every site. Counts are over the printed
chapter (comments stripped):

| PT term (published) | Canonical EN (GLOSSARY) | Chapter | Non-canonical variants |
|---|---|---|---|
| check-in | check-in | 11 | 0 ("event", "visit record": 0) |
| POI / local | POI / place | 89 | 0 ("venue": 0) |
| região | region | 14 | 0 ("area", "cell": 0) |
| aprendizado multitarefa | multi-task learning / MTL | 10 | 0 ("multitask learning": 0) |
| compartilhamento rígido de parâmetros | hard parameter sharing | 3 | 0 |
| validação cruzada / folds | cross-validation / fold | 8 | 0 |
| F1-Score médio por categoria | Average F1-Score per category | 2 | 0 |
| classificação de categoria de POI | POI Category Classification | 10 | — |
| predição do próximo POI | Next-POI Prediction | 16 | — |
| encoder espacial / temporal / categórico hierárquico | spatial / temporal / hierarchical categorical encoder | 8 / 1 / 4 | 0 |
| embedding monolítico | monolithic embedding | 10 | 0 |
| janelas não sobrepostas | non-overlapping windows | 1 | 0 |
| caminhadas aleatórias | random walks | 3 | 0 |
| MTLnet (baseline) | MTLnet | 26 printed | 2, both the registered expansion |
| ST-MTLNet (proposed) | ST-MTLNet | 13 | 0 |

**Task-name bridge.** The chapter keeps the paper's own "Next-POI Prediction" and the preface
states the mapping once: *"the term ``Next-POI Prediction'' used here denotes the frame's
\emph{next category} task (the category of the next visited place), not the exact-place task the
dissertation calls \emph{next place}."* That is the GLOSSARY §1 per-paper mapping, discharged
correctly, and the only occurrence of "next place" in the chapter is that delimiting sentence.

**Writing-law sweep on the chapter** (printed prose only): em-dashes **0**, unicode em-dashes
**0**, contractions **0**, "venue" **0**, "wins" as a verdict verb **0**, repo codenames **0**,
"mean F1" **0** (the v2 repair holds; the table's own metric name is used instead), "ensures" **0**.

---

## 8 · Coverage: what I verified clean

- **Sentence alignment, full chapter.** 202 printed sentences extracted from the wrapper and the
  five section files; 194 match the published source verbatim after sanctioned mechanical
  normalization; the 8 residual are the declared additions of §2. No sentence is unaccounted for.
- **Both directions.** Omission checked as well as addition: every claim-bearing sentence of the
  published PT prose has a counterpart in the chapter, except the front matter (title, authors,
  address, abstract, resumo, Acknowledgments) whose omission is ledger row B7 and is stated to the
  reader in Appendix B §B.2, and the `%`-commented HAVANA / Space2Vec / Nash-equation / PT
  future-work blocks, which do not render in the published paper either (ledger B8).
- **Errata interaction (persona §3).** Both known number errata are applied in the chapter text
  **and** listed in Appendix B Table B.3. Neither is silently fixed and neither is silently
  reproduced. ERRATA #3 (the `silva2025mtlnet` venue) is correctly handled at the bibliography
  level rather than in chapter text.
- **Reproduction statement (persona §4).** Present, first sentence of the preface, with the full
  published title in Portuguese, the venue ("Anais do X Workshop de Computação Urbana (CoUrb 2026,
  an SBRC workshop)"), pages 323 to 336, the DOI, and `\cite{paiva2026stmtlnet}`. The
  second-author contribution note follows in the same paragraph, including the presenter role and
  the MTLnet first-authorship. Every attribute matches the SBC SOL metadata I fetched.
- **Honesty disclosures.** The sample-stratified split is stated in the preface **and** at the
  protocol site; the "conclusions of the time, for that configuration" time-index is present; the
  "MTLnet as its only baseline / does not revisit the MTL-versus-single-task question" floor
  sentence is present. All three render (pp. 42, 52).
- **Render, not source.** Every positional or visual claim above was checked on a fresh
  `make defense` build (108 pages, `Output written on build/main.pdf (108 pages, 1339953 bytes)`),
  and the figure claims by decoding the raster.

**What reads well and should not be touched:** the Nash-MTL replacement clause is the best piece of
citation work in this chapter — it narrows an overclaim using the source's own vocabulary, glosses
the one unregistered term it needs, and its source comment cites page numbers for every component.
The protocol-addition block at `results.tex:14` is the model for how to add recovered facts to a
published chapter: three sentences, each declared, each with the code evidence in the comment, and
the deliberate refusal to claim the published runs came from that exact worktree.

---

## 9 · Findings summary

| ID | Sev | Anchor (phrase · file · line today) | What I measured | Closes when |
|---|---|---|---|---|
| L5-1 | — | "ensures that the update is beneficial" · `src/tables/courb/errata.tex:28` | The published PT reads "o que **garante** que a atualização seja benéfica" (galley p. 5); the EN "ensures" is a faithful translation. Overclaim is the ORIGINAL's. | **PASS** — no action. Appendix B row is correct. |
| L5-2 | MINOR | "carries nine marked additions" · `src/chapters/apx_b_errata.tex:262`; "The remaining three are the lead sentences" · `:275` | 8 additions measured, not 9. The category-table lead at `4_courb/results.tex:77` is the published sentence verbatim; its dissertation clause was dropped in the v2 repair. | "eight", and "the remaining two ... Tables 4.1 and 4.3". Ledger section C's C5 row updated too. |
| L5-3 | MINOR | "at all 25 places where the name" · `src/chapters/apx_b_errata.tex:234` | The Figure 4.1 raster label is `MTLNet` (IoU 0.530 Bold vs 0.442 for `MTLnet`; `.drawio` cell value `<b>MTLNet</b>`), one line from a caption printing `MTLnet`. Not in the appendix's inventory. | Inventory names the figure image, or states that it keeps the published spelling and why. |
| L5-4 | NIT (**downgraded from MINOR; my first measurement was wrong**) | same line, `:234` | **Appendix B's "one in a subsection heading" is CORRECT** — `\subsection{Baseline: MTLnet with DGI}` is in `src_en` and was normalized; `\subsection{The MTLnet framework}` is not, being the dissertation-authored recap (ledger C2). Residue: the four rows are counted under two different conventions, so `25` is reproducible under none (every printed site 28; minus preface 26; published-only 22). The `21 prose` row matches the second, the `1 subsection` row the third. | The paragraph names its counting convention in the same sentence, or the author rules the approximate total adequate. No reader is misled either way. |
| L5-5 | MINOR | "This article differs from the other two" · `src/chapters/apx_b_errata.tex:307` | `make check` exits `Error 1` on the 'this paper'/'this article' gate. Present at `1ef83867` too, so it predates today's split; not a Chapter 4 defect. | Sentence reworded, or `apx_b_errata` excluded from that gate as it already is from the banned-words gate. |

---

## 10 · Out-of-scope handoffs (one line each)

- `articles/CoUrb_2026/ERRATA.md` is **untracked**; it is cited as a source by the ledger and by
  Appendix B's provenance comments. Commit it or the trail is not reproducible.
- The ledger's `[VERIFY]` on the chapter-title wording is still open: the heading says
  "Spatio-Temporal POI Representations" where the paper's own EN title is "Spatio-Temporal
  Representations of Points of Interest". Author's call; not a fidelity defect since the preface
  carries the published Portuguese title in full.
- `src_en/references.bib` uses `church2017word2vec` where the chapter cites
  `mikolov2013word2vec,mikolov2013negsampling`. That is the CBIC bibliography erratum applied at
  merge, which is correct, but it means the chapter's citation for negative sampling differs from
  the published article's; the bibliography-errata table is the place that should say so.

## 11 · What I could not verify

- Nothing blocked. The published galley PDF was fetched and read, the method's paper (arXiv:2202.01017)
  was fetched and read, the raster was decoded and compared to its pre-edit version, and the render
  was rebuilt from source.
- One bounded limitation: I compared the chapter against the published **galley PDF text
  extraction**, whose accent handling required normalization (the SBC template places combining
  marks after the letter cluster). All string comparisons were therefore accent-insensitive and
  case-insensitive. This cannot hide a claim-strength or number difference, which is what this gate
  is for, but it would not catch a pure diacritic error inside a Portuguese quotation.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
