# Chapter 1 — citation and claim ledger (draft 1, 2026-07-23)

> Fail-closed rule: only two citations enter this draft as settled (`song2010limits`,
> `caruana1997multitask` — both previously verified firsthand in this project). Every other
> candidate key is marked `[VERIFY: key]` **in the .tex itself** and MUST be opened and confirmed
> (R1–R3) before the marker is replaced by a `\cite`. No number or claim in the chapter comes
> from model memory.

## Settled citations

| Key | Claim it supports | Verification |
|---|---|---|
| `song2010limits` | "potential predictability of an individual's next location at about 93 percent" | Opened firsthand (fundamentals pass, 2026-07-21): Song et al., Science 327:1018 (2010). The 93% figure is the upper bound of potential predictability. Wording "about 93 percent" matches the source's ~93%. |
| `caruana1997multitask` | MTL definition / fixed-weight joint training lineage | In all three papers' bibs; the canonical MTL reference (Caruana 1997, Machine Learning 28). Already cited by MobiWac §4 for the same purpose. |

## Breadth anchors — VERIFIED 2026-07-23 (abstracts opened this session; markers replaced by \cite)

Method: arXiv API abstracts opened and read this session for the five arXiv-hosted works;
`Xu2023` abstract obtained from the publisher record via the article-fetch tool (full text closed
access). Each claim in the draft was then rewritten to match what the opened source actually says.

| Key | Opened source | What it supports (as now worded in the draft) |
|---|---|---|
| `luca2021mobilitysurvey` | arXiv 2012.02825 abstract | "The study of human mobility informs urban planning, disease spreading, and pollution analysis" — the abstract lists exactly these societal impacts. Key resolves in the MobiWac bib (verified earlier this session). |
| `Xu2023` | ACM TOIS abstract (DOI 10.1145/3582553) | "place categories are the semantic characterization that annotation and recommendation services rely on" — abstract: categories "serve as excellent semantic characterization of the venues"; the paper does semantic venue annotation. NOTE: the earlier "urban planning" wording was CBIC's framing, not Xu's — the claim was reworded to what Xu2023 itself says, and urban planning moved to the luca survey where it is licensed. |
| `mai2023sphere2vec` | arXiv 2306.17624 abstract | "location encoders first validated on species recognition and remote sensing" — abstract: applied to "fine-grained species recognition, Flickr image recognition, and remote sensing image classification". |
| `wu2024torchspatial` | arXiv 2406.15658 abstract | same provenance claim — abstract names "species distribution modeling, weather forecasting" as downstream applications of location encoding. |
| `kokkinos2016ubernet` | arXiv 1609.02132 abstract | "single networks that handle many vision tasks at once" — abstract: "jointly handles low-, mid-, and high-level vision tasks in a unified architecture". |
| `lipton2015learning` | arXiv 1511.03677 abstract | "recurrent models that diagnose over a hundred clinical conditions simultaneously" — abstract: "multilabel classification of diagnoses ... 128 diagnoses". |
| `wei2022finetuned` | arXiv 2109.01652 abstract | The storyline/09 caution was CORRECT: this is FLAN (instruction tuning), not classic NLP MTL. The draft wording was set to "language models fine-tuned across dozens of tasks described by instructions" — which is what the paper does ("instruction-tune it on over 60 NLP tasks"). |

Author action remaining: the six keys above must be copied into the dissertation's global
`references.bib` from their bibs of origin (CBIC / CoUrb / MobiWac), with the `mai2023sphere2vec`
key normalized (CoUrb's bib key is the long `mai2023sphere2vecgeneralpurposelocationrepresentation`
— rename or alias when the global bib is assembled).

## Numbers in the draft and their reference points

| Number | Source of truth | Convention |
|---|---|---|
| "about 93 percent" | song2010limits (firsthand) | potential (upper-bound) predictability, not achieved accuracy |
| "seven top-level classes" | GLOSSARY / docs/context/TASKS.md | the 7-category taxonomy |
| "hundreds to several thousand classes" | MobiWac §3 (520 Istanbul … 8,501 California) | region-class counts per dataset |
| "64-dimensional place embedding" → "decomposed spatial, temporal, and categorical encoders" | CoUrb intro (firsthand) | DGI 64-d vs 192-d decomposed input |
| "category everywhere; region four of six; non-inferiority two-point margin" | NORTH_STAR §1 / MobiWac §8 (verbs bound: outperforms = paired test; non-inferiority = TOST ±2pp) | n=20; re-verify against the board before compile |
| "twenty repetitions (four seeds, five folds)" | DATA_SPLITS.md / MobiWac §5 | n = seeds × folds |
| DOIs and venue names in §1.5 | NORTH_STAR §2 table | copied verbatim |

## Claim-discipline notes (how the signed-off beats were rendered)

- **Beat 2 / F3 guard:** the tension paragraph promises *operational simplicity* only; the words
  "lower cost" do not appear. The CBIC beat says "cost more to train" (licensed, published claim).
- **Beat 4(a) task-pair acknowledgment:** rendered as its own closing paragraph of §1.2 ("The task
  pair therefore evolved…"), factual, no defense (the defense lives in §2.1 and the prefaces).
- **Beat 4(b) three legs:** one sentence in §1.1 ("chosen for what a mobility-aware service can act
  on and for the standing of both targets as end tasks in the literature on the way to the harder
  next-place problem"); leg 2 rendered in its approved fallback form (standing as end targets), NOT
  the comparative "more present in the literature" form (still gated on an opened anchor).
- **Beat 4(c) corollary:** "the static classification of places becomes the less natural fit" —
  "unnatural/less natural", never "incoherent".
- **Beat 4(d) N2 caution form:** "three candidate explanations, one of which pointed at the input
  representation" + "took the representation door first, as the cheapest controlled test among the
  three". CBIC's own future work (architecture door) is NOT claimed as a representation program.
- **Beat 4(e) mechanism-as-hypothesis:** "Any place-level embedding assigns a place the same vector
  on every visit… That observation is the hypothesis the final study tests."
- **Two-factor law (F1):** every payoff summary names both factors ("check-in-level representation
  plus a redesigned sharing topology"; Theoretical contribution: "the input representation,
  together with the sharing topology built on it").
- **Region verbs:** "outperforms … at four of six, with statistical non-inferiority within a
  two-point margin at the other two" — no upgrade of AL/AZ.
- **MobiWac status:** "submitted … and currently under review" in §1.2 and §1.5.
- **CoUrb authorship note (Comissão):** rendered in the §1.5 bullet (first author Tarik S. Paiva;
  this author second author, contributed the MTLnet baseline, presented the paper).
- **Contributions taxonomy:** Theoretical / Software / Empirical / Practical per NORTH_STAR beat 8.
- **No em-dash, no contractions** — checked; "cannot" used over "can't"; hyphens only in compounds.

## Revision record — draft 2 (2026-07-23, after the four-persona review + author's three points)

Author's three points, applied:
1. **Dropped task named**: the static task now appears in §1.1 as a fourth task with its canonical
   short name ("category classification"), with a forward pointer to §1.2 for why the final study
   replaced it; the CBIC beat names it the same way.
2. **CBIC architecture callback**: the third-study paragraph now says the sharing redesign acts "on
   another of the first study's candidate explanations, the restrictiveness of hard parameter
   sharing" — the architecture change is explicitly a reflection of CBIC's hypothesis list, in the
   approved caution form (CBIC opened doors; no foresight claimed).
3. **CoUrb authorship**: kept. Not a citation question but a Comissão-transparency one — the
   coletânea block (banca Q21) requires authorship stated where the collection is declared; the
   banca simulator confirmed the bullet as correct and necessary.

Four-persona review (cold reader / claim honesty / readability / banca; full results in
`storyline/audit/ch1_review.md`): verdicts 3× ready_with_fixes, 1× needs_work (claim honesty).
All BLOCKERs and MAJORs fixed in draft 2:
- "matches or exceeds" → licensed verbs ("outperforming … outperforming or remaining non-inferior");
- "Billions of such records" → "at large scale" (unledgered number removed);
- "pipeline that produced every number in this document" → "pipelines behind the experiments of
  Chapters 3 and 5";
- Objective 4 protocol binding: user-disjoint CV bound to Chapter 5, no longer implied for Ch. 3–4;
- "all six datasets" now preceded by the count + composition in the same sentence;
- "did not consistently beat" → "did not consistently outperform" (banned verb);
- venue expansions for CBIC/MobiWac downgraded to short names + [VERIFY before compile] comments
  (the ledger claimed "copied verbatim" but NORTH_STAR stores only short names — expansion was
  memory, now quarantined);
- encoder-provenance claim scoped to "part of the representation machinery … the spatial location
  encoders of the second study";
- Xu2023 claim trimmed to "location-based services" (recommendation not in the opened abstract);
- "version of record of each paper" → "published text … or the submitted manuscript" (MobiWac has
  no version of record);
- overpacked sentences split (arc payoff, negative-transfer closer, task-choice sentence);
  defensive class-count tail cut (the litigating clause; the count already lives at the region-task
  definition); door metaphor removed; "of the time" → "at that stage of the research";
  POI expanded at first use; "end tasks" → "end targets"; Theoretical/Software items split/scoped.

Residual NITs accepted as-is (triads at §1.1 are varied; the single-model formula repeats by
beat mandate with varied wording).

## Venue verifications (2026-07-23, pages opened this session — closes the two [VERIFY] comments)

| Chapter | Verified expansion | Source opened |
|---|---|---|
| Ch.3 | XVII Congresso Brasileiro de Inteligência Computacional (CBIC 2025), promoted by SBIC, Belo Horizonte, Oct 27–30 2025 | official site cbic2025.dcc.ufmg.br |
| Ch.4 | X Workshop de Computação Urbana (CoUrb 2026), held jointly with SBRC 2026 (XLIV Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos), May 25–29 2026, Praia do Forte/BA; proceedings in SBC OpenLibrary (SOL) | sol.sbc.org.br/index.php/courb + sbrc.sbc.org.br/2026/courb |
| Ch.5 | 23rd ACM International Symposium on Mobility Management and Wireless Access (MobiWac 2026) | mobiwac-symposium.org/2026 (official symposium site names the 23rd edition; the ACM proceedings series name matches prior editions in the ACM DL) |

Note: the draft writes the Ch.4 venue in Portuguese (proper name) with the SBRC affiliation, per
the banca simulator's NIT. English framing text around it is unchanged.

- No CoUrb-baseline-boundary sentence (Item 6) — lives in the Ch.4 preface.
- No negative-transfer-reversal / cosine number (N3) — lives in Ch.6 §6.4.
- No §3.4 confound concession — lives in Ch.6 limitations.
- No model-lineage table — lives in Ch.2.
- No capacity-baseline numbers (D1) — post-submission frame analysis, gated on the run.
