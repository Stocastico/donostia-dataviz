"""Reading GIS GeoJSON files for the spatial join.

Kept separate from :mod:`spatial` (which is pure geometry) so file I/O stays
isolated and testable. Donostia's open-data GeoJSON resources are served in
WGS84 (lon/lat) even when the companion shapefile is EPSG:25830, so these can be
fed straight to :class:`spatial.BarrioIndex` with no reprojection. (SHP-only
sources — e.g. the noise grids — will need a convert/reproject step before this.)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator


def load_geojson(path: Path) -> dict:
    """Load a GeoJSON file (tolerating a UTF-8 BOM)."""
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def iter_point_features(geojson: dict) -> Iterator[tuple[float, float, dict]]:
    """Yield ``(lon, lat, properties)`` for each Point feature; skip the rest."""
    for feature in geojson.get("features", []):
        geom = feature.get("geometry") or {}
        if geom.get("type") != "Point":
            continue
        lon, lat = geom["coordinates"][0], geom["coordinates"][1]
        yield lon, lat, feature.get("properties", {})


def point_coords(features: list[dict]) -> list[tuple[float, float]]:
    """Extract ``(lon, lat)`` tuples from a list of Point features."""
    out = []
    for feature in features:
        geom = feature.get("geometry") or {}
        if geom.get("type") == "Point":
            out.append((geom["coordinates"][0], geom["coordinates"][1]))
    return out
