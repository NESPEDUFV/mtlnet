"""T2P.0 CHECKPOINT-REEVAL (advisor gold-standard, 2026-06-05) — axis decider.

Loads mtl_cv's ACTUAL reg-best-epoch weights (saved via --save-task-best-snapshots
as task_best_snapshots/fold{N}_reg_best.pt) and re-evaluates reg Acc@10 with a direct
next_forward + my verified top-k (plain + indist). This is INDEPENDENT of mtl_cv's
own eval/summary code.

  reeval ~= 52.90 (AL) -> mtl_cv's reg WEIGHTS are genuinely at 52.90 -> the deficit is
                          TRAINING (mtl_cv trains reg to a worse optimum) -> bisect.
  reeval ~= 62.88 (AL) -> the weights are actually good; mtl_cv's eval/summary
                          UNDER-REPORTED -> the deficit is a MEASUREMENT/reporting bug
                          (much cheaper fix; the "joint loop trains worse" framing collapses).

Run: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t2p0_ckpt_reeval.py \
       --state alabama --snap-dir results/<v14>/alabama/task_best_snapshots
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
import numpy as np, torch
from sklearn.model_selection import StratifiedGroupKFold
from configs.paths import IoPaths, EmbeddingEngine
from configs.globals import DEVICE
from data.folds import load_next_data
from data.inputs.region_sequence import build_region_sequence_tensor
from models.registry import create_model
from tasks.presets import CHECK2HGI_NEXT_REGION, resolve_task_set

V14 = "check2hgi_design_k_resln_mae_l0_1"
SEED, BS = 42, 2048
MODEL_PARAMS = dict(feature_size=64, shared_layer_size=256, num_heads=8,
                    num_layers=4, seq_length=9, num_shared_layers=4)


def topk(logits, y, train_lbl, k=10):
    tk = logits.topk(k, -1).indices
    plain = (tk == y.unsqueeze(-1)).any(-1).float().mean().item()
    m = torch.isin(y, train_lbl)
    idd = ((tk[m] == y[m].unsqueeze(-1)).any(-1).float().mean().item()) if int(m.sum()) else 0.0
    return plain, idd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--snap-dir", required=True)
    a = ap.parse_args()
    eng = EmbeddingEngine(V14)
    X, y_cat, userids, _ = load_next_data(a.state, eng)
    region_seq = build_region_sequence_tensor(a.state, region_engine=eng, seq_engine=eng).float()
    rdf = IoPaths.load_next_region(a.state, eng)
    y_region = torch.from_numpy(np.ascontiguousarray(rdf["region_idx"].to_numpy(np.int64)))
    n_reg = int(y_region.max().item()) + 1
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)

    res = []
    for fold, (tr, va) in enumerate(sgkf.split(np.asarray(X), np.asarray(y_cat), groups=np.asarray(userids))):
        snap = Path(a.snap_dir) / f"fold{fold+1}_reg_best.pt"
        if not snap.exists():
            print(f"  fold{fold+1}: MISSING {snap}"); continue
        ts = resolve_task_set(CHECK2HGI_NEXT_REGION, task_b_num_classes=n_reg,
                              task_b_head_factory="next_stan_flow_dualtower",
                              task_b_head_params={"raw_embed_dim": 64, "fusion_mode": "private_only",
                                                  "freeze_alpha": True, "alpha_init": 0.0})
        model = create_model("mtlnet_crossattn_dualtower", task_set=ts, num_classes=n_reg, **MODEL_PARAMS).to(DEVICE)
        sd = torch.load(snap, map_location="cpu", weights_only=False)
        sd = sd.get("state_dict", sd) if isinstance(sd, dict) else sd
        missing, unexpected = model.load_state_dict(sd, strict=False)
        npm = [k for k in missing if "next_poi" in k]
        if npm:
            print(f"  fold{fold+1}: WARN missing next_poi keys: {npm[:4]}")
        model.eval()
        va_x, va_y = region_seq[va].to(DEVICE), y_region[va].to(DEVICE)
        train_lbl = torch.as_tensor(sorted(set(y_region[tr].tolist())), dtype=va_y.dtype, device=DEVICE)
        with torch.no_grad():
            lg = []
            for i in range(0, va_x.size(0), BS):
                with torch.autocast(DEVICE.type, dtype=torch.float16) if DEVICE.type == "cuda" else _null():
                    lg.append(model.next_forward(va_x[i:i+BS]).float())
            lg = torch.cat(lg, 0)
            plain, idd = topk(lg, va_y, train_lbl, 10)
        res.append((plain*100, idd*100))
        print(f"  fold{fold+1}: reeval reg Acc@10 plain={plain*100:.2f} indist={idd*100:.2f} "
              f"(missing={len(missing)} unexpected={len(unexpected)})")
    if res:
        p = np.mean([r[0] for r in res]); ii = np.mean([r[1] for r in res])
        print(f"\n[{a.state}] CHECKPOINT-REEVAL of mtl_cv reg-best weights: "
              f"plain={p:.2f} indist={ii:.2f} (n={len(res)} folds)")
        print(f"  >>> mtl_cv REPORTED 52.90(AL); my reconstruction 62.88(AL). "
              f"reeval~=53 => TRAINING axis; reeval~=63 => MEASUREMENT artifact.")


class _null:
    def __enter__(self): return None
    def __exit__(self, *a): return False


if __name__ == "__main__":
    main()
