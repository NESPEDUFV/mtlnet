# Baselines

Self-contained external-baseline implementations for the next-region task.
Each baseline owns its own ETL, model, and training entrypoint and does not
depend on the in-house substrate (HGI / Check2HGI) or on `src/data/inputs/*`.

## Layout

```
research/baselines/
└── stan/                # Faithful STAN (Luo et al., WWW 2021)
    ├── etl.py           # Builds windowed inputs from raw data/checkins/
    ├── model.py         # FaithfulSTAN head with ΔT/ΔD pairwise bias
    └── train.py         # Single-task next-region 5-fold CV trainer
```

Each baseline writes its inputs to `output/baselines/<name>/<state>/`
and its result JSONs to `docs/results/baselines/`.
