"""Unit tests for ``data.fold_digest`` (AUDIT-C8).

The digest is the precondition contract for paired statistical tests
across runs: identical partition → identical digest, any change
(seed, regenerated parquet → different row order, different split
algorithm) → different digest.
"""

from __future__ import annotations

from data.fold_digest import compute_fold_set_digest, digest_compatible


def _manifest(fold_idx, train_users, val_users):
    return {
        "fold_idx": fold_idx,
        "train_users": list(train_users),
        "val_users": list(val_users),
    }


def test_identical_partitions_match():
    a = [
        _manifest(0, [1, 2, 3], [4, 5]),
        _manifest(1, [4, 5], [1, 2, 3]),
    ]
    b = [
        _manifest(0, [1, 2, 3], [4, 5]),
        _manifest(1, [4, 5], [1, 2, 3]),
    ]
    assert compute_fold_set_digest(a) == compute_fold_set_digest(b)


def test_userid_order_doesnt_matter():
    a = [_manifest(0, [1, 2, 3], [4, 5])]
    b = [_manifest(0, [3, 1, 2], [5, 4])]
    assert compute_fold_set_digest(a) == compute_fold_set_digest(b)


def test_fold_order_doesnt_matter():
    """Folds are normalised by fold_idx, so iteration order over the
    list shouldn't change the digest."""
    a = [_manifest(0, [1, 2], [3]), _manifest(1, [3], [1, 2])]
    b = [_manifest(1, [3], [1, 2]), _manifest(0, [1, 2], [3])]
    assert compute_fold_set_digest(a) == compute_fold_set_digest(b)


def test_swapped_train_val_diverges():
    a = [_manifest(0, [1, 2], [3])]
    b = [_manifest(0, [3], [1, 2])]
    assert compute_fold_set_digest(a) != compute_fold_set_digest(b)


def test_different_userid_assignment_diverges():
    a = [_manifest(0, [1, 2, 3], [4, 5])]
    b = [_manifest(0, [1, 2, 4], [3, 5])]
    assert compute_fold_set_digest(a) != compute_fold_set_digest(b)


def test_extra_fields_dont_affect_digest():
    """Manifests carry diagnostics (counts, overlap fractions) that
    aren't part of the partition. They must not change the digest."""
    a = [_manifest(0, [1, 2], [3, 4])]
    b = [{**_manifest(0, [1, 2], [3, 4]),
          'split_mode': 'strict',
          'next_train_count': 999,
          'overlap': {'ambiguous_poi_count': 42}}]
    assert compute_fold_set_digest(a) == compute_fold_set_digest(b)


def test_digest_format_is_sha256_hex():
    a = [_manifest(0, [1, 2], [3])]
    digest = compute_fold_set_digest(a)
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_digest_compatible():
    """The named compat helper short-circuits on empty digests so a
    paired-test guard can refuse rather than spuriously match."""
    assert digest_compatible("abc", "abc") is True
    assert digest_compatible("abc", "abd") is False
    assert digest_compatible("", "") is False
    assert digest_compatible("abc", "") is False
