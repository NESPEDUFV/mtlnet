"""A família manchete de um estado: Holm entre as cadeias, gatekeeping dentro, co-primária por fora.

Os casos que importam são os três lugares onde Holm NÃO entra. Aplicá-lo ali é o erro clássico, e
cada um deles muda um veredito na direção errada.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mtlcheck import paths
from mtlcheck.eval import analysis as analysis_mod, compare, headline

# Caminho absoluto: em nível de módulo, um relativo quebra a COLETA INTEIRA de
# qualquer cwd que não seja a raiz — não dois testes pulados, a suíte inteira.
RECEITA = analysis_mod.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")


def _linhas(n_users=300, hits=3, task="reg", seed=0):
    rng = np.random.default_rng(seed)
    users = np.repeat(np.arange(n_users), 6)
    base = np.tile([1] * hits + [50] * (6 - hits), n_users)
    ruido = rng.permutation(len(users)) % 17 == 0
    return pd.DataFrame({"task": task, "userid": users, "y_true": 0, "y_pred": 0,
                         "model_seed": 0, "rank_of_true": np.where(ruido, 1, base),
                         "fold": 0, "window_id": np.arange(len(users))})


def _leitura(deltas_por_tarefa, **over):
    """Monta uma leitura de estado com efeitos controlados por tarefa."""
    def frame_for(test):
        a = _linhas(hits=3, task=test.task, seed=1)
        b = _linhas(hits=3 + deltas_por_tarefa[test.task], task=test.task, seed=1)
        return a, b

    return headline.read_state(state="alabama", analysis=_receita(**over), frame_for=frame_for)


def _receita(**over):
    import dataclasses
    return dataclasses.replace(RECEITA, replicates=1000, permutations=1000, **over)


def test_a_familia_de_um_estado_le_as_duas_tarefas_e_compoe_a_co_primaria() -> None:
    leitura = _leitura({"cat": 0, "reg": 1})

    assert [r.task for r in leitura.tasks] == ["cat", "reg"]
    assert leitura.co_primary in ("held", "not_held")
    assert leitura.co_primary_reason


def test_holm_entra_entre_as_cadeias_e_o_p_ajustado_e_o_que_decide() -> None:
    """Com m=2, o menor p é multiplicado por 2 e o maior fica — o step-down do Holm."""
    leitura = _leitura({"cat": 1, "reg": 1})

    for r in leitura.tasks:
        assert r.p_ni_adjusted >= r.p_ni
    assert max(r.p_ni_adjusted for r in leitura.tasks) == pytest.approx(
        max(r.p_ni for r in leitura.tasks)), "o maior p não é ajustado sob Holm"


def test_holm_NAO_entra_dentro_da_cadeia_NI_superioridade() -> None:
    """O erro clássico: tratar NI e superioridade da mesma tarefa como família de dois.

    São sequência fixa ao mesmo α — a segunda pergunta só é feita se a primeira passou, e não gasta
    α novo. Se entrasse, a superioridade de uma cadeia com NI folgada exigiria p < 0,025.
    """
    leitura = _leitura({"cat": 2, "reg": 2})
    for r in leitura.tasks:
        if r.ni_holds:
            assert r.alpha_local <= headline.ALPHA
            # O α local vem da posição no Holm ENTRE cadeias, nunca de um segundo teste dentro dela.
            assert r.alpha_local in (pytest.approx(headline.ALPHA),
                                     pytest.approx(headline.ALPHA / 2))


def test_a_co_primaria_usa_os_vereditos_a_alpha_CHEIO_sem_Holm() -> None:
    """§3: interseção-união, "each component at full α" (Berger 1982).

    Uma reivindicação conjuntiva não paga multiplicidade — exigir as duas ao mesmo tempo já é mais
    difícil que exigir uma. Corrigir aqui seria cobrar duas vezes.
    """
    leitura = _leitura({"cat": 1, "reg": 1})
    marginais = {r.task: r.marginal.verdict for r in leitura.tasks}

    esperado = ("held" if marginais["reg"] in ("superior", "non_inferior")
                and marginais["cat"] in ("superior", "non_inferior") else "not_held")
    assert leitura.co_primary == esperado
    assert all(r.marginal.level == compare.NI_LEVEL for r in leitura.tasks)


def test_sem_correcao_o_p_ajustado_e_o_bruto() -> None:
    leitura = _leitura({"cat": 1, "reg": 1}, correction="none")
    for r in leitura.tasks:
        assert r.p_ni_adjusted == r.p_ni


def test_a_linha_de_sensibilidade_sai_por_tarefa() -> None:
    leitura = _leitura({"cat": 1, "reg": 1})
    for r in leitura.tasks:
        assert set(r.sensitivity) == {"0.2", "0.4", "1.0"}


def test_um_efeito_negativo_forte_nao_vira_superior_em_lugar_nenhum() -> None:
    """A via de erro que já existiu neste código: intervalo inteiro ABAIXO de zero lido como win."""
    leitura = _leitura({"cat": -2, "reg": -2})
    for r in leitura.tasks:
        assert r.verdict != "superior"
        assert r.marginal.verdict != "superior"
    assert leitura.co_primary == "not_held"


# ── os relatórios que o protocolo obriga a sair NA leitura ──────────────────────────────────────


def _linhas_cat(n_users=300, acerta=5, seed=0):
    """Sete classes, com a 6 rara de propósito — é o caso que a tabela por classe existe para ver."""
    rng = np.random.default_rng(seed)
    users = np.repeat(np.arange(n_users), 7)
    verdade = np.tile(np.arange(7), n_users)
    certo = rng.random(len(users)) < (acerta / 7)
    return pd.DataFrame({"task": "cat", "userid": users, "y_true": verdade, "model_seed": 0,
                         "y_pred": np.where(certo, verdade, (verdade + 1) % 7),
                         "rank_of_true": np.where(certo, 1, 3),
                         "fold": 0, "window_id": np.arange(len(users))})


def test_a_tabela_por_classe_sai_com_as_sete_linhas_e_a_contagem_de_usuarios() -> None:
    """§1: "A 7-row per-class paired-delta table accompanies every headline delta"."""
    def frame_for(test):
        return _linhas_cat(acerta=4), _linhas_cat(acerta=5)

    receita = _receita(tests=(analysis_mod.HeadlineTest("cat", "cat", "joint"),))
    leitura = headline.read_state(state="alabama", analysis=receita, frame_for=frame_for)
    diag = leitura.task("cat").diagnostics

    assert len(diag["per_class"]) == 7
    assert all({"class", "f1_a", "f1_b", "delta", "users"} <= set(l) for l in diag["per_class"])
    # §3: "report min contributing-user count per class per state".
    assert diag["min_users_per_class"] > 0


def test_a_MDE_e_funcao_apenas_da_largura() -> None:
    """§5 manda publicar a MDE ANTES dos testes; ela só é publicável junto do veredito se for cega
    ao efeito. A prova direta é a identidade: MDE = (z_α + z_poder) · meia-largura / z_α, onde nem o
    Δ nem o sinal entram. Comparar dois cenários seria prova mais fraca e depende do fixture.
    """
    from scipy import stats as scipy_stats

    def frame_for(test):
        return _linhas(hits=3, seed=2), _linhas(hits=4, seed=2)

    leitura = headline.read_state(state="alabama", analysis=_receita(
        tests=(analysis_mod.HeadlineTest("reg", "reg", "joint"),)), frame_for=frame_for)
    diag = leitura.task("reg").diagnostics

    # O erro-padrão sai da largura do intervalo de 90%; a MDE é reportada na convenção do §6,
    # "α = 0.05 two-sided", que é a da tabela de poder e não a do nível de não-inferioridade.
    z_intervalo = scipy_stats.norm.ppf(1 - (1 - compare.NI_LEVEL) / 2)
    z_alpha = scipy_stats.norm.ppf(1 - headline.ALPHA / 2)
    z_poder = scipy_stats.norm.ppf(RECEITA.mde_power)
    assert diag["mde"] == pytest.approx(
        (z_alpha + z_poder) * diag["half_width"] / z_intervalo)
    assert diag["mde"] > 0 and diag["half_width"] > 0


def test_a_meia_largura_realizada_e_confrontada_com_a_projetada() -> None:
    """§3: o diagnóstico obrigatório de primeira execução, contra o alvo pré-registrado."""
    def frame_for(test):
        return _linhas(hits=3), _linhas(hits=4)

    leitura = headline.read_state(state="alabama", analysis=_receita(
        tests=(analysis_mod.HeadlineTest("reg", "reg", "joint"),)), frame_for=frame_for)
    diag = leitura.task("reg").diagnostics

    assert diag["half_width_projected"] == [0.05, 0.30]
    assert isinstance(diag["half_width_within_projection"], bool)
    assert diag["pairing_gain"] > 0, "o ganho do pareamento é hipótese a verificar, não a assumir"


def test_os_diagnosticos_de_regiao_saem_quando_os_rotulos_de_treino_existem() -> None:
    """§1: ood_fraction e o canário por estado × braço, na tabela e não só no gate."""
    def frame_for(test):
        return _linhas(hits=3), _linhas(hits=4)

    def train_labels_for(test):
        return {test.arm_a: {"reg/0": [0]}, test.arm_b: {"reg/0": [0]}}

    quadro = _linhas(hits=3)
    quadro["fold"] = 0
    leitura = headline.read_state(
        state="alabama", analysis=_receita(tests=(analysis_mod.HeadlineTest("reg", "reg", "joint"),)),
        frame_for=lambda t: (quadro, quadro), train_labels_for=train_labels_for)
    regiao = leitura.task("reg").diagnostics["region"]

    assert set(regiao) == {"reg", "joint"}
    assert {"top10_raw", "top10_acc_indist", "ood_fraction", "ood_hit_rate"} <= set(regiao["reg"])
