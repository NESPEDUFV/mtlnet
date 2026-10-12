"""O shapefile de um estado é descobrível a partir do nome.

Existe porque a ausência deste mapa era a ÚNICA fricção real do caminho de entrada, medida em
2026-08-20: para rodar o Texas era preciso saber que o código FIPS é 48 e que o arquivo é
`tl_2022_48_tract_TX/tl_2022_48_tract.shp`. Nada no código nem no `--help` revelava isso — um `grep`
por `tl_2022` em `src/` dava zero — e Istambul foge da convenção inteira.

As duas convenções não se unificam e isso é do dado, não do código: estados americanos vêm do
TIGER/Line do Census (shapefile por tract), Istambul vem de um recorte de mahalle em GeoJSON.
"""

from __future__ import annotations

import pytest

from mtlcheck import config as cfg
from mtlcheck import paths


def test_every_dataset_has_a_shapefile_mapped() -> None:
    """Um estado treinável sem shapefile mapeado é um estado que não se constrói do zero."""
    assert set(paths.SHAPEFILES) == set(cfg.DATASETS)


@pytest.mark.parametrize("state,expected", [
    ("alabama", "tl_2022_01_tract_AL/tl_2022_01_tract.shp"),
    ("arizona", "tl_2022_04_tract_AZ/tl_2022_04_tract.shp"),
    ("california", "tl_2022_06_tract_CA/tl_2022_06_tract.shp"),
    ("florida", "tl_2022_12_tract_FL/tl_2022_12_tract.shp"),
    ("texas", "tl_2022_48_tract_TX/tl_2022_48_tract.shp"),
    ("istanbul", "istanbul_mahalle/istanbul_mahalle.geojson"),
])
def test_the_mapping_is_the_one_the_banked_substrates_used(state, expected) -> None:
    """Pinado contra os caminhos que construíram os substratos bancados. Se um mudar, um build
    silenciosamente lê outra geometria e o join espacial muda sem ninguém notar."""
    directory, name = paths.SHAPEFILES[state]
    assert f"{directory}/{name}" == expected


def test_a_missing_shapefile_says_what_to_do(tmp_path, monkeypatch) -> None:
    """O erro tem de instruir. Sem isto o `geopandas` falha lá dentro com uma mensagem que não diz
    ao usuário o que fazer — e era esse o estado antes."""
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="mtlcheck data fetch"):
        paths.state_shapefile("texas")


def test_istanbul_says_it_has_no_download(tmp_path, monkeypatch) -> None:
    """Istambul não tem URL oficial estável, e a mensagem diz isso em vez de sugerir um comando que
    não funcionaria — inventar a URL seria pior que a ausência."""
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="mahalle"):
        paths.state_shapefile("istanbul")


def test_an_unknown_state_is_refused_by_name() -> None:
    with pytest.raises(ValueError, match="não há shapefile mapeado"):
        paths.state_shapefile("wyoming")


# ── o comando de dados (2026-08-21) ─────────────────────────────────────────────────────────────

def test_the_massive_steps_inventory_matches_the_published_counts() -> None:
    """As contagens vêm do repositório do Massive-STEPS, conferidas em 2026-08-21.

    Istambul é a âncora: 544 471 é exatamente o que o nosso corpus local tem, o que valida que a
    tabela descreve a mesma fonte que construiu o nosso dado.
    """
    from mtlcheck import data_fetch

    assert len(data_fetch.MASSIVE_STEPS_CITIES) == 15
    assert data_fetch.MASSIVE_STEPS_CITIES["Istanbul"] == 544_471
    assert data_fetch.MASSIVE_STEPS_CITIES["Jakarta"] == 412_100


def test_an_unknown_city_is_refused_with_the_list() -> None:
    from mtlcheck import data_fetch

    with pytest.raises(SystemExit, match="cidade desconhecida"):
        data_fetch.fetch_city("Curitiba")


def test_check_reports_every_gap_instead_of_failing_on_the_first(tmp_path, monkeypatch) -> None:
    """Um inventário que para no primeiro buraco obriga a rodar seis vezes para ver seis buracos."""
    from mtlcheck import config as cfg
    from mtlcheck import data_fetch

    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    missing = data_fetch.check()
    assert len(missing) == 2 * len(cfg.DATASETS)      # corpus + geometria, por conjunto
    assert any("Gowalla" in m or "gowalla" in m for m in missing)


def test_fetching_gowalla_does_not_claim_to_rebuild_the_state_parquets() -> None:
    """O aviso é o produto aqui: baixar o SNAP dá a matéria-prima, não os parquets deste projeto.

    Um fetcher que fingisse reconstruí-los produziria um arquivo com o nome certo e o conteúdo
    errado, que é a pior falha possível neste ponto do pipeline.
    """
    import inspect

    from mtlcheck import data_fetch

    source = inspect.getsource(data_fetch.fetch_gowalla)
    assert "NÃO É" in source and "checkins" in source
