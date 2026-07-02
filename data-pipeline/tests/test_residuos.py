"""TDD: recycling-rate annual indicator (datasets.residuos)."""

from donostia_pipeline.datasets import residuos


def _row(year, tipo, ambito, kg):
    return {"Año": year, "Tipo de recogida": tipo, "Ambito": ambito, "Total (kg)": kg}


ROWS = [
    _row("2020", "Recogida selectiva", "URBANO", "30"),
    _row("2020", "Autocompostaje", "", "10"),
    _row("2020", "Rechazo", "URBANO", "60"),
    _row("2020", "Recogida selectiva", "INDUSTRIAL", "1000"),  # excluded
    _row("2021", "Recogida selectiva", "URBANO", "50"),
    _row("2021", "Rechazo", "URBANO", "50"),
]


def test_recycling_rate_per_year_excludes_industrial():
    (ind,) = residuos.recycling_rate_from_rows(ROWS)
    assert ind.id == "recycling_rate"
    assert ind.unit == "%"
    assert ind.theme == "environment"
    # 2020: (30 selectiva + 10 compost) / (40 + 60 rechazo) = 40 %
    assert ind.values["2020"]["value"] == 40.0
    # 2021: 50 / (50 + 50) = 50 %
    assert ind.values["2021"]["value"] == 50.0


def test_years_sorted_and_value_rounded():
    (ind,) = residuos.recycling_rate_from_rows(
        ROWS + [_row("2019", "Recogida selectiva", "URBANO", "1"),
                _row("2019", "Rechazo", "URBANO", "2")]
    )
    assert sorted(ind.values) == ["2019", "2020", "2021"]
    assert ind.values["2019"]["value"] == 33.33  # 1/3


def test_incomplete_year_without_rechazo_is_dropped():
    # A partial year (only recycled reported, no Rechazo) would be a bogus 100%.
    (ind,) = residuos.recycling_rate_from_rows(
        ROWS + [_row("2099", "Recogida selectiva", "URBANO", "5")]
    )
    assert "2099" not in ind.values
