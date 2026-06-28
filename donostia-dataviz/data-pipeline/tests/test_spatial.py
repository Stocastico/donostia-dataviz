"""TDD: spatial join of GIS data onto the reference barrios (spatial)."""

from donostia_pipeline import spatial

# Three adjacent unit squares as a synthetic reference geometry.
#   a = [0,10]×[0,10]   b = [10,20]×[0,10]   c = [20,30]×[0,10]
def _square(x0, x1):
    return [[[x0, 0], [x1, 0], [x1, 10], [x0, 10], [x0, 0]]]


GEO = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"barrio_id": "a"}, "geometry": {"type": "Polygon", "coordinates": _square(0, 10)}},
        {"type": "Feature", "properties": {"barrio_id": "b"}, "geometry": {"type": "Polygon", "coordinates": _square(10, 20)}},
        {"type": "Feature", "properties": {"barrio_id": "c"}, "geometry": {"type": "Polygon", "coordinates": _square(20, 30)}},
    ],
}


def test_assign_point_to_containing_barrio():
    idx = spatial.BarrioIndex(GEO)
    assert idx.assign_point(5, 5) == "a"
    assert idx.assign_point(15, 5) == "b"
    assert idx.assign_point(25, 5) == "c"


def test_point_outside_all_barrios_is_none():
    idx = spatial.BarrioIndex(GEO)
    assert idx.assign_point(100, 100) is None
    assert idx.assign_point(5, 50) is None


def test_count_points_returns_all_barrios_with_zero_default():
    idx = spatial.BarrioIndex(GEO)
    counts = idx.count_points([(5, 5), (6, 6), (15, 5), (1000, 1000)])
    # a=2, b=1, c=0 (every barrio present; outside point dropped)
    assert counts == {"a": 2, "b": 1, "c": 0}


def test_barrio_ids_property():
    idx = spatial.BarrioIndex(GEO)
    assert set(idx.barrio_ids) == {"a", "b", "c"}
