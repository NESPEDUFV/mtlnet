"""G1 per-fold integrity assertions. usage: g1_assert.py <state> <fold> <stage>  stage in split|build|materialize"""
import sys, json, hashlib, numpy as np, pandas as pd
st, F, stage = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sha = lambda a: hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
sp = json.load(open(f"results/g1/splits/{st}_split_seed0_fold{F}.json"))
vs = np.sort(np.asarray(sp["val_users"]).astype(np.int64)); vset = set(vs.tolist())
if stage == "split":   # A5
    from sklearn.model_selection import StratifiedGroupKFold
    from configs.paths import EmbeddingEngine
    from data.folds import load_next_data
    for eng in ("check2hgi_dk_ovl",):   # FL: no v18 input copy; dk_ovl is the row source
        # FL A5-lite: the full load_next_data needs ~2x 5.5 GB; the split depends only on (label, userid),
        # so mirror load_next_data's label path exactly (_map_categories, astype(int), NaN drop) on 2 columns.
        from configs.paths import IoPaths
        from data.folds import _map_categories
        df = pd.read_parquet(IoPaths.get_next(st, EmbeddingEngine(eng)), columns=["next_category", "userid"])
        lab = _map_categories(df["next_category"]); u = df["userid"].astype(int).values.copy()
        keep = ~lab.isna(); y = lab[keep].values.astype(np.int64); u = u[keep.values].astype(np.int64)
        tr, va = list(StratifiedGroupKFold(5, shuffle=True, random_state=0).split(np.zeros(len(y)), y, u))[F]
        assert sha(va) == sp["val_idx_sha256"] and sha(tr) == sp["train_idx_sha256"], f"A5 FAIL {eng}"
        assert set(u[va].tolist()) == vset, f"A5 users FAIL {eng}"
    print(f"A5 OK {st} f{F}: n_val_rows={len(va)} n_val_users={len(vset)}")
elif stage == "build":  # A1 + A2 (category) and the a4 region record
    b = json.load(open(f"results/integ18_repr/{st}/TO_F{F}/build.json")); tu = b["training_users"]
    assert tu["n_excluded_users"] == len(vs) and tu["val_users_sha256"] == sha(vs), "A1 users FAIL"
    assert b["graph"]["restricted"] is True and b["epochs"] == 500, "A1 graph FAIL"
    e = pd.read_parquet(f"results/integ18_repr/{st}/TO_F{F}/embeddings_insample.parquet", columns=["userid"])
    assert not (set(e.userid.astype("int64")) & vset), "A2 FAIL"
    print(f"A1/A2 OK {st} f{F}: excluded={len(vs)} kept_checkins={b['graph']['n_checkins']} best_epoch={b['best_epoch']}")
elif stage == "region":
    b = json.load(open(f"output/check2hgi_design_k_resln_mae_l0_1_to_f{F}/{st}/build.json"))
    assert b["n_excluded_users"] == len(vs) and b["val_users_sha256"] == sha(vs) and b["val_users_in_training_checkins"] == 0, "A2r FAIL"
    assert b["split_val_idx_sha256"] == sp["val_idx_sha256"] and b["seed"] == 0 and b["device"] == "cpu", "region record FAIL"
    print(f"region record OK {st} f{F}: remap={b['remap']}")
elif stage == "materialize":  # A4
    m = json.load(open(f"output/check2hgi_v18_to_f{F}/{st}/materialize.json"))
    d = pd.read_parquet(f"output/check2hgi_dk_ovl/{st}/input/next.parquet", columns=["userid", "next_category"])   # FL: reference = dk_ovl
    x = pd.read_parquet(f"output/check2hgi_v18_to_f{F}/{st}/input/next.parquet", columns=["userid", "next_category"])
    assert m["n_windows"] == m["n_windows_source"] == len(d), "A4 FAIL"
    assert (x.userid.astype("int64").values == d.userid.astype("int64").values).all() and (x.next_category.values == d.next_category.values).all(), "A4 rows FAIL"
    print(f"A4 OK {st} f{F}: n_windows={m['n_windows']}")
if stage == "materialize":   # FL extra: next_region is a symlink to dk_ovl's full file, valid only if rows are the identity
    import os
    p = f"output/check2hgi_v18_to_f{F}/{st}/input/next_region.parquet"
    assert os.path.islink(p) and os.path.realpath(p) == os.path.realpath(f"output/check2hgi_dk_ovl/{st}/input/next_region.parquet"), "next_region link FAIL"
    from pathlib import Path
    from integrity_v2.materialize_engine import load_arm
    _, rows = load_arm(Path(f"results/integ18_repr/{st}/TO_F{F}/win_matched.npz"), d)
    assert (rows == np.arange(len(d))).all(), "rows are not the identity: next_region symlink would misalign"
    print(f"next_region symlink OK {st} f{F} (rows == arange, n={m['n_windows']})")
