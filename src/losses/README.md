# Loss Variants

This domain tracks multi-task weighting/scalarization strategies used in MTL
ablations.

Canonical runtime registration remains in `src/losses/registry.py`.
Each variant folder here documents rationale/source and links to the concrete
runtime class.

Variant folder contract:
- `README.md` using `docs/VARIANT_README_TEMPLATE.md`
- `metadata.yaml` with `evidence_status` in `{proposed, implemented, ablated, promoted}`
- `loss.py` runtime entrypoint
