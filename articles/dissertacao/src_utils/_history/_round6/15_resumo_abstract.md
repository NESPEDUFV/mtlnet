# 15 · The Resumo and the Abstract, cut as a claim-parity pair

**Track:** cut and rebuild the Resumo and the Abstract as a claim-parity pair (WRITING_LAW §6), and
clear the near-blank page they caused.
**Files edited:** `src/0_main.tex` only, and inside it only the Resumo prose block, the Abstract
prose block, and their surrounding comments. The two keyword blocks were **not** touched: they were
already compliant (one term per line, lowercase except proper nouns, no punctuation, PT mirroring
EN, UFV_COMPLIANCE §2) and the `minipage` guard around each is what now lets the keyword block sit
with its own Resumo.
**Baseline commit measured:** `870f882c`. **Date:** 2026-07-28.
**Status of the new prose:** `[NEEDS SIGN-OFF]`. Frame-matter prose is the author's own; he approves
every word. Nothing here is applied to a published or submitted chapter, so no errata row is owed.

---

## 1 · What was measured, and on what convention

Every count in this report comes from the **rendered page**, not from the source, and every count in
every table below is on **one convention**, applied identically to our blocks and to the five
defended dissertations. The instrument is `src_utils/_history/_round6/_measure_abs.py` (copied into
`src_utils/` alongside this report):

1. Take the text layer of the page or pages the block occupies.
2. Strip the UFV identification header: author-venue-year line, bold title, advisor and co-adviser
   fields, the `Resumo`/`Abstract` heading, and any name-only line left over where an advisor's name
   wrapped past its field label.
3. Strip the keyword block: everything from `Palavras-chave` / `Keywords` onward.
4. **Words** = tokens of letters (accented letters included) or digits. Punctuation-only tokens do
   not count. A hyphenated compound counts as **one** word.
5. **Sentences** = terminal `.`, `!`, `?`, excluding decimals, single-capital initials, and
   `Sec. Fig. cf. e.g. i.e. et al. Dr. Prof. M.Sc. Ph.D. U.S.` and similar.
6. **Mean** = words / sentences.
7. PDF line-break hyphenation is undone before any phrase matching. This matters: pdfium emits a
   soft-hyphen codepoint at a justified break, so a raw text-layer search for `user-disjoint
   cross-validation` **fails on a page that contains it**. My first floor check reported six false
   failures for exactly this reason, and the sweep was rerun with the normalization in place. It is
   the same class of error as the round-5 figure-label finding: the text layer is not the page.

### The exemplar envelope, re-measured

The brief supplied an envelope; I re-measured it on my own convention rather than trusting it. The
numbers move by a few words per block, because a stripping rule that catches a wrapped advisor name
differs from one that does not, but **the envelope does not move materially**.

| block | words | sentences | mean | brief's figure |
|---|---:|---:|---:|---|
| canesche Resumo | 265 | 11 | 24.1 | 254 / 11 / 23.1 |
| canesche Abstract | 250 | 12 | 20.8 | 241 / 12 / 20.1 |
| germano Abstract | 218 | 10 | 21.8 | 214 / 10 / 21.4 |
| lapsusvgi Resumo | 282 | 8 | 35.2 | 294 / 12 / 24.5 |
| lapsusvgi Abstract | 225 | 6 | 37.5 | 222 / 6 / 37.0 |
| passe Resumo | 233 | 10 | 23.3 | 229 / 10 / 22.9 |
| passe Abstract | 195 | 10 | 19.5 | 193 / 10 / 19.3 |
| viegas Abstract | 202 | 8 | 25.2 | 204 / 9 / 22.7 |

- **All eight blocks:** 195 to 282 words, 6 to 12 sentences, mean 19.5 to 37.5.
- **Resumos only (n=3):** 233 to 282 words, 8 to 11 sentences, mean 23.3 to 35.2.
- **Abstracts only (n=5):** 195 to 250 words, 6 to 12 sentences, mean 19.5 to 37.5.

The one block where my figures and the brief's diverge beyond rounding is the **lapsusvgi Resumo**
(282/8/35.2 against 294/12/24.5). Its sentence count is the disagreement: that Resumo contains
`et al.` and a decimal, and my sentence rule does not split on either. I did not reconcile the two
instruments further, because the envelope's outer bounds are set by other blocks in both readings.
**[VERIFY: lapsusvgi Resumo sentence count, 8 by my rule against 12 by the brief's.]**

---

## 2 · Before and after, both blocks

Measured on the rendered pages of the defense build, same convention throughout.

| block | words | sentences | mean | where it rendered |
|---|---:|---:|---:|---|
| **Resumo, before** | **500** | 10 | **50.0** | p.3, keyword block orphaned to p.4 |
| **Resumo, after** | **310** | 11 | **28.2** | p.3, keyword block on the same page |
| **Abstract, before** | **423** | 10 | **42.3** | p.5 |
| **Abstract, after** | **271** | 11 | **24.6** | p.4 |

**Cut: 190 words from the Resumo, 152 from the Abstract.** Against the envelope, the Resumo lands
28 words above the highest defended Resumo (282) and the Abstract 21 above the highest defended
Abstract (250); the Abstract is **inside** the all-eight-blocks bound of 282. Both mean sentence
lengths, 28.2 and 24.6, sit inside the defended range on either reading, where before the cut they
were 50.0 and 42.3, that is, well outside it. The pair remains slightly long, and this is a
deliberate stopping point rather than an oversight: the remaining excess is the price of the claim
floor in §4 below, which names sixteen claims that both blocks must carry, one of which (the result)
needs its metric, its selection convention, its margin, and its test named to satisfy
WRITING_LAW §3. Cutting to 250 would require dropping a hedge or a convention. **The author's
ruling was that the blocks are too long; it was not that they should shed a qualification.** If he
wants the last twenty to thirty words, the cheapest honest source is the protocol clause, whose
detail is also in Chapter 5, not the result sentence.

### Parity, verified sentence by sentence

The two blocks now carry **eleven sentences each, in one-to-one correspondence.** Verified on the
rendered pages:

| # | PT words | EN words | the claim the sentence carries |
|---|---:|---:|---|
| 1 | 17 | 15 | check-in defined as a visit by a user to a POI |
| 2 | 39 | 38 | the two tasks; the next-place exclusion; both read the same trace; MTL named and expanded |
| 3 | 27 | 26 | sharing can hurt a task; the question and its "what does it depend on" clause |
| 4 | 6 | 5 | three studies answer it |
| 5 | 30 | 24 | study 1: MTLnet, place-level embedding, hard sharing, no consistent gain |
| 6 | 34 | 30 | study 2: input replaced, category rose in every state, representation was the bottleneck |
| 7 | 31 | 24 | study 3: check-in level, one vector per visit, cross-attention trunk |
| 8 | 17 | 16 | the six datasets: five U.S. states from Gowalla, Istanbul from Massive-STEPS |
| 9 | 58 | 52 | the protocol and the category result with its range and joint-best convention |
| 10 | 29 | 25 | the region result: four of six, TOST non-inferiority within two points at the other two |
| 11 | 23 | 21 | the answer is conditional, and on what |

A mechanical floor check confirms **all nineteen tested claim strings present in both languages**,
zero failures, after hyphenation normalization.

---

## 3 · The near-blank page

**Before:** the Resumo ran to p.3, its `Palavras-chave` block broke to **p.4 alone, 21 words on an
otherwise blank page** (the count `ANCHORS.md` §2 item 3 records), and the Abstract began on p.5.

**After:** the Resumo and its keyword block sit together on **p.3**; the Abstract and its keyword
block sit together on **p.4**; the List of Figures starts on p.5. The orphan page is **gone, and the
document is one page shorter**: the defense build goes from **105 pp to 104 pp**.

This was verified on the **rendered image**, not only in the text layer. Both pages were rasterized
and read: p.3 shows the `Resumo` heading, the catalog header, one prose block, and the five
Portuguese keywords, with about a third of the page as trailing whitespace; p.4 shows the same
structure in English. No orphan, no widow, no keyword block alone.

The `minipage` guard from round 5 was left exactly as it was. It is what makes the fit possible: the
label and the five keywords are one unbreakable box, so TeX can place the whole block in the space
the shortened Resumo leaves. The round-5 comment recording why `needspace` was rejected is preserved
in the file.

---

## 4 · The claim floor: what was kept, what was cut, and where each cut claim now lives

### 4.1 · Kept, in both languages

Every item the brief names as a hard floor is present in both blocks, verified mechanically:

| floor item | PT | EN |
|---|---|---|
| the research question, and that the answer is CONDITIONAL | "permanecia em aberto" / "A resposta é, portanto, condicional" | "was unresolved" / "The answer is therefore conditional" |
| representation dominates | "o gargalo era a representação, e não a arquitetura" | "the bottleneck was the representation, not the architecture" |
| decomposing the input moved the needle more than architecture | "O segundo substituiu apenas a entrada" | "The second replaced only the input" |
| one joint model finally outperforms both dedicated models | "supera os modelos dedicados" | "outperforms the dedicated models" |
| the two tasks | "próxima categoria" / "próxima região" | "next category" / "next region" |
| the exact next PLACE is not predicted | "mas não o ponto de interesse exato" | "though not the exact next place" |
| category at all six, 5.3 to 9.4 macro-F1 points | "por 5,3 a 9,4 pontos de macro-F1" | "by 5.3 to 9.4 macro-F1 points" |
| the joint-best selection convention | "sob uma seleção *joint-best*" | "under a joint-best selection" |
| region at four of six | "supera em quatro deles" | "outperforms at four of them" |
| TOST non-inferiority within a two-point margin at the other two | "não-inferioridade dentro de uma margem de dois pontos de Acc@10 (TOST)" | "non-inferiority within a two-point Acc@10 margin (TOST)" |
| Gowalla over five U.S. states plus Istanbul from Massive-STEPS | "cinco estados dos Estados Unidos, do Gowalla, e Istambul, do Massive-STEPS" | "five states of the United States from Gowalla and Istanbul from Massive-STEPS" |
| the protocol: user-disjoint CV, 20 fitted models, n=4 inferential unit | "vinte modelos ajustados por configuração, quatro inicializações aleatórias sobre cinco partições fixas, e testes pareados sobre as quatro médias por inicialização" | "twenty fitted models per configuration, four random initializations over five fixed folds, and paired tests on the four initialization means" |

**Verbs stayed bound to their tests.** EN uses `outperform` for the paired superiority cells and
`statistically matches` only where TOST non-inferiority holds inside the two-point margin; PT uses
`supera` and `equipara-se estatisticamente` in the same places. Arizona is not upgraded. No
`beats` / `wins` / `ties` / `vence` / `empata` appears in either block.

**Publication status is not mentioned in either block,** before or after, so the brief's
"submitted, under review" requirement is satisfied vacuously. The status wording lives in
Chapter 1's organization section, where the venue bullets carry it. This is deliberate: an abstract
that names three venues and their review states spends words on bibliography rather than on claims.

### 4.2 · Cut, with the claim traced to its surviving site

Six claims left the pair. **None is on the floor.** Each survives in the body, and I quote the
surviving prose rather than citing a line number, per `ANCHORS.md` §5.

| cut sentence or clause | the claim it carried | where the claim lives now |
|---|---|---|
| "e custou mais para treinar" / "and cost more to train" | study 1 cost more to train than the dedicated pair | `1_introduction.tex`: "two dedicated single-task models, and it cost more to train"; `6_conclusion.tex`: "and it cost more to train" |
| "um resultado nulo relatado como um achado" / "a null result reported as a finding" | the null result was published as a finding, not buried | `1_introduction.tex`: "null result as a finding, together with three candidate explanations" |
| "um modo de falha conhecido como transferência negativa" / "a failure mode known as negative transfer" | the failure mode has a name | the mechanism stays in both blocks ("compartilhar parâmetros pode prejudicar uma das tarefas" / "Sharing parameters can hurt one of the tasks"); the **name** is defined in `2_fundamentals.tex`: "known as negative transfer" |
| "Foi também o estudo que introduziu a tarefa da próxima região; os dois primeiros pareavam a classificação de categoria com a previsão da próxima categoria, de modo que o próprio par de tarefas mudou ao longo da coletânea" and its EN twin | the task pair itself changed across the three studies, and study 3 introduced next region | `1_introduction.tex`: "The task pair therefore evolved across the three studies, from static category classification plus next category in the first two to next category plus next region in the last"; `6_conclusion.tex` limitation: "The task-pair confound"; `5_mobiwac.tex`: "this chapter introduces the next-region task" |
| "apresentados como uma coletânea de artigos na ordem em que aconteceram: um resultado negativo, seu diagnóstico e sua resolução" / "presented as a collection of articles in chronological order: a negative result, its diagnosis, and its resolution" | the coletânea format and the arc's three-beat shape | `1_introduction.tex`: "this dissertation is organized as a collection of works, with each central chapter presented as an independent article". The three-beat shape survives in the pair implicitly: sentences 5, 6 and 7 **are** the negative result, the diagnosis and the resolution, in order |
| "em vez de atribuir o mesmo vetor a todas as visitas a um mesmo lugar" / "instead of assigning the same vector to every visit to a place" | the contrast that makes "check-in level" meaningful | `6_conclusion.tex`: "each visit its own vector instead of assigning every visit to a place the same one"; `2_fundamentals.tex` and `5_mobiwac.tex` both carry "its own vector" |
| "entre dois fluxos específicos por tarefa" / "between two task-specific streams" | the trunk sits between two task-specific streams | `6_conclusion.tex`: "task-specific streams, with a private spatial path for the region task" |
| "teste de não-inferioridade e uma auditoria de vazamento" / "non-inferiority testing, and a leakage audit" | a leakage audit was run. **Non-inferiority is NOT cut**: it moved into the region sentence, where it belongs with the verdict it licenses | `1_introduction.tex`: "four paired observations, non-inferiority margins, and a leakage audit" |

Two further sentence-level compressions changed no claim: "Esta dissertação responde a essa pergunta
ao longo de três estudos" became "Três estudos respondem a essa pergunta" (an abstract does not need
to say that the dissertation is the thing doing the answering), and the 77-word protocol-plus-result
sentence was split at the task boundary so category and region each get their own sentence with
their own verdict verb.

---

## 5 · Source ledger: every number in the pair

No number in the pair is computed. Each is quoted from a file, with its convention.

| number, as it appears | source of record | field | convention |
|---|---|---|---|
| "5,3 a 9,4 pontos de macro-F1" / "5.3 to 9.4 macro-F1 points" | `docs/studies/closing_data/v17_completion/stats_n20/RESULTS.md` §1, category superiority table | FL Δcat **+5.34** is the low end, AZ **+9.40** the high end; CA **+6.31**, TX **+7.31**, AL **+7.73**, Istanbul **+8.59** all fall inside | macro-F1 points, MTL minus the dedicated single-task ceiling, joint-best arrays, seed-level paired *t*, n=4 inferential unit. The same range is stated in `6_conclusion.tex`: "by 5.3 to 9.4 macro-F1 points" |
| "nos seis" / "at all six" (category) | same file §1 (AL, AZ, FL, Istanbul: "outperforms") and §1b (CA, TX: "outperforms (provisional)") | six of six | Holm-corrected at α=0.05 on the paired-*t* footing for the four fully-n=20 datasets; CA and TX on a seed-0 footing and marked provisional in the record. **This provisional footing is not disclosed in the pair**; it is not disclosed in the pre-cut pair either, and `6_conclusion.tex` does not carry it in the frame. See §7. |
| "quatro deles" / "four of them" (region) | `src/tables/mobiwac/results.tex`, region block | four `$^{\uparrow}$` marks (Istanbul, FL, TX, CA) against two `$^{\approx}$` marks (AL, AZ) | Acc@10, four seeds × five folds. The table caption defines `$\uparrow$` as "supported improvement" and `$\approx$` as "a non-inferior match (TOST, ±2 pp)" |
| "margem de dois pontos de Acc@10 (TOST)" / "two-point Acc@10 margin (TOST)" | `stats_n20/RESULTS.md` §1 region table; `GLOSSARY.md` §4 row "TOST non-inferiority" | δ_reg = 2 pp, pre-registered; AL and AZ both "matches (TOST)" | two one-sided tests, 90% CI inside ±2 pp. AZ's CI lower bound is +0.001 and the record says explicitly "do NOT upgrade to beats"; the pair does not upgrade it |
| "vinte modelos ajustados" / "twenty fitted models" and "quatro médias por inicialização" / "four initialization means" | `GLOSSARY.md` §4 rows "n = 20 (fitted models) and n = 4 (inferential unit)" and "paired superiority test" | 4 seeds × 5 folds = 20 fitted models; the reported test pairs the four per-seed means | design in `.../STATISTICAL_PROTOCOL.md`; executed footings in `.../stats_n20/RESULTS.md` |
| "seleção *joint-best*" / "joint-best selection" | `GLOSSARY.md` §4 row "joint-best convention" | both tasks read at the one saved model per fold, the validation-selected epoch | defined in prose at `5_mobiwac.tex`: "every reported model is one saved artifact per fold, read at its validation-selected epoch ... with both tasks read from that one model" |
| "cinco estados dos Estados Unidos" / "five states of the United States" | `GLOSSARY.md` §3 row "Gowalla"; `1_introduction.tex` scope section | AL, AZ, FL, CA, TX | |
| "seis conjuntos de dados" / "six datasets" | `src/tables/mobiwac/results.tex` | six rows in each block: Istanbul, AL, AZ, FL, TX, CA | |

### The "four of six" versus "three of the six" reconciliation the brief asked about

The brief warned that another track was reconciling this. **I measured the current state rather than
assuming.** `grep` for `three of the six` and `three of six` across all of `src/*.tex` and
`src/chapters/*.tex` returns **zero hits, in prose or in comments.** The live text says:

- `6_conclusion.tex`, opening: "on the region task at four of the six, and is statistically
  non-inferior to them, within a two-point margin (TOST), at the other two".
- `6_conclusion.tex` §6.1: "and on the region task at four of six, Istanbul, Florida, California,
  and Texas, while remaining statistically non-inferior within a two-point margin (TOST) at Alabama
  and Arizona."
- `1_introduction.tex`: "on the region task at four of six".

Those agree with each other, with the four `$\uparrow$` rows of the results table, and with the pair
as I have written it. **The disagreement the brief anticipated is not present in the tree I
measured.** The one nearby "three" is a different quantity and is correct: `6_conclusion.tex` reads
"four Gowalla states, three of which are among the five we report", which is about a
gradient-conflict pool, not about the region verdicts. `ANCHORS.md` §3 already records that as
corrected.

---

## 6 · Build, measured in isolation

Seven other files in `src/` were modified by other agents while I worked, and HEAD advanced twice.
A shared-tree build could not attribute a page-count change to my edit. So every number below comes
from a tree containing **`870f882c` plus my `0_main.tex` and nothing else**, verified by a recursive
diff against the baseline tree before building: exactly one file differs.

| | baseline `870f882c` | with my cut | delta |
|---|---|---|---|
| DEFENSE pages | 105 | **104** | **-1**, the orphan page |
| FINAL pages | 100 | **100** | 0 |
| `tex_errors` | 0 | **0** | 0 |
| `overfull_hbox` | 0 | **0** | 0 |
| `overfull_vbox` | 0 | **0** | 0 |
| `undef_cite` | 0 | **0** | 0 |
| `undef_ref` | 0 | **0** | 0 |
| `bibtex_problems` | 0 | **0** | 0 |
| `oversized_floats` | 0 | **0** | 0 |
| `make defense` / `make final` | exit 0 | **exit 0** | both produce a PDF under `-halt-on-error` |

**The FINAL variant is untouched, and this is a measurement rather than an inference.** The Resumo
and Abstract live inside `\ifdefensebuild`, so the AcademicoPG build never sees them. The full text
layer of `main_final.pdf` was hashed before and after: **100 pages and SHA-256
`537bb752e238485e390ef9384c4d7c607141348661fdc30db5e8e04b3f0f30d5` in both builds, identical.** No
FINAL pagination moved, because no FINAL content changed.

### The build gate, validated in both directions on my own source

The round brief says to trust `build.sh`'s `tex_errors` only because it was validated both ways, and
an open reviewer finding against an earlier pass in this round notes that a validation run captured
`tail`'s exit status through a pipeline instead of `build.sh`'s own. So I validated it against **my**
file rather than inheriting the claim:

| source state | `tex_errors` | `build.sh` exit | `make defense` exit |
|---|---:|---:|---:|
| my committed `0_main.tex` | 0 | **0** | **0** |
| the same file with `\undefinedmacroXYZ` injected into the Resumo block | **1** | **1** | **2** |

The broken run still wrote a 104-page PDF, exactly the trap that let six commits carry a clean build
report off a source that would not compile, and `build.sh` printed its own warning that the PDF is
not the document. My invocations capture the status directly (`bash build.sh . defense >/dev/null
2>&1; echo $?`), not through a pipe, so the number reported is `build.sh`'s. Also checked explicitly:
`(exit 7) | tail -1; echo $?` prints **0** while `(exit 7); echo $?` prints **7**, which is the
mechanism behind that finding. The injected macro was reverted and the restored file hashes identical
to the committed one, MD5 `e4dbcefeff6c6a2d32a21e3987ae214d`.

`make check`: the substantive gates pass (em-dash 0, contractions 0, banned words 0, repo codenames
0, undefined refs and cites 0, bibtex clean, torn sentences 0, trapped prose 0, sweep-guard
self-tests 4/4). It still exits nonzero, for the same reason it exits nonzero on the untouched
baseline: the recorded page counts in `src_utils/PENDENCIAS.md` and `src_utils/codex_reviewer.md`
are stale. On the baseline it reports **6 stale claims**; with my cut it reports **3**, because the
defense count in those files, 104, is now correct again and only the final count, 99 against 100, is
still stale. Those two files are not mine and other agents are editing them, so I did not run
`sync_page_counts.py --write`. **Handoff: whoever owns the registers should re-run it once the round
settles, and the FINAL count is 100.**

---

## 7 · `[VERIFY]` flags and what I could not confirm

> ### CORRECTION to flag 1, added 2026-07-28 by the round supervisor, before this flag was acted on
>
> **Flag 1 below reads a superseded section of the record and its conclusion is wrong.** I checked
> `stats_n20/RESULTS.md` directly. The file is at **rev 4, 2026-07-13**, and its header states that
> A1 landed the CA and TX v17 MTL **n=20** runs on 2026-07-11, so the pre-registered six-dataset
> family Holm now runs. Its table reports all six datasets rejecting at α = 0.05, CA at Δcat +6.45
> with Holm-adjusted p = 8.9e-07 and TX at +7.45 with the same adjusted p, and it records that the
> n=20 result **confirms** the seed-0 provisional verdicts with no verdict changed.
>
> The §1b material the flag quotes sits under a heading that reads **"(superseded) M1-PARTIAL — rev
> 3, 2026-07-08"**, and rev 4 says in terms that the provisional material below is "retained for the
> record."
>
> **So "at all six" is correct and carries no undisclosed provisional footing.** No frame text needs
> a qualification, and none should be added on the strength of this flag. The flag is left in place
> below rather than deleted, because the reading error is instructive: the record keeps its own
> superseded revisions inline, and a search that lands inside one will find a real sentence that
> stopped being true. **Anchor on the revision header, not on the first matching line.**
>
> This is also why the flag was worth raising. It was raised rather than acted on, which is the
> correct behavior; the cost of checking it was five minutes and the cost of acting on it would have
> been weakening a defensible claim in the pair, the conclusion and the paper.


1. **[VERIFY] The CA and TX category cells are provisional in the statistical record, and no frame
   text says so.** `stats_n20/RESULTS.md` §1b labels both "outperforms (provisional)" on a seed-0
   footing, pairing fold-*k* with fold-*k* at a single seed, and states "These two cells are NOT in
   the §1 Holm family". The pair says "at all six" without that qualification. **This is inherited,
   not introduced**: the pre-cut pair said "at all six datasets studied" too, and
   `6_conclusion.tex` §6.1 says "at all six datasets, by 5.3 to 9.4 macro-F1 points" with no
   provisional note either. The claim is therefore consistent across the document, which is why I
   did not change it in a block whose only job is to mirror the body. It is a live honesty question
   for whoever owns Chapter 5 and 6, and it is the largest one I found this round.
2. **[VERIFY] "Modelos ajustados" for "fitted models" is still not in `GLOSSARY.md` §6.** The term
   was already in the Resumo before my cut, and the round-5 comment in `0_main.tex` flags it as
   proposed and pending. I kept it rather than substituting an unregistered alternative, and I am
   re-flagging it: the glossary owner should either register it or supply the canonical PT.
3. **[VERIFY] Four more PT phrasings I used are compositional rather than registered.** GLOSSARY §6
   registers `validação cruzada (5 partições)`, `inicialização aleatória (semente)`,
   `não-inferioridade (TOST, margem de 2 pontos)` and `supera / equipara-se`, and I built from those
   entries: "usuários disjuntos entre treino e teste" (the §3 EN entry is `user-disjoint split`;
   §6 has no PT row for it), "partições fixas", "médias por inicialização", and "seleção
   *joint-best*" (kept as the English term of art, as the pre-cut Resumo had it). Each is a
   composition of registered material rather than a new term, so I did not treat it as a §6
   violation, but the strict reading of the fail-closed rule is that §6 should grow four rows.
   **Handoff to the glossary track, before the next PT pass.**
4. **[VERIFY] The pair is still above the defended envelope**: Resumo 310 words against a 282
   maximum, Abstract 271 against 250. Reported rather than smoothed. §2 explains why I stopped
   here and where the next twenty to thirty words would have to come from.
5. **[VERIFY] The lapsusvgi Resumo sentence count** differs between my instrument and the brief's,
   8 against 12. Both agree on words to within twelve. Not reconciled; it does not move the
   envelope's bounds.
6. **Could not confirm: whether the author wants the coletânea framing back in the Abstract.** I cut
   "presented as a collection of articles in chronological order" as bibliographic rather than
   claim-bearing, on the reading that WRITING_LAW §5's abstract formula wants the validation design
   and the headline number, not the document's own structure. Chapter 1 carries it. If he wants it
   in the Abstract, it costs about eleven words per language and the pair goes back over 321 / 282.
7. **Could not confirm: the "another track is reconciling four of six against three of six" premise.**
   I searched the whole of `src/` and found no "three of six" claim, in prose or comment. Either
   that track landed before I measured, or the disagreement was somewhere I did not look. I report
   the state I measured; I did not coordinate with that track directly.
8. **Not verified by me: the seven other `src/` files that other agents changed during my window.**
   My isolated build deliberately excludes them, so my page counts do not describe the shared tree.
   Anyone reading 104/100 as the state of the repository should rebuild after the round settles.

---

## 8 · The one substantive addition

The cut pair says something the pre-cut pair did not: **"mas não o ponto de interesse exato" /
"though not the exact next place".** The brief lists the next-place exclusion as a floor item, and
the pre-cut pair did not carry it. Round 5 had removed a reserved-term collision from the Resumo
(the round-5 comment in the file records the reasoning) but the removal left the exclusion itself
unstated in both blocks; a reader of the front matter met the exclusion only at Chapter 1. It is now
in both, positively phrased, in the sentence that introduces the two tasks, which is the earliest
place it can go. The wording is the body's own claim: `1_introduction.tex` states "The exact next
place is not predicted anywhere in this work", and `GLOSSARY.md` §1 reserves *next place* for the
task this dissertation delimits but does not study.

This is an added claim in frame-matter prose, so it is `[NEEDS SIGN-OFF]` like the rest of the block,
and it is called out separately here because it is the one place where the cut made the pair say
more rather than less.

---

## 9 · The two tools this track leaves behind

Both live in `src_utils/_history/_round6/` and are committed with this report, because the measurement is the
part of this work that is worth repeating and the counting convention is the part that is easy to get
subtly wrong.

- **`_measure_abs.py`** takes a JSON spec of `{label, pdf, pages}` and reports words, sentences and
  mean per block under §1's convention. It is the instrument that produced every count in this
  report, ours and the exemplars', which is what makes the before/after comparable.
- **`_check_pair_parity.py`** re-runs the claim-parity floor check and the law sweep against a built
  PDF: nineteen claim strings that must appear in both languages, sentence-count parity, and the
  em-dash / contraction / banned-word / verdict-verb / codename sweep.

`_check_pair_parity.py` was **validated in both directions**, per the round's own rule that a check
which has never failed is not a check. Against the freshly built pair it reports 19/19 claims present
and PT 11 / EN 11 sentences. Against the repository's stale `build/main.pdf`, where the Abstract is
still on p.5, it dies with a `ZeroDivisionError` on an empty p.4 rather than quietly reporting a
pass. That loud failure is deliberate and is documented in the file's own docstring: it means the PDF
does not match the source, which is exactly the condition that let a broken build be certified clean
six times earlier in this project's history.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
