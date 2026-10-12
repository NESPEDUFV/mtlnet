"""T2.4 combo-(F) unit gate — mtlnet_crossattn_dualtower_swiglu (dual-tower + SwiGLU shared).

Asserts the combo composes BOTH parents' contracts on a synthetic batch, for the
run config (gated fusion, prior-OFF):
  1. forward+backward finite; out shapes [B,7]/[B,Nreg]; private STAN gets grad.
  2. partition {shared, cat_specific, reg_specific} bijective+exhaustive;
     private tower ⊆ reg_specific (dual-tower contract); SwiGLU FFN ⊆ shared
     (SwiGLU contract); no next_poi param in shared.
  3. shared blocks are _CrossAttnBlockSwiGLU (SwiGLU swap took effect).
  4. prior-OFF: next_poi.alpha is a buffer absent from .parameters().
  5. next_forward (disjoint diag path) runs, depends on the raw region seq.

Run: .venv/bin/python scripts/mtl_improvement/t24_dualtower_swiglu_gate.py
Exit 0 = GREEN.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

import torch
import torch.nn.functional as F

from data.aux_side_channel import _clear_aux
from models.registry import create_model
from models.mtl.mtlnet_crossattn_swiglu.model import _CrossAttnBlockSwiGLU
from tasks.presets import CHECK2HGI_NEXT_REGION, resolve_task_set

torch.manual_seed(0)
B, S, F_DIM, D, NREG, NCAT = 100, 9, 64, 256, 137, 7
MODEL_PARAMS = dict(feature_size=F_DIM, shared_layer_size=D, num_classes=NCAT,
                    num_heads=8, num_layers=4, seq_length=S, num_shared_layers=4)
_fail: list[str] = []


def check(c, m):
    print(f"  [{'OK  ' if c else 'FAIL'}] {m}")
    if not c:
        _fail.append(m)


def _batch():
    cat, reg = torch.randn(B, S, F_DIM), torch.randn(B, S, F_DIM)
    for t in (cat, reg):
        n = torch.randint(0, S, (B,))
        for i in range(B):
            if n[i] > 0:
                t[i, S - int(n[i]):] = 0.0
    return cat, reg, torch.randint(0, NCAT, (B,)), torch.randint(0, NREG, (B,))


def _ids(ps):
    return {id(p) for p in ps}


def main() -> int:
    cat, reg, y_cat, y_reg = _batch()
    _clear_aux()
    ts = resolve_task_set(
        CHECK2HGI_NEXT_REGION, task_b_num_classes=NREG,
        task_b_head_factory="next_stan_flow_dualtower",
        task_b_head_params={"raw_embed_dim": F_DIM, "fusion_mode": "gated",
                            "freeze_alpha": True, "alpha_init": 0.0},
    )
    model = create_model("mtlnet_crossattn_dualtower_swiglu", task_set=ts, **MODEL_PARAMS)
    model.train()

    print("=== forward/backward ===")
    oc, on = model((cat, reg))
    check(oc.shape == (B, NCAT) and on.shape == (B, NREG), f"shapes {tuple(oc.shape)}/{tuple(on.shape)}")
    check(torch.isfinite(oc).all() and torch.isfinite(on).all(), "outputs finite")
    loss = F.cross_entropy(oc, y_cat) + F.cross_entropy(on, y_reg)
    loss.backward()
    check(torch.isfinite(loss), f"loss finite ({loss.item():.3f})")
    nbad = sum(1 for p in model.parameters() if p.grad is not None and not torch.isfinite(p.grad).all())
    check(nbad == 0, f"all grads finite (bad={nbad})")
    check(all(p.grad is not None for p in model.next_poi.private_stan.parameters()),
          "private STAN tower received grad")

    print("\n=== partition ===")
    shared, cat_s, reg_s = _ids(model.shared_parameters()), _ids(model.cat_specific_parameters()), _ids(model.reg_specific_parameters())
    allp, task_s = _ids(model.parameters()), _ids(model.task_specific_parameters())
    check(shared.isdisjoint(cat_s) and shared.isdisjoint(reg_s) and cat_s.isdisjoint(reg_s), "pairwise disjoint")
    check(shared | cat_s | reg_s == allp, f"exhaustive ({len(shared|cat_s|reg_s)}=={len(allp)})")
    check(task_s == cat_s | reg_s, "task_specific == cat ∪ reg")
    priv = _ids(model.next_poi.private_stan.parameters())
    check(len(priv) > 0 and priv <= reg_s, "private tower ⊆ reg_specific (non-empty)")
    ffn = {id(p) for blk in model.crossattn_blocks for p in list(blk.ffn_a.parameters()) + list(blk.ffn_b.parameters())}
    check(ffn <= shared, "SwiGLU FFN ⊆ shared")
    check(_ids(model.next_poi.parameters()).isdisjoint(shared), "no next_poi param in shared")

    print("\n=== structure + prior-OFF ===")
    check(isinstance(model.crossattn_blocks[0], _CrossAttnBlockSwiGLU), "shared blocks are _CrossAttnBlockSwiGLU")
    has_alpha = any(n == "alpha" for n, _ in model.next_poi.named_parameters())
    check((not has_alpha) and (id(model.next_poi.alpha) not in allp), "prior-OFF → alpha is a buffer (absent from .parameters())")

    print("\n=== next_forward (disjoint diag path) ===")
    model.eval()
    with torch.no_grad():
        nf = model.next_forward(reg)
        check(nf.shape == (B, NREG) and torch.isfinite(nf).all(), f"next_forward {tuple(nf.shape)} finite")
        check(not torch.allclose(nf, model.next_forward(torch.randn_like(reg)), atol=1e-5),
              "next_forward depends on raw region seq (private tower live)")

    print("\n" + "=" * 56)
    if _fail:
        print(f"COMBO-(F) GATE: ❌ {len(_fail)} FAIL"); [print("  -", f) for f in _fail]; return 1
    print("COMBO-(F) GATE: ✅ ALL PASS — gate OPEN."); return 0


if __name__ == "__main__":
    sys.exit(main())
