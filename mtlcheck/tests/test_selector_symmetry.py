"""A simetria de seleção do §1: os dois braços escolhem pela grandeza que reportam.

Existe porque a assimetria passou. O braço dedicado de região selecionava por `top10_acc` cru — o
estimando reportado — e o joint selecionava por `top10_acc_indist`, uma variante diagnóstica. Nenhum
teste pinava a métrica do seletor, então a divergência atravessou a campanha inteira sem sintoma.

Medido depois: nas 18 células joint da `v19_defence`, a época escolhida é a mesma pelas duas
grandezas nos 90 folds — o desvio não moveu número bancado. O que ele movia era a defensabilidade:
o §1 chama a simetria de seleção de "mandatory".
"""

from __future__ import annotations

import math

import pytest

from mtlcheck.train import scoring


def _series(cat, raw, indist, ood=None):
    return ({"f1": cat},
            {"f1": [v / 2 for v in raw], "top10_acc": raw, "top10_acc_indist": indist,
             "ood_fraction": ood if ood is not None else [0.1] * len(raw)})


def test_o_seletor_do_joint_usa_o_top10_CRU_que_e_o_que_se_reporta() -> None:
    cat, reg = _series(cat=[0.3, 0.4, 0.5], raw=[0.90, 0.50, 0.40], indist=[0.40, 0.50, 0.60])
    saida = scoring.standard_scores(cat, reg)

    assert saida["selector_reg_metric"] == "top10_acc"
    # As duas grandezas apontam para lados OPOSTOS de propósito: cru cai, indist sobe. Pelo cru o
    # seletor escolhe a época 1; pelo indist escolheria a 3. Tem de seguir o cru.
    assert saida["joint_best"]["epoch"] == 1
    assert saida["joint_best"]["selector"] == pytest.approx(math.sqrt(0.3 * 0.90))
    assert saida["joint_best"]["top10_raw"] == pytest.approx(0.90)


def test_o_braco_dedicado_de_regiao_seleciona_pela_mesma_grandeza() -> None:
    """A simetria em si: os dois lados da comparação manchete, na mesma escala."""
    _, reg = _series(cat=[0.3], raw=[0.60, 0.50, 0.40], indist=[0.40, 0.50, 0.60])
    dedicado = scoring.single_task_best(reg, "top10_acc_indist")

    assert dedicado["metric"] == "top10_acc"
    assert dedicado["epoch"] == 1, "cru é máximo na primeira época"
    # E a lane de diagnóstico continua exposta, rotulada.
    assert dedicado["joint_convention"]["metric"] == "top10_acc_indist"


def test_o_indist_sobrevive_como_diagnostico_rotulado() -> None:
    cat, reg = _series(cat=[0.3, 0.4, 0.5], raw=[0.90, 0.50, 0.40], indist=[0.40, 0.50, 0.60])
    saida = scoring.standard_scores(cat, reg)

    # A lane de diagnóstico continua no MÁXIMO dela, na época dela...
    assert saida["reg_diag_best"]["epoch"] == 3
    assert saida["reg_diag_best"]["top10_indist"] == pytest.approx(0.60)
    # ...e o joint reporta o indist DA ÉPOCA QUE ELE ESCOLHEU, que é outra.
    assert saida["joint_best"]["top10_indist"] == pytest.approx(0.40)


def test_sem_serie_crua_o_seletor_avisa_em_vez_de_cair_calado() -> None:
    cat = {"f1": [0.3, 0.4]}
    reg = {"f1": [0.2, 0.3], "top10_acc_indist": [0.4, 0.5], "ood_fraction": [0.1, 0.1]}
    saida = scoring.standard_scores(cat, reg)

    assert saida["selector_reg_metric"] == "top10_acc_indist"
    assert any("no top10_acc series" in w for w in saida["warnings"])
