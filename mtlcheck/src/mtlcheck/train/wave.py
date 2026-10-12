"""Run a declared matrix of cells, and record what actually happened to each.

## Why this exists, stated plainly

The reference kept its experiment matrix in 30+ shell drivers. One of them `export`ed a variable
inside a function, the export leaked into the next cell, and eight banked category cells ran in fp16
while their sidecars said fp32 — invalidating a cross-seed comparison nobody re-derived for months.

This project then reproduced the underlying cause in its own way: with no executor, every substrate
came from an ad-hoc script, which is how `repr_seed` stayed decorative through three rounds of
validation and how an entire source package stayed outside version control. Both defects share one
shape — **a thing that must be true for every run, enforced in no single place.**

So a wave is a declarative file, the executor is library code, and nothing about a cell comes from
the environment.

## What a wave guarantees

* **Resumability that is honest.** A cell is skipped only when its `result.json` parses AND its
  recorded config fingerprint matches what the manifest resolves to now. Editing a recipe therefore
  invalidates the cells it touches instead of silently keeping their stale results — the failure the
  reference's "skip if the directory exists" produced.
* **One process, one device policy.** No shell state travels between cells.
* **A failed cell does not sink the wave**, but it is recorded as failed, and the summary refuses to
  report an aggregate over a matrix with holes without naming them.
"""

from __future__ import annotations

import json
import logging
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..eval import pilot

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Cell:
    """One (recipe, state, seed) to run."""

    recipe: str
    state: str
    #: The MODEL seed (a replicate index). `split_seed` is the PARTITION — NOMENCLATURE §1.
    seed: int
    #: A partição sobre a qual esta célula treina. Igual a `seed` numa REPETIÇÃO (redesenha os folds
    #: e reinicializa); fixa em um valor ao longo das sementes numa RÉPLICA; um valor da lista quando
    #: `partitions` faz da partição um eixo. O manifesto declara qual — não há default (§10.5).
    split_seed: int = 0
    overrides: dict[str, Any] = field(default_factory=dict)
    folds: str | None = None          # e.g. "1" to profile a single fold; None runs all
    #: Distinguishes cells that share (recipe, state, seed) and differ only by an override — the
    #: shape of every schedule gate. Without it the two arms collide on one run directory and one
    #: silently overwrites the other, which the duplicate guard catches only because the guard was
    #: keyed on the triple.
    arm: str = ""
    #: ⚠ NÃO inverta este default. Em `train` o equivalente é ligado quando há `--split-seed`
    #: (2026-08-19), e a tentação é harmonizar. Aqui isso quebraria: o resume re-executa uma célula
    #: que DECLARA predições e não as tem em disco, então mudar o default invalidaria toda célula
    #: bancada cujo manifesto omite o campo — inclusive as SELADAS, gastando uma segunda leitura do
    #: teste externo. Default de manifesto é dado congelado, não preferência. Manifestos novos
    #: declaram `save_predictions = true` explicitamente.
    save_predictions: bool = False

    @property
    def label(self) -> str:
        suffix = f"/{self.arm}" if self.arm else ""
        rep = "" if self.split_seed == self.seed else f"/p{self.split_seed}"
        return f"{Path(self.recipe).stem}/{self.state}/seed{self.seed}{rep}{suffix}"


@dataclass
class Outcome:
    cell: Cell
    status: str                    # "ran" | "skipped" | "failed"
    seconds: float = 0.0
    detail: str = ""
    metric: float | None = None
    run_dir: str | None = None


def load(path: str | Path) -> tuple[str, list[Cell]]:
    """Read a wave manifest. Returns `(study, cells)`.

    The matrix is expanded here rather than in a shell loop, so the set of cells a wave contains is a
    property of a file that can be read, diffed and committed.
    """
    path = Path(path)
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    wave = raw.get("wave")
    if wave is None:
        raise ValueError(f"{path} has no [wave] section")
    study = wave.get("study")
    if not study:
        raise ValueError(f"{path}: [wave].study is required — it names the run directory")
    # Uma chave sem leitor é "uma linha que alguém vai ler como verdade" -- o critério que este repo
    # aplica a manifesto em toda parte, e não aplicava aqui: `confirmatory = true` estava nos seis
    # manifestos da campanha e nenhum código o lia. O lacre real vem de `inner_validation` mais
    # `save_predictions`, então a linha prometia uma garantia que ela mesma não dava.
    # `confirmatory` NÃO é lida aqui e não é morta: quem a lê é `test_campaign_manifests.py`, que
    # varre por ela para exigir `save_predictions` em toda célula confirmatória. Uma auditoria a
    # chamou de linha sem leitor por ter procurado só em `src/`, e tirá-la dos manifestos derrubou
    # seis casos da suíte sem um erro sequer.
    sem_leitor = sorted(set(wave) - {"study", "analysis", "confirmatory"})
    if sem_leitor:
        raise ValueError(
            f"{path}: [wave] tem chaves que código nenhum lê: {sem_leitor}. Uma linha que não "
            f"governa nada é uma linha que alguém vai ler como verdade.")

    tipos = {entry.get("partitions") == PILOT for entry in raw.get("cell", [])}
    if len(tipos) > 1:
        raise ValueError(
            f"{path}: mistura células com `partitions = \"{PILOT}\"` e sem. A partir do segundo "
            f"degrau a escada reescreve o manifesto e as não-pilot são DESCARTADAS em silêncio — o "
            f"piso rodaria com elas e o resto sem. Separe em dois manifestos.")

    cells: list[Cell] = []
    for i, entry in enumerate(raw.get("cell", [])):
        seeds = entry.get("repetitions", entry.get("seeds"))
        missing = [k for k in ("recipe", "states") if k not in entry] + ([] if seeds else ["seeds"])
        if missing:
            raise ValueError(f"{path}: [[cell]] #{i + 1} is missing {missing}")
        overrides = dict(entry.get("set", {}))
        folds = entry.get("folds")
        arm = str(entry.get("arm", ""))
        save_predictions = bool(entry.get("save_predictions", False))
        if entry.get("partitions") == PILOT:
            # A escada do §2a define os PARES `(split_seed, model_seed)` — os dois botões andam
            # juntos. `seeds` não entra: cruzar semente com partição repetiria uma semente entre
            # partições, cravando o desvio daquele sorteio na média e escondendo-o da dispersão.
            declarados = entry.get("seeds") or seeds or []
            if declarados and list(declarados) != [pilot.sementes(1)[0][1]]:
                raise ValueError(
                    f'{path}: [[cell]] #{i + 1} usa `partitions = "{PILOT}"` e declara '
                    f'seeds = {list(declarados)}, que a escada IGNORA — ela sorteia os dois botões '
                    f'juntos. Um manifesto é dado congelado; declarar semente que não roda é uma '
                    f'linha que alguém vai ler como verdade. Omita `seeds` ou deixe '
                    f'`[{pilot.sementes(1)[0][1]}]`.')
            for state in entry["states"]:
                for p_, s_ in pilot.sementes(pilot.ESCADA[0]):
                    cells.append(Cell(entry["recipe"], state, s_, p_, overrides, folds, arm,
                                      save_predictions))
            continue

        pinned = _particao(entry, i, path)
        for state in entry["states"]:
            for particao in (pinned if pinned is not None else [None]):
                for seed in entry["seeds"] if "seeds" in entry else seeds:
                    cells.append(Cell(entry["recipe"], state, int(seed),
                                      int(particao) if particao is not None else int(seed),
                                      overrides, folds, arm, save_predictions))

    if not cells:
        raise ValueError(f"{path}: declares no cells")
    _refuse_duplicates(cells, path)
    return study, cells


PER_SEED = "per-seed"

#: `partitions = "pilot"` — a escada de escalada do §2a decide quantas execuções este conjunto
#: recebe, medindo a própria dispersão. Ver `eval/pilot.py`.
PILOT = "pilot"


def _particao(entry: dict, i: int, path) -> list[int] | None:
    """As partições que a célula declara — três formas, exatamente uma presente.

    `split_seed = 0` fixa uma partição (RÉPLICAS); `split_seed = "per-seed"` redesenha a cada
    semente (REPETIÇÕES); `partitions = "pilot"` deixa a escada do §2a decidir; `partitions = [0, 7]` faz da partição um EIXO fixo, em produto cartesiano com
    `seeds`. Omitir é recusado, e declarar `split_seed` E `partitions` também. O §10.5 separa os
    desenhos porque o desvio entre execuções mede coisas diferentes em cada um — com partição fixa
    mede inicialização, com partição por semente mede inicialização E sorteio, confundidas em 1 grau
    de liberdade. Quatro manifestos deste repo rodaram o segundo enquanto a prosa dizia o primeiro,
    e o default silencioso é o que permitiu.
    """
    for campo in ("split_seed", "partitions"):
        if campo in entry.get("set", {}):
            raise ValueError(f"{path}: [[cell]] #{i + 1} põe {campo} em [cell.set]; ele é campo da "
                             f"célula, não override de receita")
    if "split_seed" in entry and "partitions" in entry:
        raise ValueError(f"{path}: [[cell]] #{i + 1} declara split_seed E partitions — o mesmo eixo "
                         f"dito duas vezes, e as duas declarações podem discordar. Diga um só.")
    if "partitions" in entry:
        valores = entry["partitions"]
        if (not isinstance(valores, list) or not valores
                or any(isinstance(v, bool) or not isinstance(v, int) for v in valores)):
            raise ValueError(f"{path}: [[cell]] #{i + 1} tem partitions = {valores!r}; use uma "
                             f"lista não-vazia de inteiros")
        if len(set(valores)) != len(valores):
            raise ValueError(f"{path}: [[cell]] #{i + 1} repete partições em partitions = "
                             f"{valores!r}; a mesma coluna duas vezes colidiria num diretório só")
        return [int(v) for v in valores]
    if "split_seed" not in entry:
        raise ValueError(
            f"{path}: [[cell]] #{i + 1} não declara split_seed nem partitions. O §10.5 separa "
            f"RÉPLICA (partição fixa: `split_seed = 0`) de REPETIÇÃO (cada semente redesenha: "
            f'`split_seed = "{PER_SEED}"`); a escada do §2a é `partitions = "pilot"`, e um eixo '
            f'fixo é `partitions = [0, 7]`. Diga qual.')
    valor = entry["split_seed"]
    if valor == PER_SEED:
        return None
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"{path}: [[cell]] #{i + 1} tem split_seed = {valor!r}; use um inteiro ou "
                         f'"{PER_SEED}"')
    return [valor]


def is_pilot(manifest: str | Path) -> bool:
    """O manifesto declara a escada do §2a em alguma célula?"""
    with Path(manifest).open("rb") as handle:
        raw = tomllib.load(handle)
    return any(e.get("partitions") == PILOT for e in raw.get("cell", []))


def run_ladder(manifest: str | Path, *, execute, identify, dispersao, margem: float,
               device: str | None = None, resume: bool = True,
               escada: tuple[int, ...] | None = None, ruido=None) -> list[Outcome]:
    """Roda a escada do §2a: o piso, depois só o que a dispersão medida pedir.

    Fica FORA de `run` de propósito. Um manifesto sem `partitions = "pilot"` segue pelo caminho de
    sempre, byte por byte — nenhuma wave existente muda de comportamento por esta função existir.

    `dispersao(outcomes) -> {(state, task): [delta por execução]}` é injetado pelo mesmo motivo que
    `execute` e `identify`: este módulo não computa métrica nem importa torch. Os deltas vêm da
    VALIDAÇÃO INTERNA — a escada não pode olhar o teste externo, que é o recurso racionado.

    Cada degrau reaproveita as execuções do anterior; nada é descartado. O `resume` do `run` cuida
    disso sozinho, porque as células do piso já estão em disco quando o degrau seguinte roda.
    """
    from ..eval import pilot as pilot_mod

    escada = escada or pilot_mod.ESCADA
    study, _ = load(manifest)
    feitos: list[Outcome] = []
    for i, alvo in enumerate(escada):
        alvo_manifest = manifest if i == 0 else _com_execucoes(manifest, alvo)
        logger.info("escada §2a: degrau %d/%d, P=%d execuções", i + 1, len(escada), alvo)
        feitos = run(alvo_manifest, execute=execute, identify=identify, device=device,
                     resume=resume)
        if any(o.status == "failed" for o in feitos):
            logger.error("escada §2a: degrau P=%d tem célula falha — parando antes de escalar sobre "
                         "dado incompleto", alvo)
            return feitos

        por_tarefa = dispersao(feitos)
        # Fail-closed nos dois. Antes, `por_tarefa` vazio avisava e parava, e `degraus` vazio caía
        # em `all([]) is True` e parava também -- as duas coisas produzindo uma campanha que rodou
        # só o piso, com 1 grau de liberdade, sem nada falhar. O sintoma só apareceria no
        # `assert_ladder` da leitura, depois da GPU gasta.
        if not por_tarefa:
            raise SystemExit(
                f"escada §2a: P={alvo} terminou e nenhum delta pôde ser montado. A escada precisa de "
                f"joint E dedicado na mesma execução para calcular `joint - dedicado`; confira se os "
                f"três braços rodaram e se cada `result.json` tem o bloco `selection`. Parar aqui "
                f"seria bancar uma campanha de um grau de liberdade sem ninguém perceber.")

        # Contra o ALVO, não contra 2. Uma tarefa com menos deltas decide o degrau sobre outra
        # amostra sem sintoma: o filtro `len(v) >= 2` a deixava sair da decisão em silêncio, e a
        # escada podia parar pelo cat com a dispersão de reg nunca medida.
        errados = {f"{k[0]}/{k[1]}": len(v) for k, v in sorted(por_tarefa.items())
                   if len(v) != alvo}
        if errados:
            raise SystemExit(
                f"escada §2a: P={alvo} terminou e estas tarefas não têm {alvo} deltas: {errados}. "
                f"Alguma execução perdeu um braço, ou um `result.json` saiu sem o bloco `selection`. "
                f"Decidir o degrau sobre dado parcial mede outra amostra, e não deixa sintoma.")
        if i == 0:
            tarefas_piso = set(por_tarefa)
        elif set(por_tarefa) != tarefas_piso:
            raise SystemExit(
                f"escada §2a: as tarefas mudaram entre degraus ({sorted(tarefas_piso)} → "
                f"{sorted(por_tarefa)}). Uma que some deixa de ser medida sem nada falhar.")

        degraus = {k: pilot_mod.avalia(v, margem=margem, escada=escada)
                   for k, v in por_tarefa.items()}
        piso = ruido(feitos) if ruido else {}
        for (state, task), d in sorted(degraus.items()):
            logger.info("  %s/%s: %s", state, task, d.describe())
            _denuncia_piso_de_ruido(state, task, piso.get((state, task)), margem, escada,
                                    pilot_mod)
        if all(d.para or d.limitado for d in degraus.values()):
            _carimba(study, degraus, feitos, margem)
            return feitos
    _carimba(study, degraus, feitos, margem)
    return feitos


def _denuncia_piso_de_ruido(state, task, piso, margem, escada, pilot_mod) -> None:
    """Se o ruído do próprio medidor já excede o limiar de um degrau, aquele degrau é inalcançável.

    Não muda a regra -- a condição de parada segue sendo a pré-registrada, sobre o σ̂ observado. O que
    isto faz é dizer, no PRIMEIRO degrau, o que em 25-08 só se soube depois de duas horas de GPU: com
    um piso de ruído de 0,184 pp e um limiar de 0,076 no degrau P=3, o Alabama ia ao teto por
    aritmética, qualquer que fosse a dispersão verdadeira.
    """
    if piso is None:
        return
    inalcancaveis = [p for p in escada if piso > pilot_mod.sd_maximo(p, margem=margem)]
    recado = (f"    ruído do estimador ~{piso:.4f} (dispersão entre folds DENTRO de cada execução, "
              f"sobre √n)")
    if not inalcancaveis:
        logger.info("%s", recado)
        return
    logger.warning(
        "%s — ele sozinho já excede o limiar dos degraus %s, que são INALCANÇÁVEIS para "
        "%s/%s qualquer que seja a dispersão verdadeira. A escada vai comprar execuções contra o "
        "ruído do próprio medidor. Ver EVALUATION_PROTOCOL §2a.",
        recado, inalcancaveis, state, task)


def _carimba(study: str, degraus: dict, feitos: list, margem: float) -> None:
    """Grava o veredito da escada onde a LEITURA possa conferi-lo.

    Sem isto, uma escada interrompida em fronteira de degrau é indistinguível de uma resolvida: uma
    wave morta (OOM, preempção, reboot) logo depois da 3ª execução de uma subida que ia a P=4 deixa
    um disco idêntico ao de uma parada legítima em P=3, e `assert_ladder` — que confere a FORMA do
    conjunto — aceita. O mesmo vale para um sync parcial truncado numa fronteira, e para uma wave
    rodada com outro δ.

    O arquivo carrega o δ que governou a compra, para que a leitura recuse quando ele divergir do
    da receita. E carrega o desfecho, sem o qual o carimbo "partition-limited" do §2a vivia só numa
    linha de log.

    ⚠ Os DELTAS não entram, e a omissão é a escolha. A dispensa de α-spending do §2a repousa em a
    regra de escalada depender só da variância e nunca do efeito observado (Kieser & Friede 2000;
    FDA 2019) -- e a `sd` sozinha já torna a condição de parada recomputável na leitura. Gravar os
    deltas acrescentaria zero à verificação e exporia o sinal e a magnitude de `joint − dedicado`
    antes da leitura confirmatória, a quem quer que abrisse o arquivo.
    """
    from .. import paths

    # UM ARQUIVO POR CONJUNTO. Os seis manifestos da campanha compartilham `study = "v19_ladder"`,
    # então um `ladder.json` único seria sobrescrito pelo estado seguinte.
    raiz = paths.run_dir(study, "")
    for state in sorted({s for s, _ in degraus}):
        pares = sorted({(o.cell.split_seed, o.cell.seed) for o in feitos
                        if o.cell.state == state})
        payload = {
            "estado": state,
            "margem": margem,
            "execucoes": [list(par) for par in pares],
            "veredito": {task: {
                "execucoes": d.execucoes, "sd": d.sd, "sd_ucl": d.sd_ucl,
                "meia_largura": d.meia_largura,
                "desfecho": "para" if d.para else "teto" if d.limitado else "incompleto",
            } for (s_, task), d in sorted(degraus.items()) if s_ == state},
        }
        destino = raiz / f"ladder_{state}.json"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        logger.info("escada §2a: veredito de %s gravado em %s", state, destino)


def _inline(valor) -> str:
    """Uma tabela inline TOML a partir de um dict Python.

    `json.dumps` emite `{"lr": 0.001}` com `:`, e TOML exige `=`. A versão anterior tentava
    consertar com uma cadeia de `replace` que era no-op (`'"'→"'"` seguido de `"'"→'"'`) e ainda
    corrompia apóstrofos dentro de string. O degrau seguinte morria com `TOMLDecodeError` DEPOIS de
    o piso ter gastado GPU.
    """
    return "{ " + ", ".join(f"{k} = {_valor_toml(v)}" for k, v in valor.items()) + " }"


def _valor_toml(v) -> str:
    """Um valor TOML a partir de um valor Python — escalar, lista ou tabela inline."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_valor_toml(x) for x in v) + "]"
    if isinstance(v, dict):
        return _inline(v)
    return json.dumps(str(v))


def _com_execucoes(manifest: str | Path, alvo: int):
    """Um manifesto temporário com a escada expandida para `alvo` execuções.

    O arquivo original não é tocado: um manifesto é dado congelado, e reescrevê-lo em disco durante
    a execução faria o `git diff` mentir sobre o que foi lançado.
    """
    import tempfile

    from ..eval import pilot as pilot_mod

    with Path(manifest).open("rb") as handle:
        raw = tomllib.load(handle)
    pares = pilot_mod.sementes(alvo)
    # TODAS as chaves de [wave], não só `study`. Perder `analysis` faria o manifesto do degrau
    # afirmar outra proveniência que a do lançado -- e é dele que a próxima pessoa reconstrói o δ.
    cabeca = "\n".join(f"{k} = {_valor_toml(v)}" for k, v in raw["wave"].items())
    linhas = [f"[wave]\n{cabeca}\n"]
    identidade = (raw.get("substrate", {}) or {}).get("identity", {})
    planos = {k: v for k, v in identidade.items() if not isinstance(v, dict)}
    if planos:
        linhas.append("[substrate.identity]\n"
                      + "\n".join(f'{k} = "{v}"' for k, v in planos.items()) + "\n")
    for chave, bloco in identidade.items():
        if isinstance(bloco, dict):
            linhas.append(f"[substrate.identity.{chave}]\n"
                          + "\n".join(f'{k} = "{v}"' for k, v in bloco.items()) + "\n")
    for e in raw.get("cell", []):
        if e.get("partitions") != PILOT:
            continue
        for p_, s_ in pares:
            corpo = [f'recipe = "{e["recipe"]}"',
                     f'states = {json.dumps(e["states"])}',
                     f"seeds = [{s_}]", f"split_seed = {p_}",
                     f'save_predictions = {str(bool(e.get("save_predictions", False))).lower()}']
            if e.get("folds") is not None:
                corpo.append(f'folds = "{e["folds"]}"')
            if e.get("arm"):
                corpo.append(f'arm = "{e["arm"]}"')
            if e.get("set"):
                corpo.append("set = " + _inline(e["set"]))
            linhas.append("[[cell]]\n" + "\n".join(corpo) + "\n")
    alvo_path = Path(tempfile.mkdtemp()) / Path(manifest).name
    alvo_path.write_text("\n".join(linhas))
    return alvo_path


def declared_analysis(path: str | Path) -> str | None:
    """A receita de análise que o manifesto declara, de onde a escada tira o δ.

    Sem isto o δ vem do default de argparse de `--margin` — exatamente a forma que o docstring de
    `eval/analysis.py` condena ("enquanto viviam como default de argparse, o pré-registro morava na
    memória de quem digitava"). Uma wave rodada com `--margin 1.0` para no primeiro degrau sempre, e
    a leitura com δ=0,4 aceita: `assert_ladder` confere a FORMA do conjunto, não a condição de
    parada. Declarando aqui, as duas pontas leem o mesmo arquivo congelado.
    """
    with Path(path).open("rb") as fh:
        raw = tomllib.load(fh)
    valor = (raw.get("wave", {}) or {}).get("analysis")
    return str(valor) if valor else None


def declared_substrate(path: str | Path) -> dict[str, str]:
    """A identidade de substrato que o manifesto DECLARA que suas células leram, por nível.

    Uma wave é uma matriz de células de TREINO: ela não constrói substrato e não vai construir aqui
    (ver `docs/RUNNING_STUDIES.md` §4). O que este bloco faz é menor e suficiente — deixa o manifesto
    **dizer** sobre qual substrato o experimento é, para que rodá-lo sobre outro seja uma recusa em
    vez de um número silenciosamente diferente:

        [substrate]
        recipe = "recipes/v19/substrate.toml"     # informativo: como reconstruí-lo
        [substrate.identity]
        checkin = "696ac00419d287d3"

    Omitir o bloco mantém o comportamento antigo. Declarar `identity` e rodar sobre outro substrato
    aborta a wave inteira, e não célula a célula: se o disco tem o substrato errado, TODA célula da
    matriz está errada, e parar na primeira é a única leitura útil.
    """
    with Path(path).open("rb") as fh:
        raw = tomllib.load(fh)
    section = (raw.get("substrate", {}) or {}).get("identity", {}) or {}
    # Duas formas. PLANA — `{checkin = "..."}` — vale para toda célula, e é o que uma wave de um
    # estado quer. POR ESTADO — `{alabama = {checkin = "..."}}` — é o que uma campanha multi-estado
    # PRECISA, porque cada estado tem o seu substrato e uma identidade só não os cobre.
    if section and all(isinstance(v, dict) for v in section.values()):
        return {state: dict(levels) for state, levels in section.items()}
    return {"*": dict(section)} if section else {}


def _refuse_duplicates(cells: list[Cell], path: Path) -> None:
    """Two entries producing the same cell would race on one directory and one would win silently."""
    seen: dict[tuple[str, str, int, int, str], int] = {}
    for cell in cells:
        key = (cell.recipe, cell.state, cell.seed, cell.split_seed, cell.arm)
        seen[key] = seen.get(key, 0) + 1
    duplicated = [k for k, n in seen.items() if n > 1]
    if duplicated:
        raise ValueError(f"{path}: these cells are declared more than once: {duplicated}")


def run(manifest: str | Path, *, execute, identify, device: str | None = None,
        resume: bool = True, dry_run: bool = False) -> list[Outcome]:
    """Execute a wave. `execute(cell, device)` runs one cell and returns its run directory.

    The executor is injected so this module never imports torch — a wave can be listed, validated and
    diffed on a laptop with no GPU, which is where most manifest mistakes are made.

    `identify(cell) -> (cell_id, fingerprint, substrate)` resolves a cell's identity WITHOUT running
    it, and is injected for the same reason. Resume needs all three: the directory to look in, the
    fingerprint to compare against — the previous version derived the directory from the recipe
    FILENAME (which is not the family) and read a key that does not exist in the schema, so it
    compared nothing — and the substrate identity, without which a rebuilt substrate was invisible.
    """
    from .. import paths

    study, cells = load(manifest)
    declared = declared_substrate(manifest)
    logger.info("wave %s: %d cells", study, len(cells))
    # ⚠ CONFERE CADA ESTADO, não só a primeira célula. A primeira versão checava `cells[0]`, o que
    # basta numa wave de um estado e é silenciosamente inútil numa campanha multi-estado: cinco dos
    # seis substratos passariam sem conferência nenhuma.
    if declared and cells:
        for state in sorted({c.state for c in cells}):
            expectation = declared.get(state) or declared.get("*")
            if not expectation:
                logger.warning("%s não declara substrato para %s — essa célula roda sem conferência",
                               manifest, state)
                continue
            probe = next(c for c in cells if c.state == state)
            _, _, on_disk = identify(probe)
            for level, expected in expectation.items():
                actual = (on_disk.get(level) or {}).get("identity")
                if actual and actual != expected:
                    raise SystemExit(
                        f"{manifest} declara, para {state}, o substrato {level}={expected}, e o "
                        f"disco tem {actual}. Rodar assim produziria números de outro substrato sob "
                        f"o nome deste estudo. Reconstrua, aponte ARTIFACTS_ROOT para o certo, ou — "
                        f"se a intenção é um experimento NOVO — dê a ele o seu próprio manifesto.")
                if not actual:
                    # Fail-closed: declarar identidade e não poder conferir é PIOR que não declarar,
                    # porque o manifesto afirma uma garantia que ninguém verificou. Em 25-08 o
                    # `ARTIFACTS_ROOT` óbvio do A40 era um andaime de symlinks para outro engine, sem
                    # manifest.json -- a wave teria rodado sobre o substrato errado sob o nome deste
                    # estudo, avisando num log e falhando em nada.
                    raise SystemExit(
                        f"{manifest} declara, para {state}, o substrato {level}={expected}, e o do "
                        f"disco não tem manifest.json — a identidade não pode ser conferida. Rodar "
                        f"assim aceita QUALQUER substrato sob o nome deste estudo. Aponte "
                        f"ARTIFACTS_ROOT para o que foi construído por este código, ou reconstrua. "
                        f"Se a intenção é mesmo rodar sem conferência, tire o bloco "
                        f"[substrate.identity] do manifesto — assim a falta de garantia fica "
                        f"escrita onde alguém lê.")

    if dry_run:
        for cell in cells:
            logger.info("  would run %s", cell.label)
        return [Outcome(cell, "skipped", detail="dry run") for cell in cells]

    outcomes: list[Outcome] = []
    started = time.perf_counter()
    for index, cell in enumerate(cells, start=1):
        prefix = f"[{index}/{len(cells)}] {cell.label}"
        if resume and (done := _already_done(study, cell, identify)):
            logger.info("%s · skipped (%s)", prefix, done)
            # COM `run_dir`. Sem ele a escada do §2a enxergava, no degrau 2, só as células que
            # tinham acabado de rodar -- o piso inteiro, que o resume acabara de pular, sumia da
            # dispersão. Ela media P=1 achando que media P=3, e antes do fail-closed de 25-08
            # parava ali em silêncio: a escada NUNCA passaria de P=3, qualquer que fosse a
            # dispersão, e nada a jusante notaria (em disco há 3 execuções e o gate da leitura
            # aceita 3). Achado pela escada em miniatura.
            outcomes.append(Outcome(cell, "skipped", detail=done,
                                    run_dir=str(paths.run_dir(study, identify(cell)[0]))))
            continue

        cell_started = time.perf_counter()
        try:
            run_dir, metric = execute(cell, device)
        except Exception as exc:                              # one bad cell must not sink the wave
            elapsed = time.perf_counter() - cell_started
            logger.exception("%s · FAILED after %.0fs", prefix, elapsed)
            outcomes.append(Outcome(cell, "failed", elapsed, f"{type(exc).__name__}: {exc}"))
            continue

        elapsed = time.perf_counter() - cell_started
        logger.info("%s · %.0fs%s", prefix, elapsed,
                    f" · {metric * 100:.4f}" if metric is not None else "")
        outcomes.append(Outcome(cell, "ran", elapsed, metric=metric, run_dir=str(run_dir)))

    _report(study, outcomes, time.perf_counter() - started)
    return outcomes


def _already_done(study: str, cell: Cell, identify) -> str | None:
    """A cell counts as done only if its result parses AND matches AND is complete.

    Three checks, each for a failure this project has actually seen:

    * "the directory exists" is not enough — a crashed cell leaves one behind, and the reference's
      resume skipped exactly those.
    * The **fingerprint must match**. The docstring above has promised this since the module was
      written and the code did not do it: it read `payload["fingerprint"]`, a key the schema spells
      `config_fingerprint`, and then compared it to nothing. So editing a recipe kept every stale
      cell it touched — the precise behaviour the wave exists to prevent.
    * A `save_predictions` cell must actually have its rows. `result.json` is written before
      `predictions.parquet`, so a crash in between leaves a cell that resumes forever with no rows,
      and Tier A silently loses that arm — unrecoverable without retraining.
    """
    from .. import paths

    cell_id, fingerprint, current_substrate = identify(cell)
    directory = paths.run_dir(study, cell_id)
    result = directory / "result.json"
    if not result.exists():
        return None
    try:
        payload = json.loads(result.read_text())
    except json.JSONDecodeError:
        logger.warning("%s has an unreadable result.json; re-running", cell.label)
        return None

    # The SCIENCE fingerprint: turning telemetry on must not invalidate a banked cell, because
    # invalidating a banked cell is what triggers a second read of the sealed outer test. A cell
    # banked before the field existed is re-hashed from the config IT recorded — never compared
    # against the old full fingerprint, which would differ by construction.
    banked = str(payload.get("science_fingerprint") or "")
    if not banked and payload.get("config"):
        from ..config import science_digest
        banked = science_digest(payload["config"])
    if banked != fingerprint:
        logger.warning("%s was banked at fingerprint %s and the manifest now resolves to %s; "
                       "re-running", cell.label, banked[:12] or "?", fingerprint[:12])
        return None
    # O SUBSTRATO tem de ser o mesmo. Uma célula que passou daqui em 2026-08-19 podia ter sido
    # treinada sobre outro substrato inteiramente — ele é escolhido por `ARTIFACTS_ROOT`, uma
    # variável de ambiente, e nada na célula o registrava. Reconstruir o substrato e reexecutar a
    # wave pulava tudo e reportava os números antigos como atuais.
    #
    # A migração é assimétrica de propósito. AUSENTE avisa e NÃO invalida: toda célula bancada antes
    # do campo existir cairia aqui, incluindo as SELADAS, e invalidá-las gastaria uma segunda
    # leitura do teste externo. PRESENTE E DIFERENTE invalida, que é o comportamento que faltava.
    banked_substrate = payload.get("substrate") or {}
    if not banked_substrate:
        logger.warning("%s foi bancada antes de a identidade do substrato ser registrada — o resume "
                       "NÃO consegue saber se ela leu o substrato atual. Retreine-a para fechar a "
                       "lacuna, ou trate o número como sendo do substrato daquela data.", cell.label)
    elif current_substrate:
        for level, current in current_substrate.items():
            was = (banked_substrate.get(level) or {}).get("identity")
            now = (current or {}).get("identity")
            if was and now and was != now:
                logger.warning("%s foi bancada sobre o substrato %s=%s e o disco agora tem %s; "
                               "re-executando", cell.label, level, was[:12], now[:12])
                return None

    if cell.save_predictions and not (directory / "predictions.parquet").exists():
        logger.warning("%s has a result but no predictions.parquet; re-running so the confirmatory "
                       "bank is not left with a hole", cell.label)
        return None
    return f"fingerprint {fingerprint[:12]}"


def _report(study: str, outcomes: list[Outcome], wall: float) -> None:
    ran = [o for o in outcomes if o.status == "ran"]
    failed = [o for o in outcomes if o.status == "failed"]
    skipped = [o for o in outcomes if o.status == "skipped"]

    logger.info("wave %s: %d ran, %d skipped, %d failed · %.0fs total",
                study, len(ran), len(skipped), len(failed), wall)
    if ran:
        slowest = max(ran, key=lambda o: o.seconds)
        logger.info("  wall: %.0fs mean, slowest %s at %.0fs",
                    sum(o.seconds for o in ran) / len(ran), slowest.cell.label, slowest.seconds)
    for outcome in failed:
        logger.error("  FAILED %s: %s", outcome.cell.label, outcome.detail)
    if failed:
        logger.error("  the matrix has holes — any aggregate over it is over a SUBSET, and the "
                     "cells above are the ones missing")


__all__ = ["Cell", "Outcome", "load", "run"]
