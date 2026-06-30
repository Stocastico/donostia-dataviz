"""TDD: Inside Airbnb density metric + monthly review-activity series (REC-4)."""

import csv
import gzip
import io

from donostia_pipeline.datasets import airbnb
from donostia_pipeline.model import BuildContext
from donostia_pipeline.spatial import BarrioIndex


def _square(x0, x1):
    return [[[x0, 0], [x1, 0], [x1, 10], [x0, 10], [x0, 0]]]


GEO = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"barrio_id": "a"},
         "geometry": {"type": "Polygon", "coordinates": _square(0, 10)}},
        {"type": "Feature", "properties": {"barrio_id": "b"},
         "geometry": {"type": "Polygon", "coordinates": _square(10, 20)}},
    ],
}

# l1,l2 in barrio a; l3 in barrio b; l4 outside the city (dropped).
LISTINGS = [
    {"id": "l1", "longitude": "5", "latitude": "5"},
    {"id": "l2", "longitude": "6", "latitude": "6"},
    {"id": "l3", "longitude": "15", "latitude": "5"},
    {"id": "l4", "longitude": "99", "latitude": "99"},
]
REVIEWS = [
    {"listing_id": "l1", "date": "2024-01-15"},
    {"listing_id": "l2", "date": "2024-01-20"},
    {"listing_id": "l3", "date": "2024-03-01"},
    {"listing_id": "l4", "date": "2024-05-01"},  # outside city → ignored
    {"listing_id": "l1", "date": "2023-07-09"},
]


def _write_gz(path, fieldnames, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
        fh.write(buf.getvalue())


def _ctx(tmp_path):
    _write_gz(tmp_path / airbnb.LISTINGS_GZ, ["id", "longitude", "latitude"], LISTINGS)
    _write_gz(tmp_path / airbnb.REVIEWS_GZ, ["listing_id", "date"], REVIEWS)
    return BuildContext(
        raw_dir=tmp_path,
        barrio_ids={"a", "b"},
        code_to_id={},
        barrio_index=BarrioIndex(GEO),
        population_latest={"a": 4000, "b": 1000},
    )


def test_density_is_spatial_joined_and_per_capita(tmp_path):
    (m,) = airbnb.build(_ctx(tmp_path))
    assert m.id == "airbnb_density"
    assert m.theme == "tourism"
    assert m.kind == "sequential"
    assert m.time_grain == "snapshot"
    # a: 2 listings / 4000 * 1000 = 0.5 ; b: 1 / 1000 * 1000 = 1.0 ; l4 dropped.
    assert m.values["a"][airbnb.SNAPSHOT] == 0.5
    assert m.values["b"][airbnb.SNAPSHOT] == 1.0


def test_reviews_series_counts_city_listings_by_month(tmp_path):
    (s,) = airbnb.build_series(_ctx(tmp_path))
    assert s.id == "airbnb_reviews"
    assert s.kind == "month-year"
    assert s.years == ["2023", "2024"]
    assert s.values["2024"]["1"] == 2.0  # l1 + l2 in Jan 2024
    assert s.values["2024"]["3"] == 1.0  # l3
    assert "5" not in s.values["2024"]   # l4 (outside city) excluded
    assert s.values["2023"]["7"] == 1.0


def test_no_spatial_index_yields_nothing(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.barrio_index = None
    assert airbnb.build(ctx) == []
    assert airbnb.build_series(ctx) == []
