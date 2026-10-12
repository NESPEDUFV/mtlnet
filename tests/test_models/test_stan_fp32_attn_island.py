"""Guards for the opt-in fp32 attention island in _STANAttention (MTL_STAN_FP32_ATTN).

The island runs the masked-softmax attention in fp32 even under bf16/fp16 autocast — a
candidate mitigation for the A40-Ampere bf16 backward grad-NaN. These tests pin its two
load-bearing properties: (1) it is a strict NO-OP when not under autocast (so the board's
true-fp32 path is byte-identical), and (2) under bf16 autocast it runs finite and recovers
fp32-level attention precision.
"""

import torch

from models.next.next_stan import head as stan_head


def _make():
    torch.manual_seed(0)
    attn = stan_head._STANAttention(d_model=64, num_heads=4, seq_length=9, dropout=0.0)
    x = torch.randn(8, 9, 64)
    pm = torch.zeros(8, 9, dtype=torch.bool)
    pm[:, 6:] = True  # some padding
    return attn, x, pm


def test_island_is_noop_without_autocast():
    # With the flag ON but no autocast active, the gate (is_autocast_enabled) is False →
    # the default path runs → byte-identical to flag OFF. This is the board-safety guarantee.
    attn, x, pm = _make()
    orig = stan_head._FP32_ATTN
    try:
        stan_head._FP32_ATTN = False
        out_default = attn(x, pm)
        stan_head._FP32_ATTN = True
        out_flag = attn(x, pm)
        assert torch.equal(out_default, out_flag)
    finally:
        stan_head._FP32_ATTN = orig


def test_island_runs_finite_and_recovers_precision_under_bf16():
    attn, x, pm = _make()
    orig = stan_head._FP32_ATTN
    try:
        # fp32 reference (no autocast)
        stan_head._FP32_ATTN = False
        ref = attn(x, pm)
        # bf16 autocast, default (attention in bf16)
        with torch.autocast("cpu", dtype=torch.bfloat16):
            out_bf16 = attn(x, pm)
        # bf16 autocast, island (attention in fp32)
        stan_head._FP32_ATTN = True
        with torch.autocast("cpu", dtype=torch.bfloat16):
            out_island = attn(x, pm)
        assert torch.isfinite(out_island).all()
        # the island's attention is fp32, so its output tracks the fp32 reference at least as
        # closely as the all-bf16 path does (out_proj is bf16 in both, so this is conservative).
        err_bf16 = (out_bf16.float() - ref).abs().mean().item()
        err_island = (out_island.float() - ref).abs().mean().item()
        assert err_island <= err_bf16 + 1e-6
    finally:
        stan_head._FP32_ATTN = orig
