"""A4 transductivity bound — build a TRAIN-USERS-ONLY v14 substrate for one fold.

[2026-09-30, integrity re-run on the delivered protocol] Three changes, and only three:
  (a) SPLIT. Validation users come from a frozen split JSON (scripts/integrity_v2/freeze_split.py,
      StratifiedGroupKFold on the check2hgi_dk_ovl rows -- the split the delivered v18 cells use),
      not from a re-derived split on the canonical check2hgi rows. The two disagree: at Alabama
      fold 0, 169 of the 219 delivered validation users sat in the old split's training side.
  (b) OUTPUT. The remapped region table is written as a NEW engine,
      output/<--out-engine>/<state>/region_embeddings.parquet, which p1_region_head_ablation.py
      reads unmodified via its check2hgi_design_k* prefix route. Nothing goes to results/ (on
      /home) and the old skip-if-exists check on results/pre_freeze_gates/a4/ can no longer
      silently reuse a wrong-split table.
  (c) NOTHING IS OVERWRITTEN OR DELETED. A fresh pseudo tag, a pre-flight refusal if any target
      path already exists, and pseudo artifacts kept by default (--cleanup-pseudo is opt-in).
The builder itself (preprocess_check2hgi -> build_design_k_delaunay.py, 500 epochs) is unchanged.

The v14/Check2HGI substrate is transductive: it trains on ALL check-ins (incl. validation-fold
users), so val embeddings are shaped by val data. A4 quantifies the resulting downstream inflation
by rebuilding the substrate per fold on train users only and re-evaluating.

This script builds the train-only substrate for ONE (state, seed, fold):
  1. Replicate the harness split (StratifiedGroupKFold(seed) on canonical next data) → val users.
  2. Write train-only check-ins to a pseudo-state parquet.
  3. preprocess_check2hgi → train-only check-in graph (the transductive surface, rebuilt).
  4. design_k (v14) on it, REUSING the full HGI Delaunay/POI2Vec scaffolding (POI-spatial priors,
     NOT a check-in-transductive channel — held fixed; scoping noted in the verdict).
  5. GEOID-remap the train-only region embeddings into the FULL region index space (zeros for
     regions absent from train — the inductive gap; rare for coarse tracts) and save to
     results/pre_freeze_gates/a4/<state>_s{seed}_f{fold}_regemb.parquet.

Usage:
    python scripts/pre_freeze_gates/a4_build.py --state florida --seed 0 --fold 0 [--folds 5]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

from configs.paths import EmbeddingEngine, IoPaths, Resources
from data.folds import load_next_data
from embeddings.check2hgi.preprocess import preprocess_check2hgi

V14_ENGINE = "check2hgi_design_k_resln_mae_l0_1"
SHAPEFILES = {"alabama": Resources.TL_AL, "arizona": Resources.TL_AZ, "florida": Resources.TL_FL}
A4_DIR = _root / "results" / "pre_freeze_gates" / "a4"   # the ORIGINAL run's dir; read-only now, never written


def val_users_from_split_json(path, state, seed, fold):
    """Validation users of one fold, from a frozen split JSON (freeze_split.py output)."""
    sp = json.loads(Path(path).read_text())
    assert sp["state"] == state.lower() and int(sp["seed"]) == seed and int(sp["fold"]) == fold, \
        f"split JSON {path} is ({sp['state']}, s{sp['seed']}, f{sp['fold']}), asked ({state}, s{seed}, f{fold})"
    assert sp.get("engine") == "check2hgi_dk_ovl", f"split JSON engine is {sp.get('engine')}, want check2hgi_dk_ovl"
    # [2026-10-01] The str-vs-int64 userid trap: only an int64-group split equals train.py's folds.
    assert sp.get("group_dtype") == "int", (f"split JSON group_dtype is {sp.get('group_dtype')!r}; "
        "regenerate with freeze_split.py --group-dtype int (str groups give a different partition)")
    return set(int(u) for u in sp["val_users"]), sp


def val_users_for_fold(state, seed, fold, folds=5):  # ORIGINAL A4 split -- kept for the record, no longer called
    """Users in the validation split of `fold` under the harness's StratifiedGroupKFold(seed)."""
    X, y_cat, userids, _ = load_next_data(state, EmbeddingEngine.CHECK2HGI)
    sgkf = StratifiedGroupKFold(n_splits=max(2, folds), shuffle=True, random_state=seed)
    splits = list(sgkf.split(np.zeros(len(y_cat)), y_cat, groups=userids))
    _, val_idx = splits[fold]
    return set(np.asarray(userids)[val_idx].tolist()), userids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--fold", type=int, required=True)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--split-json", required=True,
                    help="frozen dk_ovl split for (state, seed, fold), from scripts/integrity_v2/freeze_split.py")
    ap.add_argument("--out-engine", default=None,
                    help="new engine name for the remapped region table; default "
                         "check2hgi_design_k_resln_mae_l0_1_to_f<fold>. Must start with check2hgi_design_k "
                         "so p1_region_head_ablation.py resolves it without modification.")
    ap.add_argument("--pseudo-tag", default="a4dk", help="pseudo-state tag; must not collide with the original 'a4'")
    ap.add_argument("--device", default="cuda", help="passed to build_design_k_delaunay.py (the original A4 used cpu)")
    ap.add_argument("--cleanup-pseudo", action="store_true",
                    help="delete pseudo-state artifacts afterwards. OFF by default: nothing is deleted.")
    args = ap.parse_args()

    state_lc = args.state.lower()
    out_engine = args.out_engine or f"{V14_ENGINE}_to_f{args.fold}"
    assert out_engine.startswith("check2hgi_design_k") and out_engine != V14_ENGINE, out_engine
    assert args.pseudo_tag != "a4", "the original run used pseudo tag 'a4'; pick a fresh one"
    out_dir = _root / "output" / out_engine / state_lc
    out_emb = out_dir / "region_embeddings.parquet"
    if out_emb.exists():
        print(f"[a4_build] {out_emb} exists (this re-run's own output) — skip")
        return

    val_users, split_meta = val_users_from_split_json(args.split_json, args.state, args.seed, args.fold)
    raw = pd.read_parquet(IoPaths.get_city(args.state))
    train_mask = ~raw["userid"].isin(val_users)
    train_ck = raw[train_mask].reset_index(drop=True)
    assert not train_ck["userid"].isin(val_users).any(), "a validation user survived into the training check-ins"
    assert int((~train_mask).sum()) > 0, "no check-ins were removed -- split/userid dtype mismatch?"
    print(f"[a4_build] {args.state} seed={args.seed} fold={args.fold}: "
          f"train rows={len(train_ck)}/{len(raw)} ({train_mask.mean()*100:.1f}%), "
          f"val_users={len(val_users)}")

    pseudo = f"{args.state}_{args.pseudo_tag}_s{args.seed}_f{args.fold}"   # IoPaths capitalizes -> <State>_a4dk_...
    pseudo_lc = pseudo.lower()
    pseudo_ck_path = IoPaths.get_city(pseudo)
    # Pre-flight: every path this run creates must be new. Refuse rather than overwrite.
    _targets = [pseudo_ck_path, _root / "output" / "check2hgi" / pseudo_lc,
                _root / "output" / V14_ENGINE / pseudo_lc, _root / "output" / "hgi" / pseudo_lc, out_dir]
    _exist = [str(p) for p in _targets if p.exists() or p.is_symlink()]
    if _exist:
        raise SystemExit(f"[a4_build] refusing to overwrite existing paths: {_exist}")
    pseudo_ck_path.parent.mkdir(parents=True, exist_ok=True)
    train_ck.to_parquet(pseudo_ck_path, index=False)

    # design_k reads its HGI scaffolding (Delaunay edges, POI2Vec, HGI POI target) under
    # output/hgi/<pseudo>/ with STATE-NAMED files. Build a real pseudo dir with symlinks to the
    # full-HGI artifacts under the names design_k expects (reg_poi_aug uses state.capitalize()).
    hgi_full = _root / "output" / "hgi" / state_lc
    hgi_pseudo = _root / "output" / "hgi" / pseudo_lc
    hgi_pseudo.mkdir(parents=True, exist_ok=True)
    links = [
        (hgi_pseudo / "temp", hgi_full / "temp"),                       # edges.csv, pois.csv, ...
        (hgi_pseudo / "poi_embeddings.parquet", hgi_full / "poi_embeddings.parquet"),
        (hgi_pseudo / f"poi2vec_poi_embeddings_{pseudo.capitalize()}.csv",
         hgi_full / f"poi2vec_poi_embeddings_{args.state.capitalize()}.csv"),
    ]
    for link, target in links:
        if link.is_symlink() or link.exists():
            link.unlink()
        os.symlink(target, link)

    print(f"[a4_build] preprocess_check2hgi (train-only graph) for {pseudo}")
    preprocess_check2hgi(city=pseudo, city_shapefile=str(SHAPEFILES[state_lc]))

    print(f"[a4_build] design_k (train-only v14) for {pseudo}")
    cmd = [str(_root / ".venv" / "bin" / "python"),
           str(_root / "scripts" / "probe" / "build_design_k_delaunay.py"),
           "--state", pseudo, "--device", args.device, "--seed", str(args.seed), "--epochs", str(args.epochs)]
    r = subprocess.run(cmd, cwd=str(_root))
    if r.returncode != 0:
        raise SystemExit(f"[a4_build] design_k build failed rc={r.returncode}")

    # GEOID-remap train-only region emb -> full region index space.
    full_graph = pickle.load(open(_root / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt", "rb"))
    to_graph = pickle.load(open(_root / "output" / "check2hgi" / pseudo_lc / "temp" / "checkin_graph.pt", "rb"))
    full_r2i = full_graph["region_to_idx"]          # GEOID -> full_idx
    to_r2i = to_graph["region_to_idx"]              # GEOID -> trainonly_idx
    n_full = len(full_r2i)

    # region_embeddings.parquet schema: region_id (int idx) + reg_0..reg_{D-1} (the harness
    # convention — _load_region_embeddings: emb_cols = startswith("reg_"), sorted by region_id).
    to_emb_path = _root / "output" / V14_ENGINE / pseudo_lc / "region_embeddings.parquet"
    # Insurance: persist the raw train-only emb + the GEOID maps so a remap-logic change never
    # forces another (expensive) substrate rebuild — re-remap offline from these.
    import shutil as _sh
    out_dir.mkdir(parents=True, exist_ok=False)
    _sh.copy(to_emb_path, out_dir / "trainonly_raw_region_embeddings.parquet")
    # Also preserve the train-only POI-level embeddings (small) + the placeid map, so the CAT
    # transductivity axis can be measured on the in-coverage POI subset WITHOUT a third rebuild
    # (cat is the substrate-driven axis where transductive inflation actually bites — A4's live part).
    _poi_path = _root / "output" / V14_ENGINE / pseudo_lc / "poi_embeddings.parquet"
    if _poi_path.exists():
        _sh.copy(_poi_path, out_dir / "trainonly_poi_embeddings.parquet")
    with open(out_dir / "maps.pkl", "wb") as _mf:
        pickle.dump({"full_r2i": full_r2i, "to_r2i": to_r2i,
                     "to_placeid_to_idx": to_graph["placeid_to_idx"],
                     "full_placeid_to_idx": full_graph["placeid_to_idx"]}, _mf)
    to_emb_df = pd.read_parquet(to_emb_path).sort_values("region_id").reset_index(drop=True)
    emb_cols = [c for c in to_emb_df.columns if c.startswith("reg_")]
    dim = len(emb_cols)
    assert dim > 0, f"no reg_* cols in {to_emb_path} (cols={list(to_emb_df.columns)[:6]})"
    to_emb = to_emb_df[emb_cols].to_numpy(dtype=np.float32)     # row = trainonly region_id = to_idx

    full_emb = np.zeros((n_full, dim), dtype=np.float32)
    for geoid, to_idx in to_r2i.items():
        f_idx = full_r2i.get(geoid)
        if f_idx is None:
            continue
        full_emb[f_idx] = to_emb[to_idx]
    n_missing = sum(1 for g in full_r2i if g not in to_r2i)
    print(f"[a4_build] remap: full_regions={n_full} trainonly_regions={len(to_r2i)} dim={dim} "
          f"absent_from_train={n_missing} ({n_missing/n_full*100:.1f}%)")

    # Write in the harness schema (region_id + reg_*) so a4_eval reads it identically to a real substrate.
    out_df = pd.DataFrame(full_emb, columns=[f"reg_{i}" for i in range(dim)])
    out_df.insert(0, "region_id", np.arange(n_full))
    out_df.to_parquet(out_emb, index=False)
    print(f"[a4_build] wrote {out_emb}")
    vu = np.sort(np.asarray(sorted(val_users), dtype=np.int64))
    (out_dir / "build.json").write_text(json.dumps({
        "study": "integrity_v18_region_half", "generated_utc": datetime.now(timezone.utc).isoformat(),
        "command": " ".join(sys.argv), "state": state_lc, "seed": args.seed, "fold": args.fold,
        "split_json": str(args.split_json), "split_engine": split_meta.get("engine"),
        "split_val_idx_sha256": split_meta.get("val_idx_sha256"),
        "n_excluded_users": int(len(val_users)),
        "val_users_sha256": hashlib.sha256(vu.tobytes()).hexdigest(),
        "val_users_in_training_checkins": 0,   # asserted above
        "n_train_checkins": int(len(train_ck)), "n_checkins_full": int(len(raw)),
        "builder": "build_design_k_delaunay.py", "epochs": args.epochs, "device": args.device,
        "base_engine": V14_ENGINE, "pseudo_state": pseudo_lc,
        "remap": {"full_regions": n_full, "trainonly_regions": len(to_r2i), "absent_from_train": n_missing},
    }, indent=2))

    if args.cleanup_pseudo:
        import shutil
        for p in [pseudo_ck_path,
                  _root / "output" / "check2hgi" / pseudo_lc,
                  _root / "output" / V14_ENGINE / pseudo_lc,
                  hgi_pseudo]:
            if p.is_symlink():
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            elif p.exists():
                p.unlink()
        print(f"[a4_build] cleaned pseudo-state artifacts for {pseudo}")


if __name__ == "__main__":
    main()
