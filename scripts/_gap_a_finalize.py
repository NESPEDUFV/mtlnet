"""Finalize Gap A: aggregate CA + TX results into per-state JSONs.

Reads the floor + faithful + STL outputs and rebuilds the v1-schema
state JSONs at docs/baselines/{next_category,next_region}/results/{california,texas}.json.

Run after all training cells finish. Idempotent.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

TODAY = date.today().isoformat()
TAG_PREFIX = {'california': 'CA', 'texas': 'TX'}
ROOT = Path(__file__).resolve().parents[1]


def round_pct(x):
    return round(float(x) * 100, 4)


def load(p):
    return json.loads(Path(p).read_text())


def best_k(kstep_data):
    """Pick K with highest macro_f1_mean from the markov_kstep dict."""
    best = max(kstep_data.items(), key=lambda kv: kv[1]['macro_f1_mean'])
    return best[0], best[1]


def faithful_block(p, key='aggregate'):
    """Extract a faithful baseline aggregate block to a state-JSON cell."""
    d = load(p)
    a = d.get(key, d)
    out = {
        "n_rows": d.get("n_rows", d.get("n_train", 0) + d.get("n_val", 0)),
    }
    # Map various aggregate field names to the canonical schema
    field_map = {
        'acc1': 'accuracy',
        'acc3': 'top3_acc',
        'acc5': 'top5_acc',
        'acc10': 'top10_acc',
        'mrr': 'mrr',
        'macro_f1': 'f1',
    }
    for canonical, source in field_map.items():
        for sm in (f"{source}_mean", f"{canonical}_mean"):
            if sm in a:
                out[f"{canonical}_mean"] = round_pct(a[sm])
                break
        for ss in (f"{source}_std", f"{canonical}_std"):
            if ss in a:
                out[f"{canonical}_std"] = round_pct(a[ss])
                break
    return out


for state in ['california', 'texas']:
    abbr = TAG_PREFIX[state]
    # ------- floors -------
    p0_cat = load(f'docs/results/P0/simple_baselines/{state}/next_category.json')
    p0_reg = load(f'docs/results/P0/simple_baselines/{state}/next_region.json')
    p0_f1 = load(f'docs/results/P0/simple_baselines/{state}/next_category_f1.json')
    p0_kcat = load(f'docs/results/P0/simple_baselines/{state}/next_category_markov_kstep.json')
    bk_name, bk_vals = best_k(p0_kcat)

    # ------- next_category -------
    cat_agg = p0_cat['aggregate']
    n_rows_cat = p0_cat['per_fold'][0]['n_train'] + p0_cat['per_fold'][0]['n_val']

    poi_rgnn_p = f'docs/results/baselines/faithful_poi_rgnn_{state}_5f_35ep_FAITHFUL_POIRGNN_{state}_5f35ep.json'
    mha_pe_p = f'docs/results/baselines/faithful_mha_pe_{state}_5f_11ep_FAITHFUL_MHAPE_{state}_5f11ep.json'
    cat_baselines = {}
    if Path(poi_rgnn_p).exists():
        b = faithful_block(poi_rgnn_p)
        b.update({"tag": f"FAITHFUL_POIRGNN_{state}_5f35ep", "date": TODAY, "source_json": poi_rgnn_p})
        cat_baselines["poi_rgnn"] = {"faithful": b}
    else:
        cat_baselines["poi_rgnn"] = {"_pending": "POI-RGNN faithful train still running."}
    if Path(mha_pe_p).exists():
        b = faithful_block(mha_pe_p)
        b.update({"tag": f"FAITHFUL_MHAPE_{state}_5f11ep", "date": TODAY, "source_json": mha_pe_p})
        cat_baselines["mha_pe"] = {"faithful": b}
    else:
        cat_baselines["mha_pe"] = {"_pending": "MHA+PE faithful train still running."}

    next_cat = {
        "schema_version": 1,
        "state": state,
        "task": "next_category",
        "n_rows": n_rows_cat,
        "n_classes": p0_cat['n_classes'],
        "protocol": {
            "folds": 5, "epochs": 35, "seed": 42,
            "stratification": "target_category",
            "groups": "userid",
            "splitter": "StratifiedGroupKFold(shuffle=True)"
        },
        "floors": {
            "majority_class": {
                "acc1_mean": round_pct(cat_agg['majority']['acc1_mean']),
                "acc1_std": round_pct(cat_agg['majority']['acc1_std']),
                "acc5_mean": round_pct(cat_agg['majority']['acc5_mean']),
                "acc5_std": round_pct(cat_agg['majority']['acc5_std']),
                "macro_f1_mean": round(p0_f1['majority_f1_mean'], 3),
                "macro_f1_std": round(p0_f1['majority_f1_std'], 3),
                "source_json": f"docs/results/P0/simple_baselines/{state}/next_category.json",
                "f1_source_json": f"docs/results/P0/simple_baselines/{state}/next_category_f1.json"
            },
            "top_k_popular": {
                "acc1_mean": round_pct(cat_agg['top_k_popular']['acc1_mean']),
                "acc1_std": round_pct(cat_agg['top_k_popular']['acc1_std']),
                "acc5_mean": round_pct(cat_agg['top_k_popular']['acc5_mean']),
                "acc5_std": round_pct(cat_agg['top_k_popular']['acc5_std']),
                "mrr_mean": round_pct(cat_agg['top_k_popular']['mrr_mean']),
                "mrr_std": round_pct(cat_agg['top_k_popular']['mrr_std']),
                "source_json": f"docs/results/P0/simple_baselines/{state}/next_category.json"
            },
            "markov_1_poi": {
                "acc1_mean": round_pct(cat_agg['markov_1step']['acc1_mean']),
                "acc1_std": round_pct(cat_agg['markov_1step']['acc1_std']),
                "acc5_mean": round_pct(cat_agg['markov_1step']['acc5_mean']),
                "acc5_std": round_pct(cat_agg['markov_1step']['acc5_std']),
                "mrr_mean": round_pct(cat_agg['markov_1step']['mrr_mean']),
                "mrr_std": round_pct(cat_agg['markov_1step']['mrr_std']),
                "macro_f1_mean": round(p0_f1['markov_1step_f1_mean'], 3),
                "macro_f1_std": round(p0_f1['markov_1step_f1_std'], 3),
                "source_json": f"docs/results/P0/simple_baselines/{state}/next_category.json",
                "f1_source_json": f"docs/results/P0/simple_baselines/{state}/next_category_f1.json"
            },
            "markov_k_cat": {
                "best_k": int(bk_name.lstrip('k')),
                "acc1_mean": round(bk_vals['acc1_mean'], 3),
                "acc1_std": round(bk_vals['acc1_std'], 3),
                "macro_f1_mean": round(bk_vals['macro_f1_mean'], 3),
                "macro_f1_std": round(bk_vals['macro_f1_std'], 3),
                "all_k": p0_kcat,
                "source_json": f"docs/results/P0/simple_baselines/{state}/next_category_markov_kstep.json"
            }
        },
        "baselines": cat_baselines
    }
    out_cat = ROOT / f'docs/baselines/next_category/results/{state}.json'
    out_cat.write_text(json.dumps(next_cat, indent=2))
    print(f'wrote {out_cat}')

    # ------- next_region -------
    n_rows_reg = p0_reg['per_fold'][0]['n_train'] + p0_reg['per_fold'][0]['n_val']
    reg_agg = p0_reg['aggregate']

    eng_blocks = {}
    for eng in ['check2hgi', 'hgi']:
        tag = f"STL_{abbr}_{eng}_stan_5f50ep"
        p = f'docs/results/P1/region_head_{state}_region_5f_50ep_{tag}.json'
        stl = load(p)
        a = stl['heads']['next_stan']['aggregate']
        eng_blocks[f'stl_{eng}'] = {
            "acc1_mean": round_pct(a['accuracy_mean']),
            "acc1_std": round_pct(a['accuracy_std']),
            "acc5_mean": round_pct(a['top5_acc_mean']),
            "acc5_std": round_pct(a['top5_acc_std']),
            "acc10_mean": round_pct(a['top10_acc_mean']),
            "acc10_std": round_pct(a['top10_acc_std']),
            "mrr_mean": round_pct(a['mrr_mean']),
            "mrr_std": round_pct(a['mrr_std']),
            "macro_f1_mean": round_pct(a['f1_mean']),
            "macro_f1_std": round_pct(a['f1_std']),
            "tag": tag,
            "date": TODAY,
            "source_json": p
        }

    stan_p = f'docs/results/baselines/faithful_stan_{state}_5f_50ep_FAITHFUL_STAN_{state}_5f50ep.json'
    stan_block = {}
    if Path(stan_p).exists():
        stan_faith = faithful_block(stan_p)
        stan_faith.update({"tag": f"FAITHFUL_STAN_{state}_5f50ep", "date": TODAY, "source_json": stan_p})
        stan_faith.pop("n_rows", None)
        stan_block["faithful"] = stan_faith
    else:
        stan_block["_pending_faithful"] = "STAN faithful train still running."

    next_reg = {
        "schema_version": 1, "state": state, "task": "next_region",
        "n_rows": n_rows_reg, "n_classes": p0_reg['n_classes'],
        "protocol": {
            "folds": 5, "epochs": 50, "seed": 42,
            "stratification": "target_category", "groups": "userid",
            "splitter": "StratifiedGroupKFold(shuffle=True)"
        },
        "floors": {
            "majority_class": {
                "acc1_mean": round_pct(reg_agg['majority']['acc1_mean']),
                "acc1_std": round_pct(reg_agg['majority']['acc1_std']),
                "acc5_mean": round_pct(reg_agg['majority']['acc5_mean']),
                "acc5_std": round_pct(reg_agg['majority']['acc5_std']),
                "acc10_mean": round_pct(reg_agg['majority']['acc10_mean']),
                "acc10_std": round_pct(reg_agg['majority']['acc10_std']),
                "mrr_mean": round_pct(reg_agg['majority']['mrr_mean']),
                "mrr_std": round_pct(reg_agg['majority']['mrr_std']),
                "source_json": f"docs/results/P0/simple_baselines/{state}/next_region.json"
            },
            "markov_1_region": {
                "acc1_mean": round_pct(reg_agg['markov_1step_region']['acc1_mean']),
                "acc1_std": round_pct(reg_agg['markov_1step_region']['acc1_std']),
                "acc5_mean": round_pct(reg_agg['markov_1step_region']['acc5_mean']),
                "acc5_std": round_pct(reg_agg['markov_1step_region']['acc5_std']),
                "acc10_mean": round_pct(reg_agg['markov_1step_region']['acc10_mean']),
                "acc10_std": round_pct(reg_agg['markov_1step_region']['acc10_std']),
                "mrr_mean": round_pct(reg_agg['markov_1step_region']['mrr_mean']),
                "mrr_std": round_pct(reg_agg['markov_1step_region']['mrr_std']),
                "source_json": f"docs/results/P0/simple_baselines/{state}/next_region.json"
            }
        },
        "baselines": {
            "stan": {
                **stan_block,
                **eng_blocks
            }
        }
    }
    out_reg = ROOT / f'docs/baselines/next_region/results/{state}.json'
    out_reg.write_text(json.dumps(next_reg, indent=2))
    print(f'wrote {out_reg}')

print('done')
