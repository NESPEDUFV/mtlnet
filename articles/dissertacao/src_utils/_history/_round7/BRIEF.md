# Round 7 brief — read before touching anything

**Repo root:** `/Users/vitor/Desktop/mestrado/ingred`  ·  **DISS:** `articles/dissertacao/`
**LaTeX source:** `DISS/src/`  ·  **Working dir for all commands below:** `articles/dissertacao/`

## Build recipe (mandatory)

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao
source src_utils/texenv.sh          # REQUIRED: PATH, TEXMFHOME, TEXMFVAR, TEXMFCONFIG
(cd src && make defense && make final && make ppgc)
bash src_utils/build.sh src both    # the report: pages, tex_errors, overfull, undefined
(cd src && make check)              # 18 gates, ~1.6s, must exit 0
```

**The TEXMFVAR trap:** a wrong `TEXMFVAR` gives `Font ntx-Regular-tlf-ot1r ... not found`, which
looks like a missing font and is a missing font *map*. `kpsewhich -var-value TEXMFVAR` reports an
unreadable path on this machine, so it cannot be probed — `texenv.sh` sets it.

## Inherited state (measured 2026-07-29, commit adbb6952)

    defense build/main.pdf       108 pp
    final   build/main_final.pdf 105 pp
    ppgc    build/main_ppgc.pdf  109 pp
    tex_errors 0, overfull hbox/vbox 0, undefined cites/refs 0, bibtex problems 0,
    oversized floats 0, Hfootnote 0 in all three logs.  make check RC=0 in 1.6s.

**Any change that moves a page count must run `python3 src_utils/sync_page_counts.py --write`.**

## The law (obey, do not skim)

1. `AGENT_GUARDRAILS.md` — process law. **§4b is new and is aimed at you**: the meta-claim
   protocol. Round 6 spent 2.4 h repairing wrong statements about *the work* (12 of 14 genuine
   rework commits). Read V1–V7 before you write any sentence of the form "the sweep found N",
   "all X pass", "every Y was checked".
2. `WRITING_LAW.md` + `GLOSSARY.md` — word-level law. Fail-closed: a term not in the registry may
   not be used. Propose it, do not self-authorize.
3. `science/AGENT_HANDOFF.md` §2 — every failure mode that has actually bitten this repository.
   §2.8 is the largest class.
4. `NORTH_STAR.md` §4 — the **errata regime**, which governs whether a sentence may be edited:
   - **Ch.3 (CBIC) and Ch.4 (CoUrb) are PUBLISHED.** Corrections go in the appendix trail, and
     the chapter text may only be corrected with an errata entry.
   - **Ch.5 (MobiWac) is UNDER REVIEW.** Every edit lands in BOTH the dissertation and
     `articles/[mobiwac]/src/` so the two stay identical, plus an `ERRATA.md` entry.
   - **Frame chapters (1, 2, 6) and appendices are the author's own prose** — edit freely, but
     mark anything substantive `[NEEDS SIGN-OFF: ...]`.

## Non-negotiables, learned the hard way

- **Anchor by PHRASE, never by line number.** A third of round 5's recorded coordinates were stale
  within one commit.
- **Greps over `.tex` strip comments FIRST:** `grep -vn '^[[:space:]]*%' "$f" | grep '<pat>'`.
  Filter the *file*, not the `grep -n` output (`:[0-9]*: *%` misses an indented comment). This
  source quotes the strings you search for in its own provenance comments — three defects in one
  day came from this.
- **Verify in the RENDER, not the source.** A change that looks right in `.tex` and wrong on the
  page is a defect. Use `pypdfium2` to read the built PDF.
- **Validate any new checker in BOTH directions** before trusting it: run it against a tree where
  the defect is present and confirm it FAILS, then the fixed tree and confirm it passes. Wire a
  self-test that runs before it reports.
- **A skip is never silent.** If your code has a `continue`/`except: pass`/filter, your claim must
  name what was excluded and how many.
- **Never `rm` in the repo.** Use `git mv` or ask.

## Deliver

Write your report to `src_utils/_history/_round7/<NN>_<name>.md`: what you changed and where (by phrase),
what you measured before and after, every `[VERIFY]` flag, and anything you could NOT confirm.
Commit your own work in this repository's style — the defect first, then the fix, then the
measurement. **Do not commit a broken build.** Self-reported success is not trusted; the author
audits independently.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-29 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
