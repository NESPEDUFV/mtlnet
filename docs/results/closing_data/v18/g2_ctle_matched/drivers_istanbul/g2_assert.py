"""G2 CTLE per-fold assertions. usage: g2_assert.py <state> <fold>"""
import sys, re, hashlib, numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from configs.paths import EmbeddingEngine, IoPaths
from data.folds import load_next_data
st, F = sys.argv[1], int(sys.argv[2])
d = pd.read_parquet(IoPaths.get_next(st, EmbeddingEngine("check2hgi_dk_ovl")), columns=["userid", "next_category"])
x = pd.read_parquet(IoPaths.get_next(st, EmbeddingEngine("check2hgi_ctle")), columns=["userid", "next_category"])
assert len(x) == len(d) and (x.userid.astype("int64").values == d.userid.astype("int64").values).all() and (x.next_category.values == d.next_category.values).all(), "CTLE rows != dk_ovl rows"
import os; mk = open(os.path.join(os.environ["OUTPUT_DIR"], "check2hgi_ctle", st, "CTLE_FOLD.txt")).read()
assert f"fold={F}" in mk and "split_engine=check2hgi_dk_ovl" in mk, mk
want = re.search(r"val_users_sha256=([0-9a-f]{64})", mk).group(1)
X, y, u, _ = load_next_data(st, EmbeddingEngine("check2hgi_ctle")); u = np.asarray(u).astype(np.int64)
tr, va = list(StratifiedGroupKFold(5, shuffle=True, random_state=0).split(np.zeros(len(y)), y, u))[F]
got = hashlib.sha256(np.sort(np.unique(u[va])).astype(np.int64).tobytes()).hexdigest()
assert got == want, f"train.py fold {F} val users sha {got} != CTLE_FOLD {want}"
print(f"G2 OK {st} f{F}: rows == dk_ovl ({len(x)}), train.py fold val-user sha == CTLE_FOLD.txt ({want[:12]}...), n_val_rows={len(va)}")
