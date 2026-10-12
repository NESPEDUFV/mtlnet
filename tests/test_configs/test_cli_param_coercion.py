"""CLI KEY=VALUE coercion — Python-style booleans must not silently invert.

2026-06-12 code audit (P1-F): ``json.loads`` rejects ``True``/``False``/``None``
so they survived as strings, and ``bool("False") is True`` — every boolean
head/model/loss param passed Python-style (``--reg-head-param
freeze_alpha=False``) silently inverted. G's own ``freeze_alpha=True`` worked
only by truthiness coincidence. See
``docs/studies/mtl_improvement/CODE_AUDIT_2026-06-12.md``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_TRAIN = Path(__file__).resolve().parents[2] / "scripts" / "train.py"


def _load_train_module():
    spec = importlib.util.spec_from_file_location("_train_cli_test", _TRAIN)
    mod = importlib.util.module_from_spec(spec)
    # train.py imports project modules at import time; they resolve via the
    # repo pythonpath configured in pytest.ini/conftest.
    sys.modules["_train_cli_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def train_mod():
    return _load_train_module()


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("True", True),
        ("False", False),
        ("None", None),
        ("true", True),       # JSON style — worked before, must keep working
        ("false", False),
        ("null", None),
        ("0.1", 0.1),
        ("64", 64),
        ("aux", "aux"),       # bare strings stay strings
        ("gated", "gated"),
        ('"False"', "False"),  # explicitly-quoted string stays a string
    ],
)
def test_coerce_cli_value(train_mod, raw, expected):
    assert train_mod._coerce_cli_value(raw) == expected


def test_false_is_actually_false_downstream(train_mod):
    """The original failure mode: KEY=False must yield a falsy value."""
    overrides = train_mod._parse_key_value_overrides(
        ["freeze_alpha=False", "raw_embed_dim=64", "fusion_mode=aux"],
        "--reg-head-param",
    )
    assert overrides["freeze_alpha"] is False
    assert not overrides["freeze_alpha"]
    assert overrides["raw_embed_dim"] == 64
    assert overrides["fusion_mode"] == "aux"
