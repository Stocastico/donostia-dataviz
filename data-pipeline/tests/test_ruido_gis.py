"""TDD: night-noise exposure GIS metric (datasets.ruido_gis)."""

from donostia_pipeline.datasets import ruido_gis
from donostia_pipeline.model import BuildContext
from donostia_pipeline.spatial import BarrioIndex


def _poly(x0, x1):
    return {"type": "Polygon", "coordinates": [[[x0, 0], [x1, 0], [x1, 10], [x0, 10], [x0, 0]]]}


FC = {
    "features": [
        {"properties": {"Isovalue": 50}, "geometry": _poly(0, 30)},
        {"properties": {"Isovalue": 55}, "geometry": _poly(0, 20)},
        {"properties": {"Isovalue": 65}, "geometry": _poly(0, 10)},
        {"properties": {"Isovalue": None}, "geometry": _poly(0, 5)},
    ],
}


def test_exposed_geoms_keeps_contours_at_or_above_threshold():
    geoms = ruido_gis._exposed_geoms(FC, 55)
    # 55 and 65 qualify; 50 is below; None is ignored
    assert len(geoms) == 2


def test_build_without_spatial_index_yields_nothing(tmp_path):
    ctx = BuildContext(raw_dir=tmp_path, barrio_ids=set(), code_to_id={})
    assert ruido_gis.build(ctx) == []


def test_build_without_zip_yields_nothing():
    geo = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"barrio_id": "a"}, "geometry": _poly(0, 10)},
    ]}
    ctx = BuildContext(raw_dir=__import__("pathlib").Path("/nonexistent"),
                       barrio_ids={"a"}, code_to_id={}, barrio_index=BarrioIndex(geo))
    assert ruido_gis.build(ctx) == []
