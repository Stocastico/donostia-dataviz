"""TDD: schools-per-1000 GIS metric via spatial join (datasets.educacion_gis)."""

import json

from conftest import write_csv

from donostia_pipeline.datasets import educacion_gis
from donostia_pipeline.model import BuildContext
from donostia_pipeline.spatial import BarrioIndex


def _square(x0, x1):
    return [[[x0, 0], [x1, 0], [x1, 10], [x0, 10], [x0, 0]]]


GEO = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"barrio_id": "a"}, "geometry": {"type": "Polygon", "coordinates": _square(0, 10)}},
        {"type": "Feature", "properties": {"barrio_id": "b"}, "geometry": {"type": "Polygon", "coordinates": _square(10, 20)}},
    ],
}

POINTS = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [5, 5]}},
        {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [6, 6]}},
        {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [15, 5]}},
    ],
}


def _ctx(tmp_path):
    write_csv(tmp_path, "educativos.json", json.dumps(POINTS))
    return BuildContext(
        raw_dir=tmp_path,
        barrio_ids={"a", "b"},
        code_to_id={},
        barrio_index=BarrioIndex(GEO),
        population_latest={"a": 4000, "b": 1000},
    )


def test_schools_per_1000_normalized_by_population(tmp_path):
    (m,) = educacion_gis.build(_ctx(tmp_path))
    assert m.id == "schools_per_1000"
    assert m.unit == "per 1000 ab."
    assert m.theme == "education"
    assert m.time_grain == "snapshot"
    # a: 2 schools / 4000 * 1000 = 0.5 ; b: 1 / 1000 * 1000 = 1.0
    assert m.values["a"]["actual"] == 0.5
    assert m.values["b"]["actual"] == 1.0


def test_returns_nothing_without_a_spatial_index(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.barrio_index = None
    assert educacion_gis.build(ctx) == []
