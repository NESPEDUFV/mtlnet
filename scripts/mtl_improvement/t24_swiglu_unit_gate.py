"""T2.4 unit-test gate — BLOCKS any multi-fold mtlnet_crossattn_swiglu launch.

Builds the SwiGLU hybrid exactly as the trainer does (``create_model`` +
``resolve_task_set``) on a synthetic 100-user batch with the T2.4 run recipe
(reg head = ``next_getnext_hard``) and asserts:

  1. forward + backward run; out shapes [B,7]/[B,Nreg]; loss + grads finite.
  2. param partition {shared, cat_specific, reg_specific} is bijective +
     exhaustive over model.parameters(); task_specific == cat ∪ reg; no
     next_poi param in shared; shared params are the SwiGLU cross-attn stack
     + final LNs (and carry the SwiGLU FFN weights).
  3. structure: the shared blocks are ``_CrossAttnBlockSwiGLU`` (pre-norm +
     SwiGLU), the FFN exposes the 3 SwiGLU projections w1/w2/w3 (no GELU
     Sequential), and SwiGLU hidden == round(2/3·ffn_dim) (param-parity rule).
  4. capacity: total params are within a small tolerance of the baseline
     ``mtlnet_crossattn`` (same recipe) — the SwiGLU swap is capacity-matched,
     not a widening.
  5. partial forwards ``cat_forward`` / ``next_forward`` run, correct shapes,
     finite (inherited from the parent unchanged — assert they still work).
  6. ``setup_per_head_optimizer`` builds; the SwiGLU FFN params land in the
     'shared' group (they are shared-backbone params).

Run::
    .venv/bin/python scripts/mtl_improvement/t24_swiglu_unit_gate.py
Exit 0 = GREEN (gate open); exit 1 = any assertion failed (gate closed).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

import torch
import torch.nn.functional as F

from models.registry import create_model
from models.mtl.mtlnet_crossattn_swiglu.model import (
    _CrossAttnBlockSwiGLU,
    _SwiGLU,
)
from tasks.presets import CHECK2HGI_NEXT_REGION, resolve_task_set
from training.helpers import setup_per_head_optimizer

torch.manual_seed(0)

B = 100
S = 9
F_DIM = 64
D = 256
NREG = 137
NCAT = 7

MODEL_PARAMS = dict(
    feature_size=F_DIM, shared_layer_size=D, num_classes=NCAT,
    num_heads=8, num_layers=4, seq_length=S, num_shared_layers=4,
)

_failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
    if not cond:
        _failures.append(msg)


def _synthetic_batch():
    cat = torch.randn(B, S, F_DIM)
    reg = torch.randn(B, S, F_DIM)
    for t in (cat, reg):
        n_pad = torch.randint(0, S, (B,))
        for i in range(B):
            if n_pad[i] > 0:
                t[i, S - int(n_pad[i]):] = 0.0
    y_cat = torch.randint(0, NCAT, (B,))
    y_reg = torch.randint(0, NREG, (B,))
    return cat, reg, y_cat, y_reg


def _build(model_name: str):
    ts = resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=NREG,
        task_b_head_factory="next_getnext_hard",
    )
    return create_model(model_name, task_set=ts, **MODEL_PARAMS)


def _ids(params) -> set:
    return {id(p) for p in params}


def _nparams(params) -> int:
    return sum(p.numel() for p in params)


def main() -> int:
    cat, reg, y_cat, y_reg = _synthetic_batch()
    model = _build("mtlnet_crossattn_swiglu")
    model.train()

    # (1) forward + backward
    print("=== forward / backward ===")
    out_cat, out_next = model((cat, reg))
    check(out_cat.shape == (B, NCAT), f"out_cat shape {tuple(out_cat.shape)} == ({B},{NCAT})")
    check(out_next.shape == (B, NREG), f"out_next shape {tuple(out_next.shape)} == ({B},{NREG})")
    check(torch.isfinite(out_cat).all() and torch.isfinite(out_next).all(), "outputs finite")
    loss = F.cross_entropy(out_cat, y_cat) + F.cross_entropy(out_next, y_reg)
    check(torch.isfinite(loss), f"loss finite ({loss.item():.4f})")
    loss.backward()
    n_bad = sum(
        1 for p in model.parameters()
        if p.requires_grad and p.grad is not None and not torch.isfinite(p.grad).all()
    )
    check(n_bad == 0, f"all grads finite (bad={n_bad})")
    # the SwiGLU FFN weights must receive gradient (they are on the active path)
    ffn_grad_ok = all(
        p.grad is not None and torch.isfinite(p.grad).all()
        for blk in model.crossattn_blocks
        for p in list(blk.ffn_a.parameters()) + list(blk.ffn_b.parameters())
    )
    check(ffn_grad_ok, "SwiGLU FFN params all received finite grad")

    # (2) param partition
    print("\n=== param partition ===")
    shared = _ids(model.shared_parameters())
    cat_s = _ids(model.cat_specific_parameters())
    reg_s = _ids(model.reg_specific_parameters())
    task_s = _ids(model.task_specific_parameters())
    allp = _ids(model.parameters())
    check(shared.isdisjoint(cat_s) and shared.isdisjoint(reg_s) and cat_s.isdisjoint(reg_s),
          "shared / cat_specific / reg_specific pairwise disjoint")
    check(shared | cat_s | reg_s == allp,
          f"partition exhaustive (union={len(shared|cat_s|reg_s)} == all={len(allp)})")
    check(task_s == cat_s | reg_s, "task_specific == cat_specific ∪ reg_specific")
    next_poi_ids = _ids(model.next_poi.parameters())
    check(next_poi_ids.isdisjoint(shared), "no next_poi param in shared_parameters()")
    ffn_ids = {
        id(p) for blk in model.crossattn_blocks
        for p in list(blk.ffn_a.parameters()) + list(blk.ffn_b.parameters())
    }
    check(ffn_ids <= shared, "SwiGLU FFN params ⊆ shared_parameters()")

    # (3) structure
    print("\n=== structure (pre-norm + SwiGLU) ===")
    blk0 = model.crossattn_blocks[0]
    check(isinstance(blk0, _CrossAttnBlockSwiGLU), "shared blocks are _CrossAttnBlockSwiGLU")
    check(isinstance(blk0.ffn_a, _SwiGLU) and isinstance(blk0.ffn_b, _SwiGLU),
          "per-stream FFNs are _SwiGLU (gated)")
    check(all(hasattr(blk0.ffn_a, attr) for attr in ("w1", "w2", "w3")),
          "SwiGLU exposes 3 projections w1/w2/w3 (not a 2-matrix GELU FFN)")
    # hidden == round(2/3 * ffn_dim); ffn_dim defaults to shared_layer_size (D)
    expected_hidden = max(1, round((2.0 / 3.0) * D))
    actual_hidden = blk0.ffn_a.w1.out_features
    check(actual_hidden == expected_hidden,
          f"SwiGLU hidden {actual_hidden} == round(2/3·{D})={expected_hidden} (param-parity rule)")

    # (4) capacity parity vs the crossattn baseline (same recipe)
    print("\n=== capacity parity vs mtlnet_crossattn ===")
    base = _build("mtlnet_crossattn")
    n_swiglu = _nparams(model.parameters())
    n_base = _nparams(base.parameters())
    # confine the comparison to the shared backbone (the only thing that changed)
    n_swiglu_shared = _nparams(model.shared_parameters())
    n_base_shared = _nparams(base.shared_parameters())
    rel = abs(n_swiglu_shared - n_base_shared) / max(1, n_base_shared)
    print(f"  total: base={n_base:,} swiglu={n_swiglu:,}")
    print(f"  shared backbone: base={n_base_shared:,} swiglu={n_swiglu_shared:,} (rel Δ={rel:.3%})")
    check(rel < 0.05, f"shared-backbone params within 5% of baseline (Δ={rel:.3%}) — capacity-matched")
    # everything outside the shared backbone must be identical (encoders + heads untouched)
    check((n_swiglu - n_swiglu_shared) == (n_base - n_base_shared),
          "non-shared params (encoders + heads) identical to baseline")

    # (5) partial forwards (inherited) still run
    print("\n=== partial forwards (inherited) ===")
    model.eval()
    with torch.no_grad():
        cf = model.cat_forward(cat)
        check(cf.shape == (B, NCAT) and torch.isfinite(cf).all(),
              f"cat_forward shape {tuple(cf.shape)} finite")
        nf = model.next_forward(reg)
        check(nf.shape == (B, NREG) and torch.isfinite(nf).all(),
              f"next_forward shape {tuple(nf.shape)} finite")

    # (6) optimizer: SwiGLU FFN in the 'shared' group
    print("\n=== per-head optimizer ===")
    opt = setup_per_head_optimizer(
        model, cat_lr=1e-3, reg_lr=3e-3, shared_lr=1e-3, weight_decay=0.05,
    )
    shared_group = next((g for g in opt.param_groups if g.get("name") == "shared"), None)
    check(shared_group is not None, "per-head optimizer has a 'shared' group")
    if shared_group is not None:
        shared_group_ids = {id(p) for p in shared_group["params"]}
        check(ffn_ids <= shared_group_ids, "SwiGLU FFN params land in the optimizer 'shared' group")

    print("\n" + "=" * 60)
    if _failures:
        print(f"T2.4 SWIGLU UNIT GATE: ❌ {len(_failures)} FAILURE(S):")
        for f in _failures:
            print(f"   - {f}")
        return 1
    print("T2.4 SWIGLU UNIT GATE: ✅ ALL CHECKS PASS — gate OPEN.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
