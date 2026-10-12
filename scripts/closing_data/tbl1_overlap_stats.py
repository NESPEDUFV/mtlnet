"""Blocker 3: Tbl 1 overlap window counts + seq-len + sparsity (CPU-only recompute).

Validates against the one on-disk dk_ovl parquet (Alabama = 96,326) before
trusting recompute for the other states.
"""
import sys
import pandas as pd
sys.path.insert(0, '.')
from src.data.inputs.core import generate_sequences

WINDOW = 9
MIN_SEQ = 10
STRIDE = 1
EMIT_TAIL = False

# state token -> checkins parquet filename
GOWALLA = {
    'alabama': 'Alabama.parquet',
    'arizona': 'Arizona.parquet',
    'florida': 'Florida.parquet',
    'california': 'California.parquet',
    'texas': 'Texas.parquet',
}
CKDIR = 'data/checkins/'


def overlap_window_count(places_by_user):
    total = 0
    for places in places_by_user:
        total += len(generate_sequences(
            places, window_size=WINDOW, stride=STRIDE,
            min_sequence_length=MIN_SEQ, emit_tail=EMIT_TAIL,
        ))
    return total


def stats_for_state(name, fname):
    df = pd.read_parquet(CKDIR + fname)
    df = df.sort_values(['userid', 'datetime'], kind='mergesort')
    grp = df.groupby('userid')['placeid']
    places_by_user = [s.tolist() for _, s in grp]

    n_checkins = len(df)
    n_users = df['userid'].nunique()
    n_pois = df['placeid'].nunique()
    sizes = grp.size()
    seq_max = int(sizes.max())
    seq_mean = float(sizes.mean())
    sparsity = 1.0 - n_checkins / (n_users * n_pois)
    windows = overlap_window_count(places_by_user)

    return dict(state=name, checkins=n_checkins, users=n_users, pois=n_pois,
                seq_max=seq_max, seq_mean=round(seq_mean, 2),
                sparsity=round(sparsity, 6), windows=windows)


if __name__ == '__main__':
    # 1) validate Alabama against on-disk parquet
    truth = len(pd.read_parquet(
        'output/check2hgi_dk_ovl/alabama/input/next.parquet'))
    al = stats_for_state('alabama', 'Alabama.parquet')
    print(f"VALIDATION alabama: recompute={al['windows']}  ondisk={truth}  "
          f"MATCH={al['windows']==truth}")
    print(al)
    if al['windows'] != truth:
        print("!!! recompute does not match on-disk; aborting other states")
        sys.exit(1)

    # 2) other Gowalla states
    rows = [al]
    for name, fname in GOWALLA.items():
        if name == 'alabama':
            continue
        print(f"... computing {name}", flush=True)
        rows.append(stats_for_state(name, fname))

    print("\n=== Gowalla T1 (overlap, stride-1, MIN_SEQ=10, emit_tail=False) ===")
    cols = ['state', 'users', 'checkins', 'pois', 'seq_max', 'seq_mean',
            'sparsity', 'windows']
    print('\t'.join(cols))
    for r in rows:
        print('\t'.join(str(r[c]) for c in cols))

    import json
    out = 'scratchpad/t1_gowalla.json' if __import__('os').path.isdir('scratchpad') else '/tmp/t1_gowalla.json'
    with open(out, 'w') as f:
        json.dump(rows, f, indent=2)
    print('saved', out)
