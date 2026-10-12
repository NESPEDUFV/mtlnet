"""The `check2hgi` CLI: argument handling and the refusals, without touching a GPU.

The build itself is exercised end to end on the A40; what belongs in a fast suite is the part that
decides whether a build should happen at all. Every refusal here replaces a way of producing a
substrate that looks fine and is not.
"""

from __future__ import annotations

import json

import pytest

from mtlcheck import cli


def test_the_region_join_is_derived_per_state_and_guarded(tmp_path, monkeypatch) -> None:
    """A preocupação original continua válida; o que mudou é COMO ela é protegida.

    Esta função exigia que o join de região fosse sempre nomeado, com a justificativa de que um
    default derivado deixaria uma execução "tomar emprestada a hierarquia de outro estado, o que é
    irrecuperável a partir dos números depois".

    O perigo é real e continua real. Mas exigir o caminho à mão nunca o preveniu: nada validava que
    a geometria correspondia ao estado, então `--state texas --shapefile <Alabama>` passava. Pior,
    era o caminho manual que CONVIDAVA o erro, porque exigia saber o código FIPS.

    A proteção agora é dupla e mais forte que a exigência era:
      * o shapefile é RESOLVIDO pelo nome do estado, de um mapa pinado (`test_shapefile_lookup.py`),
        então o caso comum não tem como errar;
      * e `regions.build` RECUSA quando os lugares caem fora de todo polígono acima de
        `MAX_SHARE_OUTSIDE` — o que cobre também o `--shapefile` explícito, que nunca foi coberto.

    O que se perdeu: o build deixou de exigir um argumento. O que se ganhou: o erro que o argumento
    devia impedir passou a ser detectado em vez de convidado.
    """
    from mtlcheck import paths
    from mtlcheck.substrate import regions

    # 1 · resolve pelo estado, sem argumento
    assert paths.state_shapefile("alabama").exists()

    # 2 · e a geometria errada é RECUSADA, não avisada
    assert regions.MAX_SHARE_OUTSIDE < 1.0

    # 3 · um estado sem shapefile em disco diz o que fazer, em vez de falhar lá dentro
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["check2hgi", "build", "--recipe", "recipes/v19/substrate.toml",
                  "--state", "texas", "--out", str(tmp_path)])
    assert "--hierarchy" in str(excinfo.value)


def test_half_a_delaunay_is_refused(tmp_path) -> None:
    """Both files or neither: one alone would silently pair a supplied table with a computed one."""
    with pytest.raises(SystemExit, match="go together"):
        cli.main(["check2hgi", "build", "--recipe", "recipes/v18/substrate.toml",
                  "--state", "alabama", "--out", str(tmp_path),
                  "--hierarchy", str(tmp_path / "h.pt"),
                  "--delaunay-places", str(tmp_path / "pois.csv")])


def test_verify_reports_a_missing_manifest(tmp_path, capsys) -> None:
    assert cli.main(["check2hgi", "verify", "--recipe", "recipes/v18/substrate.toml",
                     "--state", "alabama", "--out", str(tmp_path)]) == 1


def test_verify_rejects_a_substrate_that_cannot_be_rebuilt(tmp_path, capsys) -> None:
    """No seed, non-deterministic, or a non-forward-only graph: each is a separate refusal."""
    (tmp_path / "input").mkdir(parents=True)
    (tmp_path / "temp").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({
        "graph": {"forward_only": False},
        "training": {"seed": None},
        "switches": {"deterministic": False},
        "counts": {"windows": 10, "regions": 3},
    }))

    assert cli.main(["check2hgi", "verify", "--recipe", "recipes/v18/substrate.toml",
                     "--state", "alabama", "--out", str(tmp_path)]) == 1
    errors = capsys.readouterr().err
    assert "NOT forward-only" in errors
    assert "no seed recorded" in errors
    assert "non-deterministically" in errors


def test_the_substrate_recipe_refuses_unknown_keys(tmp_path) -> None:
    """A typo in a frozen recipe must not fall back to a default.

    That is how a run ends up being a different experiment than its file says, which is the class of
    failure the whole recipe system exists to prevent.
    """
    from mtlcheck import config

    recipe = tmp_path / "typo.toml"
    recipe.write_text('[substrate]\nengine = "x"\nforwards_only = true\n')
    with pytest.raises(ValueError, match="unknown .* keys"):
        config.load_substrate_recipe(recipe)


def test_the_v18_recipe_loads_and_says_what_v18_is() -> None:
    from mtlcheck import config

    recipe = config.load_substrate_recipe("recipes/v18/substrate.toml")
    assert recipe.engine == "check2hgi_v18"
    assert recipe.forward_only is True, "v18 IS the forward-only graph"
    assert recipe.continuous_time is True, "v18 IS the four elapsed-time columns"
    assert recipe.p2r_hard_neg_size_gate is None, "the S17 gate stays off by default"
