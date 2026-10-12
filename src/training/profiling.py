"""Ephemeral runtime profiler / audit tool for a training run.

This is a DEBUG / MONITORING tool, *not* part of the experiment record. It lives
only for the process lifetime (like the logs) and writes nothing into
``MLHistory`` or the results rundir — disable it and a run is byte-for-byte the
same. It exists so an engineer (or another agent) can answer, during or right
after a run: *where is the time going, how fast are we, is quality tracking, and
which line in the code is the pain point?*

Enable it with ``MTL_PROFILE=1`` in the environment (``scripts/train.py --profile``
sets this for you). When disabled, every call here is a cheap no-op.

What it captures, per fold and per run:
  - **section wall-time breakdown** — ``data`` / ``forward`` / ``backward`` /
    ``optim`` / ``train_metric`` / ``eval`` … (whatever the call sites name), with
    total time, call count and share-of-step. Sections are tagged ``compute`` /
    ``data`` / ``sync`` so the report can separate "real GPU work" from "waiting".
  - **throughput** — batches/s and samples/s.
  - **peak GPU memory** — allocated + reserved (per fold, reset each fold).
  - **torch.compile activity** — recompiles / graph breaks (via the dynamo
    counters), so a recompile storm is visible.
  - **GPU utilization** — sampled in a background thread via ``pynvml`` when
    available (mean / p50 / max).
  - **quality trajectory** — best val metric per task per fold (via
    :meth:`RunProfiler.record_quality`).

It then prints a summary to the logger at :meth:`fold_end` / :meth:`run_end`, and
— if ``MTL_PROFILE_JSON=<path>`` is set — dumps the same structured report to that
path (a transient debug dump, never a result artifact). It also raises heuristic
**pain-point flags** (GPU-starved / data-bound, recompile storm, sync-dominated
step, slow data path) that point back at the code.

Typical instrumentation (already wired into ``mtl_cv`` + the single-task trainer)::

    prof = get_profiler()
    prof.run_start(meta={"state": state, "engine": engine})
    for fold_id, loaders in ...:
        prof.fold_start(fold_id)
        for epoch in ...:
            for x, y in loader:
                with prof.section("data", tag="data"):
                    x = x.to(device)
                with prof.section("forward"):           # tag defaults to "compute"
                    out = model(x)
                with prof.section("backward"):
                    loss.backward()
                prof.mark(samples=x.size(0))
        prof.record_quality(fold_id, "next_region", best_top10)
        prof.fold_end()
    prof.run_end()
"""

from __future__ import annotations

import json
import logging
import os
import statistics
import threading
import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Section tags drive the pain-point heuristics: "compute" = real model work,
# "data" = input loading / host->device, "sync" = host<->device stalls.
_COMPUTE = "compute"
_DATA = "data"
_SYNC = "sync"

_TRUE = {"1", "true", "True", "yes", "on"}


def _env_true(name: str) -> bool:
    return os.environ.get(name, "") in _TRUE


class _SectionAcc:
    """Accumulator for one named section."""

    __slots__ = ("total", "count")

    def __init__(self) -> None:
        self.total = 0.0
        self.count = 0


class _GpuSampler:
    """Background pynvml sampler for GPU utilization + memory (best-effort)."""

    def __init__(self, period_s: float = 0.2) -> None:
        self.period_s = period_s
        self._util: List[float] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._handle = None
        self._ok = False
        try:  # pragma: no cover - hardware dependent
            import pynvml

            pynvml.nvmlInit()
            self._pynvml = pynvml
            self._handle = pynvml.nvmlDeviceGetHandleByIndex(
                int(os.environ.get("CUDA_VISIBLE_DEVICES", "0").split(",")[0] or 0)
            )
            self._ok = True
        except Exception:
            self._ok = False

    @property
    def available(self) -> bool:
        return self._ok

    def _loop(self) -> None:  # pragma: no cover - thread + hardware
        while not self._stop.wait(self.period_s):
            try:
                u = self._pynvml.nvmlDeviceGetUtilizationRates(self._handle)
                self._util.append(float(u.gpu))
            except Exception:
                break

    def start(self) -> None:
        if not self._ok:
            return
        self._stop.clear()
        self._util = []
        self._thread = threading.Thread(target=self._loop, name="gpu-sampler", daemon=True)
        self._thread.start()

    def snapshot_and_reset(self) -> Optional[Dict[str, float]]:
        if not self._ok or not self._util:
            return None
        vals = self._util
        self._util = []
        vals_sorted = sorted(vals)
        return {
            "mean": round(statistics.fmean(vals), 1),
            "p50": round(vals_sorted[len(vals_sorted) // 2], 1),
            "max": round(max(vals), 1),
            "n": len(vals),
        }

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None


class RunProfiler:
    """Opt-in, ephemeral runtime profiler. One instance per process."""

    def __init__(self, enabled: Optional[bool] = None) -> None:
        self.enabled = _env_true("MTL_PROFILE") if enabled is None else bool(enabled)
        # When True, insert torch.cuda.synchronize() at section boundaries for
        # true GPU section timing (perturbs throughput — opt-in only).
        self._cuda_sync = self.enabled and _env_true("MTL_PROFILE_CUDA_SYNC")
        self._json_out = os.environ.get("MTL_PROFILE_JSON", "").strip()

        self._meta: Dict[str, Any] = {}
        self._run_t0: float = 0.0
        self._tags: Dict[str, str] = {}
        # per-fold live state
        self._fold_id: Optional[int] = None
        self._fold_t0: float = 0.0
        self._sections: Dict[str, _SectionAcc] = defaultdict(_SectionAcc)
        self._samples = 0
        self._batches = 0
        self._quality: Dict[str, float] = {}
        # finished folds + run-level
        self._fold_reports: List[Dict[str, Any]] = []
        self._flags: List[str] = []
        self._compile_baseline: Dict[str, int] = {}

        self._sampler = _GpuSampler() if self.enabled else None
        self._torch = None
        if self.enabled:
            try:
                import torch

                self._torch = torch
            except Exception:
                self._torch = None

    # ------------------------------------------------------------------ helpers
    def _compile_counters(self) -> Dict[str, int]:
        if self._torch is None:
            return {}
        try:
            from torch._dynamo.utils import counters

            out: Dict[str, int] = {}
            for grp in ("frames", "graph_break", "recompiles", "recompile_reasons"):
                d = counters.get(grp)
                if isinstance(d, dict):
                    out[grp] = int(sum(v for v in d.values() if isinstance(v, (int, float))))
            return out
        except Exception:
            return {}

    def _cuda_mem(self) -> Optional[Dict[str, float]]:
        t = self._torch
        if t is None or not t.cuda.is_available():
            return None
        try:
            return {
                "peak_alloc_mb": round(t.cuda.max_memory_allocated() / 1e6, 1),
                "peak_reserved_mb": round(t.cuda.max_memory_reserved() / 1e6, 1),
            }
        except Exception:
            return None

    # --------------------------------------------------------------- public API
    def run_start(self, meta: Optional[Dict[str, Any]] = None) -> None:
        if not self.enabled:
            return
        self._meta = dict(meta or {})
        self._run_t0 = time.perf_counter()
        self._compile_baseline = self._compile_counters()
        if self._sampler is not None:
            self._sampler.start()
        logger.info("[profiler] ENABLED — run audit active (meta=%s)", self._meta)

    def fold_start(self, fold_id: int) -> None:
        if not self.enabled:
            return
        self._fold_id = int(fold_id)
        self._fold_t0 = time.perf_counter()
        self._sections = defaultdict(_SectionAcc)
        self._tags = {}
        self._samples = 0
        self._batches = 0
        self._quality = {}
        t = self._torch
        if t is not None and t.cuda.is_available():
            try:
                t.cuda.reset_peak_memory_stats()
            except Exception:
                pass

    @contextmanager
    def section(self, name: str, tag: str = _COMPUTE):
        """Time a named code block. No-op (cheap) when disabled."""
        if not self.enabled:
            yield
            return
        if self._cuda_sync and self._torch is not None and self._torch.cuda.is_available():
            self._torch.cuda.synchronize()
        t0 = time.perf_counter()
        try:
            yield
        finally:
            if self._cuda_sync and self._torch is not None and self._torch.cuda.is_available():
                self._torch.cuda.synchronize()
            acc = self._sections[name]
            acc.total += time.perf_counter() - t0
            acc.count += 1
            self._tags[name] = tag

    def mark(self, samples: int = 0, batches: int = 1) -> None:
        if not self.enabled:
            return
        self._samples += int(samples)
        self._batches += int(batches)

    def record_quality(self, fold_id: int, name: str, value: float) -> None:
        if not self.enabled:
            return
        self._quality[name] = float(value)

    def fold_end(self) -> None:
        if not self.enabled or self._fold_id is None:
            return
        wall = time.perf_counter() - self._fold_t0
        sec = {
            n: {"total_s": round(a.total, 3), "count": a.count, "tag": self._tags.get(n, _COMPUTE)}
            for n, a in sorted(self._sections.items(), key=lambda kv: -kv[1].total)
        }
        report = {
            "fold": self._fold_id,
            "wall_s": round(wall, 2),
            "batches": self._batches,
            "samples": self._samples,
            "batches_per_s": round(self._batches / wall, 2) if wall > 0 else 0.0,
            "samples_per_s": round(self._samples / wall, 1) if wall > 0 else 0.0,
            "gpu_mem": self._cuda_mem(),
            "gpu_util": self._sampler.snapshot_and_reset() if self._sampler else None,
            "sections": sec,
            "quality": dict(self._quality),
        }
        self._fold_reports.append(report)
        self._log_fold(report)
        self._fold_id = None

    def run_end(self) -> None:
        if not self.enabled:
            return
        if self._sampler is not None:
            self._sampler.stop()
        compile_delta = self._diff_counters(self._compile_baseline, self._compile_counters())
        self._raise_flags(compile_delta)
        total_wall = round(time.perf_counter() - self._run_t0, 2)
        summary = {
            "meta": self._meta,
            "run_wall_s": total_wall,
            "compile": compile_delta,
            "folds": self._fold_reports,
            "pain_points": self._flags,
        }
        self._log_run(summary)
        if self._json_out:
            try:
                with open(self._json_out, "w", encoding="utf-8") as fh:
                    json.dump(summary, fh, indent=2)
                logger.info("[profiler] report → %s", self._json_out)
            except Exception as exc:
                logger.warning("[profiler] JSON dump failed: %s", exc)

    # ------------------------------------------------------------- diagnostics
    @staticmethod
    def _diff_counters(before: Dict[str, int], after: Dict[str, int]) -> Dict[str, int]:
        keys = set(before) | set(after)
        return {k: after.get(k, 0) - before.get(k, 0) for k in sorted(keys)}

    def _aggregate_sections(self) -> Dict[str, Dict[str, float]]:
        agg: Dict[str, Dict[str, float]] = {}
        for fr in self._fold_reports:
            for name, s in fr["sections"].items():
                a = agg.setdefault(name, {"total_s": 0.0, "tag": s["tag"]})
                a["total_s"] += s["total_s"]
        return agg

    def _raise_flags(self, compile_delta: Dict[str, int]) -> None:
        utils = [fr["gpu_util"]["mean"] for fr in self._fold_reports if fr.get("gpu_util")]
        if utils:
            mean_util = statistics.fmean(utils)
            if mean_util < 40.0:
                self._flags.append(
                    f"GPU-STARVED: mean GPU util {mean_util:.0f}% (<40%) — the run is data-bound / "
                    f"sync-bound, not compute-bound. Look at the 'data'/'sync'-tagged sections below; "
                    f"candidate fixes: pin CPU-resident batches, fewer per-batch host syncs (.cpu()/.item())."
                )
        agg = self._aggregate_sections()
        if agg:
            total = sum(a["total_s"] for a in agg.values()) or 1.0
            sync_share = sum(a["total_s"] for a in agg.values() if a["tag"] == _SYNC) / total
            data_share = sum(a["total_s"] for a in agg.values() if a["tag"] == _DATA) / total
            compute_share = sum(a["total_s"] for a in agg.values() if a["tag"] == _COMPUTE) / total
            if sync_share > 0.20:
                self._flags.append(
                    f"SYNC-BOUND: host<->device sync sections are {sync_share*100:.0f}% of timed step "
                    f"time — defer .cpu()/.item() to epoch end."
                )
            if data_share > 0.25:
                self._flags.append(
                    f"DATA-BOUND: data/H2D sections are {data_share*100:.0f}% of timed step time — "
                    f"pin memory / keep the dataset GPU-resident."
                )
            if compute_share < 0.45 and (sync_share + data_share) > 0.0:
                self._flags.append(
                    f"LOW COMPUTE SHARE: only {compute_share*100:.0f}% of timed step time is model compute."
                )
        recompiles = compile_delta.get("recompiles", 0)
        n_folds = len(self._fold_reports)
        if recompiles > max(1, n_folds):
            self._flags.append(
                f"RECOMPILE STORM: torch.compile recompiled {recompiles}× across {n_folds} folds "
                f"(expect ≤1/fold) — data-dependent control flow / changing shapes are breaking the graph."
            )
        gbreaks = compile_delta.get("graph_break", 0)
        if gbreaks > 0:
            self._flags.append(
                f"GRAPH BREAKS: {gbreaks} torch.compile graph break(s) — data-dependent .any()/.item() in "
                f"the model forward fragment the compiled graph."
            )

    # ------------------------------------------------------------------- output
    def _log_fold(self, fr: Dict[str, Any]) -> None:
        lines = [
            f"[profiler] fold {fr['fold']}: wall={fr['wall_s']}s  "
            f"{fr['batches_per_s']} batch/s  {fr['samples_per_s']} samp/s"
        ]
        if fr.get("gpu_mem"):
            lines[-1] += f"  peak_gpu={fr['gpu_mem']['peak_reserved_mb']:.0f}MB"
        if fr.get("gpu_util"):
            lines[-1] += f"  gpu_util(mean/p50/max)={fr['gpu_util']['mean']}/{fr['gpu_util']['p50']}/{fr['gpu_util']['max']}%"
        wall = fr["wall_s"] or 1.0
        for name, s in list(fr["sections"].items())[:6]:
            lines.append(
                f"    {name:<16} {s['total_s']:>8.2f}s  ({s['total_s']/wall*100:>4.1f}%)  "
                f"x{s['count']}  [{s['tag']}]"
            )
        if fr.get("quality"):
            q = "  ".join(f"{k}={v:.4f}" for k, v in fr["quality"].items())
            lines.append(f"    quality: {q}")
        logger.info("\n".join(lines))

    def _log_run(self, summary: Dict[str, Any]) -> None:
        folds = summary["folds"]
        bps = [f["batches_per_s"] for f in folds if f["batches_per_s"]]
        head = [
            "",
            "=" * 78,
            "[profiler] RUN AUDIT  " + json.dumps(summary["meta"]),
            f"  run wall: {summary['run_wall_s']}s   folds: {len(folds)}   "
            f"mean throughput: {statistics.fmean(bps):.1f} batch/s" if bps else f"  run wall: {summary['run_wall_s']}s",
        ]
        cd = summary["compile"]
        if any(cd.values()):
            head.append(f"  torch.compile: " + ", ".join(f"{k}+{v}" for k, v in cd.items() if v))
        agg = self._aggregate_sections()
        if agg:
            total = sum(a["total_s"] for a in agg.values()) or 1.0
            head.append("  section totals (all folds):")
            for name, a in sorted(agg.items(), key=lambda kv: -kv[1]["total_s"])[:8]:
                head.append(f"    {name:<16} {a['total_s']:>9.1f}s  ({a['total_s']/total*100:>4.1f}%)  [{a['tag']}]")
        if summary["pain_points"]:
            head.append("  PAIN POINTS:")
            for fl in summary["pain_points"]:
                head.append(f"    ⚠ {fl}")
        else:
            head.append("  PAIN POINTS: none flagged.")
        head.append("=" * 78)
        logger.info("\n".join(head))


# --------------------------------------------------------------------- singleton
_PROFILER: Optional[RunProfiler] = None


def get_profiler() -> RunProfiler:
    """Return the process-wide profiler (constructing a disabled one on first use)."""
    global _PROFILER
    if _PROFILER is None:
        _PROFILER = RunProfiler()
    return _PROFILER


def enable_profiler(enabled: bool = True) -> RunProfiler:
    """Force-enable (or replace) the process-wide profiler. Used by ``--profile``."""
    global _PROFILER
    os.environ["MTL_PROFILE"] = "1" if enabled else "0"
    _PROFILER = RunProfiler(enabled=enabled)
    return _PROFILER


def is_enabled() -> bool:
    return get_profiler().enabled
