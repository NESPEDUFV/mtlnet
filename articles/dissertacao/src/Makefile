# Dissertation build.  `make help` lists everything.
#
#   defense    build/main.pdf            the reading copy, also copied to ./dissertacao.pdf
#   academico  build/main_academico.pdf  the AcademicoPG deposit body (was `final`)
#   ppgc       build/main_ppgc.pdf       the defense document plus the approval sheet
#   extra      build/main_extra.pdf      the SUPPLEMENTARY VOLUME -- a separate document,
#                                        not a fourth variant of the dissertation
#
# THE ENVIRONMENT IS SET UP HERE. You do NOT need to source anything first. This stack lives in a
# usermode TeX tree and needs PATH plus TEXMFHOME/TEXMFVAR/TEXMFCONFIG pointed at it; the three
# lines below read those from src_utils/texenv.sh at parse time and export them into every recipe.
# Without them a build runs three apparently-normal passes and dies with
#   Font ntx-Regular-tlf-ot1r at 657 not found
# which is a missing font MAP, not a missing font -- the .tfm and .pfb are both present. That cost
# an hour once and used to be a preflight that told you to go source a script; the Makefile knew
# the right values all along, so it sets them.
UTILS := ../src_utils
export PATH        := $(shell . $(UTILS)/texenv.sh >/dev/null 2>&1 && echo "$$PATH")
export TEXMFHOME   := $(shell . $(UTILS)/texenv.sh >/dev/null 2>&1 && echo "$$TEXMFHOME")
export TEXMFVAR    := $(shell . $(UTILS)/texenv.sh >/dev/null 2>&1 && echo "$$TEXMFVAR")
export TEXMFCONFIG := $(shell . $(UTILS)/texenv.sh >/dev/null 2>&1 && echo "$$TEXMFCONFIG")

# Every plain build is the same three passes with bibtex between the first and second, differing
# only in stem and entry file, so the recipe lives in ONE script rather than four copies. Read
# src_utils/latexbuild.sh for the three things in it that are load-bearing (isolated aux tree,
# bibtex exit handling, atomic publish) -- each was learned by breaking it.
BUILD := $(UTILS)/latexbuild.sh
FAST  := $(UTILS)/fastbuild.sh

# Timings are in src_utils/_history/_round7/20_build_speed.md with the command that produced each. They are
# deliberately not repeated here: a duration in a Makefile comment is a measurement nobody re-runs.

all: defense

# ---- the four documents ------------------------------------------------------------------
defense:   ; @$(BUILD) main main.tex && cp build/main.pdf dissertacao.pdf
academico: ; @$(BUILD) main_academico main_academico.tex
ppgc:      ; @$(BUILD) main_ppgc main_ppgc.tex
extra:     ; @echo 'O volume de material extra mudou para ../wrapup/material_extra/ em 2026-08-16.' \
	           && echo 'Ele e material de apoio a defesa, nao parte do texto depositado.' \
	           && $(MAKE) -C ../wrapup/material_extra extra

# `make final` was renamed on 2026-07-29 (LATEX_UPGRADE.md §4 A-1). Kept as an alias so a
# half-remembered command builds the right thing instead of failing.
final:
	@echo "note: 'final' is now 'academico' -> build/main_academico.pdf"
	@$(MAKE) --no-print-directory academico

# All three dissertation variants at once. -j3 is inside the recipe because a caller who forgets
# it gets the serial time and no warning; they share no file, which is why the aux trees are
# isolated. `extra` is absent on purpose -- it is a different document.
all3: ; @$(MAKE) --no-print-directory -j3 defense academico ppgc

# ---- format-accelerated builds (an ACCELERATOR, never a requirement) ----------------------
# The preamble is most of the cost of a pass; `fast` precompiles it into a pdflatex format dump.
# mkformat.py rebuilds the dump when preamble.tex's checksum moves and fastbuild.sh REFUSES a
# stale key, so a stale-format build is unreachable. The plain targets never touch the format and
# work with none present -- which is what Overleaf needs.
fast: fast-defense
fast-defense:   ; @$(UTILS)/mkformat.py --build && $(FAST) defense && cp build/main.pdf dissertacao.pdf
fast-academico: ; @$(UTILS)/mkformat.py --build && $(FAST) academico
fast-ppgc:      ; @$(UTILS)/mkformat.py --build && $(FAST) ppgc

# The dump is built ONCE first, serialized on purpose: three concurrent -ini runs race on the
# same mainpre.fmt.
fast3:
	@$(UTILS)/mkformat.py --build
	@$(MAKE) --no-print-directory -j3 fast3-defense fast3-academico fast3-ppgc
	@cp build/main.pdf dissertacao.pdf
fast3-defense:   ; @$(FAST) defense
fast3-academico: ; @$(FAST) academico
fast3-ppgc:      ; @$(FAST) ppgc

format:        ; @$(UTILS)/mkformat.py --build
format-status: ; @$(UTILS)/mkformat.py --status

# The whole proof from nothing: build all three plainly, store as reference, rebuild with the
# format, compare every text layer. Minutes on purpose -- it reuses nothing it could have got
# wrong. Run after a preamble change you want to be certain about.
verify-equiv:
	@$(MAKE) --no-print-directory all3
	@python3 $(UTILS)/verify_format.py --reference --note "make all3 (plain, no format)"
	@$(MAKE) --no-print-directory fast3
	@python3 $(UTILS)/verify_format.py --compare --all

# ---- gates ---------------------------------------------------------------------------------
# `check` is THE gate: the whole suite, nonzero on any finding. The per-checker targets exist so
# nobody needs to know the src_utils/ layout to re-run one gate while fixing what it found;
# `check-scripts` runs every build-independent checker and reports all failures, not just the first.
check:         ; @$(UTILS)/check.sh
# `selftest` proves the CHECKERS, not the document: each one must fire on a fixture containing its
# defect and stay silent on the same fixture repaired. Deliberately NOT a prerequisite of `check` --
# a lint gate that runs its own test suite every invocation is the work-inside-work mistake that
# made `check` take 265 s. Run it when you change a checker.
selftest:      ; @python3 $(UTILS)/selftest_all.py
check-scripts: ; @$(UTILS)/check_scripts.sh
sync-pages:    ; @python3 $(UTILS)/sync_page_counts.py --write

CHECKERS = trapped_prose torn_sentences doubled_macro tex_root negative_parallelism \
           meta_claims verify_list wordcount_claims sweep_guard tracker_refs \
           comment_hygiene extra_xrefs
$(addprefix check-,$(CHECKERS)): check-%: ; @python3 $(UTILS)/check_$*.py
check-pages:  ; @python3 $(UTILS)/sync_page_counts.py
check-format: ; @python3 $(UTILS)/mkformat.py --selftest
check-equiv:  ; @python3 $(UTILS)/verify_format.py --compare

help:
	@echo "BUILD  make defense | academico | ppgc | extra   one document, three passes"
	@echo "       make all3       all three dissertation variants, concurrently"
	@echo "       make fast | fast3                          with the precompiled preamble"
	@echo "       make format | format-status                build / inspect the format dump"
	@echo "       (timings: src_utils/_history/_round7/20_build_speed.md)"
	@echo "GATES  make check          THE gate: the full suite, exit 0 or bust"
	@echo "       make selftest       prove the checkers themselves, both directions"
	@echo "       make check-scripts  every build-independent gate, one line each"
	@echo "       make check-<name>   one gate: $(CHECKERS)"
	@echo "       make check-pages check-format check-equiv verify-equiv"
	@echo "       make sync-pages     rewrite recorded page counts from the build"
	@echo "OTHER  make clean          remove build/ output"

clean: ; rm -rf build/*

.PHONY: all defense academico final ppgc extra all3 fast fast-defense fast-academico fast-ppgc selftest \
        fast3 fast3-defense fast3-academico fast3-ppgc format format-status verify-equiv \
        check check-scripts check-pages check-format check-equiv sync-pages help clean \
        $(addprefix check-,$(CHECKERS))
