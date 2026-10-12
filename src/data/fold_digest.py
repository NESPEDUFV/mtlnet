"""Fold-set digest — AUDIT-C8.

A SHA-256 fingerprint over a list of fold manifests (sorted train/val
userid sets). Two FoldCreator runs that produced the same partition
yield identical digests; runs with different data, seeds, or split
algorithms yield different digests.

Used to verify paired statistical-test validity across runs: paired
Wilcoxon assumes the SAME folds were used; without a digest check,
mismatched folds (regenerated parquet, different seed, different
preprocessing version) silently invalidate the comparison while
producing plausible-looking p-values.

Public API
----------
- ``compute_fold_set_digest(manifests)`` returns the canonical hex
  digest for a list of fold manifest dicts.
- ``digest_compatible(a, b)`` is just ``a == b`` but exists as a
  named function so paired-test sites read self-documentingly.
"""
from __future__ import annotations

import hashlib
import json
from typing import Iterable, Mapping


def _normalise_fold(manifest: Mapping) -> dict:
    """Project a fold manifest down to fields that determine the partition.

    Everything else (counts, overlap diagnostics, split_mode metadata)
    is informational and shouldn't change the digest. The partition is
    defined by which userids land in train vs val, plus the fold index
    (so reordering folds counts as a different partition).
    """
    return {
        "fold_idx": int(manifest["fold_idx"]),
        "train_users": sorted(int(u) for u in manifest.get("train_users", [])),
        "val_users": sorted(int(u) for u in manifest.get("val_users", [])),
    }


def compute_fold_set_digest(manifests: Iterable[Mapping]) -> str:
    """SHA-256 over canonical-JSON of normalised fold manifests.

    Returns a 64-character hex string. Identical across runs iff the
    fold partitions match.
    """
    normalised = sorted(
        (_normalise_fold(m) for m in manifests),
        key=lambda d: d["fold_idx"],
    )
    payload = json.dumps(normalised, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def digest_compatible(a: str, b: str) -> bool:
    """Whether two fold-set digests are equal (paired-test precondition)."""
    return bool(a) and bool(b) and a == b


__all__ = [
    "compute_fold_set_digest",
    "digest_compatible",
]
