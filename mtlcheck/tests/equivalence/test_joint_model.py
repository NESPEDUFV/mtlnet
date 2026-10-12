"""The joint model, against the capacity figures the reference study published.

No transplant test here yet: constructing the reference joint the way its trainer constructs it
means replicating how the CLI assembles model_params, and a hand-built reference is a worse
comparand than none. What IS available is stronger than it looks — the capacity analysis in the
reference's POSTPONED.md quotes two exact parameter counts for Alabama, and an independent
reconstruction landing on both is not something that happens by accident.

Those counts are also the reason the architecture has to be right rather than merely plausible: the
open question about this system is whether the joint model's region advantage at the large states is
multi-task sharing or simply parameters, and the experiment that would settle it compares
capacity-matched arms.
"""

from __future__ import annotations

import pytest
import torch

from mtlcheck.models.joint import JointModel
from mtlcheck.models.stan import RegionHead

# docs/studies/closing_data/v18/POSTPONED.md §P1: "the joint model's region pathway carries 2.5-5.9x
# the dedicated baseline's parameters (alabama 2,466,542 vs 417,117)".
ALABAMA_JOINT_REGION_PATHWAY = 2_466_542
ALABAMA_DEDICATED_REGION_HEAD = 417_117

V18 = dict(
    n_categories=7, n_regions=1109,
    cat_head_params={"hidden_dim": 256, "num_layers": 4, "dropout": 0.1},
    reg_head_params={"d_model": 128, "shared_heads": 8, "shared_dropout": 0.1,
                     "private_heads": 4, "private_dropout": 0.3},
)


def _count(module) -> int:
    return sum(p.numel() for p in module.parameters())


@pytest.fixture(scope="module")
def model() -> JointModel:
    return JointModel(**V18)


@pytest.mark.equivalence
def test_region_pathway_capacity_matches_the_study(model: JointModel) -> None:
    """The study's PARTITION convention — shared (blocks + both final norms) + region-specific.

    Not "everything a region prediction passes through": `cat_final_ln` is not on the region logits'
    path, the category encoder IS upstream of them through cross-attention and is excluded, and the
    blocks are counted whole including category-stream weights. It is the reference's own
    parameter-group convention (`shared_parameters()` yields blocks + both final norms), which is
    what makes the comparison against POSTPONED meaningful — a bookkeeping ratio, not a causal one.
    """
    pathway = (_count(model.region_encoder) + _count(model.blocks)
               + _count(model.cat_final_ln) + _count(model.reg_final_ln)
               + _count(model.region_head))
    assert pathway == ALABAMA_JOINT_REGION_PATHWAY, (
        f"the joint region pathway has {pathway} parameters; the capacity analysis quotes "
        f"{ALABAMA_JOINT_REGION_PATHWAY}"
    )


@pytest.mark.equivalence
def test_dedicated_region_head_capacity_matches_the_study() -> None:
    head = RegionHead(embed_dim=64, num_classes=1109)
    assert _count(head) == ALABAMA_DEDICATED_REGION_HEAD


@pytest.mark.equivalence
def test_the_capacity_gap_is_the_one_the_study_reports(model: JointModel) -> None:
    """2.5-5.9x at Alabama — the ratio that makes capacity a live alternative explanation."""
    pathway = (_count(model.region_encoder) + _count(model.blocks)
               + _count(model.cat_final_ln) + _count(model.reg_final_ln)
               + _count(model.region_head))
    ratio = pathway / ALABAMA_DEDICATED_REGION_HEAD
    assert 2.5 <= ratio <= 6.0, f"capacity ratio {ratio:.2f} is outside the reported 2.5-5.9x band"


# ---------------------------------------------------------------- structure

@pytest.mark.equivalence
def test_parameter_partition_is_bijective_and_exhaustive(model: JointModel) -> None:
    """Per-head learning rates are applied to these groups; a leak between them mis-rates weights."""
    groups = (list(model.shared_parameters()) + list(model.category_parameters())
              + list(model.region_parameters()))
    assert sum(p.numel() for p in groups) == _count(model)
    assert len({id(p) for p in groups}) == len(groups), "a parameter appears in two groups"


@pytest.mark.equivalence
def test_the_private_tower_belongs_to_the_region_task(model: JointModel) -> None:
    """It reads the raw region window, so it is not shared and must not take the shared rate."""
    private = {id(p) for p in model.region_head.private_stan.parameters()}
    shared = {id(p) for p in model.shared_parameters()}
    assert not (private & shared)
    assert private <= {id(p) for p in model.region_parameters()}


@pytest.mark.equivalence
def test_forward_shapes(model: JointModel) -> None:
    cat, reg = model(torch.randn(4, 9, 64), torch.randn(4, 9, 64))
    assert cat.shape == (4, 7) and reg.shape == (4, 1109)


@pytest.mark.equivalence
def test_second_direction_reads_the_updated_first_stream() -> None:
    """`b` queries the `a` the block just wrote — not the `a` that entered it.

    Reordering those two lines gives a different architecture that trains and scores without
    complaint, so the dependency is asserted rather than left to the reading.
    """
    from mtlcheck.models.joint import CrossAttentionBlock

    torch.manual_seed(0)
    block = CrossAttentionBlock(dim=16, num_heads=2, dropout=0.0).eval()
    a, b = torch.randn(2, 9, 16), torch.randn(2, 9, 16)

    with torch.no_grad():
        _, b_out = block(a, b)
        # Recompute b's update from the PRE-update a; if the block used it, this would agree.
        a_update, _ = block.cross_ab(query=a, key=b, value=b)
        a_after = block.ln_a1(a + a_update)
        b_from_stale, _ = block.cross_ba(query=b, key=a, value=a)
        b_stale = block.ln_b2(block.ln_b1(b + b_from_stale)
                              + block.ffn_b(block.ln_b1(b + b_from_stale)))
        b_from_fresh, _ = block.cross_ba(query=b, key=a_after, value=a_after)
        b_fresh = block.ln_b2(block.ln_b1(b + b_from_fresh)
                              + block.ffn_b(block.ln_b1(b + b_from_fresh)))

    assert torch.allclose(b_out, b_fresh, atol=1e-6)
    assert not torch.allclose(b_out, b_stale, atol=1e-4), (
        "the two orderings agree here, so this test cannot detect the swap"
    )


@pytest.mark.equivalence
def test_missing_private_input_is_an_error(model: JointModel) -> None:
    """R12 — the reference zero-fills, turning a plumbing mistake into a quietly halved model."""
    with pytest.raises(ValueError, match="raw region window"):
        model.region_head(torch.randn(2, 9, 256), raw_region=None)


# ---------------------------------------------------------------- the recipe path

# The reference's own capacity audit puts the Alabama joint model at this total
# (articles/dissertacao/storyline/audit/capacity_baseline_experiment.md).
ALABAMA_JOINT_TOTAL = 4_197_621


def _from_recipe() -> JointModel:
    from mtlcheck.config import load_recipe
    recipe = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0)
    return JointModel(n_categories=7, n_regions=1109,
                      cat_head_params=dict(recipe.train.cat_head.params),
                      reg_head_params=dict(recipe.train.reg_head.params))


@pytest.mark.equivalence
def test_the_recipe_builds_the_reference_model() -> None:
    """Resolve the RECIPE and check the total — not hand-fed hyperparameters.

    Every other capacity test here feeds the right values directly, which is how a headless
    `joint.toml` once produced a category head half the size at triple the dropout while all of them
    passed. This one goes through the path a real run takes.
    """
    assert _count(_from_recipe()) == ALABAMA_JOINT_TOTAL


@pytest.mark.equivalence
def test_the_three_attention_head_counts_are_distinct_and_correct() -> None:
    """Head count is invisible to parameter counts — `nn.MultiheadAttention` has the same weights
    at any head count — so it needs its own assertion.

    Three different values coexist in this model and are easy to conflate: the cross-attention trunk
    runs 4, the dual tower's SHARED backbone runs 8 (that is where the model-level `num_heads` goes),
    and its PRIVATE backbone runs 4, matching the dedicated head it mirrors.
    """
    model = _from_recipe()
    assert model.blocks[0].cross_ab.num_heads == 4, "the trunk is not at the reference's 4 heads"
    assert model.blocks[0].cross_ba.num_heads == 4
    assert model.region_head.shared_stan.matching_attn.num_heads == 8
    assert model.region_head.private_stan.matching_attn.num_heads == 4


@pytest.mark.equivalence
def test_each_encoder_belongs_to_its_own_task() -> None:
    """Membership, not just coverage.

    The reference groups the category encoder with the category head at `cat_lr`, and the region
    encoder with the region head at `reg_lr`; only the blocks and final norms are shared. Putting
    both encoders in the shared group satisfies every bijectivity and exhaustiveness check while
    training the region encoder at a third of its rate.
    """
    model = _from_recipe()
    cat_encoder = {id(p) for p in model.category_encoder.parameters()}
    reg_encoder = {id(p) for p in model.region_encoder.parameters()}
    shared = {id(p) for p in model.shared_parameters()}

    assert cat_encoder <= {id(p) for p in model.category_parameters()}
    assert reg_encoder <= {id(p) for p in model.region_parameters()}
    assert not (cat_encoder & shared) and not (reg_encoder & shared)
    # What IS shared: the blocks and the two final norms, and nothing else.
    expected_shared = ({id(p) for p in model.blocks.parameters()}
                       | {id(p) for p in model.cat_final_ln.parameters()}
                       | {id(p) for p in model.reg_final_ln.parameters()})
    assert shared == expected_shared


@pytest.mark.equivalence
def test_an_active_prior_is_refused_rather_than_dropped() -> None:
    """A recipe asking for a live trajectory-flow prior must not silently build a prior-less head."""
    from mtlcheck.models.joint import JointModel as JM

    with pytest.raises(ValueError, match="ACTIVE trajectory-flow prior"):
        JM(n_categories=7, n_regions=1109,
           cat_head_params={"hidden_dim": 256, "num_layers": 4, "dropout": 0.1},
           reg_head_params={"freeze_alpha": False, "alpha_init": 0.5})
