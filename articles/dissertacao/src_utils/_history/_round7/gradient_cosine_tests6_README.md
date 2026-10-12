# gradient_cosine_tests6.csv -- the FOLD is the unit; read this before quoting any p-value

Derived by `src_utils/_history/_round7/cosine_stats6.py` (RC=0, 2026-07-30) from
`gradient_cosine_observations6.parquet`, 4,650 rows over SEVEN datasets. It supersedes
`gradient_cosine_tests.csv`, which covers the four-dataset appendix and is kept because it is the
record of what the published text was derived from.

## SEVEN datasets, not six

The dissertation's **six** are alabama, arizona, california, florida, istanbul and texas.
**Georgia is a seventh** and is NOT one of them: it is a further Gowalla state that entered because
the diagnostic ran on it cheaply, and `tables/mobiwac/datasets.tex` lists AL, AZ, FL, TX, CA and
Istanbul with no Georgia. Any sentence that says "six datasets" about this file is wrong in one
direction and any sentence that implies Georgia is one of the six is wrong in the other.

## One row per dataset, and the unit is the fold

There is exactly one row per dataset, at the fold unit, because that is the only unit the protocol
defines as independent. The 50 per-epoch cosines inside a fold are consecutive states of ONE
training trajectory: they are serially dependent, and a test that treats 250 of them as
independent draws is ANTI-CONSERVATIVE -- its p-value is smaller than the evidence supports.
Treating the epoch as the unit was a defect corrected in round 7; this file does not carry
observation-level p-values at all, so they cannot be quoted by accident. `cosine_stats6.py` still
prints them, labelled `SERIALLY DEPENDENT`, only to show the equivalence conclusion does not
depend on the choice.

- `n` = the number of independent units. **5** for six of the seven datasets (five folds);
  **60** for Florida (twelve configurations over the same five folds).
- `n_observations` = 250, or 3,150 for Florida. It **describes the data** and is not any test's
  sample size.
- Florida's twelve configurations reuse the same five folds, so its 60 fold series are not mutually
  independent either. The more conservative configuration-mean reading (n=12) gives the same mean,
  +0.00026, and TOST p = 1.28e-16. Both readings are equivalent to zero.

## The sign test cannot reach 0.05 at n=5, and three rows need that said

`sign_p_floor_at_this_n` is the smallest p the two-sided exact sign test could return at that n if
every value agreed in direction. **At n=5 the floor is 0.0625**, so no five-fold dataset can support
a significance claim about the sign of its mean, however consistent the pattern. At n=60 there is no
such limit.

Three rows have a t-test below the conventional threshold and none of them is a significant result:

| dataset | fold means positive | t p | sign p | how to report it |
|---|---|---|---|---|
| alabama | 5/5 | 0.0125 | 0.0625 = **the floor** | a consistent positive tendency on five folds |
| georgia | 5/5 | 0.0093 | 0.0625 = **the floor** | a consistent positive tendency on five folds |
| california | 4/5 | 0.0478 | **0.3750** | not even a leaning by the distribution-free test |

California is the instructive one. Its t-test crosses 0.05 while its sign test returns 0.375, so a
reader given only the t-test would see a significant positive alignment that the sign test does not
support at all. It carries no dagger in the table because 0.375 is not the floor: this is the
normality assumption doing the work, not the sample size.

**Texas: mean -0.00026 with 4 of 5 fold means POSITIVE.** Not a typo. One fold at -0.00322 outweighs
four small positive ones. This is why `n_positive` is a column rather than something to infer from
the sign of the mean.

## What survives, and what does not

**ROBUST.** Equivalence to zero within +/-0.05 by TOST holds at **every one of the seven datasets
and at every level of aggregation**, with governing p-values from 5.8e-05 (alabama) to 4.5e-62
(florida). This is the appendix's claim and it does not depend on the dependence question, on the
choice of unit, or on normality at small n.

**NOT ROBUST, and not to be upgraded.** Alabama's and Georgia's positive means, California's
t-test, and the downward drift on alabama and georgia. All rest on five folds. Report them as
tendencies; the word "significant" does not belong to any of them.

## Reproducing

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao
python3 src_utils/_history/_round7/cosine_stats6.py    # RC=0; writes this CSV and gradient_cosine_slopes6.json
python3 src_utils/_history/_round7/cosine_stats.py     # RC=0; the four-dataset record, still runs
```
Both assert their own structure before computing anything, so a parquet that has drifted kills the
script rather than producing a plausible number.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
