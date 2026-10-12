# MTL Architecture Variants

This domain tracks MTL backbone variants used in architecture ablations.

Canonical runtime exports live in `src/models/mtl/__init__.py`.
Model registration is discovered via `src/models/registry.py`.
Each variant folder documents motivation, source references, and runtime class
mapping.

Variant folder contract:
- `README.md` using `docs/VARIANT_README_TEMPLATE.md`
- `metadata.yaml` with `evidence_status` in `{proposed, implemented, ablated, promoted}`
- `model.py` runtime entrypoint
