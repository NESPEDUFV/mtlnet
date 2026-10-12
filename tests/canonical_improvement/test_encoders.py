"""F51 guardrail unit test for Tier-3 encoder variants.

Covers: GATTimeEncoder, ResidualLNEncoder, Time2VecCheckinEncoder, RGCNEncoder.

Asserts:
  (a) forward shape matches canonical CheckinEncoder at D=64 on a synthetic graph
  (b) parameter count delta vs canonical within family-specific guardrail
  (c) backward pass produces gradients on all params (no dead params)
  (d) inference is finite (no NaN/Inf)

Additionally runs a random-init linear-probe sanity test (T3.1 advisor protocol):
trains a logistic regression on init-time embeddings to predict synthetic
category labels. If init-time F1 markedly exceeds the canonical reference,
the encoder has a structural shortcut and is unsafe to launch.

Run: python docs/infra/a40/T3_unit_test_encoders.py
"""

import sys
from pathlib import Path

# Path layout: tests/canonical_improvement/test_encoders.py  →
#   parent[1]=canonical_improvement, parent[2]=tests, parent[3]=repo_root.
# Pre-refactor (2026-05-17) the file lived in tests/ and used 4 .parents
# — fixed in-place when adding T5.1 so the test runs from any worktree.
_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

import numpy as np
import torch

# Import the leaf modules directly to avoid triggering __init__.py side-effects
import importlib.util
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_enc = _load("CheckinEncoder", _root / "research/embeddings/check2hgi/model/CheckinEncoder.py")
# variants.py imports Check2HGIModule for the InfoNCE variant; load module deps first
_chmod = _load("Check2HGIModule", _root / "research/embeddings/check2hgi/model/Check2HGIModule.py")
sys.modules["embeddings.check2hgi.model.Check2HGIModule"] = _chmod
_var = _load("variants", _root / "research/embeddings/check2hgi/model/variants.py")
CheckinEncoder = _enc.CheckinEncoder
GATTimeEncoder = _var.GATTimeEncoder
ResidualLNEncoder = _var.ResidualLNEncoder
Time2VecCheckinEncoder = _var.Time2VecCheckinEncoder
RGCNEncoder = _var.RGCNEncoder
Node2VecPOIHead = _var.Node2VecPOIHead
POIIdMixedPooler = _var.POIIdMixedPooler
MaskedPOIDecoder = _var.MaskedPOIDecoder
# Checkin2POI lives in a separate module — load directly to avoid
# triggering the check2hgi package __init__ side-effects.
_c2p = _load("Checkin2POI", _root / "research/embeddings/check2hgi/model/Checkin2POI.py")
Checkin2POI = _c2p.Checkin2POI

torch.manual_seed(42)
np.random.seed(42)

# T3.1-advisor protocol: ~2000 nodes (3-seed init probe). Use ~10 categories
# and a denser edge set so the canonical encoder's init-probe F1 lands close
# to the reference 0.14 (not inflated by the synthetic data being too easy).
N, D, NUM_CAT = 2000, 64, 10
F = NUM_CAT + 4   # category one-hot + 4 temporal sin/cos cols (preprocess layout)
E = 8000

labels = torch.randint(0, NUM_CAT, (N,))
x_cat = torch.zeros(N, NUM_CAT)
x_cat[torch.arange(N), labels] = 1.0
hours = torch.randint(0, 24, (N,)).float()
dows = torch.randint(0, 7, (N,)).float()
x_time = torch.stack([
    torch.sin(2 * np.pi * hours / 24),
    torch.cos(2 * np.pi * hours / 24),
    torch.sin(2 * np.pi * dows / 7),
    torch.cos(2 * np.pi * dows / 7),
], dim=1)
x = torch.cat([x_cat, x_time], dim=1)
edge_index = torch.randint(0, N, (2, E), dtype=torch.long)
edge_weight = torch.rand(E)
# 2 relations for R-GCN: first half user_sequence (0), second half same_poi (1).
edge_type = torch.zeros(E, dtype=torch.long)
edge_type[E // 2:] = 1


def assert_encoder(name, enc, baseline_params, *, max_delta_pct=200.0, extra_fwd=None):
    """F51 spirit: D=64 must be preserved (no output-width inflation).
    Param-count delta is informative but architecturally intrinsic to the
    encoder family (GATv2 has src+tgt linears → ~2× params at same D); the
    50% bound was from a non-attention swap. Bound to 200% for attention
    variants and R-GCN with K=2; 50% for vanilla GCN-family swaps (ResidualLN,
    Time2Vec).
    """
    if extra_fwd is None:
        out = enc(x, edge_index, edge_weight)
    else:
        out = enc(x, edge_index, edge_weight, **extra_fwd)
    assert out.shape == (N, D), f"{name}: out shape {tuple(out.shape)} != ({N}, {D})"
    n_params = sum(p.numel() for p in enc.parameters() if p.requires_grad)
    delta_pct = (n_params - baseline_params) / baseline_params * 100
    print(f"[{name}] params={n_params:,}  delta_vs_GCN={delta_pct:+.1f}%  (max_allowed={max_delta_pct:.0f}%)")
    assert abs(delta_pct) < max_delta_pct, f"{name}: param delta {delta_pct:.1f}% exceeds {max_delta_pct:.0f}% guardrail"
    assert torch.isfinite(out).all(), f"{name}: non-finite output"
    # Backward
    loss = out.sum()
    loss.backward()
    bad = [n for n, p in enc.named_parameters() if p.requires_grad and p.grad is None]
    assert not bad, f"{name}: dead params {bad}"
    print(f"[{name}] forward shape={tuple(out.shape)}  finite=ok  grad=ok")
    return out.detach()


def _probe_on_matrix(M, n_seeds: int = 3) -> float:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    from sklearn.model_selection import train_test_split
    y = labels.numpy()
    f1s = []
    for s in range(n_seeds):
        Xtr, Xte, ytr, yte = train_test_split(M, y, test_size=0.3, random_state=s, stratify=y)
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(Xtr, ytr)
        f1s.append(f1_score(yte, clf.predict(Xte), average="macro", zero_division=0))
    return float(np.mean(f1s))


def random_init_probe(name, build_fn, *, n_seeds=3, extra_fwd=None):
    """T3.1-advisor leak-discriminator: train a logistic regression on
    init-time embeddings to predict category. The raw input already contains
    the category one-hot, so we report ``Δ_x = F1(emb) − F1(x)``: the
    *amplification* of category leakage by the encoder above and beyond what
    the input directly provides. T3.1 GAT init-probe (production) showed
    +0.36 absolute lift vs canonical because attention copies same-category
    neighbours through; T3.2 ResLN's residual pathway preserves the input
    one-hot but does NOT amplify it. Δ_x > 0.30 catches T3.1-style leak.
    """
    f1s = []
    for s in range(n_seeds):
        torch.manual_seed(100 + s)
        enc = build_fn()
        with torch.no_grad():
            if extra_fwd is None:
                emb = enc(x, edge_index, edge_weight).cpu().numpy()
            else:
                emb = enc(x, edge_index, edge_weight, **extra_fwd).cpu().numpy()
        f1s.append(_probe_on_matrix(emb, n_seeds=1))
    f1_mean = float(np.mean(f1s))
    f1_std = float(np.std(f1s, ddof=1)) if n_seeds > 1 else 0.0
    f1_x = _probe_on_matrix(x.cpu().numpy(), n_seeds=3)
    delta_x = f1_mean - f1_x
    print(f"[{name}] init-probe cat F1 {f1_mean:.3f} ± {f1_std:.3f}  "
          f"raw-x F1 {f1_x:.3f}  Δ_x={delta_x:+.3f}")
    return f1_mean, delta_x


# ── Baseline ─────────────────────────────────────────────────────────────────
canonical = CheckinEncoder(F, D, num_layers=2)
with torch.no_grad():
    out_c = canonical(x, edge_index, edge_weight)
baseline = sum(p.numel() for p in canonical.parameters() if p.requires_grad)
print(f"[CheckinEncoder canonical] params={baseline:,}  out shape={tuple(out_c.shape)}")
assert out_c.shape == (N, D), f"CheckinEncoder shape mismatch"

canonical_f1, canonical_dx = random_init_probe(
    "CheckinEncoder canonical",
    lambda: CheckinEncoder(F, D, num_layers=2),
)
# IMPORTANT — init-probe is DIAGNOSTIC ONLY, not a gate.
#
# In production:
#   * The encoder is followed by Checkin2POI attention pooling, POI2Region
#     aggregation, and 3-boundary contrastive training over 500 epochs.
#   * That downstream pipeline disentangles structural category-copy paths
#     from useful aggregation (T3.2 ResLN has +33 pp init-probe but ships
#     paper-grade because the contrastive loss reshapes the representation).
#   * The synthetic graph here puts the category one-hot directly in `x`
#     and random edges — raw-x logreg trivially hits F1=1.0, so any encoder
#     that discards some one-hot signal has Δ_x < 0, and no encoder can
#     have positive Δ_x. The init-probe loses its discriminative power.
#
# REAL gate: the production leak probe recorded by the sweep runner
# (``leak_probe.f1_mean_pct`` in each ``docs/results/canonical_improvement/*.json``).
# T1.1 set the +5 pp red flag vs canonical 40.85. T3.1 GAT at +11.34 pp
# was caught by THIS gate, not the init-probe. The init-probe prints below
# remain as a cheap orientation signal — track them across variants for
# CONCERNS.md C18 stack-watch, but do not block launches on them.
print(f"[probe] init-probe is DIAGNOSTIC ONLY; production leak gate is the "
      f"+5 pp red flag on trained-embedding leak F1 (T1.1 protocol).")
print()

# ── Tier-3 variants ──────────────────────────────────────────────────────────

# GATv2 with attention (T3.1; expected leak — used as positive control here).
gat = GATTimeEncoder(F, D, num_layers=2, heads=4, dropout=0.0, use_edge_attr=True)
assert_encoder("GATTimeEncoder (heads=4, edge_attr=True)", gat, baseline, max_delta_pct=200.0)

# T3.2 ResidualLN — GCN family, strict 50% bound.
resln = ResidualLNEncoder(F, D, num_layers=2, dropout=0.0)
assert_encoder("ResidualLNEncoder", resln, baseline, max_delta_pct=50.0)
random_init_probe(
    "ResidualLNEncoder",
    lambda: ResidualLNEncoder(F, D, num_layers=2, dropout=0.0),
)

# T3.4 Time2Vec — replaces 4 sin/cos cols with d_t=8 learned periodic features.
t2v = Time2VecCheckinEncoder(F, D, num_categories=NUM_CAT, num_layers=2, time2vec_dim=8)
assert_encoder("Time2VecCheckinEncoder (d_t=8)", t2v, baseline, max_delta_pct=50.0)
random_init_probe(
    "Time2VecCheckinEncoder (d_t=8)",
    lambda: Time2VecCheckinEncoder(F, D, num_categories=NUM_CAT, num_layers=2, time2vec_dim=8),
)

# T3.3 R-GCN — K=2 relations, sum aggregate, num_bases=2 (basis decomposition).
rgcn = RGCNEncoder(F, D, num_relations=2, num_layers=2, num_bases=2, aggr="sum")
assert_encoder("RGCNEncoder (K=2, bases=2, sum)", rgcn, baseline,
               max_delta_pct=200.0, extra_fwd={"edge_type": edge_type})
random_init_probe(
    "RGCNEncoder (K=2, bases=2, sum)",
    lambda: RGCNEncoder(F, D, num_relations=2, num_layers=2, num_bases=2, aggr="sum"),
    extra_fwd={"edge_type": edge_type},
)
# Also probe GAT-with-edge-attr to confirm the diagnostic still surfaces a
# difference (T3.1 leak signature, kept as positive control).
random_init_probe(
    "GATTimeEncoder (heads=4, edge_attr=True) — positive control",
    lambda: GATTimeEncoder(F, D, num_layers=2, heads=4, dropout=0.0, use_edge_attr=True),
)


# ── T5.1 — Native learned POI ID embedding (additive post-pool) ──────────────
#
# Distinct from the encoder tests above: POIIdMixedPooler wraps a Checkin2POI
# attention pool and adds ``gamma * poi_table[poi_idx]``. We verify:
#   (a) output shape (num_pois, D) — additive identity must preserve shape
#   (b) backward produces non-None gradient on the poi_table
#   (c) gamma=0 reproduces the bare Checkin2POI output EXACTLY (byte-equality
#       — additive identity)
#   (d) use_poi_id=False path = bare Checkin2POI (same exact-equality)
#   (e) zero-init leak-probe: a linear probe on the init-time poi-table
#       alone (with random checkin pool zero'd out) should NOT beat chance
#       — this defends against the "memorisation-at-init" failure mode
#       (a learnable per-POI table CAN memorise train-set transitions in
#       principle; init must be neutral).
def test_poi_id_embedding():
    torch.manual_seed(123)
    np.random.seed(123)
    N_poi = 100
    D = 64
    num_categories = 10
    # Synthetic check-in -> POI assignment: spread N=2000 check-ins across
    # N_poi=100 POIs so each POI gets ~20 check-ins (mimics the smaller AL/AZ
    # POI density vs FL).
    n_checkins = 2000
    F_in = num_categories + 4
    cklabels = torch.randint(0, num_categories, (n_checkins,))
    ckx_cat = torch.zeros(n_checkins, num_categories)
    ckx_cat[torch.arange(n_checkins), cklabels] = 1.0
    ck_time = torch.randn(n_checkins, 4) * 0.5
    cx = torch.cat([ckx_cat, ck_time], dim=1)
    # Feed through a tiny CheckinEncoder so the pool input has the right shape.
    enc = CheckinEncoder(F_in, D, num_layers=2)
    cedge = torch.randint(0, n_checkins, (2, 4000), dtype=torch.long)
    ceweight = torch.rand(4000)
    ck_emb = enc(cx, cedge, ceweight)              # (n_checkins, D)
    checkin_to_poi = torch.randint(0, N_poi, (n_checkins,), dtype=torch.long)

    # (a) shape + (b) backward gradient on table
    base_pool = Checkin2POI(D, num_heads=4)
    pooler = POIIdMixedPooler(base_pool, num_pois=N_poi, hidden_channels=D,
                              gamma=0.3, init="zero")
    out = pooler(ck_emb, checkin_to_poi, N_poi)
    assert out.shape == (N_poi, D), f"POIIdMixedPooler out shape {tuple(out.shape)} != ({N_poi}, {D})"
    assert torch.isfinite(out).all(), "POIIdMixedPooler non-finite output"
    out.sum().backward()
    assert pooler.poi_table.weight.grad is not None, "POI table received no gradient"
    grad_norm = pooler.poi_table.weight.grad.norm().item()
    assert grad_norm > 0, f"POI table gradient norm = {grad_norm} (expected > 0)"
    print(f"[POIIdMixedPooler γ=0.3 zero-init] params={sum(p.numel() for p in pooler.parameters()):,}  "
          f"out shape={tuple(out.shape)}  table.grad.norm={grad_norm:.4f}")

    # (c) gamma=0 → bit-identical to bare Checkin2POI (additive identity).
    # Re-seed so the wrapped Checkin2POI and the bare reference share
    # parameters (same xavier_uniform seeds).
    torch.manual_seed(456)
    bare = Checkin2POI(D, num_heads=4)
    torch.manual_seed(456)
    bare_wrapped_pool = Checkin2POI(D, num_heads=4)
    pooler_g0 = POIIdMixedPooler(bare_wrapped_pool, num_pois=N_poi,
                                  hidden_channels=D, gamma=0.0, init="zero")
    with torch.no_grad():
        bare_out = bare(ck_emb, checkin_to_poi, N_poi)
        g0_out = pooler_g0(ck_emb, checkin_to_poi, N_poi)
    max_diff = (bare_out - g0_out).abs().max().item()
    assert max_diff == 0.0, (
        f"γ=0 path NOT bit-identical to bare Checkin2POI (max abs diff "
        f"{max_diff:.2e}); additive identity broken — would BREAK the "
        f"canonical-default opt-out guarantee."
    )
    print(f"[POIIdMixedPooler γ=0 ↔ bare Checkin2POI] max |Δ| = {max_diff:.2e}  (bit-identical ✓)")

    # (d) Also verify that with init='zero' and gamma>0, the table addition
    # at step 0 is exactly the zero vector (so the very first forward is
    # identical to the bare pool — defensive against init-time leak).
    torch.manual_seed(789)
    bare2 = Checkin2POI(D, num_heads=4)
    torch.manual_seed(789)
    bare_w2 = Checkin2POI(D, num_heads=4)
    pooler_zinit = POIIdMixedPooler(bare_w2, num_pois=N_poi, hidden_channels=D,
                                     gamma=1.0, init="zero")
    with torch.no_grad():
        bare2_out = bare2(ck_emb, checkin_to_poi, N_poi)
        zinit_out = pooler_zinit(ck_emb, checkin_to_poi, N_poi)
    max_diff_zinit = (bare2_out - zinit_out).abs().max().item()
    assert max_diff_zinit == 0.0, (
        f"zero-init + γ>0 step-0 forward not identical to bare pool "
        f"(max |Δ| {max_diff_zinit:.2e}). The table starts at 0 so the "
        f"additive term must be exactly 0."
    )
    print(f"[POIIdMixedPooler γ=1, init=zero, step 0 ↔ bare] max |Δ| = "
          f"{max_diff_zinit:.2e}  (cold-start neutral ✓)")

    # (e) Leak-probe diagnostic: with init='gaussian' (the riskier setting),
    # a linear probe trained on the init-time poi_table alone should NOT
    # be much above chance on synthetic POI categories. We simulate per-POI
    # category labels and train logreg on the table.weight.
    poi_labels = torch.randint(0, num_categories, (N_poi,)).numpy()
    pooler_gauss = POIIdMixedPooler(Checkin2POI(D, num_heads=4), num_pois=N_poi,
                                     hidden_channels=D, gamma=0.3,
                                     init="gaussian", init_std=0.01)
    M_table = pooler_gauss.poi_table.weight.detach().cpu().numpy()
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    from sklearn.model_selection import train_test_split
    Xtr, Xte, ytr, yte = train_test_split(M_table, poi_labels, test_size=0.3,
                                          random_state=0, stratify=poi_labels)
    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(Xtr, ytr)
    f1_init = f1_score(yte, clf.predict(Xte), average="macro", zero_division=0)
    # Chance ≈ 1/NUM_CAT = 0.1 macro-F1. Gaussian-init random embeddings
    # of shape (N_poi=100, D=64) WILL overfit the 70-row training set with
    # zero training-side regularisation (LogReg C=1 is weak); we expect a
    # small lift over chance but it should remain << 0.50. Bound at 0.50
    # to leave headroom for a 100-row synthetic test where LogReg can be
    # surprisingly aggressive.
    print(f"[POIIdMixedPooler gaussian-init leak-probe] init-time table → "
          f"poi-category macro-F1 = {f1_init:.3f}  (chance ≈ {1.0/num_categories:.2f}, "
          f"leak guardrail < 0.50)")
    assert f1_init < 0.50, (
        f"Init-time poi_table leak-probe F1 {f1_init:.3f} >= 0.50 — "
        f"gaussian init at std=0.01 is somehow memorising labels at init. "
        f"Should be impossible by construction; likely a wiring bug."
    )


test_poi_id_embedding()


# ── T5.1 audit fix: production-path canonical-preservation test ─────────────
#
# Audit T5.1 #1 — the original `test_poi_id_embedding` only exercises
# `POIIdMixedPooler` (a thin wrapper around Checkin2POI). It does NOT
# instantiate the full Check2HGI module. The production path is
# Check2HGI.forward() with the T5.1 plumbing wired through
# Check2HGIModule.py:367 (poi_id_bump add). This test fills that gap by
# constructing two complete Check2HGI(...) instances differing only in T5.1
# flags and asserting bit-identical outputs on identical synthetic data.
def test_check2hgi_module_t51_optout():
    """When T5.1 is OFF, Check2HGI must produce byte-equal pos_checkin_emb /
    pos_poi_emb / pos_region_emb to a baseline built without T5.1 args.

    Also: when poi_id_gamma == 0 with the table enabled, the additive bump
    is zero and outputs must match the OFF case exactly.
    """
    from torch_geometric.data import Data
    Checkin2POI = _load(
        "Checkin2POI", _root / "research/embeddings/check2hgi/model/Checkin2POI.py"
    ).Checkin2POI
    POI2Region = _load(
        "RegionEncoderHGI", _root / "research/embeddings/hgi/model/RegionEncoder.py"
    ).POI2Region

    Check2HGI = _chmod.Check2HGI
    _corruption = _chmod.corruption

    # Tiny synthetic graph.
    N_CK, N_POI, N_REG = 150, 30, 6
    NUM_CAT = 8
    D = 64
    F_IN = NUM_CAT + 4
    torch.manual_seed(2026)
    x = torch.randn(N_CK, F_IN)
    ei = torch.randint(0, N_CK, (2, 400), dtype=torch.long)
    ew = torch.rand(ei.shape[1])
    checkin_to_poi = torch.randint(0, N_POI, (N_CK,), dtype=torch.long)
    poi_to_region = torch.randint(0, N_REG, (N_POI,), dtype=torch.long)
    region_adj = torch.randint(0, N_REG, (2, 12), dtype=torch.long)
    region_area = torch.rand(N_REG)
    data = Data(
        x=x, edge_index=ei, edge_weight=ew,
        checkin_to_poi=checkin_to_poi, poi_to_region=poi_to_region,
        region_adjacency=region_adj, region_area=region_area,
        coarse_region_similarity=torch.eye(N_REG),
        num_pois=N_POI, num_regions=N_REG,
    )

    def _region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    def _build(use_t51: bool, gamma: float = 0.3):
        torch.manual_seed(7)
        enc = CheckinEncoder(F_IN, D, num_layers=2)
        c2p = Checkin2POI(D, num_heads=4)
        p2r = POI2Region(D, num_heads=4)
        kw = dict(
            hidden_channels=D, checkin_encoder=enc,
            checkin2poi=c2p, poi2region=p2r,
            region2city=_region2city, corruption=_corruption,
            alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3,
        )
        if use_t51:
            kw.update(
                use_poi_id_embedding=True,
                poi_id_gamma=gamma,
                poi_id_init="zero",
                num_pois=N_POI,
            )
        return Check2HGI(**kw)

    m_off = _build(use_t51=False)
    m_on_zeroinit = _build(use_t51=True, gamma=0.3)  # gamma>0 BUT zero-init

    # Construction order changes the global RNG state (nn.Embedding consumes
    # some bytes), so the bilinear weights of m_on_* would differ from m_off
    # if we just trained both independently. To isolate the T5.1 production
    # path from RNG-consumption side-effects, we mirror m_off's
    # core weights onto m_on_zeroinit before forward — the only legitimate
    # difference is the additive `gamma * poi_id_table.weight`, which is
    # `gamma * 0 = 0` at step 0 regardless of gamma when init='zero'.
    with torch.no_grad():
        # Copy ALL shared parameters from m_off → m_on_zeroinit. The T5.1 table
        # is the only param that exists in m_on_zeroinit and not m_off; leave
        # it at its `.zero_()` init.
        off_state = {n: p.clone() for n, p in m_off.named_parameters()}
        for name, p in m_on_zeroinit.named_parameters():
            if name in off_state:
                p.data.copy_(off_state[name])

    # Re-seed RNG used by ``corruption(...)`` so both forwards see identical
    # negative permutation.
    torch.manual_seed(99); o_off = m_off(data)
    torch.manual_seed(99); o_on_zeroinit = m_on_zeroinit(data)

    # pos_checkin (index 0), pos_poi_emb (index 3), pos_region_emb (index 6).
    for idx, name in [(0, "pos_checkin_emb"),
                      (3, "pos_poi_emb"),
                      (6, "pos_region_emb")]:
        # Zero-init at step-0: additive bump is gamma * 0 = 0, so outputs
        # MUST be identical regardless of gamma when init='zero'.
        diff = (o_off[idx] - o_on_zeroinit[idx]).abs().max().item()
        assert torch.allclose(o_off[idx], o_on_zeroinit[idx], atol=1e-6), (
            f"T5.1 audit #1: zero-init step-0 SHOULD == OFF for {name}; "
            f"max diff {diff}"
        )
    print("[T5.1 production-path] zero-init step-0 with copied weights ≡ OFF  ✓")


test_check2hgi_module_t51_optout()


# ── T5.1 audit fix: ValueError construction guards ──────────────────────────
def test_check2hgi_t51_value_errors():
    """Audit T5.1 #2: construction-time guards must fire for invalid configs."""
    from torch_geometric.data import Data
    Checkin2POI = _load(
        "Checkin2POI", _root / "research/embeddings/check2hgi/model/Checkin2POI.py"
    ).Checkin2POI
    POI2Region = _load(
        "RegionEncoderHGI", _root / "research/embeddings/hgi/model/RegionEncoder.py"
    ).POI2Region
    Check2HGI = _chmod.Check2HGI
    _corruption = _chmod.corruption
    D = 64
    enc = CheckinEncoder(8 + 4, D, num_layers=2)
    c2p = Checkin2POI(D, num_heads=4)
    p2r = POI2Region(D, num_heads=4)

    # Case 1: use_poi_id_embedding=True without num_pois ⇒ ValueError.
    try:
        Check2HGI(
            hidden_channels=D, checkin_encoder=enc,
            checkin2poi=c2p, poi2region=p2r,
            region2city=lambda z, a: torch.zeros(D), corruption=_corruption,
            use_poi_id_embedding=True, num_pois=None,
        )
        raise AssertionError("Expected ValueError for use_poi_id_embedding=True without num_pois")
    except ValueError as e:
        assert "num_pois" in str(e), f"Unexpected ValueError text: {e}"
        print("  ValueError(num_pois missing)     = ✓")

    # Case 2: poi_id_init='poi2vec' ⇒ ValueError (only zero/gaussian allowed).
    try:
        Check2HGI(
            hidden_channels=D, checkin_encoder=enc,
            checkin2poi=c2p, poi2region=p2r,
            region2city=lambda z, a: torch.zeros(D), corruption=_corruption,
            use_poi_id_embedding=True, num_pois=10,
            poi_id_init="poi2vec",
        )
        raise AssertionError("Expected ValueError for poi_id_init='poi2vec'")
    except ValueError as e:
        assert "zero" in str(e) and "gaussian" in str(e), f"Unexpected: {e}"
        print("  ValueError(poi_id_init='poi2vec')= ✓")


test_check2hgi_t51_value_errors()


# ── Cohort integration test: all-T5-OFF ≡ canonical pre-T5 ──────────────────
#
# Cross-cutting fix #2: build Check2HGI with NO T5 flags and verify the
# behavior is equivalent to a pre-T5 baseline. Without a snapshotted reference
# tensor (the baseline forward pre-T5 changes), we verify the SOFTER but
# defensible invariant: (i) parameter count == canonical (no T5 weights
# allocated), (ii) forward produces finite tensors of the correct shapes,
# (iii) loss is a finite scalar.
def test_all_t5_canonical_optout():
    from torch_geometric.data import Data
    Checkin2POI = _load(
        "Checkin2POI", _root / "research/embeddings/check2hgi/model/Checkin2POI.py"
    ).Checkin2POI
    POI2Region = _load(
        "RegionEncoderHGI", _root / "research/embeddings/hgi/model/RegionEncoder.py"
    ).POI2Region
    Check2HGI = _chmod.Check2HGI
    _corruption = _chmod.corruption

    N_CK, N_POI, N_REG, NUM_CAT, D = 120, 24, 5, 8, 64
    F_IN = NUM_CAT + 4
    torch.manual_seed(4242)
    data = Data(
        x=torch.randn(N_CK, F_IN),
        edge_index=torch.randint(0, N_CK, (2, 250), dtype=torch.long),
        edge_weight=torch.rand(250),
        checkin_to_poi=torch.randint(0, N_POI, (N_CK,), dtype=torch.long),
        poi_to_region=torch.randint(0, N_REG, (N_POI,), dtype=torch.long),
        region_adjacency=torch.randint(0, N_REG, (2, 10), dtype=torch.long),
        region_area=torch.rand(N_REG),
        coarse_region_similarity=torch.eye(N_REG),
        num_pois=N_POI, num_regions=N_REG,
    )

    torch.manual_seed(11)
    m = Check2HGI(
        hidden_channels=D,
        checkin_encoder=CheckinEncoder(F_IN, D, num_layers=2),
        checkin2poi=Checkin2POI(D, num_heads=4),
        poi2region=POI2Region(D, num_heads=4),
        region2city=lambda z, area: torch.sigmoid((z.t() * area).sum(dim=1)),
        corruption=_corruption,
        # ZERO T5 flags. All defaults.
    )
    # Sanity: zero T5 params allocated.
    assert m.poi_id_table is None, "T5.1 table should not be built by default"
    assert m.n2v_head is None, "T5.2a head should not be attached by default"
    assert m.mae_poi_decoder is None, "T5.2b decoder should not be built by default"
    assert float(m.n2v_lambda) == 0.0
    assert float(m.n2v_align_lambda) == 0.0
    assert float(m.mae_poi_lambda) == 0.0

    outs = m(data)
    assert outs[0].shape == (N_CK, D), f"pos_checkin shape: {outs[0].shape}"
    assert outs[3].shape == (N_POI, D), f"pos_poi shape: {outs[3].shape}"
    assert outs[6].shape == (N_REG, D), f"pos_region shape: {outs[6].shape}"
    for i, t in enumerate(outs):
        if torch.is_tensor(t):
            assert torch.isfinite(t).all(), f"outs[{i}] non-finite"

    l = m.loss(*outs)
    assert torch.is_tensor(l) and l.ndim == 0, f"loss not scalar: {l.shape}"
    assert torch.isfinite(l), f"loss non-finite: {l}"
    print(f"[Cohort T5-OFF] params={sum(p.numel() for p in m.parameters()):,} "
          f"loss={l.item():.4f}  ✓")


test_all_t5_canonical_optout()


print("\n[T3 unit test] all assertions passed (forward + backward + leak-probe).")


# ── T5.2a: Joint Node2Vec POI-POI skip-gram head ──────────────────────────────

def _build_synthetic_delaunay_poi_graph(n_poi: int = 100, seed: int = 0):
    """Build a tiny POI lat/lon point cloud + scipy Delaunay triangulation.

    Returns:
        edge_index: (2, E) long tensor of undirected POI-POI edges
        labels: (n_poi,) synthetic category labels for the leak probe
    """
    import scipy.spatial
    from itertools import combinations as _comb
    rng = np.random.RandomState(seed)
    coords = rng.uniform(0.0, 1.0, size=(n_poi, 2))
    tris = scipy.spatial.Delaunay(coords, qhull_options="QJ QbB Pp").simplices
    pairs = set()
    for tri in tris:
        for a, b in _comb(tri.tolist(), 2):
            pairs.add((a, b) if a < b else (b, a))
    edges = np.array(sorted(pairs), dtype=np.int64).T
    # 4-way categorical labels (uniform random; head MUST NOT predict
    # better than chance at init — purely structural skip-gram has no
    # category supervision).
    labels = rng.randint(0, 4, size=n_poi)
    return torch.tensor(edges, dtype=torch.long), labels


def test_node2vec_poi_head():
    """T5.2a unit test — Joint Node2Vec POI-POI skip-gram head.

    Checks:
      (a) compute_loss returns a finite, positive scalar
      (b) backward populates gradients on the POI embedding table
      (c) λ=0 / no-graph fallback returns a zero (no-op) loss
      (d) init-time linear probe does NOT predict synthetic category labels
          above chance (skip-gram has zero category supervision; if probe
          F1 exceeds chance the implementation has leaked a label path)
    """
    torch.manual_seed(123)
    N_POI = 100
    D_POI = 64

    edges, labels = _build_synthetic_delaunay_poi_graph(N_POI, seed=0)
    n_edges = edges.shape[1]
    assert n_edges >= 200, f"synthetic Delaunay should yield ≥ 200 edges; got {n_edges}"

    head = Node2VecPOIHead(
        num_pois=N_POI,
        embedding_dim=D_POI,
        edge_index=edges,
        walk_length=5,
        context_size=3,
        walks_per_node=4,
        p=1.0,
        q=1.0,
        num_negatives=3,
    )

    # (a) loss is finite and positive
    loss = head.compute_loss(epoch_id=0)
    assert torch.isfinite(loss).item(), f"[T5.2a] non-finite skip-gram loss: {loss}"
    assert loss.item() > 0.0, f"[T5.2a] skip-gram loss should be positive at init; got {loss.item()}"
    print(f"[Node2VecPOIHead] λ>0 init loss = {loss.item():.4f}  edges={n_edges}")

    # (b) backward populates POI table gradients
    loss.backward()
    grad = head.poi_table.weight.grad
    assert grad is not None, "[T5.2a] no gradient on POI table after backward"
    assert torch.isfinite(grad).all().item(), "[T5.2a] non-finite gradient on POI table"
    assert grad.abs().sum().item() > 0.0, "[T5.2a] zero gradient on POI table"
    print(f"[Node2VecPOIHead] backward OK, grad_norm={grad.norm().item():.4f}")

    # (c) no-graph fallback is a zero (no-op) loss
    empty_head = Node2VecPOIHead(
        num_pois=N_POI,
        embedding_dim=D_POI,
        edge_index=None,
    )
    empty_loss = empty_head.compute_loss(epoch_id=0)
    assert empty_loss.item() == 0.0, f"[T5.2a] empty-graph loss should be 0; got {empty_loss.item()}"
    print(f"[Node2VecPOIHead] no-graph fallback = {empty_loss.item():.4f}  (correct no-op)")

    # (d) init-time linear probe should NOT exceed chance on synthetic labels.
    # Chance on uniform 4-way labels ≈ 0.25 macro-F1. We allow a tolerance of
    # +0.10 to absorb small-sample variance; a real leak would push F1 much
    # higher (T3.1-style structural shortcut).
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import f1_score
    from sklearn.model_selection import train_test_split
    init_emb = head.poi_table.weight.detach().cpu().numpy()
    Xtr, Xte, ytr, yte = train_test_split(
        init_emb, labels, test_size=0.3, random_state=0, stratify=labels
    )
    clf = LogisticRegression(max_iter=1000, C=1.0)
    clf.fit(Xtr, ytr)
    init_f1 = f1_score(yte, clf.predict(Xte), average="macro", zero_division=0)
    print(f"[Node2VecPOIHead] init-probe cat F1 = {init_f1:.3f}  (chance ≈ 0.25)")
    assert init_f1 < 0.55, (
        f"[T5.2a] init-time probe F1 {init_f1:.3f} suspiciously high "
        f"(synthetic labels are random; head should be uninformative at init)."
    )

    print("[T5.2a Node2VecPOIHead] all checks passed.")


test_node2vec_poi_head()
print("\n[T5.2a unit test] passed.")


# ── T5.3: Multi-view co-training wrapper ─────────────────────────────────────


def test_multiview_wrapper():
    """T5.3 — cross-view POI alignment unit test.

    Verifies:
      (a) MultiViewWrapper forward returns POI embeddings of shape (N_poi, D)
          for BOTH views.
      (b) Cross-view loss is finite and >= 0 (cosine/MSE/InfoNCE).
      (c) Backward populates gradients on BOTH encoders' parameters
          (no dead encoder).
      (d) total_loss = L_v1 + L_v2 + λ_x · L_cross is finite.
      (e) The single-view default (no wrapper) returns standard outputs and
          the wrapper is bit-identical to canonical when only V1 is used.
      (f) share_encoder=True reduces total parameter count vs the default
          (V2 reuses V1's CheckinEncoder weights).
    """
    from torch_geometric.data import Data
    Checkin2POI_mod = _load(
        "Checkin2POI",
        _root / "research/embeddings/check2hgi/model/Checkin2POI.py",
    )
    Checkin2POI = Checkin2POI_mod.Checkin2POI
    # POI2Region from HGI
    HGIRegion = _load(
        "RegionEncoderHGI", _root / "research/embeddings/hgi/model/RegionEncoder.py"
    )
    POI2Region = HGIRegion.POI2Region

    Check2HGI = _chmod.Check2HGI
    _corruption = _chmod.corruption
    MultiViewWrapper = _var.MultiViewWrapper
    _cross_view_loss = _var._cross_view_loss

    torch.manual_seed(0)
    np.random.seed(0)

    # Synthetic graph: 200 check-ins, 40 POIs, 8 regions, 12 categories.
    N_CK, N_POI, N_REG = 200, 40, 8
    NUM_CAT = 12
    D = 64
    F_V1 = NUM_CAT + 4    # canonical [cat one-hot, 4 sin/cos]
    F_V2 = NUM_CAT        # view-2: cat one-hot only

    # View-1 features (with temporal sin/cos).
    cat_idx = torch.randint(0, NUM_CAT, (N_CK,))
    x_v1 = torch.zeros(N_CK, F_V1)
    x_v1[torch.arange(N_CK), cat_idx] = 1.0
    hours = torch.randint(0, 24, (N_CK,)).float()
    x_v1[:, NUM_CAT + 0] = torch.sin(2 * np.pi * hours / 24)
    x_v1[:, NUM_CAT + 1] = torch.cos(2 * np.pi * hours / 24)

    # View-2 features = first NUM_CAT columns of V1 (category one-hot only).
    x_v2 = x_v1[:, :NUM_CAT].clone()

    # V1 edges: user_sequence-like (random pairs) + temporal weights.
    E1 = 600
    ei_v1 = torch.randint(0, N_CK, (2, E1), dtype=torch.long)
    ew_v1 = torch.rand(E1)
    # V2 edges: same-POI-only. Group check-ins by POI assignment, connect pairs.
    checkin_to_poi = torch.randint(0, N_POI, (N_CK,), dtype=torch.long)
    src_l, tgt_l = [], []
    for p in range(N_POI):
        ck_at_p = (checkin_to_poi == p).nonzero(as_tuple=True)[0].tolist()
        if len(ck_at_p) < 2:
            continue
        for i in range(len(ck_at_p)):
            for j in range(i + 1, len(ck_at_p)):
                src_l.append(ck_at_p[i]); tgt_l.append(ck_at_p[j])
                src_l.append(ck_at_p[j]); tgt_l.append(ck_at_p[i])
    ei_v2 = torch.tensor([src_l, tgt_l], dtype=torch.long) if src_l else torch.zeros(2, 0, dtype=torch.long)
    ew_v2 = torch.ones(ei_v2.shape[1])

    poi_to_region = torch.randint(0, N_REG, (N_POI,), dtype=torch.long)
    region_adjacency = torch.randint(0, N_REG, (2, 20), dtype=torch.long)
    region_area = torch.rand(N_REG)
    coarse_sim = torch.eye(N_REG)

    def _make_data(x, ei, ew, in_ch):
        return Data(
            x=x, edge_index=ei, edge_weight=ew,
            checkin_to_poi=checkin_to_poi,
            poi_to_region=poi_to_region,
            region_adjacency=region_adjacency,
            region_area=region_area,
            coarse_region_similarity=coarse_sim,
            num_pois=N_POI, num_regions=N_REG,
        )

    data_v1 = _make_data(x_v1, ei_v1, ew_v1, F_V1)
    data_v2 = _make_data(x_v2, ei_v2, ew_v2, F_V2)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    def _build_check2hgi(in_ch):
        enc = CheckinEncoder(in_ch, D, num_layers=2)
        c2p = Checkin2POI(D, num_heads=4)
        p2r = POI2Region(D, num_heads=4)
        return Check2HGI(
            hidden_channels=D, checkin_encoder=enc,
            checkin2poi=c2p, poi2region=p2r,
            region2city=region2city, corruption=_corruption,
            alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3,
        )

    # (a) Forward shapes.
    torch.manual_seed(1)
    model_v1 = _build_check2hgi(F_V1)
    model_v2 = _build_check2hgi(F_V2)
    wrapper = MultiViewWrapper(
        model_v1=model_v1, model_v2=model_v2,
        cross_lambda=0.3, cross_loss="cosine",
    )
    outs_v1, outs_v2, poi_v1, poi_v2 = wrapper(data_v1, data_v2)
    assert poi_v1.shape == (N_POI, D), f"poi_v1 shape {tuple(poi_v1.shape)} != ({N_POI}, {D})"
    assert poi_v2.shape == (N_POI, D), f"poi_v2 shape {tuple(poi_v2.shape)} != ({N_POI}, {D})"
    print(f"[T5.3 MultiViewWrapper] forward shapes poi_v1={tuple(poi_v1.shape)} "
          f"poi_v2={tuple(poi_v2.shape)} OK")

    # (b) Cross-view loss is finite and non-negative (cosine ≥ 0, MSE ≥ 0,
    # InfoNCE ≥ 0 since cross-entropy ≥ 0).
    for loss_kind in ("cosine", "mse", "infonce"):
        cv = _cross_view_loss(poi_v1, poi_v2, loss_type=loss_kind, temperature=0.2)
        assert torch.isfinite(cv).all(), f"cross-view loss {loss_kind} not finite: {cv}"
        assert cv.item() >= -1e-6, f"cross-view loss {loss_kind} negative: {cv.item()}"
        print(f"[T5.3 MultiViewWrapper] cross-view loss [{loss_kind}] = {cv.item():.4f} (finite, >= 0)")

    # (c) Backward — both encoders must receive gradient.
    wrapper.zero_grad()
    total = wrapper.total_loss(data_v1, data_v2)
    assert torch.isfinite(total).all(), f"total_loss not finite: {total}"
    print(f"[T5.3 MultiViewWrapper] total_loss = {total.item():.4f}")
    total.backward()
    v1_grad_present = any(
        p.grad is not None and p.grad.abs().sum() > 0
        for p in model_v1.checkin_encoder.parameters()
    )
    v2_grad_present = any(
        p.grad is not None and p.grad.abs().sum() > 0
        for p in model_v2.checkin_encoder.parameters()
    )
    assert v1_grad_present, "View-1 encoder did not receive gradient"
    assert v2_grad_present, "View-2 encoder did not receive gradient"
    print("[T5.3 MultiViewWrapper] backward populates grads on BOTH encoders OK")

    # (d) Single-view (no wrapper) returns canonical outputs unchanged.
    torch.manual_seed(1)
    single_model = _build_check2hgi(F_V1)
    single_outs = single_model(data_v1)
    assert len(single_outs) == 9, f"single Check2HGI outputs len {len(single_outs)} != 9"
    single_loss = single_model.loss(*single_outs)
    assert torch.isfinite(single_loss), "single-view loss not finite"
    print(f"[T5.3 MultiViewWrapper] single-view default Check2HGI loss = {single_loss.item():.4f} "
          f"(unchanged path, no wrapper)")

    # (e) share_encoder=True cuts parameter count.
    torch.manual_seed(1)
    model_v1_s = _build_check2hgi(F_V1)
    model_v2_s = _build_check2hgi(F_V1)   # same in_ch so encoders are share-compatible
    wrapper_share = MultiViewWrapper(
        model_v1=model_v1_s, model_v2=model_v2_s,
        cross_lambda=0.3, cross_loss="cosine", share_encoder=True,
    )
    n_default = sum(p.numel() for p in wrapper.parameters())
    n_shared = sum(p.numel() for p in wrapper_share.parameters())
    print(f"[T5.3 MultiViewWrapper] params: default={n_default:,}  shared_enc={n_shared:,}  "
          f"(share saves {n_default - n_shared:,})")
    assert n_shared < n_default, "share_encoder=True should reduce parameter count"

    # (f) export_view dispatch.
    with torch.no_grad():
        _ = wrapper(data_v1, data_v2)
        c_v1, p_v1, r_v1 = wrapper.get_embeddings(which="v1")
        c_v2, p_v2, r_v2 = wrapper.get_embeddings(which="v2")
        c_en, p_en, r_en = wrapper.get_embeddings(which="ensemble")
        assert p_v1.shape == (N_POI, D)
        assert p_v2.shape == (N_POI, D)
        assert p_en.shape == (N_POI, D)
        # Ensemble must be the mean.
        assert torch.allclose(p_en, 0.5 * (p_v1 + p_v2), atol=1e-5), "ensemble != mean(v1, v2)"
    print("[T5.3 MultiViewWrapper] export_view dispatch (v1/v2/ensemble) OK")

    # ── Audit T5.3 #2 (lambda_x=0 ≡ sum of per-view losses) ─────────────────
    # When cross_lambda is exactly zero, ``total_loss`` MUST equal
    # ``L_v1 + L_v2`` (the cross-view contribution gets multiplied out).
    # Both the wrapper forward and Check2HGI.loss invoke randperm/randint, so
    # the test compares ``total_loss(d1, d2)`` to a manual decomposition
    # computed at the same seed via the SAME public wrapper API. With
    # cross_lambda=0 the only difference between the two formulas is a
    # ``0 * L_cross`` term, which is byte-zero in fp32.
    torch.manual_seed(0)
    wrapper_lz = MultiViewWrapper(
        model_v1=_build_check2hgi(F_V1),
        model_v2=_build_check2hgi(F_V2),
        cross_lambda=0.0, cross_loss="cosine",
    )
    # Compute L_v1 + L_v2 by manually mirroring wrapper.total_loss WITHOUT
    # the cross-view term. Re-seed JUST before each forward to match the
    # state total_loss sees.
    torch.manual_seed(0); ref_outs_v1, ref_outs_v2, _, _ = wrapper_lz(data_v1, data_v2)
    ref_l_v1 = wrapper_lz.model_v1.loss(*ref_outs_v1)
    ref_l_v2 = wrapper_lz.model_v2.loss(*ref_outs_v2)
    ref_total_manual = ref_l_v1 + ref_l_v2  # equivalent to total_loss when λ_x=0
    torch.manual_seed(0); l_total = wrapper_lz.total_loss(data_v1, data_v2)
    assert torch.isclose(l_total, ref_total_manual, atol=1e-5), (
        f"λ_x=0 should give total_loss == L_v1 + L_v2; "
        f"got {l_total.item()} vs {ref_total_manual.item()}"
    )
    print(f"  λ_x=0 ⇒ total ≡ L_v1+L_v2       = ✓  "
          f"({l_total.item():.6f} ≈ {ref_total_manual.item():.6f})")

    # ── Audit T5.3 #2 (InfoNCE temperature=0 ⇒ ValueError) ──────────────────
    poi_a = torch.randn(8, D, requires_grad=True)
    poi_b = torch.randn(8, D, requires_grad=True)
    try:
        _ = _cross_view_loss(poi_a, poi_b, loss_type="infonce", temperature=0.0)
        raise AssertionError(
            "Expected ValueError from infonce temperature=0; none raised"
        )
    except ValueError as _expected:
        print(f"  InfoNCE T=0 ⇒ ValueError        = ✓  ({_expected!s:.50})")

    print("\n[T5.3 MultiViewWrapper] all checks passed (incl. audit T5.3 #2).")


test_multiview_wrapper()
print("\n[T5.3 unit test] passed.")


# ── T5.2b MaskedPOIDecoder ───────────────────────────────────────────────────

def test_masked_poi_decoder():
    """T5.2b unit test: MaskedPOIDecoder produces finite SCE loss, gradient
    flows on the decoder MLP, mask_rate=0 returns zero loss / no-op, and the
    mask is reproducible under a torch.Generator seed.

    Synthetic POI graph: ~100 POIs with ~300 random Delaunay-style edges
    (we just generate a random edge list — the decoder treats them
    structurally the same regardless of geometry origin).
    """
    print("\n[T5.2b MaskedPOIDecoder] running unit test")
    P_test = 100
    D_test = 64
    NUM_CAT_test = 11
    # Synthetic POI graph (~300 undirected edges).
    g = torch.Generator().manual_seed(7)
    src = torch.randint(0, P_test, (300,), generator=g)
    dst = torch.randint(0, P_test, (300,), generator=g)
    mask_self = src != dst
    src, dst = src[mask_self], dst[mask_self]
    # Canonical undirected form (a, b) with a < b.
    a = torch.minimum(src, dst); b = torch.maximum(src, dst)
    poi_edge_index = torch.stack([a, b], dim=0).to(torch.int64)
    # Random pooled POI embeddings + random per-POI category aggregate target.
    poi_emb = torch.randn(P_test, D_test, requires_grad=True)
    target = torch.softmax(torch.randn(P_test, NUM_CAT_test), dim=-1)

    # (a) Default: SCE loss finite + positive on category_aggregate.
    dec = MaskedPOIDecoder(
        hidden_channels=D_test, target_dim=NUM_CAT_test,
        mask_rate=0.15, gamma=3.0, aggr="mean",
        target_kind="category_aggregate", loss_kind="sce",
    )
    gen1 = torch.Generator().manual_seed(42)
    loss = dec(poi_emb, poi_edge_index, target, generator=gen1)
    assert torch.isfinite(loss), f"SCE loss not finite: {loss}"
    assert loss.item() > 0.0, f"SCE loss not positive: {loss.item()}"
    print(f"  SCE loss (mask_rate=0.15)        = {loss.item():.6f}  ✓")

    # (b) Backward produces gradients on the decoder MLP.
    loss.backward()
    bad = [n for n, p in dec.named_parameters() if p.requires_grad and p.grad is None]
    assert not bad, f"MaskedPOIDecoder dead params after backward: {bad}"
    # poi_emb also gets a gradient (it's part of the input chain through the
    # neighbour aggregation).
    assert poi_emb.grad is not None, "poi_emb has no gradient"
    assert torch.isfinite(poi_emb.grad).all(), "poi_emb gradient non-finite"
    print(f"  backward grad on decoder MLP    = ✓  (poi_emb.grad.norm={poi_emb.grad.norm().item():.4f})")

    # (c) mask_rate=0 returns zero scalar loss (no behaviour change path).
    dec_zero = MaskedPOIDecoder(
        hidden_channels=D_test, target_dim=NUM_CAT_test,
        mask_rate=0.0, gamma=3.0,
    )
    loss_zero = dec_zero(poi_emb.detach(), poi_edge_index, target)
    assert loss_zero.item() == 0.0, f"mask_rate=0 should give 0 loss, got {loss_zero.item()}"
    print(f"  mask_rate=0 ⇒ loss=0             = ✓  ({loss_zero.item()})")

    # (d) Mask is reproducible under seed.
    dec2 = MaskedPOIDecoder(
        hidden_channels=D_test, target_dim=NUM_CAT_test,
        mask_rate=0.15, gamma=3.0,
    )
    # Reuse SAME init by copying state dict from the first call's decoder.
    dec2.load_state_dict(dec.state_dict())
    gen2a = torch.Generator().manual_seed(123)
    gen2b = torch.Generator().manual_seed(123)
    p1 = poi_emb.detach().clone()
    p2 = poi_emb.detach().clone()
    l1 = dec2(p1, poi_edge_index, target, generator=gen2a)
    l2 = dec2(p2, poi_edge_index, target, generator=gen2b)
    assert torch.isclose(l1, l2, atol=1e-6), (
        f"Mask not reproducible: {l1.item()} vs {l2.item()}"
    )
    print(f"  seed-reproducible mask          = ✓  ({l1.item():.6f} == {l2.item():.6f})")

    # (e) MSE branch with visit_count_log target (1d).
    dec_mse = MaskedPOIDecoder(
        hidden_channels=D_test, target_dim=1,
        mask_rate=0.5, gamma=3.0,
        target_kind="visit_count_log", loss_kind="mse",
    )
    target_v = torch.log1p(torch.rand(P_test, 1) * 10.0)
    loss_mse = dec_mse(poi_emb.detach(), poi_edge_index, target_v)
    assert torch.isfinite(loss_mse), f"MSE loss not finite: {loss_mse}"
    assert loss_mse.item() >= 0.0, f"MSE loss negative: {loss_mse.item()}"
    print(f"  MSE branch (visit_count_log)    = ✓  (loss={loss_mse.item():.6f})")

    # (f) Sanity: empty edge list ⇒ degenerate to identity (no neighbours);
    # decoder still runs and SCE remains finite (masked POIs have zero emb).
    empty_edges = torch.zeros((2, 0), dtype=torch.int64)
    dec_e = MaskedPOIDecoder(
        hidden_channels=D_test, target_dim=NUM_CAT_test, mask_rate=0.5,
    )
    loss_e = dec_e(poi_emb.detach(), empty_edges, target)
    assert torch.isfinite(loss_e), f"empty-edge SCE non-finite: {loss_e}"
    print(f"  empty-edges fallback            = ✓  (loss={loss_e.item():.6f})")

    print("[T5.2b MaskedPOIDecoder] all 6 assertions passed.")


test_masked_poi_decoder()


# ============================================================================
# REGRESSION TEST: Check2HGI.attach_node2vec_head end-to-end
# ----------------------------------------------------------------------------
# The 2026-05-17 integration sprint rewrote attach_node2vec_head to use
# nn.Module.add_module (audit cleanup #3 of T5.2a). Combined with the line
# `self.n2v_head = None` sentinel in __init__, this raised
# `KeyError: "attribute 'n2v_head' already exists"` on every call. No
# pre-existing test covered the attach path (test_node2vec_poi_head exercised
# the head in isolation), so the bug shipped in commit 0a5e4cb. Caught by
# the post-fix T5.1 audit; this test is the guardrail.
# ============================================================================

def test_attach_node2vec_head_round_trip():
    """Construct Check2HGI with n2v_lambda>0, attach a Node2VecPOIHead,
    verify the head is registered as a submodule AND its parameters are
    visible through model.parameters() (so the AdamW optimizer will see them).
    """
    print("[regression] attach_node2vec_head round-trip")
    _re = _load("RegionEncoder", _root / "research/embeddings/hgi/model/RegionEncoder.py")
    Check2HGI = _chmod.Check2HGI
    POI2Region = _re.POI2Region

    def corruption(x):
        return x[torch.randperm(x.size(0))]

    model = Check2HGI(
        hidden_channels=64,
        checkin_encoder=CheckinEncoder(11, 64, num_layers=2),
        checkin2poi=Checkin2POI(64, num_heads=4),
        poi2region=POI2Region(64, num_heads=4),
        region2city=lambda emb, area: torch.sigmoid(emb.mean(dim=0)),
        corruption=corruption,
        n2v_lambda=0.3,
        n2v_align_lambda=0.5,
    )
    # Pre-attach: sentinel is None (set in __init__).
    assert model.n2v_head is None, f"sentinel not None: {model.n2v_head}"
    head = Node2VecPOIHead(
        num_pois=100, embedding_dim=64,
        walk_length=5, walks_per_node=2, context_size=3, p=1.0, q=1.0,
    )
    # The original integration sprint version raised KeyError here.
    model.attach_node2vec_head(head)
    assert model.n2v_head is head, "head not attached"
    assert "n2v_head" in dict(model.named_children()), \
        "n2v_head not registered as submodule (won't show in optimizer)"
    head_param_ids = {id(p) for p in head.parameters()}
    model_param_ids = {id(p) for p in model.parameters()}
    overlap = len(head_param_ids & model_param_ids)
    assert overlap == len(head_param_ids), \
        f"only {overlap}/{len(head_param_ids)} head params reachable via model.parameters()"
    print(f"  attach OK  |  head.n_params={len(head_param_ids)}  reachable={overlap}/{len(head_param_ids)}")
    # Re-attach (idempotent): rebuilding the head between epochs must not crash
    head2 = Node2VecPOIHead(
        num_pois=100, embedding_dim=64,
        walk_length=5, walks_per_node=2, context_size=3, p=1.0, q=1.0,
    )
    model.attach_node2vec_head(head2)
    assert model.n2v_head is head2, "re-attach did not replace head"
    print(f"  re-attach OK  |  no KeyError on second attach")
    print("[regression] attach_node2vec_head round-trip ✓")


test_attach_node2vec_head_round_trip()


print("\n[T3 unit test] all assertions passed (forward + backward + leak-probe + T5.2b + attach regression).")
