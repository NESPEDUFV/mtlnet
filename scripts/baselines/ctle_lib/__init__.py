"""CTLE baseline (B1) library.

Faithful-ish reimplementation of CTLE (Lin et al., AAAI 2021,
"Pre-training Context and Time Aware Location Embeddings from Spatial-Temporal
Trajectories for User Next Location Prediction"), the Logan-Lin/CTLE model.

Used by ``scripts/baselines/build_ctle_substrate.py`` to emit a 64-d PER-VISIT
(check-in-level) contextual embedding routed as a substrate column under the
matched champion heads (cat=next_gru, reg=next_stan_flow_dualtower).
"""
