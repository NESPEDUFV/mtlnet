"""Regression test for the p1 STL-ceiling OOM guard (S2-analog CPU val metric).

Background: `p1_region_head_ablation._train_single_task` used to `torch.cat` the
FULL validation logit `[N_val, n_classes]` on the GPU before scoring, which OOMs the
A40 at large-C overlap scale (TX overlap: 766083 x 6553 x 4B ~= 20 GB). The MTL
trainer was hardened (S1/S2, `OOM_MEMORY_FIX.md`); the STL ceiling never was. Fix
(`fix(p1): S2-analog CPU val metric ...`): `_should_chunk_val_metric` auto-routes the
val metric to CPU when the full val logit would exceed a GPU budget.

This test PINS the contract so the fix cannot silently regress (this codebase has a
history of a memory fix being reverted by a later merge — `33fe18da` -> `dade24ad`,
see OOM_MEMORY_FIX.md). Two properties:
  1. the auto-gate fires at large-C overlap scale WITHOUT any env (default-on);
  2. scoring on CPU is identical-at-reporting-precision to CUDA for the rank metrics.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src"))
sys.path.insert(0, str(_REPO / "scripts"))

from p1_region_head_ablation import _should_chunk_val_metric  # noqa: E402
from tracking.metrics import compute_classification_metrics  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_chunk_env(monkeypatch):
    """Start each test from a clean env (no caller's MTL_/P1_ overrides)."""
    for k in ("MTL_CHUNK_VAL_METRIC", "P1_CHUNK_VAL_METRIC", "P1_S2_AUTO_BUDGET_GB"):
        monkeypatch.delenv(k, raising=False)


class TestAutoGate:
    def test_tx_overlap_scale_auto_chunks_without_env(self):
        """The exact case that OOM'd: TX overlap val (766083 x 6553) must auto-route
        to CPU with NO env set — this is the default-on recurrence guard."""
        chunk, gb = _should_chunk_val_metric(766_083, 6553)
        assert chunk is True
        assert gb == pytest.approx(20.08, abs=0.1)

    def test_small_state_keeps_gpu_path(self):
        """AL-scale val (19265 x 1109 ~= 0.085 GB) stays on the GPU path so
        small-state / frozen p1 numbers are byte-untouched."""
        chunk, gb = _should_chunk_val_metric(19_265, 1109)
        assert chunk is False
        assert gb < 4.0

    @pytest.mark.parametrize("var", ["MTL_CHUNK_VAL_METRIC", "P1_CHUNK_VAL_METRIC"])
    def test_env_forces_chunk_even_when_small(self, monkeypatch, var):
        monkeypatch.setenv(var, "1")
        chunk, _ = _should_chunk_val_metric(100, 7)
        assert chunk is True

    def test_budget_env_override(self, monkeypatch):
        # ~0.085 GB val logit: default 4 GB budget -> GPU; tiny budget -> chunk.
        assert _should_chunk_val_metric(19_265, 1109)[0] is False
        monkeypatch.setenv("P1_S2_AUTO_BUDGET_GB", "0.01")
        assert _should_chunk_val_metric(19_265, 1109)[0] is True

    def test_boundary_at_budget(self, monkeypatch):
        monkeypatch.setenv("P1_S2_AUTO_BUDGET_GB", "1")
        # 1.0 GB exactly is NOT > budget -> GPU; just over -> chunk.
        n = int(1e9 / (1109 * 4))           # ~1.0 GB
        assert _should_chunk_val_metric(n, 1109)[0] is False
        assert _should_chunk_val_metric(n + 10_000, 1109)[0] is True


@pytest.mark.skipif(not torch.cuda.is_available(), reason="needs CUDA to compare CPU vs GPU scoring")
class TestCpuGpuEquivalence:
    """The fix relies on compute_classification_metrics being device-agnostic.
    CPU vs CUDA must agree at reporting precision for the rank-based metrics
    (top-k / MRR / NDCG use strict `>`, so they are device-independent up to
    fp32 reduction round-off; ~1e-10 in practice, far below the 4dp / +-0.05pp bar)."""

    @pytest.mark.parametrize(
        "n,c,kind",
        [(20_000, 1109, "float"), (40_000, 6553, "float"), (20_000, 1109, "ties")],
    )
    def test_rank_metrics_match(self, n, c, kind):
        torch.manual_seed(0)
        if kind == "ties":
            logits = torch.randint(0, 5, (n, c)).float()  # heavy exact ties
        else:
            logits = torch.randn(n, c)
        targets = torch.randint(0, c, (n,))
        m_cpu = compute_classification_metrics(logits.cpu(), targets.cpu(), num_classes=c, top_k=(5, 10))
        m_gpu = compute_classification_metrics(logits.cuda(), targets.cuda(), num_classes=c, top_k=(5, 10))
        for k in ("top5_acc", "top10_acc", "mrr", "ndcg_5", "ndcg_10"):
            assert m_cpu[k] == pytest.approx(m_gpu[k], abs=1e-6), f"{k}: cpu={m_cpu[k]} gpu={m_gpu[k]}"
