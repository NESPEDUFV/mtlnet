"""Testes de FIAÇÃO — que a linha de produção é de fato chamada, não só que o helper funciona.

## Por que este arquivo existe

Em 2026-08-19 um commit gravou **seis mutações** em cinco arquivos de `src/`, cada uma desfazendo
uma correção deliberada — incluindo a linha do regularizador de hierarquia, que vale −0,282 pp em
região. A suíte deu **exatamente o mesmo resultado** com e sem as seis
(`studies/porting_validation/INCIDENT_2026-08-19_commit.md`).

O motivo não foi falta de cobertura: `hierarchy_loss` tinha teste, `_draw_negatives` tinha teste,
a orientação de aresta tinha teste. Todos testavam o **helper isolado**. Nenhum testava que o laço
de treino **chama** o helper, que o `build` **usa** o amostrador, que o `load` **preenche** a
proveniência.

Um helper correto que ninguém chama é indistinguível de um helper ausente — e é exatamente o que
seis mutações produziram, verde.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def _tiny_graph(n_places=40, n_fclass=12):
    from mtlcheck.substrate import delaunay
    rows = [{"placeid": p, "category": p % 7, "fclass": p % n_fclass,
             "longitude": -86.0 + (p % 8) * 0.05, "latitude": 32.0 + (p // 8) * 0.05}
            for p in range(n_places)]
    return delaunay.build(pd.DataFrame(rows), pd.Series({p: p % 3 for p in range(n_places)}))


# ── 1 · o amostrador de negativos duros é REALMENTE usado pelo build ────────────────────────────

def test_build_calls_the_hard_negative_sampler(monkeypatch) -> None:
    """A mutação que isto pega: `n_negatives = NEGATIVES_PER_CONTEXT` no lugar do produto.

    `test_poi2vec.py` prova que `_draw_negatives` sorteia do conjunto certo. Não prova que o
    `build` o chama, nem com quantos negativos por janela.
    """
    from mtlcheck.substrate import poi2vec

    chamadas: list[int] = []
    original = poi2vec._draw_negatives

    def spy(candidates, centres, count, rng):
        chamadas.append(count)
        return original(candidates, centres, count, rng)

    monkeypatch.setattr(poi2vec, "_draw_negatives", spy)
    g = _tiny_graph()
    poi2vec.build(g.places, g.edges, seed=0, epochs=1)

    assert chamadas, "o build NÃO chamou _draw_negatives — os negativos voltaram a ser uniformes"
    esperado = (poi2vec.CONTEXT_SIZE - 1) * poi2vec.NEGATIVES_PER_CONTEXT
    assert set(chamadas) == {esperado}, (
        f"negativos por janela = {set(chamadas)}, esperado {esperado} "
        f"(= {poi2vec.CONTEXT_SIZE - 1} contextos × {poi2vec.NEGATIVES_PER_CONTEXT})")


# ── 2 · o regularizador de hierarquia entra no LAÇO ──────────────────────────────────────────────

def test_the_hierarchy_term_enters_the_training_loop(monkeypatch) -> None:
    """A mutação que isto pega: a linha `loss = loss + model.hierarchy_loss()` apagada.

    Vale −0,282 pp em região, e o comentário logo acima dela explica por que o termo não é inerte
    apesar de λ = 1e-8. O commit apagou a linha e deixou o comentário.
    """
    from mtlcheck.substrate import poi2vec

    chamadas = []
    original = poi2vec._SkipGram.hierarchy_loss

    def spy(self):
        chamadas.append(1)
        return original(self)

    monkeypatch.setattr(poi2vec._SkipGram, "hierarchy_loss", spy)
    g = _tiny_graph()
    poi2vec.build(g.places, g.edges, seed=0, epochs=1)

    assert chamadas, ("o termo de hierarquia NUNCA foi avaliado durante o treino — a linha saiu do "
                      "laço, e o resultado é o regularizador global para zero que ela substituiu")


def test_the_hierarchy_pairs_reach_the_model() -> None:
    """Um `hierarchy_loss` chamado sobre zero pares devolve 0 e passaria no teste acima."""
    from mtlcheck.substrate import poi2vec

    g = _tiny_graph()
    capturado = {}
    original = poi2vec._SkipGram.__init__

    def spy(self, vocab_size, dim=poi2vec.EMBEDDING_DIM, *, hierarchy_pairs=None):
        capturado["n"] = 0 if hierarchy_pairs is None else len(hierarchy_pairs)
        original(self, vocab_size, dim, hierarchy_pairs=hierarchy_pairs)

    poi2vec._SkipGram.__init__ = spy
    try:
        poi2vec.build(g.places, g.edges, seed=0, epochs=1)
    finally:
        poi2vec._SkipGram.__init__ = original
    assert capturado.get("n", 0) > 0, "o modelo recebeu ZERO pares (categoria, fclass)"


# ── 3 · a orientação de aresta, ARESTA A ARESTA ─────────────────────────────────────────────────

def test_edge_orientation_is_row_major_edge_by_edge() -> None:
    """A mutação que isto pega: `np.concatenate` no lugar de `np.stack(...).reshape`.

    O E12 confere a FRAÇÃO agregada de arestas high→low com tolerância 0,02. Inverter arestas é
    aproximadamente simétrico, então 2,3 % de inversões mal movem a fração — o teste é cego para
    exatamente o defeito que ele parece cobrir. Este compara a orientação de CADA aresta contra a
    ordem de varredura da referência (por linha de simplex).
    """
    from scipy.spatial import Delaunay

    from mtlcheck.substrate import delaunay

    g = _tiny_graph(n_places=60)
    points = delaunay.place_table(pd.DataFrame([
        {"placeid": p, "category": p % 7, "fclass": p % 12,
         "longitude": -86.0 + (p % 8) * 0.05, "latitude": 32.0 + (p // 8) * 0.05}
        for p in range(60)]))[["longitude", "latitude"]].to_numpy()
    simplices = Delaunay(points, qhull_options=delaunay.QHULL_OPTIONS).simplices

    # A ordem da referência: `for simplex in triangles: for x, y in combinations(simplex, 2)`.
    from itertools import combinations
    vistos: dict[tuple[int, int], tuple[int, int]] = {}
    for simplex in simplices:
        for x, y in combinations(simplex.tolist(), 2):
            if x != y and (key := tuple(sorted((x, y)))) not in vistos:
                vistos[key] = (x, y)

    obtido = {tuple(sorted(r)): tuple(r) for r in g.edges[["source", "target"]].to_numpy().tolist()}
    invertidas = [k for k, v in obtido.items() if k in vistos and vistos[k] != v]
    assert not invertidas, (
        f"{len(invertidas)} de {len(obtido)} arestas com orientação invertida contra a varredura "
        f"por linha da referência. O poi2vec caminha este grafo DIRIGIDO, então isto alcança o "
        f"code book. Exemplos: {invertidas[:3]}")


# ── 4 · a proveniência de substrato é REALMENTE preenchida ──────────────────────────────────────

def test_dataset_load_fills_the_substrate_provenance(tmp_path, monkeypatch) -> None:
    """A mutação que isto pega: `provenance = {}` no lugar da chamada a `substrate_identity.of`.

    Sem isto, o resume volta a servir número velho como novo (tarefa #20) e nada falha.
    """
    from mtlcheck.substrate import identity

    manifesto = {"engine": "check2hgi_v18", "state": "alabama", "recipe": {"repr_seed": 42},
                 "graph": {"edges": 1}, "counts": {}, "features": {},
                 "training": {"seed": 42, "best_loss": 0.2, "init_fingerprint": "a", "n_params": 1},
                 "inputs": {"digests": {"delaunay_edges": "x"}}}
    d = tmp_path / "sub"; d.mkdir()
    (d / "manifest.json").write_text(__import__("json").dumps(manifesto))

    got = identity.of(d)
    assert got and got.get("identity"), "identity.of devolveu vazio para um manifesto válido"

    # E que `dataset.load` PREENCHE o nível de check-in. Checar o texto-fonte não bastava: o ramo
    # de região logo abaixo também menciona `substrate_identity.of`, então apagar só a linha do
    # check-in passava. Verificado por mutação em 2026-08-19 — o mutante passou.
    import ast
    import inspect

    from mtlcheck.data import dataset

    arvore = ast.parse(inspect.getsource(dataset.load).lstrip())
    atribui_checkin = [
        node for node in ast.walk(arvore)
        if isinstance(node, ast.Assign)
        and any(getattr(t, "id", None) == "provenance" for t in node.targets)
        and isinstance(node.value, ast.Dict)
        and any(isinstance(k, ast.Constant) and k.value == "checkin" for k in node.value.keys)
    ]
    assert atribui_checkin, (
        "dataset.load não atribui mais `provenance` com a chave 'checkin' — a proveniência volta a "
        "ser vazia e o resume deixa de perceber que o substrato mudou (tarefa #20)")


# ── 5 · o carimbo de linhagem alimenta o guard ──────────────────────────────────────────────────

def test_the_lineage_stamp_is_what_assert_comparable_reads() -> None:
    """A mutação que isto pega: `produced_by: "wave"` incondicional no `cli.py`.

    Se o carimbo mentir, o guard de linhagem aceita tudo e nada falha.
    """
    import inspect

    from mtlcheck import cli
    from mtlcheck.eval import predictions as pred

    # O carimbo mora em `_cell_extra` desde 23-08, quando a montagem do sidecar foi extraída para
    # que os testes pudessem escrever células pelo MESMO código da produção.
    fonte = inspect.getsource(cli._cell_extra)
    assert '"produced_by": "wave" if _wave_manifest_path[0] else "train"' in fonte, (
        "o carimbo de linhagem deixou de ser condicional — uma célula rodada por `train` passaria "
        "a se declarar produzida por wave, e o guard aceitaria")
    assert "_cell_extra(" in inspect.getsource(cli._train_cell), (
        "o `_train_cell` deixou de montar o sidecar pelo caminho que os testes exercitam")

    # E o guard lê exatamente esta chave.
    guarda = inspect.getsource(pred.assert_comparable)
    assert '"lineage"' in guarda and "produced_by" in guarda, (
        "assert_comparable não lê mais a linhagem que o cli carimba")


# ── os dois braços do fatorial: alcançáveis, e não inertes (2026-08-21) ──────────────────────────

def test_the_scaffolding_flags_reach_the_functions_from_config() -> None:
    """`fix_unit_mismatch` e `symmetrise_poi2vec` existiam SÓ como parâmetro de função.

    Inalcançáveis por receita ⇒ inalcançáveis por wave ⇒ impossíveis de medir sob o regime de
    proveniência do projeto. Este teste pina a fiação: se alguém desligar a passagem, o fatorial
    volta a ser inerte e mediria o mesmo substrato quatro vezes.
    """
    import inspect

    from mtlcheck.config import SubstrateConfig
    from mtlcheck.substrate import pipeline

    campos = {f for f in SubstrateConfig.__dataclass_fields__}
    assert {"fix_unit_mismatch", "symmetrise_poi2vec"} <= campos

    fonte = inspect.getsource(pipeline._scaffolding)
    assert "fix_unit_mismatch=fix_unit_mismatch" in fonte, "o flag não chega ao delaunay.build"
    assert "symmetrise=symmetrise_poi2vec" in fonte, "o flag não chega ao poi2vec.build"

    chamador = inspect.getsource(pipeline.build)
    assert "config.fix_unit_mismatch" in chamador and "config.symmetrise_poi2vec" in chamador, (
        "a receita não alcança o scaffolding")


def test_the_defaults_are_byte_identical_to_the_old_path() -> None:
    """A justificativa para regravar o baseline de artefatos congelados em 2026-08-21.

    Acrescentar dois campos muda o `asdict` e portanto o digest de conteúdo — o teste de artefatos
    congelados falhou, corretamente. O que ele pergunta é se o COMPORTAMENTO mudou. Não mudou: as
    duas funções já tinham `False` como default, então passar `False` explicitamente é o mesmo
    caminho de código. Isto prova, em vez de afirmar.
    """
    import numpy as np
    import pandas as pd

    from mtlcheck.substrate import delaunay, poi2vec

    rows = [{"placeid": p, "category": p % 7, "fclass": p % 12,
             "longitude": -86.0 + (p % 8) * 0.05, "latitude": 32.0 + (p // 8) * 0.05}
            for p in range(40)]
    frame, regions = pd.DataFrame(rows), pd.Series({p: p % 3 for p in range(40)})

    implicito = delaunay.build(frame, regions)
    explicito = delaunay.build(frame, regions, fix_unit_mismatch=False)
    assert implicito.edges.equals(explicito.edges) and implicito.places.equals(explicito.places)

    a = poi2vec.build(implicito.places, implicito.edges, seed=0, epochs=1)
    b = poi2vec.build(implicito.places, implicito.edges, seed=0, epochs=1, symmetrise=False)
    assert np.array_equal(a.fclass_embeddings, b.fclass_embeddings)


def test_each_flag_actually_changes_something() -> None:
    """O contrapeso: sem isto, um fatorial 2×2 poderia medir o mesmo substrato quatro vezes e
    concluir 'sem efeito' pelo motivo errado."""
    import numpy as np
    import pandas as pd

    from mtlcheck.substrate import delaunay, poi2vec

    rows = [{"placeid": p, "category": p % 7, "fclass": p % 12,
             "longitude": -86.0 + (p % 8) * 0.05, "latitude": 32.0 + (p // 8) * 0.05}
            for p in range(40)]
    frame, regions = pd.DataFrame(rows), pd.Series({p: p % 3 for p in range(40)})

    base = delaunay.build(frame, regions)
    corrigido = delaunay.build(frame, regions, fix_unit_mismatch=True)
    assert not base.edges["weight"].equals(corrigido.edges["weight"]), (
        "corrigir as unidades não mudou os pesos — o braço A2 seria inerte")

    a = poi2vec.build(base.places, base.edges, seed=0, epochs=1)
    d = poi2vec.build(base.places, base.edges, seed=0, epochs=1, symmetrise=True)
    assert not np.array_equal(a.fclass_embeddings, d.fclass_embeddings), (
        "simetrizar não mudou o code book — o braço A3 seria inerte")
