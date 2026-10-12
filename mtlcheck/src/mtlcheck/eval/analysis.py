"""A receita de análise: os parâmetros da leitura confirmatória, congelados num arquivo.

Eles não são configuração. δ = 0,4 pp tem uma cadeia de ancoragem de três elos escrita no §3 do
protocolo e a frase "frozen in this document before the bridge"; os níveis 90/95, o número de
replicates e a composição da família manchete são igualmente pré-registrados. Enquanto viviam como
default de `argparse`, o pré-registro morava na memória de quem digitava a invocação, e um
`--margin 1.0` sairia com cara de resultado.

Como arquivo em `recipes/`, herdam a regra que as receitas de treino já têm — uma receita citada por
um resultado bancado é imutável, e uma configuração nova é um arquivo novo. A leitura passa a citar
um caminho versionado, e `git diff` responde "os parâmetros mudaram entre a ponte e os grandes?".

O `fingerprint` é do CONTEÚDO, não do caminho: renomear o arquivo não muda a análise, editá-lo muda.
"""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CORRECTIONS = ("holm", "none")
SD_AGGREGATIONS = ("max", "mean")
#: De onde sai a dispersão que decide o desenho.
#:
#: `"self"` é a escada do §2a: cada conjunto mede a própria, na validação interna. É o vigente.
#: `"bridge"` é a construção que a v19 usou — medir em três conjuntos pequenos e transferir. Foi
#: aposentada (protocolo §2a, `docs/v19_RECORD.md`) e continua carregável porque as receitas
#: `v19_headline*.toml` estão congeladas e os três conjuntos grandes ainda serão lidos por elas.
SD_SOURCES = ("self", "bridge")


@dataclass(frozen=True)
class HeadlineTest:
    """Uma comparação da família manchete: um braço contra o outro, numa tarefa."""

    task: str
    arm_a: str
    arm_b: str

    @property
    def label(self) -> str:
        return f"{self.task}:{self.arm_b}-vs-{self.arm_a}"


@dataclass(frozen=True)
class Analysis:
    name: str
    implements: str
    delta: float
    sensitivity: tuple[float, ...]
    ni_level: float
    superiority_level: float
    replicates: int
    permutations: int
    seed: int
    correction: str
    tests: tuple[HeadlineTest, ...]
    sd_source: str
    bridge_states: tuple[str, ...]
    sd_aggregation: str
    calibration_ratio: float
    folds: int
    replicates_by_state: dict[str, tuple[int, ...]]
    conjunction: str
    projected_half_width: tuple[float, float]
    unpaired_benchmark: float
    mde_power: float
    path: str
    fingerprint: str
    #: Fingerprints de receitas ANTECESSORAS cujos payloads de leitura esta receita aceita como
    #: calibração — a escada de escalada do §12.7. Vazio no caso comum.
    accepts_bridge_from: tuple[str, ...] = ()

    @property
    def levels(self) -> tuple[float, float]:
        return (self.ni_level, self.superiority_level)

    def test_for(self, task: str) -> HeadlineTest:
        for test in self.tests:
            if test.task == task:
                return test
        raise KeyError(f"{self.name} não declara teste manchete para a tarefa {task!r}")


def load(path: str | Path) -> Analysis:
    """Lê e VALIDA uma receita de análise.

    Chave desconhecida é recusada, como em `load_substrate_recipe`: um typo que cai em default é
    como uma leitura acaba sendo um experimento diferente do que o arquivo diz.
    """
    path = Path(path)
    blob = path.read_bytes()
    raw = tomllib.loads(blob.decode())

    cabecalho = _section(raw, "analysis", path)
    margin = _section(raw, "margin", path)
    intervals = _section(raw, "intervals", path)
    bootstrap = _section(raw, "bootstrap", path)
    family = _section(raw, "family", path)
    escalation = _section(raw, "escalation", path)
    conjunction = _section(raw, "conjunction", path)
    diagnostics = _section(raw, "diagnostics", path)
    # Sob a escada do §2a a seção não existe: quem decide as execuções é a dispersão medida.
    replicas = (raw.get("replicates", {}) or {}
                if (raw.get("escalation", {}) or {}).get("sd_source") == "self"
                else _section(raw, "replicates", path))
    design = _section(raw, "design", path)

    _no_unknown(raw, ("analysis", "margin", "intervals", "bootstrap", "family", "escalation",
                      "conjunction", "diagnostics", "replicates", "design"), path)
    _no_unknown(cabecalho, ("name", "implements", "accepts_bridge_from"), path,
                "analysis")
    _no_unknown(margin, ("delta", "sensitivity"), path, "margin")
    _no_unknown(intervals, ("ni", "superiority"), path, "intervals")
    _no_unknown(bootstrap, ("replicates", "permutations", "seed"), path, "bootstrap")
    _no_unknown(family, ("correction", "tests"), path, "family")
    _no_unknown(escalation, ("sd_source", "bridge_states", "sd_aggregation", "calibration_ratio"),
                path, "escalation")
    _no_unknown(diagnostics, ("projected_half_width", "unpaired_benchmark", "mde_power"), path,
                "diagnostics")
    _no_unknown(design, ("folds",), path, "design")
    _no_unknown(conjunction, ("combiner",), path, "conjunction")

    tests = tuple(HeadlineTest(task=t["task"], arm_a=t["arm_a"], arm_b=t["arm_b"])
                  for t in family["tests"])
    analysis = Analysis(
        name=str(cabecalho["name"]), implements=str(cabecalho["implements"]),
        delta=float(margin["delta"]), sensitivity=tuple(float(v) for v in margin["sensitivity"]),
        ni_level=float(intervals["ni"]), superiority_level=float(intervals["superiority"]),
        replicates=int(bootstrap["replicates"]), permutations=int(bootstrap["permutations"]),
        seed=int(bootstrap["seed"]), correction=str(family["correction"]), tests=tests,
        sd_source=str(escalation["sd_source"]),
        bridge_states=tuple(str(v) for v in escalation.get("bridge_states", ())),
        sd_aggregation=str(escalation["sd_aggregation"]),
        calibration_ratio=float(escalation["calibration_ratio"]),
        folds=int(design["folds"]), conjunction=str(conjunction["combiner"]),
        replicates_by_state={k: tuple(int(v) for v in vs) for k, vs in replicas.items()},
        projected_half_width=(float(diagnostics["projected_half_width"][0]),
                              float(diagnostics["projected_half_width"][1])),
        unpaired_benchmark=float(diagnostics["unpaired_benchmark"]),
        mde_power=float(diagnostics["mde_power"]),
        accepts_bridge_from=tuple(str(v) for v in
                                  cabecalho.get("accepts_bridge_from", ())),
        path=str(path), fingerprint=hashlib.sha256(blob).hexdigest()[:16])
    _validate(analysis, path)
    return analysis


def _section(raw: dict[str, Any], name: str, path: Path) -> dict[str, Any]:
    section = raw.get(name)
    if not isinstance(section, dict):
        raise ValueError(f"{path}: falta a seção [{name}]")
    return section


def _no_unknown(section: dict[str, Any], allowed: tuple[str, ...], path: Path,
                where: str = "") -> None:
    unknown = sorted(set(section) - set(allowed))
    if unknown:
        prefix = f"[{where}] " if where else ""
        raise ValueError(f"{path}: {prefix}tem chaves desconhecidas {unknown}; esperava {list(allowed)}")


def _validate(a: Analysis, path: Path) -> None:
    if a.delta <= 0:
        raise ValueError(f"{path}: delta={a.delta} — a margem é uma distância, tem de ser positiva")
    if not 0.5 < a.ni_level < a.superiority_level < 1.0:
        raise ValueError(
            f"{path}: níveis {a.ni_level}/{a.superiority_level} fora de 0.5 < ni < superiority < 1. "
            f"O de NI é o mais estreito de propósito: o limite inferior dele é o unilateral que a "
            f"não-inferioridade pede, e o de superioridade é o requisito adicional, mais exigente.")
    if a.delta not in a.sensitivity:
        raise ValueError(f"{path}: a margem {a.delta} não está em sensitivity={list(a.sensitivity)}; "
                         f"o apêndice do §3 tem de conter a margem que carrega o veredito")
    if not a.tests:
        raise ValueError(f"{path}: [family] sem testes — uma família tem de ser DECLARADA antes de "
                         f"rodar, senão a correção de multiplicidade não significa nada")
    tarefas = [t.task for t in a.tests]
    if len(set(tarefas)) != len(tarefas):
        raise ValueError(f"{path}: duas comparações manchete na mesma tarefa {tarefas}")
    for test in a.tests:
        if test.arm_a == test.arm_b:
            raise ValueError(f"{path}: {test.label} compara um braço com ele mesmo")
    if a.correction not in CORRECTIONS:
        raise ValueError(f"{path}: correction={a.correction!r}; esperava {list(CORRECTIONS)}")
    if a.sd_source not in SD_SOURCES:
        raise ValueError(f"{path}: sd_source={a.sd_source!r}; esperava {list(SD_SOURCES)}")
    if a.folds < 2:
        raise ValueError(f"{path}: [design] folds={a.folds}")
    if a.sd_source == "bridge" and not a.bridge_states:
        raise ValueError(f"{path}: [escalation] bridge_states vazio com sd_source='bridge' — sem a "
                         f"ponte declarada, nada distingue um estado que MEDE a banda de um que a "
                         f"CONSOME")
    if a.sd_source == "self" and a.bridge_states:
        raise ValueError(f"{path}: sd_source='self' declara bridge_states {list(a.bridge_states)}. "
                         f"Na escada do §2a cada conjunto mede a si mesmo; uma ponte declarada ao "
                         f"lado dela é uma regra morta que alguém vai ler como viva.")
    if a.sd_source == "self" and a.replicates_by_state:
        raise ValueError(
            f"{path}: sd_source='self' declara [replicates] {sorted(a.replicates_by_state)}. Na "
            f"escada do §2a quem decide quantas execuções existem é a dispersão medida, então um "
            f"conjunto declarado aqui ou conflita com o que chegou ou é um número morto que alguém "
            f"vai ler como pré-registro. O eixo é conferido por `assert_ladder`, com mais força: "
            f"ele exige que P seja um degrau e que os braços tenham as MESMAS execuções.")
    if a.sd_source != "self" and not a.replicates_by_state:
        raise ValueError(f"{path}: [replicates] vazio — sem o conjunto pré-registrado, um sync "
                         f"parcial vira um estimando diferente sem sintoma")
    for estado, sementes in a.replicates_by_state.items():
        if len(set(sementes)) != len(sementes) or not sementes:
            raise ValueError(f"{path}: [replicates] {estado} = {list(sementes)}")
    if a.calibration_ratio <= 1:
        raise ValueError(f"{path}: calibration_ratio={a.calibration_ratio} — o §2 pede a banda uma "
                         f"FRAÇÃO da escala de efeito, então a razão é maior que 1")
    if a.ni_level != 0.90 or a.superiority_level != 0.95:
        raise ValueError(f"{path}: níveis {a.ni_level}/{a.superiority_level}. O §3 registra 90/95 e "
                         f"o código endereça esses dois; outra dupla carrega sem erro e estoura no "
                         f"meio da leitura.")
    if a.sd_aggregation not in SD_AGGREGATIONS:
        raise ValueError(f"{path}: sd_aggregation={a.sd_aggregation!r}; "
                         f"esperava {list(SD_AGGREGATIONS)}")
    baixo, alto = a.projected_half_width
    if not 0 < baixo < alto:
        raise ValueError(f"{path}: projected_half_width={list(a.projected_half_width)} não é um "
                         f"intervalo positivo crescente")
    if not 0 < a.mde_power < 1:
        raise ValueError(f"{path}: mde_power={a.mde_power} não é uma potência em (0, 1)")
    if a.replicates < 10_000 or a.permutations < 10_000:
        raise ValueError(f"{path}: replicates={a.replicates} permutations={a.permutations} — o §3 "
                         f"registra ≥10 000 dos dois")


__all__ = ["Analysis", "HeadlineTest", "load", "CORRECTIONS", "SD_AGGREGATIONS", "SD_SOURCES"]
