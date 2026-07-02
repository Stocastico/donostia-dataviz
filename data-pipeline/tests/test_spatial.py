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


def _poly(x0, x1):
    return {"type": "Polygon", "coordinates": _square(x0, x1)}


# S1 spans a/b halves (value 100); S2 covers a fully (value 200); c untouched.
SOURCES = [(_poly(5, 15), 100.0), (_poly(0, 10), 200.0)]


def test_areal_interpolate_mean_is_area_weighted():
    idx = spatial.BarrioIndex(GEO)
    out = idx.areal_interpolate(SOURCES, mode="mean")
    # a: (50*100 + 100*200)/(50+100) = 166.67 ; b: (50*100)/50 = 100 ; c: no data
    assert round(out["a"], 2) == 166.67
    assert round(out["b"], 2) == 100.0
    assert out["c"] is None


def test_areal_interpolate_sum_distributes_by_overlap_fraction():
    idx = spatial.BarrioIndex(GEO)
    out = idx.areal_interpolate(SOURCES, mode="sum")
    # a: 100*(50/100) + 200*(100/100) = 250 ; b: 100*(50/100) = 50 ; c: 0
    assert round(out["a"], 2) == 250.0
    assert round(out["b"], 2) == 50.0
    assert out["c"] == 0.0


def test_coverage_fraction_is_share_of_barrio_area_covered():
    idx = spatial.BarrioIndex(GEO)
    # one source covering a's left half (x 0–5) and all of b
    out = idx.coverage_fraction([_poly(0, 5), _poly(10, 20)])
    assert round(out["a"], 3) == 0.5   # half of a
    assert round(out["b"], 3) == 1.0   # all of b
    assert out["c"] == 0.0             # untouched barrio present as 0


def test_coverage_fraction_unions_overlapping_sources():
    idx = spatial.BarrioIndex(GEO)
    # two overlapping sources over a must not double-count past 100%
    out = idx.coverage_fraction([_poly(0, 8), _poly(4, 10)])
    assert round(out["a"], 3) == 1.0


def test_coverage_fraction_empty_sources_all_zero():
    idx = spatial.BarrioIndex(GEO)
    assert idx.coverage_fraction([]) == {"a": 0.0, "b": 0.0, "c": 0.0}


def test_rate_per_1000():
    counts = {"a": 10, "b": 1, "c": 0}
    pop = {"a": 5000, "b": 2000, "c": 0}
    rates = spatial.rate_per_1000(counts, pop)
    assert rates["a"] == 2.0  # 10/5000*1000
    assert rates["b"] == 0.5
    assert rates["c"] is None  # zero/unknown population → undefined
