"""TDD: security indicators (HU-1) — perceived insecurity + real crime."""

from donostia_pipeline.datasets import seguridad


def _prow(zona, year, grado, val):
    return {"zona_id": zona, "zona": "z", "year": year, "grado": grado,
            "familias_miles": val, "source": "Eustat"}


def test_perception_share_computed_per_zone():
    rows = [
        _prow("70", "2024", "Total", "173.4"),
        _prow("70", "2024", "Ningun_problema", "136.2"),
        _prow("00", "2024", "Total", "100.0"),
        _prow("00", "2024", "Ningun_problema", "80.0"),
    ]
    by_id = {i.id: i for i in seguridad.perception_indicators_from_rows(rows)}
    # Donostia: (173.4-136.2)/173.4*100 = 21.5
    assert by_id["perception_insecurity_donostia"].values["2024"]["value"] == 21.5
    assert by_id["perception_insecurity_euskadi"].values["2024"]["value"] == 20.0


def test_perception_skips_year_without_total_or_ningun():
    rows = [_prow("70", "2019", "Algun_problema", "19.6")]  # sin Total ni Ningún
    out = seguridad.perception_indicators_from_rows(rows)
    assert out == []  # sin datos utilizables → sin indicador


def test_perception_metadata():
    rows = [_prow("70", "2024", "Total", "100"),
            _prow("70", "2024", "Ningun_problema", "78.5")]
    (ind,) = seguridad.perception_indicators_from_rows(rows)
    assert ind.unit == "%"
    assert ind.theme == "security"


def test_crime_indicators_levels_only():
    rows = [
        {"indicator_id": "infracciones_penales", "year": "2021",
         "value": "12705", "source": "euskadi.eus"},
        {"indicator_id": "tasa_criminalidad_1000", "year": "2021",
         "value": "67.54", "source": "euskadi.eus"},
        {"indicator_id": "var_interanual_pct", "year": "2024",
         "value": "11.8", "source": "prensa"},   # no es nivel → se ignora
    ]
    by_id = {i.id: i for i in seguridad.crime_indicators_from_rows(rows)}
    assert set(by_id) == {"crime_infractions", "crime_rate_1000"}
    assert by_id["crime_infractions"].values["2021"]["value"] == 12705.0
    assert by_id["crime_rate_1000"].theme == "security"


def test_crime_keeps_per_row_source():
    rows = [{"indicator_id": "infracciones_penales", "year": "2020",
             "value": "10640", "source": "euskadi.eus 2022"}]
    (ind,) = seguridad.crime_indicators_from_rows(rows)
    assert ind.values["2020"]["source"] == "euskadi.eus 2022"


def test_crime_gipuzkoa_indicator_from_total_row_only():
    rows = [
        {"provincia": "Gipuzkoa", "tipologia": "TOTAL INFRACCIONES PENALES",
         "year": "2019", "infracciones": "25016", "source": "Min. Interior"},
        {"provincia": "Gipuzkoa", "tipologia": "TOTAL INFRACCIONES PENALES",
         "year": "2024", "infracciones": "33425", "source": "Min. Interior"},
        {"provincia": "Gipuzkoa", "tipologia": "5.1.-Hurtos",   # no es el total
         "year": "2024", "infracciones": "8023", "source": "Min. Interior"},
    ]
    (ind,) = seguridad.crime_gipuzkoa_indicators_from_rows(rows)
    assert ind.id == "crime_infractions_gipuzkoa"
    assert ind.theme == "security"
    assert ind.values["2019"]["value"] == 25016.0
    assert ind.values["2024"]["value"] == 33425.0
    assert len(ind.values) == 2                  # solo filas TOTAL


def test_crime_gipuzkoa_label_flags_province():
    rows = [{"provincia": "Gipuzkoa", "tipologia": "TOTAL INFRACCIONES PENALES",
             "year": "2010", "infracciones": "24260", "source": "Min. Interior"}]
    (ind,) = seguridad.crime_gipuzkoa_indicators_from_rows(rows)
    assert "Gipuzkoa" in ind.label   # el nombre deja claro que es provincia


def test_build_indicators_reads_real_curated_files():
    """Integración: lee los CSV curados reales del repo."""
    inds = {i.id: i for i in seguridad.build_indicators()}
    assert "perception_insecurity_donostia" in inds
    # anclas reales: 1989 ≈ 35.4 %, 2024 ≈ 21.5 %
    don = inds["perception_insecurity_donostia"].values
    assert don["1989"]["value"] == 35.4
    assert don["2024"]["value"] == 21.5
    assert "crime_rate_1000" in inds
    # serie oficial de Gipuzkoa (provincia) también cableada
    assert "crime_infractions_gipuzkoa" in inds
    assert inds["crime_infractions_gipuzkoa"].values["2024"]["value"] == 33425.0
