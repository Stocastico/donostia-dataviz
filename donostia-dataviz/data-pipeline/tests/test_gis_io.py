"""TDD: reading GIS GeoJSON/SHP files for the spatial join (gis_io)."""

import pytest

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


# Ground truth from the real educativos file: ETRS89/UTM30N (EPSG:25830) ↔ WGS84.
UTM = (579563.94, 4795335.57)
LONLAT = (-2.0189656149, 43.306647016)


def test_reproject_point_25830_to_4326():
    lon, lat = gis_io.reproject_point(*UTM)
    assert lon == pytest.approx(LONLAT[0], abs=1e-5)
    assert lat == pytest.approx(LONLAT[1], abs=1e-5)


def test_reproject_geometry_transforms_all_coords():
    geom = {"type": "Point", "coordinates": [UTM[0], UTM[1]]}
    out = gis_io.reproject_geometry(geom)
    assert out["type"] == "Point"
    assert out["coordinates"][0] == pytest.approx(LONLAT[0], abs=1e-5)
    poly = {"type": "Polygon", "coordinates": [[list(UTM), list(UTM), list(UTM)]]}
    rp = gis_io.reproject_geometry(poly)
    assert rp["coordinates"][0][0][0] == pytest.approx(LONLAT[0], abs=1e-5)


def test_load_shapefile_reprojects_and_keeps_attributes(tmp_path):
    import shapefile

    base = tmp_path / "pts"
    w = shapefile.Writer(str(base), shapeType=shapefile.POINT)
    w.field("name", "C")
    w.point(*UTM)
    w.record("A")
    w.close()

    fc = gis_io.load_shapefile(base, source_crs="EPSG:25830")
    assert fc["type"] == "FeatureCollection"
    feat = fc["features"][0]
    assert feat["geometry"]["coordinates"][0] == pytest.approx(LONLAT[0], abs=1e-5)
    assert feat["properties"]["name"] == "A"
