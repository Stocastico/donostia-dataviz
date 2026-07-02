"""Tests de AN-14 — estacionalidad turística por barrio (reseñas mensuales).

Piezas: asignación punto→barrio (shapely), filtro de años completos (el
snapshot corta el último año), perfil mensual, ratio verano/invierno y Gini
mensual como índices de dependencia estival.
"""
import numpy as np
import pandas as pd
import pytest

import tourism_seasonality as ts


# --------------------------------------------------- punto → barrio ----
def _square(barrio_id: str, x0: float, y0: float, lado: float = 1.0) -> dict:
    return {
        "properties": {"barrio_id": barrio_id},
        "geometry": {"type": "Polygon", "coordinates": [[
            [x0, y0], [x0 + lado, y0], [x0 + lado, y0 + lado],
            [x0, y0 + lado], [x0, y0],
        ]]},
    }


def test_assign_listings_por_poligono():
    features = [_square("egia", 0, 0), _square("gros", 10, 10)]
    listings = pd.DataFrame({
        "id": [1, 2, 3],
        "longitude": [0.5, 10.5, 99.0],   # el tercero cae fuera (otro municipio)
        "latitude": [0.5, 10.5, 99.0],
    })
    out = ts.assign_listings(listings, features)
    assert out.to_dict() == {1: "egia", 2: "gros"}


# ------------------------------------------------- años completos ----
def test_complete_years_recorta_el_anio_del_snapshot():
    fechas = pd.Series(pd.to_datetime(
        ["2011-06-04", "2024-12-31", "2025-03-01"]))
    mask = ts.complete_years_mask(fechas, last_complete=2024)
    assert mask.tolist() == [True, True, False]


# ---------------------------------------------------- perfil mensual ----
def _reviews(spec: dict[str, list[tuple[int, int]]]) -> pd.DataFrame:
    """{barrio: [(mes, n), …]} → reseñas sintéticas de 2023."""
    rows = []
    for barrio, meses in spec.items():
        for mes, n in meses:
            rows += [{"barrio": barrio,
                      "date": pd.Timestamp(2023, mes, 15)}] * n
    return pd.DataFrame(rows)


def test_monthly_profile_shares():
    rev = _reviews({"gros": [(7, 30), (8, 60), (1, 10)]})
    prof = ts.monthly_profile(rev)
    assert prof.loc["gros"].sum() == pytest.approx(1.0)
    assert prof.loc["gros", 8] == pytest.approx(0.6)
    assert prof.loc["gros", 2] == pytest.approx(0.0)


def test_ratio_verano_invierno():
    # verano (jun-sep) 40/mes, invierno (nov-feb) 10/mes → ratio 4
    spec = [(m, 40) for m in ts.VERANO] + [(m, 10) for m in ts.INVIERNO]
    prof = ts.monthly_profile(_reviews({"egia": spec}))
    assert ts.summer_winter_ratio(prof).loc["egia"] == pytest.approx(4.0)


def test_ratio_invierno_cero_es_inf():
    prof = ts.monthly_profile(_reviews({"igeldo": [(7, 10)]}))
    assert np.isinf(ts.summer_winter_ratio(prof).loc["igeldo"])


# -------------------------------------------------------------- gini ----
def test_gini_uniforme_es_cero():
    assert ts.gini(np.full(12, 1 / 12)) == pytest.approx(0.0)


def test_gini_todo_en_un_mes():
    x = np.zeros(12)
    x[6] = 1.0
    assert ts.gini(x) == pytest.approx(11 / 12)


def test_gini_invariante_a_escala():
    x = np.array([1.0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    assert ts.gini(x) == pytest.approx(ts.gini(x * 1000))


# ------------------------------------------------------------ tabla ----
def test_seasonality_table_filtra_muestras_pequenas():
    rev = pd.concat([
        _reviews({"gros": [(7, 200), (1, 100)]}),
        _reviews({"zubieta": [(7, 3)]}),
    ])
    tab = ts.seasonality_table(rev, min_reviews=50)
    assert "gros" in tab.index and "zubieta" not in tab.index
    assert tab.loc["gros", "n_reviews"] == 300
