# 60 · Terminology standardization — audit of AUT item 2

**Track:** AUT (author's own considerations), `src_utils/PENDENCIAS.md` §4, item **2 only**.
**Written:** round 13. **Author's premise, verbatim:**

> "Padronização das palavras tecnicas. Palavras que já estão no 'List of abbreviations and
> acronyms' estão sendo escritas de forma distintas pelo texto. Um exemplo é Point of Interest que
> em muitos locais aparece como Point-of-Interest. Outro detalhe é o uso correto dessas palavras
> como no caso de Multi-Task Learning, essa palavra no artigo original é escrita como: Multitask
> Learning, sem o hifén sem contar que o APA Style, também define a preferencia por uso de plavras
> sem hifén; enfim faça uma pesquisa para validar essa é outras palavras técnicas e vamos
> substituir onde necessario."

**Verdict: PARTLY_CONFIRMED.** Four separate claims are bundled in item 2, and they do not share a
verdict. The measurement below separates them.

| # | Claim | Verdict |
|---|---|---|
| 2a | POI is written two ways in the text | **CONFIRMED** (9 open vs 13 hyphenated, live prose) |
| 2b | MTL is written two ways in the text | **REFUTED for the live tree.** `multitask` 79, `multi-task` **0**. The split he saw was real and has already been swept; what survives is 22 occurrences inside `%` comments, which do not print |
| 2c | Caruana's original prints `Multitask Learning`, no hyphen | **CONFIRMED**, and the repo bib already agrees |
| 2d | APA Style prefers unhyphenated forms, so we should follow it | **REFUTED on two counts.** APA is not the governing style here (ABNT / abntex2 / numeric), and APA's actual rule is the compound-modifier rule, not a preference against hyphens |

**Two findings the item did not ask for, and they are the reason this report matters more than a
sweep.** First, the sweep that produced `multi-task = 0` **altered three verbatim quotations**,
including the title of the author's own published CBIC paper as printed in the record of publication
(§5). Second, the acronym list itself disagrees with the dominant prose form for POI (§6).

**Measured against:** the WORKING TREE at `HEAD = c13fe4d2`, with `src/dissertacao.pdf` the only
modified file (`git status --porcelain` printed one line: ` M articles/dissertacao/src/dissertacao.pdf`).
Note that this is **not** the baseline named in the task brief (`82080ce4` with
`2_fundamentals.tex` + `GLOSSARY.md` + `PENDENCIAS.md` uncommitted): the concurrent lane committed
those files while this audit ran, so `HEAD` moved forward and their content is now committed. Every
count below is a **source** measurement, not a PDF measurement, so the stale-PDF question does not
arise for the numbers; `src/build/main.pdf` (mtime 2026-08-03 21:21:31) is in fact NEWER than
`src/chapters/2_fundamentals.tex` (21:03:40) as of this audit, but nothing here was read from it.

---

## 1 · The measurement: per-variant live-prose counts

### 1.1 The command

The instrument is `.temp/term_audit/count_prose.py`, run from `articles/dissertacao/`:

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao
python3 ../../.temp/term_audit/count_prose.py --selftest        # -> "SELFTEST: 10 assertions, 0 failures"
python3 ../../.temp/term_audit/count_prose.py src /tmp/prose.json
```

It is two stages, and **stage 2 is the reason a plain `grep` over-reports**:

1. **Comment stripping**, copied from the repo's own gate `src_utils/check_register.py`:
   `COMMENT = re.compile(r"(?<!\\)%")`, the comment tail of every line cut, blank remainders
   dropped (GUARDRAILS §4b V4).
2. **Non-prose argument masking**, which the repo gates do NOT do and which this measurement needs:
   the braced argument of `\label \ref \cref \autoref \pageref \eqref \cite* \input \include
   \includegraphics \bibliography \usepackage \documentclass \index \url \href \graphicspath
   \newcommand \hypersetup`… is blanked, plus the second argument of `\pdfbookmark`.
   Without it `\input{chapters/3_cbic/basis}` counts as an occurrence of "cbic" and
   `\label{sec:next-poi}` as an occurrence of "next-POI". The unmasked first run reported
   `CBIC other-case = 86`; masked, it is **2**. That 84-hit difference is entirely `\label`/`\input`
   machinery.

Two count columns are reported because a compound can wrap across a source line and be invisible to
a per-line regex: **LIVE** counts within each surviving line, **JOIN** counts over the
whitespace-normalized join of all surviving lines of a file. `JOIN > LIVE` means an occurrence is
line-wrapped. **CMNT** counts the same pattern inside the discarded comment tails, so an absence in
prose can be distinguished from an absence in the file.

**Instrument validation, both directions** (V3, V13, V15b):

- **Self-test, 10 assertions, 0 failures.** Each masker is asserted to remove its target AND to
  leave adjacent prose intact (a masker that eats prose is worse than none). The comment stripper is
  asserted to keep a live line, to cut a comment tail, to respect the escaped `\%`, and the comment
  collector to find both dead occurrences. This caught one real defect during construction: `\href`
  was in the wrong argument list, so the anchor TEXT was being masked and the URL kept, i.e. exactly
  backwards. Fixed and re-tested.
- **Sabotage, on a LIVE line.** A copy of `src/` was made at `.temp/term_audit/sab`, and the string
  `SABOTAGE multi-task and point-of-interest and Multi-Task Learning and checkin.` was appended to
  `chapters/2_fundamentals.tex` **line 14**, a line asserted to survive comment stripping (V15b: a
  sabotage placed beside a commented anchor is stripped and measures nothing). Re-running the
  instrument on the sabotaged tree moved every one of the reported zeros:
  `multi-task 0 -> 2`, `Multi-Task Learning 0 -> 1`, `checkin 1 -> 2`, `point-of-interest 13 -> 14`.
  **The zeros below are absences, not blind spots.**
- One instrument failure was caught and corrected mid-audit and is reported rather than hidden
  (V17): the bibliography tally in §4 first returned `next-POI = 0`, which is false. The bib prints
  `Next-{POI}` with a protective brace, so the pattern could not express the target. Re-measured
  with braces stripped and with an assertion that the pattern finds the known-present case; the
  corrected count is 1.

### 1.2 The counts

Scope: **57 `.tex` files** under `src/`, excluding `src/build/`. Comments stripped; non-prose
command arguments masked.

| Group | Variant | LIVE | JOIN | in comments | files |
|---|---|--:|--:|--:|--:|
| `multitask` | **multitask** | 79 | 79 | 1 | 29 |
| `multitask` | **multi-task** | 0 | 0 | 22 | 0 |
| `multitask` | **multi task (spaced)** | 0 | 0 | 0 | 0 |
| `poi` | **point of interest** | 9 | 9 | 0 | 7 |
| `poi` | **point-of-interest** | 13 | 13 | 6 | 11 |
| `checkin` | **check-in** | 153 | 153 | 41 | 34 |
| `checkin` | **checkin** | 1 | 1 | 1 | 1 |
| `checkin` | **check in (spaced)** | 0 | 0 | 0 | 0 |
| `singletask` | **single-task** | 52 | 52 | 15 | 22 |
| `singletask` | **singletask** | 0 | 0 | 0 | 0 |
| `singletask` | **single task (spaced)** | 0 | 0 | 1 | 0 |
| `crossattn` | **cross-attention** | 17 | 17 | 11 | 10 |
| `crossattn` | **cross attention (spaced)** | 0 | 0 | 0 | 0 |
| `crossattn` | **crossattention** | 0 | 0 | 0 | 0 |
| `nextcat` | **next-category** | 46 | 46 | 12 | 15 |
| `nextcat` | **next category (open)** | 32 | 35 | 15 | 13 |
| `nextreg` | **next-region** | 33 | 33 | 6 | 12 |
| `nextreg` | **next region (open)** | 21 | 24 | 4 | 10 |
| `nextplace` | **next-place** | 10 | 10 | 2 | 5 |
| `nextplace` | **next place (open)** | 10 | 11 | 11 | 8 |
| `nextpoi` | **next-POI** | 42 | 42 | 6 | 15 |
| `nextpoi` | **next POI (open)** | 15 | 16 | 1 | 8 |
| `CBIC` | **CBIC** | 10 | 10 | 40 | 7 |
| `CBIC` | **other case** | 2 | 2 | 22 | 2 |
| `Check2HGI` | **Check2HGI** | 19 | 19 | 13 | 9 |
| `Check2HGI` | **other case** | 0 | 0 | 8 | 0 |
| `CoUrb` | **CoUrb** | 12 | 12 | 35 | 7 |
| `CoUrb` | **other case** | 8 | 8 | 17 | 4 |
| `DGI` | **DGI** | 33 | 33 | 9 | 11 |
| `DGI` | **other case** | 1 | 1 | 4 | 1 |
| `FiLM` | **FiLM** | 16 | 16 | 8 | 7 |
| `FiLM` | **other case** | 1 | 1 | 0 | 1 |
| `HGI` | **HGI** | 29 | 29 | 19 | 11 |
| `HGI` | **other case** | 0 | 0 | 16 | 0 |
| `LBSN` | **LBSN** | 7 | 7 | 2 | 5 |
| `LBSN` | **other case** | 0 | 0 | 0 | 0 |
| `MobiWac` | **MobiWac** | 7 | 7 | 22 | 5 |
| `MobiWac` | **other case** | 2 | 2 | 75 | 1 |
| `MTL` | **MTL** | 87 | 87 | 37 | 17 |
| `MTL` | **other case** | 0 | 0 | 37 | 0 |
| `POI` | **POI** | 256 | 256 | 50 | 34 |
| `POI` | **Poi/poi** | 1 | 1 | 0 | 1 |
| `SBRC` | **SBRC** | 3 | 3 | 2 | 3 |
| `SBRC` | **other case** | 0 | 0 | 0 | 0 |
| `TOST` | **TOST** | 16 | 16 | 26 | 9 |
| `TOST` | **other case** | 0 | 0 | 0 | 0 |
| `exp` | **Point of Interest (TC)** | 2 | 2 | 0 | 2 |
| `exp` | **Point-of-Interest (TC)** | 6 | 6 | 5 | 5 |
| `exp` | **Multitask Learning (TC)** | 16 | 16 | 0 | 10 |
| `exp` | **Multi-Task Learning (TC)** | 0 | 0 | 6 | 0 |
| `exp` | **multitask learning (lc)** | 20 | 21 | 0 | 11 |
| `exp` | **multi-task learning (lc)** | 0 | 0 | 2 | 0 |
| `exp` | **Location-Based Social Network** | 9 | 11 | 1 | 8 |
| `exp` | **Location Based Social Network** | 0 | 0 | 0 | 0 |
| `exp` | **Deep Graph Infomax** | 12 | 13 | 1 | 10 |
| `exp` | **Hierarchical Graph Infomax** | 10 | 10 | 2 | 6 |
| `exp` | **Feature-wise Linear Modulation** | 5 | 6 | 2 | 3 |
| `exp` | **Feature wise Linear Modulation** | 0 | 0 | 0 | 0 |
| `exp` | **Two One-Sided Tests** | 4 | 4 | 0 | 4 |
| `exp` | **Two One Sided Tests** | 0 | 0 | 0 | 0 |

### 1.3 Reading the table, per group

- **`multitask` / `multi-task`.** 79 live vs **0** live. The split the author describes does not
  exist in printable prose today. See §1.4 for the reconciliation with his own numbers.
- **`point of interest` / `point-of-interest`.** 9 vs 13. **This is the live inconsistency**, and it
  is the same one already dispositioned as FAB-20 / FAB-25 (§7).
- **`check-in` / `checkin`.** 153 vs 1. The single non-canonical hit is
  `tables/cbic/errata.tex:67`, `$N_{\text{checkins}}$`, a **math-mode subscript reproducing a
  published unfilled placeholder**. It is not prose and must not be touched: the errata table's
  whole function is to show what the published paper printed.
- **`single-task` 52 / `cross-attention` 17.** Zero variants of either. Nothing to do.
- **`next-category` 46 vs `next category` 32; `next-region` 33 vs `next region` 21;
  `next-place` 10 vs `next place` 10.** These are **not** an inconsistency. WRITING_LAW §2 requires
  exactly this split: hyphenated attributive, open nominal. Verified mechanically: a probe for the
  open form immediately followed by a head noun (`prediction|task|model|label|head|accuracy|classifier`),
  which is the shape that would need a hyphen, returns **0** across all 57 files. The probe was
  validated in both directions on synthetic strings before the zero was believed (it fires twice on
  a constructed positive, zero times on a constructed negative). The word following the open form is
  `and` in 19 of the 32 `next category` cases, i.e. coordination, not modification.
- **`next-POI` 42 vs `next POI` 15.** Confined to Chapters 3 and 4 and their tables, plus the two
  Chapter 3/4 bridging sentences. This is **reproduced published prose** and the two published
  papers themselves print both forms (§5.3). Out of scope for a house-style sweep; any change here
  is an errata decision.
- **The twelve acronyms.** Eleven are clean. The residues are all machinery or math, itemized here
  per V13 rather than summarized: `CBIC other-case 2` = `\texttt{src\_utils/cbic\_recompute\_result.md}`
  (a file path) and `\dissertationlabel{ch:cbic}{3}` (a label); `CoUrb other-case 8` = the DOI string
  `10.5753/courb.2026.22960` (×2) and six `\dissertationlabel{...courb...}` entries in
  `main_extra.tex`; `MobiWac other-case 2` = two `\dissertationlabel` entries; `DGI other-case 1` =
  `\texttt{research/embeddings/dgi/preprocess.py}`, a code path; `FiLM other-case 1` =
  `\texttt{film}` inside a parameter-set equation, `chapters/3_cbic/method.tex:272`;
  `POI Poi/poi 1` = `$N_{\text{poi}}$`, the same published placeholder as above.
  `Check2HGI`, `HGI`, `MTL`, `LBSN`, `SBRC`, `TOST` have **zero** live case variants.
  **Nothing in this group needs an edit.**
- **The expansions.** `Point of Interest` 2 vs `Point-of-Interest` 6 (§6);
  `Multitask Learning` 16 vs `Multi-Task Learning` 0; `multitask learning` 20 vs
  `multi-task learning` 0; LBSN, DGI, HGI, FiLM, TOST expansions each have one form only.

### 1.4 Reconciliation with the author's own measurement — I agree, with one correction

He measured **multitask = 78 / multi-task = 0** live, and **19 multi-task hits all inside comments
or the commented title alternates at `preamble.tex:201-206`**.

**I agree on the substance and both directions of it.** My independent numbers are **79 / 0** live
and **22** in comments. The three differences are all scope, and each is explainable:

- **79 vs 78 (live).** The extra one is almost certainly `preamble.tex:210`, the `\titulo{}` macro,
  which is a live line in a file a chapter-scoped sweep would exclude. Restricting my count to
  `chapters/` gives **70**; excluding `preamble.tex` gives **78**, exactly his figure. His number is
  correct for the scope he measured; mine adds the preamble, `main_extra.tex`, `content.tex` and
  `tables/`.
- **22 vs 19 (comments).** Mine counts OCCURRENCES; `chapters/2_fundamentals.tex:1274` carries two
  on one line, so my distinct-line count is 21. Excluding `preamble.tex` and `main_extra.tex` gives
  **17**. The two counts are consistent under different scopes; neither is wrong.
- **"all inside comments or the commented title alternates."** Correct as to location, and I would
  sharpen the description: only 2 of the 22 are the `preamble.tex:201-206` title alternates. The
  rest are provenance comments quoting OTHER papers' titles verbatim (`standley2020tasks`,
  `nash`, `sener2018mgda`) plus section markers. **They must not be swept** — GUARDRAILS §1 R2
  requires those strings to match their sources exactly.

**A cross-check that the instrument is not inventing the zero.** Plain `grep -rIo -i` over the same
files, comments and all, returns 22 `multi-task` occurrences and 94 `multitask`. Comment-stripped
and masked: 0 and 79. The 22 that disappear are precisely the comment hits, which is what the CMNT
column independently reports.

---

## 2 · Claim 2c — Caruana, source of record

**CONFIRMED. The title of record carries no hyphen.**

| Field | Value as printed at the source |
|---|---|
| DOI | `10.1023/A:1007379606734` |
| **Title, exact string** | **`Multitask Learning`** |
| Author | Rich Caruana |
| Journal | Machine Learning |
| Volume / issue / pages | 28 / 1 / 41–75 |
| Year | 1997 (July) |
| Publisher | Springer Science and Business Media LLC |

**Where I opened it, this session, two independent sources of record:**

1. **Crossref**, `https://api.crossref.org/works/10.1023%2FA%3A1007379606734`. Returned
   `"title": ["Multitask Learning"]`, container `Machine Learning`, volume 28, issue 1, page
   `41-75`, author `Rich Caruana`.
2. **The publisher PDF**, resolved via Unpaywall to
   `https://link.springer.com/content/pdf/10.1023/A:1007379606734.pdf` and read at
   `articles/10.1023_A_1007379606734.pdf`, 35 pages. **Page 1 as printed**: the article title reads
   `Multitask Learning`, over `RICH CARUANA`, with the running header
   `Machine Learning, 28, 41–75 (1997)` and the copyright line
   `c 1997 Kluwer Academic Publishers, Boston. Manufactured in The Netherlands.` Page 1 also carries
   the abstract, which opens with the definition of the approach as an inductive-transfer method
   that trains tasks in parallel on a shared representation.

**Does `src/references.bib` agree? Yes, exactly.** `references.bib:86-95`:

```bibtex
@article{caruana1997multitask,
  author    = {Rich Caruana},
  title     = {Multitask Learning},
  journal   = {Mach. Learn.},
  volume    = {28},
  number    = {1},
  pages     = {41--75},
  year      = {1997},
  doi       = {10.1023/A:1007379606734},
}
```

Title, author, volume, number, pages, year and DOI all match the source of record. `Mach. Learn.`
is the abbreviated journal name; the abbreviation is a bibliography-style choice, not a discrepancy.
**No edit is owed here.** The premise is correct and the repo was already right.

**What this claim does NOT license.** Caruana's title being unhyphenated is a fact about one 1997
paper's title. It is not a rule about how the field writes the phrase, and §4 measures that the
field overwhelmingly writes it the other way.

---

## 3 · Claim 2d — APA, and whether APA governs here

### 3.1 APA is not the governing style for this document. This matters more than the rule.

Measured from the source:

- `src/preamble.tex:40` loads **`\documentclass{abntex2}`**.
- `src/preamble.tex:120` loads **`\usepackage[num,abnt-emphasize=bf]{abntex2cite}`**: the
  **numeric** ABNT citation style, not author-date.
- `src/preamble.tex:44` loads `abntex2-UFV.sty`; `src/abntex2-num.bst` is the ABNT numeric
  bibliography style, header `abntex2-num.bst, v<VERSION> laurocesar … abnTeX2 group`.
- `src/content.tex:333` and `src/main_extra.tex:338` call `\bibliography{references}`.
- The deposit norms, recorded in `reviewers/research/norms_verification_2026-07-18.md` (each URL there
  verified in that session, not this one): UFV/PPGCC requires conformance to **ABNT NBR 14724:2011**
  and **NBR 6023:2018**, plus the PPGCC pre-textual checklist and the UFV Word models.
- `WRITING_LAW.md:35` already contains a ruling that turns on exactly this precedence: terminal
  punctuation goes **outside** the closing quotation mark per **ABNT NBR 10520:2023**, explicitly
  against American practice, on the ground that "the deposit norm wins over the house language
  convention".
- Search over the whole `articles/dissertacao/` tree for `\bAPA\b` in `*.tex`, `*.md`, `*.sty`
  returns **two hits, both inside PENDENCIAS.md — the author's own sentence and its snapshot copy**.
  APA appears nowhere in the source, the class files, the norms record, or the writing law.

**So the answer to "is APA even the governing authority here" is no**, and the document already has
a decided precedent for resolving this class of conflict in ABNT's favor. An APA argument cannot
carry a change to this document's prose.

### 3.2 What APA 7 actually says — and it is close to the opposite of the premise

**[VERIFY — partial]** `apastyle.apa.org` is served behind an Incapsula bot challenge for every path
I requested (`/style-grammar-guidelines/spelling-hyphenation/hyphenation`,
`/style-grammar-guidelines/grammar/hyphenation`, and `/`), each returning HTTP 200 with a ~920-byte
challenge stub containing no guidance text. Network access to the domain WAS granted this session;
the block is the publisher's bot filter, not the sandbox. **I could not open the APA page itself**,
so the wording below comes from indexed content of the APA page rather than from the page as I
rendered it, and it is flagged accordingly.

From the indexed APA Style page *Hyphenation principles*
(`https://apastyle.apa.org/style-grammar-guidelines/spelling-hyphenation/hyphenation`), which states
that its guidance corresponds to <cite index="1-3">Publication Manual Section 6.12 and Concise Guide Section 5.2, unchanged from the 6th edition</cite>:

- <cite index="1-4,1-5,1-6">A compound not in the dictionary is a "temporary compound", and the governing principle is to hyphenate temporary compounds to prevent misreading; a compound adjective before a noun takes a hyphen</cite>.
- <cite index="1-7">After the noun, the hyphen is usually unnecessary</cite>.
- <cite index="1-9">Words with prefixes and suffixes are usually written without a hyphen in APA Style</cite>.
- <cite index="1-10,1-11">Compound words may be two separate words, one hyphenated word, or one solid word, and the dictionary decides</cite>.

**The premise is half-right and misapplied.** APA does prefer unhyphenated forms **for
prefixed/suffixed words** (`postgraduate`, `nonlinear`). That is a rule about prefixes, and `multi-`
is arguably one. But APA's headline rule for a compound is the **compound-modifier rule**: hyphenate
before the noun, open after it. There is no APA rule saying "prefer the unhyphenated form of a
compound"; APA sends you to Merriam-Webster for the compound itself. So the sentence "APA Style
define a preferencia por uso de palavras sem hifén" is not a fair statement of APA 7, and in any
case APA does not govern this deposit.

### 3.3 IEEE — read at the first-party source, and it agrees with the compound-modifier rule

**IEEE Editorial Style Manual for Authors**, downloaded and read this session from
`https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE-Editorial-Style-Manual-for-Authors.pdf`
(HTTP 200, 809,723 bytes, 67 pages of extracted text). Relevant to this item, quoting only short
strings:

- **Page 21, "Hyphenation Rules"**: IEEE style follows its own Appendix list of preferred spellings,
  the Grammar and Usage section, and "the first version of the spelling given in the most recent
  edition of The Merriam-Webster Dictionary." Then: "Do not hyphenate most compound modifiers if
  they occur after the noun being modified, even if hyphenating them before the noun." Its own
  example pair is `His boat was 42 feet long.` / `He has a 42-foot-long boat.`
- **Page 22, first line**: "The most important hyphenation guideline is to be certain that the
  hyphenation for a particular word or group of adjectives is consistent within a particular
  article."
- **Page 27, rule 11**: "A pair of words, modifying a third word separately, does not get a hyphen…
  If the first word modifies the second, and the pair together modify the third, there is a hyphen
  between the pair."
- **Page 27, rule 14**: "Do not hyphenate predicate adjectives."

**IEEE's position is therefore the same compound-modifier rule that FAB-20 already adopted**, plus
an explicit consistency requirement. It does not support flattening; it supports a rule applied
consistently. This is the relevant style for Chapters 3 and 5 (CBIC uses IEEEtran; MobiWac is an ACM
venue but the manuscript in `articles/[mobiwac]/src/` uses `\IEEEauthorblockN`).

### 3.4 ACM and ABNT

- **ACM:** **[VERIFY]** `www.acm.org` is outside the sandbox allowlist and I did not request it, on
  the ground that the IEEE finding plus the ABNT precedence finding already decide the item; opening
  a third style guide would not change the disposition. **No ACM claim is made in this report.**
- **ABNT:** nothing in the norms record (`reviewers/research/norms_verification_2026-07-18.md`) addresses
  English-language compound hyphenation, and it would be surprising if it did: NBR 14724 and NBR
  6023 govern structure and references, not English orthography. **[VERIFY]** I did not open the
  NBR texts themselves this session (they are paywalled ABNT standards); the statement here is
  scoped to what the repo's own verified norms record contains, which is the same basis
  `WRITING_LAW.md:35` uses.

---

## 4 · The field's own usage — measured, not opined

### 4.1 The seven balancer papers named in the task

Each title below was read at a record opened **this session**. The arXiv titles come from the arXiv
API (`export.arxiv.org/api/query`), one request per identifier; DOI titles from Crossref; the
Nash-MTL title from the PMLR landing page's `citation_title` metadata.

| bib key | Identifier opened this session | **Exact title string at the source** | spelling |
|---|---|---|---|
| `caruana1997multitask` | DOI `10.1023/A:1007379606734` (Crossref + Springer PDF p.1) | `Multitask Learning` | **multitask** |
| `chen2018gradnorm` | arXiv:1711.02257v4 (journal_ref: *Proceedings of the 35th ICML (2018), 793-802*) | `GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks` | **multitask** |
| `kendall2018uncertainty` | arXiv:1705.07115v3; also DOI `10.1109/CVPR.2018.00781` (Crossref) | arXiv: `Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics`; Crossref prints `Multi-task Learning Using Uncertainty…` (lowercase `t`) | **multi-task** |
| `sener2018mgda` | arXiv:1810.04650v2 | `Multi-Task Learning as Multi-Objective Optimization` | **multi-task** |
| `standley2020tasks` | arXiv:1905.07553v4 | `Which Tasks Should Be Learned Together in Multi-task Learning?` | **multi-task** |
| `yu2020pcgrad` | **[VERIFY]** arXiv:2001.06782 — four consecutive HTTP 429 responses from the arXiv API; not opened | — | not measured |
| `liu2021cagrad` | arXiv:2110.14048v2 | `Conflict-Averse Gradient Descent for Multi-task Learning` | **multi-task** |
| `nash` (Navon et al.) | `https://proceedings.mlr.press/v162/navon22a.html`, HTTP 200, 15,416 bytes | `Multi-Task Learning as a Bargaining Game` (ICML, PMLR v162, pp. 16428–16446, seven authors) | **multi-task** |

**Tally of the seven named keys: 2 unhyphenated (`caruana1997multitask`, `chen2018gradnorm`),
5 hyphenated (`kendall2018uncertainty`, `sener2018mgda`, `standley2020tasks`, `liu2021cagrad`,
`nash`), 1 unmeasured (`yu2020pcgrad`).** Note the internal disagreement in the hyphenated group
itself: `Multi-Task` (capital T) at Kendall/arXiv, Sener, Navon; `Multi-task` (lowercase t) at
Standley, Liu, and Kendall/Crossref. The literature does not even agree with itself on the
capitalization, let alone the hyphen.

### 4.2 The whole bibliography, as a wider measurement

Same question over every `title` field in `src/references.bib` (comment lines stripped first, since
provenance comments quote titles; **100 entries parsed, 99 titles**; assertion on the parse count so
a zero could not pass as clean):

| Spelling | Occurrences | Entries |
|---|--:|--:|
| `multi-task` (any case) | 28 | 28 |
| `multitask` | 3 | 3 |
| `point-of-interest` | 3 | 3 |
| `point of interest` | 0 | 0 |
| `next-POI` | 1 | 1 |
| `next POI` | 8 | 8 |
| `check-in` | 4 | 4 |
| `checkin` | 0 | 0 |

The three unhyphenated entries are `caruana1997multitask`, `chen2018gradnorm` (`Deep Multitask
Networks`) and `liu2023famo` (`Fast Adaptive Multitask Optimization`). **The cited literature prints
`multi-task` roughly nine times as often as `multitask`.** Caruana is the minority form, not the
field's form.

### 4.3 What this measurement means for the item

The author's inference runs: the original says `Multitask`, therefore we should write `multitask`.
The premise is true and the document already does it (79 vs 0). But the warrant is weak — one 1997
title does not set the field's usage, and the field measurably prefers the other form. **The good
reason for `multitask` in this document is not Caruana and not APA; it is that the choice has
already been made and applied consistently, and consistency is what both IEEE and the author are
actually asking for.** I recommend recording it that way rather than on the Caruana/APA grounds,
because a banca member who checks the bibliography will find 28 hyphenated titles against 3.

---

## 5 · The finding the item did not ask for: three verbatim quotations were de-hyphenated

The sweep that produced `multi-task = 0` did not stop at the document's own prose. It changed the
text **inside `` `` … '' `` quotation marks**, in three places, and in each case the quoted string no
longer matches its source of record. This violates GUARDRAILS §1 R2 (attributes copied from the
source, not retyped) and WRITING_LAW §1's own carve-out, which states that a verbatim quotation of
published wording keeps its source's spelling because correcting inside a quotation would falsify
it.

Each item below is reported with its own evidence beside it (V13), and each source string was
located in the source file this session, not recalled.

**5.1 — `src/chapters/3_cbic.tex:17`, the author's own published paper title.**

- Printed in the dissertation: `` ``An Investigation into Multitask Learning for Point-of-Interest Category Classification and Next-POI Prediction'' ``
- **Title of record, Crossref DOI `10.21528/CBIC2025-1191324`, opened this session:**
  `An Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction`
  (container: *Anais do XVII Congresso Brasileiro de Inteligência Computacional*, pp. 1-8, publisher
  SBIA, six authors beginning Vitor Silva).
- **Also in the repo's own submitted source**, `articles/CBIC___MTL/main.tex:31`: `\title{An
  Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI
  Prediction}`.
- **And `src/references.bib` itself still carries the correct hyphenated form** for the same paper
  under key `silva2025mtlnet`. So the chapter preface and the bibliography entry of the same
  document now print two different titles for one paper.
- This is the highest-severity instance: it is a citation attribute, it is the author's own
  publication, and the two forms sit in the same PDF.

**5.2 — `src/chapters/5_mobiwac.tex:28-29`, the submitted MobiWac title.**

- Printed: `` ``Predicting the Next Category and Region of a Visit: A Check-in-Level Multitask Study on Mobility Data,'' ``
- **Source of record**, the submitted manuscript at `articles/[mobiwac]/src/main.tex:51-52`:
  `\title{Predicting the Next Category and Region of a Visit:\\ A Check-in-Level Multi-Task Study on
  Mobility Data}`.
- The paper is under review under the hyphenated title. A reviewer or committee member matching the
  chapter against EDAS #1571313639 finds a different string.

**5.3 — `src/tables/cbic/errata_wording.tex:24`, and this one is self-defeating.**

- Printed, in the "Published wording" column of the errata table:
  `` ``Furthermore, investigating advanced multitask optimizers...'' ``
- **Published wording, located at `articles/CBIC___MTL/sections/conclusion.tex:17`:**
  `Furthermore, investigating \textbf{advanced multi-task optimizers and loss-balancing schemes}
  beyond gradient conflict mitigation could address the task difficulty imbalance.`
- Positive control run before reporting the absence (V17): the hyphenated string IS present in the
  published source (`True`), the unhyphenated string is NOT (`False`).
- **The column whose entire purpose is to show what the published paper printed no longer shows what
  the published paper printed.** The row's own subject is a wording substitution; a second,
  unrecorded substitution has been applied to the evidence.
- For contrast, the adjacent row at `errata_wording.tex:56` quotes
  `` ``Next-POI Prediction, in contrast, aims to predict which specific location a user is likely to
  visit next'' ``, which I matched exactly against `CBIC___MTL/sections/basis.tex:23`. The table is
  not broadly corrupt; this is one row.

**5.4 — the normalization is not recorded in Appendix B, and the precedent says it should be.**

`chapters/apx_b_errata.tex` carries a dedicated paragraph for a *purely typographical* departure of
exactly this class: the published CoUrb paper typesets `MTLNet` and the chapter normalizes to
`MTLnet` at 28 places, and the appendix says so, with the count broken down and the reasoning
("a reader comparing the two should find the departure listed rather than have to guess whether it
was deliberate"). Measured: `grep -c "MTLNet" apx_b_errata.tex` = 3, `grep -ci "multi-task"
apx_b_errata.tex` = **0**. The Multi-Task → Multitask normalization across two reproduced chapters
is a larger departure than the MTLnet one and has no corresponding record.

**5.5 — for completeness, the two published papers are themselves inconsistent.** In
`CBIC___MTL/`: `multi-task` 20, `multitask` 4; `Points-of-Interest` 5, `Points of Interest` 2. In
`[mobiwac]/src/`: `multi-task` 12, `multitask` 4. So the inconsistency the author is reacting to was
partly inherited, which is relevant to how it should be dispositioned: normalizing the *reproduced
prose* is a legitimate house-style choice under the errata regime, but the *quotations* and the
*titles* are attributes, and they are not the house's to normalize.

---

## 6 · Does the List of Abbreviations agree with the prose? One of two does not

The list is at `src/content.tex:266-281`. Comparing each entry against the dominant live-prose form:

| Entry, as printed at `content.tex` | Line | Dominant prose form | Agree? |
|---|--:|---|---|
| `\item[MTL] Multitask Learning` | 277 | `Multitask Learning` 16, `Multi-Task Learning` 0 | **yes** |
| `\item[POI] Point of Interest` | 278 | `Point-of-Interest` 6 vs `Point of Interest` 2 (title-case); overall 13 hyphenated vs 9 open | **no** |
| `\item[Check2HGI] Check-in-level representation extending Hierarchical Graph Infomax` | 269 | Check2HGI 19, zero variants | yes |
| `\item[DGI] Deep Graph Infomax` | 271 | 12 live, one form | yes |
| `\item[FiLM] Feature-wise Linear Modulation` | 272 | 5 live, one form | yes |
| `\item[HGI] Hierarchical Graph Infomax` | 273 | 10 live, one form | yes |
| `\item[LBSN] Location-Based Social Network` | 274 | 9 live, one form | yes |
| `\item[TOST] Two One-Sided Tests` | 280 | 4 live, one form | yes |
| CBIC / CoUrb / MobiWac / SBRC | 267,270,275,279 | venue names, zero live variants | yes |

**So the author's specific complaint lands on exactly one entry, and he named it: POI.** The
acronym list expands POI as `Point of Interest` (open), while the prose's title-case usage is
`Point-of-Interest` 6 to 2, and the dissertation's own **running title** — printed on the cover, the
folha de rosto, the Resumo/Abstract headers, the `pdftitle`, and the supplementary volume — is
`Multitask Learning for **Point-of-Interest** Classification and Prediction Tasks` (`preamble.tex:210`,
`content.tex:48`, `content.tex:171`, `main_extra.tex:106`).

**The list entry is nevertheless the grammatically correct one, and should not be flattened to
match.** `Point of Interest` in a glossary is the **nominal** form, which is precisely the form the
compound-modifier rule leaves open. The title is the **attributive** form modifying `Classification`,
which the rule hyphenates. Both are right. What is missing is not consistency but a note; see §8.

---

## 7 · Overlap with FAB-20 and FAB-25 — the required statement

**AUT item 2 is WIDER than FAB-20/FAB-25, and it fully contains them.**

Both prior items are in `src_utils/CONSIDERATIONS.md` and both are dispositioned **YOU APPLY**:

- **FAB-20** (`CONSIDERATIONS.md:369-381`), Fabricio, written, against
  `chapters/1_introduction.tex:93-94`: "Padronizar a escrita de `point of interest` (POI) em todo o
  texto. É com ou sem hífen? Manter o mesmo sempre." Recorded take: "agree, with the standard rule.
  Measured live: 11 hyphenated vs 8 spaced. The principled rule is the English compound-modifier
  rule (attributive hyphenated, nominal open), which makes 15 of the 19 already correct. Flattening
  to one form would produce 'a user visits a point-of-interest', which is wrong." Scope: "whole
  tree; 8 files". Probe `R9-poihyphen` **RESERVED, NOT IMPLEMENTED**. Measured against build commit
  `d4078c75`.
- **FAB-25** (`CONSIDERATIONS.md:430-441`), against `chapters/2_fundamentals.tex:27-28`, the sentence
  "Each record is a \emph{check-in}: a user, a point of interest (POI), and a timestamp." Recorded
  take: "agree with a correction. The instance he flagged … is ALREADY CORRECT: it is the nominal
  use. The inconsistency is real but the fix is the rule, not flattening. Handled with FAB-20."

**Every place they overlap:**

1. **The POI hyphenation question itself.** AUT-2's worked example ("Point of Interest que em muitos
   locais aparece como Point-of-Interest") is FAB-20's question verbatim. Same problem, same tree,
   same fix.
2. **The proposed remedy.** AUT-2 says "vamos substituir onde necessario". FAB-20 already settled
   what "necessario" means: apply the compound-modifier rule, do not flatten.
3. **The unimplemented probe.** `R9-poihyphen` is reserved for FAB-20/FAB-25 and would be the same
   probe AUT-2 needs. Confirmed still unimplemented: `grep -n "R9-poihyphen\|poihyphen"
   src_utils/check_audit_claims.py` returns nothing.
4. **The count drift, which is itself a small finding.** FAB-20 measured 11 hyphenated vs 8 spaced
   (19 total) against `d4078c75`. My comment-stripped, machinery-masked count on the current tree is
   **13 hyphenated vs 9 open (22 total)**. Two of the extra hyphenated hits are
   `chapters/6_conclusion.tex:15` and `:119`, prose written since. The FAB-20 numbers are not wrong;
   they are stale, and anyone re-opening that row should re-measure rather than carry them forward
   (§4b V6).

**Where AUT-2 goes beyond FAB-20/FAB-25** — four things neither prior item covers:

- The **multitask/multi-task** question (settled in the live tree; the residue is the quotation
  damage in §5, which is new and is not a hyphenation question at all).
- The **List of Abbreviations ↔ prose** agreement check (§6).
- The **other ten acronyms** and the other compound forms — all measured clean in §1.
- The **APA / source-of-record justification** (§2, §3), which is an argument about *why*, not a new
  edit.

---

## 8 · Ungrammatical-flattening warning, as required

**Flattening every POI form to the hyphenated one produces ungrammatical English.** The nominal uses
are not errors and must survive. The concrete sites, each read this session:

| Site | Text | Why it must stay open |
|---|---|---|
| `chapters/1_introduction.tex:43` | "states that a user visited a place, or point of interest (POI), at a given time" | nominal, in apposition to "a place". `visited a place, or point-of-interest` is wrong |
| `content.tex:192` (Abstract) | "associating a user, a point of interest (POI), and a time" | nominal, list member |
| `chapters/2_fundamentals.tex:27` | "a user, a point of interest (POI), and a timestamp" | nominal — this is FAB-25's instance, already ruled correct |
| `chapters/3_cbic/method.tex:21` | "A point of interest is defined as a tuple $\langle id, lat, long, cat\rangle$" | nominal, subject of a definition |
| `chapters/5_mobiwac/01_introduction.tex:14` | "Predicting the next place exactly, a single point of interest (POI), is hard" | nominal, apposition |
| `content.tex:239` (keywords) | "multitask learning, point of interest, next-category prediction" | keyword list; the ABNT keyword convention takes the base nominal form |
| `content.tex:278` | `\item[POI] Point of Interest` | glossary expansion; nominal (§6) |
| `tables/courb/dataset.tex:9` | column header "Points of Interest" | plural nominal, a count column |

And symmetrically, the hyphenated attributive uses are correct and must not be opened:
`point-of-interest prediction` (`1_introduction.tex:100`, `6_conclusion.tex:15`, `:119`),
`Point-of-Interest Category Classification` (`3_cbic.tex:18`, `3_cbic/method.tex:12`),
`point-of-interest and check-in embedding engines` (`apx_extra_platform.tex:50`), the section
heading `\section{Point-of-interest prediction tasks}` (`2_fundamentals.tex:24`), and the running
title at `preamble.tex:210`.

By the compound-modifier rule, **all 22 live POI occurrences are already correct.** FAB-20's take
said "15 of the 19 already correct"; on the current tree, applying the rule site by site, I find
**22 of 22**. The two remaining candidates for change are judgment calls, not errors:
`Points-of-Interest (POIs)` at `chapters/3_cbic/intro.tex:12` and `chapters/3_cbic/results.tex:15`
are hyphenated plural nominals, which the rule would leave open — but both are **reproduced
published CBIC prose** (`CBIC___MTL/sections/intro.tex:34` and `sections/results.tex:15` print
`Points-of-Interest (POIs)`), so changing them is an errata decision under NORTH_STAR §5.7, not a
style sweep.

**Conclusion on the POI half: there is nothing to fix in the prose.** What is missing is a
GLOSSARY row stating the rule, so the next writer does not re-open the question, and a probe so the
rule is defended.

---

## 9 · What it would take, and the recommended disposition

**Disposition: I_DECIDE.** Not YOU_APPLY, and the reason is that the author's stated warrant is
wrong in a way that changes what should be done. He asked for a flattening justified by APA and by
Caruana. APA does not govern this document and does not say what he thinks; Caruana is a minority
form in the cited literature. Meanwhile the sweep already performed in the direction he wants has
damaged three quotations, including his own paper's title of record. This needs his ruling, not an
agent's application.

**Four decisions are owed, sized:**

1. **Repair the three quotations (§5.1, §5.2, §5.3). Small: 3 strings in 3 files.** My
   recommendation is to restore the hyphen inside all three, because they are attributes of record,
   not house prose, and both GUARDRAILS §1 R2 and WRITING_LAW §1's quotation carve-out require it.
   The CBIC one is the urgent one: the same PDF currently prints two different titles for one paper.
2. **Record the Multi-Task → Multitask normalization in Appendix B. Small: one paragraph.** The
   MTLNet → MTLnet paragraph is the template and the precedent. Owed regardless of decision 1, since
   the normalization of the *reproduced prose* stands either way.
3. **Register the POI hyphenation rule in GLOSSARY. Small: one row.** The rule is already
   dispositioned (FAB-20) and already followed (22 of 22). A registry row makes it fail-closed
   instead of tribal, and it is the author's alone to add.
4. **Implement the `R9-poihyphen` probe. Small-to-medium: one checker function.** Reserved by
   FAB-20/FAB-25 and still absent. Per §4b V15, an unprobed rule is undefended; the natural probe is
   the attributive-form check validated in §1.3 (open form + head noun must be 0), plus a
   multitask/multi-task live-prose assertion, plus an assertion that the three quoted strings match
   their sources.

**No prose edit is owed for hyphenation itself.** That is the substantive result: the live tree is
already consistent under the correct rule, on both compounds, and the acronym list's one apparent
mismatch is grammatically right.

---

## 10 · Source ledger

| # | Reference | Identifier | Where opened, this session | Claim it supports |
|---|---|---|---|---|
| 1 | Caruana, *Multitask Learning* | DOI `10.1023/A:1007379606734` | Crossref API `api.crossref.org/works/10.1023%2FA%3A1007379606734`; and the Springer PDF via Unpaywall, `link.springer.com/content/pdf/10.1023/A:1007379606734.pdf`, saved at `articles/10.1023_A_1007379606734.pdf`, **page 1 read** | §2: title of record is `Multitask Learning`, unhyphenated; *Machine Learning* 28(1):41-75, 1997; `references.bib:86-95` agrees |
| 2 | Silva et al., CBIC 2025 | DOI `10.21528/CBIC2025-1191324` | Crossref API | §5.1: title of record reads `Multi-Task Learning`; the chapter preface prints `Multitask` |
| 3 | Paiva et al., CoUrb 2026 | DOI `10.5753/courb.2026.22960` | Crossref API | §1.3: the `courb` string in live prose is a DOI, not a case variant; title/pages/authors confirmed |
| 4 | Navon et al., Nash-MTL | PMLR v162 | `proceedings.mlr.press/v162/navon22a.html`, HTTP 200, `citation_title` metadata | §4.1: `Multi-Task Learning as a Bargaining Game`, pp. 16428-16446 |
| 5 | Chen et al., GradNorm | arXiv:1711.02257v4 | arXiv API | §4.1: `…in Deep Multitask Networks` (unhyphenated) |
| 6 | Kendall et al. | arXiv:1705.07115v3; DOI `10.1109/CVPR.2018.00781` | arXiv API; Crossref API | §4.1: `Multi-Task Learning Using Uncertainty…` (arXiv), `Multi-task…` (Crossref) |
| 7 | Sener & Koltun, MGDA | arXiv:1810.04650v2 | arXiv API | §4.1: `Multi-Task Learning as Multi-Objective Optimization` |
| 8 | Standley et al. | arXiv:1905.07553v4 | arXiv API | §4.1: `…in Multi-task Learning?` |
| 9 | Liu et al., CAGrad | arXiv:2110.14048v2 | arXiv API | §4.1: `…for Multi-task Learning` |
| 10 | Yu et al., PCGrad | arXiv:2001.06782 | **NOT OPENED** — four consecutive HTTP 429 from the arXiv API | **[VERIFY]** no title claim made |
| 11 | IEEE Editorial Style Manual for Authors | `journals.ieeeauthorcenter.ieee.org/…/IEEE-Editorial-Style-Manual-for-Authors.pdf` | Downloaded HTTP 200, 809,723 bytes; pages 21, 22, 26, 27 read | §3.3: compound-modifier rule; "most important hyphenation guideline is… consistent within a particular article" |
| 12 | APA Style, *Hyphenation principles* | `apastyle.apa.org/style-grammar-guidelines/spelling-hyphenation/hyphenation` | **Bot-challenged, page NOT rendered.** Content from the indexed version of that page | **[VERIFY]** §3.2: compound-adjective rule before/after the noun; prefixes usually unhyphenated |
| 13 | UFV/PPGCC deposit norms | — | `reviewers/research/norms_verification_2026-07-18.md`, read in-repo (its URLs were verified in that session, not this one) | §3.1: NBR 14724:2011 + NBR 6023:2018 govern; no APA |
| 14 | This document's own build | — | `src/preamble.tex:40,44,120`; `src/abntex2-num.bst` header; `src/content.tex:333` | §3.1: abntex2 class, `abntex2cite[num]`, ABNT numeric `.bst` |
| 15 | CBIC submitted source | — | `articles/CBIC___MTL/main.tex:31`, `sections/conclusion.tex:17`, `sections/intro.tex:34`, `sections/results.tex:15`, `sections/basis.tex:23` | §5.1, §5.3, §5.5, §8 |
| 16 | MobiWac submitted source | — | `articles/[mobiwac]/src/main.tex:51-52` | §5.2 |
| 17 | Prior dispositions | — | `src_utils/CONSIDERATIONS.md:369-381` (FAB-20), `:430-441` (FAB-25) | §7 |
| 18 | Errata precedent | — | `src/chapters/apx_b_errata.tex:270-300` | §5.4 |
| 19 | The repo's own comment-stripping convention | — | `src_utils/check_register.py:82` (`COMMENT`), `:438-450` (`strip_comments`), `:463-474` | §1.1 |

## 11 · [VERIFY] flags

1. **APA page not rendered.** `apastyle.apa.org` returns an Incapsula bot-challenge stub (~920 bytes,
   HTTP 200) on every path tried, after network access to the domain was granted. §3.2 rests on the
   indexed content of the APA page, not on the page as I loaded it. **This does not affect the
   disposition**, because §3.1's finding (APA does not govern an ABNT deposit) is independent and
   was measured in-repo.
2. **`yu2020pcgrad` (PCGrad) title not verified.** Four consecutive HTTP 429 responses from the arXiv
   API. No title claim is made for it; the §4.1 tally reports 7 of 8 keys and names the gap.
3. **ACM style not consulted.** `www.acm.org` is outside the allowlist and I chose not to request it
   (S1 budget; the IEEE + ABNT findings already decide the item). No ACM claim appears in this report.
4. **ABNT NBR texts not opened.** NBR 14724 / 6023 / 10520 are paywalled ABNT standards. §3.1 and
   §3.4 rest on the repo's own verified norms record and on `WRITING_LAW.md:35`, and are scoped to
   that basis. The narrow claim "ABNT says nothing about English compound hyphenation" is an
   inference from the scope of those standards, not a reading of them.
5. **`src/build/main.pdf` was not measured.** All counts are source measurements. The PDF's mtime
   (2026-08-03 21:21:31) is newer than `2_fundamentals.tex` (21:03:40), so the staleness noted in
   the task brief no longer holds as stated, but nothing here depends on it either way.
6. **Baseline moved during the audit.** The brief named `HEAD = 82080ce4` with three files
   uncommitted; the tree measured is `HEAD = c13fe4d2` with only `src/dissertacao.pdf` modified. The
   concurrent lane committed those files while this ran. Counts should be re-taken if the lane lands
   further prose.
7. **FAB-20's recorded counts (11/8) are stale**, measured against `d4078c75`. Current: 13/9.
   Anyone reopening that row must re-measure (§4b V6).


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
