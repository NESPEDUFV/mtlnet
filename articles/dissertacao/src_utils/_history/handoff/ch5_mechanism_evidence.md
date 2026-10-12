# Ch.5 mechanism attribution — evidence audit

> **Escrito em 2026-08-04**, antes de a geracao v18 fechar o vazamento de rotulo (2026-08-13).
> **Nao leva tarja de geracao superada, e a razao importa:** este ficheiro *menciona* celulas
> antigas em vez de as afirmar como correntes — marca as suas proprias celulas v17 como tais
> (por exemplo na tabela de Istanbul e na nota V-3) e usa-as como comparandos, nao como
> resultado. Arbitrado assim em 2026-09-08. Verificar sempre a etiqueta da celula antes de a
> citar; e para o resultado entregue, `VEREDITOS.md` na raiz da pasta.


> **Scope.** Does the repository's evidence support restoring the sentence *"One model serves both
> tasks: the shared trunk carries the semantic context that lifts the next-category task, and the
> private spatial path keeps the next-region task competitive"*? Read-only audit; no file edited.
> Every number below is quoted from its source with `file:line`, except the four paired statistics
> in §1.C, which are **computed this session** from the committed per-fold JSONs and marked
> `[COMPUTED]`.
>
> **Verdict in one line: (b) — a weaker but still positive claim, and it is only *half* the
> sentence.** The category clause is defensible in a scoped form. The `private spatial path keeps
> the next-region task competitive` clause has **no isolating control at all** in the record and is
> the more serious problem, because it is currently asserted in three places already.
>
> **The decisive new finding of this audit: the cascade control IS the trunk-removal test the
> chapter says it does not have.** Ch.5 already tells the reader the cascade "remove[s] the shared
> trunk" (`05_setup.tex:167`), it ran on the shipped configuration at four datasets, and the
> category gain survives it in full. This is strictly better evidence than the F50 arm the chapter
> currently treats as the only direct test of the trunk — and it points the other way. Nobody
> connected the two records.

---

## 1 · Controls table — what actually isolates a component

| # | Control | Held fixed | Changed | Datasets | n | Effect (verbatim) | Isolates a component? |
|---|---|---|---|---|---|---|---|
| A | **Freeze-region (W6)** | everything else | region stream `requires_grad=False` at init + reg loss off | AL, AZ, FL | seed 0 × 5f | cat `63.50 ±1.74` / `63.67 ±1.28` / `79.79 ±0.46`; Δ vs single-task ceiling `+7.63` / `+6.54` / `+4.64` | **No.** Removes region *training*, not any category-side component |
| B | **Capacity-matched dedicated** | protocol, scorer | dedicated cat width 0.64M → ~4.2M (AL) / ~5.2M (CA) | AL, CA | n=20/arm (4 seeds × 5f) | AL best arm `56.16` (std `1.89`) vs ceiling `56.82 ±0.03` vs joint `64.51 ±0.09`; CA `69.88 ±0.26` vs `70.60 ±0.07` vs `77.05 ±0.01` | **No.** Rules out a rival explanation (parameters); does not locate a component |
| C | **Cascade (CSLSL/CatDM)** | representation, heads, recipe, folds, device, precision | **shared trunk severed** (`disable_cross_attn=True`) + directed cat→region edge added | AL, AZ, FL, Istanbul | seed 0 × 5f | Δjoint `+0.02` / `+0.00` / `−0.01` / `−0.22`; **Δcat `+0.20` / `+0.20` / `+0.01` / `−0.20`** | **YES — this is the trunk-removal control** |
| D | **F50 cross-attention ablation** | rest of that model | cross-attention stack removed | FL only | 5f × 50ep, seed 42 | cat `68.36 ±0.74` on vs `68.32 ±0.67` off, Δ `−0.04 ±0.13`; Wilcoxon `W+=5 p=0.6250` | Yes, but **on a superseded configuration** |
| E | **F49 frozen-cat λ=0** | — | category stream frozen + cat loss off | AL, AZ, FL | 5f, seed 42 | arch Δ `+6.48` / `−6.02` / `−16.16` pp (region Acc@10) | Yes, but measures the **region** side, and see §5.D |
| F | **Cat-transfer decomposition** | — | reg gradient off (`--category-weight 1.0`) | AL, FL | 4 seeds {0,1,7,100} | architecture `+3.22` (AL) / `+2.27` (FL); region-transfer `−0.67` / `+0.93` | Same shape as A; **multi-seed**, and A's better-footed sibling |
| — | **Private spatial path** | — | — | — | — | **NOTHING IN THE RECORD** | — |

### Sources, verbatim

**A — freeze-region (W6).** `docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md:22-24`

```
| AL | 55.87 | 63.56 | **63.50 ±1.74** | **+7.63** | −0.06 | **trunk** ✅ |
| AZ | 57.13 | 63.39 | **63.67 ±1.28** | **+6.54** | +0.28 | **trunk** ✅ |
| FL | 75.15 | 79.82 | **79.79 ±0.46** | **+4.64** | −0.03 | **trunk** ✅ |
```

Convention, `W6:26`: "cat = macro-F1 at the f1-best epoch, fold-mean ±pstd (matched scorer
`a40_score_matched.py`)". Footing, `W6:54`: "**n=5 provisional** (seed 0; {1,7,100}→n=20
post-deadline)". Comparand caveat, `W6:52-53`: the `55.87/57.13/75.15` column is the **seed-0
single-task** value (Ch.5 Table 2), **not** the n=20 tuned dedicated ceiling of Table 3
(`56.82/56.43/74.51`) — Ch.5 handles this correctly by pointing the deltas at Table 2 by name.

**W6's own self-declared verdict overstates what it measured.** `W6:3-4`: "**Verdict: W6 CLOSED. The
joint CATEGORY win is the shared TRUNK (architecture/capacity), NOT region→category transfer.**"
The design section is the honest one — `W6:15`: "any cat lift over the STL ceiling must come from
the shared trunk" is a **disjunction with one term dropped**. Freezing the region stream leaves the
category encoder, the per-stream feed-forward blocks and the added depth untouched, so "the shared
trunk" is not the only survivor. Ch.5 caught this and says so at `06_results.tex:204-209`. **The
finding doc was never corrected**, and it is the document a reader of the internal record meets
first. See §6, defect P-1.

**Known instrument defect, `W6:64`:** "the frozen-stream probes in this study froze WEIGHTS correctly
… but `model.train()` at each epoch start re-enabled dropout in the frozen stream for all epochs
after the freeze — the 'frozen-at-init' stream was dropout-stochastic during training. Directional
conclusions stand". Ch.5 records this at `06_results.tex:281-282` and deliberately does not surface
it in prose. Acceptable, but it means A cannot be strengthened by simply adding seeds: "any n=20
seed-extension must not mix regimes with these seed-0 rows".

**B — capacity-matched.** `docs/results/closing_data/capacity_matched_stl_cat/README.md:54-55`

```
| Alabama | 56.82 ±0.03 | 56.16 ±1.89 (**−0.66**) | 64.54 (**−8.38** from the matched arm) |
| California | 70.60 ±0.07 | 69.88 ±0.26 (**−0.72**) | 77.05 (**−7.17** from the matched arm) |
```

`README.md:66-68`: "Parameter count alone, without the second task's training signal, does not
reproduce the gain **in this setting** — category task, two of six datasets, one width point per
dataset, width scaling rather than depth." Fairness scope that must travel with the number,
`README.md:81-82`: "the ceiling was tuned best-vs-best over a wider recipe grid than the 3-recipe
(AL) / 2-recipe (CA) sweeps here." Licensing, `README.md:8-9`: POST-SUBMISSION, "**never** enter
Chapter 5". Ch.6 renders it correctly at `6_conclusion.tex:211-231`.

**C — cascade.** `docs/studies/closing_data/archive/findings/CSLSL_CASCADE.md:27-30`

```
| AL | 63.45 ±2.00 | 63.25 ±2.02 | +0.20 | 69.48 ±3.03 | 69.65 ±3.32 | −0.17 | 66.39 | 66.37 | **+0.02** |
| AZ | 63.63 ±1.34 | 63.44 ±1.33 | +0.20 | 59.18 ±1.83 | 59.36 ±1.79 | −0.18 | 61.37 | 61.36 | **+0.00** |
| FL | 79.83 ±0.49 | 79.82 (§1 board, H100) | +0.01 | 77.27 ±0.95 | 77.28 (§1 board) | −0.01 | 78.54 | 78.55 | **−0.01** ≈tie |
| Istanbul (**v17**, P6) | 63.12 ±0.57 | 63.32 (H3) | −0.20 | 75.16 ±0.69 | 75.41 (H3) | −0.25 | 68.88 | 69.10 | **−0.22** ≈tie |
```

What varies, `CSLSL_CASCADE.md:15-19`: "reuses the **exact champion heads on the frozen Check2HGI
substrate**, with the ONLY varying factor a directed **cat→region** cascade edge … `disable_cross_attn=True`
(sever the symmetric channel → a true cascade, not a coupling ablation)". Everything else is
"byte-identical champion-G v16" (`:20`).

**The flags are verified active, not silent no-ops** — `CSLSL_CASCADE.md:59-63` records three
independent code audits plus runtime instrumentation: "the 2 cross-attn blocks were called **0×**
with the flag set vs **2×** without" (`:69-70`), and the learned coupling grew from ~0 to large
magnitude in the scored runs (`:82-83`, FL fold1 `0.291 → 4.613`). I confirmed the code path
myself: `src/models/mtl/mtlnet_crossattn_dualtower/model.py:64-65` guards the entire block loop with
`if not self._disable_cross_attn:`, so with the flag set the category output is
`cat_final_ln(category_encoder(x))` — the category stream **never touches the region stream**. The
added cat→region edge is region-side only and detached (`next_stan_flow_dualtower/head.py:456-457`,
`cond_detach=True`), so it cannot feed the category head.

**Therefore: in the cascade arm, the shared trunk is gone from the category path entirely — and the
category score does not move.**

**[COMPUTED] Paired per-fold test, cascade vs champion-G, next-category macro-F1.** Same seed, same
folds, same device; sources `docs/results/closing_data/a40/{al,az}_{cascade,champG_a40}_s0.json`,
key `cat_per_fold`:

| State | cascade (trunk removed) | champion-G (trunk present) | Δcat (cascade − champ) | 90% CI | Wilcoxon | paired t |
|---|---|---|---|---|---|---|
| AL | 63.45 | 63.25 | **+0.20** | [−0.08, +0.48] | W=3.0, p=0.3125 | p=0.209 |
| AZ | 63.63 | 63.44 | **+0.20** | [+0.08, +0.31] | W=0.0, p=0.0625 | p=0.021 |

Both point estimates are **positive** — removing the trunk did not cost the category task anything,
and at AZ the small difference favours the trunk-free model. Region side, same computation:
AL `−0.17` (90% CI [−0.48, +0.15], p=0.3125), AZ `−0.18` (90% CI [−0.36, −0.00], p=0.1250).

**[COMPUTED] The cascade reproduces essentially the whole "trunk" lift with no trunk.** Against the
same single-task comparand W6 uses (`W6:22-24`, Ch.5 Table 2 column):

| State | single-task ceiling | W6 freeze-region probe | Δ | cascade (**no trunk**) | Δ | cascade − W6 |
|---|---|---|---|---|---|---|
| AL | 55.87 | 63.50 | +7.63 | 63.45 | **+7.58** | −0.05 |
| AZ | 57.13 | 63.67 | +6.54 | 63.63 | **+6.50** | −0.04 |
| FL | 75.15 | 79.79 | +4.64 | 79.83 | **+4.68** | +0.04 |

Selector caveat, stated so it is not smoothed over: W6 reads cat at the **f1-best** epoch (`W6:26`),
the cascade board at the **diagnostic-best** epoch (`CSLSL_CASCADE.md:32`). Both use the same
matched scorer `a40_score_matched.py`, and the residuals here (≤0.05 pp) are far below fold-std
(1.3–2.0 pp), so the conclusion does not rest on the convention. It should still be named in any
sentence that quotes the pairing.

**D — F50.** `docs/findings/archive/F50/F50_T1_5_CROSSATTN_ABSORPTION.md:19` cat `68.36 ± 0.74` vs
`68.32 ± 0.67`, Δ `−0.04 ± 0.13`; `:35` "Paired Wilcoxon two-sided cannot reject equality on either
task: cat W+=5 p=0.6250". Scope and limits in §2.

**F — cat-transfer decomposition (not currently cited in Ch.5 or Ch.6; it should be).**
`docs/results/mtl_improvement/cat_transfer_and_T53.md:21-22`

```
| AL | 50.35 | 53.57 ± 0.24 | 52.91 ± 0.27 | **+3.22** | **−0.67** | +2.56 |
| FL | 69.96 | 72.24 ± 0.03 | 73.16 ± 0.04 | **+2.27** | **+0.93** | +3.20 |
```

This is W6's experiment done properly: **four seeds {0,1,7,100}** instead of one, with a correction
already applied and documented (`:31-39`, a manifest mis-pointing caught and re-run). Its own
honesty note, `:25-27`: "The reg-OFF isolation isn't perfectly clean: the cat stream still attends
to the reg stream's K/V in the bidirectional cross-attn even at reg-weight 0". Its verdict, `:41`:
"the cat gain is ARCHITECTURE-DOMINATED; region transfer is modest and scale-dependent" — **and it
carefully says architecture, not trunk.** Caveat that makes it conservative, `:48-50`: the
single-task comparand used logit-adjust τ=0.5, which "helps STL cat (+2.7) but hurts MTL cat — so
the STL ceiling here is, if anything, an *inflated* comparand." Different substrate generation from
the shipped board, so it is corroboration, not a Ch.5 number.

---

## 2 · The F50 cross-attention ablation — what it shows, and how the record reads it

**What it shows.** At **Florida only**, `5f × 50ep`, seed 42: removing the entire cross-attention
shared backbone ("4 cross-attn ops + 4 per-task FFNs + 8 LayerNorms, ~5.5 M params", `F50:5`)
changes next-category macro-F1 by `−0.04 ± 0.13` and region top10 by `−0.21 ± 0.86`; neither is
separable from zero (`F50:35`). Per-fold correlation `r = 0.985` on category (`F50:33`).

**Stated limitations.**
1. **One dataset.** Florida only. The AL/AZ follow-ups were planned (`F50:164-176`) and, as far as
   the record shows, never ran.
2. **Superseded configuration.** `F50:223-224` gives run dirs under `check2hgi/florida/…bs2048`;
   the shipped board is `check2hgi_dk_ovl/…bs8192`. Ch.5 states this at `06_results.tex:221-222`.
3. **The region head was driven by an α·log_T prior the shipped models do not use.** Confirmed
   independently: `src/configs/canon.py:51-52` pins `freeze_alpha=True`, `alpha_init=0.0`.
4. **C4 leak era.** `docs/findings/F50_T4_PRIOR_RUNS_VALIDITY.md:49` rates "F50 P1 no_crossattn" as
   "✅ valid" **for the paired Δ only**; `:7` "Absolute numbers … inflated by ~13-17 pp."

**Does the record read the null as "no contribution" or as "compensation"? Unambiguously
compensation.** `F50:229`: "**Cross-attn is genuinely dead at FL, but as a hidden compensation
effect, not a true null contribution.**" `F50:5`: "it is because the **cat encoder absorbs**
whatever the shared backbone would contribute". The arithmetic offered, `F50:110-113`: cross-attn
contribution to reg `−16.16` + cat-encoder compensation `+15.95` ≈ 0.

**But the compensation reading is weaker than the chapter treats it, and this matters.** Ch.5 uses
it as the reason not to read the null as absence (`06_results.tex:223-225`), and FACT_GATE_v3
confirmed only that F50 *says* it (`FACT_GATE_v3.md:324`), not that it holds. Two problems:

- **The `−16.16` it rests on is a *region* Acc@10 delta, not a category one.** The compensation
  story explains why *region* was unmoved. The chapter deploys it to protect a *category*
  attribution. `F50:106` is explicit that it reconciles "F49 architectural Δ at FL = −16.16 pp;
  live P1 ≈ H3-alt at Δ = **−0.21 pp**" — the region number.
- **`−16.16` is arithmetically dependent on a value the repo has since marked invalid.** It is
  `frozen-cat λ=0 (64.22)` minus `STL F21c (82.44)` — confirmed in
  `docs/results/paired_tests/FL_layer3_after_f37.json`, `frozen_vs_stl_f21c_top10.delta_mean_pp =
  -16.156`. And `F50_T4_PRIOR_RUNS_VALIDITY.md:45` rates that very comparand: "**F37 STL B5
  (`82.44`)** … ❌ inflated; true ceiling ~66 (estimated; clean run queued)". I found no leak-free
  recomputation of `−16.16` in the repo. The frozen arm is also unstable: `F49:275` FL frozen-cat
  `64.22 ± **12.03**`, and `F49:288` "3 of 5 folds picked very early epochs".

**Net.** F50's null is genuinely weak evidence against the trunk, for the reasons Ch.5 gives. But
the compensation counter-argument is also weak, and it is the wrong task. Neither should carry much
weight — which is fine, because control C settles the question on the shipped configuration.

---

## 3 · The cascade control — support or undercut?

**It undercuts the claim that the shared trunk carries the category gain, on the shipped
configuration, at four datasets.**

Chain of facts, each sourced:

1. Ch.5 already tells the reader the cascade removes the trunk. `05_setup.tex:167`: "we **remove
   the shared trunk**, where the two streams exchange information, and feed the predicted category
   forward into the region pathway, keeping the representation, outputs, and training configuration
   unchanged."
2. The removal is real and verified three ways (`CSLSL_CASCADE.md:59-92`), and the code confirms the
   category path is trunk-free (`model.py:64-65`).
3. The added cat→region edge is **region-side and detached** (`head.py:456-457`), so the category
   head gains nothing to compensate with. This is the cleanest feature of the control: unlike F50,
   there is no plausible compensation channel *into the category head*.
4. Category does not move: `+0.20 / +0.20 / +0.01 / −0.20` (`CSLSL_CASCADE.md:27-30`), and
   [COMPUTED] neither AL nor AZ separates from zero in the right direction — both point estimates
   are positive.
5. The trunk-free model retains `+7.58 / +6.50 / +4.68` over the same single-task comparand against
   which W6's `+7.63 / +6.54 / +4.64` was called "the shared trunk" [COMPUTED].

**Read together, W6 and the cascade eliminate the same explanation from opposite sides.** Freezing
the region stream keeps the full gain; severing the trunk keeps the full gain. What both leave
standing is the **category stream's own encoder plus the added depth of the joint model** — exactly
the residue Ch.5 named at `06_results.tex:205-207` and declined to choose among. The cascade removes
one of those candidates, and it is the one the author wants to name.

**Limits of the cascade as a trunk control** (state these; they bound the claim, they do not
overturn it):
- Seed 0 only, 5 folds, at each of AL/AZ/FL/Istanbul (`CSLSL_CASCADE.md:3`, "n=5 provisional").
- Not a pure trunk ablation: it *also* adds the directed edge. A clean `disable_cross_attn`-only arm
  on the shipped substrate does not exist in the record (I checked
  `docs/results/closing_data/**`: the only `disable_cross_attn` runs are the cascade cells).
  The added edge is region-side, so the category conclusion is unaffected; a region-side conclusion
  would need the clean arm.
- FL and Istanbul champion-G comparands are cross-device / cross-config (`CSLSL_CASCADE.md:29-30`,
  `:37-39`). AL and AZ are same-device and are the ones to quote.
- The cascade was tuned for the parallel model (`06_results.tex:379-380`). That biases *against* the
  cascade, which makes "category unchanged" conservative.

---

## 4 · The frozen-region-pathway control — what it rules out, what it does not establish

**Rules OUT:** that the next-region task's *training signal* teaches the next-category task. With
the region stream fixed at initialization and the region loss off, the full category lift survives
at AL/AZ/FL (`W6:22-24`). Ch.5 states this correctly at `06_results.tex:203-204`, and Ch.6 at
`6_conclusion.tex:197-198`. This negative result is sound and is the chapter's real mechanism
finding. Corroborated at 4 seeds by control F (`cat_transfer_and_T53.md:21-22`).

**Does NOT establish:** which component produces the gain. `06_results.tex:205-207`: "freezing the
region stream removes region training, not the category stream's own encoder, the per-stream
feed-forward blocks, or the added depth." Also does not establish anything about the region task —
`W6:41` notes the region metric is meaningless in this arm ("reg frozen + loss off").

**Three further limits on its footing:** n=5, seed 0 only (`W6:54`); the dropout-in-frozen-stream
defect (`W6:64`); and the comparand is the Table 2 single-task value, not the Table 3 tuned ceiling
(`W6:52-53`). Ch.5 discloses all three (`06_results.tex:199-203`, `:279-282`).

**Bluntly: W6 is a disjunction eliminator, not a locator — and its own title, verdict banner and
"For the paper" section all call it a locator.** The chapter is more honest than its source.

---

## 5 · Bottom line

**(b) — a weaker but still positive claim, and only for the category clause.**

### 5.A The author's sentence, as worded, is NOT supported

*"the shared trunk carries the semantic context that lifts the next-category task"* asserts the
trunk is the causal locus. The record's only shipped-configuration test of that component — the
cascade — shows the category gain **survives the trunk's removal intact** at four datasets
(§1.C, §3). The strong claim is not merely unproven; the best available evidence points against it.

The author's premise — *"com os estudos atuais comprovamos que o mecanismo dentro do shared model de
fato participam na melhora"* — is half right. The **joint architecture** demonstrably participates:
that is controls A, B, C and F together, and it is a real, defensible, non-trivial result. What no
study shows is that the participating part is the **shared trunk**. Two studies now say it is not.

### 5.B What the evidence does support

Three claims, each with a test behind it:

1. **The gain is not cross-task transfer.** Freeze-region, AL/AZ/FL, seed 0 × 5f: category retains
   `+7.63 / +6.54 / +4.64` over the single-task score of the same fixed configuration
   (`W6:22-24`). Corroborated at 4 seeds, AL/FL: architecture `+3.22 / +2.27`, region-transfer
   `−0.67 / +0.93` (`cat_transfer_and_T53.md:21-22`).
2. **The gain is not parameter count.** Capacity-matched dedicated model at the joint model's
   budget: AL `56.16` vs ceiling `56.82 ±0.03` vs joint `64.51 ±0.09`; CA `69.88 ±0.26` vs
   `70.60 ±0.07` vs `77.05 ±0.01` (`capacity_matched_stl_cat/README.md:54-55`). Post-submission;
   Ch.6 only.
3. **The gain does not require the shared trunk.** Cascade, AL/AZ/FL/Istanbul, seed 0 × 5f:
   Δcat `+0.20 / +0.20 / +0.01 / −0.20` (`CSLSL_CASCADE.md:27-30`); AL/AZ paired 90% CIs
   [−0.08, +0.48] and [+0.08, +0.31] [COMPUTED].

### 5.C Proposed wording — strongest the evidence supports

**Option 1 (recommended) — positive, scoped, no component named.** Keeps everything the author
wants except the word "trunk"; requires no new experiment; every clause has a test.

> One model serves both tasks. The category gain is a property of the joint architecture rather than
> of cross-task transfer: with the region pathway fixed at its initial values the full gain survives
> at Alabama, Arizona, and Florida, and a dedicated model given the joint model's parameter budget
> recovers none of it at Alabama and California. Which component produces the gain remains open;
> rewiring the model as a cascade, which removes the shared trunk, leaves next-category macro-F1
> unchanged at four datasets, so the shared trunk is not by itself the source.

Evidence per clause: 1 → `W6:22-24` (n=5, seed 0). 2 → `capacity_matched_stl_cat/README.md:54-55`
(n=20, post-submission, Ch.6 only). 3 → `CSLSL_CASCADE.md:27-30` + [COMPUTED] CIs.

**Option 2 — minimal edit to the live text.** Keep `06_results.tex` and `07_discussion.tex` as they
stand and add one sentence to the results paragraph:

> Rewiring the model as a cascade removes the shared trunk and leaves next-category macro-F1
> unchanged at Alabama, Arizona, Florida, and Istanbul, which is further reason not to name the
> trunk as the source.

This costs nothing, is internally consistent with `05_setup.tex:167`, and converts the current
refusal from "we cannot tell" into "we tested it and it is not that" — a stronger and more
defensible position at the defence.

**Option 3 — what would license the author's original sentence.** A clean `disable_cross_attn`-only
arm (no cascade edge) on the shipped `check2hgi_dk_ovl` substrate, seeds {0,1,7,100} × 5 folds, at
AL + FL, with the paired test against champion-G. Cost is small: the flag exists, the harness exists,
and the cascade runs took roughly 25 min/state on the A40. **Given the cascade result, the expected
outcome is a null**, i.e. it would confirm the trunk is not the locus. The honest framing is that
this experiment would *settle* the question, not that it would rescue the sentence.

### 5.D What is NOT supported at all: the region clause

*"the private spatial path keeps the next-region task competitive"* has **no isolating control in the
record.** I searched for a fusion/aux/private-tower ablation on the shipped configuration and found
none. What exists is development-era, on a different substrate and different heads:
`docs/studies/archive/mtl_improvement/CHAMPION.md:34` asserts "The private tower carries reg almost
entirely (the `private_only` variant alone clears the ceiling)" — an internal study note, not a
Ch.5-licensed control, and `docs/findings/B9_STL_STAN_SWAP_AZ_FL.md:127` records the related thin
residual-skip variant as falsified (`−0.59`).

This clause is currently asserted in **three live places** (§6, defect P-2) and is the weakest link
in the mechanism story. It is architecturally *descriptive* (the path exists and only region uses
it — `04_method.tex:31`), and Ch.5's own comment at `07_discussion.tex:22` defends it on exactly
that ground: "it is architectural, not an attribution of the gain." That defence works for
`07_discussion.tex:14-15`, which says the region output "keep[s] a private spatial path". It does
**not** work for `01_introduction.tex:36` and `08_conclusion.tex:14`, where the path is given a
causal role in the outcome.

---

## 6 · Pre-existing defects — mechanism attributions the evidence does not support

| id | Location | Text | Problem | Severity |
|---|---|---|---|---|
| **P-1** | `docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md:3-4`, `:57-61` | "**The joint CATEGORY win is the shared TRUNK (architecture/capacity)**"; "Use as the encoder-isolation evidence"; verdict column reads `**trunk** ✅` | The experiment cannot separate the trunk from the category encoder / FFNs / depth. Its own §1 concedes the alternatives exist, then the banner drops them. Ch.5 is more careful than its source. Internal record only, but it is what a reader (or a future agent) meets first — and the cascade now contradicts it | **High** (internal) |
| **P-2** | `src/chapters/5_mobiwac/01_introduction.tex:36` and `08_conclusion.tex:14` | "sharing semantic context across tasks while keeping a private spatial path for the region task"; "One model with a shared semantic context and a private spatial path anticipates both what a user will do next and where" | Mechanism framing in **live chapter prose**, with no control isolating either component. `07_discussion.tex:22` justifies the private-path mention as "architectural, not an attribution" — that defence does not cover the conclusion sentence, which ties both components to the outcome | **High** (live prose, both trees) |
| **P-3** | `articles/[mobiwac]/src/sections/06_results.tex:105` | "The control fixes region training rather than any part of the category pathway, so it does not identify which part of the joint architecture produces the gain, and we do not name the shared trunk as the source." | Correct as far as it goes, but the **article tree omits the F50 disclosure that the dissertation tree carries** (`5_mobiwac/06_results.tex:209-226`). The two trees are supposed to be paired under the under-review regime (`07_discussion.tex:62-63`). Asymmetric disclosure | **Medium** |
| **P-4** | `../../../science/storyline/README.md (seccao `06_answer_and_mechanism/answer_and_mechanism.md`):20`, `:29-31` | "A stronger shared trunk, not the region task teaching the category one."; "**What remains — the shared trunk**: cross-attention stack … builds a representation the dedicated model cannot reach at any width tried" | The planning document still carries the attribution the chapters retracted in round 5/6. It is the source Ch.6 §6.2 was drafted from, so it is a live re-contamination risk for any future drafting pass | **High** (drafting source) |
| **P-5** | `../../../science/storyline/audit/capacity_baseline_experiment.md:146-149` | "(3) what remains, and what the paper already asserts as its finding, is the shared trunk" | Same defect, in the experiment's own design record. Note this file *also* contains the correct warning at `:12-19` that the trunk answer "is NOT defensible as stated" — the document argues against itself | **Medium** |
| **P-6** | `articles/dissertacao/src_utils/_history/_specialists_v2/BANCA_v2.md:472-476`, `BANCA_v3.md:647` | "for the category task the mechanism is a stronger shared trunk, which is a weaker and more interesting claim than transfer" — offered as the recommended defence line | The rehearsal document coaches the candidate into the unsupported attribution. BANCA_v3 elsewhere endorses the chapter's refusal (`:629-642`), so the document is internally inconsistent on the single question most likely to be asked | **High** (defence prep) |
| **P-7** | `docs/CLAIMS_AND_HYPOTHESES.md:3` | "the cat beat is **architecture-dominated** … isolates the cross-attn shared trunk" | Same conflation of "architecture" with "trunk". The underlying study (`cat_transfer_and_T53.md:41`) words it correctly as "architecture-dominated"; the claims ledger upgrades it to the trunk | **Medium** |
| **P-8** | `docs/results/closing_data/MACS_BOARD_RESULTS.md:47` | "HMT reg clears the Markov floor" | Already flagged in-chapter at `06_results.tex:367-371` as inherited and stale (held against the old non-overlap floor AL `0.4701`, not the shipped stride-1 floor AL `0.6226`). Not a mechanism claim; listed for completeness since the note asks for a correction the record never made | **Low** (internal) |
| **P-9** | `docs/findings/archive/F50/F50_T1_5_CROSSATTN_ABSORPTION.md:110-116` | the `−16.16 + 15.95 ≈ 0` compensation arithmetic | Rests on `STL F21c 82.44`, which `F50_T4_PRIOR_RUNS_VALIDITY.md:45` marks "❌ inflated; true ceiling ~66". No leak-free recomputation found. Ch.5 leans on this arithmetic's *conclusion* (`06_results.tex:223-225`) without inheriting its invalidated basis | **Medium** |

### Not defects — checked and clean

- `5_mobiwac/06_results.tex:194-226` and `07_discussion.tex:12-18`: the current agnostic wording is
  accurate to the evidence and correctly scoped. The F50 numbers, the `±0.3` basis, the n=5 footing
  and the Table 2 vs Table 3 comparand are all handled correctly.
- `6_conclusion.tex:185-231`: Ch.6's mechanism section is the best-calibrated prose in the
  dissertation on this question. `:208-209` — "The available evidence supports attributing the
  category gain to the joint architecture as a whole, not to one component" — is exactly right, and
  the cascade finding strengthens rather than threatens it.
- `apx_f_cosine.tex:472-477`: the orthogonality appendix correctly declines a mechanism reading
  ("No mechanism is …", `:434`) and explicitly scopes what the measurement does not read.

---

## 7 · Recommendation

1. **Do not restore the sentence.** The category clause is contradicted by the cascade on the
   shipped configuration; the region clause has no control at all.
2. **Adopt Option 2** (one added sentence). It is a small edit, it strengthens the chapter, and it
   makes Ch.5 consistent with its own §5.3 description of the cascade. Under the under-review
   regime it needs the paired edit in `articles/[mobiwac]/src/sections/06_results.tex` and an
   errata row.
3. **Fix P-2 first** — it is live prose in both trees and the only *high*-severity defect a referee
   or examiner reads directly.
4. **Correct P-1, P-4, P-6** before the defence. P-6 in particular would put the candidate on
   record asserting a claim his own chapter refuses and his own cascade data contradicts.
5. **If a run is affordable**, Option 3 (clean trunk-ablation, 4 seeds, AL + FL) closes the question
   permanently. Expect a null, and pre-register that reading — per the licensing discipline already
   established in `capacity_baseline_experiment.md:42-63`.

### Audit provenance

Files read in full: `W6_ENCODER_ISOLATION.md`, `CSLSL_CASCADE.md`, `CSLSL_CASCADE_RESULTS.md`,
`F50_T1_5_CROSSATTN_ABSORPTION.md`, `F49_LAMBDA0_DECOMPOSITION_RESULTS.md` (§§1-3, 10, 13-14),
`capacity_matched_stl_cat/README.md`, `capacity_baseline_experiment.md`, `answer_and_mechanism.md`,
`cat_transfer_and_T53.md`, `F50_T4_PRIOR_RUNS_VALIDITY.md`, `5_mobiwac/{05_setup,06_results,07_discussion,
01_introduction,04_method,08_conclusion}.tex`, `6_conclusion.tex` (§6.2), `apx_f_cosine.tex`
(mechanism section), `[mobiwac]/src/sections/{06_results,07_discussion}.tex`, `ch5_errata_rows.md`,
`FACT_GATE_v2.md`, `FACT_GATE_v3.md`, `BANCA_v2.md`, `BANCA_v3.md`. Code verified:
`mtlnet_crossattn_dualtower/model.py:64-65,97-130`, `next_stan_flow_dualtower/head.py:291-312,456-457`,
`configs/canon.py:45-60`.

Computed this session (marked `[COMPUTED]`; nothing else was recomputed): paired Wilcoxon, paired
*t*, mean difference and 90% CI of cascade − champion-G on `cat_per_fold` and `reg_per_fold` from
`docs/results/closing_data/a40/{al,az}_{cascade,champG_a40}_s0.json`; and the cascade-minus-single-task
deltas against the `W6:22-24` comparand column. Method matches the chapter's own convention (paired
over folds, 90% interval), but n=5 at seed 0 — these are **not** n=20 chapter-grade statistics and
must not be quoted as such.

**[VERIFY] flags for the author.**
- **V-1.** The cascade↔W6 pairing crosses two epoch-selection conventions (f1-best vs
  diagnostic-best). Residuals ≤0.05 pp, far below fold-std, but confirm before any sentence quotes
  the two side by side. `AGENT_GUARDRAILS` N5 applies.
- **V-2.** No leak-free recomputation of F49's `−16.16` was found. If the compensation argument is
  kept in prose, it should be re-derived or explicitly time-indexed.
- **V-3.** The Istanbul cascade cell runs on the v17 substrate against an H3 comparand
  (`CSLSL_CASCADE.md:30`); FL's comparand is cross-device (`:29`). Quote AL/AZ for anything paired.
- **V-4.** I found no private-spatial-path ablation on the shipped configuration. If one exists
  outside `docs/`, §5.D changes.
