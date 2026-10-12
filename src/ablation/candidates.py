"""Reusable MTL experiment candidates.

This module keeps the staged MTL matrix in one place so experiments can be
created as configs or printed as canonical ``scripts/train.py`` commands.
It contains no training side effects.
"""

from __future__ import annotations

import argparse
import json
import shlex
from dataclasses import dataclass, field
from typing import Any

from ablation._utils import format_cli_value

from configs.experiment import ExperimentConfig


@dataclass(frozen=True)
class MTLCandidate:
    """Single runnable MTL candidate."""

    name: str
    stage: str
    model_name: str
    mtl_loss: str
    rationale: str
    model_params: dict[str, Any] = field(default_factory=dict)
    mtl_loss_params: dict[str, Any] = field(default_factory=dict)

    def build_config(
        self,
        state: str,
        engine: str,
        epochs: int,
        folds: int,
    ) -> ExperimentConfig:
        base = ExperimentConfig.default_mtl(
            name=f"{self.name}_{state}_{engine}",
            state=state,
            embedding_engine=engine,
            epochs=epochs,
            k_folds=max(2, folds),
            model_name=self.model_name,
            mtl_loss=self.mtl_loss,
            mtl_loss_params=dict(self.mtl_loss_params),
        )
        model_params = dict(base.model_params)
        model_params.update(self.model_params)
        return ExperimentConfig(
            **{
                **base.__dict__,
                "model_params": model_params,
            }
        )

    def command(
        self,
        state: str,
        engine: str,
        epochs: int,
        folds: int,
        python: str = "python",
    ) -> str:
        args = [
            "PYTHONPATH=src",
            python,
            "scripts/train.py",
            "--task",
            "mtl",
            "--state",
            state,
            "--engine",
            engine,
            "--epochs",
            str(epochs),
            "--folds",
            str(folds),
            "--model",
            self.model_name,
            "--mtl-loss",
            self.mtl_loss,
        ]
        for key, value in self.model_params.items():
            args.extend(["--model-param", f"{key}={format_cli_value(value)}"])
        for key, value in self.mtl_loss_params.items():
            if self.mtl_loss == "static_weight" and key == "category_weight":
                args.extend(["--category-weight", str(value)])
            else:
                args.extend(["--mtl-loss-param", f"{key}={format_cli_value(value)}"])
        return " ".join(shlex.quote(part) for part in args)


CANDIDATES: tuple[MTLCandidate, ...] = (
    MTLCandidate(
        name="baseline_nash",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="nash_mtl",
        rationale="Reference implementation; keep only if diagnostics justify solver cost.",
    ),
    MTLCandidate(
        name="equal_weight",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="equal_weight",
        rationale="Strong simple scalarization baseline.",
    ),
    MTLCandidate(
        name="static_cat_025",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="static_weight",
        mtl_loss_params={"category_weight": 0.25},
        rationale="Bias toward next-category while preserving category supervision.",
    ),
    MTLCandidate(
        name="static_cat_050",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="static_weight",
        mtl_loss_params={"category_weight": 0.50},
        rationale="Normalized fixed scalarization baseline.",
    ),
    MTLCandidate(
        name="static_cat_075",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="static_weight",
        mtl_loss_params={"category_weight": 0.75},
        rationale="Bias toward category to test task tradeoff sensitivity.",
    ),
    MTLCandidate(
        name="uncertainty_weighting",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="uncertainty_weighting",
        rationale="Low-cost learned task weighting baseline.",
    ),
    MTLCandidate(
        name="uw_so_t05",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="uw_so",
        mtl_loss_params={"temperature": 0.5},
        rationale="Soft optimal uncertainty weighting (2024), sharper inverse-loss weighting.",
    ),
    MTLCandidate(
        name="uw_so_t10",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="uw_so",
        mtl_loss_params={"temperature": 1.0},
        rationale="Soft optimal uncertainty weighting (2024), default temperature.",
    ),
    MTLCandidate(
        name="uw_so_t20",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="uw_so",
        mtl_loss_params={"temperature": 2.0},
        rationale="Soft optimal uncertainty weighting (2024), smoother weighting.",
    ),
    MTLCandidate(
        name="famo",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="famo",
        rationale="Fast adaptive weighting candidate without per-task gradient solvers.",
    ),
    MTLCandidate(
        name="random_weight",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="random_weight",
        mtl_loss_params={"alpha": 1.0},
        rationale="Cheap stochastic baseline; useful sanity check against complex optimizers.",
    ),
    MTLCandidate(
        name="fairgrad_a10",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 1.0, "solver_steps": 25},
        rationale="FairGrad-style weighting from gradient interactions (ICML 2024).",
    ),
    MTLCandidate(
        name="fairgrad_a20",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="FairGrad variant with smoother fairness curve (alpha=2.0).",
    ),
    MTLCandidate(
        name="bayesagg_mtl",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="bayesagg_mtl",
        mtl_loss_params={"ema_beta": 0.9, "uncertainty_power": 1.0},
        rationale="Bayesian uncertainty-inspired gradient aggregation (ICML 2024).",
    ),
    MTLCandidate(
        name="go4align",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="go4align",
        mtl_loss_params={"temperature": 1.0, "window_size": 12},
        rationale="Group-risk alignment inspired weighting with interaction-aware indicators (NeurIPS 2024).",
    ),
    MTLCandidate(
        name="excess_mtl",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="excess_mtl",
        mtl_loss_params={"robust_step_size": 0.01},
        rationale="Robust excess-risk multi-task weighting (ICML 2024).",
    ),
    MTLCandidate(
        name="stch",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="stch",
        mtl_loss_params={"mu": 0.5, "warmup_epochs": 1},
        rationale="Smooth Tchebycheff scalarization with nadir normalization (ICML 2024).",
    ),
    MTLCandidate(
        name="db_mtl",
        stage="phase1",
        model_name="mtlnet",
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Dual-balancing of loss/gradient scales via log-loss gradients.",
    ),
    MTLCandidate(
        name="mmoe_equal",
        stage="phase2",
        model_name="mtlnet_mmoe",
        model_params={"num_experts": 4},
        mtl_loss="equal_weight",
        rationale="Simplest sequence-aware MoE architecture probe.",
    ),
    MTLCandidate(
        name="mmoe_famo",
        stage="phase2",
        model_name="mtlnet_mmoe",
        model_params={"num_experts": 4},
        mtl_loss="famo",
        rationale="MMoE with the first adaptive optimizer candidate.",
    ),
    MTLCandidate(
        name="cgc_equal",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 1},
        mtl_loss="equal_weight",
        rationale="Small CGC-lite architecture probe with no adaptive weighting.",
    ),
    MTLCandidate(
        name="cgc_equal_s1t1",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 1, "num_task_experts": 1},
        mtl_loss="equal_weight",
        rationale="CGC-lite with minimum shared/task expert capacity baseline.",
    ),
    MTLCandidate(
        name="cgc_equal_s2t2",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="equal_weight",
        rationale="CGC-lite with balanced extra task experts.",
    ),
    MTLCandidate(
        name="cgc_equal_s4t1",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 4, "num_task_experts": 1},
        mtl_loss="equal_weight",
        rationale="CGC-lite with larger shared expert pool.",
    ),
    MTLCandidate(
        name="cgc_famo",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 1},
        mtl_loss="famo",
        rationale="CGC-lite with the first adaptive optimizer candidate.",
    ),
    # Architecture sweep matrix (all MTLnet variants x selected losses)
    MTLCandidate(
        name="arch_mtlnet_equal",
        stage="phase2",
        model_name="mtlnet",
        mtl_loss="equal_weight",
        rationale="Architecture sweep baseline: original MTLnet + equal_weight.",
    ),
    MTLCandidate(
        name="arch_mtlnet_db_mtl",
        stage="phase2",
        model_name="mtlnet",
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Architecture sweep baseline: original MTLnet + db_mtl.",
    ),
    MTLCandidate(
        name="arch_mtlnet_fairgrad_a20",
        stage="phase2",
        model_name="mtlnet",
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="Architecture sweep baseline: original MTLnet + fairgrad(alpha=2).",
    ),
    MTLCandidate(
        name="arch_mmoe_e4_equal",
        stage="phase2",
        model_name="mtlnet_mmoe",
        model_params={"num_experts": 4},
        mtl_loss="equal_weight",
        rationale="Architecture sweep: MMoE(e=4) + equal_weight.",
    ),
    MTLCandidate(
        name="arch_mmoe_e4_db_mtl",
        stage="phase2",
        model_name="mtlnet_mmoe",
        model_params={"num_experts": 4},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Architecture sweep: MMoE(e=4) + db_mtl.",
    ),
    MTLCandidate(
        name="arch_mmoe_e4_fairgrad_a20",
        stage="phase2",
        model_name="mtlnet_mmoe",
        model_params={"num_experts": 4},
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="Architecture sweep: MMoE(e=4) + fairgrad(alpha=2).",
    ),
    MTLCandidate(
        name="arch_cgc_s2t1_equal",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 1},
        mtl_loss="equal_weight",
        rationale="Architecture sweep: CGC(s=2,t=1) + equal_weight.",
    ),
    MTLCandidate(
        name="arch_cgc_s2t1_db_mtl",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 1},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Architecture sweep: CGC(s=2,t=1) + db_mtl.",
    ),
    MTLCandidate(
        name="arch_cgc_s2t1_fairgrad_a20",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 1},
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="Architecture sweep: CGC(s=2,t=1) + fairgrad(alpha=2).",
    ),
    MTLCandidate(
        name="arch_cgc_s1t1_equal",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 1, "num_task_experts": 1},
        mtl_loss="equal_weight",
        rationale="Architecture sweep: CGC(s=1,t=1) + equal_weight.",
    ),
    MTLCandidate(
        name="arch_cgc_s1t1_db_mtl",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 1, "num_task_experts": 1},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Architecture sweep: CGC(s=1,t=1) + db_mtl.",
    ),
    MTLCandidate(
        name="arch_cgc_s1t1_fairgrad_a20",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 1, "num_task_experts": 1},
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="Architecture sweep: CGC(s=1,t=1) + fairgrad(alpha=2).",
    ),
    MTLCandidate(
        name="arch_cgc_s2t2_equal",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="equal_weight",
        rationale="Architecture sweep: CGC(s=2,t=2) + equal_weight.",
    ),
    MTLCandidate(
        name="arch_cgc_s2t2_db_mtl",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Architecture sweep: CGC(s=2,t=2) + db_mtl.",
    ),
    MTLCandidate(
        name="arch_cgc_s2t2_fairgrad_a20",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="Architecture sweep: CGC(s=2,t=2) + fairgrad(alpha=2).",
    ),
    MTLCandidate(
        name="arch_cgc_s4t1_equal",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 4, "num_task_experts": 1},
        mtl_loss="equal_weight",
        rationale="Architecture sweep: CGC(s=4,t=1) + equal_weight.",
    ),
    MTLCandidate(
        name="arch_cgc_s4t1_db_mtl",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 4, "num_task_experts": 1},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Architecture sweep: CGC(s=4,t=1) + db_mtl.",
    ),
    MTLCandidate(
        name="arch_cgc_s4t1_fairgrad_a20",
        stage="phase2",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 4, "num_task_experts": 1},
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="Architecture sweep: CGC(s=4,t=1) + fairgrad(alpha=2).",
    ),
    MTLCandidate(
        name="arch_dselectk_e4k2_equal",
        stage="phase2",
        model_name="mtlnet_dselectk",
        model_params={"num_experts": 4, "num_selectors": 2, "temperature": 0.5},
        mtl_loss="equal_weight",
        rationale="Architecture sweep: DSelect-k(e=4,k=2) + equal_weight.",
    ),
    MTLCandidate(
        name="arch_dselectk_e4k2_db_mtl",
        stage="phase2",
        model_name="mtlnet_dselectk",
        model_params={"num_experts": 4, "num_selectors": 2, "temperature": 0.5},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Architecture sweep: DSelect-k(e=4,k=2) + db_mtl.",
    ),
    MTLCandidate(
        name="arch_dselectk_e4k2_fairgrad_a20",
        stage="phase2",
        model_name="mtlnet_dselectk",
        model_params={"num_experts": 4, "num_selectors": 2, "temperature": 0.5},
        mtl_loss="fairgrad",
        mtl_loss_params={"alpha": 2.0, "solver_steps": 25},
        rationale="Architecture sweep: DSelect-k(e=4,k=2) + fairgrad(alpha=2).",
    ),
    # ================================================================
    # Phase 3: New optimizer and architecture candidates
    # ================================================================
    # --- New optimizers on base MTLnet ---
    MTLCandidate(
        name="cagrad",
        stage="phase3",
        model_name="mtlnet",
        mtl_loss="cagrad",
        mtl_loss_params={"c": 0.4},
        rationale="CAGrad conflict-averse gradient (NeurIPS 2021), c=0.4 default.",
    ),
    MTLCandidate(
        name="cagrad_c02",
        stage="phase3",
        model_name="mtlnet",
        mtl_loss="cagrad",
        mtl_loss_params={"c": 0.2},
        rationale="CAGrad with smaller conflict-aversion radius c=0.2.",
    ),
    MTLCandidate(
        name="aligned_mtl",
        stage="phase3",
        model_name="mtlnet",
        mtl_loss="aligned_mtl",
        rationale="Aligned-MTL gradient alignment (CVPR 2023), no hyperparams.",
    ),
    MTLCandidate(
        name="dwa",
        stage="phase3",
        model_name="mtlnet",
        mtl_loss="dwa",
        mtl_loss_params={"temperature": 2.0},
        rationale="DWA loss-rate-based weighting (CVPR 2019), T=2.0 default.",
    ),
    MTLCandidate(
        name="dwa_t1",
        stage="phase3",
        model_name="mtlnet",
        mtl_loss="dwa",
        mtl_loss_params={"temperature": 1.0},
        rationale="DWA with more aggressive rebalancing T=1.0.",
    ),
    # --- New optimizers on best architectures ---
    MTLCandidate(
        name="arch_cgc_s2t2_cagrad",
        stage="phase3",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="cagrad",
        mtl_loss_params={"c": 0.4},
        rationale="Best HGI arch CGC(s=2,t=2) + CAGrad.",
    ),
    MTLCandidate(
        name="arch_cgc_s2t2_aligned_mtl",
        stage="phase3",
        model_name="mtlnet_cgc",
        model_params={"num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="aligned_mtl",
        rationale="Best HGI arch CGC(s=2,t=2) + Aligned-MTL.",
    ),
    MTLCandidate(
        name="arch_dselectk_e4k2_cagrad",
        stage="phase3",
        model_name="mtlnet_dselectk",
        model_params={"num_experts": 4, "num_selectors": 2, "temperature": 0.5},
        mtl_loss="cagrad",
        mtl_loss_params={"c": 0.4},
        rationale="Best DGI arch DSelect-k(e=4,k=2) + CAGrad.",
    ),
    # --- PLE architecture candidates ---
    MTLCandidate(
        name="arch_ple_l2_equal",
        stage="phase3",
        model_name="mtlnet_ple",
        model_params={"num_levels": 2, "num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="equal_weight",
        rationale="PLE(levels=2, s=2, t=2) + equal_weight.",
    ),
    MTLCandidate(
        name="arch_ple_l2_db_mtl",
        stage="phase3",
        model_name="mtlnet_ple",
        model_params={"num_levels": 2, "num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="PLE(levels=2, s=2, t=2) + db_mtl.",
    ),
    MTLCandidate(
        name="arch_ple_l2_cagrad",
        stage="phase3",
        model_name="mtlnet_ple",
        model_params={"num_levels": 2, "num_shared_experts": 2, "num_task_experts": 2},
        mtl_loss="cagrad",
        mtl_loss_params={"c": 0.4},
        rationale="PLE(levels=2, s=2, t=2) + CAGrad.",
    ),
    MTLCandidate(
        name="arch_ple_l3_equal",
        stage="phase3",
        model_name="mtlnet_ple",
        model_params={"num_levels": 3, "num_shared_experts": 2, "num_task_experts": 1},
        mtl_loss="equal_weight",
        rationale="PLE(levels=3, s=2, t=1) + equal_weight, deeper extraction.",
    ),
    # ================================================================
    # Phase 4: Head swap ablation
    # ================================================================
    #
    # Rationale:
    #   - Standalone head ablation showed category heads are near-identical
    #     (0.42-0.43 F1) while the default CategoryHeadTransformer uses 14%
    #     of params for a synthetic tokenization of a flat 128-d vector.
    #   - Standalone next head ablation: temporal_cnn (F1=0.24) and
    #     transformer_opt (F1=0.24) massively outperform next_mtl (F1=0.03).
    #   - Tests whether these standalone findings transfer to the MTL setting.
    #
    # --- Base MTLnet with head swaps + equal_weight (best simple loss) ---
    MTLCandidate(
        name="head_cat_single",
        stage="phase4",
        model_name="mtlnet",
        model_params={
            "category_head": "category_single",
            "category_head_params": {"hidden_dims": [128, 64], "dropout": 0.2},
        },
        mtl_loss="equal_weight",
        rationale="Isolate category head: simple MLP vs default transformer.",
    ),
    MTLCandidate(
        name="head_next_tcnn",
        stage="phase4",
        model_name="mtlnet",
        model_params={
            "next_head": "next_temporal_cnn",
            "next_head_params": {
                "hidden_channels": 128, "num_layers": 4,
                "kernel_size": 3, "dropout": 0.2,
            },
        },
        mtl_loss="equal_weight",
        rationale="Isolate next head: temporal CNN vs default transformer.",
    ),
    MTLCandidate(
        name="head_next_topt",
        stage="phase4",
        model_name="mtlnet",
        model_params={
            "next_head": "next_transformer_optimized",
            "next_head_params": {},
        },
        mtl_loss="equal_weight",
        rationale="Isolate next head: optimized transformer vs default.",
    ),
    MTLCandidate(
        name="head_both_tcnn",
        stage="phase4",
        model_name="mtlnet",
        model_params={
            "category_head": "category_single",
            "category_head_params": {"hidden_dims": [128, 64], "dropout": 0.2},
            "next_head": "next_temporal_cnn",
            "next_head_params": {
                "hidden_channels": 128, "num_layers": 4,
                "kernel_size": 3, "dropout": 0.2,
            },
        },
        mtl_loss="equal_weight",
        rationale="Both heads swapped: simple MLP cat + temporal CNN next.",
    ),
    MTLCandidate(
        name="head_both_topt",
        stage="phase4",
        model_name="mtlnet",
        model_params={
            "category_head": "category_single",
            "category_head_params": {"hidden_dims": [128, 64], "dropout": 0.2},
            "next_head": "next_transformer_optimized",
            "next_head_params": {},
        },
        mtl_loss="equal_weight",
        rationale="Both heads swapped: simple MLP cat + optimized transformer next.",
    ),
    # --- Best head combo on best architectures ---
    MTLCandidate(
        name="head_cgc_s2t2_both_tcnn",
        stage="phase4",
        model_name="mtlnet_cgc",
        model_params={
            "num_shared_experts": 2, "num_task_experts": 2,
            "category_head": "category_single",
            "category_head_params": {"hidden_dims": [128, 64], "dropout": 0.2},
            "next_head": "next_temporal_cnn",
            "next_head_params": {
                "hidden_channels": 128, "num_layers": 4,
                "kernel_size": 3, "dropout": 0.2,
            },
        },
        mtl_loss="equal_weight",
        rationale="Best HGI arch + swapped heads. Tests if head gains stack with arch gains.",
    ),
    MTLCandidate(
        name="head_cgc_s2t2_both_tcnn_db",
        stage="phase4",
        model_name="mtlnet_cgc",
        model_params={
            "num_shared_experts": 2, "num_task_experts": 2,
            "category_head": "category_single",
            "category_head_params": {"hidden_dims": [128, 64], "dropout": 0.2},
            "next_head": "next_temporal_cnn",
            "next_head_params": {
                "hidden_channels": 128, "num_layers": 4,
                "kernel_size": 3, "dropout": 0.2,
            },
        },
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Best HGI arch + swapped heads + db_mtl. Full combination test.",
    ),
    MTLCandidate(
        name="head_ple_l2_both_tcnn",
        stage="phase4",
        model_name="mtlnet_ple",
        model_params={
            "num_levels": 2, "num_shared_experts": 2, "num_task_experts": 2,
            "category_head": "category_single",
            "category_head_params": {"hidden_dims": [128, 64], "dropout": 0.2},
            "next_head": "next_temporal_cnn",
            "next_head_params": {
                "hidden_channels": 128, "num_layers": 4,
                "kernel_size": 3, "dropout": 0.2,
            },
        },
        mtl_loss="equal_weight",
        rationale="PLE + swapped heads. Tests if deeper extraction + better heads compound.",
    ),
    MTLCandidate(
        name="head_dselectk_both_tcnn",
        stage="phase4",
        model_name="mtlnet_dselectk",
        model_params={
            "num_experts": 4, "num_selectors": 2, "temperature": 0.5,
            "category_head": "category_single",
            "category_head_params": {"hidden_dims": [128, 64], "dropout": 0.2},
            "next_head": "next_temporal_cnn",
            "next_head_params": {
                "hidden_channels": 128, "num_layers": 4,
                "kernel_size": 3, "dropout": 0.2,
            },
        },
        mtl_loss="db_mtl",
        mtl_loss_params={"beta": 0.9, "beta_sigma": 0.5},
        rationale="Best DGI arch + swapped heads + db_mtl.",
    ),
)


def grid(
    models: list[tuple[str, dict[str, Any]]],
    losses: list[tuple[str, dict[str, Any]]],
    stage: str,
    name_prefix: str = "",
    rationale_template: str = "{model_name} + {loss_name}",
) -> list[MTLCandidate]:
    """Generate a cartesian product of (model, loss) candidates.

    Each entry in ``models`` is ``(model_name, model_params_dict)``.
    Each entry in ``losses`` is ``(loss_name, loss_params_dict)``.

    Returns one ``MTLCandidate`` per combination, with auto-generated
    names like ``{prefix}{model_short}_{loss_short}``. Use this to avoid
    hand-writing repetitive architecture-sweep blocks.
    """
    candidates: list[MTLCandidate] = []
    for model_name, model_params in models:
        for loss_name, loss_params in losses:
            m_short = model_name.replace("mtlnet_", "").replace("mtlnet", "base")
            l_short = loss_name.replace("_weight", "").replace("_mtl", "")
            name = f"{name_prefix}{m_short}_{l_short}"
            candidates.append(
                MTLCandidate(
                    name=name,
                    stage=stage,
                    model_name=model_name,
                    model_params=dict(model_params),
                    mtl_loss=loss_name,
                    mtl_loss_params=dict(loss_params),
                    rationale=rationale_template.format(
                        model_name=model_name, loss_name=loss_name
                    ),
                )
            )
    return candidates


# =====================================================================
# Head ablation candidates — standalone head variant evaluation
# =====================================================================


@dataclass(frozen=True)
class HeadCandidate:
    """Single runnable standalone head candidate."""

    name: str
    task: str  # "category" or "next"
    model_name: str
    rationale: str
    model_params: dict[str, Any] = field(default_factory=dict)

    def build_config(
        self,
        state: str,
        engine: str,
        epochs: int,
        folds: int,
    ) -> ExperimentConfig:
        factory = {
            "category": ExperimentConfig.default_category,
            "next": ExperimentConfig.default_next,
        }[self.task]
        base = factory(
            name=f"{self.name}_{state}_{engine}",
            state=state,
            embedding_engine=engine,
            epochs=epochs,
            k_folds=max(2, folds),
            model_name=self.model_name,
        )
        # Head variants have different constructor signatures, so we
        # only inherit dimension and class count from the base defaults.
        # Everything else must come from the candidate's model_params.
        _INHERIT_KEYS = {"input_dim", "embed_dim", "num_classes"}
        model_params = {
            k: v for k, v in base.model_params.items() if k in _INHERIT_KEYS
        }
        model_params.update(self.model_params)
        return ExperimentConfig(
            **{
                **base.__dict__,
                "model_params": model_params,
            }
        )

    def command(
        self,
        state: str,
        engine: str,
        epochs: int,
        folds: int,
        python: str = "python",
    ) -> str:
        args = [
            "PYTHONPATH=src",
            python,
            "scripts/train.py",
            "--task",
            self.task,
            "--state",
            state,
            "--engine",
            engine,
            "--epochs",
            str(epochs),
            "--folds",
            str(folds),
            "--model",
            self.model_name,
        ]
        for key, value in self.model_params.items():
            args.extend(["--model-param", f"{key}={format_cli_value(value)}"])
        return " ".join(shlex.quote(part) for part in args)


HEAD_CANDIDATES: tuple[HeadCandidate, ...] = (
    # --- Category heads ---
    HeadCandidate(
        name="cat_ensemble",
        task="category",
        model_name="category_ensemble",
        rationale="Default multi-path ensemble (3 paths, depth 2-4). Current baseline.",
    ),
    HeadCandidate(
        name="cat_single",
        task="category",
        model_name="category_single",
        model_params={"hidden_dims": [128, 64], "dropout": 0.2},
        rationale="Minimal MLP baseline — tests how much head complexity matters.",
    ),
    HeadCandidate(
        name="cat_attention",
        task="category",
        model_name="category_attention",
        rationale="Attention pooling over features, tests if input weighting helps.",
    ),
    HeadCandidate(
        name="cat_transformer",
        task="category",
        model_name="category_transformer",
        model_params={"num_tokens": 4, "token_dim": 16},
        rationale="Tokenize embedding → transformer encoder. Heavy for a 1D embedding.",
    ),
    HeadCandidate(
        name="cat_gated",
        task="category",
        model_name="category_gated",
        model_params={"hidden_dims": [128, 64], "dropout": 0.2},
        rationale="Gated expert paths with learned routing.",
    ),
    HeadCandidate(
        name="cat_residual",
        task="category",
        model_name="category_residual",
        model_params={"hidden_dims": [128, 64], "dropout": 0.2},
        rationale="Deep residual MLP with skip connections.",
    ),
    HeadCandidate(
        name="cat_dcn",
        task="category",
        model_name="category_dcn",
        model_params={"hidden_dims": [128, 64], "cross_layers": 2},
        rationale="Deep & Cross Network — explicit feature crosses.",
    ),
    HeadCandidate(
        name="cat_se",
        task="category",
        model_name="category_se",
        rationale="Squeeze-and-Excitation channel reweighting.",
    ),
    # --- Next-POI heads ---
    HeadCandidate(
        name="next_single",
        task="next",
        model_name="next_single",
        model_params={"num_heads": 4, "seq_length": 9, "num_layers": 4, "dropout": 0.2},
        rationale="Transformer encoder baseline. Current default for standalone next.",
    ),
    HeadCandidate(
        name="next_mtl",
        task="next",
        model_name="next_mtl",
        model_params={"num_heads": 8, "seq_length": 9, "num_layers": 4, "dropout": 0.35},
        rationale="Transformer variant used inside MTLnet (8 heads, 4 layers).",
    ),
    HeadCandidate(
        name="next_lstm",
        task="next",
        model_name="next_lstm",
        rationale="Bi-LSTM sequential encoder. Tests RNN vs attention.",
    ),
    HeadCandidate(
        name="next_gru",
        task="next",
        model_name="next_gru",
        rationale="GRU sequential encoder. Lighter than LSTM.",
    ),
    HeadCandidate(
        name="next_temporal_cnn",
        task="next",
        model_name="next_temporal_cnn",
        rationale="Dilated causal convolutions. Tests local vs global attention.",
    ),
    HeadCandidate(
        name="next_hybrid",
        task="next",
        model_name="next_hybrid",
        rationale="GRU + cross-attention hybrid. Best of both worlds?",
    ),
    HeadCandidate(
        name="next_transformer_opt",
        task="next",
        model_name="next_transformer_optimized",
        rationale="Optimized transformer with temporal decay positional encoding.",
    ),
    # --- New heads (Phase 5) ---
    HeadCandidate(
        name="cat_linear",
        task="category",
        model_name="category_linear",
        rationale="Diagnostic linear probe — tests if backbone does all representational work.",
    ),
    HeadCandidate(
        name="next_tcn_residual",
        task="next",
        model_name="next_tcn_residual",
        model_params={"hidden_channels": 128, "num_blocks": 4, "kernel_size": 3, "dropout": 0.2},
        rationale="Canonical TCN with residual blocks + dilation scheduling (Bai et al. 2018).",
    ),
    HeadCandidate(
        name="next_conv_attn",
        task="next",
        model_name="next_conv_attn",
        model_params={"hidden_channels": 128, "num_conv_layers": 3, "num_heads": 4, "dropout": 0.2},
        rationale="TCN encoder + single cross-attention pooling. Tests adaptive vs avg pooling.",
    ),
    HeadCandidate(
        name="next_transformer_relpos",
        task="next",
        model_name="next_transformer_relpos",
        model_params={"num_heads": 4, "num_layers": 2, "seq_length": 9, "dropout": 0.2},
        rationale="Lightweight Transformer with relative position bias (ALiBi-inspired).",
    ),
)


def get_head_candidate(name: str) -> HeadCandidate:
    for candidate in HEAD_CANDIDATES:
        if candidate.name == name:
            return candidate
    available = ", ".join(c.name for c in HEAD_CANDIDATES)
    raise KeyError(f"Unknown head candidate {name!r}. Available: {available}")


def iter_head_candidates(task: str = "all") -> tuple[HeadCandidate, ...]:
    if task == "all":
        return HEAD_CANDIDATES
    return tuple(c for c in HEAD_CANDIDATES if c.task == task)


def get_candidate(name: str) -> MTLCandidate:
    for candidate in CANDIDATES:
        if candidate.name == name:
            return candidate
    available = ", ".join(candidate.name for candidate in CANDIDATES)
    raise KeyError(f"Unknown MTL candidate {name!r}. Available: {available}")


def iter_candidates(stage: str = "all") -> tuple[MTLCandidate, ...]:
    if stage == "all":
        return CANDIDATES
    return tuple(candidate for candidate in CANDIDATES if candidate.stage == stage)


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="List staged MTL candidate commands.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--state", default="alabama")
    parser.add_argument("--engine", default="dgi")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--folds", type=int, default=1)
    parser.add_argument("--stage", choices=("phase1", "phase2", "all"), default="phase1")
    parser.add_argument("--python", default="python")
    parser.add_argument("--json", action="store_true", help="Print candidate metadata as JSON.")
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = _parse_args(argv)
    candidates = iter_candidates(args.stage)
    if args.json:
        print(json.dumps([candidate.__dict__ for candidate in candidates], indent=2))
        return
    for candidate in candidates:
        print(f"# {candidate.name}: {candidate.rationale}")
        print(candidate.command(args.state, args.engine, args.epochs, args.folds, args.python))


if __name__ == "__main__":
    main()
