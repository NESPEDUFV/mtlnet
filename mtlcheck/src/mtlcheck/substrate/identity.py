"""Which substrate produced a number — recorded on the cell, not inferred from an env var.

## Why this module exists

Until 2026-08-19 a banked cell said nothing about the substrate it read. The substrate is selected by
`ARTIFACTS_ROOT`, an environment variable, and two cells trained on genuinely different substrates
carried **identical** fingerprints:

    runs/tri_v18region/reg-alabama-p0s0   substrate repr_seed 42
    runs/rs0_v18region/reg-alabama-p0s0   substrate repr_seed 0
    both: config_fingerprint ff3aa005b78a7c3f, science_fingerprint fd0ecf9f49c0f6e6

That is not only a provenance hole. `wave` skips a cell whose recorded fingerprint still matches, so
rebuilding a substrate and re-running a wave **skips every cell and reports the old substrate's
numbers as current** — the exact failure the wave docstring says it prevents ("editing a recipe
invalidates the cells it touches instead of silently keeping their stale results"), one level down.
It went unnoticed only because each measurement happened to use a distinct `--study` name.

## What the identity is, and what it deliberately excludes

A canonical digest over the parts of the substrate manifest that decide what the artifacts CONTAIN:

* `recipe` — every knob the build was run with, `repr_seed` included;
* `graph` — direction, node and edge counts;
* `counts` and `features` — the shape of what came out;
* `inputs.digests` — the sha256 of the Delaunay places, Delaunay edges and POI2Vec code book that
  fed it, which is what caught the 2,3 % edge-orientation divergence;
* `training.seed`, `training.init_fingerprint`, `training.n_params`, `training.best_loss` — the run
  itself. `best_loss` is load-bearing: R16 says this build is not reproducible even against itself,
  so two builds with an identical recipe still differ here, and the identity has to notice.

**Excluded on purpose:** absolute paths (`inputs.corpus`, `inputs.hierarchy`) and wall-clock timings.
Both differ between machines for the same substrate, and an identity that changed when a study moved
from the laptop to the A40 would invalidate correct cells — the opposite of the point.

## What it is NOT

It is not a digest of the embedding files themselves. That would be stronger and costs a full read of
a 300 MB parquet per cell. The manifest route is the cheap proxy and it is sound *because* the manifest
carries `best_loss` and the input digests: a substrate whose bytes differ has a different loss curve.
If a future defect ever produces identical manifests over different artifacts, this proxy misses it —
so the trade is stated here rather than discovered later.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

#: The manifest subtrees that decide what the artifacts contain. Order is fixed; the digest is over
#: a canonical JSON dump, so adding a key to an EXCLUDED subtree cannot rotate it.
_IDENTITY_KEYS = ("recipe", "graph", "counts", "features")
_TRAINING_KEYS = ("seed", "init_fingerprint", "n_params", "best_loss")


def digest(manifest: dict[str, Any]) -> str:
    """The substrate identity, 16 hex chars, from a loaded manifest.

    Recusa um dicionário sem nenhuma das chaves de identidade. Sem essa guarda o mau uso é
    **silencioso e constante**: passar o resumo de `of()` (que tem só `engine`/`state`/`identity`)
    faz todas as chaves virarem `None`, e o hash resultante é o MESMO para qualquer entrada — um
    fingerprint plausível que nunca muda, num módulo que existe para detectar mudança. Aconteceu
    2026-08-21 ao extrair fingerprints para a campanha, e Alabama e Arizona saíram idênticos.
    """
    present = [k for k in _IDENTITY_KEYS if manifest.get(k) is not None]
    if not present:
        raise ValueError(
            f"manifesto sem nenhuma chave de identidade {_IDENTITY_KEYS}; chaves recebidas: "
            f"{sorted(manifest)[:8]}. Passe o manifest.json carregado, não o resumo de `of()` "
            f"— o hash de um dicionário sem essas chaves é constante e não identifica nada.")
    payload: dict[str, Any] = {k: manifest.get(k) for k in _IDENTITY_KEYS}
    training = manifest.get("training", {}) or {}
    payload["training"] = {k: training.get(k) for k in _TRAINING_KEYS}
    payload["digests"] = (manifest.get("inputs", {}) or {}).get("digests")
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def of(directory: Path) -> dict[str, Any] | None:
    """`{engine, state, identity}` for a substrate directory, or None when it has no manifest.

    None rather than an exception: the OLD canonical engine's directories were not written by this
    package and have no manifest, and a cell reading one is a legitimate (if undesirable) state that
    the caller should record as "unknown" rather than crash on.
    """
    path = Path(directory) / "manifest.json"
    if not path.exists():
        logger.warning("substrate at %s has no manifest.json — its identity cannot be recorded, so "
                       "a resume cannot tell whether it changed", directory)
        return None
    manifest = json.loads(path.read_text())
    return {"engine": manifest.get("engine"), "state": manifest.get("state"),
            "identity": digest(manifest)}


__all__ = ["digest", "of"]
