# Pipelines

Standard structure for all pipeline files. Every non-deprecated pipeline follows this layout.

## File Structure

```python
"""One-line description. Usage: python pipelines/embedding/X.pipe.py"""

# imports...
# logger...

# === SETTINGS ===
MAX_WORKERS = 1  # How many states to process in parallel

# === CONFIG ===
CONFIG = Namespace(
    dim=64,
    lr=0.006,
    ...
)

# Create alternative configs for experiments:
# CONFIG_FAST = Namespace(dim=32, lr=0.01, epoch=50, ...)

# === STATES ===
# Ordered dict — execution follows insertion order, MAX_WORKERS at a time.
STATES = {
    'Alabama': {'shapefile': Resources.TL_AL},
    'Arizona': {'shapefile': Resources.TL_AZ, 'config': CONFIG_FAST},
    # 'Texas':  {'shapefile': Resources.TL_TX, 'lr': 0.01},  # per-state override
}

# === PIPELINE ===
def process_state(name, state_cfg) -> bool: ...
def run_pipeline() -> dict: ...

if __name__ == '__main__': ...
```

## Key Concepts

### Multiple Configs

You can define multiple configs in the same file and assign each state to one:

```python
CONFIG = Namespace(dim=64, epoch=2000, lr=0.006)
CONFIG_FAST = Namespace(dim=32, epoch=500, lr=0.01)

STATES = {
    'Alabama': {'shapefile': Resources.TL_AL, 'config': CONFIG},
    'Arizona': {'shapefile': Resources.TL_AZ, 'config': CONFIG_FAST},
}
```

When `'config'` is omitted, the first config (`CONFIG`) is used as default.

### Per-State Overrides

Any key in the state dict (other than `'config'` and `'shapefile'`) is applied as an override on top of the selected config:

```python
STATES = {
    'Alabama': {'shapefile': Resources.TL_AL, 'cross_region_weight': 0.7},
    'Florida': {'shapefile': Resources.TL_FL, 'cross_region_weight': 0.6, 'epoch': 3000},
}
```

### Ordered Parallel Execution

`MAX_WORKERS` controls how many states run in parallel. Execution follows map insertion order in chunks:

- `MAX_WORKERS = 1`: sequential, one state at a time
- `MAX_WORKERS = 2` with `{Alabama, Texas, Florida, California}`: runs Alabama+Texas, then Florida+California

### Config Resolution in process_state

```python
def process_state(name: str, state_cfg: dict) -> bool:
    state_cfg = dict(state_cfg)               # shallow copy to avoid mutation
    base = state_cfg.pop('config', CONFIG)     # select base config
    config = copy(base)                        # deep copy base
    shapefile = state_cfg.pop('shapefile', None)  # extract non-config keys
    for k, v in state_cfg.items():             # apply overrides
        setattr(config, k, v)
```

## Pipeline Types

| Directory | Purpose | Has shapefile? |
|-----------|---------|---------------|
| `embedding/` | Train embeddings + generate inputs | Some (hgi, dgi, check2hgi, poi2hgi) |
| `create_inputs.pipe.py` | Generate inputs from existing embeddings | No |
| `fusion.pipe.py` | Generate fused multi-embedding inputs | No |
| `train/` | **Deprecated** — use `scripts/train.py` directly | N/A |
