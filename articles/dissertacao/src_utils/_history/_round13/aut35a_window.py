"""AUT-35a instrument: report the check-in time window of a parquet set.

Usage:
  python3 _tmp_window.py <timestamp_column> <parquet> [<parquet> ...]

Prints, per file and for the union: non-null count, null count, min, max,
and a per-year histogram. The per-year histogram is the part that matters:
a claim of the form "this dataset is 2017-2018" is FALSIFIABLE only if the
instrument would show non-zero counts in other years, so the histogram is
printed in full and never summarized to a range.
"""
import sys
import collections
import pyarrow.parquet as pq

col = sys.argv[1]
files = sys.argv[2:]

union = collections.Counter()
u_nonnull = 0
u_null = 0
u_min = None
u_max = None

for f in files:
    t = pq.read_table(f, columns=[col])
    a = t.column(col).to_pylist()
    nonnull = [x for x in a if x is not None and str(x).strip() != ""]
    nulls = len(a) - len(nonnull)
    years = collections.Counter(str(x)[:4] for x in nonnull)
    mn = min(nonnull) if nonnull else None
    mx = max(nonnull) if nonnull else None
    print("FILE " + f)
    print("  rows=" + str(len(a)) + " nonnull=" + str(len(nonnull)) + " null_or_blank=" + str(nulls))
    print("  min=" + repr(mn))
    print("  max=" + repr(mx))
    print("  years=" + repr(sorted(years.items())))
    union.update(years)
    u_nonnull += len(nonnull)
    u_null += nulls
    if mn is not None:
        u_min = mn if u_min is None else min(u_min, mn)
        u_max = mx if u_max is None else max(u_max, mx)

print("UNION nonnull=" + str(u_nonnull) + " null_or_blank=" + str(u_null))
print("UNION min=" + repr(u_min))
print("UNION max=" + repr(u_max))
print("UNION years=" + repr(sorted(union.items())))
