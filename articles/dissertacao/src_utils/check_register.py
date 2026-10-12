#!/usr/bin/env python3
"""check_register.py -- the register law: American English, and phrasing a non-native reader takes
in on one reading.

THE TWO DEFECTS IT ANSWERS, both found by the author reading Appendix F in the rendered PDF on
2026-07-30 (PENDENCIAS_RESOLVIDOS 2.22 (arquivado 2026-07-30) points 8, 9 and 12), and neither covered by any rule at the time.
Measured before the rule was written: `grep -cin "british"` over WRITING_LAW.md and
AGENT_GUARDRAILS.md returned 0 and 0. WRITING_LAW §1 said "American English throughout" and named
no British form; nothing at all addressed the second complaint.

  (a) BRITISH ENGLISH. His instance: "feature needs saying plainly". Note what it is NOT: not a
      spelling. It is the British `need`+gerund construction, where American English writes
      "needs to be said plainly". A spelling list would have missed it entirely, so this gate
      covers spellings AND constructions.

  (b) PHRASING A NON-NATIVE WRITER WOULD NOT PRODUCE, which forces a non-native reader to read
      twice. His instances: "Two departures from that flat picture appear" (his note: "pure A.I,
      we can be more simple"), and "Both point away from trouble in any case. A positive cosine is
      mild cooperation, not conflict, and the decline stays inside the margin throughout while
      moving toward zero rather than away from it." (his note: "well written, but is not natural
      for a non native writer in english, and force a non native read more than once").

WHICH HALF IS MECHANICAL, stated plainly because a docstring claiming more coverage than the code
has is itself a defect this repository has shipped:

  CLASS A -- British spellings and constructions -- IS MECHANICAL and is gated hard. A word either
  is the British form or is not. Every family is checked, and the ones that would over-fire on
  American text (the -ise and -our families, whose American members are ordinary words) are
  generated and then filtered through an explicit whitelist rather than hand-listed, because a
  hand-typed list only finds the wording its author imagined (AGENT_GUARDRAILS §4b V17).

  CLASS B -- hard phrasing -- IS PARTLY JUDGMENT. Four shapes are expressible and are gated: a
  delayed subject before a clause-final appearance verb, native-literary idiom, chained
  qualification inside one sentence, and an abstract noun as the agent of a motion verb. What is
  NOT expressible, and is NOT claimed here, is the general question of whether a sentence reads
  on the first pass. That belongs to the readability editor's first-read method
  (`reviewers/15_readability_editor.md`, lens 2, verdict PASS / NEEDS REVISION), which this gate
  points at instead of duplicating. A green Class B is not a first-read PASS.

NOT GATED, ON PURPOSE, and reported to the author instead (see _history/_round9/44_register_law.md):
quotation-final period placement. American style puts the period inside the closing quotation
mark; 13 sites in this tree put it outside. All 13 sit in errata tables and correction rows where
the quoted string is the evidence, and moving a period inside a quotation alters the quotation.
That is a decision about the errata convention, not a spelling error, so it is the author's.

SCOPE INCLUDES THE BIBLIOGRAPHY, and the reason is a finding in itself. This gate first covered
`src/**/*.tex` only and reported clean while `towards` printed on page 82 of the defense build: the
bibliography is not a .tex file. So `references.bib` is swept too, but ONLY the fields we author
(note, annote, abstract, howpublished, addendum). `title`, `booktitle`, `journal`, `series` and
`author` are attributes of record under §1 R2, and the one British form in this bibliography sits in
Xu2023's title, whose title of record at Crossref (10.1145/3582553, checked 2026-07-30) reads
"towards". Correcting it would corrupt an attribute the citation protocol requires be exact.

SCOPE AND THE TRAPS IT AVOIDS, each of which produced a wrong verdict on this project before:
  1. comments are stripped with the same `(?<!\\)%` rule the audit gate uses, because this tree's
     provenance comments quote the very sentences under review (this file's docstring would trip a
     comment-blind checker).
  2. lines are JOINED before matching: a phrase that wraps is invisible to a per-line regex, and
     that trap has produced false verdicts in both directions here.
  3. verbatim quotations (``...'') are masked for the SPELLING families only. A quotation of
     published wording may not be altered, so a British spelling inside one is not this gate's
     business. Constructions and Class B shapes still read the full text.
  4. scope is derived from the filesystem with a FLOOR, never typed. A chapter split silently
     shrank two prose gates' scope on this project and both reported a clean sweep of almost
     nothing.

THE OPEN REGISTER, and it retires itself. Some hits are not this gate's to fix: the two Appendix F
files are owned by a parallel track, and one hit sits in verbatim reproduced published prose where
a change costs an errata row and is the author's call. Those are listed in OPEN_REGISTER with an
owner, printed as OPEN, and excluded from the failure count -- a skip is never silent
(AGENT_GUARDRAILS §4b V7). The entry is self-retiring: when the defect is GONE the gate FAILS and
tells you to delete the entry, so a stale exemption cannot sit there hiding a future regression.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
COMMENT = re.compile(r"(?<!\\)%")
SCOPE_FLOOR = 20

# --------------------------------------------------------------------------------------------
# CLASS A1 -- spelling families.
#
# The -ise and -our families are GENERATED and then whitelisted. A hand-typed list of British
# spellings can only match the words its author thought of, which is how the first draft of this
# sweep reported zero for `-our` while four real hits sat in the tree: the pattern was `\w+our\b`
# and the words present were "neighbourS" and "neighbourHOOD". Generate, then subtract.
# --------------------------------------------------------------------------------------------

# -ise/-yse verbs and their derivatives that are spelled the same in both dialects. These are not
# British forms: the stem ends in -ise for etymological reasons (surprise, comprise), so flagging
# them would make the gate fire on correct American prose.
ISE_SAME_IN_BOTH = set("""
advertise advise appraise apprise arise braise bruise chastise circumcise comprise compromise
concise cruise demise despise devise disguise enterprise excise exercise expertise franchise
guise improvise incise likewise malaise merchandise noise otherwise paradise paraphrase phrase
poise praise precise premise promise raise revise rise supervise surmise surprise televise
treatise wise
""".split())
ISE_SUFFIXES = ("ational", "ations", "ation", "ing", "ers", "er", "es", "ed", "e", "s")
ISE_PREFIXES = ("un", "re", "pre", "non", "de", "dis", "mis", "over", "under", "semi", "co", "inter")
ISE_RE = re.compile(r"\b[A-Za-z]{3,}is(?:e|es|ed|ing|ation|ations|ational|er|ers)\b")

# -our words whose American spelling is also -our (they are not the British -our/-or pair).
OUR_SAME_IN_BOTH = set("""
amour armoury contour detour dour flour floured flouring four fourteen fourteenth fourth fourths
glamour hour hourly hours pour poured pouring pours scour scoured scouring sour sours soured tour
toured touring tourism tourist tourists tours velour your yours
course courses coursed coursework discourse discourses discoursed intercourse
source sources sourced sourcing resource resources resourced resourcing outsource outsourced
outsourcing encourage encourages encouraged encouraging encouragement discourage discourages
discouraged discouraging discouragement devour devours devoured devouring
""".split())
OUR_RE = re.compile(r"\b[A-Za-z]{3,}our[a-z]*\b", re.I)


def _ise_is_british(word: str) -> bool:
    """True when an -ise/-isation form is the British spelling of an American -ize/-ization word.

    The `-wise` family is excluded by RULE rather than by enumeration. `wise`, `likewise` and
    `otherwise` were listed individually in ISE_SAME_IN_BOTH, which is exactly the defect this
    module's own header warns about: a hand-typed list matches only the words its author thought
    of. `elementwise` (round 12) false-fired and turned `make check` red on correct American
    prose; `pairwise`, `coordinatewise`, `rowwise` and any other compound would have done the
    same. The `-wise` suffix means "in the manner of" and has no etymological relation to the
    `-ise`/`-ize` verb pair, so no `-wise` compound is ever a British spelling. Guarded so it
    cannot swallow a real hit: a true `-ise` verb whose stem happens to end in `w` (there is no
    such English verb, but the guard costs nothing) still reaches the checks below, because the
    rule requires the character before `wise` to be a letter that is part of a compound stem of
    at least three characters rather than a bare `-ise` inflection.
    """
    low = word.lower()
    if low in ISE_SAME_IN_BOTH:
        return False
    if low.endswith("wise") and len(low) > 4:
        return False
    for suf in ISE_SUFFIXES:
        if not low.endswith(suf):
            continue
        base = low[: len(low) - len(suf)]
        for cand in (base, base + "e"):
            if cand in ISE_SAME_IN_BOTH:
                return False
            for pre in ISE_PREFIXES:
                if cand.startswith(pre) and cand[len(pre):] in ISE_SAME_IN_BOTH:
                    return False
    return True


def _our_is_british(word: str) -> bool:
    return word.lower() not in OUR_SAME_IN_BOTH


# Explicit families. Written as full inflected forms, not as `\w+`-style stems: a generative
# double-l pattern matches "equally", "controlled" and "unfilled", which are American.
QUOTE_PERIOD = re.compile(r"[a-z0-9)\]](?<!\bal)\.\s*(?:''|\"|\u201d)")
QUOTE_PERIOD_REMEDY = (
    "ABNT NBR 10520:2023: write ...information''. not ...information.'' "
    "(PENDENCIAS_RESOLVIDOS 2.24 (arquivado 2026-08-02), author's ruling of 2026-08-02). A quotation that is itself a complete "
    "sentence keeps its own period inside -- that period belongs to the quoted author.")


SPELLING_RULES: tuple[tuple[str, str, str], ...] = (
    # ADDED 2026-08-02, PENDENCIAS_RESOLVIDOS 2.24 (arquivado 2026-08-02), on the author's ruling: terminal punctuation goes OUTSIDE the
    # closing quotation mark, per ABNT NBR 10520:2023, which is the deposit norm and outranks the
    # house American-English convention. WRITING_LAW carries the rule.
    #
    # THIS RULE RUNS BACKWARDS FROM EVERY OTHER ONE IN THIS FILE. The rest flag a British form and ask
    # for the American one; this flags the AMERICAN form and asks for the ABNT one. It is here rather
    # than in CONSTRUCTION_RULES because it is a spelling-level, mechanical mark, and putting it in the
    # same loop means a single sweep covers both directions.
    #
    # WHY IT IS GATED AT ALL, when the current tree already complies: because compliance here looks
    # like an error to anyone applying American style, and 14 sites carry it. A later pass "fixing"
    # them would be silently reverting the author's ruling -- and 12 of the 14 are errata tables where
    # the quoted string IS the evidence for a correction, so moving a period inside the quotation
    # alters the quotation. That is the failure this rule exists to make loud.
    #
    # The lookbehind excludes an abbreviation-final period ("et al.", "U.S.") from counting as the
    # sentence's terminal mark, and requires a word character before the closing quote so that an
    # empty or macro-only quotation does not match.
    ("-re for -er",
     r"\b[a-z]*(?:centre|metre|litre|fibre|theatre|calibre|sabre|spectre|sombre|lustre|"
     r"manoeuvre|ochre)[a-z]*\b",
     "American: center, meter, liter, fiber, theater, caliber"),
    # The negative lookahead is load-bearing and was added after a false positive that the live tree
    # could not have shown. `-yses` is BOTH the British verb inflection (analyses = he analyses) and
    # the correct American plural of a `-ysis` noun (the analyses agree). The plural appears in this
    # document's bibliography and would appear in prose the day someone writes "both analyses agree",
    # so the noun plurals are excluded by name. Found by sweeping the RENDERED PDF, where the
    # bibliography is in scope; the .tex sweep alone reported clean.
    ("-yse for -yze",
     r"\b[A-Za-z]{3,}ys(?:e|es|ed|ing|er|ers)\b(?<!analyses)(?<!paralyses)(?<!catalyses)"
     r"(?<!dialyses)(?<!electrolyses)(?<!hydrolyses)(?<!photolyses)",
     "American: analyze, paralyze, catalyze"),
    ("doubled l before a vowel suffix",
     r"\b(?:travell(?:ed|ing|er|ers)|modell(?:ed|ing|er|ers)|labell(?:ed|ing)|"
     r"cancell(?:ed|ing)|signall(?:ed|ing)|totall(?:ed|ing)|fuell(?:ed|ing)|"
     r"levell(?:ed|ing)|marvell(?:ed|ous|ously)|counsell(?:ed|ing|or|ors)|"
     r"equalled|equalling|dialled|dialling|channell(?:ed|ing)|panell(?:ed|ing)|"
     r"quarrell(?:ed|ing)|funnelled|tunnelled|refuelled|unravelled|jewellery|woollen)\b",
     "American: traveled, modeled, labeled, signaled, canceled"),
    ("single l where American doubles",
     r"\b(?:skilful[a-z]*|wilful[a-z]*|fulfil(?!l)[a-z]*|instalment[a-z]*|enrolment[a-z]*|"
     r"appal(?!l)[a-z]*|distil(?!l)[a-z]*|enthral(?!l)[a-z]*)\b",
     "American: skillful, willful, fulfill, installment, enrollment"),
    ("-ce noun / -ise verb pair",
     r"\b(?:defenc[a-z]*|offenc[a-z]*|pretenc[a-z]*|licenc[a-z]*|practis[a-z]*)\b",
     "American: defense, offense, pretense, license (noun and verb), practice (noun and verb)"),
    ("-wards adverb",
     r"\b(?:towards|afterwards|backwards|forwards|onwards|upwards|downwards|inwards|outwards|"
     r"sidewards)\b",
     "American: toward, afterward, backward, forward, onward"),
    ("whilst / amongst / amidst",
     r"\b(?:whilst|amongst|amidst|betwixt)\b",
     "American: while, among, amid"),
    ("irregular past in -t",
     r"\b(?:learnt|spelt|burnt|dreamt|leapt|knelt|smelt|spilt|leant)\b",
     "American: learned, spelled, burned, dreamed, leaped"),
    ("-e retained or added",
     r"\b(?:programme[s]?|catalogu(?:e|es|ed|ing)|analogue[s]?|dialogued|ageing|judgement[s]?|"
     r"acknowledgement[s]?|annexe)\b",
     "American: program, catalog, analog, aging, judgment, acknowledgment"),
    ("British lexical choice",
     r"\b(?:grey[a-z]*|sceptic[a-z]*|enquir(?:y|ies|e|ed|ing)|specialit(?:y|ies)|orientated|"
     r"focuss(?:ed|ing)|benefitt(?:ed|ing)|per cent|aluminium|sulphur[a-z]*|tonne[s]?|"
     r"draught[a-z]*|cheque[s]?|tyre[s]?|kerb[s]?|storey[s]?|plough[a-z]*|mould[a-z]*|"
     r"smoulder[a-z]*|moustache|gaol[a-z]*|maths|fortnight[a-z]*|anticlockwise|straightaway|"
     r"outwith)\b",
     "American: gray, skeptic, inquiry, specialty, oriented, focused, percent, aluminum"),
    ("oe / ae digraph",
     r"\b(?:haem[a-z]+|oestrog[a-z]+|foet[a-z]+|anaemi[a-z]+|encyclopaedi[a-z]+|palaeo[a-z]+|"
     r"diarrhoea|manoeuvr[a-z]*)\b",
     "American: hem-, estrog-, fet-, anemi-, encyclopedi-, paleo-"),
)

# --------------------------------------------------------------------------------------------
# CLASS A2 -- British constructions. The author's own instance is the first rule, and it is the
# reason this gate is not a spelling list: "needs saying" is spelled identically in both dialects.
# --------------------------------------------------------------------------------------------
CONSTRUCTION_RULES: tuple[tuple[str, str, str], ...] = (
    ("need / want + gerund",
     r"\b(?:need|needs|needed|want|wants|wanted)\s+(?!to\b)[a-z]+ing\b",
     'the author\'s own instance: "feature needs saying plainly" -> "needs to be said plainly"'),
    ("different to / than",
     r"\bdifferent\s+(?:to|than)\b",
     'American: "different from"'),
    ("bare institution noun",
     r"\b(?:in hospital|at university|to university|in future|at table)\b",
     'American: "in the hospital", "at the university", "in the future"'),
    ("have got",
     r"\b(?:have|has|had)\s+got\b",
     'American: "have", or "must" for obligation'),
    ("shall",
     r"\bshall\b",
     'American: "will" for the future, "must" for obligation'),
    ("at the weekend",
     r"\bat the weekend\b",
     'American: "on the weekend"'),
    ("was sat / was stood",
     r"\b(?:was|were|is|are|been|being)\s+(?:sat|stood)\b",
     'American: "was sitting", "was standing"'),
    ("collective noun with a plural verb",
     r"\b(?:team|group|committee|government|staff|band|community|panel|board|council)\s+"
     r"(?:are|were|have|do)\b",
     'American treats these as singular: "the committee has"'),
    ("providing that",
     r"\bproviding\s+that\b",
     'American: "provided that"'),
)

# --------------------------------------------------------------------------------------------
# CLASS B -- the four expressible hard-phrasing shapes. Each is seeded from one of the author's
# three sentences; the negative samples in self_test() are the sentences it must NOT touch.
# --------------------------------------------------------------------------------------------
_DET = (r"(?:Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Several|One|Both|A|An|The|Some|Many|"
        r"Few|No)")
_PREP = (r"(?:of|in|on|from|to|for|with|within|across|between|among|about|over|under|through|"
         r"throughout|against|beyond|behind|during|toward|towards|into|onto|upon|by|at|around|"
         r"near|per|via|despite)")
_APPEAR = (r"(?:appear|appears|appeared|emerge|emerges|emerged|arise|arises|arose|ensue|ensues|"
           r"recur|recurs|abound|abounds|obtain|obtains|persist|persists|remain|remains|follow|"
           r"follows|exist|exists|occur|occurs|prevail|prevails|intervene|intervenes)")

# B1. The subject is named, then held away from its verb by a prepositional phrase, and the verb
# is an intransitive verb of appearance sitting at the end of the clause. "(?<!as )" spares the
# fixed academic phrase "are as follows", which is not this shape.
SHAPE_DELAYED_SUBJECT = (
    "delayed subject before a clause-final appearance verb",
    rf"\b{_DET}\s+(?:[a-z]+\s+){{0,2}}?[a-z]+s?\s+{_PREP}\s+(?:[a-z']+\s+){{1,6}}?(?<!as )"
    rf"{_APPEAR}\s*(?=[.;:,]|$)",
    'the author\'s instance: "Two departures from that flat picture appear" -- his note was '
    '"pure A.I, we can be more simple". Name the subject and let it act: "The figure shows two '
    'departures."',
)

# B2. Native-literary idiom: correct English that a Brazilian author writing academic prose would
# not produce. "far from" is deliberately absent -- "mobility is far from random" is standard in
# this literature and appears twice in Chapter 2.
SHAPE_IDIOM = (
    "native-literary idiom",
    r"\b(?:in any case|at any rate|by the same token|for that matter|all the same|if anything|"
    r"not least|no small|goes? some way|carr(?:y|ies) the day|speaks? volumes|leaves? much to|"
    r"(?:point|points|pointing|pointed)\s+(?:away|toward|towards)\s+(?:from\s+)?"
    r"(?:trouble|danger|disaster|safety))\b",
    'the author\'s instance: "Both point away from trouble in any case." Two idioms in eight '
    'words. State the reading: "Neither departure indicates a conflict."',
)

# B3. Chained qualification: three or more qualifying connectives and two or more commas inside
# one sentence. His instance runs q=3, c=2 in 25 words.
SHAPE_CHAINED_QUALS = re.compile(
    r"\b(?:while|whereas|though|although|rather than|instead of|as well as|even as|insofar as|"
    r"except that|other than|so long as|throughout|nonetheless|nevertheless|and yet|if anything|"
    r"in any case|at any rate)\b", re.I)
CHAIN_MIN_QUALS = 3
CHAIN_MIN_COMMAS = 2

# B4. An abstract noun as the agent of a verb of VOLITION, COGNITION or SPEECH. A quantity that
# refuses, prefers or admits has been animated; a quantity that rises, falls or moves has not.
#
# THIS RULE WAS NARROWED after it fired on a correct sentence, and the evidence was internal. The
# first version also listed motion verbs (moves, drifts, climbs, stays, points), and two facts
# convicted it. FIRST, the remedy this very rule prints prescribes "the mean FALLS toward zero",
# which is a motion verb: the rule was recommending a rewrite of the shape it banned. SECOND, it
# fired on "the declining cosines stay inside the margin and move toward zero" while staying silent
# on "the mean falls toward zero", and the only difference between them is that `cosine` happens to
# sit in the noun list and `mean` does not. A detector whose verdict turns on which noun someone
# thought to type is measuring its own list, not the prose.
#
# The author's own instance is STILL COVERED, and by the rule that actually describes what is wrong
# with it: "the decline stays inside the margin throughout while moving toward zero rather than away
# from it" carries three qualifiers and two commas, so the chained-qualification shape catches it
# (asserted in self_test). What made that sentence hard was the chain, not the verb.
_ABSN = (r"(?:decline|increase|decrease|rise|fall|drop|gain|loss|gap|margin|cosine|slope|trend|"
         r"picture|pattern|result|finding|answer|question|evidence|reading|verdict|conclusion|"
         r"difference|effect|value|series|curve|distribution|departure|change|mean|number)")
_AGENTV = (r"(?:refuses?|wants?|prefers?|admits?|concedes?|insists?|agrees?|disagrees?|knows?|"
           r"believes?|decides?|chooses?|cares?|worries|hopes?|tells?|speaks?|listens?|watches|"
           r"waits?|remembers?|forgets?|complains?|argues?|claims?|denies)\b")
SHAPE_ABSTRACT_AGENT = (
    "abstract noun as the agent of a volition, cognition or speech verb",
    rf"\b(?:the|a|an|its|their|this|that|both|one|two|each)\s+{_ABSN}s?\s+"
    rf"(?:[a-z]+\s+){{0,2}}?(?:{_AGENTV})",
    'a quantity does not decide, prefer or admit anything. Name the agent: not "the evidence '
    'prefers the joint model" but "the evidence favors the joint model", or say who concluded it. '
    '(A quantity that rises, falls or moves is literal and is NOT this shape.)',
)

# B5. A REDUCED RELATIVE CLAUSE ENDING ON A STRANDED PREPOSITION. WRITING_LAW §1 requires relative
# pronouns be written ("the head THAT we do not predict") and until 2026-08-02 no gate enforced it.
# Persona 15 found the gap while reading the reworked appendix and proposed this pattern; it was the
# mechanism behind two of its four REQUIRED findings, and it is precisely the author's own class --
# grammatical, native-sounding, and a re-read for a non-native reader. His words: phrasing that
# "force a non native read more than once to understand".
#
# The general shape (any omitted relative pronoun) is not reliably expressible. Its worst sub-case
# is: the clause ends on a stranded preposition, which is exactly where the parse breaks. In the
# real defect -- "if the update next-region asks for points against the update next-category asks
# for," -- the reader takes "asks for points" as verb plus object, meets "against", and unwinds.
#
# TWO GUARDS, and both were found by the pattern failing on the CORRECT form rather than by
# reasoning. The determiner alternation includes "that", so a legally written relative pronoun is
# consumed AS the determiner and the raw pattern fires on the very sentence that fixes the defect.
# Guard 1: the match may not START with a relative pronoun. Guard 2, and this is the one a 26-char
# lookbehind got wrong: the pattern can re-match several words to the RIGHT of a clause that already
# has its pronoun ("the reference level THAT one screening argument in the dissertation is read
# against" re-matched at "the dissertation"), so the guard scopes back to the clause head -- the
# previous comma, semicolon or colon -- not a fixed character window.
_STRANDED_PRONOUNS = r"(?:that|which|whom|whose|where|what)"
SHAPE_STRANDED = (
    "reduced relative clause ending on a stranded preposition",
    r"(?<!\bwhat )(?<!\bwhich )(?<!\bthat )(?<!\bwhom )(?<!\bwhere )"
    r"\b(?:the|a|an|its|their|this|that|one|two|each|every|no)\s+"
    r"[a-z][a-z-]{2,}\s+"
    r"(?:[a-z][a-z-]*\s+){0,3}?"
    r"(?:asks?|needs?|uses?|reads?|reports?|gives?|wants?|carries|covers?|leaves?|"
    r"makes?|takes?|looks?|points?|accounts?|calls?|works?|aims?|relies|depends?)\s+"
    r"(?:for|to|of|on|at|with|from|about|against|into|by|upon)\s*(?=[,.;:]|$)",
    'write the relative pronoun: not "the prior the models do not use" but "the prior THAT the '
    'models do not use". The pronoun is what tells the reader a clause is starting; without it the '
    'verb reads as taking the next noun as its object, and the stranded preposition forces a '
    're-parse. An interrogative or an already-written pronoun is legal and is NOT this shape.',
)


def stranded_hits(text: str):
    """Yield SHAPE_STRANDED matches whose clause does NOT already carry a written pronoun.

    Guard 1 skips a match that begins with the pronoun (the alternation eats it as a determiner).
    Guard 2 scopes the lookback to the clause head, because the pattern can re-match to the right
    of a correctly written pronoun. Validated in both directions in self_test().
    """
    for m in re.finditer(SHAPE_STRANDED[1], text, re.I):
        if re.match(rf"\s*{_STRANDED_PRONOUNS}\b", m.group(0), re.I):
            continue
        clause = re.split(r"[,;:]", text[max(0, m.start() - 150):m.start()])[-1]
        if re.search(rf"\b{_STRANDED_PRONOUNS}\b", clause, re.I):
            continue
        yield m


# --------------------------------------------------------------------------------------------
# THE OPEN REGISTER. Present -> reported as OPEN, not counted as a failure. Absent -> the gate
# FAILS and asks for the entry to be deleted, so the exemption cannot outlive the defect.
# (file relative to src/, a literal substring, owner, what closing it costs)
# --------------------------------------------------------------------------------------------
# RETIRED 2026-07-30, the same day they were added, and the mechanism is worth recording because it
# is the only evidence that the self-retiring design works. Four entries held the author's own
# instances open for the parallel Appendix F track:
#     "needs saying plainly"                         (PENDENCIAS_RESOLVIDOS 2.22 (arquivado 2026-07-30) point 8)
#     "Two departures from that flat picture appear" (point 9)
#     "Both point away from trouble in any case"     (point 12)
#     "the decline stays inside the margin throughout while moving toward zero"  (point 12)
# That track landed its rewrite, this gate went RED on the next run naming all four as STALE, and
# they were deleted here. Nobody had to remember to come back: the exemption could not outlive its
# defect, which is what §4b V14 asks of every APPLIED claim. All four strings are now absent from
# chapters/apx_f_cosine.tex, and the gate fails if any returns.
OPEN_REGISTER: tuple[tuple[str, str, str, str], ...] = (
    ("chapters/3_cbic/conclusion.tex", "biased towards the features required",
     "the author (DECIDED 2026-08-02: leave it)",
     "verbatim published CBIC 2025 prose, confirmed as a substring of "
     "articles/CBIC___MTL/sections/conclusion.tex, and the ONLY British form in the whole published "
     "CBIC source (zero -our, zero -ise, zero whilst). RESOLVED by the author on 2026-08-02, "
     "PENDENCIAS_RESOLVIDOS 2.24 (arquivado 2026-08-02): option (b), leave it as it stands, and THIS ENTRY IS THE PERMANENT RECORD OF "
     "THAT DECISION rather than a pending question. Do not 'fix' it in a later sweep. NORTH_STAR "
     "5.7 reserves changes to published prose to him, and this is vocabulary, not correctness. The "
     "entry stays because it is self-retiring: if the phrase ever leaves the chapter the gate FAILS "
     "and asks for the entry to be deleted, so the decision cannot rot into a silent exemption. "
     "Reported in _history/_round9/44_register_law.md."),
)


def strip_comments(raw: str) -> str:
    """Live prose only: comment lines and inline comment tails removed, lines joined.

    Joined on purpose (trap 2 in the docstring): a construction that wraps across a source line is
    invisible to a per-line regex.
    """
    keep = []
    for line in raw.split("\n"):
        m = COMMENT.search(line)
        cut = line[: m.start()] if m else line
        if cut.strip():
            keep.append(cut)
    return re.sub(r"\s+", " ", " ".join(keep))


def mask_quotes(text: str) -> str:
    """Blank the inside of ``...'' spans, keeping length so offsets stay comparable.

    Spelling families only. A verbatim quotation of published wording is evidence; a British
    spelling inside one may not be corrected, and flagging it would push an agent toward
    falsifying a quotation.
    """
    return re.sub(r"``.*?''", lambda m: " " * len(m.group(0)), text, flags=re.S)


def live_text(path: Path) -> str:
    return strip_comments(path.read_text(encoding="utf-8", errors="replace"))


def in_scope() -> list[Path]:
    files = sorted(p for p in SRC.rglob("*.tex") if "build" not in p.parts)
    if len(files) < SCOPE_FLOOR:
        print(f"FAIL: scope collapsed to {len(files)} file(s), below the floor of {SCOPE_FLOOR}. "
              f"A move or rename has taken prose out of this gate's reach, which is how two other "
              f"prose gates here silently swept almost nothing.")
        sys.exit(2)
    return files


# Bibliography fields whose content is AUTHORED BY US and therefore subject to this law. `title`,
# `booktitle`, `journal`, `series` and `author` are deliberately absent: they are attributes of
# record, copied from the publisher under §1 R2, and a British form inside one is the source's
# spelling, not ours. Measured: the one British form in this bibliography is `towards` inside
# Xu2023's title, and the title of record at Crossref (10.1145/3582553) reads `towards` -- so
# "correcting" it would corrupt an attribute the citation protocol requires be exact.
#
# WHY THE BIB IS IN SCOPE AT ALL. The .tex sweep reported clean while `towards` printed on page 82
# of the defense build, because the bibliography is not a .tex file. A gate whose scope stops short
# of the page cannot certify the page (§4b V3).
BIB_AUTHORED_FIELDS = ("note", "annote", "abstract", "howpublished", "addendum")
BIB_FIELD_RE = re.compile(r"^\s*([a-z]+)\s*=\s*\{(.*?)\}\s*,?\s*$", re.M | re.S)


def scan_bib(bib: Path) -> list[tuple[str, str, str, str]]:
    """British forms in bibliography fields WE wrote. Returns (field, rule, match, remedy).

    Comments are stripped with the same rule; a bib `%` line is a comment exactly as in TeX.
    """
    raw = strip_comments(bib.read_text(encoding="utf-8", errors="replace"))
    fields = BIB_FIELD_RE.findall(raw)
    if not fields:
        # A parse returning zero rows is a broken instrument, not a clean result (§4b V13). The
        # joined-line form above collapses the file to one line, so re-parse without the anchors.
        fields = re.findall(r"([a-z]+)\s*=\s*\{([^{}]*)\}", raw)
    if not fields:
        print(f"FAIL: parsed 0 fields out of {bib.name}. A zero-row parse is indistinguishable "
              f"from 'no violations' in the output, so it is treated as a broken instrument.")
        sys.exit(2)
    out = []
    for name, val in fields:
        if name.lower() not in BIB_AUTHORED_FIELDS:
            continue
        for cls, rule, got, remedy, _s, _e in scan(val, mask_quotes(val)):
            if cls.startswith("A"):
                out.append((name, rule, got, remedy))
    return out


def scan(text: str, quoted_masked: str) -> list[tuple[str, str, str, str, int, int]]:
    """Return (class, rule, matched text, remedy, start, end) for one file's live prose.

    The span is carried, not just the matched string, because the open register is keyed on the
    SENTENCE the author flagged: a chained-qualification finding reports a truncated sentence
    prefix that is not a literal substring of the file, so matching by string alone cannot tell
    whether the hit is inside a sentence somebody else already owns. Attribution by position does.
    """
    out: list[tuple[str, str, str, str, int, int]] = []
    for m in ISE_RE.finditer(quoted_masked):
        if _ise_is_british(m.group(0)):
            out.append(("A1 spelling", "-ise/-isation for -ize/-ization", m.group(0),
                        "American: -ize, -ization", m.start(), m.end()))
    for m in OUR_RE.finditer(quoted_masked):
        if _our_is_british(m.group(0)):
            out.append(("A1 spelling", "-our for -or", m.group(0),
                        "American: behavior, color, neighbor, labor", m.start(), m.end()))
    for rule, pat, remedy in SPELLING_RULES:
        for m in re.finditer(pat, quoted_masked, re.I):
            out.append(("A1 spelling", rule, m.group(0), remedy, m.start(), m.end()))
    # ABNT NBR 10520:2023 terminal punctuation, PENDENCIAS_RESOLVIDOS 2.24 (arquivado 2026-08-02), author's ruling of 2026-08-02.
    # SCANNED ON UNMASKED TEXT, and that is the whole reason it is not in SPELLING_RULES. Those run
    # against `quoted_masked`, which blanks every ``...'' span INCLUDING its delimiters -- correct for
    # spelling families, since a British spelling inside a quotation may not be corrected, but it
    # makes a rule about the quote's own punctuation structurally unable to fire. Placed in
    # SPELLING_RULES first, it reported clean on a tree with three real violations.
    #
    # AND THE PATTERN WAS WRITTEN BACKWARDS BEFORE THAT: it required the period AFTER the closing
    # quote -- the compliant form -- so it matched every correct site and no violation, and the suite
    # went green. A green gate read as "the tree complies" when it meant "the rule cannot fire".
    # Caught by flipping one real site to the American form and finding the gate silent. V17: a zero
    # from a pattern that cannot express its target is not evidence.
    #
    # AUTHOR'S EXEMPTION: a quotation that is itself a COMPLETE SENTENCE keeps its own terminal period
    # INSIDE the marks, because that period is the quoted author's. NBR 10520 governs how a quotation
    # enters your sentence, not how its author punctuated theirs, and this document's errata tables
    # exist to reproduce submitted wording verbatim. Exempted by FORM, not by file: the quoted span
    # opens with `` followed by a capital, or its text ends a finite clause of its own.
    for m in re.finditer(QUOTE_PERIOD, text):
        span = m.group(0)
        # The lookback window must be wide enough for a quoted sentence (the real one here runs 118
        # characters) and must NOT exclude apostrophes, which appear inside quoted prose. A first
        # version used [^`']{0,200}, so the closing '' of the span itself broke the match and every
        # quoted sentence was reported as a violation.
        inner = text[max(0, m.start() - 400):m.end()]
        opener = re.search(r"``([^`]{0,400})$", inner)
        quoted_sentence = bool(opener and re.match(r"[A-Z]", opener.group(1).lstrip()))
        if quoted_sentence:
            continue
        out.append(("A1 punctuation", "period inside a closing quote (ABNT NBR 10520 puts it outside)",
                    span, QUOTE_PERIOD_REMEDY, m.start(), m.end()))
    for rule, pat, remedy in CONSTRUCTION_RULES:
        for m in re.finditer(pat, text, re.I):
            out.append(("A2 construction", rule, m.group(0), remedy, m.start(), m.end()))
    for rule, pat, remedy in (SHAPE_DELAYED_SUBJECT, SHAPE_IDIOM, SHAPE_ABSTRACT_AGENT):
        for m in re.finditer(pat, text, re.I):
            out.append(("B shape", rule, m.group(0), remedy, m.start(), m.end()))
    # B5 goes through stranded_hits(), not a bare finditer: its two guards cannot be expressed as
    # lookarounds, because one of them has to scope back to the clause head. See stranded_hits().
    for m in stranded_hits(text):
        out.append(("B shape", SHAPE_STRANDED[0], m.group(0), SHAPE_STRANDED[2],
                    m.start(), m.end()))
    for m in re.finditer(r"[^.!?]{20,}[.!?]", text):
        sent = m.group(0)
        quals = len(SHAPE_CHAINED_QUALS.findall(sent))
        commas = sent.count(",")
        if quals >= CHAIN_MIN_QUALS and commas >= CHAIN_MIN_COMMAS:
            out.append(("B shape", "chained qualification inside one sentence",
                        f"{quals} qualifiers, {commas} commas: {sent.strip()[:90]}",
                        "split the sentence, or drop the qualifications the claim does not need",
                        m.start(), m.end()))
    return out


def self_test() -> None:
    """Both directions, on the author's real sentences and their American equivalents.

    The negatives are not invented: every one is a real sentence from this tree, or the American
    form of a real hit. A detector that fires on correct American prose is worse than none,
    because a gate that cries wolf teaches everyone to read past its exit code -- which is
    documented in check.sh as having already happened here.
    """
    # (a) his own British instance must fire, and its American rewrite must not.
    brit = "Figure 6 shows the distributions, and one feature needs saying plainly: the equivalence."
    amer = "Figure 6 shows the distributions, and one feature needs to be said plainly."
    fired = [r for r, p, _ in CONSTRUCTION_RULES if re.search(p, brit, re.I)]
    assert "need / want + gerund" in fired, (
        f"self-test: the author's own instance 'needs saying plainly' did not fire, got {fired}. "
        "Reporting now would turn a present defect into a pass.")
    assert not any(re.search(p, amer, re.I) for _, p, _ in CONSTRUCTION_RULES), (
        "self-test: the American rewrite was flagged -- the construction rules fire on correct prose")
    assert not re.search(CONSTRUCTION_RULES[0][1], "the model needs to be trained", re.I), (
        "self-test: 'needs to be' was flagged; the (?!to\\b) guard is broken")

    # (a) spelling: each family fires on the British form and is silent on the American one.
    pairs = (("neighbours", "neighbors"), ("behaviour", "behavior"), ("centre", "center"),
             ("modelled", "modeled"), ("analyse", "analyze"), ("defence", "defense"),
             ("whilst", "while"), ("amongst", "among"), ("towards", "toward"),
             ("catalogue", "catalog"), ("grey", "gray"), ("programme", "program"),
             ("learnt", "learned"), ("licence", "license"), ("skilful", "skillful"),
             ("normalisation", "normalization"), ("judgement", "judgment"),
             ("per cent", "percent"), ("fibre", "fiber"), ("travelled", "traveled"))
    for british, american in pairs:
        b = f"The measured {british} of the model is reported in Table 3."
        a = f"The measured {american} of the model is reported in Table 3."
        assert scan(b, mask_quotes(b)), f"self-test: British {british!r} was not detected"
        got = scan(a, mask_quotes(a))
        assert not got, f"self-test: American {american!r} was flagged as British: {got}"

    # (a) the -ise and -our whitelists: same-in-both words must pass, including prefixed forms.
    # `analyses` and `paralyses` are here because they are the AMERICAN plurals of -ysis nouns and
    # collide exactly with the British verb inflection; that collision produced a false positive
    # caught only by sweeping the rendered PDF, where the bibliography is in scope.
    for ok in ("surprise", "comprises", "exercised", "supervising", "revised", "improvised",
               "unsurprising", "four", "hours", "resources", "encouraged", "discourse",
               "specialized", "initialization", "maximizing", "sources", "tourism",
               "analyses", "paralyses", "catalyses"):
        s = f"We {ok} the setting before training."
        got = [h for h in scan(s, mask_quotes(s)) if h[0] == "A1 spelling"]
        assert not got, f"self-test: {ok!r} is not a British spelling but was flagged: {got}"

    # (a) a British spelling inside a verbatim quotation is masked, one outside it is not.
    q = "The published sentence reads ``the behaviour of the model''."
    assert not [h for h in scan(q, mask_quotes(q)) if h[0] == "A1 spelling"], (
        "self-test: a spelling inside a ``...'' quotation was flagged -- correcting it would "
        "falsify the quotation")
    nq = "The behaviour of the model is stable."
    assert [h for h in scan(nq, mask_quotes(nq)) if h[0] == "A1 spelling"], (
        "self-test: quotation masking leaked and now hides unquoted prose")

    # (b) his two Class B sentences must fire; the sentences this document already uses must not.
    b1 = "Two departures from that flat picture appear, and both are worth reporting."
    assert re.search(SHAPE_DELAYED_SUBJECT[1], b1), (
        "self-test: the author's instance of the delayed-subject shape did not fire")
    b2 = "Both point away from trouble in any case."
    assert re.search(SHAPE_IDIOM[1], b2, re.I), (
        "self-test: the author's instance of the idiom shape did not fire")
    b3 = ("A positive cosine is mild cooperation, not conflict, and the decline stays inside the "
          "margin throughout while moving toward zero rather than away from it.")
    # His point-12 sentence is caught by the CHAINED-QUALIFICATION rule, not by the abstract-agent
    # rule. That is deliberate and is the outcome of narrowing B4 (see its comment): the chain is
    # what makes the sentence hard, and "the decline ... moving" is literal. Asserted here so a later
    # widening of B4 cannot quietly become the only thing covering this sentence.
    assert len(SHAPE_CHAINED_QUALS.findall(b3)) >= CHAIN_MIN_QUALS and b3.count(",") >= CHAIN_MIN_COMMAS, (
        "self-test: the author's point-12 sentence must still fire on the chained-qualification "
        "shape -- it is the rule that carries that instance now")
    assert not re.search(SHAPE_ABSTRACT_AGENT[1], b3, re.I), (
        "self-test: B4 fired on a motion verb again. It was narrowed to volition/cognition/speech "
        "because the remedy it prints ('the mean falls toward zero') is itself a motion verb, and "
        "because it flagged 'the cosines move toward zero' while passing 'the mean falls toward "
        "zero' -- a verdict that turned on which noun was in the list.")
    b4 = "The evidence prefers the joint model, and the verdict admits no other reading."
    assert re.search(SHAPE_ABSTRACT_AGENT[1], b4, re.I), (
        "self-test: the abstract-agent shape did not fire on a genuinely animated quantity")
    for literal in ("the mean falls toward zero and stays inside the margin",
                    "the declining cosines stay inside the margin and move toward zero",
                    "the region gain rises with region count",
                    "the curve climbs steeply at the largest region counts"):
        assert not re.search(SHAPE_ABSTRACT_AGENT[1], literal, re.I), (
            f"self-test: B4 flagged literal quantity motion: {literal!r}")
    # ABNT NBR 10520 terminal punctuation, pinned in BOTH DIRECTIONS because this rule failed in
    # both while it was being written: first as a pattern that matched the COMPLIANT form (so the
    # gate went green on a tree with three violations), then as a member of SPELLING_RULES, whose
    # loop reads quote-masked text and therefore cannot see a quote's own punctuation at all.
    # The positive cases below are the real defect shape; the negatives are the author's exemption
    # (a quoted complete sentence keeps its own period) and the compliant form.
    for bad in ("he called it a ``joint model.''",
                'he called it a "joint model."'):
        assert scan(bad, mask_quotes(bad)), (
            f"self-test: the ABNT punctuation rule did not fire on {bad!r}. A rule that cannot "
            "flag the American form makes a green suite mean nothing about this convention.")
    for ok in ("he called it a ``joint model''.",
               "the submitted text read ``Also, it is important to notice that the result is "
               "unbalanced.''",
               "reported by Silva et al.''"):
        assert not any(r[1].startswith("period inside a closing quote")
                       for r in scan(ok, mask_quotes(ok))), (
            f"self-test: the ABNT punctuation rule fired on a legal form: {ok!r}. The middle case "
            "is the author's exemption of 2026-08-02 -- flagging it would push a later pass into "
            "altering a verbatim quotation, which is the harm the rule exists to prevent.")
    # B5, the stranded preposition, validated in BOTH directions on the REAL sentences. The two
    # negative cases are the ones that found the guards: each is the CORRECT form of a defect this
    # gate flagged, and the raw pattern fired on both before stranded_hits() existed.
    b5 = ("if the update next-region asks for points against the update next-category asks for, "
          "one task improves at the other's expense")
    assert list(stranded_hits(b5)), (
        "self-test: B5 did not fire on the real appendix defect (R15-04)")
    for legal in ("the metrics and reference points that each result is read against, and the seeds",
                  "which is the reference level that one screening argument in the dissertation is "
                  "read against.",
                  "the answer depends on what the representation carries.",
                  "a transition prior that the models reported here do not use, and its own record"):
        assert not list(stranded_hits(legal)), (
            f"self-test: B5 fired on a correctly written relative clause: {legal[:60]!r}")
    for clean in ("Two consequences follow.",
                  "Three limits qualify these results.",
                  "The main contributions of this chapter are as follows.",
                  "The rest of this chapter is organized as follows.",
                  "Section 3.5 presents experimental results.",
                  "Three canonical sharing schemes have emerged:",
                  "The screening procedure works as follows.",
                  "The cosine of the angle between the two gradients was recorded per epoch.",
                  "The margin is two points.",
                  "The screening margin of three points is applied to every candidate.",
                  "The region gain rises with region count, from 0.41 to 2.20 points.",
                  "Both tasks read the same history, so one model could learn them jointly.",
                  "The behavior they capture is far from random.",
                  "The distance between that result and a null result is the point of this appendix."):
        got = [h for h in scan(clean, mask_quotes(clean)) if h[0] == "B shape"]
        assert not got, f"self-test: legitimate sentence flagged as a B shape: {clean!r} -> {got}"

    # the stripper: an escaped percent must not truncate, a real comment must not survive.
    assert "TAIL" in strip_comments(r"a 90\% interval and then TAIL"), (
        "self-test: an escaped \\% truncated the line; the pattern must be (?<!\\\\)%")
    assert "COMMENTED" not in strip_comments("prose\n% COMMENTED words"), (
        "self-test: a % comment leaked into live text, so this file's own docstring examples "
        "would be reported as violations")


def main() -> int:
    self_test()
    print("== register law: American English and first-read phrasing (WRITING_LAW §1) ==")
    files = in_scope()

    open_keys = {(f, s) for f, s, _, _ in OPEN_REGISTER}
    live: dict[str, str] = {}
    for f in files:
        live[str(f.relative_to(SRC))] = live_text(f)

    # The open register first: present -> OPEN, absent -> the entry is stale and must go.
    stale = []
    for rel, needle, owner, note in OPEN_REGISTER:
        text = live.get(rel)
        if text is None:
            stale.append((rel, needle, owner, "the file itself is gone"))
        elif needle in text:
            print(f"  OPEN  {rel}: {needle!r}")
            print(f"        owner: {owner}")
            print(f"        {note}")
        else:
            stale.append((rel, needle, owner, "the defect is fixed"))

    # Attribution by SPAN OVERLAP, not by string. An open-register entry owns the sentence its
    # needle sits in, so every hit whose span touches that sentence belongs to that entry's owner.
    # Sentence bounds are recomputed rather than assumed: the author's point-12 sentence carries
    # both an idiom hit and a chained-qualification hit, and the latter's reported text is a
    # truncated prefix that appears nowhere in the file.
    owned: dict[str, list[tuple[int, int]]] = {}
    for rel, needle, _owner, _note in OPEN_REGISTER:
        text = live.get(rel)
        if text is None:
            continue
        for m in re.finditer(re.escape(needle), text):
            lo = text.rfind(".", 0, m.start()) + 1
            hi = text.find(".", m.end())
            hi = len(text) if hi == -1 else hi + 1
            owned.setdefault(rel, []).append((lo, hi))

    findings = []
    for rel, text in live.items():
        spans = owned.get(rel, [])
        for cls, rule, got, remedy, start, end in scan(text, mask_quotes(text)):
            if any(start < hi and end > lo for lo, hi in spans):
                continue
            findings.append((rel, cls, rule, got, remedy))

    bib = SRC / "references.bib"
    bib_note = "absent"
    if bib.exists():
        bib_hits = scan_bib(bib)
        bib_note = (f"{len(BIB_AUTHORED_FIELDS)} authored field types checked, "
                    f"{len(bib_hits)} hit(s)")
        for field, rule, got, remedy in bib_hits:
            findings.append((f"references.bib ({field})", "A1 spelling", rule, got, remedy))

    for rel, cls, rule, got, remedy in findings:
        print(f"  {rel}: [{cls}] {rule}")
        print(f"      matched: {got!r}")
        print(f"      {remedy}")

    if stale:
        print("")
        for rel, needle, owner, why in stale:
            print(f"  STALE OPEN-REGISTER ENTRY: {rel} {needle!r} ({why})")
            print(f"      it was held open for: {owner}")
        print(f"\nFAIL: {len(stale)} open-register entry/entries no longer match anything. An "
              f"exemption that outlives its defect hides the next regression in the same place. "
              f"Delete the entry from OPEN_REGISTER in this file, in the same commit as the fix.")
        return 1

    if findings:
        n_a = sum(1 for f in findings if f[1].startswith("A"))
        n_b = sum(1 for f in findings if f[1].startswith("B"))
        print(f"\nFAIL: {n_a} British spelling/construction hit(s) and {n_b} hard-phrasing "
              f"shape(s). Class A is mechanical, so fix it. Class B names a shape, not a verdict: "
              f"rewrite so a non-native reader takes the sentence in on one reading, and see "
              f"reviewers/15_readability_editor.md lens 2 for the judgment half this gate does "
              f"not measure.")
        return 1

    print(f"OK: no British spellings or constructions and no gated hard-phrasing shape in "
          f"{len(files)} .tex files; references.bib {bib_note} (title/journal/author fields are "
          f"attributes of record and out of scope by design: Xu2023's published title reads "
          f"\"towards\" at Crossref 10.1145/3582553); {len(OPEN_REGISTER)} hit(s) held open by "
          f"name above. Class B gates four shapes only, and a green result here is NOT a "
          f"first-read PASS: that verdict is reviewers/15_readability_editor.md lens 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
