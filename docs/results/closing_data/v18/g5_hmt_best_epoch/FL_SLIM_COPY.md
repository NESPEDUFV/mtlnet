# SLIM copy of nespedgpu `output/check2hgi_dk_ovl/florida/` (2026-10-01), for G5 (b3_hmt_grn) ONLY

`b3_hmt_grn.load_b3_data` reads exactly: `next.parquet[next_category, userid]`,
`next_region.parquet[region_idx, last_region_idx]` and `temp/sequences_next.parquet` (whole), and
`build_fold_split` reads `next.parquet[next_category, userid]`. The 576 embedding columns are never read.
So input/*.parquet here carry ONLY the label columns (next_region also keeps next_category/userid).
**Do not use this directory for anything that reads embeddings** (train.py, load_next_data, materialize).

| file | box source md5 (full file) | copied | content check |
|---|---|---|---|
| input/next.parquet | 71aafef7354fa71f38c9192fa70de6bc | cols next_category,userid (1,274,418 rows) | sha256(hash_pandas_object) 669f038e…c196 equal box/local |
| input/next_region.parquet | 0438c4852fc7e12b41e46f5c67b5eecf | cols next_category,userid,region_idx,last_region_idx | ec263f71…96c2 equal box/local |
| temp/sequences_next.parquet | fe35b708dea8b9fb8da26a5210393033 | whole file | md5 equal |

Made by streaming `pyarrow.parquet.read_table(columns=…)` on the box to stdout; nothing written on the box.
