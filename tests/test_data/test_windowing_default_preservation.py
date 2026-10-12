"""Default-preservation tests for the windowing parameterization (P3 board).

HARD CONTRACT: any call to ``generate_sequences`` (and the check-in builder path)
that does NOT explicitly pass ``stride`` / ``min_sequence_length`` MUST produce
output byte-identical to the pre-parameterization behaviour:
    - stride defaults to ``None`` → step == window_size (non-overlapping windows)
    - min_sequence_length defaults to 5 (users with < 5 check-ins are dropped)

These guards protect the frozen v11/v14 substrates + §0.1 numbers (built at
stride-9 / min_seq-5). The new ``--stride 1`` / ``--min-seq 10`` knobs must be
strictly opt-in.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make ``src`` importable the same way the pipelines do.
REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from configs.model import InputsConfig  # noqa: E402
from data.inputs.core import (  # noqa: E402
    MIN_SEQUENCE_LENGTH,
    PADDING_VALUE,
    generate_sequences,
    convert_user_checkins_to_sequences,
)

WINDOW = InputsConfig.SLIDE_WINDOW  # 9


# --------------------------------------------------------------------------- #
# Reference implementation: a frozen copy of the PRE-CHANGE generate_sequences #
# behaviour (constant MIN_SEQUENCE_LENGTH=5, stride defaulting to window_size).#
# The new parameterized function with no extra args must match this exactly.   #
# --------------------------------------------------------------------------- #
def _legacy_generate_sequences(places_visited, window_size=WINDOW, pad_value=PADDING_VALUE, stride=None):
    if not places_visited or len(places_visited) < 5:  # frozen MIN_SEQUENCE_LENGTH
        return []
    sequences = []
    step = stride if stride is not None else window_size
    total = len(places_visited)
    for start_idx in range(0, total, step):
        history = places_visited[start_idx:start_idx + window_size]
        if len(history) < window_size:
            history = history + [pad_value] * (window_size - len(history))
        target_idx = start_idx + window_size
        if target_idx < total:
            target_poi = places_visited[target_idx]
        else:
            for j in range(len(history) - 1, -1, -1):
                if history[j] != pad_value:
                    target_poi = history[j]
                    history = history[:j] + history[j + 1:] + [pad_value]
                    break
            else:
                target_poi = pad_value
        if all(x == pad_value for x in history) or target_poi == pad_value:
            continue
        sequences.append(history + [target_poi])
    return sequences


@pytest.fixture
def histories():
    """A few users of varying length to exercise the windowing edges."""
    return {
        "short_below_min": list(range(4)),       # 4 < 5 → dropped
        "exactly_min": list(range(5)),           # 5 → one padded window
        "one_full_window": list(range(10)),      # 9 history + 1 target
        "multi_window": list(range(25)),         # several non-overlapping windows
        "empty": [],
    }


def test_constant_unchanged():
    assert MIN_SEQUENCE_LENGTH == 5


def test_default_matches_legacy(histories):
    """No stride / no min_sequence_length → byte-identical to legacy."""
    for name, hist in histories.items():
        assert generate_sequences(hist) == _legacy_generate_sequences(hist), name


def test_user_below_min_is_dropped(histories):
    assert generate_sequences(histories["short_below_min"]) == []


def test_non_overlapping_default_step(histories):
    """Default step == window_size (9): a 25-len history yields 3 windows."""
    seqs = generate_sequences(histories["multi_window"])
    # starts at 0, 9, 18 → 3 sequences; each length window+1
    assert len(seqs) == 3
    assert all(len(s) == WINDOW + 1 for s in seqs)
    # window starting at 0 is [0..8] history, target 9
    assert seqs[0] == list(range(9)) + [9]
    assert seqs[1] == list(range(9, 18)) + [18]


def test_min_sequence_length_override_drops_below_10(histories):
    """Passing min_sequence_length=10 drops users with < 10 check-ins."""
    # 5-len and 4-len users now dropped; 10-len still kept.
    assert generate_sequences(histories["exactly_min"], min_sequence_length=10) == []
    assert generate_sequences(histories["short_below_min"], min_sequence_length=10) == []
    assert generate_sequences(histories["one_full_window"], min_sequence_length=10) != []


def test_stride_1_yields_overlapping_windows(histories):
    """Passing stride=1 yields overlapping windows (one per start position)."""
    hist = histories["multi_window"]  # len 25
    overlap = generate_sequences(hist, stride=1)
    nonoverlap = generate_sequences(hist)
    assert len(overlap) > len(nonoverlap)
    # stride-1: start positions 0..(25-1); all-padding/None targets filtered.
    # Adjacent windows share window_size-1 history items.
    assert overlap[0][:WINDOW] == list(range(0, WINDOW))
    assert overlap[1][:WINDOW] == list(range(1, WINDOW + 1))


def test_stride_override_does_not_affect_default(histories):
    """Calling with stride=1 must not mutate the default-path result."""
    hist = histories["multi_window"]
    before = generate_sequences(hist)
    _ = generate_sequences(hist, stride=1)
    after = generate_sequences(hist)
    assert before == after == _legacy_generate_sequences(hist)


def _make_user_df(n_checkins, embedding_dim=4):
    """Build a single-user check-in DataFrame for the check-in builder path."""
    emb_cols = [str(i) for i in range(embedding_dim)]
    data = {
        "userid": [7] * n_checkins,
        "placeid": list(range(100, 100 + n_checkins)),
        "category": ["c"] * n_checkins,
    }
    rng = np.random.default_rng(0)
    for c in emb_cols:
        data[c] = rng.standard_normal(n_checkins).astype(np.float32)
    return pd.DataFrame(data), emb_cols


def test_checkin_builder_path_default_preserved():
    """convert_user_checkins_to_sequences with no stride/min args matches legacy
    sequence enumeration (the builder delegates to generate_sequences)."""
    df, emb_cols = _make_user_df(25, embedding_dim=4)
    results, poi_sequences = convert_user_checkins_to_sequences(
        df, emb_cols, WINDOW, 4
    )
    # POI sequences (sans trailing userid) must equal the legacy enumeration.
    legacy = _legacy_generate_sequences(df["placeid"].tolist())
    got = [seq[:-1] for seq in poi_sequences]  # strip userid
    assert got == legacy
    assert len(results) == len(legacy)


def test_checkin_builder_min_seq_override():
    """min_sequence_length=10 drops a 5-check-in user via the builder path."""
    df, emb_cols = _make_user_df(5, embedding_dim=4)
    results, poi_sequences = convert_user_checkins_to_sequences(
        df, emb_cols, WINDOW, 4, min_sequence_length=10
    )
    assert results == [] and poi_sequences == []


def test_checkin_builder_stride_1_overlaps():
    """stride=1 yields more sequences than the default through the builder."""
    df, emb_cols = _make_user_df(25, embedding_dim=4)
    _, default_seqs = convert_user_checkins_to_sequences(df, emb_cols, WINDOW, 4)
    _, overlap_seqs = convert_user_checkins_to_sequences(
        df, emb_cols, WINDOW, 4, stride=1
    )
    assert len(overlap_seqs) > len(default_seqs)
