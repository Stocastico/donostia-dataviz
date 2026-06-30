"""Integration tests over the committed ``web/src/data`` outputs.

These run fully offline (no raw downloads) so CI can verify the published data
honours the contract in ``docs/DATA-CONTRACT.md``.
"""

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[2] / "web" / "src" / "data"


@pytest.fixture(scope="module")
def geojson():
    return json.loads((DATA_DIR / "barrios.geojson").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def barrio_ids(geojson):
    return {f["properties"]["barrio_id"] for f in geojson["features"]}


@pytest.fixture(scope="module")
def registry():
    return json.loads((DATA_DIR / "metrics.json").read_text(encoding="utf-8"))


def test_geometry_has_unique_barrio_ids(geojson, barrio_ids):
    feats = geojson["features"]
    assert len(barrio_ids) == len(feats), "duplicate barrio_id in geometry"
    assert len(feats) == 19, "expected 19 official barrios"
    for f in feats:
        assert f["properties"].get("name"), "barrio missing display name"


def test_registry_matches_metric_files(registry):
    live = {e["id"] for e in registry if e["status"] == "live"}
    files = {p.stem.removeprefix("metric_") for p in DATA_DIR.glob("metric_*.json")}
    assert live == files, f"registry/live mismatch: {live ^ files}"


def test_metrics_join_to_geometry(registry, barrio_ids):
    for entry in registry:
        if entry["status"] != "live":
            continue
        metric = json.loads(
            (DATA_DIR / f"metric_{entry['id']}.json").read_text(encoding="utf-8")
        )
        assert metric["periods"] == sorted(set(metric["periods"]))
        period_set = set(metric["periods"])
        categories = metric.get("categories", [])
        if metric["kind"] == "categorical":
            assert categories, f"{entry['id']}: categorical metric needs categories"
        for barrio_id, by_period in metric["values"].items():
            assert barrio_id in barrio_ids, f"{entry['id']}: orphan {barrio_id}"
            for period, value in by_period.items():
                assert period in period_set, f"{entry['id']}: stray period {period}"
                if value is not None and metric["kind"] == "sequential":
                    assert value >= 0, f"{entry['id']}: negative {barrio_id}/{period}"
                if value is not None and metric["kind"] == "categorical":
                    assert value == int(value) and 0 <= value < len(categories), (
                        f"{entry['id']}: bad category index {value} for {barrio_id}"
                    )


def test_registry_entries_have_required_fields(registry):
    required = {"id", "label", "theme", "geoGrain", "timeGrain", "source", "status"}
    for entry in registry:
        assert required <= set(entry), f"missing fields in {entry.get('id')}"


# --- city-grain time series (series_*.json) ---


@pytest.fixture(scope="module")
def series_registry():
    path = DATA_DIR / "series.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def test_series_registry_matches_files(series_registry):
    listed = {e["id"] for e in series_registry}
    files = {p.stem.removeprefix("series_") for p in DATA_DIR.glob("series_*.json")}
    assert listed == files, f"series registry/files mismatch: {listed ^ files}"


def test_series_axes_are_well_formed(series_registry):
    valid_months = {str(m) for m in range(1, 13)}
    for entry in series_registry:
        series = json.loads(
            (DATA_DIR / f"series_{entry['id']}.json").read_text(encoding="utf-8")
        )
        assert series["years"] == sorted(set(series["years"]))
        year_set = set(series["years"])
        for year, by_month in series["values"].items():
            assert year in year_set, f"{entry['id']}: stray year {year}"
            for month in by_month:
                assert month in valid_months, f"{entry['id']}: bad month {month}"
