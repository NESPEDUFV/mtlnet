"""mtlcheck — the v18 multi-task POI system, rebuilt.

Three layers, coupled only by files on disk:

    substrate/   check-in graph -> per-visit embeddings          (CLI: mtlcheck check2hgi)
    data/        substrate + check-ins -> tensors + folds
    train/       tensors -> metrics                              (CLI: mtlcheck train)

`train` never imports `substrate`. See docs/ARCHITECTURE.md.
"""

__version__ = "0.1.0"
