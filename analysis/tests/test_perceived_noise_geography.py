"""Tests de H6 — el ruido percibido, ¿coincide con la isla de calor y la VUT?

Funciones puras con fixtures + integración contra los CSV curados reales
(encuesta de ruido 2026 parcial; isla de calor REC-14; ruido medido y VUT del
pipeline). El hallazgo esperado: el ruido percibido va con el calor y el ruido
*medido* (densidad/tráfico del este), no con la densidad turística (VUT).
"""
import numpy as np
import pandas as pd
import pytest

import perceived_noise_geography as png


# ------------------------------------------------------- funciones puras -----
def test_point_biserial_equals_pearson_with_binary():
    y = np.array([1.0, 1.0, 0.0, 0.0])
    x = np.array([4.0, 3.0, 1.0, 2.0])
    assert png.point_biserial(y, x) == pytest.approx(np.corrcoef(y, x)[0, 1])


def test_point_biserial_perfect_separation():
    y = np.array([1.0, 1.0, 0.0, 0.0])
    x = np.array([9.0, 8.0, 1.0, 2.0])   # ruidosos siempre por encima
    assert png.point_biserial(y, x) > 0.9


def test_spearman_rank_correlation():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.array([10.0, 20.0, 30.0, 40.0])   # monótona → rho=1
    assert png.spearman(a, b) == pytest.approx(1.0)


def test_perceived_labels_from_survey():
    df = pd.DataFrame({"barrio_id": ["gros", "igeldo"],
                       "category": ["ruidoso", "tranquilo"]})
    y = png.perceived_labels(df)
    assert y["gros"] == 1.0 and y["igeldo"] == 0.0


def test_align_signals_only_survey_barrios():
    survey = pd.DataFrame({"barrio_id": ["gros", "igeldo"],
                           "category": ["ruidoso", "tranquilo"]})
    heat = pd.Series({"gros": 4.8, "igeldo": -3.1, "egia": 4.1})
    vut = pd.Series({"gros": 20.7, "igeldo": 4.8, "egia": 4.8})
    mnoise = pd.Series({"gros": 40.2, "igeldo": 1.3, "egia": 28.4})
    out = png.align_signals(survey, heat, vut, mnoise)
    assert list(out["barrio_id"]) == ["gros", "igeldo"]     # egia no está en encuesta
    assert out.set_index("barrio_id").loc["gros", "heat"] == 4.8
    assert set(out.columns) >= {"barrio_id", "y", "heat", "vut", "mnoise"}


# ------------------------------------------------------- integración real ----
def test_heat_reference_reproduces_rec14():
    heat = png.read_heat()
    assert heat["gros"] == pytest.approx(4.80, abs=0.05)         # el más caliente
    assert heat["landerbaso"] == pytest.approx(-4.64, abs=0.05)  # el más frío
    assert len(heat) == 19


def test_survey_maps_parte_vieja_to_erdialdea():
    surv = png.read_survey()
    assert "erdialdea" in set(surv["barrio_id"])   # Parte Vieja → Erdialdea
    # 5 ruidosos + 4 tranquilos declarados por la prensa
    assert (surv["category"] == "ruidoso").sum() == 5
    assert (surv["category"] == "tranquilo").sum() == 4


def test_real_cross_heat_and_measured_strong_vut_weaker():
    """H6: el ruido percibido coincide con calor y ruido medido; con VUT, menos."""
    corr = png.correlations()
    assert corr["heat"] > 0.6            # coincide con la isla de calor
    assert corr["mnoise"] > 0.6          # y con el ruido medido (control)
    assert corr["vut"] < corr["heat"]    # con la densidad turística, más flojo
    assert corr["vut"] < corr["mnoise"]


def test_vut_link_is_confounded_by_the_dense_centre():
    """Quitar el centro turístico (Erdialdea) debilita solo el vínculo VUT."""
    full = png.correlations()
    drop = png.correlations(exclude=["erdialdea"])
    assert drop["vut"] < full["vut"]        # VUT se apoya en el centro
    assert drop["heat"] == pytest.approx(full["heat"], abs=0.1)  # el calor aguanta
