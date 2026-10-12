"""The region spatial join: places to census tracts, and the region-level scaffolding.

This is the last piece that stood between the project and building a substrate from raw data. What
it produces is everything the hierarchy needs above the place level:

    place_to_index      raw place id -> dense place index
    poi_to_region       place index  -> region index
    region_area         per region
    region_adjacency    regions that touch
    region_similarity   cosine over each region's category mix

## Four behaviours reproduced deliberately, none of which I would have chosen

Each is load-bearing for reproducing banked artifacts, and each is a trap if read as intent.

**1. Area is computed in degrees², not in metres².** The reference takes `geometry.area` on an
EPSG:4326 frame, where coordinates are latitude and longitude, so the number is not an area in any
physical sense and its scale varies with latitude. It matters because `region2city` weights regions
by it. Reprojecting to an equal-area CRS would be more correct and would change every city vector
and therefore every banked number, so it stays — recorded here rather than silently fixed.

**2. Region indices follow first appearance, not sort order.** `region_to_idx` enumerates
`GEOID.unique()` over the place table after the join, so the index of a region depends on which
place happened to be listed first. Sorting would be tidier and would renumber every region.

**3. A place is represented by its FIRST check-in's coordinates.** `groupby(placeid).first()`, so a
place whose rows disagree on latitude takes whichever row the sort put first.

**4. A place intersecting two tracts is silently resolved to one.** `sjoin` emits one row per match,
and the reference's `{pid: i for i, pid in enumerate(...)}` keeps the LAST occurrence while
`len(pois)` counts both. That is a real defect — it makes the place count disagree with the mapping.
Here the duplicates are dropped explicitly, keeping the first match, and the count is logged. On the
tract data measured so far no place matches two tracts, so this changes nothing today and stops
being silent if it ever does.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

WGS84 = "EPSG:4326"

#: Acima disto o build RECUSA em vez de avisar: é a assinatura de shapefile de outro estado.
#: Frouxo de propósito — em Alabama e Arizona o descarte medido é exatamente zero, então qualquer
#: coisa perto de 20% já é outra geometria, não imprecisão de fronteira.
MAX_SHARE_OUTSIDE = 0.20


@dataclass(frozen=True)
class Regions:
    """The place/region scaffolding, as produced from the corpus and a shapefile."""

    place_to_index: dict[int, int]
    poi_to_region: np.ndarray          # [n_places] int64
    region_area: np.ndarray            # [n_regions] float32, in degrees**2 (see the module docstring)
    region_adjacency: np.ndarray       # [2, n_edges] int64
    region_similarity: np.ndarray      # [n_regions, n_regions] float32
    region_ids: tuple[str, ...]        # region index -> GEOID, so the mapping is auditable
    dropped_places: int                # places outside every tract

    @property
    def num_places(self) -> int:
        return len(self.place_to_index)

    @property
    def num_regions(self) -> int:
        return len(self.region_ids)


#: A chave de região por fonte, em ordem de tentativa. `GEOID` é do TIGER (census tract, os cinco
#: estados dos EUA); `@id` é do OSM (as mahalles de Istambul). A referência não fazia este join para
#: Istambul: ela pré-posicionava um CSV que **renomeava `@id` para `GEOID`**, e por isso o caminho
#: nunca foi exercitado e o default `GEOID` bastou por cinco estados.
REGION_KEY_CANDIDATES = ("GEOID", "@id")

#: ⚠ Aqui existiu um `MAX_SHARE_OUTSIDE_BY_KEY` que afrouxava o limiar para `@id` (OSM) a 35 %,
#: justificado com "as mahalles não ladrilham a região metropolitana". **A justificativa era falsa e
#: a abstração era errada** — medido 2026-08-21: das 12 850 exclusões de Istambul, **12 516 (97,4 %)
#: são lugares SEM COORDENADA na fonte**, e só **328 (0,77 % do corpus)** são lacuna geométrica real.
#: O descarte não era propriedade da fonte de geometria; era dado faltante. Separar as duas coisas
#: (abaixo) deixa o limiar único valer para todo mundo.


log = logging.getLogger("mtlcheck.substrate.regions")


def build(corpus_frame: pd.DataFrame, shapefile: str | Path, *,
          category_codes: np.ndarray | None = None, region_key: str | None = None) -> Regions:
    """Join a corpus's places onto a tract shapefile and derive the region scaffolding.

    `corpus_frame` needs `placeid`, `latitude`, `longitude`; `category_codes` is the per-check-in
    category index used for the similarity matrix, aligned with the frame's rows.

    `region_key=None` resolve a chave pelas colunas presentes (`REGION_KEY_CANDIDATES`); passe uma
    string para forçar. A chave escolhida vira `region_ids`, então trocá-la reetiqueta as regiões.
    """
    import geopandas as gpd

    tracts = gpd.read_file(shapefile)
    if region_key is None:
        found = [k for k in REGION_KEY_CANDIDATES if k in tracts.columns]
        if not found:
            raise ValueError(
                f"{shapefile} tem nenhuma das chaves de região {REGION_KEY_CANDIDATES}; "
                f"colunas: {list(tracts.columns)[:8]}. Passe region_key= para declarar qual usar.")
        region_key = found[0]
        log.info("chave de região resolvida: %s (%d feições)", region_key, len(tracts))
    if region_key not in tracts.columns:
        raise ValueError(f"{shapefile} has no {region_key} column; found {list(tracts.columns)[:8]}")
    if tracts[region_key].isna().any() or tracts[region_key].nunique() != len(tracts):
        raise ValueError(
            f"{shapefile}: a chave {region_key} não identifica as feições unicamente "
            f"({tracts[region_key].nunique()} únicos, {tracts[region_key].isna().sum()} nulos, "
            f"{len(tracts)} feições) — regiões distintas colapsariam em uma.")
    if tracts.crs is None:
        tracts = tracts.set_crs(WGS84)
    tracts = tracts.to_crs(WGS84)

    places = _place_table(corpus_frame, category_codes)

    # Lugares SEM coordenada saem antes do join, e contam à parte. Se ficassem, virariam "fora de
    # todo polígono" e inflariam a taxa de descarte com uma causa que não é geométrica — foi o que
    # aconteceu com Istambul, onde 12 516 dos 42 795 lugares não têm lat/lon **na fonte**
    # (`massive_steps_istanbul/raw/tabular`, 62 621 linhas com NaN; a ETL não perdeu nada) e faziam
    # a guarda de shapefile-trocado disparar a 30 %.
    has_coords = places["latitude"].notna() & places["longitude"].notna()
    n_uncoded = int((~has_coords).sum())
    if n_uncoded:
        log.warning("%d de %d lugares não têm coordenada na fonte e não podem receber região "
                    "(%.1f%%) — excluídos antes do join espacial",
                    n_uncoded, len(places), 100 * n_uncoded / max(len(places), 1))
        places = places.loc[has_coords].reset_index(drop=True)

    geometry = gpd.points_from_xy(places["longitude"], places["latitude"], crs=WGS84)
    located = gpd.GeoDataFrame(places, geometry=geometry, crs=WGS84)

    joined = located.sjoin(tracts[[region_key, "geometry"]], how="left", predicate="intersects")
    outside = int(joined[region_key].isna().sum())

    # ⚠ A guarda que faltava: shapefile do estado ERRADO.
    #
    # Nada validava que a geometria corresponde ao estado — nem antes, quando `--shapefile` era
    # obrigatório e digitado à mão, nem agora que ele é resolvido pelo nome. Passar Alabama com
    # `--state texas` produzia um substrato que "funciona": os lugares que caem fora são descartados
    # e o build segue, com um aviso que ninguém lê num log de 500 épocas.
    #
    # A assinatura é inconfundível — em AL e AZ o descarte medido é ZERO, e um shapefile trocado
    # descarta quase tudo. Então isto recusa em vez de avisar. O limiar é frouxo de propósito: não é
    # para pegar geometria imperfeita, é para pegar geometria de outro lugar.
    share_outside = outside / max(len(located), 1)
    if share_outside > MAX_SHARE_OUTSIDE:
        raise ValueError(
            f"{share_outside:.1%} dos {len(located)} lugares caem fora de todo polígono de "
            f"{shapefile}, acima do limite de {MAX_SHARE_OUTSIDE:.0%}. Isso é a assinatura de um "
            f"shapefile de OUTRO estado (lugares sem coordenada já saíram antes). Confira se a "
            f"geometria corresponde ao "
            f"estado que está construindo; `--shapefile` é resolvido pelo nome do estado quando "
            f"omitido.")

    joined = joined.dropna(subset=[region_key])

    duplicated = int(joined["placeid"].duplicated().sum())
    if duplicated:
        # See docstring note 4: the reference keeps the last and counts both, so its place count and
        # its mapping disagree. Keep the first, say how many, and move on.
        logger.warning("%d places intersect more than one tract; keeping the first match", duplicated)
        joined = joined.drop_duplicates(subset="placeid", keep="first")

    joined = joined.reset_index(drop=True)
    region_ids = tuple(joined[region_key].unique())          # first appearance, not sorted
    region_to_index = {value: i for i, value in enumerate(region_ids)}

    place_to_index = {int(pid): i for i, pid in enumerate(joined["placeid"])}
    poi_to_region = joined[region_key].map(region_to_index).to_numpy(dtype=np.int64)

    area = _areas(tracts, region_key, region_ids)
    adjacency = _adjacency(tracts, region_key, region_to_index)
    similarity = _similarity(poi_to_region, joined["category_code"].to_numpy(), len(region_ids))

    logger.info("spatial join: %d places over %d regions (%d places outside every tract) · "
                "%d adjacency edges", len(place_to_index), len(region_ids), outside,
                adjacency.shape[1])
    return Regions(place_to_index=place_to_index, poi_to_region=poi_to_region, region_area=area,
                   region_adjacency=adjacency, region_similarity=similarity, region_ids=region_ids,
                   dropped_places=outside)


def _place_table(frame: pd.DataFrame, category_codes: np.ndarray | None) -> pd.DataFrame:
    """One row per place, taking the FIRST check-in's coordinates (docstring note 3)."""
    columns = {"placeid": frame["placeid"].to_numpy(),
               "latitude": frame["latitude"].to_numpy(),
               "longitude": frame["longitude"].to_numpy()}
    columns["category_code"] = (np.asarray(category_codes) if category_codes is not None
                                else np.zeros(len(frame), dtype=np.int64))
    return pd.DataFrame(columns).groupby("placeid", as_index=False, sort=True).first()


def _areas(tracts, region_key: str, region_ids: tuple[str, ...]) -> np.ndarray:
    """Tract areas, in the CRS's own units. Degrees squared — see the module docstring."""
    by_id = tracts.drop_duplicates(subset=region_key).set_index(region_key)
    area = np.zeros(len(region_ids), dtype=np.float32)
    for index, value in enumerate(region_ids):
        if value in by_id.index:
            area[index] = float(by_id.loc[value, "geometry"].area)
    return area


def _adjacency(tracts, region_key: str, region_to_index: dict) -> np.ndarray:
    """Regions that touch, as a [2, E] edge index.

    A self-join on `intersects`, minus the self-pairs — which is what the reference does, and which
    yields both directions of every edge (the region GCN wants that).
    """
    import geopandas as gpd

    present = tracts[tracts[region_key].isin(region_to_index)].drop_duplicates(subset=region_key)
    present = present.copy()
    present["idx"] = present[region_key].map(region_to_index)

    joined = gpd.sjoin(present[["idx", "geometry"]], present[["idx", "geometry"]],
                       how="inner", predicate="intersects")
    edges = joined[joined["idx_left"] != joined["idx_right"]]
    if edges.empty:
        return np.zeros((2, 0), dtype=np.int64)
    return np.vstack([edges["idx_left"].to_numpy(dtype=np.int64),
                      edges["idx_right"].to_numpy(dtype=np.int64)])


def _similarity(poi_to_region: np.ndarray, category_codes: np.ndarray,
                num_regions: int) -> np.ndarray:
    """Cosine similarity between regions over their place-category distributions.

    This is what the hard-negative sampler bands on, so its scale matters: a region with no places
    has a zero row and a zero similarity to everything, which correctly makes it unreachable as a
    hard negative rather than a spuriously similar one.
    """
    num_categories = int(category_codes.max()) + 1 if len(category_codes) else 1
    counts = np.zeros((num_regions, num_categories), dtype=np.float64)
    np.add.at(counts, (poi_to_region, category_codes.astype(np.int64)), 1.0)

    totals = counts.sum(axis=1, keepdims=True)
    distribution = counts / np.where(totals == 0, 1.0, totals)
    norms = np.linalg.norm(distribution, axis=1, keepdims=True)
    normalised = distribution / np.where(norms == 0, 1.0, norms)
    return (normalised @ normalised.T).astype(np.float32)


__all__ = ["Regions", "build", "WGS84"]
