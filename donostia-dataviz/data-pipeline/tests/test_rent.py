"""TDD: rent €/m² per barrio from the EMA T8.3 table (datasets.rent)."""

from donostia_pipeline.datasets import rent

CODE_TO_ID = {"3": "amaraberri", "5": "anorga", "9": "gros"}

# Mimics openpyxl rows of sheet T8.3: col1 = 3-digit barrio code, col2 = name,
# cols 3.. = annual €/m² for 2016..2024 ("-"/"." = no data).
ROWS = [
    ("Renta mensual media…", None, None, 2016, 2017, 2018),  # header noise
    ("Distrito", None, "01", 12.57, 12.11, 12.68),  # not a barrio (col1 empty)
    (None, "003", "Amara Berri, Morlans", 10.53, 10.94, 11.26, 11.87, 12.16,
     11.74, 12.54, 13.47, 14.41),
    (None, "005", "Añorga", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
    (None, "009", "Gros - Sagües", 12.19, 12.41, 12.69, 12.73, 12.61, 13.14,
     13.39, 14.9, 15.9),
    (None, "099", "Fuera mapa", 1, 2, 3, 4, 5, 6, 7, 8, 9),  # unknown code
]


def test_rent_metric_basic_shape():
    (m,) = rent._build_from_rows(ROWS, CODE_TO_ID)
    assert m.id == "rent_eur_m2"
    assert m.unit == "€/m²"
    assert m.theme == "housing"
    assert m.status == "live"
    assert m.periods == [str(y) for y in range(2016, 2025)]


def test_values_joined_by_barrio_code():
    (m,) = rent._build_from_rows(ROWS, CODE_TO_ID)
    assert m.values["amaraberri"]["2016"] == 10.53
    assert m.values["amaraberri"]["2024"] == 14.41
    assert m.values["gros"]["2021"] == 13.14


def test_all_missing_barrio_is_omitted():
    (m,) = rent._build_from_rows(ROWS, CODE_TO_ID)
    assert "anorga" not in m.values  # every year was "-"


def test_unknown_code_dropped():
    (m,) = rent._build_from_rows(ROWS, CODE_TO_ID)
    assert all(bid in CODE_TO_ID.values() for bid in m.values)
