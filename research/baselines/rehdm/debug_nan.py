"""Single-batch NaN tracer for ReHDM."""
import json
import sys
from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from research.baselines.rehdm.model import ReHDM, ReHDMConfig
from research.baselines.rehdm.train import (
    TrajectoryStore, ReHDMDataset, make_collate, _move, set_seed
)
from torch.utils.data import DataLoader

set_seed(42)
device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
print(f"device={device}")

in_dir = Path("/Users/vitor/Desktop/mestrado/ingred/output/baselines/rehdm/alabama")
df = pd.read_parquet(in_dir / "inputs.parquet")
vocab = json.loads((in_dir / "vocab.json").read_text())

store = TrajectoryStore(df, max_len=20)
cfg = ReHDMConfig(
    n_users=vocab["n_users"], n_pois=vocab["n_pois"],
    n_categories=vocab["n_categories"], n_quadkeys=vocab["n_quadkeys"],
    n_regions=vocab["n_regions"],
)
model = ReHDM(cfg).to(device)

loader = DataLoader(
    ReHDMDataset(store, store.train_ids), batch_size=32, shuffle=False,
    collate_fn=make_collate(store, 4, 4, training=True),
)
optim = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
sched = torch.optim.lr_scheduler.OneCycleLR(optim, max_lr=1e-3, total_steps=len(loader))
torch.autograd.set_detect_anomaly(True)


def chk(name, t):
    if t is None:
        print(f"  {name}: None"); return
    nan = torch.isnan(t).any().item()
    inf = torch.isinf(t).any().item()
    print(f"  {name}: shape={tuple(t.shape)} nan={nan} inf={inf} "
          f"min={t.min().item():.3g} max={t.max().item():.3g}")


for bi, batch in enumerate(loader):
    print(f"\n=== batch {bi} ===")
    t_ids, t_mask, c_ids, c_mask, adj, et, tb, db, y = batch
    t_ids = _move(t_ids, device); t_mask = t_mask.to(device); y = y.to(device)
    if c_ids is not None:
        c_ids = _move(c_ids, device); c_mask = c_mask.to(device)
        adj = adj.to(device); et = et.to(device)
        tb = tb.to(device); db = db.to(device)
        chk("c_mask", c_mask); chk("adj", adj)

    logits = model(t_ids, t_mask, c_ids, c_mask, adj, et, tb, db)
    if torch.isnan(logits).any():
        print(f"!!! batch {bi}: logits NaN — adj sum<0?={int((adj.sum(1)==0).sum().item()) if adj is not None else 'na'}")
        chk("logits", logits)
        break
    loss = F.cross_entropy(logits, y)
    if torch.isnan(loss):
        print(f"!!! batch {bi}: loss NaN")
        chk("logits", logits); chk("y", y.float())
        break
    optim.zero_grad()
    loss.backward()
    bad = [n for n, p in model.named_parameters() if p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any())]
    if bad:
        print(f"!!! batch {bi}: NaN/Inf grads in: {bad[:5]}")
        break
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optim.step(); sched.step()
    if bi % 25 == 0:
        print(f"batch {bi}: loss={loss.item():.4f} adj0rows={int((adj.sum(1)==0).sum().item()) if adj is not None else 0}")
