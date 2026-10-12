"""Configuration — frozen, validated at construction, serialised with every result.

Three properties this module is built to guarantee:

1. **Nothing scientific comes from the environment.** A run is fully described by its recipe plus
   its explicit overrides. (`paths.py` owns the three location variables; that is all.)
2. **Invalid science does not construct.** A recipe that puts logit adjustment on the region head,
   or stacks it with class weighting, raises here — it does not warn in a log that nobody reads.
3. **What is recorded is what ran.** `Resolved.fingerprint()` hashes the resolved config, and the
   runner writes that object into the result. The reference implementation hand-wrote
   `"precision": "fp32"` into its provenance files while autocast ran fp16; that class of lie is
   structurally impossible here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import tomllib
from dataclasses import dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import Any

from .device import Precision

# The v18 experiment matrix. Georgia was dropped by author decision 2026-08-12: it appears in the
# pre-v18 matrix but has no v18 cell. Recorded as a deliberate loss of coverage.
DATASETS = ("alabama", "arizona", "istanbul", "florida", "california", "texas")

SEEDS = (0, 1, 7, 100)


class TaskFamily(str, Enum):
    CAT = "cat"
    REG = "reg"
    JOINT = "joint"


class Pairing(str, Enum):
    """How the two task streams are paired inside a joint training batch.

    RANDOM is what every banked v18 cell trained under: the two loaders draw independent shuffles,
    so cross-attention sees randomly-paired category/region rows at train time (validation is always
    aligned). ALIGNED is the opt-in alternative whose gate was never closed.

    This is not a performance knob. Switching it changes the training distribution of the shared
    trunk, and no headline conclusion would detect the change.
    """

    RANDOM = "random"
    ALIGNED = "aligned"


class Selector(str, Enum):
    GEOM_SIMPLE = "geom_simple"       # sqrt(cat macro-F1 * reg top10_indist) — the v18 selector
    JOINT_F1_MEAN = "joint_f1_mean"   # 0.5*(cat_f1 + reg_f1) — the legacy v11 selector


@dataclass(frozen=True)
class SubstrateConfig:
    """Layer 1 — how a substrate is built."""

    engine: str
    forward_only: bool = True
    continuous_time: bool = True
    encoder: str = "resln"
    dim: int = 64
    num_layers: int = 2
    epochs: int = 500
    repr_seed: int = 42

    # The V14 objective, pinned. These are not tuning knobs: they were frozen in the reference's own
    # builder for the same reason they are frozen here — so an upstream default cannot drift a study
    # that has already banked numbers.
    attention_head: int = 4
    dropout: float = 0.1
    alpha_c2p: float = 0.4
    alpha_p2r: float = 0.3
    alpha_r2c: float = 0.3
    mae_poi_lambda: float = 0.3
    mae_poi_mask_rate: float = 0.15
    mae_poi_gamma: float = 3.0
    anchor_lambda: float = 0.1
    gamma_init: float = 1.0
    lr: float = 1e-3
    weight_decay: float = 0.0
    max_norm: float = 0.9

    # The POI↔region hard-negative rate and similarity band.
    p2r_hard_neg_prob: float = 0.25
    p2r_hard_neg_sim_range: tuple[float, float] = (0.6, 0.8)
    # Place count above which hard negatives switch OFF. `None` — the default — means they are
    # always on, which is the recipe as designed. The reference hard-codes 50 000, which silently
    # trains small and large states on different objectives (S17); set it to 50_000 only to
    # reproduce that split.
    p2r_hard_neg_size_gate: int | None = None

    #: ── Os dois defeitos REPRODUZIDOS do scaffolding, agora alcançáveis por receita ──────────────
    #:
    #: Existiam só como parâmetro de função (`delaunay.build`, `poi2vec.build`), o que os tornava
    #: inalcançáveis por uma wave e portanto impossíveis de medir sob o regime de proveniência do
    #: projeto. Os defaults **preservam exatamente** o comportamento de antes: as duas funções já
    #: tinham `False` como default, então passar `False` explicitamente é o mesmo caminho de código.
    #:
    #: `fix_unit_mismatch`: o peso da aresta compara a diagonal do bounding box em GRAUS com a
    #: distância em METROS, e o log sai negativo em 98,56 % das arestas — a penalidade de cruzar
    #: região vira BÔNUS. Ligar corrige as unidades. É a mudança de maior alcance do backlog.
    #:
    #: `symmetrise_poi2vec`: o `edges.csv` guarda cada par não-dirigido uma vez e a referência NÃO
    #: simetriza antes de caminhar, então a caminhada só anda de índice menor para maior.
    fix_unit_mismatch: bool = False
    symmetrise_poi2vec: bool = False

    #: Width of the masked-place reconstruction target. **8, and that is a reproduced defect.**
    #:
    #: The reference slices `len(CATEGORIES_MAP)` columns off the node-feature matrix to build the
    #: target. `CATEGORIES_MAP` has eight entries — seven real categories plus a sentinel `None`
    #: that no corpus uses — while the feature matrix is `7 one-hot + hour_sin + hour_cos + ...`.
    #: So target column 7 is each place's **mean hour_sin**, not a category at all. Measured at
    #: Alabama: that column has mean −0.4447, sd 0.3789, spans [−1, 1], and 48.9% of places carry
    #: |value| > 0.5; the cosine between the reference's 8-d target and the intended 7-d one
    #: averages 0.8785 (5th pct 0.7193). The loss is a scaled COSINE error, so this is not rounding.
    #:
    #: Reproduced rather than fixed because BOTH banked substrates carry it (`build_study_repr.py`
    #: uses the same call site), so 7 would be a different objective and every banked number would
    #: be unreproducible. Set it to 7 only for a deliberate ablation, and say so.
    mae_poi_target_dim: int = 8

    def __post_init__(self) -> None:
        if self.dim != 64:
            # 64 is hard-wired in three places: the encoder, the Delaunay place-table anchor's
            # fixed 64-d distillation target, and the downstream head's embedding dimension.
            raise ValueError("substrate dim is fixed at 64 (three downstream consumers assume it)")
        if self.encoder not in ("resln", "gcn"):
            raise ValueError(f"unknown encoder {self.encoder!r}; v18 uses 'resln'")
        if not self.forward_only:
            # v19: o grafo de check-ins é sempre forward-only. O filtro vale 28,63 pp de macro-F1 e
            # não é uma pergunta em aberto, então um grafo bidirecional deixa de ser construível por
            # receita. O parâmetro `forward_only` de `graph.build` continua existindo e testado — o
            # que sai é a possibilidade de uma RECEITA pedir a versão vazada.
            #
            # ⚠ Isto fecha o canal de vazamento LINHA A LINHA, e só ele. O substrato continua
            # treinado uma vez sobre o corpus inteiro, sem split de fold, então toda linha do teste
            # externo esteve no treino do pretexto; o objetivo do pretexto e os níveis agregados
            # seguem transdutivos. "O substrato é causal" é falso e continua falso.
            raise ValueError(
                "forward_only=false não é construível a partir de v19: o filtro forward-only é a "
                "correção de vazamento do eixo de check-ins. Para reconstruir o substrato "
                "bidirecional que a dissertação usou, use o SHA registrado em "
                "studies/porting_validation/SUBSTRATE_FROM_SCRATCH.md.")
        if self.continuous_time and not self.forward_only:
            # v18 is forward-only WITH elapsed time; v14 is bidirectional WITHOUT it. The pairing is
            # not arbitrary: the elapsed-time columns are measured up to the visit itself precisely
            # so they cannot reintroduce the leak the forward-only filter removes. Under a
            # bidirectional graph that argument does not hold and the combination has never been
            # built or measured, so it is refused rather than silently allowed.
            raise ValueError(
                "continuous_time on a bidirectional graph is an unbuilt combination: the elapsed-"
                "time features are justified by the forward-only filter. Use forward_only=true "
                "(v18) or continuous_time=false (v14).")


@dataclass(frozen=True)
class DataConfig:
    """Layer 2 — how check-ins become windows, and how windows become folds."""

    window: int = 9
    min_sequence_length: int = 10
    stride: int = 1
    n_splits: int = 5
    #: Which PARTITION the folds are drawn from — the repetition factor (NOMENCLATURE §1). Distinct
    #: from `TrainConfig.seed`, which only re-initialises the model on a FIXED partition (a
    #: replicate). One integer driving both is the conflation the protocol exists to remove: it
    #: makes partition variance and initialisation variance inseparable, so neither can be reported.
    #: `None` means "use the model seed", the legacy behaviour — allowed, but a confirmatory cell
    #: refuses to persist predictions under it, because the sidecar would claim two factors it has
    #: only one value for.
    split_seed: int | None = None
    #: Protocol §2: carve a user-disjoint 10% inner-validation set out of each fold's development
    #: block and select the checkpoint there, so the outer 20% is read exactly once. OFF by default
    #: because it CHANGES RESULTS — the legacy path selects and reports on the same fold.
    inner_validation: bool = False
    inner_splits: int = 8
    #: Separate from the outer split's seed on purpose (NOMENCLATURE §1): one integer driving two
    #: partitions is the confound this project already paid for.
    inner_split_seed: int = 0
    #: De onde a torre de região lê seus embeddings. **Toda receita v19 nomeia este campo
    #: explicitamente**, e o valor vivo é o próprio substrato — a mesma fonte que a torre de
    #: check-in. Em v18 era um substrato separado e bidirecional, que na referência era literalmente
    #: um symlink dentro do diretório do engine v18.
    #:
    #: ⚠ **O default abaixo é COMPATIBILIDADE, não escolha, e não pode mudar.** Ele só é alcançado
    #: por receitas arquivadas que não nomeiam o campo — `recipes/v18/cat.toml` é uma delas. O
    #: resume compara o digest do config BANCADO contra um resolve fresco (`wave.py:214-217`), então
    #: mexer neste default marcaria como stale toda célula `cat` selada e dispararia re-treino —
    #: isto é, **uma segunda leitura do teste externo**. Foi tentado em 19-08 e revertido no mesmo
    #: dia, antes de rodar.
    region_engine: str = "check2hgi_design_k_resln_mae_l0_1"


@dataclass(frozen=True)
class OptimConfig:
    lr: float = 1e-4
    weight_decay: float = 0.01
    eps: float = 1e-8
    beta2: float = 0.999
    max_grad_norm: float = 1.0
    scheduler: str = "onecycle"
    max_lr: float = 3e-3
    # Per-head learning rates: joint only. All three must be set or none — in the reference, a
    # half-set trio silently broadcast the scalar max_lr to every group and turned a v17 run into
    # a v16 run with no message.
    cat_lr: float | None = None
    reg_lr: float | None = None
    shared_lr: float | None = None

    def __post_init__(self) -> None:
        per_head = [self.cat_lr, self.reg_lr, self.shared_lr]
        if any(x is not None for x in per_head) and not all(x is not None for x in per_head):
            raise ValueError(
                "cat_lr / reg_lr / shared_lr must be set together or not at all — a partial trio "
                "silently degrades to the scalar max_lr on every parameter group"
            )


@dataclass(frozen=True)
class LossConfig:
    """Per-head loss shaping.

    `logit_adjust_tau` adds `tau * log P_train(y)` to the logits at TRAIN time only, from train-split
    class counts. It REPLACES class weighting — the two are mutually exclusive, enforced below.
    """

    logit_adjust_tau: float = 0.0
    class_weights: bool = False
    label_smoothing: float = 0.0

    def __post_init__(self) -> None:
        if self.logit_adjust_tau > 0 and self.class_weights:
            raise ValueError(
                "logit adjustment and class weighting are mutually exclusive: logit adjustment "
                "replaces weighted CE (stacking them was measured and it craters)"
            )
        if self.logit_adjust_tau < 0:
            raise ValueError("logit_adjust_tau must be >= 0")


@dataclass(frozen=True)
class HeadConfig:
    """Which head, and with which hyperparameters.

    This exists because of a trap in the reference. Its CLI's `--model` swaps only the head CLASS;
    every hyperparameter still comes from the task factory's `model_params`. So the v18 category
    head is `next_gru` with **4 layers and dropout 0.1** — inherited from the factory — while the
    module's own defaults are 2 layers and dropout 0.3. Reading the head's source tells you nothing
    about what ran, and building it from its defaults gives a model less than half the size
    (644 359 parameters against the 1 433 863 the run reports).

    So the head's identity and its shape live in the recipe, travel in the resolved config, and land
    in the fingerprint.
    """

    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainConfig:
    """Layer 3 — one training cell."""

    family: TaskFamily
    state: str
    #: The MODEL seed — initialisation, shuffling, dropout. NOT fold membership: that is
    #: `DataConfig.split_seed`. Re-running this alone is a replicate, not a repetition.
    seed: int
    engine: str
    epochs: int = 50
    batch_size: int = 8192
    folds: int = 5
    precision: Precision = Precision.FP32
    compile: bool = False
    tf32: bool = False
    optim: OptimConfig = field(default_factory=OptimConfig)
    cat_head: HeadConfig | None = None
    reg_head: HeadConfig | None = None
    cat_loss: LossConfig = field(default_factory=LossConfig)
    reg_loss: LossConfig = field(default_factory=LossConfig)
    # Joint only
    category_weight: float = 0.50
    pairing: Pairing = Pairing.RANDOM
    selector: Selector = Selector.GEOM_SIMPLE
    min_best_epoch: int = 0
    # Diagnostics that cost wall-clock; off in the v18 protocol.
    train_metrics: bool = False
    #: Per-epoch timing, convergence shape, gradient geometry, peak memory, health scalars.
    #: DEFAULT-ON since 2026-08-18. It was False, which made every T1/T2/T5 field dead in a default
    #: run while `result.json` still recorded `grad_geometry: true` — `--no-grad-probe` was an
    #: off-switch for something already off, and every confirmatory bridge cell banked
    #: `"diagnostics": {}`, so the trunk-orthogonality claim was measured in none of them.
    diagnostics: bool = True
    #: The gradient-geometry probe (joint only). DEFAULT-ON since 2026-08-18.
    #:
    #: It used to force eager, because taking a second gradient through the training graph fights
    #: the compiled backward — measured at 35.2% of wall, of which 24.4% was losing compilation and
    #: only 8.7% was the probe. `gradient_geometry_sidecar` gives the probe its own eager graph on
    #: the uncompiled base module, so training stays compiled and the cost falls to 14.0% (Alabama,
    #: the worst case: ~9 training batches per epoch).
    #:
    #: On by default because the alternative to measuring it during the run is measuring it in a
    #: SECOND run — +100%, against +14%. The reference left it off, and the bill was at least four
    #: training campaigns, one wholly lost remote night, and one question (the cosine at CA/TX) that
    #: is permanently unanswered. Turn it off with `--no-grad-probe` when you know you do not want
    #: it; do not turn it off to save time you have not measured.
    grad_geometry: bool = True
    #: Which weights survive the run: "none" | "selected" | "every". DEFAULT "none".
    #:
    #: It was "selected", which made every screening cell write a 13.7 MB file that the screening
    #: path cannot consume: §5 re-fits winners under sealed confirmation anyway, and under sealing a
    #: screening cell never evaluates the outer fold at all. At hundreds of cells a week that is
    #: 7-68 GB of write-only output, and this document's own rule — a field enters the artifact only
    #: with a named consumer — decides against it. Weights are the largest field of all.
    #:
    #: "selected" belongs to CONFIRMATORY recipes: one file per fold, the model a deployment claim
    #: is about, ~4.9 GB for the whole package. That is the evidentiary base, and it is what makes
    #: an independent re-score possible — the check champion G could not get for want of a .pt.
    #:
    #: "every" is for §8a, TRANSIENTLY. The protocol prices it as "transient checkpoint storage"
    #: and scopes the scoring pass per STATE ("refuses to run until all seeds x folds of a state are
    #: complete"), so the pipeline is retain -> score -> cross-check -> DELETE, one state at a time:
    #: ~42 GB peak, permanent output a few KB of scalars. Retaining without deleting is not §8a
    #: being expensive; it is half of §8a.
    retain_checkpoints: str = "none"
    #: How many top predictions to retain per outer-test row, with their probabilities. 0 disables.
    #:
    #: Pre-registered consumers, written down BEFORE the field existed so a later analysis is
    #: verifiable against this list rather than invented after the fact (docs/TELEMETRY_GUIDE.md §5.4):
    #: U5 (how far is the predicted region when the model errs), cross-arm error overlap (does the
    #: joint model fix the SAME rows the dedicated one does), abstention curves, and calibration.
    #: ⚠ Calibration is never a lever on the reported metric: any monotone class-uniform transform
    #: leaves the top-10 set unchanged, so improving ECE cannot move Acc@10.
    keep_top_k: int = 20
    decorrelated_fold_seed: bool = False

    def __post_init__(self) -> None:
        if self.state not in DATASETS:
            raise ValueError(f"unknown dataset {self.state!r}; expected one of {DATASETS}")
        if self.retain_checkpoints not in ("none", "selected", "every"):
            raise ValueError(f"retain_checkpoints={self.retain_checkpoints!r}; expected one of "
                             f"'none', 'selected', 'every'")

        # S3 — logit adjustment is Bayes-consistent for BALANCED error. It raises the region head's
        # macro-F1 and LOWERS its Acc@1/5/10 and MRR, measured at two datasets with every one of ten
        # comparisons significant and in the predicted direction. Region is reported by Acc@10.
        if self.reg_loss.logit_adjust_tau > 0:
            raise ValueError(
                "logit adjustment must stay OFF for the region head: it is optimal for macro-F1 and "
                "sub-optimal for frequency-weighted ranking, and region is reported by Acc@10 "
                "(measured: AL -1.841 pp p=0.0002, IST -2.749 pp p<0.0001)"
            )

        if self.family is TaskFamily.CAT and self.cat_head is None:
            raise ValueError("the category family needs cat_head; a head built from its module "
                             "defaults is a different model than the one v18 ran")
        if self.family is TaskFamily.REG and self.reg_head is None:
            raise ValueError("the region family needs reg_head")
        if self.family is TaskFamily.JOINT and (self.cat_head is None or self.reg_head is None):
            raise ValueError(
                "the joint family needs BOTH cat_head and reg_head. Falling back to module "
                "defaults builds a category head half the size at triple the dropout, and no "
                "shape check would notice"
            )

        if self.family is not TaskFamily.JOINT:
            if self.optim.cat_lr is not None:
                raise ValueError("per-head learning rates apply to the joint family only")
        else:
            if not 0.0 <= self.category_weight <= 1.0:
                raise ValueError(f"category_weight must be in [0, 1], got {self.category_weight}")
            # The per-head trio is not optional for this family. In the reference it only took
            # effect because a driver exported MTL_ONECYCLE_PER_HEAD_LR=1; without it the scalar
            # max_lr broadcast to every parameter group and the run was silently the previous
            # recipe. Omitting the rates here would reproduce that failure exactly.
            if self.optim.cat_lr is None:
                raise ValueError(
                    "the joint family requires cat_lr / reg_lr / shared_lr. Without them the scalar "
                    "max_lr broadcasts to every parameter group, which is a different recipe that "
                    "runs without complaint"
                )

    # No `cell_id` here on purpose: a cell is identified by BOTH seeds (protocol §10.5) and this
    # dataclass holds only the model one. The property lives on `Resolved`, which holds both.


#: Fields that decide what a run RECORDS, never what it computes. Excluded from the resume hash.
#: Adding one here is a claim that flipping it cannot move any number — verify before you do.
TELEMETRY_FIELDS = ("diagnostics", "grad_geometry", "retain_checkpoints", "keep_top_k")


def science_digest(payload: dict[str, Any]) -> str:
    """The resume hash of a config dict, telemetry stripped.

    Takes a dict rather than a `Resolved` so a BANKED result can be re-hashed from the config it
    recorded. Without that, a cell banked before this function existed has no `science_fingerprint`
    to compare, the reader falls back to the old full `config_fingerprint`, and the comparison is
    apples to oranges — every historical cell reads stale and re-runs, which for a sealed cell means
    a second read of the outer test. Migration by recomputation, not by mutating banked artifacts.
    """
    payload = json.loads(json.dumps(payload))          # cheap deep copy; the input is JSON already
    for field_name in TELEMETRY_FIELDS:
        payload.get("train", {}).pop(field_name, None)
        # Also from `overrides`, which records what the CALLER asked for. Stripping only the
        # resolved value leaves `--set diagnostics=true` in the hash, so the exclusion silently does
        # nothing for exactly the runs that use it.
        payload.get("overrides", {}).pop(field_name, None)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Resolved:
    """A fully-resolved run description — the object the runner uses and the result records."""

    train: TrainConfig
    data: DataConfig
    recipe: str          # provenance: which recipe file this came from
    overrides: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # `train.folds` NÃO tem leitor: quem decide o número de folds é `data.n_splits`. Mas ele
        # entra no `science_fingerprint`, então sobrepor um sem o outro dá identidade nova a um
        # experimento idêntico -- e um leitor que confie no campo lê um número que não governou
        # nada. Descoberto em 25-08 com `set = { folds = 2 }`, que rodou 5 folds em silêncio.
        if self.train.folds != self.data.n_splits:
            raise ValueError(
                f"train.folds={self.train.folds} e data.n_splits={self.data.n_splits} divergem. "
                f"Quem governa a validação cruzada é `n_splits`; `folds` só entra no fingerprint. "
                f"Deixe os dois iguais — ou sobreponha `n_splits`, que é o que de fato roda.")

    def to_dict(self) -> dict[str, Any]:
        return _as_plain(dataclasses.asdict(self))

    @property
    def cell_id(self) -> str:
        """The run-directory name. Both seeds, because both are experimental factors."""
        from . import paths
        split = self.data.split_seed if self.data.split_seed is not None else self.train.seed
        return paths.cell_id(self.train.family.value, self.train.state, self.train.seed, split)

    def fingerprint(self) -> str:
        """Stable hash of the resolved configuration. Two runs with the same fingerprint asked for
        the same thing; two results with different fingerprints are not directly comparable."""
        blob = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()[:16]

    def science_fingerprint(self) -> str:
        """The same hash MINUS the fields that cannot change a number. This is what resume compares.

        Telemetry is not science. `diagnostics`, `grad_geometry`, `retain_checkpoints` and
        `keep_top_k` decide what a run WRITES DOWN, not what it computes: the probe forks the RNG,
        retention only saves files, and the top-K block is extra columns on a pass that happens
        anyway. Yet all four sat inside the resume hash, so merely turning telemetry on rotated the
        fingerprint of all 36 banked bridge cells and the next `wave run` would have re-trained
        them — and, because a re-run is not bit-identical, silently installed a SECOND read of the
        sealed outer test underneath a table already reported.

        A resume key that reacts to instrumentation is a resume key that punishes measuring things.
        """
        return science_digest(self.to_dict())


def _as_plain(obj: Any) -> Any:
    """dataclasses.asdict leaves Enums as Enums; JSON and hashing want their values."""
    if isinstance(obj, dict):
        return {k: _as_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_as_plain(v) for v in obj]
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Path):
        return str(obj)
    return obj


# ---------------------------------------------------------------- recipes

def load_recipe(path: str | Path, **overrides: Any) -> Resolved:
    """Build a `Resolved` from a frozen recipe file plus explicit overrides.

    Recipes are immutable once a run cites them: changing a recipe that a banked result points at
    would rewrite history. A new setting is a new file.
    """
    path = Path(path)
    with path.open("rb") as fh:
        raw = tomllib.load(fh)

    data = DataConfig(**raw.get("data", {}))
    train_raw: dict[str, Any] = dict(raw.get("train", {}))

    # Per-state tables: any `<key>_by_state` table resolves against the state being run, at any
    # nesting depth (`[train.max_lr_by_state]`, `[train.optim.cat_lr_by_state]`, ...).
    state = overrides.get("state", train_raw.get("state"))
    _resolve_by_state(train_raw, state, path.name)

    optim_raw = train_raw.pop("optim", {})
    cat_loss_raw = train_raw.pop("cat_loss", {})
    reg_loss_raw = train_raw.pop("reg_loss", {})
    cat_head_raw = train_raw.pop("cat_head", None)
    reg_head_raw = train_raw.pop("reg_head", None)

    train_raw.update(overrides)
    # Route data-shaped overrides (`--set inner_validation=true`) into DataConfig. Without this an
    # override silently lands on TrainConfig and raises, or worse, would be ignored — the field name
    # is the routing key, so the two dataclasses must not share one.
    data_fields = {f.name for f in fields(DataConfig)}
    data_overrides = {k: train_raw.pop(k) for k in list(train_raw) if k in data_fields}
    if data_overrides:
        data = dataclasses.replace(data, **data_overrides)
    # Route optimizer-shaped overrides (`--set max_lr=...`) into the nested dataclass.
    for key in list(train_raw):
        if key in {f.name for f in dataclasses.fields(OptimConfig)}:
            optim_raw[key] = train_raw.pop(key)

    train = TrainConfig(
        family=TaskFamily(train_raw.pop("family")),
        precision=Precision(train_raw.pop("precision", "fp32")),
        pairing=Pairing(train_raw.pop("pairing", "random")),
        selector=Selector(train_raw.pop("selector", "geom_simple")),
        optim=OptimConfig(**optim_raw),
        cat_head=_head(cat_head_raw),
        reg_head=_head(reg_head_raw),
        cat_loss=LossConfig(**cat_loss_raw),
        reg_loss=LossConfig(**reg_loss_raw),
        **train_raw,
    )
    return Resolved(train=train, data=data, recipe=_proveniencia(path),
                    overrides=dict(overrides))


def _proveniencia(path: Path | str) -> str:
    """O caminho da receita como PROVENIÊNCIA, não como acidente do chamador.

    Este campo entra no `science_fingerprint`, e o `science_digest` hasheia os nomes E os valores.
    Grafá-lo como veio dava identidades diferentes para a MESMA receita conforme quem chamou usasse
    caminho relativo ou absoluto — e o absoluto carrega o nome da máquina. Medido em 2026-08-24:
    `recipes/v19/cat.toml` resolvia para `635f9f82598e` pelo relativo e `8489fe112ebd` pelo absoluto,
    e este segundo valor era diferente no A40. A identidade científica passava a depender de onde o
    repositório está montado.

    Todas as células bancadas vieram de manifesto de wave, que grava relativo, então canonizar para
    relativo não move nenhuma delas — conferido nas 54 da campanha selada.
    """
    from . import paths

    absoluto = Path(path).resolve()
    try:
        return str(absoluto.relative_to(paths.repo_root()))
    except ValueError:
        # Fora da árvore (teste, scratch): não há relativo canônico, mas o ABSOLUTO ao menos não
        # depende de como o chamador digitou. Devolver `path` cru faria duas grafias do mesmo
        # arquivo terem duas identidades — o defeito que esta função existe para fechar.
        return str(absoluto)


def load_substrate_recipe(path: str | Path) -> SubstrateConfig:
    """Read a `[substrate]` recipe. Separate from `load_recipe` because layer 1 has no train block.

    Unknown keys are refused rather than ignored: a typo in a frozen recipe that silently falls back
    to a default is how a run ends up being a different experiment than its file says.
    """
    path = Path(path)
    with path.open("rb") as fh:
        raw = tomllib.load(fh)

    section = raw.get("substrate")
    if section is None:
        raise ValueError(f"{path} has no [substrate] section")

    known = {f.name for f in fields(SubstrateConfig)}
    unknown = sorted(set(section) - known)
    if unknown:
        raise ValueError(f"{path}: unknown [substrate] keys {unknown}; known keys are "
                         f"{sorted(known)}")
    return SubstrateConfig(**section)


def _head(raw: dict[str, Any] | None) -> "HeadConfig | None":
    if raw is None:
        return None
    raw = dict(raw)
    return HeadConfig(name=raw.pop("name"), params=raw)


def _resolve_by_state(section: dict[str, Any], state: str | None, where: str) -> None:
    """Collapse every `<key>_by_state` table in `section` (recursively) to the running state's value."""
    for key in list(section):
        value = section[key]
        if isinstance(value, dict) and not key.endswith("_by_state"):
            _resolve_by_state(value, state, where)
        elif key.endswith("_by_state"):
            table = section.pop(key)
            if state is None:
                raise ValueError(f"{where} has {key} but no state was given")
            if state not in table:
                raise ValueError(f"{where}:{key} has no entry for state {state!r}")
            section[key[: -len("_by_state")]] = table[state]


def parse_set(assignments: list[str]) -> dict[str, Any]:
    """Parse `--set key=value` pairs, inferring int / float / bool / str."""
    out: dict[str, Any] = {}
    for item in assignments:
        if "=" not in item:
            raise ValueError(f"--set expects key=value, got {item!r}")
        key, _, value = item.partition("=")
        out[key.strip()] = _coerce(value.strip())
    return out


def _coerce(value: str) -> Any:
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            pass
    return value


__all__ = [
    "DATASETS", "SEEDS", "TaskFamily", "Pairing", "Selector", "Precision",
    "SubstrateConfig", "DataConfig", "OptimConfig", "LossConfig", "HeadConfig",
    "TrainConfig", "Resolved",
    "load_recipe", "parse_set",
]
