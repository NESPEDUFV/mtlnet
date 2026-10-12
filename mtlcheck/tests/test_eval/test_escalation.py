"""Os gates de S=2 do §2 — pré-registrados, e até 23-08 inexistentes em código."""

from __future__ import annotations

import pytest

from mtlcheck import paths
from mtlcheck.eval import analysis as analysis_mod, compare, escalation, gates, pilot


def _tiers(delta, low, high, seed_deltas, p=0.5):
    fazer = lambda nivel, largura: compare.TierA(
        delta=delta, percentile=(low - largura, high + largura),
        bca=(low - largura, high + largura), p_permutation=p, level=nivel,
        seed_deltas=tuple(seed_deltas), seeds=tuple(range(len(seed_deltas))))
    return {0.90: fazer(0.90, 0.0), 0.95: fazer(0.95, 0.05)}


def test_a_banda_sai_das_replicas_da_ponte_e_a_agregacao_e_declarada() -> None:
    ponte = {"alabama": (0.10, 0.12, 0.08, 0.14), "arizona": (0.30, 0.10, 0.20, 0.40),
             "istanbul": (0.05, 0.06, 0.04, 0.05)}

    maximo = escalation.calibrate(ponte, aggregation="max")
    media = escalation.calibrate(ponte, aggregation="mean")

    assert maximo.sd == max(maximo.per_state.values()) == pytest.approx(
        maximo.per_state["arizona"])
    assert media.sd < maximo.sd, "o máximo é a escolha conservadora, e é por isso que é o default"
    assert set(maximo.per_state) == {"alabama", "arizona", "istanbul"}


def test_um_estado_ponte_com_uma_replica_so_nao_entra_na_banda() -> None:
    with pytest.raises(ValueError, match="não é estimável"):
        escalation.calibrate({"alabama": (0.1,)})


def test_replicas_concordantes_e_apertadas_nao_disparam_nada() -> None:
    gates = escalation.evaluate(state="texas", task="reg",
                                tiers=_tiers(0.50, 0.30, 0.70, (0.49, 0.51)),
                                sd=0.05, margin=0.4)
    assert not gates.fired and gates.outcome == "ok"


def test_sinais_opostos_fora_do_envelope_disparam() -> None:
    """§2(i). Ambos os deltas têm de estar FORA do envelope de 2·sd — dois valores minúsculos de
    sinais trocados são ruído, e tratá-los como discordância faria o gate disparar sempre."""
    disparou = escalation.evaluate(state="california", task="cat",
                                   tiers=_tiers(0.0, -0.5, 0.5, (0.40, -0.40)),
                                   sd=0.05, margin=0.4)
    assert disparou.sign_disagreement

    ruido = escalation.evaluate(state="california", task="cat",
                                tiers=_tiers(0.0, -0.5, 0.5, (0.02, -0.02)),
                                sd=0.05, margin=0.4)
    assert not ruido.sign_disagreement


def test_a_dispersao_entre_replicas_dispara_no_envelope_de_tres_sigmas() -> None:
    """§2(ii): |Δ_s0 − Δ_s7| > 3·sd·√2."""
    sd = 0.05
    limite = escalation.SPREAD_SIGMAS * sd * (2 ** 0.5)

    dentro = escalation.evaluate(state="texas", task="reg",
                                 tiers=_tiers(0.5, 0.3, 0.7, (0.5, 0.5 + limite * 0.9)),
                                 sd=sd, margin=0.4)
    fora = escalation.evaluate(state="texas", task="reg",
                               tiers=_tiers(0.5, 0.3, 0.7, (0.5, 0.5 + limite * 1.1)),
                               sd=sd, margin=0.4)
    assert not dentro.spread_exceeded and fora.spread_exceeded


def test_em_S2_um_veredito_que_vira_ESCALA_e_nao_vira_seed_limited() -> None:
    """§2(iii) tem DOIS estágios: "if it flips, escalate to S=4; if still unstable, report
    'seed-limited'". Em duas réplicas o desfecho é comprar as outras duas — que o §7 já orça.
    Colapsar em "seed-limited" abandonaria um veredito que o protocolo mandou comprar."""
    gates = escalation.evaluate(state="texas", task="reg",
                                tiers=_tiers(-0.35, -0.39, -0.31, (-0.34, -0.36)),
                                sd=0.10, margin=0.4)
    assert gates.verdict_shifts
    assert gates.outcome == "escalate"
    assert gates.shifted_verdicts[0] != gates.verdict or gates.shifted_verdicts[1] != gates.verdict


def test_com_quatro_replicas_a_instabilidade_persistente_vira_seed_limited() -> None:
    """O segundo estágio: quatro réplicas e o veredito ainda vira — aí sim nunca resolve."""
    gates = escalation.evaluate(state="alabama", task="reg",
                                tiers=_tiers(-0.35, -0.39, -0.31, (-0.34, -0.36, -0.35, -0.35)),
                                sd=0.10, margin=0.4)
    assert gates.verdict_shifts and gates.outcome == "seed_limited"


def test_o_deslocamento_move_o_intervalo_junto_com_o_ponto() -> None:
    """Mover só o ponto inventaria um resultado com uma incerteza que não é a dele."""
    tiers = _tiers(0.5, 0.3, 0.7, (0.5, 0.5))
    movido = escalation._shift(tiers, 0.2)
    assert movido[0.90].delta == pytest.approx(0.7)
    assert movido[0.90].bca == pytest.approx((0.5, 0.9))


def test_uma_celula_de_uma_replica_so_nao_passa_pelos_gates() -> None:
    with pytest.raises(ValueError, match="precisam de duas"):
        escalation.evaluate(state="texas", task="reg", tiers=_tiers(0.5, 0.3, 0.7, (0.5,)),
                            sd=0.05, margin=0.4)


# ── réplicas de fluxo colidido (a regra `seed + fold`) ──────────────────────────────────────────


def test_replicas_cujas_sementes_distam_menos_que_os_folds_colidem() -> None:
    """`fold_seed = seed + fold`: com 5 folds, as sementes 0 e 1 treinam 4 dos 5 folds a partir dos
    MESMOS pesos iniciais. Não são réplicas independentes."""
    assert escalation.independent_subset((0, 1, 7, 100), folds=5) == [0, 2, 3]
    assert escalation.independent_subset((0, 7), folds=5) == [0, 1], "os grandes não colidem"
    assert escalation.independent_subset((0, 1, 2), folds=5) == [0]


def test_a_banda_e_o_MAXIMO_entre_todas_as_replicas_e_as_de_fluxo_disjunto() -> None:
    """Réplicas correlacionadas subestimam a dispersão, e uma banda subestimada faz os gates
    dispararem menos e a licença de S=2 passar mais fácil — o lado errado para errar."""
    # As duas colididas (0 e 1) quase idênticas; as independentes bem separadas.
    deltas = {"alabama": (0.10, 0.11, 0.40, 0.70)}
    sementes = {"alabama": (0, 1, 7, 100)}

    ingenua = escalation.calibrate(deltas, aggregation="max")
    conservadora = escalation.calibrate(deltas, aggregation="max", seeds=sementes, folds=5)

    assert conservadora.sd >= ingenua.sd
    assert conservadora.collided == {"alabama": (1,)}
    assert "colidido" in conservadora.describe()


def test_sem_colisao_a_banda_conservadora_e_a_ingenua() -> None:
    deltas = {"florida": (0.10, 0.40)}
    sementes = {"florida": (0, 7)}
    a = escalation.calibrate(deltas, aggregation="max")
    b = escalation.calibrate(deltas, aggregation="max", seeds=sementes, folds=5)
    assert a.sd == b.sd and not b.collided


# ── §12.9 · a banda própria ao lado do envelope ─────────────────────────────────────────────────

def _tier(deltas):
    return {compare.NI_LEVEL: compare.TierA(delta=sum(deltas) / len(deltas), percentile=(-1.0, 1.0),
                                            bca=(-1.0, 1.0), p_permutation=0.5,
                                            seed_deltas=tuple(deltas), seeds=(0, 1, 7, 100)),
            compare.SUPERIORITY_LEVEL: compare.TierA(delta=0.0, percentile=(-1.0, 1.0),
                                                     bca=(-1.0, 1.0), p_permutation=0.5)}


def _banda(sd):
    cal = escalation.Calibration(per_state={"alabama": sd}, sd=sd, aggregation="max",
                                 per_state_independent={}, collided={})
    return {"reg": (cal, False, "reprova")}


def test_a_banda_propria_sai_ao_lado_do_envelope() -> None:
    """§12.9: o envelope vem da PONTE e pode ser 13× a banda do próprio conjunto.

    Sem este número ao lado, um carimbo `seed-limited` é indistinguível de "esta célula é instável"
    — quando na verdade ele vem de um envelope importado de um conjunto uma ordem de grandeza menor.
    """
    receita = analysis_mod.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")
    saida = gates.for_task("texas", receita, _banda(0.3802), "reg",
                           _tier([-0.14, -0.15, -0.13, -0.14]))

    propria = saida["own_band"]
    assert propria["n_replicates"] == 4
    assert propria["sd"] == pytest.approx(0.00816, abs=1e-4)
    assert propria["envelope_over_own"] > 40, "o envelope é dezenas de vezes a banda própria"
    assert saida["calibration"]["sd"] == 0.3802, "o envelope segue sendo o que decide"


def test_com_uma_replica_os_gates_recusam_antes_do_diagnostico() -> None:
    """Uma réplica não estima dispersão nenhuma, e os gates do §2 recusam antes de chegar ao
    diagnóstico — a guarda dentro do `own_band` é defesa em profundidade, não o caminho real."""
    receita = analysis_mod.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")
    tiers = _tier([-0.14])
    with pytest.raises(ValueError, match="precisam de duas"):
        gates.for_task("texas", receita, _banda(0.3802), "reg", tiers)


def test_banda_propria_zero_nao_divide_por_zero() -> None:
    """Quatro réplicas idênticas dão dispersão zero — a razão não é computável, e não é um crash."""
    receita = analysis_mod.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")
    saida = gates.for_task("texas", receita, _banda(0.3802), "reg", _tier([-0.14] * 4))
    assert saida["own_band"]["sd"] == 0.0
    assert saida["own_band"]["envelope_over_own"] is None


# ── §2a · o gate da escada na leitura ───────────────────────────────────────────────────────────

class _Celula:
    def __init__(self, split_seed, model_seeds, arm="joint"):
        import pandas as pd
        self.frame = pd.DataFrame({"split_seed": split_seed, "model_seed": list(model_seeds)})
        self.meta = {"arm": arm}


def _receita_self():
    import dataclasses
    r = analysis_mod.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")
    return dataclasses.replace(r, sd_source="self", bridge_states=())


def test_o_piso_nao_licencia_leitura() -> None:
    """§2a: P=2 é triagem. Ler ali gasta o teste externo sobre um desenho que o protocolo recusa —
    e o `GL_MINIMO` vivia só no `avalia`, que o leitor nunca chama."""
    cells = [_Celula(p, [s]) for p, s in pilot.sementes(2)]
    with pytest.raises(SystemExit, match="o §2a proíbe parar aí"):
        gates.assert_ladder(cells, "florida", _receita_self(), True)


def test_bracos_com_execucoes_diferentes_sao_recusados() -> None:
    """joint com 3 e cat com 2 passava: a contagem unia os pares ENTRE braços, o `_align`
    intersectava em silêncio, e o Δ saía da média de 2 com o relatório carimbando 3."""
    cells = ([_Celula(p, [s], arm="joint") for p, s in pilot.sementes(3)]
             + [_Celula(p, [s], arm="cat") for p, s in pilot.sementes(2)])
    with pytest.raises(SystemExit, match="não têm as mesmas execuções"):
        gates.assert_ladder(cells, "florida", _receita_self(), True)


def test_a_escada_completa_passa(tmp_path) -> None:
    """Forma certa E carimbo: desde 25-08 as duas coisas, porque a forma sozinha aceita uma wave
    morta numa fronteira de degrau."""
    import json

    receita = _receita_self()
    cells = [_Celula(p, [s]) for p, s in pilot.sementes(3)]
    (tmp_path / "ladder_texas.json").write_text(json.dumps({
        "estado": "texas", "margem": receita.delta,
        "execucoes": [list(x) for x in pilot.sementes(3)],
        "veredito": {"cat": {"desfecho": "para"}, "reg": {"desfecho": "para"}}}))
    saida = gates.assert_ladder(cells, "texas", receita, True, raiz=str(tmp_path))
    assert saida["executions"] == 3
    assert {tuple(x) for x in saida["pairs"]} == set(pilot.sementes(3))
    assert saida["ladder_outcome"] == {"cat": "para", "reg": "para"}


def test_um_numero_de_execucoes_fora_da_escada_e_recusado() -> None:
    """Wave interrompida ou manifesto editado à mão. O Δ é a média sobre as execuções — ler isto
    estima outra coisa, e a leitura do teste externo não se desfaz."""
    receita = _receita_self()
    cells = [_Celula(p, [s]) for p, s in pilot.sementes(3)[:2]] + [_Celula(99, [99]),
                                                                   _Celula(98, [98]),
                                                                   _Celula(97, [97])]
    with pytest.raises(SystemExit, match="a escada do §2a tem os degraus"):
        gates.assert_ladder(cells, "texas", receita, True)


def test_um_par_fora_da_sequencia_e_recusado() -> None:
    """Os dois botões andam juntos e a sequência é determinística."""
    receita = _receita_self()
    cells = [_Celula(0, [0]), _Celula(7, [7]), _Celula(1, [0])]   # o terceiro par não é (1, 1)
    with pytest.raises(SystemExit, match="não é o desenho que o §2a registra"):
        gates.assert_ladder(cells, "texas", receita, True)


def test_com_sd_source_bridge_o_gate_da_escada_nao_opina() -> None:
    """A v19 ainda vai ler FL/CA/TX pela receita congelada; a escada não pode recusá-los."""
    receita = analysis_mod.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")
    assert receita.sd_source == "bridge"
    assert gates.assert_ladder([_Celula(0, [0, 7])], "texas", receita, True) is None


def test_a_banda_por_execucao_existe_e_e_a_que_encolhe_com_P() -> None:
    """§10.2 responde ao revisor "seu delta se moveria sob outro sorteio?" com "o intervalo carrega
    os graus de liberdade do P final" — e o código não publicava essa banda.

    O intervalo manchete é o bootstrap por usuário, que promedia as execuções dentro de cada réplica
    e NÃO encolhe com P. A banda do eixo de execução é a única que encolhe, e é o que as execuções
    extras compram. Reportada ao lado, nunca no lugar.
    """
    deltas = [0.10, 0.22, 0.05, 0.18, 0.12, 0.09]

    seis = compare.banda_por_execucao(deltas, margem=0.4)
    tres = compare.banda_por_execucao(deltas[:3], margem=0.4)
    assert seis["graus_de_liberdade"] == 5 and tres["graus_de_liberdade"] == 2
    assert seis["meia_largura"] < tres["meia_largura"], "mais execuções, banda menor"

    # Com 1 grau de liberdade não há banda — a mesma regra do §2a, no eixo da leitura.
    assert compare.banda_por_execucao(deltas[:2]) is None

    # A forma é a MESMA que a escada projeta, para o confronto do §3 ser uma subtração.
    import math
    import statistics

    from mtlcheck.eval import pilot
    esperado = pilot.T95[5] * statistics.stdev(deltas) / math.sqrt(6)
    assert seis["meia_largura"] == pytest.approx(esperado)
