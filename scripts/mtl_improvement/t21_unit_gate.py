"""T2.1 unit-test gate (hard rule 10) — BLOCKS any multi-fold dual-tower launch.

Builds the dual-tower exactly as the trainer does (``create_model`` +
``resolve_task_set``) on a synthetic 100-user batch and asserts, for every
fusion mode × prior ON/OFF:

  1. forward + backward run; out shapes [B,7]/[B,Nreg]; loss + grads finite.
  2. param partition {shared, cat_specific, reg_specific} is bijective + exhaustive
     over model.parameters(); task_specific == cat ∪ reg; NO next_poi param in
     shared; the private tower's params ⊆ reg_specific (non-empty).
  3. ``next_poi.alpha`` is an nn.Parameter when prior ON (so --alpha-no-weight-decay
     finds it) and a buffer (absent from .parameters()) when prior OFF.
  4. ``setup_per_head_optimizer`` builds; the reg group contains the private tower;
     --alpha-no-weight-decay peels α into its own zero-WD group (prior ON).
  5. capacity: the ONLY params added vs the B9 baseline (mtlnet_crossattn +
     next_getnext_hard) are the private tower + fusion (no accidental widening).
  6. fusion semantics (head-level): private tower contributes (zeroing the raw
     region seq changes the logits); private_only ignores the shared pathway;
     gated/aux DO use the shared pathway at init.
  7. the α·log_T prior actually fires under a published aux (prior ON shifts logits).
  8. next_forward (disjoint diagnostic-best path) runs, shape [B,Nreg], finite,
     and carries the private tower.

Run::
    .venv/bin/python scripts/mtl_improvement/t21_unit_gate.py
Exit 0 = GREEN (gate open); exit 1 = any assertion failed (gate closed).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

import torch
import torch.nn as nn
import torch.nn.functional as F

from data.aux_side_channel import _publish_aux, _clear_aux
from models.registry import create_model
from tasks.presets import CHECK2HGI_NEXT_REGION, resolve_task_set
from training.helpers import setup_per_head_optimizer

torch.manual_seed(0)

B = 100          # 100-user synthetic batch
S = 9            # window
F_DIM = 64       # feature_size (raw region / checkin emb dim)
D = 256          # shared_layer_size
NREG = 137       # synthetic region cardinality (>1 to exercise the classifier)
NCAT = 7

MODEL_PARAMS = dict(
    feature_size=F_DIM, shared_layer_size=D, num_classes=NCAT,
    num_heads=8, num_layers=4, seq_length=S, num_shared_layers=4,
)

_failures: list[str] = []


def check(cond: bool, msg: str) -> None:
    tag = "OK  " if cond else "FAIL"
    print(f"  [{tag}] {msg}")
    if not cond:
        _failures.append(msg)


def _synthetic_batch():
    """[B,S,64] cat (checkin) + reg (region) inputs with a few padded rows."""
    cat = torch.randn(B, S, F_DIM)
    reg = torch.randn(B, S, F_DIM)
    # Pad the tail of ~15% of sequences (pad row == all-zero, the pad convention).
    for t in (cat, reg):
        n_pad = torch.randint(0, S, (B,))
        for i in range(B):
            if n_pad[i] > 0:
                t[i, S - int(n_pad[i]):] = 0.0
    y_cat = torch.randint(0, NCAT, (B,))
    y_reg = torch.randint(0, NREG, (B,))
    return cat, reg, y_cat, y_reg


def _build(fusion_mode: str, prior_on: bool):
    head_params = {"raw_embed_dim": F_DIM, "fusion_mode": fusion_mode}
    if not prior_on:
        head_params.update({"freeze_alpha": True, "alpha_init": 0.0})
    ts = resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=NREG,
        task_b_head_factory="next_stan_flow_dualtower",
        task_b_head_params=head_params,
    )
    return create_model("mtlnet_crossattn_dualtower", task_set=ts, **MODEL_PARAMS)


def _build_b9_reference():
    ts = resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=NREG,
        task_b_head_factory="next_getnext_hard",
    )
    return create_model("mtlnet_crossattn", task_set=ts, **MODEL_PARAMS)


def _ids(params) -> set:
    return {id(p) for p in params}


def _nparams(module_params) -> int:
    return sum(p.numel() for p in module_params)


def test_mode(fusion_mode: str, prior_on: bool, cat, reg, y_cat, y_reg) -> None:
    label = f"{fusion_mode} / prior={'ON' if prior_on else 'OFF'}"
    print(f"\n=== {label} ===")
    _clear_aux()
    model = _build(fusion_mode, prior_on)
    model.train()

    # (1) forward + backward
    out_cat, out_next = model((cat, reg))
    check(out_cat.shape == (B, NCAT), f"out_cat shape {tuple(out_cat.shape)} == ({B},{NCAT})")
    check(out_next.shape == (B, NREG), f"out_next shape {tuple(out_next.shape)} == ({B},{NREG})")
    check(torch.isfinite(out_cat).all() and torch.isfinite(out_next).all(), "outputs finite")
    loss = F.cross_entropy(out_cat, y_cat) + F.cross_entropy(out_next, y_reg)
    check(torch.isfinite(loss), f"loss finite ({loss.item():.4f})")
    loss.backward()
    grads = [p.grad for p in model.parameters() if p.requires_grad]
    n_none = sum(1 for g in grads if g is None)
    n_bad = sum(1 for g in grads if g is not None and not torch.isfinite(g).all())
    check(n_bad == 0, f"all grads finite (bad={n_bad})")
    # private tower must receive gradient (it is on the active reg path)
    priv_grad_ok = all(
        p.grad is not None and torch.isfinite(p.grad).all()
        for p in model.next_poi.private_stan.parameters()
    )
    check(priv_grad_ok, "private tower params all received finite grad")

    # (2) param partition
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
    check(next_poi_ids <= reg_s, "all next_poi params ⊆ reg_specific")
    priv_ids = _ids(model.next_poi.private_stan.parameters())
    check(len(priv_ids) > 0 and priv_ids <= reg_s, "private tower params ⊆ reg_specific (non-empty)")

    # (3) alpha type
    has_alpha_param = any(n == "alpha" for n, _ in model.next_poi.named_parameters())
    if prior_on:
        check(isinstance(model.next_poi.alpha, nn.Parameter) and has_alpha_param,
              "prior ON → next_poi.alpha is an nn.Parameter (visible to --alpha-no-weight-decay)")
    else:
        check((not has_alpha_param) and (id(model.next_poi.alpha) not in allp),
              "prior OFF → next_poi.alpha is a buffer (absent from .parameters())")

    # (4) optimizer
    opt = setup_per_head_optimizer(
        model, cat_lr=1e-3, reg_lr=3e-3, shared_lr=1e-3, weight_decay=0.05,
        alpha_no_weight_decay=prior_on,
    )
    reg_group = next((g for g in opt.param_groups if g.get("name") == "reg"), None)
    check(reg_group is not None, "per-head optimizer has a 'reg' group")
    if reg_group is not None:
        reg_group_ids = {id(p) for p in reg_group["params"]}
        check(priv_ids <= reg_group_ids, "private tower params are in the optimizer 'reg' group")
    if prior_on:
        awd = next((g for g in opt.param_groups if g.get("name") == "alpha_no_wd"), None)
        check(awd is not None and len(awd["params"]) == 1 and awd["weight_decay"] == 0.0,
              "--alpha-no-weight-decay peels α into a single zero-WD group")


def test_capacity(cat, reg) -> None:
    print("\n=== capacity (added params attributable to the private tower + fusion) ===")
    b9 = _build_b9_reference()
    b9_n = _nparams(b9.parameters())
    for mode in ("gated", "private_only", "aux"):
        m = _build(mode, prior_on=True)
        m_n = _nparams(m.parameters())
        priv_n = _nparams(m.next_poi.private_stan.parameters())
        # fusion+shared-tower delta = everything in next_poi beyond the bits a
        # plain stan_flow head would have; just report next_poi sizes for audit.
        nextpoi_n = _nparams(m.next_poi.parameters())
        b9_nextpoi_n = _nparams(b9.next_poi.parameters())
        added = m_n - b9_n
        # The added capacity must be confined to next_poi (no widening elsewhere):
        non_nextpoi_delta = (m_n - nextpoi_n) - (b9_n - b9_nextpoi_n)
        print(f"  [{mode}] B9={b9_n:,} dualtower={m_n:,} added={added:,} "
              f"(private_stan={priv_n:,}, next_poi B9={b9_nextpoi_n:,}→{nextpoi_n:,})")
        check(non_nextpoi_delta == 0,
              f"[{mode}] no capacity added OUTSIDE next_poi (delta={non_nextpoi_delta})")
        # sanity: the change vs B9 is confined to the reg head and is roughly one
        # extra STAN backbone, not a blow-up. private_only is legitimately SMALLER
        # than B9 (its private STAN takes raw 64-dim input → smaller input_proj than
        # B9's 256-dim reg backbone, and it omits the shared tower), so allow ±.
        check(abs(added) < 2_000_000,
              f"[{mode}] |added capacity| {added:,} bounded (confined to the reg head)")


def test_fusion_semantics() -> None:
    print("\n=== fusion semantics (head-level) ===")
    from models.next.next_stan_flow_dualtower.head import NextHeadStanFlowDualTower
    _clear_aux()
    x = torch.randn(B, S, D)        # shared pathway
    raw = torch.randn(B, S, F_DIM)  # raw region pathway
    for mode in ("gated", "private_only", "aux"):
        head = NextHeadStanFlowDualTower(
            embed_dim=D, num_classes=NREG, seq_length=S, d_model=128,
            num_heads=8, dropout=0.1, raw_embed_dim=F_DIM,
            priv_num_heads=4, priv_dropout=0.3, fusion_mode=mode,
        )
        head.eval()
        base = head(x, raw_region_seq=raw)
        # private tower contributes → changing raw changes the output (all modes)
        alt_raw = head(x, raw_region_seq=raw + 1.0)
        check(not torch.allclose(base, alt_raw, atol=1e-5),
              f"[{mode}] private tower contributes (Δraw ⇒ Δlogits)")
        # shared pathway: private_only ignores it; gated/aux use it
        alt_x = head(x + 1.0, raw_region_seq=raw)
        shared_used = not torch.allclose(base, alt_x, atol=1e-5)
        if mode == "private_only":
            check(not shared_used, "[private_only] shared pathway IGNORED (Δx ⇒ no change)")
        else:
            check(shared_used, f"[{mode}] shared pathway USED (Δx ⇒ Δlogits)")


def test_prior_fires() -> None:
    print("\n=== α·log_T prior fires under a published aux ===")
    from models.next.next_stan_flow_dualtower.head import NextHeadStanFlowDualTower
    head = NextHeadStanFlowDualTower(
        embed_dim=D, num_classes=NREG, seq_length=S, d_model=128,
        num_heads=8, dropout=0.1, raw_embed_dim=F_DIM, fusion_mode="gated",
        alpha_init=1.0,
    )
    head.eval()
    # Inject a synthetic non-zero log_T and a valid last_region_idx aux.
    with torch.no_grad():
        head.log_T.copy_(torch.randn(NREG, NREG))
    x = torch.randn(B, S, D)
    raw = torch.randn(B, S, F_DIM)
    _clear_aux()
    no_aux = head(x, raw_region_seq=raw)
    _publish_aux(torch.randint(0, NREG, (B,)))
    with_aux = head(x, raw_region_seq=raw)
    _clear_aux()
    check(not torch.allclose(no_aux, with_aux, atol=1e-5),
          "prior shifts logits when aux published (α·log_T live)")


def test_next_forward(cat, reg) -> None:
    print("\n=== next_forward (disjoint diagnostic-best path) carries the private tower ===")
    _clear_aux()
    model = _build("gated", prior_on=True)
    model.eval()
    with torch.no_grad():
        nf = model.next_forward(reg)
        check(nf.shape == (B, NREG) and torch.isfinite(nf).all(),
              f"next_forward shape {tuple(nf.shape)} finite")
        nf_altraw = model.next_forward(reg * 0.0 + torch.randn_like(reg))
        check(not torch.allclose(nf, nf_altraw, atol=1e-5),
              "next_forward output depends on the raw region input (private tower live)")


def main() -> int:
    cat, reg, y_cat, y_reg = _synthetic_batch()
    for mode in ("gated", "private_only", "aux"):
        for prior_on in (True, False):
            test_mode(mode, prior_on, cat, reg, y_cat, y_reg)
    test_capacity(cat, reg)
    test_fusion_semantics()
    test_prior_fires()
    test_next_forward(cat, reg)

    print("\n" + "=" * 60)
    if _failures:
        print(f"T2.1 UNIT GATE: ❌ {len(_failures)} FAILURE(S):")
        for f in _failures:
            print(f"   - {f}")
        return 1
    print("T2.1 UNIT GATE: ✅ ALL CHECKS PASS — gate OPEN for the LR mini-sweep.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
