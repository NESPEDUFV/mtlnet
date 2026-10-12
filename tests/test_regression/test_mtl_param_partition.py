"""Parameter-partition invariant for every MTL variant.

Motivates: `docs/issues/check2hgi/MTL_PARAM_PARTITION_BUG.md`.

The gradient-surgery losses (`PCGrad`, `CAGrad`, `AlignedMTL`) assign
``p.grad`` only for parameters in
``shared_parameters() ∪ task_specific_parameters()``. Anything outside
that union is silently never trained — no error, no warning, just
zero-gradient parameters for the whole run.

These tests enforce the invariant

    shared_ids & task_ids      == ∅
    shared_ids | task_ids      == all_ids

on **every registered MTL variant**, with feature flags that install
extra `nn.Parameter`s (AdaShare on the baseline, MTLoRA on DSelect-K
— always-on) turned ON. A new feature-flag that introduces a
`nn.Parameter` without updating the partition iterators will fail one
of these tests.
"""

from __future__ import annotations

import pytest
import torch

from tests.test_integration.conftest import (
    EMBED_DIM,
    NUM_CLASSES,
    SEQ_LEN,
    seed_everything,
)


def _build_mtlnet(use_adashare: bool = False):
    from models.mtlnet import MTLnet

    return MTLnet(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
        use_adashare=use_adashare,
    )


def _build_mtlnet_cgc():
    from models.mtl.mtlnet_cgc.model import MTLnetCGC

    return MTLnetCGC(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
    )


def _build_mtlnet_mmoe():
    from models.mtl.mtlnet_mmoe.model import MTLnetMMoE

    return MTLnetMMoE(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
    )


def _build_mtlnet_ple():
    from models.mtl.mtlnet_ple.model import MTLnetPLE

    return MTLnetPLE(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
    )


def _build_mtlnet_dselectk():
    """DSelectK under the check2HGI preset — the LoRA / α-skip branch
    activates on non-legacy task_sets, which is where the partition bug
    actually shows up. Legacy-task_set DSelectK deliberately excludes
    those params (they are dead weight with no gradient path)."""
    from models.mtl.mtlnet_dselectk.model import MTLnetDSelectK
    from tasks import CHECK2HGI_NEXT_REGION
    from tasks.presets import resolve_task_set

    task_set = resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=NUM_CLASSES,
    )
    return MTLnetDSelectK(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
        task_set=task_set,
    )


def _build_mtlnet_crossattn():
    from models.mtl.mtlnet_crossattn.model import MTLnetCrossAttn

    return MTLnetCrossAttn(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
    )


# Region-task cardinality for the check2HGI-preset variants below — distinct
# from NUM_CLASSES so a cat/reg head mix-up would shape-error loudly.
N_REGIONS = 37

_COMMON_PARAMS = dict(
    feature_size=EMBED_DIM,
    shared_layer_size=256,
    num_classes=NUM_CLASSES,
    num_heads=8,
    num_layers=4,
    seq_length=SEQ_LEN,
    num_shared_layers=4,
)


def _resolve_check2hgi_task_set(**kwargs):
    from tasks import CHECK2HGI_NEXT_REGION
    from tasks.presets import resolve_task_set

    return resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=N_REGIONS,
        **kwargs,
    )


def _dualtower_head_params(prior_on: bool = False) -> dict:
    head_params = {"raw_embed_dim": EMBED_DIM, "fusion_mode": "aux"}
    if not prior_on:
        # Champion G runs prior-OFF: alpha becomes a buffer (absent from
        # .parameters()), which the partition must tolerate.
        head_params.update({"freeze_alpha": True, "alpha_init": 0.0})
    return head_params


def _build_dualtower(model_name: str, prior_on: bool = False, catpriv: bool = False):
    """Builds the dual-tower family as the trainer does (create_model +
    resolve_task_set), with the private STAN tower actually installed —
    the partition bug surface is the head-held private tower, so building
    with a default head would not exercise it."""
    from models.registry import create_model

    ts_kwargs = dict(
        task_b_head_factory="next_stan_flow_dualtower",
        task_b_head_params=_dualtower_head_params(prior_on),
    )
    if catpriv:
        # G′: the cat head gets its own private tower too.
        ts_kwargs.update(
            task_a_head_factory="next_stan_flow_dualtower",
            task_a_head_params=_dualtower_head_params(prior_on),
        )
    task_set = _resolve_check2hgi_task_set(**ts_kwargs)
    return create_model(model_name, task_set=task_set, **_COMMON_PARAMS)


def _build_registry_variant(model_name: str):
    """Plain check2HGI-preset build for the remaining registered crossattn
    variants (swiglu / mult / xstitch / crossstitch)."""
    from models.registry import create_model

    task_set = _resolve_check2hgi_task_set()
    return create_model(model_name, task_set=task_set, **_COMMON_PARAMS)


BUILDERS = [
    ("mtlnet", lambda: _build_mtlnet(use_adashare=False)),
    ("mtlnet_adashare_on", lambda: _build_mtlnet(use_adashare=True)),
    ("mtlnet_cgc", _build_mtlnet_cgc),
    ("mtlnet_mmoe", _build_mtlnet_mmoe),
    ("mtlnet_ple", _build_mtlnet_ple),
    ("mtlnet_dselectk", _build_mtlnet_dselectk),
    ("mtlnet_crossattn", _build_mtlnet_crossattn),
    # Champion-G family (mtl_improvement study; the T4.1 audit found the
    # gradient-surgery losses silently collapse when the partition misses
    # the head-held private tower — these entries are the regression guard).
    (
        "mtlnet_crossattn_dualtower_G",  # champion G: aux fusion, prior-OFF
        lambda: _build_dualtower("mtlnet_crossattn_dualtower", prior_on=False),
    ),
    (
        "mtlnet_crossattn_dualtower_prior_on",
        lambda: _build_dualtower("mtlnet_crossattn_dualtower", prior_on=True),
    ),
    (
        "mtlnet_crossattn_dualtower_catpriv",  # G′ (demoted, still registered)
        lambda: _build_dualtower(
            "mtlnet_crossattn_dualtower_catpriv", prior_on=False, catpriv=True
        ),
    ),
    (
        "mtlnet_crossattn_dualtower_swiglu",  # combo F
        lambda: _build_dualtower("mtlnet_crossattn_dualtower_swiglu", prior_on=False),
    ),
    (
        "mtlnet_crossattn_swiglu",
        lambda: _build_registry_variant("mtlnet_crossattn_swiglu"),
    ),
    (
        "mtlnet_crossattn_mult",
        lambda: _build_registry_variant("mtlnet_crossattn_mult"),
    ),
    (
        "mtlnet_crossattn_xstitch",
        lambda: _build_registry_variant("mtlnet_crossattn_xstitch"),
    ),
    (
        "mtlnet_crossstitch",
        lambda: _build_registry_variant("mtlnet_crossstitch"),
    ),
]


@pytest.mark.parametrize("name,builder", BUILDERS, ids=[b[0] for b in BUILDERS])
def test_param_partition_complete(name: str, builder):
    """``shared_parameters ∪ task_specific_parameters == all_parameters``.

    Enforced on every MTL variant — a new nn.Parameter introduced by a
    feature flag must be assigned to one bucket so PCGrad / CAGrad /
    AlignedMTL can route its gradient. See
    docs/issues/check2hgi/MTL_PARAM_PARTITION_BUG.md.
    """
    seed_everything()
    model = builder()
    shared_ids = {id(p) for p in model.shared_parameters()}
    task_ids = {id(p) for p in model.task_specific_parameters()}
    all_ids = {id(p) for p in model.parameters()}
    missing = all_ids - (shared_ids | task_ids)
    assert not missing, (
        f"{name}: {len(missing)} parameter(s) absent from "
        f"shared ∪ task_specific — gradient-surgery losses will "
        f"silently never train them. Offending names: "
        f"{[n for n, p in model.named_parameters() if id(p) in missing]}"
    )


@pytest.mark.parametrize("name,builder", BUILDERS, ids=[b[0] for b in BUILDERS])
def test_param_partition_disjoint(name: str, builder):
    """``shared_parameters ∩ task_specific_parameters == ∅``.

    PCGrad sets ``p.grad`` once from the shared path and once from the
    task-specific path — if a parameter is in both, the task-specific
    assignment overwrites the surgery-adjusted shared grad, silently.
    """
    seed_everything()
    model = builder()
    shared_ids = {id(p) for p in model.shared_parameters()}
    task_ids = {id(p) for p in model.task_specific_parameters()}
    overlap = shared_ids & task_ids
    assert not overlap, (
        f"{name}: {len(overlap)} parameter(s) present in BOTH "
        f"shared and task_specific iterators."
    )


def _forward_one_step(model) -> tuple[torch.Tensor, torch.Tensor]:
    """Minimal forward pair used by the gradient micro-check."""
    cat_in = torch.randn(4, 1, EMBED_DIM, requires_grad=False)
    next_in = torch.randn(4, SEQ_LEN, EMBED_DIM, requires_grad=False)
    out_cat, out_next = model((cat_in, next_in))
    return out_cat, out_next


def test_adashare_logits_receive_gradient_under_surgery_loss():
    """AdaShare gates must train under PCGrad after the partition fix.

    Before the fix, ``adashare_logits`` sat outside both iterators;
    PCGrad's ``p.grad = g`` loop skipped it. After the fix, the gate
    parameter should be in ``task_specific_parameters`` and receive a
    gradient when PCGrad runs its backward.
    """
    seed_everything()
    from losses.pcgrad import PCGrad

    model = _build_mtlnet(use_adashare=True)
    pcgrad = PCGrad(n_tasks=2, device=torch.device("cpu"))

    out_cat, out_next = _forward_one_step(model)
    # Simple dummy targets
    y_cat = torch.randint(0, NUM_CLASSES, (out_cat.size(0),))
    y_next = torch.randint(0, NUM_CLASSES, (out_next.size(0),))
    ce = torch.nn.CrossEntropyLoss()
    losses = torch.stack([ce(out_cat, y_cat), ce(out_next, y_next)])

    shared_params = list(model.shared_parameters())
    task_params = list(model.task_specific_parameters())
    pcgrad.backward(
        losses=losses,
        shared_parameters=shared_params,
        task_specific_parameters=task_params,
    )

    assert model.adashare_logits.grad is not None, (
        "adashare_logits.grad is None after PCGrad.backward — the "
        "parameter is not in shared ∪ task_specific, so PCGrad skipped "
        "it. This is MTL_PARAM_PARTITION_BUG."
    )
    assert model.adashare_logits.grad.abs().sum().item() > 0, (
        "adashare_logits received a gradient of exactly zero — "
        "possible numerical edge case, but more likely the param is "
        "not reaching the loss."
    )


def test_dselectk_lora_and_skip_receive_gradient_under_surgery_loss():
    """LoRA A/B and ``skip_alpha`` must train under PCGrad after the fix.

    DSelectK gates the LoRA + α-skip path on ``task_set is not
    LEGACY_CATEGORY_NEXT`` (see ``mtlnet_dselectk/model.py:139``). The
    legacy preset bypasses LoRA entirely — exercising the non-legacy
    ``CHECK2HGI_NEXT_REGION`` preset is the only way the affected
    parameters appear in the autograd graph.
    """
    seed_everything()
    from losses.pcgrad import PCGrad
    from models.mtl.mtlnet_dselectk.model import MTLnetDSelectK
    from tasks import CHECK2HGI_NEXT_REGION
    from tasks.presets import resolve_task_set

    task_set = resolve_task_set(
        CHECK2HGI_NEXT_REGION,
        task_b_num_classes=NUM_CLASSES,
    )
    model = MTLnetDSelectK(
        feature_size=EMBED_DIM,
        shared_layer_size=256,
        num_classes=NUM_CLASSES,
        num_heads=8,
        num_layers=4,
        seq_length=SEQ_LEN,
        num_shared_layers=4,
        task_set=task_set,
    )

    # Both slots are sequential under the check2HGI preset → category
    # input is [B, T, D] just like next.
    cat_in = torch.randn(4, SEQ_LEN, EMBED_DIM)
    next_in = torch.randn(4, SEQ_LEN, EMBED_DIM)
    out_cat, out_next = model((cat_in, next_in))

    y_cat = torch.randint(0, NUM_CLASSES, (out_cat.size(0),))
    y_next = torch.randint(0, NUM_CLASSES, (out_next.size(0),))
    ce = torch.nn.CrossEntropyLoss()
    losses = torch.stack([ce(out_cat, y_cat), ce(out_next, y_next)])

    pcgrad = PCGrad(n_tasks=2, device=torch.device("cpu"))
    pcgrad.backward(
        losses=losses,
        shared_parameters=list(model.shared_parameters()),
        task_specific_parameters=list(model.task_specific_parameters()),
    )

    # Every LoRA / α-skip parameter must have received a gradient.
    # lora_B_* is zero-init so its *value* starts at 0, but after the
    # fix the parameter is enumerated in task_specific_parameters and
    # PCGrad's .grad = g loop populates it.
    for param_name in (
        "lora_A_cat",
        "lora_B_cat",
        "lora_A_next",
        "lora_B_next",
        "skip_alpha_cat",
        "skip_alpha_next",
    ):
        param = getattr(model, param_name)
        if isinstance(param, torch.nn.Linear):
            param = param.weight
        assert param.grad is not None, (
            f"{param_name}.grad is None after PCGrad.backward — the "
            f"parameter is not in shared ∪ task_specific. This is "
            f"MTL_PARAM_PARTITION_BUG."
        )


def test_dualtower_private_tower_receives_gradient_under_surgery_loss():
    """Champion G's private STAN tower must receive gradients under PCGrad.

    The T4.1 audit (mtl_improvement, 2026-06-09) found that under the
    dual-tower, gradient-surgery losses apply their *combined/reweighted*
    gradient only to ``shared_parameters()`` — the private tower (inside
    ``task_specific_parameters()``) trains at unit task weight by design.
    That semantic limitation is documented
    (``docs/results/mtl_improvement/T4_audit_and_verdict.md``); what must
    NEVER happen is the silent failure mode this file guards: a private-tower
    parameter falling outside shared ∪ task_specific and receiving NO
    gradient at all. This test pins gradient *coverage* for every
    private-tower parameter of the champion-G build.
    """
    seed_everything()
    from losses.pcgrad import PCGrad

    model = _build_dualtower("mtlnet_crossattn_dualtower", prior_on=False)

    cat_in = torch.randn(4, SEQ_LEN, EMBED_DIM)
    next_in = torch.randn(4, SEQ_LEN, EMBED_DIM)
    out_cat, out_next = model((cat_in, next_in))

    y_cat = torch.randint(0, NUM_CLASSES, (out_cat.size(0),))
    y_reg = torch.randint(0, N_REGIONS, (out_next.size(0),))
    ce = torch.nn.CrossEntropyLoss()
    losses = torch.stack([ce(out_cat, y_cat), ce(out_next, y_reg)])

    pcgrad = PCGrad(n_tasks=2, device=torch.device("cpu"))
    pcgrad.backward(
        losses=losses,
        shared_parameters=list(model.shared_parameters()),
        task_specific_parameters=list(model.task_specific_parameters()),
    )

    missing = [
        name
        for name, p in model.next_poi.named_parameters()
        if p.requires_grad and p.grad is None
    ]
    assert not missing, (
        f"{len(missing)} private-tower/reg-head parameter(s) received no "
        f"gradient under PCGrad.backward — outside shared ∪ task_specific "
        f"(MTL_PARAM_PARTITION_BUG on the champion-G dual-tower): {missing}"
    )
