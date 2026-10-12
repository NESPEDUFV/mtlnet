#!/usr/bin/env python
"""Tier S Prong-A unit-test screen: build + forward + backward EVERY coded next_* head.

Hard rule 16c: "coded" != "working" — bit-rot + the registry silently drops unknown
kwargs, so a head can train while quietly ignoring a feature. This screen is the cheap
CPU gate before any GPU screen run: it confirms each registered head instantiates, runs a
finite forward on a synthetic [B, 9, 64] check-in batch, emits [B, num_classes], and
backprops a finite gradient. Heads that need the aux side-channel / a transition prior fall
back gracefully for this shape smoke (the REAL prior-consumption check is the p1 AL screen,
which wires aux + per-fold log_T correctly).

Run: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/tierS_unit_screen.py
"""
import sys
import torch

from models.registry import list_models, create_model

B, S, D = 32, 9, 64
NC_CAT, NC_REG = 7, 1109  # AL-scale region count for the reg heads

# next_mtl is the in-MTL cat head (needs the MTL wrapper); screened separately.
SKIP = {"next_mtl"}


def try_head(name: str) -> dict:
    rec = {"head": name, "build": "—", "forward": "—", "backward": "—", "out_shape": "—", "note": ""}
    # Region heads carry a large class space + prior; cat encoders use 7 classes.
    is_reg = any(k in name for k in ("getnext", "stan", "tgstan", "stahyper"))
    nc = NC_REG if is_reg else NC_CAT
    for kwargs in (
        dict(embed_dim=D, num_classes=nc, seq_length=S),
        # SASRec-style heads (next_single) need the full transformer config:
        dict(embed_dim=D, num_classes=nc, seq_length=S, num_heads=4, num_layers=2),
        dict(embed_dim=D, num_classes=nc),  # heads that don't take seq_length
    ):
        try:
            head = create_model(name, **kwargs)
            rec["build"] = "ok"
            rec["note"] = ""  # clear any earlier-attempt error once a variant builds
            break
        except Exception as e:  # noqa: BLE001
            rec["build"] = "FAIL"
            rec["note"] = f"build: {type(e).__name__}: {e}"[:140]
            head = None
    if head is None:
        return rec
    try:
        x = torch.randn(B, S, D)
        out = head(x)
        rec["out_shape"] = str(tuple(out.shape))
        ok_shape = out.shape[0] == B and out.shape[-1] == nc and torch.isfinite(out).all()
        rec["forward"] = "ok" if ok_shape else "BAD"
        if not ok_shape:
            rec["note"] = (rec["note"] + f" forward shape/finite off (exp [*,{nc}])").strip()
        loss = torch.nn.functional.cross_entropy(out, torch.randint(0, nc, (B,)))
        loss.backward()
        g_ok = all(p.grad is None or torch.isfinite(p.grad).all() for p in head.parameters())
        rec["backward"] = "ok" if (torch.isfinite(loss) and g_ok) else "BAD"
    except Exception as e:  # noqa: BLE001
        rec["forward"] = rec["forward"] if rec["forward"] != "—" else "FAIL"
        rec["note"] = (rec["note"] + f" fwd/bwd: {type(e).__name__}: {e}").strip()[:200]
    return rec


def main() -> int:
    names = sorted(n for n in list_models() if n.startswith("next_") and n not in SKIP)
    print(f"Tier S Prong-A unit screen — {len(names)} coded next_* heads\n")
    hdr = f"{'head':<28}{'build':<7}{'forward':<9}{'backward':<10}{'out_shape':<14}note"
    print(hdr); print("-" * len(hdr))
    rows = [try_head(n) for n in names]
    n_fail = 0
    for r in rows:
        bad = "FAIL" in (r["build"], r["forward"], r["backward"]) or "BAD" in (r["forward"], r["backward"])
        n_fail += bad
        print(f"{r['head']:<28}{r['build']:<7}{r['forward']:<9}{r['backward']:<10}{r['out_shape']:<14}{r['note']}")
    print("-" * len(hdr))
    print(f"\n{len(rows)-n_fail}/{len(rows)} heads pass build+forward+backward; {n_fail} flagged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
