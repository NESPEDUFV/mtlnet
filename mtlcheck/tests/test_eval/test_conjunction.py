"""§4a — "vale em pelo menos u dos conjuntos", montado dos payloads já lidos.

A camada existe porque a frase que a dissertação faz no título não é a frase que `compare --state X`
responde. E ela combina com Bonferroni e não com Simes porque a precondição de sobreposição de
usuários do §4a rodou, em 23-08, e falhou.
"""

from __future__ import annotations

import json

import pytest

from mtlcheck import paths
from mtlcheck.eval import analysis as analysis_mod, conjunction as conj

# Caminho absoluto: em nível de módulo, um relativo quebra a COLETA INTEIRA de
# qualquer cwd que não seja a raiz — não dois testes pulados, a suíte inteira.
RECEITA = analysis_mod.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")


def _payload(state, *, p_ni, p_sup=0.001, verdict="non_inferior", confirmatory=True,
             fingerprint=None, tasks=("cat", "reg"), delta=0.2):
    # `delta` entra porque o p de permutação é bilateral: sem o sinal do efeito, um Δ grande e
    # NEGATIVO viraria superioridade.
    return {
        "state": state, "confirmatory": confirmatory,
        "analysis": {"fingerprint": fingerprint or RECEITA.fingerprint},
        "tasks": [{"task": t, "p_ni": p_ni, "p_studentized": p_sup, "delta": delta,
                   "verdict_marginal": verdict} for t in tasks],
    }


def _seis(ps, **over):
    estados = ("alabama", "arizona", "istanbul", "florida", "california", "texas")
    return [_payload(e, p_ni=p, **over) for e, p in zip(estados, ps)]


def test_u_estrela_sai_por_tarefa_e_por_subfamilia() -> None:
    saida = conj.compose(_seis([0.001, 0.002, 0.003, 0.004, 0.005, 0.006]), RECEITA)
    assert {(c.task, c.family) for c in saida} == {
        (t, f) for t in ("cat", "reg") for f in ("non_inferiority", "superiority")}
    for c in saida:
        if c.family == "non_inferiority":
            assert c.u == 6, "seis p pequenos sustentam a conjunção nos seis"


def test_um_conjunto_ruim_derruba_o_u_e_nao_a_frase_inteira() -> None:
    """É o motivo de a conjunção parcial existir: um estado destoante não zera o resultado.

    O caso já aconteceu neste projeto — um braço ganhou na Flórida e desabou no Alabama.
    """
    saida = conj.compose(_seis([0.001, 0.002, 0.003, 0.004, 0.005, 0.90]), RECEITA)
    ni = [c for c in saida if c.family == "non_inferiority"]
    assert all(c.u == 5 for c in ni), "cinco sustentam; o sexto não derruba os cinco"


def test_o_combinador_sai_da_receita_e_e_bonferroni() -> None:
    """§4a: "if overlap is non-trivial ... switch to the Bonferroni combining variant"."""
    saida = conj.compose(_seis([0.01] * 6), RECEITA)
    assert {c.combiner for c in saida} == {"bonferroni"}


def test_bonferroni_custa_u_contra_simes_e_e_esse_o_preco_da_dependencia() -> None:
    ps = [0.004, 0.006, 0.008, 0.010, 0.012, 0.014]
    import dataclasses

    frouxa = dataclasses.replace(RECEITA, conjunction="simes")
    u_simes = [c.u for c in conj.compose(_seis(ps), frouxa) if c.family == "non_inferiority"][0]
    u_bonf = [c.u for c in conj.compose(_seis(ps), RECEITA) if c.family == "non_inferiority"][0]
    assert u_bonf <= u_simes, "a variante robusta nunca compra mais conjuntos"


def test_a_coluna_marginal_conta_os_vereditos_um_a_um() -> None:
    """u* nunca passa da marginal, e a folga entre as duas é o preço da afirmação conjunta.

    Em não-inferioridade as duas colunas medem a MESMA coisa por caminhos diferentes — o veredito
    marginal sai do intervalo, o p sai do endpoint daquele intervalo —, então elas coincidem quando o
    payload é coerente. É o que torna `u* < marginal` legível: a perda é da combinação, não do dado.
    """
    payloads = _seis([0.001] * 6)
    payloads[-1]["tasks"][0].update(p_ni=0.90, verdict_marginal="inconclusive")
    cat = [c for c in conj.compose(payloads, RECEITA)
           if c.task == "cat" and c.family == "non_inferiority"][0]
    assert cat.marginal == 5, "cinco estados sustentam a NI olhando um a um"
    assert cat.u == 5, "e a conjunção sustenta os mesmos cinco"
    assert cat.u <= cat.marginal


def test_payloads_de_receitas_diferentes_sao_recusados() -> None:
    """Cada p foi computado contra a margem da SUA receita; combiná-los daria um u* sem um u de quê."""
    payloads = _seis([0.001] * 6)
    payloads[2]["analysis"]["fingerprint"] = "0" * 16
    with pytest.raises(ValueError, match="daria um u\\* sem um u de quê"):
        conj.compose(payloads, RECEITA)


def test_um_estado_exploratorio_nao_entra_na_frase_confirmatoria() -> None:
    payloads = _seis([0.001] * 6)
    payloads[1]["confirmatory"] = False
    with pytest.raises(ValueError, match="modo exploratório"):
        conj.compose(payloads, RECEITA)


def test_o_mesmo_estado_duas_vezes_e_recusado() -> None:
    """Cada conjunto é UMA observação; repetir um o conta duas vezes e infla u*."""
    payloads = _seis([0.001] * 6)
    payloads[1]["state"] = "alabama"
    with pytest.raises(ValueError, match="entra duas vezes"):
        conj.read_payloads(_escreve(payloads))


def test_um_estado_sem_a_tarefa_e_recusado() -> None:
    payloads = _seis([0.001] * 6)
    payloads[3]["tasks"] = [t for t in payloads[3]["tasks"] if t["task"] != "reg"]
    with pytest.raises(ValueError, match="não traz a tarefa 'reg'"):
        conj.compose(payloads, RECEITA)


def test_a_conjuncao_usa_o_p_BRUTO_e_nao_o_de_Holm() -> None:
    """O §5 põe Holm DENTRO do estado, sobre as duas tarefas daquele estado. Combinar o ajustado
    corrigiria duas vezes pelo mesmo motivo."""
    payloads = _seis([0.02] * 6)
    for p in payloads:
        for t in p["tasks"]:
            t["p_ni_adjusted"] = 0.99
    ni = [c for c in conj.compose(payloads, RECEITA) if c.family == "non_inferiority"][0]
    assert ni.pvalues == (0.02,) * 6


def _escreve(payloads, tmp=None):
    import tempfile
    from pathlib import Path

    raiz = Path(tmp or tempfile.mkdtemp())
    saida = []
    for i, p in enumerate(payloads):
        caminho = raiz / f"{i}.json"
        caminho.write_text(json.dumps(p))
        saida.append(caminho)
    return saida


def test_os_payloads_saem_do_disco_como_o_compare_os_escreve(tmp_path) -> None:
    caminhos = _escreve(_seis([0.001] * 6), tmp_path)
    lidos = conj.read_payloads(caminhos)
    assert [p["state"] for p in lidos] == ["alabama", "arizona", "istanbul",
                                           "florida", "california", "texas"]
    assert all(c.u == 6 for c in conj.compose(lidos, RECEITA)
               if c.family == "non_inferiority")


def test_um_arquivo_que_nao_e_payload_e_recusado(tmp_path) -> None:
    ruim = tmp_path / "x.json"
    ruim.write_text(json.dumps({"qualquer": "coisa"}))
    with pytest.raises(ValueError, match="não é um payload"):
        conj.read_payloads([ruim])


def test_um_efeito_NEGATIVO_grande_nao_pode_virar_superioridade() -> None:
    """O p de permutação é BILATERAL — responde "Δ ≠ 0?", não "Δ > 0?".

    Alimentar a superioridade com ele cru inverte a frase do título: medido em 24-08 sobre os três
    payloads reais da ponte, região saía `u* = 3/3` com o veredito marginal em `0/3`, sobre
    conjuntos em que o joint é INFERIOR (Δ = −0,795 / −0,547 / −0,139). O p minúsculo vinha do
    tamanho do efeito, e o sinal era descartado.
    """
    payloads = _seis([0.9] * 6, p_sup=0.0003, verdict="inferior")
    for p in payloads:
        for t in p["tasks"]:
            t["delta"] = -0.8
    sup = [c for c in conj.compose(payloads, RECEITA) if c.family == "superiority"]
    assert all(c.u == 0 for c in sup), f"efeito negativo virou superioridade: {[c.u for c in sup]}"


def test_um_efeito_positivo_com_p_pequeno_sustenta() -> None:
    payloads = _seis([0.001] * 6, p_sup=0.002, verdict="superior")
    for p in payloads:
        for t in p["tasks"]:
            t["delta"] = +0.5
    sup = [c for c in conj.compose(payloads, RECEITA) if c.family == "superiority"]
    assert all(c.u == 6 for c in sup)


def test_o_invariante_u_menor_que_marginal_e_conferido_em_vez_de_so_declarado() -> None:
    """Estava só na docstring de `Conjunction`, e os payloads reais o violavam."""
    payloads = _seis([0.001] * 6, p_sup=0.001, verdict="non_inferior")
    for p in payloads:
        for t in p["tasks"]:
            t["delta"] = +0.5
    sup = [c for c in conj.compose(payloads, RECEITA) if c.family == "superiority"]
    assert conj.excede_o_marginal(sup) == sup, "u*=6 com marginal=0 tem de ser sinalizado"


def test_compoe_os_payloads_REAIS_de_uma_leitura(tmp_path) -> None:
    """A camada cross-state só tinha sido exercitada com payload sintético.

    Os três payloads da campanha arquivada são leituras de verdade, gastas e publicadas, e servem
    para provar que a composição roda sobre a FORMA que o `compare` emite — que é diferente da que
    um teste constrói à mão. Aqui eles ganham também os campos que a leitura da escada acrescenta
    (`ladder`, `execution_band`), para garantir que campos novos não quebram a composição.
    """
    import json

    from mtlcheck import paths
    from mtlcheck.eval import analysis, conjunction

    base = paths.repo_root() / "studies/archive/v19_defence_bridge/leitura"
    payloads = []
    for f in sorted(base.glob("*.json")):
        d = json.loads(f.read_text())
        d["ladder"] = {"executions": 4, "pairs": [[0, 0], [1, 1], [7, 7], [100, 100]],
                       "ladder_outcome": {"cat": "para", "reg": "para"}, "ladder_margin": 0.4}
        for t in d["tasks"]:
            t["execution_band"] = {"execucoes": 4, "graus_de_liberdade": 3, "sd": 0.05,
                                   "meia_largura": 0.08, "intervalo": [-0.1, 0.06],
                                   "dentro_da_margem": True}
        payloads.append(d)
    assert len(payloads) == 3

    receita = analysis.load(paths.repo_root() / "recipes/analysis/v19_headline.toml")
    saida = conjunction.compose(payloads, receita)

    assert saida, "a composição não produziu nada sobre payloads reais"
    for c in saida:
        assert c.states == ("alabama", "arizona", "istanbul")
        assert len(c.pvalues) == 3
        assert 0 <= c.u <= c.marginal <= 3, "u* nunca passa do marginal"
        assert c.combiner == "bonferroni", "a precondição do §4a falhou; Simes exigiria independência"


def test_a_composicao_recusa_receitas_diferentes() -> None:
    """Cada p foi computado contra a margem e os níveis da SUA receita.

    Combinar payloads de receitas distintas daria um u* sem um "u de quê" — e é fácil acontecer
    agora que existem duas receitas congeladas, a da ponte e a da escada.
    """
    import json

    import pytest

    from mtlcheck import paths
    from mtlcheck.eval import analysis, conjunction

    base = paths.repo_root() / "studies/archive/v19_defence_bridge/leitura"
    payloads = [json.loads(f.read_text()) for f in sorted(base.glob("*.json"))]
    escada = analysis.load(paths.repo_root() / "recipes/analysis/v19_ladder.toml")

    with pytest.raises(ValueError, match="vêm das receitas"):
        conjunction.compose(payloads, escada)
