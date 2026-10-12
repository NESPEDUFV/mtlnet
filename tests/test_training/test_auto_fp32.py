"""Coverage for the auto-fp32 default (`_auto_fp32_for_large_c` in mtl_cv).

A large-C MTL run on Ampere+ with NO explicit precision env should default to fp32
(bf16 grad-NaN / fp16 overflow at large reg logits). Explicit MTL_DISABLE_AMP /
MTL_AUTOCAST_BF16 always wins; small states keep the fp16 default. The AL parity
harness can't exercise this (AL is small-C and the harness sets MTL_DISABLE_AMP), so
this is pinned by a deterministic table.
"""

from training.runners.mtl_cv import _auto_fp32_for_large_c, _AUTO_FP32_REG_CLASS_THRESHOLD

AMPERE = 8  # sm_80+ (A40 = sm_86)


def test_large_c_states_auto_fp32_on_ampere():
    for c in (4703, 6553, 8501):  # FL, TX, CA
        assert _auto_fp32_for_large_c(c, "cuda", AMPERE, {}) is True, c


def test_small_c_states_keep_fp16_default():
    for c in (520, 1109, 1547):  # Istanbul, AL, AZ — all < threshold
        assert _auto_fp32_for_large_c(c, "cuda", AMPERE, {}) is False, c
    # threshold is exclusive
    assert _auto_fp32_for_large_c(_AUTO_FP32_REG_CLASS_THRESHOLD, "cuda", AMPERE, {}) is False
    assert _auto_fp32_for_large_c(_AUTO_FP32_REG_CLASS_THRESHOLD + 1, "cuda", AMPERE, {}) is True


def test_explicit_precision_env_always_wins():
    # explicit fp32, explicit bf16, AND explicit fp16-opt-in (=0) all disable the auto path
    for env in ({"MTL_DISABLE_AMP": "1"}, {"MTL_DISABLE_AMP": "0"}, {"MTL_AUTOCAST_BF16": "1"}):
        assert _auto_fp32_for_large_c(8501, "cuda", AMPERE, env) is False, env


def test_non_cuda_and_pre_ampere_never_auto():
    assert _auto_fp32_for_large_c(8501, "cpu", None, {}) is False
    assert _auto_fp32_for_large_c(8501, "mps", None, {}) is False
    assert _auto_fp32_for_large_c(8501, "cuda", 7, {}) is False   # Volta/Turing
    assert _auto_fp32_for_large_c(8501, "cuda", None, {}) is False


def test_none_class_count_is_safe():
    assert _auto_fp32_for_large_c(None, "cuda", AMPERE, {}) is False
