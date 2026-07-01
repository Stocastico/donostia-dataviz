"""Tests for barrio geometry normalization and display-name overrides."""

from __future__ import annotations

import json
from pathlib import Path

from donostia_pipeline.geometry import normalize_barrios


def _write_raw_council_geojson(path: Path, features: list[dict]) -> None:
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8-sig",
    )


def _feature(kod_auzo: str, name: str) -> dict:
    return {
        "type": "Feature",
        "properties": {"KodAuzo": kod_auzo, "name": name},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
        },
    }


def test_antigua_display_name_is_antiguo(tmp_path):
    raw_path = tmp_path / "auzoak.json"
    _write_raw_council_geojson(raw_path, [_feature("4", "ANTIGUA")])

    result = normalize_barrios(raw_path)

    props = result["features"][0]["properties"]
    assert props["barrio_id"] == "antigua"
    assert props["name"] == "Antiguo"


def test_unmapped_barrio_falls_back_to_title_case(tmp_path):
    raw_path = tmp_path / "auzoak.json"
    _write_raw_council_geojson(raw_path, [_feature("1", "AIETE")])

    result = normalize_barrios(raw_path)

    props = result["features"][0]["properties"]
    assert props["barrio_id"] == "aiete"
    assert props["name"] == "Aiete"
