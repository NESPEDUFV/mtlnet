"""Every filesystem location, in one place.

The three environment variables read here are the ONLY ones this project honours, and none of
them can change a number: they say *where* things live, never *what* is computed. Everything
scientific goes through ``config.py``.

Rationale — the old repository routed ~25 environment variables into scientific decisions
(precision, per-head LR activation, metric device, prior activation). One of them leaked out of a
shell function and silently ran 8 of 10 category cells in fp16 while their provenance files claimed
fp32. See ``docs/SYSTEM_MAP.md §5``.
"""

from __future__ import annotations

import os
from pathlib import Path

# The old repo's layout, which we read from (raw corpora) and compare against (reference artifacts).
_DEFAULT_DATA = "data"
_DEFAULT_ARTIFACTS = "artifacts"
_DEFAULT_RUNS = "runs"


def _root(env: str, default: str) -> Path:
    """Resolve a root directory from the environment, falling back to a repo-relative default."""
    value = os.environ.get(env)
    return Path(value).expanduser().resolve() if value else (repo_root() / default)


def repo_root() -> Path:
    """The mtlcheck project root (the directory holding pyproject.toml)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError(f"no pyproject.toml above {here}")


def data_root() -> Path:
    """Raw corpora. `DATA_ROOT`."""
    return _root("DATA_ROOT", _DEFAULT_DATA)


def artifacts_root() -> Path:
    """Substrate artifacts — bulk, gitignored except the manifests. `ARTIFACTS_ROOT`.

    On the A40 this must point at /dados: /home is 90% full and the v18 substrate alone is 44 GB.
    """
    return _root("ARTIFACTS_ROOT", _DEFAULT_ARTIFACTS)


def runs_root() -> Path:
    """Per-run training outputs — bulk, gitignored. `RUNS_ROOT`."""
    return _root("RUNS_ROOT", _DEFAULT_RUNS)


# ---------------------------------------------------------------- raw corpus

def state_checkins(state: str) -> Path:
    """The raw per-state check-in parquet.

    The corpus files are title-cased (`Alabama.parquet`); every other identifier in this project is
    lowercase. The mapping lives here so no caller has to remember it.
    """
    return data_root() / "checkins" / f"{_corpus_name(state)}.parquet"


#: state -> (subdiretório, arquivo) sob `data/miscellaneous`, e o código FIPS quando existe.
#:
#: Existe porque a sua ausência era a única fricção real de quem chega ao sistema: para rodar o
#: Texas era preciso saber que o FIPS é 48 e que o arquivo é `tl_2022_48_tract_TX/tl_2022_48_tract`
#: — nada no código nem no `--help` revelava isso, e Istambul foge da convenção inteira.
#:
#: As duas convenções são deliberadas e não se unificam: os estados americanos vêm do TIGER/Line do
#: Census (shapefile por tract) e Istambul vem de um recorte de mahalle em GeoJSON, de outra fonte.
SHAPEFILES: dict[str, tuple[str, str]] = {
    "alabama":    ("tl_2022_01_tract_AL", "tl_2022_01_tract.shp"),
    "arizona":    ("tl_2022_04_tract_AZ", "tl_2022_04_tract.shp"),
    "california": ("tl_2022_06_tract_CA", "tl_2022_06_tract.shp"),
    "florida":    ("tl_2022_12_tract_FL", "tl_2022_12_tract.shp"),
    "texas":      ("tl_2022_48_tract_TX", "tl_2022_48_tract.shp"),
    "istanbul":   ("istanbul_mahalle", "istanbul_mahalle.geojson"),
}

#: De onde os TIGER/Line vêm, para o `mtlcheck data fetch`. Istambul não está aqui de propósito:
#: não tenho uma URL oficial estável para o recorte de mahalle, e inventar uma seria pior que a
#: ausência — o erro abaixo diz isso em vez de tentar adivinhar.
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2022/TRACT/{stem}.zip"


def state_shapefile(state: str) -> Path:
    """O shapefile de um estado, resolvido pelo nome em vez de digitado à mão.

    Levanta com a instrução exata quando falta, em vez de deixar o `geopandas` falhar lá dentro com
    um erro que não diz o que fazer.
    """
    try:
        directory, name = SHAPEFILES[state]
    except KeyError:
        raise ValueError(f"não há shapefile mapeado para {state!r}; conhecidos: "
                         f"{sorted(SHAPEFILES)}") from None
    path = data_root() / "miscellaneous" / directory / name
    if not path.exists():
        hint = (f"baixe com `mtlcheck data fetch --state {state}`"
                if state != "istanbul" else
                "Istambul vem de um recorte de mahalle em GeoJSON que não tem URL oficial "
                "estável; copie o arquivo para o caminho acima")
        raise FileNotFoundError(f"shapefile de {state} não encontrado em {path} — {hint}")
    return path


def _corpus_name(state: str) -> str:
    # Istanbul is not a US state and comes from a different source, but it lands in the same
    # place with the same convention.
    return state.strip().lower().title()


# ---------------------------------------------------------------- substrate artifacts

def substrate_dir(engine: str, state: str) -> Path:
    """Where one (engine, state) substrate lives."""
    return artifacts_root() / "substrate" / engine / state.lower()


def substrate_manifest(engine: str, state: str) -> Path:
    """The committed contract for a substrate — see ``docs/ARCHITECTURE.md §1.1``.

    This is the ONLY file under artifacts/ that git tracks. It carries engine identity, content
    hashes, the placeid/region maps' provenance, the row-space origin (source engine, window,
    stride, MIN_SEQ), n_regions and its derivation rule, and the edge counts E10 validates against.
    """
    return substrate_dir(engine, state) / "manifest.json"


# ---------------------------------------------------------------- runs

def run_dir(study: str, cell_id: str) -> Path:
    """One training cell's output directory. See `cell_id` for the naming rule."""
    return runs_root() / study / cell_id


def cell_id(family: str, state: str, model_seed: int, split_seed: int) -> str:
    """`{family}-{state}-p{split_seed}s{model_seed}` — BOTH seeds, per protocol §10.5.

    It used to be `-s{seed}` alone. That made the protocol's own §10.4 decomposition
    (`split_seed ∈ {0,7} × model_seed ∈ {0,7}`) unrunnable: two of its four cells collide on one
    directory, and the second either is skipped as already-done or overwrites the first. A
    directory name that cannot express the design is the confound's signature at the filesystem
    level, which is exactly where §10.5 says it must not survive.
    """
    return f"{family}-{state.lower()}-p{split_seed}s{model_seed}"


__all__ = [
    "repo_root", "data_root", "artifacts_root", "runs_root",
    "state_checkins", "substrate_dir", "substrate_manifest", "run_dir", "cell_id",
]
