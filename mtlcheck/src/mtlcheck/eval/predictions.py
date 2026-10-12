"""The persistence contract: one row per held-out prediction, with everything inference needs.

This is the first thing built and the only thing that cannot be added later. Every other part of the
protocol is post-processing and can be redone from these rows; the rows themselves exist only while
the model runs. A confirmatory wave that forgets them loses all of Tier A — the user-cluster
bootstrap, the permutation test, every interval that carries a headline claim — and the only remedy
is retraining.

## What a row is

One held-out window, evaluated once by the selected checkpoint. `rank_of_true` is the rank of the
true class in the model's ranking (1 = top), which is all the region metric needs; `y_pred` is the
arg-max, which is what the category metric needs. Both are stored because deriving one from the
other after the fact is impossible.

## What travels beside the rows

`train_labels` — the label set the fold's TRAINING split contained. It is not recoverable later, and
`ood_fraction` and the `ood_hit_rate` leak canary both depend on it. A prediction file without it can
report an accuracy but cannot report whether that accuracy came from a leak.

`partition_hash` — the digest of the realised user→fold assignment. The hash is ground truth and the
seed is only the recipe (protocol §10.5): a reader asserts the hash, never re-derives the split from
the seed and hopes.

## Under the legacy protocol these rows are not yet sealed

Today's runner uses one held-out fold both to select the checkpoint and to report. So rows persisted
now come from observations that also chose the epoch, and any Tier A interval computed on them
inherits that selection bias. The rows are still worth persisting — the machinery is identical — but
`sealed=False` is recorded in the manifest and every consumer must surface it. The inner-validation
split of protocol §2 is what flips it to True, and that is a separate change with its own gate.
"""

from __future__ import annotations

import hashlib
import json
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

#: v2 = identidade científica no sidecar. As 54 células da campanha `v19_defence` são v1.
SCHEMA_VERSION = 2

#: Columns every prediction file carries, in order. A reader validates against this exactly — a
#: missing column is an error, never a default, because a silently-absent `userid` would turn a
#: user-clustered bootstrap into a row bootstrap and quietly narrow every interval.
COLUMNS = (
    "state", "arm", "task", "split_seed", "partition_hash", "model_seed",
    "fold", "userid", "window_id", "selected_epoch", "y_true", "y_pred", "rank_of_true",
)

#: The optional distribution block (docs/TELEMETRY_GUIDE.md §5.4). Present together or not at all — a reader that
#: found `top_ids` without `logsumexp` could renormalise over the truncated set and silently report
#: a different probability than the model produced.
DISTRIBUTION_COLUMNS = ("top_ids", "top_log_probs", "true_prob", "logsumexp")

# O contrato do sidecar. Escritor, leitor e teste importam AS MESMAS tuplas, então renomear uma
# chave quebra os dois lados juntos em vez de abrir um silêncio — a disciplina de `COLUMNS` acima,
# estendida ao `predictions_meta.json`.

#: Computadas das linhas; `extra` não sobrescreve, senão reescreveria a resposta em vez de reportá-la.
META_SELF = ("schema_version", "state", "split_seed", "partition_hash", "model_seed",
             "sealed", "rows", "has_distribution", "top_k", "users", "train_labels",
             "selected_epoch")

#: A única com dois donos: um braço pode ter nome próprio quando difere da família.
META_SELF_OVERRIDABLE = ("arm",)

#: Sem estes a célula não é interpretável no consumo — sem identidade ela gasta leitura sem registrar.
META_EXTRA_REQUIRED = ("science_fingerprint", "recipe", "study", "lineage")

#: Lidas em algum lugar e legitimamente opcionais.
META_OPTIONAL = ("config_fingerprint", "family", "engine", "selection_stream", "inner_validation",
                 "inner_split_seed", "inner_splits", "n_categories", "n_regions", "keep_top_k",
                 "cell_id")


@dataclass(frozen=True)
class FoldPredictions:
    """One (arm, model_seed, fold, task) evaluation, as rows plus the fold's training labels."""

    state: str
    arm: str
    task: str
    split_seed: int
    partition_hash: str
    model_seed: int
    fold: int
    selected_epoch: int
    userid: np.ndarray
    window_id: np.ndarray
    y_true: np.ndarray
    y_pred: np.ndarray
    rank_of_true: np.ndarray
    train_labels: frozenset[int]
    sealed: bool = False
    #: The optional top-K block: [N, K] ids and fp16 probabilities, plus [N] true-class probability
    #: and fp32 logsumexp. All four or none.
    top_ids: np.ndarray | None = None
    top_log_probs: np.ndarray | None = None
    true_prob: np.ndarray | None = None
    logsumexp: np.ndarray | None = None

    def to_frame(self) -> pd.DataFrame:
        n = len(self.y_true)
        for name, array in (("userid", self.userid), ("window_id", self.window_id),
                            ("y_pred", self.y_pred), ("rank_of_true", self.rank_of_true)):
            if len(array) != n:
                raise ValueError(f"{name} has {len(array)} rows against y_true's {n}")
        block = {name: getattr(self, name) for name in DISTRIBUTION_COLUMNS}
        present = [name for name, value in block.items() if value is not None]
        if present and len(present) != len(DISTRIBUTION_COLUMNS):
            raise ValueError(
                f"the distribution block is partial: got {present}. Without `logsumexp` a reader "
                f"renormalises over the truncated top-K and reports probabilities the model never "
                f"produced, so the columns travel together or not at all.")

        frame = pd.DataFrame({
            "state": self.state, "arm": self.arm, "task": self.task,
            "split_seed": np.int64(self.split_seed), "partition_hash": self.partition_hash,
            "model_seed": np.int64(self.model_seed), "fold": np.int64(self.fold),
            "userid": np.asarray(self.userid, dtype=np.int64),
            "window_id": np.asarray(self.window_id, dtype=np.int64),
            "selected_epoch": np.int64(self.selected_epoch),
            "y_true": np.asarray(self.y_true, dtype=np.int64),
            "y_pred": np.asarray(self.y_pred, dtype=np.int64),
            "rank_of_true": np.asarray(self.rank_of_true, dtype=np.int64),
        })[list(COLUMNS)]
        if present:
            # Ragged-free: the [N, K] arrays go in as lists so parquet keeps one row per window.
            frame["top_ids"] = list(np.asarray(self.top_ids, dtype=np.int32))
            frame["top_log_probs"] = list(np.asarray(self.top_log_probs, dtype=np.float32))
            frame["true_prob"] = np.asarray(self.true_prob, dtype=np.float32)
            frame["logsumexp"] = np.asarray(self.logsumexp, dtype=np.float32)
        return frame


def partition_hash(folds) -> str:
    """A digest of the realised user→fold assignment.

    Of the ASSIGNMENT, not of the seed: two runs claiming `split_seed=0` are the same experiment only
    if the users landed in the same places, and a library version bump can change that while the seed
    stays put.
    """
    digest = hashlib.sha256()
    for index, fold in enumerate(folds):
        digest.update(str(index).encode())
        digest.update(np.asarray(fold.val, dtype=np.int64).tobytes())
    return digest.hexdigest()[:12]


class SealedReadRefused(RuntimeError):
    """Raised rather than overwriting a sealed outer evaluation. See `write`."""


def write(directory: Path, predictions: list[FoldPredictions], *,
          extra: dict[str, Any] | None = None, overwrite: bool = False) -> Path:
    """Write one cell's predictions plus the sidecar that makes them interpretable."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if not predictions:
        raise ValueError("refusing to write an empty prediction set")

    # VALIDATE FIRST, then publish. The order used to be reversed, so a cell that failed the
    # partition check had already written its parquet — and a crash between the two left rows with
    # no sidecar, which `collect` then swallowed, dropping the cell from every comparison in
    # silence. Measured on a synthetic bank: one lost sidecar moved a Tier-A delta by 1.48 pp
    # against a 0.4 pp margin, with both commands exiting 0.
    hashes = {p.partition_hash for p in predictions}
    if len(hashes) != 1:
        raise ValueError(f"one cell must come from ONE partition; got {sorted(hashes)}")

    path = directory / "predictions.parquet"
    sealed_already = path.exists() and (directory / "predictions_meta.json").exists()
    if sealed_already and not overwrite:
        existing = json.loads((directory / "predictions_meta.json").read_text())
        if existing.get("sealed"):
            raise SealedReadRefused(
                f"{directory} already holds a SEALED outer evaluation ({existing.get('rows')} rows, "
                f"written for {existing.get('cell_id', 'this cell')}). Writing again would be a "
                f"SECOND read of the outer test for this arm, which the protocol allows once per "
                f"freeze cycle (§5, audit criterion 7). If that is genuinely intended, pass "
                f"overwrite=True and record why.")

    frame = pd.concat([p.to_frame() for p in predictions], ignore_index=True)

    sidecar = {
        "schema_version": SCHEMA_VERSION,
        "state": predictions[0].state,
        "arm": predictions[0].arm,
        "split_seed": predictions[0].split_seed,
        "partition_hash": predictions[0].partition_hash,
        "model_seed": predictions[0].model_seed,
        "sealed": all(p.sealed for p in predictions),
        "rows": int(len(frame)),
        "has_distribution": bool(set(DISTRIBUTION_COLUMNS) <= set(frame.columns)),
        # Per TASK. Read from row 0 it described list position, not the file: a joint cell puts cat
        # first, so it advertised the 7-class head's K for reg rows carrying 20 — and an Acc@10
        # abstention curve is not even expressible at K=7.
        "top_k": {p.task: int(p.top_ids.shape[1]) for p in predictions if p.top_ids is not None},
        "users": int(frame["userid"].nunique()),
        # Per (task, fold), because OOD accounting is per fold and cannot be reconstructed later.
        "train_labels": {f"{p.task}/{p.fold}": sorted(int(v) for v in p.train_labels)
                         for p in predictions},
        "selected_epoch": {f"{p.task}/{p.fold}": int(p.selected_epoch) for p in predictions},
        **(extra or {}),
    }
    # `extra` é aplicado por ÚLTIMO, então sem esta guarda ele sobrescreve em silêncio.
    colisao = sorted(set(extra or {}) & set(META_SELF))
    if colisao:
        raise ValueError(f"extra sobrescreveria {colisao}, que write() computa das próprias "
                         f"predições — reporte o valor, não o redefina")
    faltando = [k for k in META_EXTRA_REQUIRED if not sidecar.get(k)]
    if faltando:
        raise ValueError(
            f"sidecar sem {faltando}. Uma célula sem estes campos não é interpretável no consumo: "
            f"sem `science_fingerprint` ela gasta a leitura do teste externo sem entrar no livro. "
            f"Monte o `extra` por `cli._cell_extra`, que é o caminho que a produção usa.")
    # Both files staged, then swapped: a reader can never see rows without their sidecar, which is
    # the state that made a cell silently disappear from a comparison.
    staging_frame = directory / f"predictions.{os.getpid()}.tmp.parquet"
    staging_meta = directory / f"predictions_meta.{os.getpid()}.tmp.json"
    try:
        frame.to_parquet(staging_frame, index=False)
        staging_meta.write_text(json.dumps(sidecar, indent=1))
        os.replace(staging_meta, directory / "predictions_meta.json")
        os.replace(staging_frame, path)
    finally:
        staging_frame.unlink(missing_ok=True)
        staging_meta.unlink(missing_ok=True)

    logger.info("predictions: %d rows · %d users · %s", len(frame), sidecar["users"],
                "SEALED" if sidecar["sealed"] else "NOT sealed (selection shared the fold)")
    return path


@dataclass
class Loaded:
    """A cell's predictions, read back with its sidecar."""

    frame: pd.DataFrame
    meta: dict[str, Any]
    #: Necessário para alcançar o `result.json` ao lado, de onde vem a identidade das células v1.
    directory: Path | None = None

    @property
    def sealed(self) -> bool:
        return bool(self.meta.get("sealed", False))

    def train_labels(self, task: str, fold: int) -> frozenset[int]:
        return frozenset(self.meta.get("train_labels", {}).get(f"{task}/{fold}", []))

    def science_fingerprint(self) -> str | None:
        """A identidade científica da receita que produziu esta célula, ou None.

        Em v2 vem do sidecar; `read()` já recusou a ausência. O recuo para o `result.json` ao lado
        é o ramo legado das células v1, gateado por versão porque um recuo permanente deixaria uma
        regressão do escritor invisível.

        Nunca cai para o `config_fingerprint`, que inclui telemetria: ligar a sonda de gradiente
        criaria um par novo no livro.
        """
        recorded = self.meta.get("science_fingerprint")
        if recorded:
            return str(recorded)
        if int(self.meta.get("schema_version", 1)) >= 2 or self.directory is None:
            return None
        path = Path(self.directory) / "result.json"
        if not path.exists():
            return None
        return str(json.loads(path.read_text()).get("science_fingerprint") or "") or None


def read(directory: Path) -> Loaded:
    """Read one cell, validating the schema rather than trusting it."""
    directory = Path(directory)
    frame = pd.read_parquet(directory / "predictions.parquet")

    missing = [c for c in COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"{directory}: prediction file is missing {missing}")
    block = [c for c in DISTRIBUTION_COLUMNS if c in frame.columns]
    if block and len(block) != len(DISTRIBUTION_COLUMNS):
        raise ValueError(f"{directory}: partial distribution block {block}; without logsumexp the "
                         f"stored probabilities cannot be read back as the model's")

    meta_path = directory / "predictions_meta.json"
    if not meta_path.exists():
        raise ValueError(f"{directory}: predictions without a sidecar cannot be interpreted — the "
                         f"train-label set and the seal status are not recoverable from the rows")
    meta = json.loads(meta_path.read_text())

    recorded = set(frame["partition_hash"].unique())
    if recorded != {meta["partition_hash"]}:
        raise ValueError(f"{directory}: rows carry partition {sorted(recorded)} and the sidecar "
                         f"claims {meta['partition_hash']}")
    if int(meta.get("schema_version", 1)) >= 2:
        faltando = [k for k in META_EXTRA_REQUIRED if not meta.get(k)]
        if faltando:
            raise ValueError(f"{directory}: sidecar v{meta['schema_version']} sem {faltando} — o "
                             f"escritor regrediu, e o recuo para o result.json é só de v1")
    return Loaded(frame=frame, meta=meta, directory=directory)


def collect(root: Path) -> list[Loaded]:
    """Every prediction cell under a root, in a stable order."""
    root = Path(root)
    out, skipped = [], []
    for path in sorted(root.rglob("predictions.parquet")):
        try:
            out.append(read(path.parent))
        except Exception as exc:                # ArrowInvalid subclasses ValueError; catch it too
            logger.error("UNREADABLE prediction cell %s: %s", path.parent, exc)
            skipped.append(str(path.parent))
    if skipped:
        # Loud, and returned. A swallowed cell is a missing arm in a paired comparison, and the
        # comparison still prints a delta — measured at 1.48 pp of movement against a 0.4 pp margin.
        logger.error("%d prediction cell(s) could not be read and are ABSENT from everything "
                     "computed downstream: %s", len(skipped), skipped)
    collect.skipped = skipped
    return out


def _vocabulario(cells: list[Loaded]) -> dict[str, set[int]]:
    """O tamanho de catálogo que cada braço declara, por eixo."""
    return {"n_regions": {int(c.meta["n_regions"]) for c in cells if "n_regions" in c.meta},
            "n_categories": {int(c.meta["n_categories"]) for c in cells
                             if "n_categories" in c.meta}}


def assert_comparable(cells: list[Loaded], *, confirmatory: bool = True,
                      marginal: bool = False) -> None:
    """Two arms may only be compared over an identical partition, from sealed evaluations.

    Pairing is what removes the ~1.2 pp fold component, and it only removes it if both arms saw the
    same users in the same folds. Comparing across partitions silently re-admits that variance while
    still calling the result paired.

    `confirmatory=True` (the default) also REFUSES unsealed cells. It used to warn, and a warning is
    the wrong instrument: the selection optimism here is **suggested at ~0.66 pp by ONE Alabama
    fold** (`waves/sealed_bridge.toml:9`), not measured — and even that suggestion is above the
    0.4 pp equivalence margin, so an unsealed pair can produce a confident "equivalent" that the
    seal would overturn. The proper measurement is §8a (`eval/optimism.py`), which has never run. A log line scrolls past; this does not. Exploratory reading is still available, and
    saying `confirmatory=False` is how you take responsibility for it.
    """
    # §1: "every compared arm's head covers the identical full vocabulary".
    for campo, vistos in _vocabulario(cells).items():
        if len(vistos) > 1:
            raise ValueError(
                f"os braços declaram {campo} diferentes: {sorted(vistos)}. Com catálogos diferentes "
                f"a macro-F1 tem denominadores diferentes e a Acc@10 é sobre outro conjunto — o "
                f"estimando não é o mesmo dos dois lados.")
    # PARTIÇÃO. Sob o estimando condicional a UMA partição (o desenho da v19), duas partições numa
    # família eram sintoma de sync errado. Sob o estimando MARGINAL do §1, várias partições são o
    # DESENHO — cada execução é um sorteio, e o Δ é a média sobre elas. O que continua obrigatório
    # nos dois casos é que os braços sejam pareados DENTRO de cada partição: é ali que a componente
    # de fold de ~1,2 pp cancela.
    por_particao: dict[str, set] = {}
    for c in cells:
        por_particao.setdefault(c.meta["partition_hash"], set()).add(str(c.meta.get("arm")))
    if len(por_particao) > 1 and not marginal:
        raise ValueError(f"cells span {len(por_particao)} partitions {sorted(por_particao)}; a "
                         f"paired comparison under the conditional estimand requires one. Re-run "
                         f"the arms against the same frozen split, or read under the marginal "
                         f"estimand (§1, `sd_source = \"self\"`).")
    bracos = {frozenset(v) for v in por_particao.values()}
    if len(bracos) > 1:
        detalhe = " · ".join(f"{h[:8]}: {sorted(a)}" for h, a in sorted(por_particao.items()))
        raise ValueError(f"os braços não são os mesmos em toda partição ({detalhe}). O pareamento "
                         f"acontece DENTRO da partição; sem os dois braços nela, a componente de "
                         f"fold não cancela e o Δ daquela execução mede outra coisa.")
    # LINHAGEM. Uma célula que não saiu de um manifesto de wave não tem matriz reproduzível: os
    # números existem, o código está no git, e "qual célula, qual receita, qual override" só existe
    # no shell de quem rodou. Isso aconteceu em 19-08 com uma campanha inteira, e só apareceu numa
    # auditoria. Recusar aqui — no consumo — é o que faz o atalho falhar na hora de usar em vez de
    # meses depois. `confirmatory=False` continua sendo como se assume a responsabilidade.
    adhoc = sorted({c.meta["arm"] for c in cells
                    if (c.meta.get("lineage") or {}).get("produced_by") not in (None, "wave")})
    if adhoc:
        note = (f"os braços {adhoc} não saíram de um manifesto de wave, então a matriz que os "
                f"produziu não é reproduzível a partir do repositório — só os números são. Ver "
                f"docs/RUNNING_STUDIES.md.")
        if confirmatory:
            raise ValueError(note + " Refaça-os por `mtlcheck wave run`, ou passe "
                                    "confirmatory=False para lê-los como exploratórios.")
        logger.warning("%s Lendo como EXPLORATÓRIO.", note)

    unsealed = sorted({c.meta["arm"] for c in cells if not c.sealed})
    if not unsealed:
        return
    message = (f"arms {unsealed} were evaluated on a fold that ALSO selected the checkpoint. The "
               f"optimism of that rule is suggested at ~0.66 pp by ONE Alabama fold, already "
               f"above the 0.4 pp equivalence margin, "
               f"so any interval over them is biased by more than the effect it is testing for.")
    if confirmatory:
        raise ValueError(message + " Re-run them with inner_validation=true, or pass "
                                   "confirmatory=False to read them as exploratory.")
    logger.warning("%s Reading as EXPLORATORY.", message)


__all__ = ["FoldPredictions", "Loaded", "SealedReadRefused", "COLUMNS", "DISTRIBUTION_COLUMNS",
           "SCHEMA_VERSION",
           "partition_hash", "write", "read", "collect", "assert_comparable"]
