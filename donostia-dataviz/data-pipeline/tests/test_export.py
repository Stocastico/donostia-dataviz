"""TDD: tidy CSV export of metrics and series (export_tables)."""

from donostia_pipeline import export_tables
from donostia_pipeline.model import Metric, Series

METRIC = Metric(
    id="m", label="M", unit="u", kind="sequential", theme="t", source="src",
    geo_grain="barrio", time_grain="year", periods=["2020", "2021"],
    values={"gros": {"2020": 1.0, "2021": 2.0}, "egia": {"2020": 3.0}},
)
NAMES = {"gros": "Gros", "egia": "Egia"}

SERIES = Series(
    id="s", label="S", unit="u", theme="t", source="src",
    years=["2020"], values={"2020": {"1": 10.0, "2": 20.0}},
)


def test_metric_long_rows_are_tidy_and_sorted():
    rows = export_tables.metric_long_rows([METRIC], NAMES)
    # sorted by (metric_id, barrio_id, period); egia before gros
    assert [(r["barrio_id"], r["period"], r["value"]) for r in rows] == [
        ("egia", "2020", 3.0),
        ("gros", "2020", 1.0),
        ("gros", "2021", 2.0),
    ]
    assert rows[0] == {
        "metric_id": "m", "label": "M", "theme": "t", "unit": "u",
        "barrio_id": "egia", "barrio_name": "Egia", "period": "2020", "value": 3.0,
    }


def test_series_long_rows_sorted_by_month_numerically():
    s2 = Series(id="s", label="S", unit="u", theme="t", source="src",
                years=["2020"], values={"2020": {"10": 1.0, "2": 2.0}})
    rows = export_tables.series_long_rows([s2])
    assert [r["month"] for r in rows] == ["2", "10"]  # numeric, not lexical


def test_series_long_row_shape():
    rows = export_tables.series_long_rows([SERIES])
    assert rows[0] == {
        "series_id": "s", "label": "S", "theme": "t", "unit": "u",
        "year": "2020", "month": "1", "value": 10.0,
    }
