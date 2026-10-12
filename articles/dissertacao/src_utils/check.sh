#!/bin/bash
# Lint hook (TEMPLATE.md §2 item 10): the cheap half of gates G2/G3.
# Usage: make check  (or ../src_utils/check.sh from the src root). This script lives in
# src_utils/ (a SIBLING of src/); the LaTeX source it lints is in the sibling src/. Resolves
# that path from this script's location, so it works from any cwd. Exits nonzero on any finding.
FAIL=0
SRCROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../src" && pwd)"
SLOW_GATE_S=5          # a gate over this announces itself; see the timing table footer
UTILS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # absolute: this script cds into src/
cd "$SRCROOT"

# PYTHON PREFLIGHT. Several gates read the built PDFs through pypdfium2. If the python3 first on
# PATH does not have it, they die with a bare ModuleNotFoundError traceback partway through the
# suite and the reader has to work out which interpreter ran. Found 2026-07-30 while testing the
# Makefile from a bare PATH=/usr/bin:/bin, where /usr/bin/python3 is the system one and has no
# third-party packages. Say so once, up front, and name the interpreter.
if ! python3 -c "import pypdfium2" >/dev/null 2>&1; then
  echo "GATE PREREQUISITE MISSING: python3 has no pypdfium2, and several gates read the PDFs with it."
  echo "  python3 resolves to: $(command -v python3 || echo '<not on PATH>')"
  echo "  install with:        python3 -m pip install pypdfium2"
  echo "  or put the interpreter that has it first on PATH."
  exit 2
fi

# ---- per-gate timing (round 7) ---------------------------------------------------------
# WHY. The author's standing complaint was that "the checks are slow". Measured, they are not:
# the nine Python checkers total about 1.4 s and the whole suite runs in under 2 s. What was
# slow was the 95 s BUILD that people ran immediately before `make check`, and the cost got
# attributed to the gates. So this suite now prints where its own time goes, and the argument
# is settled by the table rather than by anyone's impression. It also means the NEXT gate that
# turns slow is visible on the run that made it slow, instead of being suspected months later.
#
# The clock is `perl -MTime::HiRes`, not $EPOCHREALTIME: this machine's /bin/bash is 3.2.57
# (Apple ships that), and $EPOCHREALTIME arrived in bash 5.
#
# THE HARNESS'S OWN COST, measured as the boundary is actually spelled rather than as one clock
# read. A `gate` call spawns THREE perl processes, not one: `$(_now)` inside the arithmetic, the
# arithmetic itself, and the `$(_now)` that opens the next gate. Measured 20 full boundaries in
# 0.348 s => ~17 ms each, against 0.126 s / 20 => ~6 ms for a bare clock read. My first version
# of this comment disclosed the 6 ms figure, which understated the real overhead by about 3x --
# a timing harness that is wrong about its own cost is worse than none, so the number below is
# the boundary cost and the footer computes from it.
SECS_PER_BOUNDARY=0.017
# Set CHECK_TIMING=0 to suppress the table (the gates still run; only the report is skipped).
CHECK_TIMING="${CHECK_TIMING:-1}"
GATE_NAMES=(); GATE_TIMES=(); GATE_N=0; GATE_T0=""; GATE_CUR=""
_now() { perl -MTime::HiRes -e 'printf "%.3f", Time::HiRes::time()'; }
SUITE_T0="$(_now)"
# gate "== title ==" : closes the previous gate's clock, prints the header, opens a new one.
gate() {
  if [ -n "$GATE_CUR" ]; then
    GATE_NAMES[$GATE_N]="$GATE_CUR"
    GATE_TIMES[$GATE_N]="$(perl -e "printf '%.3f', $(_now) - $GATE_T0")"
    GATE_N=$((GATE_N + 1))
  fi
  GATE_CUR="$1"; GATE_T0="$(_now)"
  echo "$1"
}
gate_report() {
  if [ -n "$GATE_CUR" ]; then
    GATE_NAMES[$GATE_N]="$GATE_CUR"
    GATE_TIMES[$GATE_N]="$(perl -e "printf '%.3f', $(_now) - $GATE_T0")"
    GATE_N=$((GATE_N + 1))
  fi
  [ "$CHECK_TIMING" = "0" ] && return 0
  local total; total="$(perl -e "printf '%.3f', $(_now) - $SUITE_T0")"
  echo ""
  echo "== per-gate timing (seconds; $GATE_N gates, suite total ${total}s) =="
  local i=0 sum=0
  while [ $i -lt $GATE_N ]; do
    # Strip the "== ... ==" decoration and truncate, so the table is readable at a glance.
    local name; name="$(echo "${GATE_NAMES[$i]}" | sed 's/^== //; s/ ==$//' | cut -c1-64)"
    printf '  %6ss  %s\n' "${GATE_TIMES[$i]}" "$name"
    sum="$(perl -e "printf '%.3f', $sum + ${GATE_TIMES[$i]}")"
    i=$((i + 1))
  done
  printf '  %6ss  SUM OF GATES (the rest is this table plus ~%s s of clock probes:\n' \
         "$sum" "$(perl -e "printf '%.2f', $SECS_PER_BOUNDARY * ($GATE_N + 1)")"
  printf '            %s boundaries x ~%s s, three perl spawns each)\n' \
         "$((GATE_N + 1))" "$SECS_PER_BOUNDARY"
  # THE TABLE NOW COMPLAINS INSTEAD OF INFORMING, and the reason is measured. This table was added
  # 2026-07-29 with a comment promising "the NEXT gate that turns slow is visible on the run that
  # made it slow". It was visible: for roughly fifty runs and 33 commits claiming RC=0, the top row
  # read 264.144s against a 265.288s total. Nobody read it, including the agent that had added it
  # the day before. The exit code was 0, and 0 answered the question the reader arrived with.
  # A diagnostic only a curious reader notices is a diagnostic that will not be noticed
  # (AGENT_GUARDRAILS §4b V12), so anything over the threshold now announces itself.
  local slow=0 i2=0
  while [ $i2 -lt $GATE_N ]; do
    if perl -e "exit((${GATE_TIMES[$i2]} > $SLOW_GATE_S) ? 0 : 1)"; then
      local nm; nm="$(echo "${GATE_NAMES[$i2]}" | sed 's/^== //; s/ ==$//' | cut -c1-56)"
      printf '  SLOW GATE: %ss (over the %ss threshold) -- %s\n' "${GATE_TIMES[$i2]}" "$SLOW_GATE_S" "$nm"
      slow=$((slow + 1))
    fi
    i2=$((i2 + 1))
  done
  if [ "$slow" -gt 0 ]; then
    echo "  ^ $slow gate(s) over threshold. A lint gate people run constantly should be seconds."
    echo "    Before optimizing, ask what it is DOING: the last time this fired, a gate was"
    echo "    rebuilding the whole document on every invocation because its build guard was a"
    echo "    list of target names that two new targets had grown past."
  else
    echo "  All $GATE_N gates under the ${SLOW_GATE_S}s threshold."
  fi
}
# ----------------------------------------------------------------------------------------
# THE PROSE SCOPE, and it has silently shrunk TWICE. chapters/*/*.tex was added 2026-07-28 after
# the paper chapters were split into per-section files and a pattern stopping at chapters/*.tex
# left 55% of the prose unswept. Then on 2026-07-29 0_main.tex became preamble.tex + content.tex
# and this list still named 0_main.tex: `grep` exits 2 on the missing file, the pipeline swallows
# it, and both halves went unswept with every gate still printing OK.
#
# BOTH FAILURES WERE SILENT, which is the point. So the scope is now DERIVED from the filesystem
# and ASSERTED non-empty below, rather than typed. If a file moves, the glob follows it; if the
# glob ever matches nothing, the suite stops instead of reporting a clean sweep of no files.
CH="$(ls chapters/*.tex chapters/*/*.tex preamble.tex content.tex 2>/dev/null | tr '\n' ' ')"
CH_N=$(echo $CH | wc -w | tr -d ' ')
if [ "$CH_N" -lt 10 ]; then
  echo "FAIL: the prose scope resolved to $CH_N files, which is too few to be right."
  echo "  A checker sweeping an empty or truncated file list reports OK and proves nothing;"
  echo "  that has happened twice here. Files found: $CH"
  exit 2
fi

gate "== em-dashes (WRITING_LAW §1: none anywhere in prose) =="
EMDASH=$(printf '\xe2\x80\x94')
if grep -n "$EMDASH" $CH 0_main.tex 2>/dev/null | grep -v '^[^:]*:[0-9]*: *%'; then FAIL=1; else echo OK; fi

gate "== 'this paper' / 'this article' inside chapters (apx_b_errata exempt: see below) =="
# THE EXEMPTION, added 2026-07-28. This sweep exists because a chapter of a coletanea must not call
# itself "this paper" -- it is a chapter now. apx_b_errata.tex is the ONE file where the phrase is
# correct: it is the errata appendix, and its whole subject is the three published/submitted ARTICLES
# as distinct from the chapter bodies that re-typeset them. At :307 "This article differs from the
# other two in a way that changes what this section has to record" refers to the MobiWac manuscript,
# under review, whose errata are handled differently BECAUSE it is still an article.
# The banned-words sweep two blocks below already exempts this same file for the same reason (it
# quotes published text). This gate now says so too.
# WHY THIS MATTERS BEYOND THE FALSE POSITIVE: `make check` exited 2 for this entire round while six
# commit messages, including mine, said "make check: all gates pass". The source-ledger pass caught
# it (finding L-1). A gate whose only hit is a known-good line trains everyone to read past its exit
# code, which is how a real hit would have been missed. Exempt the known-good line so the exit code
# means something again.
if grep -niE 'this (paper|article)' $CH | grep -v '^[^:]*:[0-9]*: *%' | grep -v '^chapters/apx_b_errata'; then FAIL=1; else echo OK; fi

gate "== contractions =="
if grep -nE "\b(don't|doesn't|isn't|aren't|won't|can't|couldn't|wouldn't|shouldn't|it's|we're|they're|there's|hasn't|haven't|didn't|wasn't|weren't)\b" $CH | grep -v '^[^:]*:[0-9]*: *%'; then FAIL=1; else echo OK; fi

gate "== WRITING_LAW §4 banned words (prose lines only; apx_b quotes published text and is exempt) =="
if grep -nwiE 'delve|delves|intricate|showcase|showcases|underscores?|pivotal|leverages?|leveraging|seamless|seamlessly|testament|moreover|furthermore' $CH | grep -v '^[^:]*:[0-9]*: *%' | grep -v '^chapters/apx_b_errata'; then FAIL=1; else echo OK; fi

gate "== banned verdict verbs (beats/wins/ties as result verbs; crude sweep, review hits) =="
# "Pareto" was in this alternation and produced five hits, every one of them the TECHNICAL term
# (Pareto-optimal descent directions, Pareto efficiency, a Pareto-stationary point) in optimization
# prose, three of them inside published chapters where the word is the field's own and cannot change.
# The banned thing is "beats"/"wins" as a RESULT verb; "Pareto" is not a verdict verb at all and was
# never going to be a real hit here. It is separated out below so this sweep can be read.
grep -nwiE 'beats?|wins?' $CH | grep -v '^[^:]*:[0-9]*: *%' || echo OK

gate "== 'Pareto' occurrences (informational: the technical term is legal, a verdict use is not) =="
# Informational, never FAIL. Read the hits: Pareto-optimal / Pareto-stationary / Pareto efficiency
# are the optimization literature's own terms and are correct. What would be wrong is "Pareto" used
# to mean "better", which no hit currently is.
grep -nwiE 'Pareto' $CH | grep -v '^[^:]*:[0-9]*: *%' | sed 's/^/    /' | cut -c1-140 || true

gate "== repo codenames =="
if grep -nwE 'B9|v1[1-7]|champion-G|H3-alt|dk_ovl|log_T|substrate' $CH | grep -v '^[^:]*:[0-9]*: *%'; then FAIL=1; else echo OK; fi

gate "== unresolved \\ref/\\cite (needs a compiled .log) =="
# NOTE 2026-07-26: this check used a line-anchored grep. LaTeX WRAPS its warnings at 79 columns, so
# a wrapped "Citation `key' on page N undefined" was invisible to it and four undefined citations
# shipped in both PDFs. The log is flattened before matching, and the .blg is read too, because a
# BibTeX error (e.g. a bare at-sign inside a % comment in references.bib) never reaches the .log.
LOG=build/main.log
BLG=build/main.blg
if [ -f "$LOG" ]; then
  # Matching is done in Python with errors='replace', NOT with tr|grep. pdflatex writes raw bytes
  # from font and PDF metadata into the log (there is an invalid UTF-8 continuation byte at offset
  # ~75.6k in a normal build of this document), and `tr` aborts on it with "Illegal byte sequence"
  # under any UTF-8 locale -- which is the default here. Everything after that byte was therefore
  # never examined, and the abort went to stderr while the pipeline still reported success.
  # Verified by injecting a synthetic undefined-citation warning after the bad byte: found under
  # LC_ALL=C, silently missed under en_US.UTF-8. This is the very check that exists because four
  # undefined citations shipped in both PDFs.
  if python3 - "$LOG" <<'PYEOF'
import re, sys
raw = open(sys.argv[1], encoding='utf8', errors='replace').read()
flat = raw.replace("\n", "")                      # LaTeX wraps warnings at 79 columns
hits = sorted(set(re.findall(r"(?:Reference|Citation) `[^']+' on page \d+ undefined", flat)))
for h in hits:
    print(h)
sys.exit(1 if hits else 0)
PYEOF
  then echo OK; else FAIL=1; fi
else echo "SKIP: no $LOG"; fi
if [ -f "$BLG" ]; then
  if grep -iE "error|didn't find|I was expecting" "$BLG"; then FAIL=1; else echo "OK (bibtex)"; fi
else echo "SKIP: no $BLG"; fi

gate "== sweep-guard self-tests (a no-op substitution must not look like a result) =="
# Twice this project drew a conclusion from a parameter sweep whose arms never applied: once a doubled
# backslash made the target unmatchable, once a bad escape killed the substitution inside a heredoc.
# Both printed identical results across arms, which read as evidence. These tests pin both cases.
if ! python3 "$UTILS/sweep_guard.py" >/dev/null 2>&1; then
  echo "  FAIL: sweep_guard self-tests do not pass -- the guard itself is broken"
  python3 "$UTILS/sweep_guard.py" 2>&1 | tail -5
  FAIL=1
else
  echo "OK (4 self-tests)"
fi

gate "== recorded page counts vs the measured build =="
# These are PRESENT-TENSE claims about what is on disk (CLAUDE.md, PLAN.md, PENDENCIAS.md,
# codex_reviewer.md). They have drifted three times, always caught by review rather than by the
# edit that caused it. The codex page-drift note is load-bearing: it tells a reader how far every
# file:line in that review has moved.
if ! python3 "$UTILS/sync_page_counts.py"; then
  echo "  -> run: python3 src_utils/sync_page_counts.py --write"
  FAIL=1
fi

gate "== the deposit build's first body page prints the number UFV requires =="
# ADDED 2026-09-06. This number (\finalbuildfirstpage, src/main.tex) had been "corrected" four
# times -- 11, 8, 9, 10 -- and all four were wrong, because the recipe in the source counted only
# OUR pre-textual pages and AcademicoPG prepends ten more that the UFV manual counts. Worse, that
# recipe claimed "check.sh runs it", and it did not: sync_page_counts above checks page TOTALS,
# never this number. So each wrong value felt verified. The measured value is 20.
# THE EXIT CODES ARE NOT INTERCHANGEABLE and that is deliberate: 1 = the macro disagrees with the
# rule (a real defect, FAIL); 2 = the gate could not run, e.g. main_academico.pdf is not built
# (NOT a pass, and NOT the same thing). Missing builds are announced separately rather than folded
# into FAIL, because a gate whose "you did not build" looks identical to its "you are wrong" is a
# gate people learn to skip -- which is exactly what happened to sync_page_counts, whose sys.exit
# on the routinely-absent main_ppgc build ends the run before any count is compared.
python3 "$UTILS/check_first_body_page.py"; FBP_RC=$?
if [ $FBP_RC -eq 1 ]; then
  FAIL=1
elif [ $FBP_RC -ne 0 ]; then
  echo "  -> NOT CHECKED (rc=$FBP_RC). Run 'make academico' (it does not overwrite dissertacao.pdf)"
  echo "     and re-run. This is not a pass."
fi

gate "== word-count claims reconcile with their own recorded stages =="
# THIRD arithmetic error in a WRITE-UP of correct work (2026-07-27): a register entry stated the
# Resumo compression split backwards ("~13 words of gloss, the other ~30 deleted clauses") when its
# own recorded stages give compression 23/19 and deletion 13/14. The measurement was right; the prose
# about it was not. This recomputes the split from the endpoints and fails when prose disagrees.
# Quoted admissions of the old figure are allowed, so the corrections themselves do not trip it.
if ! python3 "$UTILS/check_wordcount_claims.py"; then FAIL=1; fi

gate "== torn sentences (a body line opening mid-sentence: the clause before it is GONE) =="
# A DIFFERENT defect from trapped prose: nothing is trapped, the opening clause is simply absent, and
# the build is clean. Found 2026-07-27 by persona 03 in the Resumo and Abstract (rendered pp. 3-4,
# four instances), introduced by an assistant compressing those blocks. The trapped-prose detector
# cannot see it, because there is no comment involved. Rule proposed by persona 03 and implemented
# as specified. Validated both ways: 0 on the repaired tree, exactly the 4 real defects when
# reintroduced.
if ! python3 "$UTILS/check_torn_sentences.py"; then FAIL=1; fi

gate "== PENDENCIAS section citations still resolve (silent: renders fine, points nowhere) =="
# On 2026-07-29 the tracker was renumbered (2.3-2.7 -> 2.4-2.8) and FOUR source comments cited the old
# number for the static-scope section. Three were repointed; the fourth -- the header of the very file
# the citation is ABOUT -- was missed, and the commit message said all four were done. The grep that
# found four was run and read; the fix list was written with three entries.
# A stale section number is not a LaTeX error, not an undefined reference, and not a broken link: it
# renders correctly and points somewhere wrong (AGENT_HANDOFF §2.6). Historical citations are exempt
# when the citation itself says so ("PENDENCIAS 2.4, was 2.2"), and dated audit records under
# _round*/, _review_v*/, _history/_archive/ are skipped -- they describe a tracker as it stood.
# Validated against the real defect: reintroducing the bare citation of 2.2 (a number that no longer resolves) in
# apx_b_static_scope.tex:3 gives exactly 1 hit; the repaired tree gives 0.
# (This comment names the old number in the exempt form on purpose -- see the line above --
#  because the gate reads every .sh in the tree, including this one.)
if ! python3 "$UTILS/check_tracker_refs.py"; then FAIL=1; fi

gate "== coverage claims about the work carry the command that produced them (GUARDRAILS 4b V1) =="
# Round 6 measured its own rework: 17 of 61 commits, 14 genuine, and TWELVE of those fourteen were a
# wrong statement about the WORK rather than about the dissertation. Zero were fabricated citations.
# The worst carried no digit at all -- "Every command in this file was executed verbatim ... and
# returns the output its 'if all is well' line describes" -- written when four blocks had never run
# and nothing had been compared to any expectation. Validated against that exact historical file
# (1 hit at VERIFY_LIST.md:56 as of 0aceb5ee~1, 0 on the current tree).
if ! python3 "$UTILS/check_meta_claims.py"; then FAIL=1; fi

gate "== the author-facing verification commands actually return what they claim =="
# VERIFY_LIST.md and PENDENCIAS.md tell the author to run specific commands and state what each
# should return. On 2026-07-28 three of them did not: a \path{} count annotated 13 returned 15,
# a sweep promising 3 prose hits returned 4, and one promising ZERO returned 5 -- each because it
# did not strip this source's provenance comments, which quote the strings being searched for.
# What let them survive is that nothing ran them. This gate runs them, and asserts the ones
# carrying an EXPECT annotation. It reports run-but-not-asserted separately so the count of what
# is actually verified is never overstated.
if ! python3 "$UTILS/check_verify_list.py"; then FAIL=1; fi

gate "== Appendix B errata row counts vs the appendix's own claim =="
# Wired 2026-07-30 on the Chapter-text track's recommendation. It shipped a row-count claim in
# apx_b_errata.tex whose own verification command could not produce the counts it asserted -- caught
# by a reviewer, not by the gate suite. This reconciles the printed totals against the actual rows.
if [ -f "$UTILS/count_errata_rows.py" ]; then
  if ! python3 "$UTILS/count_errata_rows.py"; then FAIL=1; fi
else
  echo "  SKIP: count_errata_rows.py absent -- if it was deleted, delete this block too."
fi

gate "== process narration in prose (the author found this in Appendix F, and no rule banned it) =="
# THE DEFECT: Appendix F told the reader "the machine that would have run them was out of disk". The
# author's objection was that a dissertation states what is true and this is a fact about a lab
# machine. He also asked whether the law covered it; it did not, measured (grep over
# AGENT_GUARDRAILS.md and WRITING_LAW.md returned 0). WRITING_LAW §1 now bans the class and this gate
# enforces it. Validated by reintroducing the author's exact sentence: 4 rules fire, rc=1; rc=0 clean.
if ! python3 "$UTILS/check_process_narration.py"; then FAIL=1; fi

gate "== register: British English and hard phrasing (the author found both in Appendix F) =="
# WHICH AUTHOR INSTANCES THIS ANSWERS: PENDENCIAS_RESOLVIDOS 2.22 (arquivado 2026-07-30) points 8, 9 and 12, all from one reading of
# Appendix F on 2026-07-30, in a tree where all 24 gates were green.
#   point 8  "feature needs saying plainly" -- BRITISH, and note it is NOT a spelling: every word is
#            spelled the same in both dialects. It is the British need+gerund construction, so a
#            spelling list would have reported clean. The gate covers spellings AND constructions.
#   point 9  "Two departures from that flat picture appear" -- his note: "pure A.I, we can be more
#            simple".
#   point 12 "Both point away from trouble in any case. A positive cosine is mild cooperation, not
#            conflict, and the decline stays inside the margin throughout while moving toward zero
#            rather than away from it." -- his note: "well written, but is not natural for a non
#            native writer in english, and force a non native read more than once to understand".
# He also asked whether the law covered either; it did not, measured (`grep -cin "british"` over
# WRITING_LAW.md and AGENT_GUARDRAILS.md returned 0 and 0). WRITING_LAW §1 now bans both classes.
# HALF MECHANICAL, HALF JUDGMENT, and the gate says which is which in its own docstring: the British
# spellings and constructions are gated hard, and four expressible hard-phrasing shapes are gated;
# whether a sentence reads on the first pass is persona 15's verdict
# (reviewers/15_readability_editor.md lens 2), which this gate points at rather than duplicating.
# A GREEN RESULT HERE IS NOT A FIRST-READ PASS.
# SCOPE INCLUDES references.bib, because the .tex-only version of this gate reported clean while
# "towards" printed on page 82 of the defense build -- the bibliography is not a .tex file. Only the
# fields WE author are checked (note/annote/abstract/howpublished/addendum); title, journal and author
# are attributes of record under §1 R2, and the one British form in the bibliography is inside
# Xu2023's published title, which reads "towards" at Crossref 10.1145/3582553.
# Validated in both directions against his real sentences: planting "feature needs saying plainly" in
# a live line gives rc=1 naming the file and the rule, restoring gives rc=0; the American twin of
# every spelling family is asserted NOT to fire; and a stale open-register entry fails rather than
# silently passing. Transcript in _history/_round9/44_register_law.md.
if ! python3 "$UTILS/check_register.py"; then FAIL=1; fi

gate "== audit APPLIED claims re-measured against the source (round 8: 8 of 9 were false) =="
# THE GATE THAT DID NOT EXIST. On 2026-07-28 an outcome table recorded sixteen findings as APPLIED;
# on 2026-07-30 eight of the author's nine instructions were still not in the document, five of them
# under rows asserting they were done. Twenty gates were green throughout -- the one artifact with no
# gate was the document certifying all the others. _history/_round8/28_postmortem_false_applied.md and
# AGENT_GUARDRAILS §4b V14. Runs in ~0.1 s; it would have failed loudly on the day.
if ! python3 "$UTILS/check_audit_claims.py"; then FAIL=1; fi

gate "== round-9 Wave A: the applied edits re-measured in the RENDERED PDF, both directions =="
# check_audit_claims reads the SOURCE. This one reads the PDF, and the difference is the point: an
# edit can be in the .tex and not reach the page (wrong build gated, a conditional, a stale aux).
# Round 9 claimed "verified in both directions" for seven items when three had been checked that way,
# after already claiming it for an eighth item that was never edited at all. Prose is a claim; this is
# the measurement, and it re-runs in two seconds. Skips cleanly when the PDF has not been built --
# a missing build is not a failed verification, and saying otherwise is how a gate teaches people to
# ignore it.
#
# The path test below reads build/main.pdf RELATIVE to $SRCROOT, which this script has already cd'd
# into -- the same form the .log gates use at the top of this file. It first said "$ROOT/src/...",
# and $ROOT IS NOT DEFINED IN THIS SCRIPT, so the test was always false and the gate reported SKIP
# with the PDF sitting right there. Caught by running it with the file present and reading the
# output instead of the exit code: rc was 0 either way, because a skip is not a failure. A gate that
# cannot fail is indistinguishable from a gate that passes, which is the whole reason this suite
# self-tests.
if [ -f build/main.pdf ]; then
  if ! python3 "$UTILS/_history/_round9/35_wave_a_render_check.py" build/main.pdf >/dev/null; then
    python3 "$UTILS/_history/_round9/35_wave_a_render_check.py" build/main.pdf || true
    FAIL=1
  else
    echo "  16 two-directional assertions over 7 edited items hold in build/main.pdf,"
    echo "  plus 2 presence checks on FAB-01, which was already satisfied and never edited."
  fi
else
  echo "  SKIP: src/build/main.pdf not built. Run 'make defense' to check the rendered claims."
fi

gate "== TeX root directives (invisible to make: only an editor build ever notices) =="
# Two silent defects in one week, both found by review rather than by any gate: six files pointing
# at a main_defense.tex that has never existed in this tree, and six others with no directive at
# all, which after the per-section split included the three paper-chapter masters -- the files an
# editor opens to navigate. `make` reads main.tex and never looks at a magic comment, so the cost
# lands on whoever opens a file in an editor. Now checked.
if ! python3 "$UTILS/check_tex_root.py"; then FAIL=1; fi

gate "== negative-parallelism density (a standing guard that lived only in a review report) =="
# The AI-credibility persona froze this count on 2026-07-20 and found it raised from 67 to 79 on
# 2026-07-28, with its own verdict on why: "a guard that lives only in a previous round's review
# report is a guard nobody is checking." So the instruction moved into the gate. Density per 1k
# prose words, comments stripped (this repo's provenance comments quote the constructions).
if ! python3 "$UTILS/check_negative_parallelism.py"; then FAIL=1; fi

gate "== doubled backslash before a reference macro (silent: no warning, undef_ref stays 0) =="
# A THIRD silent class, found 2026-07-28 in 5_mobiwac.tex:789. Two cross-references written
# "\\ref{...}" with a doubled backslash: LaTeX reads a line break followed by the literal text
# "ref{tab:mobiwac:results}", so page 75 of the defense PDF printed the raw label to the reader.
# INVISIBLE TO EVERY OTHER GATE: pdflatex raises nothing (both halves are legal), and undef_ref
# stays at 0 because there is no reference to leave undefined -- every build report since the
# defect landed said undef_ref=0, truthfully. Validated both ways against the real historical
# file: 2 hits at 232befd5~1, 0 after the fix, and its own self-test runs before it reports.
if ! python3 "$UTILS/check_doubled_macro.py"; then FAIL=1; fi

gate "== comment hygiene: a duplicated story, or a self-count that disagrees with its file =="
# Round 7 measured the BUILD files' comments (round 6 had measured the chapters' and correctly
# recommended against compressing those). The defect there is duplication, not commentary: the
# "three builds, one source" story was told in 5 files, the nested-\if hazard in 4, the usermode
# TeX tree in 4, halt-on-error vs nonstopmode in 5, and "main_ppgc.tex is N lines" in 7 places --
# THREE of which said "four lines" for a file with 2 content lines. Neither class is visible to
# any other gate: every copy is legal LaTeX or Make, so nothing warns, and a comment that is
# merely WRONG costs whoever believes it. Validated both ways against the real historical tree
# reconstructed from 0bfc9e5e: CLASS B reports the 3 wrong copies there and 0 here; CLASS A
# reports README_SRC.md as a second full telling there and 0 here. Its own self-tests build
# synthetic defective and fixed trees and run before it reports.
if ! python3 "$UTILS/check_comment_hygiene.py"; then FAIL=1; fi

gate "== prose trapped inside a % comment (silent: builds clean, reader sees a broken sentence) =="
# Has happened twice: apx_a_contributions.tex, and 4_courb.tex:187 where half a PUBLISHED
# methodology sentence was appended to a comment tail and three method facts stopped rendering.
DETECTOR=""; FIXTURES=""
for d in "src_utils" "../src_utils"; do
  if [ -f "$d/check_trapped_prose.py" ]; then
    DETECTOR="$d/check_trapped_prose.py"; FIXTURES="$d/test_trapped_prose.py"; break
  fi
done
if [ -z "$DETECTOR" ]; then
  echo "SKIP: check_trapped_prose.py not found"
else
  # Run the detector's OWN fixtures first. The checker has been wrong four times, each time by
  # being tuned on the cases in front of it, so a green document means nothing unless the checker
  # still catches every defect that has actually shipped.
  if [ -f "$FIXTURES" ]; then
    # Capture the OUTPUT and the EXIT STATUS separately. Do NOT pipe into tail here: without
    # `set -o pipefail` a pipeline reports the status of its LAST command, so `python3 ... | tail -1`
    # always returns 0 and the failure branch below becomes unreachable. That defect shipped once,
    # in a commit that advertised this very block as a gate.
    FIXTURE_OUT="$(python3 "$FIXTURES" 2>&1)"
    FIXTURE_RC=$?
    echo "$FIXTURE_OUT" | tail -1
    if [ "$FIXTURE_RC" -ne 0 ]; then
      echo "  ^ detector fixtures FAILED — the checker itself is broken, its result is not evidence"
      echo "$FIXTURE_OUT" | grep '^FAIL' | sed 's/^/    /'
      FAIL=1
    fi
  fi
  if ! python3 "$DETECTOR"; then FAIL=1; fi
fi

gate_report

exit $FAIL
