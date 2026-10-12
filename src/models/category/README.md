# Category-Task Head Variants

This domain tracks head variants for the category-task branch.

Canonical runtime exports live in `src/models/category/__init__.py`.
Model registration is discovered through `src/models/registry.py`.
Each variant folder documents why it exists and maps to the runtime class.

Variant folder contract:
- `README.md` using `docs/VARIANT_README_TEMPLATE.md`
- `metadata.yaml` with `evidence_status` in `{proposed, implemented, ablated, promoted}`
- `head.py` runtime entrypoint
