"""Unit tests for the build manifest (drives "datos descargados el ..." on the site)."""

from __future__ import annotations

import json
import re

from donostia_pipeline.build import _write_manifest


def test_write_manifest_stamps_todays_date(tmp_path):
    path = tmp_path / "manifest.json"
    _write_manifest(path)

    payload = json.loads(path.read_text())
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload["generated_at"])
