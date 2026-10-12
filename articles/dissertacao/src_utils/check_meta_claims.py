#!/usr/bin/env python3
"""check_meta_claims.py -- flag coverage claims in durable records that carry no command.

WHY THIS EXISTS (measured). Round 6, 2026-07-28: 13.3 hours, 61 commits, 17 of them rework. Of the
14 genuine rework commits, TWELVE were a wrong statement about the WORK rather than about the
dissertation -- what a check covered, what a command returned, whether a gate passed. Zero were
fabricated citations: the science protocols (AGENT_GUARDRAILS §1-§2) were holding, and nothing
protected the record of the work.

AGENT_GUARDRAILS §4b V1 is the rule this enforces:

    A number about the work carries the command that produced it.

So a sentence like "all 19 commands were executed" or "the sweep covered 49 files" is only admissible
in a durable record if a runnable command sits near it. A number without its command is an opinion
with a digit in it -- and it is exactly what twelve rework commits had to go back and fix.

WHAT IT CHECKS. In the author-facing and durable records (not chapter prose, not reports that are
themselves the measurement), find sentences making a COVERAGE claim -- a count paired with a
coverage verb -- and require a fenced command block or an inline `code` command within a short
window. Flags what has no command, so the writer either adds one or rewords the claim.

DELIBERATELY NARROW. It looks for a count adjacent to a coverage verb, which is the shape the twelve
defects had. It does not try to parse prose generally: a checker that flags everything is a checker
people switch off, and this repository already has a documented case of a gate whose only hit was a
known-good line, which trained everyone to read past its exit code.

SELF-TEST runs before it reports, in both directions (§7: validate every new gate against a tree
where the defect is present, then against the fixed one).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DISS = Path(__file__).resolve().parent.parent

# Durable records the author or a future agent ACTS on. Reports under _history/_round6/ are excluded:
# they are the measurement itself, and their numbers are traceable through the report's own body.
TARGETS = [
    "src_utils/PENDENCIAS.md",
    "src_utils/_history/_round6/VERIFY_LIST.md",
    "CLAUDE.md",
    "src_utils/README_SRC.md",
]

# A coverage claim: a count next to a verb of coverage. The twelve defects were all this shape.
# A COUNT, not a date and not a version. Dates were the entire false-positive population of the
# first version of this gate: "verified 2026-07-18" matched as "a count next to a coverage verb"
# six times out of six. A count here is 1-4 digits that is NOT a year and NOT part of a date.
COUNT = r"(?:\*\*)?(?!(?:19|20)\d\d\b)\d{1,4}(?:\*\*)?"
VERB = (r"(?:executed|verified|checked|covered|passed|scanned|swept|ran)")
# The count must be QUANTIFYING the coverage: adjacent, and with a plural noun of things between
# them ("49 files ... passed", "all 19 commands were executed"). This is the shape the twelve
# round-6 defects had, and it excludes "verified <date>" and "verified vs manual §7".
NOUN = r"(?:files?|commands?|blocks?|gates?|checks?|entries|entradas|paths?|caminhos?|" \
       r"claims?|afirma\w+|cells?|instances?|targets?|hits?|references?|scripts?|rows?|" \
       r"sites?|coordinates?|figures?|tables?|chapters?|arquivos?|comandos?)"
# A UNIVERSAL quantifier counts as a coverage claim too, and this is the shape of the WORST
# instance: "Every command in this file was executed verbatim ... and returns the output its
# 'if all is well' line describes" -- written when four blocks had never run and no output had
# been compared to any expectation. It carries no digit at all, so a count-based pattern misses
# exactly the defect that cost the most. Universals are held to the SAME rule as counts.
QUANT = r"(?:every|each|all|todos?|todas?|cada)"
CLAIM = re.compile(
    rf"\b{COUNT}\s+(?:\w+\s+){{0,2}}{NOUN}\b[^.\n]{{0,50}}\b{VERB}\b"
    rf"|\b{VERB}\b[^.\n]{{0,40}}\b{COUNT}\s+(?:\w+\s+){{0,2}}{NOUN}\b"
    rf"|\b{QUANT}\s+(?:\w+\s+){{0,2}}{NOUN}\b[^.\n]{{0,60}}\b{VERB}\b"
    rf"|\b{VERB}\b[^.\n]{{0,40}}\b{QUANT}\s+(?:\w+\s+){{0,2}}{NOUN}\b",
    re.I)

# Evidence that the claim is backed: a fenced block, or an inline command with a shell/py tool.
FENCE = re.compile(r"```(?:bash|sh|console|python)?\n", re.I)
INLINE_CMD = re.compile(r"`[^`\n]*(?:grep|python3|make|git|wc |sed |bash|\.py|\.sh)[^`\n]*`")
WINDOW = 1800   # characters after the claim in which a command must appear


def _unwrap(text: str) -> str:
    """Join hard-wrapped prose lines so a claim spanning a line break is still one claim.

    Markdown in this repository wraps at ~100 characters, so almost every real coverage claim
    straddles a newline: the worst instance in the round-6 history reads "Every command in\nthis
    file was executed verbatim". A pattern using [^.\n] to stay inside one sentence therefore
    missed exactly the sentences that mattered. Blank lines, fences and list/heading markers are
    preserved so paragraph and code-block structure survives; the character COUNT is preserved
    (newline -> space) so reported line numbers stay correct.
    """
    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines):
        out.append(line)
        if i + 1 >= len(lines):
            continue
        nxt = lines[i + 1].strip()
        cur = line.strip()
        soft = (cur and nxt
                and not nxt.startswith(("#", "-", "*", "|", ">", "```", "1.", "2."))
                and not cur.startswith(("|", "```")))
        if soft:
            out[-1] = out[-1] + "\x00"      # mark: the newline AFTER this line is a soft wrap
    return "\n".join(out).replace("\x00\n", " ")   # 1 char out, 1 in: offsets preserved


# An item RANGE ("Items 7-13 are claims a pass verified", "rows 1-6") is not a coverage count: the
# digits enumerate positions in a list, not things measured. Excluding this shape keeps the gate
# from crying wolf, which matters -- this repository has a documented case of a checker whose only
# hit was a known-good line, and everyone learned to read past its exit code.
RANGE = re.compile(r"(?:items?|rows?|entries|itens|linhas)\s+\d+\s*[-\u2013]\s*\d+", re.I)


def find_unbacked(text: str) -> list[tuple[int, str]]:
    """Return (line_no, snippet) for coverage claims with no nearby command."""
    out = []
    flat = _unwrap(text)
    for m in CLAIM.finditer(flat):
        # A claim inside a fenced block IS the tool's own output -- not a prose claim.
        before = flat[:m.start()]
        if before.count("```") % 2 == 1:
            continue
        # BACKING MUST BE IN THE SAME PARAGRAPH as the claim. A 1800-character window was the
        # first version's rule and it excused the worst real defect: "Every command in this file
        # was executed verbatim" sat two paragraphs above an UNRELATED grep example, and any
        # `grep` anywhere nearby counted as backing. A command that does not sit with the claim
        # is not evidence for it -- the reader cannot tell which claim it supports.
        # skip item ranges ("Items 7-13 are ...") -- positions in a list, not a measured count
        lead = flat[max(0, m.start() - 40):m.end()]
        if RANGE.search(lead):
            continue
        para_start = flat.rfind("\n\n", 0, m.start()) + 2
        para_end = flat.find("\n\n", m.end())
        para = flat[para_start:para_end if para_end != -1 else len(flat)]
        # The command must plausibly BE the evidence for THIS claim, so it has to sit AFTER the
        # claim in its paragraph (the "...was executed; run `X`" shape) or immediately before it
        # ("run `X`: it reports N"). A command quoted incidentally elsewhere in the paragraph is
        # not evidence -- that loophole is what excused the round-6 over-claim, whose paragraph
        # happened to also carry an unrelated `grep -vn` example as advice.
        # Narrower still: the command must be in the SAME SENTENCE as the claim, or in the one
        # immediately before it. A `grep` fragment two sentences later is not evidence for this
        # claim, and that is not hypothetical: the round-6 over-claim escaped a paragraph-scoped
        # rule because its paragraph went on to mention `grep -vn '^%'` as unrelated advice. The
        # rule that holds is the one a reader would apply -- the command has to be *right there*.
        rel = m.start() - para_start
        sent_end = para.find(". ", m.end() - para_start)
        sent_end = len(para) if sent_end == -1 else sent_end + 1
        prev_start = para.rfind(". ", 0, rel)
        prev_start = 0 if prev_start == -1 else prev_start + 2
        scope = para[prev_start:sent_end]
        if INLINE_CMD.search(scope):
            continue
        # A fenced block immediately after the paragraph also backs it (the "run this:" shape),
        # but only if it opens within ~120 chars of the paragraph's end, not anywhere downstream.
        tail = flat[(para_end if para_end != -1 else len(flat)):][:120]
        if FENCE.search(tail):
            continue
        # Count newlines in the ORIGINAL text, not in `flat`: _unwrap turned soft wraps into
        # spaces, so counting in `flat` under-reports the line by the number of joins above it.
        # Offsets are byte-identical between the two (1 char out, 1 char in), so slicing the
        # original at the same offset is exact. This gate reported line 5 for a line-56 claim
        # until this was fixed -- a wrong coordinate in a checker is the defect class in §2.6.
        line = text[:m.start()].count("\n") + 1
        snippet = re.sub(r"\s+", " ", flat[m.start():m.end()])[:96]
        out.append((line, snippet))
    return out


def self_test() -> None:
    bad = "The sweep covered 49 files and every one passed.\n\nNothing else here.\n"
    # The real 2026-07-28 defect, verbatim from VERIFY_LIST.md as it stood at 0aceb5ee~1. It
    # carries NO digit, which is why the first version of this gate scored 0 hits on it.
    historical = ("Paths that reach outside the dissertation folder are written `../../` from "
                  "there. Every command in\nthis file was executed verbatim from that directory "
                  "on 2026-07-28 and returns the output its\n\"if all is well\" line describes.\n")
    assert find_unbacked(historical), (
        "self-test: must flag the real historical over-claim (a universal quantifier with a "
        "coverage verb and no command)")
    good = ("The sweep covered 49 files and every one passed.\n\n"
            "```bash\ngrep -c foo bar\n```\n")
    inline_ok = "All 19 commands were executed; run `python3 src_utils/check_verify_list.py`.\n"
    fenced_output = ("Report:\n\n```\n16 documented command(s) executed; 7 asserted\n```\n")
    assert find_unbacked(bad), "self-test: must flag a coverage claim with no command"
    assert not find_unbacked(good), "self-test: must accept a claim followed by a fenced command"
    assert not find_unbacked(inline_ok), "self-test: must accept an inline command"
    assert not find_unbacked(fenced_output), "self-test: must not flag a tool's own output"
    # A command in a DIFFERENT paragraph is not backing. This is the exact shape that excused the
    # historical defect under the first version's 1800-character window.
    far = ("Every command in this file was executed verbatim and returns what it should.\n\n"
           "Unrelated advice: greps over .tex files should use `grep -vn '^%' file`.\n")
    assert find_unbacked(far), (
        "self-test: a command in an unrelated paragraph must NOT count as backing")
    # The real escape route: SAME paragraph, but two sentences later and about something else.
    same_para = ("Every command in this file was executed verbatim and returns the output its "
                 "line describes. Greps over .tex files strip comments first "
                 "(`grep -vn '^%'`), because this source quotes what you search for.\n")
    assert find_unbacked(same_para), (
        "self-test: a command two sentences later, on another subject, must NOT count as backing")
    # ...and the legitimate shape must still pass.
    same_sentence = ("All 19 commands were executed by `python3 src_utils/check_verify_list.py`, "
                     "which reports 7 asserted.\n")
    assert not find_unbacked(same_sentence), (
        "self-test: a command in the claim's own sentence IS backing")
    # An item range enumerates list positions; it is not a coverage count.
    rng = "Items 7-13 are claims a pass verified about its own work, where none have looked.\n"
    assert not find_unbacked(rng), "self-test: an item range is not a coverage claim"


# --- §4b arithmetic: the headline must equal the table it sits above -------------------------
# WHY. The first version of §4b said "fourteen were genuine ... of which nine (64%)
# share one property" directly above a table whose rows read R1=5, R2=4, R4=3. Five plus four plus
# three is twelve, not nine. The 9 came from a hard-coded literal in an f-string
# (`print(f"R1+R2+R4 = {9}/{real}")`) while the surrounding cell computed the row counts correctly
# -- so the transcript printed a contradiction and I copied the wrong half into four durable files.
# The rule this file exists to enforce, applied to this file's own founding statistic.
GUARDRAILS = DISS / "AGENT_GUARDRAILS.md"
# The table's last row is a COMBINED "R3/R5", so a per-cause regex silently drops it and the
# denominator comes out as 12 instead of 14 -- which made this checker's first run report a
# percentage error that was the CHECKER's, not the document's. Match combined labels too.
ROW = re.compile(r"\*\*(R[0-9](?:/R?[0-9])*)\*\*[^|]*\|[^|]*\|\s*(\d+)\s*\|")
HEADLINE = re.compile(r"\*\*(\w+)\s*\n?\((\d+)%\)\s*share one property\*\*", re.I)
WORDNUM = {"nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14}


def check_4b_arithmetic() -> list[str]:
    """Headline count in §4b must equal the sum of the R1/R2/R4 rows in its own table."""
    if not GUARDRAILS.exists():
        return []
    text = GUARDRAILS.read_text(encoding="utf-8")
    flat = _unwrap(text)
    m = HEADLINE.search(flat)
    if not m:
        return ["AGENT_GUARDRAILS.md: §4b headline sentence not found — "
                "if it was reworded, update check_4b_arithmetic() or the guarantee is gone"]
    word, pct = m.group(1).lower(), int(m.group(2))
    claimed = WORDNUM.get(word)
    if claimed is None:
        return [f"AGENT_GUARDRAILS.md: §4b headline count {word!r} not recognised"]
    rows = {r: int(n) for r, n in ROW.findall(text)}
    # META = the causes named in the headline's own grouping; a combined label like "R3/R5" is
    # never part of it, so membership is tested per constituent cause.
    META_CAUSES = {"R1", "R2", "R4"}
    meta = sum(v for k, v in rows.items() if set(k.replace("R", "").split("/")) &
               {c[1:] for c in META_CAUSES} and "/" not in k)
    genuine = sum(rows.values())
    problems = []
    if meta != claimed:
        problems.append(f"AGENT_GUARDRAILS.md: §4b headline says {word} ({claimed}) share the "
                        f"property, but its own table rows R1+R2+R4 sum to {meta} "
                        f"({'+'.join(str(rows[k]) for k in ('R1','R2','R4') if k in rows)})")
    if genuine and round(claimed / genuine * 100) != pct:
        problems.append(f"AGENT_GUARDRAILS.md: §4b headline percentage {pct}% does not match "
                        f"{claimed}/{genuine} = {round(claimed/genuine*100)}%")
    return problems


def main() -> int:
    self_test()
    total = 0
    for problem in check_4b_arithmetic():
        print(problem)
        total += 1
    for rel in TARGETS:
        path = DISS / rel
        if not path.exists():
            continue
        hits = find_unbacked(path.read_text(encoding="utf-8"))
        for line, snippet in hits:
            print(f"{rel}:{line}: coverage claim with no command in range -> {snippet}")
            total += 1
    if total:
        print(f"\nFAIL: {total} coverage claim(s) about the work carry no runnable command.")
        print("AGENT_GUARDRAILS §4b V1: a number about the work carries the command that produced")
        print("it. Add the command, or reword the claim so it does not assert coverage.")
        return 1
    print(f"OK: coverage claims in {len(TARGETS)} durable records all carry a command "
          f"(self-test passed in both directions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
