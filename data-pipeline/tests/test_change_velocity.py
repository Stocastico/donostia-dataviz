"""TDD: derived per-barrio velocity-of-change metrics (datasets.change_velocity)."""

from donostia_pipeline.datasets import change_velocity
from donostia_pipeline.model import Metric


def _metric(id_, values, label="base"):
    return Metric(
        id=id_, label=label, unit="x", kind="sequential", theme="t", source="s",
        geo_grain="barrio", time_grain="year",
        periods=sorted({p for v in values.values() for p in v}), values=values,
    )


def test_level_metric_rate_is_percent_per_year():
    # income grows by a constant 1000/yr from a window mean of 21500 (2016..2019)
    income = _metric("income_total", {
        "altza": {"2016": 20000.0, "2017": 21000.0, "2018": 22000.0, "2019": 23000.0},
    })
    (m,) = change_velocity.build_from_metrics({"income_total": income})
    assert m.id == "velocity_income_total"
    assert m.kind == "diverging"
    assert m.theme == "change"
    assert m.unit == "%/año"
    assert m.periods == ["2016–2019"]
    # slope 1000/yr ÷ mean 21500 × 100 = 4.651 %/yr
    assert m.values["altza"]["2016–2019"] == 4.651


def test_pp_metric_rate_is_points_per_year_and_can_be_negative():
    foreign = _metric("pct_foreign", {
        # declining 0.5 pp/yr
        "gros": {"2016": 10.0, "2017": 9.5, "2018": 9.0},
    })
    (m,) = change_velocity.build_from_metrics({"pct_foreign": foreign})
    assert m.id == "velocity_pct_foreign"
    assert m.unit == "p.p./año"
    assert m.values["gros"]["2016–2018"] == -0.5  # diverging allows negatives


def test_short_series_and_pre_window_years_are_excluded():
    income = _metric("income_total", {
        "altza": {"2016": 20000.0, "2017": 21000.0},      # only 2 points → dropped
        "egia": {"2010": 1.0, "2011": 2.0, "2012": 3.0},  # all before window → dropped
    })
    assert change_velocity.build_from_metrics({"income_total": income}) == []


def test_period_window_uses_latest_year_seen():
    pop = _metric("population", {
        "amaraberri": {"2016": 100.0, "2017": 110.0, "2018": 120.0, "2024": 200.0},
    })
    (m,) = change_velocity.build_from_metrics({"population": pop})
    assert m.periods == ["2016–2024"]


def test_missing_base_metrics_yield_nothing():
    assert change_velocity.build_from_metrics({}) == []
