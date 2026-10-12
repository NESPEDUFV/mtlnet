# 36_source_ledger.md — every reference this round touched, and how far its verification got

Round 9, 2026-07-30. Build commit `03b53d16`. One row per reference, and the row states **which of the
three admissibility conditions of `AGENT_GUARDRAILS` §1 it met**: a resolvable identifier, the record
opened *this session*, and the specific claim located in the source. A reference that fails any one of
the three does not enter prose. Two here fail, and they are marked rather than smoothed.

## 1 · Verified in full — identifier, record opened, claim located

### `bruna2014spectral`
- **Identifier:** arXiv:1312.6203v3. No DOI; the ICLR 2014 version has no publisher DOI record.
- **Opened this session:** the arXiv API record at `export.arxiv.org/api/query?id_list=1312.6203`.
- **Attributes, copied from that record:** Joan Bruna, Wojciech Zaremba, Arthur Szlam, Yann LeCun;
  submitted 2013-12-21, v3 2014-05-21; primary class cs.LG; author comment "14 pages".
- **Claim it would support in §2.2:** that spectral graph convolution is defined through the graph
  Laplacian. **Located** in the abstract: the paper describes two constructions, one of which is
  built on the spectrum of the graph Laplacian.
- **Status:** admissible. Requested by Germano (GER-01). **Not yet inserted** — GER-01 is in Wave B,
  behind another agent's open edit of `2_fundamentals.tex`.

### `scarselli2009gnn`
- **Identifier:** DOI 10.1109/tnn.2008.2005605.
- **Opened this session:** the Crossref record, and OpenAlex for the abstract (Crossref carries none).
- **Attributes, copied from Crossref:** Franco Scarselli, Marco Gori, Ah Chung Tsoi, Markus Hagenbuchner,
  Gabriele Monfardini; *IEEE Transactions on Neural Networks* 20(1), pp. 61-80.
- **Claim it would support in §2.2:** that this paper defines the GNN model class. **Located** in the
  abstract: it proposes a neural network model called the graph neural network model, extending
  existing methods to process data represented in graph domains.
- **A discrepancy, recorded rather than resolved:** Crossref issues the work as **2009**, OpenAlex as
  **2008** (the online-first date). The bib entry uses **2009**, the journal issue year, which is what
  the volume/issue/pages describe. This was checked because the prior audit had left an open
  `[VERIFY]` on the author list — that flag is now closed: all five authors are present in Crossref,
  including Monfardini, which the earlier read had truncated.
- **Status:** admissible. Requested by Germano (GER-01). **Not yet inserted** — Wave B.

## 2 · Attributes verified, claim NOT verified — blocked, and the item with it

### `wang2025hamtl`
- **Identifier:** DOI 10.1007/s11227-025-07643-7 (*The Journal of Supercomputing*, 2025).
- **Opened this session:** the Crossref record. Attributes are sound.
- **What could NOT be obtained: the abstract.** OpenAlex holds no abstract for it. The configured
  Springer Nature key returns **401** on `meta/v2`, `metadata`, `openaccess` and `meta/v1`. The
  article is closed access. `link.springer.com` was granted and then **302-redirects to
  `idp.springer.com`**, an authentication gate, which I did not attempt to route around.
- **Author-count disagreement, unresolved:** OpenAlex reports 6 authors, Semantic Scholar 7, Crossref
  its own list. Without the publisher record there is no way to adjudicate.
- **A source I refused:** Semantic Scholar returned a machine-generated TLDR. `AGENT_GUARDRAILS` R5
  bars AI output as a source, so it was not used, even though it pointed at exactly the risk.
- **Consequence:** **FAB-28 is BLOCKED, not applied and not decided.** The item asks whether §2.3
  undercounts MTL-for-POI work; the paper that most threatens the chapter's claim of absence is this
  one, and whether it treats a region-like unit as a co-equal end target is precisely what the
  abstract would settle. The claim of absence is therefore **not** re-asserted on the strength of a
  title, and the item says so.
- **What would unblock it:** the author's institutional access to the publisher PDF, or an
  interlibrary copy. One paragraph of its introduction decides the item.

#### Correction to this entry, from the citation auditor's pass — the repo had already verified it

I wrote the entry above as if the paper's content were simply unknown. **It is not.**
`src/references.bib`:1148-1152 carries a provenance block, brought over verbatim from the MobiWac
paper's own bibliography, recording that the entry was **verified against the Springer article page on
2026-07-06** and stating what was found there: HAMTL jointly predicts the next location and its
category with a hierarchy-aware decoder, and **the location target is venue-level**.

That changes three things, and I missed all three by measuring only my own session:

1. **The dissertation's claim of absence survives, on the record it already had.** If HAMTL's headline
   target is the venue, it does not predict a region as a co-equal end target, which is what §2.3
   asserts is missing. The prose at `5_mobiwac/02_related.tex`:92-94 says exactly this ("in both, the
   location target is the exact place") and it is **supported by the recorded verification**, not
   floating.
2. **The citing sentence correctly carries no `[VERIFY]` marker.** The citation auditor read its
   absence as a defect. It is not: the marker would be wrong, because the claim was verified — by a
   prior session, with the date and the source named.
3. **What is genuinely open is narrower than "the content is unknown".** It is that *this* session
   could not independently reproduce that 2026-07-06 read, because the article is closed access and
   every route was refused. A prior verification with a recorded source and date is evidence;
   `AGENT_GUARDRAILS` §1 requires me to open a source before *I* assert something new from it, and it
   does not require me to treat the repository's own recorded verifications as worthless.

**Revised status of FAB-28:** still **BLOCKED**, but for a smaller reason, and the reason is now
stated correctly in its block. The item asks whether §2.3 undercounts MTL-for-POI work. The
strongest counter-example's target level is on the record; what is not on the record is a systematic
count of the field, which is what the item actually needs and what no single paper settles. The author
should know that the answer he most likely wants — does HAMTL break the novelty claim — is
**probably no, on the repo's own recorded reading of the paper.**

**How I got this wrong:** I treated "I could not open it this session" as equivalent to "it is
unverified", and never checked whether the repository had already done the work. The bibliography's
own provenance comments are a source of record for exactly this, and reading them costs one grep.

## 3 · Checked and left alone

### `wongso2025massivesteps` (Massive-STEPS, the Istanbul dataset)
- **Identifier:** arXiv:2505.11239, v3 updated 2026-02-09. **Opened this session** via the arXiv API.
- **Searched for a peer-reviewed record:** Semantic Scholar shows no venue; a Crossref title search
  returns no matching published version. **It is still a preprint**, and the bib entry correctly
  describes it as one. The Crossref negative is weak evidence (a title search, not an exhaustive
  check) and is labelled as such here.
- **Status:** no change needed.

### `kohavi1995crossval`
- Flagged "Recommended" by the prior audit. Entry inspected as committed; no defect found that this
  round needed to act on. Not re-verified against the source of record, and therefore **not** claimed
  as verified.

### `silva2025mtlnet`, `paiva2026stmtlnet`, `velickovic2019deep`, `huang2023hgi`
- Inspected while auditing the model-lineage table's references, not re-verified. One finding worth
  the author's attention: the CoUrb paper's DOI (`10.5753/courb.2026.22960`) is present in the bib,
  and the lineage table's ST-MTLNet row cites it. No action taken.

## 4 · What a reader should take from this ledger

Nine references were touched. **Two are fully admissible and not yet used** (both in Wave B, behind
another agent's file). **One is blocked at the claim step** and takes its review item with it. **Four
were checked without being re-verified, and are labelled that way** rather than counted as audited.
No reference was inserted into prose this round, so no citation in the built PDF changed at `03b53d16`.

The number that matters for the handoff: **0 unsupported citation claims in the built PDF.**
`wang2025hamtl` is the one reference this session could not open, and the sentence citing it turns out
to rest on a verification the repository recorded on 2026-07-06, with the source and the finding
named. The honest statement is not "a claim resting on an unread paper" — it is "a claim resting on a
prior session's read that this session could not reproduce, because the article is closed access."

Four `[VERIFY]` tokens remain in `references.bib`; two are annotated RESOLVED and two belong to other
entries (a page-range and an online-first year). None is an open citation risk. Counted here because
a `grep -c VERIFY` returns 4 and a handoff that says "1 open flag" would not survive that grep.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
