"""
Regression tests for the memory-bounded (streaming) next-input build.

These pin the behaviour that the chunked ``NextInputStreamWriter`` produces a
parquet that is *content byte-identical* to the legacy single-shot
``save_next_input_dataframe`` write (same schema names, dtypes, column order,
row order, and bit-exact float32 embeddings), in both the single-chunk and the
multi-chunk regimes — so a large stride-1 build no longer OOMs the box yet the
small/frozen builds stay unchanged.

Pure synthetic data; never touches a real state.
"""
import numpy as np
import pandas as pd
import pytest

from data.inputs.core import (
    NextInputStreamWriter,
    estimate_next_build_ram_gb,
    check_next_build_ram,
)


def _legacy_write(results, num_features, path):
    """Reconstruct the legacy save_next_input_dataframe write exactly."""
    cols = [str(i) for i in range(num_features)]
    arr = np.array(results)  # (N, num_features+2) object/<U..>
    df = pd.DataFrame(arr[:, :num_features].astype(np.float32), columns=cols)
    df["next_category"] = arr[:, num_features].tolist()
    df["userid"] = arr[:, num_features + 1].tolist()
    df.to_parquet(path, index=False)


def _make_rows(n, num_features, seed=0):
    """Build legacy-style <U32 rows: float embeddings + str cat + str userid."""
    rng = np.random.default_rng(seed)
    cats = ["Food", "Shopping", "Outdoors", "Community"]
    rows = []
    for i in range(n):
        emb = rng.standard_normal(num_features).astype(np.float32)
        cat = cats[i % len(cats)]
        uid = str(i % 37)
        # This concatenation upcasts to <U32 — exactly the legacy per-row format.
        rows.append(np.concatenate([emb, [cat, uid]]))
    return rows


@pytest.mark.parametrize("chunk_rows", [10_000, 100, 7])
def test_streaming_matches_legacy_content(tmp_path, chunk_rows):
    num_features = 16
    n = 503  # not a multiple of any chunk size -> exercises remainder flush
    rows = _make_rows(n, num_features, seed=42)

    legacy_path = tmp_path / "legacy.parquet"
    stream_path = tmp_path / "stream.parquet"
    _legacy_write(rows, num_features, legacy_path)

    w = NextInputStreamWriter(stream_path, num_features, chunk_rows=chunk_rows)
    for r in rows:
        w.add(np.asarray(r[:num_features], dtype=np.float32), r[num_features], r[num_features + 1])
    total = w.close()
    assert total == n

    a = pd.read_parquet(legacy_path)
    b = pd.read_parquet(stream_path)

    assert list(a.columns) == list(b.columns)
    assert a.shape == b.shape
    fc = [c for c in a.columns if c.isdigit()]
    # bit-exact float32 (view as uint32) — not just close
    assert np.array_equal(
        a[fc].values.astype(np.float32).view(np.uint32),
        b[fc].values.astype(np.float32).view(np.uint32),
    )
    assert (a["next_category"].values == b["next_category"].values).all()
    assert (a["userid"].astype(str).values == b["userid"].astype(str).values).all()
    assert str(a["0"].dtype) == str(b["0"].dtype)
    assert str(a["next_category"].dtype) == str(b["next_category"].dtype)
    assert str(a["userid"].dtype) == str(b["userid"].dtype)


def test_streaming_empty_input(tmp_path):
    num_features = 16
    w = NextInputStreamWriter(tmp_path / "empty.parquet", num_features)
    assert w.close() == 0
    df = pd.read_parquet(tmp_path / "empty.parquet")
    assert len(df) == 0
    assert list(df.columns) == [str(i) for i in range(num_features)] + ["next_category", "userid"]


def test_ram_estimate_and_guard():
    # legacy 2x <U32 estimate: 3M rows x 576 feats ~ 400+ GB (the box-OOM driver)
    est = estimate_next_build_ram_gb(3_000_000, 576)
    assert est > 300  # ~413 GB

    # streaming guard never raises (build is O(chunk)).
    check_next_build_ram(3_000_000, 576, streaming=True)

    # non-streaming guard raises with an absurd N + tiny headroom.
    with pytest.raises(MemoryError):
        check_next_build_ram(10**9, 576, streaming=False, headroom_gb=8)
