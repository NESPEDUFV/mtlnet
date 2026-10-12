"""
End-to-end equivalence test that compares the migrated HGI embeddings
against an OUTPUT CSV produced by the original reference pipeline.

The test loads:
  output/hgi/alabama/hgi.csv                  (original source output)
  output/hgi/alabama/embeddings_migration.parquet   (our migration's output)

and validates that the two embedding spaces are structurally equivalent on
the intersection of placeids:

  1. Placeid coverage   — every original POI must exist in the migration
  2. Per-POI alignment  — Procrustes-aligned cosine similarity >= 0.5 mean
  3. Geometry           — Spearman corr of pairwise distances >= 0.20
  4. k-NN preservation  — k=20 neighbour overlap >= 5x random baseline
  5. Categories         — every shared placeid must carry the same category

These thresholds are deliberately loose because two independent training
runs of a contrastive model on slightly different POI sets are NOT expected
to produce identical embeddings (the loss has rotation+scale ambiguity, and
SGD noise compounds across thousands of steps). What MUST be preserved is
the global geometry: POIs that are close in one space stay close in the
other, and category structure is consistent.

The test is automatically skipped if either fixture file is missing — for
example, on a CI machine that hasn't run the Alabama pipeline yet.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ALABAMA_DIR = Path("/Users/vitor/Desktop/mestrado/ingred/output/hgi/alabama")
ORIG_CSV = ALABAMA_DIR / "hgi.csv"
# When the comparison is run against the canonical migration output, the
# user backs the original up to embeddings_migration.parquet so they can
# overwrite embeddings.parquet for downstream A/B comparison.
MIG_PARQUET = ALABAMA_DIR / "embeddings_migration.parquet"
MIG_PARQUET_FALLBACK = ALABAMA_DIR / "embeddings.parquet"

pytestmark = pytest.mark.skipif(
    not ORIG_CSV.exists() or (
        not MIG_PARQUET.exists() and not MIG_PARQUET_FALLBACK.exists()
    ),
    reason="Original CSV or migrated parquet not present at hardcoded paths",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_aligned():
    """Load both files, deduplicate, restrict to intersection, align order."""
    orig = pd.read_csv(ORIG_CSV)
    mig_path = MIG_PARQUET if MIG_PARQUET.exists() else MIG_PARQUET_FALLBACK
    mig = pd.read_parquet(mig_path)

    # Normalize placeid types so set ops work
    orig["placeid"] = orig["placeid"].astype(str)
    mig["placeid"] = mig["placeid"].astype(str)

    # Deduplicate original (per-checkin replication in source format)
    orig = orig.drop_duplicates(subset="placeid").reset_index(drop=True)

    shared = sorted(set(orig["placeid"]) & set(mig["placeid"]))
    orig = orig.set_index("placeid").loc[shared]
    mig = mig.set_index("placeid").loc[shared]

    emb_cols = [str(i) for i in range(64)]
    E_orig = orig[emb_cols].to_numpy(dtype=np.float32)
    E_mig = mig[emb_cols].to_numpy(dtype=np.float32)

    return shared, E_orig, E_mig, orig, mig


def _row_normalize(M):
    return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)


def _procrustes_align(source, target):
    """Find orthogonal R that best maps source to target. Returns source @ R.T."""
    M = target.T @ source
    U, _, Vt = np.linalg.svd(M)
    R = U @ Vt
    return source @ R.T


def _topk(M, k):
    Mn = _row_normalize(M)
    sim = Mn @ Mn.T
    np.fill_diagonal(sim, -np.inf)
    return np.argsort(-sim, axis=1)[:, :k]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHGIAlabamaCSVEquivalence:
    """Structural equivalence vs the reference Alabama embeddings."""

    def test_placeid_coverage(self):
        """Every original POI must exist in the migration (no dropped POIs)."""
        shared, _, _, _, _ = _load_aligned()
        orig_full = pd.read_csv(ORIG_CSV)
        orig_full["placeid"] = orig_full["placeid"].astype(str)
        n_orig_unique = orig_full["placeid"].nunique()
        assert len(shared) == n_orig_unique, (
            f"Migration is missing POIs: shared={len(shared)}, "
            f"original unique={n_orig_unique}"
        )

    def test_categories_match_on_shared_pois(self):
        """The category label must be identical for every shared placeid."""
        _, _, _, orig, mig = _load_aligned()
        cat_o = orig["category"].astype(str)
        cat_m = mig["category"].astype(str)
        assert (cat_o.values == cat_m.values).all(), (
            "Category mismatch on shared POIs — placeid encoding is wrong"
        )

    def test_l2_norms_in_same_order_of_magnitude(self):
        """Embedding magnitudes should be within 2x of each other."""
        _, E_orig, E_mig, _, _ = _load_aligned()
        n_o = np.linalg.norm(E_orig, axis=1).mean()
        n_m = np.linalg.norm(E_mig, axis=1).mean()
        ratio = max(n_o, n_m) / min(n_o, n_m)
        assert ratio < 2.0, (
            f"L2 norms differ by more than 2x: original={n_o:.3f}, "
            f"migration={n_m:.3f}, ratio={ratio:.3f}"
        )

    def test_procrustes_aligned_cosine(self):
        """
        After best orthogonal alignment, mean per-POI cosine similarity
        must be >= 0.5 (94% of POIs above this threshold in our run).
        """
        _, E_orig, E_mig, _, _ = _load_aligned()
        E_orig_aligned = _procrustes_align(E_orig, E_mig)

        n_o = _row_normalize(E_orig_aligned)
        n_m = _row_normalize(E_mig)
        cos = (n_o * n_m).sum(axis=1)

        mean_cos = cos.mean()
        frac_above_05 = (cos > 0.5).mean()
        assert mean_cos >= 0.5, (
            f"Procrustes-aligned mean cosine too low: {mean_cos:.4f} "
            f"({frac_above_05:.1%} above 0.5)"
        )
        assert frac_above_05 >= 0.85, (
            f"Less than 85% of POIs align well: {frac_above_05:.1%}"
        )

    def test_geometry_spearman_correlation(self):
        """
        Spearman rank correlation of pairwise cosine distances on a 1000-POI
        sample must be at least 0.2 (geometry is preserved at the global level).
        """
        from scipy.stats import spearmanr

        _, E_orig, E_mig, _, _ = _load_aligned()
        rng = np.random.default_rng(0)
        idx = rng.choice(len(E_orig), size=1000, replace=False)

        def pcos(M):
            Mn = _row_normalize(M[idx])
            return 1 - Mn @ Mn.T

        D_o = pcos(E_orig)
        D_m = pcos(E_mig)
        iu = np.triu_indices(1000, k=1)
        rho, _ = spearmanr(D_o[iu], D_m[iu])
        assert rho >= 0.20, f"Pairwise distance Spearman corr too low: {rho:.4f}"

    @pytest.mark.parametrize("k,min_overlap_ratio", [
        (10, 20.0),   # observed ~30x
        (20, 15.0),   # observed ~20x
        (50, 7.0),    # observed ~10x
    ])
    def test_knn_overlap_above_random_baseline(self, k, min_overlap_ratio):
        """
        For each POI, the k nearest neighbours under both embedding spaces
        must overlap at least `min_overlap_ratio`x more than random chance.
        """
        _, E_orig, E_mig, _, _ = _load_aligned()
        rng = np.random.default_rng(1)
        N = 2000
        idx = rng.choice(len(E_orig), size=N, replace=False)

        nn_o = _topk(E_orig[idx], k)
        nn_m = _topk(E_mig[idx], k)
        overlap = np.array([
            len(set(nn_o[i]) & set(nn_m[i])) / k for i in range(N)
        ])
        random_baseline = k / N
        ratio = overlap.mean() / random_baseline
        assert ratio >= min_overlap_ratio, (
            f"k={k}: overlap={overlap.mean():.4f}, baseline={random_baseline:.4f}, "
            f"ratio={ratio:.1f}x (need >= {min_overlap_ratio}x)"
        )