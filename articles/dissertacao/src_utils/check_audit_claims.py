#!/usr/bin/env python3
"""check_audit_claims.py -- re-measures every "APPLIED" claim against the live source.

WHAT IT GATES. THREE things, and the scope is wider than the name -- stated here in full because a
docstring claiming one scope over code covering more is itself a defect this repo has hit:

  (1) the CODEX_AUDIT outcome table's COD-/NUM- findings;
  (2) fixes this project made on its own initiative (the `R8-` probes);
  (3) SINCE 2026-07-30 (round 9), the REVIEW TRACKER ITSELF -- the `R9-` probes below read
      src_utils/CONSIDERATIONS.md and src_utils/PENDENCIAS.md, which are NOT under src/. That is why
      there are two roots (SRC and UTILS) and why a probe's path is resolved against whichever root
      its file lives in. Round 9 sorted 43 reviewer points into apply/decide/blocked; the register of
      that split is a claim about the work in exactly the sense V14 means, so it is gated here rather
      than trusted.

An outcome table is a CLAIM ABOUT THE WORK, the highest-risk statement class here, and it was the one
class with no gate: on 2026-07-30 eight of nine findings marked APPLIED were still unapplied.

HOW TO ADD A PROBE -- do this in the SAME commit as the fix, not later.
    ("id", "what the claim asserts", "path/under/src", r"regex", True)   # True = must be PRESENT
Then prove it bites: revert the fix, run this file, read rc. rc must be 1. If the suite stays green,
the fix is undefended (GUARDRAILS §4b V15). A claim you cannot probe goes in NOT_CHECKABLE, never
silently omitted -- and RETIRED holds probes the author withdrew, kept visible so nobody "finishes"
a finding he closed.

FOUR MEASUREMENT TRAPS, each of which produced a WRONG verdict here before it was fixed:
  1. comment-blind matching scored a missing fix as done -- provenance comments quote the very
     strings being checked, so all matching runs on live_text().
  2. per-line matching scored a real fix as missing -- claims wrap; live_text() joins lines.
  3. an escaped `\%` mid-sentence truncated a paragraph and hid the clause after it, so the
     stripper only cuts an UNESCAPED `%`. Self-tested both ways before this file reports anything.
  4. a sabotage that does not reach live_text() reads exactly like a probe that never fires -- all
     seven `\begin{document}` in preamble.tex are inside comments. Assert the token is in
     live_text() before believing any verdict about it.

Full history -- why each probe exists, the closed-register audit, the corrected provenance of the
baseline measurements -- is in _history/_round8/29_pendencias_detail.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
UTILS = Path(__file__).resolve().parent          # the trackers live HERE, not under src/
COMMENT = re.compile(r"(?<!\\)%")


def probe_root(rel: str) -> Path:
    """Which root a probe's path is relative to.

    Added round 9 with the R9- probes. The `%`-comment stripper stays on for BOTH roots: it is a
    no-op on markdown (no unescaped `%` in these trackers -- asserted in self_test), and turning it
    off per-root would be a second code path to get wrong.
    """
    return UTILS if rel.endswith(".md") else SRC

# (finding, what the audit claimed, file, pattern, want_present)
#   want_present=False -> the flagged string must be GONE for the claim to hold
#   want_present=True  -> the added text must be THERE
PROBES: tuple[tuple[str, str, str, str, bool], ...] = (
    ("COD-003",  'Ch.1 objective 4 no longer says "leakage-guarded"',
     "chapters/1_introduction.tex", r"leakage-guarded", False),
    ("COD-006a", '"well powered" removed from the Ch.5 protocol paragraph',
     "chapters/5_mobiwac/05_setup.tex", r"well powered", False),
    # COD-006b IS DELIBERATELY EXPECTED TO BE PRESENT. The audit flagged both "well powered" and
    # "before any result was read", but the author's decision was explicitly narrow: "Let's change
    # only the second point about the: 'The equivalence is well powered'." The analysis plan
    # genuinely WAS fixed before results were read, so the phrase is accurate and stays. The probe
    # is kept, inverted, so that a later agent "tidying up" the other half of the audit finding is
    # caught by the gate instead of silently overriding an author decision.
    ("COD-006b", 'the author kept "before any result was read" -- it is accurate and he said so',
     "chapters/5_mobiwac/05_setup.tex", r"before any result was read", True),
    ("COD-013",  "Appendix C names the model family in PROSE, not only in a comment",
     "chapters/apx_c_ai_disclosure.tex", r"Opus", True),
    ("COD-015a", "Ch.3 preface no longer says Ch.4 and Ch.5 both change the representation",
     "chapters/3_cbic.tex", r"revise that verdict by changing the input representation", False),
    ("COD-015d", "Ch.2 no longer promises a relative multi-task performance metric",
     "chapters/2_fundamentals.tex", r"relative multi-task performance", False),
    ("COD-016a", "Ch.3 unbalanced-result sentence rewritten",
     "chapters/3_cbic/results.tex", r"important to notice that since we have an", False),
    # COD-018 was HERE and is retired deliberately, not dropped. See RETIRED below.
    # ---- ROUND-8 FIXES OF OUR OWN, not CODEX_AUDIT findings. Added 2026-07-30 after a review
    # observed that this file gated only the inherited audit and nothing round 8 repaired on its own
    # initiative: all three reverts below left 22 gates green, measured by sabotage.
    ("R8-head",  'Ch.5 says "region output", not the banned "region head"',
     "chapters/5_mobiwac/06_results.tex", r"region\s+output\s+was\s+driven", True),
    ("R8-head2", 'the same sentence says "region-transition prior", not the repo shorthand',
     "chapters/5_mobiwac/06_results.tex", r"region-transition\s+prior", True),
    ("R8-vintage", "Ch.6 data-vintage item prints BOTH Gowalla windows, the paper's and the measured one",
     "chapters/6_conclusion.tex", r"August\s+2011", True),
    ("R8-bibfont", "no footnotesize wrapper around the bibliography (REV-024, archived on one measurement)",
     "preamble.tex", r"footnotesize", False),
    ("NUM-4",    "HGI sweep reports its spreads and its averaging convention",
     "../wrapup/material_extra/chapters/apx_g_hgi_tuning.tex", r"0\.8186", True),
    # ---- ROUND-9c PROBES: the AUTHOR'S OWN RULINGS of 2026-07-30, one per mechanically checkable row.
    # Ledger and per-row evidence: _history/_round9/47_applied_check.md. These exist because a future edit that
    # undoes one of his requested changes must trip a gate rather than reach the banca silently.
    # The nine REMOVAL probes were each validated against git show 06529ed6:<file>, where the pattern
    # matched the original exactly once -- so an absence here is evidence and not an inexpressible pattern.
    ("A22-2",  "his point 2: 'stranger result' is gone",
     "chapters/apx_f_cosine.tex", r"stranger", False),
    ("A22-3",  "his point 3: the arc sentence relating this result to the first study is gone",
     "chapters/apx_f_cosine.tex", r"changed so little in the first study", False),
    ("A22-5",  "his point 5: the over-detailed series clause is gone",
     "chapters/apx_f_cosine.tex", r"carry a partial re-run on top of theirs", False),
    ("A22-6",  "his point 6: the development-time implementation detail is gone",
     "chapters/apx_f_cosine.tex", r"this appendix supersedes nothing there", False),
    ("A22-8",  "his point 8: the British needs+gerund is gone and the American form is present",
     "chapters/apx_f_cosine.tex", r"needs saying", False),
    ("A22-8b", "his point 8, the replacement half",
     "chapters/apx_f_cosine.tex", r"must be stated plainly", True),
    ("A22-9",  "his point 9: the AI-shaped opener is gone",
     "chapters/apx_f_cosine.tex", r"Two departures from that flat picture", False),
    ("A22-10", "his point 10: the 'rather than smoothing' clause is gone",
     "chapters/apx_f_cosine.tex", r"worth reporting rather than smoothing", False),
    ("A22-11", "his point 11: the t-test sentence names its datasets",
     "chapters/apx_f_cosine.tex", r"does reject at Alabama and at Georgia", True),
    ("A22-12", "his point 12: the native-idiom sentence is gone",
     "chapters/apx_f_cosine.tex", r"point away from trouble", False),
    ("A22-13", "his point 13: the arc-of-three-studies paragraph is gone",
     "chapters/apx_f_cosine.tex", r"arc of the three studies", False),
    ("A22-14", "his point 14: orthogonal gradients do not mean the tasks share no knowledge",
     "chapters/apx_f_cosine.tex", r"share no knowledge", True),
    ("A22-1",  "his point 1: the negative-transfer claim carries its citation",
     "chapters/apx_f_cosine.tex", r"standley2020tasks", True),
    ("A22-4",  "his point 4: the cosine approach carries its citation",
     "chapters/apx_f_cosine.tex", r"yu2020pcgrad", True),
    # The fold is the analysis unit, not an independent experimental replication: cross-validation
    # training subsets overlap. The probe preserves the author's requested fold-level statement
    # without encoding the stronger and statistically inaccurate independence wording.
    ("A22-7",  "his point 7: the fold-level analysis statement survived the simplification",
     "chapters/apx_f_cosine.tex", r"unit of analysis is the fold", True),
    ("A11-diss", "his 2.11 option B: the dissertation's Ch.5 carries the non-inferiority caveat",
     "chapters/5_mobiwac/06_results.tex", r"non-inferior", True),
    ("A11-frame", "his 2.11 option B: the caveat reaches the Resumo and Abstract, which dropped it before",
     "content.tex", r"n[aa\u00e3]o-inferior", True),
    ("A11-frame2", "his 2.11 option B: the English abstract too",
     "content.tex", r"non-inferior", True),
    ("A14-nash", "his 2.14: the Nash-MTL entry carries the PMLR page range he supplied",
     "references.bib", r"16428--16446", True),
    ("A12-errata", "his 2.12: the Pareto-optimality narrowing has its errata row",
     "tables/cbic/errata.tex", r"Pareto", True),
    # ---- ROUND-9f, 2026-08-02. Item 2.9 was closed on evidence that could not distinguish
    # done from not-done: the probe searched for "+0.001" and "0.0032", which are the OLD
    # four-seed development numbers the item itself was ABOUT, so their presence proved nothing.
    # The closure line also said "both trees edited" when the measurement globbed only src/**.
    # These three probe the actual requirement -- the same standalone sentence in BOTH trees,
    # and the appendix pointer in the dissertation's section preamble where it can resolve.
    # [2026-08-12] REPOINTED. The probe's PURPOSE is that Ch.5 states the cosine result in wording
    # that stands without holding another document; the SEVEN-dataset scope was the accident of the
    # evidence base. Appendix F was rebuilt on four datasets at the reported configuration, so the
    # sentence now carries that scope and the equivalence verdict rather than a positivity count.
    ("A9-diss",  "2.9: the cosine result is stated in the dissertation's Ch.5, at the scope the "
     "appendix actually measures, in wording that does not depend on holding another document",
     "chapters/5_mobiwac/02_related.tex",
     r"measured on the reported joint model at four datasets, is equivalent to zero at\s+every one of them", True),
    # [round14] A9-ptr REVERSED, and the reversal is the point of the entry. It used to require the
    # gradient-cosine appendix pointer to be PRESENT in this file (round 9 put it in the section
    # preamble so an internal \ref would resolve). The author then ruled that the article bodies of
    # Chapters 3-5 must read as standalone papers and may carry no reference to dissertation
    # structure, which retires the reason the pointer was placed here. The probe now guards the
    # ABSENCE instead of the presence, so a later sweep cannot quietly restore it.
    # The substantive claim is untouched and still guarded by A9-diss above: the seven-dataset
    # result is stated in this chapter in wording that stands without holding another document.
    # The appendix itself stays reachable from the frame: 1_introduction.tex, 2_fundamentals.tex,
    # and 6_conclusion.tex each cite apx:cosine (measured this round, 1 live ref each).
    ("A9-ptr",   "2.9 SUPERSEDED by the round-14 standalone rule: the article body no longer points at "
     "the gradient-cosine appendix, and the frame chapters carry that pointer instead",
     "chapters/5_mobiwac/02_related.tex",
     r"Appendix~\\ref\{apx:cosine\}", False),
    # [2026-09-30] FLIPPED, not retired. Ruling 2.9 kept the development figures; the author re-ruled
    # on 2026-09-30 that the text describes the delivered method, not the journey. The results come
    # from the delivered model, so its measurement is the one cited, because it carries more
    # confidence. The development sentence (+0.001 / +0.0032, "earlier preparation of the data") left
    # Ch.5, and the claim now rests on the reported-model measurement that A9-diss pins. This probe
    # now guards the other direction: the development number must not creep back.
    ("A9-oldnum","2.9 SUPERSEDED 2026-09-30: the development four-seed figures are REMOVED; the "
     "gradient-cosine claim rests on the measurement on the reported joint model (A9-diss)",
     "chapters/5_mobiwac/02_related.tex", r"\+0\.0032", False),
    # ---- REPOINTED 2026-08-02, when the author's revised tree (src_clean) was merged into src.
    # Seven probes went NOT APPLIED after the merge. Each was checked against the SUBSTANCE rather
    # than trusted or deleted, and in every case the claim still holds and the PATTERN was stale:
    #   A11-frame/A11-frame2  he writes the adjective ("non-inferior") where the probe demanded the
    #                         noun ("non-inferiority"). The TOST caveat is in both Resumo and Abstract.
    #   A23-EX9               he kept the Pareto-front sentence he had ruled not to change, in his own
    #                         words; the probe pinned the old phrasing.
    #   R9-pareto/2/3         the Pareto disclaimer, the dominance definition and the optimality
    #                         definition all survive his rewrite, worded differently.
    #   R9-conflict           he did better than the original: gradient conflict now has its own
    #                         subsection defining it as a negative cosine between task gradients.
    #   NUM-4                 THE ONE THAT WAS NOT A WORDING CHANGE. The HGI sweep numbers left
    #                         2_fundamentals entirely -- because he MOVED them to a new appendix,
    #                         chapters/apx_g_hgi_tuning.tex, which renders at p. 106 of the defense
    #                         build. Repointed to that file. Had I repointed by pattern-fiddling
    #                         instead of looking for the number, I would have recorded a lost
    #                         measurement as a wording change.
    # The rule this follows: a probe that fails after a legitimate rewrite is repointed only once the
    # claim has been re-verified in the new text. A probe deleted because it failed is a claim that
    # silently stopped being checked.
    # ---- ROUND-9c, SECOND PASS. These three rows were APPLIED in the ledger on a predicate that did
    # not measure anything: 2.19's ended in `or True`, 2.23's was the literal `True`, and 2.15's asked
    # only whether the word "errata" occurs somewhere. A reviewer caught it. Probed properly now, which
    # is the difference between a verdict and an assertion (_history/_round9/47_applied_check.md, the CORRECTION).
    ("A19-conv", "his 2.19: the word-count convention is a durable record stating the figure of record",
     "WORDCOUNT_CONVENTION.md", r"310", True),
    ("A23-R3",  "his 2.23 R-3: the unscoped limit on what the balancers can contribute is gone",
     "chapters/2_fundamentals.tex", r"limit on what any of these methods can contribute", False),
    ("A23-R6",  "his 2.23 R-6: the cosine appendix is reachable from the body, not one sentence",
     "chapters/6_conclusion.tex", r"apx:cosine", True),
    ("A23-EX6", "his 2.23 EX-6: the hard-sharing-costs-nothing claim is gone from the appendix",
     "chapters/apx_f_cosine.tex", r"hard sharing costs nothing", False),
    # SUPERSEDED 2026-08-02, and this probe was the wrong instrument for the whole time it existed.
    # His 2.23 ruling was "nao aplique o EX-9" -- EX-9 being four sentences: "deserves one statement"
    # (p.23), "worth reporting" (p.99), "needs saying" (p.98), "worth stating" (p.21). This probe
    # watched r"Pareto front" instead, which is still in the chapter and has nothing to do with the
    # four phrasings. So it PASSED while all four left the document: two in his own revised tree
    # (807183c1), two in earlier rounds, per git log -S on each phrase.
    # He was shown the contradiction and ruled that his own read-through supersedes the earlier
    # decision -- he rewrote those sentences with the text in hand, and one of them ("needs saying")
    # is the exact British need+gerund construction he later banned by name in WRITING_LAW.
    # Repointed to what his ruling ACTUALLY protected and what survives: the Pareto-front DEFINITION
    # he declined to cut. The lesson is the same one this file keeps relearning -- a probe must
    # express the claim it guards, or it certifies whatever it happens to match.
    ("A23-EX9", "his 2.23 EX-9 ruling, now SUPERSEDED by his own revision: the Pareto-front "
     "definition he declined to cut is still there (the four 'worth noting'-family phrasings are "
     "not, by his later choice)",
     "chapters/2_fundamentals.tex", r"corresponding loss vectors form the Pareto front", True),
    ("A15-cite", "his 2.15 path A: the substituted citation is present in the dissertation tree",
     "chapters/3_cbic/method.tex", r"baxter2000model", True),
    ("A15-old",  "his 2.15 path A: the unsupported citation is gone from the dissertation tree",
     "chapters/3_cbic/method.tex", r"ruder2017sluice", False),
    ("A15-term", "his 2.15: the banned term is gone from the CoUrb chapter",
     "chapters/4_courb/methodology.tex", r"\bfclass\b", False),
    # ---- ROUND-9 PROBES: the review-tracker split itself. Paths ending .md resolve against UTILS.
    # Each was validated by sabotage (revert the property, read rc=1) -- see _history/_round9/32_gate_validation.md.
    ("R9-schema", "CONSIDERATIONS.md carries all 43 per-item blocks, not prose",
     "CONSIDERATIONS.md", r"### AUT-01", True),
    ("R9-commit", "every item block records the build commit its measurement was taken against",
     "CONSIDERATIONS.md", r"Build commit the measurement was taken against", True),
    ("R9-verbal", "Germano's points are marked as the AUTHOR'S TRANSCRIPTION of verbal comments, "
                  "never attributed to him as written words",
     "CONSIDERATIONS.md", r"transcribed by the author", True),
    ("R9-stale",  "the stale-quote counts are stated as 9 of 41, not the 10 I first wrote",
     "CONSIDERATIONS.md", r"9 de 41 ancoras localizaveis", True),
    ("R9-blocked", "FAB-28 is recorded as BLOCKED on a failed verification, not quietly applied",
     "CONSIDERATIONS.md", r"INADMISSIBLE for any claim", True),
    # REPOINTED 2026-08-03, for the same reason R9-pend28 was repointed on 2026-08-02: the thing it pins
    # left the live tracker. All twenty-six §6 items were answered by the author, so at his request the
    # section was archived and its `## §6` heading removed from PENDENCIAS.md. Pinning the heading in the
    # live file would now fail on his own decision, which is the defect a probe on a withdrawn claim
    # always becomes. What must not rot is the RECORD of the section: that it existed, that it replaced the
    # 2.8 placeholder, and that its items went to the archive rather than vanishing -- three §6-era items
    # were lost in the past by deletion without an arrival check, which is why the archive entry states
    # the heading verbatim. So this reads the ARCHIVE and pins the closure record.
    ("R9-pend6",  "the archive records that PENDENCIAS §6 existed, replaced the 2.8 placeholder, and was "
                  "closed with all twenty-six items archived rather than dropped",
     "_history/_archive/PENDENCIAS_RESOLVIDOS.md",
     r"A SECAO §6 DO `PENDENCIAS\.md` FOI ENCERRADA E REMOVIDA", True),
    # R9-pend6b: and the heading itself, quoted verbatim in the archive, so a later reader can resolve a
    # source comment that still says "§6" without guessing what it named.
    ("R9-pend6b", "the archive quotes the removed §6 heading verbatim",
     "_history/_archive/PENDENCIAS_RESOLVIDOS.md",
     r"## §6 · As decisoes que sairam do `CONSIDERATIONS\.md` \(round 9\)", True),
        # REPOINTED 2026-08-02: item 2.8 was archived out of the tracker, so both probes now read the
    # ARCHIVE. The second also gets a wrap-tolerant pattern: the phrase it pins now wraps across
    # two lines in the archive file, and the original one-line pattern reported the sentence as
    # missing when it is present. A first check of mine split on exactly that wrap and nearly
    # recorded a live sentence as lost.
("R9-pend28", "the archived 2.8 records what was done rather than asking for a decision",
     "_history/_archive/PENDENCIAS_RESOLVIDOS.md",
     r"2\.8 `CONSIDERATIONS\.md` — EXECUTADO nesta rodada", True),
    # ---- ROUND-9, THE PARETO TRACK (PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02), author's decision "DESICAO: A."). The fix has
    # two halves that can rot independently -- the §2.3 passage can be reverted, and the glossary rows
    # it depends on can be dropped -- so it gets a probe on each. Source ledger with the page of every
    # definition, and the sabotage runs: _history/_round9/31_pareto.md.
    ("R9-pareto", "Ch.2 defines Pareto optimality and states that this dissertation does not claim it",
     "chapters/2_fundamentals.tex", r"claims no Pareto property", True),
    # R9-pareto2: the DEFINITION itself, not just the honesty clause. Found 2026-07-30 by sabotage:
    # replacing "a relation named\nPareto dominance" with "domination" left R9-pareto holding, because
    # that probe watches "claims no Pareto property of any kind" -- a different sentence. A term can be
    # struck from the definition while the disclaimer about it survives, and the glossary probe only
    # checks the REGISTRY, not the prose. So the fail-closed rule needs the prose side gated too.
    # ---- APPENDIX F's DATASET COUNTS. The cosine track measured that NOTHING gated them: it widened
    # the appendix from four datasets / 3,900 observations to seven / 4,650, verified every count in the
    # rendered PDF, and reported honestly that the counts rested on that one session's reading and on
    # nothing mechanical. It could not add the probe itself because this file belonged to the parallel
    # track that round. Three probes, so a silent regression to the old counts cannot pass:
    # [2026-08-12] REPOINTED. The three probes below pinned Appendix F to the count of datasets and
    # observations in its evidence base. That base was re-measured under the reported joint
    # configuration, so the counts changed (four datasets, 1,000 observations) while each probe's
    # PURPOSE is unchanged: the appendix must state its coverage and its row count, and must not
    # claim coverage it does not have. R9-apxfold inverts accordingly: what must now be absent is
    # the larger claim, not the smaller one.
    ("R9-apxf7",  "Appendix F states its coverage as the four datasets it measures",
     "chapters/apx_f_cosine.tex", r"four datasets", True),
    ("R9-apxfn",  "Appendix F reports 1,000 epoch-level cosines, the measured row count",
     "chapters/apx_f_cosine.tex", r"1,000 epoch-level cosines", True),
    ("R9-apxfold", "Appendix F no longer claims seven datasets or the superseded row count (inverted)",
     "chapters/apx_f_cosine.tex", r"seven datasets|4,650", False),
    ("R9-pareto2", "Ch.2 still DEFINES Pareto dominance in prose, not only disclaims Pareto claims",
     "chapters/2_fundamentals.tex", r"Pareto dominance", True),
    ("R9-pareto3", "Ch.2 still defines Pareto optimality from dominance",
     "chapters/2_fundamentals.tex", r"Pareto optimal when no other setting dominates", True),
    ("R9-conflict", "Ch.2 defines gradient conflict as the cosine between per-task gradients, so "
                    "Appendix F's orthogonality result has a definition to point back to",
     "chapters/2_fundamentals.tex", r"cosine between their gradients", True),
    # INVERTED, and the inversion is the point (GUARDRAILS V15: a fix whose correctness is an ABSENCE
    # needs an expect-not-found probe). Appendix F's dataset coverage was being extended by a parallel
    # track while this passage was written, so the passage cites it by \ref and says "the datasets
    # measured there", never a count. If a later editor writes a count into the cosine sentence, that
    # number acquires a second home and the two disagree the next time one moves -- V6, a corrected
    # number surviving at a second site.
    #
    # THE FIRST VERSION OF THIS PROBE WAS WRONG, AND IT FIRED, WHICH IS HOW I FOUND OUT. It banned
    # /(four|six)\s+datasets/ anywhere in the chapter and matched line 892, "on the next region at four
    # of six datasets" -- the §2.5 headline result, which is the protected region-wording law
    # (WRITING_LAW §3: outperforms at four, matches at the other two) and must NOT be touched. A ban on
    # a bare phrase cannot tell one claim from another, so the pattern is anchored on the SENTENCE this
    # probe is actually about: the cosine clause, whose subject is Appendix F's coverage. The prose was
    # correct and the instrument was not, which is the reverse of the usual case and the reason the
    # rule is to validate an instrument before believing it (§4b V3).
    # Kept INVERTED so it stays a true expect-not-found, and anchored so only the cosine sentence can
    # trip it: the ban is a count in the clause that follows "indistinguishable from orthogonal on".
    # Written as an alternation of the number words that could plausibly land there (a bare digit too),
    # which is narrower than banning the phrase chapter-wide and wider than banning today's value.
    ("R9-nocount", "the Ch.2 cosine sentence cites Appendix F's coverage by reference, not by count",
     "chapters/2_fundamentals.tex",
     r"indistinguishable from orthogonal on (?:all )?(?:one|two|three|four|five|six|\d+)\b", False),
    # The registry half. The prose above may not exist without these rows (GLOSSARY.md is fail-closed,
    # and this term was in prose UNREGISTERED at five sites for two rounds, which is the breach
    # PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) records). A .md path resolves against UTILS, and GLOSSARY.md is a level above it,
    # hence the "../" -- probe_root joins, it does not restrict.
    ("R9-glossary", "the four Pareto/conflict terms are registered before the prose uses them",
     "../GLOSSARY.md", r"\*\*Pareto-stationary point\*\*", True),
    # ---- R9-agree / R9-agree2: THE TWO TRACKERS CONTRADICTED EACH OTHER FOR TWO COMMITS and twenty
    # green gates said nothing, because every probe here checks ONE file against ITSELF. PENDENCIAS
    # §2.8 was generated from a Python variable whose reassignment cell had aborted on an
    # AssertionError, so it silently kept the pre-correction figures (ten stale, "todas citam
    # 0_main.tex", 21 exact) while §6 of the SAME FILE and all of CONSIDERATIONS.md carried the
    # corrected nine. The assertion that fired was protecting the OTHER file; nothing was watching
    # whether the two agreed. A number with two homes disagrees the next time one of them moves
    # (GUARDRAILS §4b V6), and here the second home was three screens down in the same document.
    # Positive probe pins the corrected figure; the inverted one bans the superseded claim. The
    # corrected count is ALSO pinned in CONSIDERATIONS.md by R9-stale, so the two files can only pass
    # together.
    ("R9-agree",  "the archived 2.8 carries the CORRECTED stale count, agreeing with its own §6 and "
                  "with CONSIDERATIONS.md (9 of 41, not the superseded 10)",
     "_history/_archive/PENDENCIAS_RESOLVIDOS.md",
     r"\*\*32 sao exatas e 9 estao\s+obsoletas\*\*", True),
    ("R9-agree2", "the superseded 'As 21 ancoras dos capitulos' claim is gone from PENDENCIAS",
     "PENDENCIAS.md", r"As 21 ancoras dos capitulos", False),
    # ---- R9-confirm: FAB-01 CHANGED NOTHING, and it was still counted as an applied-and-verified
    # edit. The Wave A loop wrote the standard note -- "verified in the RENDERED PDF, both
    # directions: new wording present and old wording absent" -- onto every member of the wave,
    # including the one whose request was ALREADY satisfied before this round started. For a no-op
    # there is no superseded wording, so the absent half of that claim cannot be measured, and
    # asserting it is a claim about a measurement that never ran. Same V13 shape as the stale-anchor
    # miscount earlier this round: a headline count that stopped agreeing with its own members.
    # The probe pins the carve-out, so the note cannot be re-applied to a no-op by a later sweep.
    ("R9-confirm", "FAB-01 is recorded as already satisfied and only CONFIRMED, never as an applied "
                   "edit verified in both directions",
     "CONSIDERATIONS.md", r"ALREADY SATISFIED; CONFIRMED IN THE RENDERED PDF, NOT APPLIED", True),
    # ---- R9-clock: the reviewer round's own process claim. The four personas were given a 25-minute
    # (1,500 s) wall-clock checkpoint BECAUSE the previous round overran (45 min -> 60, 90 -> 219),
    # and the gate report first said all four came back inside it. All four missed it: 1,598 / 1,618 /
    # 1,971 / 2,314 s, the worst 54% over. The wall times were in the results the findings were read
    # from. Reporting compliance would have retired a control on a number nobody looked at, and the
    # next round would have inherited a checkpoint believed to work. Positive probe pins the worst
    # measured time (the figure a later summary is most likely to soften); the inverted one bans the
    # superseded sentence. .md paths resolve against UTILS, so _history/_round9/ is reachable from here.
    ("R9-clock",   "the reviewer round records that every persona OVERRAN the 25-minute checkpoint, "
                   "with the measured wall times",
     "_history/_round9/37_reviewer_gate_round9.md", r"2,314 s \(38\.6 min\)", True),
    # R9-clock2 IS ANCHORED, and the first version was not, which is why it fired on a clean file.
    # The banned string is quoted inside the correction that retires it ("The first version of this
    # paragraph said \"all four came back inside it\""), and PROBES match case-insensitively, so a bare
    # ban on the phrase cannot tell the retired ASSERTION from the record of retiring it. Same lesson
    # as R9-nocount's first version, which banned a bare phrase and matched the protected region
    # wording. The pattern therefore requires the sentence-initial capitalized form followed by the
    # clause that made it an assertion -- the shape only the original can have. Keeping the quotation
    # legal is the point: a correction that cannot name what it corrects is not a correction.
    ("R9-clock2",  "the superseded 'All four came back inside it' ASSERTION is gone from the gate "
                   "report (the quotation of it inside the correction stays legal)",
     "_history/_round9/37_reviewer_gate_round9.md", r"All four came back inside it, and \*\*all four", False),
    # ---- R9-wave2: wave 2's checkpoint outcome, and the reason it needs a probe is that the LAST
    # wave's outcome was reported wrong and then its diagnosis was reported wrong too. Wave 1: 0 of 4
    # inside a 25-min budget, mean 31.3 min, which I first wrote as "all four came back inside it"
    # (R9-clock). The correction ended with a prescription -- narrow the scope, not the clock -- and
    # wave 2 acted on it: narrowed scopes, 30-min budget, and the result was 1 of 5 inside, mean 41.1
    # min. The mean got WORSE. A summary of this round is likeliest to round both waves off to "the
    # personas ran and reported", so the probe pins the number that makes the failure legible: 1 of 5.
    #
    # THIS PROBE'S FIRST PATTERN WAS WRONG AND IT FIRED ON A CLEAN FILE, which is the third time this
    # round an instrument was the defect rather than the document (after R9-clock2 and R9-nocount). I
    # wrote it against a markdown table row -- r"\*\*1 of 5\*\* \| \*\*41\.1 min\*\*" -- that lives in
    # _history/_round9/34, not in 38; the wave-2 report states the same measurement in prose. A pattern written
    # from memory of a sibling file is not a measurement of this one. Anchored now on the prose 38
    # actually carries.
    ("R9-wave2",   "the wave-2 record states that only ONE of five personas came in under the "
                   "checkpoint, with the measured mean",
     "_history/_round9/38_reviewer_wave2_round9.md", r"one of five inside, mean 41\.1 minutes", True),
    # The blocker that wave 2 found, pinned in the tracker rather than only in a report: Appendix F
    # tells the reader an experiment happened (replacing the sharing scheme in study 1) that Chapter 3
    # lists as future work. Re-verified in three places before it was written down. Inverted probes
    # would be wrong here -- the prose is the AUTHOR'S to change, so what gets gated is that the item
    # stays on his decision list until he rules on it, not that the sentence is already gone.
    ("R9-blq4",    "the Appendix F never-run-experiment blocker is on the author's decision list",
     # REPOINTED 2026-08-03: §6 was archived at the author's request once all twenty-six items were
     # answered, so the block this pins now lives in the archive. VERIFIED PRESENT THERE before the
     # repoint (grep: 1 in the archive, 0 in the live tracker) rather than assumed to have travelled.
     "_history/_archive/PENDENCIAS_RESOLVIDOS.md",
     r"BLQ-4 — o Apendice F descreve um experimento que nunca foi feito", True),
    ("R9-blq5",    "the PCGrad blocker is recorded as DOWNGRADED BY ME, with the half I could not "
                   "check named, rather than passed through at the persona's severity",
     # REPOINTED 2026-08-03 with R9-blq4, same reason, same arrival check.
     "_history/_archive/PENDENCIAS_RESOLVIDOS.md", r"eu o REBAIXEI; a decisao final e sua", True),
    # ---- ROUND-10 PROBES: the author's 28 rulings, applied 2026-08-03 against baseline dda8978e.
    # R10-blq2 is the one that would rot silently. His ruling was to keep "everywhere" for the CATEGORY
    # verdict and specify the partition where the REGION verdict needs it. Chapter 6 was already right;
    # ONE site survived in the introduction, and a line-oriented grep could not see it because the
    # sentence wraps across three source lines -- only the comment-stripped, whitespace-collapsed
    # concatenation found it. Any future rewrite of that bullet is likely to re-collapse the partition
    # into "outperforms or matches", which is the exact phrase the conclusion's own comment at :131 and
    # 5_mobiwac/06_results.tex:76 record as a defect. So: pin the partition positively AND ban the
    # collapsed form in that file. The ban is file-scoped on purpose -- the phrase is legal in comments
    # elsewhere, where it names the defect rather than committing it.
    # [2026-08-12] REPOINTED to the final ladder. The probe's PURPOSE is unchanged: the bullet must
    # state the region partition rather than collapse it. What changed is the partition itself --
    # the region axis now outperforms at Texas and California and stays within the registered
    # two-point margin at the other four, so the old string is not merely stale, it asserts a
    # verdict the tests no longer support. The positive pin follows the readable surface registered
    # in GLOSSARY (WRITING_LAW section 3), which is the phrase the prose is required to repeat.
    ("R10-blq2",   "the introduction's practical-contribution bullet states the region partition "
                   "(outperforms at TX/CA, within the registered margin elsewhere) instead of "
                   "collapsing it",
     "chapters/1_introduction.tex",
     r"within the two-point margin", True),
    ("R10-blq2b",  "the superseded collapsed wording is gone from the introduction's live prose",
     "chapters/1_introduction.tex", r"either outperforms or\s+matches it on next region", False),
    # R10-blq3: the two prose-derived ratios are gone and must not come back. The endpoint counts stay
    # (each traceable to the appendix's own table), so the positive half of this pair guards against a
    # well-meaning editor "restoring the span" by recomputing it in prose again -- which is how it got
    # there. N2/N3: quote, never compute.
    ("R10-blq3",   "the prose-derived scale ratios are gone from Appendix F, endpoint counts kept",
     "chapters/apx_f_cosine.tex", r"factor of thirty-six", False),
    # [2026-08-12] REPOINTED with R9-apxf7. The endpoint counts named Alabama and Texas as the ends
    # of the measured range; Texas is not in the re-measured set, so the appendix now spans the
    # region counts of the four datasets it has. The probe still requires the span to be stated.
    ("R10-blq3b",  "Appendix F states the endpoint span of the datasets it actually measures",
     "chapters/apx_f_cosine.tex", r"520 at Istanbul to 4,703 at\s+Florida", True),
    # R10-fab22: Istanbul's PURPOSE, not just its name. The author's point was that a reader who sees
    # only "and Istanbul" reads a sixth dataset rather than evidence about generalization. The claim the
    # sentence makes is about scope, so the scope has to be stated.
    ("R10-fab22",  "the introduction says WHY Istanbul is there (a non-United-States dataset), not "
                   "merely that it is there",
     # Re-pinned 2026-10-05 (D8b, author: one form, "non-U.S.", across the document).
     "chapters/1_introduction.tex", r"Istanbul as a non-U\.S\. dataset", True),
    # R10-ch2defs: GER-08/09/10. The chapter must keep numbered, REFERENCEABLE definitions -- the
    # environment declaration in preamble.tex is what makes them numbered, and the cross-references are
    # what make the chapter GER-10's narrative rather than a definition dump. Two probes because the
    # two halves fail independently: someone could keep the blocks and drop the references.
    ("R10-defenv", "Chapter 2 declares a chapter-numbered definition environment",
     "../src/preamble.tex", r"\\newtheorem\{definition\}\{Definition\}\[chapter\]", True),
    ("R10-cosine", "gradient conflict is DEFINED with the cosine in Chapter 2, not only named",
     "chapters/2_fundamentals.tex", r"def:fund:conflict", True),
    # R10-hamtl: FAB-28, the round-9 blocker. The novelty sentence SURVIVED the PDF (HAMTL calls its
    # category head auxiliary, names no region-like unit in 28 pages, reports no category metric), so
    # what needs guarding is that nobody later "narrows it to be safe" without reading the paper, and
    # that our description keeps the authors' own main/auxiliary framing (GUARDRAILS R2).
    ("R10-novelty", "the co-equal-end-targets claim still stands, having survived the HAMTL PDF",
     "chapters/2_fundamentals.tex",
     r"none treats next category and next region as", True),
    ("R10-hamtl",  "HAMTL is described as its own authors describe it: location prediction main, "
                   "category auxiliary",
     "chapters/2_fundamentals.tex",
     r"HAMTL sets location\s+prediction as its main task and category prediction as an auxiliary task",
     True),
    # ---- R10-pm: the postmortem's own causal account, which was FABRICATED on its first writing and is
    # therefore the one claim in this repo with a demonstrated tendency to drift back toward plausibility.
    # History: the round-10 harness reported working probes as failing. That much was diagnosed correctly.
    # Then, asked what broke, I wrote three mechanisms -- an IFS=':' split on "a Portuguese sentence
    # containing a colon", a helper that restored before reading stdout, and a stale module import -- and
    # THREE OF THE FOUR CLAIMS WERE INVENTED. No leg carried Portuguese; no helper version restored early;
    # every module load post-dated the edit. The real cause is ONE mechanism, isolated by reproduction:
    # str.replace(old, new, 1) against a string occurring twice where the FIRST occurrence sits inside a
    # % comment, which live_text() strips -- so the live text stays intact and the probe correctly holds.
    # Verified for both affected legs: def:fund:conflict occurs twice in 2_fundamentals.tex, and
    # \newtheorem{definition}{Definition}[chapter] occurs twice in preamble.tex (line 99 in a comment,
    # line 117 live). The positive probe pins the single-mechanism finding; the inverted one bans the
    # invented detail from being ASSERTED again. The ban is anchored so the RETRACTION may keep quoting
    # it -- same construction as R9-clock2, for the same reason: a correction that cannot name what it
    # corrects is not a correction.
    ("R10-pm",     "the round-10 postmortem records ONE harness mechanism, isolated by reproduction, "
                   "not the three it first invented",
     "_history/_round9/34_tracker_disagreement.md", r"There was \*\*ONE\*\* harness bug", True),
    ("R10-pm2",    "the fabricated three-mechanism account is not ASSERTED anywhere (quoting it inside "
                   "the retraction stays legal)",
     "_history/_round9/34_tracker_disagreement.md",
     r"harness was broken, in three separate ways", False),
    ("R10-pm3",    "the postmortem states the run's REAL leg counts rather than the three-of-six it "
                   "first claimed",
     "_history/_round9/34_tracker_disagreement.md",
     r"\*\*one\*\* `DID NOT FIRE`, \*\*two\*\* `mutation failed`", True),
    # ---- ROUND-11 PROBES: the five items the author authorized on 2026-08-03, after suspending the
    # Chapter 2 page budget ("pode melhorar o texto da fundamentacao sem preocupacao de paginas").
    #
    # R11-aligned is the one that earns its keep. The Aligned-MTL sentence said the method "adjusts the
    # PRINCIPAL components of the gradient system". The paper says it aligns the ORTHOGONAL components
    # (arXiv:2305.19000v1 abstract) and its stated criterion is the condition number of the linear system
    # of gradients. "Principal" invites a PCA reading the authors never claim, so this was an R2 defect
    # (describe a system as its own authors describe it), and it survived a sub-agent's own verification
    # pass plus a round-10 commit. It was caught only when the four lineage attributions that had never
    # been checked by anyone but their writer were finally checked. A summariser rewording this sentence
    # is exactly how "principal" comes back, so both halves are pinned: the authors' word positively,
    # the wrong word banned.
    ("R11-aligned", "Aligned-MTL is described with its authors' own word, ORTHOGONAL components, and "
                    "its stated condition-number criterion",
     "chapters/2_fundamentals.tex",
     r"condition number of the linear\s+system of task gradients", True),
    ("R11-aligned2","the superseded 'principal components of the gradient system' gloss is gone from "
                    "the live prose (the comment recording the correction may keep quoting it)",
     "chapters/2_fundamentals.tex", r"adjusts the principal components of the\s+gradient system", False),
    # R11-def27: the merge that round 10 made PURELY to save one page is undone, on the author's
    # authorization. The two cross-references point at opposite halves, so a re-merge silently breaks
    # both. Pin the second label's existence: it only exists because the split happened.
    ("R11-def27",  "Definition 2.7 is split, so each cross-reference can point at the concept it means",
     "chapters/2_fundamentals.tex", r"\\label\{def:fund:checkinlevel\}", True),
    # R11-hgi: GER-02's second half. HGI is the place-level baseline the whole argument turns on, and the
    # honest caveat is the part most likely to be trimmed by a later editor tightening prose: HGI was
    # built and evaluated for urban REGION representation, and this dissertation repurposes its POI-level
    # output for sequential prediction, which its original evaluation does not cover.
    ("R11-hgi",    "the HGI explanation keeps the honest caveat that this project repurposes a POI-level "
                   "output the original evaluation does not cover",
     "chapters/2_fundamentals.tex",
     r"repurposes that POI-level output for sequential prediction, a use the\s+original evaluation does not cover",
     True),
    # R11-fab15: the taxonomy must not read as part of the task DEFINITION in the introduction (the
    # author: the approach is generic and not fixed on this taxonomy), while the concrete instantiations
    # survive ONCE so an introduction-only reader keeps the context. Both halves, since either can drift.
    ("R11-fab15",  "the introduction states the targets plainly, with the label sets as properties of "
                   "the data rather than part of the definition",
     "chapters/1_introduction.tex",
     r"The prediction targets are the next category and the next region\.", True),
    ("R11-fab15b", "the definitional framing of the taxonomy is gone from the introduction",
     "chapters/1_introduction.tex", r"over the\s+seven-class taxonomy defined in Chapter", False),
    # R11-gloss: the two rows the author authorized. They were already in live prose while unregistered,
    # so the fail-closed rule was being stretched; these rows close it.
    ("R11-gloss",  "the two authorized registry rows are present (soft parameter sharing)",
     "../GLOSSARY.md", r"\| soft parameter sharing \| compartilhamento flex", True),
    ("R11-gloss2", "the second authorized registry row is present (negative transfer)",
     "../GLOSSARY.md", r"\| negative transfer \| transfer", True),

    # ---- ROUND-12 PROBES: the liu2019dwa [VERIFY] closed on 2026-08-03 against the PDF the author
    # put on disk (science/articles/1803.10704v2.pdf, arXiv:1803.10704v2). Three things were read in
    # the BODY, and all three are pinned here because each has its own way of drifting back:
    #   the NAME. The clause said "dynamic weight averaging". The authors' own name is "Dynamic
    #     Weight Average (DWA)" (p.2, end of Sec. 1; heading of Sec. 4.1.3, p.5). An R2 defect of
    #     the same class as R11-aligned, and the likeliest thing for a later editor to "normalize"
    #     back to the participle, since the CBIC chapter legitimately carries "Averaging" as its
    #     published wording. Both halves pinned: the paper's name positively, the gloss banned.
    #   the WORD "ALONGSIDE", which is what kept the sentence defensible while it was unverified and
    #     which the body confirms rather than overturns: DWA is introduced in the experimental
    #     section as one of three weighting schemes and is run on the Split, Dense and Cross-Stitch
    #     baselines as well as on MTAN (Tables 2-3, pp. 6-7), so it is separable from the
    #     architecture. Anyone tightening this clause to a bare "introduce DWA" would assert a
    #     packaged contribution the paper does not present, so the collocation is pinned whole.
    #   the DEFINITION. Eq. 7 and its text (p.5) set w_k(t-1) = L_k(t-1)/L_k(t-2) over epoch-average
    #     losses, which is narrower than the earlier "recent changes in the task losses".
    ("R12-dwa",    "DWA carries its authors' own name and stays SEPARABLE from MTAN "
                   "(the 'alongside' the closed [VERIFY] was protecting)",
     "chapters/2_fundamentals.tex",
     r"Dynamic Weight Average alongside their attention\s+architecture", True),
    ("R12-dwa2",   "the superseded 'dynamic weight averaging' gloss is gone from the live prose "
                   "(comments recording the correction may keep quoting it)",
     "chapters/2_fundamentals.tex", r"dynamic weight averaging", False),
    ("R12-dwa3",   "the DWA weight is described as the paper defines it, from the loss rate of "
                   "change measured as the ratio of the two previous loss values",
     "chapters/2_fundamentals.tex",
     r"rate of change of that task's loss,\s*measured as the ratio of its two previous loss values",
     True),
    # ---- TWO DEFECTS THE AUTHOR FOUND IN THE DEFINITION BLOCKS, 2026-08-03. Both are formalization
    # gaps rather than wrong statements, and both sit at the chapter's load-bearing points, which is
    # why they are gated: a later editor tightening prose has every incentive to drop a symbol or
    # collapse a one-line equation back into a sentence.
    #
    # (1) Definition 2.8 named NO symbol while Definition 2.7 gave the place-level vector as
    #     \mathbf{e}_p. The place-versus-check-in contrast is the pivot of the entire dissertation, and
    #     only one side of it could be written down. GLOSSARY §1.1 had already implied the gap: its
    #     \mathbf{e}_p row reads "distinct from a per-visit Check2HGI vector" and gives that vector no
    #     symbol. \mathbf{e}_{x_i} was verified free across the whole live tree before being used.
    ("R12-eqxi",   "Definition 2.8 names the check-in-level vector, so both sides of the chapter's "
                   "central contrast have a symbol",
     "chapters/2_fundamentals.tex",
     r"assigns one vector \$\\mathbf\{e\}_\{x_i\}\$ to each check-in", True),
    # (2) Definition 2.6 was the only task definition stated in prose alone: 2.3, 2.4 and 2.5 each give
    #     a function (g_cat(e_p) -> c_p, f_cat(H_i) -> c_i, f_reg(H_i) -> r_i) and next place did not.
    #     That made the excluded task look like a different KIND of object at exactly the point where
    #     the chapter's job is keeping the three formally distinct. Naming f_place SHARPENS the scope
    #     statement: the exclusion now applies to a defined mapping. Both halves pinned, because the
    #     equation and the exclusion can drift independently and the pair is what carries the meaning.
    ("R12-fplace", "next-place prediction is stated as a function like its three neighbors, not in "
                   "prose alone",
     "chapters/2_fundamentals.tex", r"f_\{\\mathrm\{place\}\}\(H_i\)\\longrightarrow p_i", True),
    ("R12-fplace2","and the scope exclusion survives beside it, so naming the function does not read "
                   "as claiming the task",
     "chapters/2_fundamentals.tex",
     r"no chapter reports a result\s*for \$f_\{\\mathrm\{place\}\}\$", True),
    # ---- ROUND-12, the author's rulings of 2026-08-03 on the definition redesign. These pin RECORDS,
    # not chapter prose, because the redesign is not applied yet and the records are what a later pass
    # reads. Each one is a claim that has already drifted once or could plausibly be softened by a
    # summarizer, which is the test for whether a probe earns its place.
    #
    # R12-thirteen: he ruled THIRTEEN definitions ("Vamos de treze"), so rho becomes a numbered
    # Definition. The twelve-definition fallback stays in the design as the record of the alternative,
    # which is exactly the condition under which a later reader could mistake the dead option for the
    # live one. Pin the ruling.
    ("R12-thirteen","the definition design records THIRTEEN as the author's settled choice, not an open "
                    "twelve-or-thirteen question",
     "../science/fundamentals/DEFINITIONS.md", r"RESOLVED 2026-08-03: THIRTEEN", True),
    # R12-streams: he confirmed F-1 and gave the mechanism -- two final embeddings of one trained graph,
    # feeding next-region and next-category respectively. The single-equation wording would misstate the
    # input of the study the whole arc resolves on, so both halves are pinned: the ruling, and the
    # two-stream statement itself.
    ("R12-streams", "Chapter 5's input is recorded as TWO elementwise streams, per his own mechanism",
     "../science/fundamentals/DEFINITIONS.md", r"RESOLVED 2026-08-03: NAME BOTH STREAMS", True),
    # R12-notagg: THE CODE FINDING, and the one most likely to be quietly reversed. His premise was that
    # Chapter 4's temporal channel is aggregated to POI level. The pipeline does the opposite: the
    # category-task builder REJECTS check-in-level engines (src/data/inputs/builders.py:191-192) and no
    # aggregation exists anywhere in it. A later pass that writes "aggregated to the place" into Chapter 2
    # would be writing the one claim the code refutes, so the investigation's negative finding is pinned
    # positively and the refuted phrasing is banned from the record.
    ("R12-notagg",  "the investigation records that NO check-in-to-POI aggregation exists in the Time2Vec "
                    "pipeline, so Chapter 2 may not claim one",
     "_history/_round12/50_courb_temporal_level_investigation.md",
     r"There is no aggregation function anywhere in the\s+Time2Vec pipeline", True),
    # R12-notagg2 WAS BROKEN ON ITS FIRST WRITING, and the defect is worth recording because it is the
    # third time in this repo that a probe's SABOTAGE LEG, not the probe, decided whether it looked
    # covered. The pattern was r"^The temporal channel is aggregated to the place" -- and this gate
    # matches with re.I ONLY, never re.MULTILINE, so `^` anchors at STRING START and nowhere else. The
    # ban therefore covered exactly one position in a 5 KB file. My sabotage leg inserted the sentence
    # as the file's first line, i.e. at the single position the pattern could reach, so it FIRED and I
    # reported the ban as covering the record. Reproduced after the fact: the same sentence placed
    # mid-document did not match.
    #
    # THE FIX cannot be an unanchored bare-phrase ban, because the record legitimately QUOTES the
    # refuted wording once, in "And I cannot write that the temporal channel is aggregated to the
    # place" -- the sentence whose whole job is to refute it. Same constraint as R9-clock2: a correction
    # that cannot name what it corrects is not a correction. So the ban keys on the ASSERTION FORM at a
    # sentence boundary ANYWHERE in the file (string start, after a sentence-final punctuation, or after
    # a newline, with optional markdown emphasis), which is position-independent without also banning
    # the quotation. Validated at five positions the old pattern could not reach plus two that must stay
    # legal; the legs below sabotage MID-document, not at the top.
    #
    # SECOND MISS, caught by the legs and not by my reasoning, and it is the same lesson one level down:
    # my first corrected pattern passed a hand-built test on RAW text and then went SILENT on a real
    # sabotage leg that put the assertion in a bold run. Cause: the gate matches live_text(), whose
    # strip_text() collapses newlines to spaces, so the text preceding a bolded line arrives as
    # "...reduction.** **The temporal channel..." -- a period followed by ASTERISKS, which my
    # [.!?]['\")\]]* class did not admit. A pattern must be tested THROUGH the gate's own normalizer,
    # never against the raw file. The lead-in now admits emphasis markers and list bullets, and the
    # pattern is validated over ten positions including two that must stay legal.
    ("R12-notagg2", "the investigation does not ASSERT the aggregation it was sent to look for, at any "
                    "position in the file (quoting the refuted wording inside the refutation stays legal)",
     "_history/_round12/50_courb_temporal_level_investigation.md",
     r"(?:\A|[.!?][*_'\")\]]*\s|\n)\s*(?:[-*+]\s+|\d+\.\s+)?(?:\*\*|__|\*)?\s*"
     r"The temporal channel is aggregated to the place", False),
    # ---- The two claims from his 2026-08-03 side-chat rulings that a later pass is most likely to
    # flatten, and both would cause real damage if flattened.
    #
    # R12-ad4cond: AD-4's title is a CONDITIONAL answer. His words: "maybe with this inversion we even
    # need this new section." If the 2.1/2.2 inversion happens, the representation definitions are
    # already in the right section and the subsubsection has no function. A summariser reading "AD-4
    # resolved: Check-in and place representation" would create the subsection, which is precisely what
    # he did NOT authorize. Pin the conditionality, not just the title.
    ("R12-ad4cond", "AD-4's title is recorded as CONDITIONAL, because the section inversion may remove "
                    "the need for the subsubsection at all",
     # PATTERN REPOINTED 2026-08-03: it was "RESOLVED CONDITIONALLY 2026-08-03", a string that vanished
     # when he revoked `place representation` and the AD-4 row had to be rewritten. The CLAIM is
     # unchanged -- AD-4 is conditional and its subsection must not be created -- so the probe is
     # repointed rather than retired, and it now pins the two halves that matter: that the item is
     # conditional, and that nothing is created either way.
     "../science/fundamentals/DEFINITIONS.md",
     r"AD-4 was always conditional.*?Nothing is created either way", True),
    # R12-planvoid: the eight-step edit plan assumes the representation definitions move UP into 2.1.
    # Under the inversion that assumption is void and the plan must be REDONE BEFORE any edit. Getting
    # this wrong means editing the chapter against a plan written for a different structure, which is
    # the most expensive mistake available here. Pinned in the design doc, whose §11 carries the cost
    # table.
    ("R12-planvoid","the record states that the eight-step plan does NOT survive the section inversion "
                    "and must be redone before any edit",
     "../science/fundamentals/DEFINITIONS.md",
     r"must be redone BEFORE any edit, not after", True),
    # ---- AD-2 ANSWERED from the original CoUrb code (temp/tarik-new), 2026-08-03. Three probes, because
    # this finding has three distinct ways of being flattened by a later pass and each would mislead
    # differently.
    #
    # R12-dropdup: the OPERATIVE WORD. The reduction is drop_duplicates -- it SELECTS one visit per POI
    # and discards the rest. "Aggregation" (mean, pooling) is the word everyone reached for, including me
    # and the author, and it is wrong: aggregation would combine the visits. A record saying "aggregated"
    # would misdescribe what ran. Pin the file path and line, so the claim stays checkable.
    # DESCRIPTION CORRECTED 2026-08-03: this said "the AD-2 answer". There is no AD-2 answer -- it was
    # retracted. The probe still earns its place because the dedup's LOCATION is an established fact and the
    # record must keep citing it checkably; what it does NOT license is the conclusion drawn from it.
    ("R12-dropdup", "the record cites the placeid dedup at its source line, as an established fact and not "
                    "as evidence of a check-in-to-POI selection step",
     "_history/_round12/50_courb_temporal_level_investigation.md",
     r"create_inputs_hgi\.py:437", True),
    # R12-shape: the EVIDENCE, and it is the strongest kind available here -- a stored notebook output
    # shape rather than a reading of code intent. 2535573 rows against 2535573 check-ins settles the
    # granularity numerically. If this number goes, the finding reverts to an argument about intent.
    ("R12-shape",  "and it carries the stored output shape that establishes the ENCODER's per-check-in "
                   "granularity numerically (which survives the retraction; what did not survive is that "
                   "this matrix is what the ETL consumes)",
     "_history/_round12/50_courb_temporal_level_investigation.md",
     r"\(2535573, 64\)", True),
    # R12-notwrong WAS REPLACED, 2026-08-03. It pinned "description, not a wrong number" -- the calibration
    # of a conclusion that has since been RETRACTED, so the probe was enforcing a withdrawn claim and went
    # correctly red when the record was corrected. A probe on a retracted conclusion is worse than no probe:
    # it fights the correction. What earns a probe now is the RETRACTION, because the tempting error for a
    # later pass is to re-derive the same conclusion from the same two facts and skip the link again.
    ("R12-retract", "the AD-2 investigation records that its own 'answered' conclusion was RETRACTED, and "
                    "why: the ETL reads a parquet nothing in that repository writes",
     "_history/_round12/50_courb_temporal_level_investigation.md",
     r"RETRACTED AND REOPENED", True),
    ("R12-retract2","and it does not assert that AD-2 is answered",
     "_history/_round12/50_courb_temporal_level_investigation.md",
     r"(?:\A|[.!?][*_'\")\]]*\s|\n)\s*(?:[-*+]\s+|\d+\.\s+)?(?:\*\*|__|\*)?\s*"
     r"AD-2 is (?:therefore )?(?:now )?answered", False),
    ("R12-verify",  "and it carries the VERIFY flag naming the one artifact that would close AD-2",
     "_history/_round12/50_courb_temporal_level_investigation.md",
     r"\[VERIFY: the granularity of time_embedding\.parquet", True),
    # ---- His closing rulings of 2026-08-03. Two probes on the LEFT_OUT entry, because that entry is now the
    # DURABLE home of a finding whose earlier version I had to retract, and the two ways it can rot are the
    # two ways the retraction can be undone.
    #
    # R12-lo12cond: the visits-per-POI table in LO-12 quantifies a HYPOTHETICAL -- what the dedup would
    # discard IF the input were per-visit. It is not evidence of granularity. A later reader finding real
    # numbers in a register entry will be tempted to read them as the finding; the sentence that forbids that
    # reading is the load-bearing part of the entry, not the table.
    ("R12-lo12cond","LO-12 states that its visits-per-POI table quantifies a hypothetical rather than an "
                    "established fact",
     "LEFT_OUT.md", r"This quantifies a hypothetical, not a fact", True),
    # R12-lo12clue: the CBIC errata line about the category task's sample unit is ADJACENT and NOT decisive
    # (different study, different encoder, and consistent with both hypotheses). It is exactly the shape of
    # the unverified link that produced the retraction, so the entry names it AND names why it does not
    # settle anything. Losing that qualification would hand a later pass a ready-made false proof.
    ("R12-lo12clue","and it records the adjacent CBIC errata clue as NOT deciding the question",
     "LEFT_OUT.md", r"One adjacent clue that does NOT decide it", True),
    # R12-ad2row: the AD-2 row in the DESIGN document. This exists because the retracted framing SURVIVED
    # in that row for a full commit. MECHANISM CORRECTED 2026-08-03 -- this comment first blamed a stale byte
    # offset whose .replace() matched nothing, which was a mechanism I supplied from memory rather than read
    # off the cells. What actually happened: the .replace() SUCCEEDED in memory, but the same cell hit an
    # `assert` (computed for a different edit) that RAISED before its write_text, so nothing was written at
    # all; a later cell re-read the file from disk and discarded the corrected string. The "verified" print
    # reported the new text as present because I had checked for a substring the new text contains -- a
    # presence check on the replacement is not a check that the replacement happened. The distinction matters
    # for the rule: re-reading before computing offsets would NOT have prevented this, whereas asserting the
    # OLD string is ABSENT would. Full account in _history/_round9/34_tracker_disagreement.md. Ban the retracted
    # framing by its two most quotable phrases, positioned anywhere.
    ("R12-ad2row",  "the design's AD-2 row does not carry the retracted 'fourth possibility' framing",
     "../science/fundamentals/DEFINITIONS.md", r"FOURTH possibility none of us had listed", False),
    ("R12-ad2row2", "nor the retracted claim that the first visit survives and the rest are discarded",
     "../science/fundamentals/DEFINITIONS.md",
     r"keeping the first visit to each POI and discarding the rest", False),
    # R12-placeterm: the author revoked `place representation` from the registry, which left ONE live line of
    # the chapter using a term absent from a fail-closed registry (2_fundamentals.tex:650, against eight live
    # uses of `place embedding`). Fixed to the registered term. Pinned because nothing else gates registry
    # conformance -- there is no term-sweep checker in this repo, as recorded above.
    ("R12-placeterm","the chapter does not use the revoked `place representation` in live prose",
     "chapters/2_fundamentals.tex", r"from a place representation with next-category", False),
    # R12-d36: the THIRD misattributed commit, and the first whose defect was an aborted cell rather than a
    # staging mistake. d36da8c5 shipped a DEFINITIONS.md whose header says "AD-2 is OPEN / the AD-2 row
    # carries the retraction" while the row itself still said ANSWERED. Recorded rather than rewritten
    # (shared checkout, successor commits). Pinned because this class is invisible to every other gate: they
    # all read the working tree and none compares a commit message against its own diff.
    ("R12-d36",     "the record carries the third commit-attribution defect, where a header asserted a "
                    "correction the table row below it did not carry",
     "_history/_round12/51_commit_attribution_correction.md",
     r"shipped a header that contradicts its own table row", True),
    ("R12-d36why",  "and it names the aborted-cell mechanism plus the negative assertion that would have "
                    "caught it",
     "_history/_round12/51_commit_attribution_correction.md",
     r"cannot detect that one specific replacement never happened", True),
    # R12-study: the inversion study's LOAD-BEARING finding. The author asked for it specifically, and the
    # answer is a negative: the frozen planning folder records NO argument for tasks-before-representations,
    # so the order was inherited from the chapter map rather than defended. A negative finding is the kind
    # that quietly becomes "we looked and found a reason" on a later retelling, which is why it is pinned.
    # Spot-checked by me against the live tree, not taken from the sub-agent's self-report: the three
    # cross-references (2_fundamentals.tex:15, :17, :197), the two labels (:25, :210), zero references
    # outside the chapter, DEFINITIONS.md:613, and NORTH_STAR.md:73-75 all read as the study reports them.
    ("R12-study",   "the inversion study records that NO recorded rationale for the tasks-first order "
                    "exists in the frozen planning folder",
     "_history/_round12/52_inversion_study.md",
     r"records NO argument for placing tasks before representations", True),
    ("R12-studyrec","and its recommendation is marked as a recommendation the author decides, not an "
                    "authorization",
     "_history/_round12/52_inversion_study.md",
     r"this is a recommendation; the author decides, and nothing is authorized", True),
    # R12-extra: `make extra` is RED and it is not the document -- BSD sed aborts on a Latin-1 byte in the
    # build log, so the page-count extraction fails while the PDF builds fine. Recorded as his decision
    # because latexbuild.sh is shared with a parallel agent. Pinned so the red target is not later rediscovered
    # as a mystery, and so "all four builds rc=0" is not written again while it stands.
    ("R12-extra",   "the record carries the diagnosis of the red `extra` target as a sed locale failure "
                    "rather than a document defect",
     # REPOINTED 2026-08-03 with R9-blq4/blq5: the §6.23 diagnosis moved to the archive when the
     # section closed. The claim it protects is unchanged -- the red `extra` target was a sed locale
     # failure and not a document defect -- and the fix itself is pinned separately by R12-locale.
     "_history/_archive/PENDENCIAS_RESOLVIDOS.md", r"illegal byte sequence", True),
    # R12-studyfix: the sub-agent's study asserted "git history begins 2026-07-23" to support its central
    # negative finding. FALSE about the repository -- root commit 2025-03-08, 2049 commits, 1666 of them
    # earlier. I checked instead of accepting the self-report, and the FINDING survives on a better
    # measurement: of those 1666 earlier commits exactly ONE touches articles/dissertacao/ (bb4449c8, a
    # .gitignore). Pinned because a correction that lives only in a [VERIFY] list is the kind a later pass
    # skips, and because the wrong reason would otherwise be quotable as support for a right conclusion.
    ("R12-studyfix","the inversion study's false 'git history begins' claim is corrected in place, with the "
                    "measurement that actually supports the finding",
     "_history/_round12/52_inversion_study.md",
     r"It stands on a measurement of what the early commits CONTAIN", True),
    # R12-mech: THE RECORD MUST CARRY ONE MECHANISM FOR THE SURVIVING-ROW DEFECT, NOT TWO. For a while it
    # carried two incompatible ones -- a stale byte offset whose replace missed (invented, written into
    # _history/_round9/34 and into the R12-ad2row rationale) and an assert that raised before write_text (measured,
    # written into _history/_round12/51). They are not variants: under one the replace ran and missed, under the other
    # it succeeded and the write never happened, and only the second is what the cells show. The derived RULE
    # differs too, which is why a contradiction here is not cosmetic: re-reading before computing offsets
    # would not have prevented the real defect. Pinned on 34 because that is the file a later pass reads for
    # the lesson.
    ("R12-mech",    "the postmortem names the assert-before-write mechanism and retracts the invented "
                    "stale-offset one",
     "_history/_round9/34_tracker_disagreement.md",
     r"the mechanism I gave for\s+it was invented", True),
    ("R12-mech2",   "and it does not assert the stale-offset story as the cause",
     "_history/_round9/34_tracker_disagreement.md",
     r"The offsets had been computed against an \*earlier\* copy", False),
    # ---- His rulings of 2026-08-03 (second batch).
    #
    # R12-locale: the LC_ALL=C fix on latexbuild.sh, his option 2. TWO probes because the two lines have
    # DIFFERENT standing and conflating them is the specific error he asked me to prevent: :PAGES was a real
    # bug (BSD sed aborted on a Latin-1 byte, so `make extra` reported a failed build that had in fact
    # produced a correct 26-page PDF), while :ERRS is hygiene -- I MEASURED that `grep -c '^! '` returns 0 in
    # both locales on that log before adding it. A later reader who takes :ERRS for a bug fix would conclude
    # the tex_errors counts had been wrong all along, which they were not.
    ("R12-locale",  "both extraction lines in latexbuild.sh run under LC_ALL=C",
     "../src_utils/latexbuild.sh", r"PAGES=\$\(LC_ALL=C sed", True),
    ("R12-locale2", "and the script says in its own comment that the ERRS line is hygiene rather than a bug "
                    "fix, with the measurement that establishes it",
     "../src_utils/latexbuild.sh", r"HYGIENE AND SYMMETRY, NOT A BUG FIX", True),
    # R12-dscope: the `d` registry row. `d` is NOT a free letter -- d_{ij} is geodesic distance and
    # d_{shared} is the shared-trunk width, both live. The row without its scope note would license reading
    # either as an instance of the representation dimension. NOTE the correction of record: the pending note
    # said d_shared lives in Chapter 5; MEASURED, it is in Chapters 3 and 4 (3_cbic/method.tex:78,
    # 4_courb/methodology.tex:25,:258) and Chapter 5 has none. The row states the measured chapters.
    ("R12-dscope",  "the new `d` registry row carries its scope note naming both live subscripted uses",
     "../GLOSSARY.md", r"\*\*This letter is NOT free, and the row is scoped for that reason\.\*\*", True),
    ("R12-rho",     "and the rho row records that varying rho while holding the task definitions fixed is "
                    "what makes the central claim expressible",
     # PATTERN NOTE: the target is the LaTeX `$\rho$`, so in this raw-string regex the backslash is escaped
     # ONCE (\\rho), not twice. My first attempt used \\\\rho and the probe went red against text that
     # was correctly present -- a pattern defect reported as a missing claim.
     "../GLOSSARY.md", r"hold the task definitions fixed and vary \$\\rho\$", True),
    # R12-cmp: the comparative study reversed the previous recommendation (52 said invert, 53 says keep), and
    # the reversal turns on ONE argument the author must be able to find: the answer-mirror only pays a reader
    # who already holds the answer, so the design-mirror serves the FIRST reading the project's own G3 gate
    # governs. If that sentence is ever smoothed away, the record loses why the two studies disagree and the
    # 52 recommendation reads as unopposed.
    ("R12-cmp",     "the comparison records the reader-side resolution of the mirror argument, which is why "
                    "it reverses 52's recommendation",
     "_history/_round12/53_order_comparison.md",
     r"scaffold for a first reading; the answer-mirror is a reward for a second", True),
    # R12-cmpval: and it must keep saying that the "already-validated" label was 52's coinage rather than 49's
    # finding, with the concrete qualifier -- AD-4, the sign-off on the section shape, is OPEN. I verified this
    # independently: grep for "validated" in 49 returns zero occurrences of that claim about the option.
    ("R12-cmpval",  "and it records that option (a) is mechanically checked but narratively unsigned, because "
                    "AD-4 is still open",
     "_history/_round12/53_order_comparison.md",
     r"mechanically checked and narratively unsigned", True),
    # R12-clock3: I published "2,236 s, 7 percent inside the checkpoint" for the comparative study and it was
    # wrong IN KIND, not by a margin: 2,236 s is when MY collect window closed with the child still reported
    # `running` and every structured field empty. I read a timeout as a completion. Measured, the child was
    # still processing at 3,201 s -- 33 percent OVER the 2,400 s checkpoint. This is the SECOND time this
    # project has published a false in-budget claim about a sub-agent (see R9-clock/R9-clock2 for the first),
    # and both times the true reading was already in hand and unread. Ban the retracted figure as an
    # assertion, anywhere in the record, while allowing the sentences that quote it as retracted.
    ("R12-clock3",  "the study record carries the parent's real measurement, that the child's lifetime "
                    "overran the checkpoint by 74 percent",
     "_history/_round12/53_order_comparison.md",
     # FIGURE CORRECTED: this probe first pinned "33 percent OVER", which was my second wrong reading of the
     # same clock (3,201 s was the child's AGE when I looked, not its lifetime). The frame record gives
     # 4,185 s, 74 percent over. Pinning the real figure, not the intermediate one.
     r"4,185 s, 74 percent OVER the 2,400 s checkpoint", True),
    ("R12-clock4",  "and PENDENCIAS does not assert the retracted in-budget reading of the collect timeout",
     "PENDENCIAS.md",
     r"(?:\A|[.!?][*_'\")\]]*\s|\n)\s*(?:[-*+]\s+|\d+\.\s+)?(?:\*\*|__|\*)?\s*"
     r"(?:Medido|Wall-clock, medido por mim):?\**\s*2\.236 s contra o checkpoint de 2\.400 s\s*—\s*7 por cento "
     r"DENTRO", False),
    # R12-clock5: THREE readings of one clock, two of them wrong, and both wrong ones were published. 2,236 s
    # was my collect timeout; 3,201 s was the child's age at an arbitrary glance; 4,185 s is its lifetime from
    # the frame record. The pattern is identical each time -- an instrument reading taken for a measurement of
    # the process -- so ban the superseded figure in assertion form while allowing the sentences that retract
    # it. The 2,236 ban lives in R12-clock4 for PENDENCIAS; this one covers the study file for both.
    ("R12-clock5",  "the study does not assert either superseded overrun figure as the measurement",
     "_history/_round12/53_order_comparison.md",
     r"(?:\A|[.!?][*_'\")\]]*\s|\n)\s*(?:[-*+>]\s+)?(?:\*\*)?\s*(?:Measured[^.\n]{0,40})?"
     r"(?:33 percent OVER the 2,400|7 percent inside the 2,400)", False),
    # ---- ROUND-12 APPLICATION of the _history/_round12/49 Part B plan, under the author's option-(a) ruling of
    # 2026-08-03 (keep 2.1 tasks, 2.2 representations; move the representation definitions UP into 2.1).
    # These are the first probes in this project that pin CHAPTER prose produced by the redesign, so each
    # names the property that would be silently lost rather than the sentence that carries it.
    ("R12-s1bind",  "STEP 1: the notation prose BINDS the per-POI attributes, which the static-classifier "
                    "equation at :119 had been consuming undefined",
     "chapters/2_fundamentals.tex",
     r"Each POI \$p\\in\\mathcal\{P\}\$ carries a\s+category \$c_p\\in\\mathcal\{C\}\$ and lies in a "
     r"region \$r_p\\in\\mathcal\{R\}\$", True),
    ("R12-s2type",  "STEP 2: the check-in definition TYPES its category and region as the visited POI's "
                    "attributes, which is what makes the place-level vector well typed",
     "chapters/2_fundamentals.tex", r"\$c_i=c_\{p_i\}\$ is its category, and \$r_i=r_\{p_i\}\$", True),
    # R12-s3head: the author chose this head himself on 2026-08-03, from two registered candidates, after
    # revoking the term that made his earlier head inadmissible. It must not drift back to a variant, and
    # in particular not to "place representation", which is NOT in the registry.
    ("R12-s3head", "STEP 3: the new subsubsection carries the head the AUTHOR named",
     "chapters/2_fundamentals.tex", r"\\subsubsection\{Check-in and place embedding\}", True),
    ("R12-s3map",   "STEP 3: the representation map is a NUMBERED definition (AD-1, thirteen), not a "
                    "displayed equation in prose",
     "chapters/2_fundamentals.tex",
     r"\\begin\{definition\}\[Representation map\]\\label\{def:fund:repmap\}", True),
    # R12-s3scope: defect F-2 of _history/_round12/49. The remark must stay scoped to the SEQUENTIAL tasks: the
    # static task reads the place embedding directly, so "every predictive model" was false of it. This
    # pins the scoping word, which is the whole correction.
    ("R12-s3scope", "STEP 3: the factorization remark is scoped to the sequential tasks",
     "chapters/2_fundamentals.tex",
     r"Every model of the sequential tasks in this dissertation reads \$\\rho\(H_i\)\$", True),
    # R12-s4moved: the MOVE is only real if the definitions are GONE from 2.2. A probe on their presence in
    # 2.1 would hold just as well if they were duplicated, which is exactly the failure mode the plan warns
    # about (two rendered definitions, one number sequence). This asserts the absence.
    ("R12-s4moved", "STEP 4: the two definition environments are GONE from 2.2, so the move is a move "
                    "rather than a duplication",
     "chapters/2_fundamentals.tex",
     r"\\subsubsection\{Representations of a check-in\}|"
     r"limitation for this research[\s\S]{0,400}\\begin\{definition\}\[Place embedding\]", False),
    # R12-s5neutral: AD-2 option 2. The author ruled that Chapter 2 states Chapter 4's input in the NEUTRAL
    # form and that the level question is documented as LO-12 rather than recorded as an erratum. Both
    # forbidden wordings are banned by R12-neutral already; this pins the positive form in 2.2 so it cannot
    # revert to the "place-level input" claim the retracted investigation had made.
    ("R12-s5neutral","STEP 5: 2.2 states Chapter 4's input in the neutral form, matching the 2.1 remark",
     "chapters/2_fundamentals.tex", r"while its input stays a function of the visited POI", True),
    # R12-wise: the -wise suffix is excluded from the British-spelling sweep BY RULE, not by enumeration.
    # "elementwise" (introduced by step 3) false-fired and turned `make check` red on correct American
    # prose; the module's own header warns that a hand-typed list matches only the words its author thought
    # of, and this was that defect. Pinned because a later "simplification" back to enumeration would
    # reintroduce it for the next compound.
    ("R12-wise",    "the register gate excludes the -wise family by rule rather than by listing words",
     "../src_utils/check_register.py", r"if low\.endswith\(\"wise\"\) and len\(low\) > 4:", True),
    # R12-legcount: I published "the eight new ones sabotage-validated" when SEVEN were. The eighth,
    # R12-s4moved, was never mutated: the validation cell made eight leg() calls, but one reused an earlier
    # probe's name as the silent control, so the row COUNT matched the probe count while the name SET did
    # not. It was the worst one to miss -- the only want=False probe of the batch, and an absence probe
    # holds identically when its pattern can never match (the R9-clock2 and R12-attrib defect). Pinned so
    # the rule that prevents it survives: reconcile the validated names against the added names as SETS.
    ("R12-legcount", "the record carries the rule that a validation table is reconciled by probe NAME "
                     "rather than by row count, because a control leg reuses a name",
     "_history/_round9/34_tracker_disagreement.md",
     r"Reconcile the two sets by name, not by cardinality", True),
    # ---- AD-6, CLOSED BY THE AUTHOR'S OWN HAND on 2026-08-03. He rewrote Definition 2.2's vague
    # retention sentence himself ("A target label is withheld from it when one of the sequential tasks is
    # trained") and asked for sharpening on top rather than a rewrite. Three probes, because the passage
    # has three independently rottable properties and his words are the load-bearing ones.
    ("R12-ad6his",  "AD-6: the author's own wording names the target PER TASK, which is what answers the "
                    "leakage question, and it is carried verbatim",
     "chapters/2_fundamentals.tex",
     r"the prediction target is \$c_i\$ for next-category\s+prediction and \$r_i\$ for next-region "
     r"prediction\. These labels belong to \$x_i\$", True),
    # R12-ad6fwd: his sentence was the FIRST live use of both task names, defined ~130 lines later. The
    # symbols were bound (Definition 2.1) so this is lighter than a symbol-before-its-definition, but it
    # is the very property the redesign's step order existed to protect. Pinned as an EXPLICIT forward
    # pointer rather than by renaming his tasks away.
    ("R12-ad6fwd",  "AD-6: the task names in Definition 2.2 point FORWARD explicitly to the definitions "
                    "that introduce them, instead of naming them undefined",
     "chapters/2_fundamentals.tex",
     r"For the two sequential tasks studied here \(Definitions~\\ref\{def:fund:nextcat\}\s+and~"
     r"\\ref\{def:fund:nextreg\}\)", True),
    # R12-ad6pos: the POSITIVE half. Excluding the label of x_i rules out leakage; the converse -- that
    # the categories and regions of PAST visits are legitimate input -- was implicit, and that exact
    # omission is what prompted the author's question about a region history. A probe on the exclusion
    # alone would hold with the informative half deleted, so this pins the half that was missing.
    ("R12-ad6pos",  "AD-6: Definition 2.2 states the POSITIVE half too, that past visits' categories and "
                    "regions are observed input",
     "chapters/2_fundamentals.tex",
     r"the categories and regions carried by the\s+visits in \$H_i\$ are observed input", True),
    # ---- FABRICIO'S NEW WAVE, 2026-08-03 (CONSIDERATIONS.md, "--- NEW WAVE ---": FAB-32/33/34).
    #
    # FAB-32 and FAB-33 are ONE defect with two occurrences and he found both: §1.1 referred to "the
    # first two studies" and "the final study" thirty-five lines BEFORE the three studies are
    # introduced at :125 in §1.2. Measured, not assumed. Two probes because the two sentences can rot
    # independently, and each is an ABSENCE probe on the old form PLUS a presence probe on the new one:
    # a presence-only probe would hold if the old sentence were restored alongside the new.
    ("R13-fab32",   "FAB-32: §1.1 introduces category classification as the dissertation's own task "
                    "rather than indexing a set of studies the reader has not met yet",
     "chapters/1_introduction.tex",
     r"This dissertation also uses \\emph\{category classification\}, a static task", True),
    ("R13-fab32b",  "FAB-32: and the superseded form, which named 'the first two studies' before any "
                    "study existed for the reader, does not come back",
     "chapters/1_introduction.tex", r"The first two studies also use \\emph\{category", False),
    ("R13-fab33",   "FAB-33: the task-pair sentence states that the pairing varies WITHOUT naming an "
                    "unintroduced 'final study', and still points at the arc section that owns it",
     "chapters/1_introduction.tex",
     r"Which two tasks are trained together is not fixed\s+across the work, as "
     r"Section~\\ref\{sec:intro:arc\} explains", True),
    ("R13-fab33b",  "FAB-33: and the superseded 'The task pair changes in the final study' form stays out",
     "chapters/1_introduction.tex", r"task\s+pair changes in the final study", False),
    # FAB-34: "o que e isso? defina" on \emph{mahalle}. His own note said "search if needed", so the
    # gloss is SOURCED rather than written from memory, and the probe pins the two properties that
    # make it correct: the level of government (which is what makes it comparable to a census tract)
    # and the appositive that matches Chapter 2's existing wording so the two chapters cannot drift.
    ("R13-fab34",   "FAB-34: mahalle is glossed at its FIRST use in the introduction, naming the "
                    "administrative level rather than implying it is a statistical unit like a tract",
     "chapters/1_introduction.tex",
     r"the smallest administrative unit of Turkish\s+local government, roughly a municipal "
     r"neighborhood", True),
    # ---- The author's follow-up, 2026-08-03: put the fuller mahalle account in §2.4.1, and answer
    # whether other terms are shown before being explained. S-1 and S-2 are the sweep's own findings,
    # not reviewer items, so they are gated the same way his items are.
    ("R13-mahfull",  "§2.4.1 defines BOTH region units and says what kind of object each is, so the "
                     "comparison across the two collections is legible",
     "chapters/2_fundamentals.tex",
     # Re-pinned 2026-10-03 (D7, author-ruled: cite the definitions; the cited wording replaced the
     # uncited one). Whitespace is \s+ throughout so a rewrap cannot break the probe.
     r"A\s+census\s+tract\s+is\s+a\s+statistical\s+subdivision\s+of\s+a\s+county", True),
    ("R13-mahfull2", "and the mahalle half names the administrative level rather than calling it a "
                     "statistical unit like a tract",
     "chapters/2_fundamentals.tex",
     r"\\emph\{mahalle\}\s+is\s+an\s+administrative\s+unit\s+within\s+a\s+municipality's\s+boundaries",
     True),
    # The unregistered-term ban: the word for the elected head of a mahalle is NOT in the GLOSSARY,
    # and §1's rule is fail-closed. This probe fails if any chapter starts using it before the author
    # approves a registry row -- the same shape as the other fail-closed bans in this suite.
    ("R13-mahterm",  "the unregistered Turkish term for the elected head of a mahalle stays OUT of "
                     "Ch.2 prose while the GLOSSARY has no row for it",
     "chapters/2_fundamentals.tex", r"\bmuhtar\b", False),
    ("R13-s1pcgrad", "S-1: PCGrad is glossed and cited at its FIRST use in §2.3.2, not only where "
                     "§2.3.5 introduces it 323 lines later",
     "chapters/2_fundamentals.tex",
     r"PCGrad, a gradient-surgery method~\\cite\{yu2020pcgrad\},", True),
    ("R13-s2base",   "S-2: the introduction's two external baselines carry a gloss and a citation, "
                     "rather than arriving as bare names",
     "chapters/1_introduction.tex",
     r"HMT-GRN, which uses a predicted region to\s+constrain the search for a place~\\cite\{Lim2022\}",
     True),
    ("R13-s2base2",  "S-2: and the same for STAN, with the gloss Ch.2 already uses",
     "chapters/1_introduction.tex",
     r"STAN, which connects non-adjacent visits through\s+spatio-temporal "
     r"correlations~\\cite\{luo2021stan\}", True),
    # R12-attrib: a commit-message attribution defect, recorded because the suite CANNOT detect this class
    # -- every gate here reads the working tree and none reads the commit log. Two of round 12's commits
    # describe diffs they do not contain, because `git add -A` in a backgrounded cell staged the tree at
    # execution time rather than dispatch time. Pinning the record is the only enforcement available.
    ("R12-attrib", "the commit-attribution defect is recorded, with the rule that a commit message is a "
                   "claim about a diff and that no gate here can check one",
     "_history/_round12/51_commit_attribution_correction.md",
     # SECOND BRANCH CORRECTED: it was "never reads the commit log", which occurs ZERO times in the
     # target -- the file says "read the working tree and never the commit log". A dead alternation
     # branch makes a probe look broader than it is; caught by a sabotage leg reporting TARGET ABSENT.
     r"no gate in `check\.sh` can detect it|never the commit log", True),
    # ---- His four rulings of 2026-08-03 (side chat). Three probes: the two whose flattening would cause
    # real damage, plus the registry scope note.
    #
    # R12-neutral: HIS RULING WAS "do not register", which is SILENCE, not licence to write the wrong
    # thing. The Chapter 4 instantiation must say only "a function of the visited POI"; both "of the
    # visit's timestamp" (false: it is ONE SELECTED visit) and "aggregated" (false: the operation selects)
    # stay forbidden. An edit pass reading "not recorded, implementation detail" could easily reintroduce
    # a wrong qualification, which is exactly the failure this pins shut.
    ("R12-neutral", "the design records that his 'do not register' ruling is silence and does NOT license "
                    "the two wordings the code refutes",
     "../science/fundamentals/DEFINITIONS.md",
     r"not a licence to write the wrong thing", True),
    # R12-ad7: AD-7 renames D13's indices from i,j to a,b so that i means a check-in everywhere in the
    # chapter. Pinned on the DESIGN, not the chapter, because the chapter edit lands with the redesign --
    # editing it earlier would desynchronize the two during the pending window. The rename departs from
    # the source's own notation (yu2020pcgrad uses i,j for tasks), so the design must keep saying WHY.
    ("R12-ad7",     "the design carries D13's renamed task indices and the reason for departing from the "
                    "source's notation",
     "../science/fundamentals/DEFINITIONS.md",
     r"departs from the source's notation deliberately", True),
    # R12-placerep WAS REMOVED, 2026-08-03, in the same commit that revoked the row it pinned. It required
    # the scope note on the `place representation` registry row. The author then revoked the row itself
    # ("vamos usar so place embedding para evitar conflitos e interpretacoes dubias"), so the note went with
    # it and the probe would have gone red ON HIS DECISION. That is the R12-notwrong defect exactly: a gate
    # enforcing a claim the author has since withdrawn fights the correction instead of protecting it.
    # A REPLACEMENT WOULD BE WRONG TOO, and it is worth saying why rather than leaving a gap that looks like
    # an oversight. The obvious candidate -- ban `place representation` from the tree -- fails on its own
    # terms: this file, PENDENCIAS, and the round-12 records all discuss the term by name while recording the
    # decision, so an absence probe would fire on the record OF the decision. The registry is already
    # fail-closed by POLICY (WRITING_LAW section 5, GLOSSARY's own preamble): a term absent from the
    # registry may not be used. Note precisely what that means mechanically, because I first wrote that
    # a `check_glossary_terms` gate handles it and NO SUCH FILE EXISTS -- the checkers are the fourteen
    # check_*.py in this directory and only this one and check_verify_list.py read GLOSSARY.md at all.
    # So registry conformance is enforced by review and by targeted probes here, not by a term sweep,
    # and the honest statement is that revoking this row leaves the term ungated rather than covered
    # elsewhere. Nothing replaces it, and that is a known gap and not an oversight.
    # ---- ROUND-13 APPLICATION of PENDENCIAS section 4 (the AUT- items), under the author's rulings
    # recorded inline in section 4.1 on 2026-08-03/04. Each probe names the property that would be
    # silently lost, not the sentence that happens to carry it today.
    #
    # R13-cbictitle / R13-mwtitle / R13-errata-hyphen: THREE VERBATIM QUOTATIONS whose hyphen a house
    # de-hyphenation sweep removed from INSIDE the quotation marks. The failure class is worth stating
    # because it will recur: a normalization rule written for house prose has no way to know it has
    # crossed into quoted material, so the sweep silently rewrote what three sources of record say. The
    # CBIC case printed the SAME PAPER under two titles in one PDF (chapter preface vs bibliography).
    # These probes are PRESENT-type on the hyphenated form rather than ABSENT-type on the unhyphenated
    # one, deliberately: an absence probe would fire on this comment and on the tracker rows that
    # discuss the defect by name, which is the R12-notwrong trap. Sources of record, each opened:
    #   CBIC title      -> Crossref DOI 10.21528/CBIC2025-1191324, and CBIC___MTL/main.tex:31
    #   MobiWac title   -> [mobiwac]/src/main.tex:52 (submitted manuscript, EDAS #1571313639)
    #   errata wording  -> CBIC___MTL/sections/conclusion.tex:17 (the published sentence)
    ("R13-cbictitle", "the Ch.3 preface quotes the CBIC title as PUBLISHED, hyphenated, matching Crossref "
                      "and the paper's own source",
     "chapters/3_cbic.tex", r"``An Investigation into Multi-Task Learning for", True),
    ("R13-mwtitle",   "the Ch.5 preface quotes the submitted MobiWac title as the manuscript carries it, "
                      "hyphenated",
     "chapters/5_mobiwac.tex", r"A Check-in-Level Multi-Task Study on Mobility Data", True),
    ("R13-errata-hyphen", "the errata table's Published-wording column shows what CBIC actually published, "
                          "hyphenated -- the column is self-defeating otherwise",
     "tables/cbic/errata_wording.tex", r"investigating advanced multi-task optimizers", True),
    # R13-obj4: objective 4 names the PROTOCOL of the final study, so it must point at Chapter 5, not at
    # the Conclusion. This defect was invisible to every gate for a reason worth recording: the wrong
    # \ref RESOLVED, so the build reported zero undefined references, the cross-reference lint passed,
    # and the rendered page printed "(Chapter 6)" with full confidence. A resolving reference is not a
    # correct one, and no existing gate distinguishes the two.
    # SCOPE, corrected 2026-08-04 after a reviewer finding: this note used to say the probe was "anchored
    # on the label token rather than on the surrounding prose so a later rewording does not turn this red
    # spuriously". The pattern beside it includes seven words of the objective's prose, so a rewording
    # WOULD turn it red. The pattern is left as it is and the description is what changed: pairing the
    # prose with the label is what makes the probe catch a silent re-point of the reference, which is the
    # defect it exists for. Whoever rewords objective 4 must update this pattern in the same commit.
    ("R13-obj4",     "objective 4's protocol reference points at the final STUDY (Ch.5), not at the "
                     "Conclusion; a resolving \\ref is not a correct one",
     "chapters/1_introduction.tex",
     r"non-inferiority protocol used in the final study\s*\(Chapter~\\ref\{ch:mobiwac\}\)", True),
    # ---- WAVE 1b: the Ch.1/Ch.2 prose items. Each is a small edit, so each probe pins the PROPERTY
    # the edit established rather than the whole sentence, which would go red on any later rewording.
    #
    # R13-aut07 is an ABSENCE probe, and the exception to this file's usual preference for presence
    # probes is deliberate: the defect WAS a term, so its absence is the fix. It is safe here only
    # because the banned string is confined to prose -- the tracker rows and provenance comments that
    # discuss it live outside SRC or inside `%` comments, which live_text() strips. Verified by
    # sabotage that it fires, and verified that it does NOT fire on the comment in 1_introduction.tex
    # that names the term while recording the decision.
    ("R13-aut07",    "the unregistered synonym `static place categories` is gone from prose; GLOSSARY §1 "
                     "registers the task as `category classification` and the registry is fail-closed",
     "chapters/1_introduction.tex", r"static place categories", False),
    ("R13-aut10",    "`hard parameter sharing` is glossed at its FIRST use in Ch.1, three uses before "
                     "Ch.2's formal definition",
     "chapters/1_introduction.tex",
     r"hard\s+parameter sharing, in which the tasks share one trunk of hidden layers", True),
    ("R13-aut04",    "the place-category clause LEADS INTO the two tasks instead of hanging off the "
                     "mobility-applications sentence",
     "chapters/1_introduction.tex",
     r"the category of the place carries its semantic\s+meaning~\\cite\{Xu2023\}, and it is one of the "
     r"two properties this dissertation predicts", True),
    # R13-aut05: absence probe on the undefined term the two deleted sentences introduced. `\cite`
    # keys are NOT probed here: wu2024torchspatial is still cited four times in Ch.4, so a key-absence
    # probe would be false, and that measurement is recorded in the removal comment instead.
    ("R13-aut05",    "`neighboring geospatial tasks`, a term the document never defines, is gone from "
                     "the opening section",
     "chapters/1_introduction.tex", r"neighboring geospatial tasks", False),
    ("R13-aut16",    "`sequential` and `static` are both glossed at first use in Ch.1, not only in Ch.2",
     "chapters/1_introduction.tex",
     r"The two tasks above are sequential, because each one reads a history of\s+visits", True),
    ("R13-aut27",    "the per-task loss symbol is glossed where the total-objective equation introduces "
                     "it; it was the one symbol in that equation with no gloss",
     "chapters/2_fundamentals.tex",
     r"where \$\\mathcal\{L\}_k\$ is the\s+loss of task \$k\$", True),
    ("R13-aut19",    "§2.2.2 states what infomax IS before stating what it maximizes",
     "chapters/2_fundamentals.tex",
     r"tell a true pairing of\s+two parts of the data from a corrupted one", True),
    ("R13-aut24",    "§2.2.4 opens by naming what each study changes, not with an abstract noun as agent",
     "chapters/2_fundamentals.tex",
     r"Each study changes the input representation, and each also changes the architecture", True),
    # R13-aut22 needs BOTH legs, because a move is two facts: gone from the origin AND present at the
    # destination. One leg alone would pass on a deletion that lost the content. The origin leg is
    # scoped to the sentence form that made FiLM read as a mobility representation.
    ("R13-aut22",    "AUT-22/GER-06 leg 1: FiLM is no longer introduced among the mobility "
                     "representations in §2.2.3.1",
     "chapters/2_fundamentals.tex",
     r"sinusoidal\s+networks~\\cite\{russwurm2024geographiclocationencodingspherical\}\.\s+"
     r"Feature-wise Linear", False),
    ("R13-aut22b",   "AUT-22/GER-06 leg 2: FiLM IS introduced with the sharing topologies in §2.3.1, "
                     "next to the hard-sharing definition it modifies",
     "chapters/2_fundamentals.tex",
     r"A shared trunk need not\s+treat both tasks identically\. Feature-wise Linear Modulation \(FiLM\)",
     True),
    # R13-aut30: the acronym. Its companion claim (that the abbreviations-list exclusion COMMENT in
    # content.tex now carries re-measured counts instead of a false blanket claim) is NOT PROBEABLE HERE
    # and is listed in NOT_CHECKABLE by name. I wrote it as a probe first and it failed, correctly: this
    # gate matches on live_text(), with `%` comments stripped, which is trap 1 of its own docstring and
    # the reason the whole file works. Measured: the token is in the raw file and absent from live_text().
    # A probe whose target the instrument cannot see is not a weak probe, it is a broken one.
    ("R13-aut30",    "OOD is expanded AT its first use in §2.4.2.2, and the metric is defined directly "
                     "rather than as an `Equivalently` restatement",
     "chapters/2_fundamentals.tex",
     r"The reported\s+out-of-distribution discounted, or OOD-discounted, Acc@10 is therefore", True),
    # ---- WAVE 2: the author-decided items. AUT-20/21/23 are ONE edit seen from three angles and were
    # applied in a single pass on his instruction, so their probes are grouped here.
    #
    # THE HONESTY PROBES. R13-aut20 and R13-aut23 are the two halves of a correction to a claim about
    # OUR OWN system, which WRITING_LAW §3 classes as a bug rather than a style matter. The old wording
    # ("trained without category or region labels", "without using task labels") was false in both
    # places: the visited place's category is an input feature of the check-in node, and the
    # configuration the final study trains reconstructs a masked place's category distribution at weight
    # 0.3. Each probe is PRESENT-type on the corrected scope claim rather than ABSENT-type on the old
    # wording, because the old wording is quoted in the provenance comments and in the tracker that
    # record the correction, and an absence probe would fire on the record OF the fix (the R12-notwrong
    # trap). Evidence for every figure: _history/_round13/71_graphnode_features.md, spec and code line by line.
    ("R13-aut20",    "§2.2.2 states the SCOPE of what the representation objectives do not read (the "
                     "next-category and next-region targets) instead of the false blanket claim that no "
                     "category or region label is used anywhere",
     "chapters/2_fundamentals.tex",
     r"trained with no next-category and no\s+next-region target", True),
    ("R13-aut23",    "§2.2.3.2 makes the same scope claim for Check2HGI and no longer says it learns "
                     "`without using task labels`",
     "chapters/2_fundamentals.tex",
     r"with no next-category and no next-region target in its\s+objective", True),
    # R13-aut23b: the equation is the hierarchical CORE, not the complete trained objective. This is the
    # assertion that had presented a three-term sum as the whole loss while the shipped configuration
    # runs five terms. Anchored on the two auxiliary terms rather than on the lead-in, because the
    # weights are the load-bearing content: a later rewording of the sentence is fine, dropping the
    # terms is not.
    # CORRECTED 2026-08-04 after a reviewer finding, and the correction is the point of this note. The
    # pattern used to stop after the 0.3 reconstruction term while the description claimed it guarded
    # BOTH auxiliary terms. Proven by measurement rather than argued: deleting ONLY the 0.1 term left the
    # suite at rc=0 with this probe reporting "holds". The original sabotage test did not expose it
    # because it replaced the whole block, so it bit for the wrong reason -- a half-covering probe passes
    # a whole-block sabotage. The pattern now spans both weights.
    ("R13-aut23b",   "the two auxiliary terms that complete the trained objective are named with their "
                     "weights, so the displayed equation is not presented as the whole loss",
     "chapters/2_fundamentals.tex",
     r"a reconstruction term at weight 0\.3, which\s+recovers a masked place's own distribution over "
     r"the seven categories from its\s+neighbors, and a term at weight 0\.1, which keeps the trainable "
     r"table of place vectors\s+near the values it started from", True),
    # R13-aut18 / R13-aut18b: the two halves of the region-unit move, and BOTH are required. The
    # definition half alone would pass on an edit that deleted the unit names without rehoming them,
    # which is exactly the defect a reviewer caught in my first attempt: the pointer was written before
    # the destination carried the referent, so the chapter briefly named the unit nowhere.
    ("R13-aut18",    "the task definition names the KIND of region unit, so it holds for any dataset the "
                     "work later adds",
     "chapters/2_fundamentals.tex",
     # Re-pinned 2026-10-10 (E3, author-approved): "administrative unit" -> "areal unit", because after D7
     # §2.4.1 calls the census tract a statistical unit; the KIND-of-unit intent of AUT-18 is kept.
     r"the target is an areal unit at\s+neighborhood scale", True),
    ("R13-aut18b",   "and §2.4.1 names the unit each dataset actually supplies, which is what makes the "
                     "definition's pointer true",
     "chapters/2_fundamentals.tex",
     r"a census tract in the five United States datasets, and a\s+\\emph\{mahalle\}", True),
    ("R13-aut31",    "§2.4 separates how the data is divided from which comparison the design supports",
     "chapters/2_fundamentals.tex",
     r"\\subsection\{Preparation and data split\}", True),
    ("R13-aut31b",   "and the remaining subsection is named for what it now does alone",
     "chapters/2_fundamentals.tex",
     r"\\subsection\{Comparison and statistical decisions\}", True),
    # R13-aut25 / R13-aut25b: the two-input contrast, and the HEDGE that is the author's actual ruling.
    # The first probe pins the contrast; the second is an ABSENCE probe on the word "correlated" in the
    # lineage subsection, because the whole point of his ruling was that a correlation is a quantity and
    # nobody measured it. The absence probe is scoped to the sentence form rather than to the word
    # anywhere in the chapter: "correlated tasks" appears legitimately in the reproduced CBIC prose, and
    # a chapter-wide ban would fire on that. The measurement he set aside is LEFT_OUT.md LO-13.
    ("R13-aut25",    "§2.2.4 contrasts the two architectures by the SOURCE of their two inputs, not by "
                     "the number of them",
     "chapters/2_fundamentals.tex",
     r"MTLnet derives both from one place\s+embedding, whereas the joint model reads two tables exported",
     True),
    ("R13-aut25b",   "and it states shared origin as a fact of construction rather than asserting a "
                     "correlation nobody measured (author's hedge ruling; the measurement is LO-13)",
     "chapters/2_fundamentals.tex",
     r"share an origin by construction, so they are not\s+independent views", True),

    # ---- ROUND-TARIK/EXTRAVOL (this session). Two author instructions: (1) remove the prose
    # sentence stating Tarik S. Paiva is the CoUrb paper's first author -- the PPGCC regimento does
    # not require first authorship for a coletânea chapter, so the role statement is not made in
    # prose; the bibliography's real author list is untouched (guardrails R2, attribute fidelity).
    # (2) remove every live-prose pointer from a main-volume chapter at "Appendix B/D of
    # \extravolume" (the supplementary volume) -- main-volume chapters must not reference the extra
    # material. Both are ABSENCE probes: revert either edit and the corresponding row must fire.
    ("RTV-01",  "1_introduction.tex no longer states Tarik S. Paiva is the CoUrb paper's first "
                "author (the role-ranking sentence, not the bibliography entry)",
     "chapters/1_introduction.tex", r"Tarik S\.\\?\s*Paiva is the first author", False),
    ("RTV-02",  "the CoUrb chapter-list bullet still credits Vitor's own MTLnet-baseline "
                "contribution and presenter role, just without the authorship-ranking sentence",
     "chapters/1_introduction.tex",
     r"contributed the MTLnet baseline used in the study\s+and presented the work at the event",
     True),
    ("RTV-03",  "3_cbic.tex's preface no longer points at Appendix B of the supplementary volume",
     "chapters/3_cbic.tex", r"\\extravolume", False),
    ("RTV-04",  "3_cbic/method.tex's three footnotes no longer point at Appendix B(.1) of the "
                "supplementary volume (DGI neighbor-averaging + two Nash-MTL corrections)",
     "chapters/3_cbic/method.tex", r"\\extravolume", False),
    ("RTV-05",  "apx_a_contributions.tex's label-history-benchmark item no longer points at "
                "Appendix D of the supplementary volume",
     "chapters/apx_a_contributions.tex", r"\\extravolume", False),
    ("RTV-06",  "4_courb.tex's preface no longer points at Appendix B of the supplementary "
                "volume for the post-publication static-task scope finding",
     "chapters/4_courb.tex", r"\\extravolume", False),
    ("RTV-06b", "and the static-task-scope finding itself is folded inline rather than lost "
                "(the venue-type -> seven-category mapping; repointed 2026-10-03: the old "
                "'one-to-one onto' wording claimed a bijection, but 284-365 types map many-to-one)",
     "chapters/4_courb.tex",
     r"each venue type maps to exactly one of the seven top-level\s+categories", True),
    ("RTV-07",  "5_mobiwac.tex's preface no longer points at Appendix B of the supplementary "
                "volume for the errata record",
     "chapters/5_mobiwac.tex", r"\\extravolume", False),
    ("RTV-08",  "5_mobiwac/05_setup.tex's label-history-benchmark paragraph no longer points at "
                "Appendix D of the supplementary volume (definition + one-candidate exception)",
     "chapters/5_mobiwac/05_setup.tex", r"\\extravolume", False),
    ("RTV-08b", "and the one-candidate exception is folded inline rather than lost (the "
                "relation-typed graph encoder's raw/standardized scores)",
     "chapters/5_mobiwac/05_setup.tex",
     r"relation-typed graph encoder, falls below the benchmark on the standardized run", True),
    # ---- ROUND 13, SECOND WAVE: the author's rulings on the eleven items left open in §4.
    # R13-aut08: the SANCTIONED FALLBACK from NORTH_STAR §6 Ch.1 beat 4 (b), replacing a comparative
    # claim about the literature that was refuted. PRESENT-type on the fallback rather than ABSENT-type
    # on the comparative form, because the refuted wording is quoted in the provenance comment and in
    # the tracker row that records the refutation (the R12-notwrong trap).
    ("R13-aut08",    "§1.2 uses the NORTH_STAR-sanctioned fallback for the task-choice defense instead "
                     "of the comparative claim that no open anchor supports",
     "chapters/1_introduction.tex",
     # Re-pinned 2026-10-05 (D8b, author dropped "established": Ch.5 related work calls category and
     # region auxiliary signals in multi-granularity systems, and region as an end target underexplored).
     r"Both are end\s+targets in the mobility literature, and the next region feeds a "
     r"broader family of\s+downstream problems", True),
    ("R13-aut09",    "the arc sentence names its subject (each study, each chapter) and time-indexes "
                     "supersession, instead of letting an abstract noun act",
     "chapters/1_introduction.tex",
     r"Each study revised what the previous one had concluded, and each\s+later chapter states which "
     r"earlier conclusion it supersedes", True),
    # R13-aut09b is ABSENT-type, and the reason it is safe is NOT the one this comment first gave.
    # CORRECTED after a reviewer finding: I wrote that the banned phrase "appears nowhere in the
    # provenance comments", and it does appear there -- the AUT-09 comment in 1_introduction.tex quotes
    # "a correction trail" verbatim to record what was deliberately not used. The probe survives because
    # this gate strips comments before matching, which is a property of the gate rather than of the text,
    # so the safety argument had to be restated rather than the probe changed. Anyone widening this gate
    # to scan comments would turn this probe red on a comment that exists to prevent the very thing the
    # probe forbids. NORTH_STAR §6 Ch.1 beat 4 (d) carries the F4 guard this pins.
    ("R13-aut09b",   "and the arc is not called a trail, which NORTH_STAR's F4 guard forbids (it would "
                     "make the null result read as act one of a script)",
     "chapters/1_introduction.tex",
     r"correction trail", False),
    ("R13-aut14",    "the Contributions section claims Check2HGI's reusability as independence from the "
                     "heads placed on it, which is a property of the construction",
     "chapters/1_introduction.tex",
     r"independent of the prediction heads placed on top of it", True),
    # CORRECTED 2026-08-04 after a reviewer finding. The sentence read "To our knowledge, no prior work
    # treats...", which is a claim about the whole literature. The project's own literature audit recorded
    # a NARROWER ceiling as the most that is defensible, "Among the works reviewed here, none treats...",
    # and it chose that scope because its sweep was incomplete by its own record: two OpenAlex queries
    # returned HTTP 504 and were not retried, and two candidate full texts were never opened. "No prior
    # work" asserts an absence across a literature that was not fully searched; the reviewed-works form
    # asserts only what was actually read. My earlier check confirmed the sentence was weaker than
    # Chapter 5's claim, which was true and was not the whole question.
    ("R13-aut14b",   "the novelty claim in the frame is scoped to the works this dissertation reviewed, "
                     "which is the ceiling its own literature audit established, and is weaker than "
                     "Chapter 5's claim (the frame must not exceed the chapter under review)",
     "chapters/1_introduction.tex",
     r"Among the works reviewed in this dissertation, none treats\s+the next category and the next "
     r"region as co-equal end targets of one joint model", True),
    # R13-aut14d is ABSENT-type on the over-broad form, so a later edit cannot quietly restore it. Safe as
    # an absence probe: the phrase is described in the comment above, not quoted, and the gate strips
    # comments in any case.
    ("R13-aut14d",   "and the over-broad `no prior work` form is not used, since the sweep behind it was "
                     "incomplete by its own record",
     "chapters/1_introduction.tex",
     r"no prior work treats the next category", False),
    # R13-aut14c: the balancer screen and the orthogonality measurement are only honest WITH their
    # scope attached, which is the author's own warning on candidate (c) and GER-11's point. Anchored on
    # the scope words, not on the headline, so a rewrite that drops "default configurations" or the
    # one-seed/two-dataset scope fails.
    ("R13-aut14c",   "and the balancer screen travels with its full scope (default configurations, one "
                     "initialization, two datasets), so a mean is not read as a general result",
     "chapters/1_introduction.tex",
     r"screened at their default configurations, at a single random\s+initialization, on Alabama and "
     r"Florida", True),
    # ---------------------------------------------------------------------------------------------
    # LADDER-* -- THE VERDICT LADDER, ADDED 2026-09-06 (author: "vamos verificar a escada").
    #
    # WHY THESE EXIST. The ladder (CLAUDE.md 0.3) is the document's central verdict and it is
    # copied BY HAND. Measured the day these were written: "half a point" appears at TWELVE live
    # sites across EIGHT files, and not one probe watched any of them. The failure is not
    # hypothetical -- it is the errata of 2026-08-21, where the Portuguese Resumo said the joint
    # model won "em todos os conjuntos" while the English Abstract, 2.5, Ch.5 and Ch.6 all said
    # one dataset. A whole-document claim drifted in ONE language and nothing caught it.
    #
    # WHAT THEY PIN, and why all three parts together. Each probe requires the scope, the count
    # and the bound in ONE match: "one dataset" AND "five remaining" AND "half a point". Widening
    # any single part breaks the match, which is the drift these are for -- the 2026-08-21 defect
    # changed only the scope and left the rest standing, so a probe on the bound alone would have
    # passed it.
    #
    # THE PORTUGUESE IS PROBED SEPARATELY AND FIRST. It is the half that actually broke, and it
    # is the half no English-reading reviewer re-reads. A single probe over both languages would
    # let one satisfy the gate for the other.
    #
    # SCOPE, stated so nobody widens these later: they guard the two ABSTRACTS plus the two frame
    # chapters that state the full ladder. They do NOT guard Ch.5, whose own sentences are
    # reproduced article text under the errata regime and must not be pinned to frame wording.
    ("LADDER-pt",   "the PT Resumo keeps the category verdict at ONE dataset with the half-point "
                    "bound -- this is the exact sentence that drifted on 2026-08-21",
     "content.tex",
     r"superou em um conjunto, enquanto as cinco diferen\S*as restantes s\S*o equivalentes a zero "
     r"dentro de meio ponto", True),
    ("LADDER-en",   "the EN Abstract keeps the category verdict at ONE dataset with the half-point bound",
     "content.tex",
     r"outperformed them at one dataset, while the five remaining differences were equivalent to "
     r"zero within half a point", True),
    ("LADDER-c1",   "Ch.1 names Florida as the single category dataset and bounds the other five",
     "chapters/1_introduction.tex",
     r"outperforms the dedicated model at Florida, and the five remaining differences are\s+"
     r"equivalent to zero within half a point", True),
    ("LADDER-c6",   "Ch.6 names Florida as the single category dataset and bounds the other five",
     "chapters/6_conclusion.tex",
     r"outperforms them at Florida, and the five remaining differences are equivalent to\s+"
     r"zero within half a point", True),
    ("R13-aut32",    "the Ch.6 opening records the static classification task as history of the first "
                     "two studies without widening the research question",
     "chapters/6_conclusion.tex",
     r"studies paired next-category prediction with a static category classification task, and\s+the "
     r"pair changed in the final study", True),
    # R13-aut35a: a NEW NUMBER about a third party's dataset, so it is pinned. TWO-SCOPE NOTE: the
    # Gowalla window is guarded separately by R8-vintage, which requires the literal string
    # "August 2011"; this probe guards the Istanbul addition in the same item. BOTH must hold and
    # neither substitutes for the other, because an edit could satisfy either one while breaking the
    # other half of the same limitation. The prose deliberately says "seven in ten" rather than 70.7%,
    # so the probe anchors the prose form and the exact figure lives in the provenance comment with the
    # command that produced it.
    ("R13-aut35a",   "the data-vintage limitation states the Istanbul two-block window and that most of "
                     "its volume is the earlier block, so the limitation covers all six datasets",
     "chapters/6_conclusion.tex",
     r"two separate periods, 2012 to 2013 and 2017 to 2018,\s+with none in between, and roughly seven "
     r"in ten belong to the earlier period", True),
    ("R13-aut35b",   "the transductive limitation cites the two identified poles instead of asserting a "
                     "bare generality about other people's work",
     "chapters/6_conclusion.tex",
     r"The place-level representation it builds\s+on~\\cite\{huang2023hgi\}", True),
    # R13-aut35c / R13-lim6live are the two halves of one repair and BOTH are required. The second is
    # the load-bearing one: limitation 6 had been commented out in the working tree, which left the
    # section claiming "Six limitations" while rendering five and silently repointing the limitation~N
    # tags in §6.4. A probe on the added sentence ALONE would not catch that, because live_text() strips
    # comments, so commenting the whole item out would remove the added sentence too and the probe would
    # simply fail without saying why. R13-lim6live names the cause.
    ("R13-aut35c",   "the task-pair limitation explains why the resolving ablation is not clean, marked "
                     "as design inference rather than measurement",
     "chapters/6_conclusion.tex",
     r"This follows from the design of the representation and was not measured, so\s+the confound is "
     r"bounded by the fixed-pair control rather than removed", True),
    ("R13-lim6live", "and limitation 6 is LIVE, not commented out: the section says `Six limitations` "
                     "and §6.4 ties future-work items to limitation numbers, so losing the item makes "
                     "the count false and repoints every tag after it",
     "chapters/6_conclusion.tex",
     r"\\item \\textbf\{The task-pair confound\.\}", True),
    ("R13-aut36a",   "§6.4 adds the initialization-coupling and hypergraph items under limitation 3, "
                     "without inventing a limitation to host them",
     "chapters/6_conclusion.tex",
     r"a hypergraph\s+formulation, in which one edge joins the several visits of a session", True),
    # R13-aut36b guards the TENSE of the next-place item. Next place is a gated scope exclusion
    # (R12-fplace, R12-fplace2), so the conditional is what keeps this item from reading as a capability
    # the dissertation already has. The author's own phrasing ("já conseguimos usar") is the banned form.
    ("R13-aut36b",   "and the next-place item stays conditional, so a gated scope exclusion is not "
                     "contradicted by the future work that proposes lifting it",
     "chapters/6_conclusion.tex",
     r"reusing the existing check-in-level\s+representation would require a change to the input "
     r"pipeline and one additional output", True),
    ("R13-aut36lim6","and the future-work item tied to limitation 6 no longer proposes the ablation "
                     "that the same limitation explains cannot be run cleanly",
     "chapters/6_conclusion.tex",
     r"needs a static target\s+that the check-in-level representation does not already carry as an "
     r"input feature", True),
    # R13-aut29 / R13-aut29b: the §2.3 promotion, and BOTH halves are needed for different reasons.
    # The first pins the HIERARCHY: "Gradient conflict" is a \subsection, sibling of "Multi-objective
    # optimization", not a \subsubsection nested under it. Anchored as an ABSENT probe on the nested
    # form because that is the state being prevented, and the string "subsubsection{Gradient conflict}"
    # appears in no provenance comment (the comments describe the promotion, they do not quote the old
    # heading), so there is no R12-notwrong risk here.
    ("R13-aut29",    "`Gradient conflict` is a subsection, not a subsubsection nested under "
                     "multi-objective optimization, so the problem is stated before the formalism "
                     "without a child preceding its own parent",
     "chapters/2_fundamentals.tex",
     r"\\subsubsection\{Gradient conflict\}", False),
    # R13-aut29b pins the ORDINAL SEQUENCE, which is the part that goes stale silently. §2.3 walks the
    # reader through numbered design choices, and promoting a subsection renumbered them: multi-objective
    # optimization moved from "second" to "third", and the promoted subsection needed the "second" that
    # was freed. A structural edit that reorders these subsections again without touching the prose
    # would leave the ordinals lying, and nothing else in the suite would notice.
    ("R13-aut29b",   "and the design-choice ordinals match the post-promotion order: conflict is the "
                     "second choice and multi-objective optimization the third",
     "chapters/2_fundamentals.tex",
     r"The second design choice depends on a quantity rather than on a preference", True),
    ("R13-aut29c",   "and multi-objective optimization is numbered third and opens on the problem it "
                     "inherits rather than on the scalar objective",
     "chapters/2_fundamentals.tex",
     r"The third design choice is how several task losses determine one parameter update\. A\s+"
     r"measured conflict has to be acted on somewhere", True),
    # R13-aut37 / R13-aut37b / R13-aut37c: the §6.2 reordering into four movements. The three probes pin
    # the three things the reordering is FOR, because the section could be re-flattened without any of
    # them failing individually.
    # R13-aut37 pins MOVEMENT 3, the movement the section did not have. It is the whole point of the
    # item, and its material is the controls' negative findings read together.
    ("R13-aut37",    "§6.2 carries the movement that states what the initial expectation got wrong, "
                     "framed as a correction of an expectation rather than of a result",
     "chapters/6_conclusion.tex",
     r"One premise did not survive the controls, and it concerns the mechanism rather than the\s+"
     r"outcome", True),
    # R13-aut37b pins the CORRECTED MECHANISM CLAIM, which is the honest core of movement 3: relatedness
    # motivated the joint model and is not, on this evidence, the source of its advantage. Anchored on
    # the hedge ("on this evidence") as well as the claim, because dropping the hedge would turn a
    # scoped reading of three controls into a general statement about multitask learning.
    ("R13-aut37b",   "and it names the corrected mechanism with its hedge intact: relatedness motivated "
                     "the joint model and is not, on this evidence, the source of its advantage",
     "chapters/6_conclusion.tex",
     r"is not, on this evidence,\s+the source of that model's advantage", True),
    # R13-aut37c pins the premise POINTER rather than a restatement of the field's expectation. The draft
    # of this section originally asserted what "the usual reading of multitask learning" expects, which
    # is a claim about other people's work and would have needed the author's C2 sign-off. Pointing at
    # §2.3, which states the expectation in the document's own voice and cites caruana1997multitask for
    # it, keeps the claim internal and already approved. A later edit that replaces the pointer with a
    # restatement reintroduces the sign-off debt silently, which is what this probe prevents.
    ("R13-aut37c",   "and the expectation is cited to the chapter that already states it rather than "
                     "restated as a new claim about the field",
     "chapters/6_conclusion.tex",
     r"Section~\\ref\{sec:fund:mtl\} states the expectation under which these models were built",
     True),
    # R13-filmfirst: FiLM is expanded at its FIRST use in the chapter. Added 2026-08-04 after a reviewer
    # finding: moving the expansion out of §2.2.3.1 and into §2.3.1 (AUT-22, via GER-06) left the bare
    # acronym in §2.2.4 EARLIER than any expansion, which is the same defect AUT-30 had just fixed for
    # OOD. Two-scope note: the abbreviations list in content.tex also carries FiLM, and that entry is NOT
    # a substitute for this one. A list entry makes an acronym resolvable; expansion at first use is what
    # WRITING_LAW requires of the prose, and the two are checked separately.
    ("R13-filmfirst","FiLM is expanded where the chapter first uses it, in the model-lineage subsection, "
                     "not only later where the mechanism is explained",
     "chapters/2_fundamentals.tex",
     r"residual layers conditioned by Feature-wise Linear Modulation \(FiLM\) as its\s+shared middle",
     True),

    # ---- round 14, the CoUrb preface protocol sentence -------------------------------
    # The author asked for the sentence to be deleted on the premise that CoUrb had used
    # Chapter 5's protocol. It had not. CoUrb's own code of record (github.com/TarikSalles/
    # Spatial_Embeddings, PoiMtlNet_Novo/src/etl/mtl/create_fold.py) builds folds with
    # StratifiedKFold at :223, calls next_skf.split(x_next, y_next) at :255 with NO groups=
    # argument, and drops userid from the feature frame at :195 -- so one user's windows can
    # land in both sides, which is sample-stratified, not user-disjoint. Chapter 3 states the
    # same splitter for CBIC (3_cbic/results.tex). So the two chapters DO share a protocol,
    # which is the author's point, but the shared one is the sample-stratified one. Resolution
    # (author-chosen, of three offered): keep the protocol fact, drop the "weaker protocol"
    # judgment and the singling-out of CoUrb, and say the two chapters share it.
    # RPV-01 guards the removal, RPV-02 the replacement. Both are needed: without RPV-02 a
    # future sweep could delete the sentence outright and RPV-01 would still pass.
    ("RPV-01", "4_courb.tex's preface no longer calls its protocol weaker than Chapter 5's, and no "
               "longer presents the sample-stratified split as this chapter's alone",
     "chapters/4_courb.tex",
     r"a weaker protocol than the user-disjoint", False),

    ("RPV-02", "and the preface states instead that Chapters 3 and 4 share one sample-stratified "
               "protocol, so the protocol disclosure survives the rewording",
     "chapters/4_courb.tex",
     r"share one evaluation protocol, which\s+stratifies the cross-validation split by sample rather than by user",
     True),

    # ---- round 14, the standalone rule for the article bodies -------------------------
    # Author's rule: the reproduced article bodies of Chapters 3-5 must read as standalone
    # papers, so no file under chapters/{3_cbic,4_courb,5_mobiwac}/ may reference a sibling
    # chapter, a dissertation appendix, or a frame section. Seven sites were rewritten this
    # round. The chapter PREFACES (chapters/3_cbic.tex, 4_courb.tex, 5_mobiwac.tex) are
    # EXEMPT and deliberately so: NORTH_STAR "Ch.3/4/5 prefaces" requires the cross-chapter
    # time-capsule framing there, and a preface is dissertation frame, not article text.
    # An internal Section~\ref inside one article is also legal and expected -- a standalone
    # paper cross-references its own sections. These probes therefore target ONLY the
    # cross-document forms: Chapter~\ref{ch:...}, Appendix~\ref{apx:...}, ref{sec:fund...}.
    # STL-01..04 are absence probes, one per body file that had a violation, so a
    # regression names the file. STL-05 guards the replacement wording that carries the
    # protocol disclosure, which must survive the removal of the Chapter 5 comparison.
    ("STL-01", "3_cbic's results body no longer points forward to Chapter 5 for the protocol "
               "comparison, while keeping the sample-stratified and single-seed disclosures",
     "chapters/3_cbic/results.tex", r"Chapter~\\ref\{ch:", False),

    ("STL-02", "4_courb's related-work body introduces MTLnet by citation rather than by chapter",
     "chapters/4_courb/related.tex", r"Chapter~\\ref\{ch:", False),

    ("STL-03", "4_courb's results body no longer points forward to Chapter 5",
     "chapters/4_courb/results.tex", r"Chapter~\\ref\{ch:", False),

    ("STL-04", "5_mobiwac's related-work body names neither a sibling chapter nor the "
               "gradient-cosine appendix nor the containing dissertation",
     "chapters/5_mobiwac/02_related.tex",
     r"Chapter~\\ref\{ch:|Appendix~\\ref\{apx:|this dissertation", False),

    ("STL-05", "and the sample-stratified disclosure survives in both results bodies, so making "
               "them standalone did not drop the limitation the pointers were attached to",
     "chapters/3_cbic/results.tex",
     r"stratified splitter over the samples rather than over the users", True),

    # ---- round 14, the title-page advisor label -------------------------------------
    # abntex2-UFV.sty hardcoded the Portuguese literal "Orientador:" and commented out the
    # language-aware \imprimirorientadorRotulo above it, so an English-frame document printed
    # one Portuguese word on an otherwise English title page while the signature page a few
    # lines below already read "Adviser". \orientadorname is "Supervisor:" under the english
    # option (abntex2.cls:183 -- the same block that yields this document's "APPENDIX",
    # "Abstract", and "List of abbreviations and acronyms"), so the macro needed restoring,
    # not relabelling. Verified in the RENDER: title page reads "Supervisor: Fabricio Aguiar
    # Silva", with zero occurrences of "Orientador".
    # NOTE: the hardcoded line is inherited from UFV's own template, so this is a deliberate
    # deviation from the supplied file and the probe is what keeps it from being re-applied
    # by a later template refresh without anyone noticing.
    ("ORI-01", "abntex2-UFV.sty no longer hardcodes the Portuguese advisor literal on the "
               "title page",
     # NB: this engine matches with re.I ONLY, never re.MULTILINE (see the note near the top of
     # this file), so "^" anchors at STRING START and cannot match mid-file. The first version of
     # this probe was r"^\s*\{Orientador:~" and therefore never fired -- it reported "holds" even
     # with the Portuguese literal restored. Sabotage validation is what caught it. No anchor here.
     "abntex2-UFV.sty", r"\{Orientador:~\\imprimirorientador", False),

    ("ORI-02", "and it uses the language-aware label macro instead, which resolves to "
               "Supervisor: under the english class option",
     "abntex2-UFV.sty", r"\{\\imprimirorientadorRotulo~\\imprimirorientador\\par\}", True),
    # ---- THE FOLD PARTITION AND THE SEEDS, 2026-08-04. The author caught a false claim in Appendix A and
    # it had propagated to four other files. The false version: the partition is fixed at seed 42, and only
    # the initialization varies across the four seeds. Both halves are wrong. src/data/folds.py passes the
    # run's seed into StratifiedGroupKFold(random_state=...) at :1159, :1247 and :1453; the only literal 42
    # in that file is the DEFAULT value of the seed parameter at :1061; scripts/train.py:1874 passes
    # seed=config.seed from --seed; and the canon guard at train.py:1961 calls 42 the development seed and
    # requires --seed in {0,1,7,100} for paper-grade numbers. Measured with a same-seed control: roughly
    # four users in five change fold when the seed changes. Full record and the reverification commands:
    # science/fold_partition_and_seeds.md.
    #
    # WHY EIGHT PROBES FOR ONE CORRECTION. The claim lived in five files, and a probe on any one of them
    # would leave the others free to drift back into contradiction. Each PRESENT-type probe pins the
    # corrected wording where it lives; the one ABSENT-type probe pins the false phrase.
    # WHY THE ABSENT PROBE IS SAFE, corrected 2026-08-05. This note used to say the provenance comments
    # "DESCRIBE it without reproducing the string the pattern matches". That is false:
    # apx_a_contributions.tex:94 quotes "a fixed partition seed of 42" verbatim to record what was fixed.
    # The probe holds for a different and stronger reason -- this gate reads live_text(), which strips
    # unescaped % comments before matching, so a phrase quoted inside a comment is invisible to it by
    # construction. The consequence for whoever edits next: quoting a retracted phrase in a comment is safe
    # HERE, but a probe on a file this gate does not comment-strip would behave differently.
    ("R13-foldseed",  "Appendix A says the partition seed is the run's seed, not a fixed 42",
     "chapters/apx_a_contributions.tex",
     r"and the run's\s+seed as the partition seed", True),
    ("R13-foldseed2", "and the retracted `fixed partition seed of 42` is gone from Appendix A",
     "chapters/apx_a_contributions.tex",
     r"fixed\s+partition seed of 42", False),
    ("R13-foldseed3", "Appendix A states that a seed sets BOTH the initialization and the partition, so "
                      "four seeds draw four partitions",
     "chapters/apx_a_contributions.tex",
     r"A seed\s+sets both the random initialization and the partition, so the four seeds draw four\s+"
     r"user partitions", True),
    # R13-foldseed4 pins the SURVIVAL ARGUMENT for the paired tests, the part a later editor is most likely
    # to cut as redundant. Without it the corrected text raises a question it does not answer: if the
    # partitions differ across seeds, why is a paired test valid? The answer (pairing is within a seed; the
    # tests pair per-seed means) has to travel with the correction.
    ("R13-foldseed4", "and it records why the paired comparison still holds: pairing is within a seed and "
                      "the tests pair per-seed means, so no fold identity across seeds is assumed",
     "chapters/apx_a_contributions.tex",
     r"the tests pair the per-seed means, so they never\s+assume that a given fold of one seed is the "
     r"same fold of another", True),
    ("R13-foldseed5", "Ch.1's empirical bullet says each seed draws its own partition and that the "
                      "intervals therefore cover both sources of variation, sampled at four draws",
     "chapters/1_introduction.tex",
     r"Because each seed draws its own partition, the reported intervals\s+cover variation from both the "
     r"initialization and the user split, sampled at four\s+draws", True),
    ("R13-foldseed6", "Ch.2's definition of a seed names both axes and explains that the seed "
                      "changes both sources of variation",
     "chapters/2_fundamentals.tex",
     r"It determines the model's\s+random initialization and how users are divided among the five "
     r"folds.*The results include variation from both the random initialization and the user\s+"
     r"partition because the seed changes both", True),
    # R13-foldseed7 / R13-foldseed8 guard the SUBMITTED chapter, and both halves are pinned because that
    # section carried two separate false statements: one in the seed definition, one in the
    # equivalence-precision sentence. Fixing either alone would leave the section self-contradictory. The
    # same correction was applied to the original manuscript at articles/[mobiwac]/src/sections/05_setup.tex
    # on the author's instruction to keep the two in sync; that file is outside this gate's scope, so the
    # sync is recorded in articles/[mobiwac]/ERRATA.md rather than probed here. (Corrected 2026-08-05: this
    # said "the MobiWac errata table", i.e. src/tables/mobiwac/errata_scope.tex. No row was added there,
    # because that table's own header records the standing policy for a paper under review -- apply the
    # correction to both texts and log it, rather than add an erratum row.)
    # Pattern updated 2026-08-05 with the prose it guards: "both models read the same folds" became "both
    # models are built from the same partition" after a reviewer found the stronger form asserted as a
    # measured fact when it is a code-level property (same splitter call, same seed, same rows), never
    # verified against saved fold indices. The probe now pins the softened claim, so restoring the stronger
    # one turns it red.
    ("R13-foldseed7", "Ch.5's seed definition says the seed sets the initialization and the partition, and "
                      "that within a seed both models are BUILT FROM the same partition (a code-level "
                      "property, not a measurement on saved indices)",
     "chapters/5_mobiwac/05_setup.tex",
     r"it sets the random initialization and the user partition, so each seed draws its own division of "
     r"the users, and within a seed both models are built from the same partition", True),
    ("R13-foldseed8", "and Ch.5's equivalence sentence measures precision across the four partitions "
                      "rather than on one fixed partition",
     "chapters/5_mobiwac/05_setup.tex",
     r"measured across these four partitions", True),
    # R13-foldseed9 closes the sweep. Found by the exhaustive pass the author asked for after the first
    # five files were corrected ("valide no restante da dissertação se isso nõa impactou alguma outra
    # parte appendix, documentações e afins"): four patterns over every .tex with comments stripped and
    # every .md, which turned up this last live prose occurrence plus defects in GLOSSARY.md:81, :102,
    # WRITING_LAW.md:181 and science/mtl_v17_complete_picture.md:281. The sweep and what each hit turned
    # out to be are tabulated in science/fold_partition_and_seeds.md §9.
    # NOT A DEFECT, and recorded so a later sweep does not "fix" them: apx_h_check2hgi_joint_model.tex:229
    # and :432 say "Seed 42", and that is TRUE — it is the seed of the representation-training stage, a
    # single fit, not the fold partition of the reported experiment.
    ("R13-foldseed9", "Ch.6's protocol summary says each seed draws its own partition, which was the "
                      "last live prose occurrence of the retracted `one fixed set of five folds`",
     "chapters/6_conclusion.tex",
     r"four seeds, each drawing its own five-fold user partition", True),
    # R13-mech-soft: the §7 mechanism passage is LIVE in the dissertation copy. It was found commented out
    # here under a marker %[AUTHOR COMMENT] while still live in the paper source, and the author ruled on
    # 2026-08-05 that this was a note parked for his attention rather than a removal ("A parked note --
    # restore it"). Restored, so both copies match NEEDS_SIGN_OFF 28 and ERRATA.md:212-228, which record
    # this softened wording as present in BOTH texts.
    # THIS PROBE GUARDS THE SOFTENED FORM, NOT MERELY ITS PRESENCE. The pattern pins "a property of the
    # joint architecture rather than of cross-task transfer", which is the wording that replaced a claim
    # crediting the shared trunk with the category lift. The author asked for the stronger version and it
    # was declined on evidence (NEEDS_SIGN_OFF.md:1516-1536: the gain survives removal of the trunk in four
    # separate studies), his ruling being "suavizar, sem desenvolver alem disso por hora". A later agent
    # restoring the stronger attribution, or re-parking the passage in one copy only, turns this red.
    ("R13-mech-soft", "the Ch.5 mechanism passage is live and keeps the softened attribution: the gain is "
                      "a property of the joint architecture, not of cross-task transfer",
     "chapters/5_mobiwac/07_discussion.tex",
     r"a\s+property of the joint architecture rather than of cross-task transfer", True),
    # ---- §7 DISCUSSION AND LIMITATIONS, redone 2026-08-05 on the author's instruction to delete and redo
    # whatever was wrong there. Four corrections, each applied to BOTH the dissertation copy and the
    # submitted paper source under the standing sync policy. Audit: _history/_round13/80_discussion_audit.md.
    #
    # (1) THE UNSOURCED RATIO. R13-ratio-abs is ABSENT-type and is the load-bearing one: the deleted phrase
    # was a DERIVED quantity in prose (AGENT_GUARDRAILS §2 N2 forbids it), sourced only to a planning
    # document's "Ready-to-paste replacement" sentence, computed from a superseded 65.66 while the chapter
    # reports 65.69, against the random floor BRIDGING_METRICS.md:21-22 tells the reader NOT to use. Honesty
    # flag F7 had already marked the line [VERIFY at adaptation] and it was never discharged. Safe as an
    # absence probe: the provenance comment describes the phrase without reproducing the matched string.
    ("R13-noratio",   "the anticipatory-set sentence keeps its two traced numbers and drops the computed "
                      "enrichment ratio",
     "chapters/5_mobiwac/07_discussion.tex",
     # [2026-08-12] REPOINTED: the shortlist share was recomputed on the final board (64.54, the
     # California joint Acc@10 cell). The probe's purpose is unchanged, that the sentence keeps its
     # traced numbers and carries no computed enrichment ratio.
     r"ten regions out of \$8\{,\}501\$ contain the true next region \$64\.54\$\s+percent of the time", True),
    ("R13-ratio-abs", "and the unsourced `times better than picking ten at random` multiplier is gone",
     "chapters/5_mobiwac/07_discussion.tex",
     r"times better than picking ten at", False),
    #
    # (2) THE WIDER-SEARCH SCOPE. The mitigation was stated of "the dedicated model" unqualified inside a
    # paragraph bounding the bias for BOTH tasks, while 06_results.tex:95 says "the dedicated region models
    # use the strongest fixed configuration". Two probes because the correction has two halves and either
    # alone would be incomplete: the scope qualifier, and the explicit statement that region runs fixed.
    ("R13-sweepscope", "the wider-search mitigation is scoped to the category comparison, which is the "
                       "only side that receives a per-dataset sweep",
     "chapters/5_mobiwac/07_discussion.tex",
     r"and, for the category comparison, the dedicated model receives the wider search", True),
    # [2026-08-12] REPOINTED. The clause this pinned was rewritten when a census of the tuning arms on
    # disk (docs/results/closing_data/v18_sweep/) showed the dedicated category search does NOT reach
    # California, so "at every dataset" was false at four sites and "where that search applies" did not
    # say where. The probe guards the same property: the region comparison is stated to run a fixed
    # configuration on both sides, and the conservative reading is attached to the comparison it is
    # licensed for, now with the dataset the license excludes named.
    ("R13-sweepscope2","and the region comparison is stated to run a fixed configuration on both sides, so "
                       "the conservative reading is attached to the comparison it is licensed for",
     "chapters/5_mobiwac/07_discussion.tex",
     r"both sides of the region comparison run a fixed configuration.*Where the dedicated\s+search is the "
     r"wider of the two, the residual favors the dedicated model, which makes the reported\s+category "
     r"difference conservative there",
     True),
    #
    # (3) THE FOURTH LIMIT. R13-limitcount pins the COUNT, not just the text, because the count is the
    # completeness claim: ERRATA.md:73-80 records it being raised from "Two" to "Three" precisely to admit a
    # disclosed threat, so a later edit that adds or drops a limit without touching the number reintroduces
    # the defect. R13-leak4th2 pins the RESIDUAL clause separately, because that clause is what keeps the
    # sentence from reading as a clean bill of health: RESCREEN.md:94-95 records the linear gate missing one
    # leak, so "bounds only ... a linear read" is doing real work and must not be trimmed as hedging.
    # [2026-08-12] REPOINTED from "Four" to "Five". The probe's PURPOSE is the completeness claim,
    # not the numeral: the count must match the ordinals the paragraph actually names. Two limits
    # were added here (the capacity confound on the region advantage, and the forward-only edge
    # construction), so the enumeration reads First..Fifth and the count moves with it. Verified by
    # extracting the ordinals from live text, not by reading the sentence.
    # [2026-08-12] REPOINTED five -> four. The capacity limit was withdrawn on the author's ruling
    # together with the parameter-count control it pointed at (relocated to the supplementary volume;
    # reasoning at its former include site in content.tex). The enumeration now names four members and
    # the former Fifth is renumbered Fourth. The probe still guards the same property: that the count
    # word agrees with the members named.
    ("R13-limitcount","§7's enumeration says four limits, matching the four it now names",
     "chapters/5_mobiwac/07_discussion.tex",
     r"Four limits qualify these results", True),
    ("R13-leak4th",   "and the fourth names the forward-edge channel in the same modal terms §5 uses, "
                      "with the screen it was given",
     "chapters/5_mobiwac/07_discussion.tex",
     # [2026-08-12] REPOINTED. The fourth/fifth limits were rewritten to state the forward-only
     # construction as the design rather than as a screened-for hazard, which is what the graph
     # actually does and what the method section now says. The probe still requires the paragraph
     # to name the channel and its direction.
     r"the graph does not pass information from a later\s+visit back to an earlier\s*one", True),
    ("R13-leak4th2",  "and it carries the residual rather than presenting the screen as clearance",
     "chapters/5_mobiwac/07_discussion.tex",
     # [2026-08-12] REPOINTED with R13-leak4th. The residual this probe guarded was the residual of
     # a screen; with the construction stated as the design there is no screen to qualify. What must
     # survive is the reason the direction matters, which the sentence now carries.
     r"keeps a node from carrying a feature of the target it is\s+used to predict", True),
)

# COD-016b needs a STRUCTURAL probe, not a string one, so it lives here rather than in PROBES --
# and it was MISSING FROM BOTH LISTS until a reviewer noticed, which made the docstring's claim to
# re-measure every APPLIED row false by omission. Exactly the defect this file exists to catch,
# in this file. Fixed by adding the probe, not by narrowing the claim.
#
# A TRAP WORTH THE PARAGRAPH: Chapter 5's setup section holds TWO substantial passages, and they
# belong to DIFFERENT findings. COD-006 is the PROTOCOL paragraph ("A claimed gain and a claimed
# match..."), which the author did not ask to split. COD-016b is the INTEGRITY passage, whose
# paragraph structure he approved in round 8 and whose didactic rewrite he requested on 2026-08-04.
# Anchor on its own heading, never on the length of the neighboring protocol paragraph.
INTEGRITY_ANCHOR = r"\emph{Integrity of the representation.}"


def integrity_paragraph_probe() -> tuple[bool, str]:
    """COD-016b: the integrity argument must remain divided into readable paragraphs."""
    path = SRC / "chapters/5_mobiwac/05_setup.tex"
    if not path.exists():
        return False, "05_setup.tex not found"
    raw = path.read_text(encoding="utf-8", errors="replace")
    j = raw.find(INTEGRITY_ANCHOR)
    if j < 0:
        return False, f"anchor absent: {INTEGRITY_ANCHOR!r} -- the block was reworded or removed"
    start = raw.rfind("\n\n", 0, j)
    m = re.search(r"\\(sub)*section\{", raw[j:])
    seg = raw[start : j + m.start()] if m else raw[start : j + 6000]
    live = "\n".join(l for l in seg.split("\n") if not l.lstrip().startswith("%"))
    paras = [re.sub(r"\s+", " ", q).strip() for q in re.split(r"\n\s*\n", live) if q.strip()]
    longest = max((len(q) for q in paras), default=0)
    ok = len(paras) >= 4
    return ok, f"{len(paras)} paragraph(s), longest {longest} chars (was 1 of ~3,900)"

# Probes retired because the AUTHOR withdrew the underlying instruction. These are NOT passes and
# NOT failures: the finding no longer describes anything the document is supposed to contain.
#
# They are printed anyway, every run. A probe deleted in silence shrinks the gate's scope without
# telling anyone, and this suite's prose scope has silently shrunk twice already (check.sh, the
# chapters/*/*.tex and preamble.tex cases). The reason is quoted from the author verbatim so a later
# reader can tell "he decided against it" from "somebody dropped it", which is the exact distinction
# LEFT_OUT.md exists to preserve.
RETIRED: dict[str, str] = {
    "COD-018": (
        "per-role CoUrb credit in Appendix A -- WITHDRAWN by the author in PENDENCIAS.md 5.8: "
        '"Nao precisa mexer nisso, pode remover essa preocupacao." Reconfirmed in session '
        "2026-07-30 when the round-8 brief asked for it anyway; a credit claim about a "
        "co-authored paper is his alone to make (GUARDRAILS C2), so the probe goes rather than "
        "the decision. Recorded in LEFT_OUT.md LO-11."
    ),
}

# Claims whose subject is a PROCESS, not a string in the source. Listed by name so the report
# covers them; asserting them mechanically would require re-running the process itself.
NOT_CHECKABLE = {
    "COD-001": "resolved-and-stayed-resolved: covered by check_trapped_prose instead",
    "COD-008": "every citation audited at its source of record -- a process, see the source ledger",
    "COD-009": "the L5 translation-fidelity gate ran -- a process",
    "COD-012": "UFV submission gate -- covered by sync_page_counts and the numbering check",
    "COD-017": "figure type size -- an author decision, PENDENCIAS 2.5",
    "R13-aut30b": (
        "the abbreviations-list exclusion comment in content.tex now carries RE-MEASURED per-acronym "
        "counts (OOD 2, CI 1, UFV 3 live occurrences; STL/CV/GRU/SGKF/PPGCC genuinely 0) instead of the "
        "false blanket claim that all eight 'never appear in prose'. UNPROBEABLE BY CONSTRUCTION: the "
        "corrected text lives inside a % comment, and this gate matches on live_text() with comments "
        "stripped (docstring trap 1), so the token is present in the raw file and absent from the text "
        "the instrument reads. Measured both ways before listing it here. The PROSE half of AUT-30 -- "
        "OOD expanded at first use -- IS probed, by R13-aut30. Re-measure with, from "
        "articles/dissertacao/src:  for a in STL CV GRU OOD CI SGKF UFV PPGCC; do n=0; for f in "
        "$(find . -name '*.tex' -not -path './build/*'); do n=$((n+$(grep -vE '^[[:space:]]*%' \"$f\" | "
        "grep -ow \"$a\" | wc -l))); done; echo \"$a $n\"; done"
    ),
}


def strip_text(raw: str) -> str:
    """The stripper itself, on a string, so it can be self-tested without a file on disk.

    Split out from live_text on 2026-07-30 (COD-006a): the self-test used to assert that the
    string "well powered" was PRESENT in the live Chapter 5 source, because at the time that
    was the escaped-percent case it needed. Applying the fix that probe exists to check would
    therefore have crashed the gate on an AssertionError, which is a self-test that fails when
    the document becomes correct. The property being proved is about the stripper, not about
    any one sentence, so it is now proved on literals that cannot drift.
    """
    keep = []
    for line in raw.split("\n"):
        m = COMMENT.search(line)
        cut = line[: m.start()] if m else line
        if cut.strip():
            keep.append(cut)
    return re.sub(r"\s+", " ", " ".join(keep))


def live_text(path: Path) -> str:
    """Source with comments removed, joined into one whitespace-normalized string.

    Joined on purpose: a claim whose numbers wrap to the next line is invisible to a per-line
    regex, and that produced a false NOT-APPLIED on NUM-4. See trap 2 in the module docstring.
    """
    return strip_text(path.read_text(encoding="utf-8", errors="replace"))


def self_test() -> None:
    """Both directions on the stripper, against the two real cases that fooled it.

    On LITERALS, not on live sentences. Both literals are reductions of the actual defects:
    the escaped-percent case is the shape of 5_mobiwac/05_setup.tex line 94, where `90\\%` at
    column 763 truncated a 2,068-character paragraph and hid the target clause at column 1848;
    the comment case is the shape of apx_c_ai_disclosure.tex, whose two "Opus" mentions are
    both inside `%` comments saying why it is NOT in the prose.
    """
    # Direction 1: an ESCAPED percent is not a comment. Everything after it must survive.
    esc = strip_text(r"a 90\% interval and then THE_TAIL_TEXT after it")
    assert "THE_TAIL_TEXT" in esc, (
        "self-test: an escaped \\% truncated the line and hid the text after it -- the comment "
        "pattern must be (?<!\\\\)% . Reporting now would turn a present defect into a pass."
    )
    assert r"90\%" in esc, "self-test: the escaped percent itself was eaten"
    # Direction 2: a REAL comment must be excluded, including an indented one and a trailing one.
    com = strip_text("prose survives\n   % INDENTED_COMMENT_TEXT\ncode % TRAILING_COMMENT_TEXT")
    assert "INDENTED_COMMENT_TEXT" not in com and "TRAILING_COMMENT_TEXT" not in com, (
        "self-test: a real % comment leaked into the live text -- every probe would then read "
        "provenance commentary as prose, which is how COD-013 was first scored as APPLIED."
    )
    assert "prose survives" in com and "code" in com, "self-test: the stripper over-stripped"
    # Direction 3: the stripper must still reach PAST the real escaped percent in the real file.
    # Anchored on a citation key rather than on prose, because a key is guarded by the
    # undefined-citation gate and so cannot be silently reworded the way a sentence can.
    esc_file = SRC / "chapters/5_mobiwac/05_setup.tex"
    if esc_file.exists():
        live = live_text(esc_file)
        assert "lakens2017tost" in live, (
            "self-test: the stripper no longer reaches the TOST citation, which sits 766 "
            "characters past the escaped percent on the same source line. Every probe on this "
            "file would be reading a truncated paragraph."
        )
    # Direction 4 (round 9): the SECOND root must actually resolve, and the stripper must not eat
    # markdown. A probe whose file is read from the wrong root, or whose text the stripper mangles,
    # reports exactly like a probe that never fires -- which is trap 4 in the module docstring,
    # one root over. Anchored on a heading the schema cannot lose without the split being gone.
    assert probe_root("CONSIDERATIONS.md") == UTILS, "self-test: .md probes must resolve under src_utils/"
    assert probe_root("chapters/2_fundamentals.tex") == SRC, "self-test: .tex probes must resolve under src/"
    trk = UTILS / "CONSIDERATIONS.md"
    if trk.exists():
        live_md = live_text(trk)
        assert "### FAB-01" in live_md and "### GER-01" in live_md, (
            "self-test: the tracker's item headings do not survive live_text(), so every R9- probe "
            "would be measuring mangled text. Check the comment stripper against markdown."
        )


def main() -> int:
    self_test()
    bad, missing_files = [], []
    print("== audit APPLIED claims re-measured against the live source ==")
    for fid, what, rel, pat, want in PROBES:
        path = probe_root(rel) / rel
        if not path.exists():
            missing_files.append((fid, rel))
            print(f"  SKIP        {fid:9s} {rel} not found -- probe cannot run")
            continue
        found = bool(re.search(pat, live_text(path), re.I))
        ok = found == want
        if not ok:
            bad.append(fid)
        print(f"  {'holds' if ok else 'NOT APPLIED':11s} {fid:9s} {what}")
    ok, detail = integrity_paragraph_probe()
    if not ok:
        bad.append("COD-016b")
    print(f"  {'holds' if ok else 'NOT APPLIED':11s} {'COD-016b':9s} "
          f"the integrity block is several paragraphs: {detail}")

    for fid, why in sorted(NOT_CHECKABLE.items()):
        print(f"  unprobed    {fid:9s} {why}")
    for fid, why in sorted(RETIRED.items()):
        print(f"  RETIRED     {fid:9s} {why}")

    # V13, applied to this file's own report: a total must reconcile with the rows above it. The
    # count was 8-of-8 for one turn after COD-016b's structural probe was added, i.e. a headline
    # that did not count a row it had just printed -- the exact arithmetic defect V13 names.
    total = len(PROBES) + 1  # string probes, plus the structural COD-016b probe
    held = total - len(bad) - len(missing_files)
    print(f"\n  {held} of {total} probes hold; "
          f"{len(bad)} claim(s) not applied; {len(NOT_CHECKABLE)} process claim(s) unprobed; "
          f"{len(RETIRED)} withdrawn by the author")
    print(f"  ({total} = {len(PROBES)} string + 1 structural; rows printed above must equal "
          f"{total + len(NOT_CHECKABLE) + len(RETIRED)})")
    if missing_files:
        print("  A probe whose file is gone is NOT a pass. Re-point it or retire it deliberately.")
        return 2
    if bad:
        print(f"\nFAIL: {', '.join(bad)} are recorded as APPLIED and are not in the document.")
        print("  Do not re-mark them from a report. Fix the source, then re-run this.")
        return 1
    print("\nOK: every mechanically checkable audit claim is true of the live source.")
    return 0


# ---------------------------------------------------------------------------------------------
# THE CLOSED-ITEM REGISTER was audited for this same defect on 2026-07-30, not trusted:
# _history/_archive/PENDENCIAS_RESOLVIDOS.md carries 16 closed items with 40 commit citations, the identical
# claim shape that failed in CODEX_AUDIT. Its most exposed row (item 1.2, nine checkable artifacts)
# holds for five rows; the other four do not reproduce and are recorded as PENDENCIAS_RESOLVIDOS 2.19 (arquivado 2026-08-02) with the
# reason -- they are STALE, not false: taken in round 6 against a tree that has since gained an
# appendix and lost 0_main.tex, and none records the tree state it was taken against.
# Full audit in _history/_round8/29_pendencias_detail.md. Do not redo it; extend 2.19 if a number moves.
if __name__ == "__main__":
    sys.exit(main())
