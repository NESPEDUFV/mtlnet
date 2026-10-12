"""A escada do §2a dentro da wave — o piso, a escalada, e o que ela nunca faz.

O que estes testes guardam é que a escada não olhe o teste externo (o recurso racionado), que os
dois botões andem juntos, e que um manifesto SEM `partitions = "pilot"` siga byte por byte pelo
caminho de sempre.
"""

from __future__ import annotations

import pytest

from mtlcheck import paths
from mtlcheck.eval import pilot
from mtlcheck.train import wave


def _manifesto(tmp_path, corpo: str):
    p = tmp_path / "w.toml"
    p.write_text(corpo)
    return p


PILOTO = '''
[wave]
study = "escada"

[[cell]]
recipe = "recipes/v19/cat.toml"
states = ["alabama"]
seeds = [0]
partitions = "pilot"
save_predictions = true
'''


def test_o_piso_sai_com_os_DOIS_botoes_andando_juntos(tmp_path) -> None:
    """Repetir uma semente de modelo entre partições cravaria o desvio daquele sorteio na média —
    onde ele nunca se dissolve ao crescer P — e o esconderia da dispersão observada.

    A primeira versão desta integração cruzava `partitions` com `seeds` e produzia `(0,0)` e
    `(7,0)`: duas partições, a MESMA semente. O piso media menos do que prometia.
    """
    _, cells = wave.load(_manifesto(tmp_path, PILOTO))
    pares = [(c.split_seed, c.seed) for c in cells]
    assert pares == [(0, 0), (7, 7)]
    assert len({p for p, _ in pares}) == 2 and len({s for _, s in pares}) == 2


def test_o_piso_e_o_primeiro_degrau_da_escada(tmp_path) -> None:
    _, cells = wave.load(_manifesto(tmp_path, PILOTO))
    assert len(cells) == pilot.ESCADA[0] == 2


@pytest.mark.parametrize("declaracao", ["seeds = [0, 1, 7]", "seeds = [5]"])
def test_declarar_seeds_que_a_escada_ignora_e_recusado(tmp_path, declaracao) -> None:
    """A escada sorteia os dois botões junto e IGNORA `seeds`.

    A versão anterior só recusava listas com mais de um valor, então `seeds = [5]` passava em
    silêncio e o piso rodava `(0,0),(7,7)` — o manifesto, que é dado congelado, declarava uma
    semente que não rodou.
    """
    corpo = PILOTO.replace("seeds = [0]", declaracao)
    with pytest.raises(ValueError, match="que a escada IGNORA"):
        wave.load(_manifesto(tmp_path, corpo))


def test_a_expansao_sobrevive_a_set_e_a_identidade_plana(tmp_path) -> None:
    """O gerador de manifesto temporário quebrava com qualquer `set` não vazio — `json.dumps` emite
    `:` e TOML exige `=` — e explodia com identidade de substrato na forma plana. O degrau seguinte
    morria DEPOIS de o piso ter gastado GPU.
    """
    corpo = PILOTO.replace(
        'states = ["alabama"]',
        'states = ["alabama"]\nfolds = "1"\n'
        'set = { inner_validation = true, lr = 0.001, note = "ok" }')
    corpo = corpo.replace('study = "escada"',
                          'study = "escada"\n\n[substrate.identity]\ncheckin = "abc123"')

    expandido = wave._com_execucoes(_manifesto(tmp_path, corpo), 3)
    _, cells = wave.load(expandido)
    assert len(cells) == 3
    assert cells[0].overrides == {"inner_validation": True, "lr": 0.001, "note": "ok"}
    assert cells[0].folds == "1", "o `folds` do manifesto não pode sumir na expansão"
    assert wave.declared_substrate(expandido) == {"*": {"checkin": "abc123"}}


def test_is_pilot_reconhece_o_manifesto(tmp_path) -> None:
    assert wave.is_pilot(_manifesto(tmp_path, PILOTO))
    fixo = PILOTO.replace('partitions = "pilot"', "split_seed = 0")
    assert not wave.is_pilot(_manifesto(tmp_path, fixo))


def test_um_manifesto_sem_piloto_nao_muda_de_comportamento(tmp_path) -> None:
    """A escada existe por fora do `run`. Nenhuma wave existente muda por ela existir."""
    fixo = PILOTO.replace('partitions = "pilot"', "split_seed = 0").replace("seeds = [0]",
                                                                           "seeds = [0, 1, 7, 100]")
    _, cells = wave.load(_manifesto(tmp_path, fixo))
    assert [(c.split_seed, c.seed) for c in cells] == [(0, 0), (0, 1), (0, 7), (0, 100)]


def test_a_expansao_de_um_degrau_preserva_o_piso(tmp_path) -> None:
    """Aninhamento: o degrau seguinte reaproveita as execuções do anterior, nenhuma descartada."""
    expandido = wave._com_execucoes(_manifesto(tmp_path, PILOTO), 4)
    _, cells = wave.load(expandido)
    pares = [(c.split_seed, c.seed) for c in cells]
    assert pares[:2] == [(0, 0), (7, 7)], "o piso tem de sobreviver à expansão"
    assert len(pares) == 4
    assert pares == pilot.sementes(4)


def test_a_expansao_nao_toca_o_manifesto_original(tmp_path) -> None:
    """Um manifesto é dado congelado; reescrevê-lo durante a execução faria o `git diff` mentir
    sobre o que foi lançado."""
    caminho = _manifesto(tmp_path, PILOTO)
    antes = caminho.read_text()
    wave._com_execucoes(caminho, 6)
    assert caminho.read_text() == antes


def test_a_escada_para_quando_a_dispersao_resolve(tmp_path, monkeypatch) -> None:
    """E a dispersão vem de quem foi injetado — a escada nunca abre predição de teste externo."""
    rodados = []

    def execute(cell, device):
        rodados.append((cell.split_seed, cell.seed))
        return tmp_path / f"run-{cell.split_seed}-{cell.seed}", 0.5

    def identify(cell):
        return (f"c{cell.split_seed}{cell.seed}", "f" * 16, {})

    # dispersão minúscula, mas o piso (1 g.l.) não pode parar; em P=3 resolve
    chamadas = []

    def dispersao(outcomes):
        n = len({(o.cell.split_seed, o.cell.seed) for o in outcomes})
        chamadas.append(n)
        return {("alabama", "cat"): [0.10, 0.101, 0.1005][:n]}

    wave.run_ladder(_manifesto(tmp_path, PILOTO), execute=execute, identify=identify,
                    dispersao=dispersao, margem=0.4)

    assert chamadas[0] == 2, "o piso roda duas execuções"
    assert len(chamadas) == 2, f"tinha de parar em P=3, avaliou {chamadas}"
    assert (1, 1) in rodados, "a terceira execução usa o par seguinte da escada"


def test_uma_celula_falha_para_a_escada_antes_de_escalar(tmp_path) -> None:
    """Escalar sobre dado incompleto mediria dispersão de uma amostra que não é a que se pensa."""
    def execute(cell, device):
        raise RuntimeError("boom")

    def identify(cell):
        return (f"c{cell.split_seed}", "f" * 16, {})

    chamou = []
    saida = wave.run_ladder(_manifesto(tmp_path, PILOTO), execute=execute, identify=identify,
                            dispersao=lambda o: chamou.append(1) or {}, margem=0.4)
    assert any(o.status == "failed" for o in saida)
    assert not chamou, "não se mede dispersão sobre uma wave com buraco"


def test_o_CLI_chama_a_escada_num_manifesto_piloto(tmp_path, monkeypatch) -> None:
    """O achado mais caro da revisão: `run_ladder` tinha ZERO chamadores.

    O `cli` chamava `wave.run` incondicionalmente, então um manifesto `pilot` rodava só o piso, ele
    parava, e nada avisava. O commit dizia "ligada nos dois lados" e nenhum lado estava.
    """
    from mtlcheck import cli
    from mtlcheck.train import wave as wave_mod

    chamou = {}
    def _escada(*a, **k):
        chamou["escada"] = k
        return []

    def _run(*a, **k):
        chamou["run"] = True
        return []

    monkeypatch.setattr(wave_mod, "run_ladder", _escada)
    monkeypatch.setattr(wave_mod, "run", _run)

    cli.main(["wave", "run", str(_manifesto(tmp_path, PILOTO))])
    assert "escada" in chamou, "manifesto pilot tem de ir pela escada"
    assert "run" not in chamou
    assert chamou["escada"]["margem"] == 0.4


def test_o_CLI_nao_chama_a_escada_num_manifesto_normal(tmp_path, monkeypatch) -> None:
    from mtlcheck import cli
    from mtlcheck.train import wave as wave_mod

    chamou = {}
    def _escada(*a, **k):
        chamou["escada"] = True
        return []

    def _run(*a, **k):
        chamou["run"] = True
        return []

    monkeypatch.setattr(wave_mod, "run_ladder", _escada)
    monkeypatch.setattr(wave_mod, "run", _run)

    fixo = PILOTO.replace('partitions = "pilot"', "split_seed = 0")
    cli.main(["wave", "run", str(_manifesto(tmp_path, fixo))])
    assert chamou == {"run": True}


def test_o_provedor_de_dispersao_pareia_joint_contra_dedicado(tmp_path) -> None:
    """E ele lê `result.json` — a validação INTERNA — nunca predição de teste externo."""
    import json

    from mtlcheck import cli

    def escreve(nome, bloco):
        d = tmp_path / nome
        d.mkdir()
        (d / "result.json").write_text(json.dumps({"folds": [{"selection": bloco}]}))
        return d

    class _C:
        def __init__(self, arm, p, s):
            self.state, self.arm, self.split_seed, self.seed = "alabama", arm, p, s
            self.recipe = f"recipes/v19/{arm}.toml"

    class _O:
        def __init__(self, cell, run_dir):
            self.cell, self.run_dir = cell, run_dir

    saida = cli._dispersao_interna([
        _O(_C("joint", 0, 0), escreve("j0", {"joint_best": {"cat_f1": 0.40, "top10_indist": 0.60}})),
        _O(_C("cat", 0, 0), escreve("c0", {"metric": "f1", "value": 0.38})),
        _O(_C("joint", 7, 7), escreve("j7", {"joint_best": {"cat_f1": 0.41, "top10_indist": 0.61}})),
        _O(_C("cat", 7, 7), escreve("c7", {"metric": "f1", "value": 0.39})),
    ])
    assert saida[("alabama", "cat")] == pytest.approx([2.0, 2.0]), saida
    assert ("alabama", "reg") not in saida, "sem o braço dedicado de região não há par"


def test_a_escada_recusa_em_vez_de_parar_quando_nao_ha_delta(tmp_path) -> None:
    """Parar em silêncio aqui banca uma campanha de 1 grau de liberdade.

    Os dois ramos eram fail-open: `por_tarefa` vazio avisava e retornava, e `degraus` vazio caía em
    `all([]) is True`. Nos dois casos a wave terminava no piso, sem falhar, e o sintoma só aparecia
    no `assert_ladder` da leitura — depois de a GPU estar gasta.
    """
    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n[[cell]]\n'
                    'recipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\nseeds = [0]\n'
                    'partitions = "pilot"\n')

    def executa(cell, device):
        return tmp_path / cell.label.replace("/", "_"), None

    def identifica(cell):
        return cell.label, "fp", {}

    with pytest.raises(SystemExit, match="nenhum delta pôde ser montado"):
        wave.run_ladder(path, execute=executa, identify=identifica,
                        dispersao=lambda _: {}, margem=0.4)

    # Dado PARCIAL: o piso tem 2 execuções e a tarefa traz 1 delta. Antes o filtro `len(v) >= 2`
    # a deixava sair da decisão em silêncio -- a escada podia parar por uma tarefa com a dispersão
    # da outra nunca medida.
    with pytest.raises(SystemExit, match="não têm 2 deltas"):
        wave.run_ladder(path, execute=executa, identify=identifica,
                        dispersao=lambda _: {("alabama", "cat"): [0.1]}, margem=0.4)


def test_o_sorteio_de_desenvolvimento_nao_entra_na_escada() -> None:
    """42 é o sorteio de DESENVOLVIMENTO e não pode virar 1/6 da média confirmatória.

    O §10.1 tirou o congelamento da partição de 42 exatamente por isso: as receitas foram afinadas
    nele, e o overshoot de +3/+8 pp em CA/TX é o sintoma confundido. A escada o trazia de volta no
    teto -- que a validação em miniatura de 25-08 mostrou ser alcançável, não hipotético.
    """
    from mtlcheck.eval import pilot

    for p in pilot.ESCADA:
        usados = {v for par in pilot.sementes(p) for v in par}
        assert 42 not in usados, f"P={p} usa o sorteio de desenvolvimento: {sorted(usados)}"


def test_o_delta_da_escada_sai_da_receita_e_nao_do_argparse() -> None:
    """Os seis manifestos da campanha declaram a receita de análise de onde o δ vem.

    Sem isso o δ vinha do default de `--margin`, que é CLI e não pré-registro — a forma que o
    docstring de `eval/analysis.py` condena. Uma wave rodada com `--margin 1.0` para no primeiro
    degrau sempre, e a leitura com δ=0,4 aceita: `assert_ladder` confere a FORMA do conjunto de
    execuções, nunca a condição de parada que as comprou.
    """
    from mtlcheck import paths
    from mtlcheck.eval import analysis
    from mtlcheck.train import wave

    manifestos = sorted((paths.repo_root() / "studies/v19_defence/waves").glob("ladder_*.toml"))
    assert len(manifestos) == 6
    for m in manifestos:
        declarada = wave.declared_analysis(m)
        assert declarada, f"{m.name} não declara `analysis` em [wave]"
        assert analysis.load(paths.repo_root() / declarada).delta == 0.4


def test_a_receita_da_escada_nao_pode_declarar_replicas_fixas() -> None:
    """Na escada quem decide as execuções é a dispersão medida.

    Uma lista pré-registrada aqui ou conflita com o que chegou, ou é um número morto que alguém lê
    como pré-registro. O eixo é conferido por `assert_ladder`, que exige mais: P num degrau, P−1 ≥ 2,
    e os MESMOS pares em todos os braços.
    """
    from mtlcheck import paths
    from mtlcheck.eval import analysis

    receita = analysis.load(paths.repo_root() / "recipes/analysis/v19_ladder.toml")
    assert receita.sd_source == "self"
    assert receita.replicates_by_state == {}
    assert receita.bridge_states == ()

    # E a ponte continua exigindo a lista: afrouxar para os dois teria desarmado a campanha antiga.
    ponte = analysis.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")
    assert ponte.sd_source == "bridge" and ponte.replicates_by_state


def _celula(arm: str, execucoes):
    """Uma célula de predição mínima: o gate só olha `arm` e os dois botões por linha."""
    import types

    import pandas as pd

    frame = pd.DataFrame({"split_seed": [p for p, _ in execucoes],
                          "model_seed": [s for _, s in execucoes]})
    return types.SimpleNamespace(meta={"arm": arm}, frame=frame)


def test_o_veredito_da_escada_e_gravado_e_a_leitura_o_exige(tmp_path, monkeypatch) -> None:
    """Sem o carimbo, uma escada interrompida numa fronteira de degrau passa pelo gate.

    Uma wave morta (OOM, preempção, reboot) logo depois da 3ª execução de uma subida que ia a P=4
    deixa um disco IDÊNTICO ao de uma parada legítima em P=3: mesmo número de execuções, mesmos
    pares, mesmos braços. As três checagens de `assert_ladder` conferem a FORMA do conjunto e nunca
    a condição que o comprou. O mesmo vale para um sync parcial truncado ali, e para uma wave
    comprada contra outro δ.
    """
    import json

    from mtlcheck.eval import analysis, gates

    receita = analysis.load(paths.repo_root() / "recipes/analysis/v19_ladder.toml")
    execucoes = pilot.sementes(3)
    cells = [_celula(arm, execucoes) for arm in ("cat", "reg", "joint")]

    # Sem o arquivo: recusa, mesmo com o disco em forma perfeita de degrau.
    with pytest.raises(SystemExit, match="não há `ladder_alabama.json`"):
        gates.assert_ladder(cells, "alabama", receita, True, raiz=str(tmp_path))

    alvo = tmp_path / "ladder_alabama.json"
    payload = {"estado": "alabama", "margem": 0.4,
               "execucoes": [list(x) for x in execucoes],
               "veredito": {"cat": {"desfecho": "para"}, "reg": {"desfecho": "teto"}}}
    alvo.write_text(json.dumps(payload))
    out = gates.assert_ladder(cells, "alabama", receita, True, raiz=str(tmp_path))
    assert out["ladder_outcome"] == {"cat": "para", "reg": "teto"}

    # δ divergente: a escada comprou contra outra margem.
    alvo.write_text(json.dumps({**payload, "margem": 1.0}))
    with pytest.raises(SystemExit, match="comprou as execuções contra"):
        gates.assert_ladder(cells, "alabama", receita, True, raiz=str(tmp_path))

    # A escada ainda ia escalar quando parou.
    alvo.write_text(json.dumps({**payload,
                                "veredito": {"cat": {"desfecho": "para"},
                                             "reg": {"desfecho": "incompleto"}}}))
    with pytest.raises(SystemExit, match="NÃO resolveu"):
        gates.assert_ladder(cells, "alabama", receita, True, raiz=str(tmp_path))


def test_o_carimbo_nao_grava_os_deltas() -> None:
    """A dispensa de α-spending repousa em a regra depender só da VARIÂNCIA.

    A `sd` sozinha torna a condição de parada recomputável na leitura, então gravar os deltas
    acrescentaria zero à verificação — e exporia o sinal e a magnitude de `joint − dedicado` antes
    da leitura confirmatória, a quem quer que abrisse o arquivo. Kieser & Friede (2000), FDA (2019).
    """
    import inspect

    fonte = inspect.getsource(wave._carimba)
    assert '"deltas"' not in fonte and "por_tarefa" not in fonte
    assert '"sd"' in fonte and '"meia_largura"' in fonte


def test_um_degrau_inalcancavel_pelo_ruido_e_denunciado_no_primeiro(tmp_path, caplog) -> None:
    """A validação que faltava, e que teria custado quatro minutos em vez de duas horas.

    Em 25-08 dois conjuntos subiram ao teto e ninguém sabia por quê até depois da GPU gasta. O motivo
    era aritmético e visível no PRIMEIRO degrau: com a validação interna a 10 % dos usuários, o ruído
    do estimador sozinho (~0,184 pp no Alabama) já excedia o limiar dos degraus P=2, P=3 e P=4
    (0,011 / 0,076 / 0,146). O teto estava decidido antes da primeira execução terminar.
    """
    import logging

    from mtlcheck.train import wave

    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n[[cell]]\n'
                    'recipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\nseeds = [0]\n'
                    'partitions = "pilot"\n')

    def executa(cell, device):
        return tmp_path / cell.label.replace("/", "_"), None

    # Dispersão que resolve de cara, para o laço parar no piso e o teste isolar a denúncia.
    with caplog.at_level(logging.WARNING):
        wave.run_ladder(path, execute=executa, identify=lambda c: (c.label, "fp", {}),
                        dispersao=lambda _: {("alabama", "cat"): [0.0, 0.0, 0.0]},
                        ruido=lambda _: {("alabama", "cat"): 0.184},
                        margem=0.4, escada=(3,))
    assert "INALCANÇÁVEIS" in caplog.text
    assert "[3]" in caplog.text, "o degrau P=3 tem limiar 0,076 e o ruído é 0,184"

    # O contrapeso: um ruído pequeno não denuncia nada.
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        wave.run_ladder(path, execute=executa, identify=lambda c: (c.label, "fp", {}),
                        dispersao=lambda _: {("alabama", "cat"): [0.0, 0.0, 0.0]},
                        ruido=lambda _: {("alabama", "cat"): 0.001},
                        margem=0.4, escada=(3,))
    assert "INALCANÇÁVEIS" not in caplog.text


def test_o_limiar_por_degrau_inverte_a_condicao_de_parada() -> None:
    """`sd_maximo` é a condição de parada resolvida para σ̂, e tem de bater com `avalia` na fronteira."""
    from mtlcheck.eval import pilot

    for p in pilot.ESCADA:
        limite = pilot.sd_maximo(p, margem=0.4)
        # Uma amostra com desvio EXATAMENTE no limite resolve; um pouco acima, não.
        import statistics
        def com_sd(alvo, n):
            base = [-1.0] * (n // 2) + [1.0] * (n - n // 2)
            k = alvo / statistics.stdev(base)
            return [v * k for v in base]
        assert pilot.avalia(com_sd(limite * 0.99, p), margem=0.4).meia_largura < 0.4
        assert pilot.avalia(com_sd(limite * 1.01, p), margem=0.4).meia_largura > 0.4


def test_o_preflight_roda_so_o_piso_e_nao_escala(tmp_path, monkeypatch, capsys) -> None:
    """A checagem barata que responde "esta campanha pode resolver?" antes de comprometer as horas.

    Em 25-08 dois conjuntos subiram ao teto porque o ruído do estimador excedia o limiar dos degraus
    baixos — computável em minutos, e ninguém tinha perguntado. O preflight roda o piso, mede o piso
    de ruído, e PARA.
    """
    import sys
    from types import SimpleNamespace

    from mtlcheck import cli

    manifesto = tmp_path / "w.toml"
    manifesto.write_text('[wave]\nstudy = "estudo"\n\n[[cell]]\n'
                         'recipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\nseeds = [0]\n'
                         'partitions = "pilot"\n')
    rodadas = []
    monkeypatch.setattr(cli, "_execute_cell",
                        lambda c, d: (rodadas.append(c), (tmp_path, None))[1])
    monkeypatch.setattr(cli, "_identify_cell", lambda c: (c.label, "fp", {}))
    monkeypatch.setattr(cli, "_dispersao_interna", lambda o: {("alabama", "cat"): [0.0, 0.0]})
    monkeypatch.setattr(cli, "_ruido_interno", lambda o: {("alabama", "cat"): 0.184})

    saida = cli._preflight_escada(SimpleNamespace(manifest=str(manifesto), device=None,
                                                 no_resume=True), 0.4)
    texto = capsys.readouterr().out
    assert saida == 0
    assert len(rodadas) == 2, "o preflight roda o PISO e nada mais"
    assert "0.0761" in texto, "a tabela de limiares por degrau"
    assert "RUÍDO DO MEDIDOR JÁ DECIDE" in texto
    assert "NENHUM degrau é alcançável" not in texto, "P=6 (0,2608) ainda cabe para ruído 0,184"
    del sys


def test_um_fold_sem_selection_recusa_em_vez_de_encolher_a_amostra(tmp_path) -> None:
    """A série encolhia em silêncio e a média saía sobre 4 folds.

    Um fold sem `joint_best` — o gate `min_best_epoch` pode devolver `joint = None` — sumia da série,
    e a guarda do `run_ladder` conferia número de EXECUÇÕES, não de folds. A escada mediria a
    dispersão sobre uma amostra menor sem nada falhar.
    """
    import json
    from types import SimpleNamespace

    from mtlcheck import cli

    d = tmp_path / "cat-alabama-p0s0"
    d.mkdir()
    folds = [{"selection": {"metric": "f1", "value": 0.30}} for _ in range(5)]
    folds[2] = {"selection": {}}                       # o fold que o gate rejeitou
    (d / "result.json").write_text(json.dumps({"folds": folds}))

    saida = SimpleNamespace(cell=SimpleNamespace(state="alabama", split_seed=0, seed=0, arm="cat",
                                                 recipe="recipes/v19/cat.toml"),
                            run_dir=str(d), status="ran")
    with pytest.raises(SystemExit, match="folds com bloco `selection`"):
        cli._dispersao_interna([saida])


def test_o_manifesto_do_degrau_preserva_a_proveniencia(tmp_path) -> None:
    """Perder `analysis` faria o manifesto do degrau afirmar outra proveniência que a do lançado.

    É dele que a próxima pessoa reconstrói de onde veio o δ, e a escada reescreve o manifesto a cada
    degrau. Antes só `study` sobrevivia.
    """
    import tomllib

    q = wave._com_execucoes(paths.repo_root() / "studies/v19_defence/waves/ladder_arizona.toml", 3)
    raw = tomllib.loads(q.read_text())
    assert raw["wave"]["study"] == "v19_ladder"
    assert raw["wave"]["analysis"] == "recipes/analysis/v19_ladder.toml"
    assert raw["wave"]["confirmatory"] is True
    assert wave.declared_analysis(q) == "recipes/analysis/v19_ladder.toml"


def test_manifesto_misto_pilot_e_nao_pilot_e_recusado(tmp_path) -> None:
    """A partir do segundo degrau as células não-pilot seriam DESCARTADAS em silêncio.

    O piso rodaria com elas e o resto sem — uma matriz com buraco, e o agregado sobre um subconjunto.
    """
    path = tmp_path / "w.toml"
    path.write_text('[wave]\nstudy = "estudo"\n\n'
                    '[[cell]]\nrecipe = "recipes/v19/cat.toml"\nstates = ["alabama"]\n'
                    'seeds = [0]\npartitions = "pilot"\n\n'
                    '[[cell]]\nrecipe = "recipes/v19/reg.toml"\nstates = ["alabama"]\n'
                    'seeds = [0]\nsplit_seed = 0\n')
    with pytest.raises(ValueError, match="DESCARTADAS em silêncio"):
        wave.load(path)
