"""A config resolvida, e os campos que ela não deixa mentir."""

import pytest


def test_folds_e_n_splits_nao_podem_divergir() -> None:
    """`train.folds` não governa nada e entra no fingerprint — divergir é identidade nova para o
    mesmo experimento.

    Em 25-08 um manifesto com `set = { folds = 2 }` rodou 5 folds em silêncio, com fingerprint
    próprio. O campo tem zero leitores no código; quem decide é `data.n_splits`.
    """
    from mtlcheck import paths
    from mtlcheck.config import load_recipe

    receita = str(paths.repo_root() / "recipes/v19/cat.toml")
    with pytest.raises(ValueError, match="divergem"):
        load_recipe(receita, state="alabama", seed=0, split_seed=0, folds=2)

    # O contrapeso: sobrepor os dois juntos continua valendo.
    r = load_recipe(receita, state="alabama", seed=0, split_seed=0, folds=2, n_splits=2)
    assert r.train.folds == 2 and r.data.n_splits == 2
