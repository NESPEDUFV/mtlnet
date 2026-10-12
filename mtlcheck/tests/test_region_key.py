"""A chave de região é resolvida pelas colunas, e uma chave não-única é recusada.

Por que este arquivo existe: os cinco estados dos EUA trazem `GEOID` do TIGER, e o default cobria
todos. Istambul traz mahalles do OSM (`@id`/`name`) e **falhava** — descoberto ao construir o
substrato dele pela primeira vez, 2026-08-21. A referência escondia isso porque não fazia este join
para Istambul: pré-posicionava um CSV que renomeava `@id` para `GEOID`.

A guarda de unicidade é a parte que importa mais que o fallback. No arquivo real de Istambul, `name`
tem 774 valores únicos para 964 feições — escolhê-la colapsaria 190 mahalles distintas em outras, em
silêncio, e o efeito apareceria só como uma contagem de regiões diferente lá na frente.
"""
from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon

from mtlcheck.substrate import regions


def _squares(keys, col):
    """Um quadrado por chave, lado a lado, no CRS do projeto."""
    return gpd.GeoDataFrame(
        {col: list(keys)},
        geometry=[Polygon([(i, 0), (i + 1, 0), (i + 1, 1), (i, 1)]) for i in range(len(keys))],
        crs=regions.WGS84)


def _corpus(n):
    return pd.DataFrame({"placeid": range(n),
                         "latitude": [0.5] * n,
                         "longitude": [i + 0.5 for i in range(n)]})


@pytest.mark.parametrize("col", ["GEOID", "@id"])
def test_a_chave_e_resolvida_pelas_colunas_presentes(tmp_path, col):
    path = tmp_path / "r.geojson"
    _squares(["a", "b", "c"], col).to_file(path, driver="GeoJSON")
    built = regions.build(_corpus(3), path)
    assert built.num_regions == 3
    assert built.region_ids == ("a", "b", "c")


def test_geoid_vence_quando_as_duas_existem(tmp_path):
    path = tmp_path / "r.geojson"
    g = _squares(["a", "b"], "GEOID")
    g["@id"] = ["x", "y"]
    g.to_file(path, driver="GeoJSON")
    assert regions.build(_corpus(2), path).region_ids == ("a", "b")


def test_uma_chave_nao_unica_e_recusada(tmp_path):
    """O caso Istambul/`name`: chaves repetidas colapsariam regiões distintas em silêncio."""
    path = tmp_path / "r.geojson"
    _squares(["dup", "dup", "c"], "GEOID").to_file(path, driver="GeoJSON")
    with pytest.raises(ValueError, match="não identifica as feições unicamente"):
        regions.build(_corpus(3), path)


def test_sem_nenhuma_chave_conhecida_o_erro_diz_o_que_fazer(tmp_path):
    path = tmp_path / "r.geojson"
    _squares(["a", "b"], "nome_qualquer").to_file(path, driver="GeoJSON")
    with pytest.raises(ValueError, match="region_key="):
        regions.build(_corpus(2), path)


def test_region_key_explicito_ainda_manda(tmp_path):
    path = tmp_path / "r.geojson"
    g = _squares(["a", "b"], "GEOID")
    g["outra"] = ["p", "q"]
    g.to_file(path, driver="GeoJSON")
    assert regions.build(_corpus(2), path, region_key="outra").region_ids == ("p", "q")


def test_lugares_sem_coordenada_saem_antes_do_join_e_nao_contam_como_descarte(tmp_path) -> None:
    """O caso Istambul, e a razão de não haver tolerância por fonte.

    12 516 dos 42 795 lugares de Istambul não têm lat/lon **na fonte** (o `tabular` bruto do
    Massive-STEPS traz 62 621 linhas com NaN; a ETL não perde nada). Se entrassem no join eles
    contariam como "fora de todo polígono" e levariam a taxa a 30 %, disparando a guarda de
    shapefile-trocado por uma causa que não é geométrica. As lacunas geométricas reais são 328
    lugares — 0,77 % do corpus.
    """
    corpus = pd.DataFrame({"placeid": [0, 1, 2, 3],
                           "latitude": [0.5, np.nan, 0.5, np.nan],
                           "longitude": [0.5, np.nan, 1.5, np.nan]})
    path = tmp_path / "r.geojson"
    _squares(["a", "b"], "GEOID").to_file(path, driver="GeoJSON")
    built = regions.build(corpus, path)
    assert built.num_places == 2, "só os lugares com coordenada entram"


def test_geometria_de_outro_lugar_ainda_e_recusada(tmp_path) -> None:
    """A guarda de shapefile-trocado continua valendo, com limiar único para toda fonte."""
    path = tmp_path / "r.geojson"
    _squares(["a", "b"], "@id").to_file(path, driver="GeoJSON")
    longe = pd.DataFrame({"placeid": range(10), "latitude": [80.0] * 10,
                          "longitude": [170.0] * 10})
    with pytest.raises(ValueError, match="OUTRO estado"):
        regions.build(longe, path)


def test_nao_ha_tolerancia_por_fonte_de_geometria() -> None:
    """Houve, e a justificativa era falsa. O limiar é um só; ver o comentário em regions.py."""
    assert not hasattr(regions, "MAX_SHARE_OUTSIDE_BY_KEY")
