"""TaskConfig / TaskSet / resolve_task_set unit tests."""

from __future__ import annotations

import dataclasses

import pytest

from tasks import (
    CHECK2HGI_NEXT_REGION,
    LEGACY_CATEGORY_NEXT,
    PrimaryMetric,
    TaskConfig,
    TaskSet,
    get_preset,
    resolve_task_set,
)
from tasks.presets import list_presets


def test_legacy_preset_has_expected_slot_names():
    assert LEGACY_CATEGORY_NEXT.task_a.name == "category"
    assert LEGACY_CATEGORY_NEXT.task_b.name == "next"
    # Legacy factory=None routes MTLnet to its hardcoded historical
    # defaults; this guarantees bit-exact preservation of the
    # pre-parameterisation head configuration.
    assert LEGACY_CATEGORY_NEXT.task_a.head_factory is None
    assert LEGACY_CATEGORY_NEXT.task_b.head_factory is None


def test_check2hgi_preset_has_placeholder_num_classes_for_regions():
    """task_b.num_classes stays 0 until resolve_task_set injects the
    actual region cardinality from the data pipeline. The test pins
    that the preset is shaped for runtime resolution, so call sites
    that forget to resolve are forced to fail loudly (zero-sized
    classifier rather than silent miscount)."""
    assert CHECK2HGI_NEXT_REGION.task_a.name == "next_category"
    assert CHECK2HGI_NEXT_REGION.task_a.num_classes == 7
    assert CHECK2HGI_NEXT_REGION.task_b.name == "next_region"
    assert CHECK2HGI_NEXT_REGION.task_b.num_classes == 0  # placeholder
    assert CHECK2HGI_NEXT_REGION.task_a.is_sequential is True
    assert CHECK2HGI_NEXT_REGION.task_b.is_sequential is True
    # Per-head primary metric differs — macro-F1 for 7-class category,
    # Acc@1 for ~10^3-class region (HMT-GRN / MGCL lineage).
    assert CHECK2HGI_NEXT_REGION.task_a.primary_metric == PrimaryMetric.F1
    assert CHECK2HGI_NEXT_REGION.task_b.primary_metric == PrimaryMetric.ACCURACY


def test_resolve_task_set_overrides_one_slot():
    resolved = resolve_task_set(CHECK2HGI_NEXT_REGION, task_b_num_classes=1109)
    assert resolved.task_b.num_classes == 1109
    assert resolved.task_a.num_classes == 7, "task_a must be left alone"
    assert resolved.task_b.name == "next_region", "name preserved"
    assert resolved.task_b.head_factory == CHECK2HGI_NEXT_REGION.task_b.head_factory


def test_resolve_task_set_no_change_returns_identity():
    """When no overrides are given, the original preset instance is
    returned — call sites can do ``preset is original`` for a
    fast-path no-op check."""
    resolved = resolve_task_set(LEGACY_CATEGORY_NEXT)
    assert resolved is LEGACY_CATEGORY_NEXT


def test_resolve_task_set_overrides_both_slots_simultaneously():
    resolved = resolve_task_set(
        LEGACY_CATEGORY_NEXT,
        task_a_num_classes=11,
        task_b_num_classes=13,
    )
    assert resolved.task_a.num_classes == 11
    assert resolved.task_b.num_classes == 13


def test_resolve_task_set_overrides_head_params():
    overrides_a = {"dropout": 0.42}
    overrides_b = {"num_layers": 8}
    resolved = resolve_task_set(
        LEGACY_CATEGORY_NEXT,
        task_a_head_params=overrides_a,
        task_b_head_params=overrides_b,
    )
    assert resolved.task_a.head_params == overrides_a
    assert resolved.task_b.head_params == overrides_b


def test_taskset_iter_yields_slot_a_then_b():
    slots = list(LEGACY_CATEGORY_NEXT)
    assert slots == [LEGACY_CATEGORY_NEXT.task_a, LEGACY_CATEGORY_NEXT.task_b]


def test_taskset_names_property():
    assert LEGACY_CATEGORY_NEXT.names == ("category", "next")
    assert CHECK2HGI_NEXT_REGION.names == ("next_category", "next_region")


def test_get_preset_known_name():
    assert get_preset(LEGACY_CATEGORY_NEXT.name) is LEGACY_CATEGORY_NEXT
    assert get_preset(CHECK2HGI_NEXT_REGION.name) is CHECK2HGI_NEXT_REGION


def test_get_preset_unknown_name_raises_keyerror_with_list():
    with pytest.raises(KeyError, match="Available"):
        get_preset("not_a_preset")


def test_list_presets_returns_sorted_unique():
    presets = list_presets()
    assert presets == sorted(presets)
    assert len(presets) == len(set(presets))
    assert LEGACY_CATEGORY_NEXT.name in presets
    assert CHECK2HGI_NEXT_REGION.name in presets


def test_taskconfig_is_frozen():
    """frozen=True is load-bearing: mutating at runtime would break the
    preset-as-constant contract and the `resolve_task_set` identity
    fast-path. Pinning this with an explicit assert prevents a silent
    regression if someone flips the decorator."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        LEGACY_CATEGORY_NEXT.task_a.num_classes = 99  # type: ignore[misc]


