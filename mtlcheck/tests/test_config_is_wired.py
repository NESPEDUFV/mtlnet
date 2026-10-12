"""Every config field must reach behaviour. Two got shipped that did not.

`SubstrateConfig.repr_seed` was declared and read by nothing, so two builds labelled "seed 42"
differed and the manifest recorded a seed that had no effect. One commit later the round-2 audit
found `DataConfig.min_sequence_length` and `.stride` in the same state.

The defect is invisible to every other kind of test: the code runs, the numbers look plausible, and
the field's default happens to match what the call sites hard-code. So this file tests the property
directly — change a field, and something observable must change.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest
import torch

from mtlcheck.config import DataConfig, SubstrateConfig


# Deliberately uneven: a threshold between these lengths must exclude some users and keep others.
# An earlier version of this fixture gave every eligible user the same length, so raising the
# threshold excluded nobody and the test failed against correct code.
USER_LENGTHS = (9, 11, 13, 15, 17, 19)


def _corpus() -> pd.DataFrame:
    rows = []
    for user, length in enumerate(USER_LENGTHS):
        for i in range(length):
            rows.append({"userid": user, "placeid": 100 + (user * 7 + i) % 40,
                         "category": f"c{i % 3}",
                         "datetime": pd.Timestamp("2020-01-01") + pd.Timedelta(hours=i)})
    return pd.DataFrame(rows)


def test_min_sequence_length_changes_the_windows() -> None:
    """The field must exclude users, not sit in the dataclass looking authoritative."""
    from mtlcheck.data import sequences

    frame = _corpus()
    lenient = sequences.build_from(frame, DataConfig(min_sequence_length=10))
    strict = sequences.build_from(frame, dataclasses.replace(DataConfig(), min_sequence_length=16))

    assert len(strict.target) < len(lenient.target), (
        "raising min_sequence_length excluded nobody — the field is not reaching the builder")
    assert set(np.unique(strict.userid)) < set(np.unique(lenient.userid))


def test_stride_reaches_the_builder() -> None:
    """v18 only defines stride 1, so the proof that the field is read is that another value refuses.

    A silently ignored stride would accept 3 and quietly produce stride-1 windows — which is exactly
    the failure this file exists for.
    """
    from mtlcheck.data import sequences

    with pytest.raises(NotImplementedError, match="stride"):
        sequences.build_from(_corpus(), dataclasses.replace(DataConfig(), stride=3))


def test_window_reaches_the_builder() -> None:
    from mtlcheck.data import sequences

    narrow = sequences.build_from(_corpus(), dataclasses.replace(DataConfig(), window=4))
    assert narrow.history.shape[1] == 4


def test_repr_seed_determines_the_build() -> None:
    """Two builds at one seed must agree; two seeds must not. The field is the contract."""
    from mtlcheck.substrate.model import Check2HGI
    from mtlcheck.substrate.training import init_fingerprint
    from mtlcheck import seeding

    places, regions, dim = 40, 8, 64
    args = (torch.zeros(places, dim), torch.zeros(2, 4, dtype=torch.long), torch.ones(4), 7)

    def fingerprint(seed: int) -> str:
        seeding.seed_everything(seed)
        return init_fingerprint(Check2HGI(11, places, regions, *args,
                                          SubstrateConfig(engine="t", repr_seed=seed)))

    assert fingerprint(42) == fingerprint(42), "same seed gave two different initialisations"
    assert fingerprint(42) != fingerprint(43), "the seed does not reach initialisation"


def test_every_dataconfig_field_is_read_somewhere() -> None:
    """A field nobody reads is a lie in a dataclass. Fail on new ones.

    Deliberately crude — a grep over the package. It cannot prove a field is used *correctly*, only
    that it is mentioned, which is precisely the bar the two defects failed.
    """
    from pathlib import Path

    package = Path(__file__).resolve().parents[1] / "src" / "mtlcheck"
    source = "\n".join(p.read_text() for p in package.rglob("*.py") if p.name != "config.py")

    unread = [f.name for f in dataclasses.fields(DataConfig) if f.name not in source]
    assert not unread, f"declared in DataConfig and read nowhere: {unread}"

    unread = [f.name for f in dataclasses.fields(SubstrateConfig) if f.name not in source]
    assert not unread, f"declared in SubstrateConfig and read nowhere: {unread}"
