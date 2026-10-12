"""A escada de escalada — o substituto da ponte.

O que estes testes protegem não é a aritmética (ela é de três linhas): é que a escada nunca licencie
uma parada que o dado não sustenta, e que ela cresça no eixo certo.
"""

from __future__ import annotations

import math

import pytest
from scipy import stats

from mtlcheck.eval import pilot


def test_o_piso_nunca_para_nem_com_dispersao_zero() -> None:
    """Duas execuções idênticas NÃO provam dispersão baixa — provam uma amostra de 1 g.l.

    Esta era a versão anterior do módulo: o fator de Browne de 3,95× inviabiliza a parada em P=2 na
    prática, mas multiplica zero por 3,95 e dá zero. Uma regra que depende de "isso não acontece"
    não é regra. `GL_MINIMO` fecha explicitamente.
    """
    assert pilot.avalia([0.1, 0.1], margem=0.4).proximo == 3, "dispersão zero não licencia parar"
    assert pilot.avalia([0.1, 0.1000001], margem=0.4).proximo == 3


def test_a_escada_cresce_so_em_execucoes_e_na_ordem_registrada() -> None:
    grande = [0.0, 1.0, -1.0, 0.5]
    assert pilot.avalia(grande[:2], margem=0.4).proximo == 3
    assert pilot.avalia(grande[:3], margem=0.4).proximo == 4
    assert pilot.avalia(grande, margem=0.4).proximo == 6


def test_o_teto_carimba_em_vez_de_pedir_mais_gpu() -> None:
    """Chegar ao teto sem resolver é um desfecho declarado, não um convite a comprar mais fits."""
    d = pilot.avalia([0.0, 2.0, -2.0, 1.0, -1.0, 3.0], margem=0.4)
    assert d.limitado and not d.para
    assert d.proximo is None
    assert "partition-limited" in d.describe()


def test_dispersao_pequena_com_graus_de_liberdade_suficientes_para() -> None:
    d = pilot.avalia([0.10, 0.10, 0.11], margem=0.4)
    assert d.para and d.proximo is None
    assert d.meia_largura < 0.4


def test_o_gate_usa_o_limite_superior_e_nao_o_ponto() -> None:
    """Browne 1995: dimensionar pela estimativa pontual de um piloto subdimensiona com probabilidade
    alta. O `sd_ucl` é o que decide; o `sd` observado só é reportado."""
    d = pilot.avalia([0.0, 0.2, -0.2], margem=0.4)
    assert d.sd_ucl > d.sd
    assert d.sd_ucl == pytest.approx(d.sd * pilot.UCL80[2], rel=1e-9)


def test_a_tabela_de_browne_confere_com_a_formula() -> None:
    """Tabelada para ser legível num diff, mas tem de bater com `sqrt(gl / χ²₀,₂₀)`."""
    for gl, valor in pilot.UCL80.items():
        assert valor == pytest.approx(math.sqrt(gl / stats.chi2.ppf(0.20, gl)), abs=5e-4), gl


def test_as_execucoes_sorteiam_os_DOIS_botoes_e_nenhum_valor_se_repete() -> None:
    """Repetir uma semente de modelo entre partições cravaria o desvio daquele sorteio na média —
    onde ele nunca se dissolveria ao crescer P — e o esconderia da dispersão observada."""
    pares = pilot.sementes(4)
    assert len(pares) == 4
    assert all(p == s for p, s in pares), "os dois botões andam juntos"
    assert len({p for p, _ in pares}) == 4, "nenhuma partição se repete"
    assert len({s for _, s in pares}) == 4, "nenhuma semente de modelo se repete"


def test_a_escada_e_aninhada() -> None:
    """Cada degrau é superconjunto do anterior — nenhum fit é descartado ao escalar."""
    anterior = []
    for n in pilot.ESCADA:
        atual = pilot.sementes(n)
        assert atual[:len(anterior)] == anterior, f"P={n} descarta execuções do degrau anterior"
        anterior = atual


def test_uma_execucao_so_e_recusada() -> None:
    with pytest.raises(ValueError, match="pelo menos duas"):
        pilot.avalia([0.1], margem=0.4)


def test_margem_nao_positiva_e_recusada() -> None:
    with pytest.raises(ValueError, match="margem tem de ser positiva"):
        pilot.avalia([0.1, 0.2], margem=0.0)


def test_o_conjunto_grande_da_v19_pararia_em_tres_execucoes() -> None:
    """Calibração contra o dado real: com a dispersão interna medida no Texas (~0,047 em região),
    a escada para em P=3 — que é o custo que o desenho promete nos conjuntos grandes."""
    sd = 0.0473
    deltas = [-0.5, -0.5 + sd * math.sqrt(2)]
    assert pilot.avalia(deltas, margem=0.4).proximo == 3

    tres = deltas + [-0.5 + sd]
    d = pilot.avalia(tres, margem=0.4)
    assert d.para, f"esperava parar em P=3, deu: {d.describe()}"
