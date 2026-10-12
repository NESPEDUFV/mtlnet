#!/usr/bin/env python3
"""check_tracker_refs.py -- every live PENDENCIAS section citation must resolve.

WHY THIS EXISTS. On 2026-07-29 PENDENCIAS.md was renumbered (2.3-2.7 -> 2.4-2.8) to insert a new
item. Four source comments cited "PENDENCIAS 2.2" for the static-scope section. Three were
repointed; the fourth -- apx_b_static_scope.tex's own header, the file the citation is ABOUT -- was
missed, and the commit message claimed all four had been done. The grep that found four was run,
its output was read, and the fix list was written with three entries.

Nothing caught it, because a stale section number is not a LaTeX error, not an undefined reference,
and not a broken link. It renders fine and points somewhere wrong. That is the same silent class as
AGENT_HANDOFF §2.6 (records that drift from the thing they describe): the citation and its target
drift apart and only a reader who follows the pointer notices.

WHAT IT CHECKS. Every `PENDENCIAS <n>.<m>` citation in the live tree resolves to a heading that
exists in PENDENCIAS.md. A citation may be deliberately historical -- the tracker is rewritten every
round and a quote can outlive its coordinate -- so a citation is EXEMPT when its own text says so,
by carrying "was <n>.<m>" or naming the date of the tracker it refers to. That keeps the gate from
punishing an honest historical reference while still catching a silently orphaned one.

DELIBERATELY NOT CHECKED: citations inside dated audit records (_round*/, _review_v*/, _history/_archive/,
_gates/, _specialists*/). Those describe a tracker as it stood and must not be rewritten.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DISS = Path(__file__).resolve().parent.parent
TRACKER = DISS / "src_utils" / "PENDENCIAS.md"
SKIP = ("_round", "_review_v", "_archive", "_gates", "_specialists", "/build/", "__pycache__")

# The citation may or may not carry a section symbol, and BOTH spellings are in the live tree.
# Found 2026-07-29 (round 8 audit): the original pattern was `PENDENCIAS\s+(\d+)\.(\d+)`, which
# requires whitespace immediately before the digits and therefore could not see `PENDENCIAS_RESOLVIDOS §2.9 (arquivado 2026-08-02)`.
# Two live citations use that spelling -- src/chapters/apx_f_cosine.tex:316 and
# src_utils/check_verify_list.py:128 -- so this gate reported "every live citation resolves" while
# never having looked at them. Reproduced before the fix: a file citing `PENDENCIAS §9.9` (no such
# heading) gave RC=0; the same file with `PENDENCIAS 9.9` gave RC=1. That is T1/T2 -- a guard whose
# pattern is a list of the spellings that existed when it was written. The `§` may also arrive as
# `\S` from LaTeX source or as the word "section".
# A SECOND BLINDNESS OF THE SAME CLASS, found 2026-07-30 (round 9c): the tracker numbers a
# subdivided item with a LETTER SUFFIX -- `### 5.6b A premissa da sua decisao 5.6 nao e o que os
# arquivos mostram` is a live heading, and `1b.1`, `2b.1` are in the archive. Neither pattern below
# could express one. HEADING required a word boundary right after the second number, and in "5.6b"
# the digit and the letter are both word characters, so no boundary exists there and the heading was
# invisible. CITE stopped at the digits, so a comment citing `PENDENCIAS_RESOLVIDOS 5.6b (arquivado 2026-08-02)` produced the
# coordinate (5, 6) and was reported as pointing at a section that does not exist -- which was true
# of 5.6, archived, and false of 5.6b, live and open. Reproduced before the fix: three round-9c
# comments citing the author's own item number failed this gate while the heading sat in the tracker.
# The suffix is now part of the key on BOTH sides, so 5.6 and 5.6b are different coordinates and a
# citation of the archived 5.6 still fails, which is the behavior that caught the renumber of 2.2.
CITE = re.compile(r"PENDENCIAS\s*(?:§|\\S|[Ss]ection|[Ss]ec\.?|item)?\s*(\d+)\.(\d+)([a-z]?)(?![\w.])")
# O `(?:\u00a7\s*)?` foi acrescentado em 2026-08-28. Sem ele o regex exigia o digito logo a seguir
# aos `#`, e as seccoes escritas `## \u00a74.1 \u00b7 ...` ficavam INVISIVEIS ao gate -- que entao
# declarava FAIL sobre citacoes corretas a \u00a74.1 e \u00a74.2. O gate estava cego a uma familia
# inteira de seccoes e a acusar quem as citava certo.
HEADING = re.compile(r"^#{2,4}\s+(?:~~)?(?:\u00a7\s*)?(\d+)\.(\d+)([a-z]?)(?![\w.])", re.M)
# An exemption must be adjacent to the citation, not anywhere in the file: a "was 2.2" on line 400
# does not license a bare "PENDENCIAS 2.2" on line 3. 90 chars is about one wrapped line.
EXEMPT = re.compile(r"was\s+\d+\.\d+|tracker (?:of|was)|no longer resolves|de que data|daquela data")


def sections() -> set[tuple[str, str, str]]:
    if not TRACKER.exists():
        return set()
    return {(a, b, c) for a, b, c in HEADING.findall(TRACKER.read_text(encoding="utf-8"))}


def scan() -> list[str]:
    live = sections()
    if not live:
        return [f"{TRACKER.name}: no numbered section headings found -- "
                f"if the format changed, update check_tracker_refs.py or this gate is blind"]
    problems = []
    for path in sorted(DISS.rglob("*")):
        if not path.is_file() or path.suffix not in (".tex", ".md", ".sh", ".py"):
            continue
        rel = str(path.relative_to(DISS))
        if any(s in rel for s in SKIP) or rel.endswith("check_tracker_refs.py"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in CITE.finditer(text):
            key = (m.group(1), m.group(2), m.group(3))
            if key in live:
                continue
            window = text[m.start(): m.start() + 90]
            if EXEMPT.search(window):
                continue          # honest historical citation, says so on its own line
            line = text[:m.start()].count("\n") + 1
            problems.append(f"{rel}:{line}: cites PENDENCIAS {key[0]}.{key[1]}{key[2]}, "
                            f"which is not a heading in PENDENCIAS.md")
    return problems


def self_test() -> None:
    live = sections()
    assert live, "self-test: the tracker must expose numbered headings"
    # a bare citation of a nonexistent section is a finding; the same with "was N.M" is not
    assert not EXEMPT.search("PENDENCIAS 2.2: deixe isso facil"), \
        "self-test: a bare citation must NOT be exempt"
    assert EXEMPT.search("PENDENCIAS 2.4, was 2.2 before the renumber"), \
        "self-test: a citation carrying 'was N.M' must be exempt"
    # EVERY SPELLING IN THE LIVE TREE MUST BE VISIBLE TO CITE. A guard written as the set of
    # spellings that existed on the day it was written expires without announcing it, and this one
    # had: `PENDENCIAS_RESOLVIDOS §2.9 (arquivado 2026-08-02)` was invisible for as long as the gate existed. Each variant below is
    # asserted to yield the SAME coordinate, so adding a spelling to the tree without adding it
    # here fails the self-test instead of passing the gate.
    for variant in ("PENDENCIAS 2.4", "PENDENCIAS §2.4", "PENDENCIAS \\S2.4",
                    "PENDENCIAS section 2.4", "PENDENCIAS Sec. 2.4"):
        assert CITE.findall(variant) == [("2", "4", "")], \
            f"self-test: CITE cannot see the spelling {variant!r} -- it would go unchecked"
    # ...and a bare number that is not a tracker citation must not be swept in.
    assert not CITE.findall("see Table 2.4 of the manual"), \
        "self-test: CITE must not match a coordinate that does not name the tracker"
    # SEVERANCE, both directions, on literals so the property cannot drift with the tracker's text.
    # A rule BEFORE an item of the same section is the defect; a rule that closes the section (next
    # line is a `##`) is legitimate and must not fire, or every well-formed section fails.
    assert _severed_in("## §2 · x\n\n### 2.1 a\n\n---\n\n### 2.2 b\n"), \
        "self-test: a '---' between two items of §2 must be reported -- it visually ends the section"
    assert not _severed_in("## §2 · x\n\n### 2.1 a\n\n---\n\n## §3 · y\n\n### 3.1 c\n"), \
        "self-test: a '---' that CLOSES a section must not fire; that is this file's own convention"
    # AND the reset branch, which the two assertions above do NOT reach. Without it a rule stays
    # "pending" across intervening prose and fires on whatever item comes next, however far below --
    # a false positive on a shape this file does not consider a defect. Sabotaging `elif
    # line.strip():` left both assertions above passing, which is AGENT_GUARDRAILS §4b V13's fourth
    # instance (a self-test that does not cover a detector reads as proof while proving nothing), so
    # the branch gets its own literal.
    assert not _severed_in("## §2 · x\n\n### 2.1 a\n\n---\n\nprose resumes here\n\n### 2.2 b\n"), \
        "self-test: prose after a '---' must clear it -- only a rule ADJACENT to an item severs"


def nesting_problems() -> list[str]:
    """A "### N.M" heading must sit under its own "## §N", not under some other section's.

    FOUND 2026-07-30 BY THE AUTHOR, not by this gate. Items 2.9 and 2.10 were appended at the end of
    the file, which by then was inside "§5 - raised from CODEX_AUDIT", so a reader following the
    headings found a GPU-disk item and a checker-coverage item filed under an audit they have
    nothing to do with. Every citation still resolved -- scan() was green throughout -- because a
    citation resolves on the NUMBER and this defect is about POSITION.

    That is the same shape as the round-6 failure this whole round is about: the check that existed
    was green, and the thing that was wrong was not the thing it checked.
    """
    out, current = [], None
    for line in TRACKER.read_text(encoding="utf-8").split("\n"):
        m_sec = re.match(r"^## §(\d+)\b", line)
        if m_sec:
            current = m_sec.group(1)
            continue
        m_item = re.match(r"^### (\d+)\.(\d+)\b(.*)", line)
        if m_item and current is not None and m_item.group(1) != current:
            out.append(
                f"MISFILED  item {m_item.group(1)}.{m_item.group(2)} sits inside §{current}: "
                f"{m_item.group(3).strip()[:56]}"
            )
    return out


def severed_items() -> list[str]:
    """A horizontal rule inside a section visually ends it before its items run out.

    THE RESIDUAL OF THE DEFECT ABOVE, found 2026-07-30 after nesting_problems() was already green.
    In this tracker `---` is a SECTION separator: it precedes `## Como ler`, `## §2`, `## §3` and
    `## §4` and nothing else. Items 2.8, 2.9 and 2.10 were originally APPENDED AT THE END of the
    file, each behind such a rule. Commit 74e8e411 moved their HEADINGS under §2 and the rules came
    with them, so §2 read as though it closed after 2.7 and three items sat past its apparent end --
    which is the same reader-navigation failure nesting_problems() exists to prevent, one layer
    down. Heading nesting was correct, every citation resolved, and the file still misled.

    So the rule is: between a `## §N` and the next `##`, a `---` may not appear before a `### N.M`.
    A rule at the very end of the section (immediately before the next `##`) is legitimate -- that
    is what closes the section.
    """
    return _severed_in(TRACKER.read_text(encoding="utf-8"))


def _severed_in(text: str) -> list[str]:
    """The severance rule on a STRING, so self_test() can prove it without a file on disk."""
    lines = text.split("\n")
    out, current, pending_rule = [], None, None
    for i, line in enumerate(lines, start=1):
        if re.match(r"^## ", line):
            current = re.match(r"^## §(\d+)\b", line)
            current = current.group(1) if current else None
            pending_rule = None
            continue
        if current is None:
            continue
        if line.strip() == "---":
            pending_rule = i
            continue
        m_item = re.match(r"^### (\d+)\.(\d+)\b(.*)", line)
        if m_item and pending_rule is not None:
            out.append(
                f"SEVERED   a '---' at line {pending_rule} closes §{current} before item "
                f"{m_item.group(1)}.{m_item.group(2)} at line {i}: "
                f"{m_item.group(3).strip()[:44]}"
            )
            pending_rule = None
        elif line.strip():
            pending_rule = None
    return out


def orphaned_items() -> list[str]:
    """An item that leaves PENDENCIAS.md must be archived, not deleted.

    THE DEFECT, found by the author on 2026-07-30 and then measured across all 63 revisions of the
    tracker: 91 distinct items have existed by title; 30 are live; 61 left. Nineteen went to
    _history/_archive/PENDENCIAS_RESOLVIDOS.md as intended. Of the rest, most were retitles of an item that is
    still live or archived (the sign-off marker item alone was retitled six times as its count changed,
    27 -> 31 -> 32 -> 46 -> 53 -> 55). Seven survived that filter as candidate losses, and the first
    version of this docstring said "TWO were real losses" -- a count taken before two of the seven had
    been measured at all. Corrected after review. All seven, each probed:

      * Ch.4 ITALICS -- LOST. 153 \emph of ordinary English, title said "e uma decisao sua", gone at
        1ef83867 with no decision and no archive entry. Restored as 2.20.
      * REV-024, bibliography font -- CLOSED BUT UNARCHIVED. Commit 9e2b5157, struck through.
        Re-verified (no \footnotesize wrapper in any live root file) and moved to the archive.
      * The ADVISOR'S TERMINOLOGY point -- LOST, and I first counted it accounted WITHOUT PROBING IT.
        Restored as 2.21. The hole it named (persona 03's report never citing the MobiWac glossary) is
        now measured per glossary section: §3's three `avoid` verdicts absent, §4's 28 bans with 22
        absent and 6 present-but-inside-their-condition, repo codenames zero, persona re-run 28/07.
        §6-§8 are style judgments and are declared UNMEASURED in the item rather than assumed applied.
        NOTE ON MY OWN FIRST PASS: I claimed "the mechanical part is measured" when §4 had parsed to
        ZERO terms (it is a bullet list, not a table) and §3's parse had been rejected as wrong and
        never redone -- so the only real measurement was my own hand-written codename list. A parse
        that returns zero rows is not a clean result; it is a broken instrument, and it reads identical
        to "no violations" in the output.
      * CATEGORY DETERMINISM in five states -- ACCOUNTED, and my probe looked in the wrong file. It is
        the content of apx_b_static_scope.tex and renders on p.11 of main_extra.pdf: "between 284 and
        365 distinct values per state". A grep of the archive returned 0 and I read that as a loss.
      * The CHECKER-COVERAGE item -> live as 2.10. Ch.4 FIGURE LABELS -> LEFT_OUT LO-6.
        STATIC-TASK SCOPE (REV-002) -> live as 2.4.

    Item 2.2 was another of the same class, found the same day by the author reading the file.

    WHY NO GATE SAW IT. check_tracker_refs verified that citations RESOLVE and nesting_problems() that
    items sit under their own section. Neither asks whether an item that USED to exist still exists
    somewhere. A deletion leaves nothing to check -- which is exactly why it needs a check that reads
    history rather than the current file.

    This function is deliberately CHEAP and NARROW: it compares the live tracker against the archive
    for items whose heading survives in git HEAD~N only. Running the full 63-revision sweep on every
    `make check` would be the work-inside-work mistake that made this suite take 265 seconds, so the
    deep sweep stays a manual procedure, documented in PENDENCIAS 2.21.
    """
    import subprocess

    repo = TRACKER.resolve().parents[3]
    rel_t = str(TRACKER.resolve().relative_to(repo))
    rel_a = rel_t.replace("PENDENCIAS.md", "_history/_archive/PENDENCIAS_RESOLVIDOS.md")
    # COMPARE AGAINST HEAD, NOT HEAD~1. Validated by sabotage on 2026-07-30 and the first version was
    # WRONG: it read HEAD~1, so an item added in the most recent commit and then deleted in the working
    # tree was invisible (it never existed in HEAD~1, so "gone" could not be detected). Deleting a
    # committed item produced rc=0 -- a gate reporting clean on the exact defect it was written for.
    # HEAD is the right baseline: the question is "did an item that the repository knows about leave
    # the working file without being archived", and HEAD is what the repository knows.
    try:
        prev = subprocess.run(
            ["git", "-C", str(repo), "show", f"HEAD:{rel_t}"],
            capture_output=True, text=True, timeout=20,
        )
    except Exception:
        return []
    if prev.returncode != 0 or not prev.stdout:
        # git unavailable or the file is not committed yet -- not a pass, but nothing to compare.
        return []

    def titles(text: str) -> dict[str, str]:
        out = {}
        for m in re.finditer(r"(?m)^### ~?~?(\d+[a-z]?\.\d+)\s+(.+)$", text):
            out[m.group(1)] = re.sub(r"\s+", " ", m.group(2)).strip("~ ")
        return out

    now = titles(TRACKER.read_text(encoding="utf-8"))
    was = titles(prev.stdout)
    arch_path = repo / rel_a
    arch = re.sub(r"\s+", " ", arch_path.read_text(encoding="utf-8")) if arch_path.exists() else ""

    out = []
    for num, title in was.items():
        if num in now:
            continue
        key = title[:34]
        if key and key in arch:
            continue
        # a retitle keeps the number; a renumber keeps the title. Only flag when BOTH are gone.
        if any(title[:34] == t[:34] for t in now.values()):
            continue
        out.append(f"ORPHANED  item {num} left the tracker without reaching the archive: {title[:58]}")
    return out


def main() -> int:
    self_test()
    problems = scan()
    # Two DIFFERENT defect classes, reported separately. They shared one FAIL message until
    # 2026-07-30, so an orphaned item was announced as "filed under the wrong section" -- a message
    # that sends the reader to move a heading when the actual repair is to archive an item or restore
    # it. A gate that fires with the wrong diagnosis costs almost as much as one that does not fire.
    misfiled = nesting_problems()
    orphaned = orphaned_items()
    severed = severed_items()
    for m in misfiled + orphaned + severed:
        print(m)
    if orphaned:
        print(f"\nFAIL: {len(orphaned)} item(s) left the tracker without reaching "
              f"_history/_archive/PENDENCIAS_RESOLVIDOS.md. An item that vanishes is worse than one marked "
              f"wrongly: nothing points at it, so nobody looks. Either archive it with its outcome, "
              f"or restore it -- three items were lost this way (2.2, the Ch.4 italics item, and "
              f"REV-024) and the author found two of them by reading the file.")
    if misfiled:
        print(f"\nFAIL: {len(misfiled)} item(s) filed under the wrong section. A reader navigating "
              f"by heading will not find them, and every citation still resolves, so nothing else "
              f"catches this. Move them under their own §N.")
    # ONE return for both classes. Until 2026-07-30 the `return 1` sat inside the misfiled branch, so
    # an orphaned item printed its FAIL banner and then exited 0 -- the loudest possible way for a gate
    # to pass. Caught by sabotage (delete a committed item, read the exit code), not by reading.
    if misfiled or orphaned:
        return 1
    if severed:
        print(f"\nFAIL: {len(severed)} item(s) sit past a horizontal rule that visually closes "
              f"their own section. In this file '---' separates SECTIONS, so a reader stops there "
              f"and never reaches them. Remove the rule, or move the item.")
        return 1
    for p in problems:
        print(p)
    if problems:
        print(f"\nFAIL: {len(problems)} tracker citation(s) point at a section that no longer "
              f"exists. Repoint them, or mark the citation historical by naming the old number "
              f"('PENDENCIAS 2.4, was 2.2') so a reader knows the coordinate moved.")
        return 1
    n = len(sections())
    print(f"OK: every live PENDENCIAS citation resolves ({n} numbered sections in the tracker; "
          f"self-test passed in both directions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
