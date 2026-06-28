"""Reading GIS GeoJSON files for the spatial join.

Kept separate from :mod:`spatial` (which is pure geometry) so file I/O stays
isolated and testable. Donostia's open-data GeoJSON resources are served in
WGS84 (lon/lat) even when the companion shapefile is EPSG:25830, so these can be
fed straight to :class:`spatial.BarrioIndex` with no reprojection. (SHP-only
sources — e.g. the noise grids — will need a convert/reproject step before this.)
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterator

import shapefile  # pyshp
from pyproj import Transformer

# Donostia/Gipuzkoa GIS is published in ETRS89 / UTM zone 30N.
DEFAULT_SOURCE_CRS = "EPSG:25830"
WGS84 = "EPSG:4326"


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


# --- reprojection (for SHP-only sources, served in EPSG:25830) ---------------


@lru_cache(maxsize=8)
def _transformer(source_crs: str) -> Transformer:
    # always_xy=True → (x=lon/easting, y=lat/northing) order, matching GeoJSON.
    return Transformer.from_crs(source_crs, WGS84, always_xy=True)


def reproject_point(x: float, y: float, source_crs: str = DEFAULT_SOURCE_CRS) -> tuple[float, float]:
    """Reproject a single coordinate to WGS84 ``(lon, lat)``."""
    return _transformer(source_crs).transform(x, y)


def reproject_geometry(geom: dict, source_crs: str = DEFAULT_SOURCE_CRS) -> dict:
    """Return a copy of a GeoJSON geometry with all coordinates in WGS84."""
    tr = _transformer(source_crs)

    def walk(coords):
        # A coordinate pair is [x, y(, z…)] of numbers; otherwise recurse.
        if coords and isinstance(coords[0], (int, float)):
            lon, lat = tr.transform(coords[0], coords[1])
            return [lon, lat]
        return [walk(c) for c in coords]

    return {"type": geom["type"], "coordinates": walk(geom["coordinates"])}


def load_shapefile(path, source_crs: str = DEFAULT_SOURCE_CRS) -> dict:
    """Read a shapefile (pyshp) into a GeoJSON ``FeatureCollection`` in WGS84.

    ``path`` may be the base path or the ``.shp``. Attributes are kept as the
    feature properties. Use this for SHP-only sources (e.g. the noise grids).
    """
    reader = shapefile.Reader(str(path))
    features = []
    for sr in reader.shapeRecords():
        geom = reproject_geometry(sr.shape.__geo_interface__, source_crs)
        features.append({
            "type": "Feature",
            "properties": dict(sr.record.as_dict()),
            "geometry": geom,
        })
    return {"type": "FeatureCollection", "features": features}
