"""Durability checks for the dissertation Appendix A artifact references."""

from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
APPENDICES = (
    REPO / "articles/dissertacao/src/chapters/apx_a_contributions.tex",
    REPO / "articles/dissertacao/src_clean/chapters/apx_a_contributions.tex",
)


def _live_paths(path: Path) -> list[str]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("%"):
            continue
        values.extend(re.findall(r"\\path\{([^}]+)\}", line))
    return values


def test_appendix_paths_are_durable_and_present():
    for appendix in APPENDICES:
        values = _live_paths(appendix)
        assert values, f"no live paths found in {appendix}"
        for value in values:
            assert not value.startswith("scripts/"), value
            assert not value.startswith("docs/studies/"), value
            assert (REPO / value).exists(), value
