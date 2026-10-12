# Concrete Execution Plan — per-state `w_r` sweep (AZ, TX, CA, FL)

Status: ready-to-execute
Written: 2026-04-12
Prereqs: PR #13 merged (confirmed)

---

## 0. Source-file audit (findings before writing this plan)

### `pipelines/embedding/hgi.pipe.py`
- **No CLI flags.** The pipeline is configured by editing the `STATES` dict and `CONFIG` Namespace at the top of the file.
- Per-state `cross_region_weight` is passed inline in the `STATES` dict:
  ```python
  STATES = {
      'Alabama': {'shapefile': Resources.TL_AL, 'cross_region_weight': 0.7},
  }
  ```
- The README §5 references a `CROSS_REGION_WEIGHT_PER_STATE` top-level dict — this refactor has NOT landed. The actual mechanism is the `STATES` dict entry.
- **`force_preprocess=True` is baked into `CONFIG`** — the pipeline overwrites `output/hgi/<state>/` unconditionally. Per the README Smoke Testing Hazard section, you MUST snapshot existing artifacts before each sweep run.

### `scripts/train.py`
- `--folds N`: Run only the first N folds. The split structure uses `max(2, N)` splits.
- `--epochs N`: Override epoch count.
- Fast-protocol invocation: `python scripts/train.py --task mtl --state <state> --engine hgi --folds 2 --epochs 15`

### Existing state of the repo
- All 5 states have current HGI embeddings at `output/hgi/<state>/embeddings.parquet` and model inputs at `output/hgi/<state>/input/{category,next}.parquet`.
- Data prerequisites confirmed present: checkins parquets for all 5 states, shapefiles for all 5 states.
- `results_save/` does not yet exist — create it on first snapshot.
- Python env: `.venv` at repo root (Python 3.12 + torch).

### Metric output location
After `scripts/train.py` completes, the summary JSON is at:
```
results/hgi/<state>/mtlnet_lr*/summary/full_summary.json
```
The `full_summary.json` contains `category.f1.mean` and `category.f1.std` — these are the Cat F1 values.

---

## 1. Environment setup (once)

```bash
cd "/Volumes/Vitor's SSD/ingred"
export PYTHONPATH="src:research"
export HGI_NUM_THREADS=4    # for concurrent pair runs (AZ+TX, CA+FL)
VENV=".venv/bin/python"

# Create results_save directory
mkdir -p results_save
```

---

## 2. Helper functions (paste into shell or save as sweep_helpers.sh)

```bash
# Snapshot current HGI output for a state before overwriting
snapshot_hgi() {
    local state="$1"     # e.g. "alabama"
    local label="$2"     # e.g. "wr04"
    local ts=$(date +%Y%m%d_%H%M%S)
    local src="output/hgi/${state}"
    local dst="results_save/${state}_${label}_${ts}"
    echo "[snapshot] $src -> $dst"
    cp -a "$src" "$dst"
}

# Extract Cat F1 mean and std from the most recent MTL run summary
get_cat_f1() {
    local state="$1"   # e.g. "alabama"
    local dir=$(ls -td "results/hgi/${state}/mtlnet_"* 2>/dev/null | head -1)
    if [ -z "$dir" ]; then echo "NO_RESULT"; return; fi
    python3 -c "
import json, sys
with open('${dir}/summary/full_summary.json') as f:
    d = json.load(f)
mean = d['category']['f1']['mean']
std  = d['category']['f1']['std']
print(f'Cat F1: {mean:.4f} +/- {std:.4f}')
"
}

# Run one HGI embedding sweep point: edit STATES in hgi.pipe.py temporarily
# Usage: run_hgi_sweep <StateName> <wr_float>
# e.g.: run_hgi_sweep Alabama 0.4
run_hgi_sweep() {
    local name="$1"
    local wr="$2"
    echo "[hgi] Running $name w_r=$wr"
    $VENV - <<PYEOF
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'research')
import pickle as pkl, logging, torch
from copy import copy
from argparse import Namespace
from configs.paths import Resources, EmbeddingEngine, IoPaths
from configs.model import InputsConfig
from embeddings.hgi.hgi import train_hgi
from embeddings.hgi.preprocess import preprocess_hgi
from embeddings.hgi.poi2vec import train_poi2vec
from data.inputs.builders import generate_category_input, generate_next_input_from_poi

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

STATE_SHAPEFILES = {
    'Alabama':    Resources.TL_AL,
    'Arizona':    Resources.TL_AZ,
    'Texas':      Resources.TL_TX,
    'California': Resources.TL_CA,
    'Florida':    Resources.TL_FL,
}

name = '$name'
wr   = $wr

config = Namespace(
    dim=InputsConfig.EMBEDDING_DIM, alpha=0.5, attention_head=4,
    lr=0.006, gamma=1.0, max_norm=0.9, epoch=2000, warmup_period=40,
    poi2vec_epochs=100, force_preprocess=True,
    cross_region_weight=wr,
    device='cpu',
    shapefile=str(STATE_SHAPEFILES[name]),
)

# Stage 1: Delaunay graph
preprocess_hgi(city=name, city_shapefile=str(config.shapefile),
               poi_emb_path=None, cta_file=None, cross_region_weight=wr)

# Stage 2: POI2Vec
poi_emb_path = train_poi2vec(city=name, epochs=config.poi2vec_epochs,
                             embedding_dim=config.dim,
                             device='cuda' if torch.cuda.is_available() else 'cpu')

# Stage 3: Preprocess with embeddings
data = preprocess_hgi(city=name, city_shapefile=str(config.shapefile),
                      poi_emb_path=str(poi_emb_path), cta_file=None,
                      cross_region_weight=wr)
graph_data_file = IoPaths.HGI.get_graph_data_file(name)
graph_data_file.parent.mkdir(parents=True, exist_ok=True)
with open(graph_data_file, 'wb') as f:
    pkl.dump(data, f)

# Stage 4: Train HGI
train_hgi(name, config)

# Stage 5: Generate inputs
generate_category_input(name, EmbeddingEngine.HGI)
generate_next_input_from_poi(name, EmbeddingEngine.HGI)

print(f'[hgi] DONE: {name} w_r={wr}')
PYEOF
}
```

---

## 3. Calibration (Alabama go/no-go gate)

The existing Alabama run (5f×50e, w_r=0.7) gives Cat F1 ≈ 0.8186 ± 0.0123. The 2f×15e fast protocol produces lower values — the calibration determines whether the *rank order* is preserved and differences are statistically meaningful.

### Step C1: Alabama w_r=0.4 at 2f×15e

```bash
# Snapshot existing Alabama HGI artifacts
snapshot_hgi alabama before_calib_wr04

# Run HGI with w_r=0.4
run_hgi_sweep Alabama 0.4

# Snapshot the w_r=0.4 artifacts
snapshot_hgi alabama calib_wr04

# Run MTLnet 2 folds × 15 epochs
$VENV scripts/train.py --task mtl --state alabama --engine hgi --folds 2 --epochs 15

# Record result
get_cat_f1 alabama
# -> RECORD as AL_04_F1 and AL_04_STD
```

### Step C2: Alabama w_r=0.7 at 2f×15e

```bash
# Snapshot current Alabama output (w_r=0.4 artifacts)
snapshot_hgi alabama calib_wr04_before_wr07

# Run HGI with w_r=0.7
run_hgi_sweep Alabama 0.7

# Snapshot w_r=0.7 artifacts
snapshot_hgi alabama calib_wr07

# Run MTLnet 2 folds × 15 epochs
$VENV scripts/train.py --task mtl --state alabama --engine hgi --folds 2 --epochs 15

# Record result
get_cat_f1 alabama
# -> RECORD as AL_07_F1 and AL_07_STD
```

### Step C3: Calibration pass/fail check

```bash
python3 -c "
AL_04_F1  = <fill>; AL_04_STD  = <fill>
AL_07_F1  = <fill>; AL_07_STD  = <fill>
diff      = AL_07_F1 - AL_04_F1
threshold = 2 * AL_04_STD
print(f'diff={diff:.4f}  threshold(2σ_04)={threshold:.4f}')
if diff >= threshold:
    print('PASS: rank order confirmed, proceed with 2f15e protocol')
else:
    print('FAIL: signal too noisy — switch to 3f25e protocol')
    print('  Re-run all sweep points with: --folds 3 --epochs 25')
"
```

**Expected outcome**: PASS (based on Alabama's strong w_r sensitivity: +0.08 F1 per 0.3 step with σ≈0.012 at 5f×50e, the signal should survive truncation).

---

## 4. State sweeps (run after calibration PASS)

All four states: 3-point grid {0.4, 0.7, 1.0}. Each w_r takes:
- ~30–60 min HGI regeneration (CPU, 2000 epochs, state-size dependent)
- ~5–10 min MTLnet training (2 folds × 15 epochs)

### Pair 1: Arizona and Texas (run concurrently in two terminals)

**Terminal A — Arizona:**
```bash
cd "/Volumes/Vitor's SSD/ingred"
export PYTHONPATH="src:research"
export HGI_NUM_THREADS=4
VENV=".venv/bin/python"

# w_r=0.4
snapshot_hgi arizona before_sweep
run_hgi_sweep Arizona 0.4
snapshot_hgi arizona sweep_wr04
$VENV scripts/train.py --task mtl --state arizona --engine hgi --folds 2 --epochs 15
get_cat_f1 arizona   # record AZ_04

# w_r=0.7
snapshot_hgi arizona sweep_wr04_done
run_hgi_sweep Arizona 0.7
snapshot_hgi arizona sweep_wr07
$VENV scripts/train.py --task mtl --state arizona --engine hgi --folds 2 --epochs 15
get_cat_f1 arizona   # record AZ_07

# w_r=1.0
snapshot_hgi arizona sweep_wr07_done
run_hgi_sweep Arizona 1.0
snapshot_hgi arizona sweep_wr10
$VENV scripts/train.py --task mtl --state arizona --engine hgi --folds 2 --epochs 15
get_cat_f1 arizona   # record AZ_10
```

**Terminal B — Texas:**
```bash
cd "/Volumes/Vitor's SSD/ingred"
export PYTHONPATH="src:research"
export HGI_NUM_THREADS=4
VENV=".venv/bin/python"

# w_r=0.4
snapshot_hgi texas before_sweep
run_hgi_sweep Texas 0.4
snapshot_hgi texas sweep_wr04
$VENV scripts/train.py --task mtl --state texas --engine hgi --folds 2 --epochs 15
get_cat_f1 texas   # record TX_04

# w_r=0.7
snapshot_hgi texas sweep_wr04_done
run_hgi_sweep Texas 0.7
snapshot_hgi texas sweep_wr07
$VENV scripts/train.py --task mtl --state texas --engine hgi --folds 2 --epochs 15
get_cat_f1 texas   # record TX_07

# w_r=1.0
snapshot_hgi texas sweep_wr07_done
run_hgi_sweep Texas 1.0
snapshot_hgi texas sweep_wr10
$VENV scripts/train.py --task mtl --state texas --engine hgi --folds 2 --epochs 15
get_cat_f1 texas   # record TX_10
```

### Pair 2: California and Florida (after Pair 1 completes, run concurrently)

**Terminal A — California:**
```bash
# w_r=0.4
snapshot_hgi california before_sweep
run_hgi_sweep California 0.4
snapshot_hgi california sweep_wr04
$VENV scripts/train.py --task mtl --state california --engine hgi --folds 2 --epochs 15
get_cat_f1 california   # record CA_04

# w_r=0.7
snapshot_hgi california sweep_wr04_done
run_hgi_sweep California 0.7
snapshot_hgi california sweep_wr07
$VENV scripts/train.py --task mtl --state california --engine hgi --folds 2 --epochs 15
get_cat_f1 california   # record CA_07

# w_r=1.0
snapshot_hgi california sweep_wr07_done
run_hgi_sweep California 1.0
snapshot_hgi california sweep_wr10
$VENV scripts/train.py --task mtl --state california --engine hgi --folds 2 --epochs 15
get_cat_f1 california   # record CA_10
```

**Terminal B — Florida:**
```bash
# w_r=0.4
snapshot_hgi florida before_sweep
run_hgi_sweep Florida 0.4
snapshot_hgi florida sweep_wr04
$VENV scripts/train.py --task mtl --state florida --engine hgi --folds 2 --epochs 15
get_cat_f1 florida   # record FL_04

# w_r=0.7
snapshot_hgi florida sweep_wr04_done
run_hgi_sweep Florida 0.7
snapshot_hgi florida sweep_wr07
$VENV scripts/train.py --task mtl --state florida --engine hgi --folds 2 --epochs 15
get_cat_f1 florida   # record FL_07

# w_r=1.0
snapshot_hgi florida sweep_wr07_done
run_hgi_sweep Florida 1.0
snapshot_hgi florida sweep_wr10
$VENV scripts/train.py --task mtl --state florida --engine hgi --folds 2 --epochs 15
get_cat_f1 florida   # record FL_10
```

---

## 5. Decision rule (apply per state)

```python
# Fill in measured values after sweep
results = {
    'arizona':    {0.4: (AZ_04_F1, AZ_04_STD), 0.7: (AZ_07_F1, AZ_07_STD), 1.0: (AZ_10_F1, AZ_10_STD)},
    'texas':      {0.4: (TX_04_F1, TX_04_STD), 0.7: (TX_07_F1, TX_07_STD), 1.0: (TX_10_F1, TX_10_STD)},
    'california': {0.4: (CA_04_F1, CA_04_STD), 0.7: (CA_07_F1, CA_07_STD), 1.0: (CA_10_F1, CA_10_STD)},
    'florida':    {0.4: (FL_04_F1, FL_04_STD), 0.7: (FL_07_F1, FL_07_STD), 1.0: (FL_10_F1, FL_10_STD)},
}

for state, pts in results.items():
    best_wr   = max(pts, key=lambda w: pts[w][0])
    best_f1, best_std = pts[best_wr]
    others = {w: v for w, v in pts.items() if w != best_wr}
    second_wr = max(others, key=lambda w: others[w][0])
    second_f1, second_std = others[second_wr]

    margin  = best_f1 - second_f1
    sigma   = second_std      # 1σ of second-best

    if margin >= sigma:
        decision = f"PIN w_r={best_wr}"
    else:
        decision = f"INCONCLUSIVE (margin={margin:.4f} < 1σ={sigma:.4f}) — keep interpolated default"
    print(f"{state}: best={best_wr} F1={best_f1:.4f}±{best_std:.4f}  {decision}")
```

---

## 6. Update `hgi.pipe.py` with results

After running the decision rule, update the `STATES` dict in
`pipelines/embedding/hgi.pipe.py`. For each state where a winner was found,
uncomment the state entry and set its `cross_region_weight` to the swept value:

```python
STATES = {
    'Alabama':    {'shapefile': Resources.TL_AL, 'cross_region_weight': 0.7},   # swept 5f50e, confirmed
    'Arizona':    {'shapefile': Resources.TL_AZ, 'cross_region_weight': <AZ_WINNER>},  # swept 2f15e YYYY-MM-DD
    'Texas':      {'shapefile': Resources.TL_TX, 'cross_region_weight': <TX_WINNER>},  # swept 2f15e YYYY-MM-DD
    'California': {'shapefile': Resources.TL_CA, 'cross_region_weight': <CA_WINNER>},  # swept 2f15e YYYY-MM-DD
    'Florida':    {'shapefile': Resources.TL_FL, 'cross_region_weight': <FL_WINNER>},  # swept 2f15e YYYY-MM-DD
}
```

If INCONCLUSIVE, keep the extrapolated default and add a comment:
```python
'California': {'shapefile': Resources.TL_CA, 'cross_region_weight': 0.6},  # extrapolated; 2f15e sweep INCONCLUSIVE YYYY-MM-DD
```

---

## 7. Append results to README.md §5

After the table at line ~580 in `research/embeddings/hgi/README.md`, insert a new
subsection (immediately before the `---` separator at line 590):

```markdown
**Per-state `w_r` sweep (2 folds × 15 epochs, fast protocol):**

Calibration (Alabama): w_r=0.4 → Cat F1 <AL_04_F1> ± <AL_04_STD>,
                        w_r=0.7 → Cat F1 <AL_07_F1> ± <AL_07_STD>. PASS/FAIL.

| State       | w_r=0.4 Cat F1 | w_r=0.7 Cat F1 | w_r=1.0 Cat F1 | Winner | Decision |
|-------------|----------------|----------------|----------------|--------|----------|
| Arizona     | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.X | ... |
| Texas       | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.X | ... |
| California  | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.X | ... |
| Florida     | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.XXXX ± X.XXXX | X.X | ... |

Decision threshold: (best − second_best) ≥ 1σ of second_best → PIN; else INCONCLUSIVE.
```

---

## 8. Artifact inventory in results_save/

After completion, `results_save/` will contain:

```
results_save/
  alabama_before_calib_wr04_<ts>/    # baseline before calibration
  alabama_calib_wr04_<ts>/           # Alabama HGI at w_r=0.4
  alabama_calib_wr04_before_wr07_<ts>/
  alabama_calib_wr07_<ts>/           # Alabama HGI at w_r=0.7 (restored baseline)
  arizona_before_sweep_<ts>/
  arizona_sweep_wr04_<ts>/
  arizona_sweep_wr07_<ts>/
  arizona_sweep_wr10_<ts>/
  texas_before_sweep_<ts>/
  texas_sweep_wr04_<ts>/
  texas_sweep_wr07_<ts>/
  texas_sweep_wr10_<ts>/
  california_before_sweep_<ts>/
  california_sweep_wr04_<ts>/
  california_sweep_wr07_<ts>/
  california_sweep_wr10_<ts>/
  florida_before_sweep_<ts>/
  florida_sweep_wr04_<ts>/
  florida_sweep_wr07_<ts>/
  florida_sweep_wr10_<ts>/
```

After the sweep is done, restore each state's `output/hgi/<state>/` from its
winner snapshot to ensure downstream pipelines use the best embedding:

```bash
rsync -a --delete "results_save/<state>_sweep_wr<winner>_<ts>/" "output/hgi/<state>/"
```

---

## 9. Known constraints and gotchas

1. **No `--wr` CLI flag in hgi.pipe.py.** The `run_hgi_sweep` function in §2 above bypasses the pipeline script entirely and calls the Python API directly. This is intentional — editing the STATES dict for every sweep point is error-prone.

2. **`force_preprocess=True` is always active.** Every `run_hgi_sweep` call overwrites `output/hgi/<state>/`. ALWAYS call `snapshot_hgi` before calling `run_hgi_sweep`.

3. **Within-state sequential, across-state concurrent.** Never run two `run_hgi_sweep` calls for the same state at the same time (shared output path). AZ and TX can run in parallel since they write to separate paths.

4. **MTLnet results go to `results/hgi/<state>/`.** They are NOT overwritten by HGI regeneration. But multiple `train.py` invocations accumulate timestamped subdirs. `get_cat_f1` picks the most recently modified one (`ls -td ... | head -1`).

5. **HGI is CPU-only** (`device='cpu'`). The POI2Vec stage uses CUDA if available, else CPU.

6. **Alabama calibration artifacts**: After calibration, restore Alabama's production w_r=0.7 embedding from `results_save/alabama_calib_wr07_<ts>/` before running downstream tasks.

7. **Dry-run to verify imports** (run once before starting):
   ```bash
   $VENV -c "
   import sys; sys.path.insert(0,'src'); sys.path.insert(0,'research')
   from embeddings.hgi.hgi import train_hgi
   from embeddings.hgi.preprocess import preprocess_hgi
   from embeddings.hgi.poi2vec import train_poi2vec
   from data.inputs.builders import generate_category_input, generate_next_input_from_poi
   print('imports OK')
   "
   ```

---

## 10. Phase 2 execution status

| Step | Status | Notes |
|------|--------|-------|
| Environment check | pending | `.venv` present, imports to verify |
| C1: Alabama w_r=0.4 | pending | |
| C2: Alabama w_r=0.7 | pending | |
| Calibration decision | pending | |
| AZ w_r=0.4 | pending | |
| AZ w_r=0.7 | pending | |
| AZ w_r=1.0 | pending | |
| TX w_r=0.4 | pending | |
| TX w_r=0.7 | pending | |
| TX w_r=1.0 | pending | |
| CA w_r=0.4 | pending | |
| CA w_r=0.7 | pending | |
| CA w_r=1.0 | pending | |
| FL w_r=0.4 | pending | |
| FL w_r=0.7 | pending | |
| FL w_r=1.0 | pending | |
| Update hgi.pipe.py | pending | |
| Append README §5 | pending | |
