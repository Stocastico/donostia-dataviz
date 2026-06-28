"""TDD: reading GIS GeoJSON files for the spatial join (gis_io)."""

from donostia_pipeline import gis_io

GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature",
         "properties": {"Tipo": "EDUCATIVO", "name": "A"},
         "geometry": {"type": "Point", "coordinates": [-2.01, 43.30]}},
        {"type": "Feature",
         "properties": {"Tipo": "EDUCATIVO", "name": "B"},
         "geometry": {"type": "Point", "coordinates": [-1.98, 43.32]}},
        {"type": "Feature",  # non-point geometry is skipped by iter_point_features
         "properties": {"name": "poly"},
         "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}},
    ],
}


def test_load_geojson_handles_bom(tmp_path):
    p = tmp_path / "x.json"
    p.write_text("﻿" + '{"type":"FeatureCollection","features":[]}', encoding="utf-8")
    assert gis_io.load_geojson(p) == {"type": "FeatureCollection", "features": []}


def test_iter_point_features_yields_lonlat_and_props():
    pts = list(gis_io.iter_point_features(GEOJSON))
    assert len(pts) == 2  # polygon skipped
    (lon, lat, props) = pts[0]
    assert (lon, lat) == (-2.01, 43.30)
    assert props["name"] == "A"


def test_point_coords():
    coords = gis_io.point_coords(GEOJSON["features"])
    assert coords == [(-2.01, 43.30), (-1.98, 43.32)]
