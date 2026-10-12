# AUT-35a — Massive-STEPS: validation of the "most modern public dataset" claim

**Task.** Validate or refute the author's claim, from the tracker: *"o masive step e o conjunto mais
moderno que temos na literatura publica, pode validar."* Establish the exact check-in window of the
Istanbul split.

**Report only.** No `.tex` file and no `PENDENCIAS.md` line was edited. Instruments are committed
next to this file (`aut35a_*.py`), so every number below is re-runnable.

**How to check the `L<n>` citations.** Line numbers into the Massive-STEPS paper refer to a text
extraction of the **v3 PDF**, not to a file in this repository (the manuscript is a third party's and
is not committed). Regenerate it and the numbers line up:

```
curl -sSL -o ms_v3.pdf https://arxiv.org/pdf/2505.11239v3
python3 articles/dissertacao/src_utils/_history/_round13/aut35a_extract_pdf_text.py ms_v3.pdf > ms_v3.txt
sed -n '385p' ms_v3.txt      # -> "non-consecutive periods, spanning 2012-2013 and 2017-2018 (24"
```

All ten cited line numbers were re-resolved this way after the report was written, and the
regenerated extraction was byte-identical (`cmp`) to the one the quotations were taken from.

---

## 0 · Verdict, up front

> **REFUTED as stated, and the premise underneath it is also wrong.**

Two independent findings, each fatal to the sentence as the author phrased it:

1. **The Istanbul split is not a 2017-2018 dataset.** It is a *two-period* dataset, and **70.7% of
   the check-ins the dissertation actually models are from 2012-2013.** The measured window of the
   Istanbul data on disk is **2012-04-03 to 2018-10-19**. The prior audit's "2017-2018" reading
   came from the benchmark's abstract, which describes the collection as a whole and does not say
   that every subset is confined to the newer period. Opening the data shows otherwise.
2. **A more recent publicly available check-in dataset exists.** The **Yelp Open Dataset**
   `checkin.json` carries check-in timestamps up to **2022-01-19**, measured by streaming the file.
   Its distribution is more restricted than Massive-STEPS (academic-use agreement, no
   redistribution), which matters for the narrower form below, but it is publicly downloadable and
   it is unambiguously more recent. I make **no** claim that it is widely used for next-POI
   prediction: Massive-STEPS v3's own survey of 40 studies (Table 8) lists Yelp in only two of them,
   and flags both, so the evidence I opened does not support a popularity claim in either direction.

The strongest form that survives is **not** the author's sentence. See §5 for the one defensible
narrowing and §6 for what may be written into §6.3.

---

## 1 · Massive-STEPS: the record (Step 1)

| Field | Value | Where I read it |
|---|---|---|
| Identifier | `arXiv:2505.11239` — **resolves** | `https://arxiv.org/abs/2505.11239`, HTTP 200, opened this session |
| Title | Massive-STEPS: Massive Semantic Trajectories for Understanding POI Check-ins -- Dataset and Benchmarks | abs page, `<h1 class="title">` |
| Authors | Wilson Wongso, Hao Xue, Flora D. Salim | abs page, authors block |
| Submitted | 16 May 2025 (v1); v2 19 May 2025; **v3 9 Feb 2026** | abs page, submission history |
| `journal-ref` | **ABSENT** | abs page — no `tablecell jref` element |
| DOI field | **ABSENT** on the arXiv page | abs page — no `tablecell doi` element |
| Crossref | **no published version found**; a bibliographic query for the exact title returns five unrelated works (globular clusters, CERN storage, rural buildings) | `api.crossref.org/works?query.bibliographic=…`, HTTP 200 |
| OpenAlex | one record only, `https://doi.org/10.48550/arxiv.2505.11239`, source **arXiv (Cornell University)**, year 2025 | `api.openalex.org/works` with `api_key` from `OPENALEX_API_KEY` |
| **Status** | **preprint, not published in a venue** | the three rows above, agreeing |

**Note for the author, new since the earlier audit:** the preprint was **revised on 9 February
2026** (v3, 1,925 KB vs 702 KB for v1/v2). The version I read and quote below is **v3**. The v3
benchmark tables include GPT-5 Nano among the evaluated LLMs, so v3 is materially expanded, not a
typo fix. Anything the dissertation says about this benchmark should be checked against v3 rather
than against a note taken from v1.

### The temporal-coverage sentences, quoted

Abstract, and this is the sentence the earlier audit read (arXiv:2505.11239v3, abstract, page 1):

> "Massive-STEPS spans 15 geographically and culturally diverse cities and features more recent
> (2017-2018) and longer-duration (24 months) check-in data than prior datasets."

The body is more specific, and it contradicts a 2017-2018-only reading (L84-85, §1 Introduction):

> "Massive-STEPS includes high-quality check-ins from 2012-2013 and 2017-2018, providing more
> modern and updated POI check-in data".

And §3.2 (L385-386):

> "Massive-STEPS provides temporal coverage across two non-consecutive periods, spanning 2012-2013
> and 2017-2018 (24 months in total)".

Their own Table 1 (L151-153) lists the Massive-STEPS "Years" cell as **"2012-2013, 2017-2018"** and
"#months" as **24**, against NYC/TKY at 2012-2013 (11 months) and Gowalla-CA at 2009-2010 (21
months).

**No per-city window is given anywhere in the paper.** Table 3 (L317) gives Istanbul's *counts*
(23,700 users; 216,411 trajectories; 53,812 POIs; 544,471 check-ins) but no dates. So the Istanbul
window cannot be quoted from the paper; it has to be measured.

**Their own limitation, worth having on the record** (L716-728, Conclusion):

> "although Massive-STEPS does not reflect present-day mobility patterns, it was designed to provide
> an alternative to older datasets".

The benchmark's own authors decline the claim the dissertation's author wants to make.

---

## 2 · The Istanbul window, MEASURED (Step 1, the part the paper cannot answer)

### Instrument and its validation (V3)

`articles/dissertacao/src_utils/_history/_round13/aut35a_window.py` reads a timestamp column from parquet
files and prints, per file and for the union: non-null count, blank count, min, max, and **a full
per-year histogram**. The histogram is the point: a range alone cannot distinguish "continuous
2012-2018" from "two blocks with a four-year hole", and a claim of the form "this is a 2017-2018
dataset" is falsifiable only by an instrument that would show counts in other years.

**Blindness check, run on a case where the defect is present.** Pointed at the Gowalla state files,
whose window is independently known from the Ch.6 limitation text (January 2009 to August 2011), the
instrument returns 2009/2010/2011 and nothing else:

```
$ cd /Users/vitor/Desktop/mestrado/ingred
$ python3 articles/dissertacao/src_utils/_history/_round13/aut35a_window.py local_datetime \
    "/Users/vitor/Desktop/mestrado/data/checkins_by_state/Alabama.parquet" \
    "/Users/vitor/Desktop/mestrado/data/checkins_by_state/Arizona.parquet"
UNION min=Timestamp('2009-03-18 10:20:09')
UNION max=Timestamp('2011-07-27 12:05:54')
UNION years=[('2009', 15427), ('2010', 223069), ('2011', 111800)]
```

It reports absence of other years correctly on a dataset whose window is known, and it reports 0
nulls where there are none. It is fit to answer the Istanbul question.

### Result A — the upstream Massive-STEPS Istanbul release, as distributed

Three parquet files as downloaded from Hugging Face
(`CRUISEResearchGroup/Massive-STEPS-Istanbul`, cached at
`data/massive_steps_istanbul/raw/tabular/`):

```
$ python3 articles/dissertacao/src_utils/_history/_round13/aut35a_window.py timestamp \
    data/massive_steps_istanbul/raw/tabular/train-00000-of-00001.parquet \
    data/massive_steps_istanbul/raw/tabular/validation-00000-of-00001.parquet \
    data/massive_steps_istanbul/raw/tabular/test-00000-of-00001.parquet
UNION nonnull=544471 null_or_blank=0
UNION min='2012-04-03 18:00:00'
UNION max='2018-10-19 20:52:00'
UNION years=[('2012', 198108), ('2013', 203042), ('2017', 60327), ('2018', 82994)]
```

544,471 non-null timestamps, 0 blanks (V8 satisfied: the column was opened and counted, not
assumed). The 544,471 matches Table 3's Istanbul check-in count exactly, which confirms the local
copy is the complete published subset and not a partial download.

**Composition: 2012 + 2013 = 401,150 of 544,471 (73.7%). 2017 + 2018 = 143,321 of 544,471 (26.3%).**
No check-ins in 2014, 2015, or 2016.

Every aggregate and percentage in this report is printed by
`aut35a_derived_counts.py`, whose inputs are the verbatim histogram lines above, so
that no figure here is prose arithmetic (N2). Disclosed because it caught two of my own errors: the
first draft of this report wrote "66.7%" for the 70.7% modeled share and "3,164,987" for the
2,007,753 post-2018 Yelp count. Both were mental sums, both were wrong, and neither changed the
verdict, which is exactly why they would have survived a reading that only checked the conclusion.

### Result B — the check-ins the dissertation actually models

The Istanbul rows that reach the chronological split (`n_rows` after the pipeline's filtering; this
is the 462,615 that appears in `src_clean/tables/mobiwac/datasets.tex` L17):

```
$ python3 articles/dissertacao/src_utils/_history/_round13/aut35a_window.py datetime \
    output/check2hgi/istanbul/chrono_split/split_assignment.parquet
UNION nonnull=462615 null_or_blank=0
UNION min=Timestamp('2012-04-03 18:00:00')
UNION max=Timestamp('2018-10-19 20:52:00')
UNION years=[('2012', 160601), ('2013', 166641), ('2017', 56797), ('2018', 78576)]
```

**The modeled Istanbul data is 327,242 of 462,615 check-ins from 2012-2013 and 135,373 from
2017-2018.** The pipeline applies no year filter: `src/etl/massive_steps/stage_1.py` and `stage_2.py`
contain no date restriction (grep for `201[2-8]`, `year`, `between` returns only a column-alias list
and a timezone normalization), and the two windows above are identical, which is the expected
signature of no filtering.

Corroborating in-repo record, produced by the pipeline itself rather than by me:
`data/massive_steps_istanbul/parse_report.json` field `datetime_range_local` =
`["2012-04-03 18:00:00", "2018-10-19 20:52:00"]`, with `n_rows` 544471.

### The answer to "what is the Istanbul window"

> **April 2012 to October 2018, in two blocks: 2012-2013 and 2017-2018, with no check-ins in
> 2014-2016.** Of the 462,615 Istanbul check-ins the dissertation models, 327,242 (70.7%) fall in
> 2012-2013 and 135,373 (29.3%) in 2017-2018.

The percentage is stated because it decides the honesty question. A sentence in §6.3 implying the
Istanbul evidence rests on 2017-2018 data would misdescribe roughly seven check-ins in ten.

**Sub-finding the author should know about, since it bears on 2.4 and Ch.5 rather than on 6.3:** the
Istanbul split is *not* newer than the Gowalla splits by a clean margin. Gowalla ends August 2011;
Istanbul's larger block begins April 2012. The genuinely newer part of Istanbul is the 29.3% from
2017-2018.

---

## 3 · The comparative search (Step 2)

Candidates checked. Every row states whether I opened the source, and the window comes from that
source, not from a secondary citation.

| # | Dataset | Identifier | Opened? | Check-in / visit window, per its own source | Publicly available? |
|---|---|---|---|---|---|
| 1 | **Massive-STEPS** (Istanbul) | arXiv:2505.11239 (v3); HF `CRUISEResearchGroup/Massive-STEPS-Istanbul` | **Yes** — abs page, v3 PDF, HF API record, and the data files | **2012-04-03 to 2018-10-19**, two blocks (measured, §2) | **Yes.** HF API reports `license: apache-2.0` in `cardData`; created 2025-01-17, last modified 2025-09-26 |
| 2 | **Yelp Open Dataset** | no DOI; `business.yelp.com/data/resources/open-dataset/` | **Yes** — landing page, the bundled documentation PDF, and `checkin.json` itself | **2009-12-30 to 2022-01-19** (measured, §4) | **Partly.** Free download, no paid or partner agreement, but the Data Agreement is **academic-use-only, no redistribution, 12-month term**. See §4 |
| 3 | **FSQ-NYC / FSQ-TKY** (NYC and Tokyo Check-in Dataset) | Yang et al., the standard next-POI benchmark | **No** — not opened directly; window taken from Massive-STEPS v3 Table 1 and §2, which cite it | 2012-2013 (11 months) | Yes, per Massive-STEPS Table 1 ("Replicable ✓ Open ✓") |
| 4 | **Global-scale Check-in Dataset (GSCD)** | Yang et al. | **No** — not opened directly | 2012-2013, per Massive-STEPS v3 L248-252: "GSCD is temporally limited to the same 2012-2013 period" | Per Massive-STEPS, yes but with quality problems |
| 5 | **Semantic Trails Dataset (STD)** — the upstream of Massive-STEPS | arXiv:1812.04367 | **Yes** — abs page opened; title, authors, dates confirmed | STD 2013 covers 2012-2013; **STD 2018 covers 2017-2018 "sourced from Foursquare Swarm"** (Massive-STEPS v3 L264-266) | Yes; Massive-STEPS L299 records STD as CC0 1.0 |
| 6 | **Gowalla / Brightkite** (the floor) | Gowalla state files in this repo | **Yes** — measured, §2 blindness check | Gowalla, five states as extracted here: 2009-03 to 2011-07 | Yes |
| 7 | **Context Trails** | `10.1145/3705328.3748151`; Zenodo `10.5281/zenodo` record 15855966 | **Yes** — Zenodo record page opened in full | Trails built on **2017 and 2018** weather-joined check-ins (record: "historical weather data from the years 2017 and 2018"); POI attributes retrieved from the Foursquare API in **November 2024** | **No, not as check-ins.** The record states: "Since Foursquare does not grant explicit permission to redistribute the original data, you must run the download_process_poi_info.sh script" with your own Foursquare API key |
| 8 | **YJMob100K** | `10.1038/s41597-024-03237-9`, Scientific Data 11:397 (2024) | **Yes** — full PDF fetched and read | **Not applicable, and this is the point:** "The actual date of the observations was also masked (i.e., timeslot t of day d) to protect privacy"; 75 days, dates undisclosed | Open, but it is **not a check-in dataset** (mobile-phone location pings on a 500 m grid, metropolitan area undisclosed) and it has **no absolute dates**, so it cannot be more or less "modern" in the sense at issue |
| 9 | **FSQ OS Places** | Foursquare open POI release | **No** — not opened | **Not applicable:** a POI *inventory*, not a check-in log. No visit timestamps | Apache 2.0, per Massive-STEPS L99 and L126 |

Searches run, so the coverage claim is auditable in both directions (V13): OpenAlex
(`from_publication_date` 2023-01-01 through 2025-01-01) on seven query formulations — recent
check-in / LBSN benchmark datasets, Semantic Trails, GSCD, YJMob100K, FSQ OS Places, Swarm-sourced
collections, Google Local reviews; the Hugging Face dataset API sorted by `lastModified` for
`search=check-in` (40 most recent: nothing mobility-related except restatements of Brightkite and
Gowalla); and the Massive-STEPS v3 Table 8 survey of 40 next-POI studies' datasets, which is itself
a field-wide audit of what is public and reproducible, and in which **no entry is newer than
2017-2018**.

**What I could not do:** the arXiv API returned HTTP 429 on every attempt (five tries across the
session, `export.arxiv.org` rate limit), so I could not run a systematic recency-sorted sweep of
arXiv submissions. The abs pages for the specific identifiers I needed all resolved. See the
[VERIFY] flag in §7.

---

## 4 · The Yelp finding, in detail (this is what refutes the claim)

The Yelp Open Dataset is the one candidate whose check-ins are demonstrably more recent, so it gets
its own section and its own first-hand measurement.

### What I opened

- `https://business.yelp.com/data/resources/open-dataset/`, HTTP 200. States the dataset "provides
  real-world data related to businesses including reviews, photos, **check-ins**". Counts on the
  page: 6,990,280 reviews; 150,346 businesses; 11 metropolitan areas.
- The **documentation PDF bundled inside the download**, extracted from the archive by HTTP range
  request rather than downloading 4.35 GB (`aut35a_zipprobe.py`). It documents `checkin.json` as
  "Checkins on a business", with a `date` field that is "a comma-separated list of timestamps for
  each checkin, each with format YYYY-MM-DD HH:MM:SS".
- **`checkin.json` itself**, streamed and scanned (`aut35a_yelp_checkin_scan.py`).

### The measurement

```
$ cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao/src_utils/_round13
$ python3 aut35a_yelp_checkin_scan.py 9000000000
tar member data offset=115143
TAR member=Dataset_User_Agreement.pdf size=80358 at_inflated=5574558
TAR member=yelp_academic_dataset_business.json size=118863795 at_inflated=5574558
TAR member=yelp_academic_dataset_checkin.json size=286958945 at_inflated=122318267
CHECKIN DONE min=2009-12-30 max=2022-01-19
YEARS=[('2009', 2), ('2010', 209154), ('2011', 901460), ('2012', 1289505), ('2013', 1552816),
       ('2014', 1625890), ('2015', 1709865), ('2016', 1554780), ('2017', 1348470),
       ('2018', 1157260), ('2019', 1035165), ('2020', 474174), ('2021', 477474), ('2022', 20940)]
```

The whole of `checkin.json` was read (the scanner exits only on completing the member's declared
286,958,945 bytes; it does not stop early and call that a result). Of the 13,356,955 timestamps
scanned, **2,007,753 fall in 2019 or later** (`aut35a_derived_counts.py`), that is, after the end of
every window in the table in §3. The remote file
carries `last-modified: Wed, 15 Jan 2025 22:16:07 GMT`, so this is the current release.

### V3 disclosure: this instrument was wrong on its first run, and I caught it

The first version of the scanner reported walking sixteen tar members with binary-garbage names and
`size=0`, then "CAP/EOF reached without completing checkin.json". Read naively, that output would
have supported "Yelp's check-in window could not be established" and thereby propped up the author's
claim. The defect: the zip member is named `yelp_dataset.tar` but its inflated content begins
`1f 8b 08` — it is a **gzip stream**, so a single-stage DEFLATE decompressor yields compressed bytes
and the tar header walk desyncs into noise. Diagnosed by dumping the first 512 inflated bytes;
fixed by chaining a second decompressor (`zlib.MAX_WBITS + 16`). The fixed run prints three
real member names and completes. **The clean-looking failure of the first run was the instrument,
not the data**, which is precisely the class §4b V3 exists for. The fix and its reason are recorded
in the script's own comments.

### Is Yelp "publicly available"?

Honestly: **partly, and less freely than Massive-STEPS.** From the bundled Terms of Use ("Last
Updated: July 7, 2023"), read first-hand:

- the license is for "solely academic purposes", "Academic use means … non-commercial use";
- prohibited: "share or make available the Data to any third party", and to "display, perform, or
  distribute any of the Data";
- the term is "twelve (12) months from the Effective Date".

There is **no fee and no partner agreement**, so it is not excluded by the task's paid-or-partner
test, and anyone can download it. But it is **not openly redistributable**, whereas the
Massive-STEPS Istanbul subset is distributed on Hugging Face under Apache 2.0 (`cardData.license`
= `apache-2.0`, read from the HF API this session; the same license the dissertation already states
in `src_clean/chapters/apx_e_ethics.tex`). That distinction is the only thing standing between
"refuted" and "refuted with a consolation prize", and it is the hinge of the narrower form below.

---

## 5 · Verdict (Step 3)

**(c) REFUTED**, on two independent grounds:

1. **The Yelp Open Dataset** has check-ins through **2022-01-19**, measured first-hand, against
   Massive-STEPS Istanbul's **2018-10-19**. It is publicly downloadable at no cost and is a
   check-in dataset by its own documentation. It is more modern.
2. **The premise about Massive-STEPS itself is wrong.** The Istanbul split is not a 2017-2018
   dataset; **70.7% of the modeled Istanbul check-ins are from 2012-2013**. Even if Yelp did not
   exist, "the most modern set we have in the public literature" would misdescribe the dataset's own
   composition.

### The narrower form that IS defensible

If the author wants a defensible sentence in this neighborhood, this is what the evidence supports,
and it is considerably narrower than what he asked to validate:

> **Among the openly redistributable, city-partitioned check-in benchmarks used in the next-POI
> literature, the Massive-STEPS collection contributes the most recent check-ins, and its newer
> period (2017-2018) postdates the 2012-2013 window of the Foursquare NYC/Tokyo and global-scale
> benchmarks and the 2009-2010 window of Gowalla.**

Each qualifier is load-bearing, and each was forced by a specific piece of evidence:

- **"openly redistributable"** is forced by Yelp: without it, Yelp (2022) wins outright.
- **"city-partitioned … used in the next-POI literature"** is forced by Yelp again (11 metro areas,
  but not partitioned or conventionally used for next-POI) and by YJMob100K (open, newer paper, but
  grid pings with masked dates, not check-ins).
- **"the collection contributes"**, not "the Istanbul split is", is forced by §2: the Istanbul split
  is majority 2012-2013, so a claim about *its* modernity does not hold. What holds is a claim about
  the newer period *within* the collection.
- **"postdates"** with the comparison windows named is forced by N1/§3 of the writing law: a
  recency claim without its reference points is a naked comparative.

I am **not** recommending this sentence for §6.3. It belongs in §2.4 if anywhere, where the
benchmark's contribution is already discussed, and it is a claim about third parties that under C2
needs the author's sign-off. §6.3 is a *limitations* section, and the honest content there is the
opposite in sign: see §6.

---

## 6 · The §6.3 sentence (Step 4)

The verdict is (c), so per the task's own instruction the answer is: **the sentence the author
envisioned should not be written.** A §6.3 addition asserting that Istanbul is the field's most
modern public data would be false on both grounds in §5.

But the author's underlying editorial goal is legitimate and is served better by the truth. His
recorded intent (`src_utils/PENDENCIAS.md` L1051-1053) is to keep the Gowalla window literal,
because probe `R8-vintage` (`src_utils/check_audit_claims.py:91-92`) requires the literal string
`August 2011` in `chapters/6_conclusion.tex`, and to **add one sentence naming the Istanbul
window**. That addition is not only writable, it is *owed*: the current item 1 is headed **"Data
vintage"** and names only Gowalla, so a reader finishing it does not learn that the sixth dataset
also predates the present, nor that most of it is contemporaneous with the Gowalla era.

**Proposed addition to §6.3 item 1** (an addition; the existing text, including `August 2011`,
remains untouched):

> The Istanbul check-ins span April 2012 to October 2018 in two separate periods, and 327,242 of the
> 462,615 check-ins used here fall in 2012 and 2013, so the Istanbul evidence is not substantially
> more recent than the Gowalla evidence.

Compliance notes for the author's audit of that sentence:

- **`August 2011` is untouched.** The sentence is appended inside item 1; `grep -vn '^[[:space:]]*%'
  chapters/6_conclusion.tex | grep -c "August 2011"` returns 1 today and must still return 1 after
  the edit, which is what probe `R8-vintage` checks.
- Names "Istanbul" rather than "the non-United-States evidence", because item 5 (Geographic
  coverage) already carries the phrase "Outside the United States" and Ch.6 uses the spelled-out
  form. Naming the city keeps item 1 about vintage and avoids restating item 5.
- 39 words, one sentence, zero chained qualifiers, no delayed subject: checked mechanically against
  the four banned shapes of WRITING_LAW §1.

- Both numbers carry their convention: they are counts of modeled Istanbul check-ins, and 462,615
  is the figure already published in `src_clean/tables/mobiwac/datasets.tex` L17. Traceable to
  `aut35a_window.py` on `split_assignment.parquet`, §2 Result B.
- No em-dash; no contractions; American English; digits for data quantities per WRITING_LAW §1.
- Canonical names only: "check-in", not "event"; no repo codenames.
- No process narration: it states a property of the data, not how the property was measured.
- The comparative clause is a *limitation*, not a superiority claim, so no test needs to be bound
  to it.
- **New numbers.** 327,242 and 462,615-as-Istanbul-total need ledger lines under N3 before landing,
  and `wongso2025massivesteps` does not support them (the paper gives no per-city window), so the
  ledger source must be the repo measurement, not the citation. Do not attach the citation to this
  sentence as if it were the source of the window.

Ledger lines for whoever lands it:

| Value | Source | Command |
|---|---|---|
| 327,242 (2012 + 2013 modeled Istanbul check-ins) | `output/check2hgi/istanbul/chrono_split/split_assignment.parquet` | `python3 articles/dissertacao/src_utils/_history/_round13/aut35a_window.py datetime output/check2hgi/istanbul/chrono_split/split_assignment.parquet` → `years=[('2012',160601),('2013',166641),…]` |
| 462,615 (modeled Istanbul check-ins) | same file; already published in `tables/mobiwac/datasets.tex` L17 | same command, `UNION nonnull=462615` |
| April 2012 / October 2018 | same file | same command, `UNION min` / `UNION max` |

---

## 7 · [VERIFY] flags

1. **[VERIFY: arXiv recency sweep not run.]** `export.arxiv.org/api/query` returned HTTP 429 on
   five attempts across this session, so I could not run a submission-date-sorted sweep of recent
   arXiv preprints for check-in dataset releases. The gap is bounded but real: a 2025-2026 preprint
   releasing check-ins newer than 2022 could exist and be absent from my table. Mitigation actually
   performed: seven OpenAlex queries, the Hugging Face dataset index, and Massive-STEPS v3's own
   40-study survey of public POI datasets. None surfaced anything post-2018 other than Yelp. Retry
   with a pause between calls.
2. **[VERIFY: rows 3, 4, and 9 of the §3 table were not opened at the source.]** FSQ-NYC/TKY, GSCD,
   and FSQ OS Places windows are quoted from **Massive-STEPS v3**, which I did open, rather than
   from Yang et al. or Foursquare directly. Under R2 that is second-hand attribution. It does not
   affect the verdict (all three are *older* than Istanbul, so they cannot refute anything), but if
   any of those windows is written into the dissertation, open the primary source first.
3. **[VERIFY: Massive-STEPS v3 is a 9 February 2026 revision that postdates the earlier audit.]**
   The dissertation's provenance comments (`2.4_datasets_and_evaluation.tex:80`,
   `2.4_citations.md:28`) record the preprint without a version. Anything the dissertation claims
   about this benchmark should be re-read against v3, whose benchmark tables differ from v1.
4. **[VERIFY: Yelp's 11 metropolitan areas are not named on the landing page.]** The page says "11
   Metropolitan areas" without listing them, and I did not stream `business.json` to enumerate
   them. Not needed for the recency verdict; needed if Yelp were ever proposed as a dataset for
   this work.
5. **Not a flag, a caution.** The Istanbul two-period structure (2012-2013 plus 2017-2018, four-year
   gap, no 2014-2016) may interact with the user-disjoint chronological split in ways nothing in
   this task examined. `chrono_split_report.json` records all three leak checks as passing and
   2,780 users appearing in both train and test. Whether a user's timeline straddles the 2014-2016
   gap, and what a nine-visit sliding window means across a four-year discontinuity, is a separate
   question. Flagging it because it was visible from here, not because AUT-35a asked.

---

## 8 · Source ledger

| # | Source | Identifier | Opened this session | Claim it supports here |
|---|---|---|---|---|
| 1 | Massive-STEPS abs page | arXiv:2505.11239 | Yes, HTTP 200 | Title, authors, v1/v2/v3 dates, absent `journal-ref` and DOI → preprint status |
| 2 | Massive-STEPS v3 PDF | arXiv:2505.11239v3, 21 pp extracted | Yes | Abstract's "(2017-2018)" sentence; §1's "2012-2013 and 2017-2018"; §3.2's "two non-consecutive periods"; Table 1 years cells; Table 3 Istanbul counts; Table 8 survey; the authors' own "does not reflect present-day mobility patterns" limitation |
| 3 | Crossref works API | `api.crossref.org/works?query.bibliographic=…` | Yes, HTTP 200 | No published version of Massive-STEPS: five unrelated hits |
| 4 | OpenAlex works API | `api.openalex.org/works`, `api_key` from env | Yes, HTTP 200 | Single Massive-STEPS record, source arXiv, 2025; also the seven candidate-search sweeps |
| 5 | Hugging Face dataset API | `CRUISEResearchGroup/Massive-STEPS-Istanbul` | Yes, HTTP 200 | Apache 2.0 license in `cardData`; created 2025-01-17, modified 2025-09-26 |
| 6 | Massive-STEPS Istanbul parquet files, as distributed | `data/massive_steps_istanbul/raw/tabular/*.parquet` | Yes, all three read | Upstream Istanbul window and per-year histogram; 544,471 non-null, 0 blanks |
| 7 | Modeled Istanbul split | `output/check2hgi/istanbul/chrono_split/split_assignment.parquet` | Yes | The 462,615 window and per-year counts; the 327,242 figure |
| 8 | Pipeline parse report | `data/massive_steps_istanbul/parse_report.json` | Yes | `datetime_range_local` corroborating source 6, produced by the pipeline itself |
| 9 | ETL source | `src/etl/massive_steps/stage_1.py`, `stage_2.py` | Yes | No year filter, so sources 6 and 7 windows are not an artifact of filtering |
| 10 | Gowalla state files | `checkins_by_state/{Alabama,Arizona}.parquet` | Yes | Instrument blindness check (V3); the 2009-2011 floor |
| 11 | Yelp Open Dataset landing page | `business.yelp.com/data/resources/open-dataset/` | Yes, HTTP 200 (domain access granted this session) | Check-ins are in the dataset; 11 metro areas; free download |
| 12 | Yelp documentation and Terms PDF | extracted from the download archive by HTTP range | Yes, 10 pp | `checkin.json` schema and timestamp format; academic-use-only, no-redistribution, 12-month terms, "Last Updated: July 7, 2023" |
| 13 | Yelp `yelp_academic_dataset_checkin.json` | streamed from the same archive | Yes, member read to completion | **Check-ins 2009-12-30 to 2022-01-19**, full per-year histogram → the refutation |
| 14 | Semantic Trails abs page | arXiv:1812.04367 | Yes, HTTP 200 | Title, authors, 2018/2019 dates; the upstream of Massive-STEPS |
| 15 | Context Trails Zenodo record | Zenodo record 15855966 (paper `10.1145/3705328.3748151`) | Yes, full record read | 2017-2018 weather-joined trails; POI metadata retrieved November 2024; **Foursquare check-ins not redistributable** |
| 16 | YJMob100K | `10.1038/s41597-024-03237-9`, Scientific Data 11:397 | Yes, full PDF read | Dates masked ("timeslot t of day d"), 75 days, undisclosed metropolitan area, grid pings not check-ins → out of scope for a recency comparison |
| 17 | `src_clean/chapters/6_conclusion.tex` | repo, comment-stripped grep | Yes | Item 1 text and the literal `August 2011` at L156 |
| 18 | `src_utils/check_audit_claims.py` | repo, L91-92 | Yes | Probe `R8-vintage` requires the regex `August\s+2011` in `chapters/6_conclusion.tex` |
| 19 | `src_utils/PENDENCIAS.md` | repo, L1051-1053 | Yes | The author's recorded plan: keep the Gowalla window literal, add one Istanbul-window sentence |

**Instruments, all committed at `articles/dissertacao/src_utils/_history/_round13/`:**
`aut35a_window.py` (parquet window and per-year histogram, blindness-validated on Gowalla),
`aut35a_zipprobe.py` (remote zip central directory over HTTP ranges),
`aut35a_yelp_checkin_scan.py` (streaming scan of `checkin.json`, with the two-stage decompression
fix and its reason in the comments), `aut35a_openalex_search.py`, `aut35a_parse_arxiv.py`, `aut35a_derived_counts.py` (every aggregate
and percentage in this report), `aut35a_extract_pdf_text.py` (regenerates the line numbering the
`L<n>` citations use).

**Not done, by instruction:** no `.tex` file edited, no `PENDENCIAS.md` line edited. §6 proposes a
sentence; it does not land it.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
