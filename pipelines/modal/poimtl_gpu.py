"""PoiMtlNet v18_2 training env — torch 2.11.0+cu128 + PyTorch Geometric 2.7.0.

Pins are taken from the GPU host this study has been running on, so a rented
container reproduces the same numerics rather than an approximation:

    python 3.12.3   torch 2.11.0+cu128 (cuda 12.8)   torch_geometric 2.7.0
    numpy 2.0.2     pandas 2.2.3       pyarrow 24.0.0
    scikit-learn 1.8.0  scipy 1.16.3   tqdm 4.67.1   pyyaml 6.0.3

WHY THE COMPILED PyG EXTRAS ARE OMITTED
=======================================
torch_scatter / torch_sparse / torch_cluster are installed on the origin host,
but the two job entrypoints do not import them:

    grep -c 'torch_scatter|torch_sparse|torch_cluster' scripts/train.py                  -> 0
    grep -c 'torch_scatter|torch_sparse|torch_cluster' scripts/p1_region_head_ablation.py -> 0

The only references live in research/embeddings/hgi/README.md and two host setup
scripts. Those extras need per-torch-version compiled wheels and are the single
most fragile part of a PyG install, so they are left out deliberately. If a job
ever ImportErrors on one, add it as its own pip phase against the live torch
version rather than relaxing the torch pin.

ORDERING IS LOAD-BEARING
========================
torch is installed FIRST, from the cu128 index, as its own phase. torch_geometric
is installed AFTER, in a separate phase, so its resolver sees torch already
satisfied and cannot drag in a different (CPU or cu12x-mismatched) wheel. This is
the same ordering scripts/runpod_setup.sh uses on the other rented backend.

PRECISION
=========
Nothing here selects precision. The job command pins MTL_DISABLE_AMP=1 (fp32)
because california (8462 region classes) and texas (6530) sit in the band where
bf16 backward grad-NaNs and fp16 logits overflow, and the resulting collapse is
SILENT — the per-task best-epoch selector reports the pre-collapse peak. See
docs/studies/closing_data/archive/lessons/CA_MTL_DIVERGENCE.md.
"""

import modal

META = {
    "packages": ["torch", "torch_geometric", "pandas", "pyarrow", "scikit-learn"],
    "gpu_default": "H100",
    "egress_domains": [],
}

_TORCH_INDEX = "https://download.pytorch.org/whl/cu128"


def build(
    *, secrets: dict[str, str] | None = None
) -> tuple["modal.Image", dict[str, "modal.Volume"], dict[str, str]]:
    secrets = secrets or {}
    img = (
        modal.Image.debian_slim(python_version="3.12")
        .apt_install("git", "curl", "zstd")
        # phase 1 — torch alone, from the cu128 index, so nothing can outvote it
        .pip_install(
            "torch==2.11.0+cu128",
            extra_index_url=_TORCH_INDEX,
        )
        # phase 2 — PyG against the already-satisfied torch
        .pip_install("torch_geometric==2.7.0")
        # phase 3 — the rest of the stack, pinned to the origin host.
        # These come from the repo's requirements.txt, NOT from grepping imports: the first
        # build of this image was assembled from a hand-list and shipped WITHOUT torchmetrics,
        # which next_cv.py imports at module scope. The job died 17 s in on the GPU tier.
        # Read the declared manifest; do not infer the dependency set.
        .pip_install(
            "numpy==2.0.2",
            "pandas==2.2.3",
            "pyarrow==24.0.0",
            "scikit-learn==1.8.0",
            "scipy==1.16.3",
            "tqdm==4.67.1",
            "pyyaml==6.0.3",
            "matplotlib==3.9.4",
            "torchmetrics==1.9.0",     # next_cv.py: multiclass_confusion_matrix
            "networkx==3.2.1",
            "h5py==3.13.0",
            "psutil==7.0.0",
            "numba==0.60.0",
            "hydra-core==1.3.2",
            "omegaconf==2.3.0",
            "pytorch-warmup==0.2.0",
            "shapely==2.1.2",
            "geopandas==1.0.1",
            "cvxpy==1.6.4",
        )
        .env({
            # os.cpu_count() reports the HOST's cores, not the container's
            # allocation; without this a 8-CPU tier spawns a thread storm.
            "OMP_NUM_THREADS": "8",
            "MKL_NUM_THREADS": "8",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        })
    )
    # One persistent volume holds the staged representation (embeddings_insample
    # + auxiliaries) so it is uploaded ONCE and every later job mounts it with
    # zero per-submit transfer.
    vols = {"/data": modal.Volume.from_name("poimtl-v18-data", create_if_missing=True)}
    env = {"POIMTL_DATA": "/data"}
    return img, vols, env
