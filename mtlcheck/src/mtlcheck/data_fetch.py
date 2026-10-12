"""Baixar os dados primários — e dizer com honestidade o que não dá para baixar.

## O que este módulo cobre

| fonte | comando | procedência |
|---|---|---|
| geometrias TIGER/Line (5 estados US) | `mtlcheck data fetch --state florida` | Census, URL oficial |
| Massive-STEPS (15 cidades) | `mtlcheck data fetch --city Jakarta` | HuggingFace, Apache-2.0 |
| Gowalla bruto | `mtlcheck data fetch --gowalla` | Stanford SNAP |
| o que falta, sem baixar nada | `mtlcheck data check` | — |

## O que ele deliberadamente NÃO faz

**Não reconstrói `data/checkins/<Estado>.parquet`.** Esses parquets são um recorte DESTE projeto sobre
o Gowalla bruto — filtro geográfico, mapeamento de categorias, normalização de ids. Baixar o SNAP dá
a matéria-prima, não o produto. Um fetcher que fingisse reconstruí-los produziria um arquivo com o
nome certo e o conteúdo errado, que é a pior falha possível aqui.

**Não baixa o recorte de mahalle de Istambul.** É um GeoJSON de bairros sem URL oficial estável.
Inventar uma seria pior que a ausência; o `check` diz onde ele tem de estar.

Toda URL abaixo foi verificada, nenhuma foi adivinhada.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from . import paths

logger = logging.getLogger(__name__)

#: TIGER/Line 2022, tract por estado. Oficial e estável.
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2022/TRACT/{stem}.zip"

#: Gowalla bruto. O que os parquets por estado foram construídos A PARTIR de — não o que eles são.
GOWALLA_CHECKINS = "https://snap.stanford.edu/data/loc-gowalla_totalCheckins.txt.gz"
GOWALLA_EDGES = "https://snap.stanford.edu/data/loc-gowalla_edges.txt.gz"

#: Massive-STEPS, uma dataset do HuggingFace por cidade. Apache-2.0.
#: Contagens conferidas no repositório em 2026-08-21; Istambul bate com o corpus local (544 471).
MASSIVE_STEPS_REPO = "CRUISEResearchGroup/Massive-STEPS-{city}"
MASSIVE_STEPS_CITIES = {
    "Istanbul": 544_471, "PetalingJaya": 506_430, "Jakarta": 412_100, "NewYork": 272_368,
    "SaoPaulo": 256_824, "KuwaitCity": 232_706, "Bandung": 161_284, "Moscow": 105_620,
    "Tangerang": 45_521, "Sydney": 29_900, "Melbourne": 22_050, "Palembang": 14_467,
    "Tokyo": 13_839, "Shanghai": 10_491, "Beijing": 1_470,
}


def _download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    logger.info("baixando %s", url)
    with tempfile.NamedTemporaryFile(delete=False, dir=target.parent) as tmp:
        with urllib.request.urlopen(url) as response:
            shutil.copyfileobj(response, tmp)
    Path(tmp.name).replace(target)          # atômico: um download interrompido não deixa meio arquivo
    logger.info("-> %s (%.1f MB)", target, target.stat().st_size / 2**20)


def fetch_shapefile(state: str, *, force: bool = False) -> Path:
    """A geometria de um estado, do Census."""
    directory, name = paths.SHAPEFILES[state]
    target = paths.data_root() / "miscellaneous" / directory
    if (target / name).exists() and not force:
        logger.info("%s: já em disco", state)
        return target / name
    if not name.endswith(".shp"):
        raise SystemExit(
            f"{state} não vem do TIGER/Line e não tem download automático. O recorte de mahalle de "
            f"Istambul é um GeoJSON sem URL oficial estável; coloque-o em {target / name}.")
    stem = name[:-4]
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / f"{stem}.zip"
        _download(TIGER_URL.format(stem=stem), archive)
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target)
    if not (target / name).exists():
        raise SystemExit(f"o zip não continha {name}; extraído em {target}")
    return target / name


def fetch_gowalla(*, force: bool = False) -> list[Path]:
    """O Gowalla BRUTO do SNAP — a matéria-prima, não os parquets por estado."""
    out = paths.data_root() / "gowalla" / "snap_raw"
    written = []
    for url in (GOWALLA_CHECKINS, GOWALLA_EDGES):
        target = out / url.rsplit("/", 1)[-1]
        if target.exists() and not force:
            logger.info("%s: já em disco", target.name)
        else:
            _download(url, target)
        written.append(target)
    logger.warning(
        "Gowalla bruto baixado em %s. ISTO NÃO É `data/checkins/<Estado>.parquet` — aqueles são um "
        "recorte deste projeto (filtro geográfico, mapa de categorias, normalização de ids) e não "
        "são reconstruídos por este comando.", out)
    return written


def fetch_city(city: str, *, force: bool = False) -> Path:
    """Uma cidade do Massive-STEPS, do HuggingFace."""
    if city not in MASSIVE_STEPS_CITIES:
        raise SystemExit(f"cidade desconhecida {city!r}; conhecidas: "
                         f"{', '.join(sorted(MASSIVE_STEPS_CITIES))}")
    target = paths.data_root() / f"massive_steps_{city.lower()}"
    if target.exists() and not force:
        logger.info("%s: já em disco (%s)", city, target)
        return target
    try:
        from datasets import load_dataset
    except ImportError:
        raise SystemExit(
            f"o Massive-STEPS vem do HuggingFace e precisa do pacote `datasets`:\n"
            f"    pip install datasets\n"
            f"    # depois: mtlcheck data fetch --city {city}\n"
            f"Ou baixe à mão de https://huggingface.co/datasets/"
            f"{MASSIVE_STEPS_REPO.format(city=city)} para {target}") from None
    logger.info("%s: %d check-ins esperados", city, MASSIVE_STEPS_CITIES[city])
    dataset = load_dataset(MASSIVE_STEPS_REPO.format(city=city))
    target.mkdir(parents=True, exist_ok=True)
    dataset.save_to_disk(str(target / "raw"))
    logger.warning("%s baixado em %s. Ainda precisa do recorte deste projeto para virar "
                   "`data/checkins/%s.parquet`.", city, target, city)
    return target


def check(states: list[str] | None = None) -> list[str]:
    """O que falta para construir, sem baixar nada. Lista tudo em vez de falhar no primeiro."""
    from . import config as cfg

    missing: list[str] = []
    for state in states or list(cfg.DATASETS):
        corpus = paths.state_checkins(state)
        if not corpus.exists():
            missing.append(
                f"corpus de {state}: {corpus} AUSENTE\n"
                f"    ← recorte deste projeto sobre o Gowalla bruto ({GOWALLA_CHECKINS}); "
                f"`data fetch --gowalla` traz a matéria-prima, não o recorte")
        try:
            paths.state_shapefile(state)
        except FileNotFoundError as exc:
            missing.append(str(exc))
    return missing


__all__ = ["fetch_shapefile", "fetch_gowalla", "fetch_city", "check",
           "TIGER_URL", "GOWALLA_CHECKINS", "MASSIVE_STEPS_CITIES"]
