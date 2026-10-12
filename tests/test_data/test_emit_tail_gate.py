"""M1 tail-gate (stride-1 OOB tail-window suppression).

The stride-1 overlap build emits ~window_size OOB "tail" windows per user, all
targeting the user's LAST POI on near-all-padding histories — a label-distribution
skew (not a leak). `emit_tail=False` (auto at stride==1) suppresses them. Default
`emit_tail=True` keeps the legacy behaviour byte-identically.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from data.inputs.core import generate_sequences, MIN_SEQUENCE_LENGTH  # noqa: E402
from data.inputs.builders import _resolve_emit_tail  # noqa: E402


def test_resolve_emit_tail_auto_gates_only_stride1():
    # AUTO (None): emit everywhere except stride==1
    assert _resolve_emit_tail(None, None) is True   # non-overlap default
    assert _resolve_emit_tail(None, 9) is True
    assert _resolve_emit_tail(None, 1) is False      # the gate
    # explicit overrides win
    assert _resolve_emit_tail(True, 1) is True
    assert _resolve_emit_tail(False, None) is False


def test_stride1_gate_drops_only_oob_tail_windows():
    places = list(range(15))  # one user, 15 visits
    full = generate_sequences(places, stride=1, emit_tail=True)
    gated = generate_sequences(places, stride=1, emit_tail=False)
    # gate drops the OOB tail windows (target_idx >= n): ~window_size-1 of them
    assert len(gated) < len(full)
    dropped = [s for s in full if s not in gated]
    # every dropped window targets the user's LAST POI (the M1 skew)
    assert all(s[-1] == places[-1] for s in dropped)
    # every surviving window has a genuine in-history next-visit target
    assert all(s[-1] in places for s in gated)


def test_non_overlap_default_byte_identical_to_emit_tail_true():
    # The default (emit_tail=True) must NOT change the frozen non-overlap build.
    for n in (5, 9, 10, 18, 27, 40):
        places = list(range(n))
        assert generate_sequences(places) == generate_sequences(places, emit_tail=True)


def test_gate_is_noop_at_non_overlap_when_explicitly_false_only_drops_tail():
    # At non-overlap, the LAST window per user is an OOB tail window; the default
    # MUST keep it (it is how the user's final/last-POI target is produced).
    places = list(range(20))  # stride-9 -> starts 0,9,18; start=18 is OOB tail
    full = generate_sequences(places)  # default emit_tail=True
    assert any(s[-1] == places[-1] for s in full), "non-overlap must keep last-POI target"


def test_min_sequence_length_still_respected_with_gate():
    short = list(range(MIN_SEQUENCE_LENGTH - 1))
    assert generate_sequences(short, stride=1, emit_tail=False) == []
