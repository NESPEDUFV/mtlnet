# `src_utils/_history/_archive/` — superseded working files

Nothing here is live. These files were the working record of rounds 1 to 5 and are kept because they
are the provenance of decisions the document now carries. Archived 2026-07-27 at the author's request,
so `src_utils/` holds only what is still in use.

**If you are looking for the current state**, it is in `src_utils/PENDENCIAS.md` (what still needs the
author) and `src_utils/codex_reviewer.md` (the external review, annotated with per-finding verdicts).

## `reviews_v1/` — superseded review documents

| File | What it was | Why it is here |
|---|---|---|
| `dissertation_review_codex_v1_89pp.md` | The first external review, against an 89/84-page build (was `test.md` at the repo root) | Superseded by `codex_reviewer.md`; every finding was dispositioned |
| `dissertation_review_v1.md` | The first internal review pass | Superseded by v2, then by the round-4 and round-5 work |
| `dissertation_review_v2.md` | The re-audited review, 39 findings with per-finding disposition | Its open items moved to `PENDENCIAS.md`; kept as the audit trail |
| `DECISOES_PENDENTES_ptBR.md` | The first author-decision register | Every item carried into `PENDENCIAS.md` or resolved; verified item by item 2026-07-27 |
| `noth_star_consideration.md` | Three author notes on arc, fundamentals and scope | Absorbed into `NORTH_STAR.md` §4b, which records which points landed and which is still open |

## `reports_2026-07/` — one-off reports

| File | What it was |
|---|---|
| `FRAME_INTEGRATION_REPORT.md` | How the three papers were stitched into one document |
| `APPENDIX_D_EXPLAINED.md` | A working explanation of the benchmark appendix, written before the appendix was rewritten |
| `evidence/cbic_recompute_result.md` | NOT archived. Still cited as provenance from `3_cbic.tex`, `apx_b_errata.tex` and `NORTH_STAR.md` |

## `handoffs/` — machine handoff payloads

`HANDOFF_v1.md`, `cbic_recompute_handoff.json`, `handoff_tooling.json`,
`item4_licence_evidence.json`. Structured evidence produced by sub-agents. The claims they support are
in the document; these are the raw payloads behind them.

## What deliberately stayed in `src_utils/`

| File | Why it is still live |
|---|---|
| `PENDENCIAS.md` | The register of what needs the author |
| `codex_reviewer.md`, `CODEX_VS_PERSONAS.md` | The external review and the seam against the persona suite. **`CODEX_AUDIT.md` is no longer live** — see the round-7 section below |
| `evidence/DATASET_LICENSING_FINDINGS.md` | Every licence claim in Appendix E traces here |
| `evidence/etl_tooling_contribution_evidence.md` | The evidence behind Appendix A's software-contribution claim |
| `evidence/cbic_recompute_result.md` | Cited as provenance from three source files |
| `evidence/BIB_MERGE_REPORT.md` | Cited from `apx_b_errata.tex` and `references.bib` |
| `build.sh`, `check.sh`, `check_trapped_prose.py`, `test_trapped_prose.py` | The build and gate toolchain |
| `README_SRC.md` | The build recipe and TeX-tree notes |
| `_history/_review_v1/`, `_history/_review_v2/`, `_specialists_v1/`, `_history/_specialists_v2/`, `_gates/` | Reviewer reports, referenced by both registers |
| `adaptation_ledgers/` | Per-chapter records of what changed against the published text |

## Archived 2026-07-29 (round 7)

| File | What it was | Why it is here, and what was lifted out first |
|---|---|---|
| `CODEX_AUDIT.md` | The per-finding audit of `codex_reviewer.md`: 18 COD- items, 8 NUM- rows, sixteen `DECISAO` boxes in the author's own words, and a round-6 outcome table | Archived at the author's instruction (*"if we finish with it archive it or delete, and if some point still pending my approval or I need to be aware add in the pendencias"*). **Before the move, every COD-/NUM- id and every `DECISAO` box was swept, and NINE points still needing him were lifted into `PENDENCIAS.md` §5**, each with the command that measures it. Five of the nine sit under outcome-table rows that say "APPLIED" while the sentence they name is still in the document; the §5 items say so and show the measurement |
| `PENDENCIAS_RESOLVIDOS.md` (extended) | Not newly archived — the round-6 §1 of `PENDENCIAS.md` was appended to it | The tracker's §1 ("Fechado nesta rodada", the whole of round 6) moved here verbatim **with its 19 commit hashes**, so the audit trail survives the move and the live tracker holds only what needs a decision |

**If you are looking for a COD- or NUM- verdict**, it is in `_history/_archive/CODEX_AUDIT.md`. Read it the way
its own §8 asks to be read: it is a competent audit of a build that no longer exists, about a third of
its `file:line` coordinates are stale, and the three paper chapters have since been split into
per-section files. Re-anchor by phrase before acting on anything in it.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-29 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
