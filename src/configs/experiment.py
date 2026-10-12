"""ExperimentConfig and RunManifest for unified experiment configuration.

ExperimentConfig is the canonical input: it defines what to run.
RunManifest is write-only output: it freezes provenance after a run.

Created in Phase 3 of the refactoring plan.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class ExperimentConfig:
    """Canonical experiment configuration.

    One instance per experiment. Different task types (MTL, category, next)
    get different instances with different defaults via factory classmethods.

    Serialization: save()/load() use JSON. Enums stored as .value strings.
    """

    # --- Identification ---
    name: str
    state: str
    embedding_engine: str  # EmbeddingEngine.value string

    # --- Model ---
    model_name: str = "mtlnet"
    model_params: dict = field(default_factory=dict)

    # --- Training ---
    task_type: str = "mtl"  # "mtl", "category", "next"
    next_target: str = "next_category"  # reserved for future "next_poi" ranking target
    epochs: int = 50
    batch_size: int = 2**12
    learning_rate: float = 1e-4
    max_lr: float = 1e-3
    weight_decay: float = 0.05
    # pipeline_audit 2026-07-01 — field default aligned with every factory /
    # driver (all pin 1). The old field default 2 was reachable only by direct
    # dataclass construction and, pre-fix, hit the broken ga>1 path (per-batch
    # zero_grad wiped accumulated grads — fixed in mtl_cv.py the same day).
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    optimizer_eps: float = 1e-8
    # AdamW beta2 (2nd-moment decay). 0.999 is the default; lowering to ~0.95
    # adapts faster — a standard large-batch (bs8192) stabilizer.
    optimizer_beta2: float = 0.999
    # F51 Tier 3 — cosine scheduler floor LR; 0.0 preserves legacy behaviour
    # (CosineAnnealingLR decays to 0). Non-zero values keep a small LR in the
    # late-cosine tail, which can stabilize α growth in next_getnext_hard.
    eta_min: float = 0.0

    # --- LR scheduler ---
    # "onecycle" preserves legacy behaviour bit-exactly. "constant" and
    # "cosine" are F44-F46 knobs for disentangling "more epochs" from
    # "stretched schedule" in the CH18 attribution chain.
    scheduler_type: str = "onecycle"
    # pct_start only applies when scheduler_type == "onecycle". None →
    # PyTorch default (0.3). Smaller values push peak LR earlier.
    pct_start: Optional[float] = None

    # Per-head LR (F48-H3). When ALL three are set, the optimizer is
    # built with three param groups (cat / reg / shared) at distinct
    # LRs. Currently only honored by mtlnet_crossattn. ``--max-lr`` is
    # ignored in this mode. Recommended pairing: scheduler_type =
    # "constant" so the per-group LRs survive (OneCycleLR would override
    # them with its own max_lr peak).
    cat_lr: Optional[float] = None
    reg_lr: Optional[float] = None
    shared_lr: Optional[float] = None

    # F49 encoder-frozen λ=0 isolation. When True, freezes
    # `category_encoder` + `category_poi` parameters (requires_grad=False)
    # so the cat encoder cannot co-adapt as a reg-helper through cross-attn
    # K/V. Used together with `mtl_loss=static_weight` and
    # `mtl_loss_params={"category_weight": 0.0}` to measure pure
    # architectural overhead (encoder-frozen). See
    # `docs/findings/F49_LAMBDA0_DECOMPOSITION_GAP.md`.
    freeze_cat_stream: bool = False

    # W6 category-side encoder-isolation probe — the MIRROR of freeze_cat_stream:
    # set requires_grad=False on `next_encoder` + `next_poi` so the region stream
    # cannot co-adapt as a cat-helper via cross-attention K/V. Run with
    # `mtl_loss=static_weight` + `category_weight=1.0` (reg-loss=0). If cat F1
    # still beats the STL cat ceiling with the region stream frozen, the joint
    # cat win is the shared trunk (architecture), NOT region->category transfer.
    freeze_reg_stream: bool = False

    # F50 P3 — warmup-then-freeze: train cat side normally for the first
    # N epochs, then freeze ``category_encoder`` + ``category_poi`` from
    # epoch N onward (continued reg + shared training). Tests whether the
    # cat encoder's continued co-adaptation as reg-helper (F49 Layer 2
    # mechanism) is hurting reg at FL scale. None disables. See
    # `docs/findings/MTL_FLAWS_AND_FIXES.md` §3 H1.5.
    freeze_cat_after_epoch: Optional[int] = None

    # F50 P4 — per-batch alternating-SGD. Even batches update cat-side params
    # from L_cat only; odd batches update reg-side params from L_reg only.
    # Shared params see only one task's gradient signal per batch (alternating).
    # Tests "does fine-grained per-task alternation prevent the shared backbone
    # from being hijacked by either loss?" Requires --mtl-loss static_weight
    # and --gradient-accumulation-steps 1 (alternation is by batch-idx).
    alternating_optimizer_step: bool = False

    # F50 D3 — separate LR for next_encoder (split out of reg_lr group). Tests
    # mechanism α (reg encoder is under-trained because loss-side cat_weight=0.75
    # scaling shrinks effective reg gradient by 4x). When set, the reg group
    # splits into reg_encoder (next_encoder params, this LR) + reg_head
    # (next_poi params, reg_lr). Default None reuses reg_lr for both.
    reg_encoder_lr: Optional[float] = None

    # F50 D6 — separate LR for next_poi (the reg head, where α scalar lives in
    # next_getnext_hard). Tests if α growth is the bottleneck rather than the
    # encoder. Setting reg_head_lr higher than reg_lr accelerates α's growth.
    # When set, reg group splits into reg_encoder (next_encoder, reg_lr) +
    # reg_head (next_poi, this LR). Can combine with reg_encoder_lr.
    reg_head_lr: Optional[float] = None

    # F50 F64/B2 — warmup-decay LambdaLR multiplier on reg_head + alpha_no_wd
    # groups. Only consumed when scheduler_type == "reg_head_warmup_decay".
    # Defaults reproduce the F50 T3 spec (warmup ep 0-5, plateau 5-15, decay
    # 15-50, peak 10× base). Tests whether late-window α growth can be unlocked
    # without the sustained instability of D6 (constant high reg_head_lr).
    reg_head_warmup_decay_peak_mult: float = 10.0
    reg_head_warmup_decay_warmup_epochs: int = 5
    reg_head_warmup_decay_plateau_epochs: int = 15

    # F50 F65 — joint-dataloader cycling strategy. ``max_size_cycle``
    # (legacy default) cycles the shorter loader to match the longer; the
    # shorter loader's data is re-fed within an epoch. ``min_size_truncate``
    # stops at the shortest loader's end with no cycling. Tests if the
    # repeated re-feeding pattern is contributing to the F50 D5
    # reg-saturation observation.
    joint_loader_strategy: str = "max_size_cycle"

    # AUDIT-C4 fix — directory holding per-fold transition matrices
    # ``region_transition_log_fold{1..k_folds}.pt``. When set, the MTL
    # trainer overrides the static ``transition_path`` in next-head
    # params with the per-fold file before constructing the model each
    # fold. Build with ``python scripts/compute_region_transition.py
    # --state STATE --per-fold``. Default None preserves legacy
    # full-data behaviour (which leaks val rows; see C4).
    per_fold_transition_dir: Optional[str] = None

    # F50 B1 — earliest epoch (0-indexed) eligible to be selected as
    # best by the per-task BestModelTracker. Defends against
    # init-artifact peaks: with GETNext α_init=2.0, val top10 at ep 1
    # is the prior alone (not learned signal). Set ``min_best_epoch=2``
    # to force the selector past the init window. Default 0 = legacy.
    min_best_epoch: int = 0

    # C21 (mtl-protocol-fix) — which scalar gates the single joint MTL
    # checkpoint (``model_task.best``) per epoch. The headline-aligned,
    # validated default is ``geom_simple`` = sqrt(cat_macroF1 *
    # reg_Acc@10) (cat key ``f1``, reg key ``top10_acc_indist``). It
    # selects on the metrics each head is actually reported on, is
    # scale-coherent without any majority normalization, and recovered
    # +5.62 pp deployable reg Acc@10 vs the v11 selector at FL multi-seed
    # (docs/CONCERNS.md §C21). Options:
    #   "geom_simple"   — sqrt(cat_f1 * reg_top10_acc_indist)  [DEFAULT, correct]
    #   "joint_f1_mean" — 0.5*(cat_f1 + reg_f1)  [v11 paper LEGACY/broken; reproduction only]
    #   "geom_lift"     — sqrt((cat_acc1/maj)*(reg_acc1/maj))  [interim 2026-04-15 acc1-lift form]
    # For non-region task_b (no ``top10_acc_indist`` key, e.g. the
    # {category,next} preset) geom_simple falls back to that head's
    # ``f1`` → sqrt(cat_f1 * task_b_f1), a sane scale-coherent default.
    checkpoint_selector: str = "geom_simple"

    # G0.1 (pre_freeze_gates) — aligned cross-task batch pairing. When True,
    # FoldCreator builds ONE joint TRAIN loader (shared permutation, seeded
    # seed+fold_idx) so cat-window k trains paired with reg-window k (same
    # user/window; val loaders are already aligned). Default False = the
    # champion behaviour: the two task train loaders shuffle independently,
    # so cross-attention trains on randomly-paired rows. Advisory G0.1
    # verdict: NULL at FL, cat −4.77 at AL (random pairing = beneficial
    # augmentation) — see docs/studies/pre_freeze_gates/LANE1_G01_VERDICT.md.
    # Field added 2026-07-01: --aligned-pairing previously crashed in
    # dataclasses.replace (the binding G0.1 gate used lane1_run.sh instead).
    aligned_pairing: bool = False

    # F50 B9 — exempt the learnable α scalar (in next_getnext_hard*
    # heads) from AdamW weight decay. WD=0.05 applies a constant pull-
    # toward-zero force every step, fighting the gradient-driven α
    # growth needed for the STL ep 17-20 reach (α ~ 2.0). When True, α
    # gets its own param group with weight_decay=0.0. Default False
    # = legacy behaviour. Only takes effect with per-head LR mode.
    alpha_no_weight_decay: bool = False

    # F50 B4 — freeze α at its init value for the first N epochs, then
    # unfreeze. Lets cat stabilise at the un-α-amplified prior magnitude
    # before α starts growing. Set 0 (default) = legacy (α trainable
    # from epoch 0). Mirrors P3 (freeze_cat_after_epoch) but inverted:
    # P3 freezes part of cat AFTER warmup; B4 freezes α UNTIL warmup.
    # Implemented via toggling alpha.requires_grad at epoch boundary
    # (α stays a Parameter throughout — different from D1 freeze_alpha
    # which makes α a buffer permanently).
    alpha_frozen_until_epoch: Optional[int] = None

    # substrate-protocol-cleanup Tier C2 — freeze the reg-side stream
    # (task_b_encoder.* and next_head.*) at the start of epoch N and zero
    # the reg loss contribution from that epoch onward. Mirrors P3's
    # ``freeze_cat_after_epoch`` but inverted: tests whether locking in
    # the reg peak (epoch ~2-4) while continuing cat-only training
    # improves the joint deploy outcome. None disables. See
    # ``docs/studies/substrate-protocol-cleanup/INDEX.md`` §C2.
    reg_freeze_at_epoch: Optional[int] = None

    # substrate-protocol-cleanup Tier C1 — opt-in three-snapshot routing.
    # When True, the MTL runner maintains a ``MultiTaskBestTracker`` (in
    # addition to the existing single-best ``BestModelTracker``) and
    # persists three full MTL checkpoints per fold:
    # ``fold{N}_cat_best.pt`` / ``fold{N}_reg_best.pt`` / ``fold{N}_joint_best.pt``.
    # The existing single-best path is untouched. See
    # ``docs/studies/substrate-protocol-cleanup/INDEX.md`` §C1.
    save_task_best_snapshots: bool = False

    # substrate-protocol-cleanup Tier A1 / mtl-protocol-fix Phase 3 §4.5 —
    # log_T as supervisory signal. Adds a distillation KL term to the reg
    # loss (task_b_loss) of the form
    #     L_reg += log_t_kd_weight · τ² · KL(student || teacher)
    # where teacher = softmax(log_T[last_region_idx] / τ) (the per-sample
    # Markov-1 transition row from the per-fold log_T) and student =
    # softmax(reg_logits / τ). Padding rows (last_region_idx < 0 or
    # >= num_classes) excluded. Default 0.0 is a strict no-op (KD branch
    # entirely skipped). NORTH_STAR-grade promotion candidate per Phase 3
    # Rank 1 single-seed=42 sweep at AL/AZ/FL (W=0.2 strongest). Tier A1
    # multi-seed n=20 promotion test. See
    # ``docs/results/mtl_protocol_fix/phase3_rank1_findings.md`` and
    # ``docs/studies/substrate-protocol-cleanup/INDEX.md`` §A1.
    log_t_kd_weight: float = 0.0
    log_t_kd_tau: float = 1.0
    # R5 (mtl_frontier) — per-instance log_T-KD gating. Redistribute the (mean-fixed)
    # KD weight across check-ins by Markov-coverage of the sample's last-region log_T
    # row: peaked row (Markov-1 binds) → upweight KD; flat row → downweight. Mean-1
    # normalized per batch so the TOTAL KD budget matches global-W (tests redistribution,
    # not strength). "none" (default) = global W (bit-identical). See FINDINGS §R5.
    log_t_kd_gate: str = "none"  # none | coverage_max | coverage_entropy

    # R1 (mtl_frontier) — log_C co-location KD prior (ESMM probability-chain).
    # A SECOND distillation term on the reg loss whose teacher is the
    # cat-marginalized region prior:
    #     prior(reg) = Σ_c P(reg|c) · P̂(c)        (P̂ = softmax(cat_logits).detach())
    #     L_reg += log_c_kd_weight · τ² · KL(student || softmax(log(prior)/τ))
    # P(reg|c) is the per-fold/per-seed train-only matrix from
    # ``scripts/compute_region_colocation.py`` (buffer ``log_C`` on the reg head).
    # Stacks ON TOP of log_t_kd (the comparand is G WITH log_T-KD). Default 0.0 =
    # strict no-op. See docs/studies/mtl_frontier/ (R1).
    log_c_kd_weight: float = 0.0
    log_c_kd_tau: float = 1.0

    # R3 (mtl_frontier) — CrossDistil refinements over the R1 co-location KD.
    #   log_c_kd_warmup_epochs: apply BOTH co-location KD arms only from this epoch
    #     on (teacher is noisy early; CrossDistil warm-up gating). 0 = always on.
    #   log_c_kd_ec_lambda: CrossDistil ERROR-CORRECTION — blend the soft teacher
    #     with the ground-truth one-hot: teacher* = (1-λ)·teacher + λ·onehot(y).
    #     0 = pure soft teacher (R1). Corrects the synchronous teacher's errors.
    #   cat_kd_weight / cat_kd_tau: the REVERSE arm — distill the reg-implied
    #     category prior Σ_r P(cat|r)·P̂_reg(r) into the CAT head (KD on task_a_loss).
    log_c_kd_warmup_epochs: int = 0
    log_c_kd_ec_lambda: float = 0.0
    cat_kd_weight: float = 0.0
    cat_kd_tau: float = 1.0

    # T4.0a (mtl_improvement) loss-scale normalization. When True, each task's
    # raw CE is divided by ``log(num_classes_of_that_task)`` BEFORE the MTL
    # combiner / inter-task weight, decoupling the built-in ~4.7x CE-magnitude
    # gap (ln(n_regions)≈8.5 reg vs ln(7)≈1.95 cat) from the inter-task weight
    # ``w`` (DB-MTL / UW log-transform principle). Default False = strict no-op
    # (champion G + all canon versions untouched). CLI: ``--loss-scale-norm``.
    loss_scale_norm: bool = False

    # Per-task input modality (Check2HGI MTL only). These mirror the
    # ``--task-a-input-type`` / ``--task-b-input-type`` CLI flags and the
    # ``FoldCreator(task_a_input_type=..., task_b_input_type=...)`` parameters.
    # Persisting them is REQUIRED so downstream scorers (e.g.
    # ``scripts/route_task_best.py``) can rebuild the validation loaders with
    # the SAME modality the run trained on. Defaults ``"checkin"`` preserve the
    # legacy behaviour for any config that does not set them. NORTH_STAR B9
    # uses task_b="region"; scoring a region-trained reg head on checkin-modality
    # loaders silently produces garbage reg metrics (substrate-protocol-cleanup
    # Tier C1 modality bug, fixed 2026-05-28).
    task_a_input_type: str = "checkin"
    task_b_input_type: str = "checkin"

    # torch.compile: disabled by default.  On CUDA it uses the inductor
    # backend; MPS compatibility needs separate testing first.
    use_torch_compile: bool = False

    # --- Loss ---
    task_loss: str = "cross_entropy"
    mtl_loss: str = "nash_mtl"
    mtl_loss_params: dict = field(default_factory=dict)
    use_class_weights: bool = True
    # C25 (2026-06-05) — PER-TASK class weighting. The single ``use_class_weights``
    # flag silently weighted BOTH MTL heads' CE, which depresses the REG head's
    # top-K (Acc@10) metric by ~10-14pp (class-balancing optimises macro accuracy
    # AWAY from the frequency-weighted top-K the study reports), while the STL reg
    # ceiling is unweighted. These per-task overrides decouple cat/reg. ``None`` =
    # inherit ``use_class_weights`` (back-compat: legacy runs unchanged). Best
    # defaults are set in ``default_mtl`` (reg OFF for Acc@10; cat inherits, ON for
    # macro-F1). See CONCERNS.md §C25.
    use_class_weights_cat: Optional[bool] = None
    use_class_weights_reg: Optional[bool] = None
    # T1.4 STL loss calibration (next_cv.py). Empty -> legacy CrossEntropyLoss
    # path. Keys: focal_gamma, logit_adjust_tau, label_smoothing, tail_mode
    # ('balanced'|'cb'|'ldam'), cb_beta, ldam_max_m, ldam_scale. All class
    # statistics are derived from the TRAIN fold only (leak guard).
    loss_calibration: dict = field(default_factory=dict)

    # --- Cross-validation and split protocol ---
    k_folds: int = 5
    seed: int = 42
    split_relaxation: bool = False
    min_category_val_fraction: float = 0.05
    min_next_val_fraction: float = 0.05
    min_class_count: int = 5
    min_class_fraction: float = 0.03

    # --- Early stopping ---
    timeout: Optional[float] = None
    target_cutoff: Optional[float] = None
    early_stopping_patience: int = -1

    # --- Schema evolution ---
    schema_version: int = 1

    # --- Input windowing provenance (pre-freeze P3 board) ---
    # PROVENANCE ONLY — these fields are NEVER consumed by the training code
    # path; they exist so a run's manifest records HOW the windowing-dependent
    # inputs were built (see ``pipelines/create_inputs.pipe.py --stride/--min-seq``
    # and the ``<task>_build_provenance.json`` sidecar). Appended at the END of
    # the dataclass so existing positional/asdict ordering is unchanged and old
    # ``manifest.json`` / ``config.json`` files (lacking these keys) still load
    # via ``ExperimentConfig.load`` (defaults apply). ``stride=None`` means the
    # frozen non-overlapping build (step == window_size); ``min_sequence_length=5``
    # is the frozen MIN_SEQUENCE_LENGTH. DatasetSignature hashes data-file bytes,
    # not this config, so adding these fields does NOT change any signature.
    stride: Optional[int] = None
    min_sequence_length: int = 5

    def __post_init__(self):
        if self.epochs <= 0:
            raise ValueError(f"epochs must be > 0, got {self.epochs}")
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be > 0, got {self.batch_size}")
        if self.learning_rate <= 0:
            raise ValueError(f"learning_rate must be > 0, got {self.learning_rate}")
        if self.k_folds < 2:
            raise ValueError(f"k_folds must be >= 2, got {self.k_folds}")
        if self.next_target not in {"next_category", "next_poi"}:
            raise ValueError(
                f"next_target must be 'next_category' or 'next_poi', got {self.next_target!r}"
            )
        if self.schema_version != 1:
            raise ValueError(f"Unsupported schema_version: {self.schema_version}")

    def save(self, path) -> Path:
        """Serialize to JSON file.

        Args:
            path: File path (str or Path). Parent directory must exist.

        Returns:
            The Path written to.
        """
        path = Path(path)
        data = asdict(self)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path) -> ExperimentConfig:
        """Deserialize from JSON file.

        Validates schema_version before constructing.

        Args:
            path: File path (str or Path).

        Returns:
            ExperimentConfig instance.

        Raises:
            ValueError: If schema_version doesn't match.
            FileNotFoundError: If path doesn't exist.
        """
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        sv = data.get("schema_version", None)
        if sv != 1:
            raise ValueError(
                f"Cannot load ExperimentConfig with schema_version={sv} "
                f"(supported: 1)"
            )
        return cls(**data)

    # ------------------------------------------------------------------
    # Factory classmethods — produce defaults matching current code exactly
    # ------------------------------------------------------------------

    @classmethod
    def default_mtl(
        cls,
        name: str,
        state: str,
        embedding_engine: str,
        **overrides,
    ) -> ExperimentConfig:
        """MTL defaults for multi-task training."""
        defaults = dict(
            name=name,
            state=state,
            embedding_engine=embedding_engine,
            model_name="mtlnet",
            model_params={
                "feature_size": 64,
                "shared_layer_size": 256,
                "num_classes": 7,
                "num_heads": 8,
                "num_layers": 4,
                "seq_length": 9,
                "num_shared_layers": 4,
            },
            task_type="mtl",
            epochs=50,
            batch_size=2**11,  # effective batch=2048; grad_accum kept at 1 (NashMTL calls backward() internally)
            learning_rate=1e-4,
            max_lr=1e-3,
            weight_decay=0.05,
            gradient_accumulation_steps=1,
            max_grad_norm=1.0,
            optimizer_eps=1e-8,
            task_loss="cross_entropy",
            mtl_loss="nash_mtl",
            mtl_loss_params={
                # max_norm=1.0 is the upstream Nash-MTL paper default. The
                # previous 2.2 was tuned against the broken-NashMTL ([1,1])
                # regime; under real Nash weighting the dgi+alabama 2-fold
                # sweep showed 1.0 wins on cat F1/Acc and matches 2.2 on
                # next-F1 within fold noise, with the tightest per-fold
                # spread on next-F1 (range 0.001 vs 0.013 for 2.2).
                "max_norm": 1.0,
                "update_weights_every": 4,
                "optim_niter": 30,
            },
            use_class_weights=True,  # legacy master (kept for back-compat / reproduction)
            # C25 fix (2026-06-05): BOTH heads' CE are UNWEIGHTED by default.
            #   reg: class-balancing HURTS top-K Acc@10 (it optimises macro accuracy);
            #        the STL reg ceiling is unweighted. (verified: AL 56.45→64.51 ≥ ceiling.)
            #   cat: EMPIRICALLY unweighted also wins macro-F1 (+5.1pp AL: 48.37→53.51) —
            #        the "balancing helps macro-F1" assumption was FALSE (tested 2026-06-05,
            #        user-requested). So cat-CE is unweighted too.
            # Recover the pre-C25 (both-weighted) behaviour for v11-v14 reproduction with
            # ``--reg-class-weights --cat-class-weights`` (or ``--use-class-weights``).
            # See CONCERNS.md §C25 + log.md 2026-06-05 cat-axis test.
            use_class_weights_reg=False,
            use_class_weights_cat=False,
            k_folds=5,
            seed=42,
        )
        defaults.update(overrides)
        return cls(**defaults)

    @classmethod
    def default_category(
        cls,
        name: str,
        state: str,
        embedding_engine: str,
        **overrides,
    ) -> ExperimentConfig:
        """Category defaults for single-task training."""
        defaults = dict(
            name=name,
            state=state,
            embedding_engine=embedding_engine,
            model_name="category_ensemble",
            model_params={
                "input_dim": 64,
                "hidden_dim": 64,
                "num_classes": 7,
                "dropout": 0.1,
            },
            task_type="category",
            epochs=2,
            batch_size=2**10,
            learning_rate=1e-4,
            max_lr=1e-2,
            weight_decay=0.05,
            gradient_accumulation_steps=1,
            max_grad_norm=1.0,
            optimizer_eps=1e-8,
            task_loss="cross_entropy",
            mtl_loss="",
            mtl_loss_params={},
            use_class_weights=False,
            k_folds=5,
            seed=42,
        )
        defaults.update(overrides)
        return cls(**defaults)

    @classmethod
    def default_next(
        cls,
        name: str,
        state: str,
        embedding_engine: str,
        **overrides,
    ) -> ExperimentConfig:
        """Next-POI defaults for single-task training."""
        defaults = dict(
            name=name,
            state=state,
            embedding_engine=embedding_engine,
            model_name="next_single",
            model_params={
                "embed_dim": 64,
                "num_classes": 7,
                "num_heads": 4,
                "seq_length": 9,
                "num_layers": 4,
                "dropout": 0.1,
            },
            task_type="next",
            epochs=100,
            batch_size=2**10,
            learning_rate=1e-4,
            max_lr=1e-2,
            weight_decay=0.01,
            gradient_accumulation_steps=1,
            max_grad_norm=1.0,
            optimizer_eps=1e-8,
            task_loss="cross_entropy",
            mtl_loss="",
            mtl_loss_params={},
            use_class_weights=True,
            k_folds=5,
            seed=42,
            early_stopping_patience=-1,
        )
        defaults.update(overrides)
        return cls(**defaults)


# ---------------------------------------------------------------------------
# RunManifest — write-only provenance record
# ---------------------------------------------------------------------------

@dataclass
class DatasetSignature:
    """Immutable fingerprint of a dataset file."""
    path: str
    sha256: str
    size_bytes: int
    mtime: str  # ISO 8601

    @staticmethod
    def from_path(p: Path) -> DatasetSignature:
        """Compute signature from a file on disk."""
        p = Path(p)
        h = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        stat = p.stat()
        return DatasetSignature(
            path=str(p.resolve().as_posix()),
            sha256=h.hexdigest(),
            size_bytes=stat.st_size,
            mtime=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        )


def _get_git_commit() -> str:
    """Return current git commit hash, or 'unknown' if not in a repo."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


@dataclass
class RunManifest:
    """Write-only provenance record. Serialized as manifest.json.

    Never drives training — only captures what happened.
    """
    config: ExperimentConfig
    git_commit: str
    seeds: dict
    pytorch_version: str
    device: str
    deterministic_flags: dict
    timestamp: str  # ISO 8601
    dataset_signatures: dict  # str -> DatasetSignature
    split_signature: Optional[DatasetSignature] = None
    feasibility_report_signature: Optional[DatasetSignature] = None
    schema_version: int = 1

    def write(self, output_dir: Path) -> Path:
        """Serialize as manifest.json in output_dir.

        Returns:
            Path to the written manifest file.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "manifest.json"

        data = {
            "config": asdict(self.config),
            "git_commit": self.git_commit,
            "seeds": self.seeds,
            "pytorch_version": self.pytorch_version,
            "device": self.device,
            "deterministic_flags": self.deterministic_flags,
            "timestamp": self.timestamp,
            "dataset_signatures": {
                k: asdict(v) if hasattr(v, "__dataclass_fields__") else v
                for k, v in self.dataset_signatures.items()
            },
            "split_signature": (
                asdict(self.split_signature)
                if self.split_signature is not None
                else None
            ),
            "feasibility_report_signature": (
                asdict(self.feasibility_report_signature)
                if self.feasibility_report_signature is not None
                else None
            ),
            "schema_version": self.schema_version,
        }
        path.write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )
        return path

    @classmethod
    def from_current_env(
        cls,
        config: ExperimentConfig,
        dataset_paths: Optional[dict[str, Path]] = None,
        split_path: Optional[Path] = None,
        feasibility_path: Optional[Path] = None,
    ) -> RunManifest:
        """Capture current environment into a manifest.

        Args:
            config: The experiment config used for this run.
            dataset_paths: Mapping of dataset name to file path.
            split_path: Path to the split manifest artifact.
            feasibility_path: Path to the feasibility report artifact.
        """
        import torch

        dataset_sigs = {}
        if dataset_paths:
            for name, p in dataset_paths.items():
                p = Path(p)
                if p.exists():
                    dataset_sigs[name] = DatasetSignature.from_path(p)

        split_sig = None
        if split_path is not None and Path(split_path).exists():
            split_sig = DatasetSignature.from_path(split_path)

        feasibility_sig = None
        if feasibility_path is not None and Path(feasibility_path).exists():
            feasibility_sig = DatasetSignature.from_path(feasibility_path)

        return cls(
            config=config,
            git_commit=_get_git_commit(),
            seeds={
                "torch_manual_seed": config.seed,
                "numpy_seed": config.seed,
                "python_seed": config.seed,
            },
            pytorch_version=torch.__version__,
            device=str(torch.device(
                "mps" if torch.backends.mps.is_available()
                else "cuda" if torch.cuda.is_available()
                else "cpu"
            )),
            deterministic_flags={
                "torch.backends.cudnn.deterministic": (
                    torch.backends.cudnn.deterministic
                    if hasattr(torch.backends, "cudnn")
                    else False
                ),
                "torch.backends.cudnn.benchmark": (
                    torch.backends.cudnn.benchmark
                    if hasattr(torch.backends, "cudnn")
                    else False
                ),
            },
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            dataset_signatures=dataset_sigs,
            split_signature=split_sig,
            feasibility_report_signature=feasibility_sig,
        )
