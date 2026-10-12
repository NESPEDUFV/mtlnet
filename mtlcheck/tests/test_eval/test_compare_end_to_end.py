"""O ensaio geral: a campanha inteira, pelo `cli.main` com argv, em dado sintético.

Os outros arquivos testam peças. Este monta uma campanha no **formato exato** das 54 células da
`v19_defence` — três braços, seis conjuntos, uma célula por semente, sidecar v1 sem identidade com o
`science_fingerprint` no `result.json` ao lado, `lineage.produced_by = "wave"` — e a leva pela
sequência que a leitura real vai seguir: ponte primeiro, os três payloads alimentando os grandes.

Entra pelo `main(argv)` e não pelo `_run_compare(Namespace)` de propósito. O `Namespace` montado à
mão foi o que deixou passar, por dias, um `--json` que saía antes do livro: um teste que constrói os
argumentos não exercita o parser, e metade das guardas mora nos defaults dele.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from conftest import extra_valido
from mtlcheck import cli
from mtlcheck.eval import ledger, predictions as P

PONTE = ("alabama", "arizona", "istanbul")
GRANDES = ("florida", "california", "texas")
SEMENTES = {**{e: (0, 1, 7, 100) for e in PONTE}, **{e: (0, 7) for e in GRANDES}}

RECEITA = """
[analysis]
name = "ensaio"
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
tests = [
    { task = "cat", arm_a = "cat", arm_b = "joint" },
    { task = "reg", arm_a = "reg", arm_b = "joint" },
]
[escalation]
sd_source = "bridge"
bridge_states = ["alabama", "arizona", "istanbul"]
sd_aggregation = "max"
calibration_ratio = 3.0
[conjunction]
combiner = "bonferroni"
[design]
folds = 2
[replicates]
alabama = [0, 1, 7, 100]
arizona = [0, 1, 7, 100]
istanbul = [0, 1, 7, 100]
florida = [0, 7]
california = [0, 7]
texas = [0, 7]
[diagnostics]
projected_half_width = [0.05, 0.30]
unpaired_benchmark = 0.5
mde_power = 0.80
"""

N_USERS, N_WINDOWS, N_FOLDS = 200, 4, 2


def _estavel(*partes) -> int:
    """Semente derivada por digest, não por `hash()`.

    `hash()` de string é randomizado por processo (PYTHONHASHSEED), então o dado sintético mudaria
    a cada execução — um teste que muda de resultado entre rodadas não guarda coisa nenhuma, e o
    dia em que ele falhasse ninguém saberia reproduzir.
    """
    return int(hashlib.sha256("|".join(map(str, partes)).encode()).hexdigest()[:12], 16)


def _rows(state, arm, task, seed, fold, vantagem, rng):
    """Linhas de um fold. `vantagem` desloca o braço, e o ruído por usuário dá o que resamplear.

    As réplicas veem QUASE o mesmo dado — só uma fração de mil muda com a semente. É o regime real:
    o §2 mede a banda entre réplicas em 0,05 a 0,15 pp, e um fixture em que cada semente sorteia
    tudo de novo tem banda de pontos percentuais, o que faz o gate de licenciamento reprovar por
    artefato do teste e não por propriedade do desenho.
    """
    users = np.arange(N_USERS * fold, N_USERS * (fold + 1))
    userid = np.repeat(users, N_WINDOWS)
    base = rng.random(len(userid))
    jitter = np.random.default_rng(_estavel(seed, fold)).random(len(userid)) < 0.0008
    acerta = np.where(jitter, ~(base < (0.45 + vantagem)), base < (0.45 + vantagem))
    if task == "cat":
        verdade = np.tile(np.arange(N_WINDOWS) % 7, N_USERS)
        return dict(y_true=verdade, y_pred=np.where(acerta, verdade, (verdade + 1) % 7),
                    rank_of_true=np.where(acerta, 1, 4), userid=userid)
    return dict(y_true=np.zeros(len(userid), dtype=np.int64),
                y_pred=np.zeros(len(userid), dtype=np.int64),
                rank_of_true=np.where(acerta, 1, 50), userid=userid)


def _campanha(raiz: Path) -> None:
    """As 54 células, em miniatura e no formato real."""
    vantagens = {"cat": 0.0, "reg": 0.0, "joint": 0.02}
    for state in PONTE + GRANDES:
        particao = f"{_estavel(state) % 10**12:012d}"
        for arm in ("cat", "reg", "joint"):
            tarefas = ("cat", "reg") if arm == "joint" else (arm,)
            for seed in SEMENTES[state]:
                banked = []
                # Sem a semente: a réplica muda só pelo jitter, como um re-treino muda.
                rng = np.random.default_rng(_estavel(state, arm) % 2**32)
                for task in tarefas:
                    for fold in range(N_FOLDS):
                        campos = _rows(state, arm, task, seed, fold, vantagens[arm], rng)
                        banked.append(P.FoldPredictions(
                            state=state, arm=arm, task=task, split_seed=0,
                            partition_hash=particao, model_seed=seed, fold=fold,
                            selected_epoch=11, window_id=np.arange(len(campos["userid"])),
                            train_labels=frozenset(range(7)), sealed=True, **campos))
                celula = raiz / f"{arm}-{state}-p0s{seed}"
                P.write(celula, banked, extra=extra_valido(arm=arm))
                # Formato das 54 reais: sidecar v1, identidade no result.json ao lado.
                meta = json.loads((celula / "predictions_meta.json").read_text())
                meta["schema_version"] = 1
                meta.pop("science_fingerprint"), meta.pop("recipe")
                (celula / "predictions_meta.json").write_text(json.dumps(meta))
                (celula / "result.json").write_text(json.dumps({
                    "science_fingerprint": f"{arm}{state}"[:16].ljust(16, "0"),
                    "config": {"recipe": f"recipes/v19/{arm}.toml"}}))


@pytest.fixture(scope="module")
def campanha(tmp_path_factory):
    raiz = tmp_path_factory.mktemp("v19_ensaio")
    _campanha(raiz)
    return raiz


@pytest.fixture(scope="module")
def receita(tmp_path_factory):
    caminho = tmp_path_factory.mktemp("analise") / "ensaio.toml"
    caminho.write_text(RECEITA)
    return str(caminho)


def _argv(campanha, receita, state, *extra):
    return ["compare", str(campanha), "--analysis", receita, "--state", state, *extra]


# ── o ensaio ────────────────────────────────────────────────────────────────────────────────────


def test_o_dry_run_confere_tudo_e_nao_le_nada(campanha, receita, livro_fora_do_repo, capsys) -> None:
    """A pergunta "a leitura vai passar?" respondida sem gastá-la."""
    assert cli.main(_argv(campanha, receita, "alabama", "--dry-run")) == 0
    out = capsys.readouterr().out

    assert "TODAS AS GUARDAS PASSAM" in out
    assert "réplicas [0, 1, 7, 100]" in out
    assert "este estado É a ponte" in out
    assert ledger.load() == [], "um ensaio não gasta leitura nenhuma"
    assert "SUPERIOR" not in out and "CO-PRIMÁRIA" not in out, "nem veredito nem número"


def test_a_sequencia_completa_ponte_depois_grandes(campanha, receita, livro_fora_do_repo,
                                                   tmp_path, capsys) -> None:
    """A leitura real, na ordem que o §2 impõe, pelo parser de verdade."""
    payloads = {}
    for state in PONTE:
        assert cli.main(_argv(campanha, receita, state, "--json")) == 0
        payloads[state] = json.loads(capsys.readouterr().out)

    # A ponte mede a banda de réplica; sem ela os gates dos grandes não existem.
    for state, payload in payloads.items():
        assert payload["state"] == state and payload["confirmatory"] is True
        assert payload["escalation"] is None, "um estado-ponte não consome banda, ele a produz"
        assert {t["task"] for t in payload["tasks"]} == {"cat", "reg"}
        for tarefa in payload["tasks"]:
            assert len(tarefa["seed_deltas"]) == 4
            assert tarefa["p_ni"] is not None and tarefa["p_ni_adjusted"] >= tarefa["p_ni"]

    arquivos = []
    for state, payload in payloads.items():
        caminho = tmp_path / f"{state}.json"
        caminho.write_text(json.dumps(payload))
        arquivos += ["--bridge-reading", str(caminho)]

    assert cli.main(_argv(campanha, receita, "florida", "--json", *arquivos)) == 0
    grande = json.loads(capsys.readouterr().out)

    assert grande["escalation"] is not None, "um estado grande sai COM os gates"
    for task, bloco in grande["escalation"].items():
        assert set(bloco["calibration"]["per_state"]) == set(PONTE)
        assert bloco["gates"]["outcome"] in ("ok", "escalate", "seed_limited")
        assert "licensed_for_two" in bloco
    # Quatro estados lidos × três braços, uma identidade por (braço, estado).
    assert len(ledger.load()) == 4 * 3


def test_um_estado_grande_antes_da_ponte_e_recusado(campanha, receita, livro_fora_do_repo) -> None:
    """A ordem do §2 vira recusa: sem a banda medida, nenhum gate audita o veredito."""
    with pytest.raises(SystemExit, match="banda medida na PONTE"):
        cli.main(_argv(campanha, receita, "texas"))
    assert ledger.load() == []


def test_o_ensaio_de_um_estado_grande_REPORTA_a_pendencia_em_vez_de_parar(
        campanha, receita, livro_fora_do_repo, capsys) -> None:
    """Um ensaio serve para ver TUDO. Parar na primeira pendência esconderia se os dados estão em
    ordem — que é justamente o que se quer saber antes de ir ler a ponte."""
    assert cli.main(_argv(campanha, receita, "texas", "--dry-run")) == 0
    out = capsys.readouterr().out

    assert "GUARDAS DE DADOS PASSAM, FALTA A PONTE" in out
    assert "réplicas [0, 7]" in out, "os dados do estado grande foram conferidos mesmo assim"
    assert ledger.load() == []


def test_o_relatorio_humano_traz_o_que_o_protocolo_obriga(campanha, receita, livro_fora_do_repo,
                                                          capsys) -> None:
    assert cli.main(_argv(campanha, receita, "arizona")) == 0
    out = capsys.readouterr().out

    assert "arizona · família ensaio" in out
    assert "CO-PRIMÁRIA:" in out
    assert "sensibilidade: δ=0.2" in out
    assert "meia-largura" in out and "MDE@80%" in out
    assert "mínimo de usuários por classe" in out, "§3, e só sai na tarefa de categoria"
    assert "classe 0:" in out and "classe 6:" in out, "§1 manda as sete linhas"
    assert "ood_fraction" in out and "full" in out, "§1, os diagnósticos de região"


def test_ler_o_mesmo_estado_duas_vezes_e_reproducao_e_nao_gasta_de_novo(
        campanha, receita, livro_fora_do_repo, capsys) -> None:
    """O livro é idempotente por par: a segunda leitura não inventa uma entrada nova.

    Não é permissão para reler — é a garantia de que reproduzir um número publicado não corrompe o
    registro de quantas vezes o conjunto foi de fato gasto.
    """
    assert cli.main(_argv(campanha, receita, "istanbul")) == 0
    capsys.readouterr()
    primeira = [(r.fingerprint, r.state, r.on) for r in ledger.load()]

    assert cli.main(_argv(campanha, receita, "istanbul")) == 0
    capsys.readouterr()
    assert [(r.fingerprint, r.state, r.on) for r in ledger.load()] == primeira


def test_uma_celula_com_fold_faltando_e_recusada(campanha, receita, livro_fora_do_repo,
                                                 tmp_path) -> None:
    """`--only-folds` não entra no fingerprint e o resume marca "feita" por arquivo existente.

    Uma célula parcial entraria no OOF agrupado com uma fração dos usuários daquele braço — outro
    estimando, e nada no veredito denunciaria. O gatilho existiu: um teste de sanidade de 21-08
    rodou um fold só, com predições seladas.
    """
    import shutil

    import pandas as pd

    recorte = tmp_path / "recorte"
    shutil.copytree(campanha, recorte)
    alvo = recorte / "cat-alabama-p0s0" / "predictions.parquet"
    frame = pd.read_parquet(alvo)
    frame[frame["fold"] == 0].to_parquet(alvo, index=False)

    with pytest.raises(SystemExit, match="cobre os folds"):
        cli.main(["compare", str(recorte), "--analysis", receita, "--state", "alabama"])
    assert ledger.load() == []


# ── o handoff ponte→grandes: cada premissa conferida ────────────────────────────────────────────


@pytest.fixture(scope="module")
def pontes(campanha, receita, tmp_path_factory):
    """As três leituras de ponte, como arquivos — o insumo real dos estados grandes."""
    import contextlib
    import io

    from mtlcheck import paths

    destino = tmp_path_factory.mktemp("pontes")
    falso = tmp_path_factory.mktemp("repo_pontes")
    original, paths.repo_root = paths.repo_root, lambda: falso
    try:
        for state in PONTE:
            saida = io.StringIO()
            with contextlib.redirect_stdout(saida):
                cli.main(_argv(campanha, receita, state, "--json"))
            (destino / f"{state}.json").write_text(saida.getvalue())
    finally:
        paths.repo_root = original
    return destino


def _com_pontes(pontes, *estados):
    args = []
    for e in estados:
        args += ["--bridge-reading", str(pontes / f"{e}.json")]
    return args


def test_uma_ponte_incompleta_e_recusada(campanha, receita, pontes, livro_fora_do_repo) -> None:
    """Com agregação por máximo, omitir um estado-ponte só pode BAIXAR o sd — e um sd menor faz os
    gates dispararem menos e a licença passar mais fácil. É anti-conservador e o operador controla."""
    with pytest.raises(SystemExit, match="faltam as leituras"):
        cli.main(_argv(campanha, receita, "florida", *_com_pontes(pontes, "alabama")))
    assert ledger.load() == []


def test_uma_ponte_de_estado_que_nao_e_ponte_e_recusada(campanha, receita, pontes, tmp_path,
                                                        livro_fora_do_repo) -> None:
    impostor = tmp_path / "impostor.json"
    payload = json.loads((pontes / "alabama.json").read_text())
    payload["state"] = "texas"
    impostor.write_text(json.dumps(payload))

    with pytest.raises(SystemExit, match="não está em bridge_states"):
        cli.main(_argv(campanha, receita, "florida", "--bridge-reading", str(impostor)))


def test_uma_ponte_de_OUTRA_receita_e_recusada(campanha, receita, pontes, tmp_path,
                                               livro_fora_do_repo) -> None:
    """Calibrar com o payload de outra análise mistura dois δ, e nada na saída denunciaria."""
    alheio = tmp_path / "alheio.json"
    payload = json.loads((pontes / "alabama.json").read_text())
    payload["analysis"]["fingerprint"] = "0" * 16
    alheio.write_text(json.dumps(payload))

    with pytest.raises(SystemExit, match="produzido pela análise"):
        cli.main(_argv(campanha, receita, "florida", "--bridge-reading", str(alheio),
                       *_com_pontes(pontes, "arizona", "istanbul")))


def test_uma_ponte_exploratoria_e_recusada(campanha, receita, pontes, tmp_path,
                                           livro_fora_do_repo) -> None:
    solto = tmp_path / "solto.json"
    payload = json.loads((pontes / "alabama.json").read_text())
    payload["confirmatory"] = False
    solto.write_text(json.dumps(payload))

    with pytest.raises(SystemExit, match="EXPLORATÓRIA"):
        cli.main(_argv(campanha, receita, "florida", "--bridge-reading", str(solto),
                       *_com_pontes(pontes, "arizona", "istanbul")))


def test_uma_ponte_truncada_recusa_com_mensagem_e_nao_com_traceback(campanha, receita, pontes,
                                                                    tmp_path,
                                                                    livro_fora_do_repo) -> None:
    quebrado = tmp_path / "quebrado.json"
    quebrado.write_text((pontes / "alabama.json").read_text()[:200])

    with pytest.raises(SystemExit, match="ilegível"):
        cli.main(_argv(campanha, receita, "florida", "--bridge-reading", str(quebrado)))


def test_o_ensaio_de_um_grande_COM_a_ponte_ja_mostra_a_licenca(campanha, receita, pontes,
                                                               livro_fora_do_repo, capsys) -> None:
    """A licença não lê nada da célula grande, então o ensaio pode mostrá-la — e é a pergunta que
    decide se vale gastar a leitura."""
    assert cli.main(_argv(campanha, receita, "florida", "--dry-run",
                          *_com_pontes(pontes, *PONTE))) == 0
    out = capsys.readouterr().out

    assert "licencia S=2: True" in out
    assert "TODAS AS GUARDAS PASSAM" in out
    assert "canário §1" in out, "o canário mora no frame_for, que o ensaio não chamava"
    assert ledger.load() == []


def test_a_conjuncao_do_paragrafo_4a_consome_os_payloads_da_leitura(
        campanha, receita, livro_fora_do_repo, tmp_path, capsys) -> None:
    """A frase cross-state, montada do que a leitura por estado já produziu.

    Não abre parquet nenhum, então rodá-la não gasta leitura de teste selado — e por isso ela pode
    rodar de novo quantas vezes o texto precisar depois que os seis estados foram lidos.
    """
    caminhos = []
    for state in PONTE:
        cli.main(["compare", str(campanha), "--analysis", str(receita), "--state", state, "--json"])
        alvo = tmp_path / f"{state}.json"
        alvo.write_text(capsys.readouterr().out)
        caminhos.append(str(alvo))

    assert cli.main(["conjunction", *caminhos, "--analysis", str(receita), "--json"]) == 0
    saida = json.loads(capsys.readouterr().out)

    assert saida["states"] == list(PONTE)
    assert saida["analysis"]["combiner"] == "bonferroni"
    assert {(c["task"], c["family"]) for c in saida["conjunctions"]} == {
        (t, f) for t in ("cat", "reg") for f in ("non_inferiority", "superiority")}
    for c in saida["conjunctions"]:
        assert 0 <= c["u"] <= len(PONTE)
        assert c["curve"] == sorted(c["curve"]), "a curva de u tem de ser monótona"
        if c["family"] == "non_inferiority":
            assert c["u"] <= c["marginal"], "a conjunção nunca compra mais que os vereditos avulsos"


def test_a_conjuncao_recusa_um_estado_lido_por_outra_receita(
        campanha, receita, livro_fora_do_repo, tmp_path, capsys) -> None:
    caminhos = []
    for state in PONTE[:2]:
        cli.main(["compare", str(campanha), "--analysis", str(receita), "--state", state, "--json"])
        alvo = tmp_path / f"{state}.json"
        alvo.write_text(capsys.readouterr().out)
        caminhos.append(str(alvo))

    adulterado = json.loads(Path(caminhos[0]).read_text())
    adulterado["analysis"]["fingerprint"] = "0" * 16
    Path(caminhos[0]).write_text(json.dumps(adulterado))

    with pytest.raises(ValueError, match="sem um u de quê"):
        cli.main(["conjunction", *caminhos, "--analysis", str(receita)])


# ── a escada de escalada do §12.7 ───────────────────────────────────────────────────────────────
#
# Estas guardas não tinham UM teste. A recusa que segurou 27 h de GPU em 24-08 era código sem
# cobertura, e foi um levantamento adversarial que encontrou a segunda recusa — não a suíte.


def _receita_s4(tmp_path_factory, receita, *, aceita=True, delta=0.4):
    """A receita escalada: mesma inferência, tabela de compra a quatro."""
    from mtlcheck.eval import analysis as analysis_mod

    anterior = analysis_mod.load(receita)
    texto = RECEITA.replace('name = "ensaio"', 'name = "ensaio_s4"')
    if aceita:
        texto = texto.replace('implements = "docs/plans/EVALUATION_PROTOCOL.md"',
                              f'implements = "docs/plans/EVALUATION_PROTOCOL.md"\n'
                              f'accepts_bridge_from = ["{anterior.fingerprint}"]')
    texto = texto.replace("delta = 0.4", f"delta = {delta}")
    for e in GRANDES:
        texto = texto.replace(f"{e} = [0, 7]", f"{e} = [0, 1, 7, 100]")
    caminho = tmp_path_factory.mktemp("analise_s4") / "ensaio_s4.toml"
    caminho.write_text(texto)
    return str(caminho)


@pytest.fixture(scope="module")
def campanha_s4(tmp_path_factory):
    """A campanha com a Flórida a QUATRO réplicas — o disco depois da escalada do §2."""
    global SEMENTES
    raiz = tmp_path_factory.mktemp("v19_ensaio_s4")
    antes = SEMENTES
    SEMENTES = {**antes, "florida": (0, 1, 7, 100)}
    try:
        _campanha(raiz)
    finally:
        SEMENTES = antes
    return raiz


def _receita_ratio(tmp_path_factory, receita, *, ratio):
    """A mesma receita com a razão de calibração apertada — o botão que força a licença a reprovar
    sem mexer em δ nem nos níveis.

    Ela declara a antecessora em `accepts_bridge_from` porque a ponte já foi lida sob aquele
    fingerprint (§12.7); sem isso o `assert_calibrates` recusa antes de o gate ser computado, que é
    a escada de escalada fazendo o trabalho dela.
    """
    from mtlcheck.eval import analysis as analysis_mod

    anterior = analysis_mod.load(receita)
    texto = (RECEITA.replace("calibration_ratio = 3.0", f"calibration_ratio = {ratio}")
                    .replace('name = "ensaio"', 'name = "ensaio_apertada"')
                    .replace('implements = "docs/plans/EVALUATION_PROTOCOL.md"',
                             f'implements = "docs/plans/EVALUATION_PROTOCOL.md"\n'
                             f'accepts_bridge_from = ["{anterior.fingerprint}"]'))
    caminho = tmp_path_factory.mktemp("analise_ratio") / "apertada.toml"
    caminho.write_text(texto)
    return str(caminho)


def test_a_receita_escalada_aceita_a_ponte_lida_pela_antecessora(
        campanha_s4, receita, pontes, livro_fora_do_repo, tmp_path_factory, capsys) -> None:
    """O nó do §12.7: escalar produz receita nova, e as leituras de ponte já gastas carregam o
    fingerprint da ANTIGA. Sem a escada, o caminho que o §2 MANDA seguir é inalcançável — as três
    leituras irreversíveis viram lixo e não há segunda leitura possível.

    Aqui o disco está a quatro réplicas, como fica depois da escalada: o guarda de réplicas passa,
    a licença deixa de ter objeto, e a leitura acontece contra a ponte da antecessora.
    """
    s4 = _receita_s4(tmp_path_factory, receita)
    assert cli.main(_argv(campanha_s4, s4, "florida", "--dry-run",
                          *_com_pontes(pontes, *PONTE))) == 0
    out = capsys.readouterr().out
    assert "TODAS AS GUARDAS PASSAM" in out, out


def test_uma_receita_estranha_nao_calibra(
        campanha_s4, receita, pontes, livro_fora_do_repo, tmp_path_factory) -> None:
    """Sem `accepts_bridge_from`, a receita nova não herda leitura de ninguém."""
    s4 = _receita_s4(tmp_path_factory, receita, aceita=False)
    argv = _argv(campanha_s4, s4, "florida",
                 *_com_pontes(pontes, *PONTE))
    with pytest.raises(SystemExit, match="Calibrar com outra receita mistura dois δ"):
        cli.main(argv)


def test_uma_sucessora_que_mexe_na_margem_e_recusada_apesar_do_fingerprint(
        campanha_s4, receita, pontes, livro_fora_do_repo, tmp_path_factory) -> None:
    """A declaração é VERIFICADA, não acreditada.

    Uma receita pode declarar-se sucessora de qualquer uma. O que a impede de herdar leitura gasta
    sob outra margem é a conferência dos parâmetros que o payload carrega — o hash de bytes nunca
    olhou para esse eixo, e δ é a alavanca mais barata: δ = 1,0 sozinho licencia S=2.
    """
    s4 = _receita_s4(tmp_path_factory, receita, delta=1.0)
    argv = _argv(campanha_s4, s4, "florida",
                 *_com_pontes(pontes, *PONTE))
    with pytest.raises(SystemExit, match="a tabela de compra pode mudar, a margem não"):
        cli.main(argv)


def test_o_ensaio_REPORTA_a_licenca_reprovada_em_vez_de_morrer(
        campanha, receita, pontes, livro_fora_do_repo, tmp_path_factory, capsys) -> None:
    """Antes de 24-08 o `--dry-run` de um estado grande com licença REPROVADA levantava SystemExit.

    Isso torna impossível ensaiar exatamente o estado em que alguém está prestes a comprar dezenas
    de horas de GPU: o operador não consegue ver se o RESTO do estado está em ordem.

    ⚠ A primeira versão deste teste rodava com a receita normal, cuja ponte sintética tem jitter
    minúsculo — a licença **aprovava**, e o ramo que o teste diz guardar tinha cobertura ZERO. Um
    revisor adversarial pegou. Daí a razão de calibração apertada: ela força a reprovação.
    """
    apertada = _receita_ratio(tmp_path_factory, receita, ratio=100.0)
    argv = _argv(campanha, apertada, "florida", "--dry-run",
                 *_com_pontes(pontes, *PONTE))
    assert cli.main(argv) == 0, "o ensaio tem de reportar, não morrer"
    out = capsys.readouterr().out
    assert "REPROVA" in out, f"o ramo da licença reprovada não foi exercitado:\n{out}"
    assert "escale para S=4" in out
