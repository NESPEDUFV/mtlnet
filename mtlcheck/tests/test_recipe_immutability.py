"""As receitas arquivadas têm que resolver exatamente como resolviam quando as células foram bancadas.

Este teste existe por um erro cometido em 2026-08-19. A unificação do substrato (v19) mudou o default
de `DataConfig.region_engine`. `recipes/v18/cat.toml` não nomeia esse campo, então herdava o default —
e passou a resolver para outra coisa. O resume compara o digest do config BANCADO contra um resolve
fresco (`wave.py:214-217`), então toda célula `cat` selada teria virado stale e o `wave run` a
re-treinaria: **uma segunda leitura do teste externo**, que é o recurso mais caro do projeto.

Os fingerprints abaixo foram conferidos contra as células bancadas em `sealed_bridge` no dia em que
foram fixados. Se um deles quebrar, a pergunta NÃO é "atualizo o literal?" — é "que default eu mexi,
e ele alcança uma receita arquivada?".
"""
import pytest

from mtlcheck.config import load_recipe

# family -> science_fingerprint sob (alabama, seed 0, split_seed 0, inner_validation=True)
FROZEN_V18 = {
    "cat":   "5913dfd73423",
    "reg":   "95020a62a440",
    "joint": "1a8a2514f4b3",
}


@pytest.mark.parametrize("family,expected", sorted(FROZEN_V18.items()))
def test_archived_v18_recipes_still_resolve_identically(family, expected):
    resolved = load_recipe(f"recipes/v18/{family}.toml", state="alabama", seed=0,
                           split_seed=0, inner_validation=True)
    assert resolved.science_fingerprint()[:12] == expected, (
        f"recipes/v18/{family}.toml mudou de resolução. Células seladas que a citam virariam "
        f"stale e seriam re-treinadas, gastando uma segunda leitura do teste externo. Procure o "
        f"default que você mexeu.")


@pytest.mark.parametrize("family", sorted(FROZEN_V18))
def test_v19_is_a_distinct_identity(family):
    """v19 não pode colidir com v18: célula nova tem que ser célula nova."""
    v18 = load_recipe(f"recipes/v18/{family}.toml", state="alabama", seed=0,
                      split_seed=0, inner_validation=True).science_fingerprint()
    v19 = load_recipe(f"recipes/v19/{family}.toml", state="alabama", seed=0,
                      split_seed=0, inner_validation=True).science_fingerprint()
    assert v18 != v19


@pytest.mark.parametrize("family", sorted(FROZEN_V18))
def test_v19_never_relies_on_the_compatibility_default(family):
    """O default de `region_engine` é compatibilidade para receitas v18 e não pode mudar; nenhuma
    receita viva pode depender dele, ou mexer nele silenciosamente moveria ciência."""
    import tomllib
    with open(f"recipes/v19/{family}.toml", "rb") as fh:
        raw = tomllib.load(fh)
    assert "region_engine" in raw.get("data", {}), (
        f"recipes/v19/{family}.toml não nomeia region_engine e está herdando o default de "
        f"compatibilidade")
    assert raw["data"]["region_engine"] == "check2hgi_v18"
