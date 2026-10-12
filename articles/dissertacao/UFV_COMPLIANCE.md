# UFV_COMPLIANCE.md — norms, formatting, prerequisites, and the submission pipeline

> Everything the dissertation must comply with, distilled from the primary sources and
> **re-verified against the live pages on 2026-07-18**. Supersedes
> `articles/[TESE]_MTL_POI/NORMAS_UFV.md` (June 2026 extraction) — one material change since
> then: a **new PPGCC regimento interno approved 2026-07-09** (§3 below). The local copy of the
> submission manual is [the UFV PDF](https://www.ppg.ufv.br/wp-content/uploads/2026/04/Manual-de-entrega-de-dissertacoes-e-teses-04_2026.pdf) (the repository copy was removed 2026-08-28).

---

## 1 · The two-build reality (understand this first)

There are TWO deliverable shapes, and they differ:

1. **Defense build** (to secretariat + banca, ≥20 days before the defense): a conventional full
   PDF — cover page, approval sheet, lists, sumário, body — like the Viegas example PDF. This is
   what the banca reads.
2. **Final AcademicoPG build** (after approval, within 3 months): the system generates/holds the
   cover, ficha catalográfica, dedicatória, agradecimentos, epígrafe, resumo, abstract and
   keywords (filled in web forms, "colar sem formatação"); the **uploaded PDF contains ONLY**, in
   order: lista de ilustrações / tabelas / siglas / símbolos (all optional) → apresentação
   (optional) → **sumário (mandatory)** → **body (mandatory)**. Page numbering starts on the
   first body page; the SYSTEM's emitted PDF (RASCUNHO watermark) is the authoritative numbering
   reference.

The LaTeX setup must produce both from one source ([`archive/TEMPLATE.md`](archive/TEMPLATE.md) §2,
checklist item 4, "Two build modes"; the link and the section were stale until 2026-10-02 — the file
moved to `archive/` in the 2026-10-01 reorganisation).

## 2 · Mandatory formatting (Manual 04_2026 §7–§8)

| Item | Rule |
|---|---|
| Font | **Arial or Times New Roman, size 12** (note: Viegas used Palatino and passed — but that predates strict enforcement; comply, don't gamble) |
| Paper | A4 (21 × 29.7 cm) |
| Margins | top + left **3 cm**; bottom + right **2 cm** |
| Line spacing | **1.5** |
| Page numbers | top-right corner, arabic; **start on the first body page (introduction)** |
| Pre-textual pages | **counted but not numbered**; cover + ficha catalográfica neither counted nor numbered |
| Numbering example | 10 pre-textual pages → the first body page is numbered 11 |
| Resumo/Abstract (system fields) | text block only, no paragraphs, no header (system generates the header); keywords one per line, lowercase except proper nouns, no punctuation |
| Agradecimentos (system field) | 🛑 **The funding sentence is PRE-FILLED and FREELY EDITABLE — it is NOT protected by the system.** The field's own label reads *"Até 4000 caracteres. **Deve conter** o texto «This work has been sponsored by…»"*: **"deve conter" is an obligation on the student**, not an auto-insert. Up to 4000 chars; reorderable among other thanks. **If you rewrite this field, carry the sentence across yourself — nothing restores it.** |

> 🛑 **CORRECTED 2026-09-08, and the old wording was the dangerous kind.** This row used to read
> *"auto-inserted and cannot be altered"*. The reordering half was right; **the immutability half was
> false**, and it asserted a guarantee the portal does not give.
>
> **How it was established, and it is not inference:** the `academico` session **edited the field**.
> On 2026-09-04 it held only the funding sentence (296 chars, read from the widget's own value); the
> session replaced the contents with the seven acknowledgement paragraphs from `content.tex` and
> **deliberately put the sentence back at the end**, because a warning told it not to duplicate. The
> system accepted and stored 3,114 characters. Had it not known, the sentence would have been gone.
>
> ✅ **The funders ARE acknowledged**, verified in the emitted RASCUNHO (**sheet 6**), full text:
> *"This work has been sponsored by the following Brazilian research agencies: Coordination for the
> Improvement of Higher Education Personnel (CAPES; Financing code 001), Minas Gerais State
> Foundation for Research Aid (FAPEMIG) and National Council of Scientific and Technological
> Development (CNPq)."* Their absence from `src/` is therefore **correct, not an omission** — the
> field is filled in the portal, like the Resumo.
>
> ⚠ **The standing risk, which replaces the false guarantee:** the sentence survives by the
> discipline of whoever edits the field. **Re-check it in the RASCUNHO every time the Agradecimentos
> are touched.**
>
> *Caveat recorded rather than hidden: the AcademicoPG session has since expired, so this could not
> be re-confirmed live. What is reported is direct observation logged at the time — the initial value
> read, the label read, and an edit that saved successfully — not a reading of this file.*
>
> **Same shape as the page-numbering defect**, and worth naming: there, the recipe in our source was
> blind to what the portal prepends; here, our note credited the portal with a protection that is in
> fact the student's responsibility. **Our documentation asserting a guarantee is not the system
> giving one.**

Older Normas-gerais print-era rules (≥40 mm binding margin etc.) are superseded by the manual
for the final build; SI units and legibility rules (§3.x) still apply.

## 3 · Coletânea + defense prerequisites (Normas gerais rev. 11/10/2019 + regimento 2026-07-09)

**Coletânea format (Normas §2.3, §2.6 — confirmed verbatim on the live PDF):**
- Body as "artigos científicos … **publicados, aceitos, ou submetidos** para publicação" →
  MobiWac as a submitted paper is eligible.
- Structure: **(i) Introdução Geral, (ii) Artigo(s), (iii) Conclusão Geral**; Introdução/Conclusão
  may carry their own bibliographies; articles have **free formatting** given internal
  consistency (§2.6); different formattings (§2.6.2) and **different languages (§2.6.3)**
  admitted; previously published articles may be reproduced from the originals (§2.6.4).
- Language of the work: PT, EN, or ES **at the Comissão Orientadora's discretion** (§1.3) —
  the English frame needs the advisor's OK, nothing more.
- Optional closing sections ("Perspectivas Futuras" etc.) allowed (§2.7); post-textual
  apêndices/anexos allowed (§2.8).

**Defense prerequisites (PPGCC regimento interno — ⚠ NEW VERSION approved 2026-07-09):**
- **Art. 21 §1 (new wording):** master's student is apt to defend only after proof of
  **publication or acceptance of ≥1 article from the research in a scientific event**, OR
  **proof of submission to a CS journal**, with minimum quality per an internal resolution
  (CAPES-Computação-aligned). The word "Qualis" no longer appears — BUT the still-linked
  June/2024 defense checklist demands "Qualis A4 or superior" proof. **STATUS 2026-07-18: the
  substance is covered — CBIC is published with DOI `10.21528/CBIC2025-1191324` (verified;
  CoUrb `10.5753/courb.2026.22960` is a second published article as backup). Remaining action:
  file the comprovante with the secretariat (ppgcc@ufv.br) and confirm the operative checklist
  bar.** *(Moot since 2026-08-28: the defense took place and was approved, so the apt-to-defend
  question is closed.)*
- **Art. 22:** dissertation text to the secretariat **≥20 days before the defense date**.
- **Art. 23:** public defense, presentation up to 50 min, then arguição.
- **Anti-plagiarism certificate** (UFV institutional tools) is mandatory — "a defesa não será
  aprovada" without it (defense checklist item; also relevant to the AI-use disclosure,
  [`AGENT_GUARDRAILS.md`](AGENT_GUARDRAILS.md) §6).
- Wet-signature items survive the online flow: termo de assentimento (checklist item 12) and
  the BBT authorization term — plan physical signatures around the defense.

## 4 · Post-defense pipeline (Manual 04_2026, step by step)

1. Corrections per the banca → final text.
2. AcademicoPG → "Entrega de tese/dissertação" → fill pre-textual forms (**colar sem
   formatação**; system does not auto-create paragraphs).
3. Upload the body-only PDF (§1 build 2).
4. "Emitir PDF para solicitação da ficha catalográfica" → RASCUNHO-watermarked draft → **check
   numbering against the system PDF** (it is authoritative; adjust the LaTeX page-counter offset).
5. Send the RASCUNHO to BBT (https://www.bbt.ufv.br/ficha-catalografica-on-line/) → ficha ready
   in ~7 days (email notification) → attach it in the system.
6. "Visualizar documento completo" → final check → "Enviar" (password = digital signature) →
   advisor approves → PPG homologation → diploma request automatic.
7. **Deadline: 3 months after the defense** — for this dissertation **2026-11-28**, which the portal
   itself states on the banca page ("você tem até 28/11/2026 para submeter a versão final"). Monthly
   fine afterwards (PagTesouro); the 7-day ficha SLA is inside the window.

   ⚠ **THE CLOCK SUSPENDS AT "ENVIAR" — and this half was missing here until 2026-09-29.** Manual de
   entrega 04/2026, verbatim: *"Quando o trabalho é encaminhado para apreciação do orientador, **o
   prazo é suspenso**. Se o orientador reprovar, o prazo é reiniciado e pode ocorrer incidência de
   multa."* And under *Reprovação pelo orientador*: *"O prazo será reiniciado **a partir da data da
   defesa**, e poderá haver incidência de nova multa"* — with a new payment, a new PPG validation of
   it, and ten calendar days to resubmit.

   Read together, three rules for the calendar:
   1. **Time with the advisor does not consume the window if he approves.** The clock stops at
      "Enviar". His turnaround is therefore NOT the critical number.
   2. **If he rejects, the suspension collapses and the count runs from the defense** — the time the
      text spent with him becomes elapsed time retroactively. A rejection close to the deadline goes
      straight to a fine.
   3. **Homologation comes after approval and has no stated deadline**; if the PPG returns it, *"o
      prazo para nova submissão será reavaliado, podendo haver incidência de multa"*.

   **So the risk is not a slow advisor, it is a formal rejection.** One way to neutralise it would be
   an informal advisor read of the RASCUNHO before "Enviar". **The author decided against it
   (2026-09-29):** the advisor already read the dissertation and sent his remarks together with the
   banca's, and those remarks have been applied. What remains is touch-ups, so the path is: finish the
   corrections here, then go to the Library. The rejection rule above still stands as a fact.

   *Verified 2026-09-29 against the manual itself, not relayed: the `academico` session read §§12-17
   and quoted them; both clauses were then re-read at the source (`~/Downloads/Manual-de-entrega-de-
   dissertacoes-e-teses-04_2026.pdf`, the copy downloaded 2026-09-06). This row previously said only
   "if the advisor rejects, the clock restarts from the defense date" — true, and the unfavourable
   half. The omission made the advisor's turnaround look like the binding constraint, and a calendar
   was briefly built on that wrong model.*

## 5 · Timeline flags for an August 2026 defense (today: 2026-07-18)

- Defense in the window **Aug 18–29** ⇒ **text + banca locked between Jul 29 and Aug 9**
  (Art. 22's 20 days + banca formed in AcademicoPG + members informed).
- Before the defense is approved: anti-plagiarism certificate + Art. 21 proof on file. *(Moot: defended
  and approved 2026-08-28.)*
- After an August defense: final AcademicoPG deposit due by **~late November 2026**.
- Full schedule and fallback: [`archive/PLAN.md`](archive/PLAN.md).

## 6 · AI-use policy state (2026-07-18; details in AGENT_GUARDRAILS §6)

- No binding UFV/PPGCC norm on AI-assisted writing found. UFV/DPE published recommended
  disclosure guidelines (03/2026). **CNPq Portaria nº 2.664/2026** mandates AI-use declaration
  for CNPq-linked researchers (tool + purpose; AI-generated content as human-authored is
  vedado). CAPES converging via GT/technical notes (primary texts partially unverified).
- Practical ruling: include a disclosure note (AGENT_GUARDRAILS §6 D1) and raise it with the
  advisor early.

## 7 · Verified sources (all HTTP-checked 2026-07-18)

- Manual de entrega 04_2026 (PPG):
  https://www.ppg.ufv.br/wp-content/uploads/2026/04/Manual-de-entrega-de-dissertacoes-e-teses-04_2026.pdf
  (the repository copy was removed 2026-08-28; this URL is the source)
- Normas gerais de Teses e Dissertações (rev. 11/10/2019):
  https://www.ppg.ufv.br/wp-content/uploads/2012/08/Normas-gerais-de-Teses-e-Dissertac%CC%A7o%CC%83es-12.pdf
- PPGCC Regimento interno (aprovado 09/07/2026): https://ppgcc.ufv.br/regimento-interno/
- PPGCC Procedimentos finais (Word models PT/EN, checklists): https://ppgcc.ufv.br/procedimentos-finais/
  - Word model EN: https://ppgcc.ufv.br/wp-content/uploads/2024/07/UFV-2019-Modelo-dissertacao-tese-em-ingles-7-1-2.docx
  - Pre-textual checklist: https://ppgcc.ufv.br/wp-content/uploads/2024/07/CHECK-LIST-%E2%80%93-Formatacao-das-Paginas-Pre-Textuais-Dissertacao-e-Tese.pdf
  - Defense checklist (Jun/2024 — predates the new regimento, Qualis wording likely stale):
    https://ppgcc.ufv.br/wp-content/uploads/2024/07/CHECK-LIST-PARA-DEFESA-DE-DISSERTACAO.pdf
- PPG signature pages + Resumo/Abstract models:
  http://www.ppg.ufv.br/wp-content/uploads/2012/08/Modelo-pgs-de-assinaturas.pdf ·
  http://www.ppg.ufv.br/wp-content/uploads/2012/08/Modelo-Resumo-e-Abstract1.pdf
- BBT: ficha catalográfica https://www.bbt.ufv.br/ficha-catalografica-on-line/ · Normalização
  2025 https://www.bbt.ufv.br/wp-content/uploads/2025/02/Normalizacao-de-trabalhos-academicos-2025-UFV.pdf
- AI policy: UFV/DPE guide
  https://tecido.dpe.ufv.br/wp-content/uploads/2026/03/IA-em-Pesquisa-Educacional_-Recomendacoes-1.pdf ·
  CNPq Portaria 2.664/2026 announcement
  https://www.gov.br/cnpq/pt-br/assuntos/noticias/cnpq-em-acao/cnpq-publica-portaria-que-institui-politica-de-integridade-na-atividade-cientifica

> **2026-10-02: item (a), the Art. 21 / Qualis question, is moot.** It asked what the secretariat
> would accept before the defense; the defense took place on 2026-08-28 and was approved. It stays
> below as the record of what was open. Item (c) is not about the defense and is left as it was.

**Open items (carried into `archive/PLAN.md`):** (a) operative Art. 21 quality bar + which regimento
governs pre-2026 enrollees — ask the secretariat (substance already covered, §3); **Qualis
strata now known** (deep-research, 2026-07-20, 3-vote adversarial verify, primary source =
CAPES "Relatório Qualis Eventos 2017-2020, Computação"): **CBIC = B4, CoUrb = B4, MobiWac = B2**
— all three classified directly by CAPES's own Computação area coordination (not by an
Engineering/Automação committee, despite CBIC being organized by ABRICOM/SBIC/SBA). This is the
most recent complete nominal listing found; whether it still governs 2025/2026 (vs. a newer
"Qualis Eventos 2025" Sucupira cycle, unconfirmed per-venue) and whether B4/B2 actually clear
the Art. 21 "resolução interna" bar (not itself located) is **still the open question for the
secretariat** — full findings + sources in
[`reviewers/research/qualis_classification_2026-07-20.md`](reviewers/research/qualis_classification_2026-07-20.md);
(b) ~~CBIC proceedings entry/DOI~~ RESOLVED 2026-07-18 (`10.21528/CBIC2025-1191324` verified);
(c) CAPES NT 3/2025 primary text.
