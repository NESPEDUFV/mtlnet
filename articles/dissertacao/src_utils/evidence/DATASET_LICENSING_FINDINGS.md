# Dataset licensing: findings note (REV-026, ethics gap)

**Prepared** 2026-07-25, references track. **Scope:** evidence only. No dissertation prose was
written and no chapter was edited for this item. Every line below was opened this session; where
a source could not be opened, the line says so.

**What this note is for.** The dissertation currently renders zero sentences on data licensing.
Before any such sentence is written, the two facts below have to be settled, and one of them
carries a discrepancy the author should rule on first.

---

## 1 · Gowalla (Chapters 3, 4, 5)

### 1.1 The source the Chapter 5 pipeline actually consumes

The hidden comment at `src/chapters/5_mobiwac.tex:299-303` records the provenance. It reads, in
part, that the Gowalla source is "the public CC0 category-annotated dump,
figshare.com/articles/dataset/gowalla_data/22126586 (gowalla_checkins + gowalla_spots_subset1/2,
the exact files the ETL consumes; 36,001,959 check-ins)", that the date range was measured on the
parquet on 2026-07-09 as 2009-01-21 to 2011-08-16, and that "The SNAP/cho2011 dump (Feb 2009-Oct
2010) is NOT the data source; cho2011gowalla is cited as the LBSN reference only." The same
Figshare URL is already printed to the reader in the Chapter 5 footnote at
`src/chapters/5_mobiwac.tex:55`.

The comment's file claim checks out against the code: `src/etl/gowalla/main.py:22-24` names
`gowalla_checkins.parquet`, `gowalla_spots_subset1.csv` and `gowalla_spots_subset2.csv`.

### 1.2 What the Figshare record says (VERIFIED)

| Field | Value |
|---|---|
| Record | Gowalla_data, https://figshare.com/articles/dataset/gowalla_data/22126586 |
| DOI | 10.6084/m9.figshare.22126586.v2 |
| Licence | **CC0**, identifier `CC0`, URL https://creativecommons.org/publicdomain/zero/1.0/ |
| Depositor | "Yang" (single name; no ORCID on the record) |
| Published | 2023-02-20 |
| Files | `gowalla_checkins.csv`, `gowalla_spots_subset1.csv`, `gowalla_spots_subset2.csv`, `gowalla_category_structure.json`, `gowalla_friendship.csv`, `gowalla_userinfo.csv` |
| Record's own description | states the data was "downloaded from http://www.yongliu.org/datasets/" and reports 36,001,959 check-ins by 319,063 users over 2,844,076 locations |

Opened at https://api.figshare.com/v2/articles/22126586 (Figshare public API, the record of
record for its own deposits). The CC0 label and the check-in count in the LaTeX comment are
therefore both **confirmed**, and the three consumed filenames appear verbatim in the deposit.

### 1.3 What remains unverifiable, and why it matters

The CC0 label is an assertion made by a **third-party depositor**, not by the party that
collected the data. The record itself says the files were downloaded from another site, and that
upstream site (`www.yongliu.org/datasets/`) returned HTTP 403 to this session, so **its terms
could not be read**. The depositor is identified only as "Yang". Nothing on the Figshare record
establishes that the depositor held the rights to place the data under CC0.

The honest statement available today: *the copy consumed is distributed on Figshare under CC0
(DOI 10.6084/m9.figshare.22126586.v2), a licence applied by the depositor of that copy.* Anything
stronger, in particular any claim that the Gowalla data as such is CC0, is not supported by what
could be opened.

### 1.4 The SNAP discrepancy (REPORTED, not resolved)

`docs/context/DATASETS.md:187-199` records the Gowalla source as **Stanford SNAP**
(https://snap.stanford.edu/data/loc-gowalla.html) and carries **no License row at all**, while
the Chapter 5 ETL consumes the Figshare dump. These are two different artifacts, not two links
to one artifact:

| | SNAP `loc-gowalla` | Figshare 22126586 |
|---|---|---|
| Files | `loc-gowalla_edges.txt.gz`, `loc-gowalla_totalCheckins.txt.gz` | `gowalla_checkins.csv`, `gowalla_spots_subset1/2.csv`, + 3 more |
| Check-ins | 6,442,890 | 36,001,959 (per the record's description) |
| Period stated | Feb 2009 to Oct 2010 | (not stated on the record; the repo measured 2009-01-21 to 2011-08-16 on the parquet) |
| Categories | none | 7 top-level categories (the category annotation the work depends on) |
| Licence | **none stated on the page** (searched for licence, terms, copyright: absent) | CC0 |

SNAP page opened 2026-07-25 at https://snap.stanford.edu/data/loc-gowalla.html. It publishes no
licence or terms-of-use statement of any kind.

Two consequences for the author to rule on:

1. `docs/context/DATASETS.md` documents a source the Chapter 5 pipeline does not read. The
   Chapter 5 comment already flags this ("the SNAP/cho2011 dump is NOT the data source"), so the
   defect is in DATASETS.md, not in the chapter. It is a repo-documentation fix, outside this
   track's edit scope.
2. The bibliography cites `cho2011gowalla` and `jure2014snap` for Gowalla. Per the Chapter 5
   comment those are the LBSN and SNAP references, not the provenance of the consumed files. Any
   licensing sentence must therefore name the Figshare deposit, not SNAP, or it will describe the
   wrong artifact.

---

## 2 · Massive-STEPS / Istanbul (Chapter 5)

### 2.1 What the repo currently records

`docs/context/DATASETS.md:153` gives the License row as "Open-source; academic research". That is
a characterization, not an identified licence: it names no licence, no version, and no URL.

### 2.2 What the dataset records say (VERIFIED)

| Where | Identifier | Licence |
|---|---|---|
| Hugging Face dataset (the distribution) | https://huggingface.co/datasets/CRUISEResearchGroup/Massive-STEPS-Istanbul | **Apache-2.0** (`license: apache-2.0` in the dataset card front matter; repository tag `license:apache-2.0`) |
| GitHub repository | https://github.com/cruiseresearchgroup/Massive-STEPS | **Apache-2.0** (SPDX `Apache-2.0`, `LICENSE` at repository root) |
| Paper | arXiv:2505.11239, Wongso, Xue, Salim | (no licence claim in the record) |

Opened via the Hugging Face datasets API, the raw dataset card, and the GitHub licence API. Note
that `docs/context/DATASETS.md:145` points at `w11wo/Massive-STEPS-*`; that namespace now
redirects to `CRUISEResearchGroup/Massive-STEPS-Istanbul`, which is the same record.

So the licence **is** identifiable, and "Apache-2.0" replaces the current characterization. Two
qualifications belong with it:

1. Apache-2.0 is a software licence applied here to a data release. That is what the distributors
   published; it is not this note's place to interpret its effect on data.
2. Massive-STEPS is derived material. Its README states the dataset "is derived from the
   [Semantic Trails Dataset] and [Foursquare Open Source Places]". Both upstreams were checked:
   Semantic Trails is on Figshare under **CC0** (DOI 10.6084/m9.figshare.7429076.v2), and
   Foursquare Open Source Places is distributed under **apache-2.0** on Hugging Face. The chain
   is therefore consistent, with no upstream term more restrictive than the Massive-STEPS
   licence surfacing in what could be opened.

### 2.3 What remains unverifiable

The Foursquare Open Source Places **product terms** (as distinct from the Hugging Face licence
tag) were not opened; only the Hugging Face record's tag was read. If a licensing sentence needs
to speak to the Foursquare terms specifically, that check is still outstanding.

---

## 3 · Summary for the author

| Dataset | Source actually consumed | Licence verified this session | Identifier / URL | Unverifiable |
|---|---|---|---|---|
| Gowalla (Ch. 3/4/5) | Figshare deposit `gowalla_data` | CC0, applied by the depositor of that copy | 10.6084/m9.figshare.22126586.v2 ; creativecommons.org/publicdomain/zero/1.0/ | Whether the depositor held the rights to apply it; the upstream terms at yongliu.org (403 to this session) |
| Gowalla as documented in DATASETS.md | Stanford SNAP `loc-gowalla` (NOT what the ETL reads) | none: the page states no licence | snap.stanford.edu/data/loc-gowalla.html | n/a; the absence is the finding |
| Massive-STEPS / Istanbul (Ch. 5) | Hugging Face `CRUISEResearchGroup/Massive-STEPS-Istanbul` | Apache-2.0 | huggingface.co/datasets/CRUISEResearchGroup/Massive-STEPS-Istanbul ; github.com/cruiseresearchgroup/Massive-STEPS | Foursquare Open Source Places product terms (only the HF licence tag was read) |

**Open decisions this note does not take:**

1. Whether to correct `docs/context/DATASETS.md` (Gowalla source row plus a missing License row;
   Massive-STEPS License row "Open-source; academic research" to Apache-2.0). Outside this
   track's edit scope.
2. Where a licensing sentence should live (Chapter 5 setup, or a general ethics or data statement
   in the frame), and how it should hedge the Gowalla case. No such prose was drafted.

**Machine-readable evidence:** `src_utils/_history/_archive/handoffs/item4_licence_evidence.json` (same session, same URLs).

---

## 4 · Round 2 (2026-07-27): re-verification, provenance ruling, pipeline facts, prior-dissertation check

**Scope of this round.** Appended when Appendix E (`src/chapters/apx_e_ethics.tex`) was drafted.
Every line below was opened or read this session. Nothing in §1–§3 above was edited.

### 4.1 Licences re-verified at source (all three still hold)

| Record | Re-opened at | Result |
|---|---|---|
| Gowalla Figshare 22126586 | `https://api.figshare.com/v2/articles/22126586` | HTTP 200; `doi` = `10.6084/m9.figshare.22126586.v2`; `license` = `{"value": 2, "name": "CC0", "url": "https://creativecommons.org/publicdomain/zero/1.0/"}`; `published_date` = `2023-02-20T09:53:26Z`; `authors` = `["Yang"]`; six files, incl. the four the ETL declares |
| Massive-STEPS Istanbul (HF) | `https://huggingface.co/api/datasets/CRUISEResearchGroup/Massive-STEPS-Istanbul` | HTTP 200; `cardData.license` = `apache-2.0`; tag `license:apache-2.0` |
| Massive-STEPS (GitHub) | `https://api.github.com/repos/cruiseresearchgroup/Massive-STEPS/license` | HTTP 200; SPDX `Apache-2.0`, `LICENSE` at repo root |

The dataset card was also read raw. It states the collection "is derived from the [Semantic
Trails Dataset] and [Foursquare Open Source Places]", and its License block reproduces an
Apache-2.0 notice headed "Copyright 2024 Foursquare Labs, Inc." The §2.3 gap is unchanged: the
Foursquare **product terms** were still not opened, only the distribution's licence tag.

### 4.2 NEW, and stronger than §1.3: the upstream address is gone, not merely blocked

§1.3 records that `www.yongliu.org/datasets/` returned 403 on 2026-07-25. That is no longer the
right description. Checked 2026-07-27, both `http://www.yongliu.org/datasets/` and the bare host
return **HTTP 301 to `https://idnpokerasia.net/`**, an unrelated domain. The upstream terms are
therefore not merely unread; the address the Figshare record cites no longer serves the dataset.
This *strengthens* the §1.3 conclusion rather than weakening it: the only readable licence
statement for the consumed copy is the depositor's CC0 label, and no upstream document is
available to corroborate or contradict it. Appendix E says exactly this and no more.

### 4.3 Author ruling recorded (PENDENCIAS.md:139, item 2.1)

The author confirmed the Figshare deposit as the source of record for Gowalla, describing it as a
version of the original release with the seven categories applied, and authorized recording that
provenance in the datasets documentation. Two supporting facts were verified in code and data
this session, and they are consistent with that description:

- The seven top-level names in `data/gowalla/gowalla_category_structure.json` are exactly
  `Community, Entertainment, Food, Nightlife, Outdoors, Shopping, Travel`, matching the taxonomy in
  `src/configs/globals.py:27-30`. **The taxonomy comes with the deposit**, which is what the author
  described. One precision the first draft of Appendix E got wrong and now states correctly: the
  fine-to-top mapping is not purely the deposit's. `src/etl/gowalla/stage_1.py:100-108` merges the
  structure file with two project-local files, `callback_categories.json` (31 entries) and
  `extra_categories.json` (108 entries), for names the structure file does not cover. Appendix E
  therefore says the taxonomy arrives with the deposit and the mapping plus a local supplement is
  what the pipeline adds.
- `src/etl/gowalla/main.py:22-25` declares the four deposit files the pipeline reads.

The `docs/context/DATASETS.md` correction the author approved (item 3 of his answer) is **not in
this track's edit scope** and was not made. It remains open: that file still records SNAP as the
Gowalla source and carries no License row.

### 4.4 Pipeline facts as stated in Appendix E (verified in code, not asserted)

Appendix E claims only what the code does. Each claim and its check:

| Appendix E claim | Verified at |
|---|---|
| No coordinate perturbation, rounding, masking, or formal privacy mechanism anywhere | re-run and corrected 2026-07-27. Two searches: (a) `jitter|add_noise|perturb|laplace|differential_privacy|anonym|pseudonym|deidentif|obfusc` over `src/**/*.py` returns **four** hits, none of them a privacy mechanism: `src/training/profiling.py:158` (GPU timing perturbs throughput), `src/models/next/next_gru_simgcl/head.py:4,:15` (SimGCL embedding noise), and `src/data/folds.py:323` (fold consumption order). (b) the same terms plus `k-anon` restricted to `src/etl/` and `src/data/` return one hit, the folds.py comment above. NOTE: the earlier version of this row claimed the search included `mask` and returned no hit; including `mask` matches 78 files, all attention masks and padding, so that term was dropped as uninformative rather than counted. The conclusion is unchanged and now rests on searches that were actually run: no coordinate perturbation, rounding, or formal privacy mechanism exists in the ETL or data path |
| Raw coordinates used at source precision | `src/etl/gowalla/stage_3.py:40-43` builds point geometry directly from `longitude`/`latitude` |
| Friendship and profile files never read | `gowalla_friendship.csv` and `gowalla_userinfo.csv` are present in `data/gowalla/` and in the deposit, but are declared in neither `src/configs/paths.py` (no `FRIENDSHIP`/`USERINFO` Resource) nor `src/etl/gowalla/main.py:22-25`, and a repo-wide search finds no reader for either |
| Non-numeric user ids replaced by a position index, mapping not persisted | `src/etl/massive_steps/stage_1.py:84-90` (`uid_index` is a local dict; only the venue index is saved) |
| No cross-collection linkage | no code path joins the two collections on any user key; none exists |
| Data not redistributed with the code | `.gitignore:5` excludes `/data/*` |

### 4.5 The prior-dissertation ethics-board check (the author's question 1)

The author asked whether the comparable prior dissertation (same advisor, same area, 2024) needed
a research-ethics-committee determination. **Answer: no such determination appears in it, and its
absence is all that the document can establish.**

Method, so the negative is auditable. The full 96-page text layer of
`exemples/germano/Dissertação_Mestrado___Germano.pdf` was extracted and searched for
`comitê|comite|CAAE|Plataforma Brasil|CEP|IRB|institutional review|ethics committee|ethics board|
ethics approval|approved by the|Resolução N`. **Zero hits.** The extraction is sound: the same text
layer yields two hits for "Ethical Statement", so the search was reading real text.

What the document does contain is a §2.6 "Ethical Statement" (PDF p. 23) that discusses location
privacy, states that anonymized Gowalla user identifiers were used, and states plainly that
latitude and longitude were left unmasked. So the precedent handled the question as a written
ethics statement inside the text, with no committee involvement mentioned anywhere.

**This is evidence, not a rule.** The absence of a mention in one dissertation does not establish
what the program requires. Appendix E is worded accordingly: it records the author's own position
that review was not required, reports this precedent as a precedent, and claims no approval and no
exemption. If a formal determination is required for secondary analysis of public data, only the
program or the committee can supply it, and it is not something an agent can settle.

### 4.6 Still open after this round

1. Foursquare Open Source Places **product terms** (carried over from §2.3, unchanged).
2. Whether the depositor held the rights to apply CC0 (§1.3; now unresolvable from the upstream
   address, per §4.2).
3. `docs/context/DATASETS.md` correction, author-approved but outside this track's scope (§4.3).
4. Whether UFV/PPGCC requires an ethics-committee determination here (§4.5). Author decision, or a
   question for the program.
