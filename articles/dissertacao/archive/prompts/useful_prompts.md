We are working on my dissertation in articles/dissertacao/. Read, in this order: CLAUDE.md,
NORTH_STAR.md, WRITING_LAW.md, GLOSSARY.md, AGENT_GUARDRAILS.md (obey §1-§4b exactly — every
numbered rule there was paid for by a real failure). Then learn the build: src/Makefile and the
tooling in src_utils/ (check.sh, selftest_all.py, check_audit_claims.py).

Your target is src_utils/CONSIDERATIONS.md — 1,229 lines of review feedback from Germano and from
Fabrício, as continuous prose with no item IDs. Germano's section is MY TRANSCRIPTION of verbal
comments, so treat that wording as my paraphrase, not his. A prior agent (STEP 0, report at
<path>) audited the fundamentals-related part; the text has changed substantially since.

1. ASSIGN STABLE IDS — GER-01, FAB-01, … Everything downstream references them. Never reuse an ID:
   recycled numbers made this repo's tracker history unauditable, and the recovery had to sweep 63
   revisions by title to find what had been lost.

2. STALE-QUOTE PASS. Each point anchors on a quoted passage. Locate every quote in the live source
   and classify it exact / changed / gone. Report the counts before judging anything. Roughly a
   third of cited coordinates were stale the last time this was measured.

3. AUDIT EACH SURVIVING POINT and say whether you agree. Sort into: you apply / I decide / blocked.
   Two admissibility tests decide the bucket.

   3.1 For each point, check whether the passage it quotes is load-bearing for a gate probe in
       check_audit_claims.py, a GLOSSARY registry entry, or an Appendix B errata row. One known
       case: Germano calls the HGI tuning-sweep sentence "jogado no texto", and that sentence is
       probe NUM-4, which requires it to keep its spreads and its averaging convention —
       compatible with relocating it, not with deleting it. Find the others rather than trusting
       that this is the only one.

   3.2 Any point requesting a citation (Germano asks for "Spectral Networks and Locally Connected
       Networks on Graphs" and "The graph neural network model") is admissible only under §1-§3:
       resolvable identifier, landing page opened this session, and the specific claim located in
       the source. If verification fails, the item is blocked or flagged — never "added anyway".

   DISAGREEMENT WITH A REVIEWER IS MINE TO SETTLE, NOT YOURS. If you think a committee member is
   wrong on substance, that is an "I decide" item with your argument attached, however confident
   you are. Staleness is different: "this quote no longer exists" is a measurement, and yours.

4. RECORD THE SPLIT. PENDENCIAS.md gets a new ## §6 carrying ONLY the items needing my decision,
   replacing the §2.8 placeholder — options and costs per item, as §2 already does. Everything
   else stays in CONSIDERATIONS.md, rewritten from prose into one standard per-item block:
   ID · reviewer (and verbal vs written) · the quote · its live-source status · your take with
   reasoning · disposition · where it renders in the PDF if applied · its probe name in
   check_audit_claims.py · and THE BUILD COMMIT THE MEASUREMENT WAS TAKEN AGAINST. That last field
   is not optional: four numbers in the closed-item register cannot be re-checked today, only
   re-taken, because none of them recorded its tree state.

   Every item you mark APPLIED gets its probe added to check_audit_claims.py IN THE SAME COMMIT. A
   register of applied items with no gate reading it is how eight false APPLIED rows survived
   thirteen hours of work here. If that gate ends up covering two sources, its docstring must say
   so — a docstring claiming one scope over code covering two is itself a defect this repo has hit.

5. PLAN THE "YOU APPLY" WORK — what parallelizes, what serializes. Sub-agents get a wall-clock
   checkpoint and must report unfinished work as unfinished; every wave in the last round overran
   (45 min → 60, 90 min → 219). Their self-reports are not evidence: verify each claimed edit
   yourself in the RENDERED PDF, not in the source.

6. THEN run reviewers/ in its documented gate order against the final build, recording that
   build's commit and page counts in each report. Stale persona reports get cited as current — one
   was two days and thirty commits old.

DONE MEANS: all four targets build clean (defense, academico, ppgc, extra), make check and make
selftest at rc=0 READ DIRECTLY AND NOT THROUGH A PIPE, PENDENCIAS §6 current, CONSIDERATIONS.md
fully in the new schema, and a source ledger for every reference touched. Commit constantly.

---- BREAK ----

We are working on my dissertation in articles/dissertacao/. Read, in this order: CLAUDE.md, NORTH_STAR.md, WRITING_LAW.md, GLOSSARY.md, AGENT_GUARDRAILS.md (obey §1-§4b exactly). Learn the build system: src/Makefile and src_utils/ (check.sh, selftest_all.py, check_audit_claims.py).

Your target is the items located in PENDENCIAS.md under the section "## §4 · Pensamentos e considerações do Autor". The text in the dissertation has evolved significantly since these thoughts/considerations were written. Your job is to audit these items thoroughly, evaluate their current validity, spawn sub-agents for complex tasks (codebase scraping, web searches, GPU executions on nespegpu if needed), identify overlaps, and build a concrete execution plan without altering the actual dissertation text yet.

1. ASSIGN STABLE SUB-IDS
   - Prefix every item under §4 with AUT-01, AUT-02, ... (or preserve existing stable IDs if already assigned). Never reuse or recycle IDs.

2. STALE-QUOTE & RELEVANCE PASS
   - Locate every anchor text, quote, or reference from these items in the live source files.
   - Classify each anchor as: [EXACT] / [CHANGED] / [GONE].
   - Report the total counts (e.g., 5 Exact, 3 Changed, 2 Gone) before performing deeper evaluation.

3. AUDIT, EVALUATE & SORT
   - For every item under §4, evaluate its current validity against the updated codebase and dissertation draft.
   - For complex items: Spawn background/sub-agents to perform required actions (e.g., web search for literature, codebase scraping, running verification scripts or GPU runs on nespegpu).
   - Identify dependencies and overlaps: Explicitly flag if resolving AUT-X inherently alters or resolves AUT-Y.
   - Sort each audited item into one of three buckets:
     a) YOU APPLY (Clear-cut, small/medium edits, no overlap conflicts, fully valid).
     b) I DECIDE (Items requiring my explicit decision, subjective choices, structural shifts, or where you disagree with my initial premise).
     c) BLOCKED / INVALID (The cited passage is GONE, no longer relevant due to text changes, or failed external claim verification under §1-§3).

4. CHECK GATE INTEGRITY & PROBES
   - Check if any item impacts load-bearing probes in check_audit_claims.py, GLOSSARY entries, or Appendix errata. Do not propose deleting or refactoring text tied to active probes without flagging it.

5. UPDATE PENDENCIAS.md (DO NOT TOUCH DISSERTATION TEXT YET)
   - Rewrite the items under "## §4 · Pensamentos e considerações do Autor" to adopt a standardized schema per item:
     - ID · Source Status ([EXACT]/[CHANGED]/[GONE]) · Your Take & Evaluation · Proposed Resolution Plan · Overlaps/Dependencies · Target Disposition ([YOU APPLY] / [I DECIDE] / [BLOCKED]) · Build Commit Measured Against.
   - Create/Update a distinct sub-section "## §4.1 · Decisões Pendentes do Autor" carrying ONLY the [I DECIDE] items, explicitly detailing options, trade-offs, and estimated effort/costs for my final call.

6. BUILD THE EXECUTION PLAN
   - For all items marked [YOU APPLY], construct an ordered execution plan:
     - Group items into Wave 1 (Independent/Small/No-overlap items that can run in parallel) and Wave 2 (Larger or sequential items).
     - Specify expected PDF render locations for each proposed edit.

OUTPUT REQUIRED WHEN DONE:
A summary report of the Audit Pass (counts, bucket distribution, key overlaps, and items placed in "§4.1 Decisões Pendentes do Autor" awaiting my input). No edits to dissertation .tex files should be made during this phase.

---- BREAK ----

We are working on my dissertation in articles/dissertacao/. Read, in this order: CLAUDE.md, NORTH_STAR.md, WRITING_LAW.md, GLOSSARY.md, AGENT_GUARDRAILS.md (obey §1-§4b exactly). Learn the build system: src/Makefile and src_utils/ (check.sh, selftest_all.py, check_audit_claims.py).

Your target is the items located in PENDENCIAS.md under the section "## §4 · Pensamentos e considerações do Autor". The text in the dissertation has evolved significantly since these thoughts/considerations were written. Your job is to audit these items thoroughly, evaluate their current validity, spawn sub-agents for complex tasks (codebase scraping, web searches, GPU executions on nespegpu if needed), identify overlaps, and build a concrete execution plan without altering the actual dissertation text yet.

1. ASSIGN STABLE SUB-IDS
   - Prefix every item under §4 with AUT-01, AUT-02, ... (or preserve existing stable IDs if already assigned). Never reuse or recycle IDs.

2. STALE-QUOTE & RELEVANCE PASS
   - Locate every anchor text, quote, or reference from these items in the live source files.
   - Classify each anchor as: [EXACT] / [CHANGED] / [GONE].
   - Report the total counts (e.g., 5 Exact, 3 Changed, 2 Gone) before performing deeper evaluation.

3. AUDIT, EVALUATE & SORT
   - For every item under §4, evaluate its current validity against the updated codebase and dissertation draft.
   - For complex items: Spawn background/sub-agents to perform required actions (e.g., web search for literature, codebase scraping, running verification scripts or GPU runs on nespegpu).
   - Identify dependencies and overlaps: Explicitly flag if resolving AUT-X inherently alters or resolves AUT-Y.
   - Sort each audited item into one of three buckets:
     a) YOU APPLY (Clear-cut, small/medium edits, no overlap conflicts, fully valid).
     b) I DECIDE (Items requiring my explicit decision, subjective choices, structural shifts, or where you disagree with my initial premise).
     c) BLOCKED / INVALID (The cited passage is GONE, no longer relevant due to text changes, or failed external claim verification under §1-§3).

4. CHECK GATE INTEGRITY & PROBES
   - Check if any item impacts load-bearing probes in check_audit_claims.py, GLOSSARY entries, or Appendix errata. Do not propose deleting or refactoring text tied to active probes without flagging it.

5. UPDATE PENDENCIAS.md (DO NOT TOUCH DISSERTATION TEXT YET)
   - Rewrite the items under "## §4 · Pensamentos e considerações do Autor" to adopt a standardized schema per item:
     - ID · Source Status ([EXACT]/[CHANGED]/[GONE]) · Your Take & Evaluation · Proposed Resolution Plan · Overlaps/Dependencies · Target Disposition ([YOU APPLY] / [I DECIDE] / [BLOCKED]) · Build Commit Measured Against.
   - Create/Update a distinct sub-section "## §4.1 · Decisões Pendentes do Autor" carrying ONLY the [I DECIDE] items, explicitly detailing options, trade-offs, and estimated effort/costs for my final call.

6. BUILD THE EXECUTION PLAN
   - For all items marked [YOU APPLY], construct an ordered execution plan:
     - Group items into Wave 1 (Independent/Small/No-overlap items that can run in parallel) and Wave 2 (Larger or sequential items).
     - Specify expected PDF render locations for each proposed edit.

OUTPUT REQUIRED WHEN DONE:
A summary report of the Audit Pass (counts, bucket distribution, key overlaps, and items placed in "§4.1 Decisões Pendentes do Autor" awaiting my input). No edits to dissertation .tex files should be made during this phase.

---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-20 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
