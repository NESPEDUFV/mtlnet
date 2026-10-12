"""A receita de análise — o pré-registro como arquivo em vez de default de linha de comando."""

from __future__ import annotations

import pytest

from mtlcheck.eval import analysis

RECEITA = "recipes/analysis/v19_headline.toml"

BASE = """
[analysis]
name = "t"
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
bridge_states = ["alabama"]
sd_aggregation = "max"
calibration_ratio = 3.0
[design]
folds = 2
[conjunction]
combiner = "bonferroni"
[replicates]
alabama = [0, 1]
[diagnostics]
projected_half_width = [0.05, 0.30]
unpaired_benchmark = 0.5
mde_power = 0.80
"""


def escreve(tmp_path, texto):
    caminho = tmp_path / "a.toml"
    caminho.write_text(texto)
    return caminho


def test_a_receita_congelada_da_v19_carrega_e_diz_o_que_o_protocolo_registra() -> None:
    a = analysis.load(RECEITA)

    assert (a.delta, a.ni_level, a.superiority_level) == (0.4, 0.90, 0.95)
    assert a.sensitivity == (0.2, 0.4, 1.0)
    assert a.replicates == 10_000 and a.permutations == 10_000
    assert a.correction == "holm"
    assert [t.task for t in a.tests] == ["cat", "reg"]
    assert a.test_for("reg") == analysis.HeadlineTest("reg", "reg", "joint")


def test_o_fingerprint_e_do_conteudo_nao_do_caminho(tmp_path) -> None:
    """Renomear não muda a análise; editar muda. É o que permite citar a receita num resultado."""
    um, outro = tmp_path / "um.toml", tmp_path / "outro.toml"
    um.write_text(BASE)
    outro.write_text(BASE)
    assert analysis.load(um).fingerprint == analysis.load(outro).fingerprint

    editado = tmp_path / "editado.toml"
    editado.write_text(BASE.replace("seed = 0", "seed = 7"))
    assert analysis.load(editado).fingerprint != analysis.load(um).fingerprint


def test_uma_chave_desconhecida_e_recusada(tmp_path) -> None:
    """Um typo que cai em default é como uma leitura acaba sendo outro experimento."""
    with pytest.raises(ValueError, match="chaves desconhecidas"):
        analysis.load(escreve(tmp_path, BASE.replace("seed = 0", "seed = 0\nreplicate = 10")))


def test_os_niveis_tem_de_estar_na_ordem_registrada(tmp_path) -> None:
    """Inverter 90 e 95 leria a NI do intervalo mais largo e a superioridade do mais estreito —
    conservador numa ponta e ANTI-conservador na outra, que é o pior dos dois."""
    trocado = BASE.replace("ni = 0.90", "ni = 0.95").replace("superiority = 0.95", "superiority = 0.90")
    with pytest.raises(ValueError, match="ni < superiority"):
        analysis.load(escreve(tmp_path, trocado))


def test_a_margem_tem_de_aparecer_na_linha_de_sensibilidade(tmp_path) -> None:
    with pytest.raises(ValueError, match="não está em sensitivity"):
        analysis.load(escreve(tmp_path, BASE.replace("delta = 0.4", "delta = 0.3")))


def test_duas_comparacoes_na_mesma_tarefa_sao_recusadas(tmp_path) -> None:
    """A família é por (estado, tarefa); duas na mesma tarefa tornariam o m de Holm ambíguo."""
    duplicado = BASE.replace(
        '{ task = "reg", arm_a = "reg", arm_b = "joint" },',
        '{ task = "cat", arm_a = "cat", arm_b = "outro" },')
    with pytest.raises(ValueError, match="mesma tarefa"):
        analysis.load(escreve(tmp_path, duplicado))


def test_uma_familia_vazia_e_recusada(tmp_path) -> None:
    vazia = BASE[:BASE.index("tests = [")] + "tests = []\n" + BASE[BASE.index("[escalation]"):]
    with pytest.raises(ValueError, match="família tem de ser DECLARADA"):
        analysis.load(escreve(tmp_path, vazia))


def test_menos_replicates_que_o_registrado_e_recusado(tmp_path) -> None:
    """O §3 registra ≥10 000. Um piso mais frouxo deixaria uma receita nova governar uma leitura
    confirmatória com a cauda estimada por ruído — e é a cauda que carrega o veredito."""
    with pytest.raises(ValueError, match="§3 registra"):
        analysis.load(escreve(tmp_path, BASE.replace("replicates = 10000", "replicates = 5000")))


@pytest.mark.parametrize("campo,valor", [("correction", "bonferroni"), ("sd_source", "grandes"),
                                         ("sd_aggregation", "mediana")])
def test_valores_fora_do_vocabulario_sao_recusados(tmp_path, campo, valor) -> None:
    original = {"correction": 'correction = "holm"', "sd_source": 'sd_source = "bridge"',
                "sd_aggregation": 'sd_aggregation = "max"'}[campo]
    with pytest.raises(ValueError, match=campo):
        analysis.load(escreve(tmp_path, BASE.replace(original, f'{campo} = "{valor}"')))
