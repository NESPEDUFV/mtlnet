"""Stage 2 end to end — o único comando que lê o teste externo.

A unidade do modo confirmatório é o ESTADO, não a célula: Holm é dentro da família de um estado e a
reivindicação co-primária junta as duas tarefas. Os flags soltos sobrevivem para exploração de uma
célula, que é o uso em que a margem é uma pergunta e não um pré-registro.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pytest

from conftest import extra_valido
from mtlcheck import cli
from mtlcheck.eval import ledger, predictions as P

USERS, WINDOWS = 80, 4

#: Família de uma tarefa só — os fixtures deste arquivo bancam `reg`, e uma família que declarasse
#: `cat` sem células correspondentes falharia por ausência de dado, não pelo que o teste mede.
REG_ONLY = """
[analysis]
name = "teste"
implements = "docs/plans/EVALUATION_PROTOCOL.md"
[margin]
delta = 0.4
sensitivity = [0.2, 0.4, 1.0]
[intervals]
ni = 0.90
superiority = 0.95
[bootstrap]
replicates = 10000
permutations = 10000
seed = 0
[family]
correction = "holm"
tests = [{ task = "reg", arm_a = "cat", arm_b = "joint" }]
[escalation]
sd_source = "bridge"
bridge_states = ["alabama"]
sd_aggregation = "max"
calibration_ratio = 3.0
[conjunction]
combiner = "bonferroni"
[design]
folds = 2
[replicates]
alabama = [0, 1]
[diagnostics]
projected_half_width = [0.05, 0.30]
unpaired_benchmark = 0.5
mde_power = 0.80
"""


@pytest.fixture(autouse=True)
def _ledger_fora_do_repo(livro_fora_do_repo):
    """Autouse: a próxima pessoa a escrever um caso confirmatório aqui não vai lembrar do desvio."""


@pytest.fixture
def receita(tmp_path_factory):
    caminho = tmp_path_factory.mktemp("analise") / "reg_only.toml"
    caminho.write_text(REG_ONLY)
    return str(caminho)


def _cell(directory, arm: str, seeds, *, hits: int, sealed: bool = True, task: str = "reg",
          fingerprint: str | None = "5c1e" * 4):
    """One arm's prediction cell: `hits` of every user's six windows rank inside the top ten.

    `fingerprint` reproduz o que as células reais carregam. O fixture original omitia o campo, e por
    isso o bloco do livro de leituras nunca era exercido: ele filtra por identidade científica, o
    filtro vinha vazio, e um `NameError` a duas linhas de distância passou verde por dias.
    """
    # UMA célula por semente, como a produção: o `cell_id` real é `cat-alabama-p0s0`, e o sidecar
    # grava um `model_seed` só. Empilhar sementes num diretório era um formato que não existe.
    for seed in seeds:
        alvo = Path(f"{directory}-s{seed}")
        banked = []
        for fold in range(2):
            users = np.repeat(np.arange(USERS // 2 * fold, USERS // 2 * (fold + 1)), WINDOWS)
            rank = np.tile([1] * hits + [50] * (WINDOWS - hits), USERS // 2)
            banked.append(P.FoldPredictions(
                state="alabama", arm=arm, task=task, split_seed=0, partition_hash="abcabcabcabc",
                model_seed=seed, fold=fold, selected_epoch=11,
                userid=users, window_id=np.arange(len(users)),
                y_true=np.zeros(len(users), dtype=np.int64),
                y_pred=np.zeros(len(users), dtype=np.int64),
                rank_of_true=rank, train_labels=frozenset({0}), sealed=sealed))
        extra = extra_valido(arm=arm)
        if fingerprint is not None:
            extra["science_fingerprint"] = f"{arm[:3]}{fingerprint}"[:16]
        P.write(alvo, banked, extra=extra)
        if fingerprint is None:
            _rebaixa_para_v1(alvo)
    return Path(f"{directory}-s{seeds[0]}")


def _rebaixa_para_v1(directory) -> None:
    """Reescreve o sidecar no formato LEGADO — sem identidade, `schema_version` 1.

    Rebaixar depois de escrever, e não montar um `extra` v1, porque `write()` recusa os dois. Escrever
    uma célula legada hoje é impossível pelo caminho normal, que é o ponto do contrato — mas as 54
    células da campanha `v19_defence` existem nesse formato.
    """
    caminho = Path(directory) / "predictions_meta.json"
    meta = json.loads(caminho.read_text())
    meta["schema_version"] = 1
    meta.pop("science_fingerprint", None)
    meta.pop("recipe", None)
    caminho.write_text(json.dumps(meta, indent=1))


def _familia(root, receita, **over):
    base = dict(run_root=str(root), analysis=receita, arm_a=None, arm_b=None, task=None,
                state="alabama", margin=0.4, level=0.95, replicates=10000, permutations=10000,
                bridge_reading=[], exploratory=False, json=False)
    base.update(over)
    return argparse.Namespace(**base)


def _solto(root, **over):
    base = dict(run_root=str(root), analysis=None, arm_a="cat", arm_b="joint", task="reg",
                state="alabama", margin=0.4, level=0.95, replicates=10000, permutations=10000,
                bridge_reading=[], exploratory=True, json=False)
    base.update(over)
    return argparse.Namespace(**base)


def _dois_bracos(tmp_path, **over):
    _cell(tmp_path / "cat", "cat", (0, 1), hits=2, **over)
    _cell(tmp_path / "joint", "joint", (0, 1), hits=3, **over)


# ── o modo, antes de tudo ───────────────────────────────────────────────────────────────────────


def test_leitura_confirmatoria_sem_receita_e_recusada(tmp_path) -> None:
    """δ e os níveis são pré-registro. Como flag, viram escolha de quem digita a invocação."""
    _dois_bracos(tmp_path)
    with pytest.raises(SystemExit, match="exige --analysis"):
        cli._run_compare(_solto(tmp_path, exploratory=False))
    assert ledger.load() == []


def test_receita_e_flags_soltos_juntos_sao_recusados(tmp_path, receita) -> None:
    """A receita já declara a família; os flags soltos seriam uma segunda declaração em conflito."""
    _dois_bracos(tmp_path)
    with pytest.raises(SystemExit, match="silenciosamente ignorados"):
        cli._run_compare(_familia(tmp_path, receita, task="reg"))


def test_o_modo_exploratorio_de_celula_unica_continua_existindo(tmp_path, capsys) -> None:
    """Sobre células NÃO-seladas, que é o que o exploratório existe para fazer."""
    _dois_bracos(tmp_path, sealed=False)
    assert cli._run_compare(_solto(tmp_path)) == 0
    assert "EXPLORATORY" in capsys.readouterr().out
    assert ledger.load() == []


def test_sem_receita_e_sem_flags_o_exploratorio_diz_o_que_falta(tmp_path) -> None:
    _dois_bracos(tmp_path)
    with pytest.raises(SystemExit, match="precisa de"):
        cli._run_compare(_solto(tmp_path, task=None))


# ── a leitura da família ────────────────────────────────────────────────────────────────────────


def test_a_familia_reporta_veredito_co_primaria_e_os_diagnosticos(tmp_path, receita, capsys) -> None:
    _dois_bracos(tmp_path)

    assert cli._run_compare(_familia(tmp_path, receita)) == 0
    out = capsys.readouterr().out

    assert "alabama · família teste" in out
    assert "EXPLORATÓRIO" not in out
    # 5/6 contra 3/6 é +33,3 pp — fora de qualquer margem, e a direção tem de estar certa.
    assert "SUPERIOR" in out
    assert "sensibilidade:" in out, "§3 torna a linha multi-margem obrigatória"
    assert "meia-largura" in out and "MDE@80%" in out, "§3 e §5 obrigam os dois na leitura"
    assert "CO-PRIMÁRIA:" in out


def test_a_familia_recusa_celulas_nao_seladas_a_menos_que_peca(tmp_path, receita, capsys) -> None:
    _cell(tmp_path / "cat", "cat", (0, 1), hits=2, sealed=False)
    _cell(tmp_path / "joint", "joint", (0, 1), hits=2, sealed=False)

    with pytest.raises(ValueError, match="selection optimism|ALSO selected"):
        cli._run_compare(_familia(tmp_path, receita))

    assert cli._run_compare(_familia(tmp_path, receita, exploratory=True)) == 0
    assert "EXPLORATÓRIO" in capsys.readouterr().out


def test_a_familia_nomeia_o_braco_que_falta(tmp_path, receita) -> None:
    _cell(tmp_path / "cat", "cat", (0, 1), hits=2)
    with pytest.raises(SystemExit, match="no cells for arm 'joint'"):
        cli._run_compare(_familia(tmp_path, receita))


def test_as_linhas_de_categoria_de_uma_celula_joint_nao_viram_regiao(tmp_path, receita, capsys) -> None:
    """Uma célula joint banca as duas tarefas num arquivo; `reg` tem de ver só as linhas de região."""
    _cell(tmp_path / "cat", "cat", (0, 1), hits=2)
    joint = _cell(tmp_path / "joint", "joint", (0, 1), hits=4)
    extra = P.read(joint).frame.copy()
    extra["task"] = "cat"
    extra["rank_of_true"] = 1
    import pandas as pd
    pd.concat([P.read(joint).frame, extra], ignore_index=True).to_parquet(
        joint / "predictions.parquet", index=False)

    assert cli._run_compare(_familia(tmp_path, receita)) == 0
    assert "joint 100.0000" in capsys.readouterr().out, (
        "as linhas de região são 5/6; misturar as de categoria inflaria o número")


# ── o livro de leituras ─────────────────────────────────────────────────────────────────────────


def test_uma_leitura_confirmatoria_FICA_no_livro(tmp_path, receita) -> None:
    """O ato é irreversível; o registro dele é o que impede a segunda leitura.

    Até 23-08 nenhum `compare` registrava nada: o sidecar gravava `config_fingerprint` e o bloco
    procurava `science_fingerprint`, então o filtro vinha sempre vazio. A leitura era gasta, o livro
    ficava vazio, e o `--confirmatory` recusava para sempre — inclusive o par recém-lido.
    """
    _dois_bracos(tmp_path)
    assert cli._run_compare(_familia(tmp_path, receita)) == 0

    lidas = ledger.load()
    assert {r.state for r in lidas} == {"alabama"}
    assert {r.fingerprint for r in lidas} == {"cat5c1e5c1e5c1e5", "joi5c1e5c1e5c1e5"}
    assert all(r.arms == ("cat", "joint") for r in lidas)
    assert all(r.recipe.endswith(".toml") for r in lidas)


def test_o_json_tambem_registra_a_leitura(tmp_path, receita, capsys) -> None:
    """`--json` saía antes do livro: imprimia o número do teste externo e não registrava nada.

    É o modo que um driver usaria para montar a tabela dos seis conjuntos — ou seja, o modo em que a
    leitura seria gasta em lote.
    """
    _dois_bracos(tmp_path)
    assert cli._run_compare(_familia(tmp_path, receita, json=True)) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["analysis"]["fingerprint"], "a leitura tem de citar a receita que a governou"
    assert payload["co_primary"]["verdict"]
    tarefa = payload["tasks"][0]
    assert set(tarefa["sensitivity"]) == {"0.2", "0.4", "1.0"}
    assert "bca_90" in tarefa and "bca_95" in tarefa, "os dois níveis registrados"
    assert "diagnostics" in tarefa and "mde" in tarefa["diagnostics"]
    assert len(ledger.load()) == 2


def test_uma_leitura_exploratoria_NAO_entra_no_livro(tmp_path, receita) -> None:
    _dois_bracos(tmp_path, sealed=False)
    assert cli._run_compare(_familia(tmp_path, receita, exploratory=True)) == 0
    assert ledger.load() == [], "quem não gasta a leitura não a declara gasta"


def test_o_exploratorio_NAO_e_porta_dos_fundos_para_celulas_seladas(tmp_path, receita) -> None:
    """O bootstrap é determinístico pela semente da receita.

    Sobre células seladas e não-lidas, o exploratório imprimiria exatamente os números da leitura
    confirmatória — e não registraria nada. Um flag digitado por engano gastaria um conjunto de
    forma invisível, que é o modo de falha mais barato de cometer em toda esta camada.
    """
    _dois_bracos(tmp_path)
    with pytest.raises(SystemExit, match="porta dos fundos|não registra como lidas"):
        cli._run_compare(_familia(tmp_path, receita, exploratory=True))
    assert ledger.load() == []


def test_recusa_ANTES_de_gastar_a_leitura_quando_nao_daria_para_registrar(
        tmp_path, receita, capsys) -> None:
    """A recusa é um PREFLIGHT, e a diferença importa: as identidades já se conhecem antes de existir
    número, então recusar ali não gasta a leitura."""
    _dois_bracos(tmp_path, fingerprint=None)

    with pytest.raises(SystemExit, match="não expõem identidade científica"):
        cli._run_compare(_familia(tmp_path, receita))
    assert ledger.load() == []
    assert "família" not in capsys.readouterr().out, "o veredito não pode ter sido computado"


def test_um_unico_braco_orfao_ja_recusa(tmp_path, receita) -> None:
    """O contador global deixava passar: um braço identificado bastava para o outro escapar."""
    _cell(tmp_path / "cat", "cat", (0, 1), hits=2)
    _cell(tmp_path / "joint", "joint", (0, 1), hits=3, fingerprint=None)

    with pytest.raises(SystemExit, match=r"\['joint'\]"):
        cli._run_compare(_familia(tmp_path, receita))
    assert ledger.load() == []


def test_o_fingerprint_vem_do_result_json_quando_o_sidecar_nao_o_tem(tmp_path, receita) -> None:
    """As 54 células da campanha `v19_defence` são anteriores ao campo no sidecar."""
    for arm, hits in (("cat", 2), ("joint", 3)):
        _cell(tmp_path / arm, arm, (0, 1), hits=hits, fingerprint=None)
        for seed in (0, 1):
            (tmp_path / f"{arm}-s{seed}" / "result.json").write_text(json.dumps({
                "science_fingerprint": f"{arm[:3]}0000000000000"[:16],
                "config": {"recipe": f"recipes/v19/{arm}.toml"}}))

    assert cli._run_compare(_familia(tmp_path, receita)) == 0
    assert {r.fingerprint for r in ledger.load()} == {"cat0000000000000", "joi0000000000000"}


def test_selada_sem_identidade_recuperavel_tambem_e_recusada(tmp_path, receita) -> None:
    """A fechadura sem a porta: o filtro do livro descartava fingerprint nulo e a célula passava.

    Sem identidade não dá nem para consultar se aquele conjunto já foi lido — que é a única coisa
    que separa uma segunda leitura de uma primeira.
    """
    _dois_bracos(tmp_path)
    # v1: `read` só exige a identidade a partir da v2, e o recuo dela é um `result.json` que a
    # célula legada pode não ter.
    for caminho in tmp_path.glob("*/predictions_meta.json"):
        meta = json.loads(caminho.read_text())
        meta.pop("science_fingerprint", None)
        meta["schema_version"] = 1
        caminho.write_text(json.dumps(meta))

    with pytest.raises(SystemExit, match="não expõem identidade científica"):
        cli._run_compare(_familia(tmp_path, receita, exploratory=True))
    assert ledger.load() == []
