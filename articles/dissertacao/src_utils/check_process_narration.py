#!/usr/bin/env python3
"""check_process_narration.py -- prose may not narrate how the work was done.

THE DEFECT IT ANSWERS. The author read Appendix F on 2026-07-30 and found this in the deposited
prose: "California, Texas, and Istanbul were absent from an earlier version of this appendix, and
their absence was a matter of computational resource rather than of principle: the machine that would
have run them was out of disk." His objection was exact -- a dissertation states what is true, and a
lab machine's free space is not a fact about mobility data. He also asked whether the governing
documents banned it. They did not: `grep -cin "process narration|out of disk|the machine that"` over
AGENT_GUARDRAILS.md and WRITING_LAW.md returned 0 and 0. The rule is now WRITING_LAW §1, and this file
is its enforcement.

WHY A GATE AND NOT JUST A RULE. Every other prose gate here exists because a rule alone did not hold:
the trapped-prose, torn-sentence and doubled-macro classes were each written down before they were
gated, and each recurred. Process narration is the easiest class to reintroduce, because an agent that
has just done difficult work is the one most tempted to explain the difficulty.

FOUR SUB-CLASSES, each pattern taken from a real instance rather than imagined:
  infrastructure       "out of disk", "the machine that", GPU/queue/wall-clock/checkpoint mentions
  version history      "an earlier version of this appendix", "originally reported"
  effort scheduling    "computational resource", "were measured afterward", "at the time of writing"
  writing self-talk    "the paragraph above", "as noted above", "this appendix originally"

SCOPE. Live prose only: comments are stripped with the SAME `(?<!\\)%` rule the audit gate uses, since
provenance comments quote the banned sentences verbatim and must not be flagged -- this file's own
docstring would trip a comment-blind checker. Scope is derived from the filesystem with a FLOOR, not
hardcoded: a chapter split silently shrank a prose gate's scope twice on this project, and both times
the gate reported a clean sweep of almost nothing.

TWO DELIBERATE EXEMPTIONS, both narrow:
  - apx_b_errata.tex and tables/*/errata.tex: the errata appendix's PURPOSE is to record what changed
    between the published and reproduced text. Version history is its subject matter.
  - apx_c_ai_disclosure.tex: a disclosure appendix must describe the process by which the document was
    written. That is the one place where narrating the work IS the content.
Anything else is in scope, including the frame chapters and every appendix.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"

COMMENT = re.compile(r"(?<!\\)%")

EXEMPT = {
    "apx_b_errata.tex",       # errata: version history is the subject
    "apx_b_static_scope.tex",  # included from the errata appendix, same regime
    "apx_c_ai_disclosure.tex",  # AI disclosure: describing the process IS the content
}

# (class, pattern, the real instance it was written from)
RULES: tuple[tuple[str, str, str], ...] = (
    ("infrastructure",
     r"out of disk|the machine that would|ran out of (?:disk|memory|space)|free space on|"
     r"wall.clock (?:cap|limit)|the GPU was|checkpoint files? (?:filled|took)",
     'Appendix F 2026-07-30: "the machine that would have run them was out of disk"'),
    ("version history",
     r"an earlier version of this (?:appendix|chapter|section)|"
     r"(?:this|the) (?:appendix|chapter|section) originally|originally reported|"
     r"a previous version of this",
     'Appendix F 2026-07-30: "absent from an earlier version of this appendix"'),
    ("effort scheduling",
     # "at the time of writing" is banned EXCEPT where it qualifies a publication status, which is the
     # one case where the circumstance genuinely belongs to the reader: a submitted paper's review
     # state changes, and this project's law requires the status be stated as "submitted, under
     # review" and never upgraded. The negative lookbehind spares that construction and nothing else.
     # Found by the gate's first run on chapters/5_mobiwac.tex: "under review at the time of writing
     # (EDAS #1571313639)". That sentence is honest and required; flagging it would have taught the
     # next agent to weaken a status claim, which is the opposite of the law.
     r"a matter of computational resource|were measured afterward|"
     r"(?<!under review )at the time of (?:writing|this writing)|were added later|we then ran",
     'Appendix F 2026-07-30: "a matter of computational resource rather than of principle"'),
    ("presence justification",
     # A FIFTH SHAPE, found 2026-07-30 by the style persona reading 79 of 79 Appendix F sentences after
     # this gate had already reported rc=0. Appendix F said Georgia "enters because the diagnostic ran on
     # it cheaply and stays because dropping a measured dataset would be a choice about the evidence".
     # Not infrastructure, not version history, not scheduling, not self-talk: it explains why a dataset
     # is PRESENT, and grounds it in a run's cost and an editorial decision. The four original patterns
     # were each written from one deleted sentence, so they covered that sentence's shapes and no others.
     r"ran on it cheaply|because the diagnostic ran|it enters because|"
     r"stays because dropping|would be a choice about the evidence|"
     r"(?:included|kept|retained) (?:here )?because (?:it|the run|the measurement) (?:was|were) (?:cheap|free|available)",
     'Appendix F 2026-07-30: "it enters because the diagnostic ran on it cheaply"'),
    ("writing self-talk",
     r"the paragraph above (?:draws|shows|states)|as noted above|as mentioned above|"
     r"the (?:preceding|previous) paragraph (?:draws|shows)",
     'Appendix F 2026-07-30: "the boundary the paragraph above draws"'),
)


def live_text(path: Path) -> str:
    """Source with comments removed, joined into one whitespace-normalized string.

    Joined on purpose: a banned phrase that wraps to the next line is invisible to a per-line regex,
    and that exact trap produced a false clean verdict on this project twice in one week.
    """
    keep = []
    for line in path.read_text(encoding="utf-8", errors="replace").split("\n"):
        m = COMMENT.search(line)
        cut = line[: m.start()] if m else line
        if cut.strip():
            keep.append(cut)
    return re.sub(r"\s+", " ", " ".join(keep))


def self_test() -> None:
    """Both directions, on literals reduced from the real deleted paragraph."""
    banned = ("their absence was a matter of computational resource rather than of principle: "
              "the machine that would have run them was out of disk.")
    fired = [c for c, pat, _ in RULES if re.search(pat, banned, re.I)]
    assert len(fired) >= 2, (
        f"self-test: the real deleted sentence must trip at least two rules, tripped {fired}. "
        "Reporting now would turn a present defect into a pass."
    )
    clean = ("The observations are 4,650 epoch-level cosines from seven datasets, and this appendix "
             "covers one architecture family.")
    assert not any(re.search(pat, clean, re.I) for _, pat, _ in RULES), (
        "self-test: a legitimate limitation sentence was flagged. A limitation is a property of the "
        "evidence and must pass; only the narration of how it came about is banned."
    )
    # the stripper must respect an escaped percent, or a long line is truncated and its tail hidden
    assert "TAIL" in live_text_from_string(r"a 90\% interval and then TAIL"), (
        "self-test: an escaped \\% truncated the line -- the pattern must be (?<!\\\\)%"
    )
    assert "COMMENTED" not in live_text_from_string("prose\n% COMMENTED words"), (
        "self-test: a real % comment leaked into live text, so provenance comments quoting the "
        "banned sentences would be flagged as violations"
    )


def live_text_from_string(raw: str) -> str:
    keep = []
    for line in raw.split("\n"):
        m = COMMENT.search(line)
        cut = line[: m.start()] if m else line
        if cut.strip():
            keep.append(cut)
    return re.sub(r"\s+", " ", " ".join(keep))


def in_scope() -> list[Path]:
    """Every .tex under src/, minus the exemptions. Derived, with a floor."""
    files = sorted(p for p in SRC.rglob("*.tex")
                   if p.name not in EXEMPT and "build" not in p.parts)
    FLOOR = 20
    if len(files) < FLOOR:
        print(f"FAIL: scope collapsed to {len(files)} file(s), below the floor of {FLOOR}. A file "
              f"move or rename has taken prose out of this gate's reach, which is how two other "
              f"prose gates on this project silently swept almost nothing.")
        sys.exit(2)
    return files


def main() -> int:
    self_test()
    print("== process narration in prose (WRITING_LAW §1: state the work, never narrate it) ==")
    files = in_scope()
    hits = []
    for f in files:
        txt = live_text(f)
        for cls, pat, instance in RULES:
            for m in re.finditer(pat, txt, re.I):
                ctx = re.sub(r"\s+", " ", txt[max(0, m.start() - 60):m.end() + 60])
                hits.append((f.relative_to(SRC), cls, m.group(0), ctx, instance))
    for rel, cls, got, ctx, instance in hits:
        print(f"  {rel}: [{cls}] {got!r}")
        print(f"      ...{ctx}...")
        print(f"      the rule was written from: {instance}")
    if hits:
        print(f"\nFAIL: {len(hits)} passage(s) narrate the process instead of stating the work. A "
              f"reader cannot verify that a machine was full, and the sentence becomes false the day "
              f"the circumstance changes. Move the reason to a source comment or a round report; if "
              f"the reader must know a limitation, state it as a property of the evidence.")
        return 1
    print(f"OK: no process narration in {len(files)} files "
          f"({len(EXEMPT)} exempt: errata and AI disclosure, where the process IS the subject); "
          f"self-test passed in both directions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
