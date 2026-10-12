"""An index of what has been run, so "did we already do this?" is a query.

A sweep asks that question hundreds of times. Without an index the answers are a filesystem walk and
a memory, and this project has already shown what memory is worth: three separate claims about its
own work turned out to be wrong in ways only a file could have caught.

Deliberately a flat JSONL append. One line per cell, no database, no schema migration — a sweep that
crashes half way leaves a readable file, and `grep` is a legitimate query engine at this size.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterator

logger = logging.getLogger(__name__)

INDEX_NAME = "index.jsonl"


def record(runs_root: Path, study: str, resolved, aggregate: dict, *,
           run_dir: Path, wall_seconds: float, arm: str = "", eval_stream: str = "outer_fold") -> None:
    """Append one cell to the study's index. Never raises — indexing must not lose a result."""
    cfg = resolved.train
    split_seed = (resolved.data.split_seed if resolved.data.split_seed is not None else cfg.seed)
    entry: dict[str, Any] = {
        "study": study,
        "cell_id": resolved.cell_id,
        "arm": arm,
        "family": cfg.family.value,
        "state": cfg.state,
        "model_seed": cfg.seed,
        "split_seed": split_seed,
        "engine": cfg.engine,
        "epochs": cfg.epochs,
        "fingerprint": resolved.fingerprint(),
        "run_dir": str(run_dir),
        "wall_seconds": round(wall_seconds, 1),
    }
    # OUTSIDE the `if aggregate` block on purpose. The joint family banks no aggregate — it has two
    # metrics — so keying the seal off the metric block left the index blind for exactly the family
    # whose seal was the bug.
    entry["eval_stream"] = aggregate.get("eval_stream", eval_stream)
    if aggregate:
        entry |= {"metric": aggregate.get("metric"), "lane": aggregate.get("lane"),
                  "mean": aggregate.get("mean"), "n_folds": aggregate.get("n_folds")}
    try:
        path = Path(runs_root) / study / INDEX_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
    except Exception as exc:                      # an index is a convenience; a result is not
        logger.warning("could not append to the run index: %s", exc)


def read(runs_root: Path, study: str) -> Iterator[dict]:
    path = Path(runs_root) / study / INDEX_NAME
    if not path.exists():
        return iter(())
    def rows():
        for line in path.read_text().splitlines():
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("skipping an unreadable index line in %s", path)
    return rows()


def find(runs_root: Path, study: str, **filters) -> list[dict]:
    """Cells matching every filter. `find(root, s, state="alabama", family="cat")`."""
    return [row for row in read(runs_root, study)
            if all(row.get(k) == v for k, v in filters.items())]


def latest_by_cell(runs_root: Path, study: str) -> dict[str, dict]:
    """The most recent entry per (cell_id, arm) — a cell re-run appends rather than replacing."""
    out: dict[str, dict] = {}
    for row in read(runs_root, study):
        out[f"{row.get('cell_id')}::{row.get('arm', '')}"] = row
    return out


__all__ = ["record", "read", "find", "latest_by_cell", "INDEX_NAME"]
