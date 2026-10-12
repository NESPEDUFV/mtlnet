# WRITING_LAW.md — the writing law for the dissertation (v1, 2026-07-18)

> **Scope.** Every sentence written in this dissertation — by the author or by an agent — obeys
> this file. It inherits the MobiWac [`GLOSSARY.md`](../%5Bmobiwac%5D/GLOSSARY.md) (the paper's
> writing law, battle-tested through two review cycles) and adapts it to a **dissertation**:
> different audience (a computing banca, not networking reviewers), different length (didactic
> register allowed), same honesty discipline. **Where the two files conflict, THIS file wins —
> everywhere, including the MobiWac chapter's re-typeset prose and the article's own camera-ready.**
>
> ⚠ **The exception that used to sit here is gone (author's decision, 2026-09-06).** Until then this
> line read "for the MobiWac chapter's re-typeset prose, the paper GLOSSARY wins", and it made sense
> while the article fed the chapter: the chapter reproduced a text written under the paper's law, so
> that law travelled with it. **The direction has reversed.** The submitted article carries the v17
> leaked numbers and is being rewritten from the dissertation's Chapter 5, so the chapter is now the
> source and the paper the destination — and a chapter written under this file, governed by the
> paper's glossary, would be governed by the weaker of the two in the one place it matters most.
>
> **The concrete consequence the author named when deciding:** the TOST result would license writing
> that the two models *match*, and this file's ban on that verb as a verdict surface **still holds**,
> in the camera-ready as well as here. His words: *"Vale a lei da dissertação, WRITING_LAW governa o
> camera-ready, apesar de já termos feito os testes estatísticos e podermos usar o matches."* Do not
> re-derive permission for `matches` / `empata` / `ties` from the statistics — the tests were run,
> the verb is still refused. The verdict ladder in `CLAUDE.md` §0.3 is the permitted wording.
>
> Process rules (how agents verify citations/numbers) are in
> [`AGENT_GUARDRAILS.md`](AGENT_GUARDRAILS.md) — this file is about the words on the page.

---

## 1 · Register: dissertation ≠ paper

- **Audience:** a CS/ML banca + future students. Unlike MobiWac's networking audience, standard
  ML vocabulary (embedding, transformer, cross-attention, macro-F1) is fine **once defined**.
  The MobiWac plain-word substitutions (§3 of the paper GLOSSARY) are therefore relaxed for the
  frame chapters — but every term still gets ONE definition at first use (Fundamentals is where
  most of them live) and is then used consistently.
- **Didactic room:** the dissertation may explain (worked examples, notation tables, "Relevance"
  subsections) where the paper had to compress. Viegas patterns to use: definition → citation →
  concrete example rhythm; sections open with a 1–3 sentence purpose statement; background always
  tied to its downstream use ("this assumption matters for Chapter 5's protocol because…").
- **Register bar (inherited, unchanged):** clear, simple academic English that a Brazilian
  non-native English writer would defend aloud. Prefer common, precise words and direct
  constructions. Do not replace an established technical term with an inaccurate plain word, but
  do explain the term at first use. Both failure poles are banned: AI-inflated vocabulary AND
  native-literary idiom (phrasal-verb metaphors, money/motion metaphors). The test: *would the
  author say it at the defense, would the community write it, and would a qualified reader
  understand it on the first reading?* Safe verbs: use, cost, show, obtain, reach, remain, include,
  provide, predict, measure, train, keep.
- **American English throughout, with ONE deliberate exception.** Use American spelling,
  vocabulary, and usage consistently.
- **Terminal punctuation goes OUTSIDE the closing quotation mark, per ABNT NBR 10520:2023.**
  Author's ruling of 2026-08-02, PENDENCIAS 2.24. American style puts the period inside; this
  document is deposited under ABNT, whose citation standard places the closing punctuation after
  the quotation mark, and the deposit norm wins over the house language convention. The document
  already follows ABNT against American practice elsewhere: table captions go above the table.
  Write `... shared information".` and never `... shared information."`
  This is not a style preference to be tidied by a later pass. The 14 sites that carry it are
  almost all errata tables, where the quoted string IS the evidence for a correction: moving a
  period inside such a quotation alters the quotation, which is a worse fault than a punctuation
  convention a reader may not share. Measured 2026-08-02: 6 in `tables/cbic/errata.tex`, 3 in
  `tables/courb/errata.tex`, 2 each in `tables/cbic/errata_wording.tex` and
  `chapters/3_cbic/method.tex`, 1 in `chapters/apx_b_errata.tex`.
- **Clarity takes priority over variation or elegance:** a reader must not need to
  re-read a sentence or paragraph to recover its intended meaning or logical connection. If a
  passage needs a second reading, revise it by reducing clause load, naming the referent, making
  the logical link explicit, or splitting it. No contractions; "cannot" is correct. Digits for
  data quantities ("8,501 regions"); words for small counts ("two tasks, seven categories").
  Comma after sentence-initial adverbial phrases. Write relative pronouns ("the head **that** we
  do not predict").

- **No British English, and the ban is wider than a spelling list.** The author read Appendix F on
  2026-07-30 and found *"feature needs saying plainly"* in the deposited prose (PENDENCIAS_RESOLVIDOS 2.22 (arquivado 2026-07-30)
  point 8). Read the instance carefully, because it is the reason this rule is shaped the way it is:
  **it is not a misspelling.** Every word is spelled identically in both dialects. It is the British
  `need`+gerund construction, where American English writes "needs to be said plainly". He also
  asked whether the governing documents banned it; they did not. Measured before this rule was
  written: `grep -cin "british"` over this file and `AGENT_GUARDRAILS.md` returned 0 and 0. The
  previous line said "American English throughout" and named no British form, so an agent had
  nothing to check against. Both halves are now named.

  **Spellings.** American in every case: `-ize`/`-ization` not `-ise`/`-isation`, `-yze` not `-yse`,
  `-or` not `-our` (behavior, color, neighbor, labor), `-er` not `-re` (center, meter, fiber),
  single `l` before a vowel suffix (traveled, modeled, labeled, signaled) and double `l` where
  American doubles it (skillful, fulfill, installment), `-se` for the noun (defense, offense,
  license, pretense) and `practice` for both noun and verb, `while` not `whilst`, `among` not
  `amongst`, `toward`/`forward`/`afterward` without the `-s`, `learned`/`spelled`/`burned` not
  `learnt`/`spelt`/`burnt`, `program` not `programme`, `catalog` not `catalogue`, `gray` not `grey`,
  `judgment`/`acknowledgment` without the medial `e`, `aging` not `ageing`, `percent` not `per
  cent`, `skeptic` not `sceptic`, `inquiry` not `enquiry`, `oriented` not `orientated`, `focused`
  not `focussed`, no `oe`/`ae` digraph. **Words that end in `-ise` in both dialects are not
  British** and must not be "corrected": surprise, comprise, exercise, advertise, supervise, revise,
  devise, improvise, compromise, franchise, arise, precise, premise, and their prefixed and
  inflected forms.

  **Constructions**, which no spelling list reaches: `need`/`want` + gerund ("needs saying",
  "wants doing"), `different to` or `different than` for `different from`, the bare institution
  noun ("in hospital", "at university", "in future" for "in the future"), `have got` for `have` or
  `must`, `shall` for the future or for obligation, `at the weekend`, `was sat`/`was stood` for the
  progressive, a collective noun with a plural verb ("the committee have"), and `providing that`
  for `provided that`.

  Two carve-outs, both narrow. A **verbatim quotation** of published wording keeps its source's
  spelling: correcting inside `` ``...'' `` would falsify the quotation. A British form in
  **reproduced published prose of one of the three papers** is an errata decision, not a spelling
  fix, and goes to the author with its cost under the errata regime (NORTH_STAR §5.7) rather than
  being changed quietly. Gate 25 (`src_utils/check_register.py`) enforces the mechanical half and
  holds the author-owned hits open by name.

- **No phrasing a non-native writer would not produce, and this is the harder rule.** The author's
  second complaint, from the same reading (PENDENCIAS_RESOLVIDOS 2.22 (arquivado 2026-07-30) points 9 and 12): prose that is correct,
  even well written, and still forces a non-native reader to read it twice. His two instances, both
  from Appendix F, and his own words on each:
  - *"Two departures from that flat picture appear"* — **"pure A.I, we can be more simple"**.
  - *"Both point away from trouble in any case. A positive cosine is mild cooperation, not conflict,
    and the decline stays inside the margin throughout while moving toward zero rather than away
    from it."* — **"well written, but is not natural for a non native writer in english, and force a
    non native read more than once to understand"**.

  "Avoid awkward phrasing" would be unenforceable, so the ban names **shapes**:
  - **Inverted or delayed subjects.** A named subject held away from its verb by a modifier chain,
    with an intransitive verb of appearance at the end of the clause ("Two departures from that flat
    picture *appear*"), and the cleft that does the same job ("What carries that diagnosis is…").
    Name the subject and let it act: "The figure shows two departures."
  - **An abstract noun as the subject where a person or a thing would do.** A number does not move,
    prefer, or point: "the decline stays inside the margin *while moving toward zero rather than
    away from it*" asks the reader to animate a statistic. Say what was measured: "the mean falls
    toward zero and stays inside the margin."
  - **Chained qualification inside one sentence.** Three or more qualifying connectives (while,
    whereas, though, rather than, instead of, throughout, nevertheless) in one sentence, each
    narrowing the last. Split it, or drop the qualifications the claim does not need. Honesty does
    not require them in a single breath; §3 requires them *present*, not *stacked*.
  - **Idiom that is native literary register rather than academic register.** "point away from
    trouble", "in any case", "at any rate", "by the same token", "not least", "if anything". This
    extends §4's idiom rule from phrasal-verb metaphors to literary connective idiom, which is the
    class that survived the earlier sweeps.

  **The test is his, and it has two halves.** Would a Brazilian non-native writer of academic
  English produce this sentence? And can a non-native reader take it in on **one** reading? A no to
  either sends the sentence back. Technical difficulty is not a defense: keep the technical term,
  define it once, and simplify everything around it.

  **What is gated and what is judged.** Gate 25 catches the four shapes above, and that is the
  mechanical half only. The judgment half is the readability editor's first-read method
  (`reviewers/15_readability_editor.md`, review method and lens 2), whose verdict is PASS only with
  zero passages that need a second reading; `AGENT_GUARDRAILS.md` §5 makes that verdict part of G3.
  This rule deliberately does not restate that method, and **a green gate is not a first-read PASS**.
- **No em-dash anywhere.** Use commas, parentheses, semicolons, or two sentences. (Also an AI
  tell; also the MobiWac rule.)
- **No process narration, and this is a hard ban.** The prose states what is true of the work, never
  how the work came to be done or what the writing went through. Four sub-classes, each with a real
  instance from this repository that a reader would have received:
  - **Infrastructure.** *"the machine that would have run them was out of disk"* (Appendix F, deleted
    2026-07-30 at the author's instruction). A lab machine's free space is not a fact about mobility
    data. Also banned: GPU model, queue state, wall-clock caps, checkpoint sizes, run directories.
  - **The document's own version history.** *"California, Texas, and Istanbul were absent from an
    earlier version of this appendix"* (same paragraph). The reader of the deposited document never
    saw an earlier version and cannot act on the fact that one existed. Errata belong in the errata
    appendix, where the regime is deliberate and the reader is told why.
  - **Scheduling and provenance of the agent's own effort.** *"were measured afterward"*, *"at the
    time of writing"*, *"we then ran"*. When a measurement was taken is a fact about the project, not
    about the result. If a date genuinely qualifies a claim (a dataset vintage, a snapshot of a live
    resource), the date goes in and the narrative does not.
  - **Self-reference to the writing.** *"this appendix originally reported"*, *"as noted above"*,
    *"the boundary the paragraph above draws"*. The last of these also violates §4's ban on restating
    a section, and it appeared in the same deleted paragraph.

  **Why the ban is absolute rather than a matter of taste.** Process narration reads as an excuse, it
  dates the document the moment the circumstance changes, and it is unverifiable by the reader: a
  banca member cannot check that a machine was full. It is also the single easiest AI tell to spot,
  because a human author simply omits it. **The test:** if the sentence would be false or pointless
  once the circumstance changes, or if it explains why something is missing rather than stating what
  is present, cut it and put the reason in a source comment or a round report.

  **Where the material goes instead.** A limitation the reader must know ("this appendix covers one
  architecture family") is a LIMITATION and stays, stated as a property of the evidence. The reason
  the limitation exists goes in the provenance comment. Nothing is lost by the cut; measured before
  deleting the paragraph above, its only fact (the dataset coverage) was already stated three other
  times including in the figure caption.

## 2 · Canonical names (repo-wide; unchanged from the paper GLOSSARY §1)

> This section is the core rules only — the FULL expanded registry (model lineage, protocol
> terms, metrics, acronyms, PT equivalents, per-paper task mapping) is
> [`GLOSSARY.md`](GLOSSARY.md), and its fail-closed maintenance rule governs new terms.

| Concept | Use | Never |
|---|---|---|
| The "what" task | **next category** / category prediction | activity, POI classification |
| The "where" task | **next region** / region prediction | area, "next-POI" for region |
| The exact-place task | **next place** (we do NOT predict it; say so once, early) | conflating it with the other two |
| A place | place / point of interest (POI) | venue |
| One visit | check-in | event |
| Our representation | **check-in-level representation (Check2HGI)** | "substrate" (repo word) |
| Place-level baseline | place embedding (HGI) | "the baseline" alone |
| One model, both tasks | the joint model / single multitask model | bare "MTLnet" before it is introduced |
| One task, one model | dedicated single-task model | "baseline" alone |
| Repetition unit | **seed** = one complete repetition of the five-fold experiment; it sets the random initialization **and** the fold partition (define once, then "seed") | "run", "multi-seed run", bare "seed" in the abstract (say "random initialization"); "over the same folds" / "one fixed partition" as a property across seeds — corrected 2026-08-04, see `science/fold_partition_and_seeds.md` |

- Hyphenate the compound adjective ("next-category prediction"), leave the bare task name open
  ("the next category").
- **No repo codenames in dissertation prose**: B9, v11–v17, champion-G, H3-alt, dk_ovl, log_T
  (write "region-transition prior"), C25/CH16/F-numbers, "engine", "board", "recipe" (write
  "training configuration"), "frozen" (write "fixed", except frozen weights, glossed).
- One name per concept for the whole document; synonym-cycling is both imprecise and an AI tell.
  If a paragraph repeats a term 4+ times, restructure the sentences, never rotate synonyms.
- Model names across chapters: **MTLnet** (CBIC/CoUrb architecture), **ST-MTLNet** (CoUrb input
  variant), **Check2HGI** (representation), and the MobiWac joint model described per its paper.
  The Fundamentals chapter carries a small lineage table so the names never blur.

## 3 · Honesty rules (non-negotiable; violations are bugs, not style)

- **Every number carries its reference point** (majority-class floor, Markov floor, dedicated
  ceiling) and its convention (which metric, which selection rule, n=how many). Never a naked
  percentage.
- **Verbs bound to tests** (applies wherever the final study's results appear). The ladder below is
  the single home for these bindings; every other file points here rather than restating them.
  - **"outperforms"** only where paired superiority survives Holm correction within its task
    family: **next region at Texas (+1.21) and California (+1.06)**; **next category at Florida
    (+0.19)**. Nowhere else, on either axis.
  - **"stays within the two-point margin"** is the recurring readable surface for the region axis,
    where the ±2 pp margin was registered before any result was read. The technical name
    ("statistically non-inferior", TOST) is glossed once at first use in each language and then used
    only where the test itself is being named. All six region datasets clear it.
  - **Derived equivalence bounds, one per axis — never quote one axis's bound on the other.** The
    bound is *derived, not chosen*: two one-sided tests at margin *d* pass exactly when the 90 % CI
    falls inside ±*d*, so it is read off the intervals. Because nothing is chosen there is no
    post-hoc margin to justify.
    - **Next category: "equivalent to zero within half a point."** Per-dataset 0.334 pp;
      simultaneous over the six datasets under Bonferroni, 0.489 pp. This is the axis the
      half-point phrase belongs to, and the only one.
    - **Next region: the registered two-point margin is the claim**; the derived bound is
      **1.372 pp** simultaneous (1.287 pp per-dataset), which is tighter than the registered margin
      but is emphatically *not* half a point. Writing "half a point" on the region axis is a
      three-fold overstatement and contradicts the Texas (+1.21) and California (+1.06) gains
      recorded in the bullet above.
    - Quote the bound for the axis being discussed, never a margin invented for the sentence, and
      never a single cross-axis number.
  - **Direction always travels with an equivalence claim.** The bound constrains magnitude, not
    sign. On region the dedicated model is *resolved* better at Alabama (−0.87), Arizona (−0.44) and
    Florida (−0.16), all inside the margin; on category the intervals at Istanbul, Alabama and Texas
    exclude zero before correction. A cell inside the margin is never written as "no difference".
  - **Banned on either axis**: "matches", "ties", "empata", "semelhante", "a par", "Pareto",
    "beats", "wins", "outperforms everywhere", and any bare claim of equality. The category cells
    are written as **"equivalent to zero within half a point"**, a bounded-magnitude claim whose
    bound is read off the intervals rather than chosen, never as a match.
- **Time-indexed claims** (this arc's rule): CBIC's "MTL does not help" and CoUrb's protocol
  are presented as conclusions *of the time, for that configuration*. Superseded numbers never
  read as current. Corrections are stated as corrections ("later shown to be
  configuration-specific"), with the correcting chapter named.
- **Describe the method as it stands, not the journey to it** (author, 2026-09-29). The reader
  wants the current method and the state of the solution, not how the code got there: no "an
  earlier build of the same graph", no generation names, no "we first tried". The arc between the
  three articles (the rule just above) is the exception that serves the narrative, and others must
  earn their place the same way. **The rule removes words, never evidence.** Where a qualifier
  exists because a measurement was NOT taken on the delivered build, deleting the qualifier alone
  makes the text claim something unmeasured. Re-measure on the delivered build, drop the claim, or
  keep it as a declared exception. Never silently drop the qualifier.
- **Do not justify what the reader has no reason to doubt** (author, 2026-09-30). A defensive
  sentence about a property the text already makes plain makes the reader wonder why it needed
  defending. The case was "only the HMT-GRN comparison model uses this prior; our models do not": the
  method section already shows our models don't use it, so the sentence stays out. This differs
  from the fairness disclosures the reader cannot infer (who was trained on which users): those
  stay, and they are written so the intention is plain.
- **Uncertainty is stated, not implied**: fold-std or CI wherever a mean appears in a claim;
  "significant" only with the test named.
- Scope every universal: "at all six datasets" only right after the six are enumerated; the
  region-count scaling claim is scoped to the five U.S. states; bare "everywhere" never.
- Limitations are concrete ("3,150 rows", "2009–2010 Gowalla") and split Viegas-style:
  design-time scope/assumptions in §1.4 vs. evaluation-time limitations in §6.2.
- Failures and negative results are findings, not embarrassments — the CBIC null result is the
  arc's foundation; write it with the same care as the wins.

## 4 · AI-tell law (2026 state; inherits GLOSSARY §7 wholesale, plus the updates below)

**Inherited bans (see the paper GLOSSARY §7 for the full tables — they apply verbatim):** the
banned-word list (delve, intricate, showcase, underscore, pivotal, leverage, seamless, testament,
moreover-family openers, "it is worth noting", …), banned templates ("not only X but also Y",
"plays a crucial role", "in today's world", Firstly/Secondly scaffolds, participial significance
tails), and the density rules (≤1 intensifier per claim; -ly adverb density ≈0.8% max, never two
in one sentence; no semicolon braids; no rule-of-three cascades; vary paragraph openings; never
end a section by restating it).

**2025–2026 updates (from the current detection literature; sources in
[`AGENT_GUARDRAILS.md`](AGENT_GUARDRAILS.md) §8). The numbered items below are cited elsewhere
as §4.1–§4.10:**

1. **The list is versioned and rotting.** Word lists decay as models and authors adapt (the
   classic tells are already declining in 2024–25 corpora). Re-audit with fresh eyes per pass;
   do not treat the ban table as complete protection.
2. **Distributional tells matter more than tokens.** Watch for: nominal style (noun/determiner
   density creeping up, adjectives/adverbs vanishing), uniformly formal impersonal register, and
   shrinking vocabulary. Spot-check: read one page aloud; if every sentence has the same weight,
   rewrite.
3. **Variance compression is the deepest tell.** LLM revision homogenizes sentence and paragraph
   statistics (measured: Claude-family revision reduced variance in ~78% of stylometric
   features). The law: **preserve burstiness** — keep short sentences next to long ones, let some
   paragraphs open with a result, keep the author's own phrasings when editing; an editing pass
   that only smooths is a regression.
4. **Discourse-skeleton reuse.** Models recycle the same section shapes (identical opening move,
   same transition sentences, same wrap-up) — across a 100-page document this is glaring. Chapter
   openers must not follow one template; results discussions must vary their move order; the
   per-section "purpose statement" rule (§1) is about content, not a fixed sentence shape.
5. **Model-specific tics ("aidiolects").** For Claude-family drafting specifically: watch
   "genuine/genuinely", "comprehensive", "robust" (decorative), "crucially", "notably", and
   over-hedging stacks ("it is important to note, however, that…"). One decorative instance is
   noise; density convicts.
6. **Do not over-ban:** robust, novel, framework, comprehensive, baseline are normal CS words
   when load-bearing. The offense is decoration and stacking.
7. **Claim-first paragraph shape ("fixed arc").** Confirmed against 2025–2026 corpus work, not
   folklore: LLM essays "follow a more fixed arc, often opening with a direct claim and moving
   quickly toward proposals" (Kim, Chang, Pham & Iyyer, *Argument Collapse: LLMs Flatten Long-Form
   Public Debate*, arXiv 2606.01736, 2026; 23,384 essays, verified at the source). Measured: within
   one debate, main-argument uniqueness is 65.3% for humans vs. **3.4% for LLMs**; sub-argument
   uniqueness 41.0% vs. 9.1% — "LLMs often reuse generalized and hedged sub-arguments, while humans
   prefer more concrete and topic-specific ones." The defect is not the strong opening sentence
   itself, it is that the elaboration behind it is generic support rather than a specific fact.
   **The rule:** a paragraph-opening claim must already carry a scoped, concrete element (a number,
   a name, a citation, a file reference) — never a free-floating assertion unpacked only by
   restatement. Not every paragraph in a chapter may open with its strongest sentence; vary which
   sentence carries the claim (first, mid-paragraph after a setup, or last as a landed conclusion).
8. **Connective loss tracks lexical inflation — check them together.** 823,798 arXiv abstracts,
   pre/post-ChatGPT: cohesion and readability "indicates that abstracts have fewer connecting
   words" after LLM adoption, alongside greater lexical complexity but simplified sentence
   structure, and **Computer Science showed the most pronounced shift of any discipline measured**
   (Bao, Zhao, Mao & Zhang, *Examining Linguistic Shifts in Academic Writing Before and After the
   Launch of ChatGPT*, arXiv 2505.12218, 2025, verified at the source). The failure mode is not
   zero connectives — it is a connective that is either **absent** or **templated/interchangeable**
   (a stock "moreover"/"furthermore" that could be deleted or swapped without changing the logic).
   **The test:** for every transition between two sentences or two paragraphs, delete the
   connective and read the join; if the logical relation still has to be inferred, or reads
   identically with a different connective substituted, the transition is decorative, not
   load-bearing — name the actual relation (contrast, consequence, restriction, added constraint)
   instead of reaching for the reflex word.
9. **Sentence length without local repair.** 2025-generation model sentences run **15–30% longer**
   than human-authored text (vs. 2023-generation models, which ran 10–20% *shorter* than human),
   while parsing more cleanly (98–99% success under a formal grammar vs. 93–95% for the human
   baseline) — longer sentences that are grammatically too clean (Gude, Santos-Ríos, Bond,
   Flickinger, Gómez-Rodríguez & Zamaraeva, *More Aligned, Less Diverse? Analyzing the Grammar and
   Lexicon of Two Generations of LLMs*, arXiv 2605.06030, 2026, verified at the source). Real
   non-native academic prose is locally bumpier even when the overall argument is careful — a long
   sentence with zero internal correction, apposition, or re-phrasing earns a second look. Extends
   §1's hard-phrasing rule: length alone is not the defect, but a long, perfectly regular sentence
   is a signal to re-read.
10. **Rigid section skeletons (reconfirmed live for 2025–2026, not decayed).** A "Challenges"-shaped
    section that always opens "Despite its [positive framing], X faces challenges…"; headings that
    contain only sub-headings with no prose between them; an inline vertical bullet list standing
    in for connected prose where a section expects paragraphs (*Wikipedia:Signs of AI writing*,
    community-maintained, verified 2026-08-21). None of these are new bans — they are §4.4's
    discourse-skeleton rule and §5's structure rules, applied at the sub-section level; recorded
    here because the source shows these specific shapes still fire in 2025–2026 output.

**Idiom rule (inherited GLOSSARY §8):** no phrasal-metaphor idioms ("edges past", "buys",
"ships", "lands", "folds in", "clears it by"); metaphor budget for "carry/carries" ≤3 per
chapter; "deliberately X" → "X by design"; "sits above" → "lies above" (one verb everywhere).

## 5 · Structure and presentation rules (Viegas-derived; details in `exemples/viegas/VIEGAS_ANALYSIS.md`)
*(A pasta `exemples/` foi apagada em 28/08/2026 na limpeza; o conteudo esta em `~/Backups/dissertacao_exemples_2026-08-20.tgz`, backup verificado.)*

- **Abstract formula:** problem → barrier → named contribution → concrete capabilities →
  validation design → ONE headline number → closing thesis-verb restatement. UFV catalog header;
  keywords per system rules (one per line, lowercase except proper nouns).
- **Introduction devices:** funnel (3 paragraphs max to the gap); the research question bold
  inline, once; objectives 1:1 with chapters; the coletânea "magic sentence" in the organization
  section with per-chapter venue+status bullets; contributions taxonomy (Theoretical / Software /
  Empirical / Practical) with section cross-refs.
- **Every chapter Introduction ends with a roadmap paragraph**; every section opens with a
  purpose statement (varying shape, per §4.4).
- **Paragraph-to-paragraph transitions are explicit, never templated.** Read the last sentence of
  paragraph N and the first sentence of paragraph N+1 together: the logical link (contrast,
  consequence, restriction, elaboration) must be inferable without re-reading, and stated in the
  receiving sentence's own words rather than a reflex connective (§4.8's delete-and-reread test
  applies at the paragraph boundary too, not only within a sentence). A long section in which every
  paragraph could be reordered without a reader noticing has this defect.
- **Tables:** booktabs only (no vertical rules); captions **above** tables (ABNT; fix Viegas's
  inconsistency); mean ± std with per-block bolded best values; every results table introduced by
  a lead takeaway sentence (a normal sentence, never a literal "Read this as:" tag).
- **Figures:** captions below, 2–4 self-contained interpretive sentences (name every element,
  include reading instructions and color/symbol legends); a notation/legend figure before any
  figure that uses custom notation; color + hatch dual encoding (grayscale-safe); in-figure text
  near body size.
- **Metrics defined defensively:** formula + one-sentence plain reading + boundary/degenerate
  behavior (the Viegas KIS pattern) — apply to macro-F1, Acc@10, the OOD-discounted region
  metric, and the checkpoint-selection rule.
- **Reproducibility blocks:** each experimental section opens with hardware, seeds, folds,
  versions; the code repository footnoted at first mention of each artifact; infrastructure
  software (PyTorch etc.) cited formally in the bibliography.
- **Hygiene sentences:** one explicit in-line sentence per leakage-sensitive step ("X was
  computed on the training folds only…") — the pattern MobiWac §5.2 and the A4 audit already use.
- **Anti-patterns from the example (do NOT imitate):** leftover "this paper"/"the article is
  organized as" inside chapters; "Dataset N" instead of names in results prose; unresolved
  citation keys; inconsistent caption placement; cross-ref typos; 3-line stretched chapter
  titles.

## 6 · Language mechanics per part

- **Frame chapters (1, 2, 6):** English, this file in full force.
- **Paper chapters (3–5):** the source paper's prose is the base; edits obey this file; the
  MobiWac chapter additionally obeys the paper GLOSSARY (it is stricter about plain words —
  do not "re-technicalize" its prose when re-typesetting).
- **Portuguese surfaces** (Resumo; AcademicoPG fields; folha de rosto boilerplate): formal
  PT-BR, no anglicisms where a standard PT term exists (aprendizado multitarefa, ponto de
  interesse, representação em nível de check-in); the Resumo mirrors the Abstract content
  exactly (same claims, same numbers, same hedges — audit them as a pair).
- **The CoUrb chapter** follows open decision #3 (NORTH_STAR §5): if kept PT, this file's
  honesty and structure rules still apply; if translated, translation is a *faithful* re-typeset
  (asserted claims may not drift in strength — see AGENT_GUARDRAILS §4 gate).

## 7 · Consistency checklist (run before every advisor handoff; the gates in AGENT_GUARDRAILS automate part)

- [ ] Canonical names only (§2); zero repo codenames; zero synonym-cycling.
- [ ] Every acronym expanded at first use; acronym count minimal; List of Abbreviations complete.
- [ ] next category / next region / next place kept distinct; "we do not predict the exact next
      place" stated once, early.
- [ ] Verdict ladder intact per §3: "outperforms" only at region TX/CA and category FL; the
      two-point margin is the readable surface on region; the half-point bound appears **only on the
      next-category axis** and is quoted as derived, never as a chosen margin (the region bound is
      1.372 pp, so "half a point" on that axis is a defect, not a rounding); direction travels with
      every equivalence claim; the category cells read "equivalent to zero within half a point" and never "matches"; zero
      occurrences of the banned equality words.
- [ ] Scaling claim scoped to the five U.S. states, stated as an observation with both hedges (not
      monotone inside the Texas–California pair; region count co-varies with corpus size).
- [ ] Time-index framing on CBIC/CoUrb conclusions; no superseded number reads as current.
- [ ] Every number has reference point + convention; every mean has its spread; "significant"
      only with a test.
- [ ] AI-tell sweep: banned words/templates at zero; intensifiers ≤1 per claim; -ly density in
      band; no semicolon braids; paragraph shapes vary; chapter openers not templated.
- [ ] §4.7–§4.10 sweep: no paragraph-opening claim without a concrete element; every transition
      passes the delete-and-reread test (within sentences, between sentences, between paragraphs);
      no long sentence that is too grammatically clean to have been re-worked; no rigid section
      skeleton (the "Despite its X, faces challenges" shape, headings-only-subheadings, bullet
      lists standing in for prose).
- [ ] Language pass: simple, direct American English that the author would defend aloud; American
      spelling and usage are consistent; no passage requires a second reading for its intended
      meaning or logical connection.
- [ ] Register sweep (§1, gate 25 `check_register.py`): zero British spellings and zero British
      constructions outside a verbatim quotation; any hit in reproduced published prose is with the
      author as an errata decision, not changed quietly.
- [ ] Hard-phrasing sweep (§1): no delayed or inverted subject, no abstract noun as agent of a
      motion verb, no chained qualification, no literary connective idiom. The gate covers these
      four shapes; the first-read verdict is persona 15's and is required separately.
- [ ] Idiom sweep: no phrasal metaphors; em-dash count = 0; contractions = 0.
- [ ] Tables captioned above with lead sentences; figures self-contained; metrics defined with
      boundary behavior; hygiene sentences present at every leakage-sensitive step.
- [ ] Resumo ↔ Abstract claim-parity audit passed.
- [ ] "this paper"→"this chapter" sweep in re-typeset chapters; no "Dataset N" prose; no
      unresolved \ref/\cite.
