"""The primary statistic: does the reported predictor's performance DEPEND on the target visit?

Levels 0 and 1 of the ladder measure properties of the representation. This script measures the
thing the dissertation actually claims: a metric. It trains the dedicated category model on the
intact reported representation and then evaluates on validation windows whose input vectors were
recomputed under an intervention on the target visit.

There are TWO training regimes and they differ exactly here. In TRANSFER the head is trained once,
frozen, and re-evaluated, so only the inputs change and a drop cannot come from a different fit or
initialization. In MATCHED the head is deliberately RETRAINED per arm and per seed, because its
question requires it, so a matched drop does involve a different fit; that is controlled by holding
the seeds, the rows, and the labels identical across arms rather than by avoiding retraining.

TWO QUESTIONS THAT LOOK THE SAME AND ARE NOT. A frozen head evaluated on intervened inputs is
being fed vectors from a distribution it never trained on, so it can lose accuracy even if the
destroyed information was useless to it. That measures RELIANCE, not the honest cost of not having
the information. The two are separated by training regime:

  transfer  head trained on intact, evaluated on intervened. Answers "does the fitted predictor
            lean on the target's own features?" Confounded with distribution shift, on purpose:
            it is an upper bound on reliance.
  matched   head RETRAINED on the intervened (or strict) representation and evaluated on it.
            Answers the question the dissertation needs: "what does the reported number become
            under a protocol that never sees the future?" No distribution shift, because train and
            test come from the same representation.

A large transfer drop with a small matched drop means the predictor was using the channel but did
not need it, and the reported metric is not inflated. A large matched drop means the reported number
genuinely depended on information unavailable at prediction time. Only the matched contrast may be
quoted against the reported result.

PLACEBOS. Two arms exist to catch a pipeline that would produce a drop from any perturbation at all:
a far-future intervention outside every slot's receptive field, whose drop must be zero, and an
observed-history intervention, which gives the scale of "how much does the head care about one
visit" for comparison with the target's contribution.

Intervals come from a user-clustered bootstrap, because windows of one user are not independent.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "scripts"))

from configs.globals import CATEGORIES_MAP           # noqa: E402
from integrity_v2.probe_ladder import build_window_matrix, load_arm_windows, _CAT  # noqa: E402

WINDOW = 9
N_CAT = 7


class GRUCat(torch.nn.Module):
    """The dedicated category model, in the shape the reported runs use: a GRU over the nine
    check-in vectors with a linear classifier on the final state. Kept deliberately small and
    self-contained so the counterfactual measures the REPRESENTATION, not a head's capacity."""

    def __init__(self, d_in: int = 64, hidden: int = 128, n_classes: int = N_CAT, dropout: float = 0.1):
        super().__init__()
        self.gru = torch.nn.GRU(d_in, hidden, num_layers=1, batch_first=True)
        self.drop = torch.nn.Dropout(dropout)
        self.out = torch.nn.Linear(hidden, n_classes)

    def forward(self, x):
        h, _ = self.gru(x)
        return self.out(self.drop(h[:, -1]))


def train_head(Xtr, ytr, seed: int, epochs: int = 30, bs: int = 2048,
               device: str = "cuda") -> GRUCat:
    torch.manual_seed(seed); np.random.seed(seed)
    dev = torch.device(device)
    model = GRUCat(d_in=Xtr.shape[2]).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-4)
    xt = torch.as_tensor(Xtr, dtype=torch.float32)
    yt = torch.as_tensor(ytr, dtype=torch.long)
    n = len(xt)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=3e-3, total_steps=max(1, epochs * ((n + bs - 1) // bs)))
    model.train()
    for _ in range(epochs):
        perm = torch.randperm(n)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            opt.zero_grad()
            loss = F.cross_entropy(model(xt[idx].to(dev)), yt[idx].to(dev))
            loss.backward(); opt.step(); sched.step()
    model.eval()
    return model


@torch.no_grad()
def evaluate(model: GRUCat, X, y, device: str = "cuda", bs: int = 8192) -> tuple[float, np.ndarray]:
    dev = torch.device(device)
    preds = []
    for i in range(0, len(X), bs):
        xb = torch.as_tensor(X[i:i + bs], dtype=torch.float32).to(dev)
        preds.append(model(xb).argmax(1).cpu().numpy())
    pred = np.concatenate(preds)
    return float(f1_score(y, pred, average="macro", zero_division=0)), pred


def clustered_bootstrap(y, pred_a, pred_b, users, n_boot: int = 1000, seed: int = 0) -> dict:
    """Bootstrap the paired metric difference by resampling USERS, not windows."""
    rng = np.random.default_rng(seed)
    uu = np.unique(users)
    idx_by_user = {u: np.where(users == u)[0] for u in uu}
    diffs = []
    for _ in range(n_boot):
        pick = rng.choice(uu, size=len(uu), replace=True)
        rows = np.concatenate([idx_by_user[u] for u in pick])
        fa = f1_score(y[rows], pred_a[rows], average="macro", zero_division=0)
        fb = f1_score(y[rows], pred_b[rows], average="macro", zero_division=0)
        diffs.append(fa - fb)
    d = np.asarray(diffs)
    return {"mean": float(d.mean()), "sd": float(d.std()),
            "ci95_lo": float(np.percentile(d, 2.5)), "ci95_hi": float(np.percentile(d, 97.5)),
            "n_boot": n_boot, "resampling_unit": "user"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--intact", required=True, help="embeddings parquet for the reported readout")
    ap.add_argument("--intervened", nargs="+", required=True,
                    help="label=embeddings.parquet, each an intervened recomputation")
    ap.add_argument("--next-parquet", required=True)
    ap.add_argument("--split", required=True)
    ap.add_argument("--head-seeds", type=int, default=3)
    ap.add_argument("--no-matched", action="store_true",
                    help="skip the retrained (matched) regime; transfer only")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    split = json.loads(Path(args.split).read_text())
    nxt_all = pd.read_parquet(args.next_parquet)

    def windows(path: str) -> dict:
        return load_arm_windows(path, nxt_all)

    W0 = windows(args.intact)
    tr_u = np.asarray(split["train_users"]); va_u = np.asarray(split["val_users"])
    uu = W0["userid"]
    tr = np.where(np.isin(uu, tr_u))[0]; te = np.where(np.isin(uu, va_u))[0]
    assert len(tr) and len(te), "the intact arm must cover both split sides"
    assert np.intersect1d(uu[tr], uu[te]).size == 0

    res = {
        "study": "check2hgi_integrity_v2 / frozen-predictor counterfactual",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "command": " ".join(sys.argv), "state": args.state,
        "split": {k: split[k] for k in ("seed", "fold", "n_folds", "engine") if k in split},
        "design": ("two regimes per arm. TRANSFER: heads trained once on the intact representation "
                   "and frozen, then evaluated here -- an upper bound on reliance, confounded with "
                   "distribution shift by construction. MATCHED: heads retrained on this "
                   "representation, so train and test agree -- this is the only contrast quotable "
                   "against the reported result. Same rows, same labels, same seeds throughout."),
        "quotable_contrast": "matched",
        "metric": "next-category macro-F1", "n_train_rows": int(len(tr)), "n_val_rows": int(len(te)),
        "arms": {},
    }
    print(f"[cf] {args.state}: train {len(tr)} rows, val {len(te)} rows", flush=True)

    heads = []
    for s in range(args.head_seeds):
        h = train_head(W0["seq"][tr], W0["y"][tr], seed=s, epochs=args.epochs, device=args.device)
        f1, pred = evaluate(h, W0["seq"][te], W0["y"][te], device=args.device)
        heads.append((h, f1, pred))
        print(f"  head seed {s}: intact macro-F1 {f1:.4f}", flush=True)
    res["intact"] = {"per_seed_macro_f1": [f for _, f, _ in heads],
                     "mean_macro_f1": float(np.mean([f for _, f, _ in heads]))}

    intact_mean = float(np.mean([f for _, f, _ in heads]))
    for spec in args.intervened:
        label, path = spec.split("=", 1)
        Wi = windows(path)
        # Arms need not carry identical window sets: a per-visit table and a per-window readout are
        # built from different constructions and a user subsample can differ at the margins. What
        # the comparison REQUIRES is that both sides be scored on the same rows, so intersect rather
        # than abort, and record how many windows each contributed.
        if not np.array_equal(Wi["rows"], W0["rows"]):
            common = np.intersect1d(Wi["rows"], W0["rows"])
            assert common.size > 0, f"{label} shares no windows with the intact arm"
            _ret = common.size / max(min(Wi["rows"].size, W0["rows"].size), 1)
            assert _ret >= 0.95, (
                f"{label}: pairing kept only {common.size} of {min(Wi['rows'].size, W0['rows'].size)} "
                f"windows ({_ret:.1%}); the arms are not built on a common basis -- refusing to report")
            ki = np.isin(Wi["rows"], common); k0 = np.isin(W0["rows"], common)
            oi = np.argsort(Wi["rows"][ki], kind="mergesort")
            o0 = np.argsort(W0["rows"][k0], kind="mergesort")
            Wi = {k: (v[ki][oi] if isinstance(v, np.ndarray) else v) for k, v in Wi.items()}
            W0p = {k: (v[k0][o0] if isinstance(v, np.ndarray) else v) for k, v in W0.items()}
            n_dropped = int(W0["rows"].size - common.size)
        else:
            W0p, n_dropped = W0, 0
        assert np.array_equal(Wi["y"], W0p["y"]), f"{label} labels do not align after pairing"
        assert np.array_equal(Wi["userid"], W0p["userid"]), \
            f"{label} user ids do not align after pairing; the arms index different frames"
        # every metric for this arm is computed against the paired intact arm, not the full one
        tr_a = np.where(np.isin(W0p["userid"], np.asarray(split["train_users"])))[0]
        te_a = np.where(np.isin(W0p["userid"], np.asarray(split["val_users"])))[0]

        # The intact reference is re-evaluated on the PAIRED rows, so the drop is a like-for-like
        # difference. Using the full-arm intact mean against a paired arm would fold the change of
        # row set into the reported effect.
        uu_a = W0p["userid"]
        base_vals, base_preds = [], []
        for (h, f1_full, pred_full) in heads:
            f1_b, pred_b = evaluate(h, W0p["seq"][te_a], W0p["y"][te_a], device=args.device)
            base_vals.append(f1_b); base_preds.append(pred_b)
        base_mean = float(np.mean(base_vals))

        # transfer: the frozen intact-trained heads, evaluated on this representation
        t_vals, boots = [], []
        for (h, _, _), pred_b in zip(heads, base_preds):
            f1_i, pred_i = evaluate(h, Wi["seq"][te_a], Wi["y"][te_a], device=args.device)
            t_vals.append(f1_i)
            boots.append(clustered_bootstrap(W0p["y"][te_a], pred_b, pred_i, uu_a[te_a]))
        t_drop = base_mean - float(np.mean(t_vals))

        entry = {
            "embeddings": path,
            "transfer": {
                "regime": "head trained on intact, evaluated here (upper bound on reliance)",
                "per_seed_macro_f1": t_vals, "mean_macro_f1": float(np.mean(t_vals)),
                "drop_points": t_drop * 100,
                "bootstrap_first_seed": boots[0],
                "bootstrap_ci95_points": [boots[0]["ci95_lo"] * 100, boots[0]["ci95_hi"] * 100],
            }}
        line = (f"  {label}: transfer {np.mean(t_vals):.4f} (drop {t_drop*100:+.2f} pts, "
                f"CI {boots[0]['ci95_lo']*100:+.2f} to {boots[0]['ci95_hi']*100:+.2f})")

        if not args.no_matched:
            # matched: retrain on THIS representation, so train and test agree
            m_vals, m_boots = [], []
            for s in range(args.head_seeds):
                hm = train_head(Wi["seq"][tr_a], Wi["y"][tr_a], seed=s, epochs=args.epochs,
                                device=args.device)
                f1_m, pred_m = evaluate(hm, Wi["seq"][te_a], Wi["y"][te_a], device=args.device)
                m_vals.append(f1_m)
                m_boots.append(clustered_bootstrap(W0p["y"][te_a], base_preds[s], pred_m, uu_a[te_a]))
            m_drop = base_mean - float(np.mean(m_vals))
            entry["matched"] = {
                "regime": "head RETRAINED on this representation (the quotable contrast)",
                "per_seed_macro_f1": m_vals, "mean_macro_f1": float(np.mean(m_vals)),
                "drop_points": m_drop * 100,
                "bootstrap_first_seed": m_boots[0],
                "bootstrap_ci95_points": [m_boots[0]["ci95_lo"] * 100, m_boots[0]["ci95_hi"] * 100],
            }
            entry["distribution_shift_share_points"] = (t_drop - m_drop) * 100
        entry["paired_windows"] = int(W0p["rows"].size)
        entry["intact_windows_dropped_by_pairing"] = n_dropped
        entry["intact_reference_on_paired_rows"] = base_mean
        if n_dropped:
            entry["pairing_note"] = (
                f"this arm shares {W0p['rows'].size} of the intact arm's {W0['rows'].size} windows; "
                "both sides were reduced to the shared set and the intact reference re-evaluated "
                f"on them ({base_mean:.4f}) so the drop is like-for-like")
            line += (f" | matched {np.mean(m_vals):.4f} (drop {m_drop*100:+.2f} pts, "
                     f"CI {m_boots[0]['ci95_lo']*100:+.2f} to {m_boots[0]['ci95_hi']*100:+.2f})")

        res["arms"][label] = entry
        print(line, flush=True)

    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, indent=2))
    print(f"[cf] wrote {outp}")


if __name__ == "__main__":
    main()
