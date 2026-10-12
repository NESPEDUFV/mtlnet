"""D2 e2e comparison: old vs new (and old vs old) per-epoch CSVs must be identical; patch must have been exercised."""
import glob, sys, pandas as pd
D = "/Users/vitor/d2_scratch"
def rundir(tag):
    r = glob.glob(f"{D}/results/{tag}/check2hgi_v18/alabama/next_*"); assert len(r) == 1, (tag, r); return r[0]
def log_ok(tag):
    t = open(f"{D}/logs/{tag}/out.log").read()
    return "Generating folds on the fly" in t
def frames(tag):
    r = rundir(tag); out = {}
    for f in sorted(glob.glob(f"{r}/metrics/*.csv")): out[f.split("/")[-1]] = pd.read_csv(f)
    return out
def same(a, b, name):
    fa, fb = frames(a), frames(b); ok = set(fa) == set(fb)
    for k in fa:
        if k in fb:
            eq = fa[k].equals(fb[k]); ok &= eq
            if not eq:
                d = (fa[k].select_dtypes("number") - fb[k].select_dtypes("number")).abs().max().max()
                print(f"  {name} {k}: DIFFERS (max |Δ| {d})")
    best = lambda t: (frames(t)["fold1_next_val.csv"].f1.max() * 100)
    print(f"{name}: per-epoch CSVs identical={ok} | files {sorted(fa)} | best F1 {best(a):.4f} vs {best(b):.4f}")
    return ok
for t in ("old_f0", "new_f0", "old_f3", "new_f3", "old_f0_rep"):
    print(t, "exercised 'Generating folds on the fly':", log_ok(t), "|", open(f"{D}/logs/{t}/RUN.txt").read().split("\n")[-2])
r = [same("old_f0", "new_f0", "f0 old-vs-new"), same("old_f3", "new_f3", "f3 old-vs-new"), same("old_f0", "old_f0_rep", "f0 old-vs-old (control)")]
print("D2 E2E:", "PASS" if all(r) else "SEE DIFFS")
