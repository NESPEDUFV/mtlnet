"""T2.3 audit: param-partition gate for mtlnet_mmoe + mtlnet_cgc.

Mirrors t21_unit_gate's _build/_ids approach. Builds each MoE model under
CHECK2HGI_NEXT_REGION with task_b_head_factory='next_getnext_hard' and
asserts the F49-class partition safety properties:

  P1 shared / cat_specific / reg_specific pairwise DISJOINT
  P2 their union == ALL model.parameters()  (exhaustive, 0 uncovered)
  P3 task_specific == cat_specific ∪ reg_specific
  P4 no next_poi param in shared
  P5 all next_poi params ⊆ reg_specific
  P6 the MoE expert/gate modules are actually COVERED by some bucket
     (no silent drop) — list any uncovered param names.
  P7 forward+backward run; grads finite; no shared-expert param has grad None.
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
from tasks.presets import CHECK2HGI_NEXT_REGION, resolve_task_set

torch.manual_seed(0)

B, S, F_DIM, D, NREG, NCAT = 100, 9, 64, 256, 137, 7
MODEL_PARAMS = dict(
    feature_size=F_DIM, shared_layer_size=D, num_classes=NCAT,
    num_heads=8, num_layers=4, seq_length=S, num_shared_layers=4,
)

_fail = []


def check(cond, msg):
    print(f"  [{'OK  ' if cond else 'FAIL'}] {msg}")
    if not cond:
        _fail.append(msg)


def _ids(ps):
    return {id(p) for p in ps}


def _synth():
    cat = torch.randn(B, S, F_DIM)
    reg = torch.randn(B, S, F_DIM)
    for t in (cat, reg):
        n_pad = torch.randint(0, S, (B,))
        for i in range(B):
            if n_pad[i] > 0:
                t[i, S - int(n_pad[i]):] = 0.0
    return cat, reg, torch.randint(0, NCAT, (B,)), torch.randint(0, NREG, (B,))


def audit(model_name):
    print(f"\n=== {model_name} ===")
    ts = resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=NREG,
        task_b_head_factory="next_getnext_hard",
    )
    model = create_model(model_name, task_set=ts, **MODEL_PARAMS)
    model.train()

    name_by_id = {id(p): n for n, p in model.named_parameters()}
    shared = _ids(model.shared_parameters())
    cat_s = _ids(model.cat_specific_parameters())
    reg_s = _ids(model.reg_specific_parameters())
    task_s = _ids(model.task_specific_parameters())
    allp = _ids(model.parameters())

    check(shared.isdisjoint(cat_s) and shared.isdisjoint(reg_s) and cat_s.isdisjoint(reg_s),
          "P1 shared/cat/reg pairwise disjoint")
    union = shared | cat_s | reg_s
    uncovered = allp - union
    check(union == allp,
          f"P2 partition exhaustive (union={len(union)} all={len(allp)} uncovered={len(uncovered)})")
    if uncovered:
        print("       UNCOVERED PARAMS:")
        for pid in uncovered:
            print(f"         - {name_by_id.get(pid, '?')}")
    extra = union - allp
    if extra:
        print(f"       WARNING: partition references {len(extra)} param(s) not in model.parameters()")
    check(task_s == cat_s | reg_s, "P3 task_specific == cat ∪ reg")
    next_poi_ids = _ids(model.next_poi.parameters())
    check(next_poi_ids.isdisjoint(shared), "P4 no next_poi param in shared")
    check(next_poi_ids <= reg_s, "P5 all next_poi params ⊆ reg_specific")

    # P6: every expert/gate param landed in exactly one bucket
    moe_ids = {id(p) for n, p in model.named_parameters()
               if any(k in n for k in ("expert", "gate", "mmoe", "cgc"))}
    moe_uncovered = moe_ids - union
    check(len(moe_uncovered) == 0,
          f"P6 all MoE expert/gate params covered ({len(moe_ids)} moe params, {len(moe_uncovered)} dropped)")
    for pid in moe_uncovered:
        print(f"         DROPPED MoE param: {name_by_id.get(pid, '?')}")

    # report shared-bucket contents for sanity
    shared_names = sorted({name_by_id[i].split('.')[0] + '.' + name_by_id[i].split('.')[1]
                           for i in shared}) if shared else []
    print(f"       shared bucket prefixes: {shared_names}")

    # P7: fwd/bwd + grads
    cat, reg, y_cat, y_reg = _synth()
    out_cat, out_next = model((cat, reg))
    loss = F.cross_entropy(out_cat, y_cat) + F.cross_entropy(out_next, y_reg)
    loss.backward()
    n_bad = sum(1 for p in model.parameters()
                if p.grad is not None and not torch.isfinite(p.grad).all())
    n_none_shared = sum(1 for n, p in model.named_parameters()
                        if id(p) in shared and p.grad is None)
    check(torch.isfinite(loss) and n_bad == 0,
          f"P7 fwd/bwd ok, loss={loss.item():.4f}, bad_grads={n_bad}")
    check(n_none_shared == 0, f"P7b every shared(expert) param got a grad (None={n_none_shared})")


def main():
    for m in ("mtlnet_mmoe", "mtlnet_cgc"):
        audit(m)
    print("\n" + "=" * 60)
    if _fail:
        print(f"T2.3 PARTITION AUDIT: FAIL — {len(_fail)} issue(s):")
        for f in _fail:
            print("   -", f)
        return 1
    print("T2.3 PARTITION AUDIT: ALL PASS — partition bijective+exhaustive for both MoE models.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
