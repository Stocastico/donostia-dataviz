"""TDD: derived rent-to-income housing-stress metric (datasets.housing_tension)."""

from donostia_pipeline.datasets import housing_tension
from donostia_pipeline.model import Metric


def _metric(id_, values):
    return Metric(
        id=id_, label=id_, unit="x", kind="sequential", theme="t", source="s",
        geo_grain="barrio", time_grain="year",
        periods=sorted({p for v in values.values() for p in v}), values=values,
    )


# rent €/m²/month and per-capita annual income, by barrio/year.
RENT = _metric("rent_eur_m2", {
    "gros": {"2020": 12.0},
    "egia": {"2020": 15.0, "2022": 10.0},  # 2022 income missing → no tension
})
INCOME = _metric("income_total", {
    "gros": {"2020": 24000.0},
    "egia": {"2020": 18000.0, "2021": 20000.0},  # 2021 rent missing → no tension
})


def test_tension_is_annual_rent_share_of_income():
    (m,) = housing_tension.build_from_metrics({"rent_eur_m2": RENT, "income_total": INCOME})
    assert m.id == "housing_tension"
    assert m.theme == "housing"
    assert m.unit == "%"
    assert m.periods == ["2020"]
    # 12 €/m² × 12 months × 30 m²/person ÷ 24000 × 100 = 18.0
    assert m.values["gros"]["2020"] == 18.0
    # 15 × 12 × 30 ÷ 18000 × 100 = 30.0
    assert m.values["egia"]["2020"] == 30.0


def test_year_present_in_only_one_input_is_skipped():
    (m,) = housing_tension.build_from_metrics({"rent_eur_m2": RENT, "income_total": INCOME})
    assert "2021" not in m.values.get("egia", {})  # rent missing
    assert "2022" not in m.values.get("egia", {})  # income missing


def test_missing_inputs_yield_no_metric():
    assert housing_tension.build_from_metrics({"rent_eur_m2": RENT}) == []
    assert housing_tension.build_from_metrics({}) == []
