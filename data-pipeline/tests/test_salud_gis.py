"""TDD: REC-18 — health facilities per 1000 inhabitants via spatial join."""

import json

from conftest import write_csv

from donostia_pipeline.datasets import salud_gis
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
        {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [15, 5]}},
        {"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [16, 6]}},
    ],
}


def _ctx(tmp_path):
    write_csv(tmp_path, salud_gis.GEOJSON_NAME, json.dumps(POINTS))
    return BuildContext(
        raw_dir=tmp_path,
        barrio_ids={"a", "b"},
        code_to_id={},
        barrio_index=BarrioIndex(GEO),
        population_latest={"a": 2000, "b": 4000},
    )


def test_health_per_1000_normalized_by_population(tmp_path):
    (m,) = salud_gis.build(_ctx(tmp_path))
    assert m.id == "health_per_1000"
    assert m.unit == "por 1000 hab."
    assert m.theme == "health"
    assert m.time_grain == "snapshot"
    # a: 1 / 2000 * 1000 = 0.5 ; b: 2 / 4000 * 1000 = 0.5
    assert m.values["a"]["actual"] == 0.5
    assert m.values["b"]["actual"] == 0.5


def test_returns_nothing_without_a_spatial_index(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.barrio_index = None
    assert salud_gis.build(ctx) == []
