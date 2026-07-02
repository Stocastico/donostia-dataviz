"""Shared test helpers for dataset modules.

Dataset modules read a CSV from ``ctx.raw_dir``; these helpers let a test drop a
small fixture CSV into a temp raw dir and build a matching ``BuildContext``,
so each dataset's transform is unit-tested without any network or real data.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from donostia_pipeline.model import BuildContext


def write_csv(raw_dir: Path, name: str, rows: str) -> None:
    """Write a fixture CSV (``rows`` is the full file text) into ``raw_dir``."""
    (raw_dir / name).write_text(rows.lstrip("\n"), encoding="utf-8")


@pytest.fixture
def make_ctx(tmp_path):
    """Factory: ``make_ctx(code_to_id)`` -> BuildContext over ``tmp_path``."""

    def _make(code_to_id: dict[str, str]) -> BuildContext:
        return BuildContext(
            raw_dir=tmp_path,
            barrio_ids=set(code_to_id.values()),
            code_to_id=code_to_id,
        )

    return _make
