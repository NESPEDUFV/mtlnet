"""D2 unit equivalence (CPU, no training): eager (old code path) vs lazy (new) single-task NEXT folds on AL v18.
Checks per fold: split indices, tensor equality, loader config; and that fold construction leaves the global
torch / numpy / python RNG state untouched in both modes. Run with the NEW clone on PYTHONPATH."""
import random, sys, numpy as np, torch
from configs.paths import EmbeddingEngine
from data.folds import FoldCreator, TaskType
eng = EmbeddingEngine("check2hgi_v18")
def rng_state():
    return (torch.get_rng_state().clone(), np.random.get_state()[1].copy(), random.getstate())
def same_rng(a, b):
    return torch.equal(a[0], b[0]) and np.array_equal(a[1], b[1]) and a[2] == b[2]
torch.manual_seed(0); np.random.seed(0); random.seed(0)
s0 = rng_state()
eager = FoldCreator(TaskType.NEXT, n_splits=5, batch_size=8192, seed=0, lazy_single_task=False).create_folds("alabama", eng)
s1 = rng_state()
lazy_fc = FoldCreator(TaskType.NEXT, n_splits=5, batch_size=8192, seed=0, lazy_single_task=True)
lazy = lazy_fc.create_folds("alabama", eng)
s2 = rng_state()
print("eager type:", type(eager).__name__, "| lazy type:", type(lazy).__name__, "| len", len(eager), len(lazy))
print("RNG untouched by eager construction (all 5 folds):", same_rng(s0, s1))
print("RNG untouched by lazy create_folds:", same_rng(s1, s2))
ok = True
for k in range(5):
    a, b = eager[k].next, lazy[k].next
    s3 = rng_state(); _ = lazy[k]; s4 = rng_state()
    checks = {
        "train_x": torch.equal(a.train.x, b.train.x), "train_y": torch.equal(a.train.y, b.train.y),
        "val_x": torch.equal(a.val.x, b.val.x), "val_y": torch.equal(a.val.y, b.val.y),
        "batch": a.train.dataloader.batch_size == b.train.dataloader.batch_size == 8192,
        "sampler": type(a.train.dataloader.sampler).__name__ == type(b.train.dataloader.sampler).__name__ == "RandomSampler",
        "val_sampler": type(a.val.dataloader.sampler).__name__ == type(b.val.dataloader.sampler).__name__ == "SequentialSampler",
        "gen_none": a.train.dataloader.generator is None and b.train.dataloader.generator is None,
        "rng_untouched_by_lazy_build": same_rng(s3, s4),
    }
    ok &= all(checks.values())
    print(f"fold {k}: n_train={len(a.train.y)} n_val={len(a.val.y)}", {kk: v for kk, v in checks.items() if not v} or "ALL EQUAL")
fi_e = FoldCreator  # fold index records
print("UNIT EQUIVALENCE:", "PASS" if ok and same_rng(s0, s1) and same_rng(s1, s2) else "FAIL")
