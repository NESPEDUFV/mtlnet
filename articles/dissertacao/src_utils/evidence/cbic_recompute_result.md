> **RESOLVED — author ruling 2026-07-24 (supersedes the recommendation below).**
> Ch.3 now reports the Florida figures of record from the CoUrb dataset table:
> **20,301 users / 65,009 POIs / 990,518 check-ins**. The author confirmed that the
> `data/output/florida_dgi.zip::filtrado.csv` artifact analysed below (10,460 / 64,454 / 960,520)
> is from a PRIOR ETL that is no longer in use, so it must not be the source. Since the CBIC
> paper never published these three statistics, no published value is overridden, and using the
> current-pipeline Florida figures keeps Ch.3 consistent with the same corpus in Ch.4. The
> `[VERIFY]` flag is cleared. The analysis below is retained for provenance — it records the
> alternatives that were weighed (fresh-ETL raw, fresh-ETL <5-filtered, and the abandoned
> `filtrado.csv`) and why the N_users question could not be settled from committed artifacts alone.

---

# CBIC Florida dataset recompute — `3_cbic.tex:235` [VERIFY] placeholders

**Task:** produce `N_users`, `N_poi`, `N_checkins` for the CBIC-era Florida subset of Gowalla,
to replace the three `[VERIFY]` placeholders in the sentence
*"This subset comprises a total of [N_users] users, [N_poi] unique Points-of-Interest (POIs),
and [N_checkins] check-ins."* (`articles/dissertacao/src/chapters/3_cbic.tex:235`).

**Verdict:** `[VERIFY-still-needed]` — author sign-off required. Source-backed numbers recommended
below, but one of the three (`N_users`) has a ~2x disagreement between the two repo sources that I
cannot resolve without the author. See §5.

---

## 1. The convention (what "the subset" means)

From `articles/CBIC___MTL/sections/method.tex:44` (trajectory building for the next-POI task):

> "Check-ins (user, POI, timestamp) are ordered chronologically per user; users with fewer than
> five visits are discarded."

and `method.tex:45`: non-overlapping windows of length `L_h = 9`.

I traced this to the committed code. The `<5-visit` rule lives in
`src/data/inputs/core.py::generate_sequences` (line 250):

```python
MIN_SEQUENCE_LENGTH = 5              # core.py:21
...
if not places_visited or len(places_visited) < min_sequence_length:
    return []                        # user dropped
```

`places_visited` is the per-user chronological list of **check-in rows** (built by
`groupby('userid')['placeid']` in `src/data/inputs/builders.py:261`). So **"fewer than five visits"
= fewer than five check-in rows per user**, not fewer than five distinct POIs. Window size 9
matches `method.tex:45`.

**Source of record for these counts:** the ETL is `pipelines/etl/gowalla.pipe.py` →
`src/etl/gowalla/{stage_1,stage_2,stage_3}.py` (author-confirmed same pipeline). Only two ETL
operations change the row set:
- **stage_1** (`label_categories`): dedup on `(userid, placeid, datetime)`, inner-merge check-ins
  to the POI/category tables, then **drop rows whose category does not map** (`dropna(['category'])`).
- **stage_3** (`checking_states`): spatial join of every check-in to the TIGER-2022 US-state
  polygons; keep the rows that fall inside Florida.

stage_2 (timezone `local_datetime`) drops only invalid `lat/lon` and is **not consumed** by
stage_3, so it cannot change the Florida set. I reproduced stage_1 -> (coord filter) -> stage_3
verbatim from the repo code; the timezone shapefile was not needed.

---

## 2. The three number sets

| source | basis | N_users | N_poi | N_checkins |
|---|---|---:|---:|---:|
| **`filtrado.csv`** (CBIC-era DGI Florida input) | working subset the CBIC models consumed | **10,460** | **64,454** | **960,520** |
| fresh ETL (current repo code + TIGER-2022), raw | today's pipeline, pre-`<5` filter | 21,052 | 76,544 | 1,407,034 |
| fresh ETL (current repo code + TIGER-2022), `<5` filtered | today's pipeline, post-`<5` filter | 13,935 | 76,266 | 1,392,262 |
| **CoUrb published** (`tabela_dataset.tex`) — *cross-check only* | — | 20,301 | 65,009 | 990,518 |

`filtrado.csv` = `data/output/florida_dgi.zip :: florida_test/filtrado.csv` (dated 2025-05-06;
228 MB; every row `state_name = Florida`, `category` already assigned). It is the file the CBIC-era
DGI embedding pipeline actually read (its sibling `pre-processing/poi-sequences.csv` holds the
21,338 length-9 sequences fed to the model). `N_checkins` is the table's row count (960,520);
distinct `(user, POI, timestamp)` triples = 959,693 (827 exact-duplicate rows).

---

## 3. Why the fresh ETL does NOT match (and why `filtrado.csv` is the right source)

Re-running the current ETL over-counts. I checked set membership: **`filtrado.csv` is a strict
subset of the fresh ETL Florida output** —

- 100.0% of `filtrado`'s 64,454 POIs are in the fresh ETL (which adds 12,090 more);
- 100.0% of `filtrado`'s 10,460 users are in the fresh ETL (which adds 10,592 more);
- 100.0% of `filtrado`'s 959,693 check-ins are in the fresh ETL (which adds 447,341 more).

**Root cause: category-mapping drift.** The extra ETL-only POIs skew hard toward Entertainment
(21.1% of ETL-only POIs vs 5.2% of CBIC-era POIs), Outdoors and Travel — i.e. categories that were
newly mapped. The mapping files `data/gowalla/callback_categories.json` and
`extra_categories.json` were last modified **2026-04-14**, ~11 months *after* the CBIC-era Florida
extraction (`filtrado.csv`, 2025-05-06). stage_1 drops rows whose category does not map, so the
expanded 2026 mapping keeps ~418k more check-ins / 12k more POIs / 10.6k more users that the
CBIC-era run discarded. **The current code therefore cannot reproduce the CBIC-era counts**; the
committed CBIC-era artifact (`filtrado.csv`) is the faithful record and is what I recommend.

---

## 4. CoUrb cross-check (NOT a source — CBIC `ERRATA.md`)

CoUrb documents the *identical* filter (`src_en/sections/metodology.tex:45`: "users with fewer than
five visits are discarded", `L_h = 9`) and publishes a Florida row of **990,518 check-ins /
65,009 POIs / 20,301 users** (`src_en/resultados/tabela_dataset.tex`, caption "Total number of
check-ins, POIs, and users").

- **N_poi:** `filtrado` 64,454 vs CoUrb 65,009 -> **+0.9%. Agreement.**
- **N_checkins:** `filtrado` 960,520 vs CoUrb 990,518 -> **+3.1%. Agreement** (within-era pipeline drift).
- **N_users:** `filtrado` 10,460 vs CoUrb 20,301 -> **~2x. DISAGREEMENT — unresolved.** See §5.

Two of three CBIC-era numbers are corroborated by CoUrb to within a few percent. The check-in and
POI recomputes are therefore in a sane range of the cross-check.

---

## 5. The open question the author must decide (N_users)

The `<5-visit` filter is **not** the source of the 10,460-vs-20,301 gap: applying `>=5` to
`filtrado.csv` drops only **279** of its 10,460 users. So `filtrado.csv` is essentially the
CBIC-era Florida population *after category assignment* and *before* the `<5` trajectory filter.

The ~2x user gap comes from a filtering/convention difference between the CBIC-era run (2025) and
CoUrb (2026) that I **cannot fully reconstruct from committed artifacts**. Candidate explanations
(none confirmable from the repo this session): CoUrb ran with the expanded 2026 category mapping
(its user count 20,301 ~ fresh-ETL-raw 21,052), while `filtrado` used the older mapping; and/or the
two runs counted the user population at different pipeline stages. This is the fail-closed boundary:
I will not invent the resolving convention.

**Editorial hazard:** if Ch.3 (CBIC) reports 10,460 users and Ch.5-adjacent CoUrb material reports
20,301 for "the same" Florida, an examiner will see a contradiction. The author needs to choose and
document the convention, or time-index it per chapter.

**Recommendation (do not insert without sign-off):** the prose "This subset comprises ..." most
naturally denotes the working data the CBIC models actually consumed, which is `filtrado.csv`:

- **N_users = 10,460**  *(flagged: CoUrb reports 20,301; reconcile or time-index before final)*
- **N_poi = 64,454**  *(corroborated by CoUrb 65,009)*
- **N_checkins = 960,520**  *(corroborated by CoUrb 990,518; 959,693 distinct triples)*

If the author prefers the raw pre-`<5` population under the *current* pipeline, use the fresh-ETL-raw
row (21,052 / 76,544 / 1,407,034) — but that reflects the 2026 mapping, not CBIC-era, so it is not
recommended for a CBIC chapter.

---

## 6. Method / reproducibility ledger

- **Env:** conda `geo` (python 3.13, geopandas, pyarrow, pandas, shapely, tqdm).
- **Shapefile:** `data/miscellaneous/tl_2022_us_state/` fetched from
  `https://www2.census.gov/geo/tiger/TIGER2022/STATE/tl_2022_us_state.zip` (network access granted
  this session). ESRI Shapefile, Polygon, verified.
- **ETL run:** `src/etl/gowalla/stage_1.label_categories()` (36,001,959 raw -> 43,599 dupes removed
  -> 35,958,080 after POI merge -> 35,620,879 after category drop) -> coord filter (32 rows) ->
  `stage_3.checking_states()` spatial join (51.22% of check-ins matched to US states). The full-US
  stage-3 result is `data/temp/gowalla/stage3_states.parquet` (779 MB); Florida read back via
  predicate pushdown `state_name == 'Florida'` = 1,407,034 rows.
- **CBIC-era source:** `data/output/florida_dgi.zip :: florida_test/filtrado.csv`, read directly
  from the zip (no extraction).
- **Evidence artifact:** `florida_etl_stage3_slice.parquet` (the fresh-ETL Florida slice,
  1,407,034 rows x 4 cols) saved for audit.
- **Numbers are computed, not typed:** every count above is `nunique()` / `len()` / `groupby().size()`
  over the named file. CoUrb values are copied verbatim from `tabela_dataset.tex`.

## 7. `[VERIFY]` flags still open

1. **N_users basis** — 10,460 (filtrado, CBIC-era) vs 20,301 (CoUrb). Author to pick the convention
   and confirm it is consistent across chapters.
2. **raw vs filtered** — recommended numbers are the CBIC-era working subset (`filtrado`, ~pre-`<5`);
   confirm this is what "This subset comprises" should report.
3. The current ETL code cannot regenerate the CBIC-era counts (category-mapping drift, §3); the
   recommendation rests on the committed `filtrado.csv` artifact, not a fresh code run.
