# Trunk-ablation triage at the four states that beat the region ceiling

> **Copied into the repo 2026-08-07.** These runs were made 2026-08-05/06 and lived at
> `/home/vitor.oliveira/region_1fold/` — **outside the repository**, which is why a repo-wide search
> for trunk ablations found nothing and an audit concluded (wrongly) that CA/TX had never been
> ablated. They are the **only** trunk-ablation evidence that exists at california and texas.
> Preserved here so they cannot be lost again.

## Arms

Byte-identical to the champion joint cell except for the stated flag. Engine `check2hgi_dk_ovl`
(**v17, the leaked substrate**), seed 0, `--only-fold 0`.

| arm | flag | what it removes |
|---|---|---|
| `baseline` | — | nothing |
| `rg1` | `--model-param disable_cross_attn=True` | the shared trunk: two fully independent towers |
| `rg2` | `disable_cross_attn=True --category-weight 0.0` | the trunk **and** all category supervision |

`rg2` is the sharp control: with category weight 0 the model is effectively a **dedicated region
model running through the joint pathway**.

## Results (region = `top10_acc_indist · (1 − ood_fraction) · 100`)

| state | baseline | rg1 (trunk severed) | Δ | rg2 (+ no category task) | Δ | cat @ rg2 |
|---|---:|---:|---:|---:|---:|---:|
| istanbul | 76.7195 | 76.6293 | −0.090 | 76.5814 | −0.138 | 9.31 |
| florida | 77.6377 | 77.6110 | −0.027 | 77.5498 | −0.088 | 14.12 |
| **california** | **65.4044** | **65.3051** | **−0.099** | **65.3276** | **−0.077** | 8.95 |
| **texas** | **66.9797** | **66.8600** | **−0.120** | *(not run)* | | |

Category collapses to 9–14 under `rg2`, confirming the category task really was switched off.

## What it shows

**At california and texas the ~+2 pp region advantage survives severing the trunk AND deleting the
category task entirely** — region moves by less than 0.15 pp in every arm. Whatever produces that
advantage, it is **not cross-task sharing**. The remaining candidates are architectural: the
`next_stan_flow_dualtower` head with `fusion_mode=aux`, and a region pathway carrying **2.5–5.9×**
the dedicated baseline's parameters (alabama 2,466,542 vs 417,117; california 3,420,110 vs
1,370,685 — counts reproduced independently on CPU).

This is consistent with, and much stronger than, the earlier FL-only ablations (F50 P1, F52 P5) and
the CSLSL cascade, all of which also found trunk severance ≈ free.

## Limits — stated by the driver itself

`run_1f.sh` is explicit that this is **a screen, not a measurement**:

> "One fold gives ONE number per arm — no dispersion, no paired test, no interval — so it can only
> detect a LARGE effect. … if rg2 collapses toward the region ceiling (a several-point drop), one
> fold shows it unambiguously and the conclusion is settled early. If the arms land within a few
> tenths of each other, that is NOT a null result — it is an inconclusive screen."

So: the arms *did* land within a few tenths, which by that rule is **inconclusive for a small
effect**. But the test had power for the hypothesis actually at stake — "the trunk carries the +2 pp"
predicts a several-point collapse under `rg2`, and no collapse occurred. The trunk-causation reading
is therefore **disfavoured by a test that could have detected it**, while a sub-0.15 pp trunk
contribution remains unresolved.

Two further caveats: the substrate is the **leaked** `dk_ovl`, and the recipe is the pre-retune one.
Neither should matter much for the region axis (region is leak-immune — its v17→v18 shift is
≤0.16 pp) but both should be stated when citing these numbers.

## Why this matters for what comes next

- It removes "does the trunk **carry** the CA/TX win?" from the priority list — that specific
  hypothesis is refuted by a test with power for it. It does **not** answer "does the trunk
  contribute anything at CA/TX?", which stays unmeasured: one fold cannot resolve a sub-0.15 pp
  effect, and no 5-fold ablation exists at those states.
- It sharpens the remaining open question to **small data**: at alabama the joint model is *worse*
  than dedicated on both heads (Δcat −0.65/−1.04, Δreg −0.31/−0.33) while the dedicated model
  overfits badly (train macro-F1 66.4 vs val 24.0). Was the trunk **actively harmful** there?
  **Answered 2026-08-07, no:** 5-fold arms at alabama give Δcat −0.015 (T1, `disable_cross_attn`) /
  −0.154 (T2, `identity_cross_attn`) and Δreg −0.138 / −0.004 — inside fold-σ (~1.7 cat, ~3.0 reg).
  The trunk is inert at alabama, neither helpful nor harmful. That is a **one-state** result and does
  not transfer to CA/TX, where only this 1-fold screen exists.
- It reframes the dissertation's region claim: the joint model's region advantage should be
  attributed to the **dual-tower architecture and its capacity**, not to multi-task transfer,
  unless a capacity-matched control says otherwise. That control was computed but never run
  (`d_model=480` AL, `352` CA).
