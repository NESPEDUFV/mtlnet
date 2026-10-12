# 38_reviewer_wave2_round9.md — the five style and domain personas, against build `901a0408`

Round 9, 2026-07-30, second wave. Requested by the author: 15 readability, 16 AI credibility,
17 excellence, 11 POI/mobility expert, 10 MTL expert. Fresh-eyes agents, none of which wrote the text.

**Build under review:** commit `901a0408`; `main.pdf` 102 pp, `main_academico.pdf` 99 pp,
`main_ppgc.pdf` 103 pp, `main_extra.pdf` 20 pp. `make check` rc=0 (31 probes at dispatch),
`make selftest` rc=0.

| persona | blockers | should-fix | nits | wall clock | report |
|---|--:|--:|--:|--:|---|
| 16 AI credibility | **1** | 3 | 3 | 27.5 min | `reviews/16_ai_credibility.md` |
| 15 readability | 0 | 12 | 4 | 31.2 min | `reviews/15_readability.md` |
| 10 MTL expert | 1 (downgraded) | 5 | 3 | 44.2 min | `reviews/10_mtl_expert.md` |
| 11 POI/mobility expert | 0 | 4 | 1 | 46.2 min | `reviews/11_poi_mobility_expert.md` |
| 17 excellence | 0 | 5 | 2 | 56.2 min | `reviews/17_excellence_assessor.md` |

## The checkpoint failed again, and my diagnosis of why it failed the first time was wrong

Wave 1: four personas, a 25-minute checkpoint, all four over, mean 31.3 min. I diagnosed **scope, not
the clock**, and acted on it — every persona in this wave got a deliberately narrowed scope (frame
chapters only, one section only, skip the paper chapters) and a 30-minute checkpoint.

**Result: one of five inside, mean 41.1 minutes, worst 87 percent over.** The mean got *worse* than
the wave whose diagnosis this was supposed to fix.

So the narrowing was not the operative variable. What separates the one persona that finished
(27.5 min) from the three that ran 44 to 56 minutes is not how much text they were given — the MTL
expert had one section, the excellence assessor had the whole volume, and both overran. It is **how
many external sources the work required opening**. The AI-credibility pass is mechanical sweeps over
text already on disk. The MTL expert downloaded and paged through five arXiv PDFs. The POI expert
built and then rebuilt a pointer-verification instrument. The excellence assessor read across the
whole volume and corrected one of its own instruments mid-report.

**Two of those overruns bought something.** The MTL expert **withdrew two of its own findings** after
opening the pages that refuted them, and the POI expert **caught its own location layer twice** —
first stripped-grep line numbers, then a repair whose heuristic could not detect the very defect class
it was checking, and replaced it with a phrase-anchored check plus a negative control. That work is
why their reports are usable, and it is exactly the work that does not fit in 30 minutes. Time spent
retracting a wrong finding is the best-spent time in a review round.

**The honest conclusion:** a wall-clock checkpoint disciplines a persona that reads what is already on
disk, and does not bind one that must resolve external sources. For source-resolving personas the
budget should be stated in **sources opened** rather than minutes — "verify at most five attributions,
name the rest as unreached" — and the clock should be advisory. Recorded rather than smoothed because
I got this wrong once already this round and wrote the wrong conclusion into a report.

## Findings I verified myself before recording them

### CONFIRMED · Appendix F describes an experiment that was never run (AI credibility, blocker)
- **Where:** `chapters/apx_f_cosine.tex`:83, rendering at `main.pdf` p. 97.
- **Verbatim:** "That is why replacing the sharing scheme changed so little in the first study, and
  why changing the representation changed so much in the second and third."
- **What I checked.** Chapter 3 built **one** architecture — `3_cbic/method.tex`:69, "built upon a
  hard parameter-sharing scheme" — and its conclusion lists alternatives as future work:
  `3_cbic/conclusion.tex`:23, "We plan to explore alternative parameter-sharing mechanisms, such as
  **soft sharing (e.g., Cross-Stitch Networks) or Mixture-of-Experts (MoE) models**". Its results
  compare MTL against single-task baselines and against MHA+PE and HMRM, never two sharing schemes.
  `1_introduction.tex`:133-135 attributes the sharing-topology replacement to the **third** study.
- **And the same appendix states it correctly two pages later**, at :294-299: the first study's null
  was *read* as evidence about sharing at the time, and the limit turned out to lie elsewhere.
- **Severity confirmed as blocker.** A reader of p. 97 is told an experiment happened that did not.
  The correct sentence already exists in the same appendix.

### DOWNGRADED · PCGrad "makes no Pareto claim at all" (MTL expert, filed as blocker)
- **Where:** `chapters/2_fundamentals.tex`:442-445.
- **The report's evidence:** CAGrad p. 5 attributes arbitrary-Pareto-point convergence to PCGrad's own
  analysis, so the chapter's absolute is contradicted.
- **What I checked, opening both records this session.** arXiv:2001.06782 (PCGrad, *Gradient Surgery
  for Multi-Task Learning*, NeurIPS 2020): no 'Pareto' and no convergence sentence in the abstract;
  the repo's own extraction found **zero** 'Pareto' in 27 pages with the instrument validated on the
  same text. arXiv:2110.14048 (CAGrad, NeurIPS 2021) abstract: prior methods "lack convergence
  guarantee and/or could converge to any Pareto-stationary point."
- **The distinction the report collapses.** The chapter's clause is cited to `yu2020pcgrad` and its
  subject is what **that paper** claims. CAGrad's sentence is a third party characterising a family.
  "X makes no Pareto claim" and "Y says methods like X converge to arbitrary Pareto points" are
  compatible; the second is not a claim by X. **The sentence is accurate about the source it cites.**
- **What survives, as a should-fix on phrasing.** If CAGrad p. 5 does attribute a result to PCGrad's
  own analysis, a reader who knows CAGrad will find "no Pareto claim at all" flatter than the
  surrounding literature supports. **I could not read p. 5** — only the abstract was reachable — so I
  am downgrading, not dismissing, and saying which half I could not check.

### CONFIRMED · the central claim carries five different names (readability, should-fix)
Measured across the three frame chapters: "bottleneck" (Ch.1, Ch.6), "moves the results" (Ch.2),
"the lever" (Ch.2, three times), "binding constraint" (Ch.6), "decisive variable" (Ch.6). Five
phrasings for the dissertation's single most important finding, in the three chapters whose job is to
make three papers read as one document. `WRITING_LAW` bans synonym-cycling; this is the highest-value
instance of it in the volume.

### CONFIRMED, and already known · the trapped chapter-list stem (readability, should-fix)
`1_introduction.tex`:225, "% The collection is organized as follows:" — commented out, so the reader
falls from the errata sentence straight into the bullets. The comment above it explains the deferral
and instructs the author to restore it and re-measure page counts. Logged in `_history/_round7/27`, still open.

## What the domain experts confirmed as sound, which is the load-bearing half

**The POI/mobility expert found zero blockers** and confirmed the three-task distinction (next
category / next region / next place) is held cleanly everywhere it read, that the check-in-level
versus place-level argument is correct as a mobility-modelling claim and properly grounded on CTLE
rather than on the author's own result, and that Chapter 5's protocol disclosures are **stronger than
this literature's norm**. Its four should-fix items are all one defect class: **placement, not truth**
— defences Chapter 5 carries that Chapter 2 does not (window construction, transductivity, the region
unit's justification, the revisitation intuition).

**The MTL expert verified six of the seven guarantee clauses** in today's Pareto passage as written,
against five source PDFs, and found two clean end-to-end attributions (Sener-Koltun, Aligned-MTL).

**The excellence assessor scored it a strong VERY GOOD** with a cheap path to outstanding, and made
one judgment worth quoting to the committee: the published null result is **unambiguously an asset**
as presented — time-indexed where it appears, kept as a finding, and converted into method. Both
cross-cutting tests pass. What holds it below outstanding is not honesty, coverage or rigor but two
syntheses left for the reader: no consolidated cross-study evidence table, and the volume's strongest
representation evidence never reaches the frame.

## A finding of mine that these reports closed

The wave-1 honesty gate flagged the convexity clause at `2_fundamentals.tex`:437-440 as possibly the
writer's gloss rather than the source's claim, having not opened arXiv:2202.01017. **The provenance
comment at :454-461 already resolves it**: Theorem 5.5, pp. 6 and 14, quoted verbatim — "if we also
assume that all the loss functions are convex then the sequence ... converges to a Pareto optimal
point". I opened the arXiv record this session and confirmed the title, the ICML 2022 venue, and that
the abstract carries neither 'convex' nor 'deep'. So the *guarantee* is sourced; what remains the
writer's inference is only the trailing "that a deep network does not satisfy", which is the narrower
half of the flag and the half the honesty gate's fix (b) addresses.

## Unfinished, reported by the personas themselves

All five reported unfinished scope. The largest gaps:

1. **No persona in this wave resolved a citation identifier except the MTL expert.** The POI expert
   states plainly that its silence on citations is "unexamined, not clean" — the right way to report
   an unrun check.
2. **The excellence assessor did not read 40-odd pages**, including the Portuguese Resumo, so the
   intro-conclusion loop test was never run against the claim-parity pair; and it names a table whose
   values it did not open, warning that whoever applies its fix must copy from the table.
3. **The MTL expert's five surviving findings were not re-verified beyond the pages quoted**, and it
   says so — having had two findings fail for exactly that reason.
4. **The readability pass covered only `main.pdf`**, and did not diff today's new Chapter 2 lines
   against the prior commit, so it could not establish whether two of its findings were introduced
   there.
