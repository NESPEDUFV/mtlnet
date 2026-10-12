"""The POI2Vec table — a categorical code book, not a spatial prior.

The banked Alabama table has 11,848 rows and 284 distinct vectors, because the per-place table is a
pure lookup `poi_emb[i] = fclass_emb[fclass[i]]`. That is the structural property to pin: there is no
bit-exact target, since nothing in the reference's call path is seeded.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from mtlcheck.substrate import delaunay, poi2vec


def _graph(n_places=40, n_fclass=12):
    # n_fclass > 7: o regularizador de hierarquia da referência indexa a tabela de FCLASS com um
    # código de CATEGORIA, então um vocabulário de fclass menor que o de categorias estoura. Nos
    # corpora reais são 7 categorias contra ~284 fclasses; a fixture tem de respeitar isso.
    rng = np.random.default_rng(0)
    rows = [{"placeid": p, "category": p % 7, "fclass": p % n_fclass,
             "longitude": -86.5 + (p % 8) * 0.05 + rng.normal(0, 1e-4),
             "latitude": 32.3 + (p // 8) * 0.05 + rng.normal(0, 1e-4)}
            for p in range(n_places) for _ in range(2)]
    return delaunay.build(pd.DataFrame(rows), pd.Series({p: p % 3 for p in range(n_places)}))


def test_the_table_is_a_code_book_keyed_by_fclass() -> None:
    """The property that says what this artifact IS, and the one a reader most needs.

    Banked Alabama: 11,848 places, 284 distinct vectors. Anything that made those numbers equal
    would mean the table had become per-place, i.e. a different artifact than every substrate was
    anchored against.
    """
    graph = _graph()
    table = poi2vec.build(graph.places, graph.edges, seed=42, epochs=2)

    assert len(table.frame) == len(graph.places)
    assert table.distinct_vectors == graph.places["fclass"].nunique()
    assert table.distinct_vectors < len(table.frame), "a code book, not a per-place embedding"

    # Two places sharing an fclass must carry a bit-identical vector.
    by_fclass = graph.places.groupby("fclass")["placeid"].apply(list)
    shared = next(v for v in by_fclass if len(v) > 1)
    vectors = table.frame.set_index("placeid").loc[shared[:2]].to_numpy()
    assert np.array_equal(vectors[0], vectors[1])


def test_the_seed_actually_reproduces() -> None:
    """The claim that had to be earned rather than asserted.

    `torch_cluster.random_walk` — which PyG's Node2Vec calls — does NOT respect
    `torch.manual_seed`: two calls under one seed give different walks. A first version of this
    module called manual_seed and claimed reproducibility, and did not have it. The walk kernel is
    written here, over a numpy Generator, so the claim is testable and tested.
    """
    graph = _graph()
    a = poi2vec.build(graph.places, graph.edges, seed=42, epochs=2)
    b = poi2vec.build(graph.places, graph.edges, seed=42, epochs=2)
    c = poi2vec.build(graph.places, graph.edges, seed=7, epochs=2)

    assert np.array_equal(a.fclass_embeddings, b.fclass_embeddings)
    assert not np.array_equal(a.fclass_embeddings, c.fclass_embeddings), (
        "if a different seed gave the same table, the seed would not be reaching the walk")


def test_the_walk_respects_the_second_order_bias() -> None:
    """The FREQUENCIES, not the shape — the shape test passed under a uniform mutant.

    A previous commit message claimed this weakness was fixed. It was not: the assertions were
    shape/fill/start/sink only, and replacing the entire p/q-weighted draw with `rng.integers`
    still passed. This asserts the ratio node2vec actually specifies.

    Graph: 0->1, 1->2, 1->3, 2->3. From node 1 having come from 0, the candidates are 2 and 3, and
    NEITHER is a neighbour of 0 — so at p=q both score 1/q and the split must be even. Then from 2
    having come from 1, the candidates are 3 (a neighbour of 1, weight 1) and nothing else. So the
    discriminating case is built by hand below with an explicit return edge.
    """
    # 0 <-> 1, 1 -> 2, and 0 -> 2: from 1 having come from 0, candidate 0 is the RETURN (1/p) and
    # candidate 2 is a neighbour of 0 (weight 1). With p = 0.25, 1/p = 4, so returns should be ~4x.
    edges = np.array([[0, 1, 1, 0], [1, 0, 2, 2]])
    walks = poi2vec._walks(edges, 3, length=3, per_node=4000, p=0.25, q=1.0,
                           rng=np.random.default_rng(0))

    from_one = walks[walks[:, 0] == 0]                 # 0 -> 1 -> {0 (return) | 2 (common)}
    step_two = from_one[from_one[:, 1] == 1][:, 2]
    returns = int((step_two == 0).sum())
    common = int((step_two == 2).sum())
    assert returns + common == len(step_two) > 1000, "the fixture must exercise the choice"

    ratio = returns / common
    assert 3.0 < ratio < 5.0, (
        f"return:common was {ratio:.2f}; node2vec at p=0.25, q=1 specifies 4. A uniform draw gives "
        f"1.0, which is what the previous version of this test could not tell apart.")


def test_the_graph_is_walked_directed_unless_told_otherwise() -> None:
    """Reproduced: edges.csv stores each pair once and the reference never symmetrises, so a walk
    can only move from a lower row index to a higher one. It shapes the whole co-occurrence."""
    graph = _graph()
    directed = poi2vec.build(graph.places, graph.edges, seed=42, epochs=2)
    both = poi2vec.build(graph.places, graph.edges, seed=42, epochs=2, symmetrise=True)
    assert not np.array_equal(directed.fclass_embeddings, both.fclass_embeddings), (
        "if these agreed, symmetrise would be a no-op and the quirk would be unpinned")


# ── negativos duros (correção de 2026-08-19) ────────────────────────────────────────────────────

def test_hard_negatives_exclude_every_co_occurring_fclass():
    """O candidato NUNCA pode ser um fclass que co-ocorreu com o centro, nem o próprio centro.

    Este é o teste que separa a correção do que havia antes: um amostrador uniforme sobre o
    vocabulário passa em qualquer verificação de forma, e falha aqui.
    """
    import numpy as np
    from mtlcheck.substrate import poi2vec as pv

    windows = np.array([[0, 1, 2, 1, 2],
                        [1, 0, 3, 3, 0],
                        [2, 4, 4, 4, 4]])
    candidates = pv._hard_negative_candidates(windows, vocab_size=5)

    assert candidates[0] == [3, 4]          # 1 e 2 co-ocorrem, 0 é o próprio centro
    assert candidates[1] == [2, 4]          # 0 e 3 co-ocorrem
    assert candidates[2] == [0, 1, 3]       # só 4 co-ocorre
    for centre, pool in enumerate(candidates):
        assert centre not in pool


def test_hard_negatives_fall_back_when_everything_co_occurs():
    """A referência cai para 'todos menos o centro' quando a lista esvazia; centros densos batem
    nesse ramo e ele muda o resultado."""
    import numpy as np
    from mtlcheck.substrate import poi2vec as pv

    windows = np.array([[0, 1, 2, 1, 2]])            # 0 co-ocorre com TODO o resto do vocabulário
    candidates = pv._hard_negative_candidates(windows, vocab_size=3)
    assert candidates[0] == [1, 2]


def test_drawn_negatives_come_only_from_the_centres_own_pool():
    import random

    import numpy as np
    from mtlcheck.substrate import poi2vec as pv

    windows = np.array([[0, 1, 2, 1, 2],
                        [1, 0, 3, 3, 0],
                        [2, 4, 4, 4, 4]])
    candidates = pv._hard_negative_candidates(windows, vocab_size=5)
    drawn = pv._draw_negatives(candidates, windows[:, 0], count=2, rng=random.Random(0))

    assert drawn.shape == (3, 2)
    for row, centre in zip(drawn, windows[:, 0]):
        assert set(row.tolist()) <= set(candidates[centre])


def test_negatives_are_without_replacement_while_the_pool_allows_it():
    """`random.sample` é sem reposição; só o ramo de fallback repete. Um amostrador com reposição
    passaria nos testes acima e falha aqui."""
    import random

    import numpy as np
    from mtlcheck.substrate import poi2vec as pv

    windows = np.array([[0, 1, 1, 1, 1]])                     # centro 0 co-ocorre só com 1
    candidates = pv._hard_negative_candidates(windows, vocab_size=12)
    assert len(candidates[0]) == 10                            # 12 - {0} - {1}

    for trial in range(20):
        drawn = pv._draw_negatives(candidates, windows[:, 0], count=10,
                                   rng=random.Random(trial))[0]
        assert len(set(drawn.tolist())) == 10, "repetiu com pool suficiente"


def test_the_hierarchy_regulariser_pulls_pairs_together_not_toward_zero():
    """O termo é `½·λ·Σ‖in[a] − in[b]‖²` sobre pares, não `λ·Σ emb²`.

    Os dois são "um regularizador com o mesmo λ" e têm gradientes completamente diferentes: um
    aproxima vetores entre si, o outro encolhe todos para a origem. Este teste separa os dois.
    """
    import torch
    from mtlcheck.substrate import poi2vec as pv

    pairs = torch.tensor([[0, 1]], dtype=torch.long)
    model = pv._SkipGram(vocab_size=4, dim=3, hierarchy_pairs=pairs)
    with torch.no_grad():
        model.in_embed.weight.copy_(torch.tensor([[1.0, 0.0, 0.0],
                                                  [1.0, 0.0, 0.0],     # igual ao par 0
                                                  [9.0, 9.0, 9.0],     # longe da origem
                                                  [0.0, 0.0, 0.0]]))
    # Par idêntico -> termo ZERO, por maior que seja a norma das outras linhas.
    assert float(model.hierarchy_loss()) == 0.0, (
        "um puxão para zero daria termo > 0 aqui, porque a linha 2 é enorme")

    with torch.no_grad():
        model.in_embed.weight[1] = torch.tensor([1.0, 0.0, 2.0])       # afasta o par
    assert float(model.hierarchy_loss()) == pytest.approx(0.5 * pv.LE_LAMBDA * 4.0)


def test_no_hierarchy_pairs_means_no_term():
    import torch
    from mtlcheck.substrate import poi2vec as pv

    model = pv._SkipGram(vocab_size=4, dim=3)
    assert float(model.hierarchy_loss()) == 0.0
