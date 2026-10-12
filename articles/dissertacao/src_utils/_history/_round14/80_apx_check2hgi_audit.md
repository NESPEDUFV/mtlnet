# Round 14 — audit of Appendix E, "How Check2HGI and the Joint Model Work"

**Scope.** Every technical claim in `src/chapters/apx_h_check2hgi_joint_model.tex` re-measured
against the live implementation, plus a visual audit of the two figures in the rendered PDF. The
appendix renders as **Appendix E**, pages 107-116 of the 116-page defense build.

**Method.** Claims were read from the appendix source, then located in the code by grep and read in
place. Paths below are relative to the repository root (`/Users/vitor/Desktop/mestrado/ingred`).
The figures were audited by rendering `build/main.pdf` pages to images and looking at them, not by
reading the TikZ source, because the defects found are collisions that only exist in the output.

---

## 1 · Defects found

| # | Where | Defect | Evidence |
|---|---|---|---|
| **D1** | `apx_h:eq:apx-region-fusion` | `\mathbf{W}_{mathrm{shr}}` is missing the backslash on `\mathrm`. **Not a TeX error** — it compiles silently and prints as italic literal `mathrmshr` in the PDF (visible on rendered p. 113). The symbol is written correctly (`\mathbf{W}_{\mathrm{shr}}`) in the very next sentence that defines it, so the equation and its own legend disagree. | rendered p. 113, Eq. (E.4) |
| **D2** | appendix-wide | **The region-transition prior being OFF is never stated.** `freeze_alpha=True` and `alpha_init=0.0` appear nowhere in the appendix (`grep -n "alpha\|prior\|log_T\|transition"` over the file returns nothing). `CHAMPION.md:37` calls prior-OFF a key lever worth **~+1.4 pp region**, and `mtl_v17_complete_picture.md:171-181` devotes a section to it. A table headed "Reproduction-critical settings" that omits a +1.4 pp switch is not reproduction-critical. | `docs/studies/archive/mtl_improvement/CHAMPION.md:37`; `science/mtl_v17_complete_picture.md:171-181` |
| **D3** | `apx_h`, §E.3.2 (Step 2) | Prose says the attention module "uses one learned seed query **for every place**". The code has **one seed shared across all places**: `self.S = nn.Parameter(torch.Tensor(1, hidden_channels))`, whose own comment reads "Learnable seed vector (shared query for all POIs)". A per-place seed would be `(num_pois, D)`. This is a factual error about the mechanism, not a wording preference. | `research/embeddings/check2hgi/model/Checkin2POI.py:45-47`, and `:104` "Project Q (shared seed)" |
| **D4** | Figure 9 (`figures/check2hgi_flow.tex`) | **Node overlap in the render.** The export row collides with the hierarchy row above it: "Exported check-in table" overprints `$\mathbf{x}_i\in\mathbb{R}^{64}$`, and "Detached place summary" overprints the `$\mathcal{L}_{P\!R}$` label and the words "region adjacency", which are clipped. Cause: nodes are placed at hardcoded `y=1.25` / `y=-1.35` with `minimum height=1.35cm`, but the "Spatial context" node carries four text lines and grows past its slot. | rendered p. 109 |
| **D5** | Figure 10 (`figures/joint_model_flow.tex`) | **Label collisions in the render.** (a) the "two blocks" exchange label sits on top of the "$9\times256$" text of the category node; (b) the "Shared route" and "Private route" nodes touch with no gap, reading as one box; (c) the "raw-region bypass" label is struck through by its own dashed arrow. | rendered p. 112 |

## 2 · Discrepancy in a theory document, not in the appendix

**T1 — GRU depth. The appendix is right and `mtl_v17_complete_picture.md` is stale.**

- Appendix: "a four-layer unidirectional GRU with input and hidden width 256" (§E.5.3), and the
  settings table row "Four-layer GRU; hidden width 256".
- `science/mtl_v17_complete_picture.md:409` (§11 checklist): "`next_gru` category head, hidden width
  256, **two layers**."
- Code: the head's own default is `num_layers: int = 2`
  (`src/models/next/next_gru/head.py:18`), **but the head does not use its default** — `num_layers`
  is injected from the model-level parameter by `_build_category_head`
  (`src/models/mtl/mtlnet/model.py:161-166`, `:243`), and the MTL experiment config sets
  **`"num_layers": 4`** (`src/configs/experiment.py:428`). The v17 reproduction command
  (`mtl_v17_complete_picture.md:353-390`) passes no `--num-layers`, so the config default stands.

So the rendered dissertation is correct and the theory document's checklist line is wrong. Recorded
here rather than "fixed" in the appendix, because the fix belongs in the theory document and it is
the author's file. **Flagged for the author, not applied.**

## 2b · The appendix is unreachable from the document, and that is an author decision

**T2 — no chapter points at it.** Measured over live prose with comments stripped, across every file
under `src/chapters/`: the label `apx:check2hgi-joint-model` is referenced **zero** times outside its
own `\label` declaration. For contrast, the gradient-cosine appendix is pointed at from four places
(`1_introduction.tex:448`, `2_fundamentals.tex:1023`, `5_mobiwac/02_related.tex:25`,
`6_conclusion.tex:242`). So a reader reaching Appendix E has no route into it from the argument, and
nothing tells them the walk-through exists.

The natural host is Chapter 5, whose method section is what the appendix expands. **NOT APPLIED here**
for two reasons: Chapter 5 is the under-review MobiWac chapter, whose errata regime reserves changes
to its body (`NORTH_STAR` §4), and choosing where to send the reader is an editorial call.
**Flagged for the author.** One sentence in `5_mobiwac/04_method.tex` or in the Chapter 5 preface
would close it.

Separately, and cosmetic: the file is named `apx_h_check2hgi_joint_model.tex` but prints as
**Appendix E**, because B, D, and G moved to the supplementary volume and the printed letters now run
A, B, C, D, E over files A, C, E, F, H. Nothing depends on the filename and no letter is hardcoded
anywhere, so this is a naming wart rather than a defect. Renaming it would touch `content.tex:398`
and nothing else.

## 3 · Claims verified as correct

Each row was read in the code, not inferred.

### Check2HGI

| Appendix claim | Code | Verdict |
|---|---|---|
| Check-in feature width 11 = 7 category indicators + 4 cyclic time values | `check2hgi/preprocess.py:620-636` (`category_onehot` over `num_categories`, then `hour_sin/hour_cos/dow_sin/dow_cos`) | ✓ |
| Two weighted GCN layers, 11→64 then 64→64, PReLU | `check2hgi/model/CheckinEncoder.py:34-39` (`num_layers=2`; `GCNConv(in,hidden)` then `GCNConv(hidden,hidden)`; `nn.PReLU()`) | ✓ |
| Four attention heads at both hierarchy pools | `check2hgi/check2hgi.py:1000` (`--attention_head` default 4), used at `:339` (Checkin2POI) and `:344` (POI2Region) | ✓ |
| Each head summarizes a 16-dimensional part | `Checkin2POI.py:108` (`dim_split = hidden_channels // num_heads` = 64/4) | ✓ |
| Residual projection and PReLU combine the four outputs | `Checkin2POI.py:158-166` (`O = Q_broadcast + poi_agg`; `O = O + F.relu(self.fc_o(O))`; `self.prelu(O)`) | ✓ |
| Learned scalar initialized to 1.0 controls the place table's contribution | `Check2HGIModule.py:177` (`gamma_init: float = 1.0`), `:440` (`nn.Parameter(torch.tensor(float(gamma_init)))`) | ✓ |
| The pooled place representation is detached on the spatial route | `Check2HGIModule.py:646-647` (`pos_poi_emb.detach() + self.reg_gamma * poi2vec_residual`) | ✓ |
| City summary is area-weighted then sigmoid | `check2hgi.py:346-347` (`torch.sigmoid((z.transpose(0,1) * area).sum(dim=1))`) | ✓ |
| Region-to-city negatives permute check-in feature rows | `Check2HGIModule.py:17-27` (`corruption(x)` = `x[torch.randperm(x.size(0))]`) | ✓ |
| Place-to-region negatives partly target moderately similar regions | `Check2HGIModule.py:58` (`p2r_hard_neg_sim_range=(0.6, 0.8)`) | ✓ |
| Masked-place reconstruction hides 15% and reconstructs the category distribution | `check2hgi.py:415` (`mae_poi_mask_rate` default `0.15`); `Check2HGIModule.py:109` (`mae_poi_target_kind = "category_aggregate"`) | ✓ |
| Loss weights 0.4 / 0.3 / 0.3 / 0.3 / 0.1 (Eq. E.3) | `check2hgi.py:1001-1003` (`alpha_c2p=0.4`, `alpha_p2r=0.3`, `alpha_r2c=0.3`); `:477-478` (v14 recipe `--mae-poi-lambda 0.3 --anchor-lambda 0.1`) | ✓ |
| Full-batch Adam, 500 epochs, lr 1e-3, weight decay 0, clip 0.9, seed 42 | `check2hgi.py:1029` (`--lr` default `0.001`); `:721` (`weight_decay` default `0.0`) with `:732` taking the no-decay branch, `optimizer = torch.optim.Adam(..., lr=args.lr)`, and `:733` printing "Adam lr=... (no WD)"; `:86` (`train_epoch_full_batch`, the full-batch path); `:1032` (`--epoch` default 500); `:1031` (`--max_norm` default 0.9); `:203` (`_ssl_seed` defaults 42) | ✓ |

### Joint model

| Appendix claim | Code | Verdict |
|---|---|---|
| Independent encoders, three linears 64→256, 256→256, 256→256; ReLU + LayerNorm after each; dropout after the first two only | `models/mtl/mtlnet/model.py:315-332` (`_build_encoder`: first block Linear+ReLU+LN+Dropout, `num_layers-1` more of the same, then a final Linear+ReLU+LN **with no Dropout**), called at `:112-125` with `encoder_layer_size=256`, `num_encoder_layers=2` (`:66` defaults) | ✓ |
| Two bidirectional cross-attention blocks, four heads, width 256, dropout 0.15 | `mtlnet_crossattn/model.py:229-230` (`num_crossattn_blocks=2`, `num_crossattn_heads=4`), `:228` (`shared_dropout=0.15`), `:249-250` (`ffn_dim` defaults to `shared_layer_size`=256) | ✓ |
| Category stream queries region first; region then queries the **already updated** category stream | `mtlnet_crossattn/model.py:168-199` (`cross_ab` runs, `a = self.ln_a1(a + a_upd)`, then `kv_a = a` — the updated `a` — feeds `cross_ba`) | ✓ |
| Each direction has its own projections, residuals, layer norms, and a 256→256→256 GELU feed-forward network | `:127-148` (separate `cross_ab`/`cross_ba`, `ln_a1/b1/a2/b2`, `ffn_a`/`ffn_b` each `Linear→GELU→Dropout→Linear→Dropout`) | ✓ |
| Padding positions are excluded from the attention weights | `:170-171,193-194` (`key_padding_mask=b_pad_mask` / `a_pad_mask`) | ✓ |
| Separate final layer normalizations after two blocks | `mtlnet_crossattn_dualtower/model.py:74-75` (`cat_final_ln`, `next_final_ln`) | ✓ |
| Four-layer GRU, hidden width 256, seven category logits | `configs/experiment.py:428` (`num_layers: 4`) injected via `mtlnet/model.py:161-166`; `next_gru/head.py:23-33` | ✓ (see T1) |
| GRU head takes the last valid position, then LayerNorm + Dropout + Linear | `next_gru/head.py:31-33` | ✓ |
| Private tower reads the raw 9×64 region history; shared tower reads the 9×256 cross-attention output | `mtlnet_crossattn_dualtower/model.py:96,124` (`raw_region_seq=next_input` alongside `shared_next`); `next_stan_flow_dualtower/head.py:44-52` | ✓ |
| Private tower 4 heads / dropout 0.3; shared tower 8 heads / dropout 0.1; both width 128 | `next_stan_flow_dualtower/head.py:143-149` (`d_model=128`, `num_heads=8`, `dropout=0.1`, `priv_num_heads=4`, `priv_dropout=0.3`) | ✓ |
| Additive fusion with trainable β initialized to 0.1 (Eq. E.4, structure) | `head.py:239` (`self.beta = nn.Parameter(torch.tensor(0.1))`), `:412` (`priv_feat + self.beta * self.aux_proj(shared_feat)`) — this is `fusion_mode="aux"`, and `aux` is the reported champion (`CHAMPION.md:36`) | ✓ structure; ✗ typesetting (D1) |
| Supervised objective is the fixed 0.75 / 0.25 combination | `mtl_v17_complete_picture.md:373-374` (`--mtl-loss static_weight --category-weight 0.75`) | ✓ |
| Three AdamW groups: category, region, shared; one backward pass | `mtl_v17_complete_picture.md:186-196` (group table); accessors in `mtlnet_crossattn_dualtower/model.py` docstring `:20-26` | ✓ |
| Checkpoint maximizes the geometric mean of category macro-F1 and region Acc@10 | `src/training/runners/mtl_cv.py:206` (`joint_geom_simple = sqrt(f1_a * reg_acc10)`), `:211` (default `geom_simple`) | ✓ |
| 50 epochs, batch 8192 per task, clip 1.0, five user-disjoint folds, seeds {0,1,7,100} | `mtl_v17_complete_picture.md:358-361,415-417` | ✓ |
| Peak learning rates: category 1e-3, region 3e-3, shared 3e-3 for AL/AZ/FL and 1e-3 for CA/TX/Istanbul | `mtl_v17_complete_picture.md:380-383` (`--shared-lr 1e-3` for CA/TX/Istanbul) and `:394-400` (§10.2: AL/AZ/FL change only `--shared-lr 3e-3`) | ✓ |
| The four stated implementation paths exist | `research/embeddings/check2hgi/`, `src/models/mtl/mtlnet_crossattn_dualtower/`, `src/models/next/`, `src/losses/`, `src/training/` all present on disk | ✓ |

### Notation consistency with the rest of the dissertation

The check-in tuple $c_i=(u_i,p_i,l_i,g_i,t_i)$, the place embedding $\mathbf{e}_{p_i}\in\mathbb{R}^{d}$
and the check-in vector notation are used in the appendix in the same shapes the frame chapters use.
The appendix writes the widths concretely as $\mathbb{R}^{64}$ rather than the symbolic $d$/$d'$,
which is consistent with its stated purpose (an operational walk-through) and does not conflict.

## 4 · What was NOT checked, and why

- **Numerical results.** The appendix reports no result cells, so the number protocol has nothing to
  audit here. The one quantitative claim about outcomes (`+1.4 pp` for prior-OFF) is in THIS report,
  quoted from `CHAMPION.md`, and is deliberately NOT put into the appendix prose.
- **Whether the reported runs used these exact files.** Same limit as the round-4 CoUrb seed finding:
  the code on disk is evidence of what the code does, not proof of which commit produced the board.
  No claim in this report asserts otherwise.
- **The `aux_proj` weight-decay detail.** `mtl_v17_complete_picture.md:167` states β receives the
  normal 0.05 decay. The appendix does not mention β's decay at all, which is an omission rather than
  an error, and adding it was judged below the reproduction-critical bar. Noted, not applied.

## 5 · Reproduction of this audit

```bash
cd /Users/vitor/Desktop/mestrado/ingred
# D3, the seed-query defect:
sed -n '44,48p' research/embeddings/check2hgi/model/Checkin2POI.py
# T1, the GRU depth:
grep -n 'num_layers' src/configs/experiment.py | head -2
sed -n '409p' articles/dissertacao/science/mtl_v17_complete_picture.md
# D2, prior-OFF absent from the appendix:
grep -c 'alpha\|prior\|log_T\|transition' articles/dissertacao/src/chapters/apx_h_check2hgi_joint_model.tex
# D1/D4/D5, the render (requires a built main.pdf):
cd articles/dissertacao/src && make defense
python3 -c "
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument('build/main.pdf')
for p in (109, 112, 113):
    pdf[p-1].render(scale=2.4).to_pil().save(f'/tmp/apx_p{p}.png')
"
```

---

## 6 · Second pass: what the figures were missing (author-raised)

**D6 — Figure 9 showed the stages but never named the levels.** Raised by the author after the
layout fix landed. Section E.2 builds its whole explanation on "four node levels" and "the four
resolutions of the representation" (check-in, place, region, city) and on the membership chain
"every check-in belongs to one place, every retained place belongs to one region, and every region
belongs to the city". None of that vocabulary appeared in the figure, so a reader could not map the
prose onto the boxes.

Two additions, both verified in the render (p. 110):

1. **A hierarchy spine** across the top: `check-in` $c_i$ → `place` $p$ → `region` $r$ → `city`
   $\Omega$, with each containment arrow labelled by the objective that spans that boundary
   ($\mathcal{L}_{CP}$, $\mathcal{L}_{PR}$, $\mathcal{L}_{R\Omega}$). The labelling is not
   decorative: the three discriminators are defined across exactly these level pairs
   (`alpha_c2p`, `alpha_p2r`, `alpha_r2c` at `check2hgi.py:1001-1003`), so the spine reads directly
   against Equation E.2 instead of needing a separate legend.
2. **A level tag on each processing box** (`raw records`, `check-in level`, `place level`,
   `region level`, `city level`), set inside the box rather than beside it, because an outside label
   would sit in a band gap where it could collide with an arrow, which is the defect class D4/D5
   were about.

The caption now describes both. Band `minimum height` was raised from 2.8cm to 3.3cm to absorb the
extra text line; without that the tags would have clipped, reintroducing D4.

**Gate note.** The first caption wording, "each processing stage is tagged with the level it works
at", tripped `check_register.py` as a stranded-preposition shape (a Class B hard-phrasing hit under
WRITING_LAW §1) and made `make check` exit 2 with zero FAIL lines in the summary. Rewritten to
"carries a tag naming its own level". Worth recording because rc=2 with no visible FAIL is easy to
misread as an infrastructure problem rather than a register hit.

## 7 · Final state

| Target | rc | pages | tex_errors | Overfull |
|---|---|---|---|---|
| `defense` | 0 | 117 | 0 | 0 |
| `academico` | 0 | 114 | 0 | 0 |
| `ppgc` | 0 | 118 | 0 | 0 |
| `extra` | 0 | 26 | 0 | 0 |
| `make check` | 0 | — | — | 0 FAIL lines |
| `make selftest` | 0 | — | — | required set passes |

The three main-volume targets each gained one page against the pre-round baseline (116 / 113 / 117),
because Table 12 gained the prior-OFF row and reflowed. `extra` is unchanged.

**T1 and the title-page label: CLOSED on the author's instruction (see §9). T2 remains open**
(no chapter points at Appendix E) -- that one is an editorial call about where to send the
reader, and it would touch the under-review Chapter 5.

---

## 8 · Overleaf log findings (author-supplied, TeX Live 2025)

The author's Overleaf build reports warnings this tree does not. **Cause: version skew.**
Overleaf runs TeX Live 2025, this tree runs TeX Live 2026 (`pdfTeX 3.141592653-2.6-1.40.29`).
Babel and the font metrics differ between them, and line breaking follows. **For anything
submitted, the Overleaf log is authoritative, not this one.**

| Item | Status |
|---|---|
| `Overfull \hbox (9.27821pt too wide)` at `1_introduction.tex:158-162` | **FIXED at source, version-independently.** Local TL2026 reports zero Overfull boxes for that paragraph, so the defect could not be reproduced here and no local measurement could confirm a fix. Hyphenation points were therefore added for the paragraph's long words (`preamble.tex`, after the existing `\hyphenation{fe-de-ral}`), which changes no wording and only widens the set of lines TeX may choose. `dimensional` is the load-bearing entry: it follows an explicit hyphen in "64-dimensional", and TeX does not hyphenate the remainder of a word after an explicit hyphen unless the parts are given. **Confirm on Overleaf.** |
| `Package babel Warning: Last declared language option is 'brazil', but the last processed one was 'english'` | **NOT changed. Author decision needed.** This is a real latent ambiguity, not noise: `brazil` and `english` are both class options (`preamble.tex:38-39`), `brazil` is declared last but `english` is processed last, which is exactly why the preamble needs the `\addto\captionsbrazil` block to anglicize captions by hand. `main=english` was TESTED here: rc=0, 116 pages, warning gone, Portuguese `Resumo`/`Palavras-chave` intact, English captions intact, zero hyphenation change on page 2. It was reverted rather than shipped, because the warning does not fire on TL2026 and a babel main-language change should be verified where it actually fires. Apply and confirm on Overleaf. |
| `Underfull \hbox` at `content.tex:121`, `3_cbic/method.tex:16` (x2), `4_courb.tex:2` | **Pre-existing, previously audited, no action.** The first is front matter; the two in `3_cbic/method.tex` are inside a footnote about the released implementation's neighbor mean. Underfull boxes are loose spacing, not overrun text, and none of these is in the appendix under audit. |

**Note on parallel builds.** `latexbuild.sh:33` gives every target its own `build/<stem>-aux`,
added (per its own header note) because concurrent builds previously corrupted each other's
aux files. Building the four targets concurrently is therefore safe and is what this round
does. The one caveat: do not run two builds of the SAME target at once, which produced a
spurious `ppgc: rc=2` earlier in this session.


---

## 9 · T1 and the advisor label, closed

Both were flagged rather than fixed in the first pass and the author then asked for them.

**T1, the GRU depth: the theory document was corrected, not the appendix.** The direction is
the point. `mtl_v17_complete_picture.md` said "two layers" in TWO places (the §3.4 code block
and the §11 checklist); the runtime value is four; Appendix E already said four and was right.
The trap that produced the error is worth stating, because it makes the wrong answer look
verified: `NextHeadGRU.__init__` really does declare `num_layers: int = 2`
(`next_gru/head.py:18`), so reading the head file alone confirms "two". That default never
applies on the MTL path -- `MTLnet` forwards its model-level `num_layers` into the category
head (`mtlnet/model.py:161-166`, `:243`) and the MTL config sets `"num_layers": 4`
(`configs/experiment.py:428`), with no `--num-layers` in the v17 command to override it.

Settled by instantiation rather than by reading, which is the only way to be sure which
default wins:

```
gru.num_layers = 4      weight_ih parameter sets = 4
gru.hidden_size = 256   bidirectional = False
```

§3.4 now carries that explanation, so the next reader does not "correct" it back to the head
default.

**The advisor label: the macro was restored, not the text relabelled.** `abntex2-UFV.sty`
hardcoded `Orientador:` with the language-aware `\imprimirorientadorRotulo` commented out on
the line directly above. `\orientadorname` is already `Supervisor:` under the `english` class
option (`abntex2.cls:183` -- the same block that yields this document's "APPENDIX", "Abstract",
and "List of abbreviations and acronyms"), and the signature page eleven lines below already
read "Adviser", so the file was inconsistent with itself and with the language the document
selects. Rendered title page now reads `Supervisor: Fabrício Aguiar Silva`, zero occurrences
of "Orientador". The line is inherited from UFV's own template, so the deviation is recorded
in the file and reverting that hunk restores the template's literal.

**One instrument defect found by sabotage, worth recording.** `ORI-01`'s first pattern was
`r"^\s*\{Orientador:~"`. This engine matches with `re.I` only and never `re.MULTILINE`, so
`^` binds to STRING START and cannot match mid-file: the probe reported "holds" even with the
Portuguese literal restored. It guarded nothing. Sabotage validation is the only reason this
surfaced, and it is a reusable lesson for probes in this file -- **never anchor a probe pattern
with `^` here.** Fixed to an unanchored literal; both `ORI-01` and `ORI-02` now flip on
sabotage and hold when restored.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
