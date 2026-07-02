"""TDD: disposable income per barrio + gender income gap (datasets.renta)."""

from conftest import write_csv

from donostia_pipeline.datasets import renta

# Anyo,CodBarrio,DesBarrio,RentaPer_Total,RentaPer_Hombres,RentaPer_Mujeres
FIXTURE = """
Anyo,CodBarrio,DesBarrio,RentaPer_Total,RentaPer_Hombres,RentaPer_Mujeres
2020,9,GROS,20000,24000,16000
2021,9,GROS,22000,26000,18000
2020,8,EGIA,18000,19000,17000
2019,99,DESCONOCIDO,9999,9999,9999
"""

CODE_TO_ID = {"9": "gros", "8": "egia"}


def _build(make_ctx):
    write_csv(make_ctx({}).raw_dir, "renta_barrio.csv", FIXTURE)
    metrics = {m.id: m for m in renta.build(make_ctx(CODE_TO_ID))}
    return metrics


def test_income_total_per_barrio_per_year(make_ctx):
    income = _build(make_ctx)["income_total"]
    assert income.periods == ["2020", "2021"]
    assert income.values["gros"] == {"2020": 20000.0, "2021": 22000.0}
    assert income.values["egia"] == {"2020": 18000.0}


def test_gender_gap_is_percentage_of_male_income(make_ctx):
    gap = _build(make_ctx)["income_gender_gap"]
    # (24000 - 16000) / 24000 * 100 = 33.33
    assert round(gap.values["gros"]["2020"], 2) == 33.33
    assert gap.unit == "%"


def test_unknown_barrio_code_is_dropped(make_ctx):
    income = _build(make_ctx)["income_total"]
    assert "2019" not in income.periods
    for by_period in income.values.values():
        assert "2019" not in by_period
